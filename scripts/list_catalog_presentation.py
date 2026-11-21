"""Default presentation metadata for future OCR list imports; never changes ordering rows."""
import re,copy

def prepare_list_catalog(system):
 system['catalogType']='list'
 groups={g['id']:g for g in system.get('componentGroups',[])}
 features=[]
 rules=[(r'working length\s*([\d.]+\s*mm)',{'ru':'Рабочая длина','en':'Working length'}),(r'([\d.]+\s*mm)\s+outside diameter',{'ru':'Наружный диаметр','en':'Outside diameter'}),(r'([\d°.,\s]+)\s*field.of.view',{'ru':'Поле зрения','en':'Field of view'}),(r'([\d°.,\sand]+)\s*angle.of.view',{'ru':'Направление обзора','en':'Viewing angle'})]
 for feature in system.get('features',[]):
  group=groups.get(feature.get('groupId'));matched=False
  if group:
   for pattern,parameter in rules:
    match=re.search(pattern,feature.get('text',{}).get('en',''),re.I)
    if match:
     value=match[1].strip();group.setdefault('keyParameters',[]).append({'parameter':parameter,'value':{'en':value,'ru':value.replace('mm','мм').replace(' and ',' и ')},'sourcePages':feature.get('sourcePages',[]),'sourceBounds':feature.get('sourceBounds')});matched=True;break
  if matched:continue
  # Identical short callouts require semantic review, not synthetic feature cards.
  if feature.get('title')==feature.get('text'):
   if group:group.setdefault('unclassifiedCallouts',[]).append(copy.deepcopy(feature))
   system.setdefault('review',{}).setdefault('flags',[]).append({'path':'componentGroups.'+str(feature.get('groupId')),'code':'callout-classification-review','message':{'ru':'Классифицируйте выноску как параметр или преимущество; одинаковые заголовок и текст не показаны в карточке.','en':'Classify this callout as a specification or benefit; duplicate title/text is not rendered as a feature card.'},'sourcePages':feature.get('sourcePages',[])})
  else:features.append(feature)
 system['features']=features
 for table in system.get('specTables',[]):
  group=groups.get(table.get('groupId',table.get('id')),{});table['description']=copy.deepcopy(group.get('description',{'ru':'','en':''}));table['keyParameters']=copy.deepcopy(group.get('keyParameters',[]));table['images']=copy.deepcopy(group.get('images',[]))
 # Do not concatenate subgroup descriptions into the overview.
 if not system.get('overview'):
  system['overview']={lang:system['name'][lang]+('. 'if not system['name'][lang].endswith('.')else ' ')+({'ru':'В разделах ниже приведены компоненты и каталожные номера производителя.','en':'The sections below list manufacturer components and catalog numbers.'}[lang])for lang in ['ru','en']}
 system['description']=system['overview']
 return system
