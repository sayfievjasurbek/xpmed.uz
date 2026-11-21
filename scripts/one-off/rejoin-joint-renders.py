"""Render PDF compositing correctly before enhancement for three split-mask images."""
import json,subprocess
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'public/images/products/double-medical/joint-catalogue';W=Path('/tmp/dm-joint/rejoined');D=f.open(R/'catalogs-source/double-medical/joint-catalogue.pdf');fix=json.loads((P/'corrected-assets.json').read_text());names=['cpt-cemented-stem-complete','bipolar-cup-front-complete','cynthia-tibial-tray-complete']
for d in [W/'input',W/'output']:d.mkdir(parents=True,exist_ok=True)
for name in names:
 a=fix[name];n=a['placements'][0]['pdfPage'];b=a['placements'][0]['bounds'];p=D[n-1];clip=f.Rect(b[0]*p.rect.width,b[1]*p.rect.height,b[2]*p.rect.width,b[3]*p.rect.height);pix=p.get_pixmap(matrix=f.Matrix(150/72,150/72),clip=clip,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(P/'_originals'/(name+'-composited.png'));im.save(W/'input'/(name+'.png'));a['originalSize']=list(im.size)
with(W/'log').open('w')as log:subprocess.run(['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','256','-f','png'],stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider'])
for name in names:
 a=fix[name];size=tuple(x*2 for x in a['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(P/'_originals'/(name+'-upscaled-2x.png'));out=remove(im,session=session).convert('RGBA');rgb=np.array(im);out.putalpha(ImageChops.lighter(out.getchannel('A'),Image.fromarray(np.clip((250-rgb.min(axis=2).astype(float))*20,0,255).astype('uint8'))));out=out.crop(out.getchannel('A').getbbox());canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));canvas.save(P/(name+'.webp'),lossless=True);canvas.save(P/(name+'.png'));a.update(width=canvas.width,height=canvas.height,imageEnhancement={'method':'PDF mask/blend compositing at 150 DPI, Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)})
(P/'corrected-assets.json').write_text(json.dumps(fix,indent=2));print('Rejoined and checked',len(names))
