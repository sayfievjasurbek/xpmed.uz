"""Restore embedded PDF opacity masks before accepting cutouts; retain all raw originals."""
import json,io
from pathlib import Path
from PIL import Image
import pymupdf as f
R=Path(__file__).resolve().parents[1];O=R/'public/images/products/conmed/hall';F=R/'reports/conmed/hall-powered-instruments';D=f.open(R/'catalogs-source/conmed/hall-powered-instruments.pdf');assets=json.loads((O/'prepared-assets.json').read_text());fixed=[]
for name,a in assets.items():
 kind,ref=D.xref_get_key(a['pdfImageXref'],'SMask')
 if kind!='xref':continue
 x=int(ref.split()[0]);mask=Image.open(io.BytesIO(D.extract_image(x)['image'])).convert('L');mask.save(O/'_originals'/(name+'-source-alpha.png'));original=Image.open(O/'_originals'/(name+'.png')).convert('RGBA');original.putalpha(mask);original.save(O/'_originals'/(name+'-with-pdf-mask.png'))
 enhanced=Image.open(O/'_originals'/(name+'-upscaled-2x.png')).convert('RGBA');alpha=mask.resize(enhanced.size,Image.Resampling.LANCZOS);enhanced.putalpha(alpha);enhanced.save(O/'_originals'/(name+'-upscaled-2x-with-pdf-mask.png'));box=alpha.getbbox();enhanced=enhanced.crop(box);chosen=Image.new('RGBA',(enhanced.width+64,enhanced.height+64));chosen.alpha_composite(enhanced,(32,32));chosen.save(O/(name+'.png'));chosen.save(O/(name+'.webp'),lossless=True,method=4);a.update(width=chosen.width,height=chosen.height,imageType='cutout',maskReview='Embedded source-PDF opacity mask retained; rembg mask rejected where it lost instrument parts');fixed.append(name)
# Preserve the two visually reviewed originals on white when segmentation would damage their edges/structure.
for name in ['page-059-xref-795','page-076-xref-1104']:
 if name not in assets:continue
 im=Image.open(O/'_originals'/(name+'-upscaled-2x.png')).convert('RGBA')
 if name.endswith('1104'):
  padded=Image.new('RGBA',(im.width+64,im.height+64),'white');padded.alpha_composite(im,(32,32));im=padded
 im.save(O/(name+'.png'));im.save(O/(name+'.webp'),lossless=True);assets[name].update(width=im.width,height=im.height,imageType='scene',maskReview='Source photo retained on white to preserve edges and perforations.')
(F/'image-fallbacks.json').write_text(json.dumps([{'file':a['src'],'pdfPage':a['pdfPage'],'reason':a.get('maskReview','Source background retained.')}for a in assets.values()if a['imageType']=='scene'],indent=2))
(O/'prepared-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2));(F/'embedded-mask-review.json').write_text(json.dumps(fixed,indent=2));print('Restored PDF alpha',len(fixed))
