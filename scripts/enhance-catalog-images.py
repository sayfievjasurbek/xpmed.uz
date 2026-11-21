#!/usr/bin/env python3
"""Real-ESRGAN general-model enhancement with exact 2x output and original alpha."""
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--system',type=Path,required=True);ap.add_argument('--binary',type=Path,required=True);a=ap.parse_args();p=a.system.resolve();s=json.loads(p.read_text());folder=ROOT/'public/images/products'/s['brand']/s['slug'];originals=folder/'_originals';originals.mkdir(exist_ok=True)
for file in folder.iterdir():
 if file.is_file() and file.suffix in ['.png','.webp'] and not (originals/file.name).exists():shutil.copy2(file,originals/file.name)
work=Path(tempfile.mkdtemp(prefix='xpmed-realesrgan-'));inp=work/'input';out=work/'output';inp.mkdir();out.mkdir();selected=[]
for file in sorted(originals.glob('*.webp')):
 im=Image.open(file).convert('RGBA')
 if min(im.size)>=640:continue
 rgb=Image.new('RGB',im.size,'white');rgb.paste(im,mask=im.getchannel('A'));rgb.save(inp/(file.stem+'.png'));selected.append(file)
if selected:
 command=[str(a.binary.resolve()),'-i',str(inp),'-o',str(out),'-n','realesrgan-x4plus','-s','4','-m',str(a.binary.resolve().parent/'models'),'-j','1:1:1','-t','128','-f','png']
 print(f'Enhancing {len(selected)} low-resolution images with Real-ESRGAN general model',flush=True)
 with (work/'inference.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
records=[]
for file in selected:
 original=Image.open(file).convert('RGBA');size=(original.width*2,original.height*2);result=Image.open(out/(file.stem+'.png')).convert('RGB').resize(size,Image.Resampling.LANCZOS)
 # Keep the known-good manufacturer cutout; no rembg pass is needed.
 result.putalpha(original.getchannel('A').resize(size,Image.Resampling.LANCZOS));result.save(folder/(file.stem+'.png'));result.save(folder/file.name,lossless=True,method=6)
 records.append({'file':file.name,'originalSize':list(original.size),'finalSize':list(size),'scale':2,'model':'RealESRGAN_x4plus','pipeline':'general model 4x inference, downsampled to exact 2x; manufacturer alpha resampled 2x','original':'_originals/'+file.name})
 print(file.name,original.size,'->',size,flush=True)
s['imageDimensions']={}
for file in folder.glob('*.webp'):
 with Image.open(file) as im:s['imageDimensions']['/images/products/'+s['brand']+'/'+s['slug']+'/'+file.name]={'width':im.width,'height':im.height}
s.setdefault('review',{})['imageEnhancement']={'method':'Real-ESRGAN','scale':2,'images':len(records),'originals':'_originals','alpha':'Manufacturer masks retained; rembg not needed'}
for flag in s['review'].get('flags',[]):
 if flag['code']=='low-native-resolution':flag['resolution']='upscaled-2x';flag['message']={'ru':'Изображения низкого разрешения увеличены в 2 раза с Real-ESRGAN. Оригиналы сохранены; отображение ограничено итоговым размером.','en':'Low-resolution images enhanced 2x with Real-ESRGAN. Originals retained; display limited to final pixel dimensions.'}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');(folder/'enhancement-manifest.json').write_text(json.dumps({'images':records},ensure_ascii=False,indent=2)+'\n');print('DONE:',len(records),'images; logs:',work,flush=True)
