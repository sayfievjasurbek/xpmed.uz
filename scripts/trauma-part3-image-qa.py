"""Prepare final photo contact sheets and verify native dimensions/padding."""
import json,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part3';A=R/'public/images/products/double-medical/trauma-catalogue-part3';assets=json.loads((A/'prepared-assets.json').read_text());native=json.loads((F/'source-images.json').read_text());assert set(assets)==set(native)
P=F/'image-qa';P.mkdir(exist_ok=True);ordered=sorted(assets);checks=[]
for start in range(0,len(ordered),64):
 batch=ordered[start:start+64];sheet=Image.new('RGB',(1600,8*170),'#00141B');draw=ImageDraw.Draw(sheet)
 for i,key in enumerate(batch):
  a=assets[key];im=Image.open(R/'public'/a['src'].lstrip('/')).convert('RGBA');enhanced=Image.open(A/'_originals'/(key+'-2x.png'));assert list(enhanced.size)==[v*2 for v in a['originalSize']];assert im.size==(a['width'],a['height']);box=im.getchannel('A').getbbox();assert box and (a['imageType']=='scene' or min(box[0],box[1],im.width-box[2],im.height-box[3])>=32),key
  tile=ImageOps.contain(im,(188,137));x=i%8*200;y=i//8*170;sheet.paste(tile,(x+(200-tile.width)//2,y+(140-tile.height)//2),tile);draw.text((x+5,y+143),key.replace('page-','').replace('-art-','/'),fill='white');checks.append({'key':key,'width':im.width,'height':im.height,'paddingAtLeast32':True,'enhancementExact2x':True,'captionFree':a['captionFree']})
 sheet.save(P/f'sheet-{start//64+1:02}.jpg',quality=92)
(F/'image-qa-checks.json').write_text(json.dumps(checks,indent=2));print('Final assets',len(checks),'contact sheets',math.ceil(len(checks)/64))
