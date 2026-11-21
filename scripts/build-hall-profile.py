"""Source-positioned HALL recipe. No uncorroborated number is silently repaired."""
import json,re,hashlib,collections,sys,io
from pathlib import Path
import pymupdf as fitz
import numpy as np
from PIL import Image,ImageChops
from hall_sections import SECTIONS,MATRIX_BLADES,ROW_BLADES,BUR_MATRICES
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';P=R/'catalogs-source/conmed/hall-powered-instruments.pdf';D=fitz.open(P);O=R/'public/images/products/conmed/hall';(O/'drawings').mkdir(parents=True,exist_ok=True)
def bi(ru,en=None):return {'ru':str(ru),'en':str(ru if en is None else en)}
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
V=json.loads((F/'verification.json').read_text());records=[r for r in V['records']if not r.get('excludedReason')];byid={r['id']:r for r in records};layouts={n:json.loads((F/'layout'/f'{n:03}.json').read_text())for n in range(8,79)};assets=json.loads((O/'prepared-assets.json').read_text())if(O/'prepared-assets.json').exists()else{};numeric=[];assigned=[];unknown=set();drawmeta={}
TRANSLATIONS={
'Cat. No.':'Кат. №','Width':'Ширина','Body Width':'Ширина тела','Head Width':'Ширина головки','Length':'Длина','Depth Stop':'Ограничитель глубины','Material Thickness':'Толщина материала','Cut Thickness':'Толщина пропила','Thickness':'Толщина','Tooth':'Зубья','Edge':'Кромка','Shank':'Хвостовик','Non-sterile':'Нестерильное изделие','Sterile':'Стерильное изделие','Flutes':'Режущие грани','Diameter':'Диаметр','Bur Head Length':'Длина рабочей головки бора','Working Length':'Рабочая длина','Compatible Bur Guard':'Совместимый защитный тубус','Fine':'Мелкие','Coarse':'Крупные','Straight':'Прямая','Curved':'Изогнутая','Round':'Круглый','Flat':'Плоский','Round Fluted':'Шаровидные боры с режущими гранями','Fine Round Diamond':'Шаровидные боры с мелкозернистым алмазным покрытием','Coarse Round Diamond':'Шаровидные боры с крупнозернистым алмазным покрытием','Straight Side Cutting Burs':'Прямые боры с боковым резанием','Side Cutting Burs':'Боры с боковым резанием','Lindemann Burs':'Боры Линдеманна','Cylindrical':'Цилиндрические боры','Fine Diamond Cylindrical Burs':'Цилиндрические боры с мелкозернистым алмазным покрытием','Wire Pass Burs':'Боры для проведения проволоки','Wirepass burs':'Боры для проведения проволоки','Oval Fluted Burs':'Овальные боры с режущими гранями','Oval Diamond Burs':'Овальные алмазные боры','Round Diamond':'Шаровидные алмазные боры','L50 Round Fluted':'Шаровидные боры L50 с режущими гранями','Fine Diamond':'Мелкозернистое алмазное покрытие','Coarse Diamond':'Крупнозернистое алмазное покрытие','Fluted Round Burs':'Шаровидные боры с режущими гранями','Graft Harvesting Blades':'Лезвия для забора трансплантата','Sagittal Saw Blades':'Лезвия для сагиттальных пил','Oscillating Saw Blades':'Лезвия для осциллирующих пил','Reciprocating Rasp':'Реципрокный рашпиль','Reciprocating Saw Blades':'Лезвия для реципрокных пил','Sternum Saw Blades':'Лезвия для стернальных пил','Repeat Sternotomy Blades':'Лезвия для повторной стернотомии','Handpieces':'Наконечники','Attachments & Accessories':'Насадки и принадлежности','Attachments':'Насадки','Miscellaneous Attachments':'Прочие насадки','Drill-Ream 1:1/5:1 Combination Attachments':'Комбинированные насадки для сверления и рассверливания 1:1/5:1','1:1 Multipurpose Attachments':'Многофункциональные насадки 1:1','1:1 Quick Connect Drill Attachments':'Быстросъёмные сверлильные насадки 1:1','3:1 Reamers':'Римеры 3:1','5:1 Reamers':'Римеры 5:1','1-Trigger Wire and Pin Drivers':'Однокурковые драйверы для спиц и штифтов','2-Trigger Wire and Pin Drivers':'Двухкурковые драйверы для спиц и штифтов'}
PHRASES=[('Sternum Guard','Ограничитель стернальной пилы'),('Sternum Saw Wrench','Ключ стернальной пилы'),('Hall Titan 2-Trigger Modular Drill','Двухкурковая модульная дрель Hall Titan'),('Hall Titan Reciprocating Saw','Реципрокная пила Hall Titan'),('Hall Titan Sternum Saw','Стернальная пила Hall Titan'),('Hall Titan Oscillating','Осциллирующая пила Hall Titan'),('PowerPro Electric II 1-Trigger Modular Handpiece','Однокурковый модульный наконечник PowerPro Electric II'),('PowerPro Pneumatic Single Trigger Modular Handpiece','Однокурковый пневматический модульный наконечник PowerPro'),('PowerPro Electric II Oscillating Saw','Осциллирующая пила PowerPro Electric II'),('PowerPro Electric II Reciprocating Saw','Реципрокная пила PowerPro Electric II'),('PowerPro Pneumatic Oscillating Saw','Пневматическая осциллирующая пила PowerPro'),('PowerPro Pneumatic Reciprocating Saw','Пневматическая реципрокная пила PowerPro'),('Wire Driver','Драйвер для спиц'),('Pin Driver','Драйвер для штифтов'),('Drill-Ream Attachment','Насадка для сверления и рассверливания'),('Jacobs Chuck','Патрон Jacobs'),('Keyless Chuck','Бесключевой патрон'),('Chuck Key','Ключ патрона'),('Replacement Chuck','Сменный патрон'),('High Torque','С высоким крутящим моментом'),('Hudson Reamer','Ример Hudson'),('Zimmer/Hudson Reamer','Ример Zimmer/Hudson'),('Large AO Reamer','Большой ример AO'),('Aesculap Reamer','Ример Aesculap'),('DHS Reamer','Ример DHS'),('Trinkle Reamer','Ример Trinkle'),('Radiolucent Drive Adaptor','Рентгенопрозрачный приводной адаптер'),('High Speed Drill Attachment','Высокоскоростная сверлильная насадка'),('Sagittal Saw Attachment','Насадка сагиттальной пилы'),('Reciprocating Saw Attachment','Насадка реципрокной пилы'),('Multipurpose High Speed','Многофункциональная высокоскоростная насадка'),('Quick Connect Drill Attachment','Быстросъёмная сверлильная насадка'),('Small AO','Малая AO'),('Large AO','Большая AO'),('Mini AO','Мини-AO'),('Low Profile','Низкопрофильная'),('One Handed Operation','Управление одной рукой'),('Standard Hudson (DePuy)','Стандартная Hudson (DePuy)'),('Lithium Power Unit','Литиевый блок питания'),('Power Unit Adapter','Адаптер блока питания'),('Lithium Charger','Зарядное устройство для литиевых аккумуляторов'),('Large Lithium Battery','Большой литиевый аккумулятор'),('Medium Speed Drill','Среднескоростная дрель'),('High Speed Drill','Высокоскоростная дрель'),('Orthopedic','Ортопедическая'),('Removable Lever','Съёмный рычаг'),('Medium Precision Bur Guard','Средний прецизионный защитный тубус бора'),('Long Precision Bur Guard','Длинный прецизионный защитный тубус бора'),('X-Long Precision Bur Guard','Удлинённый прецизионный защитный тубус бора'),('Medium Bur Guard','Средний защитный тубус бора'),('Long Bur Guard','Длинный защитный тубус бора'),('X-Long Bur Guard','Удлинённый защитный тубус бора'),('Short Neuro Guard','Короткий нейрохирургический защитный тубус'),('Medium Neuro Guard','Средний нейрохирургический защитный тубус'),('Long Neuro Guard','Длинный нейрохирургический защитный тубус'),('Cranial Perforator Drive','Привод краниального перфоратора'),('Irrigation Tubing Set','Набор ирригационных трубок'),('Drill Tubing','Трубка для дрели'),('without irrigation','без ирригации'),('with irrigation','с ирригацией'),('Standard Sterilization Case','Стандартный стерилизационный контейнер'),('Rigid Sterilization Container','Жёсткий стерилизационный контейнер'),('Inner Tray','Внутренний лоток'),('Full Set','Полный набор'),('Drill Set with Mini-Driver','Набор для дрели с мини-драйвером'),('Drill Set','Набор для дрели'),('Saw Set','Набор для пилы'),('Large Bone Tray with Battery Holders','Лоток для хирургии крупных костей с держателями аккумуляторов'),('3-Pedal Footswitch','Трёхпедальный ножной переключатель'),('Handpiece Cord','Кабель наконечника'),('Console with Irrigation','Консоль с ирригацией'),('Console','Консоль'),('Saw','Пила'),('with','с'),('for','для'),('and','и'),('Volt','В'),('Size','размера')]
# Longest phrases first avoids splitting a recognized medical term.
PHRASES.sort(key=lambda a:-len(a[0]))
def trans(text):
 text=re.sub(r'\s+',' ',text).strip();base=re.sub(r'\s*\((?:mm|mm\))\)?','',text,flags=re.I).strip()
 if text in TRANSLATIONS:return bi(TRANSLATIONS[text],text)
 ru=text
 for a,b in PHRASES:ru=re.sub(r'(?<![A-Za-z])'+re.escape(a)+r'(?![A-Za-z])',lambda m:b,ru,flags=re.I)
 ru=re.sub(r'\bmm\b','мм',ru);ru=re.sub(r'\bcm\b','см',ru)
 if ru==text and re.search(r'[a-z]{3}',text)and not re.search(r'^(?:HALL|Hall|PowerPro|MicroPower|MicroFree|UltraPower|Osteon|E\d)',text):unknown.add(text)
 return bi(ru,text)
def textcell(c,n):
 reads={k:re.sub(r'\s+',' ',v).strip(' |')for k,v in c['texts'].items()};official=re.sub(r'\s+',' ',c['officialText']).strip(' |');values=collections.Counter(v for v in reads.values()if v)
 # Official text is used only when independently present in the supplied source crop.
 value=official if official and official in values else values.most_common(1)[0][0]if values else''
 nonempty=any(reads.values());verified=not value or sum(v==value for v in reads.values())>=2 or(value==official and value in reads.values())
 ident=f'{n}-'+','.join(f'{x:.5f}'for x in c['bounds']);reviewed=json.loads((F/'numeric-visual-readings.json').read_text())if(F/'numeric-visual-readings.json').exists()else{}
 if ident in reviewed:value=reviewed[ident];verified=True;reads['Codex visual 600-DPI crop']=value
 numeric.append({'id':ident,'pdfPage':n,'bounds':c['bounds'],'value':value,'readings':reads,'official':official,'verified':verified,'sourceBlank':not nonempty})
 return value,ident,verified

def crop(n,b,name,unblue=False):
 name=name+'-'+hashlib.sha256(json.dumps(b).encode()).hexdigest()[:8];path=O/'drawings'/(name+'.webp')
 if not path.exists():
  p=D[n-1];rect=fitz.Rect(b[0]*p.rect.width,b[1]*p.rect.height,b[2]*p.rect.width,b[3]*p.rect.height);pix=p.get_pixmap(matrix=fitz.Matrix(600/72,600/72),clip=rect,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  if unblue:
   ar=np.asarray(im).copy();blue=(ar[:,:,2].astype(int)-ar[:,:,0]>5)&(ar.min(axis=2)>170);ar[blue]=255;im=Image.fromarray(ar)
  ar=np.asarray(im);mask=Image.fromarray((ar.min(axis=2)<225).astype('uint8')*255);box=mask.getbbox()
  if box:im=im.crop(box)
  canvas=Image.new('RGB',(im.width+32,im.height+32),'white');canvas.paste(im,(16,16));canvas.save(path,lossless=True)
 else:canvas=Image.open(path)
 a={'src':'/images/products/conmed/hall/drawings/'+name+'.webp','width':canvas.width,'height':canvas.height,'imageType':'scene','pdfPage':n,'bounds':b,'drawing':True,'backgroundRemoval':'not applied: source line art preserved','captionFree':True}
 drawmeta[a['src']]=a;return a

def evidence(r,table,row):return {**{k:v for k,v in r.items()if k not in ['lineCrop','candidate','value']},'tableId':table,'row':row,'column':2,'value':r['value']}
def addflag(s,code,n,path,readings,ru,en):
 if any(f.get('path')==path and f['code']==code for f in s['reviewFlags']):return
 s['reviewFlags'].append({'code':code,'status':'open','pdfPage':n,'path':path,'readings':readings,'message':bi(ru,en)})
def addrow(s,t,r,desc,values,dim=None,drawing=None):
 idx=len(t['rows']);t['rows'].append([desc,r['value'],*values]);t['rowSources'].append({'pdfPage':r['pdfPage'],'bounds':r['sourceBounds'],'codeEvidence':[evidence(r,t['id'],idx+1)]});t.setdefault('rowDimensions',[]).append(dim or{});t.setdefault('rowImages',[]).append(drawing);assigned.append(r['id'])
 if r['value']:s['refCodes'].append(r['value'])
 else:addflag(s,'unverified-code',r['pdfPage'],f'specTables.{len(s["specTables"])}.rows.{idx}.1',[x['text']for x in r['readings']],'Не подтверждён каталожный номер.','Catalog number is unverified.')
def table(name,id,cols,n):return {'id':id,'groupId':id,'title':name,'columns':[bi('Наименование','Description'),bi('Кат. №','Cat. No.'),*cols],'rows':[],'rowSources':[],'sourcePages':[n],'unit':'mm','images':[]}
def coating(a):
 im=Image.open(R/'public'/a['src'].lstrip('/')).convert('RGB');ar=np.asarray(im);neutral=(ar.max(axis=2)-ar.min(axis=2)<15);gray=neutral&(ar.mean(axis=2)>60)&(ar.mean(axis=2)<230);fraction=float(gray.mean());return fraction>.12,fraction
systems=[]
for slug,en,ru,pages,specialties,indEn,indRu in SECTIONS:
 s={'schemaVersion':1,'slug':slug,'brand':'conmed','brandName':bi('CONMED'),'category':'hall-powered-instruments','subcategory':'','specialty':specialties,'catalogType':'list','name':bi(ru,en),'shortDescription':bi(ru,en),'description':bi('В каталоге HALL представлены '+ru[0].lower()+ru[1:]+'. '+(indRu+'.'if indRu else''),'The HALL catalog presents '+en+'. '+('Indications for use: '+indEn+'.'if indEn else'')),'indications':bi(indRu,indEn)if indEn else None,'heroImage':'','imageType':'cutout','gallery':[],'features':[],'hotspots':[],'variants':[],'components':[],'componentGroups':[],'specTables':[],'refCodes':[],'sourcePages':pages,'catalogEdition':None,'catalogTitle':bi('CONMED HALL Powered Instruments System — каталог продукции','CONMED HALL Powered Instruments System — Product Catalog'),'isNew':True,'status':'draft','reviewFlags':[],'relatedSystemSlugs':[],'imageDimensions':{},'availabilityNote':bi('Не вся продукция доступна на всех рынках.','All products may not be available in all markets.')}
 for n in pages:
  layout=layouts[n];rr=[r for r in records if r['pdfPage']==n];bands=layout['bands'];groups={}
  if n in ROW_BLADES:
   for band in bands:
    if not band['cells'][0].get('id'):continue
    r=byid.get(band['cells'][0]['id']);
    if not r:continue
    cells=band['cells'];cnt=len(cells);cy=(band['bounds'][1]+band['bounds'][3])/2
    # Printed row formats differ; retain additional columns, never fabricate missing dimensions.
    if n==60:labels=['Width','Length','Non-sterile'] if cnt==5 else ['Width','Length']
    elif n in [61,62]or(n==39 and cnt==4):labels=['Width','Length']
    elif n==55:
     labels=['Shank','Length','Material Thickness','Cut Depth'] if cnt==6 else ['Shank','Width','Length'] if r['value'] in ['5053-080','5053-081','5053-082','5053-083','5053-084','5053-085','5080-007'] else ['Shank','Length','Material Thickness']
    elif n==48:labels=['Tooth','Width','Length','Material Thickness']
    elif n==49:labels=['Tooth','Angle','Width','Length','Material Thickness','Cut Thickness']
    elif n==50:labels=['Tooth','Edge','Depth Stop','Width','Length','Material Thickness','Cut Thickness']
    elif n==51:labels=['Tooth','Edge','Width','Length','Material Thickness'] if cnt==7 else ['Depth Stop','Width','Material Thickness','Cut Thickness']
    elif n==52:labels=['Tooth','Edge','Width','Length','Material Thickness','Cut Thickness']
    elif n in [53,54]:labels=['Tooth','Width','Length','Material Thickness','Cut Thickness','Cutting Depth']
    elif cnt==7:labels=['Tooth','Width','Length','Material Thickness','Cut Thickness']
    elif n==34 and r['value'] in ['5071-106','5071-107','5071-108','5071-109','5071-110','5071-111']:labels=['Depth Stop','Width','Material Thickness','Cut Thickness']
    else:labels=['Width','Length','Material Thickness','Cut Thickness']
    labels=labels[:cnt-2]
    vals=[];dim={};bad=[]
    for j,c in enumerate(cells[1:1+len(labels)]):
     val,ident,ok=textcell(c,n);vals.append(trans(val));label=labels[j]
     if label in ['Width','Length','Cut Thickness']:dim[{'Width':'width','Length':'length','Cut Thickness':'thickness'}[label]]=val
     if not ok:bad.append((j+2,ident))
    printed=[a for a in layout['vision']if a['bounds'][1]<cy and re.search(r'Thickness:\s*[0-9.]',a['text'])];match=re.search(r'Thickness:\s*([0-9.]+)',printed[-1]['text'])if printed else None;thickness=match.group(1)if match else dim.get('thickness','');dim['thickness']=thickness;key=(thickness,tuple(labels));gid=f'page-{n:03}-thickness-'+re.sub(r'[^0-9A-Za-z]+','-',thickness or 'unspecified')+'-'+str(len(labels))
    if key not in groups:
     title=bi(('Толщина: '+thickness+' мм')if thickness else ru,('Thickness: '+thickness+' mm')if thickness else en);t=table(title,gid,[trans(x)for x in labels]+[bi('Покрытие','Coating')],n);t['hideDescriptionColumn']=True;t['legend']=bi('Серым отмечены лезвия с покрытием.','Grey-shaded drawings indicate coated blades.');groups[key]=t
    t=groups[key];a=crop(n,[cells[len(labels)+1]['bounds'][0]+.003,band['bounds'][1]+.002,cells[-1]['bounds'][2]-.003,band['bounds'][3]-.002],r['id'],True);a['imageCaption']=bi(ru+' — '+r['value'],en+' — '+r['value']);coated,shade=coating(a);a['coatingEvidence']={'method':'neutral gray area in source drawing','fraction':shade,'coated':coated};vals.append(bi('Да'if coated else'Нет','Yes'if coated else'No'));addrow(s,t,r,bi(ru,en),vals,dim,a)
    for col,ident in bad:addflag(s,'dimension-review',n,f'specTables.{gid}.rows.{len(t["rows"])-1}.{col}',[ident],'Расхождение чтений параметра.','Parameter readings disagree.')
   s['specTables']+=list(groups.values())
  elif n in MATRIX_BLADES:
   fontSource=Image.open(R/f'public/catalogs/conmed/hall-powered-instruments/ocr/{n:03}-600dpi.png').convert('RGB')
   headers=[]
   for band in bands:
    codecells=[c for c in band['cells']if c.get('id')]
    if not codecells:headers.append(band);continue
    thick,_,ok=textcell(band['cells'][0],n);thick=re.sub(r'\s*mm\s*','',thick);gid=f'page-{n:03}-thickness-{thick}';t=table(bi('Толщина: '+thick+' мм','Thickness: '+thick+' mm'),gid,[bi('Ширина тела','Body Width'),bi('Ширина головки','Head Width'),bi('Длина','Length'),bi('Толщина','Thickness'),bi('Покрытие','Coating')],n);t['hideDescriptionColumn']=True;t['legend']=bi('Серым отмечены лезвия с покрытием. Жирный код в исходной таблице обозначает хромовое покрытие.','Grey-shaded drawings indicate coated blades. Bold catalog numbers in the source table indicate chromium coating.')
    for ci,c in enumerate(band['cells'][1:],1):
     cs=[r for r in rr if r['id']==c.get('id')or r['id'].startswith(str(c.get('id'))+'-')]
     if not cs:continue
     def head(label):
      for hb in reversed(headers):
       ht=' '.join(x['officialText']or x['texts']['Vision']for x in hb['cells'][:1])
       if label.lower()in ht.lower():
        cx=(c['bounds'][0]+c['bounds'][2])/2;hc=next((x for x in hb['cells'][1:]if x['bounds'][0]<=cx<=x['bounds'][2]),None)
        if hc:return textcell(hc,n)[0].replace('mm','').strip()
      return ''
     width=head('Body Width')or head('Width');length=head('Length');headwidth=head('Head Width');dim={'width':width,'length':length,'thickness':thick}
     # Above-table profiles have their own evenly spaced columns, independent of the ruled table x positions.
     tableTop=min((b['bounds'][1]for b in bands if any(re.search(r'(?:Body|Head) Width',x['officialText']or x['texts']['Vision'],re.I)for x in b['cells'])),default=.68)
     labels=[a for a in layout['vision']if re.search(r'(?:[A-Z]*\d{3,4})-[\dA-Z-]+',a['text'])and .12<a['bounds'][1]<tableTop-.015]
     labelcodes=[a for a in labels if re.fullmatch(r'(?:[A-Z]*\d{3,4})-[\dA-Z-]+',a['text'].strip())]
     dedup=[]
     for label in sorted(labelcodes,key=lambda a:-a['bounds'][1]):
      cx=(label['bounds'][0]+label['bounds'][2])/2
      if not any(abs(cx-(x['bounds'][0]+x['bounds'][2])/2)<.055 for x in dedup):dedup.append(label)
     labelcodes=sorted(dedup,key=lambda a:a['bounds'][0]);a=None
     # Best exact/prefix match then ordinal; avoid QR and captions by ending above label baseline.
     matches=[a for a in labelcodes if any(r['value']==a['text'].strip()for r in cs)]
     pick=matches[0]if matches else labelcodes[min(ci-1,len(labelcodes)-1)]if labelcodes else None
     if pick:
      ix=labelcodes.index(pick);cx=(pick['bounds'][0]+pick['bounds'][2])/2;left=((labelcodes[ix-1]['bounds'][0]+labelcodes[ix-1]['bounds'][2])/2+cx)/2 if ix else max(.04,cx-.12);right=(cx+(labelcodes[ix+1]['bounds'][0]+labelcodes[ix+1]['bounds'][2])/2)/2 if ix+1<len(labelcodes)else min(.83,cx+.13);a=crop(n,[left,.15,right,pick['bounds'][1]-.005],f'matrix-{n:03}-{ci}',False)
     if not a:
      count=len(band['cells'])-1;left=.06+(ci-1)*.76/count;right=.06+ci*.76/count;a=crop(n,[left,.15,right,max(.2,tableTop-.035)],f'matrix-{n:03}-{ci}',False)
     for r in cs:
      # Boldness comes from the source outlines, measured on the glyph crop, and stays auditable.
      import cv2
      sourceWords=[a for a in layout['vision']if a['text'].strip()==r['value']and c['bounds'][0]-.01<a['bounds'][0]<c['bounds'][2]and c['bounds'][1]-.01<a['bounds'][1]<c['bounds'][3]]
      box=sourceWords[0]['bounds']if sourceWords else c['bounds'];source=fontSource;sw,sh=source.size;pixels=np.asarray(source.crop((int(box[0]*sw),int(box[1]*sh),int(box[2]*sw),int(box[3]*sh))));ink=(pixels.min(axis=2)<130).astype('uint8');dt=cv2.distanceTransform(ink,cv2.DIST_L2,5);weight=float(np.percentile(dt[dt>0],80)/max(1,pixels.shape[0]))if(dt>0).any()else 0;coated=bool((dt>0).any()and np.percentile(dt[dt>0],80)>=3.5)if n in [15,16,17]else False

      vals=[bi(width),bi(headwidth),bi(length),bi(thick),bi('Да'if coated else'Нет','Yes'if coated else'No')];addrow(s,t,r,bi(ru,en),vals,dim,{**a,'imageCaption':bi(ru+' — '+r['value'],en+' — '+r['value'])}if a else None)
    if t['rows']:s['specTables'].append(t)
  elif n in BUR_MATRICES:
   headers=[];kind=en
   for band in bands:
    cells=band['cells'];codecells=[c for c in cells[1:]if c.get('id')and c['id']in byid]
    if not codecells:
     headers.append(band)
     first=cells[0]['officialText']or cells[0]['texts']['Vision']
     if not re.search(r'Diameter|Flutes|Length|Guard',first,re.I)and re.search(r'[A-Za-z]{3}',first):kind=first
     continue
    gid=f'page-{n:03}-group-'+str(len(groups)+1);title=trans(kind);key=kind
    if key not in groups:groups[key]=table(title,gid,[bi('Совместимый защитный тубус','Compatible Bur Guard'),bi('Диаметр','Diameter'),bi('Режущие грани','Flutes'),bi('Длина головки бора','Bur Head Length'),bi('Рабочая длина','Working Length')],n)
    t=groups[key];guard=textcell(cells[0],n)[0]
    for c in codecells:
     r=byid[c['id']];cx=(c['bounds'][0]+c['bounds'][2])/2;fields={}
     for hb in reversed(headers):
      first=hb['cells'][0]['officialText']or hb['cells'][0]['texts']['Vision'];label=next((l for l in ['Diameter','Flutes','Bur Head Length','Working Length']if l.lower()in first.lower()),None)
      if label and label not in fields:
       hc=next((x for x in hb['cells'][1:]if x['bounds'][0]<=cx<=x['bounds'][2]),None)
       if hc:fields[label]=textcell(hc,n)[0]
      # Do not borrow headers from the previous independent matrix.
      if re.search(r'Round|Burs|Diamond|Fluted|Cylindrical',first,re.I)and not re.search(r'Guard',first,re.I):break
     vals=[bi(guard),*[bi(fields.get(k,''))for k in ['Diameter','Flutes','Bur Head Length','Working Length']]];addrow(s,t,r,title,vals,{'width':fields.get('Diameter',''),'length':fields.get('Working Length','')})
   s['specTables']+=list(groups.values())
  else:
   # One source orderable code per page; compatibility references inside captions are not extra products.
   dedup={}
   for r in rr:
    key=r['value']or r['candidate'];old=dedup.get(key)
    if not old or r['sourceBounds'][1]>old['sourceBounds'][1]:dedup[key]=r
   for r in sorted(dedup.values(),key=lambda r:(r['sourceBounds'][1],r['sourceBounds'][0])):
    b=r['sourceBounds'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;lines=layout['vision'];same=[a for a in lines if abs((a['bounds'][1]+a['bounds'][3])/2-cy)<.012 and a['bounds'][0]<b[2]+.02];line=' '.join(a['text']for a in sorted(same,key=lambda a:a['bounds'][0]));line=re.sub(r'\.{2,}|•+',' ',line);line=re.sub(r'(?:'+re.escape(r['value']or r['candidate'])+r')\s*$','',line).strip(' .|')
    # Official caption text is retained only if its code is visible in source and the source has that description.
    if len(line)<6 or not re.search(r'[a-z]{3}',line):line=en
    line=re.sub(r'[®™]','',line);desc=trans(line)
    gid=f'page-{n:03}';t=groups.setdefault(gid,table(bi(ru,en),gid,[],n));t['unit']=None
    aa=[a for a in assets.values()if a['pdfPage']==n];a=min(aa,key=lambda a:abs(a['bounds'][3]-cy)+abs((a['bounds'][0]+a['bounds'][2])/2-cx)*.5)if aa else None
    addrow(s,t,r,desc,[])
    if a:
     asset={**a,'imageCaption':desc}
     if not any(x['src']==asset['src']for x in t['images']):t['images'].append(asset)
     s['components'].append({'name':desc,'image':a['src'],'imageType':a['imageType'],'refCodes':[r['value']],'groupId':gid})
   s['specTables']+=list(groups.values())
 # No duplicated source header/caption entries within a system; preserve repeated codes with different compatibility rows in matrices.
 for t in s['specTables']:
  for a in t.get('rowImages',[])+t.get('images',[]):
   if a:s['imageDimensions'][a['src']]={'width':a['width'],'height':a['height']}
 imgs=[a for t in s['specTables']for a in t.get('images',[])];draws=[a for t in s['specTables']for a in t.get('rowImages',[])if a];s['gallery']=imgs[:8]if imgs else draws[:4]
 if s['gallery']:
  a=s['gallery'][0];s['heroImage']=a['src'];s['imageType']=a['imageType']
 s['refCodes']=list(dict.fromkeys(s['refCodes']))
 if slug=='hall-stryker-compatible-replacement-blades':
  s['compatibilityNote']=bi('Совместимы с инструментами Stryker','Compatible with Stryker instruments');s['description']={l:s['description'][l]+' '+s['compatibilityNote'][l]+'.'for l in ['ru','en']}
 systems.append(s)
from hall_reviewed_context import enrich
systems=enrich(systems,layouts,assets,records,crop)
# Keep omissions explicit; they are not silently treated as completed extraction.
unassigned=[r for r in records if r['id']not in assigned];dump(F/'unassigned.json',unassigned);dump(F/'numeric-verification.json',numeric);dump(F/'drawing-assets.json',list(drawmeta.values()));dump(F/'translation-unknown.json',sorted(unknown))
profile={'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'layoutReviewed':True,'method':'600-DPI Tesseract PSM3/11, isolated PSM7/13, independent Apple Vision and Codex visual readings of disagreements; official CONMED catalog corroboration; source-positioned tables and white vector drawings; Codex-authored professional Russian.','nonProductPages':[1,2,3,4,5,6,7,79,80],'systems':systems,'assets':list(assets.values())+list(drawmeta.values())};from hall_source_review import apply
from hall_bur_review import refine
profile=apply(refine(profile));dump(R/'scripts/profiles/conmed-hall-powered-instruments.json',profile);print('Systems',len(systems),'rows',sum(len(t['rows'])for s in systems for t in s['specTables']),'flags',sum(len(s['reviewFlags'])for s in systems),'unassigned',len(unassigned),'photos',len(assets),'drawings',len(drawmeta),'unknown translations',len(unknown))
