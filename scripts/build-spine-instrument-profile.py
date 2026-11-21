"""Source-bound Part 2 recipe; separate partition preserves the published implant import."""
import json,re,hashlib,collections
from pathlib import Path
from spine_instrument_manifest import S
from spine_instrument_resolutions import resolve_system
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';A=R/'public/images/products/double-medical/spine-instruments';P=R/'scripts/profiles/double-medical-spine-instruments.json'
rows=json.loads((F/'rows-translated.json').read_text());heads=json.loads((F/'page-headers.json').read_text());assets={}
for name in ['artwork-assets.json']:
 if (A/name).exists():assets.update(json.loads((A/name).read_text()))
manualFile=A/'manual-photo-assets.json'
if manualFile.exists():
 assets={k:a for k,a in assets.items()if not k.startswith(('art-290-','art-308-','art-383-'))};assets.update(json.loads(manualFile.read_text()))
bi=lambda ru,en:{'ru':ru,'en':en}
existing=[(p,json.loads(p.read_text()))for p in(R/'content/products').glob('*/*.json')];audit=[];systems=[];used=[]
def slugify(t):return re.sub('[^a-z0-9]+','-',t.lower()).strip('-')
def picture(row):
 found=[]
 for a in assets.values():
  for p in a['placements']:
   if p.get('sourceRowId')==row['id']:found.append((abs((p['bounds'][1]+p['bounds'][3])/2-row['cy']),a))
 return min(found,key=lambda x:x[0])[1]if found else None
def image(a,caption):
 return {**{k:a[k]for k in ['src','width','height','imageType','captionFree','imageEnhancement']},'imageCaption':caption,'sourcePages':sorted({p['pdfPage']for p in a['placements']})}
for code,(en,ru,links)in S.items():
 own=[r for r in rows if r['setCode']==code];pages=sorted({r['pdfPage']for r in own});matches=[(p,s)for p,s in existing if s.get('brand')=='double-medical'and(s.get('setCode')==code or code in s.get('refCodes',[])or s['name']['en'].casefold()==en.casefold())]
 # An importer rerun sees its own drafts; another source match requires an additive update recipe.
 matches=[(p,s)for p,s in matches if s.get('importPartition')!='spine-instruments']
 if matches:raise ValueError('Existing set needs additive update, refusing duplicate: '+code+' '+str([str(p)for p,s in matches]))
 audit.append({'setCode':code,'name':bi(ru,en),'matches':[],'action':'new'})
 duplicate=sum(name[0]==en for name in S.values())>1;slug=slugify(en)+(('-'+code)if duplicate else'');name=bi(ru+(' · '+code if duplicate else''),en+(' · '+code if duplicate else''))
 region='cervical'if any(x in en for x in ['Cervical','Occipital','Laminoplasty'])else'sacroiliac'if'Sacroiliac'in en else'spinal-mesh'if'Mesh'in en else'spine-mis'if any(x in en for x in ['MIS','OLIF','ATP','Endo LIF','UBE'])else'thoracolumbar'
 if code=='113791700':region='cervical' # Source components explicitly name cervical cages and plate IV instruments.
 specialties=['spine'];specialties+=['neurosurgery']if region=='cervical'else[]
 if region!='cervical'and any(x in en for x in ['TINA','HOBBIT','Thoracic','Universal Pedicle','PLIF','TLIF','Endo LIF']):
  if any('traumatology'in json.loads((R/'content/products/double-medical'/(link+'.json')).read_text()).get('specialty',[])for link in links):specialties.append('traumatology')
 photos=[(r,picture(r))for r in own];photos=[(r,a)for r,a in photos if a];case=next(((r,a)for r,a in photos if 'Case'in r['name']['en']),photos[0]if photos else(None,None));hero=case[1];gallery=[]
 for r,a in ([case]+photos if hero else[]):
  if a and a['src']not in [g['src']for g in gallery]:gallery.append(image(a,r['name']))
  if len(gallery)>=5:break
 tables=[];flags=[]
 for page in pages:
  pr=[r for r in own if r['pdfPage']==page];table={'id':f'spine-set-{code}-p{page}','groupId':f'spine-set-{code}-p{page}','title':bi(f'Инструменты · стр. {page-2}',f'Instruments · p. {page-2}'),'columns':[bi('Наименование','Description'),bi('REF','REF')],'rows':[],'rowSources':[],'rowImages':[],'sourcePage':page,'sourcePages':[page],'printedPage':page-2,'catalogNumberTable':True}
  for ri,r in enumerate(pr):
   table['rows'].append([r['name'],r['value']]);table['rowSources'].append({'pdfPage':page,'printedPage':page-2,'bounds':r['sourceBounds'],'sourceBounds':r['sourceBounds'],'codeBounds':r['codeBounds'],'sourceRowId':r['id'],'codeEvidence':[{'tableId':table['id'],'row':ri+1,'column':2,'pdfPage':page,'readings':[{'reader':reader,'text':value,'bounds':r['codeBounds']}for reader,value in r['readings'].items()],'verificationStatus':r['codeVerification']}],'descriptionReadings':r['printedDescriptionReadings'],'descriptionVerification':r['descriptionVerification']});a=picture(r);table['rowImages'].append(image(a,r['name'])if a else None)
   for f in r.get('realFlags',[]):flags.append({**f,'path':f.get('path')or f'specTables.{len(tables)}.rows.{ri}.0','pdfPage':page,'sourceBounds':r['sourceBounds'],'readings':[str(v)for v in f['readings'].values()]})
  tables.append(table)
 for link in links:
  assert(R/'content/products/double-medical'/(link+'.json')).exists(),link
 dims={a['src']:{'width':a['width'],'height':a['height']}for r,a in photos}
 system={'slug':slug,'brand':'double-medical','category':'spine-instrument-sets','subcategory':region,'specialty':specialties,'name':name,'setCode':code,'setCodeEvidence':[dict(h, pdfPage=page['pdfPage'])for page in heads for h in page['setCodes']if h['value']==code],'catalogType':'list','importPartition':'spine-instruments','shortDescription':bi('Инструменты для хирургии позвоночника','Spine surgery instruments'),'description':bi(ru+'. Комплектация и каталожные номера приведены по Spine Catalogue Double Medical.',en+'. Contents and catalog numbers are listed according to the Double Medical Spine Catalogue.'),'heroImage':hero['src']if hero else'','imageType':hero['imageType']if hero else'cutout','gallery':gallery,'features':[],'components':[],'specTables':tables,'referenceTables':[],'refCodes':list(dict.fromkeys([code]+[r['value']for r in own])),'sourcePages':pages,'catalogEdition':None,'catalogTitle':bi('Double Medical Spine Catalogue — каталог продукции','Double Medical Spine Catalogue — product catalog'),'documentCover':'/catalogs/double-medical/spine-catalogue/pages/001.webp','isNew':False,'status':'draft','relatedSystemSlugs':links,'relatedRelationship':'Clinical family/context; no additional compatibility claim','imageDimensions':dims,'reviewFlags':flags}
 # A source has no FC photos at all. Keep the page text/table-led rather than invent artwork.
 if not hero:system['sourceImageNote']=bi('В этом разделе исходного каталога фотографии инструментов отсутствуют.','The source section contains no instrument photographs.')
 resolve_system(system)
 systems.append(system);used.extend([a['src']for r,a in photos])
profile={'sha256':hashlib.sha256((R/'catalogs-source/double-medical/spine-catalogue.pdf').read_bytes()).hexdigest(),'partition':'instruments','reportSlug':'spine-catalogue-instruments','authorizedPhysicalPages':list(range(210,412)),'layoutReviewed':True,'method':'600-DPI Tesseract PSM3 + PSM11 + independent Apple Vision accurate; exact REF agreement; Codex-authored RU medical terminology; native photo composites, Real-ESRGAN 2x before rembg','systems':systems,'merges':[],'assets':sorted(set(used)),'nonProductPages':list(range(1,210))+[412]}
P.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n');(F/'duplicate-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print('Sets',len(systems),'rows',len(rows),'tables',sum(len(s['specTables'])for s in systems),'photos ready',len(assets),'flags',len([f for s in systems for f in s['reviewFlags']]))
