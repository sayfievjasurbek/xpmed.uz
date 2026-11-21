"""Clear the photographed white background, including plate holes, after rembg."""
import json,os
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'public/images/products/double-medical/trauma-catalogue-part2';F=R/'reports/double-medical/trauma-catalogue-part2';assets=json.loads((A/'prepared-assets.json').read_text());native=json.loads((F/'source-images.json').read_text())
assert set(assets)==set(native),'Finish all source photos before final matte refinement'
for name,a in assets.items():
    im=Image.open(A/(name+'.png')).convert('RGBA');pixels=np.array(im);cap=np.clip((254-pixels[:,:,:3].min(axis=2).astype(float))*25.5,0,255).astype('uint8');pixels[:,:,3]=np.minimum(pixels[:,:,3],cap)
    if a.get('sourceComposite')=='page-440-art-01':
        count,labels,stats,centers=cv2.connectedComponentsWithStats((pixels[:,:,3]>32).astype('uint8'),8)
        main=1+int(np.argmax(stats[1:,4]));mainTop=stats[main,1]
        for lab in range(1,count):
            x,y,w,h,area=stats[lab]
            if lab!=main and x<im.width*.25 and w<im.width*.3 and h/max(w,1)<.12:pixels[labels==lab,3]=0
    out=Image.fromarray(pixels);box=out.getchannel('A').getbbox()
    if not box:raise ValueError('Empty cutout: '+name)
    out=out.crop(box);canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas
    out.save(A/(name+'.png'));out.save(A/(name+'.webp'),lossless=True,method=0);a.update(width=out.width,height=out.height,imageType='cutout');a['matteRefinement']='Source-white background and apertures cleared; nonwhite product pixels retained; 32px padding'
(A/'prepared-assets.json').write_text(json.dumps(assets,indent=2)+'\n');print('Refined cutouts',len(assets))
