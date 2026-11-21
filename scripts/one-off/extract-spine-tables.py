"""Keep three independent readers and printed row/column geometry, never infer numbers."""
import json,re,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'public/catalogs/double-medical/spine-catalogue/ocr';F=R/'reports/double-medical/spine-catalogue';tables=[];issues=[]
def norm(s):return re.sub(r'\s+','',s).strip('_|=,;')
def code(s):
 s=s.strip('_|,;')
 return s if re.fullmatch(r'[0-9O][0-9A-Z]{7,10}',s) and sum(c.isdigit()for c in s)>=6 else None
def choose(readings):
 counts=collections.defaultdict(set)
 for k,v in readings.items():
  if v:counts[norm(v)].add(k)
 best=max(counts,key=lambda x:len(counts[x]))if counts else''
 return next((v for v in readings.values()if norm(v)==best),'')if len(counts.get(best,[]))>=2 else None
for n in range(4,210):
 if not(O/f'{n:03}.json').exists()or not(F/'vision'/f'{n:03}.json').exists():continue
 j=json.loads((O/f'{n:03}.json').read_text());v=json.loads((F/'vision'/f'{n:03}.json').read_text());readers={'PSM3':j['passes']['3']['words'],'PSM11':j['passes']['11']['words'],'Vision':v}
 refs=sorted([w for w in v if re.match(r'^REF(?:$|[.(])',w['text'].strip())and .08<w['bounds'][0]<.23 and .1<w['bounds'][1]<.9],key=lambda w:w['bounds'][1]);pagecodes=[]
 for reader,words in readers.items():
  for w in words:
   b=w['bounds'];c=code(w['text'])
   if c and .08<b[0]<.22 and .12<b[1]<.94:
    cy=(b[1]+b[3])/2;near=next((r for r in pagecodes if abs(r['cy']-cy)<.005),None)
    if near:near['readings'][reader]=c;near['boundsByReader'][reader]=b
    else:pagecodes.append({'cy':cy,'bounds':b,'readings':{reader:c},'boundsByReader':{reader:b}})
 pagecodes.sort(key=lambda r:r['cy']);prevend=.11
 for k,h in enumerate(refs):
  hy=sum(h['bounds'][1::2])/2;nexty=refs[k+1]['bounds'][1]if k+1<len(refs)else .94;rows=[r for r in pagecodes if hy<r['cy']<nexty]
  if not rows:issues.append({'pdfPage':n,'issue':'REF header without extracted rows','bounds':h['bounds']});continue
  # Column starts are source coordinates; exclude the product artwork to the right.
  candidates=[]
  header_re=r'^(?:REF|Holes|Length|Lenght|Lengtn|Diameter|Height|Angles|Angle|Width|Thickness|Size|Direction|Type|Spec\.|Specification|Distance|Model)'
  for reader,words in readers.items():
   for word in words:
    if .08<word['bounds'][0]<.89 and abs(sum(word['bounds'][1::2])/2-hy)<.012 and re.match(header_re,word['text'],re.I):candidates.append({**word,'reader':reader})
  groups=[]
  for word in sorted(candidates,key=lambda w:w['bounds'][0]):
   group=next((g for g in groups if abs(g[0]['bounds'][0]-word['bounds'][0])<.023),None)
   if group is None:groups.append([word])
   else:group.append(word)
  heads=[]
  for group in groups:
   preferred=next((x for x in group if x['reader']=='Vision'),group[0]);text=preferred['text']
   if re.search(r'(?:Holes|REF.+)\s+(?:Length|Height|Diameter)',text):preferred=next((x for x in group if x['reader']=='PSM3'),preferred);text=preferred['text']
   if text.startswith('REF'):
    if 'PEEK'in text:text='REF (PEEK)'
    elif 'Titanium'in text or 'Titanium'in ' '.join(w['text']for w in readers['PSM3']if abs(sum(w['bounds'][1::2])/2-hy)<.012 and abs(w['bounds'][0]-preferred['bounds'][0])<.09):text='REF (Titanium Alloy)'if n==191 else'REF (Titanium)'
    else:text='REF'
   elif re.match(r'Leng',text):text='Length (mm)'
   elif re.match(r'Angle',text):text='Angles (°)'
   elif re.match(r'Spec',text):text='Spec.'
   else:
    key=re.match(r'[A-Za-z]+',text)[0];text=key+(' (mm)'if key in ['Height','Width','Diameter','Thickness']else'')
   heads.append({**preferred,'text':text})
  if not heads or not heads[0]['text'].startswith('REF'):heads.insert(0,{**h,'text':'REF'})
  starts=[x['bounds'][0]for x in heads];boundaries=[.08]+[(starts[i]+starts[i+1])/2 for i in range(len(starts)-1)]+[max(.56,starts[-1]+.15)]
  before=[w for w in v if prevend<w['bounds'][1]<h['bounds'][1]-.006 and .08<w['bounds'][0]<.54]
  # Ignore preceding table rows in the section preamble.
  if k:
   previousrows=[r['cy']for r in pagecodes if r['cy']<hy];lastprevious=max([r for r in previousrows if r<refs[k-1]['bounds'][1]+.01]+[prevend])
  prose=[w for w in before if re.search(r'[A-Za-z]{2}',w['text'])and not re.match(r'^[0-9A-Z]{8,}',w['text'])]
  specs=[x for x in prose if ':'in x['text']];titles=[x for x in prose if ':'not in x['text']];title=' '.join(x['text']for x in sorted(titles,key=lambda x:x['bounds'][1]))
  out=[]
  for ri,r in enumerate(rows):
   vals=[choose(r['readings'])];evidence=[{'readings':r['readings'],'value':vals[0],'bounds':r['bounds']}]
   for ci in range(1,len(heads)):
    readings={}
    for reader,words in readers.items():
     candidates=[w for w in words if boundaries[ci]<=w['bounds'][0]<boundaries[ci+1]and abs(sum(w['bounds'][1::2])/2-r['cy'])<.0055 and (heads[ci]['text'].startswith('REF') or not code(w['text']))]
     readings[reader]=' '.join(w['text']for w in sorted(candidates,key=lambda w:w['bounds'][0]))
    value=choose(readings);vals.append(value);evidence.append({'readings':readings,'value':value})
   out.append({'values':vals,'evidence':evidence,'cy':r['cy'],'sourceBounds':[.08,r['bounds'][1]-.003,.56,r['bounds'][3]+.003]})
  tables.append({'id':f'spine-p{n}-{k+1}','pdfPage':n,'printedPage':n-2,'title':title,'preamble':[x['text']for x in specs],'headerReadings':[x['text']for x in heads],'headerStarts':starts,'headerY':hy,'rows':out})
  prevend=max(r['bounds'][3]for r in rows)
(F/'tables-evidence.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2)+'\n');(F/'table-detection-issues.json').write_text(json.dumps(issues,indent=2));print('Tables',len(tables),'rows',sum(len(t['rows'])for t in tables),'code gaps',sum(r['values'][0]is None for t in tables for r in t['rows']),'cell gaps',sum(c is None for t in tables for r in t['rows']for c in r['values'][1:]),'issues',len(issues))
(F/'headings.txt').write_text('\n'.join(f"{t['pdfPage']:03} | {t['title']} | {'; '.join(t['preamble'])} | {t['headerReadings']} | {len(t['rows'])}"for t in tables))
