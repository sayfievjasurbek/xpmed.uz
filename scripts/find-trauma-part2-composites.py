import json,collections
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part2';A=R/'public/images/products/double-medical/trauma-catalogue-part2';native=json.loads((F/'source-images.json').read_text());rows=json.loads((F/'instrument-rows-final.json').read_text());out=[]
for key,a in native.items():
 if a.get('sourceComposite')or a['bounds'][3]-a['bounds'][1]<.075:continue
 rr=[r for r in rows if r['pdfPage']==a['pdfPage']]
 if not rr:continue
 im=Image.open(A/'_originals'/(key+'.png')).convert('RGB');arr=np.array(im);mask=(arr.min(axis=2)<240).astype('uint8')
 if mask.mean()>.3:continue
 count,labels,stats,centroids=cv2.connectedComponentsWithStats(cv2.dilate(mask,np.ones((3,3),np.uint8)),8);owned=collections.defaultdict(list)
 for lab in range(1,count):
  if stats[lab,4]<max(15,mask.sum()*.02):continue
  cy=a['bounds'][1]+centroids[lab,1]/im.height*(a['bounds'][3]-a['bounds'][1]);row=min(rr,key=lambda r:abs(r['cy']+.015-cy));owned[row['id']].append(lab)
 if len(owned)>1:out.append({'key':key,'rowIds':list(owned),'captions':{r['id']:r['description']for r in rr if r['id']in owned}})
(F/'additional-composite-candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for start in range(0,len(out),12):
 sheet=Image.new('RGB',(1200,4*310),'white');d=ImageDraw.Draw(sheet)
 for i,entry in enumerate(out[start:start+12]):
  im=Image.open(A/'_originals'/(entry['key']+'.png')).convert('RGB');im=ImageOps.contain(im,(380,270));x=i%3*400;y=i//3*310;sheet.paste(im,(x+(400-im.width)//2,y+25));d.text((x+5,y+3),entry['key']+' '+','.join(entry['rowIds']),fill='black')
 sheet.save(F/f'extra-composite-candidates-{start//12+1:02}.png')
print('Composite candidates',len(out))
