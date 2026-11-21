#!/usr/bin/env python3
"""Codex source-reviewed transcription, not a translation service or OCR guess."""
import json,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def bi(ru,en):return {'ru':ru,'en':en}
def c(value,colspan=1,rowspan=1,tone=None):return {'value':value,**({'colspan':colspan}if colspan>1 else{}),**({'rowspan':rowspan}if rowspan>1 else{}),**({'tone':tone}if tone else{})}
def grid(n):return ['']*n
def table(id,title,page,n,rows,legend=None):return {'id':id,'title':title,'unit':'mm','columns':['']*n,'showColumnHeaders':False,'headersVerified':True,'rows':rows,'sourcePages':[page],'legend':legend,'rowSources':[{'pdfPage':page,'sourceBounds':([.10,.60,.89,.75]if page==5 else[.10,.49,.89,.95]),'sourceMethod':'Visually checked against 600-DPI PDF and two OCR passes'}for _ in rows]}
def stem_table(page):
 n=21;rows=[grid(n)for _ in range(7 if page==5 else 6)]
 rows[0][0]=c(bi('Плечевая ножка THS','Humeral Stem THS'),rowspan=4);rows[0][1]=bi('Тип','Type')
 for pos,span,ru,en in [(2,6,'Цементная плечевая ножка','Cemented humeral stem'),(8,4,'Удлинённая ревизионная цементная плечевая ножка','Extended revision cemented humeral stem'),(12,5,'Цементная платформенная плечевая ножка для переломов L/R','Cemented platform fracture humeral stem L/R'),(17,4,'Цементная плечевая ножка для переломов L/R','Cemented fractured humeral stem L/R')]:rows[0][pos]=c(bi(ru,en),colspan=span)
 rows[1][1]=bi('Длина ножки'if page==5 else'Длина ножки L1','Stem length'if page==5 else'L1 stem length')
 for i,v in enumerate(['107','112','117','122','127','132','175','200','200','215']):rows[1][i+2]=v
 for pos,span,val in [(12,1,'120'),(13,3,'140'),(16,1,'200'),(17,3,'140'),(20,1,'200')]:rows[1][pos]=c(val,colspan=span)
 rows[2][1]=bi('Диаметр','Diameter');rows[2][2:]=['6.7','8.8','11','13','15','17','8','10','12','8','6.5','8.5','10.5','12.5','6.5','7','9.5','12','7']
 rows[3][1]=bi('Офсет','Offset')
 if page==5:
  for pos,span,value in [(2,2,'7.5'),(4,1,'8.5'),(5,3,'9.5'),(8,4,'8'),(12,9,'/')]:rows[3][pos]=c(value,colspan=span)
  rows[4][0]=c(bi('Плечевая адаптерная платформа','Humeral Adapter Tray'),rowspan=2);rows[4][1]=bi('Тип','Type');rows[4][2]=c(bi('Адаптерная платформа реверсивной плечевой ножки THA I','Inverted humeral stem adapter tray THA I'),colspan=15);rows[4][17]=c(bi('Адаптерная платформа плечевой ножки для переломов THA II','Fractured humeral stem adapter tray THA II'),colspan=4)
  rows[5][1]=bi('Офсет','Offset');rows[5][2]=c('+0、+5、+10、15',colspan=15);rows[5][17]=c('0',colspan=4)
  rows[6][0]=bi('Блокирующий винт адаптерной платформы','Adapter tray locking screw');rows[6][1]=bi('Тип','Type');rows[6][2]=c(bi('Блокирующий винт адаптерной платформы реверсивной плечевой ножки THAS I','Inverted humeral stem adapter tray locking screw THAS I'),colspan=15);rows[6][17]=c(bi('Блокирующий винт адаптерной платформы плечевой ножки для переломов THAS II','Fractured humeral stem adapter tray locking screw THAS II'),colspan=4)
 else:
  for pos,span,value in [(2,2,'8'),(4,1,'9'),(5,3,'9.5'),(8,4,'8'),(12,9,'/')]:rows[3][pos]=c(value,colspan=span)
  rows[4][0]=bi('Анатомический адаптер','Anatomy Replicator');rows[4][1]=bi('Офсет','Offset');rows[4][2]=c('0、1.5、4.5',colspan=15);rows[4][17]=c('/',colspan=4,rowspan=2)
  rows[5][0]=bi('Винт анатомического адаптера TRPS I','Anatomical Replicator Screw TRPS I');rows[5][1]=bi('Тип','Type');rows[5][2]=c(bi('Блокирующий винт','Locking screw'),colspan=15)
 return table('reverse-shoulder-set'if page==5 else'anatomic-shoulder-set',bi('Комплект для реверсивного эндопротезирования'if page==5 else'Комплект для анатомического эндопротезирования / гемиартропластики','Reverse Shoulder Set'if page==5 else'Shoulder/half shoulder set'),page,n,rows)
reverse_set=stem_table(5);anatomic_set=stem_table(8)
# The lower source table uses 6 equal offset cells and 8 equal screw cells.
# A 24-column common grid preserves both source geometries without duplicated values.
rows=[grid(26)for _ in range(8)]
for row,ru,en in [(0,'Плечевой вкладыш PEHL I','Humeral Liner PEHL I'),(2,'Ограничивающий плечевой вкладыш PEHL II','Limited Humeral Liner PEHL II')]:
 rows[row][0]=c(bi(ru,en),rowspan=2);rows[row][1]=bi('Диаметр','Diameter');rows[row+1][1]=bi('Офсет','Offset')
 for pos,val in [(2,'38'),(10,'42'),(18,'46')]:rows[row][pos]=c(val,colspan=8)
 for j,val in enumerate(['+0','+2.5']*3):rows[row+1][2+j*4]=c(val,colspan=4)
rows[4][0]=bi('Гленосфера CGH I','Inverted Glenosphere CGH I');rows[4][1]=bi('Диаметр','Diameter')
for pos,val in [(2,'38'),(10,'42'),(18,'46')]:rows[4][pos]=c(val,colspan=8)
for row,ru,en,value in [(5,'Блокирующий винт гленосферы TGHS I','Inverted Glenosphere Locking Screw TGHS I',bi('Блокирующий винт гленосферы','Inverted glenosphere locking screw')),(6,'Базовая пластина гленосферы TGP I','Inverted Glenosphere Plate TGP I',bi('Центральная костная опора с фиксацией press-fit','Press-fit fixed bone cage'))]:rows[row][0]=bi(ru,en);rows[row][1]=bi('Тип','Type');rows[row][2]=c(value,colspan=24)
rows[7][0]=bi('Комплект компрессионных гленоидальных винтов TGPS I (φ4.5)','Glenoid Compression Screw Kit TGPS I (φ4.5)');rows[7][1]=bi('Длина','Length')
for j,v in enumerate(['18','22','26','30','34','38','42','46']):rows[7][2+j*3]=c(v,colspan=3)
fitting=table('reverse-liner-glenosphere',bi('Сочетаемость плечевого вкладыша и гленосферы','Fitting relationship between humeral liner and glenosphere'),5,26,rows)
zones=table('glenoid-radius-zones',bi('Тип суставной поверхности по диаметру головки','Joint-surface type by head diameter'),7,7,[[bi('Диаметр головки','Diameter of the head'),'38','41','44','47','50','53'],[bi('Тип плечевого протеза','Shoulder prosthesis type'),c('α',colspan=3,tone='alpha'),'','',c('β',colspan=3,tone='beta'),'','']])
dimensions=table('cemented-stem-dimensions',bi('Размеры цементной плечевой ножки','Cemented humeral stem dimensions'),8,7,[[bi('Диаметр на уровне A','Diameter at A'),'6.7','8.8','11','13','15','17'],[bi('Длина ножки L2','L2 stem length'),'100','105','110','115','120','125']])
rows=[grid(8)for _ in range(12)]
rows[0][0]=c(bi('Головка плечевой кости CHH I','Humeral Head CHH I'),rowspan=4);rows[0][1]=bi('Диаметр','Diameter');rows[0][2:]=['38','41','44','47','50','53'];rows[1][1]=c(bi('Высота','Height'),rowspan=3)
rows[1][2:]=[bi('Низкая-'+v,'Low-'+v)for v in ['16','16','17','18','19','20']];rows[2][2:]=[bi('Высокая-'+v,'High-'+v)for v in ['19','20','21','22','23','24']];rows[3][2:]=['/','/','/']+[bi('Сверхвысокая-'+v,'Ultrahigh-'+v)for v in ['26','27','28']]
rows[4][0]=c(bi('Цементный гленоидальный компонент PEGL I / Гленоидальный компонент с фиксирующими штифтами PEGL II','Bonded glenoid liner PEGL I / Glenoid liner with fixation bolt PEGL II'),rowspan=4)
sizes=[('Малый','Small','22*30'),('Средний','Medium','26*35'),('Большой','Large','30*39'),('Очень большой','Extra Large','32*44')]
for i,(ru,en,size)in enumerate(sizes):
 r=4+i;rows[r][1]=bi(ru+' (ширина*высота '+size+')',en+' (Width*Height '+size+')')
 rows[r][2]=c(bi('α '+ru,'α '+en)if i<3 else'/',colspan=3,tone='alpha'if i<3 else None)
 rows[r][5]=c(bi('β '+ru,'β '+en)if i<3 else bi('β Очень большой (только гленоидальный компонент с фиксирующими штифтами)','β Extra Large (with fixed-bolt glenoid liner only)'),colspan=3,tone='beta')
rows[8][0]=c(bi('Гленоидальный компонент с задним аугментом 8° (L/R) PEGL III','8° rear enlarged glenoid liner (L/R) PEGL III'),rowspan=4)
for i,(ru,en,size)in enumerate(sizes):
 rows[8+i][1]=bi(ru+' (ширина*высота '+('22*30.0'if i==0 else size)+')',en+' (Width*Height '+('22*30.0'if i==0 else size)+')')
 for j in ([0,1,2,3]if i==0 else[1,2,3,4]if i==1 else[2,3,4,5]):rows[8+i][2+j]=c('●',tone='compatible')
compat=table('head-glenoid-compatibility',bi('Сочетаемость головки плечевой кости и гленоидального компонента','Relationship between the humeral head and the glenoid liner'),8,8,rows,bi('α — коралловая зона; β — голубая зона. Зелёная ячейка с ● — совместимое сочетание. Знак / и пустые ячейки сохранены как в каталоге; совместимость не предполагается.','α: coral zone; β: blue zone. Green cells with ● indicate compatible combinations. Printed / and blank cells are preserved; compatibility is not inferred.'))
# Native, caption-free images produced separately from this source-reviewed recipe.
# Row locations are the actual ruled source intervals, normalized for review highlighting.
for t,edges,x0,x1 in [
 (reverse_set,[519.82,537.55,555.28,573.02,590.75,608.48,626.22,644.01],62.7,544.0),
 (fitting,[671.71,687.75,703.79,719.83,735.88,751.92,767.96,784.0,800.09],62.7,544.0),
 (zones,[776.46,797.86,819.8],86.0,421.0),
 (dimensions,[424.10,443.07,462.45],294.5,544.6),
 (anatomic_set,[509.28,526.28,543.27,560.27,577.26,594.26,611.25],65.0,544.6),
 (compat,[636.45,652.17,667.38,683.10,698.81,713.01,729.24,743.63,759.66,774.87,789.91,805.8,819.81],65.0,544.6)]:
 t['sourceBounds']=[x0/613.2755737304688,edges[0]/859.8897705078125,x1/613.2755737304688,edges[-1]/859.8897705078125]
 for i,row in enumerate(t['rowSources']):row['sourceBounds']=[x0/613.2755737304688,edges[i]/859.8897705078125,x1/613.2755737304688,edges[i+1]/859.8897705078125]
assetfile=R/'public/images/products/double-medical/angel-shoulder-system/prepared-assets.json'
assets=json.loads(assetfile.read_text())if assetfile.exists()else[]
A={x['name']:x for x in assets}
def img(name):return A.get(name,{'src':'/images/products/double-medical/angel-shoulder-system/'+name+'.webp','imageType':'cutout'})
def feature(id,ru,en,text_ru,text_en,page,image=None):return {'id':id,'title':bi(ru,en),'text':bi(text_ru,text_en),'image':img(image)['src']if image else None,'sourcePages':[page]}
rev=[
 feature('rotation-center','Центр ротации','Center of rotation','Центр ротации расположен на уровне поверхности гленоида.','Center of rotation built into the glenoid surface.',6),
 feature('glenosphere-design','Конструкция гленосферы','Glenosphere design','Гленоидальный компонент имеет нижнее нависание; используются гленосферы большого диаметра.','The glenoid-side component adopts a downward overhang design and a large-diameter glenoid ball head.',6,'component-glenosphere'),
 feature('baseplate','Анатомическая базовая пластина','Anatomic glenoid baseplate','Изогнутое анатомическое основание с центральной костной опорой и 6 отверстиями для винтов.','Curved anatomic base with a central bone cage and 6 screw holes.',6,'glenoid-baseplate-screws'),
 feature('glenoid-screws','Компрессионные винты','Compression screws','Гленоидальные компрессионные винты с блокирующими колпачками: диаметр 4.5 мм, длина 18–46 мм с шагом 4 мм; допускается отклонение ±30°.','Glenoid compression screws with locking caps: 4.5 mm diameter, 18–46 mm length in 4 mm increments, allowing ±30°.',6,'component-glenoid-compression-screw'),
 feature('reverse-offset','Регулируемый офсет','Adjustable offset','Офсет адаптерной платформы 0/5/10/15 мм; стандартный и ограничивающий вкладыши дают прибавку +0/+2.5 мм. Общий диапазон офсета: +0–17.5 мм.','Humeral adapter tray offset 0/5/10/15 mm; standard and limited liners add +0/+2.5 mm. Overall offset range: +0–17.5 mm.',6,'reverse-liner-assembly'),
 feature('limited-liner','Углублённый ограничивающий вкладыш','Deeper limited liner','Ограничивающий плечевой вкладыш на 4 мм глубже стандартного.','The limited humeral liner is 4 mm deeper than the standard liner.',6,'component-humeral-liner')]
anat=[
 feature('anatomy-replicator','Анатомический адаптер','Anatomy replicator','Независимая регулировка наклона головки на ±7.5°: шеечно-диафизарный угол 125°–140°, переднезадний наклон ±7.5°.','Independent humeral head deflection adjustment by ±7.5°, allowing a head–shaft angle of 125°–140° and an anteroposterior tilt of ±7.5°.',7,'feature-anatomic-angle'),
 feature('replicator-offset','Восстановление офсета','Offset restoration','Предусмотрены три типоразмера анатомического адаптера, в том числе со встроенным офсетом 1.5 мм и 4.5 мм.','Anatomical offset replicators are available in three specifications, with built-in offsets of 1.5 mm and 4.5 mm.',7,'feature-anatomic-offset'),
 feature('head-centering','Положение центра головки','Head center positioning','Центр головки можно совместить с осью плечевой ножки. Медиолатеральный офсет 0–14 мм; переднезадний офсет ±6 мм.','The humeral head center can be aligned with the stem axis. Mediolateral offset 0–14 mm; anteroposterior offset ±6 mm.',7),
 feature('head-height','Выбор высоты головки','Head height options','Для каждого диаметра головки предусмотрены варианты высоты 16–28 мм для регулировки натяжения мягких тканей.','Each humeral head diameter has height options of 16–28 mm to facilitate soft-tissue tension adjustment.',7,'component-humeral-head'),
 feature('in-situ','Регулировка in situ','In-body adjustment','Не требуется пробная сборка шаблона ножки или предварительная сборка протеза на отдельном столе; регулировка и сборка выполняются непосредственно in situ.','No humeral stem mold testing or back-table prosthesis assembly is required; adjustment and assembly are performed directly in the body.',7),
 feature('glenoid-options','Варианты гленоидального компонента','Glenoid options','Система включает килевой и штифтовой гленоидальные компоненты, а также гленоидальный компонент с задним аугментом 8°.','The system provides keel-type and fixed-type glenoid prostheses and an 8° posterior augmented glenoid liner.',7,'anatomic-glenoid-options'),
 feature('glenoid-sizing','Анатомическая форма гленоида','Anatomic glenoid design','Грушевидная анатомическая форма. Четыре размера: малый, средний, большой и очень большой; каждый тип разделяется на зоны α и β по радиусу суставной поверхности.','Anatomic pear-shaped design in four sizes: small, medium, large and extra large. Each type is divided into α and β according to the joint-surface radius.',7,'component-pegged-glenoid')]
fract=[
 feature('fracture-wing','Асимметричное переднелатеральное крыло','Asymmetric anterolateral wing','Крыло располагается на уровне линии перелома и не препятствует репозиции. Оно направляет репозицию, поддерживает фрагменты большого и малого бугорков, облегчает их фиксацию и задаёт направление введения и ретроверсию протеза.','The wing lies at the fracture line without interfering with reduction. It guides reduction, supports greater and lesser tuberosity fragments, facilitates fixation, guides insertion and determines prosthetic retroversion.',5,'feature-fracture-02'),
 feature('tuberosity-fixation','Фиксация бугорков','Tuberosity fixation','Асимметричное переднелатеральное крыло и окна для проведения нескольких швов обеспечивают двухточечную компрессию и фиксацию фрагментов бугорков, способствуя репозиции.','Asymmetric anterolateral wings combined with multi-suture windows provide two-point compression and tuberosity fragment fixation, benefiting reduction.',5,'feature-fracture-04'),
 feature('fracture-offset','Офсет ножки','Stem offset','Встроенный офсет 1.8 мм; наружный офсет 7.5 мм.','The stem has a built-in offset of 1.8 mm and an outer offset of 7.5 mm.',5,'fracture-stem-front'),
 feature('suture-holes','Шовные отверстия','Suture anchor holes','Асимметричные латеральные крылья и анкерные отверстия для нескольких швов.','Asymmetrical lateral wings and multi-stitch anchor holes.',5,'feature-fracture-02'),
 feature('proximal-surface','Проксимальная поверхность','Proximal surface','Шероховатая проксимальная поверхность.','Proximal rough surface.',5,'feature-fracture-03'),
 feature('small-proximal-end','Компактный проксимальный отдел','Small proximal end','Небольшой проксимальный отдел ножки не препятствует репозиции и облегчает костную пластику.','The small proximal end does not interfere with reduction and facilitates bone grafting.',5,'feature-fracture-01'),
 feature('distal-cement','Дистальный отдел для цементной фиксации','Distal end for cement fixation','Цилиндрический дистальный отдел с бороздкой для фиксации костным цементом.','Cylindrical distal end with a groove for bone cement fixation.',5,'fracture-stem-rear')]
cement=[
 feature('platform','Платформенная конструкция','Platform design','Сферическая соединительная поверхность позволяет перейти к анатомическому или реверсивному эндопротезированию без извлечения и замены ножки. Анатомические параметры регулируются in situ.','The spherical connection surface enables conversion to total or reverse shoulder arthroplasty without removing and replacing the stem. Anatomical parameters can be adjusted in the body.',8,'cemented-stem'),
 feature('fixation','Варианты фиксации','Fixation options','Платформенная конструкция допускает биологическую либо цементную фиксацию, обеспечивая стабильность фиксации и удобство ревизии.','Platform design permits biological or bone cement fixation, providing fixation stability and convenient revision.',8),
 feature('proximal-stability','Проксимальная стабильность','Proximal stability','Проксимальный отдел прямоугольного сечения обеспечивает ротационную стабильность. Пескоструйная шероховатая поверхность предназначена для биологической фиксации; натяг press-fit 0.5 мм.','The rectangular proximal section provides anti-rotation stability. A sandblasted rough surface supports biological fixation; press-fit is 0.5 mm.',8),
 feature('distal-design','Конструкция дистального отдела','Distal design','Цилиндрический дистальный отдел с бороздками уменьшает жёсткость ножки. Полированная дистальная поверхность подходит для цементной фиксации.','The cylindrical grooved distal section reduces stem stiffness. The polished distal surface is suitable for cement fixation.',8,'cemented-stem'),
 feature('cement-offset','Офсет протеза','Prosthetic offset','Офсет протеза 7.5 мм.','The prosthesis comes with a 7.5 mm offset.',8)]
component_names=[('glenoid-compression-screw','Компрессионный гленоидальный винт','Glenoid compression screw'),('locking-cap','Блокирующий колпачок','Locking cap'),('glenoid-baseplate','Базовая гленоидальная пластина','Glenoid baseplate'),('central-screw','Центральный винт','Central screw'),('glenosphere','Гленосфера','Glenosphere'),('humeral-liner','Плечевой вкладыш','Humeral liner'),('augmented-glenoid','Гленоидальный компонент с задним аугментом','Posterior augmented glenoid'),('humeral-adapter-tray','Плечевая адаптерная платформа','Humeral adapter tray'),('humeral-head','Головка плечевой кости','Humeral head'),('pegged-glenoid','Штифтовой гленоидальный компонент','Pegged glenoid'),('fracture-stem','Плечевая ножка для переломов','Fracture humeral stem'),('keeled-glenoid','Килевой гленоидальный компонент','Keeled glenoid')]
components=[{'id':id,'name':bi(ru,en),'image':img('component-'+id)['src'],'refCodes':[],'sourcePages':[3]}for id,ru,en in component_names]
components += [{'id':id,'name':bi(ru,en),'image':img(id)['src'],'refCodes':[],'sourcePages':[page]}for id,ru,en,page in [('modular-stem','Модульная плечевая ножка','Modular humeral stem',4),('cemented-stem','Цементная плечевая ножка','Cemented humeral stem',8),('component-anatomic-replicator','Анатомический адаптер','Anatomy replicator',4),('component-replicator-screw','Винт анатомического адаптера','Anatomical replicator screw',4)]]
gallery=[]
for i in range(1,7):
 a=copy.deepcopy(img('configuration-%02d'%i));a['imageCaption']=bi(('Анатомическая конфигурация 'if i<=3 else'Реверсивная конфигурация ')+str(i if i<=3 else i-3),('Anatomic configuration 'if i<=3 else'Reverse configuration ')+str(i if i<=3 else i-3));gallery.append(a)
variants=[]
for id,ru,en,features,tables,hero,ids,first in [
 ('reverse','Реверсивное эндопротезирование','Reverse arthroplasty',rev,[reverse_set,fitting],'exploded-modular',['glenoid-compression-screw','locking-cap','glenoid-baseplate','central-screw','glenosphere','humeral-liner','humeral-adapter-tray','modular-stem'],4),
 ('anatomic','Анатомическое (гемиартропластика)','Anatomic (hemiarthroplasty)',anat,[zones,anatomic_set,compat],'exploded-modular',['humeral-head','pegged-glenoid','keeled-glenoid','augmented-glenoid','modular-stem','component-anatomic-replicator','component-replicator-screw'],1),
 ('fracture','Ножка для переломов','Fracture stem',fract,[reverse_set,fitting],'exploded-fracture',['fracture-stem','humeral-adapter-tray','humeral-liner','glenosphere','humeral-head'],3),
 ('cemented','Цементная ножка','Cemented stem',cement,[dimensions,anatomic_set,compat],'exploded-modular',['cemented-stem','humeral-head','pegged-glenoid','keeled-glenoid','augmented-glenoid','component-anatomic-replicator','component-replicator-screw'],1)]:
 variants.append({'id':id,'name':bi(ru,en),'heroImage':img(hero)['src'],'imageType':'cutout','features':features,'specTables':copy.deepcopy(tables),'gallery':[gallery[first-1]]+[a for j,a in enumerate(gallery)if j!=first-1],'componentIds':ids,'sourcePages':sorted(set(p for t in tables for p in t['sourcePages'])|{p for f in features for p in f['sourcePages']})})
S={'schemaVersion':1,'slug':'angel-shoulder-system','brand':'double-medical','catalogType':'system','category':'joint-replacement','subcategory':'shoulder','specialty':['orthopedics','traumatology'],'name':bi('Система эндопротезирования плечевого сустава Angel','Angel Shoulder Replacement System'),'shortDescription':bi('Модульные решения для реверсивного, анатомического эндопротезирования и переломов проксимального отдела плечевой кости.','Modular solutions for reverse and anatomic arthroplasty and proximal humeral fractures.'),'description':bi('Система Angel включает компоненты для реверсивного и анатомического эндопротезирования плечевого сустава, в том числе гемиартропластики. В каталоге представлены плечевые ножки для переломов, цементные и удлинённые ревизионные ножки, головки, гленосферы, вкладыши и адаптерные платформы. Размеры и сочетаемость компонентов приведены в таблицах производителя.','The Angel system includes components for reverse and anatomic shoulder replacement, including hemiarthroplasty. The catalog presents fracture, cemented and extended revision humeral stems, humeral heads, glenospheres, liners and adapter trays. Manufacturer tables specify component dimensions and compatibility.'),'heroImage':img('exploded-modular')['src'],'imageType':'cutout','gallery':gallery,'variants':variants,'features':[],'hotspots':[],'components':components,'specTables':[],'refCodes':[],'sourcePages':[3,4,5,6,7,8,9],'catalogEdition':None,'catalogTitle':bi('Double Medical Angel Shoulder Replacement System — каталог продукции','Double Medical Angel Shoulder Replacement System — Product Catalog'),'isNew':True,'status':'draft','imageDimensions':{a['src']:{'width':a['width'],'height':a['height']}for a in assets}}
digest=hashlib.sha256((R/'catalogs-source/double-medical/angel-shoulder-system.pdf').read_bytes()).hexdigest()
profile={'sha256':digest,'method':'600-DPI dual-pass OCR with Codex visual transcription of six source tables, merged-cell geometry and compatibility colours; professional RU translation. Native embedded manufacturer-alpha images, rembg reviewed against original masks.','nonProductPages':[1,2,10],'system':S,'layoutReviewed':True,'assets':assets}
p=R/'scripts/profiles/angel-shoulder-system.json';p.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n');print('Profile written: 4 variants, 6 unique source tables')
