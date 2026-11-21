"""Owner-confirmed Joint Catalogue corrections, bound to the reviewed PDF hash."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DECISIONS=ROOT/'reports/double-medical/joint-catalogue/owner-resolutions.json'
def bi(ru,en=None):return {'ru':ru,'en':en if en is not None else ru}
def decisions(digest):
 if not DECISIONS.exists():return None
 d=json.loads(DECISIONS.read_text())
 if d['sourceSha256']!=digest:raise ValueError('Joint owner decisions do not match this source PDF')
 return d

def apply(system,digest):
 d=decisions(digest)
 if not d:return system
 s=copy.deepcopy(system);slug=s['slug'];tables=s.get('specTables',[])+s.get('referenceTables',[])
 if slug=='amity-a-ve-acetabular-liner':
  for t in tables:
   if t['id'].startswith('joint-'):
    # The REF header was copied from a cup table; the polyethylene grade remains unchanged.
    t['columns'][1]=bi('REF')
    t['columns'][2]=bi('Размер','Size')
    t['keyParameters']=[p for p in t.get('keyParameters',[])if p['parameter'].get('en')!='Coating']
 if slug=='accurate-ps-knee-instrument-set':
  for t in tables:
   for i,row in enumerate(t['rows']):
    if row[1]=='11516140' or (row[1]is None and row[0].get('en')=='Cynthia Osteotome for Intercondylar, 18#'):
     row[1]=None
     notes=[n for n in t.get('cellNotes',[])if not(n['row']==i+1 and n['column']==2)]
     notes.append({'row':i+1,'column':2,'text':bi('Каталожный номер уточняйте у менеджера','Confirm the catalog number with your sales manager')});t['cellNotes']=notes
  s['refCodes']=[code for code in s['refCodes']if code!='11516140']
 if slug=='apollo-62-72-cup-instrument-set':
  t=next(t for t in tables if t.get('sourcePages')==[82]);expected=[['113099200','113099300'],['113099400','113099500'],['113099600','113099700'],['115091300','115662500'],['115662600','115662700'],['115662800','115662900']]
  if len(t['rows'])==12:
   original=copy.deepcopy(t);rows=[];sources=[];images=[]
   for i,(size,pair)in enumerate(zip([62,64,66,68,70,72],expected)):
    a,b=original['rows'][2*i:2*i+2];assert [a[1],b[1]]==pair
    name=bi(f'Пробный вкладыш Apollo 10° Ø{size}/36 мм',f'Apollo 10° Trial Liner Ø{size}/36 mm');rows.append([name,*pair]);source=copy.deepcopy(original['rowSources'][2*i]);second=original['rowSources'][2*i+1];source['sourceRows']=[copy.deepcopy(source),copy.deepcopy(second)];source['codeEvidence']+=copy.deepcopy(second['codeEvidence']);box=source['sourceBounds'];other=second['sourceBounds'];source['sourceBounds']=[min(box[0],other[0]),min(box[1],other[1]),max(box[2],other[2]),max(box[3],other[3])];source['bounds']=source['sourceBounds'];sources.append(source)
    image=copy.deepcopy(original.get('rowImages',[None]*12)[2*i]);
    if image and isinstance(image,dict):image['imageCaption']=name
    images.append(image)
   t.update(rows=rows,rowSources=sources,rowImages=images,columns=[bi('Наименование','Description'),bi('REF'),bi('Дополнительный REF','Additional REF')])
  assert len(t['rows'])==6
  assert [row[1:]for row in t['rows']]==expected
  t['note']=bi('Два каталожных номера на размер, уточняйте у менеджера','Two catalog numbers per size; confirm with your sales manager')
 if slug=='angel-shoulder-system':
  for t in tables:
   if not t['id'].startswith('joint-'):continue
   for row in t['rows']:
    if row[1]=='13Y010001S':row[2]=bi('107 мм × 6.7 мм','107 mm × 6.7 mm');row[0]=bi(t['title']['ru']+' · '+row[2]['ru'],t['title']['en']+' · '+row[2]['en'])
    if row[1]=='13Y081015S':row[2]=bi('15');row[0]=bi(t['title']['ru']+' · 15',t['title']['en']+' · 15')
   if t['id'].endswith('p34-1'):t.pop('cellNotes',None)
   if t['id'].endswith('p36-1'):t.pop('note',None)
 affected={c['system']for c in d['corrections']}
 if slug in affected:
  resolved={'coating-header-conflict','printed-code-pattern','incomplete-source-descriptions','brochure-unit-conflict','brochure-conflict'}
  if 'reviewFlags'in s:s['reviewFlags']=[f for f in s['reviewFlags']if f['code']not in resolved]
  for review in [s.get('review',{}),*[source.get('review',{})for source in s.get('catalogImports',[])if source.get('sourceSha256')==digest]]:
   old=[f for f in review.get('flags',[])if f['code']in resolved]
   if old:review.setdefault('resolvedFlags',[]).extend([{**f,'status':'resolved','resolution':'Owner-confirmed Joint Catalogue correction'}for f in old])
   if 'flags'in review:review['flags']=[f for f in review['flags']if f['code']not in resolved]
   if review.get('status')=='review-required':review['status']='owner-resolved'
 return s
