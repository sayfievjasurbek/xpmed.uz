"""Clear the photographed white background, including plate holes, after rembg."""
import json,os
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'public/images/products/double-medical/trauma-catalogue';F=R/'reports/double-medical/trauma-catalogue-part1';assets=json.loads((A/'prepared-assets.json').read_text());native=json.loads((F/'source-images.json').read_text())
assert set(assets)==set(native),'Finish all source photos before final matte refinement'
for name,a in assets.items():
    im=Image.open(A/(name+'.png')).convert('RGBA');pixels=np.array(im);cap=np.clip((254-pixels[:,:,:3].min(axis=2).astype(float))*25.5,0,255).astype('uint8');pixels[:,:,3]=np.minimum(pixels[:,:,3],cap)
    out=Image.fromarray(pixels);box=out.getchannel('A').getbbox()
    if not box:raise ValueError('Empty cutout: '+name)
    out=out.crop(box);canvas=Image.new('RGBA',(out.width+64,out.height+64));canvas.alpha_composite(out,(32,32));out=canvas
    out.save(A/(name+'.png'));out.save(A/(name+'.webp'),lossless=True,method=0);a.update(width=out.width,height=out.height,imageType='cutout');a['matteRefinement']='Source-white background and apertures cleared; nonwhite product pixels retained; 32px padding'
(A/'prepared-assets.json').write_text(json.dumps(assets,indent=2)+'\n');print('Refined cutouts',len(assets))
