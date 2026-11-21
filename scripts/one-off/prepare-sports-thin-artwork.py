"""Recover the native thin instrument drawings omitted by the main photo threshold."""
import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/double-medical/sports-medicine-catalogue'
OUT=ROOT/'public/images/products/double-medical/sports-medicine-catalogue'
WORK=Path('/tmp/xpmed-sports-assets/pending-input')
WORK.mkdir(parents=True,exist_ok=True)
assets=json.loads((REPORT/'source-images.json').read_text())
known={(v['page'],v['xref'])for v in assets.values()}
doc=fitz.open(ROOT/'catalogs-source/double-medical/sports-medicine-catalogue.pdf')
added=0
for n in range(19,39):
    page=doc[n-1];i=0
    for info in page.get_images(full=True):
        xref,smask,width,height=info[:4]
        if (n,xref)in known or width<70 or height<3:continue
        rects=page.get_image_rects(xref)
        if not rects:continue
        rect=rects[0]
        if not(.12*page.rect.height<rect.y0<.92*page.rect.height and rect.x0>.35*page.rect.width):continue
        i+=1;key=f'page-{n:03}-thin-{i:02}'
        pix=fitz.Pixmap(doc,xref)
        if pix.colorspace and pix.colorspace.n!=3:pix=fitz.Pixmap(fitz.csRGB,pix)
        if smask:pix=fitz.Pixmap(pix,fitz.Pixmap(doc,smask))
        im=Image.frombytes('RGBA'if pix.alpha else'RGB',(pix.width,pix.height),pix.samples).convert('RGBA')
        im.save(OUT/'_originals'/f'{key}.png')
        white=Image.new('RGBA',im.size,'white');white.alpha_composite(im)
        white.convert('RGB').save(WORK/f'{key}.png')
        assets[key]={'page':n,'xref':xref,'sourceBounds':[rect.x0/page.rect.width,rect.y0/page.rect.height,rect.x1/page.rect.width,rect.y1/page.rect.height],
                     'originalSize':[im.width,im.height],'sourceAlpha':bool(smask),'captionFree':True,
                     'nativeSource':'PDF embedded thin instrument image with original alpha mask'if smask else'PDF embedded thin instrument image'}
        known.add((n,xref));added+=1
(REPORT/'source-images.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
print('added',added,'total',len(assets))
