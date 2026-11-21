"""Position-preserving row evidence for the authorized Joint Catalogue."""
import json,re,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/joint-catalogue';O=R/'public/catalogs/double-medical/joint-catalogue/ocr'
V=json.loads((F/'verification.json').read_text());pages={};rows=[]
def norm(s):
 s=re.sub(r'\s+','',s).lower().replace('×','x').replace('х','x').replace('o#','0#').replace('ф','ø').replace('φ','ø').replace('®','ø').replace('mm','').replace('m','')
 return s.strip('=_|,;')
for n in sorted({x['pdfPage']for x in V['records']}):
 j=json.loads((O/f'{n:03}.json').read_text());pages[n]={'PSM3':j['passes']['3']['words'],'PSM11':j['passes']['11']['words'],'Vision':json.loads((F/'vision'/f'{n:03}.json').read_text())}
for code in V['records']:
 n=code['pdfPage'];b=code['sourceBounds'];cy=(b[1]+b[3])/2;readings={}
 for reader,words in pages[n].items():
  chosen=[]
  for w in words:
   bb=w['bounds'];wy=(bb[1]+bb[3])/2
   if abs(wy-cy)>(.0032 if n in range(17,30)else .005):continue
   if bb[0]>.61:continue
   if bb[0]>.245:chosen.append((bb[0],w['text']))
   elif reader=='Vision':
    m=re.search(r'(?<![A-Za-z0-9])[1I4][A-Z0-9]{8,9}(?![A-Za-z0-9])',w['text'])
    if m and m.end()<len(w['text']):chosen.append((.25,w['text'][m.end():].strip()))
  readings[reader]=' '.join(s for x,s in sorted(chosen)).strip(' _=|')
 # Keep separate column boundaries from actual printed header words.
 hdr=[w for w in pages[n]['PSM3']if w['text'].startswith('REF')and w['bounds'][0]<.25 and .13<w['bounds'][1]<b[1]]
 hy=max((w['bounds'][1]for w in hdr),default=0)
 heads=[w for w in pages[n]['PSM3']if abs(w['bounds'][1]-hy)<.004 and .245<w['bounds'][0]<.55 and re.search(r'Size|Length|Thickness|Direction|Degree|Holes',w['text'],re.I)]
 heads=sorted(heads,key=lambda w:w['bounds'][0]);cols=[]
 for i,h in enumerate(heads):
  start=.245 if i==0 else (heads[i-1]['bounds'][0]+h['bounds'][0])/2
  end=.61 if i==len(heads)-1 else(h['bounds'][0]+heads[i+1]['bounds'][0])/2
  vals={}
  for reader in ['PSM3','PSM11']:
   vals[reader]=' '.join(w['text']for w in sorted(pages[n][reader],key=lambda w:w['bounds'][0])if start<w['bounds'][0]<end and abs((w['bounds'][1]+w['bounds'][3])/2-cy)<(.0032 if n in range(17,30)else .005)).strip(' _=|')
  cols.append({'header':h['text'],'readings':vals})
 counts=collections.Counter(norm(v)for v in readings.values()if norm(v));best,count=counts.most_common(1)[0]if counts else('',0)
 value=next((v for v in readings.values()if norm(v)==best),'')
 # Instrument set headings are not instrument rows.
 isSet=n>=40 and bool(re.search(r'Instrument|Instument',value,re.I))and cy<.18
 rows.append({**code,'itemReadings':readings,'itemValue':value if count>=2 else None,'itemCandidate':value,'itemVerification':'two-reader agreement'if count>=2 else'requires review','columns':cols,'tableHeaderY':hy,'isSetHeading':isSet})
(F/'rows-evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('Rows',len(rows),'item agreement',sum(r['itemValue']is not None for r in rows),'pending',sum(r['itemValue']is None for r in rows),'set headings',sum(r['isSetHeading']for r in rows))
(F/'row-review.txt').write_text('\n'.join(f"{r['id']} {r['value']} {r['itemReadings']}"for r in rows if r['itemValue']is None))
