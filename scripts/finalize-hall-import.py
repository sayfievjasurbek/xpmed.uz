"""Validate all source evidence, publish clean HALL families, and emit the requested audit sample."""
import json,re,random,collections,subprocess,csv,sys
from pathlib import Path
from datetime import datetime,timezone
from finalize_translation_loader import finalize_translation
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';profile=json.loads((R/'scripts/profiles/conmed-hall-powered-instruments.json').read_text());verification=json.loads((F/'verification.json').read_text());byid={r['id']:r for r in verification['records']};systems=[];sample=[];evidenceRows=[]
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for incoming in profile['systems']:
 path=R/'content/products/conmed'/(incoming['slug']+'.json');s=json.loads(path.read_text());assert s['review']['sourceSha256']==profile['sha256']
 if any(a.get('drawing')and a['src']==s['heroImage']for a in s['gallery']):s['imageType']='cutout';incoming['imageType']='cutout'
 for ti,t in enumerate(s['specTables']):
  assert len(t['rows'])==len(t['rowSources'])
  assert len(t['rows'])==len(t['rowImages'])or not t.get('rowImages')
  for i,(row,source)in enumerate(zip(t['rows'],t['rowSources'])):
   assert len(row)==len(t['columns']),(s['slug'],t['id'],i)
   assert len(source['codeEvidence'])==1
   evidence=source['codeEvidence'][0];r=byid[evidence['id']];assert not r.get('excludedReason');assert row[1]==r['value']==evidence['value'];assert r['value'];assert len(r['readings'])>=3
   # A linked occurrence keeps printed specifications, but has only one canonical ordering owner.
   linked=any(link['row']==i+1 and link['column']==2 for link in t.get('codeLinks',[]));assert (row[1]in s['refCodes'])!=linked
   values={c['en']:row[j]['en']for j,c in enumerate(t['columns'])if j>1 and isinstance(row[j],dict)};dims=t['rowDimensions'][i]if i<len(t.get('rowDimensions',[]))else{}
   record={'system':s['name'],'slug':s['slug'],'pdfPage':source['pdfPage'],'code':row[1],'width':dims.get('width',''),'length':dims.get('length',''),'thickness':dims.get('thickness',''),'printedValues':values,'description':row[0],'officialConfirmed':bool(r.get('officialEvidence')),'verificationId':r['id']};sample.append(record);evidenceRows.append(r['id'])
 flags=[f for f in s['review']['flags']if f.get('status','open')not in ['resolved','dismissed']];s['status']='draft'if flags else'published';s['review']['status']='source-reviewed-with-open-items'if flags else'published-source-reviewed'
 if not flags:s['review']['publishedAt']=datetime.now(timezone.utc).isoformat();s['review']['publicationReason']='Owner authorized automatic publication of systems with zero real flags.'
 s=finalize_translation(s);check=subprocess.run(['node','scripts/validate-system.mjs'],cwd=R,input=json.dumps(s),text=True,capture_output=True);assert not check.returncode,check.stdout+check.stderr;systems.append((path,s))
# Every non-excluded code is represented; repeated image inscriptions are audited aliases, not extra products.
for r in verification['records']:
 if not r.get('excludedReason'):assert any(x['pdfPage']==r['pdfPage']and x['code']==r['value']for x in sample),(r['id'],r['value'])
for path,s in systems:dump(path,s)
dump(R/'scripts/profiles/conmed-hall-powered-instruments.json',profile)
flags=[{'system':s['name'],'slug':s['slug'],**flag}for _,s in systems for flag in s['review']['flags']if flag.get('status','open')not in ['resolved','dismissed']];overlaps=json.loads((F/'overlaps.json').read_text());rows=random.Random(20261119).sample([x for x in sample if x['width']and x['length']and x['thickness']],20)
report={'systemsCreated':len(systems),'published':sum(s['status']=='published'for _,s in systems),'drafts':sum(s['status']=='draft'for _,s in systems),'catalogNumbersFound':len(sample),'catalogNumbersVerified':len(sample),'confirmedInOfficialConmedDocuments':sum(x['officialConfirmed']for x in sample),'uniqueCatalogNumbers':len(set(x['code']for x in sample)),'publishedOverlapCodes':len(set(x['code']for x in overlaps['existingPublishedSystems'])),'overlaps':overlaps,'openRealFlags':flags,'imageFallbacks':json.loads((F/'image-fallbacks.json').read_text()),'random20Rows':rows,'sampleMethod':'Seed 20261119; random source rows with printed width, length and thickness; sample includes the imported systems. Thickness is the printed thickness subgroup if present, otherwise cut thickness.','officialDocument':'https://www.conmed.com/-/media/conmed/documents/catalog/hallpoweredinstruments_catalog.ashx','systems':[{'slug':s['slug'],'name':s['name'],'status':s['status'],'sourcePages':s['sourcePages'],'orderingRows':sum(len(t['rows'])for t in s['specTables']),'openFlags':len(s['review']['flags'])}for _,s in systems]};dump(F/'report.json',report);dump(F/'random-20-rows.json',rows)
corrections=[{'system':f['system'],'sourcePages':f.get('sourcePages',[f['pdfPage']]),'issue':f['message'],'readings':f['readings'],'visibility':'internal-only','status':'manufacturer clarification required'}for f in flags];corrections.append({'sourcePages':[59],'printed':'Image inscription 5059-07; ordering line 5059-007','used':'5059-007','visibility':'internal-only','status':'Order-line code retained; image inscription is not an extra ordering item.'});dump(F/'source-catalog-corrections.json',corrections)
with (F/'random-20-rows.csv').open('w',newline='',encoding='utf-8-sig')as file:
 writer=csv.writer(file);writer.writerow(['System','PDF page','Code','Width (mm)','Length (mm)','Thickness (mm)'])
 for r in rows:writer.writerow([r['system']['en'],r['pdfPage'],r['code'],r['width'],r['length'],r['thickness']])
lines=['# HALL Powered Instruments System',f"\nSystems: {report['systemsCreated']} created / {report['published']} published / {report['drafts']} drafts.",f"Catalog numbers: {report['catalogNumbersFound']} printed ordering occurrences / {report['catalogNumbersVerified']} verified / {report['confirmedInOfficialConmedDocuments']} confirmed in the official CONMED catalog; {report['uniqueCatalogNumbers']} unique codes.",f"Overlaps: {report['publishedOverlapCodes']} codes link to existing published systems; their printed dimensional rows remain available without creating another ordering owner.",'\n## Open real flags']
if not flags:lines.append('None.')
for f in flags:lines.append('- '+f['system']['en']+'; PDF pp. '+', '.join(map(str,f.get('sourcePages',[f['pdfPage']])) )+': '+'; '.join(f['readings']))
lines+=['\n## Verification','All 80 pages cached at 600 DPI. Product pages use Tesseract PSM3/11 and Apple Vision. Isolated PSM7/13 and Codex visual readings resolve disagreements. Original readings, coordinates, rejected aliases, and source page images are retained. No T-prefix substitutions were used.','Official confirmation checks exact codes in https://www.conmed.com/-/media/conmed/documents/catalog/hallpoweredinstruments_catalog.ashx; the current manufacturer catalog is a different edition, so its extra products were not imported.','Raw catalog code candidates, repeated picture inscriptions and compatibility references are not reported as separate ordering items.','\n## Images','Real-ESRGAN 2x photos precede rembg; embedded PDF transparency masks override damaged segmentation. Raw originals and enhanced copies are preserved in _originals. Only caption-matched visible photos are used; hidden PDF objects are not exposed. White blade drawings are 600-DPI source crops, never rembg. Gray drawing shading and the source bold-code chromium legend determine coating.','Two original photos are retained on white: the p.59 long sternum guard and the p.76 sterilization case.','\n## Random 20-row sample','Widths, lengths and thicknesses are printed source values, not inferred dimensions. '+report['sampleMethod'],'| System | PDF page | Code | Width | Length | Thickness |','|---|---:|---|---:|---:|---:|']
for r in rows:lines.append(f"| {r['system']['en']} | {r['pdfPage']} | {r['code']} | {r['width']} | {r['length']} | {r['thickness']} |")
(F/'report.md').write_text('\n'.join(lines)+'\n');importReport=R/'reports/conmed/hall-powered-instruments.json';data=json.loads(importReport.read_text());status={s['slug']:s['status']for _,s in systems}
for entry in data['systems']:
 entry['status']=status[entry['slug']];entry['flags']=next(s['review']['flags']for _,s in systems if s['slug']==entry['slug'])
data['uncertainties']=flags
data.update(systemsPublished=report['published'],systemsDrafts=report['drafts']);dump(importReport,data);print(json.dumps({k:report[k]for k in ['systemsCreated','published','drafts','catalogNumbersFound','catalogNumbersVerified','confirmedInOfficialConmedDocuments','uniqueCatalogNumbers','publishedOverlapCodes']}))
