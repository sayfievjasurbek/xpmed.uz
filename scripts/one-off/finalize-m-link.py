"""Publish the verified M-Link system and link existing meniscal repair families."""
import json,subprocess,datetime,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/m-link-all-inside';path=R/'content/products/double-medical/m-link-all-inside-meniscal-repair-system.json';s=json.loads(path.read_text());assert not s['review']['flags'];s['status']='published';s.setdefault('publishedAt',datetime.datetime.now(datetime.timezone.utc).isoformat());s['review']['publicationDecision']='Owner-authorized publication after 600-DPI source review, seven triple-verified REF codes and complete Codex RU/EN translations.'
check=subprocess.run(['node','scripts/validate-system.mjs'],input=json.dumps(s),text=True,capture_output=True,cwd=R)
if check.returncode:raise ValueError(check.stdout+check.stderr)
path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
for ref in s['relatedSystemSlugs']:
 target=R/'content/products'/(ref+'.json');other=json.loads(target.read_text());back=F/'related-backups'/target.name;back.parent.mkdir(parents=True,exist_ok=True)
 if not back.exists():shutil.copyfile(target,back)
 other['relatedSystemSlugs']=list(dict.fromkeys(other.get('relatedSystemSlugs',[])+['double-medical/'+s['slug']]));target.write_text(json.dumps(other,ensure_ascii=False,indent=2)+'\n')
rpath=R/'reports/double-medical/m-link-all-inside.json';report=json.loads(rpath.read_text());report.update(status='published',surgicalTechniqueSteps=8,surgicalTechniqueIllustrations=14,codesFound=7,codesVerified=7,codes=json.loads((F/'verified-codes.json').read_text()),openRealFlags=[],pageNumbering='Printed pages 2–8 correspond to physical PDF pages 4–10. Implants/instruments are physical pages 11/12.',notes=['Approach (step 2) has no illustration in the source. Preserved as text only.','Surgical illustrations retain original inset diagrams and are never passed through rembg.','Only six device photographs received exact 2x Real-ESRGAN enhancement before rembg.']);report['systems'][0]['status']='published';rpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# M-Link All-Inside import report','','Published: 1 system. Open real flags: 0.','8 surgical technique steps, 14 intact source illustrations, 4 feature descriptions, 2 ordering tables.','7 REF codes verified against PSM3, PSM11, Apple Vision and visual 600-DPI crops.','','Printed features page 2 is PDF page 4; printed technique pages 3–8 are PDF pages 5–10.','Skipped PDF pages: 1, 2, 3, 13, 14, 15, 16. Approach has no source illustration.','','| REF | Description | PDF page |','|---|---|---:|']
for row in report['codes']:lines.append(f"| {row['REF']} | {row['name']['en']} | {row['pdfPage']} |")
(F/'REPORT.md').write_text('\n'.join(lines)+'\n');print('Published M-Link: 8 steps, 2 tables, 7 verified codes, 0 real flags')
