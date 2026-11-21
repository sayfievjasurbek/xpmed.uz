"""Owner-authorized publication of reviewed Trauma Part 1 systems with zero real flags."""
import json,hashlib,datetime,random,csv
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part1';profile=json.loads((R/'scripts/profiles/double-medical-trauma-part1.json').read_text());qa=json.loads((F/'image-qa.json').read_text());assets=json.loads((F/'source-images.json').read_text());assert qa['status']=='reviewed'and set(qa['assetsReviewed'])==set(assets)
for path,digest in json.loads((F/'existing-system-hashes.json').read_text()).items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,'Existing system was modified: '+path
now=datetime.datetime.now(datetime.timezone.utc).isoformat();systems=[];sampleRows=[];bodyCodes=[];setCodes=[];flags=[]
for source in profile['systems']:
    path=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(path.read_text());assert s['refCodes']==source['refCodes'];assert s['sourcePages']==source['sourcePages'];assert set(s['sourcePages'])<=set(profile['authorizedPhysicalPages'])
    openFlags=[f for f in s['review']['flags']if f.get('status')not in ['resolved','dismissed']]
    s['status']='draft'if openFlags else'published'
    if not openFlags:s['publishedAt']=now;s['review']['publicationDecision']='Owner authorized automatic publication: exact source REF verification, Codex-authored RU/EN, complete image QA, zero open real flags'
    s['review']['imageQA']='All source photos checked visually; native resolution corrected for rotations; Real-ESRGAN exact 2x, rembg, source-white aperture cleanup; originals retained.'
    path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');systems.append(s);setCodes+=s.get('setCodes',[])
    flags.extend({'system':s['name'],'slug':s['slug'],**f}for f in openFlags)
    for t in s['specTables']:
        for i,row in enumerate(t['rows']):
            codes=[v for v in row[1:]if isinstance(v,str)and v and len(v)==9 and v.isdigit()];bodyCodes+=codes
            if codes:sampleRows.append({'system':s['name'],'slug':s['slug'],'pdfPage':t['sourcePages'][0],'printedPage':t.get('printedPage'),'REF':' / '.join(codes),'size':row[0]})
published=[s for s in systems if s['status']=='published'];drafts=[s for s in systems if s['status']=='draft'];sample=random.Random(20261120).sample(sampleRows,20)
p=R/'reports/double-medical/trauma-catalogue-part1.json';report=json.loads(p.read_text());report.update(systemsNew=len(systems),implantSystems=205,instrumentSets=19,systemsMerged=0,mergedNames=[],systemsPublished=len(published),systemsDraft=len(drafts),codesFound=len(bodyCodes)+len(setCodes),codesVerified=len(bodyCodes)+len(setCodes),componentRefOccurrences=len(bodyCodes),setCodeOccurrences=len(setCodes),distinctCodes=len(set(bodyCodes+setCodes)),codeVerification='600-DPI Tesseract PSM3 and PSM11 + independent Apple Vision; every printed code has at least two exact high-confidence readings; source prefix anomaly is held despite verified reading',scope=profile['scope'],authorizedPhysicalPages=profile['authorizedPhysicalPages'],imagesExtracted=len(assets),imageQA=qa,openRealFlags=flags,uncertainties=flags,randomSample=sample,randomSampleSeed=20261120,publicationDate=now,sourceCatalogCorrections=json.loads((F/'source-catalog-corrections.json').read_text()),missingSourceCodeRows=1)
for entry in report['systems']:
    s=next(s for s in systems if s['slug']==entry['slug']);entry['status']=s['status'];entry['flags']=s['review']['flags']
p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(F/'random-sample-20.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n')
with(F/'random-sample-20.csv').open('w')as out:
    writer=csv.writer(out);writer.writerow(['System RU','System EN','PDF page','Printed page','REF','Size/description RU','Size/description EN'])
    for r in sample:writer.writerow([r['system']['ru'],r['system']['en'],r['pdfPage'],r['printedPage'],r['REF'],r['size']['ru'],r['size']['en']])
lines=['# Double Medical Trauma Catalogue · Part 1','',f'New systems: {len(systems)} (205 implant families + 19 instrument-set families). Merged: 0. Published: {len(published)}. Drafts: {len(drafts)}.',f'Catalog numbers found / verified: {len(bodyCodes)+len(setCodes)} / {len(bodyCodes)+len(setCodes)} ({len(bodyCodes)} component/size REF occurrences + {len(setCodes)} set codes). One source item has no printed REF.','',f'Images: {len(assets)}; native-resolution source extraction, exact 2x Real-ESRGAN, rembg, transparent PNG/WebP. Originals retained. All images visually reviewed.','','## Authorized PDF ranges']
for scope in profile['scope']:lines.append(f"- {scope['en']}: product PDF pages {scope['productPhysicalPages'][0]}–{scope['productPhysicalPages'][1]} ({scope['productPrintedPages']}); section index {scope['indexPage']} excluded.")
lines+=['','Cover, about, main index, blank pages and section indexes excluded. No products from sections 5–13 were imported. The source PDF remains in catalogs-source/double-medical/trauma-catalogue.pdf.','','## Open real flags']
for flag in flags:lines.append(f"- **{flag['system']['en']}**, PDF p. {flag['pdfPage']}: {flag['message']['en']} Readings: {json.dumps(flag.get('readings',[]),ensure_ascii=False)}")
lines+=['','## Random sample of 20 rows','','| System | PDF page | REF | Size / description |','|---|---:|---|---|']
for r in sample:lines.append(f"| {r['system']['en']} | {r['pdfPage']} | {r['REF']} | {r['size']['en']} |")
lines+=['','## New systems (all names)']
for s in systems:lines.append(f"- {s['name']['en']} / {s['name']['ru']} — {s['status']}; PDF {', '.join(map(str,s['sourcePages']))}")
(F/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:report[k]for k in ['systemsNew','implantSystems','instrumentSets','systemsMerged','systemsPublished','systemsDraft','codesFound','codesVerified','imagesExtracted']}))
