"""Independent local Vision OCR for the authorized instrument page range only."""
import subprocess,time,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'public/catalogs/double-medical/spine-catalogue/ocr';F=R/'reports/double-medical/spine-catalogue-instruments/vision';W=Path('/tmp/xpmed-spine-instruments/vision-input');W.mkdir(parents=True,exist_ok=True);F.mkdir(parents=True,exist_ok=True)
while True:
 for p in O.glob('*-600dpi.png'):
  if not 210<=int(p.name[:3])<=411:continue
  target=W/p.name
  if not target.exists():target.symlink_to(p)
 subprocess.run(['/tmp/spinendos-vision',str(W),str(F)],check=True)
 if len(list(F.glob('*.json')))>=202:break
 time.sleep(4)
print('Third reader finished authorized 202 instrument pages',flush=True)
