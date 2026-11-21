"""Build the source-bound Joint recipe: reviewed rows, additive merges, no clinical invention."""
import json,re,hashlib,collections,sys
from pathlib import Path
from joint_catalogue_manifest import PAGES,SETS,MATERIALS,bi
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/joint-catalogue';A=R/'public/images/products/double-medical/joint-catalogue';PDF=R/'catalogs-source/double-medical/joint-catalogue.pdf';SOURCE='/catalogs/double-medical/joint-catalogue';rs=json.loads((F/'rows-evidence.json').read_text());assets={}
for file in ['prepared-assets.json','extra-assets.json','corrected-assets.json']:
 if(A/file).exists():assets.update(json.loads((A/file).read_text()))
ignored=set(json.loads((F/'ignored-qr-assets.json').read_text())) if(F/'ignored-qr-assets.json').exists()else set()
superseded={'page-007-xref-106','page-007-xref-107','page-007-xref-108','page-015-xref-220','page-015-xref-221','page-025-xref-351','page-025-xref-352'}
assets={k:v for k,v in assets.items()if k not in ignored|superseded}
terms=dict(line.rstrip('\n').split('\t')for line in (R/'scripts/profiles/joint-terms-ru.tsv').read_text().splitlines()if '\t'in line)
existing=['pbg-proximal-bone-growth-cementless-stem','cynthia-knee-system','angel-shoulder-system','anty-f-series'];systems={};unknown=[];sample=[];exceptions=[]

def flag(code,ru,en,pages,path='referenceTables',**extra):return {'code':code,'path':path,'sourcePages':pages,'message':bi(ru,en),**extra}
def photo(n,cy=None,lo=0,hi=1):
 candidates=[]
 for a in assets.values():
  for p in a['placements']:
   if p['pdfPage']!=n:continue
   b=p['bounds'];mid=(b[1]+b[3])/2
   if not lo<mid<hi:continue
   candidates.append((abs(mid-(cy if cy is not None else(lo+hi)/2)),a))
 return min(candidates,key=lambda a:a[0])[1]if candidates else None

def img(a,caption=None):
 if not a:return None
 d={k:a[k]for k in ['src','width','height','imageType','captionFree','imageEnhancement']};d['sourcePages']=sorted({p['pdfPage']for p in a['placements']})
 if caption:d['imageCaption']=caption
 return d

def dims(s,images):
 for a in images:
  if a:s.setdefault('imageDimensions',{})[a['src']]={'width':a['width'],'height':a['height']}

def translate(en):
 # This lexicon is authored by Codex for this run, without a translation adapter.
 en=en.strip();en=re.sub(r'(?i)\bO(?=#|mm)','0',en).replace('®','φ').replace('Ф','φ').replace('ф','φ').replace('$','φ');en=en.replace('Twin Peg Femoral Trial |','Twin Peg Femoral Trial I,').replace('Trial Plug |','Trial Plug I')
 if en=='Depth Gauge a':en='Depth Gauge' # stray OCR shape is absent from the printed label
 # A case label retains the set's identity in both languages.
 if re.search(r'Inst[r]?ument Case|Instument Case',en,re.I):
  for code,slug,ru,name,pages,sub,links in SETS:
   if en.casefold().replace('instument','instrument')==name.replace('Set','Case').casefold()or(name.startswith(en.split(' Instrument')[0])and len(en.split(' Instrument')[0])>8):return bi('Контейнер: '+ru,en)
  known={'Hip Stem Instrument Case':'Контейнер инструментов для бедренной ножки','Bipolar Cup Instrument Case':'Контейнер для биполярных чашек','Apollo Acetabular Cup Universal Instument Case':'Контейнер универсального набора для чашки Apollo','Apollo Acetabular Cup(62-72mm) Instument Case':'Контейнер набора для чашки Apollo 62-72мм'}
  if en in known:return bi(known[en],en)
 if not re.search(r'[A-Za-z]{2}',re.sub('mm','',en)):return bi(en.replace('mm','мм'),en)
 prefix=next((k for k in sorted(terms,key=len,reverse=True)if en==k or en.startswith(k+',')or en.startswith(k+' ')),None)
 if not prefix:unknown.append(en);return bi('Описание требует проверки перевода',en)
 tail=en[len(prefix):];replacements={'extra large':'очень большой','left medial':'левый медиальный','right medial':'правый медиальный','with Quick Coupling':'с быстросъёмным соединением','for Osteotome':'для остеотома','for Tibial Drill':'для тибиального сверла','for cannulated Drill Bits':'для канюлированных свёрл','Malleolar Clamp':'голеностопный зажим','Upper Shaft':'верхняя штанга','Arc-shaped':'дугообразный','Cruciform':'крестообразный','Semicircle':'полукруглый','Terrace shape':'ступенчатый','V shape':'V-образный','Flat':'плоский','long tip':'длинный наконечник','short tip':'короткий наконечник','small':'малый','medium':'средний','large':'большой','left':'левый','right':'правый','length':'длина','hexagonal':'шестигранный','cannulated':'канюлированное','curved':'изогнутый','straight':'прямой','triangular':'треугольный','Triangular':'треугольный'}
 for a,b in sorted(replacements.items(),key=lambda x:len(x[0]),reverse=True):tail=tail.replace(a,b)
 tail=tail.replace('mm','мм')
 if re.search(r'[a-z]{3,}',tail,re.I):unknown.append(en)
 return bi(terms[prefix]+tail,en)

def sizeValue(r):
 raw=r['itemValue'];en=raw.replace('®','φ').replace('ф','φ').replace('Ф','φ');en=en.replace('mmMm','mm').replace('Omm','0mm');en=re.sub(r'([0-4])4(?=\s+\dmm)',r'\1#',en)
 # Header alignment gives two independent parameter columns rather than guessing from REF digits.
 if len(r['columns'])>1 and ' / 'not in en:
  values=[c['readings']['PSM3']for c in r['columns']]
  if all(values)and re.sub(r'\s+','', ''.join(values))==re.sub(r'\s+','',raw):en=' / '.join(values)
 ru=en.replace('mm','мм').replace('Left','Левый').replace('Right','Правый').replace('small','малый').replace('medium','средний').replace('big','большой').replace('oversize','увеличенный')
 return bi(ru,en)

def init(slug,ru,en,sub='hip',instrument=False):
 if slug not in systems:
  systems[slug]={'slug':slug,'brand':'double-medical','category':'arthroplasty-instrument-sets'if instrument else'joint-replacement','subcategory':sub,'specialty':['orthopedics'],'name':bi(ru,en),'catalogType':'list'if instrument else'system','shortDescription':bi('Инструменты для эндопротезирования'if instrument else'Компоненты для эндопротезирования','Arthroplasty instruments'if instrument else'Joint replacement components'),'description':bi(ru+'. Каталожные номера и комплектация приведены по Joint Catalogue Double Medical.'if instrument else ru+'. Материалы и доступные исполнения приведены в таблицах каталожных номеров.',en+'. Catalog numbers and contents are listed according to the Double Medical Joint Catalogue.'if instrument else en+'. Materials and available configurations are listed in the reference tables.'),'heroImage':'','imageType':'cutout','gallery':[],'features':[],'components':[],'specTables':[],'referenceTables':[],'refCodes':[],'sourcePages':[],'catalogEdition':None,'catalogTitle':bi('Double Medical Joint Catalogue — каталог продукции','Double Medical Joint Catalogue'),'documentCover':SOURCE+'/pages/001.webp','isNew':False,'status':'draft','relatedSystemSlugs':[],'reviewFlags':[]}
 return systems[slug]
for n in range(4,40):
 page=[r for r in rs if r['pdfPage']==n];ys=sorted({r['tableHeaderY']for r in page});entries=PAGES[n]
 assert len(ys)==len(entries),(n,ys,entries)
 for i,(slug,ru,en,material,coating)in enumerate(entries):
  sub='hip'if n<=16 else'knee'if n<=31 else'radius'if n<=33 else'shoulder';s=init(slug,ru,en,sub);group=[r for r in page if r['tableHeaderY']==ys[i]];lo=ys[i-1]if i else .12;hi=ys[i+1]if i+1<len(ys)else .91
  title=bi(ru+(' · '+coating if coating else''),en+(' · '+coating if coating else''));tid=f'joint-{slug}-p{n}-{i+1}';params=[]
  if material:params.append({'parameter':bi('Материал','Material'),'value':MATERIALS.get(material,bi(material))})
  if coating:params.append({'parameter':bi('Покрытие','Coating'),'value':bi('Титановое'if coating=='Ti'else'Титан + гидроксиапатит',coating)})
  labels=[]
  for c in group[0]['columns']:
   label=re.sub(r'[^A-Za-z]','',c['header']);labels.append(label)
  headers={'Size':bi('Размер','Size'),'Length':bi('Длина','Length'),'Thickness':bi('Толщина','Thickness'),'Direction':bi('Сторона','Direction'),'Degree':bi('Угол','Degree'),'Holes':bi('Отверстия','Holes')}
  detail=bi(' / '.join(headers.get(x,bi(x))['ru']for x in labels)or'Размер',' / '.join(labels)or'Size')
  table={'id':tid,'title':title,'unit':('mm'if any('mm'in c['header']for c in group[0]['columns'])or any('mm'in r['itemValue']for r in group)or any('Length'in c['header']or'Thickness'in c['header']for c in group[0]['columns'])else''),'columns':[bi('Наименование','Description'),bi('REF'),detail],'rows':[],'rowSources':[],'keyParameters':params,'sourcePages':[n],'sourcePdf':SOURCE+'/source.pdf','hideDescriptionColumn':True}
  a=photo(n,cy=.23 if i==0 else ys[i],lo=lo,hi=hi)
  if a:table['images']=[img(a,title)];dims(s,[a]);s['gallery']+=[]if any(x['src']==a['src']for x in s['gallery'])else[img(a,title)];s['heroImage']=s['heroImage']or a['src']
  for r in group:
   detailValue=sizeValue(r);table['rows'].append([bi(title['ru']+' · '+detailValue['ru'],title['en']+' · '+detailValue['en']),r['value'],detailValue]);table['rowSources'].append({'pdfPage':n,'sourceBounds':[r['sourceBounds'][0],r['sourceBounds'][1],.6,r['sourceBounds'][3]],'codeEvidence':[{'tableId':tid,'row':len(table['rows']),'readings':r['readings'],'verificationStatus':r['verificationStatus']}],'itemReadings':r['itemReadings'],'itemVerification':r['itemVerification']});s['refCodes'].append(r['value']);sample.append({'system':slug,'pdfPage':n,'REF':r['value'],'sizeDescription':detailValue['en']})
  if n==34 and i==0:
   table['cellNotes']=[{'row':1,'column':3,'text':bi('В источнике напечатано 6.7m; в брошюре Angel — 6.7 мм. Уточняйте у менеджера.','The source prints 6.7m; the Angel brochure gives 6.7 mm. Confirm with your sales manager.')}];s['reviewFlags'].append(flag('brochure-unit-conflict','REF 13Y010001S: в Joint Catalogue напечатано 6.7m, в брошюре Angel — 6.7 мм.','REF 13Y010001S: Joint Catalogue prints 6.7m; Angel brochure gives 6.7 mm.',[34],readings=['Joint Catalogue: 107mm×6.7m','Angel brochure: 107mm×6.7mm']))
  if n==36 and i==0:table['note']=bi('Для REF 13Y081015S здесь указано 5 мм; в отдельной брошюре Angel — 15 мм. Уточняйте у менеджера.','REF 13Y081015S is listed here as 5 mm; the separate Angel brochure lists 15 mm. Confirm with your sales manager.');s['reviewFlags'].append(flag('brochure-conflict','REF 13Y081015S: Joint Catalogue — 5 мм; брошюра Angel — 15 мм.','REF 13Y081015S: Joint Catalogue 5 mm; Angel brochure 15 mm.',[36],readings=['Joint Catalogue: 5','Angel brochure: 15']))
  if n==13:s['reviewFlags'].append(flag('coating-header-conflict','В таблице полиэтиленового вкладыша заголовок REF содержит «Ti coating»; покрытие не подтверждено.','The polyethylene liner REF header says Ti coating; coating is not established.',[13]))
  s['referenceTables'].append(table);s['sourcePages'].append(n)
for setCode,slug,ru,en,pages,sub,links in SETS:
 s=init(slug,ru,en,sub,True);s['setCode']=setCode;s['refCodes'].append(setCode);s['relatedSystemSlugs']=links
 for n in pages:
  group=[r for r in rs if r['pdfPage']==n and not r['isSetHeading']];tid=f'joint-{slug}-p{n}';title=bi('Инструменты · страница '+str(n),'Instruments · page '+str(n));table={'id':tid,'title':title,'columns':[bi('Наименование','Description'),bi('REF')],'rows':[],'rowSources':[],'rowImages':[],'rowImageLabel':bi('Инструмент','Instrument'),'sourcePages':[n]}
  for r in group:
   name=translate(r['itemValue']);table['rows'].append([name,r['value']]);table['rowSources'].append({'pdfPage':n,'sourceBounds':[r['sourceBounds'][0],r['sourceBounds'][1],.65,r['sourceBounds'][3]],'codeEvidence':[{'tableId':tid,'row':len(table['rows']),'readings':r['readings'],'verificationStatus':r['verificationStatus']}],'itemReadings':r['itemReadings'],'itemVerification':r['itemVerification']});s['refCodes'].append(r['value']);a=photo(n,sum(r['sourceBounds'][1::2])/2)
   table['rowImages'].append(img(a,name));dims(s,[a]);sample.append({'system':slug,'pdfPage':n,'REF':r['value'],'sizeDescription':name['en']})
   if a and re.search(r'Inst[r]?ument Case|Instument Case',r['itemValue'],re.I):s['heroImage']=a['src'];s['gallery']=[img(a,name)]
   if a and not s['heroImage']:s['heroImage']=a['src'];s['gallery']=[img(a,name)]
   if not re.fullmatch(r'\d{9}',r['value']):s['reviewFlags'].append(flag('printed-code-pattern','В источнике напечатан восьмизначный код '+r['value']+'; требуется подтверждение производителя.','The source prints eight-digit code '+r['value']+'; manufacturer confirmation is required.',[n],'specTables',readings=[x['text']for x in r['readings']]))
  if n==82:s['reviewFlags'].append(flag('incomplete-source-descriptions','Шесть строк REF содержат название вкладыша без размера; следующие строки — только размеры. Соответствие размеров первым кодам не установлено.','Six REF rows name a trial liner without a size; alternating rows contain dimensions only. Size-to-code pairing for the incomplete rows is not established.',[82],'specTables',readings=['113099200 / 113099400 / 113099600 / 115091300 / 115662600 / 115662800: Apollo 10° Trial Liner,','113099300 / 113099500 / 113099700 / 115662500 / 115662700 / 115662900: φ62/36 / φ64/36 / φ66/36 / φ68/36 / φ70/36 / φ72/36 mm']))
  s['specTables'].append(table);s['sourcePages'].append(n)
 for target in links:
  if target in systems:systems[target]['relatedSystemSlugs'].append(slug)
# All source codes remain byte-for-byte as verified, including the lettered implant prefixes.
for s in systems.values():
 s['sourcePages']=sorted(set(s['sourcePages']));s['refCodes']=list(dict.fromkeys(s['refCodes']));s['relatedSystemSlugs']=list(dict.fromkeys(s['relatedSystemSlugs']))
 if not s['heroImage']:s['reviewFlags'].append(flag('missing-product-image','Нет проверенного изображения изделия.','No verified product image is available.',s['sourcePages']))
 for table in s['referenceTables']:
  codes=[row[1]for row in table['rows']if not re.fullmatch(r'\d{9}S',row[1])]
  if codes:exceptions.append({'system':s['slug'],'sourcePages':table['sourcePages'],'codes':codes,'status':'resolved: letter prefix visually confirmed in source; table pattern consistent'})
 if any(name in unknown for t in s['specTables']for row in t['rows']for name in [row[0]['en']]):s['reviewFlags'].append(flag('translation-review','Нужна проверка отдельных названий инструментов.','Some instrument labels need translation review.',s['sourcePages']))
for s in systems.values():
 for t in s['specTables']+s['referenceTables']:
  for row in t['rowSources']:row['bounds']=row['sourceBounds'];row['coordinateSpace']='normalized'
systems['pbg-proximal-bone-growth-cementless-stem']['relatedSystemSlugs'].insert(0,'anty-f-series')
from joint_owner_resolutions import apply as apply_owner_resolutions
digest=hashlib.sha256(PDF.read_bytes()).hexdigest()
systems={slug:apply_owner_resolutions(system,digest)for slug,system in systems.items()}
merges=[{k:s[k]for k in ['slug','brand','referenceTables','refCodes','relatedSystemSlugs','sourcePages','reviewFlags']}for slug,s in systems.items()if slug in existing];new=[s for slug,s in systems.items()if slug not in existing]
for patch in merges:
 if patch['slug']=='cynthia-knee-system':patch['referenceVariantId']='primary'
profile={'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'layoutReviewed':True,'method':'600-DPI PSM3/PSM11 + independent Vision + Codex visual row checks; additive REF merges','catalogTitle':bi('Double Medical Joint Catalogue — каталог продукции','Double Medical Joint Catalogue'),'nonProductPages':[1,2,3,71,81,94,95,96],'systems':new,'merges':merges,'assets':list(assets.values())}
(R/'scripts/profiles/double-medical-joint-catalogue.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n');(F/'source-pattern-exceptions.json').write_text(json.dumps(exceptions,ensure_ascii=False,indent=2));(F/'all-rows.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2));(F/'translation-unknown.json').write_text(json.dumps(sorted(set(unknown)),ensure_ascii=False,indent=2));print('New',len(new),'merges',len(merges),'sets',len(SETS),'assets',len(assets),'unknown translations',sorted(set(unknown)));print('Flags',[(s['slug'],[f['code']for f in s['reviewFlags']])for s in systems.values()if s['reviewFlags']])
