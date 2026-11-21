#!/usr/bin/env python3
"""600-DPI evidence preparation and explicit visual+OCR verification. Drafts only."""
import argparse,hashlib,json,sys,io,subprocess,os,re
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
from catalog_ocr import tesseract_words,lines_from_words
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'public/catalogs/conmed/advanced-visualization-system'
REPORT=ROOT/'reports/conmed/verification-600'
PDF=ROOT/'catalogs-source/conmed/advanced-visualization-system.pdf'
def dump(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def prepare():
 baseline=json.loads((REPORT/'baseline-400dpi.json').read_text());doc=fitz.open(PDF);digest=hashlib.sha256(PDF.read_bytes()).hexdigest();cache=REF/'ocr-600';cache.mkdir(exist_ok=True);(REF/'pages-600').mkdir(exist_ok=True)
 for n in range(4,17):
  output=cache/f'{n:03}.json';png_path=cache/f'{n:03}-600dpi.png'
  if output.exists()and json.loads(output.read_text()).get('sourceSha256')==digest:print('600DPI cached',n,flush=True);continue
  page=doc[n-1];pix=page.get_pixmap(dpi=600,alpha=False);png=pix.tobytes('png');png_path.write_bytes(png);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(REF/'pages-600'/f'{n:03}.webp',quality=92)
  data={'page':n,'printedPage':n-2,'dpi':600,'sourceSha256':digest,'pageSize':[page.rect.width,page.rect.height],'pixelSize':[pix.width,pix.height],'passes':{}}
  for psm in [3,11]:
   raw,words=tesseract_words(png,psm,dpi=600);(cache/f'{n:03}-psm{psm}.tsv').write_text(raw)
   for word in words:word['bounds']=[word['pixelBounds'][0]/pix.width,word['pixelBounds'][1]/pix.height,word['pixelBounds'][2]/pix.width,word['pixelBounds'][3]/pix.height]
   data['passes'][str(psm)]={'words':words,'lines':lines_from_words(words)}
  dump(output,data);print('600DPI two passes',n,flush=True)
 # Build a full item-line crop for every previously flagged cell, not just the number.
 entries=[];canvases={}
 for index,flag in enumerate(baseline['flaggedCodes'],1):
  sid=flag['system'];system=json.loads((ROOT/'content/products/conmed'/f'{sid}.json').read_text());table=next(t for t in system['specTables']if t['id']==flag['tableId']);row=table['rows'][flag['row']-1];box=table['rowSources'][flag['row']-1]['sourceBounds'];n=flag['pdfPage']
  if n not in canvases:canvases={n:Image.open(cache/f'{n:03}-600dpi.png').convert('RGB')}
  page=canvases[n];w,h=page.size;region=[max(0,round((box[0]-.008)*w)),max(0,round((box[1]-.0035)*h)),min(w,round((box[2]+.008)*w)),min(h,round((box[3]+.0035)*h))];line=page.crop(region);crop_path=REPORT/'line-crops'/f'{index:03}-pdf{n:02}.png';crop_path.parent.mkdir(exist_ok=True);line.save(crop_path)
  entries.append({'id':index,'pdfPage':n,'printedPage':n-2,'system':sid,'tableId':flag['tableId'],'row':flag['row'],'column':flag['column'],'componentId':flag['componentId'],'itemName':row[0],'sourceBounds':box,'baseline':flag,'lineCrop':str(crop_path.relative_to(ROOT)),'cropPixelBounds':region,'cropSize':list(line.size)})
 dump(REPORT/'items.json',entries)
 for start in range(0,len(entries),10):
  batch=entries[start:start+10];width=max(e['cropSize'][0]for e in batch)+30;height=sum(e['cropSize'][1]+62 for e in batch)+20;sheet=Image.new('RGB',(width,height),'#eef0f2');draw=ImageDraw.Draw(sheet)
  try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',30)
  except OSError:font=ImageFont.load_default(size=30)
  y=10
  for entry in batch:
   draw.text((15,y),f"ID {entry['id']:03} | PDF {entry['pdfPage']} | code column {entry['column']}",fill='#003242',font=font);sheet.paste(Image.open(ROOT/entry['lineCrop']),(15,y+44));y+=entry['cropSize'][1]+62
  sheet.save(REPORT/f"batch-{batch[0]['id']:03}-{batch[-1]['id']:03}.png")
 print('Prepared',len(entries),'independent visual line crops',flush=True)
def identity(e):return (e['system'],e['tableId'],e['row'],e['column'])
def official_matches(code,entries):
 return [e for e in entries if e['code']==code]
def collect_official():
 entries=json.loads((REPORT/'official/product-page-codes.json').read_text())
 sources=[('surgicalimaging-catalog.pdf','https://www.conmed.com/-/media/conmed/documents/catalog/surgicalimaging_catalog.ashx'),('looking-glass-emea.pdf','https://www.conmed.com/-/media/conmed/documents/literature/lookingglass_productbrochure-emea.ashx')]
 for filename,url in sources:
  doc=fitz.open(REPORT/'official'/filename)
  for n,page in enumerate(doc,1):
   lines=page.get_text(sort=True).splitlines()
   for i,line in enumerate(lines):
    rowparts=re.split(r'\.{3,}',line)
    if len(rowparts)>1:
     # Preserve every explicit ordering code, including both Eyecup/Cartridge columns.
     name=rowparts[0].strip()
     codes=[part.strip('.*† ')for part in rowparts[1:]]
    elif filename=='looking-glass-emea.pdf':
     match=re.match(r'^(.*?)\s+1\s+([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)[*†]?\s*$',line)
     if not match:continue
     name=match[1].strip();codes=[match[2]]
    else:continue
    for code in codes:
     if not re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',code):continue
     entries.append({'code':code,'name':name,'context':'\n'.join(lines[max(0,i-2):i+1]),'url':url+'#page='+str(n),'sourceType':'official-manufacturer-pdf','pdfPage':n,'localSource':str((REPORT/'official'/filename).relative_to(ROOT))})
 dump(REPORT/'official/evidence.json',entries);return entries

def verify():
 from catalog_code_verification import code_tokens,pattern_candidates,verify_visual
 from collections import defaultdict
 import copy
 baseline=json.loads((REPORT/'baseline-400dpi.json').read_text());items=json.loads((REPORT/'items.json').read_text());visual={e['id']:e for e in json.loads((REPORT/'visual-readings.json').read_text())};ocr={e['id']:e for e in json.loads((REPORT/'ocr-readings.json').read_text())};official=collect_official()
 assert len(items)==len(visual)==212
 folder=ROOT/'content/products/conmed';systems={}
 for e in baseline['systems']:
  s=json.loads((ROOT/e['file']).read_text());assert s['status']=='draft';assert s['review']['sourceSha256']==baseline['sha256'];systems[s['slug']]=s
 original_dir=REPORT/'drafts-before-verification';original_dir.mkdir(exist_ok=True)
 for slug,s in systems.items():
  original=original_dir/(slug+'.json')
  if not original.exists():dump(original,s)
 # Use immutable original audits, including the original 45 accepted occurrences.
 audits=[]
 for original in sorted(original_dir.glob('*.json')):
  s=json.loads(original.read_text())
  for t in s['specTables']:
   for row in t['rowSources']:audits.extend(copy.deepcopy(row.get('codeEvidence',[])))
 assert len(audits)==257
 bykey={identity(e):e for e in audits};seeds=defaultdict(set);records=[]
 for e in audits:
  if not e['flagged'] and e['value']:seeds[(e['system'],e['tableId'])].add(e['value'])
 for item in items:
  old=bykey[identity(item)];readings=copy.deepcopy(ocr[item['id']]['readings'])
  readings.extend([{'reader':'400dpi-page-psm3','text':old['pass1'],'confidence':old['confidence1']},{'reader':'400dpi-page-psm11','text':old['pass2'],'confidence':old['confidence2']}])
  v=visual[item['id']];direct=verify_visual(v,readings,[])
  if direct['value']:seeds[(item['system'],item['tableId'])].add(direct['value'])
  record={**copy.deepcopy(old),'visualId':item['id'],'itemName':item['itemName'],'lineCrop':item['lineCrop'],'visualReading':v,'ocrReadings':readings,'baseline400':copy.deepcopy(old)};records.append(record)
 for r in records:
  candidates=pattern_candidates(r['ocrReadings'],seeds[(r['system'],r['tableId'])]);r['patternCandidates']=candidates;r.update(verify_visual(r['visualReading'],r['ocrReadings'],candidates));r['reasons']=[]if not r['flagged']else ['visual-reading-does-not-match-any-raw-OCR-or-supported-first-character-candidate'];r['officialEvidence']=official_matches(r['value'],official)if r['value']else [];r['manufacturerStatus']='confirmed on conmed.com'if r['officialEvidence']else 'not confirmed on conmed.com'
  if r.get('visualId')==73:
   r['sourceDiscrepancy']={'note':'The source item line clearly prints T490, including a wider-margin re-check. The official manufacturer ordering row for Arthroscopic Portal Rod prints T4907. No digit was appended.','visualWideMargin':'reports/conmed/verification-600/item-073-wide-margin.png','officialDifferentCode':'T4907','officialEvidence':official_matches('T4907',official)}
  bykey[identity(r)]=r
 for r in audits:
  if r['flagged']:continue
  r['verificationStatus']='verified (two OCR passes, original import)';r['officialEvidence']=official_matches(r['value'],official);r['manufacturerStatus']='confirmed on conmed.com'if r['officialEvidence']else 'not confirmed on conmed.com';bykey[identity(r)]=r
 # Explicit user-authorized source errata are separate from visual/OCR verification.
 decisions=json.loads((REPORT/'user-corrections.json').read_text()) if (REPORT/'user-corrections.json').exists() else {'corrections':[]}
 if decisions['corrections']:assert decisions['sourceSha256']==baseline['sha256']
 for decision in decisions['corrections']:
  assert decision['authorizedBy']=='user' and decision['visibility']=='internal-only'
  r=next(r for r in records if r['visualId']==decision['visualId'])
  proof=next(e for e in bykey.values()if e['pdfPage']==decision['corroboratingPdfPage'] and e['value']==decision['value'] and not e['flagged'])
  official_proof=official_matches(decision['value'],official);assert official_proof
  r.update({'value':decision['value'],'flagged':False,'reasons':[],'verificationStatus':'corrected (user-approved source typo)','userCorrection':decision,'officialEvidence':official_proof,'manufacturerStatus':'confirmed on conmed.com','corroboratingSource':{'pdfPage':proof['pdfPage'],'tableId':proof['tableId'],'row':proof['row'],'column':proof['column'],'value':proof['value']}})
  r['sourceDiscrepancy']['note']=decision['note'];bykey[identity(r)]=r
 all_records=list(bykey.values());flagged=[r for r in all_records if r['flagged']]
 result={'sourceSha256':baseline['sha256'],'status':'draft-only','dpi':600,'productPages':list(range(4,17)),'baselineTotal':257,'baselineVerified':45,'baselineFlagged':212,'visuallyRead':len(records),'userCorrected':sum('userCorrection'in r for r in records),'newlyVerified':sum(not r['flagged']and 'userCorrection'not in r for r in records),'verified':sum(not r['flagged']for r in all_records),'confirmedOnConmedCom':sum(bool(r.get('officialEvidence'))for r in all_records),'confirmedOnProductPages':sum(any(e['sourceType']=='official-product-page'for e in r.get('officialEvidence',[]))for r in all_records),'confirmedOnlyInManufacturerPdfs':sum(bool(r.get('officialEvidence'))and not any(e['sourceType']=='official-product-page'for e in r.get('officialEvidence',[]))for r in all_records),'stillFlagged':len(flagged),'records':all_records,'flaggedCodes':flagged,'acceptancePolicy':'Every previously flagged code requires an independently recorded clear visual reading matching a raw OCR token or a first-character-only candidate supported by at least two different confirmed codes in the same table. Official sources corroborate; they never fill an unresolved source code. Explicit user-authorized source errata are recorded separately with cross-page and official evidence.'}
 dump(REPORT/'verification.json',result)
 print(json.dumps({k:v for k,v in result.items()if k not in ['records','flaggedCodes']},indent=2))
 write_verification_report(result)
 return result

def write_verification_report(result):
 safe=lambda x:str(x).replace('|','\\|').replace('\n',' ')
 lines=['# CONMED catalog — 600 DPI code verification','',f"- Total code occurrences: {result['baselineTotal']} (repeated codes count per printed cell).",f"- Verified: **{result['verified']}**; newly verified by visual + OCR: **{result['newlyVerified']} / 212**; user-approved source corrections: {result.get('userCorrected',0)}; retained original two-pass verifications: 45.",f"- Confirmed on conmed.com: **{result['confirmedOnConmedCom']}** ({result['confirmedOnProductPages']} on product pages; {result['confirmedOnlyInManufacturerPdfs']} additional occurrences in official manufacturer PDFs).",f"- Still flagged / empty: **{result['stillFlagged']}**.",'- All 10 systems remain drafts. Nothing published.','- Product pages 4–16 rendered at 600 DPI. Physical PDF page numbers are used; printed page = PDF page − 2.','',result['acceptancePolicy'],'','## Still flagged — full readings']
 for r in result['flaggedCodes']:
  lines += ['',f"### PDF {r['pdfPage']} / printed {r['printedPage']} — {r['itemName']['en']}",f"- Table: `{r['tableId']}`; row {r['row']}, column {r['column']}.",f"- Visual reading: `{r['visualReading']['reading']}` (clear). Stored value: empty.",f"- [Original 600 DPI item line]({Path(r['lineCrop']).relative_to('reports/conmed/verification-600')})",'- OCR readings:']
  for e in r['ocrReadings']:lines.append(f"  - {e['reader']}: `{e['text'] or '∅'}` (confidence {e['confidence']:.2f}).")
  if r.get('sourceDiscrepancy'):lines.append('- Source discrepancy: '+r['sourceDiscrepancy']['note']+' [Official ordering row]('+r['sourceDiscrepancy']['officialEvidence'][0]['url']+').')
  lines += ['- Supported pattern candidates: '+(', '.join(sorted({e['value']for e in r['patternCandidates']}))or 'none')+'.','- Reason: '+', '.join(r['reasons'])+'.']
 lines += ['','## Internal source corrections']
 for r in result['records']:
  if 'userCorrection'in r:lines.append('- '+r['userCorrection']['note']+f". Accepted code: `{r['value']}`. Internal only; not rendered publicly.")
 lines += ['','## Every independently read item','| ID | PDF / printed page | Item | Visual | Accepted | Verification | Manufacturer |','|---:|---|---|---|---|---|---|']
 for r in sorted((r for r in result['records']if 'visualId'in r),key=lambda r:r['visualId']):lines.append(f"| {r['visualId']} | {r['pdfPage']} / {r['printedPage']} | {safe(r['itemName']['en'])} | `{r['visualReading']['reading']}` | `{r['value']or '∅'}` | {r['verificationStatus']} | {r['manufacturerStatus']} |")
 lines += ['','## Evidence files','- `visual-readings.json`: independent visual readings, each linked to its full item-line crop.','- `ocr-readings.json`: raw page and cropped-code OCR, separate settings/confidences, no code substitutions.','- `verification.json`: all 257 cell audits, baseline, visual, OCR, pattern basis and official URLs.','- `official/evidence.json`: exact manufacturer SKU/ordering-row evidence and source URLs.','- `baseline-400dpi.json` and `drafts-before-verification/`: preserved previous state.']
 (REPORT/'report.md').write_text('\n'.join(lines)+'\n')

def apply_verified(result):
 if (ROOT/'reports/conmed/list-layout/report.json').exists():raise ValueError('The draft catalog has been reorganized. Verification is historical; refusing to overwrite its new structure.')
 from catalog_code_verification import verify_visual
 import copy
 bykey={identity(r):r for r in result['records']}
 for entry in json.loads((REPORT/'baseline-400dpi.json').read_text())['systems']:
  path=ROOT/entry['file'];s=json.loads(path.read_text());assert s['status']=='draft';assert s['review']['sourceSha256']==result['sourceSha256']
  for t in s['specTables']:
   for row in t['rowSources']:
    new=[]
    for old in row.get('codeEvidence',[]):
     r=bykey[identity(old)]
     if 'userCorrection'in r:
      decision=next(d for d in json.loads((REPORT/'user-corrections.json').read_text())['corrections']if d['visualId']==r['visualId']);assert decision['authorizedBy']=='user' and decision['value']==r['value'] and r['officialEvidence']
     elif 'visualReading'in r:
      checked=verify_visual(r['visualReading'],r['ocrReadings'],r['patternCandidates']);assert checked['value']==r['value']
     t['rows'][r['row']-1][r['column']-1]=r['value'];new.append(copy.deepcopy(r))
    row['codeEvidence']=new
  for c in s['components']:
   c['codeEvidence']=[copy.deepcopy(bykey[identity(e)])for e in c.get('codeEvidence',[])];c['refCodes']=list(dict.fromkeys(e['value']for e in c['codeEvidence']if e['value']))
  s['refCodes']=list(dict.fromkeys(code for c in s['components']for code in c['refCodes']))
  flags=[]
  for f in s['review']['flags']:
   if f['code']!='ocr-code-review':flags.append(f);continue
   r=bykey[identity(f['details'])]
   if r['flagged']:
    f['details']=copy.deepcopy(r);f['message']={'ru':f"Cat. No. требует проверки после 600 DPI: визуально «{r['visualReading']['reading']}»; нет точного совпадения с OCR или допустимой коррекцией первого символа. Значение не заполнено.",'en':f"600-DPI review: visual reading {r['visualReading']['reading']} has no exact raw OCR or supported first-character candidate match; value left empty."};flags.append(f)
  s['review']['flags']=flags;s['review']['codeVerification']={'report':'reports/conmed/verification-600/verification.json','dpi':600,'policy':result['acceptancePolicy'],'verified':sum(not e['flagged']for c in s['components']for e in c.get('codeEvidence',[])),'stillFlagged':sum(e['flagged']for c in s['components']for e in c.get('codeEvidence',[]))};s['review']['importMethod']='400-DPI initial import; 600-DPI PSM3/11 and isolated-code OCR; independently recorded Codex visual readings; auditable first-character table-pattern candidates'
  ref='/catalogs/conmed/advanced-visualization-system';s['sourcePageImages']=[ref+f'/pages-600/{n:03}.webp'for n in s['sourcePages']]
  for n in s['sourcePages']:
   evidence=json.loads((REF/'ocr-600'/f'{n:03}.json').read_text());s['sourcePageDimensions'][str(n)]={'width':evidence['pixelSize'][0],'height':evidence['pixelSize'][1]}
  dump(path,s)
 report=json.loads((REPORT/'baseline-400dpi.json').read_text());report['ocr']['initialDpi']=400;report['ocr']['dpi']=600;report['ocr']['verificationPolicy']=result['acceptancePolicy'];report['ocr']['substitutions']='first-character table-pattern candidates require exact independent visual agreement; all raw readings retained';report['verificationReport']='reports/conmed/verification-600/report.md';report['confirmedCatalogNumberOccurrences']=result['verified'];report['confirmedOnConmedCom']=result['confirmedOnConmedCom'];report['flaggedCodes']=result['flaggedCodes'];report['uniqueConfirmedCatalogNumbers']=len({r['value']for r in result['records']if r['value']});report['codeVerificationSummary']={k:result[k]for k in ['baselineVerified','baselineFlagged','newlyVerified','verified','confirmedOnConmedCom','stillFlagged']}
 for entry in report['systems']:
  s=json.loads((ROOT/entry['file']).read_text());entry['flags']=s['review']['flags'];entry['flaggedCodes']=s['review']['codeVerification']['stillFlagged']
 dump(ROOT/'reports/conmed/advanced-visualization-system.json',report)
 main=ROOT/'reports/conmed/advanced-visualization-system.md';history=REPORT/'baseline-400dpi.md'
 if not history.exists():history.write_text(main.read_text())
 main.write_text((REPORT/'report.md').read_text()+'\n\nThe initial import report (systems, images, company text, contacts and QR references) is preserved in [baseline-400dpi.md](verification-600/baseline-400dpi.md).\n')
 print('Applied verified codes to 10 drafts; nothing published.')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--verify',action='store_true');parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 if args.prepare:prepare()
 if args.verify or args.apply:
  result=verify()
  if args.apply:apply_verified(result)
