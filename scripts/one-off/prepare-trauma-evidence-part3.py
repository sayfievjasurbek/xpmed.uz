"""Reconcile three independent source readers with recorded visual/glyph evidence."""
import json,re,collections
from pathlib import Path
from trauma_part3_translation import implant,instrument,FIXES
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part3'
tables=json.loads((F/'tables-evidence.json').read_text());rows=json.loads((F/'instrument-rows-evidence.json').read_text());glyphs=json.loads((F/'glyph-readings.json').read_text());G={(g['table'],g['row'],g['column']):g for g in glyphs}
manualFile=R/'scripts/profiles/trauma-part3-visual-values.json';manual=json.loads(manualFile.read_text())if manualFile.exists()else[];M={(v['table'],v['row'],v['column']):v['value']for v in manual}
flags=[];corrections=[]
def clean(v,iscode=False):
 v=(v or '').strip(' _|~=—–,')
 if iscode:
  a=v.split();return a[0]if a else''
 v=re.sub(r'^[=,;]+\s*','',v)
 v=re.sub(r'[ФфΦφ$©]','Ø',v)
 v=re.sub(r'\b(Left|Right)\b.*',lambda m:m[1],v)
 return v[:-1]if re.fullmatch(r'\d+\.',v)else v
for t in tables:
 t['printedTitleReading']=t['title'];t['title']=FIXES.get(t['title'],t['title']);t['name']=implant(t['title']);t['reviewFlags']=[]
 for i,r in enumerate(t['rows']):
  for ci,e in enumerate(r['evidence']):
   iscode=t['headerReadings'][ci].startswith('REF');reads={k:clean(v,iscode)for k,v in e['readings'].items()}
   if not iscode and any('Ø'in v for v in reads.values()):
    reads={k:re.sub(r'(?<!\d)[0$©](?=\d(?:\.\d)?)','Ø',v)for k,v in reads.items()}
   counts=collections.Counter(v for v in reads.values()if v);value=counts.most_common(1)[0][0]if counts and counts.most_common(1)[0][1]>=2 else None
   if not counts:value=''
   g=G.get((t['id'],i,ci))
   if g and g['accepted']and g['text']in reads.values():value=g['text'];e['glyphReading']={'text':g['text'],'scores':g['scores'],'sourceRect':g['rect']}
   if (t['id'],i,ci)in M:value=M[(t['id'],i,ci)];e['visualReading']={'reader':'Codex 600-DPI source crop','text':value}
   if value is None:
    flag={'code':'unverified-table-value','pdfPage':t['pdfPage'],'tableId':t['id'],'row':i,'column':ci,'readings':e['readings']};t['reviewFlags'].append(flag);flags.append(flag)
   r['values'][ci]=value;e['verifiedValue']=value
  for ci,h in enumerate(t['headerReadings']):
   if not h.startswith('REF'):continue
   ref=r['values'][ci]
   if ref and not re.fullmatch(r'\d{9}[A-Za-z]?',ref):
    flag={'code':'ref-pattern-mismatch','pdfPage':t['pdfPage'],'tableId':t['id'],'row':i,'column':ci,'readings':r['evidence'][ci]['readings']};t['reviewFlags'].append(flag);flags.append(flag)
 # Only diagnose a genuine repeated REF with conflicting dimensions, not two parallel REF columns.
 for ci,h in enumerate(t['headerReadings']):
  if not h.startswith('REF'):continue
  seen={}
  for i,r in enumerate(t['rows']):
   ref=r['values'][ci]
   if not ref:continue
   if ref in seen and r['values']!=seen[ref]:
    flag={'code':'duplicate-ref-different-size','pdfPage':t['pdfPage'],'tableId':t['id'],'row':i,'column':ci,'readings':[seen[ref],r['values']]};t['reviewFlags'].append(flag);flags.append(flag)
   seen[ref]=r['values']
descriptionFixes={'566-02':'Drill Guide for Bone Screws, Ø4.0/Ø5.4','598-07':'LCP Drill Sleeve, Ø2.8','626-03':'Hollow Reamer, Ø3.5, length 70mm','633-09':'3.5/5.0mm Small Fragment Implant Case Lid (Aluminium Alloy)'}
for r in rows:
 text=descriptionFixes.get(r['id'],r['description'])
 if r['id']in descriptionFixes:r['descriptionVisualReading']=text
 if r['pdfPage']in [632,633]:
  j=json.loads((R/f'public/catalogs/double-medical/trauma-catalogue/ocr/{r["pdfPage"]}.json').read_text())
  quantities={reader:next((w['text']for w in j['passes'][psm]['words']if .60<w['bounds'][0]<.66 and abs(sum(w['bounds'][1::2])/2-r['cy'])<.006 and w['text'].isdigit()),'')for reader,psm in [('PSM3','3'),('PSM11','11')]}
  q=next(iter(quantities.values()));r['quantity']=q;r['quantityReadings']=quantities
  words=[w for w in j['passes']['11']['words']if .22<w['bounds'][0]<.595 and r['sourceBounds'][1]<sum(w['bounds'][1::2])/2<r['sourceBounds'][3] and w['text']not in ['Description','qty']]
  words.sort(key=lambda w:(round(w['bounds'][1]/.008),w['bounds'][0]));text=' '.join(w['text']for w in words)
  if r['id']in descriptionFixes:text=descriptionFixes[r['id']]

 text=text.strip(' =_|*').replace('Description qty','').replace('Description Qty','')
 text=re.sub(r'[©®$ФфΦφ](?=\d)','Ø',text)
 text=re.sub(r'(?<=\d)\s*mm\b','mm',text)
 r['description']=text;r['name']=instrument(text)
 if not r['value']:
  flags.append({'code':'unverified-ref','pdfPage':r['pdfPage'],'rowId':r['id'],'readings':r['readings']})
for name,data in [('tables-final.json',tables),('instrument-rows-final.json',rows),('value-review.json',flags),('source-catalog-corrections.json',corrections)]:
 (F/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Tables',len(tables),'flags',len(flags),collections.Counter(f['code']for f in flags))
