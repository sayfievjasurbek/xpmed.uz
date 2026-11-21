"""Reassemble embedded artwork only, excluding outlined captions before cropping.
Remove outlined captions in a temporary PDF and retain native image masks/transforms.
Connected artwork is assigned to the nearest source instrument row, not cut at row rules.
"""
import json,hashlib,collections,re
from pathlib import Path
import pymupdf as f
import numpy as np,cv2
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'public/images/products/double-medical/spine-instruments';F=R/'reports/double-medical/spine-catalogue-instruments';W=Path('/tmp/xpmed-spine-instruments/artwork');D=f.open(R/'catalogs-source/double-medical/spine-catalogue.pdf');rows=json.loads((F/'rows-translated.json').read_text());assets={};absent=[]
for p in [A/'_originals',W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
for n in range(210,412):
 page=D[n-1];pr=[r for r in rows if r['pdfPage']==n];native=[max(a['width']/(a['bbox'][2]-a['bbox'][0]),a['height']/(a['bbox'][3]-a['bbox'][1]))*72 for a in page.get_image_info()if a['bbox'][1]>.09*page.rect.height and a['bbox'][3]<.95*page.rect.height];dpi=min(600,max(150,int(max(native,default=150)+.999)));artdoc=f.open();artdoc.insert_pdf(D,from_page=n-1,to_page=n-1);artpage=artdoc[0];artpage.clean_contents();streams=set(artpage.get_contents())|{i for i in range(1,artdoc.xref_length())if artdoc.xref_get_key(i,'Subtype')==('name','/Form')}
 for xref in streams:
  data=artdoc.xref_stream(xref)
  if data:artdoc.update_stream(xref,re.sub(rb'(?<![A-Za-z0-9/])(?:f\*?|S|s|B\*?|b\*?)(?=[^A-Za-z0-9]|$)',b'n',data))
 pix=artpage.get_pixmap(dpi=dpi,alpha=False);arr=np.array(Image.frombytes('RGB',(pix.width,pix.height),pix.samples));h,w=arr.shape[:2];mask=(arr.min(axis=2)<244).astype('uint8');artdoc.close();mask[:int(.095*h)]=0;mask[int(.935*h):]=0;mask[:,:int(.1*w)]=0;mask[:,int(.94*w):]=0
 count,labels,stats,centroids=cv2.connectedComponentsWithStats(cv2.dilate(mask,np.ones((3,3),np.uint8)),8);owned=collections.defaultdict(list)
 for lab in range(1,count):
  x,y,bw,bh,area=stats[lab]
  if area<5:continue
  cy=(y+bh/2)/h
  row=min(pr,key=lambda r:abs(cy-(r['cy']+.015)))
  owned[row['id']].append(lab)
 # When every row has one connected photo, source order is authoritative and
 # avoids sending a tall handle to the following caption's baseline.
 major=[lab for lab in range(1,count)if stats[lab][4]>=20]
 if len(major)==len(pr):
  order=sorted(major,key=lambda lab:centroids[lab][1]);owned=collections.defaultdict(list)
  for r,lab in zip(pr,order):owned[r['id']].append(lab)
  for lab in range(1,count):
   if lab in major or stats[lab][4]<5:continue
   best=min(major,key=lambda main:sum((centroids[main][i]-centroids[lab][i])**2 for i in [0,1]));owned[pr[order.index(best)]['id']].append(lab)
 if n==226:
  # The source long drill guide spans a second caption's baseline.
  for key in list(owned):
   for lab in list(owned[key]):
    x,y,bw,bh,area=stats[lab]
    if y/h<.2 and bh/h>.15:owned[key].remove(lab);owned['226-01'].append(lab)
 for r in pr:
  selected=owned[r['id']]
  if not selected:absent.append(r['id']);continue
  m=np.isin(labels,selected)&(mask>0);yy,xx=np.where(m)
  if len(xx)<10:absent.append(r['id']);continue
  x0,y0,x1,y1=max(0,int(xx.min())-2),max(0,int(yy.min())-2),min(w,int(xx.max())+3),min(h,int(yy.max())+3)
  picture=arr[y0:y1,x0:x1].copy();keep=np.isin(labels[y0:y1,x0:x1],selected);picture[~keep]=255;image=Image.fromarray(picture);name='art-'+r['id'];image.save(A/'_originals'/(name+'.png'));image.save(W/'input'/(name+'.png'));assets[name]={'name':name,'originalSize':list(image.size),'captionFree':True,'sourceMethod':'Native PDF raster artwork with original masks/transforms; outlined captions removed from a temporary document before rendering; source untouched','placements':[{'pdfPage':n,'printedPage':n-2,'sourceRowId':r['id'],'bounds':[x0/w,y0/h,x1/w,y1/h]}]}
 print(n,len(assets),flush=True)
(F/'artwork-images.json').write_text(json.dumps(assets,indent=2));(F/'artwork-absent-source-images.json').write_text(json.dumps(absent,indent=2));print('Artwork',len(assets),'without source image',len(absent))
