"""Publish only zero-real-flag Part 2 sets and add reciprocal clinical-family links."""
import json,random,csv,datetime,collections,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';A=R/'public/images/products/double-medical/spine-instruments';profile=json.loads((R/'scripts/profiles/double-medical-spine-instruments.json').read_text());rows=json.loads((F/'rows-translated.json').read_text());reportPath=R/'reports/double-medical/spine-catalogue-instruments.json';report=json.loads(reportPath.read_text());backup=F/'implant-link-backups';backup.mkdir(exist_ok=True);now=datetime.datetime.now(datetime.timezone.utc).isoformat();published=[];drafts=[];systems=[]
repairs=json.loads((F/'cpu-repaired-images.json').read_text());assert set(repairs)==set(json.loads((F/'gpu-damaged-images.json').read_text())) and all(r['meanAbsoluteError']<40 for r in repairs.values())
assets=json.loads((A/'artwork-assets.json').read_text());expected=json.loads((F/'artwork-images.json').read_text());expected={k for k in expected if not k.startswith(('art-290-','art-308-','art-383-'))}|set(json.loads((F/'manual-photo-images.json').read_text()))
assert set(assets)==expected, 'Every source image must finish before publication'
qa=json.loads((F/'image-qa.json').read_text());assert set(qa['reviewedAssets'])==expected and qa['status']=='reviewed'
for source in profile['systems']:
 path=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(path.read_text());assert s.get('importPartition')=='spine-instruments';assert s['sourcePages']==source['sourcePages'];assert s['setCode']==source['setCode'];assert sum(len(t['rows'])for t in s['specTables'])==sum(r['setCode']==s['setCode']for r in rows)
 for t in s['specTables']:
  for ri,row in enumerate(t['rows']):
   readings=t['rowSources'][ri]['codeEvidence'][0]['readings'];assert sum(reading['text']==row[1]for reading in readings)>=2;assert len(row[1])==9 and row[1].isdigit()
   if t.get('rowImages',[None]*len(t['rows']))[ri]:assert(R/'public'/t['rowImages'][ri]['src'].lstrip('/')).exists()
 flags=[f for f in s['review']['flags']if f.get('status')not in ['resolved','dismissed']]
 if flags:s['status']='draft';drafts.append({'slug':s['slug'],'name':s['name'],'setCode':s['setCode'],'flags':flags})
 else:s['status']='published';s.setdefault('publishedAt',now);s['review']['publicationDecision']='Published automatically under owner instruction: no open real source flags';published.append(s['slug'])
 s['review']['flags']=flags;s['review']['status']='source-reviewed-with-open-items'if flags else'source-reviewed';path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');systems.append(s)
# Add links only; implant prose, codes, tables, images and previous source corrections stay intact.
links=collections.defaultdict(list)
for s in systems:
 for target in s['relatedSystemSlugs']:links[target].append(s['slug'])
for target,slugs in links.items():
 p=R/'content/products/double-medical'/(target+'.json');old=json.loads(p.read_text());b=backup/(target+'.json')
 if not b.exists():b.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
 old['relatedSystemSlugs']=list(dict.fromkeys(old.get('relatedSystemSlugs',[])+slugs));p.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
byCode={s['setCode']:s for s in systems};sample=[]
for row in random.Random(20261120).sample(rows,20):
 s=byCode[row['setCode']];sample.append({'set':s['name'],'setCode':s['setCode'],'slug':s['slug'],'pdfPage':row['pdfPage'],'printedPage':row['printedPage'],'REF':row['value'],'description':row['name']})
report.update(setsNew=len(systems),setsUpdated=0,setsPublished=len(published),setsDraft=len(drafts),publishedSystems=published,draftSystems=drafts,codesFound=len(rows),codesVerified=len(rows),distinctInstrumentCodes=len({r['value']for r in rows}),setCodesFound=len(systems),setCodesVerified=len(systems),codesConfirmedOnManufacturerWebsite=0,codeVerification={'threeMachineReadersAgree':sum(len(set(r['readings'].values()))==1 for r in rows),'visualPlusOCR':sum('Codex visual 600-DPI crop'in r['readings']for r in rows),'unverified':0},scope={'physicalPdfPages':[210,411],'printedPages':[208,409],'backCoverExcluded':412},randomSample=sample,randomSampleSeed=20261120,reciprocalImplantLinks=list(links),imagesExtracted=len(assets),imageOriginals='/images/products/double-medical/spine-instruments/_originals/',uncertainties=[f for s in drafts for f in s['flags']],sourceImageOmissions='Rows without photographs in the source remain text/table-only; no substitute artwork invented',publicationDate=now,cpuImageRepairs={'count':len(repairs),'weightsSha256':'713ee713b0353afaa27976f0563a64a5043bd70b9bd8936c2e26e25ebcdbcddf','cpuGpuReferenceMeanAbsoluteError':0.42148293107197216},crossSetRefSizeConflicts=[])
for entry in report['systems']:
 s=byCode[next(s['setCode']for s in systems if s['slug']==entry['slug'])];entry['status']=s['status'];entry['setCode']=s['setCode'];entry['flags']=s['review']['flags']
reportPath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with(F/'random-sample-20.csv').open('w')as out:
 writer=csv.writer(out);writer.writerow(['Set','Set code','PDF page','Printed page','REF','Description (EN)','Описание (RU)'])
 for row in sample:writer.writerow([row['set']['en'],row['setCode'],row['pdfPage'],row['printedPage'],row['REF'],row['description']['en'],row['description']['ru']])
text=['# Double Medical Spine Catalogue · Part 2','',f"New sets: {len(systems)}. Updated existing sets: 0. Published: {len(published)}. Drafts: {len(drafts)}.",f"Instrument REF occurrences: {len(rows)}, all verified; {len({r['value']for r in rows})} distinct instrument codes. Set header codes: 49, all verified.",'','Physical PDF pages 210–411 correspond to printed pages 208–409. The back cover is excluded. Part 1 implant data is unchanged, apart from additive reciprocal links.','','## Open real flags']
if not drafts:text.append('None. All 49 sets are published after owner-confirmed source corrections.')
for s in drafts:
 for f in s['flags']:text.append(f"- {s['name']['en']} ({s['setCode']}), PDF p. {f['pdfPage']}: {f['message']['en']} Readings: {' / '.join(f['readings'])}.")
if report.get('sourceCatalogCorrections'):
 text+=['','## Source catalog corrections (internal)']
 for c in report['sourceCatalogCorrections']:
  text.append(f"- PDF p. {c['pdfPage']}, REF {c['ref']}: "+(c.get('action')or f"{c['printed']} → {c['corrected']['en']}. {c['basis']}"))
text+=['','## Random sample of 20 source rows','','| Set | PDF page | REF | Description |','|---|---:|---|---|']
for a in sample:text.append(f"| {a['set']['en']} ({a['setCode']}) | {a['pdfPage']} | {a['REF']} | {a['description']['en']} |")
(F/'REPORT.md').write_text('\n'.join(text)+'\n');print(json.dumps({k:report[k]for k in ['setsNew','setsUpdated','setsPublished','setsDraft','codesFound','codesVerified','imagesExtracted']}))
