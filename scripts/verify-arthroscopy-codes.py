#!/usr/bin/env python3
"""Retain raw source OCR, independent local Vision lines and official exact-code evidence."""
import json,re,difflib,io,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from catalog_ocr import tesseract_words
F=R/'reports/conmed/arthroscopy-product-catalog';ref=R/'public/catalogs/conmed/arthroscopy-product-catalog';(F/'line-crops').mkdir(exist_ok=True);official=(F/'official/text.txt').read_text();records=[]
def normalize(s):return s.strip(' .,:;|_\t').replace('®','').replace('™','')
def matches(text,code):
 return any(normalize(t)==code for t in re.split(r'\s+|\.{2,}',text))or code in [normalize(''.join(text.split()[a:b]))for a in range(len(text.split()))for b in range(a+1,min(a+4,len(text.split()))+1)]
for p in sorted((F/'layout').glob('*.json')):
 page=json.loads(p.read_text());n=page['pdfPage'];e=json.loads((ref/'ocr'/f'{n:03}.json').read_text());vision_file=F/'vision'/f'{n:03}.json';vision=json.loads(vision_file.read_text())if vision_file.exists()else[];im=None
 for gi,g in enumerate(page['groups']):
  for ri,row in enumerate(g['rows']):
   for ci,code in enumerate(row['codes']):
    value=code['candidate'];b=code['sourceBounds'];
    if b[1]<0 or b[3]>1:
     options=[w for w in e['passes']['11']['words'] if matches(w['text'],value)]
     if options:b=min(options,key=lambda w:abs(w['bounds'][0]-b[0]))['bounds']
    cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;readings=[]
    # Prefer a unique exact source token as the actual location; no character substitution.
    for mode in ['3','11']:
     words=e['passes'][mode]['words'];exact=[w for w in words if matches(w['text'],value)and abs((w['bounds'][0]+w['bounds'][2])/2-cx)<.06]
     if exact:
      best=min(exact,key=lambda w:abs((w['bounds'][1]+w['bounds'][3])/2-cy));
      if abs((best['bounds'][1]+best['bounds'][3])/2-cy)<.05:b=best['bounds'];cy=(b[1]+b[3])/2;cx=(b[0]+b[2])/2
     ww=[w for w in words if abs((w['bounds'][1]+w['bounds'][3])/2-cy)<.006 and w['bounds'][2]>b[0]-.02 and w['bounds'][0]<b[2]+.015];ww.sort(key=lambda w:w['bounds'][0]);readings.append({'reader':'Tesseract-600dpi-PSM'+mode,'text':' '.join(w['text']for w in ww),'confidence':min((w['confidence']for w in ww),default=0)})
    vv=[line for line in vision if abs((line['bounds'][1]+line['bounds'][3])/2-cy)<.008 and line['bounds'][2]>b[0]-.025 and line['bounds'][0]<b[2]+.02];readings.append({'reader':'Apple-Vision-accurate','text':' '.join(line['text']for line in vv),'confidence':min((line['confidence']for line in vv),default=0)})
    agreement=[r['reader']for r in readings if matches(r['text'],value)];third=any(r['reader']=='Apple-Vision-accurate'and matches(r['text'],value)for r in readings);verified=len(agreement)>=2 and third
    found=bool(re.search(r'(?<![A-Za-z0-9-])'+re.escape(value)+r'(?![A-Za-z0-9-])',official))
    ident=f'{n:03}-{gi+1:02}-{ri+1:02}-{ci+1}';line_path=F/'line-crops'/(ident+'.png')
    if im is None:im=Image.open(ref/'ocr'/f'{n:03}-600dpi.png').convert('RGB');w,h=im.size
    rb=row['rowBounds'];y0=min(rb[1],b[1])-.004;y1=max(rb[3],b[3])+.004;x0=min(rb[0],b[0])-.01;x1=max(rb[2],b[2])+.012;pixel=[max(0,int(x0*w)),max(0,int(y0*h)),min(w,int(x1*w)),min(h,int(y1*h))]
    if pixel[3]<=pixel[1]or pixel[2]<=pixel[0]:
     print('BAD',n,ident,value,pixel,page['alignment']);pixel=[0,0,w,h]
    im.crop(pixel).save(line_path)
    records.append({'id':ident,'pdfPage':n,'groupIndex':gi,'rowIndex':ri,'columnIndex':ci,'expectedOfficialCode':value,'value':value if verified else None,'sourceDescription':row['description'],'sourceBounds':b,'rowBounds':[x0,y0,x1,y1],'readings':readings,'matchedReaders':agreement,'verificationStatus':'verified (independent OCR readers)'if verified else'requires visual source reading','officialEvidence':[{'url':'https://www.conmed.com/-/media/conmed/documents/catalog/arthroscopy_catalog.ashx#page='+str(page['officialPage']),'code':value,'officialPdfPage':page['officialPage']}]if found else[],'lineCrop':str(line_path.relative_to(R))})
(F/'verification.json').write_text(json.dumps({'found':len(records),'verified':sum(r['value']is not None for r in records),'confirmedOnConmedCom':sum(bool(r['officialEvidence'])for r in records),'flagged':sum(r['value']is None for r in records),'records':records},ensure_ascii=False,indent=2)+'\n');print('Codes',len(records),'verified',sum(r['value']is not None for r in records),'flagged',sum(r['value']is None for r in records),'Vision pages',len(list((F/'vision').glob('*.json'))))
