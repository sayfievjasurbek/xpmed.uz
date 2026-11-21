"""Separate two reviewed multi-instrument source composites without clipping silhouettes."""
import json,collections
from pathlib import Path
import cv2,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part1';A=R/'public/images/products/double-medical/trauma-catalogue';W=Path('/tmp/xpmed-trauma/native-artwork/input');assets=json.loads((F/'source-images.json').read_text());old=json.loads((F/'source-images-before-logo-cleanup.json').read_text());rows=json.loads((F/'instrument-rows-final.json').read_text());records=[]
for key in ['page-056-art-02','page-068-art-05']:
    children=[(k,v)for k,v in assets.items()if v.get('sourceComposite')==key]
    if key in assets:parent=assets[key]
    elif children:parent={**children[0][1],'name':key,'bounds':old[key]['bounds']}
    else:raise ValueError('Missing reviewed source composite '+key)
    im=Image.open(A/'_originals'/(key+'.png')).convert('RGB');arr=np.array(im);parent['originalSize']=list(im.size);n=parent['pdfPage'];rr=[r for r in rows if r['pdfPage']==n];mask=(arr.min(axis=2)<240).astype('uint8');count,labels,stats,centroids=cv2.connectedComponentsWithStats(cv2.dilate(mask,np.ones((3,3),np.uint8)),8);owned=collections.defaultdict(list)
    for lab in range(1,count):
        if stats[lab,4]<max(10,mask.sum()*.001):continue
        cy=parent['bounds'][1]+centroids[lab,1]/im.height*(parent['bounds'][3]-parent['bounds'][1]);row=min(rr,key=lambda r:abs(r['cy']-cy));owned[row['id']].append(lab)
    for child,_ in children:assets.pop(child);(W/(child+'.png')).unlink(missing_ok=True)
    assets.pop(key,None);(W/(key+'.png')).unlink(missing_ok=True)
    for ident,labs in owned.items():
        ys,xs=np.where(np.isin(labels,labs));x0=max(0,int(xs.min())-2);y0=max(0,int(ys.min())-2);x1=min(im.width,int(xs.max())+3);y1=min(im.height,int(ys.max())+3);picture=arr[y0:y1,x0:x1].copy();picture[~np.isin(labels[y0:y1,x0:x1],labs)]=255;crop=Image.fromarray(picture);name=key+'-item-'+ident;crop.save(A/'_originals'/(name+'.png'));crop.save(W/(name+'.png'));b=parent['bounds'];bounds=[b[0]+x0/im.width*(b[2]-b[0]),b[1]+y0/im.height*(b[3]-b[1]),b[0]+x1/im.width*(b[2]-b[0]),b[1]+y1/im.height*(b[3]-b[1])];assets[name]={**parent,'name':name,'bounds':bounds,'originalSize':list(crop.size),'sourceComposite':key,'sourceRowId':ident,'sourceMethod':'Native source composite separated by connected product silhouettes, matched to printed instrument rows; original composite preserved'}
    records.append({'sourceComposite':key,'pdfPage':n,'printedRows':list(owned),'parts':len(owned)})
(F/'source-images.json').write_text(json.dumps(assets,indent=2)+'\n');(F/'split-composites.json').write_text(json.dumps(records,indent=2)+'\n');print('Refined',records,'native photos',len(assets))
