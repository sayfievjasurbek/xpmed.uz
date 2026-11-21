"""Codex medical RU terminology for the authorized final five source sections."""
import re
import trauma_part2_translation as previous
FIXES={'Post Post':'Post','Circular Connecting Rod Circular Connecting Rod':'Circular Connecting Rod','Bone Screw ClampI':'Bone Screw Clamp I','Bone Screws 2.5mm Cortex Bone Screw I':'2.5mm Cortex Bone Screw I','3,5m Petiatic Ttbia Siding Straight Locking Pate O.0000':'3.5mm Pediatric Tibia Sliding Straight Locking Plate','41.OClasp':'Ø1.0 Clasp','Ф1.0Clasp':'Ø1.0 Clasp','$1.0 Cable':'Ø1.0 Cable','Post, 0°, $11.0':'Post, 0°, Ø11.0','Post, 30°, Ф11.0':'Post, 30°, Ø11.0','Post to Pin Coupling, 5 Holes, Ф11.0-Ф6.0':'Post to Pin Coupling, 5 Holes, Ø11.0–Ø6.0','Rod to Pin Coupling, Ф11.0/Ф8.0-Ф6.0/Ф5.0':'Rod to Pin Coupling, Ø11.0/Ø8.0–Ø6.0/Ø5.0'}
NAMES={
'Mini External Fixator':'Мини-аппарат внешней фиксации',
'External Fixator for Hand':'Аппарат внешней фиксации для кисти',
'External Fixator for Wrist and Forearm':'Аппарат внешней фиксации для лучезапястного сустава и предплечья',
'External Fixator for Elbow':'Аппарат внешней фиксации для локтевого сустава',
'External Fixator for Calcaneus':'Аппарат внешней фиксации для пяточной кости',
'External Fixator for Pelvis':'Аппарат внешней фиксации для таза',
'Threaded Shaft':'Резьбовой стержень','Threaded Shaft with Ball Joint':'Резьбовой стержень с шаровым шарниром',
'Pin Clamp':'Зажим для стержня','L-Pin Clamp':'L-образный зажим для стержня','Ulnar Clamp':'Локтевой зажим',
'Regulator':'Регулировочный узел','Drill Sleeve for Calcaneus External Fixator':'Сверлильная втулка для аппарата внешней фиксации пяточной кости',
'Post':'Опорная стойка','Post to Pin Coupling':'Соединитель стойки и стержня','Rod to Pin Coupling':'Соединитель штанги и стержня',
'Rod Clamp':'Зажим для штанги','Connecting Rod for Elbow Joint':'Соединительная штанга для локтевого сустава',
'Circular Connecting Rod':'Дугообразная соединительная штанга','Curved Rod':'Изогнутая штанга','Pin Coupling':'Соединитель стержней',
'Carbon Fiber Rod':'Углепластиковая штанга','3.0mm Titanium Alloy Rod':'Штанга из титанового сплава 3.0 мм',
'Rail':'Рейка','Bone Screw Clamp':'Зажим для костных винтов','Bone Screw Spacer':'Проставка для костных винтов',
'Dynamic-Clamp':'Динамический зажим','T-Clamp':'T-образный зажим','Multiplanar-Clamp':'Многоплоскостной зажим',
'Threaded Regulator':'Резьбовой регулировочный узел','Horizontal Transport':'Узел поперечного перемещения',
'Full Ring':'Полное кольцо','Semi-Ring':'Полукольцо','C-Ring':'C-образное кольцо','U-Ring':'U-образное кольцо','U-Ring, long':'Удлинённое U-образное кольцо','G-Ring':'G-образное кольцо',
'Angulation of Joint Device':'Шарнирное угловое устройство','Threaded Rod':'Резьбовая штанга','S-Threaded Rod':'S-образная резьбовая штанга',
'Connector Plate':'Соединительная пластина','Angle Plate, of Round External Fixator':'Угловая пластина для кольцевого аппарата внешней фиксации',
'Twisted Plate':'Изогнутая соединительная пластина','Retangular Column Connector with Internal Thread':'Прямоугольный соединитель с внутренней резьбой',
'Universal Hinge':'Универсальный шарнир','Tube Hinge':'Трубчатый шарнир','Tube-Screw Hinge':'Трубчато-винтовой шарнир',
'Tube-Screw Hinge and Shaft, of Round External Fixator':'Трубчато-винтовой шарнир со стержнем для кольцевого аппарата внешней фиксации',
'Wire Clamp, of Round External Fixator':'Спицефиксатор для кольцевого аппарата внешней фиксации','Hexagonal Nut':'Шестигранная гайка','Hexagonal Screw':'Винт с шестигранной головкой',
'Protection Sleeve':'Защитная втулка','Spring':'Пружина','Oblique Buttress Device':'Косая опорная стойка','Screw Clamp':'Винтовой зажим','Wire Clamp':'Спицефиксатор',
'Extender':'Удлинитель','Extension Plate':'Удлинительная пластина','Washer':'Шайба','Variable Angle Washer, of Round External Fixator':'Шайба с переменным углом для кольцевого аппарата внешней фиксации',
'Compression Nut':'Компрессионная гайка','Complex Hinge':'Комбинированный шарнир','Hinge with External Thread':'Шарнир с наружной резьбой',
'Connecting Bolt':'Соединительный болт','Hinge with Internal Thread':'Шарнир с внутренней резьбой','Retangular Column Connector with Internal Thread, of Round External Fixator':'Прямоугольный соединитель с внутренней резьбой для кольцевого аппарата внешней фиксации',
'Square Nut':'Квадратная гайка','Silicone Cap':'Силиконовый колпачок','Buttress Shaft':'Опорный стержень','Support Shaft':'Поддерживающий стержень',
'Support Shaft, of 3-D External Fixator':'Поддерживающий стержень для 3D-аппарата внешней фиксации','Buttress Shaft, of 3-D External Fixator':'Опорный стержень для 3D-аппарата внешней фиксации',
'Numbered Ring':'Маркировочное кольцо с номером','Direction Indication Ring':'Кольцо-указатель направления',
'Patella Pin':'Спица для фиксации надколенника','Cable':'Серкляжный трос','Clasp':'Обжимной фиксатор','Ø1.0 Clasp':'Обжимной фиксатор Ø1.0','Ø1.0 Cable':'Серкляжный трос Ø1.0',
'Patella Locking Plate':'Блокируемая пластина для надколенника',
}
previous.LEXICAL_MODIFIERS.update({'Aluminium Alloy':'алюминиевый сплав','Small Fragment':'для малых фрагментов','Small Fragment ImplantSet':'набор имплантов для малых фрагментов','System':'система','Fixation Pin':'фиксирующий штифт','Small':'малый','Large':'большой','Universal Plate':'универсальные пластины','Radius':'лучевая кость','Variable Angle':'переменный угол','pins':'штифтов','Pin':'штифт','Lid':'крышка','ImplantSet':'набор имплантов'})
previous.EXTRA_NOUNS.update({'Pinching Forceps':'Щипцы для натяжения','Universal Drill Sleeve':'Универсальная сверлильная втулка','Bone Screw':'Костный винт','Half Ring':'Полукольцо','Aiming Block':'Прицельный блок','Aiming Block Positioner':'Позиционер прицельного блока','Positioner for Aiming Block':'Позиционер прицельного блока','Medium Distractor':'Средний дистрактор','Holding Sleeve':'Удерживающая втулка','Sharp Hook':'Остроконечный крючок','Extraction Forceps':'Экстракционные щипцы','Broken Screw Extractor':'Экстрактор сломанного винта','Hollow Reamer':'Полый ример','Flexible Reamer':'Гибкий ример','Hard Reamer':'Жёсткий ример','Implant Tray':'Лоток для имплантов','Bench-type Rod Cutter/Bender':'Настольное устройство для резки и гибки стержней','Torque Indicating Handle':'Динамометрическая рукоятка','Torque Limiting Handle':'Рукоятка с ограничением крутящего момента','Holding Forceps with Long Screws':'Удерживающие щипцы с длинными винтами','Bending Clamp with Adjusting Bar':'Гибочный зажим с регулировочной штангой','Bone Lever':'Костный элеватор','Implant Holder for Nail':'Держатель интрамедуллярного штифта'})
def implant(en):
 en=FIXES.get(en,en)
 if en in NAMES:return {'ru':NAMES[en],'en':en}
 for key in sorted(NAMES,key=len,reverse=True):
  if en.startswith(key+' '):return {'ru':NAMES[key]+en[len(key):],'en':en}
  if en.startswith(key+','):
   suffix=en[len(key):].replace('Holes','отверстий').replace('long','длинный')
   return {'ru':NAMES[key]+suffix,'en':en}
 m=re.fullmatch(r'([\d.]+)mm (Cortex Bone Screw(?: II?)?|Cancellous Bone Screw|Taper Bone Screw|Reduction Bone Screw, Thread|Calcaneus Bone Screw)',en)
 if m:
  stem={'Cortex Bone Screw':'Кортикальный стержень-винт','Cortex Bone Screw I':'Кортикальный стержень-винт I','Cortex Bone Screw II':'Кортикальный стержень-винт II','Cancellous Bone Screw':'Спонгиозный стержень-винт','Taper Bone Screw':'Конический стержень-винт','Reduction Bone Screw, Thread':'Репозиционный стержень-винт с резьбой','Calcaneus Bone Screw':'Стержень-винт для пяточной кости'}[m[2]]
  return {'ru':stem+' '+m[1]+' мм','en':en}
 if en=='4mm Threaded Bone Pin':return {'ru':'Резьбовая костная спица 4 мм','en':en}
 if en.startswith('2.0mm Kirschner Wire'):return {'ru':'Спица Киршнера 2.0 мм'+(' с оливой'if 'olive'in en else''),'en':en}
 m=re.fullmatch(r'Pediatric Hip Locking Plate ([\d.]+)(?:, head ([23]) holes)?',en)
 if m:return {'ru':'Детская блокируемая пластина для проксимального отдела бедренной кости '+m[1]+(' — '+m[2]+' отверстия в головной части'if m[2]else''),'en':en}
 m=re.fullmatch(r'([\d.]+)mm Epiphyseal (Hinge Plate|Plate, arc-bridge shape|Plate, terrace shape|Plate, butterfly shape)',en)
 if m:return {'ru':{'Hinge Plate':'Шарнирная эпифизарная пластина','Plate, arc-bridge shape':'Дугообразная эпифизарная пластина','Plate, terrace shape':'Ступенчатая эпифизарная пластина','Plate, butterfly shape':'Эпифизарная пластина в форме бабочки'}[m[2]]+' '+m[1]+' мм','en':en}
 m=re.fullmatch(r'([\d.]+)mm Pediatric (Femoral|Tibia) Sliding (Barrel|Straight) Locking Plate',en)
 if m:return {'ru':'Детская скользящая '+('углостабильная пластина с втулкой'if m[3]=='Barrel'else'прямая блокируемая пластина')+' для '+('бедренной'if m[2]=='Femoral'else'большеберцовой')+' кости '+m[1]+' мм','en':en}
 m=re.fullmatch(r'([\d.]+)mm Cannulated Screw for ([\d.]+)mm Epiphyseal Plate, self-tapping',en)
 if m:return {'ru':'Самонарезающий канюлированный винт '+m[1]+' мм для эпифизарной пластины '+m[2]+' мм','en':en}
 return previous.implant(en)
def instrument(en,context=''):
 return previous.instrument(en,context)
# Additional terminology from the illustrated captions, reviewed in this import run.
CAPTION_TERMS={
'Caliper':'Измерительный циркуль','Clamping Forceps':'Зажимные щипцы','Tightening Forceps':'Натяжные щипцы','Gouge':'Желобоватое долото',
'Cancellous Bone Tamp':'Импактор для губчатой кости','Double Joint, complete':'Двойной шарнир в сборе','Knurled Nut':'Гайка с накаткой',
'Implant Holder for Mesh':'Держатель сетчатого импланта','Mesh Cutter':'Кусачки для сетчатого импланта','Tamp for Mesh':'Импактор для сетчатого импланта',
'Positioner for Osteotomy':'Позиционер для остеотомии','Positioning Plate, triangular':'Треугольная позиционирующая пластина',
'Sliding Carriage with Adjusting Nut':'Подвижная каретка с регулировочной гайкой','Instrument for Medialization':'Инструмент для медиализации',
'Spare Centering Tube for Hollow Reamer':'Запасная центрирующая втулка для полого римера','Spare Centering Pin for Hollow Reamer':'Запасный центрирующий штифт для полого римера',
'Handle for Torque Limiter':'Рукоятка для ограничителя крутящего момента','Pin Clamp Guide Block':'Направляющий блок зажима для стержня',
'3.0mm Aiming Block, arc-bridge shape':'Прицельный блок для дугообразной пластины 3.0 мм',
'4.5mm Aiming Block, arc-bridge shape':'Прицельный блок для дугообразной пластины 4.5 мм',
'4.5mm Aiming Block, butterfly shape':'Прицельный блок для пластины в форме бабочки 4.5 мм',
'4.5mm Aiming Block, terrace shape':'Прицельный блок для ступенчатой пластины 4.5 мм',
'Aiming Device, Arc-bridge Shape':'Прицельное устройство для дугообразной пластины','Aiming Device, Terrace Shape':'Прицельное устройство для ступенчатой пластины',
'Aiming Block for Proximal Lateral Tibial':'Прицельный блок для латеральной пластины проксимального отдела большеберцовой кости',
'Drill Sleeve for Screw Holes of Hinge Plate':'Сверлильная втулка для винтовых отверстий шарнирной пластины',
'Drill Sleeve for Screw Holes':'Сверлильная втулка для винтовых отверстий','Holding Sleeve with Wing Screw':'Удерживающая втулка с винтом-барашком',
}
CASE_NAMES={
'Instrument Case':'Контейнер для инструментов','Aluminum Case':'Алюминиевый контейнер','Aluminium Case':'Алюминиевый контейнер',
'Small Screw Case':'Контейнер для малых винтов','Large Screw Case':'Контейнер для больших винтов','Universal Plate Case':'Контейнер для универсальных пластин',
'Locking Radius System 2.4':'Контейнер для блокируемой системы лучевой кости 2.4','Locking Radius Variable Angle System 2.4':'Контейнер для блокируемой системы лучевой кости 2.4 с переменным углом',
'Locking Clavicle System 2.4':'Контейнер для блокируемой системы ключицы 2.4',
'Femoral Nail Case':'Контейнер для бедренных штифтов','Humeral Nail Case':'Контейнер для плечевых штифтов','Tibial Nail Case':'Контейнер для большеберцовых штифтов','PFNA Nail Case':'Контейнер для штифтов PFNA','Proximal Femoral Nail Case':'Контейнер для проксимальных бедренных штифтов',
'Flexible Reamer Case':'Контейнер для гибких римеров','3.0/4.5 Epiphyseal Plate Instrument Case':'Контейнер для инструментов эпифизарных пластин 3.0/4.5',
'Patella Pin Instrument Case':'Контейнер для инструментов фиксации надколенника','Pediatric Hip Locking Plate Instrument Case':'Контейнер для инструментов детских блокируемых пластин тазобедренного сустава',
'Large External Fixation Modular Rod System Instrument Case':'Контейнер для инструментов большой модульной стержневой системы внешней фиксации',
'Small External Fixation Modular Rod System Instrument Case':'Контейнер для инструментов малой модульной стержневой системы внешней фиксации',
'Instrument Case for Removal of Damaged Screws, small':'Малый контейнер для инструментов удаления повреждённых винтов',
'Epiphyseal Plate Case':'Контейнер для эпифизарных пластин','Pediatric Hip Locking Plate Case':'Контейнер для детских блокируемых пластин тазобедренного сустава',
}
base_instrument=instrument
def instrument(en,context=''):
 original=en;en=en.replace('Dill Bit','Drill Bit').replace('ImplantSet','Implant Set');ru=None
 for key in sorted(CAPTION_TERMS,key=len,reverse=True):
  if en.casefold().startswith(key.casefold()):
   suffix=en[len(key):];suffix=previous.replace_terms(suffix,{**previous.DETAILS,'large':'большой','small':'малый','left':'левый','right':'правый','length':'длина'})
   ru=CAPTION_TERMS[key]+suffix;break
 if ru is None:
  for key in sorted(CASE_NAMES,key=len,reverse=True):
   if en.casefold().startswith(key.casefold()):ru=CASE_NAMES[key]+en[len(key):];break
 if ru is None and re.match(r'^[\d./]+mm .*?(?:Implant Set|Implant Case|Screw Caddy)',en,re.I):
  m=re.match(r'^([\d./]+)mm\s+(.*)',en);rest=m[2];kind='Крышка контейнера для имплантов'if re.search(r'Case Lid',rest,re.I)else'Органайзер для винтов'if'Screw Caddy'in rest else'Контейнер для имплантов'if'Implant Case'in rest else'Набор для имплантов'
  ru=kind+(' для малых фрагментов'if'Small Fragment'in rest else' системы')+' '+m[1]+' мм'+(' (алюминиевый сплав)'if re.search(r'Alumin[iu]+m Alloy',rest,re.I)else'')+(', 60 фиксирующих штифтов'if re.search(r'60\s*pins',rest,re.I)else'')
 if ru is None:ru=base_instrument(en,context)['ru']
 cleanup={'arc-bridge shape':'дугообразная форма','terrace shape':'ступенчатая форма','butterfly shape':'форма бабочки','thread tip':'резьбовой наконечник','with Wing Screw':'с винтом-барашком','Wing Screw':'винт-барашек','Screw Holes':'винтовые отверстия','Holes':'отверстия','Aluminum':'алюминий','Epiphyseal':'эпифизарная','Pediatric Hip':'детские пластины тазобедренного сустава','Fragment':'фрагменты','Alloy':'сплав','Implant':'имплант','Femoral':'бедренный','Tibial':'большеберцовый','Humeral':'плечевой','Reamer':'ример','External':'наружный','Modular Rod':'модульная штанга','of Damaged':'повреждённых','Spare Centering Tube':'запасная центрирующая втулка','Spare Centering Pin':'запасный центрирующий штифт'}
 ru=previous.replace_terms(ru,cleanup);ru=re.sub(r'(?<=\d)\s*mm\b',' мм',ru).replace('N.m','Н·м');ru=re.sub(r'\s+',' ',ru).strip()
 return {'ru':ru,'en':en}
CAPTION_TERMS.update({'Pin Clamp Guiding Block':'Направляющий блок зажима для стержня','Cancellous Bone Impactor':'Импактор для губчатой кости','Impactor for Mesh':'Импактор для сетчатого импланта'})
base_implant=implant
def implant(en):
 if re.search(r'\bHoles?\b',en)and not re.search('[A-Za-z]{2}',re.sub(r'Holes?','',en)):
  return {'ru':re.sub(r'\bHoles?\b','отв.',en),'en':en}
 if en=='Cobalt-base alloy':return {'ru':'Сплав на основе кобальта','en':en}
 m=re.fullmatch(r'([\d.]+)mm Cannulated Screw for ([\d.]+)?mm Epiphyseal Plate',en)
 if m:return {'ru':'Канюлированный винт '+m[1]+' мм для эпифизарной пластины'+(' '+m[2]+' мм'if m[2]else''),'en':en}
 return base_implant(en)
