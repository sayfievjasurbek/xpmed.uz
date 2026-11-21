"""Codex-reviewed Sports Medicine systems and additive M-Link recipe."""
import hashlib, json, random, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'catalogs-source/double-medical/sports-medicine-catalogue.pdf'
REPORT=ROOT/'reports/double-medical/sports-medicine-catalogue'
OCR=ROOT/'public/catalogs/double-medical/sports-medicine-catalogue/ocr'
ASSETS=json.loads((ROOT/'public/images/products/double-medical/sports-medicine-catalogue/prepared-assets.json').read_text())
EVIDENCE=json.loads((REPORT/'row-evidence.json').read_text())
bi=lambda ru,en:{'ru':ru,'en':en}
def flag(code,page,text):return {'code':code,'pdfPage':page,'sourcePages':[page],'message':bi(text,text)}

# One heading per contents entry. The two Meniscal entries are merged into M-Link.
SYSTEMS=[
 ('metal-suture-anchor',range(4,6),'Металлические шовные якоря Merit','Metal Suture Anchor','sports-suture-anchors',['sports','orthopedics'],'Титановые шовные якоря для фиксации мягких тканей к кости.','Titanium suture anchors for soft-tissue fixation to bone.'),
 ('peek-suture-anchor',range(6,9),'Шовные якоря из PEEK','PEEK Suture Anchor','sports-suture-anchors',['sports','orthopedics'],'Шовные якоря из PEEK для фиксации мягких тканей к кости.','PEEK suture anchors for soft-tissue fixation to bone.'),
 ('g-max-interference-screw',[9],'Интерферентный винт G-Max','G-Max Interference Screw','sports-interference-screws',['sports','orthopedics'],'Интерферентный винт из PEEK.','PEEK interference screw.'),
 ('ac-joint-repair-system',range(11,13),'Система реконструкции акромиально-ключичного сустава','AC Joint Repair System','sports-ac-joint',['sports','orthopedics','traumatology'],'Фиксация при вывихе акромиально-ключичного сустава.','Fixation for acromioclavicular dislocation.'),
 ('knee-repair-and-reconstruction-system',range(13,16),'Система восстановления и реконструкции связок коленного сустава','Knee Repair and Reconstruction System','sports-knee-ligament',['sports','orthopedics'],'Импланты для реконструкции крестообразных связок коленного сустава.','Implants for knee cruciate-ligament reconstruction.'),
 ('knotless-syndesmosis-cfloop-button',[16],'Бесузловая система CFLoop для фиксации синдесмоза','Knotless Syndesmosis CFLoop Button','sports-syndesmosis',['sports','orthopedics','traumatology'],'Пуговичная система для фиксации межберцового синдесмоза.','Button system for tibiofibular syndesmosis fixation.'),
 ('mini-cfloop-adjustable-button',[17],'Мини-пуговица CFLoop с регулируемой петлёй','Mini CFLoop Adjustable Button','sports-syndesmosis',['sports','orthopedics','traumatology'],'Пуговица для реконструкции связок голеностопного и мелких суставов.','Button for ankle and small-joint ligament reconstruction.'),
 ('non-absorbable-surgical-suture-upe',[18],'Нерассасывающийся хирургический шовный материал UPE','Non-absorbable Surgical Suture (UPE)','sports-suture',['sports','orthopedics'],'Шовный материал из сверхвысокомолекулярного полиэтилена.','Ultra-high-molecular-weight polyethylene suture.'),
 ('merit-mpt-suture-anchor-instrument-set',[19],'Набор инструментов для шовных якорей Merit MPT','Merit MPT Suture Anchor Instrument Set','sports-instrument-sets',['sports','orthopedics'],'Инструменты для установки шовных якорей Merit MPT.','Instruments for Merit MPT suture anchors.'),
 ('peek-suture-anchor-instruments',range(20,23),'Инструменты для шовных якорей из PEEK','PEEK Suture Anchor Instruments','sports-instrument-sets',['sports','orthopedics'],'Инструменты для установки шовных якорей из PEEK.','Instruments for PEEK suture anchors.'),
 ('shoulder-repair-and-reconstruction-instrument-set',range(23,25),'Набор инструментов для реконструкции плечевого сустава','Shoulder Repair and Reconstruction Instrument Set','sports-instrument-sets',['sports','orthopedics'],'Инструменты для артроскопической реконструкции плечевого сустава.','Instruments for arthroscopic shoulder reconstruction.'),
 ('arthroscopic-cannula',[25],'Артроскопические канюли','Arthroscopic Cannula','sports-instrument-sets',['sports','orthopedics'],'Артроскопические канюли различных размеров.','Arthroscopic cannulas in multiple sizes.'),
 ('ac-joint-reconstruction-instrument-set',range(26,29),'Набор инструментов для артроскопической реконструкции АКС','AC Joint Reconstruction Instrument Set (Arthroscopy)','sports-instrument-sets',['sports','orthopedics','traumatology'],'Инструменты для артроскопической реконструкции акромиально-ключичного сустава.','Instruments for arthroscopic AC-joint reconstruction.'),
 ('knee-repair-and-reconstruction-instrument-set',range(29,36),'Набор инструментов для реконструкции связок коленного сустава','Knee Repair and Reconstruction Instrument Set','sports-instrument-sets',['sports','orthopedics'],'Инструменты для реконструкции связок коленного сустава.','Instruments for knee-ligament reconstruction.'),
 ('tibiofibular-syndesmosis-instrument-set',[36],'Набор инструментов для фиксации межберцового синдесмоза','Tibiofibular Syndesmosis Instrument Set','sports-instrument-sets',['sports','orthopedics','traumatology'],'Инструменты для фиксации межберцового синдесмоза.','Instruments for tibiofibular syndesmosis fixation.'),
 ('mini-cfloop-adjustable-button-instrument-set',[37],'Набор инструментов для мини-пуговицы CFLoop','Mini CFLoop Adjustable Button Instrument Set','sports-instrument-sets',['sports','orthopedics','traumatology'],'Инструменты для мини-пуговицы CFLoop с регулируемой петлёй.','Instruments for the Mini CFLoop adjustable button.'),
]

RELATED={
 'metal-suture-anchor':['merit-mpt-suture-anchor-instrument-set','shoulder-repair-and-reconstruction-instrument-set'],
 'peek-suture-anchor':['peek-suture-anchor-instruments','shoulder-repair-and-reconstruction-instrument-set'],
 'g-max-interference-screw':['knee-repair-and-reconstruction-instrument-set'],
 'ac-joint-repair-system':['ac-joint-reconstruction-instrument-set'],
 'knee-repair-and-reconstruction-system':['knee-repair-and-reconstruction-instrument-set','m-link-all-inside-meniscal-repair-system'],
 'knotless-syndesmosis-cfloop-button':['tibiofibular-syndesmosis-instrument-set'],
 'mini-cfloop-adjustable-button':['mini-cfloop-adjustable-button-instrument-set'],
 'merit-mpt-suture-anchor-instrument-set':['metal-suture-anchor'],
 'peek-suture-anchor-instruments':['peek-suture-anchor'],
 'shoulder-repair-and-reconstruction-instrument-set':['metal-suture-anchor','peek-suture-anchor','arthroscopic-cannula'],
 'arthroscopic-cannula':['shoulder-repair-and-reconstruction-instrument-set'],
 'ac-joint-reconstruction-instrument-set':['ac-joint-repair-system'],
 'knee-repair-and-reconstruction-instrument-set':['knee-repair-and-reconstruction-system','g-max-interference-screw'],
 'tibiofibular-syndesmosis-instrument-set':['knotless-syndesmosis-cfloop-button'],
 'mini-cfloop-adjustable-button-instrument-set':['mini-cfloop-adjustable-button'],
}

MATERIAL={
 'metal':bi('Титан; сверхвысокомолекулярный полиэтилен (СВМПЭ).','Titanium; ultra-high-molecular-weight polyethylene.'),
 'peek':bi('PEEK; сверхвысокомолекулярный полиэтилен (СВМПЭ).','PEEK; ultra-high-molecular-weight polyethylene.'),
 'gmax':bi('PEEK.','PEEK.'),
 'button':bi('Титан; сверхвысокомолекулярный полиэтилен (СВМПЭ).','Titanium; ultra-high-molecular-weight polyethylene.'),
 'titanium':bi('Титан.','Titanium.'),
 'poly':bi('Сверхвысокомолекулярный полиэтилен (СВМПЭ).','Ultra-high-molecular-weight polyethylene.'),
}
INDICATION={
 'soft':bi('Фиксация мягких тканей, связок и сухожилий к кости.','Fixation of soft tissue, ligaments and tendons to bone.'),
 'ac':bi('Вывих акромиально-ключичного сустава.','Acromioclavicular dislocation.'),
 'ac-fracture':bi('Перелом дистального отдела ключицы в сочетании с вывихом акромиально-ключичного сустава.','Distal clavicular fracture combined with acromioclavicular dislocation.'),
 'knee':bi('Реконструкция крестообразных связок коленного сустава.','Cruciate ligament reconstruction of the knee.'),
 'syndesmosis':bi('Расхождение межберцового синдесмоза.','Separation of the tibiofibular syndesmosis.'),
 'mini':bi('Реконструкция связок голеностопного и мелких суставов.','Reconstruction of ankle or tendons and ligaments in small joints.'),
}

# Page/vertical position boundaries follow the printed product subheadings.
GROUPS={
 4:[(.45,'Merit MPT Suture Anchor','Шовный якорь Merit MPT','metal','soft'),(1,'Merit MFT Suture Anchor','Шовный якорь Merit MFT','metal','soft')],
 5:[(.45,'Merit MAT Suture Anchor','Шовный якорь Merit MAT','metal','soft'),(1,'Merit MDT Suture Anchor','Шовный якорь Merit MDT','metal','soft')],
 6:[(.45,'PEEK SwirlFix Suture Anchor','Шовный якорь PEEK SwirlFix','peek','soft'),(1,'PEEK SwirlLock Suture Anchor','Шовный якорь PEEK SwirlLock','peek','soft')],
 7:[(.45,'PEEK TowerFix Suture Anchor','Шовный якорь PEEK TowerFix','peek','soft'),(1,'PEEK TowerLock Suture Anchor','Шовный якорь PEEK TowerLock','peek','soft')],
 8:[(1,'PEEK Tenodesis Suture Anchor','Тенодезный шовный якорь PEEK','peek','soft')],
 9:[(1,'G-Max Interference Screw','Интерферентный винт G-Max','gmax','soft')],
 11:[(.45,'AC CFLoop Adjustable Button System','Система CFLoop с регулируемой петлёй для АКС','button','ac'),(1,'AC CFLoop Anatomic Button System','Анатомическая пуговичная система CFLoop для АКС','button','ac')],
 12:[(.45,'AC CFLoop Adjustable Button and Plate System','Система CFLoop с регулируемой петлёй и пластиной для АКС','button','ac-fracture'),(1,'AC Butterfly Button','Пуговица AC Butterfly','titanium','ac')],
 13:[(.45,'CFLoop Adjustable Button','Пуговица CFLoop с регулируемой петлёй','button','knee'),(1,'CF Button System','Пуговичная система CF','button','knee')],
 14:[(.45,'Low Profile and Attachable Button','Низкопрофильная присоединяемая пуговица','titanium','knee'),(1,'All-inside and Attachable Button','Пуговица All-inside присоединяемая','titanium','knee')],
 15:[(1,'Loop','Петля','poly',None)],
 16:[(1,'Knotless Syndesmosis CFLoop Button','Бесузловая пуговица CFLoop для синдесмоза','button','syndesmosis')],
 17:[(1,'Mini CFLoop Adjustable Button','Мини-пуговица CFLoop с регулируемой петлёй','button','mini')],
 18:[(1,'Non-absorbable Surgical Suture (UPE)','Нерассасывающийся шовный материал UPE','poly',None)],
}

def group(page,y):
    for i,(limit,en,ru,material,indication) in enumerate(GROUPS[page]):
        if y<limit:return i,bi(ru,en),material,indication
    raise ValueError((page,y))

def normalized_dimension(text):
    text=text.strip()
    text=re.sub(r'(?<=\d)[xX](?=\d)','×',text)
    text=re.sub(r'(?<=\d)\s+x\s+(?=\d)',' × ',text)
    text=re.sub(r'(?<![\dA-Za-z])[O0Ф$](?=\d+(?:\.\d+)?\s*(?:mm|,|\-|$))','Ø',text)
    return re.sub(r'(?<=\d)\s*mm\b',' mm',text)

def rows_for(page):return [r for r in EVIDENCE if r['page']==page]
def vision(page):return json.loads((REPORT/'vision'/f'{page:03}.json').read_text())
def psm(page):return json.loads((OCR/f'{page:03}.json').read_text())['passes']['3']['words']

def source_row(row):
    readings=[{'reader':name,'text':r['raw'],'bounds':r['bounds']}
              for name,r in row['readings'].items()]
    return {'pdfPage':row['page'],'sourceBounds':[.08,max(0,row['y']-.004),.8,min(1,row['y']+.018)],
            'codeEvidence':[{'readings':readings,'visualReading':row.get('visualReading'),
                             'verificationStatus':row['verification'],'verifiedValue':row['code']}]}

def image_for(page,y,all_in_page=False):
    options=[a for a in ASSETS.values() if a['page']==page]
    if not options:return None
    if all_in_page:
        a=max(options,key=lambda x:(x['sourceBounds'][2]-x['sourceBounds'][0])*(x['sourceBounds'][3]-x['sourceBounds'][1]))
    else:
        a=min(options,key=lambda x:abs((x['sourceBounds'][1]+x['sourceBounds'][3])/2-y))
        if abs((a['sourceBounds'][1]+a['sourceBounds'][3])/2-y)>.07:return None
    return {k:a[k] for k in ('src','width','height','imageType','captionFree','imageEnhancement')}

def implant_cells(row):
    page,y=row['page'],row['y']
    ocr=[w for w in psm(page) if abs(w['bounds'][1]-y)<.008]
    vr=[w for w in vision(page) if abs(w['bounds'][1]-y)<.008]
    lo=.18 if page<=10 or page==18 else .28
    hi=.48 if page<=10 or page==18 else .55
    o=' '.join(w['text']for w in ocr if lo<w['bounds'][0]<hi).strip()
    v=' '.join(w['text']for w in vr if lo<w['bounds'][0]<hi and not re.search(r'\d{9}',w['text'])).strip()
    if not v:
        for w in vr:
            if re.search(r'\d{9}',w['text']):
                v=re.sub(r'^\d{9}[S8]?\s*','',w['text']).strip();break
    # Prefer clear independent Vision readings when the PSM3 digit is degraded.
    value=v if v and (not o or re.search(r'(?:99|D8|O10|^45×)',o)) else o or v
    value=normalized_dimension(value)
    if page==4 and row['code']=='150974515S':value='4.5×15'
    if page==13 and row['code']=='157130500S':value='50'
    if page==13 and row['code']=='150110055S':value='55'
    if page==16:value='55'
    if page==18:
        colour=' '.join(w['text']for w in ocr if w['bounds'][0]>.50 and w['bounds'][0]<.80)
        return [value,colour]
    if page<=8:
        suture=' '.join(w['text']for w in ocr if w['bounds'][0]>(.48 if page==8 else .50) and w['bounds'][0]<.70).replace('|','/').replace('xX','×').replace('#€&X','#×')
        suture=re.sub(r'(?<=[#\d])x(?=\d)','×',suture)
        suture=re.sub(r'\s+',' ',suture).strip()
        if page in (4,5) and '/ #' in suture:suture='/ #'
        if page in (6,7) and not re.search(r'\d',suture):suture='/ # × mm'
        return [value,suture]
    return [value]

HEAD_TRANSLATIONS=[
 ('Cannulated Headed Reamer','Канюлированная фреза с головкой'),
 ('Tibial Tunnel Passing Femoral Drill Guide','Бедренный направитель сверла для проведения через большеберцовый канал'),
 ('Femoral ACL Drill Guide','Бедренный направитель сверла для реконструкции ПКС'),
 ('Tibial ACL Drill Guide','Большеберцовый направитель сверла для реконструкции ПКС'),
 ('Tibial PCL Drill Guide','Большеберцовый направитель сверла для реконструкции ЗКС'),
 ('AC Joint Reconstruction Instrument Case','Контейнер для инструментов реконструкции АКС'),
 ('Knee Repair and Reconstruction Instrument Case','Контейнер для инструментов реконструкции связок коленного сустава'),
 ('Merit MPT Suture Anchor Instrument Case','Контейнер для инструментов шовных якорей Merit MPT'),
 ('Ratcheting Drill Sleeve for FlipCutter','Храповая направляющая втулка для FlipCutter'),
 ('PEEK Tenodesis Suture Anchor','тенодезного шовного якоря из PEEK'),
 ('PEEK Interference Screw','интерферентного винта из PEEK'),
 ('Hamstring Tendon Stripper','Стриппер сухожилий задней группы мышц бедра'),
 ('Nitinol Suture Passing Wire','Нитиноловая спица для проведения шовной нити'),
 ('Blunt Tip Obturator','Тупоконечный обтуратор'),
 ('Trocar Tip Obturator','Обтуратор с троакарным наконечником'),
 ('Reusable Obturator','Многоразовый обтуратор'),
 ('Shoulder Tissue Elevator','Элеватор мягких тканей плечевого сустава'),
 ('Suture Tensioning Handles','Рукоятки для натяжения шовной нити'),
 ('Simple Suture Passer','Проводник шовной нити'),
 ('Curving Suture Passer','Изогнутый проводник шовной нити'),
 ('PCL Suture Passer','Проводник шовной нити для ЗКС'),
 ('AC Target Guide','Прицел для акромиально-ключичного сустава'),
 ('AC Drill Guide Assembly','Направитель сверла для АКС в сборе'),
 ('AC Guide','Направитель для АКС'),
 ('Cannulated Reamer','Канюлированная фреза'),
 ('Cannulated Drill Bit','Канюлированное сверло'),
 ('Cannulated Drill','Канюлированное сверло'),
 ('Drill Tip Guide Pin','Направляющая спица со сверлящим наконечником'),
 ('Femoral Guide Drill Sleeve','Бедренная направляющая втулка для сверла'),
 ('Drill Sleeve','Направляющая втулка для сверла'),
 ('Guide Wire Sleeve','Направляющая втулка для спицы'),
 ('Graft Sizing Block','Калибратор трансплантата'),
 ('Side-Release Handle','Рукоятка с боковым высвобождением'),
 ('Knot Pusher/Suture Cutter','Инструмент для продвижения узла и обрезания нити'),
 ('Knot Pusher','Инструмент для продвижения узла'),
 ('Crochet Hook','Крючок'),
 ('Depth Gauge','Глубиномер'),
 ('Hook Probe','Крючковый зонд'),
 ('Meniscus Repair Rasp','Рашпиль для шва мениска'),
 ('FlipCutter Reamer','Фреза FlipCutter'),
 ('ACL Drill Pin','Направляющая спица для реконструкции ПКС'),
 ('Punch/Tap','Пробойник-метчик'),
 ('Punch','Пробойник'),
 ('Drill Bit','Сверло'),
 ('Drill Guide','Направитель сверла'),
 ('Guide Wire','Направляющая спица'),
 ('Drill Pin','Сверлящая спица'),
 ('Screwdriver','Отвёртка'),
 ('Switching Stick','Переключающий стержень'),
 ('Cannula','Канюля'),
 ('Hammer','Молоток'),
 ('Awl','Шило'),
 ('Drill','Сверло'),
 ('Spear','Остроконечный обтуратор'),
]
TAIL_TRANSLATIONS=[
 ('for AC Repair','для реконструкции АКС'),
 ('for MPT Suture Anchor','для шовного якоря MPT'),
 ('for PEEK Tenodesis Suture Anchor','для тенодезного шовного якоря из PEEK'),
 ('for PEEK Interference Screw','для интерферентного винта из PEEK'),
 ('for 7 mm and 8 mm Cannula','для канюль Ø7 и Ø8 мм'),
 ('for 6 mm Cannula','для канюли Ø6 мм'),
 ('for 5.0mm and 5.5mm SwirlLock anchor','для якорей SwirlLock Ø5.0 и Ø5.5 мм'),
 ('for 5.0 mm SwirlLock Anchor','для якоря SwirlLock Ø5.0 мм'),
 ('for 5.5 mm SwirlLock Anchor','для якоря SwirlLock Ø5.5 мм'),
 ('for 3.5 mm SwirlLock Anchor','для якоря SwirlLock Ø3.5 мм'),
 ('for 3.5mm SwirlLock','для SwirlLock Ø3.5 мм'),
 ('for arthroscopy','для артроскопии'),
 ('for FlipCutter','для FlipCutter'),
 ('closed end','с закрытым концом'),
 ('open end','с открытым концом'),
 ('close end','с закрытым концом'),
 ('open eyelet','с открытым ушком'),
 ('with stop','с ограничителем'),
 ('with Stop','с ограничителем'),
 ('footprint','по анатомической зоне прикрепления'),
 ('pin tip','с наконечником-спицей'),
 ('reusable','многоразовый'),
 ('left','левый'),('right','правый'),
 ('length','длина'),('Extra Long','удлинённый'),
 ('tight curve','крутой изгиб'),('curve','изгиб'),
 ('Step','шаг'),('and','и'),('for','для'),
]

def clean_instrument_en(text,page,code):
    text=text.strip().lstrip('—=•.,; ')
    # These terms are plainly printed, while the dimensional glyphs on these
    # source pages are damaged. Do not recover missing dimensions by pattern.
    if page in (20,21):
        if code in ('111036700','111036800'):return ''
        fixes={'nowWerFix':'SwirlFix','mnoWerFix':'SwirlFix','mnowerFix':'SwirlFix','mnoTverFix':'SwirlFix','mnoerFix':'SwirlFix',
               'mnowverFix':'SwirlFix','mnowverLock':'SwirlLock','mnoWverLock':'SwirlLock','Swidkk':'SwirlLock'}
        for a,b in fixes.items():text=text.replace(a,b)
        text=re.sub(r'\s*(?:[.•])\s*mm\s*',' ',text)
        text=re.sub(r'\s*for\s*[. ]*\s*',' for ',text,flags=re.I)
        text=re.sub(r'\s*[.•]\s*',' ',text)
        text=re.sub(r'\b00\s*$','',text)
        text=re.sub(r'\b\w*(?:Se Tip|Sde Tip)\w*\b','Side Tip',text)
        text=re.sub(r'\bapered\b','Tapered',text)
    if page in (35,36):
        text=re.sub(r'\s*[, ]*[bФØ$f]\s*[.v•]*\s*mm','',text)
        text=re.sub(r',?\s*length\s*mm','',text,flags=re.I)
        text=re.sub(r'\s*[.•]\s*',' ',text)
    text=normalized_dimension(text)
    text=re.sub(r'\s+[A-ZА-Я]{3,}.*$','',text) if 'mE ts' in text or 'CTPFEE' in text else text
    text=re.sub(r'\s+[—=()\-]+\s*$','',text)
    text=re.sub(r'\s+',' ',text).strip(' ,;')
    overrides={
      '115013000':'ACL Drill Pin, Ø4 mm, open eyelet',
      '115014700':'Cannulated Drill Bit, Ø6 mm',
      '115010800':'Cannulated Headed Reamer, Ø7 mm',
      '115011000':'Cannulated Headed Reamer, Ø9 mm',
      '115085100':'Cannula, 6×30 mm',
      '115017100':'Cannulated Drill Bit', '115017200':'Cannulated Drill Bit',
      '115017300':'Cannulated Drill Bit', '115017400':'Cannulated Drill Bit',
      '115017500':'Cannulated Headed Reamer','115017600':'Cannulated Headed Reamer',
      '115017700':'Cannulated Headed Reamer','115017800':'Cannulated Headed Reamer',
      '115260100':'Guide Wire','115260200':'Drill Pin, open',
      '115260300':'Drill Sleeve','115260400':'Cannulated Drill Bit',
      '115260500':'Guide Wire Sleeve',
    }
    return overrides.get(code,text)

def translate_instrument(text):
    if not text:return '—'
    if text.startswith('5.1 mm Cannulated Reamer with Stop'):
        return 'Канюлированная фреза Ø5.1 мм с ограничителем'
    t=text
    t=re.sub(r'for\s+Ø?([\d.]+)\s*mm\s+MPT Suture Anchor',r'для шовного якоря Merit MPT Ø\1 мм',t)
    t=re.sub(r'for\s+Ø?([\d.]+)\s*[-–]\s*Ø?([\d.]+)\s*mm\s+MPT Suture Anchor',r'для шовных якорей Merit MPT Ø\1–Ø\2 мм',t)
    for en,ru in TAIL_TRANSLATIONS:t=re.sub(r'(?<!\w)'+re.escape(en)+r'(?!\w)',ru,t)
    for en,ru in HEAD_TRANSLATIONS:t=re.sub(r'(?<!\w)'+re.escape(en)+r'(?!\w)',ru,t)
    t=t.replace('Ø','Ø').replace('mm','мм').replace(' in',' дюймов')
    t=t.replace(', для',' для')
    t=re.sub(r'\s+',' ',t).strip(' ,;')
    return t[:1].upper()+t[1:]

def instrument_description(row):
    page,y,code=row['page'],row['y'],row['code']
    candidates=[]
    for w in vision(page):
        if abs(w['bounds'][1]-y)<.009 and .17<w['bounds'][0]<.88:
            s=re.sub(r'^\d{9}\s*','',w['text']).strip()
            if s and not re.fullmatch(r'\d{9}',s):candidates.append((w['bounds'][0],s))
    candidates.sort();text=' '.join(s for _,s in candidates)
    if not text:
        line=row['readings'].get('PSM3',{}).get('text','')
        text=re.sub(r'^.*?\d{9}\s*','',line).strip()
    return clean_instrument_en(text,page,code)

def implant_tables(pages):
    tables={};flags=[]
    for page in pages:
        for row in rows_for(page):
            code=row['code'];assert code and re.fullmatch(r'\d{9}S',code),(page,code)
            i,title,material,indication=group(page,row['y'])
            key=(page,i)
            if key not in tables:
                text=bi('Материал: '+MATERIAL[material]['ru']+(' Показания: '+INDICATION[indication]['ru'] if indication else ''),
                        'Material: '+MATERIAL[material]['en']+(' Indication: '+INDICATION[indication]['en'] if indication else ''))
                if page<=8:
                    col3=bi('Шовная нить (количество / диаметр)' if page<=5 else 'Шовная нить (количество / спецификация)',
                            'Suture (amount / diameter)' if page<=5 else 'Suture (amount / specification)')
                    cols=[bi('Размер (диаметр × длина)','Size (diameter × length)'),bi('REF','REF'),col3]
                elif page==18:cols=[bi('Размер (диаметр × длина)','Size (diameter × length)'),bi('REF','REF'),bi('Цвет','Colour')]
                else:cols=[bi('Размер','Size'),bi('REF','REF')]
                tables[key]={'id':f'sports-p{page}-{i+1}','groupId':f'sports-p{page}-{i+1}',
                             'title':title,'description':text,'unit':'mm','columns':cols,
                             'rows':[],'rowSources':[],'sourcePages':[page],'rowImages':[],'images':[]}
            t=tables[key]
            values=implant_cells(row)
            assert values[0],(page,code,values)
            local=lambda v:v.replace('mm','мм').replace('blue-white','сине-белый')
            t['rows'].append([bi(local(values[0]),values[0]),code]+[bi(local(v),v) for v in values[1:]])
            t['rowSources'].append(source_row(row))
            t['rowImages'].append(None)
            if page in (4,5) and i==1:
                flags.append(flag('source-incomplete-suture-specification',page,'The source prints an incomplete suture amount/diameter ("/ #") for some anchor rows.'))
            if page in (6,7):
                flags.append(flag('source-incomplete-suture-specification',page,'The source omits numeric suture amount/specification values.'))
    for (page,i),t in tables.items():
        bounds=[0]+[x[0]for x in GROUPS[page]]
        images=[a for a in ASSETS.values() if a['page']==page and bounds[i]<=a['sourceBounds'][1]<bounds[i+1]]
        t['images']=[{**{k:a[k]for k in ('src','width','height','imageType','captionFree','imageEnhancement')},'imageCaption':t['title'],'sourcePages':[page]}for a in images[:2]]
    unique_flags=list({(f['code'],f['pdfPage']):f for f in flags}.values())
    return list(tables.values()),unique_flags

HEADER_PAGES={19,23,26,29,36,37}
def instrument_tables(pages):
    tables={};set_code=None;flags=[]
    for page in pages:
        for row in rows_for(page):
            code=row['code'];assert code and re.fullmatch(r'\d{9}',code),(page,code)
            if page in HEADER_PAGES and row['y']<.15:
                assert set_code is None,(page,code)
                set_code=code
                continue
            group='optional' if page in (28,35) else 'instruments'
            if group not in tables:
                tables[group]={'id':f'sports-{min(pages)}-{group}','groupId':f'sports-{min(pages)}-{group}',
                               'title':bi('Дополнительные инструменты','Optional instruments')if group=='optional'else bi('Инструменты','Instruments'),
                               'columns':[bi('Наименование','Description'),bi('REF','REF')],
                               'rows':[],'rowSources':[],'rowImages':[],'sourcePages':[]}
            t=tables[group]
            en=instrument_description(row)
            if not en:
                flags.append(flag('unreadable-source-description',page,f'Instrument description for {code} is unreadable in the source.'))
                en='—'
            ru=translate_instrument(en)
            t['rows'].append([bi(ru,en),code])
            t['rowSources'].append(source_row(row))
            image=image_for(page,row['y'])
            t['rowImages'].append({**image,'imageCaption':bi(ru,en),'sourcePages':[page]}if image else None)
            if page not in t['sourcePages']:t['sourcePages'].append(page)
            if page in (20,21,35,36):
                flags.append(flag('source-incomplete-instrument-specification',page,
                                  'Some printed instrument dimensions/descriptions are incomplete; no dimensions were inferred.'))
    if set_code:
        assert sum(1 for p in pages for r in rows_for(p)if r['code']==set_code)==1
    return list(tables.values()),set_code,list({(f['code'],f['pdfPage']):f for f in flags}.values())

def make_system(spec):
    slug,pages,ru,en,subcategory,specialty,short_ru,short_en=spec
    pages=list(pages);category='sports-medicine'if pages[0]<=18 else'sports-instrument-sets'
    if category=='sports-medicine':tables,flags=implant_tables(pages);set_code=None
    else:tables,set_code,flags=instrument_tables(pages)
    codes=[r[1]for t in tables for r in t['rows']]
    if set_code:codes=[set_code]+codes
    assert len(codes)==len(set(codes)),(slug,codes)
    artwork=[a for a in ASSETS.values()if a['page']in pages]
    first_page=[a for a in artwork if a['page']==pages[0]]
    preferred=[a for a in first_page if a['imageType']=='cutout']or first_page
    hero=max(preferred,key=lambda a:(a['sourceBounds'][2]-a['sourceBounds'][0])*(a['sourceBounds'][3]-a['sourceBounds'][1]))if preferred else None
    if slug=='knotless-syndesmosis-cfloop-button':hero=ASSETS['page-016-composite']
    gallery=[{**{k:a[k]for k in ('src','width','height','imageType','captionFree','imageEnhancement')},
              'imageCaption':bi(ru,en),'sourcePages':[a['page']]}for a in artwork[:8]]
    indications=None
    if pages[0]<=18:
        selected=[INDICATION[x[4]]for p in pages for x in GROUPS.get(p,[])if x[4]]
        if selected:indications=selected[0]
    s={'slug':slug,'brand':'double-medical','category':category,'subcategory':subcategory,
       'specialty':specialty,'name':bi(ru,en),'shortDescription':bi(short_ru,short_en),
       'description':bi(short_ru+' Таблицы ниже содержат варианты и каталожные номера, приведённые в каталоге Double Medical.',
                        short_en+' The tables below list the variants and catalog numbers printed in the Double Medical catalog.'),
       'heroImage':hero['src']if hero else'','imageType':hero['imageType']if hero else'scene',
       'gallery':gallery,'features':[],'components':[],'specTables':tables,
       'refCodes':codes,'sourcePages':pages,'catalogEdition':None,
       'catalogTitle':bi('Double Medical — каталог спортивной медицины','Double Medical — Sports Medicine Catalogue'),
       'documentCover':'/catalogs/double-medical/sports-medicine-catalogue/pages/001.webp',
       'isNew':False,'status':'draft','catalogType':'list',
       'imageDimensions':{a['src']:{'width':a['width'],'height':a['height']}for a in artwork},
       'relatedSystemSlugs':RELATED.get(slug,[]),'reviewFlags':flags}
    if indications:s['indications']=indications
    if set_code:s.update(setCode=set_code,setCodes=[set_code],instrumentSet=True,
                         setCodeEvidence=source_row(next(r for r in rows_for(pages[0])if r['code']==set_code)))
    return s

def prepare_merge():
    old=json.loads((ROOT/'content/products/double-medical/m-link-all-inside-meniscal-repair-system.json').read_text())
    assert old['status']=='published'
    old_codes=set(old['refCodes'])
    assert '151260000S'in old_codes and {'114301300','114301400','115012500'}<=old_codes
    assert '114301200'not in old_codes and '114302000'not in old_codes
    by_code={r['code']:r for r in rows_for(38)}
    assert {'114302000','114301200'}<=set(by_code)
    new=by_code['114301200'];image=image_for(38,new['y'])
    t={'id':'sports-medicine-m-link-added-instrument','title':bi('Дополнение к набору инструментов M-Link','M-Link instrument-set supplement'),
       'columns':[bi('Наименование','Description'),bi('REF','REF')],
       'rows':[[bi('Набор инструментов для шва мениска','Meniscal Repair System Instrument Set'),'114302000'],
               [bi('Инструмент для продвижения узла и обрезания нити, многоразовый','Knot Pusher/Suture Cutter, reusable'),'114301200']],
       'rowSources':[source_row(by_code['114302000']),source_row(new)],'rowImages':[None,{**image,'imageCaption':bi('Инструмент для продвижения узла и обрезания нити','Knot Pusher/Suture Cutter'),'sourcePages':[38]}if image else None],
       'sourcePages':[38]}
    return {'slug':old['slug'],'brand':'double-medical','name':old['name'],
            'sourcePages':[10,38],'referenceTables':[t],
            'refCodes':['114302000','114301200'],
            'relatedSystemSlugs':['knee-repair-and-reconstruction-system'],
            'gallery':[{**image,'imageCaption':bi('Инструмент для продвижения узла и обрезания нити','Knot Pusher/Suture Cutter'),'sourcePages':[38]}]if image else[],
            'imageDimensions':{image['src']:{'width':image['width'],'height':image['height']}}if image else{},
            'matchedBy':'REF 151260000S and Meniscal Repair System title'}

def run():
    for row in EVIDENCE:
        if row['page']==36 and row['code']=='115260300':
            assert row['normalizedReadings']=={'Vision':'115260300','PSM11':'115260300'}
            row['visualReading']='115260300'
            row['verification']='verified (visual + PSM11 + Vision)'
        assert row['code'] and row['verification'].startswith('verified'),(row['page'],row['y'])
    systems=[make_system(s)for s in SYSTEMS]
    merge=prepare_merge()
    existing={}
    for file in (ROOT/'content/products').glob('*/*.json'):
        data=json.loads(file.read_text())
        for code in data.get('refCodes',[]):existing.setdefault(code,[]).append(data['brand']+'/'+data['slug'])
    overlaps=[]
    for system in systems:
        for code in system['refCodes']:
            if code in existing:overlaps.append({'system':system['slug'],'REF':code,'existingSystems':existing[code]})
    assert len(systems)==16 and len(merge['refCodes'])==2
    profile={'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
             'layoutReviewed':True,'reportSlug':'sports-medicine-catalogue',
             'method':'600-DPI PSM3/PSM11 + independent Apple Vision; Codex visual source review and professional medical RU; Real-ESRGAN exact 2x and rembg/source-alpha preservation',
             'authorizedPhysicalPages':list(range(4,39)),
             'nonProductPages':[1,2,3,39,40],
             'systems':systems,'merges':[merge],
             'assets':list(ASSETS.values()),
             'catalogTitle':bi('Double Medical — каталог спортивной медицины','Double Medical — Sports Medicine Catalogue'),
             'existingMatchAudit':overlaps}
    out=ROOT/'scripts/profiles/double-medical-sports-medicine.json'
    out.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
    (REPORT/'overlaps.json').write_text(json.dumps(overlaps,ensure_ascii=False,indent=2)+'\n')
    (REPORT/'code-verification.json').write_text(json.dumps(EVIDENCE,ensure_ascii=False,indent=2)+'\n')
    print('systems',len(systems),'merge',merge['slug'],'REF occurrences',len(EVIDENCE),'overlaps',len(overlaps),'open flags',sum(len(s['reviewFlags'])for s in systems))

if __name__=='__main__':run()


