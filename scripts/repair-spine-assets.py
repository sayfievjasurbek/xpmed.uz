"""Rejoin source artwork split into masked image fragments, without captions."""
import json,subprocess
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'public/images/products/double-medical/spine-catalogue';F=R/'reports/double-medical/spine-catalogue';W=Path('/tmp/xpmed-spine/repairs');D=f.open(R/'catalogs-source/double-medical/spine-catalogue.pdf');A=json.loads((O/'prepared-assets.json').read_text());T=json.loads((F/'tables-final.json').read_text());repair={4,5,9,23,26,75,186}
for p in [W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
rejected=[]
for key,a in list(A.items()):
 if all(p['bounds'][1]>.8 for p in a['placements']):rejected.append(key);del A[key]
(F/'excluded-qr-assets.json').write_text(json.dumps(rejected,indent=2))
new={}
for n in repair:
 p=D[n-1];art=[a for a in p.get_image_info(xrefs=True)if a['xref']and a['bbox'][1]/p.rect.height>.10 and a['bbox'][1]/p.rect.height<.8];groups={}
 for a in art:
  cy=(a['bbox'][1]+a['bbox'][3])/2/p.rect.height;table=min((t for t in T if t['pdfPage']==n),key=lambda t:abs(t['headerY']-cy));groups.setdefault(table['id'],[]).append(a)
 for ident,items in groups.items():
  bbox=f.Rect(min(a['bbox'][0]for a in items)-1,min(a['bbox'][1]for a in items)-1,max(a['bbox'][2]for a in items)+1,max(a['bbox'][3]for a in items)+1);bbox &= p.rect;pix=p.get_pixmap(dpi=150,clip=bbox,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);name=ident+'-rejoined';im.save(O/'_originals'/(name+'.png'));im.save(W/'input'/(name+'.png'));new[name]={'name':name,'originalSize':list(im.size),'placements':[{'pdfPage':n,'printedPage':n-2,'bounds':[bbox.x0/p.rect.width,bbox.y0/p.rect.height,bbox.x1/p.rect.width,bbox.y1/p.rect.height]}],'tableId':ident,'reassembledFromSource':True}
 for key,a in list(A.items()):
  if any(q['pdfPage']==n for q in a['placements']):del A[key]
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png']
with(W/'upscale.log').open('w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
from rembg import remove,new_session
session=new_session('u2net',providers=['CPUExecutionProvider'])
for name,a in new.items():
 size=tuple(x*2 for x in a['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-2x.png'));out=remove(im,session=session).convert('RGBA');rgb=np.asarray(im);white_alpha=Image.fromarray(np.clip((248-rgb.min(axis=2).astype(float))*12,0,255).astype('uint8'));alpha=ImageChops.lighter(out.getchannel('A'),white_alpha);out=im.convert('RGBA');out.putalpha(alpha);out=out.crop(alpha.getbbox());canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;out.save(O/(name+'.png'));out.save(O/(name+'.webp'),lossless=True);A[name]={**a,'src':'/images/products/double-medical/spine-catalogue/'+name+'.webp','width':out.width,'height':out.height,'imageType':'cutout','captionFree':True,'imageEnhancement':{'method':'PDF composite at native effective 150 DPI, Real-ESRGAN x4plus downsampled to 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)}}
(O/'prepared-assets.json').write_text(json.dumps(A,indent=2));print('Artwork assets',len(A),'rejoined',len(new),'excluded QR',len(rejected))
