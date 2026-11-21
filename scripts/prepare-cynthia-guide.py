"""Extract a text-layer surgical guide without OCR, rembg or generated imagery."""
import json,io,hashlib
from pathlib import Path
import pymupdf as f
from PIL import Image
R=Path(__file__).resolve().parents[1];D=f.open(R/'catalogs-source/double-medical/cynthia-revision-surgical-guide.pdf');P=R/'public/images/products/double-medical/cynthia-revision-technique';F=R/'reports/double-medical/cynthia-revision-surgical-guide';P.mkdir(parents=True,exist_ok=True);(P/'_originals').mkdir(exist_ok=True)
def stepFor(n,cy):
 return {3:lambda y:'1'if y<.406 else'2.1',4:lambda y:'2.1'if y<.238 else'2.2'if y<.497 else'2.3',5:lambda y:'2.3'if y<.263 else'2.4',6:lambda y:'2.5'if y<.389 else'2.6',7:lambda y:'2.6',8:lambda y:'2.7'if y<.5 else'2.8',9:lambda y:'3.1'if y<.499 else'3.2',10:lambda y:'3.3'if y<.309 else'3.4',11:lambda y:'3.5',12:lambda y:'3.6',13:lambda y:'3.6',14:lambda y:'3.7'if y<.308 else'3.8',15:lambda y:'3.9',16:lambda y:'4'if y<.377 else'5.1'}[n](cy)
assets=[];blocks=[]
for n,page in enumerate(D,1):
 blocks.append({'pdfPage':n,'text':page.get_text(sort=True),'blocks':page.get_text('blocks')})
 if n<3 or n>17:continue
 images=sorted(page.get_image_info(xrefs=True),key=lambda a:(round(a['bbox'][1],1),a['bbox'][0]))
 for i,a in enumerate(images,1):
  b=a['bbox'];bounds=[b[0]/page.rect.width,b[1]/page.rect.height,b[2]/page.rect.width,b[3]/page.rect.height];step=stepFor(n,(bounds[1]+bounds[3])/2);name=f'step-{step.replace(".","-")}-p{n:02}-{i:02}';data=D.extract_image(a['xref']);(P/'_originals'/(name+'.'+data['ext'])).write_bytes(data['image']);pix=f.Pixmap(D,a['xref']);smask=next((entry[1] for entry in page.get_images(full=True) if entry[0]==a['xref']),0);pix=f.Pixmap(pix,f.Pixmap(D,smask)) if smask else pix;im=Image.frombytes('RGBA' if pix.alpha else 'RGB',(pix.width,pix.height),pix.samples);background=Image.new('RGB',im.size,'white');background.paste(im,mask=im.getchannel('A')) if pix.alpha else background.paste(im);im=background;im.save(P/(name+'.webp'),quality=94,method=6);assets.append({'src':'/images/products/double-medical/cynthia-revision-technique/'+name+'.webp','width':im.width,'height':im.height,'imageType':'scene','pdfPage':n,'printedPage':n-2,'sourceBounds':bounds,'step':step,'sourceXref':a['xref'],'sourceMethod':'Native embedded source photograph/illustration; no OCR, no rembg, no generated enhancement'})
(P/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(F/'direct-text.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n');print('Native source images',len(assets),'step counts', {step:sum(a['step']==step for a in assets)for step in dict.fromkeys(a['step']for a in assets)})
