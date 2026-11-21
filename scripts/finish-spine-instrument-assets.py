"""Consume completed GPU images incrementally, retaining originals and resumable metadata."""
import os,json,time
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
from rembg import remove,new_session
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';O=R/'public/images/products/double-medical/spine-instruments';W=Path('/tmp/xpmed-spine-instruments/assets');assets=json.loads((F/'source-images.json').read_text());target=O/'prepared-assets.json';done=json.loads(target.read_text())if target.exists()else{};session=new_session('u2net',providers=['CPUExecutionProvider']);idle=0
while len(done)<len(assets):
 progress=0
 for name,a in assets.items():
  if name in done:continue
  source=W/'output'/(name+'.png')
  if not source.exists():continue
  try:
   with Image.open(source)as check:check.verify()
   size=tuple(x*2 for x in a['originalSize']);im=Image.open(source).convert('RGB').resize(size,Image.Resampling.LANCZOS)
  except Exception:continue
  im.save(O/'_originals'/(name+'-2x.png'));out=remove(im,session=session).convert('RGBA');alpha=ImageChops.lighter(out.getchannel('A'),Image.fromarray(np.clip((246-np.array(im).min(axis=2).astype(float))*12,0,255).astype('uint8')));out=im.convert('RGBA');out.putalpha(alpha);box=alpha.getbbox()
  if box:
   out=out.crop(box);canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;kind='cutout'
  else:out=im;kind='scene'
  out.save(O/(name+'.png'));out.save(O/(name+'.webp'),lossless=True);done[name]={**a,'src':'/images/products/double-medical/spine-instruments/'+name+'.webp','width':out.width,'height':out.height,'imageType':kind,'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)}};progress+=1;source.unlink()
  if len(done)%16==0:target.write_text(json.dumps(done,indent=2));print('Prepared',len(done),'/',len(assets),flush=True)
 target.write_text(json.dumps(done,indent=2))
 if not progress:
  time.sleep(3);idle+=1
  if idle>1200:raise RuntimeError('GPU outputs stopped arriving; partial work preserved')
 else:idle=0
print('Finished',len(done),'instrument photos',flush=True)
