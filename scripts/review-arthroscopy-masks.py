from PIL import Image
import json,pathlib,numpy as np
R=pathlib.Path(__file__).resolve().parents[1];p=R/'public/images/products/conmed/arthroscopy/prepared-assets.json';a=json.load(open(p));names=['page-033-xref-876','page-033-xref-879','page-039-xref-992','page-040-xref-997','page-069-xref-1444','page-089-xref-1671','page-040-xref-1000','page-107-xref-1882']
for name in names:
 x=a[name]
 if 'enclosed white background cleared' in x['maskMethod']:continue
 f=R/'public'/x['src'].lstrip('/');im=Image.open(f).convert('RGBA');pixels=np.asarray(im).copy();rgb=pixels[:,:,:3].astype(float);white=rgb.min(2);background=np.clip((white-240)/15,0,1);pixels[:,:,3]=(pixels[:,:,3]*(1-background)).astype('uint8');Image.fromarray(pixels).save(f,'WEBP',lossless=True,method=4);x['maskMethod']+='; enclosed white background cleared after visual review of sutures and handle openings'
p.write_text(json.dumps(a,indent=2)+'\n')
