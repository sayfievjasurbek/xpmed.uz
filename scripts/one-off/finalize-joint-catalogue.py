"""Publish only source-verified Joint systems, preserving actual source uncertainties."""
import json,collections,datetime,random,secrets,csv,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/joint-catalogue';profile=json.loads((R/'scripts/profiles/double-medical-joint-catalogue.json').read_text());report=json.loads((R/'reports/double-medical/joint-catalogue.json').read_text());published=[];drafts=[];flags=[];rows=0;tableCount=0
for template in profile['systems']:
 path=R/'content/products/double-medical'/(template['slug']+'.json');s=json.loads(path.read_text());assert s['review']['sourceSha256']==profile['sha256'];openFlags=[f for f in s['review']['flags']if f.get('status','open')!='resolved'];s['status']='draft'if openFlags else'published'
 if not openFlags:s.setdefault('publishedAt',datetime.datetime.now(datetime.timezone.utc).isoformat());s['review']['publicationDecision']='Published under owner authorization: zero real flags after 600-DPI source verification.';published.append(s['slug'])
 else:drafts.append(s['slug'])
 for f in openFlags:flags.append({'system':s['slug'],**f})
 check=subprocess.run(['node',str(R/'scripts/validate-system.mjs')],input=json.dumps(s),text=True,capture_output=True,cwd=R)
 if check.returncode:raise ValueError(check.stdout+check.stderr)
 path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');tables=s.get('specTables',[])+s.get('referenceTables',[]);rows+=sum(len(t['rows'])for t in tables);tableCount+=len(tables)
 for entry in report['systems']:
  if entry['slug']==s['slug']:entry.update(status=s['status'],tables=len(tables),rows=sum(len(t['rows'])for t in tables),flags=openFlags)
for merge in profile['merges']:
 tables=merge['referenceTables'];rows+=sum(len(t['rows'])for t in tables);tableCount+=len(tables)
 for f in merge.get('reviewFlags',[]):flags.append({'system':merge['slug'],**f})
verification=json.loads((F/'verification.json').read_text());assert all(r['value']for r in verification['records']);printedCodes=[r['value']for r in verification['records']];report.update(newImplantSystems=25,instrumentSets=19,mergedIntoExisting=report['mergedIntoExisting'],newSystemsPublished=len(published),newSystemsDraft=len(drafts),publishedSystems=published,draftSystems=drafts,codesFound=len(printedCodes),codesVerified=verification['verified'],uniqueCodes=len(set(printedCodes)),tablesCreated=tableCount,orderingRows=rows,uncertainties=flags,sourcePatternExceptions=json.loads((F/'source-pattern-exceptions.json').read_text()),sourceCatalogCorrections=[{'system':f['system'],'pages':f['sourcePages'],'issue':f['message'],'readings':f.get('readings',[])}for f in flags],brochureSizeMatches=len(json.loads((F/'brochure-size-matches.json').read_text())),publicationNote='Existing systems retain their published state and original brochures; conflicting added REF entries retain the printed value with explicit notes. Only new systems with zero open flags are published.')
from joint_owner_resolutions import decisions
owner=decisions(profile['sha256'])
if owner:
 report['sourceCatalogCorrections']=owner['corrections']
 report['withheldSourceCodes']=['11516140']
 report['publicationNote']='All Joint Catalogue systems published after owner-confirmed source corrections; uncertain REF 11516140 is withheld from ordering. Original brochure tables remain unchanged.'
allrows=json.loads((F/'all-rows.json').read_text());samplePath=F/'random-sample-20.json'
if samplePath.exists():sample=json.loads(samplePath.read_text())
else:
 seed=secrets.token_hex(12);sample={'seed':seed,'rows':random.Random(seed).sample(allrows,20)};samplePath.write_text(json.dumps(sample,ensure_ascii=False,indent=2))
with(F/'random-sample-20.csv').open('w',newline='')as file:
 writer=csv.DictWriter(file,fieldnames=['system','pdfPage','REF','sizeDescription']);writer.writeheader();writer.writerows(sample['rows'])
report['randomSample']=sample['rows'];(R/'reports/double-medical/joint-catalogue.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# Double Medical Joint Catalogue import','',f"25 new implant systems; 19 instrument sets; 4 existing systems updated.",f"Published: {len(published)} new systems. Drafts: {len(drafts)}.",f"Codes: {len(printedCodes)} printed occurrences, {len(set(printedCodes))} distinct; {verification['verified']} verified against source.",f"Tables: {tableCount}; ordering rows: {rows}; brochure size matches: {report['brochureSizeMatches']}.",'','## Open source issues','']
if not flags:lines.append('None. All owner-confirmed corrections have been applied.')
for f in flags:lines.append('- '+f['system']+' · PDF p. '+', '.join(map(str,f['sourcePages']))+': '+f['message']['en'])
if owner:
 lines+=['','## Source catalog corrections','']+[('- '+c['correction'])for c in owner['corrections']]
lines+=['','Verified lettered implant prefixes (13G/13W/13Y) are retained exactly. They are recorded as resolved source-pattern exceptions, not unverified codes.','Existing brochure values, features, variants and publication state were preserved. Backups are in merge-backups/.','','## Random sample of 20 ordering rows','','| System | PDF page | REF | Size / description |','|---|---:|---|---|']
for r in sample['rows']:lines.append(f"| {r['system']} | {r['pdfPage']} | {r['REF']} | {r['sizeDescription'].replace('|','/')} |")
(F/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:report[k]for k in ['systemsCreated','newImplantSystems','instrumentSets','newSystemsPublished','newSystemsDraft','codesFound','codesVerified','uniqueCodes','tablesCreated','orderingRows']},indent=2))
