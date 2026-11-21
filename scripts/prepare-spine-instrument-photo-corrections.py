"""Visually aligned source photographs on three irregular pages; source PDF stays untouched."""
import json,re
from pathlib import Path
import pymupdf as f,numpy as np,cv2
from PIL import Image
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';A=R/'public/images/products/double-medical/spine-instruments';W=Path('/tmp/xpmed-spine-instruments/manual');regions=json.loads((R/'scripts/profiles/spine-instruments-photo-regions.json').read_text());D=f.open(R/'catalogs-source/double-medical/spine-catalogue.pdf');assets={}
(W/'input').mkdir(parents=True,exist_ok=True);(W/'output').mkdir(exist_ok=True)
for page in [290,308,383]:
 doc=f.open();doc.insert_pdf(D,from_page=page-1,to_page=page-1);p=doc[0];p.clean_contents()
 for xref in p.get_contents():doc.update_stream(xref,re.sub(rb'(?<![A-Za-z0-9/])(?:f\*?|S|s|B\*?|b\*?)(?=[^A-Za-z0-9]|$)',b'n',doc.xref_stream(xref)))
 dpi=300;pix=p.get_pixmap(dpi=dpi,alpha=False);full=np.array(Image.frombytes('RGB',(pix.width,pix.height),pix.samples));h,w=full.shape[:2]
 for row,b in regions[str(page)].items():
  x0,y0,x1,y1=[int(v*d)for v,d in zip(b,[w,h,w,h])];arr=full[y0:y1,x0:x1].copy();mask=(arr.min(axis=2)<244).astype('uint8');n,labels,stats,centroids=cv2.connectedComponentsWithStats(cv2.dilate(mask,np.ones((3,3),np.uint8)),8);main=max(range(1,n),key=lambda k:stats[k][4]);arr[labels!=main]=255;yy,xx=np.where((arr.min(axis=2)<244));arr=arr[max(0,yy.min()-2):min(len(arr),yy.max()+3),max(0,xx.min()-2):min(arr.shape[1],xx.max()+3)];im=Image.fromarray(arr);name=f'reviewed-{page}-{row}';im.save(A/'_originals'/(name+'.png'));im.save(W/'input'/(name+'.png'));assets[name]={'name':name,'originalSize':list(im.size),'captionFree':True,'sourceMethod':'Codex-verified source photograph ROI; native PDF masks/transforms, printed captions excluded','placements':[{'pdfPage':page,'printedPage':page-2,'sourceRowId':f'{page}-{row}','bounds':b}]}
(F/'manual-photo-images.json').write_text(json.dumps(assets,indent=2));print(len(assets),'source photos')
