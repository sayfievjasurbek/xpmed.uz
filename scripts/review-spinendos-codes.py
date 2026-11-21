"""Apply Codex visual readings already checked against this exact source; do not use for other PDFs."""
import json,sys,re,io,collections
from pathlib import Path
sys.path.insert(0,'scripts');from catalog_ocr import tesseract_words
assert __import__('hashlib').sha256(Path('catalogs-source/spinendos/endoscopic-spine-surgery-system.pdf').read_bytes()).hexdigest()=='bf5f6a1a58ca73e2eeab772c1ad98f5bdfe8c3021b51029d4494814199b8d034', 'Reviewed readings apply only to this exact source PDF'
F=Path('reports/spinendos/endoscopic-spine-surgery-system');r=json.loads((F/'verification.json').read_text());omit=['007-017','007-018'];fix={'008-009':'SP082628.261','011-009':'SP082181.111','014-016':'SP082781.841','018-008':'SP082799.035S'};out=[];visual={}
for x in r['records']:
 if x['id']in omit:continue
 if not x['value']:
  value=fix.get(x['id'],x['candidate']);visual[x['id']]={'value':value,'author':'codex','method':'Visual reading of supplied 600-DPI caption/row crop','crop':x['lineCrop']};x['visualReading']=visual[x['id']]
  if not any(o['code']==value for o in x['readings']):
   from PIL import Image
   im=Image.open(x['lineCrop']);im=im.crop((0,0,im.width,min(im.height,round(im.height*.35))));buf=io.BytesIO();im.save(buf,format='PNG')
   for psm in [7,13]:
    raw,words=tesseract_words(buf.getvalue(),psm,dpi=600);text=' '.join(w['text']for w in words);x['readings'].append({'reader':'Isolated-PSM'+str(psm),'line':text,'code':text,'confidence':min((w['confidence']for w in words),default=0)})
  agreed=any(value in o['code'] or value in o.get('line','') for o in x['readings']);x['value']=value if agreed else None;x['verificationStatus']='verified (visual + OCR)'if agreed else'requires review: visual/OCR disagreement'
 out.append(x)
# Multiple OCR rows can point to the same printed item. Retain every observation in the one source record.
done=[]
for x in out:
 old=next((v for v in done if v['pdfPage']==x['pdfPage'] and v['value'] and v['value']==x['value']),None)
 if old:old.setdefault('additionalOCRLocations',[]).append(x);continue
 done.append(x)
r.update(records=done,found=len(done),verified=sum(bool(x['value'])for x in done),excludedPhotoEngravings=omit);(F/'verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(F/'visual-readings.json').write_text(json.dumps(visual,indent=2));print(r['found'],r['verified']);print([(x['id'],x['candidate'],x['readings'][-2:])for x in done if not x['value']])
