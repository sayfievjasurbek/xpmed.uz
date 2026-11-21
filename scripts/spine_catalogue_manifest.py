"""Codex-authored medical terminology and contents mapping for the implant import."""
import re

def bi(ru,en):return {'ru':str(ru),'en':str(en)}
FAMILIES=[
('anterior-cervical-plate-iii','Передняя шейная пластина III','Anterior Cervical Spine Locking Plate System III','cervical'),
('anterior-cervical-plate-iv','Передняя шейная пластина IV','Anterior Cervical Spine Locking Plate System IV','cervical'),
('delta-anterior-cervical-plate-cage','Передняя шейная пластина и кейдж DELTA','DELTA Anterior Cervical Plate and Cage System','cervical'),
('zero-profile-anterior-cervical-intervertebral-locking-plate-and-cage-combination-system','Шейные кейджи','Cervical Cage','cervical'),
('posterior-cervical-spine-system','Система задней фиксации шейного отдела позвоночника','Posterior Cervical Spine System','cervical'),
('hobbit-posterior-cervical-spine-system','Система задней шейной фиксации HOBBIT','HOBBIT Posterior Cervical Spine System','cervical'),
('laminoplasty-plate-system','Пластины для ламинопластики','Laminoplasty Plate System','cervical'),
('anterior-thoracolumbar-spine-system-i','Система передней грудопоясничной фиксации I','Anterior Thoracic-Lumbar Spine System I','thoracolumbar'),
('spinal-hooks','Крючки для фиксации позвоночника','Spinal Hooks','thoracolumbar'),
('tina-spine-5-5-6-0-system','Спинальная система TINA','TINA Spine System','thoracolumbar'),
('hobbit-spine-system','Спинальная система HOBBIT','HOBBIT Spine System','thoracolumbar'),
('sacroiliac-fixation-system','Система крестцово-подвздошной фиксации','Sacroiliac System','sacroiliac'),
('spinal-transconnectors','Поперечные коннекторы для позвоночника','Transconnectors','thoracolumbar'),
('spinal-rods','Стержни для фиксации позвоночника','Spinal Rods','thoracolumbar'),
('mis-spinal-rods','Стержни для малоинвазивной фиксации позвоночника','MIS Rods','spine-mis'),
('thoracolumbar-cages','Грудопоясничные межтеловые кейджи','Thoracic-Lumbar Cages','thoracolumbar'),
('olif-system','Система косого латерального межтелового спондилодеза OLIF','Oblique Lateral Interbody Fusion Cage (OLIF)','spine-mis'),
('spinal-titanium-mesh','Титановые сетки для позвоночника','Spinal Titanium Mesh','spinal-mesh')]
MERGES={FAMILIES[3][0],FAMILIES[9][0]}

def family(t):
 n=t['pdfPage'];title=t['title']
 if n<=7:return FAMILIES[0]
 if n<=11:return FAMILIES[1]
 if n<=13:return FAMILIES[2]
 if n<=18:return FAMILIES[3]
 if n==19:return FAMILIES[4]
 if n<=39:return FAMILIES[5]
 if n<=46:return FAMILIES[6]
 if n<=50:return FAMILIES[7] # Source calls the hook pages anterior-system connectors/nuts.
 if n==51:return FAMILIES[8]
 if n<=94:return FAMILIES[9]
 if n<=144:
  if 'Sacroiliac'in title:return FAMILIES[11]
  return FAMILIES[10]
 if n<=147:return FAMILIES[12]
 if n<=151:return FAMILIES[13]
 if n<=156:return FAMILIES[14]
 if n<=185:return FAMILIES[10] # HOBBIT 4.75 components printed under the MIS Rod running header.
 if n<=191:return FAMILIES[15]
 if n<=201:return FAMILIES[16]
 return FAMILIES[17]

def clean_title(text,n):
 if 57<=n<=61:text='TINA Long Arm Polyaxial Pedicle Screw (5.5 System)'
 if n==76:text='TINA Long Arm Polyaxial Pedicle Screw, Cannulated (5.5 System)'
 if n==79:text='TINA Long Arm Cannulated Monoaxial Pedicle Screw (5.5 System)'
 if n==80:text='TINA Long Arm Cannulated Polyaxial Pedicle Screw (5.5 System)'
 if 96<=n<=100:text='HOBBIT Monoaxial Pedicle Screw (5.5/6.0 System)'
 if 101<=n<=105:text='HOBBIT Long Arm Monoaxial Pedicle Screw (5.5/6.0 System)'
 if n==201 and 'fixed ang'in text:text='Locking Screw for OLIF Plate with 4 Holes, self-drilling, fixed angle'
 text=text.replace('ca0d ','').replace('Gervical','Cervical').replace('Pedicie Serew','Pedicle Screw').replace('self-driling','self-drilling').replace('variale','variable').replace('Paralledlled','Parallel').replace('Parellelled','Parallel').replace('Parallelled','Parallel').replace('Paralleled','Parallel').replace('fully-threaded','fully threaded').replace('5.5/6.0System','5.5/6.0 System').replace('5.5/60System','5.5/6.0 System')
 text=re.sub(r'\bystem\b','System',text).replace('Screw, $','Screw, Ø').replace('$9.4','Ø9.4').replace('$8.0','Ø8.0').replace('$6.5','Ø6.5').replace('Ф','Ø')
 if text.endswith(' Length (mm)'):text=text[:-12]
 return text.rstrip(', ')
# Phrase lexicon is authored for this run; no translation adapter is called.
PHRASES={
'Anterior Cervical Spine Plate':'Передняя шейная пластина','Delta Cervical Plate':'Шейная пластина DELTA','Delta Cervical Cage':'Шейный кейдж DELTA',
'Anterior Cervical Intervertebral Locking Cage':'Передний шейный межтеловой блокируемый кейдж','Cervical Cage':'Шейный кейдж',
'Locking Screw for Cervical Plate':'Блокируемый винт для шейной пластины','Emergency Screw for Cervical Plate':'Ревизионный винт для шейной пластины',
'Screw for Delta Cervical Plate':'Винт для шейной пластины DELTA','Emergency Screw for Delta Cervical Plate':'Ревизионный винт для шейной пластины DELTA',
'Posterior Cervical':'для задней шейной фиксации','Long Arm':'с удлинёнными лепестками','Polyaxial Pedicle Screw':'Полиаксиальный транспедикулярный винт','Monoaxial Pedicle Screw':'Моноаксиальный транспедикулярный винт','Uni-Planar Pedicle Screw':'Унипланарный транспедикулярный винт','Sacroiliac Cannulated Screw':'Канюлированный крестцово-подвздошный винт','Double-headed Pedicle Screw':'Двухголовочный транспедикулярный винт','Midline Cortex Screw':'Кортикальный винт для срединной фиксации',
'Snap-off Screw Nut':'Гайка со срывной головкой','Screw Nut':'Гайка','One-step Locking Nut':'Одноступенчатая фиксирующая гайка','Two-step Locking Nut':'Двухступенчатая фиксирующая гайка',
'Cervical Rod':'Шейный стержень','Stepped Rod':'Ступенчатый стержень','Occipital Plate':'Затылочная пластина','Anatomical':'анатомическая','Occipital Screw':'Затылочный винт','Transconnector':'Поперечный коннектор','Straight Connector':'Прямой коннектор','Parallel Connector':'Параллельный коннектор','Lateral Connector':'Латеральный коннектор','Polyaxial Parallel Connector':'Полиаксиальный параллельный коннектор','Cable Fixator':'Фиксатор серкляжного троса','Lamina Hook':'Ламинарный крючок','Pedicle Hook':'Педикулярный крючок','Laminoplasty Mini Plate':'Мини-пластина для ламинопластики','Laminoplasty Plate':'Пластина для ламинопластики',
'Cortex Screw for Laminoplasty Plate':'Кортикальный винт для пластины для ламинопластики','Cortex Bone Screw':'Кортикальный костный винт','Vertebral Screw':'Винт для тела позвонка','Rod for Anterior Thoracic-Lumbar Spine System':'Стержень для системы передней грудопоясничной фиксации','for Anterior Thoracic-lumbar Spine System':'для системы передней грудопоясничной фиксации','Washer':'Шайба','Locking Screw':'Блокируемый винт','Non-Locking Screw':'Неблокируемый винт','OLIF Plate':'Пластина OLIF','for OLIF Plate':'для пластины OLIF','Thoracic-Lumbar Cage':'Грудопоясничный кейдж','Endo LIF Cage':'Кейдж Endo LIF','TLIF Cage':'Кейдж TLIF','OLIF Cage':'Кейдж OLIF','Titanium Mesh for Cervical Spine':'Титановая сетка для шейного отдела позвоночника','Titanium Mesh for Thoracic-Lumbar Spine':'Титановая сетка для грудопоясничного отдела позвоночника','End Cap for Cervical Mesh':'Торцевая заглушка для шейной сетки','End Cap for Thoracic-Lumbar Mesh':'Торцевая заглушка для грудопоясничной сетки',
'Growth Connector':'Коннектор для растущих конструкций','Single U Connector':'Одинарный U-образный коннектор','Double U Connector':'Двойной U-образный коннектор','MIS Rod':'Стержень MIS','Z-shaped Rod':'Z-образный стержень','Rod':'Стержень',
'self-drilling':'самосверлящий','self-tapping':'самонарезающий','variable angle':'с переменным углом','fixed angle':'с фиксированным углом','fully threaded':'с полной резьбой','half threaded':'с частичной резьбой','fully-threaded':'с полной резьбой','cannulated':'канюлированный','Cannulated':'канюлированный','single line':'однорядная','double line':'двухрядная','wedge-shaped':'клиновидный','curved':'изогнутый','parallel':'параллельный','straight':'прямой','triangular':'треугольная','hinged':'шарнирный','angled':'угловой','single bend':'с одним изгибом','double bend':'с двумя изгибами','narrow-mouth':'с узким устьем','wide-mouth':'с широким устьем','narrow mouth':'с узким устьем','wide mouth':'с широким устьем','single Hole':'одно отверстие','double hole':'два отверстия','torxdrive':'со шлицем Torx','extended tab':'удлинённые лепестки','closed':'закрытый','open':'открытый','pressed':'запрессовываемая','I-shaped':'I-образная','T-shaped':'T-образная','Closed':'Закрытый','Plate':'пластина','holes':'отверстия','for':'для','with':'с','Holes':'отверстиями','System':'система','Length':'длина','Polyaxial':'полиаксиальный'
}
def translate_title(en):
 ru=en
 for a,b in sorted(PHRASES.items(),key=lambda x:len(x[0]),reverse=True):ru=ru.replace(a,b)
 ru=ru.replace('mm',' мм').replace(' |',' I')
 unknown=re.findall(r'[A-Za-z][A-Za-z-]{2,}',ru)
 unknown=[x for x in unknown if x not in ['TINA','HOBBIT','DELTA','PEEK','OLIF','TLIF','Endo','LIF','MIS','Torx','III','Co-Cr-Mo','Co-Cr']]
 return bi(ru,en),unknown
PREAMBLE={'Material':'Материал','Pure Titanium':'Чистый титан','Titanium Alloy':'Титановый сплав','Titanium alloy':'Титановый сплав','Titanium':'Титан','Diameter':'Диаметр','Thickness':'Толщина','Width':'Ширина','Height':'Высота','Length':'Длина','Hexagonal Socket':'Внутренний шестигранник','Torxdrive':'Шлиц Torx'}
def translate_spec(en):
 ru=en
 for a,b in sorted(PREAMBLE.items(),key=lambda x:len(x[0]),reverse=True):ru=ru.replace(a,b)
 return bi(ru.replace('mm',' мм'),en)
HEADERS={'REF':'REF','REF (PEEK)':'REF (PEEK)','REF (Titanium)':'REF (Титан)','REF (Titanium Alloy)':'REF (Титановый сплав)','Holes':'Количество отверстий','Length (mm)':'Длина (мм)','Diameter (mm)':'Диаметр (мм)','Height (mm)':'Высота (мм)','Width (mm)':'Ширина (мм)','Thickness (mm)':'Толщина (мм)','Angles (°)':'Угол (°)','Direction':'Сторона','Spec.':'Размеры'}
