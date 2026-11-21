"""Build reviewed Part 1 families from source-positioned evidence, never per-size pages."""
import json,re,collections,copy,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from trauma_manifest import SETS,SUBCATEGORIES
from trauma_translation import implant,instrument
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part1';A=R/'public/images/products/double-medical/trauma-catalogue'
scope=json.loads((F/'scope.json').read_text());tables=json.loads((F/'tables-final.json').read_text());rows=json.loads((F/'instrument-rows-final.json').read_text());headers=json.loads((F/'page-headers.json').read_text());native=json.loads((F/'source-images.json').read_text());ready=json.loads((A/'prepared-assets.json').read_text())if(A/'prepared-assets.json').exists()else{}
bi=lambda ru,en:{'ru':ru,'en':en}
def slugify(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def issue(code,page,ru,en,path,readings=None):
    return {'code':code,'pdfPage':page,'sourcePages':[page],'path':path,'message':bi(ru,en),'readings':readings or []}
def caption_value(value):
    if value is None:return None
    if value.casefold()=='left':return bi('Левая','Left')
    if value.casefold()=='right':return bi('Правая','Right')
    if value.casefold()in ['standard','short']:return bi('Стандартный'if value.casefold()=='standard'else'Короткий',value)
    if re.search('[A-Za-z]{2}',value):return implant(value)
    return bi(value,value)
LABELS={'Holes':'Отверстия','Head Holes':'Отверстия в головной части','Direction':'Сторона (L/R)','Length':'Длина','Height':'Высота','Diameter':'Диаметр','Tip Diameter':'Диаметр наконечника','Teeth Length':'Длина резьбы','Bending':'Изгиб','Size':'Размер','Description':'Описание'}
def column(h):
    if h.startswith('REF'):return bi('REF (шестигранный шлиц)'if'Hex'in h else h.replace('Small','малая').replace('Large','большая'),h)
    base=re.sub(r'\s*\(mm\)','',h).strip()
    if base.startswith('Direction'):base='Direction'
    if base.startswith('Length'):base='Length'
    if base.startswith('Holes'):base='Holes'
    return bi(LABELS.get(base,base),base)
PARAMETERS={'Thickness':'Толщина','Width':'Ширина','Head Width':'Ширина головной части','Hole Spacing':'Расстояние между отверстиями','Material':'Материал','Screws':'Совместимые винты','Screw':'Совместимый винт','Diameter':'Диаметр','Diameter(mm)':'Диаметр','Head Diameter':'Диаметр головки','Hexagonal Socket':'Шестигранный шлиц','Torxdrive':'Шлиц Torx'}
def parameters(t):
    out=[]
    for line in t['preamble']:
        line=line.replace('TThickness:','Thickness:').replace('HexagonalSocket:','Hexagonal Socket:')
        pairs=list(re.finditer(r'(Thickness|Head Width|Width|Hole Spacing|Material|Screws?|Diameter(?:\(mm\))?|Head Diameter|Hexagonal Socket|Torxdrive)\s*:',line))
        if not pairs:
            if out and re.match(r'^[0-9]',line):
                v=implant(line);out[-1]['value']={l:out[-1]['value'][l]+'; '+v[l]for l in ['ru','en']}
            continue
        for i,m in enumerate(pairs):
            key=m[1];value=line[m.end():pairs[i+1].start()if i+1<len(pairs)else len(line)].strip().replace('Lockng','Locking');v=implant(value)
            v['ru']=v['ru'].replace('Pure Titanium','чистый титан').replace('Titanium Alloy','титановый сплав').replace('Titanium','титан').replace('Co-Cr Alloy','кобальт-хромовый сплав')
            out.append({'parameter':bi(PARAMETERS[key],key),'value':v})
    return out
def source_image(key,label,slug):
    if key not in ready:return None
    a=ready[key];dest=R/'public/images/products/double-medical'/slug;dest.mkdir(parents=True,exist_ok=True)
    target=dest/(key+'.webp')
    shutil.copy2(R/'public'/a['src'].lstrip('/'),target)
    return {k:a[k]for k in ['width','height','imageType','captionFree','imageEnhancement']}|{'src':f'/images/products/double-medical/{slug}/{key}.webp','imageCaption':label,'sourcePages':[a['pdfPage']]}
def page_photos(n):return [(k,a)for k,a in native.items()if a['pdfPage']==n]
def base(name,category,sections,pages):
    slug=slugify(name['en']);return {'slug':slug,'brand':'double-medical','category':category,'subcategory':SUBCATEGORIES[min(sections)],'subcategories':[SUBCATEGORIES[s]for s in sorted(sections)],'specialty':['traumatology','orthopedics'],'name':name,'shortDescription':bi('Импланты для остеосинтеза','Implants for fracture fixation')if category=='trauma-implants'else bi('Инструменты для травматологии','Trauma surgery instruments'),'description':bi(name['ru']+'. Характеристики и каталожные номера приведены по Trauma Catalogue Double Medical.',name['en']+'. Specifications and reference numbers are listed according to the Double Medical Trauma Catalogue.'),'heroImage':'','imageType':'cutout','gallery':[],'features':[],'components':[],'specTables':[],'refCodes':[],'sourcePages':sorted(pages),'catalogEdition':None,'catalogTitle':bi('Double Medical Trauma Catalogue — каталог продукции','Double Medical Trauma Catalogue — product catalog'),'documentCover':'/catalogs/double-medical/trauma-catalogue/pages/001.webp','isNew':False,'status':'draft','catalogType':'list','importPartition':'trauma-part1','availabilityNote':bi('Изображения приведены для справки','Images for reference only'),'reviewFlags':[],'imageDimensions':{},'relatedSystemSlugs':[]}
def finish_images(s,photos):
    seen=set()
    for photo in photos:
        if not photo or photo['src']in seen:continue
        seen.add(photo['src']);s['imageDimensions'][photo['src']]={k:photo[k]for k in ['width','height']}
        if len(s['gallery'])<6:s['gallery'].append(photo)
    if s['gallery']:s['heroImage']=s['gallery'][0]['src'];s['imageType']=s['gallery'][0]['imageType']
systems=[]
families=collections.defaultdict(list)
for t in tables:families[t['title']].append(t)
for title,ts in families.items():
    s=base(implant(title),'trauma-implants',{t['section']for t in ts},{t['pdfPage']for t in ts});photos=[]
    for ti,t in enumerate(ts):
        n=t['pdfPage'];pr=[a for a in tables if a['pdfPage']==n];idx=pr.index(t);lower=max([r['cy'] for other in pr[:idx]for r in other['rows']],default=.12)+(.012 if idx else 0);upper=t['rows'][-1]['cy']+.025
        pictureKeys=[k for k,a in page_photos(n)if next((p for p in reversed(pr)if p['titleY']<=a['bounds'][1]+.04),pr[0])is t]
        images=[source_image(k,s['name'],s['slug'])for k in pictureKeys];images=[a for a in images if a];photos+=images
        table={'id':t['id'],'groupId':t['id'],'title':s['name'],'unit':'mm','sourcePage':n,'sourcePages':[n],'printedPage':t['printedPage'],'hideDescriptionColumn':True,'columns':[bi('Позиция','Item')]+[column(h)for h in t['headerReadings']],'rows':[],'rowSources':[],'images':images,'keyParameters':parameters(t)}
        for ri,r in enumerate(t['rows']):
            values=[];dimensions=[]
            for ci,(h,value)in enumerate(zip(t['headerReadings'],r['values'])):
                values.append(value if h.startswith('REF')else caption_value(value))
                if h.startswith('REF')and value:s['refCodes'].append(value)
                elif value is not None:dimensions.append(f'{h}: {value}')
            rowName={l:s['name'][l]+(' · '+', '.join(column(h)[l]+': '+str(caption_value(value)[l]if isinstance(caption_value(value),dict)else value)for h,value in zip(t['headerReadings'],r['values'])if not h.startswith('REF')and value is not None)if dimensions else'')for l in ['ru','en']}
            table['rows'].append([rowName]+values);table['rowSources'].append({'pdfPage':n,'printedPage':t['printedPage'],'sourceBounds':r['sourceBounds'],'codeEvidence':[{'tableId':t['id'],'row':ri+1,'column':ci+2,'pdfPage':n,'readings':[{'reader':reader,'text':value}for reader,value in r['evidence'][ci]['readings'].items()],'verificationStatus':'verified (three readers compared; exact agreement)'}for ci,h in enumerate(t['headerReadings'])if h.startswith('REF')],'cellEvidence':r['evidence']})
        for f in t['reviewFlags']:
            ru=('REF '+f['ref']+' отличается от префикса '+f['commonPrefix']+' остальных строк. Код подтверждён тремя чтениями и сохранён; требуется подтверждение производителя.')if f['code']=='source-ref-prefix-outlier'else'Требуется проверка значения по исходному каталогу.'
            en=('REF '+f['ref']+' differs from the '+f['commonPrefix']+' prefix of the other rows. All three readers confirm the printed code; manufacturer confirmation is required.')if f['code']=='source-ref-prefix-outlier'else'Verify the value against the source catalog.'
            s['reviewFlags'].append(issue(f['code'],n,ru,en,f'specTables.{ti}.rows.{f.get("row",0)}.{f.get("column",0)+1}',f.get('readings')))

        if n in [50,51]:s['reviewFlags'].append(issue('source-diameter-conflict',n,'В заголовке указан винт 4.0 мм, в строке Diameter напечатано 3.5 мм. Оба исходных значения сохранены.','The title specifies 4.0 mm, while the Diameter line prints 3.5 mm. Both source values are retained.',f'specTables.{ti}.keyParameters',['Title: 4.0mm','Diameter:3.5mm']))
        s['specTables'].append(table)
    finish_images(s,photos);s['refCodes']=list(dict.fromkeys(s['refCodes']));systems.append(s)
for start,end,section,en,ru in SETS:
    own=[r for r in rows if start<=r['pdfPage']<=end];s=base(bi(ru,en),'trauma-instrument-sets',{section},{r['pdfPage']for r in own});codes=[dict(c,pdfPage=h['pdfPage'])for h in headers if start<=h['pdfPage']<=end for c in h['setCodes']];setCodes=list(dict.fromkeys(c['value']for c in codes if c['value']));s['setCode']=' / '.join(setCodes);s['setCodes']=setCodes;
    if len(setCodes)==2 and start in [58,115]:
        s['setCodeLegend']=[{'code':setCodes[0],'connection':bi('Соединение AO','AO coupling')},{'code':setCodes[1],'connection':bi('Треугольное соединение','Triangle coupling')}]
        s['description']={l:s['description'][l]+' '+('; '.join(v['code']+' — '+v['connection'][l]for v in s['setCodeLegend']))+'.'for l in ['ru','en']}
    if start==121:
        s['description']={l:s['description'][l]+(' Стандартный набор: 111540000; дополнительная комплектация по заказу: 111850000.'if l=='ru'else' Standard set: 111540000; customized optional set: 111850000.')for l in ['ru','en']}
    s['setCodeEvidence']=codes;s['refCodes']+=setCodes;photos=[]
    for n in s['sourcePages']:
        rr=[r for r in own if r['pdfPage']==n];table={'id':f'trauma-set-{start}-p{n}','groupId':f'trauma-set-{start}-p{n}','title':bi(f'Инструменты · {rr[0]["printedPage"]}',f'Instruments · {rr[0]["printedPage"]}'),'unit':'mm','columns':[bi('Наименование','Description'),bi('REF','REF')],'rows':[],'rowImages':[],'rowSources':[],'sourcePage':n,'sourcePages':[n],'printedPage':rr[0]['printedPage']};assigned={r['id']:[]for r in rr}
        for k,a in page_photos(n):
            cases=[r for r in rr if 'Case'in r['description']and a['bounds'][1]-.02<=r['cy']<=a['bounds'][3]+.02];nearest=next((r for r in rr if r['id']==a.get('sourceRowId')),None)or(min(cases,key=lambda r:abs(r['cy']-(a['bounds'][1]+a['bounds'][3])/2))if cases else min(rr,key=lambda r:abs(r['codeBounds'][1]-a['bounds'][1])));assigned[nearest['id']].append(k)
        for ri,r in enumerate(rr):
            name=instrument(r['description'],ru);photoList=[source_image(k,name,s['slug'])for k in assigned[r['id']]];photoList=[p for p in photoList if p];photos+=photoList;table.setdefault('images',[]).extend(photoList[1:]);table['rows'].append([name,r['value']]);table['rowImages'].append(photoList[0]if photoList else None);table['rowSources'].append({'pdfPage':n,'sourceBounds':r['sourceBounds'],'printedPage':r['printedPage'],'sourceRowId':r['id'],'codeEvidence':[{'tableId':table['id'],'row':ri+1,'column':2,'pdfPage':n,'readings':[{'reader':reader,'text':value}for reader,value in r['readings'].items()],'verificationStatus':'verified (three readers compared; exact agreement)'if r['value']else'missing in source'}],'descriptionReadings':r['descriptionReadings']})
            s['components'].append({'id':'trauma-'+r['id'],'groupId':table['groupId'],'name':name,'image':photoList[0]['src']if photoList else'','refCodes':[r['value']]if r['value']else[],'sourcePages':[n]})
            if r['value']:s['refCodes'].append(r['value'])
            else:s['reviewFlags'].append(issue('source-ref-missing',n,'Каталожный номер костодержателя не напечатан в исходном PDF.','The source PDF does not print a catalog number for the self-centering bone-holding forceps.',f'specTables.{len(s["specTables"])}.rows.{ri}.1',['Source code cell is empty']))
        if n==123:
            for optional in [False,True]:
                group=copy.deepcopy(table);suffix='optional'if optional else'standard';group['id']+='-'+suffix;group['groupId']=group['id'];group['title']=bi('Дополнительная комплектация 111850000','Customized optional set 111850000')if optional else bi('Контейнер набора 111540000','Case for set 111540000')
                for field in ['rows','rowImages','rowSources']:group[field]=group[field][1:]if optional else group[field][:1]
                group['images']=[];s['specTables'].append(group)
            for c in s['components']:
                if c['groupId']==table['groupId']:c['groupId']=table['groupId']+('-standard'if c['id']=='trauma-123-01'else'-optional')
        else:s['specTables'].append(table)
    if start==204:s['reviewFlags'].append(issue('duplicate-ref-different-instruments',205,'REF 110021300 напечатан для гибочных щипцов и костного крючка. Коды сохранены без предположений.','REF 110021300 is printed for both bending pliers and a bone hook. Neither code has been guessed or changed.','specTables.1.rows',['110021300 — Bending Pliers for Reconstruction Plates','110021300 — Bone Hook, sharp, medium']))
    finish_images(s,photos);s['refCodes']=list(dict.fromkeys(s['refCodes']));systems.append(s)
# Reciprocal links follow the source index and explicitly named clinical families.
implants=[s for s in systems if s['category']=='trauma-implants'];sets=[s for s in systems if s['category']=='trauma-instrument-sets']
for st,manifest in zip(sets,SETS):
    start=manifest[0]
    def matches(s):
        name=s['name']['en'];section=SUBCATEGORIES[manifest[2]] in s['subcategories']
        if start in [52,58,115]:return section
        if start==64:return name.startswith('Low Profile Distal Medial Tibial')
        if start in [68,69]:return name.startswith('Proximal Humeral')
        if start==72:return manifest[2]==1 and section and ('Radius'in name or 'Radial'in name or '2.4mm'in name)
        if start==121:return 'Femoral'in name and name.startswith('Distal')
        if start==124:return 'Tibial'in name and name.startswith('Proximal')
        if start==127:return name.startswith('Proximal Femoral')
        if start==132:return 'Cable'in name
        if start==135:return 'Osteotomy'in name and section
        if start==175:return section and name.startswith(('MD ','MT ','DMT '))
        if start==183:return name.startswith('Hammertoe')
        if start==185:return name=='Tarsal Sinus Screw'
        if start==188:return name=='Tarsal Sinus Screw II'
        if start==204:return section
        return False
    for s in implants:
        if matches(s):st['relatedSystemSlugs'].append(s['slug']);s['relatedSystemSlugs'].append(st['slug'])
def image_refs(v):
    if isinstance(v,str):return{v}if v.startswith('/images/products/')else set()
    if isinstance(v,list):return set().union(*(image_refs(x)for x in v))if v else set()
    if isinstance(v,dict):return set().union(*(image_refs(x)for x in v.values()))if v else set()
    return set()
profile={**scope,'layoutReviewed':True,'method':'600-DPI Tesseract PSM3/11 plus independent Apple Vision; source glyph reconciliation and Codex visual reading; Codex medical RU; native photo composites, original Real-ESRGAN weights exact 2x then rembg','systems':systems,'merges':[],'assets':sorted(image_refs(systems))}
(R/'scripts/profiles/double-medical-trauma-part1.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
(F/'profile-summary.json').write_text(json.dumps({'systems':len(systems),'implantSystems':len(implants),'instrumentSets':len(sets),'photosReady':len(ready),'photosExpected':len(native),'flags':[f for s in systems for f in s['reviewFlags']]},ensure_ascii=False,indent=2)+'\n')
print('Systems',len(systems),'implants',len(implants),'sets',len(sets),'photos',len(ready),'/',len(native),'flags',sum(len(s['reviewFlags'])for s in systems))
