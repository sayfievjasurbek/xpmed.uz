"""Publish only implant systems with zero real flags; report both legacy merges."""
import json,datetime,random,secrets,csv,subprocess,collections
from pathlib import Path
from spine_owner_resolutions import apply as apply_owner, decisions as owner_decisions
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue';P=json.loads((R/'scripts/profiles/double-medical-spine-catalogue.json').read_text());report=json.loads((R/'reports/double-medical/spine-catalogue.json').read_text());published=[];drafts=[];flags=[]
for template in P['systems']:
 path=R/'content/products/double-medical'/(template['slug']+'.json');s=apply_owner(json.loads(path.read_text()),P['sha256']);assert s['review']['sourceSha256']==P['sha256'];actual=[f for f in s['review']['flags']if f.get('status','open')!='resolved'];s['status']='draft'if actual else'published';s['review']['publicationDecision']='Draft: real source REF-size contradictions remain.'if actual else'Published under owner authorization after source verification; zero real flags.'
 if not actual:s['review'].setdefault('publishedAt',datetime.datetime.now(datetime.timezone.utc).isoformat());published.append(s['slug'])
 else:drafts.append(s['slug'])
 check=subprocess.run(['node','scripts/validate-system.mjs'],input=json.dumps(s),text=True,capture_output=True,cwd=R)
 if check.returncode:raise ValueError(check.stdout+check.stderr)
 path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');flags.extend({'system':s['name'],'slug':s['slug'],**f}for f in actual)
 for entry in report['systems']:
  if entry['slug']==s['slug']:entry.update(status=s['status'],flags=actual,resolvedFlags=s['review'].get('resolvedFlags',[]))
# Clinical prose, original source assets, variants and old sizes are protected on both merges.
merge_results=[]
for patch in P['merges']:
 s=json.loads((R/'content/products/double-medical'/(patch['slug']+'.json')).read_text());before=json.loads((F/'merge-backups'/P['sha256']/(patch['slug']+'.json')).read_text())
 for key in ['name','shortDescription','description','features','specTables','variants','heroImage','sourcePdf','sourcePages','status']:assert s.get(key)==before.get(key),(patch['slug'],key)
 merge_results.append({'slug':s['slug'],'name':s['name'],'tablesAdded':len(patch['referenceTables']),'codesAdded':len(patch['refCodes']),'textPreserved':True,'status':s['status']})
rows=json.loads((F/'all-rows.json').read_text());samplefile=F/'random-sample-20.json'
if samplefile.exists():sample=json.loads(samplefile.read_text())
else:
 seed=secrets.token_hex(12);rng=random.Random(seed);groups=collections.defaultdict(list)
 for row in rows:groups[row['slug']].append(row)
 chosen=[rng.choice(group)for group in groups.values()];chosen+=rng.sample([r for r in rows if r not in chosen],20-len(chosen));rng.shuffle(chosen);sample={'method':'Stratified random sample: one row from each implant family plus two extra random rows','seed':seed,'rows':chosen};samplefile.write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n')
with(F/'random-sample-20.csv').open('w',newline='')as file:
 w=csv.DictWriter(file,fieldnames=['system','slug','pdfPage','printedPage','REF','size']);w.writeheader();w.writerows(sample['rows'])
V=json.loads((F/'verification.json').read_text());report.update(systemsCreated=16,systemsMerged=2,newSystemsPublished=len(published),newSystemsDraft=len(drafts),publishedSystems=published,draftSystems=drafts,mergedIntoExisting=merge_results,codesFound=V['found'],codesVerified=V['verified'],uniqueCodes=len({r['value']for r in V['records']}),tablesCreated=sum(len(s['referenceTables'])for s in P['systems']+P['merges']),imagesExtracted=len(P['assets']),sourceRange={'printedPages':[2,207],'physicalPdfPages':[4,209],'instrumentsStartPhysicalPdfPage':210,'pages208AndLaterPrintedNotImported':True},contentsNote='The source contents lists 18 implant entries, not 19. No extra family was invented. Some running headers and contents boundaries mislabel HOBBIT components; specific printed component names govern their family assignment.',uncertainties=flags,sourceCatalogCorrections=[{'REF':f['refCode'],'system':f['system'],'pdfPages':f['sourcePages'],'readings':f['readings'],'action':'Keep both source values; confirm correct REF with Double Medical.'}for f in flags],randomSample=sample['rows'],imageReview=json.loads((F/'image-review.json').read_text()),existingMatchAudit=json.loads((F/'existing-match-audit.json').read_text()),sourcePatternExceptions=json.loads((F/'source-pattern-exceptions.json').read_text()),clinicalConflictsWithLegacy=[])
owner=owner_decisions(P['sha256'])
if owner:
 report['sourceCatalogCorrections']=owner['corrections']
 report['requestableRefOccurrences']=V['found']-1
 report['unavailableRefOccurrences']=1
 report['publicationNote']='All implant systems published after owner-confirmed source corrections; the unconfirmed height-12 cage REF remains unavailable for ordering.'
(R/'reports/double-medical/spine-catalogue.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# Double Medical Spine Catalogue — Part 1: implants','',f"16 new systems: {len(published)} published, {len(drafts)} drafts. 2 existing systems updated.",f"{V['found']} printed REF occurrences; {V['verified']} source-verified; {report['uniqueCodes']} distinct codes. {report['tablesCreated']} tables; {report['imagesExtracted']} reviewed product images.",'','Only printed pages 2–207 (physical PDF pages 4–209) imported. Instruments beginning at printed page 208 / PDF page 210 were excluded. The source contents has 18 implant entries, not 19.','','## Merged into existing pages','']
lines += [f"- {m['name']['ru']} / {m['name']['en']}: {m['tablesAdded']} REF tables added; current text, old size tables and primary source retained."for m in merge_results]
lines+=['','## New systems','']+[f"- {s['name']['ru']} / {s['name']['en']} — {'draft'if s['slug']in drafts else'published'}."for s in P['systems']]
lines+=['','## Open real source issues','']
if not flags:lines.append('None. All six owner decisions applied; the uncertain cage REF is withheld from ordering.')
for issue in flags:
 lines.append('- '+issue['system']['en']+' — REF '+issue['refCode']+': '+'; '.join('PDF p. '+str(x['pdfPage'])+' → '+' / '.join(x['values'][1:])for x in issue['readings'])+'. The printed REF is the same; both values are retained pending manufacturer confirmation.')
if owner:
 lines+=['','## Source catalog corrections','']+['- '+c['correction']for c in owner['corrections']]
lines+=['','The six original contradictions were visually confirmed on 600-DPI source crops and resolved by explicit owner instructions. The uncertain height-12 cage REF is withheld rather than inferred. No clinical conflict was found with the two legacy products. Codes with internal letters (e.g. 09A and 08C) are retained exactly as printed; documented consistent table patterns resolve those exceptions.','','## Images','', 'Real-ESRGAN 2x before rembg; originals retained in _originals. Nine QR assets excluded. Seven source composites were reassembled to avoid displaying masked fragments separately. The source artwork on PDF page 26 is itself incomplete; its original appearance is retained on white as a scene image.','','## Random sample: 20 rows','','| System | PDF page | Printed page | REF | Size / printed values |','|---|---:|---:|---|---|']
for row in sample['rows']:lines.append(f"| {row['system']} | {row['pdfPage']} | {row['printedPage']} | {row['REF']} | {row['size']} |")
(F/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:report[k]for k in ['systemsCreated','systemsMerged','newSystemsPublished','newSystemsDraft','codesFound','codesVerified','tablesCreated','imagesExtracted']},indent=2))
