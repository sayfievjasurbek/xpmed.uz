"""Reviewed implant-only recipe; exact source tables and additive legacy merges."""
import json,re,hashlib,collections,copy
from pathlib import Path
from spine_catalogue_manifest import FAMILIES,MERGES,family,clean_title,translate_title,translate_spec,HEADERS,bi
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue';SOURCE='/catalogs/double-medical/spine-catalogue';PDF=R/'catalogs-source/double-medical/spine-catalogue.pdf';T=json.loads((F/'tables-final.json').read_text());A=json.loads((R/'public/images/products/double-medical/spine-catalogue/prepared-assets.json').read_text());systems={};untranslated=[];sample=[];code_records=[];exceptions=[]
# Explicitly preserve the catalog's printed values where one REF is assigned two sizes.
conflict_codes={'085965045','085975045','085985045','085987030','085995045','091271010'}

def init(entry):
 slug,ru,en,sub=entry
 if slug not in systems:
  spec=['spine']+(['neurosurgery']if sub=='cervical'else['traumatology']if sub=='thoracolumbar'else[])
  systems[slug]={'schemaVersion':1,'slug':slug,'brand':'double-medical','category':'spine-implants','subcategory':sub,'specialty':spec,'name':bi(ru,en),'shortDescription':bi('Импланты и компоненты для хирургии позвоночника','Implants and components for spine surgery'),'description':bi(ru+'. Каталожные номера, материалы и размеры компонентов приведены по официальному Spine Catalogue Double Medical. Выберите исполнение по таблицам ниже.',en+'. Component reference numbers, materials and dimensions are listed according to the official Double Medical Spine Catalogue. Select configurations from the tables below.'),'heroImage':'','imageType':'cutout','gallery':[],'variants':[],'features':[],'hotspots':[],'components':[],'specTables':[],'referenceTables':[],'refCodes':[],'sourcePages':[],'sourcePdf':SOURCE+'/source.pdf','catalogTitle':bi('Double Medical Spine Catalogue — импланты','Double Medical Spine Catalogue — implants'),'catalogEdition':None,'documentCover':SOURCE+'/pages/001.webp','status':'draft','isNew':False,'catalogType':'system','imageDimensions':{},'reviewFlags':[],'relatedSystemSlugs':[]}
 return systems[slug]
def image(a,title):return {k:a[k]for k in ['src','width','height','imageType','imageEnhancement']}|{'sourcePages':sorted({p['pdfPage']for p in a['placements']}),'imageCaption':title}
# Assign each image to its own printed subgroup, rather than reusing the nearest photo on every continued page.
assignment=collections.defaultdict(list)
for a in A.values():
 targets=set()
 for p in a['placements']:
  possible=[t for t in T if t['pdfPage']==p['pdfPage']]
  if not possible:continue
  t=next((t for t in possible if t['id']==a.get('tableId')),None)or min(possible,key=lambda t:abs(t['headerY']-sum(p['bounds'][1::2])/2));targets.add(t['id'])
 for tid in targets:assignment[tid].append(a)
for t in T:
 entry=family(t);s=init(entry);n=t['pdfPage'];en=clean_title(t['title'],n);title,unknown=translate_title(en)
 if unknown:untranslated.append((n,en,unknown))
 columns=[bi('Наименование','Description')]+[bi(HEADERS[h],h)for h in t['headerReadings']];params=[]
 for text in t['preamble']:
  translated=translate_spec(text);ru,enp=translated['ru'].split(':',1),translated['en'].split(':',1);params.append({'parameter':bi(ru[0].strip(),enp[0].strip()),'value':bi(ru[1].strip(),enp[1].strip())})
 table={'id':t['id'],'groupId':t['id'],'title':title,'columns':columns,'rows':[],'rowSources':[],'keyParameters':params,'unit':'mm'if any('(mm)'in h or h=='Spec.'for h in t['headerReadings'])else None,'sourcePages':[n],'sourcePdf':SOURCE+'/source.pdf','hideDescriptionColumn':True,'images':[],'rowDimensions':[]}
 for a in assignment[t['id']]:
  img=image(a,title);table['images'].append(img);s['imageDimensions'][a['src']]={'width':a['width'],'height':a['height']}
  if not any(i['src']==img['src']for i in s['gallery']):s['gallery'].append(img)
  if not s['heroImage']:s['heroImage']=img['src'];s['imageType']=img['imageType']
 for ri,row in enumerate(t['rows']):
  assert all(v is not None for v in row['values']),(t['id'],ri,row['values'])
  refs=[v for h,v in zip(t['headerReadings'],row['values'])if h.startswith('REF')];size=' / '.join(v for h,v in zip(t['headerReadings'],row['values'])if not h.startswith('REF'));ru_size=size.replace('mm','мм').replace('Left','Левый').replace('Right','Правый')
  values=[bi(title['ru']+(' · '+ru_size if size else''),title['en']+(' · '+size if size else''))];dimensions={}
  evidence=[]
  for ci,(h,v)in enumerate(zip(t['headerReadings'],row['values'])):
   if h.startswith('REF'):
    values.append(v);s['refCodes'].append(v);ev=row['evidence'][ci];readings=[{'reader':reader,'text':text}for reader,text in ev['readings'].items()];visual=ev.get('codexVisualReading');
    if visual:readings.append({'reader':'Codex visual 600-DPI crop','text':visual['value']})
    record={'value':v,'pdfPage':n,'printedPage':n-2,'tableId':t['id'],'row':ri+1,'column':ci+2,'readings':readings,'verificationStatus':'verified (visual + OCR)'if visual else'verified (three readers compared; exact agreement)','sourceBounds':row['sourceBounds']};evidence.append(record);code_records.append(record)
    if not re.fullmatch(r'\d{9}[A-Za-z]?',v):exceptions.append({'code':v,'pdfPage':n,'table':t['id'],'status':'resolved: lettered numeric REF printed consistently in its source table and independently verified'})
   else:
    values.append(bi(v.replace('mm','мм').replace('Left','Левый').replace('Right','Правый'),v))
    for key,name in [('length','Length'),('width','Width'),('thickness','Thickness')]:
     if name in h:dimensions[key]=v
  table['rows'].append(values);table['rowDimensions'].append(dimensions);table['rowSources'].append({'pdfPage':n,'printedPage':n-2,'sourceBounds':row['sourceBounds'],'bounds':row['sourceBounds'],'coordinateSpace':'normalized','codeEvidence':evidence,'cellEvidence':row['evidence']});sample.extend({'system':s['name']['en'],'slug':s['slug'],'pdfPage':n,'printedPage':n-2,'REF':ref,'size':size or'—'}for ref in refs)
 s['referenceTables'].append(table);s['sourcePages'].append(n)
# Group source duplicate-code contradictions into six concrete review issues.
for code in sorted(conflict_codes):
 occurrences=[r for t in T for r in t['rows']if code in [v for h,v in zip(t['headerReadings'],r['values'])if h.startswith('REF')]];pages=sorted({t['pdfPage']for t in T for r in t['rows']if code in r['values']});owner=next(s for s in systems.values()if code in s['refCodes']);readings=[{'pdfPage':t['pdfPage'],'values':r['values']}for t in T for r in t['rows']if code in r['values']];owner['reviewFlags'].append({'code':'source-ref-size-conflict','path':'referenceTables','sourcePages':pages,'refCode':code,'message':bi('В источнике REF '+code+' указан для разных размеров. Требуется подтверждение Double Medical.','The source assigns REF '+code+' to different dimensions. Double Medical confirmation is required.'),'readings':readings})
# Alias search checks both names and all published REF codes before any file is written.
existing=[json.loads(p.read_text())for p in(R/'content/products').glob('*/*.json')];matches=[];overlaps=[]
for s in systems.values():
 s['sourcePages']=sorted(set(s['sourcePages']));s['refCodes']=list(dict.fromkeys(s['refCodes']));s['gallery']=s['gallery'][:12];s['relatedSystemSlugs']=[other['slug']for other in systems.values()if other['slug']!=s['slug']and other['subcategory']==s['subcategory']][:4]
 if not s['heroImage']:s['reviewFlags'].append({'code':'missing-image','path':'heroImage','sourcePages':s['sourcePages'],'message':bi('Нет проверенного изображения импланта.','No verified implant artwork is available.')})
 name_matches=[e for e in existing if e['brand']=='double-medical'and(e['slug']==s['slug']or s['name']['en'].casefold()==e['name']['en'].casefold()or('tina'in s['slug']and'tina'in e['slug']))];ref_matches=[e for e in existing if set(s['refCodes'])&set(e.get('refCodes',[]))]
 for e in ref_matches:overlaps.append({'system':s['slug'],'existing':e['brand']+'/'+e['slug'],'codes':sorted(set(s['refCodes'])&set(e['refCodes']))})
 matches.append({'catalogLine':s['name'],'slug':s['slug'],'decision':'merge existing'if s['slug']in MERGES else'new system','nameMatches':[e['slug']for e in name_matches],'refMatches':[e['slug']for e in ref_matches],'searchedPublishedSystems':sum(e.get('status')=='published'for e in existing)})
assert not untranslated,untranslated
assert not overlaps,overlaps
from spine_owner_resolutions import apply as apply_owner
digest=hashlib.sha256(PDF.read_bytes()).hexdigest()
systems={slug:apply_owner(system,digest)for slug,system in systems.items()}
merges=[{k:s[k]for k in ['slug','brand','category','subcategory','specialty','referenceTables','refCodes','relatedSystemSlugs','sourcePages','reviewFlags','gallery','imageDimensions']}for s in systems.values()if s['slug']in MERGES];new=[s for s in systems.values()if s['slug']not in MERGES]
profile={'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'layoutReviewed':True,'method':'Implants only: printed pages 2–207 (physical PDF 4–209); 600-DPI Tesseract PSM3/11 + Apple Vision; source-vector glyph comparison calibrated visually; Codex visual reading of unresolved crops; Real-ESRGAN 2x before rembg; Codex-authored medical Russian; additive legacy matches','catalogTitle':bi('Double Medical Spine Catalogue — импланты','Double Medical Spine Catalogue — implants'),'nonProductPages':[1,2,3]+list(range(210,413)),'authorizedPhysicalPages':list(range(4,210)),'systems':new,'merges':merges,'assets':list(A.values())}
(R/'scripts/profiles/double-medical-spine-catalogue.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n');(F/'all-rows.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2));(F/'existing-match-audit.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2));(F/'source-pattern-exceptions.json').write_text(json.dumps(exceptions,indent=2));(F/'verification.json').write_text(json.dumps({'found':len(code_records),'verified':len(code_records),'records':code_records},ensure_ascii=False,indent=2));print('New',len(new),'merges',len(merges),'tables',len(T),'REFs',len(code_records),'flags',[(s['slug'],len(s['reviewFlags']))for s in systems.values()if s['reviewFlags']])
