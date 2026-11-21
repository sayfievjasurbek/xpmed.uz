"""Codex-authored professional Russian terminology for Trauma Part 1 (no adapter)."""
import re
from functools import lru_cache

TERMS = {
 'Small Limited Contact Locking Plate':'Малая блокируемая пластина ограниченного контакта',
 'Broad Limited Contact Locking Plate':'Широкая блокируемая пластина ограниченного контакта',
 'Narrow Limited Contact Locking Plate':'Узкая блокируемая пластина ограниченного контакта',
 'Humeral Shaft Straight Locking Plate':'Прямая блокируемая пластина для диафиза плечевой кости',
 'Curved Locking Compression Plate':'Изогнутая блокируемая компрессионная пластина',
 'Metaphyseal Locking Plate':'Метафизарная блокируемая пластина',
 '1/3 Tubular Locking Plate':'Блокируемая пластина 1/3 трубчатая',
 'Acromion Locking Plate':'Блокируемая пластина для акромиона',
 'Scapula Medial Locking Plate':'Медиальная блокируемая пластина для лопатки',
 'Scapula Lateral Locking Plate':'Латеральная блокируемая пластина для лопатки',
 'Glenoid Locking Plate':'Блокируемая пластина для суставной впадины лопатки',
 'Superior Anterior Distal Clavicle Locking Plate':'Верхнепередняя блокируемая пластина для дистального отдела ключицы',
 'Superior Anterior Clavicle Locking Plate':'Верхнепередняя блокируемая пластина для ключицы',
 'Clavicular Hook Locking Plate':'Крючковидная блокируемая пластина для ключицы',
 'Proximal Humeral Greater Tuberosity Locking Compression Plate':'Блокируемая компрессионная пластина для большого бугорка плечевой кости',
 'Proximal Humeral Twisted Locking Plate':'Торсионная блокируемая пластина для проксимального отдела плечевой кости',
 'Proximal Humeral Locking Plate':'Блокируемая пластина для проксимального отдела плечевой кости',
 'Distal Lateral Humeral Locking Plate':'Латеральная блокируемая пластина для дистального отдела плечевой кости',
 'Distal Medial Humeral Reconstruction Locking Plate':'Медиальная реконструктивная блокируемая пластина для дистального отдела плечевой кости',
 'Distal Medial Humeral Locking Plate':'Медиальная блокируемая пластина для дистального отдела плечевой кости',
 'Distal Humeral Sub-condylar Locking Plate':'Подмыщелковая блокируемая пластина для дистального отдела плечевой кости',
 'Extra-articular Distal Humeral Locking Plate':'Внесуставная блокируемая пластина для дистального отдела плечевой кости',
 'Proximal Posterior Tibial Locking Plate':'Задняя блокируемая пластина для проксимального отдела большеберцовой кости',
 'Proximal Medial Tibial Locking Plate':'Медиальная блокируемая пластина для проксимального отдела большеберцовой кости',
 'Proximal Lateral Tibial Locking Plate':'Латеральная блокируемая пластина для проксимального отдела большеберцовой кости',
 'Proximal Lateral Tibial L-Locking Plate':'Латеральная L-образная блокируемая пластина для проксимального отдела большеберцовой кости',
 'Proximal Medial Tibial T-Locking Plate':'Медиальная T-образная блокируемая пластина для проксимального отдела большеберцовой кости',
 'Low Profile Distal Medial Tibial Locking Plate':'Низкопрофильная медиальная блокируемая пластина для дистального отдела большеберцовой кости',
 'Distal Medial Tibial Locking Plate':'Медиальная блокируемая пластина для дистального отдела большеберцовой кости',
 'Distal Anterior Tibial Locking Plate':'Передняя блокируемая пластина для дистального отдела большеберцовой кости',
 'Distal Lateral Tibial Locking Plate':'Латеральная блокируемая пластина для дистального отдела большеберцовой кости',
 'Distal Tibial T-Locking Plate':'T-образная блокируемая пластина для дистального отдела большеберцовой кости',
 'Distal Tibial L-Locking Plate':'L-образная блокируемая пластина для дистального отдела большеберцовой кости',
 'Distal Tibial Hook Locking Plate':'Крючковидная блокируемая пластина для дистального отдела большеберцовой кости',
 'Lateral Ankle Fusion Locking Plate':'Латеральная блокируемая пластина для артродеза голеностопного сустава',
 'Ankle Fusion Locking Plate':'Блокируемая пластина для артродеза голеностопного сустава',
 'Wrist Fusion Locking Plate':'Блокируемая пластина для артродеза лучезапястного сустава',
 'Distal Lateral Fibular Locking Plate':'Латеральная блокируемая пластина для дистального отдела малоберцовой кости',
 'Posterior Lateral Fibular Locking Plate':'Заднелатеральная блокируемая пластина для малоберцовой кости',
 'Distal Fibular Locking Plate':'Блокируемая пластина для дистального отдела малоберцовой кости',
 'Distal Fibular Reconstruction Plate':'Реконструктивная пластина для дистального отдела малоберцовой кости',
 'Olecranon U-Locking Plate':'U-образная блокируемая пластина для локтевого отростка',
 'Olecranon Locking Plate':'Блокируемая пластина для локтевого отростка',
 'Coronoid Locking Plate':'Блокируемая пластина для венечного отростка',
 'Anatomic Radius Volar Locking Plate':'Анатомическая ладонная блокируемая пластина для лучевой кости',
 'Anatomic Forearm Locking Plate':'Анатомическая блокируемая пластина для костей предплечья',
 'Distal Diaphyseal Radius Locking Plate':'Блокируемая пластина для дистальной части диафиза лучевой кости',
 'Distal Volar Rim Radial Locking Plate':'Блокируемая пластина для ладонного края дистального отдела лучевой кости',
 'Distal Volar Radial Locking Plate':'Ладонная блокируемая пластина для дистального отдела лучевой кости',
 'Distal Dorsal Radius Delta Locking Plate':'Тыльная дельтаобразная блокируемая пластина для дистального отдела лучевой кости',
 'Distal Dorsal Radial π Locking Plate':'Тыльная π-образная блокируемая пластина для дистального отдела лучевой кости',
 'Distal Lateral Radius Locking Plate':'Латеральная блокируемая пластина для дистального отдела лучевой кости',
 'Distal Medial Radius Locking Plate':'Медиальная блокируемая пластина для дистального отдела лучевой кости',
 'Distal Radius Locking Plate':'Блокируемая пластина для дистального отдела лучевой кости',
 'Proximal Radius Locking Plate':'Блокируемая пластина для проксимального отдела лучевой кости',
 'Distal Ulnar Locking Plate':'Блокируемая пластина для дистального отдела локтевой кости',
 'Great Trochanter Locking Plate':'Блокируемая пластина для большого вертела',
 'Greater Trochanter U Plate':'U-образная пластина для большого вертела',
 'Greater Trochanter H Plate':'H-образная пластина для большого вертела',
 'Greater Trochanter π Plate':'π-образная пластина для большого вертела','Greater Trochanter n Plate':'n-образная пластина для большого вертела',
 'Distal Medial Femoral Sub-condylar Locking Plate':'Медиальная подмыщелковая блокируемая пластина для дистального отдела бедренной кости',
 'Distal Femoral Sub-condylar Locking Plate':'Подмыщелковая блокируемая пластина для дистального отдела бедренной кости',
 'Distal Medial Femoral Condylar Locking Plate':'Медиальная блокируемая пластина для мыщелка бедренной кости',
 'Distal Lateral Femoral Condylar Locking Plate':'Латеральная блокируемая пластина для мыщелка бедренной кости',
 'Distal Medial Femoral L-Locking Plate':'Медиальная L-образная блокируемая пластина для дистального отдела бедренной кости',
 'Distal Medial Femoral Locking Plate':'Медиальная блокируемая пластина для дистального отдела бедренной кости',
 'Distal Femoral Locking Plate':'Блокируемая пластина для дистального отдела бедренной кости',
 'Lateral Tibial Head Buttress Locking Plate':'Латеральная опорная блокируемая пластина для мыщелков большеберцовой кости',
 'Posterior Medial Proximal Tibial Plate':'Заднемедиальная пластина для проксимального отдела большеберцовой кости',
 'Proximal Femoral Locking Plate':'Блокируемая пластина для проксимального отдела бедренной кости',
 'Cable Grip Locking Plate':'Блокируемая пластина с захватом для серкляжного троса',
 'Cable Locking Plate':'Блокируемая пластина для серкляжного троса',
 'Distal Lateral Femoral Osteotomy Locking Plate':'Латеральная блокируемая пластина для остеотомии дистального отдела бедренной кости',
 'Distal Medial Femoral Osteotomy Locking Plate':'Медиальная блокируемая пластина для остеотомии дистального отдела бедренной кости',
 'Proximal Lateral Tibial Osteotomy Locking Plate':'Латеральная блокируемая пластина для остеотомии проксимального отдела большеберцовой кости',
 'Proximal Medial Tibial Osteotomy Locking Plate':'Медиальная блокируемая пластина для остеотомии проксимального отдела большеберцовой кости',
 'Posterior Tuberosity Calcaneal Locking Plate':'Блокируемая пластина для заднего отдела пяточного бугра',
 'Anterior Process Calcaneal Locking Plate':'Блокируемая пластина для переднего отростка пяточной кости',
 'AP and PT Calcaneal Locking Plate':'Блокируемая пластина AP/PT для пяточной кости',
 'MIS Posterior Calcaneal Locking Plate':'Задняя блокируемая пластина для малоинвазивного остеосинтеза пяточной кости',
 'Calcaneal Fusion Locking Plate':'Блокируемая пластина для артродеза пяточной кости',
 'Calcaneal Step Locking Plate':'Ступенчатая блокируемая пластина для пяточной кости',
 'Calcaneal Locking Plate':'Блокируемая пластина для пяточной кости',
 'Fifth Metatarsal Locking Plate':'Блокируемая пластина для V плюсневой кости',
 'First MTC Plantar Fusion Locking Plate':'Подошвенная блокируемая пластина для артродеза I плюснеклиновидного сустава',
 'First MTC Fusion Locking Plate':'Блокируемая пластина для артродеза I плюснеклиновидного сустава',
 'First MTP Fusion Locking Plate':'Блокируемая пластина для артродеза I плюснефалангового сустава',
 'First Metatarsal Osteotomy Locking Plate':'Блокируемая пластина для остеотомии I плюсневой кости',
 'Distal First Metatarsal T-Locking Plate':'T-образная блокируемая пластина для дистального отдела I плюсневой кости',
 'Proximal First Metatarsal T-Locking Plate':'T-образная блокируемая пластина для проксимального отдела I плюсневой кости',
 'First Metarsal L-Locking Plate':'L-образная блокируемая пластина для I плюсневой кости',
 'L-Locking Plate for Metatarsal':'L-образная блокируемая пластина для плюсневой кости',
 'Lateral Column Lengthening Locking Plate':'Блокируемая пластина для удлинения латеральной колонны стопы',
 'Straight Fusion Locking Plate':'Прямая блокируемая пластина для артродеза',
 'Talus Locking Plate':'Блокируемая пластина для таранной кости',
 'Cuboid Locking Plate':'Блокируемая пластина для кубовидной кости',
 'Navicular Locking Plate':'Блокируемая пластина для ладьевидной кости стопы',
 'Hallux Step Plate':'Ступенчатая пластина для большого пальца стопы',
 'T-Locking Plate':'T-образная блокируемая пластина', 'X-Locking Plate':'X-образная блокируемая пластина',
 'Tarsal Sinus Screw':'Винт для подтаранного артроэреза',
 'End Cap for Calcaneal Cannulated Screw':'Заглушка канюлированного винта для пяточной кости',
 'Calcaneal Cannulated Screw':'Канюлированный винт для пяточной кости',
 'Hammertoe Cannulated Screw':'Канюлированный винт для коррекции молоткообразной деформации пальцев стопы',
 'Anatomical Posterior Acetabular Locking Plate':'Анатомическая задняя блокируемая пластина для вертлужной впадины',
 'Anatomical Pelvic Acetabular Locking Plate':'Анатомическая тазовая блокируемая пластина для вертлужной впадины',
 'Anatomical Acetabular Plate':'Анатомическая пластина для вертлужной впадины',
 'Posterior Surface Quadrangular Plate':'Пластина для задней части четырёхугольной поверхности',
 'Anterior Surface Quadrangular Plate':'Пластина для передней части четырёхугольной поверхности',
 'Posterior Pelvic Plate':'Задняя тазовая пластина','Anterior Pelvic Plate':'Передняя тазовая пластина',
 'Anatomical Pelvic Plate':'Анатомическая тазовая пластина','Pelvic Crest Plate':'Пластина для гребня подвздошной кости',
 'Anterior Sacroiliac Joint Plate':'Передняя пластина для крестцово-подвздошного сочленения',
 'Sacroiliac Joint Plate':'Пластина для крестцово-подвздошного сочленения',
 'Symphyseal Plate':'Пластина для лонного сочленения','Anatomical Iliopubic Plate':'Анатомическая подвздошно-лобковая пластина',
 'Low Posterior Column Infra-arcuate Line Locking Plate':'Низкая блокируемая пластина для задней колонны ниже дугообразной линии',
 'High Posterior Column Infra-arcuate Line Locking Plate':'Высокая блокируемая пластина для задней колонны ниже дугообразной линии',
 'High Posterior Column Supra-arcuate Line Locking Plate':'Высокая блокируемая пластина для задней колонны выше дугообразной линии',
 'Supra-arcuate Line Locking Plate':'Блокируемая пластина выше дугообразной линии',
 'Infra-arcuate Line Locking Plate':'Блокируемая пластина ниже дугообразной линии',
 'Puboischiatic Locking Plate':'Лобково-седалищная блокируемая пластина',
 'Ilioischiatic Locking Plate':'Подвздошно-седалищная блокируемая пластина',
 'Universal Locking Plate':'Универсальная блокируемая пластина',
 'Connecting Locking Screw':'Соединительный блокируемый винт',
 'Pelvic Reconstruction Locking Plate':'Тазовая реконструктивная блокируемая пластина',
 'Reconstruction Locking Plate':'Реконструктивная блокируемая пластина',
 'Pelvic Reconstruction Plate':'Тазовая реконструктивная пластина','Reconstruction Plate':'Реконструктивная пластина',
 'Press Plate':'Прижимная пластина','Osteotomy Locking Plate':'Блокируемая пластина для остеотомии',
 'Locking Buttress Screw':'Блокируемый опорный винт','Sliding Cannulated Locking Screw':'Скользящий канюлированный блокируемый винт',
 'Cannulated Locking Screw':'Канюлированный блокируемый винт','Locking Screw':'Блокируемый винт',
 'Cortex Screw':'Кортикальный винт','Cancellous Screw':'Спонгиозный винт','Snap-off Screw':'Винт с отламываемой головкой',
 'Locking Spacer':'Блокируемая проставка','Cable Spacer':'Проставка для серкляжного троса','Cable Clasp':'Фиксатор серкляжного троса','Cable':'Серкляжный трос',
}
QUALIFIERS = {
 'Twin Hole':'со сдвоенными отверстиями','variable angle':'с переменным углом','self-tapping with three flute':'самонарезающий, с тремя режущими канавками',
 'self-tapping':'самонарезающий','half threaded':'с частичной резьбой','fully threaded':'с полной резьбой',
 'torxdrive':'со шлицем Torx','torxdirve':'со шлицем Torx','hexagon':'с шестигранным шлицем','flat head':'с плоской головкой',
 'thread length':'длина резьбы','with drill guide':'с направителем сверла','suture hole':'с отверстием для шовного материала',
 'standard bend':'стандартный изгиб','low bend':'малый изгиб','for union plate':'для составной пластины',
 'for supra-arcuate line':'выше дугообразной линии','for infra-arcuate line':'ниже дугообразной линии',
 'curved':'изогнутая','straight':'прямая','Oblique':'косая','flat':'плоская','broad':'широкая','small':'малая','medium':'средняя','large':'большая','square':'с квадратным шлицем',
}
@lru_cache(maxsize=32)
def compiled_rules(items):
    return [(re.compile(r'(?<![A-Za-z])'+re.escape(en)+r'(?![A-Za-z])',re.I),ru)for en,ru in sorted(items,key=lambda x:-len(x[0]))]
def replace_terms(text,terms):
    for pattern,ru in compiled_rules(tuple(terms.items())):text=pattern.sub(lambda _:ru,text)
    return text
def implant(en):
    ru=re.sub(r'for ([0-9.]+)mm Cannulated Locking Screw',r'для канюлированного блокируемого винта Ø\1 мм',en)
    ru=replace_terms(ru,TERMS);ru=replace_terms(ru,QUALIFIERS)
    ru=re.sub(r'(?<=\d)mm\b',' мм',ru,flags=re.I)
    return {'ru':ru,'en':en}

INSTRUMENTS = {
 'Extraction Screw':'Винтовой экстрактор','Insertion Guide':'Установочный направитель','Fixation Bolt':'Фиксирующий болт',
 'Guide Wire with Single Trocar':'Спица-проводник с односторонней трёхгранной заточкой',
 'Guide Wire Sleeve':'Втулка для спицы-проводника','Guide Wire Caddy':'Органайзер для спиц-проводников','Guide Wire':'Спица-проводник',
 'Tap for Cortex Screws':'Метчик для кортикальных винтов','Tap for Cancellous Screws':'Метчик для спонгиозных винтов',
 'Tap for Cannulated Screws':'Метчик для канюлированных винтов','Tap':'Метчик',
 'Drill Sleeve for Drill Bits':'Сверлильная втулка','Drill Sleeve for Drill Bit':'Сверлильная втулка',
 'Drill Sleeve for Guide Wire':'Втулка для спицы-проводника','Drill Sleeve for Insertion Guide':'Сверлильная втулка для установочного направителя',
 'Drill Sleeve Box':'Контейнер для сверлильных втулок','Drill Sleeve':'Сверлильная втулка',
 'Double Drill Guide':'Двухканальный направитель сверла','Universal Drill Guide':'Универсальный направитель сверла',
 'Variable Angle Drill Sleeve':'Сверлильная втулка с переменным углом','Drill Guide For Flexible Drill Bits':'Направитель гибкого сверла',
 'DCP Drill Guide':'Направитель сверла DCP','Drill Bit':'Сверло','AO Coupling Drill Bit':'Сверло с соединением AO',
 'Countersink':'Зенкер','Torque Limiting Handle':'Рукоятка с ограничителем крутящего момента',
 'Torque Indicating Screwdriver':'Динамометрическая отвёртка','Torque Indicating Handle':'Динамометрическая рукоятка',
 'Screwdriver Shaft':'Стержень отвёртки','Screwdriver':'Отвёртка','Depth Gauge for Drill Sleeve':'Глубиномер для сверлильной втулки',
 'Depth Gauge':'Глубиномер','Bending Iron for Reconstruction Plates':'Гибочный инструмент для реконструктивных пластин',
 'Bending Pliers for Reconstruction Plates':'Гибочные щипцы для реконструктивных пластин',
 'Bending Template for Straight Reconstruction Plates':'Шаблон для изгибания прямых реконструктивных пластин',
 'Bending Template for Curved Reconstruction Plates':'Шаблон для изгибания изогнутых реконструктивных пластин',
 'Bending Iron':'Гибочный инструмент','Bending Pliers':'Гибочные щипцы',
 'T-Handle with Quick Coupling':'T-образная рукоятка с быстросъёмным соединением','Handle with Quick Coupling':'Рукоятка с быстросъёмным соединением',
 'Reduction Forceps with Serrated Jaw':'Репозиционные щипцы с зубчатой губкой','Reduction Forceps with Points':'Репозиционные щипцы с острыми концами',
 'Pelvic Reduction Forceps':'Тазовые репозиционные щипцы','Reduction Forceps':'Репозиционные щипцы',
 'Bone Holding Forceps':'Костодержатель','Screw Forceps':'Щипцы для винтов',
 'Periosteal Elevator':'Распатор','Bone Lever':'Костный рычаг','Bone Hook':'Костный крючок','Pelvic Retractor':'Тазовый ретрактор',
 'Bone Retractor':'Костный ретрактор','Bone Rongeur':'Костные кусачки','Bone Spreader':'Костный расширитель',
 'Holding Sleeve for Torque Indicating Screwdriver':'Удерживающая втулка для динамометрической отвёртки',
 'Holding Sleeve for Cortex Screw':'Удерживающая втулка для кортикального винта',
 'Holding Sleeve for Locking Screw':'Удерживающая втулка для блокируемого винта','Holding Sleeve':'Удерживающая втулка',
 'Extraction Screw for Screws':'Винтовой экстрактор','Broken Screw Extractor':'Экстрактор сломанных винтов',
 'Aiming Block for Distal Radius Locking Plate':'Прицельный блок для блокируемой пластины дистального отдела лучевой кости',
 'Guiding Block for Distal Radius Variable Angle Locking Plate':'Направляющий блок для пластины дистального отдела лучевой кости с переменным углом',
 'Guiding Block for LCP Distal Femur':'Направляющий блок для пластины LCP дистального отдела бедренной кости',
 'Aiming Arm':'Прицельная штанга','Aiming Device':'Прицельное устройство','Guiding Block':'Направляющий блок',
 'Insertion Guide for Distal Femur':'Установочный направитель для дистального отдела бедренной кости',
 'Insertion Guide for Proximal Femur':'Установочный направитель для проксимального отдела бедренной кости',
 'Insertion Guide for Proximal Tibia':'Установочный направитель для проксимального отдела большеберцовой кости',
 'Fixation Bolt for Insertion Guide':'Фиксирующий болт установочного направителя','Stopper for Insertion Guide':'Ограничитель установочного направителя',
 'Drill Sleeve for Insertion Guide':'Сверлильная втулка установочного направителя',
 'Wrench for Fixation Bolt':'Ключ для фиксирующего болта','Wrench for Fixation Sleeve':'Ключ для фиксирующей втулки',
 'Wrench for locking shaft':'Ключ для блокирующего стержня','L-Wrench':'L-образный ключ','Wrench':'Ключ',
 'Centering Sleeve for Guide Wire':'Центрирующая втулка для спицы-проводника','Centering Sleeve':'Центрирующая втулка',
 'Fixation Sleeve for Drill Bits':'Фиксирующая втулка для свёрл','Fixation Sleeve':'Фиксирующая втулка',
 'Connecting Screw for Sleeve':'Соединительный винт для втулки','Connecting Screw':'Соединительный винт',
 'Compression Sleeve':'Компрессионная втулка','Outer Sleeve':'Наружная втулка','Out Sleeve':'Наружная втулка',
 'Insertion Handle':'Установочная рукоятка','Attachment Bit':'Насадка','Trocar':'Троакар','Stopper':'Ограничитель',
 'Cable Crimper':'Обжимной инструмент для серкляжного троса','Cable Cutter':'Кусачки для серкляжного троса',
 'Cable Tension Holder':'Фиксатор натяжения серкляжного троса','Cable Tensioner':'Натяжитель серкляжного троса',
 'Cable Passer':'Проводник серкляжного троса','Cerclage Passer':'Серкляжный проводник','Cable Lock':'Замок серкляжного троса',
 'Osteotomy Gap Measuring Device':'Измеритель остеотомической щели','Osteotomy Chisel':'Остеотомическое долото','Osteotome':'Остеотом',
 'Direct Measuring Device':'Измеритель прямого отсчёта','Femoral Alignment Rods':'Бедренные осевые стержни','Tibial Alignment Rods':'Большеберцовые осевые стержни',
 'Large Stand for Alignment Rods':'Большая стойка для осевых стержней','Small Stand for Alignment Rods':'Малая стойка для осевых стержней',
 'Spreader Forceps':'Расширяющие щипцы','Spreader':'Расширитель','Cutting Pliers':'Кусачки','Pulling Device':'Тяговое устройство',
 'Hammertoe Awl':'Шило для коррекции молоткообразной деформации','Hammertoe Hammer':'Молоток для коррекции молоткообразной деформации',
 'Hammertoe Screwdriver':'Отвёртка для коррекции молоткообразной деформации',
 'TSS II Universal Screwdriver':'Универсальная отвёртка TSS II','TSS II Positioning Sleeve':'Позиционирующая втулка TSS II',
 'TSS Straight Handle with Quick Coupling':'Прямая рукоятка TSS с быстросъёмным соединением',
 'TSS II Guide Wire':'Спица-проводник TSS II','TSS Guide Wire':'Спица-проводник TSS','TSS Screwdriver':'Отвёртка TSS',
 'TSS II Trial':'Пробник TSS II','TSS Trial':'Пробник TSS','TSS Probe':'Зонд TSS',
 'Donor Harvester':'Инструмент для забора донорского костно-хрящевого трансплантата',
 'Recipient Harvester':'Инструмент для подготовки реципиентного ложа','Delivery Tube':'Трубка для введения трансплантата',
 'Alignment Rod':'Центрирующий стержень','Tamp':'Импактор','Ball Spike':'Шаровидный толкатель',
 'Disc for Reduction Forceps':'Опорный диск для репозиционных щипцов','Handle':'Рукоятка',
 'Instrument Case':'Контейнер для инструментов','Implant Case':'Контейнер для имплантов','Screw Case':'Контейнер для винтов',
 'Tarsal Sinus Screw Caddy':'Органайзер для винтов подтаранного артроэреза',
 'Hammertoe Cannulated Screw Caddy':'Органайзер для канюлированных винтов коррекции молоткообразной деформации',
 'Cable/Clasp Case':'Контейнер для серкляжных тросов и фиксаторов',
}
DETAILS = {
 'for Proximal Medial Tibia':'для проксимального медиального отдела большеберцовой кости',
 'for Proximal Lateral Tibia':'для проксимального латерального отдела большеберцовой кости',
 'for Distal Medial Femur':'для дистального медиального отдела бедренной кости',
 'for Distal Femur':'для дистального отдела бедренной кости',
 'for Guiding Block of LCP Distal Femur':'для направляющего блока LCP дистального отдела бедренной кости',
 'for Tension Holder':'для фиксатора натяжения','for Cable Tensioner':'для натяжителя серкляжного троса',
 'for Cerclage Passer':'для серкляжного проводника','for Screws':'для винтов',
 'for Aiming Device':'для прицельного устройства','for Insertion Guide':'для установочного направителя',
 'for Fixation Sleeve':'для фиксирующей втулки','for Torque Indicating Screwdriver':'для динамометрической отвёртки',
 'for load position':'для компрессионного положения','for neutral position':'для нейтрального положения',
 'with Quick Coupling':'с быстросъёмным соединением','with threaded tip':'с резьбовым наконечником',
 'with tip diameter':'диаметр наконечника','with Scale':'со шкалой',
 'one-hand operable':'для работы одной рукой','point tip':'с острым наконечником',
 'self-retaining':'самоудерживающий','quick guiding':'быстрое позиционирование',
 'head holes':'отверстий в головной части','flat edge':'с плоской рабочей кромкой',
 'rectangular':'прямоугольный','semicircle':'полукруглый','threaded':'с резьбой','blue':'синяя',
 'for Neutral And Load Position':'для нейтрального и компрессионного положения','with AO Quick Coupling':'с быстросъёмным соединением AO',
 'with Triangle Coupling':'с треугольным соединением','with AO Coupling':'с соединением AO','AO Coupling':'соединение AO',
 'Triangle Coupling':'треугольное соединение','for Quick Coupling':'для быстросъёмного соединения',
 'with universal joint':'с карданным шарниром','with angled pointed ball tips':'с угловыми острыми шаровидными наконечниками',
 'with three pointed ball tips':'с тремя острыми шаровидными наконечниками','with pointed ball tips':'с острыми шаровидными наконечниками',
 'with points':'с острыми концами','for use with Cortex Screws':'для использования с кортикальными винтами',
 'for Foot & Ankle':'для стопы и голеностопного сустава','for Drill Bits':'для свёрл',
 'for Drill Bit':'для сверла',
 'for Guide Wire':'для спицы-проводника','for Cortex Screws':'для кортикальных винтов','for Locking Screws':'для блокируемых винтов',
 'Cortex Screws':'кортикальные винты','Locking Screws':'блокируемые винты',
 'self-holding':'самоудерживающие','self-centering':'самоцентрирующийся','speed lock':'с быстрой фиксацией',
 'oblique edge':'с косой рабочей кромкой','round edge':'с закруглённой рабочей кромкой','straight edge':'с прямой рабочей кромкой',
 'torxdrive':'со шлицем Torx','hexagonal':'с шестигранным шлицем','closed':'закрытый','opened':'открытый',
 'cannulated':'канюлированная','solid':'цельная','adjustable':'регулируемые','asymmetric':'асимметричные',
 'angled':'угловые','blunt':'тупой','sharp':'острый','flexible':'гибкое','customized':'специальное исполнение',
 'small':'малый','large':'большой','short':'короткий','long':'длинный','medium':'средний','left':'левый','right':'правый',
 'curved':'изогнутый','flat':'плоский','length':'длина','width':'ширина','straight':'прямой',
 'Aluminium Alloy':'алюминиевый сплав','Aluminium':'алюминий',
}
def instrument(en,context=''):
    prep={k:v for k,v in DETAILS.items()if k.startswith(('for ','with '))}
    ru=re.sub(r'for (Ø[0-9.]+) Locking Screws',r'для блокируемых винтов \1',en)
    ru=re.sub(r'for (Ø[0-9.]+) Cortex Screws',r'для кортикальных винтов \1',ru)
    ru=re.sub(r'for (Ø[0-9.]+) Drill Bits',r'для свёрл \1',ru)
    ru=replace_terms(ru,prep)
    ru=replace_terms(ru,INSTRUMENTS)
    # Case names carry the clinical family separately from the instrument name.
    if 'Case' in en and context:
        material=re.search(r'\((?:Aluminium(?: Alloy)?\s*)\)',en,re.I)
        ru=('Контейнер имплантов' if 'Implant Case' in en else 'Контейнер инструментов')+' — '+context
        if re.search(r'\bII\b',en)and not re.search(r'\bII\b',context):ru+=' II'
        if material:ru+=' ('+replace_terms(material.group()[1:-1].strip(),DETAILS)+')'
    ru=replace_terms(ru,DETAILS);ru=re.sub(r'(?<=\d)mm\b',' мм',ru,flags=re.I);ru=ru.replace('N.m','Н·м').replace('Nm','Н·м')
    # Agree modifiers with the actual medical instrument noun.
    if re.search(r'Forceps|Pliers',en,re.I):
        for a,b in {'малый':'малые','большой':'большие','длинный':'длинные','короткий':'короткие','левый':'левые','правый':'правые','самоудерживающие':'самоудерживающиеся'}.items():ru=re.sub(r'\b'+a+r'\b',b,ru)
    elif re.match(r'(?:AO Coupling )?Drill Bit',en,re.I):
        for a,b in {'малый':'малое','большой':'большое','длинный':'длинное','короткий':'короткое','левый':'левое','правый':'правое','полукруглый':'полукруглое'}.items():ru=re.sub(r'\b'+a+r'\b',b,ru)
    elif re.match(r'(?:TSS (?:II )?)?(?:Drill Sleeve|Guide Wire|Holding Sleeve|Centering Sleeve|Fixation Sleeve|Outer Sleeve|Out Sleeve|Compression Sleeve|Aiming Arm|Handle|Screwdriver(?! Shaft))',en,re.I):
        for a,b in {'малый':'малая','большой':'большая','длинный':'длинная','короткий':'короткая','левый':'левая','правый':'правая','прямой':'прямая','прямоугольный':'прямоугольная'}.items():ru=re.sub(r'\b'+a+r'\b',b,ru)
    return {'ru':ru,'en':en}

# Codex-authored clinical terminology for the authorized sections 5–8.
TERMS.update({
 'No Profile Cannulated Screw':'Канюлированный винт без выступающей головки',
 'Headless Compression Screw':'Безголовочный компрессионный винт','Headless Screw':'Безголовочный винт',
 'Cannulated Screw':'Канюлированный винт','Spiked Washer':'Шипованная шайба','Washer':'Шайба',
 'Compression Locking Rod System':'Блокируемая компрессионная стержневая система','Compression Rod System':'Компрессионная стержневая система',
 'Heberden Screw':'Винт Heberden','Mini Hook Locking Plate':'Крючковидная мини-блокируемая пластина',
 'Adaption Locking Plate':'Моделируемая блокируемая пластина','Straight Locking Plate':'Прямая блокируемая пластина',
 'Locking T-Plate':'T-образная блокируемая пластина','Locking Y-Plate':'Y-образная блокируемая пластина',
 'Locking Condylar Plate':'Мыщелковая блокируемая пластина','Condylar Locking Plate':'Мыщелковая блокируемая пластина',
 'Locking Strut Plate':'Опорная блокируемая пластина','Mini Wed Locking Plate':'Клиновидная мини-блокируемая пластина',
 'Mini Wedge Locking Plate':'Клиновидная мини-блокируемая пластина',
 'Y-Adaption Locking Plate':'Y-образная моделируемая блокируемая пластина','T-Adaption Locking Plate':'T-образная моделируемая блокируемая пластина',
 'T-Locking Plate':'T-образная блокируемая пластина','L-Locking Plate':'L-образная блокируемая пластина',
 'H-Locking Plate':'H-образная блокируемая пластина','X-Locking Plate':'X-образная блокируемая пластина',
 'Locking Plate':'Блокируемая пластина',
 'Barrel Locking Plate Spiral Blade':'Спиральный клинок для блокируемой пластины DHS/DCS',
 'Compression Screw for Barrel Locking Plate Spiral Blade':'Компрессионный винт спирального клинка блокируемой пластины DHS/DCS',
 'Barrel Locking Plate(Dynamic Hip Screw)':'Блокируемая пластина с втулкой для динамического бедренного винта (DHS)',
 'Barrel Locking Plate(Dynamic Condylar Screw)':'Блокируемая пластина с втулкой для динамического мыщелкового винта (DCS)',
 'Barrel Plate(Dynamic Hip Screw)':'Пластина с втулкой для динамического бедренного винта (DHS)',
 'Barrel Plate(Dynamic Condylar Screw)':'Пластина с втулкой для динамического мыщелкового винта (DCS)',
 'Trochanter Stabilizing Locking Plate':'Блокируемая пластина для стабилизации большого вертела',
 'Trochanter Stabilizing Plate':'Пластина для стабилизации большого вертела',
 'Big Lag Screw for Barrel Plate':'Большой шеечный винт для пластины с втулкой',
 'Proximal Femoral Nail, anti-rotation':'Антиротационный проксимальный бедренный штифт',
 'Proximal Femoral Nail Spiral Blade':'Спиральный клинок проксимального бедренного штифта',
 'Aimstrong Proximal Femoral Nail':'Проксимальный бедренный штифт Aimstrong',
 'Aimstrong Spiral Blade':'Спиральный клинок Aimstrong','Aimstrong Lag Screw':'Шеечный винт Aimstrong','Aimstrong End Cap':'Торцевая заглушка Aimstrong',
 'Proximal Femoral Compression Nail':'Компрессионный проксимальный бедренный штифт',
 'Universal Femoral Nail':'Универсальный бедренный штифт','Retrograde Femoral Nail':'Ретроградный бедренный штифт',
 'Distal Femoral Nail':'Дистальный бедренный штифт','Universal Humeral Nail':'Универсальный плечевой штифт',
 'Advanced Humeral Nail':'Усовершенствованный плечевой штифт','Universal Tibial Nail':'Универсальный большеберцовый штифт',
 'Suprapatellar Tibial Nail':'Супрапателлярный большеберцовый штифт','Distal Tibial Nail':'Дистальный большеберцовый штифт',
 'Fibular Nail':'Малоберцовый штифт','Ulna Nail':'Штифт локтевой кости','Radius Nail':'Штифт лучевой кости',
 'Adolescent Femoral Nail':'Бедренный штифт для подростков','Titanium Elastic Nail':'Титановый эластичный штифт',
 'Sliding Nail System':'Система скользящих штифтов','Spiral Blade':'Спиральный клинок',
 'Condyle Screw':'Мыщелковый винт','Condyle Nut and Washer':'Мыщелковая гайка и шайба',
 'Universal End Cap for UFN/UTN':'Универсальная торцевая заглушка UFN/UTN',
 'End Cap':'Торцевая заглушка','Locking Bolt':'Блокирующий болт','Lag Screw':'Шеечный винт','Compression Screw':'Компрессионный винт',
 'Pure Titanium':'чистый титан','Titanium Alloy':'титановый сплав','Titanium':'титан',
})
QUALIFIERS.update({'fully thread':'с полной резьбой','short thread':'с короткой резьбой','long thread':'с длинной резьбой',
 'long threaded':'с длинной резьбой','short threaded':'с короткой резьбой','self-retaining':'с удерживающей фиксацией',
 'oblique-angled':'с косым углом','for Foot':'для стопы','Cannulated':'Канюлированный',
 'for PFNA':'для PFNA','for UFN/UTN':'для UFN/UTN',
 'for Proximal Femoral Compression Nail':'для компрессионного проксимального бедренного штифта',
 'for Universal Femoral Nail':'для универсального бедренного штифта',
 'for Distal Femoral Nail':'для дистального бедренного штифта',
 'for Universal Humeral Nail':'для универсального плечевого штифта',
 'for Humeral Nail':'для плечевого штифта','for Advanced Humeral Nail':'для усовершенствованного плечевого штифта',
 'for Universal Tibial Nail':'для универсального большеберцового штифта',
 'for Suprapatellar Tibial Nail':'для супрапателлярного большеберцового штифта',
 'for Distal Tibial Nail':'для дистального большеберцового штифта','for Fibular Nail':'для малоберцового штифта',
 'for Adolescent Femoral Nail':'для бедренного штифта для подростков',
})
INSTRUMENTS.update({
 'Guide Wire Drill Sleeve':'Сверлильная втулка для спицы-проводника','Protection Sleeve':'Защитная втулка',
 'Reverse Awl':'Реверсивное шило','Tissue Protector':'Протектор мягких тканей',
 'Measuring Device':'Измеритель','Proximal Reamer':'Проксимальный ример','Cannulated Reamer':'Канюлированный ример',
 'Flexible Reamer':'Гибкий ример','Flexible Drill Bit':'Гибкое сверло','Reamer':'Ример',
 'Impactor for TEN':'Импактор для титанового эластичного штифта','Inserter for TEN':'Инструмент для введения титанового эластичного штифта',
 'Extraction Pliers for TEN':'Щипцы для удаления титанового эластичного штифта','Hammer Guide for TEN':'Направитель молотка для титанового эластичного штифта',
 'Cannulated Screwdriver':'Канюлированная отвёртка','Cannulated Countersink':'Канюлированный зенкер',
 'Cannulated Drill Bit':'Канюлированное сверло','Cannulated Tap':'Канюлированный метчик',
 'Extraction Rod':'Экстракционный стержень','Extraction Bolt':'Экстракционный болт','Extraction Hook':'Экстракционный крючок',
 'Slotted Hammer':'Молоток с прорезью','Sliding Hammer':'Скользящий молоток','Slide Hammer':'Скользящий молоток',
 'Connecting Rod':'Соединительный стержень','Connecting Bolt':'Соединительный болт','Connecting Shaft':'Соединительный стержень',
 'Locking Shaft':'Блокирующий стержень','Locking Bolt':'Блокирующий болт',
 'Inner Sleeve':'Внутренняя втулка','Outer Drill Sleeve':'Наружная сверлильная втулка','Inner Drill Sleeve':'Внутренняя сверлильная втулка',
 'Nail Holder':'Держатель штифта','Nail Extractor':'Экстрактор штифта','Impactor':'Импактор','Extractor':'Экстрактор',
 'Awl':'Шило','Hammer':'Молоток','Ruler':'Линейка','Screw Extractor':'Экстрактор винта',
 'Reduction Rod':'Репозиционный стержень','Drill Guide':'Направитель сверла','Drill Bits':'Свёрла',
 'Parallel Guide':'Параллельный направитель','Socket Wrench':'Торцевой ключ','Open Wrench':'Рожковый ключ',
 'Screw Holding Forceps':'Щипцы для удержания винтов','Screw Holder':'Держатель винта','Screw Holding Sleeve':'Удерживающая втулка винта',
 'Screw Caddy':'Органайзер для винтов','Wire Caddy':'Органайзер для спиц','Pin Wrench':'Штифтовый ключ',
 'DHSA Triple Reamer':'Трёхступенчатый ример DHSA','Triple Reamer':'Трёхступенчатый ример',
})
DETAILS.update({
 'with Proximal Diameter':'с проксимальным диаметром','Proximal Diameter':'Проксимальный диаметр',
 'for Guide Wire':'для спицы-проводника','for Drill Bit':'для сверла','for Spiral Blade':'для спирального клинка',
 'for Lag Screw':'для шеечного винта','for Locking Screw':'для блокируемого винта',
 'with olive head':'с оливообразным наконечником','with ball tip':'с шаровидным наконечником',
 'with T-Handle':'с T-образной рукояткой','for End Cap':'для торцевой заглушки',
 'for TEN':'для титанового эластичного штифта','for Nail':'для штифта',
 'universal':'универсальный','reverse':'реверсивный','distal':'дистальный','proximal':'проксимальный',
 'diameter':'диаметр','for Blade':'для клинка',
})

TERMS.update({'Stainless Steel':'нержавеющая сталь','S-Mini Wed Locking Plate':'S-образная клиновидная мини-блокируемая пластина'})
# Genitive anatomical qualifiers are applied as whole phrases, before the noun lexicon.
for phrase,genitive in {
 'Proximal Femoral Compression Nail':'компрессионного проксимального бедренного штифта',
 'Universal Femoral Nail':'универсального бедренного штифта','Distal Femoral Nail':'дистального бедренного штифта',
 'Universal Humeral Nail':'универсального плечевого штифта','Humeral Nail':'плечевого штифта',
 'Advanced Humeral Nail':'усовершенствованного плечевого штифта','Universal Tibial Nail':'универсального большеберцового штифта',
 'Suprapatellar Tibial Nail':'супрапателлярного большеберцового штифта','Distal Tibial Nail':'дистального большеберцового штифта',
 'Fibular Nail':'малоберцового штифта','Ulna Nail':'штифта локтевой кости','Radius Nail':'штифта лучевой кости',
 'Forearm Nail':'штифта костей предплечья','Adolescent Femoral Nail':'бедренного штифта для подростков',
 'Titanium Elastic Nail':'титанового эластичного штифта',
}.items():
 for prefix,ruPrefix in {'End Cap':'Торцевая заглушка','Locking Screw':'Блокируемый винт','Spiral Blade':'Спиральный клинок','Lag Screw':'Шеечный винт','Compression Screw':'Компрессионный винт'}.items():
  TERMS[prefix+' for '+phrase]=ruPrefix+' для '+genitive
INSTRUMENTS.update({
 'Guide Sleeve':'Направляющая втулка','Cleaning Brush':'Щётка для очистки','Screw Forcep':'Щипцы для винтов',
 'Parallel Wire Guide':'Параллельный направитель спиц','Multiple Wire Guide':'Многоканальный направитель спиц',
 'Radiographic Ruler':'Рентгеноконтрастная линейка','Holder for Guide Wire':'Держатель спицы-проводника',
 'Proximal Reaming Drill':'Проксимальное рассверливающее сверло','Blocker':'Блокиратор',
 'Measuring Device for RFN':'Измеритель для RFN','RFN Insertion Handle':'Установочная рукоятка RFN',
 'RFN Distal Aiming Shaft':'Дистальная прицельная штанга RFN',
 'Connecting Screw for Insertion Handle':'Соединительный винт установочной рукоятки',
})
DETAILS.update({'for Guide Wires':'для спиц-проводников','for Cannulated Drill Bits':'для канюлированных свёрл',
 'for Predrilling':'для предварительного сверления','for Parallel Wire Guide':'для параллельного направителя спиц',
 'for Cannulated Screws':'для канюлированных винтов','Advanced':'расширенная комплектация',
 'Headless Compression Screw':'Безголовочный компрессионный винт','No Profile':'без выступающей головки',
 'Cannulated Screws':'канюлированные винты','Screws':'винты',
})
QUALIFIERS.update({'long':'длинный','short':'короткий','for Tibial Nail':'для большеберцового штифта'})
# Full clinical phrases preserve grammatical case while retaining every dimension.
_original_implant=implant

def implant(en):
 ru=en
 ru=re.sub(r'for ([0-9./]+)mm Cannulated Screw',r'для канюлированного винта \1 мм',ru,flags=re.I)
 ru=re.sub(r'for ([0-9.]+)mm Distal Tibial Nail',r'для дистального большеберцового штифта \1 мм',ru,flags=re.I)
 ru=replace_terms(ru,TERMS);ru=replace_terms(ru,QUALIFIERS);ru=re.sub(r'(?<=\d)mm\b',' мм',ru,flags=re.I)
 ru=ru.replace('for Tibial Nail','для большеберцового штифта')
 return {'ru':ru,'en':en}
_original_instrument=instrument

def instrument(en,context=''):
 text=re.sub(r'for (Ø[0-9.]+(?:/Ø?[0-9.]+)*) Cannulated Screws',r'для канюлированных винтов \1',en,flags=re.I)
 text=re.sub(r'for (Ø[0-9.]+(?:/Ø?[0-9.]+)*) Guide Wire',r'для спицы-проводника \1',text,flags=re.I)
 result=_original_instrument(text,context)
 result['en']=en
 return result

# Clinical instrument nomenclature for the nail, screw and mini-fragment sets.
EXTRA_NOUNS={
 'Depth Guage':'Глубиномер','Depth Cauge':'Глубиномер','Combination Wrench':'Комбинированный ключ',
 'Holding Forceps for Plates':'Щипцы для удержания пластин','Holding Forceps for Screws':'Щипцы для удержания винтов',
 'Bone Reduction Forcep':'Костные репозиционные щипцы','Bending/Cutting Pliers':'Гибочные щипцы-кусачки','Sharp Hook':'Острый крючок',
 'Case Cover':'Крышка контейнера','Tray for Plate':'Лоток для пластин','Centering Sleeve for Tap':'Центрирующая втулка метчика',
 'Tap for DHS/DCS Screws':'Метчик для винтов DHS/DCS','DHS Angled Guide':'Угловой направитель DHS','DCS Angled Guide':'Угловой направитель DCS',
 'Wrench for DHS/DCS Lag Screws':'Ключ для шеечных винтов DHS/DCS','T- Wrench for One-step Insertion':'T-образный ключ для одноэтапного введения',
 'T-wrench':'T-образный ключ','T-Handle':'T-образная рукоятка','Reaming Drill':'Рассверливающее сверло','Key':'Ключ','Connector':'Соединитель',
 'Buttress/Compression Nut':'Опорно-компрессионная гайка','Compression Nut':'Компрессионная гайка','Compression screw':'Компрессионный винт',
 'Hammer Guide for Slide Hammer':'Направитель скользящего молотка','Hammer Guide':'Направитель молотка',
 'Cleaning Stylet':'Стилет для очистки','Stretch Aiming Arm Shaft':'Удлинённая прицельная штанга','Stretch Aiming Arm':'Удлинённая прицельная штанга',
 'Connecting Aiming Shaft':'Соединительная прицельная штанга','Proximal Aiming Shaft':'Проксимальная прицельная штанга',
 'External Aiming Handle':'Рукоятка наружного прицельного устройства','External Aiming Shaft':'Штанга наружного прицельного устройства',
 'Distal Aiming Arm Shaft':'Штанга дистального прицельного устройства','Aiming Arm Shaft':'Штанга прицельного устройства','Aiming Shaft':'Прицельная штанга',
 'Location Arm':'Позиционирующая штанга','Location Block':'Позиционирующий блок','Fixation Pin':'Фиксирующий штифт','Calibrating Pin':'Калибровочный штифт',
 'Locking Screw I for Aiming Arm':'Фиксирующий винт I прицельной штанги','Locking Screw II for Aiming Arm':'Фиксирующий винт II прицельной штанги',
 'Locking Screw for Aiming Arm':'Фиксирующий винт прицельной штанги','Locking Screw for Aiming Shaft':'Фиксирующий винт прицельной штанги',
 'Locking Screw':'Фиксирующий винт','U-Clip':'U-образная скоба','Compression Support Shaft':'Опорный стержень для компрессии',
 'Jig':'Прицельный шаблон','Connection Shaft':'Соединительный стержень','Bone Cement Injector':'Инжектор костного цемента',
 'Aimstrong Lag Screw Inserter':'Инструмент для введения шеечного винта Aimstrong',
 'Soft Tissue Protector':'Протектор мягких тканей','Ratchet Handle':'Рукоятка с храповым механизмом','Ratchet Wrench':'Ключ с храповым механизмом',
 'Ratchet':'Храповой механизм','Positioning Pin':'Позиционирующий штифт','Hollow Reamer':'Канюлированный ример',
 'Extraction Shaft':'Экстракционный стержень','Reduction Shaft':'Репозиционный стержень','Reduction Sleeve':'Репозиционная втулка',
 'Stop Sleeve':'Ограничительная втулка','Compression Device':'Компрессионное устройство','Driving Cap':'Насадка для импакции',
 'Wire Guide':'Направитель спицы','Outer Protection Sleeve':'Наружная защитная втулка','Protection Sleeves':'Защитные втулки',
 'Trial Implant':'Пробный имплант','Retractor':'Ретрактор','Chisel':'Долото','Sloped Drill Sleeve':'Наклонная сверлильная втулка',
 'Inserter-Extractor':'Инструмент для введения и удаления','Inserter':'Инструмент для введения','Extraction Pliers':'Экстракционные щипцы',
 'Broken Nail Extractor':'Экстрактор сломанных штифтов','Pliers for Nail Removal':'Щипцы для удаления штифта',
 'Intramedullary Nail Removal Set Case':'Контейнер набора для удаления интрамедуллярных штифтов',
 'Cutter':'Кусачки','Bender':'Гибочный инструмент','Holder':'Держатель','Instrument':'Инструмент',
}
GENITIVE={
 'Guide Wires':'спиц-проводников','Guide Wire':'спицы-проводника','Calibrating Pin':'калибровочного штифта','Fixation Pin':'фиксирующего штифта',
 'Connecting Screw':'соединительного винта','Connecting Screws':'соединительных винтов','Compression Screw':'компрессионного винта',
 'Aiming Arm':'прицельной штанги','Aiming Shaft':'прицельной штанги','Protection Sleeves':'защитных втулок','Protection Sleeve':'защитной втулки',
 'Spiral Blade':'спирального клинка','Extracting Spiral Blade':'удаления спирального клинка','Extracting Blade':'удаления клинка',
 'Inserting Blade':'введения клинка','Impacting Aimstrong Spiral Blade and Lag Screw':'импакции спирального клинка и шеечного винта Aimstrong',
 'Aimstrong Spiral Blade and Lag Screw':'спирального клинка и шеечного винта Aimstrong','Aimstrong Lag Screw Inserter':'инструмента для введения шеечного винта Aimstrong',
 'Aimstrong Lag Screw':'шеечного винта Aimstrong','Aimstrong Lag':'шеечного винта Aimstrong',
 'Dynamic and Static Locking':'динамического и статического блокирования','Locking Bolts':'блокирующих болтов','Locking':'блокирования',
 'Slide Hammer':'скользящего молотка','Cannulated Instruments':'канюлированных инструментов','Anti-rotation Guide Wire':'антиротационной спицы-проводника',
 'Anti-rotation':'предотвращения ротации','Distal End':'дистального отдела','Impactor':'импактора','Tap':'метчика','End Cap':'торцевой заглушки',
 'Screw':'винта','Screws':'винтов','Drill Bit':'сверла','Drill Bits':'свёрл','Cutter':'кусачек','DHS/DCS Wrench':'ключа DHS/DCS',
 'Extraction Screw':'винтового экстрактора','Parallel Wire Guide':'параллельного направителя спиц','Aiming Device':'прицельного устройства',
 'Anteroposterior Interlocking':'переднезаднего блокирования','Extracting Nails':'удаления штифтов','Nail Removal':'удаления штифта',
 'Cancellous Bone':'губчатой кости','the Nail':'штифта','Nail':'штифта','TEN':'титанового эластичного штифта',
 'DHS/DCS Lag Screws':'шеечных винтов DHS/DCS','DHS/DCS Screws':'винтов DHS/DCS','DHSA Blade':'клинка DHSA',
 'Instruments':'инструментов','Blade':'клинка','Outer Protection Sleeve':'наружной защитной втулки',
}
CLINICAL_FAMILIES={
 'Fibular Nail':'малоберцового штифта','Forearm Nail':'штифта костей предплечья','Ulna':'локтевой кости','Radius':'лучевой кости',
 'Tibial Nail':'большеберцового штифта','Humeral Nail':'плечевого штифта','Femoral Nail':'бедренного штифта',
}
GENITIVE.update(CLINICAL_FAMILIES)
for abbr in ['UFN','UTN','RFN','AHN','PFCN','DTN','AFN','SPTN']:GENITIVE[abbr]=abbr
PREPOSITIONS={**{'for '+k:'для '+v for k,v in GENITIVE.items()},
 'with Flat Head':'с плоской головкой','with Hook':'с крючком','with olive head':'с оливообразным наконечником',
 'without olive head':'без оливообразного наконечника','with ball tip':'с шаровидным наконечником','with threaded tip':'с резьбовым наконечником',
 'without Threaded tip':'без резьбового наконечника','with Proximal Diameter':'с проксимальным диаметром',
 'with AO QuickCoupling':'с быстросъёмным соединением AO','with AO Quick Coupling':'с быстросъёмным соединением AO',
 'with T-Handle and Universal Joint':'с T-образной рукояткой и карданным шарниром','with T-Handle':'с T-образной рукояткой',
 'quick coupling':'быстросъёмное соединение','variable angle':'с переменным углом','for neutral and load position':'для нейтрального и компрессионного положения',
 'with Scale':'со шкалой','with Tip':'с наконечником',
}
LEXICAL_MODIFIERS={
 'stardrive':'со звездообразным шлицем','tardrive':'со звездообразным шлицем','starrive':'со звездообразным шлицем',
 'optional':'дополнительная комплектация','multi-holes':'с несколькими отверстиями','oblique':'косой','lateral':'латеральный','anterior':'передний',
 'Outer':'наружный','Head':'головка','Shaft':'стержень','Joint':'шарнир','Soft':'мягкие ткани','Support':'опорный',
 'Headless Compression':'безголовочные компрессионные винты','Sprial Blade':'спиральный клинок','Spiral Blade':'спиральный клинок',
 'Lag Screw':'шеечный винт','End Cap':'торцевая заглушка','Locking Screw':'блокируемый винт','Nail':'штифт',
 'Instruments':'инструменты','Implants':'импланты','Bone':'кость','Caddy':'органайзер','Case':'контейнер','Tray':'лоток','Plate':'пластина','Box':'контейнер',
 'Guide':'направитель','Fixation':'фиксация','Compression':'компрессия','Insertion':'введение','Removal':'удаление',
 'Connecting':'соединительный','Conneting':'соединительный','Depth':'глубина','Cutting':'режущий','Bending':'гибочный',
 'Broken':'сломанный','Sloped':'наклонный','and':'и','for':'для','with':'с','without':'без','the':'',
}

def instrument(en,context=''):
 text=en.strip();text=re.sub(r'forEnd\b','for End',text,flags=re.I)
 # Preserve source article/model identifiers; clinical family prefixes become a grammatical qualifier.
 family=None
 for prefix,genitive in CLINICAL_FAMILIES.items():
  m=re.match(r'^(\*\s*)?'+re.escape(prefix)+r'\s+',text,re.I)
  if m:family=genitive;text=text[m.end():];break
 abbreviations=[]
 while (m:=re.match(r'^(?:\*\s*)?(PFCN|PFNA|AHN|RFN|REN|UFN|UTN|SPTN|SP|DTN|AFN)\s*',text)):
  abbreviations.append(m[1]);text=text[m.end():]
 if re.search(r'\b(?:Case|Box|Caddy)\b',en,re.I):
  original=en.strip(' *«')
  kind='Крышка контейнера'if re.search('Case Cover',original,re.I)else'Органайзер'if re.search('Caddy',original,re.I)else'Контейнер для инструментов'if re.search('Instrument Case',original,re.I)else'Контейнер'
  detail=re.sub(r'\b(?:Instrument Case|Implant Case|Screw Case|Case Cover|Case|Box|Caddy)\b','',original,flags=re.I).strip()
  detail=replace_terms(detail,{**TERMS,'Headless Compression Screw':'Безголовочные компрессионные винты','No Profile Cannulated Screw':'Канюлированные винты без выступающей головки','Cannulated Screw':'Канюлированные винты','Screw':'Винты','Mini Locking':'Мини-фрагментарная блокируемая система','Advanced':'Расширенная комплектация'})
  detail=replace_terms(detail,DETAILS);detail=replace_terms(detail,LEXICAL_MODIFIERS)
  detail=re.sub(r'(?<=\d)\s*mm\b',' мм',detail,flags=re.I);detail=re.sub(r'\s+',' ',detail).strip()
  return {'ru':kind+(' — '+detail if detail else''),'en':en}
 text=re.sub(r'for (Ø?[0-9./]+(?:/Ø?[0-9.]+)*) (Locking Screws|Cortex Screws|Cannulated Screws|Screws|Drill Bits|Guide Wires?)',lambda m:'для '+{'Locking Screws':'блокируемых винтов','Cortex Screws':'кортикальных винтов','Cannulated Screws':'канюлированных винтов','Screws':'винтов','Drill Bits':'свёрл','Guide Wire':'спицы-проводника','Guide Wires':'спиц-проводников'}[m[2].title()]+' '+m[1],text,flags=re.I)
 text=re.sub(r'for (Ø[0-9.]+)( (?:Long )?DTN)',r'для DTN \1',text)
 text=replace_terms(text,PREPOSITIONS)
 text=replace_terms(text,{**INSTRUMENTS,**EXTRA_NOUNS})
 text=replace_terms(text,DETAILS);text=replace_terms(text,LEXICAL_MODIFIERS)
 text=re.sub(r'(?<=\d)\s*mm(?=\b|x)',' мм',text,flags=re.I).replace('N.m','Н·м').replace('Nm','Н·м')
 text=re.sub(r'(?<=\d)x(?=\d)','×',text)
 if family:
  parts=text.split(',',1);text=parts[0]+' для '+family+(','+parts[1]if len(parts)>1 else'')
 if abbreviations:
  parts=text.split(',',1);text=parts[0]+' '+' '.join(abbreviations)+(','+parts[1]if len(parts)>1 else'')
 text=re.sub(r'\s+',' ',text).strip()
 feminine=bool(re.match(r'(?:Направляющая втулка|Сверлильная втулка|Защитная втулка|Фиксирующая втулка|Центрирующая втулка|Удерживающая втулка|Рукоятка|Спица|Отвёртка|Прицельная штанга|Удлинённая прицельная штанга)',text))
 neuter=bool(re.match(r'(?:Сверло|Рассверливающее сверло|Прицельное устройство|Компрессионное устройство)',text))
 if neuter:
  for a,b in {'канюлированная':'канюлированное','цельная':'цельное','гибкое':'гибкое','длинный':'длинное','короткий':'короткое','прямой':'прямое','изогнутый':'изогнутое','левый':'левое','правый':'правое'}.items():text=re.sub(r'\b'+a+r'\b',b,text)
 elif feminine:
  for a,b in {'длинный':'длинная','короткий':'короткая','прямой':'прямая','изогнутый':'изогнутая','гибкое':'гибкая','левый':'левая','правый':'правая','дистальный':'дистальная','проксимальный':'проксимальная','цельная':'цельная'}.items():text=re.sub(r'\b'+a+r'\b',b,text)
 else:text=text.replace('канюлированная','канюлированный').replace('цельная','цельный')
 return {'ru':text[0].upper()+text[1:]if text else'', 'en':en}
TERMS['Universal End Cap for SPTN/AFN']='Универсальная торцевая заглушка SPTN/AFN'

TERMS.update({'Washer for 6.5mm/7.3mm Cannulated Screw':'Шайба для канюлированного винта 6.5/7.3 мм','Spiked Washer for 6.5mm/7.3mm Cannulated Screw':'Шипованная шайба для канюлированного винта 6.5/7.3 мм'})
EXTRA_NOUNS.update({
 'Holding Forceps':'Удерживающие щипцы','Cortex Drill Bit':'Кортикальное сверло','Anti-rotation Handle':'Антиротационная рукоятка',
 'Location Sleeve':'Позиционирующая втулка','Connector Block':'Соединительный блок',
 'Conneting Screw':'Соединительный винт','Positioning Screw Shaft':'Стержень позиционирующего винта',
 'Positioning Reamer':'Позиционирующий ример','Guide Block':'Направляющий блок','Hollow Drill Bit':'Канюлированное сверло',
 'Screw Countersink':'Зенкер для винта','Pliers':'Щипцы',
})
PREPOSITIONS.update({'for inserting Spiral Blade':'для введения спирального клинка','use with Protection Sleeve':'для использования с защитной втулкой',
 'for Proximal Aiming Shaft':'для проксимальной прицельной штанги','for distal locking':'для дистального блокирования',
 'for Distal Femoral Nail':'для дистального бедренного штифта','with Stop':'с ограничителем',
})
LEXICAL_MODIFIERS.update({'hook':'с крючком','Stop':'ограничитель','Block':'блок'})

TERMS.update({'Advanced Proximal Femoral Nail':'Усовершенствованный проксимальный бедренный штифт','Advanced Titanium Elastic Nail':'Усовершенствованный титановый эластичный штифт'})
