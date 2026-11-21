"""SPINENDOS photo/caption recipe with independent code evidence and Codex medical RU."""
import json,re,hashlib,sys,collections
from pathlib import Path
from spinendos_layout import ZONES
from spinendos_source_corrections import apply_system, CORRECTION
from spinendos_caption_review import CAPTIONS
R=Path(__file__).resolve().parents[1];F=R/'reports/spinendos/endoscopic-spine-surgery-system';P=R/'catalogs-source/spinendos/endoscopic-spine-surgery-system.pdf';REF='/catalogs/spinendos/endoscopic-spine-surgery-system';O=R/'public/images/products/spinendos/endoscopic-spine-surgery'
def bi(ru,en):return {'ru':ru,'en':en}
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
verification=json.loads((F/'verification.json').read_text());records=verification['records'];assets=json.loads((O/'prepared-assets.json').read_text());visions={n:json.loads((F/'vision'/f'{n:03}.json').read_text())for n in range(3,20)}
# Whitespace joining is evidence-preserving; ambiguous characters are never silently substituted.
PAT=re.compile(r'(?:SP|5P|9P)\s*[0O]\s*(?:\d\s*){5}\.\s*\d(?:\s*\d){2}(?:[A-Z]|\d)?')
FAMILIES=[('spinal-endoscopes','Спинальные эндоскопы','Spinal endoscopes','Эндоскопы для трансфораминального и интерламинарного доступа, стеноза и шейного отдела.','Endoscopes for spinal access, stenosis and the cervical spine.'),('guiding-cannulas-guide-wires-and-dilators','Направляющие канюли, спицы и дилататоры','Guiding cannulas, guide wires and dilators','Инструменты для формирования и последовательного расширения эндоскопического доступа.','Instruments for establishing and progressively dilating the endoscopic access.'),('working-tubes','Рабочие тубусы','Working tubes','Рабочие тубусы с различной геометрией окон и дистального конца.','Working tubes with different window and distal-tip configurations.'),('trephines-reamers-drills-and-protection-tubes','Трепаны, рашпили, свёрла и защитные тубусы','Trephines, reamers, drills and protection tubes','Инструменты для обработки костной ткани и защитные тубусы.','Bone-working instruments and protection tubes.'),('forceps-punches-and-scissors','Щипцы, выкусыватели и ножницы','Forceps, punches and scissors','Захватывающие, чашечные и микрощипцы, кусачки Kerrison и ножницы.','Grasping, cup and micro forceps, Kerrison punches and scissors.'),('handles-hammer-and-accessories','Рукоятки, молоток и принадлежности','Handles, hammer and accessories','Рукоятки, зонды и принадлежности для спинальной эндоскопии.','Handles, probes and accessories for spinal endoscopy.')]
INTRO=bi('В каталоге описаны трансфораминальный и интерламинарный эндоскопические доступы к позвоночнику с использованием направляющей спицы, последовательных дилататоров и рабочего тубуса. Эндоскопическая визуализация сочетается с применением специализированных инструментов для работы с диском, костными структурами и мягкими тканями.','The catalog describes transforaminal and interlaminar endoscopic spinal approaches using a guide wire, sequential dilators and a working tube. Endoscopic visualization is combined with specialized instruments for disc tissue, bone and soft tissue work.')
# Authored locally by Codex: source-specific medical phrases, no external translation adapter.
PHRASES=[('Rod Forceps','Стержневые щипцы'),('Forceps Handle','Рукоятка щипцов'),('Curved up','Изгиб вверх'),('Endoscopic Kerrison rotatable irrigation','Поворотные эндоскопические кусачки Kerrison с ирригацией'),('Endoscopic Kerrison BDsys, Curved up','Эндоскопические кусачки Kerrison BDsys, изгиб вверх'),('Endoscopic Kerrison BDsys','Эндоскопические кусачки Kerrison BDsys'),('Suction Punch SPINE rotatable /detach','Поворотный разборный аспирационный выкусыватель SPINE'),('Dilator working sleeve straight tip','Рабочий тубус дилататора с прямым концом'),('Dilator working sleeve oblique tip','Рабочий тубус дилататора с косым концом'),('Working tube with oblique window','Рабочий тубус с косым окном'),('Working tube with dual window','Рабочий тубус с двойным окном'),('Working tube with lateral window','Рабочий тубус с боковым окном'),('Working tube with long window','Рабочий тубус с удлинённым окном'),('Working tube with elevator tip','Рабочий тубус с концом-элеватором'),('Working tube, straight','Прямой рабочий тубус'),('Spare cap for working tube','Запасной колпачок рабочего тубуса'),('Spare cap for endoscope','Запасной колпачок эндоскопа'),('Straight jaw (double action)','Прямые бранши двойного действия'),('Straight jaw, double action','Прямые бранши двойного действия'),('Upward angled jaw','Бранши, изогнутые вверх'),('Straight (S)','Прямые бранши (S)'),('Straight (M)','Прямые бранши (M)'),('Straight jaw','Прямые бранши'),('Upward jaw','Бранши, направленные вверх'),('Downward jaw','Бранши, направленные вниз'),('Left jaw','Левые бранши'),('Right jaw','Правые бранши'),('Dilator, conical tube','Конический трубчатый дилататор'),('Dilator, complanate','Уплощённый дилататор'),('Dilator, conical','Конический дилататор'),('Dilator conical','Конический дилататор'),('Dilator, curved','Изогнутый дилататор'),('Dilator 2-channels','Дилататор с 2 каналами'),('Dilator 2-channel','Дилататор с 2 каналами'),('Dilator 2-chanels','Дилататор с 2 каналами'),('Spinal endoscope','Спинальный эндоскоп'),('Rasp, retrograde','Ретроградный рашпиль'),('Hook probe','Крючковидный зонд'),('Bone chisel; blunt','Тупое костное долото'),('Bone chisel: awl','Костное долото-шило'),('Bone chisel; awl','Костное долото-шило'),('Bone chisel','Костное долото'),('Bone Curette','Костная кюретка'),('Endo-Bone knife','Эндоскопический костный нож'),('Probe Handle','Рукоятка зонда'),('Endoscopic Kerrison Handle','Рукоятка эндоскопических кусачек Kerrison'),('Punch, tube shaft','Выкусыватель с трубчатым стержнем'),('Endo-Flexprobe. Suction.','Гибкий аспирационный зонд Endo-Flexprobe.'),('Endo-Probe.','Эндоскопический зонд.'),('With quickLock mechanism for all blades','С механизмом QuickLock для всех лезвий'),('direction of view','направление обзора'),('working length','рабочая длина'),('outer diameter','наружный диаметр'),('diameter','диаметр'),('length','длина'),('360° rotating','поворот на 360°'),('detachable','разборный'),('cervical','для шейного отдела'),('Straight, overload protection with irrigation','Прямые бранши, защита от перегрузки и ирригация'),('PATENT','ПАТЕНТ'),('Obturator','Обтуратор'),('Dilator','Дилататор'),('Working tube','Рабочий тубус'),('Probe','Зонд'),('wide','ширина')]
unknown=[]
def translate(en):
 ru=en
 for a,b in [('Extracting Forceps','Экстракционные щипцы'),('Steel ruler','Стальная линейка')]:ru=ru.replace(a,b)
 for a,b in PHRASES:ru=re.sub(r'(?<![A-Za-z])'+re.escape(a)+r'(?![A-Za-z])',lambda m:b,ru,flags=re.I)
 ru=re.sub(r'\bmm\b','мм',ru,flags=re.I);ru=ru.replace('WC','рабочий канал ').replace('WL','рабочая длина ').replace('ID','внутренний диаметр ').replace('OD','наружный диаметр ')
 ru=re.sub(r'\bL(?=\d)','длина ',ru)
 return ru

def caption(r,z,rr):
 n=r['pdfPage'];b=r['sourceBounds'];x,y=b[0],b[1];cy=(b[1]+b[3])/2
 # Forceps tables keep jaw, length and diameter independently.
 tab=n in [14,15,16]or(n==17 and y<.34)
 if tab and not r['value'].endswith('H'):
  same=[a for a in visions[n]if abs((a['bounds'][1]+a['bounds'][3])/2-cy)<.008]
  jaw=' '.join(a['text']for a in same if .35<a['bounds'][0]<.51)
  dim=' '.join(a['text']for a in same if a['bounds'][0]>.66)
  length=re.search(r'L\s*(\d+)\s*mm',dim);diam=re.search(r'mm\s*[^\d]*(\d+(?:\.\d+)?)\s*mm',dim)
  return jaw, length.group(1)if length else'',diam.group(1)if diam else'',dim
 # Bound each caption by its next row and its neighboring column, never by reading order alone.
 nearby=[q for q in rr if q['id']!=r['id']and abs(q['sourceBounds'][1]-y)<.009 and q['sourceBounds'][0]>x+.07]
 right=min([q['sourceBounds'][0]-.008 for q in nearby]+[z[6]])
 nextrows=[q['sourceBounds'][1]-.002 for q in rr if q['sourceBounds'][1]>y+.012 and abs(q['sourceBounds'][0]-x)<.07]
 bottom=min(nextrows+[y+.065,z[7]])
 lines=[]
 for a in sorted(visions[n],key=lambda a:(round(a['bounds'][1],3),a['bounds'][0])):
  ab=a['bounds'];ay=(ab[1]+ab[3])/2
  if cy-.009<=ay<bottom and x-.012<=ab[0]<right:
   text=a['text'];matches=list(PAT.finditer(text))
   if matches:
    # A line containing another item never enters this caption.
    if not any(re.sub(r'\s+','',m.group())in {r['candidate'],r['value']}for m in matches):continue
    text=text[matches[0].end():].strip(' #*☆★+¥x')
   if text and re.search(r'[A-Za-z0-9]',text):lines.append(text)
 text=' '.join(lines);text=re.sub(r'^Same,?\s*','Spinal endoscope, ',text)
 # Prefix a product name only when the source caption is dimensions alone.
 if not re.search(r'[A-Za-z]{3}',re.sub(r'(?:mm|WL|WC|OD|ID)','',text)) or re.match(r'^(?:\d|[IL]D\d|OD\d|L\d|HTP)',text):text=z[1]+(': '+text if text else '')
 if not text:text=z[1]
 return text,None,None,None

def photo(r,z):
 manual={'SP082610.008':438,'SP082610.009':438,'SP082600.001H':523,'SP082700.041H':539,'SP082710.112H':240}
 if r['value']in manual:z=(*z[:8],manual[r['value']])
 aa=[a for a in assets.values()if a['pdfPage']==r['pdfPage']]
 if z[8]:
  specific=next((a for a in aa if a['pdfImageXref']==z[8]),None)
  if specific:return specific
 x,y=r['sourceBounds'][:2]
 def score(a):
  b=a['bounds'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
  return abs(y-b[3])+max(0,b[1]-y)*5+abs(x-cx)*.35+(1 if b[1]>y+.03 else 0)
 return min(aa,key=score)if aa else None
systems=[];assigned=[];corrections=[{'pdfPage':5,'printed':'Ø9..5mm','corrected':'9.5 mm','code':'SP082616.301','visibility':'internal-only','basis':'Codex visual reading of 600-DPI caption'}];markers=[]
for fi,(slug,ru,en,tagru,tagen)in enumerate(FAMILIES):
 s={'schemaVersion':1,'slug':slug,'brand':'spinendos','brandName':bi('SPINENDOS','SPINENDOS'),'category':'endoscopic-spine-surgery','subcategory':'','specialty':['spine'],'catalogType':'list','name':bi(ru,en),'shortDescription':bi(tagru,tagen),'description':{l:INTRO[l]+' '+v for l,v in [('ru',tagru),('en',tagen)]},'heroImage':'','imageType':'cutout','gallery':[],'variants':[],'features':[],'hotspots':[],'components':[],'componentGroups':[],'specTables':[],'refCodes':[],'sourcePages':[],'catalogEdition':None,'catalogTitle':bi('SPINENDOS Endoscopic Spine Surgery System — каталог продукции','SPINENDOS Endoscopic Spine Surgery System — Product Catalog'),'isNew':True,'status':'draft','reviewFlags':[],'relatedSystemSlugs':['spinendos/'+a[0]for a in FAMILIES if a[0]!=slug],'imageDimensions':{}}
 for zi,z in enumerate(ZONES):
  if z[0]!=fi:continue
  rr=[r for r in records if r['pdfPage']==z[3]and z[4]-.01<=r['sourceBounds'][0]<z[6]and z[5]-.005<=r['sourceBounds'][1]<z[7]]
  if not rr:continue
  group=f'page-{z[3]:03}-group-{zi+1:02}';table={'id':group,'groupId':group,'title':bi(z[2],z[1]),'unit':None,'columns':[bi('Наименование','Description'),bi('Кат. №','Cat. No.')],'rows':[],'rowSources':[],'sourcePages':[z[3]],'images':[]}
  is_table=z[3]in [14,15,16]or(z[3]==17 and z[5]<.34)
  if is_table and fi==4:table['columns'] += [bi('Длина, мм','Length, mm'),bi('Диаметр, мм','Diameter, mm')]
  for r in rr:
   if r['id']in assigned:continue
   code=r['value'];text,length,diam,rawdim=caption(r,z,rr)
   text=CAPTIONS.get((r['pdfPage'],code),text)
   if text=='traight jaw':text='Straight jaw'
   text=text.replace('rotatable/detach','rotatable /detach').replace('mт','mm').replace('Д','Ø')
   if code=='SP082700.041H'and fi==4:continue
   text=text.replace('9..5','9.5');text=re.sub(r'(?<=\d)\s*mm',' mm',text);text=text.replace('0D','OD').replace('1D','ID')
   if code=='SP082616.301':text='Dilator 2-channels, L225mm Ø9.5mm'
   # Contextual names for descriptions that consist solely of table jaw geometry.
   desc=bi(z[2]+': '+translate(text)if is_table else translate(re.sub('^'+re.escape(z[1])+r'(?=:|$)',z[2],text,flags=re.I)),z[1]+': '+text if is_table else text)
   row=[desc,code];idx=len(table['rows']);ev={'id':r['id'],'pdfPage':r['pdfPage'],'tableId':group,'row':idx+1,'column':2,'bounds':r['sourceBounds'],'coordinateSpace':'normalized','value':code,'candidate':r['candidate'],'verificationStatus':r['verificationStatus'],'readings':r['readings'],**({'visualReading':r['visualReading']}if 'visualReading'in r else{})}
   if len(table['columns'])==4:
    row += [bi(length or'',length or''),bi(diam or'',diam or'')]
    if not length or not diam:s['reviewFlags'].append({'code':'unreadable-dimension','path':f'specTables.{len(s["specTables"])}.rows.{idx}','pdfPage':r['pdfPage'],'readings':[rawdim],'message':bi('Проверьте длину или диаметр в исходной строке.','Verify the source row length or diameter.')})
   table['rows'].append(row);table['rowSources'].append({'pdfPage':r['pdfPage'],'bounds':r['sourceBounds'],'coordinateSpace':'normalized','codeEvidence':[ev]})
   a=photo(r,z)
   if a:
    image={**a,'imageCaption':desc}
    if not any(i['src']==a['src']for i in table['images']):table['images'].append(image)
    s['imageDimensions'][a['src']]={'width':a['width'],'height':a['height']}
    s['components'].append({'name':desc,'image':a['src'],'imageType':a['imageType'],'refCodes':[code]if code else[],'groupId':group,'pdfPage':r['pdfPage'],'sourceBounds':r['sourceBounds']})
   if code:s['refCodes'].append(code)
   if not code:s['reviewFlags'].append({'code':'unverified-code','pdfPage':r['pdfPage'],'path':f'specTables.{len(s["specTables"])}.rows.{idx}.1','readings':r['readings'],'message':bi('Каталожный номер требует проверки.','Catalog number requires review.')})
   assigned.append(r['id']);s['sourcePages'].append(r['pdfPage'])
  if table['rows']:
   s['componentGroups'].append({'id':group,'name':table['title'],'images':table['images']});s['specTables'].append(table)
 s['refCodes']=list(dict.fromkeys(s['refCodes']));s['sourcePages']=sorted(set(s['sourcePages']));images={a['src']:a for t in s['specTables']for a in t['images']};s['gallery']=list(images.values());s['heroImage']=s['gallery'][0]['src']if s['gallery']else''
 if s['gallery']:
  hero=max((a for a in s['gallery']if a['imageType']=='cutout'),key=lambda a:a['width']*a['height'],default=s['gallery'][0]);s['heroImage']=hero['src'];s['imageType']=hero['imageType']
 systems.append(s)
# Printed subgroup notes belong alongside their ordering tables.
NOTES={
'Spinal guiding cannulas':bi('Многоразовый набор спинальных канюль: канюля, острая внутренняя игла, тупой и острый обтураторы.','Reusable spinal cannula set: cannula, sharp inner needle, blunt and sharp obturators.'),
'Alligator grasper':bi('Короткие бранши с множественными зубцами. Защита от перегрузки и ирригация.','Short jaw with multiple serrations. Overload protection and irrigation.'),
'Cupped grasper':bi('Чашечные бранши с атравматичными зубцами. Защита от перегрузки и ирригация.','Cupped jaw with atraumatic serrations. Overload protection with irrigation.'),
'Spoon forceps':bi('Прямые бранши, защита от перегрузки и ирригация.','Straight, overload protection with irrigation.')}
for ss in systems:
 for tt in ss['specTables']:
  title=tt['title']['en']
  if title in NOTES:tt['description']=NOTES[title]
  elif title in ['Grasping forceps','Cup forceps','Scissors punch','Scissors punch, M','Hook scissors','Duckling basket punch','Semi-flexible grasper','Micro cup forceps']:tt['description']=bi('Защита от перегрузки и ирригация.','Overload protection with irrigation.')
# Owner resolved source duplicates; ordering codes on page 18 remain unknown.
systems[4]=apply_system(systems[4])
corrections.append(CORRECTION)
# A handle printed alongside Kerrison instruments belongs in accessories.
r=next(r for r in records if r['value']=='SP082700.041H');assigned.append(r['id']);s=systems[5];group='kerrison-handle';a=photo(r,(5,'Kerrison handle','Рукоятка Kerrison',17,.7,.55,.9,.6,None));desc=bi('Рукоятка эндоскопических кусачек Kerrison','Endoscopic Kerrison Handle');s['specTables'].append({'id':group,'groupId':group,'title':desc,'unit':None,'columns':[bi('Наименование','Description'),bi('Кат. №','Cat. No.')],'rows':[[desc,r['value']]],'rowSources':[{'pdfPage':17,'bounds':r['sourceBounds'],'codeEvidence':[{'id':r['id'],'pdfPage':17,'tableId':group,'row':1,'column':2,'value':r['value'],'verificationStatus':r['verificationStatus'],'readings':r['readings']}]}],'sourcePages':[17],'images':[{**a,'imageCaption':desc}]});s['sourcePages']=sorted(set(s['sourcePages']+[17]));s['refCodes'].append(r['value'])
s['imageDimensions'][a['src']]={'width':a['width'],'height':a['height']}
if not any(g['src']==a['src']for g in s['gallery']):s['gallery'].append({**a,'imageCaption':desc})
# Page 4: only benefit statements become cards. Technical data remains with its subgroup.
s=systems[0];s['features']=[{'title':bi('Защита оптики','Optical durability'),'text':bi('Сапфировые стёкла повышают устойчивость линзовой системы к повреждениям.','Sapphire glasses ensure highest stability against damage to the lens system.'),'image':None,'sourcePages':[4]},{'title':bi('Равномерная яркость','Uniform image brightness'),'text':bi('Оптимизированная укладка стекловолокна обеспечивает равномерную яркость изображения.','Optimised glass fibre arrangements ensure uniform image brightness.'),'image':None,'sourcePages':[4]},{'title':bi('Детализация Full HD','Full HD detail'),'text':bi('Стержневая линзовая система, разработанная с помощью CAD, повышает детализацию изображения Full HD.','CAD-designed rod-lens systems provide Full HD pictures with increased detail resolution.'),'image':None,'sourcePages':[4]}]
s['specTables'][0]['keyParameters']=[{'parameter':bi('Автоклавирование','Autoclaving'),'value':bi('134 °C; 2.3 бар','134 °C; 2.3 bar')},{'parameter':bi('Окуляр','Eyepiece'),'value':bi('Съёмный; C-mount или SPINENDOS QuickSnap','Removable; C-mount or SPINENDOS QuickSnap')},{'parameter':bi('Подключение световода','Light guide connection'),'value':bi('3-ступенчатые адаптеры','3-step light post adaptors')}]
# Ensure all source captions found by the readers are represented once.
unassigned=[r for r in records if r['id']not in assigned];dump(F/'unassigned.json',unassigned)
profile={'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'layoutReviewed':True,'method':'600-DPI Tesseract PSM3/11 and independent Apple Vision; Codex visual review of every disagreement; caption/photo regions mapped from the supplied PDF; Codex-authored Russian medical terminology; Real-ESRGAN exact 2x followed by rembg.','nonProductPages':[1,2,3,20],'systems':systems,'assets':list(assets.values())};dump(R/'scripts/profiles/spinendos-endoscopic-spine.json',profile);dump(F/'source-catalog-corrections.json',corrections);print('Systems',len(systems),'assigned',len(assigned),'unassigned',[(r['id'],r['candidate'])for r in unassigned]);print('Flags',[(s['slug'],len(s['reviewFlags']))for s in systems])
