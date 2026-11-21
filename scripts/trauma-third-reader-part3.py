"""Independent local reader, bounded to authorized Trauma Part 3 pages."""
import json, subprocess, time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
scope=json.loads((R/'reports/double-medical/trauma-catalogue-part3/scope.json').read_text())
pages=set(scope['authorizedPhysicalPages'])
O=R/'public/catalogs/double-medical/trauma-catalogue/ocr'
F=R/'reports/double-medical/trauma-catalogue-part3/vision'
W=Path('/tmp/xpmed-trauma-part3/vision-input')
F.mkdir(parents=True,exist_ok=True);W.mkdir(parents=True,exist_ok=True)
while True:
    for p in O.glob('*-600dpi.png'):
        if int(p.name[:3]) not in pages: continue
        if not (W/p.name).exists(): (W/p.name).symlink_to(p)
    subprocess.run(['/tmp/spinendos-vision',str(W),str(F)],check=True)
    done={int(p.stem) for p in F.glob('*.json')}
    print(f'Third reader: {len(done & pages)}/{len(pages)}',flush=True)
    if pages<=done: break
    time.sleep(4)
