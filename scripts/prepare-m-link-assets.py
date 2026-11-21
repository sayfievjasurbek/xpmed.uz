"""Keep surgical illustrations intact; enhance and cut out only device photographs."""
import json,os,subprocess
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'public/images/products/double-medical/m-link-all-inside';W=Path('/tmp/m-link/assets');D=f.open(R/'catalogs-source/double-medical/m-link-all-inside.pdf');assets=[]
for d in [W/'input',W/'output',P/'technique',P/'_originals/technique']:d.mkdir(parents=True,exist_ok=True)
# Main illustration rectangles include their original inset diagrams, labels and circle borders.
regions={1:[(5,[.575,.217,.915,.417])],3:[(5,[.563,.699,.914,.905])],4:[(6,[.523,.223,.893,.441]),(6,[.523,.468,.893,.686])],5:[(7,[.545,.190,.915,.408]),(7,[.575,.434,.945,.652])],6:[(8,[.524,.190,.894,.408]),(8,[.524,.434,.894,.652])],7:[(9,[.545,.190,.915,.408]),(9,[.545,.434,.915,.652]),(9,[.545,.679,.915,.897])],8:[(10,[.524,.190,.894,.408]),(10,[.524,.434,.894,.652]),(10,[.478,.652,.894,.897])]}
for step,figures in regions.items():
 for i,(n,b)in enumerate(figures,1):
  page=D[n-1];box=f.Rect(b[0]*page.rect.width,b[1]*page.rect.height,b[2]*page.rect.width,b[3]*page.rect.height);pix=page.get_pixmap(matrix=f.Matrix(600/72,600/72),clip=box,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);name=f'step-{step:02}-{i:02}';im.save(P/'_originals/technique'/(name+'.png'));im.save(P/'technique'/(name+'.webp'),quality=94,method=6);assets.append({'src':'/images/products/double-medical/m-link-all-inside/technique/'+name+'.webp','width':im.width,'height':im.height,'imageType':'scene','step':step,'pdfPage':n,'sourceBounds':b,'sourceMethod':'600-DPI source illustration crop; original inset diagrams retained; no rembg'})
originals=json.loads((P/'original-assets.json').read_text())
for a in originals:
 im=Image.open(P/'_originals'/(a['name']+'.png')).convert('RGBA');bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.getchannel('A'));bg.save(W/'input'/(a['name']+'.png'))
with(W/'upscale.log').open('w')as log:subprocess.run(['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','256','-f','png'],stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider'])
for a in originals:
 size=tuple(x*2 for x in a['nativeSize']);im=Image.open(W/'output'/(a['name']+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(P/'_originals'/(a['name']+'-upscaled-2x.png'));cut=remove(im,session=session).convert('RGBA')
 if a['sourceMask']:
  cut=im.convert('RGBA');cut.putalpha(Image.open(P/'_originals'/(a['name']+'.png')).getchannel('A').resize(size,Image.Resampling.LANCZOS))
 else:
  rgb=np.array(im);cut.putalpha(ImageChops.lighter(cut.getchannel('A'),Image.fromarray(np.clip((248-rgb.min(axis=2).astype(float))*20,0,255).astype('uint8'))))
 box=cut.getchannel('A').getbbox();assert box,a['name'];cut=cut.crop(box);canvas=Image.new('RGBA',(cut.width+64,cut.height+64));canvas.alpha_composite(cut,(32,32));canvas.save(P/(a['name']+'.png'));canvas.save(P/(a['name']+'.webp'),lossless=True);assets.append({**a,'src':'/images/products/double-medical/m-link-all-inside/'+a['name']+'.webp','width':canvas.width,'height':canvas.height,'imageType':'cutout','imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':a['nativeSize'],'enhancedSize':list(size)}})
(P/'prepared-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2));print('Prepared',len(assets),'assets; technique illustrations untouched by rembg',flush=True)
