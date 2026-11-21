#!/usr/bin/env python3
"""Caption-free source recrops. Preserve printed device markings and every original."""
import json,os,copy
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np
from rembg import new_session,remove
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);REPORT=ROOT/'reports/conmed/list-layout';assets=[]
for f in sorted((REPORT/'before').glob('*.json')):assets.extend(json.loads(f.read_text())['gallery'])
# Caption zones were reviewed on source image sheets; only OCR word boxes in these
# zones are erased. Labels engraved on devices are deliberately retained.
zones={1:[0,.9,1,1],2:[0,.9,1,1],3:[0,.83,.5,1],4:[0,.85,.5,1],5:[0,.9,1,1],6:[0,.78,1,1],7:[0,.83,1,1],8:[0,.62,1,1],9:[0,.78,1,1],10:[0,.78,1,1],11:[.4,0,1,.25],12:[0,0,1,.29],13:[0,.79,1,1],14:[0,.87,1,1],15:[0,.88,1,1],16:[0,.88,1,1],17:[0,.47,.55,.62],18:[0,.5,.55,.7],19:[0,.53,.55,.7],20:[0,.89,1,1],21:[0,.89,1,1],22:[0,.89,1,1],25:[0,0,0,0],26:[.7,.75,1,.9],27:[.7,.35,1,.65],28:[.65,.84,1,1],29:[.77,.4,1,.7],30:[.65,.35,1,.82],31:[.7,.79,1,1],32:[.75,.75,1,1],33:[0,.88,1,1],34:[0,.9,1,1],35:[0,.9,1,1],36:[0,.87,1,1],37:[0,.9,1,1],38:[0,.87,1,1],39:[0,.9,1,1],40:[0,.87,1,1],41:[0,.87,1,1],42:[.5,.93,1,1],43:[0,.8,1,1],44:[0,.84,1,1],45:[0,.9,.6,1],46:[0,.69,.45,.92],47:[0,.8,.6,1],48:[0,.94,1,1]}
exclusions={}
for profile in (ROOT/'scripts/profiles').glob('conmed-visualization-sections-*.json'):
 data=json.loads(profile.read_text())
 for section in (data['sections']if isinstance(data,dict)else data):
  for group in section['groups']:
   for photo in group.get('photos',[]):
    if photo.get('excludeBounds'):exclusions[tuple(photo['bounds'])]=photo['excludeBounds']
manifest=REPORT/'caption-free-images.json';outputs=json.loads(manifest.read_text())if manifest.exists()else {};session=None;page=None;last=None
for index,a in enumerate(assets,1):
 if a['src']in outputs:continue
 n=a['pdfPage'];b=a['sourceBounds']
 if last!=n:page=Image.open(f'public/catalogs/conmed/advanced-visualization-system/ocr-600/{n:03}-600dpi.png').convert('RGB');last=n
 w,h=page.size;pixel=[round(b[0]*w),round(b[1]*h),round(b[2]*w),round(b[3]*h)];im=page.crop(pixel);draw=ImageDraw.Draw(im);rects=[]
 evidence=json.loads(Path(f'public/catalogs/conmed/advanced-visualization-system/ocr-600/{n:03}.json').read_text())
 z=zones.get(index)
 if z:
  for word in evidence['passes']['11']['words']:
   x1,y1,x2,y2=word['bounds'];cx=((x1+x2)/2-b[0])/(b[2]-b[0]);cy=((y1+y2)/2-b[1])/(b[3]-b[1])
   if z[0]<=cx<=z[2]and z[1]<=cy<=z[3]:
    rect=[max(0,round(x1*w)-pixel[0]-4),max(0,round(y1*h)-pixel[1]-4),min(im.width,round(x2*w)-pixel[0]+4),min(im.height,round(y2*h)-pixel[1]+4)];draw.rectangle(rect,fill='white');rects.append(rect)
 # Captions not recognized at all, callout leaders, and neighboring photo fragments.
 extra={9:[[0,.78,1,1]],23:[[.25,.3,.7,.5]],24:[[.25,.36,.7,.55]],25:[[.145,.22,.84,.44],[.085,.06,.25,.18],[.7,.06,.85,.17],[0,0,1,.035]],37:[[0,0,.2,.11],[.8,.98,1,1]],18:[[.74,0,.98,.24]],19:[[.74,0,.98,.2]],48:[]}
 for r in extra.get(index,[]):
  rect=[round(r[0]*im.width),round(r[1]*im.height),round(r[2]*im.width),round(r[3]*im.height)];draw.rectangle(rect,fill='white');rects.append(rect)
 folder=ROOT/'public/images/products/conmed/list-clean';folder.mkdir(exist_ok=True);originals=folder/'_originals';originals.mkdir(exist_ok=True);stem=Path(a['src']).stem;originals_file=originals/(stem+'-600dpi.png')
 if not originals_file.exists():page.crop(pixel).save(originals_file)
 for box in exclusions.get(tuple(b),[]):
  rect=[round(box[0]*w)-pixel[0],round(box[1]*h)-pixel[1],round(box[2]*w)-pixel[0],round(box[3]*h)-pixel[1]];draw.rectangle(rect,fill='white');rects.append(rect)
 im.save(originals/(stem+'-caption-free.png'))
 if session is None:session=new_session('u2net',providers=['CPUExecutionProvider'])
 cut=remove(im,session=session).convert('RGBA');rgb=np.asarray(im);ink=np.clip((248-rgb.min(axis=2).astype(float))*8,0,255).astype('uint8');alpha=ImageChops.lighter(cut.getchannel('A'),Image.fromarray(ink));cut=im.convert('RGBA');cut.putalpha(alpha)
 bbox=cut.getchannel('A').getbbox()
 if bbox:cut=cut.crop(bbox)
 out=Image.new('RGBA',(cut.width+64,cut.height+64));out.alpha_composite(cut,(32,32));dest=folder/(stem+'.webp');out.save(dest,format='WEBP',lossless=True,method=5)
 if index in [23,24]:
  pixels=np.array(out);pixels[pixels[:,:,:3].min(axis=2)>247,3]=0;out=Image.fromarray(pixels);out.save(dest,format='WEBP',lossless=True,method=5)
 entry={**copy.deepcopy(a),'src':'/images/products/conmed/list-clean/'+dest.name,'width':out.width,'height':out.height,'captionFree':True,'imageType':'cutout','originalImage':a['src'],'captionRemovalPixelBounds':rects};outputs[a['src']]=entry
 manifest.write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n');print('Caption-free',index,'/48',flush=True)
# Replace exact asset references without modifying any ordering data or codes.
for f in (ROOT/'content/products/conmed').glob('*.json'):
 s=json.loads(f.read_text())
 if s.get('catalogType')!='list' or s['status']!='draft':continue
 def transform(v):
  if isinstance(v,str):return outputs[v]['src']if v in outputs else v
  if isinstance(v,list):return [transform(x)for x in v]
  if isinstance(v,dict):
   if v.get('src')in outputs:return copy.deepcopy(outputs[v['src']])
   existing=next((a for a in outputs.values()if a['src']==v.get('src')),None)
   if existing:return copy.deepcopy(existing)
   return {k:transform(x)if k not in ['review','codeEvidence','refCodes']else x for k,x in v.items()}
  return v
 s=transform(s)
 for asset in outputs.values():s.setdefault('imageDimensions',{})[asset['src']]={'width':asset['width'],'height':asset['height']}
 # Every caption appears in HTML alongside the corresponding subgroup image.
 for t in s['specTables']:
  for asset in t.get('images',[]):assert asset.get('captionFree')
 for g in s['componentGroups']:
  for c in s['components']:
   if c.get('image'):
    asset=next((a for a in outputs.values()if a['src']==c['image']),None)
    if asset:c['imageCaption']=asset['imageCaption']
 f.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('All draft references updated.')
