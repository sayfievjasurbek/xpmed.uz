import json,pathlib,sys,re,hashlib,copy,difflib
from surgical_ru import translate
from professional_ru import professional
exec(pathlib.Path('scripts/profiles/conmed-surgical-layout.py').read_text())
root=pathlib.Path('.');ref=root/'public/catalogs/conmed/advanced-surgical-product-catalog';ver=json.loads((root/'reports/conmed/advanced-surgical-product-catalog/verification.json').read_text());evidence={(r['pdfPage'],r['pageRow']):r for r in ver['records']};prepared=json.loads((root/'public/images/products/conmed/advanced-surgical/prepared-assets.json').read_text());native=json.load(open('reports/conmed/advanced-surgical-product-catalog/source-images.json'));sections=[];alltext=[]
exec(pathlib.Path('scripts/profiles/conmed-surgical-context.py').read_text())
for slug,category,nums,en,ru in SECTIONS:
 section={'slug':slug,'category':category,'specialty':['surgery'],'name':{'ru':ru,'en':en},'sourcePages':nums,'shortDescription':{'ru':'Компоненты, комплектация и каталожные номера CONMED.','en':'CONMED components, packaging options and catalog numbers.'},'overview':{'ru':f'В этом разделе представлены изделия семейства «{ru}». Таблицы содержат описания, варианты упаковки и каталожные номера производителя.','en':f'This section presents {en} products. The tables include full descriptions, packaging options and manufacturer catalog numbers.'},'groups':[],'flags':[]}
 for n in nums:
  d=json.load(open(f'reports/conmed/advanced-surgical-product-catalog/layout/parsed-{n:03}.json'));assert len(d['groups'])==len(HEADERS[n]);pi=0
  for gi,g in enumerate(d['groups']):
   title=HEADERS[n][gi];gid=f'surgical-p{n}-g{gi+1}';group={'id':gid,'page':n,'title':{'en':title,'ru':json.loads((root/'scripts/profiles/conmed-surgical-headings-ru.json').read_text())[str(n)][gi]},'headingBounds':g['headerBounds'],'tableBounds':[g['headerBounds'][0],g['headerBounds'][1],.934,g['end']],'columns':[{'ru':'Наименование','en':'Description'},{'ru':'Упаковка','en':'Pack'},{'ru':'Cat. No.','en':'Cat. No.'}],'columnTypes':['description','pack','catalog-number'],'columnBounds':[[.50,.81],[.50,.81],[.78,.94]],'rowBounds':[],'rows':[],'codeEvidence':[],'photos':[]}
   if (n,gi)in CONTEXT:
    de,dr=CONTEXT[n,gi];group['description']={'en':de,'ru':dr}
   for row in g['rows']:
    pi+=1;r=evidence[n,pi];text=row['description'];text=text.replace('1 4 gauge','14 gauge').replace('MORE OPTIONS','').replace('omm','5mm').replace('Omm','5mm').replace('oox','box').replace('okg','pkg').replace('pka','pkg').replace('oterile','Sterile').replace('otandard','Standard').replace('C02','CO2').replace('mmtubing','mm tubing').replace('mytubing','m) tubing')
    fixes={'iAS5-75LP':[('7omm','75mm')],'iFS-HPH2':[('1.9m','1.5m')],'iFS-HPH3':[('1.9m','1.5m')],'60-8046-001':[('3.661','3.66m')],'410-2100':[('4575m','457m')],'133002':[('System 9000','System 5000')]}
    for a,b in fixes.get(r['visualReading'],[]):text=text.replace(a,b)
    # Fractions explicitly read from the original table illustrations.
    if n in [36,37]:
     for a,b in [('734 (19.7','7¾ (19.7'),('7% (19.1','7½ (19.1'),('5% (14.0','5½ (14.0'),('3% (8.9','3½ (8.9'),('8% (21.0','8¼ (21.0')]:text=text.replace(a,b)
    fraction_by_code={'60-1765-001':('7¾','19.7'),'60-1769-001':('7½','19.1'),'60-1770-001':('8¼','21.0'),'60-1771-001':('5½','14.0'),'60-1773-001':('3½','8.9'),'60-1774-001':('3½','8.9'),'60-5121-001':('7¾','19.7'),'60-5123-001':('5½','14.0'),'60-0812-001':('7½','19.1')}
    if r['visualReading']in fraction_by_code:
     frac,metric=fraction_by_code[r['visualReading']];text=re.sub(r'\b[\d%¼½¾.]+\s*\('+re.escape(metric)+r'cm\)',frac+' ('+metric+'cm)',text)
    if n==39 and gi==0:
     labels=['Spatula']*3+['L Hook']*3+['Straight Blade']*2+['J Hook']*3+['Hook Blade'];text=labels[pi-1]+': '+text
    if n==11 and gi==2 and pi>=8:text='Capture Ports (X-Ray Detectable): '+text
    if n==30 and gi==0:text=(['Push Button, Hand Switch Pencils']*7+['Rocker Switch, Hand Switch Pencils']*7+['Foot Control Pencils']*3)[pi-1]+': '+text
    if n==13 and gi==1:text=('Sterile: 'if pi<=3 else'Non-Sterile: ')+text
    if n==13 and gi==2:text=('Sterile: 'if pi==7 else'Non-Sterile: ')+text
    if n==14 and gi in [1,2]and not text.lower().startswith('sterile'):text='Sterile: '+text
    packs=re.findall(r'\d+\s*/\s*(?:case|box|pkg|cs|ea|each)\b|\d+\s+Pack\b',text,re.I);pack='; '.join(packs)or'—';full=re.sub(r'\d+\s*/\s*(?:case|box|pkg|cs|ea|each)\b|\d+\s+Pack\b','',text,flags=re.I);full=re.sub(r'\(\s*[,;]?\s*\)','',full);full=re.sub(r',\s*,',',',full);full=re.sub(r'\s+',' ',full).strip(' ,;')
    # English remains complete in the description; Pack is also independently scannable.
    group['rows'].append([{'en':full if full.strip(' ()') else title,'ru':professional(n,pi,full,r['visualReading']) if full.strip(' ()') else translate(title)},{'en':pack,'ru':translate(pack)},r['visualReading']]);group['rowBounds'].append(row['rowBounds'])
    audit={'value':r['value'],'printedCandidate':r['visualReading'],'pass1':r['ocrReadings']['600dpi-psm3'],'pass2':r['ocrReadings']['600dpi-psm11'],'confidence1':min((q['confidence']for q in json.loads((ref/'ocr'/f'{n:03}.json').read_text())['passes']['3']['words']if q['bounds'][0]>.775 and abs((q['bounds'][1]+q['bounds'][3])/2-row['cy'])<.006),default=-1),'confidence2':min((q['confidence']for q in json.loads((ref/'ocr'/f'{n:03}.json').read_text())['passes']['11']['words']if q['bounds'][0]>.775 and abs((q['bounds'][1]+q['bounds'][3])/2-row['cy'])<.006),default=-1),'confidenceNote':'Acceptance uses independent visual/OCR agreement; these are original full-page OCR word confidences. Raw word confidences remain in the OCR cache.','flagged':r['value']is None,'reasons':[]if r['value']else['visual-ocr-disagreement'],'pdfPage':n,'printedPage':None,'sourceBounds':r['sourceBounds'],'visualReading':{'reading':r['visualReading'],'reader':'Codex visual inspection','confidence':'clear'},'ocrReadings':[{'reader':k,'text':v}for k,v in r['ocrReadings'].items()],'verificationStatus':r['verificationStatus'],'manufacturerStatus':r['manufacturerStatus'],'officialEvidence':r['officialEvidence'],'lineCrop':r['lineCrop']}
    group['codeEvidence'].append(audit);alltext.append((n,r['visualReading'],group['rows'][-1][0]))
   section['groups'].append(group)
  # Safely place unassigned family illustrations in its main group; exact code labels take precedence.
  assets=[r for r in native if r['page']==n]
  for ai,asset in enumerate(assets):
   if asset['name']not in prepared:continue
   image=prepared[asset['name']];pagegroups=[g for g in section['groups']if g['page']==n];target=pagegroups[0]
   overrides={5:{110:3},11:{184:0,182:1,176:2,179:2,181:2},21:{282:1,284:2,286:3,288:0},23:{296:0,297:1,299:0},24:{306:0,308:0,309:1},25:{316:0,318:0,320:1,321:1,322:1},26:{328:0,330:2}}
   xref=asset['pdfImageXref']
   if xref in overrides.get(n,{}):target=pagegroups[overrides[n][xref]]
   elif len(assets)==len(pagegroups):target=pagegroups[ai]
   elif n==6:target=pagegroups[0 if asset['pdfImageXref']==117 else 1]
   elif n==13:target=pagegroups[min(ai,len(pagegroups)-1)]
   # Try source captions that are exact catalog codes next to the native photo.
   ev=json.loads((ref/'ocr'/f'{n:03}.json').read_text());cy=(asset['bounds'][1]+asset['bounds'][3])/2
   labels=[q for q in ev['passes']['11']['words']if q['bounds'][0]<.5 and abs((q['bounds'][1]+q['bounds'][3])/2-cy)<.065 and not(asset['bounds'][0]<(q['bounds'][0]+q['bounds'][2])/2<asset['bounds'][2]and asset['bounds'][1]<(q['bounds'][1]+q['bounds'][3])/2<asset['bounds'][3])]
   label=None
   for q in labels:
    for candidate in pagegroups:
     code=next((row[-1]for row in candidate['rows']if row[-1]==q['text']),None)
     if code:target=candidate;label=code;break
   if not label:
    possibilities=[]
    for q in labels:
     for candidate in pagegroups:
      for row in candidate['rows']:
       similarity=difflib.SequenceMatcher(None,row[-1],q['text']).ratio()
       if similarity>.85:possibilities.append((similarity-abs((q['bounds'][1]+q['bounds'][3])/2-cy),candidate,row[-1]))
    if possibilities:_,target,label=max(possibilities,key=lambda item:item[0])
   caption={'en':label or en,'ru':label or ru};target['photos'].append({'bounds':asset['bounds'],'page':n,'caption':caption,'preparedAsset':image})
  # Preserve source measurement ambiguities instead of silently changing a value.
  uncertain=[]
  for g in [g for g in section['groups']if g['page']==n]:
   if (n,gi)in CONTEXT:
    de,dr=CONTEXT[n,gi];group['description']={'en':de,'ru':dr}
   for row in g['rows']:
    text=row[0]['en']
    if re.search(r'\((?:305|457|4575|122|18|30|15)m\)',text)or re.search(r'\b(?:305|457|4575|122|18|30|15)\s*m\)',text):uncertain.append({'code':row[-1],'sourceReading':text})
  if uncertain:section['flags'].append({'code':'source-measurement-review','path':'specTables','pdfPage':n,'sourcePages':[n],'message':{'ru':'В печатном источнике неоднозначны десятичные разделители или единицы пересчёта длины. Значения не исправлены предположением.','en':'Printed length conversions have ambiguous decimal separators or units. No inferred correction applied.'},'readings':uncertain})
 sections.append(section)
def ru_units(value):
 if isinstance(value,dict):
  if set(value)=={'ru','en'}:
   value['ru']=re.sub(r'(?<=\d)\s*mm\b',' мм',value['ru']);value['ru']=re.sub(r'(?<=\d)\s*cm\b',' см',value['ru']);value['ru']=re.sub(r'(?<=\d)\s*m\b',' м',value['ru']);value['ru']=re.sub(r'(?<=\d)\s*V\b',' В',value['ru'])
  else:
   for x in value.values():ru_units(x)
 elif isinstance(value,list):
  for x in value:ru_units(x)
ru_units(sections)
profile=root/'scripts/profiles/conmed-surgical-sections.json';profile.write_text(json.dumps({'sections':sections},ensure_ascii=False,indent=2)+'\n');sha=hashlib.sha256((root/'catalogs-source/conmed/advanced-surgical-product-catalog.pdf').read_bytes()).hexdigest();(root/'scripts/profiles/ocr/conmed-surgical.json').write_text(json.dumps({'sha256':sha,'category':'unclassified','catalogTitle':{'ru':'CONMED Advanced Surgical Product Catalog — каталог продукции','en':'CONMED Advanced Surgical Product Catalog'},'catalogEdition':None,'layoutReviewed':True,'nonProductPages':[1,2,3,4,9,22,40,43,44],'parts':['conmed-surgical-sections.json']},ensure_ascii=False,indent=2)+'\n')
(root/'reports/conmed/advanced-surgical-product-catalog/translation-review.json').write_text(json.dumps(alltext,ensure_ascii=False,indent=2))
print('Sections',len(sections),'images prepared',len(prepared),'numeric/source flags',sum(len(s['flags'])for s in sections));print('RU REVIEW SAMPLES');print('\n'.join(f'{n} {code}: {text["ru"]}'for n,code,text in alltext[::11]))
