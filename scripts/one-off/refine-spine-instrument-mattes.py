"""Clear edge-connected white backdrop left by rembg without deleting enclosed white surfaces.
Erode background seeds first so one-pixel highlights cannot connect a white instrument face
with the outer backdrop. Original native and 2x photographs stay in _originals.
"""
import json,os
from pathlib import Path
import cv2,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'public/images/products/double-medical/spine-instruments';F=R/'reports/double-medical/spine-catalogue-instruments';stamp=F/'matte-refinement.json';done=json.loads(stamp.read_text())if stamp.exists()else{};assets={}
for name in ['artwork-assets.json','manual-photo-assets.json']:
 if(A/name).exists():assets.update(json.loads((A/name).read_text()))
for key,record in assets.items():
 if key in done:continue
 png=A/(key+'.png')
 try:
  im=Image.open(png).convert('RGBA')
 except Exception:
  im=Image.open(A/(key+'.webp')).convert('RGBA')
 a=np.array(im);candidate=((a[:,:,:3].min(axis=2)>246)|(a[:,:,3]<4)).astype('uint8');candidate=cv2.erode(candidate,np.ones((3,3),np.uint8),borderType=cv2.BORDER_REPLICATE);n,labels=cv2.connectedComponents(candidate,8);edge=set(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]));edge.discard(0);background=np.isin(labels,list(edge));changed=bool(np.any(a[background,3]));a[background,3]=0
 webp=A/(key+'.webp');valid=True
 try:
  with Image.open(webp)as check:check.load()
 except Exception:valid=False
 if changed or not valid:
  out=Image.fromarray(a);temporary=png.with_suffix('.work.png');out.save(temporary);os.replace(temporary,png);temporary=webp.with_suffix('.work.webp');out.save(temporary,lossless=True,method=0);os.replace(temporary,webp)
 done[key]={'method':'rembg + eroded edge-connected white backdrop cleanup','nativeAnd2xOriginalsRetained':True}
 if len(done)%40==0:stamp.write_text(json.dumps(done,indent=2));print('Refined',len(done),flush=True)
stamp.write_text(json.dumps(done,indent=2));print('Refined matte backgrounds',len(done))
