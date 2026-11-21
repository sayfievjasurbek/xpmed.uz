#!/usr/bin/env python3
"""Finalize this source-reviewed import; publish only systems without real flags."""
import json,datetime,hashlib,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from finalize_translation_loader import finalize_translation
now=datetime.datetime.now(datetime.timezone.utc).isoformat();folder=ROOT/'reports/conmed/advanced-surgical-product-catalog';verification=json.loads((folder/'verification.json').read_text());systems=[];open_flags=[];published=[];drafts=[]
for p in sorted((ROOT/'content/products/conmed').glob('*.json')):
 s=json.loads(p.read_text())
 if '/advanced-surgical-product-catalog/'not in(s.get('sourcePdf')or''):continue
 def clean(v):
  if isinstance(v,dict):
   if 'pdfPage'in v:v['printedPage']=None
   for x in v.values():clean(x)
  elif isinstance(v,list):
   for x in v:clean(x)
 clean(s)
 s['review']['importMethod']='600-DPI Tesseract PSM3/11 plus isolated PSM7/13 at multiple scales; independent Codex visual readings; additional local Apple Vision OCR; official CONMED catalog cross-check. No prefix or ambiguous-character substitutions.'
 source_codes=[e for t in s['specTables']for row in t['rowSources']for e in row['codeEvidence']]
 s['review']['codeVerification']={'report':'reports/conmed/advanced-surgical-product-catalog/verification.json','dpi':600,'found':len(source_codes),'verified':sum(e['value']is not None for e in source_codes),'stillFlagged':sum(e['value']is None for e in source_codes),'confirmedOnConmedCom':sum(bool(e.get('officialEvidence'))for e in source_codes),'policy':'A source code is accepted only when independent visual reading agrees exactly with at least one raw OCR reading. Official matches corroborate; no T-prefix or case/suffix corrections are inferred.'}
 # One-dimensional source pages have no independent printed page numbering.
 s['gallery'].sort(key=lambda x:(x.get('pdfPage',999),x.get('sourceBounds',[0,0,0,0])[1]))
 if s['gallery']:
  # A single complete source illustration, never a caption or composite card.
  hero=max(s['gallery'],key=lambda x:x.get('width',0)*x.get('height',0));s['heroImage']=hero['src'];s['imageType']=hero['imageType']
 for flag in s['review']['flags']:
  flag['status']='open';open_flags.append({'system':s['slug'],'name':s['name'],'page':flag.get('pdfPage',flag.get('sourcePages',[None])[0]),'code':flag['code'],'message':flag['message'],'readings':flag.get('readings',flag.get('details',{}))})
 s=finalize_translation(s)
 s['status']='draft'if s['review']['flags']else'published'
 if s['status']=='published':s['review']['publishedAt']=now;s['review']['publicationReason']='Explicit owner authorization: automatically publish imported systems with zero real flags.';published.append(s['slug'])
 else:drafts.append(s['slug'])
 p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');systems.append({'slug':s['slug'],'name':s['name'],'pages':s['sourcePages'],'status':s['status'],'openFlags':len(s['review']['flags']),'images':len(s['gallery'])})
report={'catalog':'CONMED Advanced Surgical Product Catalog','pages':44,'sourcePdf':'/catalogs/conmed/advanced-surgical-product-catalog/source.pdf','systemsCreated':len(systems),'published':len(published),'drafts':len(drafts),'catalogNumbersFound':verification['found'],'catalogNumbersVerified':verification['verified'],'catalogNumbersConfirmedOnConmedCom':verification['confirmedOnConmedCom'],'uniquePrintedCodes':len(set(r['visualReading']for r in verification['records'])),'imagesExtracted':sum(s['images']for s in systems),'imagePipeline':'Original embedded photos (no vector captions), Real-ESRGAN x4plus downsampled to exactly 2x, then rembg; originals retained; native-size rendering caps.','nonProductPages':[1,2,3,4,9,22,40,43,44],'systems':systems,'openRealFlags':open_flags,'verificationReport':'reports/conmed/advanced-surgical-product-catalog/verification.json','brandNote':json.loads((ROOT/'content/catalogs/conmed/advanced-surgical-product-catalog.json').read_text())['brandNote'],'finishedAt':now}
(folder/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# CONMED Advanced Surgical Product Catalog','',f"Systems: {len(systems)} created / {len(published)} published locally / {len(drafts)} drafts.",f"Catalog-number entries: {verification['found']} found / {verification['verified']} verified / {verification['confirmedOnConmedCom']} confirmed on conmed.com. Counts refer to occurrences, including repeated codes.",f"Product images: {report['imagesExtracted']}; Real-ESRGAN 2x, rembg, source originals retained. OCR: 600 DPI; independent visual reading and raw OCR agreement; no family-prefix substitutions.",'','## Open real flags','']
for f in open_flags:
 lines.append(f"- **{f['name']['en']} — PDF {f['page']}**: {f['message']['en']}")
 if f['code']=='ocr-code-review':
  e=f['readings'];visual=e.get('visualReading',{}).get('reading');lines.append(f"  - Visual: `{visual}`; accepted value: empty. Manufacturer: {e.get('manufacturerStatus')}.")
  for r in e.get('ocrReadings',[]):lines.append(f"  - {r['reader']}: `{r['text'] or '—'}`")
 else:
  for r in f['readings']:lines.append(f"  - `{r['code']}`: `{r['sourceReading']}`. Printed/source conversion retained; no inferred decimal inserted.")
lines+=['','## Systems','']+[f"- {s['name']['en']}: {s['status']}; PDF {', '.join(map(str,s['pages']))}."for s in systems]
(folder/'report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:report[k]for k in ['systemsCreated','published','drafts','catalogNumbersFound','catalogNumbersVerified','catalogNumbersConfirmedOnConmedCom','imagesExtracted']},indent=2))
