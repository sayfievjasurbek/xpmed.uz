import json,pathlib,sys,os,time
from PIL import Image,ImageChops
import numpy as np
from rembg import new_session,remove
records=json.load(open('/tmp/conmed-surgical/assets.json'));folder=pathlib.Path('public/images/products/conmed/advanced-surgical');manifest=folder/'prepared-assets.json';done=json.loads(manifest.read_text())if manifest.exists()else{};session=new_session('u2net',providers=['CPUExecutionProvider'])
for r in records:
 name=r['name'];output=pathlib.Path('/tmp/conmed-surgical/esrgan-output')/(name+'.png')
 if name in done or not output.exists():continue
 try:sr=Image.open(output);sr.load()
 except Exception:continue
 original=Image.open(folder/'_originals'/(name+'.png'));size=(original.width*2,original.height*2);sr=sr.convert('RGB').resize(size,Image.Resampling.LANCZOS);sr.save(folder/'_originals'/(name+'-upscaled-2x.png'));cut=remove(sr,session=session).convert('RGBA');rgb=np.asarray(sr);ink=np.clip((246-rgb.min(axis=2).astype(float))*6,0,255).astype('uint8');alpha=ImageChops.lighter(cut.getchannel('A'),Image.fromarray(ink))
 if original.mode=='RGBA':alpha=ImageChops.multiply(alpha,original.getchannel('A').resize(size,Image.Resampling.LANCZOS))
 cut=sr.convert('RGBA');cut.putalpha(alpha);bbox=alpha.getbbox()
 if bbox:cut=cut.crop(bbox)
 if r.get('rotateAfterUpscale'):cut=cut.rotate(-r['rotateAfterUpscale'],expand=True,resample=Image.Resampling.BICUBIC)
 padded=Image.new('RGBA',(cut.width+64,cut.height+64));padded.alpha_composite(cut,(32,32));padded.save(folder/(name+'.png'));padded.save(folder/(name+'.webp'),lossless=True,method=4)
 done[name]={**r,'src':'/images/products/conmed/advanced-surgical/'+name+'.webp','width':padded.width,'height':padded.height,'imageType':'cutout','captionFree':True,'imageEnhancement':{'method':'Real-ESRGAN x4plus then exact 2x resize, followed by rembg','scale':2,'originalSize':list(original.size),'enhancedSize':list(size)},'originals':'_originals'};manifest.write_text(json.dumps(done,indent=2));print('CUTOUT',name,flush=True)
print('Prepared',len(done),'of',len(records),flush=True)
