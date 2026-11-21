#!/usr/bin/env python3
"""Assemble source-linked list systems from reviewed Arthroscopy extraction evidence.
All uncertain code/translation/image associations stay explicit review flags, never inferred numbers.
"""
import json,re,hashlib,copy,sys,collections,random
from pathlib import Path
from functools import lru_cache
from arthroscopy_ru import translate,unknown
from arthroscopy_polish import polish
from arthroscopy_source_corrections import corrected_record,apply_system
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/arthroscopy-product-catalog';S=R/'catalogs-source/conmed/arthroscopy-product-catalog.pdf'
sections=json.loads((F/'sections.json').read_text());layouts=[json.loads(f.read_text())for f in sorted((F/'layout-source').glob('*.json'))];verification=json.loads((F/'verification-source.json').read_text());records={r['id']:r for r in verification['records']};visualfile=F/'visual-readings.json';visual=json.loads(visualfile.read_text())if visualfile.exists()else{}
featuresRU=json.loads((R/'scripts/profiles/arthroscopy-features-ru.json').read_text());proseRU=json.loads((R/'scripts/profiles/arthroscopy-prose-ru.json').read_text());assetsfile=R/'public/images/products/conmed/arthroscopy/prepared-assets.json';assets=json.loads(assetsfile.read_text())if assetsfile.exists()else{};sourceimages=json.loads((F/'source-images.json').read_text())['images']
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bi(ru,en):return {'ru':ru,'en':en}
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def flag(code,field,ru,en,pages,**kw):return {'code':code,'field':field,'severity':'review','status':'open','message':bi(ru,en),'sourcePages':pages,**kw}
def key(s):return s['brand']+'/'+s['slug']
existing={};existingmeta={}
for f in (R/'content/products/conmed').glob('*.json'):
 s=json.loads(f.read_text())
 if (s.get('sourcePdf')or'').find('/arthroscopy-product-catalog/')>=0 or s.get('status')!='published':continue
 existingmeta[key(s)]=s
 codes=set(s.get('refCodes',[]))
 for c in s.get('components',[]):codes.update(c.get('refCodes',[]))
 for code in codes:existing.setdefault(code,key(s))
# Explicit title repair where the manufacturer's decorative wordmark has no text layer.
headingFix={18:{'Kits — ':''},24:{'™ Adjustable Retractor Cannula':'ARC™ Adjustable Retractor Cannula','® Cannula System':'Dry-Doc® Cannula System','® Cannula':'Hex Flex® Cannula'},26:{'™ Limb Positioner':'AssistArm™ Limb Positioner'},50:{'™ Limb Positioner':'AssistArm™ Limb Positioner'},23:{'® Suture':'Hi-Fi® Suture','™ Hi-FI® Suture':'SutureLoop™ Hi-Fi® Suture'},111:{'™ Arthroscopic Energy Generator':'Edge™ Arthroscopic Energy Generator','™ Disposable Probes':'Edge™ Disposable Probes'}}
allSystems=collections.OrderedDict();overlaps=[];internalDuplicates=[];samples=[];owners=dict(existing);exclusions=[]
for page in layouts:
 n=page['pdfPage'];identity=page['category']+'-'+slug(page['title']['en']);s=allSystems.setdefault(identity,{'schemaVersion':1,'slug':identity,'brand':'conmed','category':page['category'],'subcategory':'','subcategories':[],'specialty':['orthopedics','sports'],'name':page['title'],'shortDescription':bi('Решения CONMED: '+page['title']['ru'].lower()+'.','CONMED solutions for '+page['title']['en'].lower()+'.'),'description':bi('Система CONMED «'+page['title']['ru']+'». В разделах ниже представлены изделия и принадлежности из каталога производителя; выберите позиции по наименованию и каталожному номеру.','The CONMED '+page['title']['en']+' range brings together the products and accessories listed in the manufacturer’s catalog. Browse the sections below and select items by description and catalog number.'),'heroImage':'','imageType':'cutout','gallery':[],'features':[],'components':[],'componentGroups':[],'specTables':[],'refCodes':[],'sourcePages':[],'catalogEdition':None,'catalogTitle':bi('CONMED Arthroscopy Product Catalog — каталог продукции','CONMED Arthroscopy Product Catalog'),'isNew':False,'status':'draft','catalogType':'list','layout':'list','related':[],'availabilityNote':bi('Не вся продукция может быть доступна на всех рынках.','All products may not be available in all markets.'),'imageDimensions':{},'_flags':[],'_featureTexts':set(),'_sourceRows':0})
 s['sourcePages'].append(n)
 if any(w in page['title']['en'].lower()for w in ['repair','fixation','reconstruction','screw','anchor','tenodesis']):
  if 'traumatology'not in s['specialty']:s['specialty'].append('traumatology')
 for gi,g in enumerate(page['groups']):
  title=g['title']
  for a,b in headingFix.get(n,{}).items():title=title.replace(a,b)
  # Keep a reviewed page heading when an outlined wordmark left only a trademark glyph.
  title=title.lstrip('®™ ');titleRU=translate(title);tid=f'page-{n:03}-group-{gi+1:02}';rows=[];rowSources=[];cellNotes=[];related=set();tableflags=[];s['_sourceRows']+=len(g['rows'])
  multi=g.get('columnCount',max([len(r['codes'])for r in g['rows']]+[1]));columns=[bi('Наименование','Description'),bi('Кат. №','Cat. No.')]
  if multi==2:
   columns={12:[bi('Наименование','Description'),bi('Без шовного материала','No Suture'),bi('Шовный материал Hi-Fi','Hi-Fi Suture')],13:[bi('Наименование','Description'),'PEEK',bi('Биокомпозит','Biocomposite')],14:[bi('Наименование','Description'),bi('Нити: белая, бело-синяя, бело-чёрная и/или бело-зелёная','Sutures: White, white-blue, white-black, and/or white-green'),bi('Нити: синяя, бело-синяя и/или бело-чёрная','Sutures: blue, white-blue, and/or white-black')]}[n]
  for ri,row in enumerate(g['rows']):
   desc=('4.2mm, Large Hub, Merlin®, Shaver, Great White' if n==94 and any(c['candidate']=='C9299M'for c in row['codes'])else row['description']);parts=re.split(r'(?<=[a-z)])\.\s+(?=[A-Z0-9])',desc)
   if len(parts)>1 and (len(desc)>180 or re.search(r'\b(This|The|can be|allows|allowing|will|must)\b',desc)):
    prose='. '.join(parts[:-1])+'.';desc=parts[-1];g.setdefault('_rowProse',[]).append(prose)
   codes=[None]*multi;audits=[];new=False;rowRelated=[]
   for ci,c in enumerate(row['codes']):
    printedColumn=c.get('printedColumn',ci);ident=f'{n:03}-{gi+1:02}-{ri+1:02}-{ci+1}';r=copy.deepcopy(records.get(ident,{}));value=r.get('value');reading=visual.get(ident)
    if reading:
     r['visualReading']=reading
     if reading.get('action')=='exclude':exclusions.append({'pdfPage':n,'description':desc,'candidate':c['candidate'],'reason':reading['note']});continue
     if reading.get('value') is not None and reading.get('agreesWithOCR'):
      value=reading['value'];r['value']=value;r['verificationStatus']='verified (visual + OCR)' if reading.get('agreesWithOCR') else 'visual source reading; agreement requires review'
    r['value']=value;r=corrected_record(r);value=r['value']
    candidate=c['candidate'];owner=owners.get(value or c['candidate'])
    if value and value.endswith('*'):
     base=value.rstrip('*');baseOwner=owners.get(base)
     s['_flags'].append(flag('unexplained-code-marker','specTables','На стр. 94 после артикула стоят * / ** без найденной расшифровки. На другой странице тот же базовый артикул напечатан без звёздочек.','Page 94 appends * / ** without a found legend; another source page prints the same base article without markers.',[n],itemName=desc,readings=[value,base],lineCrop=r.get('lineCrop')))
     if baseOwner:owner=baseOwner

    audit={'id':ident,'tableId':tid,'row':len(rows)+1,'column':printedColumn+2,'pdfPage':n,'bounds':r.get('sourceBounds',c['sourceBounds']),'coordinateSpace':'normalized','readings':r.get('readings',[]),'candidate':candidate,'value':value,'verificationStatus':r.get('verificationStatus'),'officialEvidence':r.get('officialEvidence',[]),'lineCrop':r.get('lineCrop')}
    if reading:audit['visualReading']=reading
    audits.append(audit)
    if owner and owner!=key(s):
     rowRelated.append(owner);overlaps.append({'system':identity,'pdfPage':n,'description':desc,'catalogNumber':value or candidate,'existingSystem':owner,'withinThisPdf':owner not in existingmeta});codes[printedColumn]=None
     cellNotes.append({'row':len(rows)+1,'column':printedColumn+2,'text':bi('См. связанную систему','See related system')});continue
    if owner==key(s):
     internalDuplicates.append({'system':identity,'pdfPage':n,'description':desc,'catalogNumber':value});codes[printedColumn]=None;continue
    codes[printedColumn]=value;new=True
    owners[value or candidate]=key(s)
    if value:s['refCodes'].append(value)
    else:tableflags.append(flag('catalog-number-unverified',f'specTables.{len(s["specTables"])}.rows.{len(rows)}','Каталожный номер не подтверждён по строке исходного PDF.','Catalog number not verified against the source PDF item line.',[n],itemName=desc,candidate=candidate,readings=r.get('readings',[]),lineCrop=r.get('lineCrop')))
   related.update(rowRelated)
   if not new:continue
   while len(codes)<multi:codes[printedColumn]=None
   rows.append([bi(translate(desc),desc)]+codes);rowSources.append({'pdfPage':n,'bounds':row['rowBounds'],'coordinateSpace':'normalized','codeEvidence':audits})
   samples.append({'system':identity,'pdfPage':n,'description':desc,'catalogNumbers':[c for c in codes if c]})
   unknowns=unknown(desc)
   if unknowns:tableflags.append(flag('translation-terminology',f'specTables.{len(s["specTables"])}.rows.{len(rows)-1}.0.ru','Требуется уточнить перевод наименования: '+', '.join(dict.fromkeys(unknowns)), 'Item terminology needs translation review: '+', '.join(dict.fromkeys(unknowns)),[n],itemName=desc,readings=[rows[-1][0]]))
   s['components'].append({'id':tid+'-row-'+str(len(rows)),'name':rows[-1][0],'refCodes':[c for c in codes if c],'image':'','showInGrid':False,'groupId':tid,'pdfPage':n})
  s['related']+=list(related)
  if not rows and n!=69:continue
  group={'id':tid,'title':bi(titleRU,title),'name':bi(titleRU,title),'sourcePages':[n],'images':[],'keyParameters':[]};table={'id':tid,'groupId':tid,'title':group['title'],'unit':None,'columns':columns,'rows':rows,'rowSources':rowSources,'cellNotes':cellNotes,'sourcePages':[n],'images':group['images'],'keyParameters':group['keyParameters']}
  notes=' '.join(g['notes']);prose=proseRU.get(notes)
  if prose and n not in [88,89,90]:
   group['description']=bi(prose,notes);table['description']=group['description']
   if n in [67,88,89,90]:tableflags.append(flag('specification-association',f'specTables.{len(s["specTables"])}.description','Проверьте полноту текста и привязку характеристик к изделиям на странице.','Check prose completeness and assignment of specifications to individual items.',[n],readings=[notes,prose]))
  elif notes and len(notes)>120:
   # Raw source prose stays in review evidence until its medical translation and association are resolved.
   tableflags.append(flag('subgroup-prose',f'specTables.{len(s["specTables"])}.description','Требуется перевод и привязка текста подраздела.','Subgroup prose translation and association require review.',[n],readings=[notes]))
  # Short numeric bullet specifications are not benefit cards.
  for f in g['features']:
   text=f['text'];ru=featuresRU.get(text)
   if not ru:
    tableflags.append(flag('feature-text-association','features','Требуется проверить извлечение текста выноски.','Extracted callout text requires checking.',[n],readings=[text]));continue
   if (re.search(r'\d',text)or re.search(r'^(?:Available|PEEK|Titanium|Stainless|Polyester|Single|Double|Triple|Disposable|Reusable|Material|Latex|Limited|Non-|Implants|Packaged|Sterile|Working|Length|Diameter)',text,re.I))and not re.search(r'\b(less|reduce|prevent|enhance|better|allow|easy|simpl|strong|provid|improv|protect|preserv|fixation|purchase)\b',text,re.I):
    parameter=bi('Характеристика','Specification');value=bi(ru,text)
    if re.search(r'working length',text,re.I):parameter=bi('Рабочая длина','Working length')
    elif re.search(r'diameter|\bdia\b',text,re.I):parameter=bi('Диаметр','Diameter')
    elif re.search(r'per box|/box',text,re.I):parameter=bi('Упаковка','Pack')
    group['keyParameters'].append({'parameter':parameter,'value':value,'pdfPage':n});continue
   if text in s['_featureTexts']:continue
   s['_featureTexts'].add(text)
   titleEN=text.split(' = ')[0] if ' = 'in text else title
   titleRU=translate(titleEN)
   s['features'].append({'id':'feature-'+str(len(s['features'])+1),'title':bi(titleRU,titleEN),'text':bi(ru,text),'image':'','sourcePages':[n],'bounds':f['bounds']})
  s['_flags']+=tableflags;s['componentGroups'].append(group)
  if rows:s['specTables'].append(table)
# Assign native caption-free source photos, keeping uncertain subgroup placement explicit.
for s in allSystems.values():
 for record in sourceimages:
  pages=set(record['sourcePages'])&set(s['sourcePages'])
  if not pages:continue
  a=assets.get(record['name'])
  if not a:
   s['_flags'].append(flag('image-processing','gallery','Обработка исходного изображения ещё не завершена.','Source image enhancement and masking are incomplete.',sorted(pages),asset=record['name']));continue
  a=copy.deepcopy(a);n=min(pages);groups=[g for g in s['componentGroups']if n in g['sourcePages']];pg=next(p for p in layouts if p['pdfPage']==n);sourceg={f'page-{n:03}-group-{i+1:02}':g for i,g in enumerate(pg['groups'])};b=record.get('sourceBounds',[0,0,1,1]);cy=(b[1]+b[3])/2;cx=(b[0]+b[2])/2
  def distance(g):
   gb=sourceg.get(g['id'],{}).get('headingBounds',[.1,.1,.9,.1]);return abs(cy-gb[1])+(.3 if (cx<.55)!=(gb[0]<.55)else 0)
  group=min(groups,key=distance)if groups else None
  caption=group['title']if group else s['name'];a['imageCaption']=caption;a['pdfPage']=n;s['gallery'].append(a);s['imageDimensions'][a['src']]={'width':a['width'],'height':a['height']}
  if group:
   group['images'].append(a)
   for t in s['specTables']:
    if t['id']==group['id']:t['images']=group['images']
  if not group or len(groups)>1:s['_flags'].append(flag('image-caption-association','gallery.'+str(len(s['gallery'])-1),'Проверьте соответствие фотографии подразделу и подписи.','Verify this source photo’s subgroup and caption association.',[n],asset=a['src'],readings=[caption]))
 if s['gallery']:
  hero=max(s['gallery'],key=lambda a:a['width']*a['height']);s['heroImage']=hero['src'];s['heroImageMeta']=hero
 else:s['_flags'].append(flag('hero-image-missing','heroImage','Не найдено подходящее изображение системы.','No suitable system image has been assigned.',s['sourcePages']))
 s['refCodes']=list(dict.fromkeys(s['refCodes']));s['relatedSystemSlugs']=list(dict.fromkeys(s.pop('related')));s['sourcePages']=sorted(set(s['sourcePages']))
# Families that consist exclusively of rows already owned elsewhere are references, never duplicate pages.
systems=[];omitted=[]
for s in allSystems.values():
 if not s['specTables'] and s['_sourceRows'] and not s['refCodes']:
  omitted.append({'name':s['name'],'sourcePages':s['sourcePages'],'related':s['relatedSystemSlugs'],'reason':'All catalog numbers already imported; duplicate page not created'});continue
 flags=s.pop('_flags');s.pop('_featureTexts');s.pop('_sourceRows');s['reviewFlags']=flags
 s=apply_system(polish(s,R));systems.append(s)
# The repeated Shutt small-joint set page adds one extra instrument: keep it inside the original family instead of a one-row duplicate page.
repeat=next((x for x in systems if x['sourcePages']==[85]),None)
original=next((x for x in systems if 63 in x['sourcePages']),None)
if repeat and original:
 for field in ['specTables','componentGroups','components','gallery','features','refCodes']:
  original[field]+=repeat[field]
 original['sourcePages']=sorted(set(original['sourcePages']+repeat['sourcePages']));original['imageDimensions'].update(repeat['imageDimensions']);original['imageAssignmentReview']+=repeat.get('imageAssignmentReview',[])
 original['relatedSystemSlugs']=list(dict.fromkeys(original['relatedSystemSlugs']+repeat['relatedSystemSlugs']));original['relatedSystemSlugs']=[k for k in original['relatedSystemSlugs']if k not in [key(original),key(repeat)]]
 original['reviewFlags']+=repeat['reviewFlags'];systems.remove(repeat)
 omitted.append({'name':repeat['name'],'sourcePages':[85],'related':[key(original)],'reason':'Repeated Shutt small-joint set page merged into the original family; its additional 35.60017 row is retained'})
 for row in samples:
  if row['system']==repeat['slug']:row['system']=original['slug']
profile={'sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'method':'600-DPI dual Tesseract + independent Apple Vision, supplied-source visual crops, official CONMED exact-code corroboration; Codex medical RU; native images enhanced with Real-ESRGAN 2x before rembg','layoutReviewed':True,'nonProductPages':[1,2,3,4,5,6,7,8,28,51,60,68,87,105,110,113,114,115,116],'systems':systems,'assets':list(assets.values())}
dump(R/'scripts/profiles/arthroscopy-product-catalog.json',profile);dump(F/'overlaps.json',{'overlaps':overlaps,'duplicateRows':internalDuplicates,'omittedDuplicateSystems':omitted,'officialEditionExclusions':exclusions});rng=random.Random(20261119);sample=rng.sample([r for r in samples if r['catalogNumbers']],min(20,len([r for r in samples if r['catalogNumbers']])));dump(F/'random-20-rows.json',sample)
print(json.dumps({'systems':len(systems),'tables':sum(len(s['specTables'])for s in systems),'rows':sum(len(t['rows'])for s in systems for t in s['specTables']),'assetsPrepared':len(assets),'overlaps':len(overlaps),'omittedDuplicateSystems':len(omitted),'flags':collections.Counter(f['code']for s in systems for f in s['reviewFlags'])},ensure_ascii=False))
