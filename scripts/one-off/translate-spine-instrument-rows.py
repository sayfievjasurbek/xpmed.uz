import json,re,sys
from pathlib import Path
sys.path.insert(0,'scripts')
from spine_instrument_translation import translate
from spine_instrument_manifest import S
from spine_instrument_resolutions import resolve_row
F=Path('reports/double-medical/spine-catalogue-instruments');rows=json.loads((F/'rows-final.json').read_text());headers=json.loads((F/'page-headers.json').read_text());by={};current=None
for h in headers:
 if h['setCodes']:current=h['setCodes'][0]['value']
 by[h['pdfPage']]=current
for r in rows:
 r['setCode']=by[r['pdfPage']];r['description']=r['description'].lstrip('- ');t=translate(r['description'],S[r['setCode']][1])
 if r['id']=='363-01':t={'ru':'Контейнер пластины и винтов OLIF (пластина с 4 отверстиями)','en':'OLIF Plate&Screw Case (4 holes plate)'}
 if r['id']=='365-04':t={'ru':'Контейнер пластины и винтов OLIF (пластина с 2 отверстиями)','en':'OLIF Plate&Screw Case (2 holes plate)'}
 if r['id']=='382-05':t={'ru':'Ретракционный крючок I MIS, 140 мм','en':'MIS Retraction Hook I, 140mm'}
 t['en']=t['en'].replace('1,140mm','I, 140mm');r['name']=t
 resolve_row(r)
 # Do not convert a comma between a Roman type and a dimension to a decimal.
 assert sorted(re.findall(r'\d+(?:[.,]\d+)?',t['ru']))==sorted(re.findall(r'\d+(?:[.,]\d+)?',t['en'])),(r['id'],t)
(F/'rows-translated.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(len(rows),'bilingual rows')
