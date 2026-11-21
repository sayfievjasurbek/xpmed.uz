"""Correlate supplied outline-only HALL pages with CONMED's official logical pages."""
import json,re,math,collections
from pathlib import Path
import pymupdf as f,numpy as np,cv2
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';D=f.open(F/'official/logical.pdf')
def norm(s):return re.sub('[^a-z0-9-]','',s.lower())
def tokens(text):return {t for t in map(norm,re.split(r'[\s.]+',text))if len(t)>3 and t not in ['customer','service','within','outside','phone','conmed','products','available','markets']}
off=[{'page':n,'tokens':tokens(p.get_text()),'text':p.get_text()}for n,p in enumerate(D,1)];df=collections.Counter(t for p in off for t in p['tokens']);idf={t:math.log(1+len(off)/n)*(4 if re.search(r'\d{3}',t)else 1)for t,n in df.items()};rows=[]
for n in range(8,79):
 e=json.loads((R/f'public/catalogs/conmed/hall-powered-instruments/ocr/{n:03}.json').read_text());source=tokens(' '.join(w['text']for w in e['passes']['11']['words']if .1<w['bounds'][1]<.93));scores=sorted([(sum(idf[t]for t in source&p['tokens'])/(sum(idf.get(t,1)for t in source)+.01),p['page'])for p in off],reverse=True);pn=27 if n==25 else scores[0][1];p=D[pn-1];pw,ph=p.rect.width,p.rect.height;ow=collections.defaultdict(list);sw=collections.defaultdict(list)
 for w in p.get_text('words'):
  if .10<w[1]/ph<.92:ow[norm(w[4])].append([(w[0]+w[2])/2/pw,(w[1]+w[3])/2/ph])
 for w in e['passes']['11']['words']:
  if .1<w['bounds'][1]<.93:sw[norm(w['text'])].append([(w['bounds'][0]+w['bounds'][2])/2,(w['bounds'][1]+w['bounds'][3])/2])
 src=[];dst=[]
 for key in ow.keys()&sw.keys():
  if len(key)>=4 and len(ow[key])==len(sw[key])==1:src.append(ow[key][0]);dst.append(sw[key][0])
 M,ins=cv2.estimateAffine2D(np.array(src)*1000,np.array(dst)*1000,ransacReprojThreshold=7)if len(src)>=4 else(None,None)
 if M is None:M=np.array([[1,0,0],[0,1,0]],float)
 else:M[:,2]/=1000
 row={'pdfPage':n,'officialPage':pn,'score':scores[0][0],'alternatives':scores[:3],'alignment':M.tolist(),'alignmentMatches':len(src),'alignmentInliers':int(ins.sum())if ins is not None else 0};rows.append(row)
(F/'page-mapping.json').write_text(json.dumps(rows,indent=2));print('\n'.join(f"{r['pdfPage']:2} -> {r['officialPage']:2} score {r['score']:.2f} matches {r['alignmentMatches']}/{r['alignmentInliers']}"for r in rows))
