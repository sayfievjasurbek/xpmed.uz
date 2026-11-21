"""Render the original outlined captions for Codex's numeric review."""
import re,json,math
from pathlib import Path
import pymupdf as f
from PIL import Image,ImageDraw,ImageOps
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part2';D=f.open(R/'catalogs-source/double-medical/trauma-catalogue.pdf');rows=json.loads((F/'instrument-rows-final.json').read_text());flags=json.loads((F/'caption-numeric-review.json').read_text());ids={a['row']for a in flags}
for row in rows:
 if re.search(r'(?<![A-Za-z0-9Ø])(?:0|9|4|6)[0-9]+\.\d|Ø[0-9]+\.[0-9]{3,}|lenath|CAMM|wre|W rench|moO|pØ',row['description']):ids.add(row['id'])
already=set(json.loads((R/'scripts/profiles/trauma-part2-visual-descriptions.json').read_text())['readings']);selected=[r for r in rows if r['id']in ids and r['id']not in already];(F/'caption-review-selected.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2))
P=F/'caption-review-extra';P.mkdir(exist_ok=True);crops=[]
for row in selected:
 n=row['pdfPage'];original=D[n-1];b=row['sourceBounds'];qs=[a['rect']for a in original.get_drawings()if a['type']=='f'and .22<a['rect'].x0/original.rect.width<.72 and 1<a['rect'].height<13 and b[1]<(a['rect'].y0+a['rect'].y1)/2/original.rect.height<b[3]]
 if not qs:continue
 rect=qs[0]
 for q in qs[1:]:rect|=q
 rect+=(-2,-2,2,2);art=f.open();art.insert_pdf(D,from_page=n-1,to_page=n-1);pg=art[0];pg.clean_contents();blocked={}
 for info in pg.get_images(full=True):blocked.setdefault(info[9],set()).add(info[7])
 pageStreams=set(pg.get_contents());streams=pageStreams|{i for i in range(1,art.xref_length())if art.xref_get_key(i,'Subtype')==('name','/Form')}
 for x in streams:
  data=art.xref_stream(x)
  if not data:continue
  for name in blocked.get(x,set())|(blocked.get(0,set())if x in pageStreams else set()):data=re.sub(rb'/'+re.escape(name.encode())+rb'\s+Do\b',b'',data)
  art.update_stream(x,data)
 pix=pg.get_pixmap(dpi=500,clip=rect,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im=ImageOps.contain(im,(1120,170));crops.append((row['id'],im));im.save(P/(row['id']+'.png'))
for i in range(0,len(crops),8):
 batch=crops[i:i+8];sheet=Image.new('RGB',(1200,200*len(batch)),'white');draw=ImageDraw.Draw(sheet)
 for j,(ident,im)in enumerate(batch):draw.text((10,j*200+5),ident,fill='black');sheet.paste(im,(30,j*200+25))
 sheet.save(P/f'sheet-{i//8+1:02}.png')
print('Source captions to inspect',len(selected),'sheets',math.ceil(len(crops)/8))
