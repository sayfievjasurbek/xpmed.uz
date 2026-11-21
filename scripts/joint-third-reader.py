"""Run the independent local reader as 600-DPI source pages become ready."""
import subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'public/catalogs/double-medical/joint-catalogue/ocr';F=R/'reports/double-medical/joint-catalogue/vision';W=Path('/tmp/dm-joint/vision-input');W.mkdir(parents=True,exist_ok=True);F.mkdir(parents=True,exist_ok=True)
while len(list(F.glob('*.json')))<96:
 for p in O.glob('*-600dpi.png'):
  target=W/p.name
  if not target.exists():target.symlink_to(p)
 subprocess.run(['/tmp/spinendos-vision',str(W),str(F)],check=True)
 if len(list(F.glob('*.json')))<96:time.sleep(3)
print('Independent third reader completed all 96 pages',flush=True)
