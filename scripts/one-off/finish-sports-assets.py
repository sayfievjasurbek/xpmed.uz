"""Prepare exact-2x transparent WebP assets, retaining every native source image."""
import json, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
import numpy as np
from rembg import new_session, remove

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports/double-medical/sports-medicine-catalogue'
OUT=ROOT/'public/images/products/double-medical/sports-medicine-catalogue'
UPSCALED=Path('/tmp/xpmed-sports-assets/output')
assets=json.loads((REPORT/'source-images.json').read_text())
os.environ.setdefault('REMBG_HOME','/tmp/xpmed-rembg-models')
session=new_session('u2netp',providers=['CPUExecutionProvider'])

def finish(entry):
    key,meta=entry
    original=Image.open(OUT/'_originals'/f'{key}.png').convert('RGBA')
    size=(original.width*2,original.height*2)
    enhanced=Image.open(UPSCALED/f'{key}.png').convert('RGB').resize(size,Image.Resampling.LANCZOS)
    original_rgb=Image.new('RGBA',original.size,'white');original_rgb.alpha_composite(original)
    delta=np.abs(np.asarray(enhanced.resize(original.size,Image.Resampling.LANCZOS),dtype=np.int16)-np.asarray(original_rgb.convert('RGB'),dtype=np.int16)).mean()
    if delta>42: raise RuntimeError(f'{key}: 2x source mismatch {delta:.1f}')
    source_alpha=original.getchannel('A').resize(size,Image.Resampling.LANCZOS)
    source_coverage=np.mean(np.asarray(source_alpha)>128)
    if meta['sourceAlpha'] and source_coverage<.9:
        # The manufacturer alpha mask is more faithful than an inferred rembg mask.
        # Run rembg for comparison, but retain the exact source silhouette.
        _=remove(enhanced,session=session)
        alpha=source_alpha
        kind='cutout';method='source alpha retained after rembg comparison'
    else:
        alpha=remove(enhanced,session=session).convert('RGBA').getchannel('A')
        area=np.mean(np.asarray(alpha)>128)
        if .015<area<.9:
            kind='cutout';method='rembg u2netp'
        else:
            kind='scene';method='original scene retained after rembg review'
            alpha=Image.new('L',size,255)
    img=enhanced.convert('RGBA');img.putalpha(alpha)
    if kind=='cutout':
        bbox=alpha.getbbox()
        if bbox:img=img.crop(bbox)
        canvas=Image.new('RGBA',(img.width+64,img.height+64));canvas.alpha_composite(img,(32,32));img=canvas
    img.save(OUT/f'{key}.png')
    img.save(OUT/f'{key}.webp',lossless=kind=='cutout',quality=90,method=6)
    return key,{**meta,'src':f'/images/products/double-medical/sports-medicine-catalogue/{key}.webp',
                'width':img.width,'height':img.height,'imageType':kind,
                'backgroundRemoval':method,
                'imageEnhancement':{'method':'Real-ESRGAN x4plus downsampled to exact 2x','scale':2,'originalSize':meta['originalSize'],'enhancedSize':list(size)}}

if __name__=='__main__':
    missing=[key for key in assets if not (UPSCALED/f'{key}.png').exists()]
    if missing:raise RuntimeError(f'{len(missing)} enhanced images missing')
    results={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(key,record) in enumerate(pool.map(finish,assets.items()),1):
            results[key]=record
            if i%25==0:print(i,len(assets),flush=True)
    (OUT/'prepared-assets.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print('prepared',len(results))
