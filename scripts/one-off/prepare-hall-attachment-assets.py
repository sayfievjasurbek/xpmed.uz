"""Five visible attachment photos rejected by the initial QR prefilter."""
import pymupdf as f,json,io,subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];D=f.open(R/'catalogs-source/conmed/hall-powered-instruments.pdf');O=R/'public/images/products/conmed/hall';W=Path('/tmp/conmed-hall/attachment-assets');(W/'input').mkdir(parents=True,exist_ok=True);(W/'output').mkdir(exist_ok=True);meta=[]
for n,x in [(13,195),(13,198),(13,199),(13,201),(13,229)]:
 name=f'page-{n:03}-xref-{x}';a=next(a for a in D[n-1].get_image_info(xrefs=True)if a['xref']==x);im=Image.open(io.BytesIO(D.extract_image(x)['image'])).convert('RGBA');im.save(O/'_originals'/(name+'.png'));kind,ref=D.xref_get_key(x,'SMask');mask=None
 if kind=='xref':mask=Image.open(io.BytesIO(D.extract_image(int(ref.split()[0]))['image'])).convert('L');im.putalpha(mask);mask.save(O/'_originals'/(name+'-source-alpha.png'))
 bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.getchannel('A'));bg.save(W/'input'/(name+'.png'));meta.append((n,x,name,im.size,a['bbox'],mask))
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png']
with (W/'upscale.log').open('w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider']);assets=json.loads((O/'prepared-assets.json').read_text())
for n,x,name,size,b,mask in meta:
 enhanced=Image.open(W/'output'/(name+'.png')).convert('RGB').resize((size[0]*2,size[1]*2),Image.Resampling.LANCZOS);enhanced.save(O/'_originals'/(name+'-upscaled-2x.png'));out=remove(enhanced,session=session).convert('RGBA')
 if mask is not None:out=enhanced.convert('RGBA');out.putalpha(mask.resize(out.size,Image.Resampling.LANCZOS))
 # Case photograph remains intact on white; its perforations are product structure.
 if n==76:out=enhanced.convert('RGBA');kind='scene'
 else:out=out.crop(out.getchannel('A').getbbox());kind='cutout'
 canvas=Image.new('RGBA',(out.width+64,out.height+64),(255,255,255,255)if kind=='scene'else(0,0,0,0));canvas.alpha_composite(out,(32,32));canvas.save(O/(name+'.png'));canvas.save(O/(name+'.webp'),lossless=True);p=D[n-1];assets[name]={'name':name,'src':'/images/products/conmed/hall/'+name+'.webp','width':canvas.width,'height':canvas.height,'imageType':kind,'pdfPage':n,'pdfImageXref':x,'bounds':[b[0]/p.rect.width,b[1]/p.rect.height,b[2]/p.rect.width,b[3]/p.rect.height],'captionFree':True,'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':list(size),'enhancedSize':[v*2 for v in size]}}
(O/'prepared-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2));print('Added source attachment photos')
