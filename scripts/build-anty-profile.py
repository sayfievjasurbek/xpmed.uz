#!/usr/bin/env python3
"""Source-reviewed Anty F-series matrix and Codex-authored medical Russian."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def bi(ru,en):return {'ru':ru,'en':en}
def cell(value,colspan=1,rowspan=1):return {'value':value,**({'colspan':colspan}if colspan>1 else{}),**({'rowspan':rowspan}if rowspan>1 else{})}
assetdata=json.loads((R/'public/images/products/double-medical/anty-f-series/prepared-assets.json').read_text());assets=assetdata['assets'];A={a['name']:a for a in assets}
def image(name):return A[name]['src']
heads=[bi('Размер','Size')]+[bi('Длина ножки '+str(v),'Stem length '+str(v))for v in [170,205,245,285]]+[bi('Длина шейки','Neck length'),bi('Высота шейки','Neck height')]+[bi('Проксимальный наружный диаметр — '+str(v),'Proximal outer diameter — '+str(v))for v in [170,205,245,285]]+[bi('Диаметр средней части','Mid-section diameter'),bi('Дистальный диаметр','Distal diameter')]
h0=['']*13;h1=['']*13
h0[0]=cell(bi('Размер','Size'),rowspan=2);h0[1]=cell(bi('Длина ножки','Stem length'),colspan=4);h0[5]=cell(bi('Длина шейки','Neck length'),rowspan=2);h0[6]=cell(bi('Высота шейки','Neck height'),rowspan=2);h0[7]=cell(bi('Проксимальный наружный диаметр','Proximal outer diameter'),colspan=4);h0[11]=cell(bi('Диаметр средней части','Mid-section diameter'),rowspan=2);h0[12]=cell(bi('Дистальный диаметр','Distal diameter'),rowspan=2)
h1[1:5]=['170','205','245','285'];h1[7:11]=['170','205','245','285']
# Each source row is transcribed independently; no interpolated 11# or regenerated dimensions.
rows=[
 ['1# / 14mm','●','●','●','○','42','22','13','14','15','16','14','9'],
 ['2# / 15mm','●','●','●','○','42','22','14','15','16','17','15','10'],
 ['3# / 16mm','●','●','●','○','42','22','15','16','17','17','16','11'],
 ['4# / 17mm','●','●','●','○','42','22','16','17','17','17','17','12'],
 ['5# / 18mm','●','●','●','○','44','24','17','18','17','17','18','13'],
 ['6# / 19mm','●','●','●','○','44','24','18','19','20','21','19','14'],
 ['7# / 20mm','●','●','●','○','44','24','19','20','21','21','20','15'],
 ['8# / 21mm','●','●','●','○','44','24','20','21','21','21','21','16'],
 ['9# / 22mm','×','●','●','○','46','26','×','22','21','21','22','17'],
 ['10# / 23mm','×','○','○','○','46','26','×','23','24','25','23','18'],
 ['12# / 25mm','×','×','×','○','46','26','×','×','×','25','25','20']]
# Table bounds/row pitch read directly from the ruled page-2 matrix.
edges=[652.548,662.413,672.278,682.144,692.009,701.874,711.739,721.604,731.469,741.334,751.2,761.198]
T={'id':'anty-f-series-sizes','title':bi('Размеры ревизионной бедренной ножки Anty F-series','Anty F-series femoral revision stem specifications'),'unit':'mm','columns':heads,'headerRows':[h0,h1],'headersVerified':True,'rows':rows,'legend':bi('● / ○ / × — наличие уточняйте у менеджера','● / ○ / × — please confirm availability with your manager'),'sourcePages':[2],'sourceBounds':[.085,.735,.914,.889],'rowSources':[{'pdfPage':2,'sourceBounds':[52/613.2755737304688,edges[i]/859.8897705078125,561/613.2755737304688,edges[i+1]/859.8897705078125]}for i in range(11)],'sourceHeaders':{'长度':'Stem length','颈长':'Neck length','颈高':'Neck height','近端外直径':'Proximal outer diameter','中段外直径':'Mid-section diameter','远端外直径':'Distal diameter'},'sourceSizeLabelLayout':'Two printed size fields combined as size # / diameter, as explicitly requested. No values changed.'}
features=[]
for id,ru,en,text_ru,text_en in[
 ('shoulder-coating','Покрытие плеча ножки','Shoulder coating','Покрытие плеча ножки способствует остеоинтеграции.','The shoulder coating design is beneficial for bone integration.'),
 ('cable-holes','Отверстия для серкляжа','Cable holes','Отверстия облегчают фиксацию костных фрагментов и мягких тканей.','Cable holes facilitate fixation of bone fragments and soft tissues.'),
 ('longitudinal-ribs','8 острых продольных рёбер','8 sharp longitudinal ribs','8 острых продольных рёбер увеличивают площадь контакта ножки, обеспечивая ротационную и первичную аксиальную стабильность.','8 sharp longitudinal ribs increase the stem contact surface and enhance anti-rotation and initial axial stability.'),
 ('taper','Конусность 2°','2° taper','Конусность 2° обеспечивает преимущественно диафизарную фиксацию.','The 2° taper provides fixation predominantly in the diaphysis.'),
 ('circular-cross-section','Круглое поперечное сечение','Circular cross-section','Круглое поперечное сечение облегчает регулировку антеверсии бедренного компонента.','The circular cross-section facilitates adjustment of femoral anteversion.'),
 ('minimum-diameter','Минимальный диаметр тела ножки 13 мм','Minimum stem body diameter 13 mm','Минимальный диаметр тела ножки составляет 13 мм, что позволяет использовать её в узких костномозговых каналах.','The minimum stem body diameter is 13 mm, sized to fit small canals.')]:
 features.append({'id':id,'title':bi(ru,en),'text':bi(text_ru,text_en),'image':image('feature-'+id),'sourcePages':[2]})
gallery=[{**A['technical-drawing'],'imageCaption':bi('Технический чертёж Anty F-series: размеры и поперечные сечения','Anty F-series technical drawing: dimensions and cross-sections')}]
S={'schemaVersion':1,'slug':'anty-f-series','brand':'double-medical','catalogType':'system','category':'joint-replacement','subcategory':'hip','specialty':['orthopedics'],'name':bi('Ревизионная бедренная ножка Anty F-series','Anty F-series Femoral Revision Stem System'),'shortDescription':bi('Ревизионная бедренная ножка с конусностью 2° и 8 продольными рёбрами.','Femoral revision stem with a 2° taper and 8 longitudinal ribs.'),'description':bi('Anty F-series — система ревизионных бедренных ножек Double Medical. Конструкция включает покрытие плеча ножки для остеоинтеграции, отверстия для серкляжа и острые продольные рёбра для первичной стабильности. Круглое поперечное сечение позволяет регулировать антеверсию; размеры и варианты длины приведены в таблице производителя.','Anty F-series is a Double Medical femoral revision stem system. Its design includes shoulder coating for bone integration, cable holes and sharp longitudinal ribs for initial stability. A circular cross-section allows anteversion adjustment; manufacturer dimensions and length options are listed in the specification table.'),'heroImage':image('hero-stem'),'imageType':'cutout','gallery':gallery,'variants':[],'features':features,'hotspots':assetdata['hotspots'],'components':[],'specTables':[T],'refCodes':[],'sourcePages':[1,2],'catalogEdition':None,'catalogTitle':bi('Double Medical Anty F-series — каталог продукции','Double Medical Anty F-series — Product Catalog'),'isNew':True,'status':'draft','relatedSystemSlugs':['pbg-proximal-bone-growth-cementless-stem'],'imageDimensions':{a['src']:{'width':a['width'],'height':a['height']}for a in assets}}
profile={'sha256':hashlib.sha256((R/'catalogs-source/double-medical/anty-f-series.pdf').read_bytes()).hexdigest(),'method':'600-DPI two-setting Tesseract OCR; complete matrix visually transcribed and checked cell by cell, with Chinese header translations supplied by owner; page-2 callouts mapped onto native stem coordinates.','layoutReviewed':True,'nonProductPages':[],'system':S,'assets':assets,'flags':[]}
(R/'scripts/profiles/anty-f-series.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n');print('Anty profile: 11 source rows, 13 columns, 6 hotspots')
