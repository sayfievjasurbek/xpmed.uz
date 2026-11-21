#!/usr/bin/env python3
"""Finalize the explicitly authorized Arthroscopy source batch; only flag-free systems may publish."""
import json,re,copy,random,collections,subprocess,argparse
from pathlib import Path
from datetime import datetime,timezone
from arthroscopy_source_corrections import corrected_record,CORRECTIONS
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/arthroscopy-product-catalog';ref='/catalogs/conmed/arthroscopy-product-catalog/source.pdf';ap=argparse.ArgumentParser();ap.add_argument('--publish-clean',action='store_true');args=ap.parse_args()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
source=json.load(open(F/'verification-source.json'));visual=json.load(open(F/'visual-readings.json'));official=(F/'official/text.txt').read_text();checks=json.load(open(F/'manufacturer-checks.json'));final=[]
for rec in source['records']:
 r=copy.deepcopy(rec);reading=visual.get(r['id'])
 if reading and reading.get('agreesWithOCR'):
  r['value']=reading['value'];r['visualReading']=reading;r['verificationStatus']='verified (visual + OCR)'
 value=r['value'];r['confirmedOnConmedCom']=bool(value and re.search(r'(?<![A-Za-z0-9-])'+re.escape(value)+r'(?![A-Za-z0-9-])',official))
 if value=='Y1802':r['confirmedOnConmedCom']=True;r['officialEvidence'].append(checks['additionalChecks'][0])
 if value and value.endswith('*'):r['markerInterpretation']='Unexplained source marker; real flag retained on draft system'
 r=corrected_record(r)
 final.append(r)
dump(F/'verification-final.json',{'found':len(final),'verified':sum(bool(r['value'])for r in final),'confirmedOnConmedCom':sum(r['confirmedOnConmedCom']for r in final),'flaggedReadings':[r for r in final if not r['value']],'records':final})
systems=[]
for p in sorted((R/'content/products/conmed').glob('*.json')):
 s=json.load(open(p))
 if s.get('sourcePdf')!=ref:continue
 flags=[f for f in s.get('review',{}).get('flags',[])if f.get('status','open')not in ['resolved','dismissed']]
 if args.publish_clean and not flags:
  s['status']='published';s['review'].setdefault('publishedAt',datetime.now(timezone.utc).isoformat());s['review']['status']='published-source-reviewed';s['review']['publicationReason']='User authorized automatic publication of systems with zero real flags.'
 elif flags:s['status']='draft'
 check=subprocess.run(['node','scripts/validate-system.mjs'],input=json.dumps(s),text=True,capture_output=True,cwd=R)
 if check.returncode:raise ValueError(s['slug']+check.stdout+check.stderr)
 systems.append((p,s,flags))
# Check publication and cross-catalog ownership before mutating statuses.
seen={}
for p in (R/'content/products/conmed').glob('*.json'):
 s=json.load(open(p))
 if s.get('sourcePdf')==ref or s.get('status')!='published':continue
 for code in s.get('refCodes',[]):seen[code]=s['slug']
for _,s,flags in systems:
 if s['status']=='published'and flags:raise ValueError('Open flag publication blocked')
 for code in s['refCodes']:
  if code in seen:raise ValueError('Duplicate CONMED code '+code+' in '+seen[code]+' and '+s['slug'])
  seen[code]=s['slug']
for p,s,flags in systems:dump(p,s)
sections=json.load(open(F/'sections.json'))['sections'];overlaps=json.load(open(F/'overlaps.json'));summary=[]
for category,en,ru,start,end in sections:
 ss=[s for _,s,_ in systems if s['category']==category];codes=[r for r in final if start<=r['pdfPage']<=end];oo=[o for o in overlaps['overlaps']if start<=o['pdfPage']<=end]
 summary.append({'category':category,'name':{'ru':ru,'en':en},'created':len(ss),'published':sum(s['status']=='published'for s in ss),'drafts':sum(s['status']=='draft'for s in ss),'catalogNumberCellsFound':len(codes),'verified':sum(bool(r['value'])for r in codes),'confirmedOnConmedCom':sum(r['confirmedOnConmedCom']for r in codes),'overlapsWithPublishedSystems':len({o['catalogNumber']for o in oo if not o['withinThisPdf']}),'withinPdfRepeatedEntries':sum(o['withinThisPdf']for o in oo)})
flags=[{'system':s['name'],'slug':s['slug'],**f}for _,s,fs in systems for f in fs]
rows=[]
for _,s,_ in systems:
 for t in s['specTables']:
  for i,row in enumerate(t['rows']):
   codes=[c for c in row[1:]if isinstance(c,str)and c]
   if codes:rows.append({'system':s['name'],'slug':s['slug'],'pdfPage':t['rowSources'][i]['pdfPage'],'description':row[0]['en'],'catalogNumber':random.Random(s['slug']+str(i)).choice(codes)})
sample=random.Random(20261119).sample(rows,20);dump(F/'random-20-rows.json',sample)
main=R/'reports/conmed/arthroscopy-product-catalog.json';report=json.load(open(main));report.update(sections=summary,systemsCreated=len(systems),published=sum(s['status']=='published'for _,s,_ in systems),drafts=sum(s['status']=='draft'for _,s,_ in systems),catalogNumbersFound=len(final),catalogNumbersVerified=sum(bool(r['value'])for r in final),confirmedOnConmedCom=sum(r['confirmedOnConmedCom']for r in final),openRealFlags=flags,uncertainties=flags,random20Rows=sample,overlaps=overlaps,sourceTranscription='Provided PDF is the inventory. Official edition is corroboration only; unmatched official items are excluded and retained in the evidence report.',imagesExtracted=len(json.load(open(R/'public/images/products/conmed/arthroscopy/prepared-assets.json'))),imageQualityReview='All image contact sheets visually reviewed; enclosed white background cleaned on six wire/handle images; originals and exact 2x images retained.')
report['sourceCatalogCorrections']=CORRECTIONS;dump(F/'source-catalog-corrections.json',CORRECTIONS)
report['systems']=[{'slug':s['slug'],'name':s['name'],'category':s['category'],'status':s['status'],'sourcePages':s['sourcePages'],'tables':len(s['specTables']),'flags':fs}for _,s,fs in systems];dump(main,report)
md=['# CONMED Arthroscopy import report','',f"**{report['systemsCreated']} systems: {report['published']} published, {report['drafts']} drafts.** {len(final)} catalog-number cells, {report['catalogNumbersVerified']} source-verified, {report['confirmedOnConmedCom']} corroborated on conmed.com. {report['imagesExtracted']} native product images enhanced 2x with Real-ESRGAN before rembg.",'','Counts include repeated printed cells; duplicate products were not created.','', '| Section | Created / Published / Drafts | Codes / Verified / CONMED | Existing overlaps |','|---|---:|---:|---:|']
for x in summary:md.append(f"| {x['name']['en']} | {x['created']} / {x['published']} / {x['drafts']} | {x['catalogNumberCellsFound']} / {x['verified']} / {x['confirmedOnConmedCom']} | {x['overlapsWithPublishedSystems']} |")
md+=['','## Open real flags','']
for f in flags:md.append('- '+f['system']['en']+', PDF p. '+', '.join(map(str,f['sourcePages']))+': '+f['message']['en']+' Readings: '+'; '.join(map(str,f.get('readings',[]))))
if not flags:md.append('None.')
md+=['','## Source catalog corrections (internal)','']
for correction in CORRECTIONS:md.append('- '+correction['internalNote']+' — '+correction['verificationStatus']+'; '+correction['manufacturerUrl'])
md+=['','## Existing-system overlaps','']
for owner in sorted({o['existingSystem']for o in overlaps['overlaps']if not o['withinThisPdf']}):md.append('- '+owner+': '+', '.join(sorted({o['catalogNumber']for o in overlaps['overlaps']if o['existingSystem']==owner and not o['withinThisPdf']})))
md+=['','## Within-PDF duplicates / merges','']
for x in overlaps['omittedDuplicateSystems']:md.append('- PDF p. '+', '.join(map(str,x['sourcePages']))+': '+x['name']['en']+' — '+x['reason'])
md+=['','## Random 20-row sample (seed 20261119)','','| System | PDF page | Description | Catalog number |','|---|---:|---|---|']
for x in sample:md.append('| '+x['system']['en']+' | '+str(x['pdfPage'])+' | '+x['description'].replace('|','/')+' | '+x['catalogNumber']+' |')
(F/'report.md').write_text('\n'.join(md)+'\n');print(json.dumps({k:report[k]for k in ['systemsCreated','published','drafts','catalogNumbersFound','catalogNumbersVerified','confirmedOnConmedCom','imagesExtracted']},indent=2));print('Open real flags',len(flags))
