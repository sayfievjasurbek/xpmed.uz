"""Three independent local readers; retain disagreements and source crops, never infer digits."""
import json,re,collections,sys
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/spinendos/endoscopic-spine-surgery-system';O=R/'public/catalogs/spinendos/endoscopic-spine-surgery-system/ocr';(F/'line-crops').mkdir(exist_ok=True)
PAT=re.compile(r'(?:SP|5P|9P)\s*[0O]\s*(?:\d\s*){5}\.\s*\d(?:\s*\d){2}(?:[A-Z]|\d)?')
def found(text):
 return [(m.group(),re.sub(r'\s+','',m.group()),m.span())for m in PAT.finditer(text)]
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
from spinendos_layout import ZONES
records=[]
for n in range(4,20):
 v=json.loads((F/'vision'/f'{n:03}.json').read_text());e=json.loads((O/f'{n:03}.json').read_text());lines={'Vision':v,**{'PSM'+p:e['passes'][p]['lines']for p in ['3','11']}};candidates=[]
 # Vision usually separates captions cleanly; Tesseract adds any omitted lines.
 for reader,rr in lines.items():
  for line in rr:
   for raw,code,span in found(line['text']):
    b=line['bounds'];b=list(b)
    # Exact Tesseract token location narrows a mixed multi-column line.
    words=[w for p in ['11','3']for w in e['passes'][p]['words']if code==re.sub(r'\s+','',w['text']).strip('*#')and abs(w['bounds'][1]-b[1])<.012]
    if words:b=min(words,key=lambda w:abs(w['bounds'][0]-b[0]))['bounds']
    elif len(found(line['text']))>1:
     width=b[2]-b[0];b=[b[0]+width*span[0]/len(line['text']),b[1],b[0]+width*span[1]/len(line['text']),b[3]]
    existing=next((c for c in candidates if abs(c['bounds'][1]-b[1])<.011 and abs(c['bounds'][0]-b[0])<.06),None)
    if existing:existing['observations'].append({'reader':reader,'raw':raw,'code':code,'line':line['text'],'confidence':line['confidence']})
    else:candidates.append({'bounds':b,'observations':[{'reader':reader,'raw':raw,'code':code,'line':line['text'],'confidence':line['confidence']}]})
 im=Image.open(O/f'{n:03}-600dpi.png');w,h=im.size
 candidates=[c for c in candidates if any(z[3]==n and z[4]-.01<=c['bounds'][0]<z[6] and z[5]-.005<=c['bounds'][1]<z[7] for z in ZONES)]
 for i,c in enumerate(sorted(candidates,key=lambda c:(round(c['bounds'][1],2),c['bounds'][0])),1):
  counts=collections.Counter(x['code']for x in c['observations']);best=counts.most_common(1)[0][0];agree={x['reader']for x in c['observations']if x['code']==best};valid=bool(re.fullmatch(r'SP0\d{5}\.\d{3}[A-Z]?',best));ok=valid and len(agree)==3
  b=c['bounds'];ident=f'{n:03}-{i:03}';crop=F/'line-crops'/(ident+'.png');im.crop((max(0,int((b[0]-.01)*w)),max(0,int((b[1]-.004)*h)),min(w,int((b[2]+.05)*w)),min(h,int((b[3]+.045)*h)))).save(crop)
  records.append({'id':ident,'pdfPage':n,'candidate':best,'value':best if ok else None,'sourceBounds':b,'readings':c['observations'],'matchedReaders':sorted(agree),'verificationStatus':'verified (three independent OCR readings)'if ok else'requires visual source reading','lineCrop':str(crop.relative_to(R))})
dump(F/'verification.json',{'found':len(records),'verified':sum(bool(r['value'])for r in records),'records':records})
flagged=[r for r in records if not r['value']];print('Found',len(records),'triple verified',len(records)-len(flagged),'visual review',len(flagged))
for start in range(0,len(flagged),24):
 sheet=Image.new('RGB',(1600,6*240),'white');d=ImageDraw.Draw(sheet)
 for k,r in enumerate(flagged[start:start+24]):
  im=Image.open(R/r['lineCrop']);im.thumbnail((390,205));x=(k%4)*400;y=(k//4)*240;sheet.paste(im,(x,y+28));d.text((x+4,y+4),r['id']+' '+r['candidate'],fill='black')
 sheet.save('/tmp/spinendos/flags-'+str(start//24)+'.png')
