import json,pathlib,sys,io,re
from PIL import Image,ImageOps,ImageFilter
sys.path.insert(0,'scripts');from catalog_ocr import tesseract_words
folder=pathlib.Path('reports/conmed/advanced-surgical-product-catalog');v=json.load(open(folder/'verification.json'));cache={}
for r in v['flagged']:
 n=r['pdfPage'];key=f'code-{n:03}-{r["pageRow"]:02}.json';p=folder/key;s=json.loads(p.read_text());expected=s['visualReading'];im=cache.get(n)
 if im is None:im=Image.open(f'public/catalogs/conmed/advanced-surgical-product-catalog/ocr/{n:03}-600dpi.png');cache[n]=im
 w,h=im.size;b=s['sourceBounds'];crop=im.crop((int(w*.79),int(h*b[1])-3,int(w*.935),int(h*b[3])+3)).convert('L')
 for mode in [7,13]:
  for scale,threshold in [(.5,None),(.5,175),(.75,210),(1,None)]:
   label=f'isolated-psm{mode}-scale{scale}-threshold{threshold}'
   if label in s['ocrReadings']:continue
   image=crop
   if threshold:image=image.point(lambda x:0 if x<threshold else 255)
   image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS);image=ImageOps.expand(image,border=24,fill=255);blob=io.BytesIO();image.save(blob,format='PNG');_,words=tesseract_words(blob.getvalue(),mode,dpi=round(600*scale));raw=' '.join(x['text']for x in words);s['ocrReadings'][label]=raw;tokens=[t.strip('.,:;|_')for t in raw.split()]
   if expected in tokens or expected==''.join(tokens):s['matchedReaders'].append(label);s['value']=expected;s['verificationStatus']='verified (visual + OCR)'
   if s['value']:break
  if s['value']:break
 p.write_text(json.dumps(s,ensure_ascii=False,indent=2));print(n,expected,'OK'if s['value']else'FLAG',flush=True)
records=[json.loads((folder/f'code-{r["pdfPage"]:03}-{r["pageRow"]:02}.json').read_text())for r in v['records']];v.update(records=records,verified=sum(r['value']is not None for r in records),flagged=[r for r in records if r['value']is None]);(folder/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2));print('VERIFIED',v['verified'],'FLAGS',len(v['flagged']),flush=True)
