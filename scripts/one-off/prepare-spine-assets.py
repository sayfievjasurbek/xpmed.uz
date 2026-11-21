"""Native implant artwork only (printed pages 2–207); Real-ESRGAN 2x before rembg."""
import json,hashlib,subprocess,math
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue';O=R/'public/images/products/double-medical/spine-catalogue';W=Path('/tmp/xpmed-spine/assets');D=f.open(R/'catalogs-source/double-medical/spine-catalogue.pdf')
for p in [O/'_originals',W/'input',W/'output',F]:p.mkdir(parents=True,exist_ok=True)
assets={};hashes={}
for n in range(4,210):
 p=D[n-1]
 for a in p.get_image_info(xrefs=True):
  x=a['xref'];b=a['bbox']
  if not x or min(a['width'],a['height'])<20 or b[1]/p.rect.height<.10 or b[1]/p.rect.height>.84:continue
  pix=f.Pixmap(D,x)
  if pix.colorspace.n!=3:pix=f.Pixmap(f.csRGB,pix)
  kind,ref=D.xref_get_key(x,'SMask');mask=f.Pixmap(D,int(ref.split()[0]))if kind=='xref'else None
  im=Image.frombytes('RGBA'if pix.alpha else'RGB',(pix.width,pix.height),pix.samples).convert('RGBA')
  if mask:im.putalpha(Image.frombytes('L',(mask.width,mask.height),mask.samples).resize(im.size,Image.Resampling.LANCZOS))
  angle=-round(math.degrees(math.atan2(a['transform'][1],a['transform'][0]))/90)*90
  im=im.rotate(angle,expand=True);digest=hashlib.sha256(im.tobytes()).hexdigest();name=hashes.get(digest,f'page-{n:03}-xref-{x}');hashes[digest]=name
  if name not in assets:
   im.save(O/'_originals'/(name+'.png'));bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.getchannel('A'));bg.save(W/'input'/(name+'.png'));assets[name]={'name':name,'originalSize':list(im.size),'sourceMask':bool(mask),'rotation':angle,'placements':[]}
   if mask:im.getchannel('A').save(O/'_originals'/(name+'-alpha.png'))
  assets[name]['placements'].append({'pdfPage':n,'printedPage':n-2,'xref':x,'bounds':[b[0]/p.rect.width,b[1]/p.rect.height,b[2]/p.rect.width,b[3]/p.rect.height]})
(F/'source-images.json').write_text(json.dumps(assets,indent=2));print('Native images',len(assets),flush=True)
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png']
with(W/'upscale.log').open('w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider']);done={};fallback=[]
for name,a in assets.items():
 size=tuple(v*2 for v in a['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-2x.png'));out=remove(im,session=session).convert('RGBA')
 if a['sourceMask']:out=im.convert('RGBA');out.putalpha(Image.open(O/'_originals'/(name+'-alpha.png')).resize(size,Image.Resampling.LANCZOS))
 else:
  rgb=np.asarray(im);bg=float(np.median(np.concatenate([rgb[:4,:4].min(axis=2).ravel(),rgb[-4:,-4:].min(axis=2).ravel()])))
  if bg>240:
   alpha=ImageChops.lighter(out.getchannel('A'),Image.fromarray(np.clip((bg-10-rgb.min(axis=2).astype(float))*12,0,255).astype('uint8')));out=im.convert('RGBA');out.putalpha(alpha)
 box=out.getchannel('A').point(lambda v:255 if v>100 else 0).getbbox();bad=not box or(box[2]-box[0]<im.width*.35 and box[3]-box[1]<im.height*.5)
 if bad:out=im.convert('RGBA');kind='scene';fallback.append(name)
 else:
  out=out.crop(out.getchannel('A').getbbox());canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;kind='cutout'
 out.save(O/(name+'.png'));out.save(O/(name+'.webp'),lossless=True);done[name]={**a,'src':'/images/products/double-medical/spine-catalogue/'+name+'.webp','width':out.width,'height':out.height,'imageType':kind,'captionFree':True,'imageEnhancement':{'method':'Real-ESRGAN x4plus; exact 2x downsample before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)}};(O/'prepared-assets.json').write_text(json.dumps(done,indent=2));(W/'output'/(name+'.png')).unlink();print('Prepared',name,kind,flush=True)
(F/'image-fallbacks.json').write_text(json.dumps(fallback,indent=2))
