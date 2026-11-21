from PIL import Image,ImageDraw
import numpy as np,json,pathlib,re,sys
root=pathlib.Path('public/catalogs/conmed/advanced-surgical-product-catalog');out=pathlib.Path('reports/conmed/advanced-surgical-product-catalog/layout');out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,'scripts');from catalog_ocr import tesseract_words,lines_from_words
pages=list(range(5,9))+list(range(10,22))+list(range(23,40))+[41,42]
for n in pages:
 p=root/'ocr'/f'{n:03}.json'
 if not p.exists():continue
 target=out/f'parsed-{n:03}.json'
 if target.exists():target.unlink()
 evidence=json.loads(p.read_text());im=Image.open(root/'ocr'/f'{n:03}-600dpi.png');w,h=im.size;small=im.resize((800,round(h*800/w)));a=np.array(small);sh,sw=a.shape[:2];black=(a[int(sh*.12):int(sh*.89),int(sw*.535):int(sw*.925)].max(axis=2)<80).mean(axis=1)>.5
 ys=np.flatnonzero(black)+int(sh*.12);runs=[]
 for y in ys:
  if runs and y-runs[-1][-1]<=3:runs[-1].append(int(y))
  else:runs.append([int(y)])
 import pymupdf as fitz
 page=fitz.open('catalogs-source/conmed/advanced-surgical-product-catalog.pdf')[n-1];pw,ph=page.rect.width,page.rect.height;bars=[]
 for drawing in page.get_drawings():
  if drawing.get('fill') and max(drawing['fill'])<.22:
   for item in drawing['items']:
    if item[0]=='re':
     rect=item[1]
     if rect.width>pw*.30 and ph*.12<rect.y0<ph*.88 and ph*.012<rect.height<ph*.06:bars.append([rect.x0/pw,rect.y0/ph,rect.x1/pw,rect.y1/ph])
 bars=sorted(bars,key=lambda b:b[1])
 groups=[]
 for gi,bar in enumerate(bars):
  end=bars[gi+1][1]if gi+1<len(bars)else .885
  hb=im.crop((int(bar[0]*w),int((bar[1]-.001)*h),int(bar[2]*w),int((bar[3]+.001)*h)));import io
  from PIL import ImageOps
  hb=ImageOps.expand(ImageOps.invert(hb.convert('RGB')),border=16,fill='white');b=io.BytesIO();hb.save(b,format='PNG');raw,words=tesseract_words(b.getvalue(),7,dpi=600);title=' '.join(word['text']for word in words)
  ewords=[q for q in evidence['passes']['3']['words']if bar[3]<=(q['bounds'][1]+q['bounds'][3])/2<end and q['bounds'][0]>bar[0]-.005]
  codewords=[q for q in ewords if (q['bounds'][2]>.88 or q['bounds'][0]>.82) and q['bounds'][0]>.775]
  codeLines=[]
  for q in sorted(codewords,key=lambda x:(x['bounds'][1],x['bounds'][0])):
   cy=(q['bounds'][1]+q['bounds'][3])/2
   if codeLines and abs(cy-codeLines[-1]['cy'])<.004:codeLines[-1]['words'].append(q)
   else:codeLines.append({'cy':cy,'words':[q]})
  rows=[]
  for line in codeLines:
   line['words'].sort(key=lambda q:q['bounds'][0]);code=''.join(q['text']for q in line['words']).strip('.,:;|')
   if code=='Neptune3':continue
   if not (re.search('[0-9-]',code) or re.fullmatch('[A-Z]{5,}',code)) or re.search(r'(Box|case|mm|Tanks|Fitting)',code,re.I):continue
   bounds=[min(q['bounds'][0]for q in line['words']),min(q['bounds'][1]for q in line['words']),max(q['bounds'][2]for q in line['words']),max(q['bounds'][3]for q in line['words'])]
   rows.append({'candidate':code,'bounds':bounds,'cy':line['cy'],'rawWords':line['words']})
  # Thin horizontal vector rules mark the row boundaries; derive them from the image.
  gray=a[:,:,0].astype(float); rules=[]
  for yy in range(int(bar[3]*sh),int(end*sh)):
   strip=a[yy,int(sw*.535):int(sw*.925)]; dark=(strip.max(axis=1)-strip.min(axis=1)<15)&(strip.mean(axis=1)<220)
   if dark.mean()>.85:rules.append(yy/sh)
  for ri,row in enumerate(rows):
   prev=rows[ri-1]['bounds'][3]if ri else bar[3];nxt=rows[ri+1]['bounds'][1]if ri+1<len(rows)else end
   before=[y for y in rules if prev<y<row['bounds'][1]];after=[y for y in rules if row['bounds'][3]<y<nxt]
   top=max(before)if before else ((prev+row['bounds'][1])/2 if ri else bar[3]);bottom=min(after)if after else ((row['bounds'][3]+nxt)/2 if ri+1<len(rows)else end)
   ww=[q for q in ewords if top<=(q['bounds'][1]+q['bounds'][3])/2<=bottom and q['bounds'][0]<.82 and q not in row['rawWords']]
   texts=lines_from_words(ww);row['description']=' '.join(l['text']for l in texts);row['rowBounds']=[bar[0],top,.934,bottom]
   row.pop('rawWords')
  groups.append({'title':title,'headerBounds':bar,'end':end,'rows':rows})
 if n in [13,20] and not groups[0]['rows']:
  words=[q for q in evidence['passes']['11']['words']if q['bounds'][0]>.79 and groups[0]['headerBounds'][3]<(q['bounds'][1]+q['bounds'][3])/2<groups[1]['headerBounds'][1]]
  if words:
   q=max(words,key=lambda q:len(q['text']));b=q['bounds'];groups[0]['rows']=[{'candidate':q['text'],'description':'Sterile, 10 (3.0 m) 10/case'if n==13 else'1/case','bounds':b,'cy':(b[1]+b[3])/2,'rowBounds':[.529,groups[0]['headerBounds'][3],.934,groups[1]['headerBounds'][1]]}]
 data={'page':n,'groups':groups};target.write_text(json.dumps(data,indent=2));print(n,len(groups),'groups',sum(len(g['rows'])for g in groups),'rows',flush=True)
