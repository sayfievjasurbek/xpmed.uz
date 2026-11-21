"""HALL photo assets only. Blade drawings are rendered separately without rembg."""
import json,io,hashlib,subprocess,os
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np,cv2
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';W=Path('/tmp/conmed-hall/assets');O=R/'public/images/products/conmed/hall';(O/'_originals').mkdir(parents=True,exist_ok=True);(W/'input').mkdir(parents=True,exist_ok=True);(W/'output').mkdir(exist_ok=True)
D=f.open(R/'catalogs-source/conmed/hall-powered-instruments.pdf');meta=[];hashes={};qr=cv2.QRCodeDetector()
for n in list(range(8,15))+list(range(42,46))+[59,63,69,70,71,72,73,76,78]:
 p=D[n-1];w,h=p.rect.width,p.rect.height
 for info in p.get_image_info(xrefs=True):
  x=info['xref'];b=info['bbox'];bw=b[2]-b[0];bh=b[3]-b[1]
  if not x or min(info['width'],info['height'])<20 or b[1]<h*.10:continue
  blob=D.extract_image(x);im=Image.open(io.BytesIO(blob['image'])).convert('RGB')
  if b[1]>h*.73 and .65<bw/bh<1.4:continue
  try:
   if qr.detect(np.asarray(im))[0]:continue
  except Exception:pass
  digest=hashlib.sha256(im.tobytes()).hexdigest();name=hashes.get(digest,f'page-{n:03}-xref-{x}');hashes[digest]=name
  if not (W/'input'/(name+'.png')).exists():im.save(W/'input'/(name+'.png'));im.save(O/'_originals'/(name+'.png'))
  meta.append({'name':name,'pdfPage':n,'pdfImageXref':x,'bounds':[b[0]/w,b[1]/h,b[2]/w,b[3]/h],'originalSize':list(im.size)})
(F/'source-images.json').write_text(json.dumps(meta,indent=2));print('Source placements',len(meta),'unique photos',len(hashes),flush=True)
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png']
with (W/'upscale.log').open('w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import new_session,remove
session=new_session('u2net',providers=['CPUExecutionProvider']);done={};fallback=[]
for r in meta:
 name=r['name']
 if name in done:continue
 size=tuple(v*2 for v in r['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-upscaled-2x.png'));candidate=remove(im,session=session).convert('RGBA');rgb=np.asarray(im);alpha=candidate.getchannel('A');corners=np.concatenate([rgb[:8,:8].reshape(-1,3),rgb[-8:,-8:].reshape(-1,3),rgb[:8,-8:].reshape(-1,3),rgb[-8:,:8].reshape(-1,3)]);bg=np.median(corners.min(axis=1))
 if bg>240:alpha=ImageChops.lighter(alpha,Image.fromarray(np.clip((bg-10-rgb.min(axis=2).astype(float))*8,0,255).astype('uint8')))
 box=alpha.point(lambda v:255 if v>100 else 0).getbbox();bad=not box or(bg<240 and (box[2]-box[0])<im.width*.75)
 if bad:chosen=im.convert('RGBA');kind='scene';fallback.append({'src':name,'pdfPage':r['pdfPage'],'reason':'Mask would remove instrument parts; original photo retained'})
 else:
  im=im.convert('RGBA');im.putalpha(alpha);im=im.crop(alpha.getbbox());chosen=Image.new('RGBA',(im.width+64,im.height+64));chosen.alpha_composite(im,(32,32));kind='cutout'
 chosen.save(O/(name+'.png'));chosen.save(O/(name+'.webp'),lossless=True,method=4);done[name]={**r,'src':'/images/products/conmed/hall/'+name+'.webp','width':chosen.width,'height':chosen.height,'imageType':kind,'captionFree':True,'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':r['originalSize'],'enhancedSize':list(size)}};(O/'prepared-assets.json').write_text(json.dumps(done,indent=2));(W/'output'/(name+'.png')).unlink();print('PHOTO',name,kind,flush=True)
(F/'image-fallbacks.json').write_text(json.dumps(fallback,indent=2));print('Complete',len(done),flush=True)
