#!/usr/bin/env python3
import json,sys,math
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
from rembg import remove,new_session
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/arthroscopy-product-catalog';out=R/'public/images/products/conmed/arthroscopy';meta=json.loads((F/'source-images.json').read_text());target=out/'prepared-assets.json';done=json.loads(target.read_text())if target.exists()else{};done={k:v for k,v in done.items()if k in {a['name']for a in meta['images']}};session=new_session('u2net',providers=['CPUExecutionProvider'])
for record in meta['images']:
 name=record['name'];src=Path('/tmp/conmed-arthroscopy/assets/output')/(name+'.png')
 if name in done or not src.exists():continue
 try:im=Image.open(src);im.load()
 except Exception:continue
 original=Image.open(out/'_originals'/(name+'.png')).convert('RGBA');size=(original.width*2,original.height*2);im=im.convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(out/'_originals'/(name+'-upscaled-2x.png'));candidate=remove(im,session=session).convert('RGBA');rgb=np.asarray(im);ink=Image.fromarray(np.clip((247-rgb.min(axis=2).astype(float))*6,0,255).astype('uint8'));alpha=ImageChops.lighter(candidate.getchannel('A'),ink)
 if record.get('pdfAlphaMask'):alpha=ImageChops.multiply(alpha,original.getchannel('A').resize(size,Image.Resampling.LANCZOS))
 im=im.convert('RGBA');im.putalpha(alpha);bbox=alpha.getbbox()
 if bbox:im=im.crop(bbox)
 angle=record.get('sourceRotation',0)
 if abs(angle)>1:im=im.rotate(-angle,expand=True,resample=Image.Resampling.BICUBIC)
 padded=Image.new('RGBA',(im.width+64,im.height+64));padded.alpha_composite(im,(32,32));padded.save(out/(name+'.webp'),'WEBP',lossless=True,method=4)
 done[name]={**record,'src':'/images/products/conmed/arthroscopy/'+name+'.webp','width':padded.width,'height':padded.height,'imageType':'cutout','captionFree':True,'maskMethod':'rembg combined with source ink and manufacturer alpha where available','imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exactly 2x before rembg','scale':2,'originalSize':record['originalSize'],'enhancedSize':list(size)}};target.write_text(json.dumps(done,indent=2)+'\n');print('ASSET',name,flush=True)
 # Only the disposable x4 inference output is removed; originals and exact 2x remain.
 src.unlink()
print('Prepared',len(done),'of',len(meta['images']),flush=True)
