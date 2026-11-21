"""Resumable Real-ESRGAN outputs -> exact 2x -> rembg -> padded PNG/WebP."""
import os,time,json,threading,concurrent.futures,argparse
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
from rembg import remove,new_session
parser=argparse.ArgumentParser();parser.add_argument('--manifest',default='source-images.json');parser.add_argument('--work',type=Path,default=Path('/tmp/xpmed-trauma-part3/artwork'));parser.add_argument('--output',default='prepared-assets.json');parser.add_argument('--model',default='u2netp');args=parser.parse_args()
R=Path(__file__).resolve().parents[1];A=R/'public/images/products/double-medical/trauma-catalogue-part3';F=R/'reports/double-medical/trauma-catalogue-part3';W=args.work;assets=json.loads((F/args.manifest).read_text());target=A/args.output;done=json.loads(target.read_text())if target.exists()else{};done={k:v for k,v in done.items()if k in assets};session=new_session(args.model,providers=['CPUExecutionProvider'])
def finish(entry):
 name,a=entry;source=W/'output'/(name+'.png')
 size=tuple(x*2 for x in a['originalSize']);im=Image.open(source).convert('RGB').resize(size,Image.Resampling.LANCZOS);original=Image.open(A/'_originals'/(name+'.png')).convert('RGB');score=float(np.abs(np.array(im.resize(original.size,Image.Resampling.LANCZOS)).astype(float)-np.array(original)).mean())
 if score>40:raise RuntimeError(f'Enhancement failed source comparison: {name}, MAE={score:.2f}; original preserved for CPU recovery')
 im.save(A/'_originals'/(name+'-2x.png'));out=remove(im,session=session).convert('RGBA');alpha=ImageChops.lighter(out.getchannel('A'),Image.fromarray(np.clip((246-np.array(im).min(axis=2).astype(float))*12,0,255).astype('uint8')));out=im.convert('RGBA');out.putalpha(alpha);box=alpha.getbbox()
 if box:
  out=out.crop(box);canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas;kind='cutout'
 else:out=im;kind='scene'
 out.save(A/(name+'.png'));out.save(A/(name+'.webp'),lossless=True);result={**a,'src':'/images/products/double-medical/trauma-catalogue-part3/'+name+'.webp','width':out.width,'height':out.height,'imageType':kind,'backgroundRemoval':{'tool':'rembg','model':args.model},'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x before rembg','scale':2,'originalSize':a['originalSize'],'enhancedSize':list(size)}};source.unlink();return name,result
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 pending={};submitted=set(done);idle=0
 while len(done)<len(assets):
  for name,a in assets.items():
   if name in submitted or len(pending)>=8:continue
   p=W/'output'/(name+'.png')
   try:
    with Image.open(p)as check:check.verify()
   except Exception:continue
   pending[pool.submit(finish,(name,a))]=name;submitted.add(name)
  completed=[future for future in pending if future.done()]
  for future in completed:
   name,result=future.result();done[name]=result;del pending[future];target.write_text(json.dumps(done,indent=2))
   if len(done)%20==0:print('Prepared',len(done),'/',len(assets),flush=True)
  if not completed:time.sleep(1);idle+=1
  else:idle=0
  if idle>3600:raise RuntimeError('GPU stopped; resumable output preserved')
print('Finished',len(done),flush=True)
