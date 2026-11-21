"""Extract the catalog's native, caption-free alpha-masked product artwork."""
import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT/'catalogs-source/double-medical/sports-medicine-catalogue.pdf'
OUT = ROOT/'public/images/products/double-medical/sports-medicine-catalogue'
WORK = Path('/tmp/xpmed-sports-assets/input')
REPORT = ROOT/'reports/double-medical/sports-medicine-catalogue'
for p in (OUT/'_originals', WORK, REPORT): p.mkdir(parents=True, exist_ok=True)
doc = fitz.open(PDF)
assets = {}
for page_no in range(4, 39):
    page = doc[page_no-1]
    candidates=[]
    for info in page.get_images(full=True):
        xref, smask, width, height = info[:4]
        for rect in page.get_image_rects(xref):
            if rect.y0 < page.rect.height*.12 or rect.y0 > page.rect.height*.92:
                continue
            if min(width,height) < 9 or rect.width < 15 or rect.height < 3:
                continue
            candidates.append((rect.y0, xref, smask, width, height, rect))
    candidates.sort(key=lambda x: (x[0], x[5].x0))
    seen=set()
    for _,xref,smask,width,height,rect in candidates:
        if xref in seen: continue
        seen.add(xref)
        base=fitz.Pixmap(doc,xref)
        if base.colorspace and base.colorspace.n!=3:
            base=fitz.Pixmap(fitz.csRGB,base)
        if smask:
            pix=fitz.Pixmap(base,fitz.Pixmap(doc,smask))
        else: pix=base
        mode='RGBA' if pix.alpha else 'RGB'
        im=Image.frombytes(mode,(pix.width,pix.height),pix.samples).convert('RGBA')
        key=f'page-{page_no:03}-image-{len(seen):02}'
        im.save(OUT/'_originals'/f'{key}.png')
        white=Image.new('RGBA',im.size,'white');white.alpha_composite(im)
        white.convert('RGB').save(WORK/f'{key}.png')
        assets[key]={'page':page_no,'xref':xref,'sourceBounds':[rect.x0/page.rect.width,rect.y0/page.rect.height,rect.x1/page.rect.width,rect.y1/page.rect.height],
                     'originalSize':[im.width,im.height],'sourceAlpha':bool(smask),
                     'captionFree':True,'nativeSource':'PDF embedded image with original alpha mask' if smask else 'PDF embedded image'}
    print(page_no,len(seen),flush=True)
(REPORT/'source-images.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
print('native assets',len(assets))
