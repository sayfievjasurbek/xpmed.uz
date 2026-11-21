#!/usr/bin/env python3
import json,sys,hashlib,io,math
from pathlib import Path
import pymupdf as fitz
from PIL import Image
import numpy as np,cv2
qr_detector=cv2.QRCodeDetector()
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from pdf_product_images import extract_product_photo
F=R/'reports/conmed/arthroscopy-product-catalog';D=fitz.open(R/'catalogs-source/conmed/arthroscopy-product-catalog.pdf');out=R/'public/images/products/conmed/arthroscopy';orig=out/'_originals';orig.mkdir(parents=True,exist_ok=True);work=Path('/tmp/conmed-arthroscopy/assets');(work/'input').mkdir(parents=True,exist_ok=True);(work/'output').mkdir(exist_ok=True);records=[];seen={};qrs=[]
for path in sorted((F/'layout').glob('*.json')):
 n=int(path.stem);page=D[n-1];pw,ph=page.rect.width,page.rect.height;photos=[]
 for info in page.get_image_info(xrefs=True):
  xref=info['xref'];b=info['bbox'];box=[b[0]/pw,b[1]/ph,b[2]/pw,b[3]/ph]
  if not xref or box[1]<.085 or (box[1]+box[3])/2>.92 or info['width']<40 or info['height']<40:continue
  blob=D.extract_image(xref);raw=Image.open(io.BytesIO(blob['image'])).convert('RGB');a=np.asarray(raw);extreme=((a.min(axis=2)>232)|(a.max(axis=2)<35)).mean()
  qr_url,qr_points,_=qr_detector.detectAndDecode(a) if .65<raw.width/raw.height<1.5 else ('',None,None)
  qr_texture=.65<raw.width/raw.height<1.5 and (a.max(2)<65).mean()>.3 and (a.min(2)>215).mean()>.2
  if qr_url or qr_points is not None or qr_texture:
   qrs.append({'pdfPage':n,'xref':xref,'sourceBounds':box,'url':qr_url});continue
  if xref in seen:
   asset=seen[xref];asset['sourcePages'].append(n);photos.append(asset['name']);continue
  result=extract_product_photo(R/'catalogs-source/conmed/arthroscopy-product-catalog.pdf',n,box)
  if not result:continue
  im,meta=result
  # Keep native pixels. Rotation is applied after SR to avoid enlarging the inference canvas.
  angle=meta['sourceRotation']
  if abs(angle)>1:
   im=raw.convert('RGBA')
   if blob.get('smask'):im.putalpha(Image.open(io.BytesIO(D.extract_image(blob['smask'])['image'])).convert('L').resize(im.size,Image.Resampling.LANCZOS))
  else:im=im.convert('RGBA')
  name=f'page-{n:03}-xref-{xref}';im.save(orig/(name+'.png'));bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);bg.convert('RGB').save(work/'input'/(name+'.png'))
  asset={'name':name,'pdfPage':n,'sourcePages':[n],'sourceBounds':box,'originalSize':list(im.size),**meta};records.append(asset);seen[xref]=asset;photos.append(name)
print('Native photos',len(records),'QRs',len(qrs));(F/'source-images.json').write_text(json.dumps({'images':records,'qrs':qrs},indent=2)+'\n')
