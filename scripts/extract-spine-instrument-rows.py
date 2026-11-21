"""Three-reader, geometry-preserving instrument REF/description extraction."""
import json,re,collections,difflib
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';O=R/'public/catalogs/double-medical/spine-catalogue/ocr';rows=[];headers=[]
def candidate(s):
 s=s.strip('|_,;')
 return s if re.fullmatch(r'[0-9IlO][0-9A-Za-z]{6,11}',s)and sum(c.isdigit()for c in s)>=6 else None
def choose(reads):
 counts=collections.defaultdict(set)
 for reader,text in reads.items():
  if text:counts[text].add(reader)
 if not counts:return None
 best=max(counts,key=lambda x:len(counts[x]));return best if len(counts[best])>=2 else None
for n in range(210,412):
 if not(O/f'{n:03}.json').exists()or not(F/'vision'/f'{n:03}.json').exists():continue
 page=json.loads((O/f'{n:03}.json').read_text());v=json.loads((F/'vision'/f'{n:03}.json').read_text());readers={'PSM3':page['passes']['3']['words'],'PSM11':page['passes']['11']['words'],'Vision':v};groups=[];sets=[]
 title=' '.join(w['text']for w in sorted(v,key=lambda w:w['bounds'][1])if w['bounds'][1]<.095 and w['bounds'][0]>.09 and re.search(r'Instrument|Set|System|HOBBIT|TINA|Spine|Cage|III|Plate|Locking|OLIF|PLIF|MIS|TLIF|Mesh|Light|Retraction|Pedicle',w['text']))
 for reader,words in readers.items():
  for w in words:
   b=w['bounds'];c=candidate(w['text'])
   if not c:continue
   cy=(b[1]+b[3])/2
   if .09<b[0]<.40 and .095<cy<.145:dest=sets
   elif .08<b[0]<.24 and .14<cy<.93:dest=groups
   else:continue
   group=next((g for g in dest if abs(g['cy']-cy)<.006),None)
   if group is None:group={'cy':cy,'bounds':b,'readings':{}};dest.append(group)
   group['readings'][reader]=c
 headers.append({'pdfPage':n,'title':title,'setCodes':[{**g,'value':choose(g['readings'])}for g in sets]})
 groups.sort(key=lambda g:g['cy'])
 for i,g in enumerate(groups):
  descriptions={};bottom=(groups[i+1]['cy']+g['cy'])/2 if i+1<len(groups)else .93
  for reader,words in readers.items():
   lower=(groups[i-1]['cy']+g['cy'])/2 if i else max(.14,g['bounds'][1]-.035)
   selected=[w for w in words if .22<w['bounds'][0]<.73 and .006<w['bounds'][3]-w['bounds'][1]<.025 and lower<w['bounds'][1]<bottom]
   selected=sorted(selected,key=lambda w:(round(w['bounds'][1]/.012),w['bounds'][0]));text=' '.join(w['text']for w in selected);descriptions[reader]=text.strip('_| ')
  # Keep the independent readings, even when a normalized prose candidate is selected.
  clean=lambda s:re.sub(r'\s+','',s).replace('×','x').replace('φ','Ø').replace('Ф','Ø').casefold()
  norms=collections.Counter(clean(v)for v in descriptions.values()if v);best,count=norms.most_common(1)[0]if norms else('',0);desc=next((v for v in descriptions.values()if clean(v)==best),'')
  if count<2:desc=descriptions.get('Vision')or descriptions.get('PSM3')or descriptions.get('PSM11')or''
  rows.append({'id':f'{n:03}-{i+1:02}','pdfPage':n,'printedPage':n-2,'value':choose(g['readings']),'candidate':next(iter(g['readings'].values())),'readings':g['readings'],'description':desc,'descriptionReadings':descriptions,'descriptionAgreement':count>=2,'sourceBounds':[g['bounds'][0],g['bounds'][1]-.003,.56,min(bottom,g['bounds'][3]+.055)],'codeBounds':g['bounds'],'cy':g['cy']})
F.mkdir(parents=True,exist_ok=True);(F/'rows-evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(F/'page-headers.json').write_text(json.dumps(headers,ensure_ascii=False,indent=2)+'\n');(F/'description-review.txt').write_text('\n'.join(f"{r['id']} | {r['value']or r['candidate']} | {r['description']} | {r['descriptionReadings']}"for r in rows if not r['descriptionAgreement']));print('Pages',len(headers),'instrument rows',len(rows),'unresolved codes',sum(r['value']is None for r in rows),'description disagreements',sum(not r['descriptionAgreement']for r in rows));print('Set headings',[(h['pdfPage'],h['title'],h['setCodes'])for h in headers if h['setCodes']])
