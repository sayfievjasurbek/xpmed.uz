"""Caption-free instrument row composites, Real-ESRGAN 2x, then rembg.
Render the PDF artwork as a composite so masked fragments never become separate products.
"""
import json,hashlib,subprocess,os
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'public/images/products/double-medical/spine-instruments';F=R/'reports/double-medical/spine-catalogue-instruments';W=Path('/tmp/xpmed-spine-instruments/assets');D=f.open(R/'catalogs-source/double-medical/spine-catalogue.pdf')
for p in [O/'_originals',F,W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
assets={};hashes={};empty=[]
for n in range(210,412):
 p=D[n-1];width,height=p.rect.width,p.rect.height;lines=[]
 for a in p.get_drawings():
  b=a['rect']
  if b.height<1 and .08<b.x0/width<.3 and .4<b.x1/width<.57 and .13<b.y0/height<.92:lines.append(b.y0/height)
 ys=[]
 for y in sorted(lines):
  if not ys or y-ys[-1]>.008:ys.append(y)
 if not ys:empty.append(n);continue
 for i,top in enumerate(ys):
  bottom=ys[i+1]if i+1<len(ys)else .925;clip=f.Rect(width*.557,height*(top+.001),width*.92,height*(bottom-.001));pix=p.get_pixmap(dpi=150,clip=clip,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);arr=np.array(im);mask=arr.min(axis=2)<238;yy,xx=np.where(mask)
  if len(xx)<10:continue
  box=(max(0,int(xx.min())-3),max(0,int(yy.min())-3),min(im.width,int(xx.max())+4),min(im.height,int(yy.max())+4));im=im.crop(box);digest=hashlib.sha256(im.tobytes()).hexdigest();name=hashes.get(digest,f'page-{n:03}-row-{i+1:02}');hashes[digest]=name
  if name not in assets:
   im.save(O/'_originals'/(name+'.png'));im.save(W/'input'/(name+'.png'));assets[name]={'name':name,'originalSize':list(im.size),'captionFree':True,'sourceMethod':'Original PDF row artwork composite at native effective 150 DPI; text captions excluded','placements':[]}
  assets[name]['placements'].append({'pdfPage':n,'printedPage':n-2,'sourceRow':i+1,'bounds':[.557,top,.92,bottom]})
(F/'source-images.json').write_text(json.dumps(assets,indent=2));(F/'image-line-detection-empty-pages.json').write_text(json.dumps(empty));print('Source row images',len(assets),'placements',sum(len(a['placements'])for a in assets.values()),'pages without row lines',empty,flush=True)
pending=W/'pending';pending.mkdir(exist_ok=True)
for sourcefile in(W/'input').glob('*.png'):
 target=W/'output'/sourcefile.name
 try:
  with Image.open(target)as check:check.verify()
  continue
 except Exception:pass
 link=pending/sourcefile.name
 if not link.exists():link.symlink_to(sourcefile)
print('Unfinished GPU images',len(list(pending.glob('*.png'))),flush=True)
if list(pending.glob('*.png')):
 with(W/'upscale-resume.log').open('w')as log:subprocess.run(['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(pending),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','256','-f','png'],stdout=log,stderr=subprocess.STDOUT,check=True)

from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider']);done={};fallback=[]
for name,a in assets.items():
 size=tuple(x*2 for x in a['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-2x.png'));out=remove(im,session=session).convert('RGBA');rgb=np.array(im);alpha=ImageChops.lighter(out.getchannel('A'),Image.fromarray(np.clip((246-rgb.min(axis=2).astype(float))*12,0,255).astype('uint8')));out=im.convert('RGBA');out.putalpha(alpha);box=alpha.point(lambda p:255 if p>100 else 0).getbbox()
 if not box:out=im.convert('RGBA');kind='scene';fallback.append(name)
 else:
  out=out.crop(alpha.getbbox());canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;kind='cutout'
 out.save(O/(name+'.png'));out.save(O/(name+'.webp'),lossless=True);done[name]={**a,'src':'/images/products/double-medical/spine-instruments/'+name+'.webp','width':out.width,'height':out.height,'imageType':kind,'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)}};(O/'prepared-assets.json').write_text(json.dumps(done,indent=2));(W/'output'/(name+'.png')).unlink();print('Prepared',len(done),'/',len(assets),name,flush=True)
(F/'image-fallbacks.json').write_text(json.dumps(fallback,indent=2))
