"""Isolated 600-DPI code reads; original OCR and official corroboration retained."""
import json,sys,re,io,collections,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent));from catalog_ocr import tesseract_words
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';O=R/'public/catalogs/conmed/hall-powered-instruments/ocr'
PAT=re.compile(r'(?<![A-Za-z0-9])(?:[A-Z]{0,6}\d{2,6}(?:-[A-Z0-9]{2,8})+|[A-Z]{1,6}\d{2,6}[A-Z]{0,6})(?![A-Za-z0-9])')
def work(r):
 n=r['pdfPage'];im=Image.open(O/f'{n:03}-600dpi.png');w,h=im.size;b=r['sourceBounds'];crop=im.crop((max(0,int(b[0]*w)-10),max(0,int(b[1]*h)-7),min(w,int(b[2]*w)+10),min(h,int(b[3]*h)+7)));path=F/'line-crops'/(r['id']+'.png');crop.save(path);r['lineCrop']=str(path.relative_to(R))
 if r['value']:return r
 raw=io.BytesIO();crop.save(raw,format='PNG')
 for psm in [7,13]:
  _,words=tesseract_words(raw.getvalue(),psm,dpi=600);text=' '.join(w['text']for w in words);r['readings'].append({'reader':'isolated-PSM'+str(psm),'text':text})
 candidates=collections.Counter(c for read in r['readings']for c in set(PAT.findall(read['text'])));official=[e['code']for e in r['officialEvidence']];candidate=next((c for c in official if c in candidates),candidates.most_common(1)[0][0]if candidates else r['candidate']);agree=[x['reader']for x in r['readings']if candidate in PAT.findall(x['text'])];r['candidate']=candidate;r['matchedReaders']=agree
 if len(agree)>=3 and any(x.startswith('isolated-')for x in agree)and('Vision'in agree or candidate in official):r['value']=candidate;r['verificationStatus']='verified (isolated OCR + third-reader/official agreement)'
 return r
if __name__=='__main__':
 records=json.loads((F/'verification-initial.json').read_text())['records']
 with ProcessPoolExecutor(max_workers=4)as pool:records=list(pool.map(work,records))
 (F/'verification.json').write_text(json.dumps({'records':records,'found':len(records),'verified':sum(bool(r['value'])for r in records)},ensure_ascii=False,indent=2));flagged=[r for r in records if not r['value']];print('Found',len(records),'verified',len(records)-len(flagged),'flagged',len(flagged))
 for start in range(0,len(flagged),30):
  sheet=Image.new('RGB',(1800,6*180),'white');draw=ImageDraw.Draw(sheet)
  for k,r in enumerate(flagged[start:start+30]):
   im=Image.open(R/r['lineCrop']);im.thumbnail((350,145));x=k%5*360;y=k//5*180;sheet.paste(im,(x,y+24));draw.text((x+2,y+2),r['id']+' '+r['candidate'],fill='black')
  sheet.save('/tmp/conmed-hall/flags-'+str(start//30)+'.png')
