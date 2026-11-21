#!/usr/bin/env python3
"""Propose source tables using official text only where geometrically corroborated by supplied 600-DPI OCR."""
import json,re,sys,math
from pathlib import Path
from collections import defaultdict,Counter
import pymupdf as fitz,numpy as np,cv2
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/arthroscopy-product-catalog';D=fitz.open(F/'official/arthroscopy-catalog.pdf');maps=json.loads((F/'page-mapping.json').read_text());out=F/'layout';out.mkdir(exist_ok=True)
# Physical source headings, reviewed from every section's page overview.
sections=[('shoulder-arthroscopy','Shoulder Arthroscopy','Артроскопия плечевого сустава',9,27),('knee-arthroscopy','Knee Arthroscopy','Артроскопия коленного сустава',29,50),('hip-arthroscopy','Hip Arthroscopy','Артроскопия тазобедренного сустава',52,59),('small-joint-arthroscopy','Small Joint Arthroscopy','Артроскопия мелких суставов',61,67),('arthroscopy-manual-instruments','Arthroscopy Manual Instruments','Ручные артроскопические инструменты',69,86),('arthroscopy-resection','Resection Products','Резекция (шейверы, боры, консоли)',88,104),('arthroscopy-fluid-management','Fluid Management','Управление жидкостью (помпы)',106,109),('arthroscopy-electrosurgery','ESA Electrosurgical Arthroscopy','Электрохирургическая артроскопия',111,112)]
titles={}
for start,end,title,ru in[(9,15,'Rotator Cuff Repair','Восстановление вращательной манжеты'),(16,17,'Instability Repair','Стабилизация плечевого сустава'),(18,18,'Biceps Tenodesis','Тенодез длинной головки бицепса'),(19,21,'Suture Passing','Проведение шовного материала'),(22,22,'MASTER Arthroscopy Shoulder Instrument Set','Набор артроскопических инструментов MASTER для плечевого сустава'),(23,23,'Hi-Fi Suture','Шовный материал Hi-Fi'),(24,25,'Cannula Systems','Системы канюль'),(26,26,'Positioning Devices','Устройства для позиционирования'),(27,27,'Arthroscopic Accessories','Принадлежности для артроскопии'),(29,29,'Biocomposite Interference Screws','Биокомпозитные интерференционные винты'),(30,32,'Bioabsorbable Interference Screws','Биорезорбируемые интерференционные винты'),(33,33,'Femoral Fixation Implants','Имплантаты для бедренной фиксации'),(34,35,'Cruciate Reconstruction System','Система реконструкции крестообразных связок'),(36,41,'Cruciate Reconstruction Accessories','Принадлежности для реконструкции крестообразных связок'),(42,42,'Graft Preparation System','Система подготовки трансплантата'),(43,45,'Reamer Systems','Системы канюлированных развёрток'),(46,46,'OCD Repair','Лечение рассекающего остеохондрита'),(47,47,'Meniscal Fixation Implants','Имплантаты для фиксации мениска'),(48,48,'Meniscal Fixation Systems','Системы фиксации мениска'),(49,49,'Sterilization Trays','Лотки для стерилизации'),(50,50,'Positioning Devices','Устройства для позиционирования'),(52,52,'Bridge System','Системы мостов'),(53,53,'Hip Access','Доступ к тазобедренному суставу'),(54,54,'Shutt Series 210 Manual Instruments','Ручные инструменты Shutt Series 210'),(55,55,'Hip Blades and Burs','Шейверные насадки и боры для тазобедренного сустава'),(56,56,'Hip Manual Instruments','Ручные инструменты для тазобедренного сустава'),(57,57,'Hip Suture Passers','Проводники шовного материала для тазобедренного сустава'),(58,58,'Anchors','Якорные фиксаторы'),(59,59,'Suction Ablator and Tray','Аспирационный аблятор и лоток'),(61,62,'Small Joint Forceps and Graspers','Кусачки и захваты для мелких суставов'),(63,63,'Small Joint Instrument Sets and Case','Наборы инструментов и контейнер для мелких суставов'),(64,64,'Small Joint Probes, Curettes and Dissectors','Зонды, кюретки и диссекторы для мелких суставов'),(65,65,'Small Joint Arthroscopy Knives, Tubing and Cannula Set','Ножи, трубки и набор канюль для артроскопии мелких суставов'),(66,66,'Carpal Tunnel Release Kit','Набор для релиза карпального канала'),(67,67,'Anchors','Якорные фиксаторы'),(69,69,'Shutt Manual Instruments','Ручные инструменты Shutt'),(70,74,'Shutt','Ручные инструменты Shutt'),(75,75,'Shutt Instrument Sets','Наборы инструментов Shutt'),(76,82,'Concept','Ручные инструменты Concept'),(83,83,'MASTER Arthroscopy Shoulder Instrument Set','Набор артроскопических инструментов MASTER для плечевого сустава'),(84,84,'Shutt Small Joint','Инструменты Shutt для мелких суставов'),(85,85,'Shutt Small Joint Sets','Наборы Shutt для мелких суставов'),(86,86,'Accessories','Принадлежности для ручных инструментов'),(88,88,'Consoles','Консоли'),(89,89,'Footswitches and Accessories','Педали и принадлежности'),(90,90,'Handpieces','Наконечники'),(91,92,'Hip Blades and Burs','Шейверные насадки и боры для тазобедренного сустава'),(93,97,'Large Hub Shaver Blades','Шейверные насадки с большим разъёмом'),(98,100,'Large Hub Burs and Routers','Боры и фрезы с большим разъёмом'),(101,103,'Micro Hub Blades','Шейверные насадки с микроразъёмом'),(104,104,'Micro Hub Burs and Routers','Боры и фрезы с микроразъёмом'),(106,107,'24k Pump System','Помповая система 24k'),(108,108,'10k Fluid System','Система управления жидкостью 10k'),(109,109,'Gravity Tubing and Suction Devices','Трубки для гравитационной подачи и аспирационные устройства'),(111,111,'Edge Bipolar Arthroscopic Radiofrequency System','Биполярная артроскопическая радиочастотная система Edge'),(112,112,'LightWave Ablators','Абляторы LightWave')]:
 for n in range(start,end+1):titles[n]={'en':title,'ru':ru}
(F/'sections.json').write_text(json.dumps({'sections':sections,'titles':titles},ensure_ascii=False,indent=2)+'\n')
def clean(s):return re.sub(r'\s+',' ',s.replace('\x07','').replace('\t',' ')).strip()
def norm(s):return re.sub('[^a-z0-9-]','',s.lower())
def official_lines(page):
 rows=[]
 for b in page.get_text('rawdict')['blocks']:
  if b['type']!=0:continue
  for l in b['lines']:
   chars=[c for s in l['spans']for c in s['chars']];text=''.join(c['c']for c in chars);sizes=[s['size']for s in l['spans']];fonts=[s['font']for s in l['spans']]
   if not clean(text):continue
   rows.append({'text':clean(text),'rawText':text,'chars':chars,'bbox':list(l['bbox']),'size':max(sizes),'font':fonts[0],'bold':any('Bd'in font for font in fonts)})
 return rows
for m in maps:
 n=m['pdfPage'];pn=m['officialPage'];e=json.loads((R/f'public/catalogs/conmed/arthroscopy-product-catalog/ocr/{n:03}.json').read_text())
 # Exact source title breaks ties where a partial product group is repeated in Accessories.
 if n==64:pn=84
 if n==26:pn=34
 if n==77:pn=103
 page=D[pn-1];pw,ph=page.rect.width,page.rect.height;lines=official_lines(page)
 ow=defaultdict(list);sw=defaultdict(list)
 for w in page.get_text('words'):
  if .11<w[1]/ph<.9:ow[norm(w[4])].append([(w[0]+w[2])/2/pw,(w[1]+w[3])/2/ph])
 for w in e['passes']['11']['words']:
  if .1<w['bounds'][1]<.91:sw[norm(w['text'])].append([(w['bounds'][0]+w['bounds'][2])/2,(w['bounds'][1]+w['bounds'][3])/2])
 src=[];dst=[]
 for key in ow.keys()&sw.keys():
  if len(key)>=4 and len(ow[key])==len(sw[key])==1:src.append(ow[key][0]);dst.append(sw[key][0])
 M,inliers=cv2.estimateAffine2D(np.array(src)*1000,np.array(dst)*1000,ransacReprojThreshold=8)if len(src)>=4 else(None,None)
 if M is None:M=np.array([[1,0,0],[0,1,0]],float)
 M[:,2]/=1000
 def box(b):
  corners=np.array([[b[0]/pw,b[1]/ph,1],[b[2]/pw,b[3]/ph,1]]);v=corners@M.T;return [float(v[0,0]),float(v[0,1]),float(v[1,0]),float(v[1,1])]
 def is_content(l):return .11<l['bbox'][1]/ph<.93 and l['size']>=6
 content=[l for l in lines if is_content(l)];merged=[]
 for line in sorted(content,key=lambda l:(round(l['bbox'][1],1),l['bbox'][0])):
  found=next((a for a in merged[-6:]if abs(a['bbox'][1]-line['bbox'][1])<.7 and abs(a['size']-line['size'])<.5 and 0<=line['bbox'][0]-a['bbox'][2]<8),None)
  if found:
   found['rawText']+=line['rawText'];found['text']=clean(found['rawText']);found['chars']+=line['chars'];found['bbox']=[min(found['bbox'][0],line['bbox'][0]),min(found['bbox'][1],line['bbox'][1]),max(found['bbox'][2],line['bbox'][2]),max(found['bbox'][3],line['bbox'][3])]
  else:merged.append(line)
 content=merged;groups=[];unparsed=[]
 # Read each table column top-to-bottom. Each dotted line terminates a source item row.
 for side in [0,1]:
  relevant=[l for l in content if (l['bbox'][0]/pw<.35)==(side==0)];relevant.sort(key=lambda l:(round(l['bbox'][1],1),l['bbox'][0]))
  current={'title':titles[n]['en'],'page':n,'officialPage':pn,'headingBounds':[.08,.12,.92,.15],'rows':[],'features':[],'notes':[],'keyParameters':[]};prefix=[];pending=[];context=[];cat_headers=[];parent_title='';parent_features=[];parent_notes=[]
  for l in relevant:
   text=l['text'];dotted=re.search(r'[.…]{3,}(?:[ .…]*[.…])?',l['rawText']);is_heading=l['bold']and l['size']>=8.5 and not dotted and 'Cat.'not in text and not text.startswith(('All products','Customer'))
   if is_heading:
    if current and current['rows']:groups.append(current)
    if l['size']>=9.8:
     parent_title=text;parent_features=[];parent_notes=[]
    elif current and not current['rows']:
     parent_features=current['features'];parent_notes=current['notes']
    title=(parent_title+' — '+text)if parent_title and parent_title!=text else text
    current={'title':title,'page':n,'officialPage':pn,'headingBounds':box(l['bbox']),'rows':[],'features':list(parent_features),'notes':list(parent_notes),'keyParameters':[]};prefix=[];pending=[];continue
   if not current:continue
   if text.startswith('Cat. No'):cat_headers.append(l);continue
   if dotted:
    raw=l['rawText'];parts=list(re.finditer(r'[.…]{3,}(?:[ .…]*[.…])?',raw));description=clean(raw[:parts[0].start()]);codes=[]
    for j,match in enumerate(parts):
     stop=parts[j+1].start()if j+1<len(parts)else len(raw);segment=raw[match.end():stop].strip(' .\t');code=segment.split()[0]if segment else''
     code=code.strip('.,;')
     if not code:continue
     start=raw.find(code,match.end());chars=l['chars'][start:start+len(code)];b=[min(c['bbox'][0]for c in chars),min(c['bbox'][1]for c in chars),max(c['bbox'][2]for c in chars),max(c['bbox'][3]for c in chars)]
     codes.append({'candidate':code,'sourceBounds':box(b),'officialBounds':b,'officialCode':code})
    # Only same-style immediately preceding continuation lines belong to this item.
    
    if prefix and l['bbox'][1]-prefix_bottom>5:current['notes'].append(clean(' '.join(prefix)));prefix=[]
    desc=clean(' '.join(prefix+[description]));top=prefix_top if prefix else l['bbox'][1];prefix=[]
    current['rows'].append({'description':desc,'codes':codes,'rowBounds':box([l['bbox'][0],top,max(l['bbox'][2],l['bbox'][0]+30),l['bbox'][3]]),'pdfPage':n,'officialPage':pn});continue
   if l['size']>=9.8:
    if text.startswith('»'):
     current['features'].append({'text':text.lstrip('» '),'bounds':box(l['bbox']),'officialStartX':l['bbox'][0]})
    elif current['features']and l['bbox'][1]-pending_y<15 if 'pending_y'in locals()else False:
     current['features'][-1]['text']+=' '+text
    else:current['notes'].append(text)
    pending_y=l['bbox'][3];continue
   if l['size']>=8.4 and not l['bold']and not re.fullmatch(r'[\s.]+',text):
    if prefix and l['bbox'][1]-prefix_bottom>5:current['notes'].append(clean(' '.join(prefix)));prefix=[]
    if not prefix:prefix_top=l['bbox'][1]
    prefix.append(text);prefix_bottom=l['bbox'][3]
   elif text and len(text)>5:current['notes'].append(text)
  if current and (current['rows']or n==69 and current['notes']):groups.append(current)
 
 if n==89:
  for g in groups:g['rows']=[r for r in g['rows']if r['description'] not in ['ZEN® Wireless 3-Pedal Footswitch','Wireless Adapter for ZEN','2-Pedal Footswitch']]
 if n==109:groups=[g for g in groups if 'PuddleVac' in g['title']]
 record={'pdfPage':n,'officialPage':pn,'alignment':M.tolist(),'alignmentMatches':len(src),'alignmentInliers':int(inliers.sum())if inliers is not None else 0,'category':next(s[0]for s in sections if s[3]<=n<=s[4]),'title':titles[n],'groups':groups,'dottedRows':sum(len(g['rows'])for g in groups)}
 (out/f'{n:03}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(n,pn,len(groups),record['dottedRows'],flush=True)
