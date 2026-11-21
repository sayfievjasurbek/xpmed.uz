"""Explicit owner-reviewed source corrections; never infer unapproved REF values."""
import copy,json
from finalize_translation_loader import finalize_translation
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'reports/double-medical/spine-catalogue/owner-resolutions.json'
def decisions(digest):
 if not FILE.exists():return None
 d=json.loads(FILE.read_text())
 if d['sourceSha256']!=digest:raise ValueError('Spine corrections do not match the source PDF')
 return d

def apply(system,digest):
 d=decisions(digest)
 if not d:return system
 s=copy.deepcopy(system);affected=set()
 for correction in d['corrections']:
  if s['slug']!=correction['systemSlug']:continue
  code=correction['REF'];affected.add(code)
  for table in s.get('referenceTables',[]):
   if table.get('sourcePages')!=[correction['pdfPage']]:continue
   for i,row in enumerate(table['rows']):
    if correction['kind']=='diameter':
     if row[1]!=code:continue
     old=copy.deepcopy(row[2]);row[2]={'ru':correction['diameter'],'en':correction['diameter']}
     source=table['rowSources'][i];source.setdefault('sourceCorrections',[])
     if not any(x.get('id')==correction['id']for x in source['sourceCorrections']):source['sourceCorrections'].append({'id':correction['id'],'column':3,'printedValue':old,'catalogValue':row[2],'basis':'Explicit owner-confirmed PDF source typo'})
    else:
     if row[1]not in [code,None]or row[2].get('en')!='10'or row[3].get('en')!='12':continue
     row[1]=None;table['cellNotes']=[x for x in table.get('cellNotes',[])if not(x['row']==i+1 and x['column']==2)]+[{'row':i+1,'column':2,'text':{'ru':'Каталожный номер уточняйте у менеджера','en':'Confirm the catalog number with your sales manager'}}]
     source=table['rowSources'][i]
     for e in source.get('codeEvidence',[]):e.update(printedCode=code,value=None,catalogValue=None,sourceCorrectionId=correction['id'],verificationStatus='unavailable: duplicate REF in source; owner confirmed')
    values=[v['en'] if isinstance(v,dict)else str(v)for v in row[2:]]
    row[0]={'ru':table['title']['ru']+' · '+' / '.join(v['ru'] if isinstance(v,dict)else str(v)for v in row[2:]),'en':table['title']['en']+' · '+' / '.join(values)}
 for key,review in [('reviewFlags',s),('flags',s.get('review',{}))]:
  flags=review.get(key,[]);resolved=[f for f in flags if f.get('code')=='source-ref-size-conflict'and f.get('refCode')in affected]
  if resolved:
   destination=s.setdefault('review',{}) if key=='reviewFlags'else review
   existing=destination.setdefault('resolvedFlags',[])
   for flag in resolved:
    if not any(f.get('refCode')==flag.get('refCode')and f.get('code')==flag.get('code')for f in existing):existing.append({**flag,'status':'resolved','resolution':'Explicit owner-confirmed Spine Catalogue correction; uncertain cage REF withheld from ordering.'})
   review[key]=[f for f in flags if f not in resolved]
 if affected:s.setdefault('review',{})['status']='owner-resolved'
 return finalize_translation(s) if affected else s
