#!/usr/bin/env python3
"""One-time, lossless ordering-data regrouping and source-image recrops for the authorized CONMED draft."""
import json,copy,re,hashlib,os
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
REPORT=ROOT/'reports/conmed/list-layout';BACKUP=REPORT/'before';BACKUP.mkdir(parents=True,exist_ok=True)
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bi(ru,en):return {'ru':ru,'en':en}
files=[p for p in (ROOT/'content/products/conmed').glob('*.json')if json.loads(p.read_text())['status']=='draft']
for p in files:
 if not (BACKUP/p.name).exists():(BACKUP/p.name).write_bytes(p.read_bytes())
original=[json.loads(p.read_text())for p in sorted(BACKUP.glob('*.json'))]
assert len(original)==10
# Group assignment, preserving complete rows and all accepted reference codes.
groups={g['id']:(s,g)for s in original for g in s['componentGroups']}
assignments={
 'conmed-arthroscopes':['quicklatch-2-9mm-arthroscope','autoclavable-1-9mm-arthroscope','autoclavable-2-5mm-arthroscope','uhd-4mm-arthroscope','hd-autoclavable-4mm'],
 'sheath-and-bridge-systems':['quicklatch-2-9mm-sheath','sheath-1-9mm-arthroscope','sheath-2-5mm-arthroscope','doublelatch-bridge','doublelatch-hip-bridge','quicklatch-4mm-bridge','quicklatch-4mm-replacement-parts','quicklatch-4mm'],
 'cannulas':['bridge-cannulas','pressure-sensing-cannula','quick-connect-replacement-parts']}
names={'conmed-arthroscopes':bi('Артроскопы CONMED','CONMED arthroscopes'),'sheath-and-bridge-systems':bi('Системы тубусов и мосты','Sheath and bridge systems'),'cannulas':bi('Канюли','Cannulas')}
intros={
'conmed-arthroscopes':bi('Артроскопы CONMED диаметром 1.9, 2.5, 2.9 и 4 мм представлены в нескольких вариантах направления обзора. В каталоге приведены модели HD и UHD, а также совместимые варианты окулярного и картриджного соединения.','CONMED arthroscopes are available in 1.9, 2.5, 2.9 and 4 mm diameters with several viewing angles. The catalog includes HD and UHD models with eyecup and cartridge options.'),
'sheath-and-bridge-systems':bi('Системы тубусов и мостов CONMED включают решения QuickLatch® и DoubleLatch® для артроскопии. В разделах ниже приведены совместимые тубусы, мосты и запасные части с каталожными номерами.','CONMED sheath and bridge systems include QuickLatch® and DoubleLatch® solutions for arthroscopy. The sections below list compatible sheaths, bridges and replacement parts with their catalog numbers.'),
'cannulas':bi('Канюли CONMED предназначены для применения с артроскопическими мостовидными системами. Каталог объединяет мостовидные канюли, систему канюль с датчиком давления и запасные части для тубусов Quick-Connect®.','CONMED cannulas are used with arthroscopic bridge systems. This catalog brings together bridge cannulas, the pressure sensing cannula system and replacement parts for Quick-Connect® sheath sets.'),
'camera-systems':bi('Система CONMED IM8000 объединяет блок управления True HD 3MOS и автоклавируемые видеоголовки. Ниже представлены варианты Eyecup, Cartridge и Urology с их каталожными номерами.','The CONMED IM8000 system combines a True HD 3MOS camera control unit with autoclavable camera heads. Eyecup, Cartridge and Urology options are listed below with their catalog numbers.'),
'light-sources-and-light-guides':bi('В разделе представлены светодиодный источник LS8000, ксеноновый источник LS7700 и универсальные световоды CONMED. Таблицы содержат варианты световодов, адаптеров и соединений.','This section includes the LS8000 LED light source, LS7700 Xenon light source and CONMED universal light guides. The tables list light-guide, adapter and fitting options.'),
'medical-monitors':bi('Медицинские мониторы CONMED представлены моделями 4K UHD и HD. В каталоге также приведены беспроводные комплекты и защитные чехлы для мониторов.','The catalog includes CONMED 4K UHD and HD medical monitors. Wireless kits and protective monitor covers are also listed.'),
'surgical-video-carts-and-accessories':bi('Видеостойки CONMED VP8500 предназначены для размещения оборудования хирургической визуализации. Каталог включает стойки и принадлежности: кронштейны, держатели, полки и элементы крепления.','CONMED VP8500 video carts provide a platform for surgical imaging equipment. The catalog includes carts and accessories such as arms, holders, shelves and mounting components.'),
'looking-glass':bi('Каталог Looking Glass объединяет компоненты видеосистемы CONMED, источники света и принадлежности для видеостоек. Найдите нужный компонент в соответствующем разделе и добавьте его в запрос по каталожному номеру.','The Looking Glass catalog brings together CONMED video system components, light sources and video cart accessories. Find the required component in its section and add it to an inquiry by catalog number.'),
'uhd-laparoscopes':bi('Лапароскопы CONMED UHD представлены моделями со стандартной и увеличенной рабочей длиной. В таблице приведены варианты диаметра и направления обзора с каталожными номерами.','CONMED UHD laparoscopes are available with standard and extended working lengths. The table lists diameter and viewing-angle options with their catalog numbers.'),
'hd-laparoscopes':bi('Каталог HD-лапароскопов CONMED включает автоклавируемые модели диаметром 5.5 и 10 мм. Для каждой подгруппы приведены варианты направления обзора, рабочая длина и каталожные номера.','The CONMED HD laparoscope catalog includes autoclavable 5.5 and 10 mm models. Viewing-angle options, working lengths and catalog numbers are listed for each subgroup.'),
'sterilization-trays':bi('Лотки CONMED серии VP100X предназначены для хранения и обработки автоклавируемых устройств 2DHD. В разделе приведены лотки для видеоголовок, эндоскопов, тубусов, канюль и мостовидных систем.','CONMED VP100X trays support storage and reprocessing of autoclavable 2DHD devices. The catalog lists trays for camera heads, scopes, sheaths, cannulas and bridge systems.')}
merged=[]
for slug,gids in assignments.items():
 s=copy.deepcopy(groups[gids[0]][0]);s.update(slug=slug,name=names[slug],componentGroups=[],components=[],specTables=[],features=[],gallery=[],refCodes=[],sourcePages=[])
 s['review']['flags']=[];s['relatedSystemSlugs']=[x for x in assignments if x!=slug]
 for gid in gids:
  parent,g=groups[gid];s['componentGroups'].append(copy.deepcopy(g))
  for key in ['components','specTables','features']:s[key].extend(copy.deepcopy([x for x in parent[key]if x.get('groupId',x.get('id'))==gid]))
  s['gallery'].extend(copy.deepcopy(g.get('images',[])))
  s['sourcePages'].extend(g['sourcePages'])
  # Preserve source review concerns, but do not retain obsolete array-index paths.
  for flag in parent['review']['flags']:
   if flag.get('code')!='ocr-code-review'and flag not in s['review']['flags']:s['review']['flags'].append(copy.deepcopy(flag))
 s['sourcePages']=sorted(set(s['sourcePages']));s['refCodes']=list(dict.fromkeys(c for x in s['components']for c in x.get('refCodes',[])))
 s['sourcePageImages']=[f'/catalogs/conmed/advanced-visualization-system/pages-600/{n:03}.webp'for n in s['sourcePages']]
 s['heroImage']=s['gallery'][0]['src'];s['review']['regroupedFrom']=sorted({groups[g][0]['slug']for g in gids});merged.append(s)
remaining=[copy.deepcopy(s)for s in original if s['slug']not in ['arthroscopes-and-sheath-systems','uhd-and-hd-arthroscopes']];systems=remaining+merged
# Values are transcribed from existing source callouts; no numeric inference.
params={
'quicklatch-2-9mm-arthroscope':[(bi('Наружный диаметр','Outside diameter'),bi('2.9 мм','2.9 mm')),(bi('Рабочая длина','Working length'),bi('152 мм','152 mm')),(bi('Поле зрения','Field of view'),'100°'),(bi('Направление обзора','Viewing angle'),'0° / 30° / 45° / 70°')],
'autoclavable-1-9mm-arthroscope':[(bi('Рабочая длина','Working length'),bi('60 мм','60 mm'))],
'autoclavable-2-5mm-arthroscope':[(bi('Рабочая длина','Working length'),bi('72 мм','72 mm'))],
'hd-autoclavable-4mm':[(bi('Рабочая длина','Working length'),bi('170 мм','170 mm'))],
'uhd-4mm-arthroscope':[(bi('Наружный диаметр тубусов','Outside sheath diameter'),bi('5.5 / 5.9 мм','5.5 / 5.9 mm'))],
'quicklatch-4mm':[(bi('Наружный диаметр тубусов','Outside sheath diameter'),bi('5.5 / 5.9 мм','5.5 / 5.9 mm'))],
'hd-5-5mm-laparoscope':[(bi('Рабочая длина','Working length'),bi('325 мм','325 mm'))],
'hd-5-5mm-extended-laparoscope':[(bi('Рабочая длина','Working length'),bi('450 мм','450 mm'))],
'hd-10mm-laparoscope':[(bi('Рабочая длина','Working length'),bi('325 мм','325 mm'))],
'universal-light-guides':[(bi('Обработка','Reprocessing'),bi('Автоклавирование','Autoclavable')),(bi('Соединения','Fittings'),bi('Универсальные','Universal'))]}
benefit_titles={
'Equivalent light transmission and image size to a 4mm arthroscope':bi('Оптика при меньшем диаметре','Optics in a smaller diameter'),
'Increased depth-of-field and less distortion compared to competitive 4mm arthroscopes':bi('Глубина резкости и геометрия изображения','Depth of field and image geometry'),
'Increased durability with new proprietary sheath system':bi('Защита артроскопа','Arthroscope protection'),
'Smaller outside diameter allows for better maneuverability':bi('Манёвренность','Maneuverability'),
'Scope-sheath interface ensures excellent tip protection':bi('Защита дистального конца','Distal tip protection'),
'Ease-of-use increases efficiency':bi('Эффективность работы','Workflow efficiency'),
'Dual cannulation to provide separate fluid inflow and pressure measurement':bi('Раздельные каналы','Separate channels'),
'Outer cannula is removable for patient entry and cleaning':bi('Съёмная наружная канюля','Removable outer cannula'),
'Superior light transmission':bi('Светопропускание','Light transmission'),
'Lightweight and flexible':bi('Удобство обращения','Ease of handling')}
def numbers(ss):return Counter((t['id'],i,j,c)for s in ss for t in s['specTables']for i,row in enumerate(t['rows'])for j,c in enumerate(row)if j and isinstance(c,str))
assert numbers(original)==numbers(systems),'Ordering code cells changed'
for s in systems:
 s['catalogType']='list';s['description']=intros[s['slug']];s['shortDescription']=copy.deepcopy(s['description']);s['status']='draft'
 for g in s['componentGroups']:
  g['keyParameters']=[{'parameter':p,'value':v}for p,v in params.get(g['id'],[])]
  t=next(t for t in s['specTables']if t['id']==g['id']);t['description']=g.get('description',bi('',''));t['keyParameters']=g['keyParameters'];t['images']=g.get('images',[])
 new=[]
 for f in s['features']:
  text=f['text']['en'];title=f['title']['en']
  if re.search(r'working length|outside diameter|outside sheath diameters|field.of.view|angle.of.view',title+' '+text,re.I)and f['groupId']in params:continue
  if title in ['Autoclavable','Universal fittings']:continue
  if s['slug']=='sterilization-trays':
   # These are compatibility limits, not user benefits.
   t=s['specTables'][0];t.setdefault('compatibilityNotes',[]).append({'title':f['title'],'text':f['text']});continue
  if title==text:
   if title not in benefit_titles:raise ValueError('Unclassified duplicate feature '+title)
   f['title']=benefit_titles[title]
  new.append(f)
 s['features']=new
 # Source-only medical review labels are rebuilt after regrouping.
 s['review']['translatedFields']=[]
 def translated(v,p=''):
  if isinstance(v,dict):
   if set(['ru','en']).issubset(v)and v['ru']:s['review']['translatedFields'].append(p+'.ru')
   for k,x in v.items():
    if k!='review':translated(x,p+'.'+k if p else k)
  elif isinstance(v,list):
   for i,x in enumerate(v):translated(x,p+'.'+str(i))
 translated(s)
 s['review']['listLayoutMigration']={'sourceSystems':10,'codesUnchanged':True,'report':'reports/conmed/list-layout/report.json'}
 dump(ROOT/'content/products/conmed'/(s['slug']+'.json'),s)
for slug in ['arthroscopes-and-sheath-systems','uhd-and-hd-arthroscopes']:(ROOT/'content/products/conmed'/(slug+'.json')).unlink(missing_ok=True)
dump(REPORT/'report.json',{'status':'draft-only','systemsBefore':10,'systemsAfter':len(systems),'systems':[{'slug':s['slug'],'name':s['name'],'groups':[g['id']for g in s['componentGroups']],'rows':sum(len(t['rows'])for t in s['specTables'])}for s in systems],'orderingCodeCellsUnchanged':True,'codeCellSnapshot':[list(x)+[n]for x,n in sorted(numbers(original).items())]})
print('Regrouped',len(systems),'draft systems; all catalog-number cells unchanged.')
