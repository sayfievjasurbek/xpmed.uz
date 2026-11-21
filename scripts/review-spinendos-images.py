"""Preserve thin instruments; never classify a retained gray scene as a cutout."""
import json,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw
from rembg import new_session,remove
R=Path(__file__).resolve().parents[1];O=R/'public/images/products/spinendos/endoscopic-spine-surgery';F=R/'reports/spinendos/endoscopic-spine-surgery-system';assets=json.loads((O/'prepared-assets.json').read_text());assert len(assets)==len(json.loads((F/'source-images.json').read_text())),'Wait for enhancement pipeline to finish';session=new_session('u2net',providers=['CPUExecutionProvider']);fallbacks=[]
for name,r in assets.items():
 im=Image.open(O/'_originals'/(name+'-upscaled-2x.png')).convert('RGB');w,h=im.size
 if name=='page-019-xref-609':
  # This native image embeds two printed caption lines below the left shaft.
  # The white rectangle contains no part of the instrument; keep original untouched.
  ImageDraw.Draw(im).rectangle((0,370,1450,700),fill='white');r['captionRemoval']={'method':'Source-reviewed caption-only rectangle on exact 2x image','bounds':[0,370,1450,700]}
 rgb=np.asarray(im);corner=np.concatenate([rgb[:8,:8].reshape(-1,3),rgb[-8:,-8:].reshape(-1,3),rgb[:8,-8:].reshape(-1,3),rgb[-8:,:8].reshape(-1,3)]);bg=float(np.median(corner.min(axis=1)));candidate=remove(im,session=session).convert('RGBA');alpha=candidate.getchannel('A')
 if bg>=240 or h<=16:
  # On truly white backgrounds source ink protects fine shafts that rembg removes.
  ink=Image.fromarray(np.clip(((255 if h<=16 else bg)-12-rgb.min(axis=2).astype(float))*8,0,255).astype('uint8'));alpha=ImageChops.lighter(alpha,ink)
 bbox=alpha.point(lambda v:255 if v>100 else 0).getbbox();mask=np.asarray(alpha);frame=np.r_[mask[0],mask[-1],mask[:,0],mask[:,-1]]
 broken=r['pdfImageXref']in [236,244,252,361,380,446,449,523] or not bbox or (w/h>3 and (bbox[2]-bbox[0])/w<.85) or (bg<240 and np.mean(frame>127)>.45)
 if broken:
  chosen=im.convert('RGBA');kind='scene';fallbacks.append({'file':r['src'],'pdfPage':r['pdfPage'],'reason':'rembg loses a thin shaft or retains the gray background; original photo retained after exact 2x enhancement'})
 else:
  chosen=im.convert('RGBA');chosen.putalpha(alpha);bbox=alpha.getbbox()
  if bbox:chosen=chosen.crop(bbox)
  canvas=Image.new('RGBA',(chosen.width+64,chosen.height+64));canvas.alpha_composite(chosen,(32,32));chosen=canvas;kind='cutout'
 chosen.save(O/(name+'.png'));chosen.save(O/(name+'.webp'),lossless=True,method=4);r.update(width=chosen.width,height=chosen.height,imageType=kind,maskMethod='Source-reviewed rembg; white-background source-ink protection only; failed masks retained as scenes',captionFree=True);print(name,kind,flush=True)
(O/'prepared-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2));(F/'image-fallbacks.json').write_text(json.dumps(fallbacks,ensure_ascii=False,indent=2));print('Reviewed',len(assets),'scene fallbacks',len(fallbacks),flush=True)
