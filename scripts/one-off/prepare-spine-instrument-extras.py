"""Recover instrument photos on pages without ruled rows; preserve absent source images as absent."""
import json,subprocess
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageChops
import numpy as np
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';O=R/'public/images/products/double-medical/spine-instruments';W=Path('/tmp/xpmed-spine-instruments/extras');D=f.open(R/'catalogs-source/double-medical/spine-catalogue.pdf');rows=json.loads((F/'rows-evidence.json').read_text());source=json.loads((F/'source-images.json').read_text());assets={};absent=[]
for p in [W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
for row in rows:
 n=row['pdfPage'];cy=row['cy'];existing=[a for a in source.values()if any(p['pdfPage']==n and p['bounds'][1]-.005<=cy<p['bounds'][3] for p in a['placements'])]
 if existing:continue
 siblings=[r for r in rows if r['pdfPage']==n];i=siblings.index(row);top=row['codeBounds'][1]-.014;bottom=siblings[i+1]['codeBounds'][1]-.014 if i+1<len(siblings)else .925;p=D[n-1];bbox=f.Rect(p.rect.width*.557,p.rect.height*top,p.rect.width*.92,p.rect.height*bottom);pix=p.get_pixmap(dpi=150,clip=bbox,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);yy,xx=np.where(np.array(im).min(axis=2)<238)
 if len(xx)<10:absent.append({'id':row['id'],'pdfPage':n,'code':row['value'],'description':row['description'],'reason':'No source instrument artwork in the corresponding row'});continue
 im=im.crop((max(0,int(xx.min())-3),max(0,int(yy.min())-3),min(im.width,int(xx.max())+4),min(im.height,int(yy.max())+4)));name='extra-'+row['id'];im.save(O/'_originals'/(name+'.png'));im.save(W/'input'/(name+'.png'));assets[name]={'name':name,'originalSize':list(im.size),'captionFree':True,'sourceMethod':'Caption-free source photo, unruled instrument row','placements':[{'pdfPage':n,'printedPage':n-2,'bounds':[.557,top,.92,bottom]}]}
(F/'absent-source-images.json').write_text(json.dumps(absent,indent=2));print('Extra photos',len(assets),'absent source art',len(absent),flush=True)
if assets:
 with(W/'upscale.log').open('w')as log:subprocess.run(['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(W/'input'),'-o',str(W/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png'],stdout=log,stderr=subprocess.STDOUT,check=True)
 from rembg import remove,new_session
 session=new_session('u2net',providers=['CPUExecutionProvider'])
 for name,a in assets.items():
  size=tuple(x*2 for x in a['originalSize']);im=Image.open(W/'output'/(name+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS);im.save(O/'_originals'/(name+'-2x.png'));out=remove(im,session=session).convert('RGBA');alpha=ImageChops.lighter(out.getchannel('A'),Image.fromarray(np.clip((246-np.array(im).min(axis=2).astype(float))*12,0,255).astype('uint8')));out=im.convert('RGBA');out.putalpha(alpha);out=out.crop(alpha.getbbox());canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;out.save(O/(name+'.png'));out.save(O/(name+'.webp'),lossless=True);a.update(src='/images/products/double-medical/spine-instruments/'+name+'.webp',width=out.width,height=out.height,imageType='cutout',imageEnhancement={'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)})
(O/'extra-assets.json').write_text(json.dumps(assets,indent=2));print('Prepared extra photos',len(assets),flush=True)
