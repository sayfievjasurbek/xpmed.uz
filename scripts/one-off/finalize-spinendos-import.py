"""Publish only flag-free SPINENDOS systems and retain a reproducible source audit."""
import json,random,re,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
from spinendos_source_corrections import apply_verification
R=Path(__file__).resolve().parents[1];F=R/'reports/spinendos/endoscopic-spine-surgery-system'
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
verification=apply_verification(json.loads((F/'verification.json').read_text()));dump(F/'verification.json',verification);expected={r['id']:r.get('catalogValue',r['value'])for r in verification['records']};systems=[];seen={};sample=[]
for p in sorted((R/'content/products/spinendos').glob('*.json')):
 s=json.loads(p.read_text());flags=[f for f in s['review']['flags']if f.get('status','open')not in ['resolved','dismissed']]
 for t in s['specTables']:
  for i,row in enumerate(t['rows']):
   src=t['rowSources'][i]
   for evidence in src['codeEvidence']:
    ident=evidence['id'];assert ident not in seen,'Duplicate source item';assert expected[ident]==row[1],'Code changed from verified source';seen[ident]=row[1]
   sample.append({'system':s['name'],'slug':s['slug'],'pdfPage':src['pdfPage'],'description':row[0],'code':row[1]})
 s['status']='draft'if flags else'published';s['review']['status']='source-reviewed-with-open-items'if flags else'published-source-reviewed'
 if not flags:s['review']['publishedAt']=datetime.now(timezone.utc).isoformat();s['review']['publicationReason']='Owner explicitly authorized publishing systems with zero real flags.'
 result=subprocess.run(['node','scripts/validate-system.mjs'],cwd=R,input=json.dumps(s),text=True,capture_output=True);assert result.returncode==0,result.stdout+result.stderr
 systems.append((p,s))
assert seen==expected,'Missing source entries'
for p,s in systems:dump(p,s)
flags=[{'system':s['name'],**flag}for _,s in systems for flag in s['review']['flags']];rows=random.Random(20261119).sample(sample,20);dump(F/'random-20-rows.json',rows)
checks={'checkedAt':datetime.now(timezone.utc).isoformat(),'attemptedUrls':['https://spinendos.com/','https://www.spinendos.com/','http://spinendos.com/','https://spinendos.de/'],'result':'German website unavailable: TLS handshake failure; no codes marked confirmed on spinendos.com.','brandDescriptionSource':'https://en.spinendos.com.cn/about.html','confirmedOnSpinendosCom':0};dump(F/'manufacturer-checks.json',checks)
report={'systemsCreated':len(systems),'published':sum(s['status']=='published'for _,s in systems),'drafts':sum(s['status']=='draft'for _,s in systems),'catalogEntriesFound':len(sample),'codesVerified':sum(bool(r['value'])for r in verification['records']),'requestableCatalogEntries':sum(bool(v)for v in seen.values()),'unavailableCatalogEntries':sum(v is None for v in seen.values()),'uniqueCodes':len({v for v in seen.values()if v}),'confirmedOnSpinendosCom':0,'openRealFlags':flags,'sourceCatalogCorrections':json.loads((F/'source-catalog-corrections.json').read_text()),'manufacturerChecks':checks,'imageFallbacks':json.loads((F/'image-fallbacks.json').read_text()),'random20Rows':rows};dump(F/'report.json',report)
lines=['# SPINENDOS Endoscopic Spine Surgery System',f"\nSystems: {report['systemsCreated']} created / {report['published']} published / {report['drafts']} drafts.",f"Codes: {len(sample)} printed catalog entries / {report['codesVerified']} verified / 0 confirmed on spinendos.com; {report['uniqueCodes']} unique codes.",'\nVerification: two independent 600-DPI Tesseract settings, Apple Vision, and Codex visual readings of disagreements. Original readings and source coordinates retained.','\n## Open real flags']
if not flags:lines.append('None.')
for f in flags:lines.append('- '+f['system']['en']+'; PDF pages '+', '.join(map(str,f.get('sourcePages',[f['pdfPage']])) )+': '+'; '.join(f['readings']))
lines+=['\n## Manufacturer checks','spinendos.com could not be reached (TLS handshake failure). No third-party code matches are counted as manufacturer confirmation. Company copy is based on the official SPINENDOS regional website: https://en.spinendos.com.cn/about.html.','\n## Source catalog corrections']
for c in report['sourceCatalogCorrections']:
 lines.append('- '+c['internalNote'] if c.get('internalNote') else f"- p.{c['pdfPage']}: {c['printed']} → {c['corrected']} ({c['code']}).")
lines.append(f"- {report['requestableCatalogEntries']} requestable entries; {report['unavailableCatalogEntries']} unavailable codes remain as rows with sales notes.")
lines+=['\n## Image review',f"{len(report['imageFallbacks'])} images retain their source backgrounds as scenes because a clean cutout would lose instrument parts. Original and exact 2x images are preserved in _originals."]
for a in report['imageFallbacks']:lines.append(f"- PDF p.{a['pdfPage']}: {a['file']}")
lines+=['- Separate outlined stars following codes are markers, not code characters; OCR readings a / # / * / stray 7 are retained in the evidence. Alphabetic H/L/S/C suffixes printed as part of codes are retained. No marker legend was supplied in the PDF.','\n## Random 20-row sample (seed 20261119)','| System | PDF page | Description | Code |','|---|---:|---|---|']
for r in rows:lines.append('| '+r['system']['en']+' | '+str(r['pdfPage'])+' | '+r['description']['en'].replace('|','/')+' | '+(r['code']or'—')+' |')
import csv
with (F/'random-20-rows.csv').open('w',newline='',encoding='utf-8-sig')as file:
 writer=csv.writer(file);writer.writerow(['System','PDF page','Description (EN)','Description (RU)','Code'])
 for r in rows:writer.writerow([r['system']['en'],r['pdfPage'],r['description']['en'],r['description']['ru'],r['code']])
import_report=R/'reports/spinendos/endoscopic-spine-surgery-system.json'
if import_report.exists():
 data=json.loads(import_report.read_text());statuses={s['slug']:s['status']for _,s in systems}
 for entry in data['systems']:
  entry['status']=statuses[entry['slug']];entry['flags']=next(s['review']['flags']for _,s in systems if s['slug']==entry['slug'])
 data['uncertainties']=[f for e in data['systems']for f in e['flags']]
 data.update(systemsPublished=report['published'],systemsDrafts=report['drafts']);dump(import_report,data)
(F/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:report[k]for k in ['systemsCreated','published','drafts','catalogEntriesFound','codesVerified','uniqueCodes','confirmedOnSpinendosCom']},ensure_ascii=False))
