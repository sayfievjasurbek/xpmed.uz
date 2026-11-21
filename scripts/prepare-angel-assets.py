#!/usr/bin/env python3
"""Extract manufacturer-alpha photos and label-free components at native resolution."""
import json,sys
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageChops
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'public/images/products/double-medical/angel-shoulder-system';originals=out/'_originals';originals.mkdir(parents=True,exist_ok=True)
work=Path('/tmp/angel-assets');(work/'input').mkdir(parents=True,exist_ok=True);(work/'output').mkdir(exist_ok=True)
doc=fitz.open(ROOT/'catalogs-source/double-medical/angel-shoulder-system.pdf');items=[]
names={57:'exploded-fracture',65:'exploded-modular',67:'modular-stem',74:'fracture-stem-rear',76:'fracture-stem-front',78:'feature-fracture-01',80:'feature-fracture-04',82:'feature-fracture-02',84:'feature-fracture-03',89:'reverse-liner-assembly',91:'glenoid-baseplate-screws',96:'anatomic-assembly',98:'anatomic-glenoid-options',103:'feature-anatomic-angle',105:'feature-anatomic-offset',110:'cemented-stem',115:'configuration-03',117:'configuration-01',119:'configuration-02',124:'configuration-04',126:'configuration-05',128:'configuration-06'}
def add(name,im,page,meta):
 im=im.convert('RGBA');im.save(originals/(name+'.png'));scale=2 if max(im.size)<1800 else 1
 if scale==2:
  bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);bg.convert('RGB').save(work/'input'/(name+'.png'))
 items.append({'name':name,'pdfPage':page,'nativeSize':list(im.size),'scale':scale,**meta})
for number,page in enumerate(doc,1):
 for info in page.get_images(full=True):
  x,sm=info[:2]
  if x not in names:continue
  pix=fitz.Pixmap(doc,x)
  if pix.colorspace.n!=3:pix=fitz.Pixmap(fitz.csRGB,pix)
  if sm:pix=fitz.Pixmap(pix,fitz.Pixmap(doc,sm))
  im=Image.frombytes('RGBA'if pix.alpha else'RGB',(pix.width,pix.height),pix.samples)
  bbox=page.get_image_rects(x)[0];bounds=[bbox.x0/page.rect.width,bbox.y0/page.rect.height,bbox.x1/page.rect.width,bbox.y1/page.rect.height]
  add(names[x],im,number,{'pdfImageXref':x,'sourceBounds':bounds,'manufacturerAlpha':bool(sm)})
# Connected manufacturer-alpha islands keep every actual part, without printed labels.
im=Image.open(originals/'exploded-fracture.png').convert('RGBA');n,labels,stats,centroids=cv2.connectedComponentsWithStats((np.asarray(im.getchannel('A'))>10).astype('uint8'))
partnames=['glenoid-compression-screw','locking-cap','glenoid-baseplate','central-screw','glenosphere','humeral-liner','augmented-glenoid','humeral-adapter-tray','humeral-head','pegged-glenoid','fracture-stem','keeled-glenoid'];index=0
for label,(x,y,w,h,area) in enumerate(stats[1:],1):
 if area<400:continue
 part=im.copy();part.putalpha(ImageChops.multiply(im.getchannel('A'),Image.fromarray(np.where(labels==label,255,0).astype('uint8'))));part=part.crop((x,y,x+w,y+h));add('component-'+partnames[index],part,3,{'manufacturerAlpha':True,'sourceImage':'exploded-fracture','pixelBounds':[int(x),int(y),int(x+w),int(y+h)]});index+=1
(out/'source-assets.json').write_text(json.dumps(items,indent=2)+'\n');print(f'{len(items)} assets; {sum(x["scale"]==2 for x in items)} enhancement inputs')
