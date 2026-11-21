"""Source-reviewed descriptions and specifications transcribed from supplied pages, not another edition."""
import copy,json,re,difflib
from pathlib import Path
from arthroscopy_ru import translate,unknown
B=lambda ru,en:{'ru':ru,'en':en}
def param(ru,en,value):return {'parameter':B(ru,en),'value':value if isinstance(value,dict)else B(value,value)}
ROW_PROSE=[
'Пульт C8115 для помпы 24k полностью автоклавируемый. Пульт C8115 имеет 6 кнопок и 9 функций: управление давлением, расходом, скоростью аспирации, тампонадой, функцией Clearfield, очисткой шейвера, дренированием, пуском и остановкой.',
'Интерфейсный кабель 24K обеспечивает прямое соединение консоли D4000/D4000A с помпой 24K, позволяя помпе 24K управлять аспирацией через шейверный наконечник.',
'Датчик шейвера 24k900 подключается к помпе 24k и крепится на кабеле любого шейверного наконечника, позволяя помпе 24k управлять аспирацией через этот наконечник.',
'Этот артроскопический трубчатый комплект позволяет помпе 24k управлять оттоком и аспирацией шейвера.',
'Этот трубчатый комплект обеспечивает непосредственное измерение внутрисуставного давления. Он совместим только с тубусами артроскопов или канюлями с контролем давления.',
'Артроскопический комплект только для притока с соединением Luer Lock совместим с помпой 24k или 10k.',
'Артроскопический комплект только для притока имеет дополнительную линию аспирации шейвера для подключения к настенной системе. Линию можно отделить для применения с шейверным наконечником или отдельным источником аспирации.',
'Артроскопический комплект только для притока с адаптером Colder устанавливается на тубус артроскопа или канюлю Dyonics.',
'Лапароскопическая рукоятка для аспирации/ирригации с трубчатым комплектом совместима с определёнными канюлями CONMED Endoscopy.',
'Лапароскопическая рукоятка для аспирации/ирригации с трубчатым комплектом оснащена фиксированной канюлей 5 × 33 мм.',
'Этот артроскопический приточный комплект устанавливается на передней панели помпы 10k или 24k и используется в течение одного операционного дня.',
'Этот артроскопический приточный комплект предназначен исключительно для однократного применения с помпой 10k или 24k.'
]
def polish(s,root):
 F=root/'reports/conmed/arthroscopy-product-catalog';raw=json.loads((F/'caption-proposals.json').read_text())if(F/'caption-proposals.json').exists()else{}
 # Ambiguous optional photo-to-subgroup links are removed rather than presented as facts.
 for g in s['componentGroups']:g['images']=[]
 for t in s['specTables']:t['images']=[]
 decisions=[]
 for a in s['gallery']:
  name=a['name'];proposal=raw.get(name,{});cap=proposal.get('caption');acceptable=bool(cap and not re.search(r'[А-Яа-яЁё]',cap['en'])and not re.fullmatch(r'[^a-z]*',cap['en'])and not re.fullmatch(r'[A-Z]?CONMED|XPmed|XPMED',cap['en'],re.I)and not proposal.get('unknownTerminology')and not cap['en'].endswith('.')and not re.fullmatch(r'[^a-z]*[0-9][A-Za-z0-9. -]*',cap['en']))
  if acceptable:a['imageCaption']=cap
  else:a.pop('imageCaption',None)
  groups=[g for g in s['componentGroups']if a['pdfPage']in g['sourcePages']]
  def similarity(g):
   if not acceptable:return 0
   en=cap['en'].lower();options=[g['title']['en']]+[r[0]['en']for t in s['specTables']if t['groupId']==g['id']for r in t['rows']]
   return max([difflib.SequenceMatcher(None,re.sub('[^a-z0-9]','',en),re.sub('[^a-z0-9]','',x.lower())).ratio()for x in options]+[0])
  ranked=sorted([(similarity(g),g)for g in groups],key=lambda p:p[0],reverse=True)
  group=groups[0]if len(groups)==1 else ranked[0][1]if ranked and ranked[0][0]>.65 and(len(ranked)==1 or ranked[0][0]-ranked[1][0]>.08)else None
  if group:
   group['images'].append(a)
   for t in s['specTables']:
    if t['groupId']==group['id']:t['images']=group['images']
  decisions.append({'asset':name,'sourcePages':a['sourcePages'],'captionFromSource':a.get('imageCaption'),'groupId':group['id']if group else None,'unassignedPlacement':'Retained in the system gallery; no unsupported component association'if not group else None})
 s['imageAssignmentReview']=decisions
 s['reviewFlags']=[f for f in s['reviewFlags']if f['code']!='image-caption-association']
 if s['gallery']:
  s['heroImage']=s['gallery'][0]['src'];s['heroImageMeta']=s['gallery'][0]
 # Preserve the handpiece compatibility note above every table to which its source heading applies.
 for t in s['specTables']:
  n=t['sourcePages'][0]
  if 93<=n<=104:
   if n==93 and not any(x in t['title']['en']for x in ['UltraGator','UltraFRR','UltraTiger']):continue
   en='For use with Ergo (D4240, D4200), Advantage Turbo (D9924, D9920), and Advantage (D9824, D9820).'
   ru='Для применения с наконечниками Ergo (D4240, D4200), Advantage Turbo (D9924, D9920) и Advantage (D9824, D9820).'
   if 94<=n<=100:en=en[:-1]+' and Apex (C9820, C9824, C9828).';ru=ru[:-1]+' и Apex (C9820, C9824, C9828).'
   if n==101:en='For use with C9840 and MC9840 handpieces.';ru='Для применения с наконечниками C9840 и MC9840.'
   if n>=102:en='For use with MC9840 handpiece.';ru='Для применения с наконечником MC9840.'
   t['compatibilityNotes']=[{'title':B('Совместимость с наконечниками','Handpiece compatibility'),'text':B(ru,en),'sourcePages':[n]}]
 # Resolve the six real prose/specification association issues using the supplied source pages.
 for t in s['specTables']:
  n=t['sourcePages'][0];title=t['title']['en']
  if n==33 and 'Implants'in title:t['description']=B('Пуговица GraftMax сочетает удобство регулируемой петли с фиксацией трансплантата, характерной для петли фиксированной длины.','The GraftMax Button gives surgeons the benefits and ease of use of an adjustable loop button, with the graft fixation of a fixed loop.')
  if n==106 and any('24k'in str(c) for row in t['rows']for c in row[1:])and 'Technical' in title:
   t['keyParameters']=[param('Масса','Weight',B('10.3 фунта (4.6 кг)','10.3 lbs (4.6 Kg)')),param('Размеры (Ш × В × Г)','Dimensions (W × H × D)',B('14.0″ × 7.1″ × 15.9″ (35.6 × 18.0 × 40.4 см)','14.0″ × 7.1″ × 15.9″ (35.6 × 18.0 × 40.4 cm)')),param('Напряжение','Voltage',B('100–240 В переменного тока','100–240 VAC'))]
  if n==108 and 'Console'in title:
   t['description']=B('Настройка и заполнение выполняются быстрее и проще, чем у любой другой артроскопической помповой системы в мире. Помпа 10k применяется в артроскопии и лапароскопии.','Setup and priming are faster and easier than any arthroscopy pump system in the world. The 10k® pump can be used in arthroscopy and laparoscopy.')
   t['keyParameters']=[param('Максимальный расход','Maximum flow',B('2000 мл/мин','2000 ml/min')),param('Диапазон давления','Set pressure range',B('30–150 мм рт. ст.','30–150 mmHg')),param('Масса','Weight',B('7 фунтов','7 lbs')),param('Размеры (Ш × В × Г)','Dimensions (W × H × D)',B('7.75″ × 6.5″ × 8″','7.75″ × 6.5″ × 8″')),param('Напряжение','Voltage',B('100–240 В','100–240 V')),param('Сетевой кабель','Power cord',B('10′ (3 м)','10′ (3 m)'))]
 rowprose=json.loads((root/'reports/conmed/arthroscopy-product-catalog/row-prose-source.json').read_text())
 for entry,ru in zip(rowprose,ROW_PROSE):
  n,title,en,last=entry
  for t in s['specTables']:
   if n in t['sourcePages']and t['title']['en']==title.lstrip('®™ '):
    t['description']=B(ru,en)
    if last.startswith(('This ','Only ','Can ','Must ')):
     compatibility=B(translate(last),last);t.setdefault('compatibilityNotes',[]).append({'title':B('Совместимость','Compatibility'),'text':compatibility,'sourcePages':[n]})
     for row in t['rows']:row[0]=B(translate(title.split(' — ')[-1]),title.split(' — ')[-1])
 # Source pages 88–90 print specifications under each item, not as one unassigned block.
 replacements=[]
 for t in s['specTables']:
  n=t['sourcePages'][0]
  if n not in [88,89,90]:replacements.append(t);continue
  for i,row in enumerate(t['rows']):
   code=next((c for c in row[1:]if isinstance(c,str)),None);q=copy.deepcopy(t);q['id']=t['id']+'-item-'+str(i+1);q['groupId']=q['id'];q['title']=row[0];q['rows']=[row];q['rowSources']=[t['rowSources'][i]];q['description']=B('','');q['cellNotes']=[];q['images']=[a for a in s['gallery']if code and re.search(r'(?<![A-Za-z0-9])'+re.escape(code)+r'(?![A-Za-z0-9])',a.get('imageCaption',{}).get('en',''))];q['keyParameters']=[]
   if n==88:
    q['keyParameters']=[param('Высота','Height',B('5.6″ (14.2 см)','5.6″ (14.2 cm)')),param('Ширина','Width',B('14″ (35.6 см)','14″ (35.6 cm)')),param('Глубина','Depth',B('16.5″ (41.9 см)','16.5″ (41.9 cm)')),param('Масса','Weight',B('14.5 фунта (6.35 кг)','14.5 lbs (6.35 kg)'))]
   elif n==89:
    notes={'C9863':B('Для применения с консолями Advantage, E9000 и PowerPro.','For use with Advantage, E9000 and PowerPro Consoles.'),'MC5057':B('Для консолей Advantage, E9000 и PowerPro. Длина 12′ (3.6 м). Совместим с наконечниками MicroChoice, PowerPro, E9000 и MC Shaver.','For use with Advantage, E9000 and PowerPro Consoles. Length 12′ (3.6 m). Operates MicroChoice, PowerPro, E9000 and MC Shaver Handpieces.'),'P9305':B('Для всех изгибаемых шейверных насадок Merlin.','For use with all Merlin Bendable Shaver Blades.')}
    if code in notes:q['description']=notes[code]
   elif n==90:
    if code in ['D4240','D4200']:q['keyParameters']=[param('Частота вращения вперёд','Forward speed',B('500–12,000 об/мин','500–12,000 rpm')),param('Частота осцилляции','Oscillate speed',B('500–2,500 циклов/мин, одно- и многооборотная осцилляция','500–2,500 cpm, single- and multi-turn oscillate')),param('Масса','Weight',B('17.8 унции (505 г)','17.8 oz (505 g)'))];q['description']=B('Для шейверных насадок и боров с большим разъёмом. Совместим с Advantage и E9000.','For use with Large Hub Shaver Blades and Burs. For use with Advantage and E9000.')
    elif code=='D9900':q['keyParameters']=[param('Крутящий момент','Torque',B('10 дюйм-фунтов','10 inch-lbs')),param('Передаточное отношение','Gear box','5 : 1'),param('Масса','Weight',B('3.5 унции (100 г)','3.5 oz (100 g)'))]
   replacements.append(q)
 s['specTables']=replacements
 s['componentGroups']=[{'id':t['groupId'],'title':t['title'],'name':t['title'],'sourcePages':t['sourcePages'],'images':t.get('images',[]),'keyParameters':t.get('keyParameters',[])}for t in s['specTables']]
 
 if any('Y1802'in row[1:]for t in s['specTables']for row in t['rows']):
  s['reviewFlags'].append({'code':'manufacturer-description-conflict','field':'specTables','severity':'review','status':'open','message':B('На стр. 16 напечатано Y1802 с описанием синей нити; у CONMED этому цвету соответствует Y1802A. Код исходника сохранён, требуется уточнение.','Page 16 prints Y1802 for blue suture; CONMED assigns the blue configuration to Y1802A. Source code retained pending confirmation.'),'sourcePages':[16],'itemName':'Y-Knot Flex 1.8mm','readings':['Supplied PDF: Y1802 — blue suture','CONMED brochure: Y1802 — white-blue / white-black','CONMED brochure: Y1802A — blue / white-black'],'manufacturerUrl':'https://www.conmed.com/-/media/conmed/documents/literature/y-knotflex_productbrochure.ashx'})
 s['reviewFlags']=[f for f in s['reviewFlags']if not(f['code']=='subgroup-prose'and any(n in [33,88,89,90,106,108]for n in f['sourcePages']))]
 return s
