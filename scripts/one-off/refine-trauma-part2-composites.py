"""Split visually reviewed multi-instrument bitmaps without clipping silhouettes."""
import json,collections
from pathlib import Path
import cv2,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part2';A=R/'public/images/products/double-medical/trauma-catalogue-part2';W=Path('/tmp/xpmed-trauma-part2/composites');(W/'input').mkdir(parents=True,exist_ok=True)
assets=json.loads((F/'source-images.json').read_text());rows=json.loads((F/'instrument-rows-evidence.json').read_text());records=[]
reviewed={'page-440-art-01':8,'page-441-art-01':6,'page-442-art-01':5,'page-443-art-01':3,'page-443-art-02':4,'page-444-art-01':3,'page-445-art-03':3,'page-446-art-01':5,'page-446-art-02':3,'page-447-art-01':3,'page-447-art-04':3,'page-448-art-01':3,'page-448-art-02':4}
for key,expected in reviewed.items():
 parent=assets.get(key)
 if not parent:raise ValueError('Already split or missing '+key)
 im=Image.open(A/'_originals'/(key+'.png')).convert('RGB');arr=np.array(im);rr=[r for r in rows if r['pdfPage']==parent['pdfPage']];mask=(arr.min(axis=2)<240).astype('uint8');count,labels,stats,centroids=cv2.connectedComponentsWithStats(cv2.dilate(mask,np.ones((3,3),np.uint8)),8);owned=collections.defaultdict(list)
 for lab in range(1,count):
  x,y,w,h,area=stats[lab]
  if area<max(10,mask.sum()*.001):continue
  if x<im.width*.16 and h<6 and w<im.width*.18:continue # raster table-rule stubs, not instrument parts
  cy=parent['bounds'][1]+centroids[lab,1]/im.height*(parent['bounds'][3]-parent['bounds'][1]);row=min(rr,key=lambda r:abs(r['cy']+(0 if parent['pdfPage']==448 else .025)-cy));owned[row['id']].append(lab)
 if len(owned)!=expected:raise ValueError(f'{key}: expected {expected} source instruments, got {list(owned)}')
 assets.pop(key)
 for ident,labs in owned.items():
  ys,xs=np.where(np.isin(labels,labs));x0=max(0,int(xs.min())-2);y0=max(0,int(ys.min())-2);x1=min(im.width,int(xs.max())+3);y1=min(im.height,int(ys.max())+3);picture=arr[y0:y1,x0:x1].copy();picture[~np.isin(labels[y0:y1,x0:x1],labs)]=255;crop=Image.fromarray(picture);name=key+'-item-'+ident;crop.save(A/'_originals'/(name+'.png'));crop.save(W/'input'/(name+'.png'));b=parent['bounds'];bounds=[b[0]+x0/im.width*(b[2]-b[0]),b[1]+y0/im.height*(b[3]-b[1]),b[0]+x1/im.width*(b[2]-b[0]),b[1]+y1/im.height*(b[3]-b[1])];assets[name]={**parent,'name':name,'bounds':bounds,'originalSize':list(crop.size),'sourceComposite':key,'sourceRowId':ident,'sourceMethod':'Codex-reviewed connected instrument silhouettes; original composite retained; raster table-rule stubs excluded'}
 records.append({'sourceComposite':key,'pdfPage':parent['pdfPage'],'sourceRows':sorted(owned),'parts':len(owned)})
(F/'source-images-before-composite-split.json').write_text((F/'source-images.json').read_text());(F/'source-images.json').write_text(json.dumps(assets,indent=2)+'\n');(F/'split-composites.json').write_text(json.dumps(records,indent=2)+'\n');print('Split composites',len(records),'final native photos',len(assets),'new photos',sum(v['parts']for v in records))
