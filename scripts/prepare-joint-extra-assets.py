"""Recover sparse alpha-masked photos incorrectly resembling binary QR graphics."""
import json,os,subprocess
from pathlib import Path
import pymupdf as f
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'public/images/products/double-medical/joint-catalogue';F=R/'reports/double-medical/joint-catalogue';W=Path('/tmp/dm-joint/extra');D=f.open(R/'catalogs-source/double-medical/joint-catalogue.pdf');out={}
for p in [W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
for x in json.loads((F/'skipped-qr-images.json').read_text()):
 n=x['pdfPage'];ref=x['xref'];p=f.Pixmap(D,ref)
 if p.colorspace.n!=3:p=f.Pixmap(f.csRGB,p)
 typ,mask=D.xref_get_key(ref,'SMask')
 if typ=='xref':p=f.Pixmap(p,f.Pixmap(D,int(mask.split()[0])))
 im=Image.frombytes('RGBA'if p.alpha else'RGB',(p.width,p.height),p.samples).convert('RGBA');name=f'page-{n:03}-xref-{ref}';im.save(O/'_originals'/(name+'.png'));box=im.getchannel('A').getbbox()or(0,0,im.width,im.height);cropped=im.crop(box);cropped.getchannel('A').save(W/(name+'-alpha.png'));bg=Image.new('RGB',cropped.size,'white');bg.paste(cropped,mask=cropped.getchannel('A'));bg.save(W/'input'/(name+'.png'));info=next(a for a in D[n-1].get_image_info(xrefs=True)if a['xref']==ref);b=info['bbox'];page=D[n-1];out[name]={'name':name,'originalSize':list(im.size),'sourceCrop':list(box),'cropSize':list(cropped.size),'sourceMask':typ=='xref','placements':[{'pdfPage':n,'pdfImageXref':ref,'bounds':[b[0]/page.rect.width,b[1]/page.rect.height,b[2]/page.rect.width,b[3]/page.rect.height]}]}
with(W/'upscale.log').open('w')as log:subprocess.run(['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','256','-f','png'],stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider'])
for name,a in out.items():
 size=tuple(v*2 for v in a['cropSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-upscaled-2x.png'));cut=remove(im,session=session).convert('RGBA')
 if a['sourceMask']:cut=im.convert('RGBA');cut.putalpha(Image.open(W/(name+'-alpha.png')).resize(size,Image.Resampling.LANCZOS))
 cut=cut.crop(cut.getchannel('A').getbbox());canvas=Image.new('RGBA',(cut.width+64,cut.height+64));canvas.alpha_composite(cut,(32,32));canvas.save(O/(name+'.webp'),lossless=True);canvas.save(O/(name+'.png'));a.update(src='/images/products/double-medical/joint-catalogue/'+name+'.webp',width=canvas.width,height=canvas.height,imageType='cutout',captionFree=True,imageEnhancement={'method':'Real-ESRGAN x4plus, downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)});print(name,flush=True)
(O/'extra-assets.json').write_text(json.dumps(out,indent=2));print('Recovered sparse product renders',len(out),flush=True)
