"""Visual QA corrections: omit QR graphics, rejoin PDF image fragments, retain cutouts."""
import json
from pathlib import Path
from PIL import Image,ImageChops
from rembg import remove,new_session
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'public/images/products/double-medical/joint-catalogue';F=R/'reports/double-medical/joint-catalogue';assets={}
for name in ['prepared-assets.json','extra-assets.json','corrected-assets.json']:assets.update(json.loads((P/name).read_text()))
qrrefs={65,81,98,114,130,146,159,173,190,250,264,278,292,308};ignored=[k for k,a in assets.items()if any(p['pdfImageXref']in qrrefs for p in a['placements'])];(F/'ignored-qr-assets.json').write_text(json.dumps(ignored,indent=2));fix=json.loads((P/'corrected-assets.json').read_text());session=new_session('u2net',providers=['CPUExecutionProvider'])
def save(name,im,meta):
 alpha=im.getchannel('A');box=alpha.point(lambda v:255 if v>12 else 0).getbbox();im=im.crop(box);out=Image.new('RGBA',(im.width+64,im.height+64));out.alpha_composite(im,(32,32));out.save(P/(name+'.webp'),lossless=True);out.save(P/(name+'.png'));fix[name]={**meta,'name':name,'src':'/images/products/double-medical/joint-catalogue/'+name+'.webp','width':out.width,'height':out.height,'imageType':'cutout','captionFree':True};return fix[name]
for n,refs,name in [(7,[106,107,108],'cpt-cemented-stem-complete'),(15,[220,221],'bipolar-cup-front-complete'),(25,[351,352],'cynthia-tibial-tray-complete')]:
 parts=[a for a in assets.values()if any(p['pdfPage']==n and p['pdfImageXref']in refs for p in a['placements'])];positions=[next(p for p in a['placements']if p['pdfPage']==n)for a in parts];bs=[p['bounds']for p in positions];bbox=[min(b[0]for b in bs),min(b[1]for b in bs),max(b[2]for b in bs),max(b[3]for b in bs)];# common grid follows the least-resolved enhanced fragment, never inflating its native dimensions
 scale=min(min(a['originalSize'][0]*2/(b[2]-b[0]),a['originalSize'][1]*2/((b[3]-b[1])*613.28/437.53))for a,b in zip(parts,bs));hscale=scale*613.28/437.53;out=Image.new('RGBA',(round((bbox[2]-bbox[0])*scale)+2,round((bbox[3]-bbox[1])*hscale)+2))
 for a,b in zip(parts,bs):
  im=Image.open(P/'_originals'/(a['name']+'-upscaled-2x.png')).convert('RGBA');maskfile=P/'_originals'/(a['name']+'-source-alpha.png')
  if maskfile.exists():im.putalpha(Image.open(maskfile).resize(im.size,Image.Resampling.LANCZOS))
  else:im=remove(im,session=session).convert('RGBA')
  im=im.resize((round((b[2]-b[0])*scale),round((b[3]-b[1])*hscale)),Image.Resampling.LANCZOS);out.alpha_composite(im,(round((b[0]-bbox[0])*scale),round((b[1]-bbox[1])*hscale)))
 meta={**parts[0],'placements':[{'pdfPage':n,'bounds':bbox,'pdfImageXrefs':refs}],'compositeSourceAssets':[a['name']for a in parts]};save(name,out,meta)
for name in ['page-013-xref-198','page-039-xref-523','page-085-xref-1270']:
 a=assets[name];im=Image.open(P/'_originals'/(name+'-upscaled-2x.png')).convert('RGB');cut=remove(im,session=session).convert('RGBA');save(name,cut,a)
(P/'corrected-assets.json').write_text(json.dumps(fix,indent=2));print('Image QA corrections',len(fix),'ignored QR assets',len(ignored))
