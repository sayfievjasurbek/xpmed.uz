"""Native Joint Catalogue photos, exact Real-ESRGAN 2x, source masks and rembg."""
import json,io,hashlib,subprocess,os
from pathlib import Path
import pymupdf as f
import numpy as np
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/joint-catalogue';O=R/'public/images/products/double-medical/joint-catalogue';W=Path('/tmp/dm-joint/assets');D=f.open(R/'catalogs-source/double-medical/joint-catalogue.pdf')
for p in [O/'_originals',W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
assets={};hashes={};skipped=[]
for n,p in enumerate(D,1):
 if n in [1,2,3,96]:continue
 for a in p.get_image_info(xrefs=True):
  x=a['xref'];b=a['bbox']
  if not x or min(a['width'],a['height'])<20:continue
  pix=f.Pixmap(D,x)
  if pix.colorspace.n!=3:pix=f.Pixmap(f.csRGB,pix)
  kind,ref=D.xref_get_key(x,'SMask');mask=f.Pixmap(D,int(ref.split()[0]))if kind=='xref'else None
  if mask:pix=f.Pixmap(pix,mask)
  im=Image.frombytes('RGBA'if pix.alpha else'RGB',(pix.width,pix.height),pix.samples).convert('RGBA');ab=im.getchannel('A').getbbox()or(0,0,im.width,im.height);visibleTop=b[1]+(b[3]-b[1])*ab[1]/im.height
  if visibleTop<p.rect.height*.12:continue
  rgb=np.asarray(im.convert('RGB'));ratio=im.width/im.height;binary=((rgb.min(axis=2)<40)|(rgb.min(axis=2)>235)).mean();neutral=(rgb.max(axis=2).astype(int)-rgb.min(axis=2)<12).mean()
  if not mask and .7<ratio<1.35 and binary>.94 and neutral>.98:
   skipped.append({'pdfPage':n,'xref':x,'reason':'Binary square QR graphic'});continue
  digest=hashlib.sha256(im.tobytes()).hexdigest();name=hashes.get(digest,f'page-{n:03}-xref-{x}');hashes[digest]=name
  if name not in assets:
   im.save(O/'_originals'/(name+'.png'));bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.getchannel('A'));bg.save(W/'input'/(name+'.png'))
   if mask:im.getchannel('A').save(O/'_originals'/(name+'-source-alpha.png'))
   assets[name]={'name':name,'originalSize':list(im.size),'sourceMask':bool(mask),'placements':[]}
  assets[name]['placements'].append({'pdfPage':n,'pdfImageXref':x,'bounds':[b[0]/p.rect.width,b[1]/p.rect.height,b[2]/p.rect.width,b[3]/p.rect.height]})
(F/'source-images.json').write_text(json.dumps(assets,indent=2));(F/'skipped-qr-images.json').write_text(json.dumps(skipped,indent=2));print('Unique photos',len(assets),'QRs skipped',len(skipped),flush=True)
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','256','-f','png']
with (W/'upscale.log').open('w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider']);done={};fallback=[]
for name,a in assets.items():
 size=tuple(v*2 for v in a['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-upscaled-2x.png'));out=remove(im,session=session).convert('RGBA')
 if a['sourceMask']:out=im.convert('RGBA');out.putalpha(Image.open(O/'_originals'/(name+'-source-alpha.png')).resize(size,Image.Resampling.LANCZOS))
 else:
  rgb=np.asarray(im);corners=np.concatenate([rgb[:6,:6].reshape(-1,3),rgb[-6:,-6:].reshape(-1,3)]);bg=np.median(corners.min(axis=1));alpha=out.getchannel('A')
  if bg>242:alpha=ImageChops.lighter(alpha,Image.fromarray(np.clip((bg-12-rgb.min(axis=2).astype(float))*10,0,255).astype('uint8')));out=im.convert('RGBA');out.putalpha(alpha)
 box=out.getchannel('A').point(lambda v:255 if v>100 else 0).getbbox();bad=not box or(not a['sourceMask'] and box[2]-box[0]<im.width*.45 and box[3]-box[1]<im.height*.6)
 if bad:out=im.convert('RGBA');imageType='scene';fallback.append(name)
 else:out=out.crop(out.getchannel('A').getbbox());canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;imageType='cutout'
 out.save(O/(name+'.png'));out.save(O/(name+'.webp'),lossless=True);done[name]={**a,'src':'/images/products/double-medical/joint-catalogue/'+name+'.webp','width':out.width,'height':out.height,'imageType':imageType,'captionFree':True,'imageEnhancement':{'method':'Real-ESRGAN x4plus, downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)}};(O/'prepared-assets.json').write_text(json.dumps(done,indent=2));(W/'output'/(name+'.png')).unlink();print('Prepared',name,imageType,flush=True)
(F/'image-fallbacks.json').write_text(json.dumps(fallback,indent=2));print('Complete',len(done),flush=True)
