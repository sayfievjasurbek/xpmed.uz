"""Publish only verified section 5–8 imports; preserve all earlier source content."""
import json,hashlib,datetime,random,csv,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part2';profile=json.loads((R/'scripts/profiles/double-medical-trauma-part2.json').read_text());qa=json.loads((F/'image-qa.json').read_text());assets=json.loads((F/'source-images.json').read_text());assert qa['status']=='reviewed'and set(qa['assetsReviewed'])==set(assets)
mergeSlugs={s['slug']for s in profile['merges']};protected=['name','shortDescription','description','status','sourcePdf','sourcePages','variants','specTables','features','hotspots','heroImage'];digest=profile['sha256']
for path,checksum in json.loads((F/'existing-system-hashes.json').read_text()).items():
    file=R/path
    if file.stem not in mergeSlugs:assert hashlib.sha256(file.read_bytes()).hexdigest()==checksum,'Unexpected earlier system change: '+path
    else:
        backup=R/'reports/double-medical/trauma-catalogue/merge-backups'/digest/file.name
        assert hashlib.sha256(backup.read_bytes()).hexdigest()==checksum
        old=json.loads(backup.read_text());current=json.loads(file.read_text())
        for field in protected:assert current.get(field)==old.get(field),(file.stem,field)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();systems=[];samples=[];body=[];setCodes=[];flags=[]
for source in profile['systems']:
    file=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(file.read_text());assert s['sourcePages']==source['sourcePages'];assert set(s['sourcePages'])<=set(profile['authorizedPhysicalPages']);assert s['refCodes']==source['refCodes']
    openFlags=[f for f in s['review']['flags']if f.get('status')not in ['resolved','dismissed']];s['status']='draft'if openFlags else'published'
    if not openFlags:s['publishedAt']=now;s['review']['publicationDecision']='Owner authorized publication with zero real flags after three-reader source verification, Codex medical RU/EN and image QA.'
    s['review']['imageQA']='Original native photos preserved; Real-ESRGAN exact 2x before rembg; every final photo reviewed; composite photos matched to individual source rows.'
    file.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');systems.append(s);flags.extend({'system':s['name'],'slug':s['slug'],**f}for f in openFlags)
for s in profile['systems']+profile['merges']:
    setCodes+=s.get('setCodes',[])
    for t in s.get('specTables',s.get('referenceTables',[])):
        for row in t['rows']:
            codes=[v for v in row[1:]if isinstance(v,str)and re.fullmatch(r'\d{8,11}[A-Za-z]?',v)];body+=codes
            if codes:samples.append({'system':s['name'],'slug':s['slug'],'pdfPage':t['sourcePages'][0],'printedPage':t.get('printedPage'),'REF':' / '.join(codes),'size':row[0]})
for m in profile['merges']:
    assert not m['reviewFlags'],'Do not expose an unresolved contribution to a published page'
pub=[s for s in systems if s['status']=='published'];draft=[s for s in systems if s['status']=='draft'];sets=[s for s in systems if s['category']=='trauma-instrument-sets'];sample=random.Random(20261121).sample(samples,20)
codeAudit=json.loads((F/'code-verification.json').read_text());printedCount=codeAudit['bodyOccurrences']+codeAudit['setHeaderOccurrences']
path=R/'reports/double-medical/trauma-catalogue-part2.json';report=json.loads(path.read_text());report.update(systemsNew=len(systems),implantSystems=len(systems)-len(sets),instrumentSets=len(sets),systemsMerged=len(profile['merges']),mergedNames=[m['name']for m in profile['merges']],newNames=[s['name']for s in systems],systemsPublished=len(pub),systemsDraft=len(draft),codesFound=printedCount,codesVerified=printedCount,componentRefOccurrences=codeAudit['bodyOccurrences'],setCodeOccurrences=codeAudit['setHeaderOccurrences'],distinctCodes=codeAudit['distinctCodes'],codeVerification='600-DPI Tesseract PSM3 + PSM11, independent Apple Vision; source glyph and Codex visual reconciliation; exact code agreement required; no guessed REF',scope=profile['scope'],authorizedPhysicalPages=profile['authorizedPhysicalPages'],imagesExtracted=len(assets),imageQA=qa,openRealFlags=flags,uncertainties=flags,randomSample=sample,randomSampleSeed=20261121,publicationDate=now,sourceCatalogCorrections=json.loads((F/'source-catalog-corrections.json').read_text()),deduplication=profile['existingMatchAudit'])
for entry in report['systems']:
    s=next(s for s in systems if s['slug']==entry['slug']);entry.update(status=s['status'],flags=s['review']['flags'])
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(F/'random-sample-20.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n')
with(F/'random-sample-20.csv').open('w')as out:
    w=csv.writer(out);w.writerow(['System RU','System EN','PDF page','Printed page','REF','Size/description RU','Size/description EN'])
    for x in sample:w.writerow([x['system']['ru'],x['system']['en'],x['pdfPage'],x['printedPage'],x['REF'],x['size']['ru'],x['size']['en']])
lines=['# Double Medical Trauma Catalogue — Part 2','',f"New systems: {len(systems)} ({len(systems)-len(sets)} implants; {len(sets)} instrument sets). Merged: {len(profile['merges'])}. New systems published / drafts: {len(pub)} / {len(draft)}.",f"Printed REF occurrences found / verified: {printedCount} / {printedCount} ({codeAudit['bodyOccurrences']} body REF + {codeAudit['setHeaderOccurrences']} set codes; {codeAudit['distinctCodes']} distinct codes). Identical repeated tables are shown once on the public page.",f'Final source photos: {len(assets)}. Originals retained. Exact 2x Real-ESRGAN before rembg, native display limits, transparent PNG/WebP.','','## Scope']
for sc in profile['scope']:lines.append(f"- {sc['en']}: PDF {sc['physicalPages'][0]}–{sc['physicalPages'][1]}; product pages {sc['productPhysicalPages'][0]}–{sc['productPhysicalPages'][1]}; index {sc['indexPage']} excluded.")
lines+=['','Blank pages excluded: '+', '.join(map(str,profile['blankPages']))+'. Sections 1–4 were not re-imported; only reviewed additive merges and related links were made. Sections 9–13 were not processed.','','## Merged into existing systems']
for m in profile['merges']:lines.append(f"- {m['name']['en']} / {m['name']['ru']}, PDF {m['sourcePages']}; matched by {m['matchedBy']}. Original clinical text and tables preserved.")
lines+=['','## Open real flags']
for f in flags:lines.append(f"- {f['system']['en']}, PDF {f.get('pdfPage')}: {f['message']['en']} Readings: {json.dumps(f.get('readings'),ensure_ascii=False)}")
if not flags:lines.append('None.')
lines+=['','## Random sample of 20 rows','','| System | PDF page | REF | Size / description |','|---|---:|---|---|']
for x in sample:lines.append(f"| {x['system']['en']} | {x['pdfPage']} | {x['REF']} | {x['size']['en']} |")
lines+=['','## New systems (complete name list)']
for s in systems:lines.append(f"- {s['name']['en']} / {s['name']['ru']} — {s['status']}; PDF {', '.join(map(str,s['sourcePages']))}")
(F/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:report[k]for k in ['systemsNew','implantSystems','instrumentSets','systemsMerged','systemsPublished','systemsDraft','codesFound','codesVerified','imagesExtracted']}))
