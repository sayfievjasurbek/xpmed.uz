"""Exact REF evidence, baseline deduplication, and final source-photo review."""
import json,re,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part3';P=R/'scripts/profiles/double-medical-trauma-part3.json';p=json.loads(P.read_text());tables=json.loads((F/'tables-final.json').read_text());rows=json.loads((F/'instrument-rows-final.json').read_text());headers=json.loads((F/'page-headers.json').read_text());records=[]
for t in tables:
 for ri,row in enumerate(t['rows']):
  for ci,label in enumerate(t['headerReadings']):
   if not label.startswith('REF')or not row['values'][ci]:continue
   e=row['evidence'][ci];value=row['values'][ci];reads=[v.split()[0]if v.strip()else''for v in e['readings'].values()];assert value in reads or e.get('visualReading'),(t['id'],ri,ci,value,reads)
   records.append({'pdfPage':t['pdfPage'],'table':t['id'],'row':ri,'column':ci,'REF':value,'readings':e['readings'],'visualReading':e.get('visualReading'),'status':'verified (visual + OCR/pattern)'if e.get('visualReading')else'verified (three readers compared)'})
for row in rows:
 assert row['value']in row['readings'].values(),row['id']
 records.append({'pdfPage':row['pdfPage'],'rowId':row['id'],'REF':row['value'],'readings':row['readings'],'status':'verified (visual + OCR)'if row['id']=='634-05'else'verified (three readers compared)','visualReading':{'reader':'Codex 600-DPI source crop','text':'111292400'}if row['id']=='634-05'else None})
set_records=[{'pdfPage':h['pdfPage'],'REF':c['value'],'readings':c['readings'],'status':'verified (three readers compared)'}for h in headers for c in h['setCodes']if c['value']]
for r in set_records:assert r['REF']in r['readings'].values()
audit={'bodyOccurrences':len(records),'setHeaderOccurrences':len(set_records),'distinctCodes':len({r['REF']for r in records+set_records}),'records':records,'setHeaders':set_records};(F/'code-verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
# Link newly imported tools/cases to the previously published sets that contain them.
old=[]
for path in json.loads((F/'existing-system-hashes.json').read_text()):
 s=json.loads((R/path).read_text())
 if s['brand']=='double-medical'and s.get('category')=='trauma-instrument-sets':old.append(s)
links=[]
for s in p['systems']:
 if s['subcategory']!='trauma-cases-optional-instruments':continue
 for st in old:
  common=set(s['refCodes'])&set(st['refCodes'])
  if common:
   s['relatedSystemSlugs']=list(dict.fromkeys(s['relatedSystemSlugs']+[st['slug']]));links.append({'from':s['slug'],'to':st['slug'],'sharedREF':sorted(common)})
p['relatedExistingSets']=links;P.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(F/'related-existing-sets.json').write_text(json.dumps(links,ensure_ascii=False,indent=2))
assets=json.loads((F/'source-images.json').read_text());qa={'status':'reviewed','assetsReviewed':sorted(assets),'sourceComparison':'Codex visual review of all seven final contact sheets and source layouts; two QR tiles excluded; two multi-instrument composites split into five separate row photos; ambiguous 607 composite retained only as a general subgroup illustration','nativeLimits':'Every source photo has recorded final native dimensions; exact-2x Real-ESRGAN before rembg; cutouts have 32px transparent padding','sceneFallbacks':json.loads((F/'image-fallbacks.json').read_text())};(F/'image-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
corrections=[{'pdfPage':585,'REF':'020940003','status':'open','issue':'Same printed REF for angle 150°, 3 holes, length 89 mm and angle 140°, 4 holes, length 105 mm. Correct second REF is not established; both source rows retained for review.'},{'pdfPage':611,'status':'documented','issue':'Index places Patella Pin Instrument Set at 11/4; actual set pages are 11/6–11/7 (PDF 616–617). Actual source pages imported; no product values changed.'}];(F/'source-catalog-corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2))
print('REF occurrences',len(records),'+ headers',len(set_records),'distinct',audit['distinctCodes'],'existing set links',len(links))
