"""Reassemble native embedded photos, excluding outlined printed text; Part 1 only."""
import json,re,math,hashlib,shutil
from pathlib import Path
import pymupdf as f
from PIL import Image
from catalog_image_geometry import native_image_dpi
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part1';A=R/'public/images/products/double-medical/trauma-catalogue';W=Path('/tmp/xpmed-trauma/native-artwork')
for p in [A/'_originals',W/'input',W/'output']:p.mkdir(parents=True,exist_ok=True)
previous=json.loads((F/'source-images-before-logo-cleanup.json').read_text())if(F/'source-images-before-logo-cleanup.json').exists()else{};changed=[];removed=[]
D=f.open(R/'catalogs-source/double-medical/trauma-catalogue.pdf');scope=json.loads((F/'scope.json').read_text());assets={}
for n in scope['authorizedPhysicalPages']:
    page=D[n-1];width,height=page.rect.width,page.rect.height
    photos=[a for a in page.get_image_info() if a['bbox'][3]>.12*height and a['bbox'][1]<.935*height and a['bbox'][0]>.08*width and min(a['width'],a['height'])>=8]
    # Square QR tiles at the bottom are catalog navigation, not product photos.
    photos=[a for a in photos if not(a['bbox'][1]>.81*height and (a['width'],a['height'])==(120,128))]
    rawPhotos=list(photos);photos=[a for a in photos if (a['width'],a['height'])not in [(191,47),(173,47)]]
    groups=[]
    for a in photos:
        box=f.Rect(a['bbox']);near=[g for g in groups if any((box+(-1,-1,1,1)).intersects(f.Rect(b['bbox'])) for b in g)]
        if near:
            joined=[a]+[b for g in near for b in g];groups=[g for g in groups if g not in near];groups.append(joined)
        else:groups.append([a])
    groups.sort(key=lambda g:min(a['bbox'][1] for a in g))
    dpi=min(600,max(150,math.ceil(max((native_image_dpi(a) for a in rawPhotos),default=150))))
    art=f.open();art.insert_pdf(D,from_page=n-1,to_page=n-1);pg=art[0];pg.clean_contents()
    blocked={}
    for info in pg.get_images(full=True):
        if tuple(info[2:4])in [(191,47),(173,47)]:blocked.setdefault(info[9],set()).add(info[7])
    pageStreams=set(pg.get_contents())
    streams=set(pg.get_contents())|{i for i in range(1,art.xref_length())if art.xref_get_key(i,'Subtype')==('name','/Form')}
    for x in streams:
        data=art.xref_stream(x)
        if data:
            for name in blocked.get(x,set())| (blocked.get(0,set())if x in pageStreams else set()):
                data=re.sub(rb'/'+re.escape(name.encode())+rb'\s+Do\b',b'',data)
            art.update_stream(x,re.sub(rb'(?<![A-Za-z0-9/])(?:f\*?|S|s|B\*?|b\*?)(?=[^A-Za-z0-9]|$)',b'n',data))
    usedNames={}
    for i,g in enumerate(groups,1):
        b=f.Rect(g[0]['bbox'])
        for a in g[1:]:b|=f.Rect(a['bbox'])
        old=[(k,a)for k,a in previous.items()if a['pdfPage']==n]
        def overlap(entry):
            a=entry[1];q=f.Rect(a['bounds'][0]*width,a['bounds'][1]*height,a['bounds'][2]*width,a['bounds'][3]*height);intersection=b&q
            return intersection.get_area()/max(b.get_area(),1)
        found=max(old,key=overlap)if old else None
        baseName=found[0]if found and overlap(found)>.5 else f'page-{n:03}-art-{i:02}'
        usedNames[baseName]=usedNames.get(baseName,0)+1;name=baseName if usedNames[baseName]==1 else baseName+f'-part-{usedNames[baseName]:02}'
        dpi=min(600,max(72,math.ceil(max(native_image_dpi(a)for a in g))))
        pix=pg.get_pixmap(dpi=dpi,clip=b,alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
        path=A/'_originals'/(name+'.png')
        if path.exists() and Image.open(path).convert('RGB').tobytes()!=im.tobytes():
            backup=A/'_originals/before-logo-cleanup';backup.mkdir(exist_ok=True);shutil.copy2(path,backup/path.name)if not(backup/path.name).exists()else None;changed.append(name)
        im.save(path);im.save(W/'input'/(name+'.png'))
        assets[name]={'name':name,'pdfPage':n,'bounds':[b.x0/width,b.y0/height,b.x1/width,b.y1/height],'originalSize':list(im.size),'nativeDpi':dpi,'captionFree':True,'sourceMethod':'Native embedded photo tiles reassembled with original transforms; outlined text removed in temporary PDF only'}
    art.close()
    print(n,len(groups),len(assets),flush=True)
(F/'source-images.json').write_text(json.dumps(assets,indent=2)+'\n')
removed=sorted(set(previous)-set(assets))
(F/'logo-cleanup.json').write_text(json.dumps({'removedNonProductLogos':removed,'replacedPhotoComposites':changed},indent=2)+'\n')
print('Native product photos',len(assets),'removed logos',len(removed),'changed photos',len(changed),flush=True)
