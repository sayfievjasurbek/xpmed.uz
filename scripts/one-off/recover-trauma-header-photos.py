"""Four rotated plate photos overlap the header with white padding; keep their full artwork."""
import json,re,math
from pathlib import Path
import pymupdf as f
from PIL import Image
from catalog_image_geometry import native_image_dpi
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part1';A=R/'public/images/products/double-medical/trauma-catalogue';W=Path('/tmp/xpmed-trauma/native-artwork');P=F/'source-images.json';assets=json.loads(P.read_text());D=f.open(R/'catalogs-source/double-medical/trauma-catalogue.pdf');added=[]
for n in [22,82,85,194]:
    if any(a['pdfPage']==n for a in assets.values()):continue
    page=D[n-1];photos=[a for a in page.get_image_info()if(a['width'],a['height'])not in [(191,47),(173,47)]and a['bbox'][3]>.12*page.rect.height and a['bbox'][1]<.935*page.rect.height];assert len(photos)==1
    a=photos[0];b=f.Rect(a['bbox']);art=f.open();art.insert_pdf(D,from_page=n-1,to_page=n-1);pg=art[0];pg.clean_contents();blocked={}
    for info in pg.get_images(full=True):
        if tuple(info[2:4])in[(191,47),(173,47)]:blocked.setdefault(info[9],set()).add(info[7])
    contents=set(pg.get_contents());streams=contents|{i for i in range(1,art.xref_length())if art.xref_get_key(i,'Subtype')==('name','/Form')}
    for x in streams:
        data=art.xref_stream(x)
        if not data:continue
        for name in blocked.get(x,set())|(blocked.get(0,set())if x in contents else set()):data=re.sub(rb'/'+re.escape(name.encode())+rb'\s+Do\b',b'',data)
        art.update_stream(x,re.sub(rb'(?<![A-Za-z0-9/])(?:f\*?|S|s|B\*?|b\*?)(?=[^A-Za-z0-9]|$)',b'n',data))
    dpi=math.ceil(native_image_dpi(a));pix=pg.get_pixmap(dpi=dpi,clip=b,alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);name=f'page-{n:03}-recovered-01';im.save(A/'_originals'/(name+'.png'));im.save(W/'input'/(name+'.png'));extra=W/'recovered';extra.mkdir(exist_ok=True);im.save(extra/(name+'.png'));assets[name]={'name':name,'pdfPage':n,'bounds':[b.x0/page.rect.width,b.y0/page.rect.height,b.x1/page.rect.width,b.y1/page.rect.height],'nativeDpi':dpi,'originalSize':list(im.size),'captionFree':True,'sourceMethod':'Full native rotated photo bounding box, including source white padding above the body; outlined header and logo objects excluded'};added.append(name)
    art.close()
P.write_text(json.dumps(assets,indent=2)+'\n');(F/'recovered-header-photos.json').write_text(json.dumps(added,indent=2)+'\n');print('Recovered',added,'total',len(assets))
