#!/usr/bin/env python3
"""Publish the single source-reviewed Angel system and freeze a random source-cell sample."""
import json,random,secrets,datetime,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'content/products/double-medical/angel-shoulder-system.json';s=json.loads(p.read_text());reportpath=R/'reports/double-medical/angel-shoulder-system.json';report=json.loads(reportpath.read_text());folder=reportpath.with_suffix('');folder.mkdir(exist_ok=True)
if s['review']['flags']:raise ValueError('Open real flags; publication not authorized')
s['status']='published';s['review']['publishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();s['review']['publicationReason']='Owner authorized automatic publication after source verification with zero real flags.';s['review']['imageReview']='All source images visually compared with source; manufacturer alpha preserves white liners and screws. RemBG candidates and originals retained.';s['review']['sourceDifferences']=[{'pages':[5,8],'field':'Humeral stem offset','note':'Page 5 prints 7.5 / 8.5 / 9.5; page 8 prints 8 / 9 / 9.5. Each variant retains its own source table, without harmonizing.'}];p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
tables={t['id']:t for v in s['variants']for t in v['specTables']};seed=secrets.randbits(64);rng=random.Random(seed);samples=[]
for i,t in enumerate(tables.values()):
 candidates=[];covered=set()
 for r,row in enumerate(t['rows']):
  visible=0
  for c,entry in enumerate(row):
   if (r,c)in covered:continue
   visible+=1;value=entry.get('value')if isinstance(entry,dict)and'value'in entry else entry
   rs=entry.get('rowspan',1)if isinstance(entry,dict)else 1;cs=entry.get('colspan',1)if isinstance(entry,dict)else 1
   for y in range(r,r+rs):
    for x in range(c,c+cs):
     if y!=r or x!=c:covered.add((y,x))
   if c>0 and isinstance(value,str)and value and(value[0].isdigit()or value[0]in'+/αβ●'):
    candidates.append({'tableId':t['id'],'tableName':t['title'],'row':r+1,'column':visible,'gridColumn':c+1,'value':value,'pdfPage':t['sourcePages'][0],'colspan':cs,'rowspan':rs,'sourceBounds':t['rowSources'][r]['sourceBounds']})
 samples.extend(rng.sample(candidates,4 if i<2 else 3))
rng.shuffle(samples)
sample={'selection':'Stratified random sample of non-empty source anchor cells across all six tables; covered coordinates excluded. Row counts start at the first printed row, including the type/diameter row. Column counts visible cells in that row; gridColumn is the internal span coordinate.','seed':seed,'samples':samples};(folder/'sample-20.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n')
report.update(status='published',published=1,drafts=0,openRealFlags=[],sampleFile='reports/double-medical/angel-shoulder-system/sample-20.json',sampleSeed=seed,sourceDifferences=s['review']['sourceDifferences']);report['systems'][0]['status']='published';reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# Angel Shoulder Replacement System','', '4 variants / 6 unique source tables / 0 open real flags. Published locally in RU and EN.','', 'Source-specific offset values on pages 5 and 8 are preserved separately. No source values were harmonized.','', '## Random sample of 20 table values','', 'Rows include the first printed type/diameter row. Columns count visible cells within that row; merged anchors are sampled once.','', '| Table | Row | Column | Value | PDF page |','|---|---:|---:|---|---:|']
for x in samples:lines.append(f'| {x["tableName"]["ru"]} | {x["row"]} | {x["column"]} | {x["value"]} | {x["pdfPage"]} |')
(folder/'report.md').write_text('\n'.join(lines)+'\n');print('Published Angel; frozen random sample:',seed)
