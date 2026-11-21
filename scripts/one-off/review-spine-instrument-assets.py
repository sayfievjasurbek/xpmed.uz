"""Compact native-image contact sheets for Codex inspection; no image edits."""
import json,argparse
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];A=R/'public/images/products/double-medical/spine-instruments';out=Path('/tmp/xpmed-spine-instruments/qa');out.mkdir(exist_ok=True);assets={}
for f in ['artwork-assets.json','manual-photo-assets.json']:
 if(A/f).exists():assets.update(json.loads((A/f).read_text()))
assets={k:a for k,a in assets.items()if not k.startswith(('art-290-','art-308-','art-383-'))}
ordered=sorted(assets.items());(out/'manifest.json').write_text(json.dumps([k for k,a in ordered]))
for start in range(0,len(ordered),80):
 sheet=Image.new('RGB',(1800,10*155),'#2B3A40');d=ImageDraw.Draw(sheet)
 for i,(key,a)in enumerate(ordered[start:start+80]):
  im=Image.open(R/'public'/a['src'].lstrip('/')).convert('RGBA');im.thumbnail((215,124));x=(i%8)*225;y=(i//8)*155;sheet.paste(im,(x+(225-im.width)//2,y+23+(124-im.height)//2),im);d.text((x+3,y+3),key.replace('page-','').replace('-row-','/'),fill='white')
 sheet.save(out/f'{start//80:02}.jpg',quality=93)
print(len(assets),'assets',len(list(out.glob('*.jpg'))),'sheets')
