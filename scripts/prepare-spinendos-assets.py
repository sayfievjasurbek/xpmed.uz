"""Extract caption-free native photos; enhance exactly 2x before rembg."""
import json,io,subprocess,sys,os
from pathlib import Path
import pymupdf as fitz
from PIL import Image
R=Path(__file__).resolve().parents[1];F=R/'reports/spinendos/endoscopic-spine-surgery-system';W=Path('/tmp/spinendos');O=R/'public/images/products/spinendos/endoscopic-spine-surgery';(O/'_originals').mkdir(parents=True,exist_ok=True)
doc=fitz.open(R/'catalogs-source/spinendos/endoscopic-spine-surgery-system.pdf');records=[];seen=set()
for n in range(4,20):
 p=doc[n-1];w,h=p.rect.width,p.rect.height
 for info in p.get_image_info(xrefs=True):
  x=info['xref'];b=info['bbox'];key=(n,x)
  if not x or key in seen or info['width']<40 or info['height']<2 or b[3]<65 or b[1]>h*.95:continue
  seen.add(key);blob=doc.extract_image(x);im=Image.open(io.BytesIO(blob['image'])).convert('RGB');name=f'page-{n:03}-xref-{x}';im.save(O/'_originals'/(name+'.png'));im.save(W/'input'/(name+'.png'));records.append({'name':name,'pdfPage':n,'bounds':[b[0]/w,b[1]/h,b[2]/w,b[3]/h],'originalSize':list(im.size),'pdfImageXref':x})
(F/'source-images.json').write_text(json.dumps(records,indent=2));print('Photos:',len(records),flush=True)
# The supplied x4 model is downsampled to exact 2x, as in earlier imports.
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png']
with (W/'upscale.log').open('w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
import numpy as np
from PIL import ImageChops
session=new_session('u2net',providers=['CPUExecutionProvider']);done={}
for r in records:
 name=r['name'];size=tuple(v*2 for v in r['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-upscaled-2x.png'))
 candidate=remove(im,session=session).convert('RGBA');rgb=np.asarray(im);ink=Image.fromarray(np.clip((247-rgb.min(axis=2).astype(float))*6,0,255).astype('uint8'));alpha=ImageChops.lighter(candidate.getchannel('A'),ink);im=im.convert('RGBA');im.putalpha(alpha);box=alpha.getbbox()
 if box:im=im.crop(box)
 canvas=Image.new('RGBA',(im.width+64,im.height+64));canvas.alpha_composite(im,(32,32));canvas.save(O/(name+'.png'));canvas.save(O/(name+'.webp'),lossless=True,method=4)
 done[name]={**r,'src':'/images/products/spinendos/endoscopic-spine-surgery/'+name+'.webp','width':canvas.width,'height':canvas.height,'imageType':'cutout','captionFree':True,'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':r['originalSize'],'enhancedSize':list(size)}};(O/'prepared-assets.json').write_text(json.dumps(done,indent=2));print('Processed',name,flush=True)
print('Complete',len(done),flush=True)
