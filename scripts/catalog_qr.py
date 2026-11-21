"""Decode QR locally from rendered source pixels; never execute/follow decoded URLs."""
import json
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
from PIL import Image
import zxingcpp

def decode_catalog_qrs(reference,evidence,product_pages):
    reference=Path(reference);cache=reference/'ocr/qr-results.json';digest=evidence[0]['sourceSha256']
    if cache.exists():
        saved=json.loads(cache.read_text())
        if saved.get('sourceSha256')==digest:return saved
    results=[];failures=[]
    for number in sorted(product_pages):
        dpi=next(p['dpi']for p in evidence if p['page']==number);image=Image.open(reference/'ocr'/f'{number:03}-{dpi}dpi.png').convert('RGB');width,height=image.size
        for barcode in zxingcpp.read_barcodes(np.asarray(image),return_errors=True):
            if 'QR' not in str(barcode.format):continue
            points=[barcode.position.top_left,barcode.position.top_right,barcode.position.bottom_left,barcode.position.bottom_right]
            bounds=[min(p.x for p in points)/width,min(p.y for p in points)/height,max(p.x for p in points)/width,max(p.y for p in points)/height]
            if not barcode.valid:failures.append({'page':number,'sourceBounds':bounds,'error':str(barcode.error)});continue
            url=barcode.text;parsed=urlparse(url);official=parsed.scheme in ['http','https']and(parsed.hostname=='conmed.com'or(parsed.hostname or '').endswith('.conmed.com'))
            kind='product-page'if official and '/products/'in parsed.path else 'manufacturer-literature'if official and '/media/'in parsed.path else 'manufacturer-reference'if official else 'external-video'if parsed.hostname in ['youtu.be','www.youtube.com','youtube.com']else 'external-reference'
            results.append({'page':number,'printedPage':number-2,'bounds':bounds,'url':url,'officialConmed':official,'resourceType':kind,'decoded':True,'decoder':'ZXing-C++ (local source pixels)','coordinateSpace':'normalized-page','urlAvailabilityChecked':False})
    saved={'sourceSha256':digest,'dpi':evidence[0]['dpi'],'qrs':results,'decodeFailures':failures};cache.write_text(json.dumps(saved,ensure_ascii=False,indent=2)+'\n');return saved
