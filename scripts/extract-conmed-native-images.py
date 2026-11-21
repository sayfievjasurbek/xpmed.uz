#!/usr/bin/env python3
"""Extract original PDF photo objects, excluding separate vector caption artwork."""
import pymupdf as fitz,json,io,copy,os,math
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
from rembg import new_session,remove
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);report=ROOT/'reports/conmed/list-layout';originals=[]
for f in sorted((report/'before').glob('*.json')):originals.extend(json.loads(f.read_text())['gallery'])
doc=fitz.open('catalogs-source/conmed/advanced-visualization-system.pdf');folder=ROOT/'public/images/products/conmed/list-clean';cache=report/'native-image-extraction.json';outputs=json.loads(cache.read_text())if cache.exists()else {};session=None
for index,a in enumerate(originals,1):
 if a['src']in outputs:continue
 page=doc[a['pdfPage']-1];w,h=page.rect.width,page.rect.height;b=a['sourceBounds'];target=fitz.Rect(b[0]*w,b[1]*h,b[2]*w,b[3]*h)
 candidates=[]
 for info in page.get_image_info(xrefs=True):
  if not info['xref']:continue
  rect=fitz.Rect(info['bbox']);overlap=(rect&target).get_area()
  if overlap/rect.get_area()>.4 or (index==20 and info['xref']==375):candidates.append((overlap,info))
 if not candidates:
  approved=json.loads((report/'caption-free-images.json').read_text())[a['src']];approved['sourceMethod']='Reviewed source-region crop; caption-free fallback';outputs[a['src']]=approved;cache.write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n');print('Reviewed fallback',index,flush=True);continue
 _,info=max(candidates,key=lambda x:x[0]);blob=doc.extract_image(info['xref']);image=Image.open(io.BytesIO(blob['image'])).convert('RGB');source_alpha=None
 if blob.get('smask'):
  mask=doc.extract_image(blob['smask']);source_alpha=Image.open(io.BytesIO(mask['image'])).convert('L')
  rgba=image.convert('RGBA');rgba.putalpha(source_alpha);white=Image.new('RGBA',image.size,'white');white.alpha_composite(rgba);image=white.convert('RGB')
 source_size=list(image.size);angle=math.degrees(math.atan2(info['transform'][1],info['transform'][0]));
 if abs(angle)>1:
  image=image.rotate(-angle,expand=True,resample=Image.Resampling.BICUBIC,fillcolor='white')
  if source_alpha is not None:source_alpha=source_alpha.rotate(-angle,expand=True,resample=Image.Resampling.BICUBIC,fillcolor=0)
 native_path=folder/'_originals'/(Path(a['src']).stem+'-native.png');image.save(native_path)
 if session is None:session=new_session('u2net',providers=['CPUExecutionProvider'])
 segmented=remove(image,session=session).convert('RGBA');rgb=np.array(image);ink=np.clip((248-rgb.min(axis=2).astype(float))*8,0,255).astype('uint8');alpha=np.array(ImageChops.lighter(segmented.getchannel('A'),Image.fromarray(ink)))
 # Pure paper remains transparent, including large enclosed cable loops.
 if index in [23,24]:alpha[rgb.min(axis=2)>247]=0
 if source_alpha is not None:alpha=np.minimum(alpha,np.array(source_alpha))
 cut=image.convert('RGBA');cut.putalpha(Image.fromarray(alpha));bbox=cut.getchannel('A').getbbox()
 if bbox:cut=cut.crop(bbox)
 out=Image.new('RGBA',(cut.width+64,cut.height+64));out.alpha_composite(cut,(32,32));dest=folder/(Path(a['src']).stem+'.webp');out.save(dest,format='WEBP',lossless=True,method=5)
 outputs[a['src']]={**copy.deepcopy(a),'src':'/images/products/conmed/list-clean/'+dest.name,'width':out.width,'height':out.height,'imageType':'cutout','captionFree':True,'originalImage':a['src'],'pdfImageXref':info['xref'],'nativeSourceSize':source_size,'sourceRotation':angle,'pdfAlphaMask':blob.get('smask',0),'sourceMethod':'Original embedded PDF image; vector captions excluded'}
 cache.write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n');print('Native photo',index,'/48',info['xref'],image.size,flush=True)
for file in Path('content/products/conmed').glob('*.json'):
 s=json.loads(file.read_text())
 if s.get('catalogType')!='list' or s['status']!='draft':continue
 def replace(v):
  if isinstance(v,str):return outputs[v]['src']if v in outputs else v
  if isinstance(v,list):return [replace(x)for x in v]
  if isinstance(v,dict):
   asset=outputs.get(v.get('src'))or next((a for a in outputs.values()if a['src']==v.get('src')),None)
   if asset:return copy.deepcopy(asset)
   return {k:replace(x)if k not in ['review','codeEvidence','refCodes']else x for k,x in v.items()}
  return v
 s=replace(s)
 for a in outputs.values():s['imageDimensions'][a['src']]={'width':a['width'],'height':a['height']}
 file.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('Native images applied to drafts only.')
