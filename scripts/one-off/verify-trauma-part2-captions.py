"""Read the printed phi glyph instead of treating its OCR 0/4/9 as a digit.
Only descriptions are normalized; REF codes are never changed here.
The independent raster template is Codex-calibrated on PDF p238, first caption.
"""
import json,re,collections
from pathlib import Path
import numpy as np
from PIL import Image
import pymupdf as fitz
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part2';O=R/'public/catalogs/double-medical/trauma-catalogue/ocr';D=fitz.open(R/'catalogs-source/double-medical/trauma-catalogue.pdf');rows=json.loads((F/'instrument-rows-evidence.json').read_text());pageImage=None;pageNumber=None

def glyphs(n,bounds):
 global pageImage,pageNumber
 if n!=pageNumber:
  if pageImage:pageImage.close()
  pageImage=Image.open(O/f'{n:03}-600dpi.png').convert('L');pageNumber=n
 b=bounds;w,h=pageImage.size;x0=max(0,int(b[0]*w)-2);y0=max(0,int(b[1]*h)-2);im=pageImage.crop((x0,y0,int(b[2]*w)+3,int(b[3]*h)+3));a=np.array(im)<100;ink=np.where(a.any(axis=0))[0]
 if not len(ink):return []
 runs=[];start=prev=ink[0]
 for x in ink[1:]:
  if x>prev+1:runs.append((start,prev+1));start=x
  prev=x
 runs.append((start,prev+1));out=[]
 for l,r in runs:
  ys=np.where(a[:,l:r].any(axis=1))[0]
  if not len(ys):continue
  v=a[ys[0]:ys[-1]+1,l:r];out.append({'array':np.asarray(Image.fromarray((v*255).astype('uint8')).resize((32,48),Image.Resampling.BILINEAR),dtype=float)/255,'aspect':v.shape[1]/v.shape[0],'height':v.shape[0],'width':v.shape[1]})
 return out
p=D[237];rect=next(a['rect']for a in p.get_drawings()if a['type']=='f'and .22<a['rect'].x0/p.rect.width<.72 and .18<a['rect'].y0/p.rect.height<.22 and a['rect'].height<13)
seed=glyphs(238,[rect.x0/p.rect.width,rect.y0/p.rect.height,rect.x1/p.rect.width,rect.y1/p.rect.height])[9]
def isphi(g):return float(np.mean(np.abs(g['array']-seed['array'])))+min(abs(g['aspect']-seed['aspect']),2)*.12<.10

def normalize_word(n,w):
 text=w['text'];parts=text.split('/')
 if not re.search(r'\d\.\d',text):return text,None
 gs=glyphs(n,w['bounds']);phis=[i for i,g in enumerate(gs)if isphi(g)]
 if not phis:return text,None
 numericParts=[i for i,t in enumerate(parts)if re.search(r'\d\.\d',t)]
 if len(phis)!=len(numericParts):return text,{'text':text,'issue':'phi/decimal-part alignment','phiGlyphs':phis,'bounds':w['bounds']}
 changes=[]
 for ii,(partIndex,pi)in enumerate(zip(numericParts,phis)):
  part=parts[partIndex];end=phis[ii+1]if ii+1<len(phis)else len(gs);dot=next((j for j in range(pi+1,end)if gs[j]['height']<9 and gs[j]['width']<9),None)
  if dot is None:return text,{'text':text,'issue':'decimal glyph not isolated','bounds':w['bounds']}
  sourceCount=dot-pi-1;match=re.search(r'([0-9]+)\.',part)
  if not match:return text,None
  digits=match[1]
  if len(digits)==sourceCount+1 and digits[0]in '049':digits=digits[1:]
  elif len(digits)!=sourceCount:return text,{'text':text,'issue':'digit count disagrees with source glyphs','printedDigitsBeforeDecimal':sourceCount,'bounds':w['bounds']}
  before=part[:match.start()];before=re.sub(r'[0O49@$©®ФфΦφØ]+$','',before)
  parts[partIndex]=before+'Ø'+digits+part[match.end()-1:];changes.append({'printedDigitsBeforeDecimal':sourceCount,'phiGlyph':pi})
 result='/'.join(parts)
 return result,{'raw':text,'normalized':result,'bounds':w['bounds'],'method':'600-DPI source phi glyph + counted printed digits before decimal','parts':changes}
currentPage=None;wordReaders={};records=[];uncertain=[]
for ri,row in enumerate(rows):
 n=row['pdfPage']
 if n!=currentPage:
  j=json.loads((O/f'{n:03}.json').read_text());wordReaders={k:j['passes'][p]['words']for k,p in [('PSM3','3'),('PSM11','11')]};currentPage=n
 normalized=dict(row['descriptionReadings']);evidence=[]
 for reader,words in wordReaders.items():
  for w in words:
   b=w['bounds'];y=(b[1]+b[3])/2
   if not(.22<b[0]<.72 and row['sourceBounds'][1]<y<row['sourceBounds'][3]):continue
   if w['text']not in normalized[reader]:continue
   new,record=normalize_word(n,w)
   if record:
    if record.get('issue'):uncertain.append({'row':row['id'],'reader':reader,**record})
    else:evidence.append({'reader':reader,**record});normalized[reader]=normalized[reader].replace(w['text'],new)
 # Visible Greek phi variants are the diameter symbol, not a numerical value.
 normalized={reader:re.sub(r'[@©®ФфΦφØ$](?=\d)','Ø',text)for reader,text in normalized.items()}
 numeric=lambda text:re.findall(r'\d+(?:\.\d+)?',text)
 grouped=collections.Counter(tuple(numeric(t))for t in normalized.values());best,count=grouped.most_common(1)[0]
 candidates=[(reader,text)for reader,text in normalized.items()if tuple(numeric(text))==best]
 # Prefer the detailed English OCR wording once numeric agreement has been checked.
 selected=next((t for r,t in candidates if r=='PSM3'),candidates[0][1])
 if count<2:uncertain.append({'row':row['id'],'issue':'caption numerical readings disagree','readings':normalized})
 row['description']=selected;row['descriptionNormalizedReadings']=normalized;row['descriptionGlyphEvidence']=evidence
 if evidence:records.append({'row':row['id'],'sourcePage':n,'evidence':evidence})
 if ri%100==0:print('Caption verification',ri,'/',len(rows),flush=True)
(F/'instrument-rows-evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(F/'caption-glyph-evidence.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');(F/'caption-numeric-review.json').write_text(json.dumps(uncertain,ensure_ascii=False,indent=2)+'\n');print('Rows',len(rows),'phi normalized',len(records),'items to inspect',len(uncertain),flush=True)
