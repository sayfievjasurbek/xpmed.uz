"""Consolidate source-catalog corrections without changing product records."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
 ('CONMED Advanced Visualization System','reports/conmed/verification-600/user-corrections.json','corrections'),
 ('CONMED Advanced Visualization System','reports/conmed/flag-audit/report.json','sourceCatalogCorrections'),
 ('CONMED Advanced Surgical Product Catalog','reports/conmed/advanced-surgical-product-catalog/report.json','sourceCatalogCorrections'),
 ('CONMED Arthroscopy Product Catalog','reports/conmed/arthroscopy-product-catalog/source-catalog-corrections.json',None),
 ('CONMED HALL Powered Instruments','reports/conmed/hall-powered-instruments/source-catalog-corrections.json',None),
 ('Double Medical Joint Catalogue','reports/double-medical/joint-catalogue.json','sourceCatalogCorrections'),
 ('Double Medical Spine Catalogue — implants','reports/double-medical/spine-catalogue.json','sourceCatalogCorrections'),
 ('Double Medical Spine Catalogue — instruments','reports/double-medical/spine-catalogue-instruments/source-catalog-corrections.json',None),
 ('Double Medical Trauma Catalogue — Part 3','reports/double-medical/trauma-catalogue-part3/source-catalog-corrections.json',None),
 ('SPINENDOS Endoscopic Spine Surgery System','reports/spinendos/endoscopic-spine-surgery-system/source-catalog-corrections.json',None),
]
def text(value):
 if isinstance(value,dict):return value.get('en') or value.get('ru') or json.dumps(value,ensure_ascii=False)
 if isinstance(value,list):return ' / '.join(map(text,value))
 return str(value or '—')
def parse(catalog,item,path):
 page=item.get('pdfPage') or item.get('sourcePdfPage') or (item.get('sourcePages') or item.get('pages') or ['—'])[0]
 printed=item.get('printed') or item.get('asPrinted') or item.get('sourceReading') or item.get('printedCodes') or item.get('printedDiameter')
 used=item.get('used') or item.get('corrected') or item.get('correctedCodes') or item.get('value') or item.get('diameter')
 reason=item.get('basis') or item.get('internalNote') or item.get('issue') or item.get('action') or item.get('correction') or item.get('status') or 'Source catalog correction.'
 needs=False
 if catalog=='CONMED Advanced Visualization System':
  if item.get('visualId')==73:printed='T490';used='T4907';reason=item['note']
  elif item.get('system')=='cannulas':printed='Inner-cannula REF absent; 83234 printed under Inflow Adapter';used='— (inner cannula); 83234 remains inflow adapter';reason='The source and official CONMED catalog omit the inner-cannula REF.';needs=True
 elif catalog=='CONMED Arthroscopy Product Catalog':needs=item.get('id')=='p16-blue-suture'
 elif catalog=='Double Medical Joint Catalogue':
  slug=item.get('system')
  if slug=='amity-a-ve-acetabular-liner':printed='REF (Ti coating) header';used='UHMWPE liner; coating label removed';reason=item['correction']
  elif slug=='accurate-ps-knee-instrument-set':printed='11516140';used='—';reason=item['correction'];needs=True
  elif slug=='apollo-62-72-cup-instrument-set':printed='Two REF lines per trial-liner size';used='Six size rows, each retaining both printed REFs';reason=item['correction'];needs=True
  elif slug=='angel-shoulder-system' and page==34:printed='107mm×6.7m';used='107 mm × 6.7 mm';reason=item['correction']
  elif slug=='angel-shoulder-system' and page==36:printed='5 (fourth row)';used='15 mm';reason=item['correction']
 elif catalog=='Double Medical Spine Catalogue — implants':
  if item.get('kind')=='diameter':printed=f"Ø{item['printedDiameter']} mm (REF {item['REF']})";used=f"Ø{item['diameter']} mm";reason=item['correction']
  else:printed='091271010 printed for 10×10 and 10×12';used='091271010 for 10×10; — for 10×12';reason=item['correction'];needs=True
 elif catalog=='Double Medical Spine Catalogue — instruments':
  if item.get('action'):printed=f"{item['printedName']} with mismatched photo (REF {item['ref']})";used='Printed name and REF; photo removed';reason=item['action'];needs=True
  if item.get('ref')=='110042500':needs=True
 elif catalog=='Double Medical Trauma Catalogue — Part 3':
  if page==585:printed='020940003 on two different sizes';used='020940003 on 150° / 3 holes / 89 mm only';needs=True
  else:printed='Index 11/4';used='Actual set pages 11/6–11/7'
 elif catalog=='SPINENDOS Endoscopic Spine Surgery System':
  if page==18:needs=True
 elif catalog=='CONMED HALL Powered Instruments':needs=False
 return {'catalog':catalog,'page':page,'printed':text(printed),'used':text(used),'reason':text(reason),'needsConfirmation':needs,'source':path}

rows=[]
for catalog,path,key in SOURCES:
 data=json.loads((ROOT/path).read_text())
 entries=data.get(key,[]) if key else data
 assert isinstance(entries,list),(path,type(entries))
 rows.extend(parse(catalog,item,path) for item in entries)
assert len(rows)==28,len(rows)
rows.sort(key=lambda r:(r['catalog'],int(r['page']) if str(r['page']).isdigit() else 0,r['printed']))
(ROOT/'reports/source-corrections.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
def esc(value):return str(value).replace('|','\\|').replace('\n',' ')
lines=['# Source catalog corrections','','Internal production reference. These entries describe discrepancies in source PDFs; they are not shown on product pages.','','## Needs manufacturer or XPMED sales confirmation','','| Catalog | PDF page | Printed value | Value used on site | Reason |','|---|---:|---|---|---|']
for row in rows:
 if row['needsConfirmation']:lines.append('| '+' | '.join(esc(row[k]) for k in ('catalog','page','printed','used','reason'))+' |')
lines+=['','## All corrections by catalog and PDF page','']
for catalog in dict.fromkeys(r['catalog'] for r in rows):
 lines += [f'### {catalog}','','| PDF page | Printed value | Value used on site | Reason | Needs confirmation |','|---:|---|---|---|---|']
 for row in rows:
  if row['catalog']==catalog:lines.append('| '+' | '.join(esc(row[k]) for k in ('page','printed','used','reason'))+f" | {'Yes' if row['needsConfirmation'] else 'No'} |")
 lines.append('')
(ROOT/'reports/source-corrections.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'entries':len(rows),'needConfirmation':sum(r['needsConfirmation'] for r in rows)}))
