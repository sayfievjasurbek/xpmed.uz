#!/usr/bin/env python3
import json,os
from pathlib import Path
from PIL import Image,ImageChops
from rembg import new_session,remove
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'public/images/products/double-medical/angel-shoulder-system';items=json.loads((out/'source-assets.json').read_text());session=new_session('u2net',providers=['CPUExecutionProvider']);assets=[]
for item in items:
 name=item['name'];original=Image.open(out/'_originals'/(name+'.png')).convert('RGBA');scale=item['scale'];size=(original.width*scale,original.height*scale)
 if scale==2:im=Image.open('/tmp/angel-assets/output/'+name+'.png').convert('RGBA').resize(size,Image.Resampling.LANCZOS)
 else:im=original.copy()
 alpha=original.getchannel('A').resize(size,Image.Resampling.LANCZOS)
 # Run rembg, then preserve the manufacturer's authoritative alpha, including white liners.
 bg=Image.new('RGBA',size,'white');bg.alpha_composite(im);candidate=remove(bg,session=session).convert('RGBA');candidate.save(out/'_originals'/(name+'-rembg-candidate.png'))
 if item.get('manufacturerAlpha'):im.putalpha(alpha);mask_method='Manufacturer alpha retained after rembg comparison; prevents loss of white polymer and fine screws'
 else:im=candidate;mask_method='rembg'
 bbox=im.getchannel('A').getbbox()
 if bbox:im=im.crop(bbox)
 padded=Image.new('RGBA',(im.width+64,im.height+64));padded.alpha_composite(im,(32,32));padded.save(out/(name+'.png'));padded.save(out/(name+'.webp'),'WEBP',lossless=True,method=6)
 assets.append({**item,'src':'/images/products/double-medical/angel-shoulder-system/'+name+'.webp','width':padded.width,'height':padded.height,'imageType':'cutout','captionFree':True,'maskMethod':mask_method,'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exactly 2x'if scale==2 else'Original native embedded image','scale':scale,'originalSize':item['nativeSize'],'enhancedSize':list(size)}})
 print(name,flush=True)
(out/'prepared-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
