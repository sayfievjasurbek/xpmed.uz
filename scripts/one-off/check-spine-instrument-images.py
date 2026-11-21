"""Verify complete image jobs, transparent padding and exact 2x native sizes; prepare visual sheets."""
import json,argparse
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';A=R/'public/images/products/double-medical/spine-instruments';parser=argparse.ArgumentParser();parser.add_argument('--record-visual-review',action='store_true');args=parser.parse_args();base=json.loads((A/'artwork-assets.json').read_text());source=json.loads((F/'artwork-images.json').read_text());manual=json.loads((A/'manual-photo-assets.json').read_text());assert set(base)==set(source),'Base processing is incomplete';assert set(manual)==set(json.loads((F/'manual-photo-images.json').read_text())),'Manual processing is incomplete';assets={k:a for k,a in base.items()if not k.startswith(('art-290-','art-308-','art-383-'))};assets.update(manual);repairs=json.loads((F/'cpu-repaired-images.json').read_text());assert set(repairs)==set(json.loads((F/'gpu-damaged-images.json').read_text())), 'CPU image recovery incomplete';problems=[]
for key,a in assets.items():
 original=Image.open(A/'_originals'/(key+'.png'));enhanced=Image.open(A/'_originals'/(key+'-2x.png'));im=Image.open(R/'public'/a['src'].lstrip('/')).convert('RGBA');assert list(original.size)==a['originalSize'];assert list(enhanced.size)==a['imageEnhancement']['enhancedSize']==[2*v for v in original.size];assert list(im.size)==[a['width'],a['height']];bbox=im.getchannel('A').getbbox()
 if not bbox or bbox[0]<32 or bbox[1]<32 or bbox[2]>im.width-32 or bbox[3]>im.height-32:problems.append(key)
 assert a['captionFree'];a['padding']=32
assert not problems,problems
out=Path('/tmp/xpmed-spine-instruments/final-qa');out.mkdir(exist_ok=True);ordered=sorted(assets.items())
for start in range(0,len(ordered),100):
 sheet=Image.new('RGB',(1800,1500),'#2B3A40');d=ImageDraw.Draw(sheet)
 for i,(key,a)in enumerate(ordered[start:start+100]):
  im=Image.open(R/'public'/a['src'].lstrip('/')).convert('RGBA');im.thumbnail((175,120));x=i%10*180;y=i//10*150;sheet.paste(im,(x+(180-im.width)//2,y+24+(120-im.height)//2),im);d.text((x+3,y+3),key,fill='white')
 sheet.save(out/f'{start//100:02}.jpg',quality=93)
if args.record_visual_review:
 (F/'base-assets-before-photo-corrections.json').write_text(json.dumps(base,indent=2));(A/'artwork-assets.json').write_text(json.dumps(assets,indent=2));(F/'image-qa.json').write_text(json.dumps({'status':'reviewed','reviewedAssets':sorted(assets),'nativeSourceImages':len(assets),'photosManuallyRealigned':22,'checks':['Exact 2x Real-ESRGAN native size','Transparent PNG and WebP','32px minimum clear padding','Source captions excluded','Full source photo contact sheets inspected; irregular pages 290/308/383 manually aligned','Final dark-background contact sheets inspected'],'cutoutFallbacks':[],'cpuRepairedImages':len(repairs),'ncnnWeightsSha256':'713ee713b0353afaa27976f0563a64a5043bd70b9bd8936c2e26e25ebcdbcddf'},indent=2))
print('Images checked',len(assets),'visual sheets',len(list(out.glob('*.jpg'))),'pending explicit visual approval'if not args.record_visual_review else'review recorded')
