"""Publish only the source-reviewed Part 3 families with zero real open issues."""
import json,hashlib,datetime,random,csv,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part3';p=json.loads((R/'scripts/profiles/double-medical-trauma-part3.json').read_text());qa=json.loads((F/'image-qa.json').read_text());assets=json.loads((F/'source-images.json').read_text());assert qa['status']=='reviewed'and set(qa['assetsReviewed'])==set(assets)
merges={s['slug']:s for s in p['merges']};protected=['name','shortDescription','description','status','sourcePdf','sourcePages','variants','specTables','features','hotspots','heroImage']
for file,checksum in json.loads((F/'existing-system-hashes.json').read_text()).items():
 path=R/file
 if path.stem not in merges:assert hashlib.sha256(path.read_bytes()).hexdigest()==checksum,'Earlier system changed: '+file
 else:
  backup=R/'reports/double-medical/trauma-catalogue/merge-backups'/p['sha256']/path.name;assert hashlib.sha256(backup.read_bytes()).hexdigest()==checksum
  old=json.loads(backup.read_text());after=json.loads(path.read_text())
  for key in protected:assert old.get(key)==after.get(key),(file,key)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();systems=[];flags=[];samples=[]
for source in p['systems']:
 path=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(path.read_text());assert s['refCodes']==source['refCodes'];assert set(s['sourcePages'])<=set(p['authorizedPhysicalPages']);openFlags=[f for f in s['review']['flags']if f.get('status')not in ['resolved','dismissed']];s['status']='draft'if openFlags else'published'
 if not openFlags:s['publishedAt']=now;s['review']['publicationDecision']='Owner authorized automatic publication after source review with zero real open flags; no REF inferred.'
 s['review']['imageQA']=qa['sourceComparison'];path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');systems.append(s);flags +=[{'system':s['name'],'slug':s['slug'],**flag}for flag in openFlags]
for s in p['systems']+p['merges']:
 for t in s.get('specTables',s.get('referenceTables',[])):
  for row in t['rows']:
   codes=[v for v in row[1:]if isinstance(v,str)and re.fullmatch(r'\d{8,9}[A-Za-z]?',v)]
   if codes:samples.append({'system':s['name'],'slug':s['slug'],'pdfPage':t['sourcePages'][0],'printedPage':t.get('printedPage'),'REF':' / '.join(codes),'size':row[0]})
sample=random.Random(20261121).sample(samples,20);audit=json.loads((F/'code-verification.json').read_text());reportPath=R/'reports/double-medical/trauma-catalogue-part3.json';report=json.loads(reportPath.read_text());published=sum(s['status']=='published'for s in systems);sets=sum(s.get('instrumentSet')is True for s in systems);collections=sum(s['subcategory']=='trauma-cases-optional-instruments'for s in systems)
report.update(systemsNew=len(systems),systemsMerged=len(merges),systemsPublished=published,systemsDraft=len(systems)-published,implantSystems=sum(s['category']=='trauma-implants'for s in systems),instrumentSets=sets,instrumentCollections=collections,codesFound=audit['bodyOccurrences']+audit['setHeaderOccurrences'],codesVerified=audit['bodyOccurrences']+audit['setHeaderOccurrences'],distinctCodes=audit['distinctCodes'],componentRefOccurrences=audit['bodyOccurrences'],setCodeOccurrences=audit['setHeaderOccurrences'],scope=p['scope'],authorizedPhysicalPages=p['authorizedPhysicalPages'],blankPages=p['blankPages'],openRealFlags=flags,uncertainties=flags,randomSample=sample,randomSampleSeed=20261121,newNames=[s['name']for s in systems],mergedNames=[s['name']for s in p['merges']],deduplication=p['existingMatchAudit'],relatedExistingSets=p['relatedExistingSets'],imagesExtracted=len(assets),imageQA=qa,sourceCatalogCorrections=json.loads((F/'source-catalog-corrections.json').read_text()),publicationDate=now)
for entry in report['systems']:
 s=next(s for s in systems if s['slug']==entry['slug']);entry.update(status=s['status'],flags=s['review']['flags'])
reportPath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(F/'random-sample-20.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n')
with(F/'random-sample-20.csv').open('w')as out:
 w=csv.writer(out);w.writerow(['System RU','System EN','PDF page','Printed page','REF','Size/description RU','Size/description EN'])
 for row in sample:w.writerow([row['system']['ru'],row['system']['en'],row['pdfPage'],row['printedPage'],row['REF'],row['size']['ru'],row['size']['en']])
lines=['# Double Medical Trauma Catalogue — Part 3','',f'New systems: {len(systems)}; published: {published}; drafts: {len(systems)-published}; additive merges: {len(merges)}.',f'Implant/component families: {report["implantSystems"]}; instrument sets: {sets}; instrument/case collections: {collections}.',f'Printed REF occurrences found / verified: {report["codesFound"]} / {report["codesVerified"]}; {audit["distinctCodes"]} distinct codes. Verification confirms what is printed; source duplicate handling is documented below.',f'Images: {len(assets)}. Original native photos retained; Real-ESRGAN exact 2x before rembg; two original scene photos retained after failed ring-interior masks.','','## Source ranges']
for sc in p['scope']:lines.append(f'- Section {sc["section"]} {sc["en"]}: PDF {sc["physicalPages"][0]}–{sc["physicalPages"][1]}; index {sc["indexPage"]} excluded.')
lines+=['','## Existing systems merged']
for s in p['merges']:lines.append(f'- {s["name"]["en"]} / {s["name"]["ru"]}: PDF {s["sourcePages"]}, matched by {s["matchedBy"]}; earlier descriptions, material tables, hero and publication preserved. New material/dimension rows remain separate from the old rows.')
lines+=['','All earlier system JSON files are byte-identical except the documented additive Cable merge. No sections 1–8 were re-imported.','','## Open real issues']
for f in flags:lines.append(f'- {f["system"]["en"]}, PDF {f.get("pdfPage")}: {f["code"]}; readings {json.dumps(f.get("readings"),ensure_ascii=False)}')
if not flags:lines.append('None.')
lines+=['','## Source corrections / source index issues']
for c in report['sourceCatalogCorrections']:lines.append(f'- PDF {c["pdfPage"]}: {c["issue"]}')
lines+=['','## Random sample of 20 rows','','| System | PDF page | REF | Size / description |','|---|---:|---|---|']
for row in sample:lines.append(f'| {row["system"]["en"]} | {row["pdfPage"]} | {row["REF"]} | {row["size"]["en"]} |')
lines+=['','## All new system names']
for s in systems:lines.append(f'- {s["name"]["en"]} / {s["name"]["ru"]} — {s["status"]}; PDF {", ".join(map(str,s["sourcePages"]))}')
(F/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:report[k]for k in ['systemsNew','systemsMerged','systemsPublished','systemsDraft','implantSystems','instrumentSets','instrumentCollections','codesFound','codesVerified','distinctCodes','imagesExtracted']}))
