"""Reconcile HALL bur matrices by physical columns, including adjacent independent grids."""
import json,re,collections,hashlib,sys
from pathlib import Path
import pymupdf as fitz
from PIL import Image
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';O=R/'public/images/products/conmed/hall/drawings';PAGES={56,57,58,64,65,66,67,68,74,75,77}
TITLES={'Round Fluted':'Шаровидные боры с режущими гранями','Fine Round Diamond':'Шаровидные боры с мелкозернистым алмазным покрытием','Coarse Round Diamond':'Шаровидные боры с крупнозернистым алмазным покрытием','Wire Pass Burs':'Боры для проведения проволоки','Swanson Reamers':'Римеры Swanson','Dermabraders – Fine Diamond':'Дермабразивные насадки с мелкозернистым алмазным покрытием','Straight Side – Cutting Burs':'Прямые боры с боковым резанием','Tapered Side-cutting':'Конусные боры с боковым резанием','Oval Burs':'Овальные боры','Barrel Burs':'Бочковидные боры','Lindemann Burs':'Боры Линдеманна','Cylindrical':'Цилиндрические боры','Cone Burs':'Конусные боры','Tapered Cross-cut Fissure Burs':'Конусные фиссурные боры с поперечной насечкой','Heavy Grit Diamond- Microbur. X-Long':'Удлинённый микробор с крупнозернистым алмазным покрытием','Side Cutting, Burs':'Боры с боковым резанием','Side Cutting Burs':'Боры с боковым резанием','Fluted Cylindrical Burs':'Цилиндрические боры с режущими гранями','Fine Diamond Cylindrical Burs':'Цилиндрические боры с мелкозернистым алмазным покрытием','Fluted Acorn Burs':'Жёлудевидные боры с режущими гранями','Trephine Burs':'Трепанационные боры','Oval Fluted Burs':'Овальные боры с режущими гранями','Carbide Metal Cutting Burs':'Твердосплавные боры для обработки металла','Wire Pass Burs – Depth Limiting':'Боры для проведения проволоки с ограничением глубины','LSO Round Fluted':'Шаровидные боры LSO с режущими гранями','Wirepass burs':'Боры для проведения проволоки','Neuro Burs':'Нейрохирургические боры','Helical Bur for E9010 Drill':'Спиральный бор для дрели E9010','E9010 Lindemann Bur':'Бор Линдеманна для E9010','E9010 Side Cutting Burs':'Боры с боковым резанием для E9010','Fluted Round Burs':'Шаровидные боры с режущими гранями','Fine Diamond Round Burs':'Шаровидные боры с мелкозернистым алмазным покрытием'}
FIELDS={'Guard':'Совместимый защитный тубус','Diameter':'Диаметр','Flutes':'Режущие грани','Bur Head Length':'Длина головки бора','Length':'Длина','Working Length':'Рабочая длина','Grit':'Зернистость'}
def bi(ru,en=None):return {'ru':str(ru),'en':str(ru if en is None else en)}
def text(c):
 reads=[re.sub(r'\s+',' ',v).strip()for v in c['texts'].values()];off=re.sub(r'\s+',' ',c['officialText']).strip();counter=collections.Counter(v for v in reads if v);return off if off and off in counter else counter.most_common(1)[0][0]if counter else''
def clean(s):return re.sub(r'\s+',' ',s).strip()
def field(s):
 s=clean(s);flat=re.sub(r'[^A-Za-z]','',s).lower()
 if 'diameter'in flat:return'Diameter'
 if 'flutes'in flat:return'Flutes'
 if 'grit'in flat:return'Grit'
 if 'burhead'in flat and 'length'in flat:return'Bur Head Length'
 if 'length'in flat:return'Length'
 return None

def refine(profile):
 D=fitz.open(R/'catalogs-source/conmed/hall-powered-instruments.pdf');layouts={n:json.loads((F/'layout'/f'{n:03}.json').read_text())for n in PAGES};vpath=F/'verification.json';verification=json.loads(vpath.read_text());records={r['id']:r for r in verification['records']};exclusions={f'058-020-{i:02}':'Abrasive grit range is a parameter, not a catalog number'for i in range(2,7)};exclusions['058-005-05']='Compatible bur guard for the adjacent cylindrical-bur matrix, not another orderable bur'
 for ident,reason in exclusions.items():records[ident]['excludedReason']=reason
 vpath.write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n');audit=[];newassets={}
 def drawing(n,b,name,caption):
  suffix=hashlib.sha256(json.dumps(b).encode()).hexdigest()[:8];path=O/f'bur-reviewed-{n}-{name}-{suffix}.webp'
  if not path.exists():
   p=D[n-1];rect=fitz.Rect(b[0]*p.rect.width,b[1]*p.rect.height,b[2]*p.rect.width,b[3]*p.rect.height);pix=p.get_pixmap(matrix=fitz.Matrix(600/72,600/72),clip=rect,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(path,lossless=True)
  else:im=Image.open(path)
  a={'src':'/images/products/conmed/hall/drawings/'+path.name,'width':im.width,'height':im.height,'imageType':'scene','drawing':True,'pdfPage':n,'bounds':b,'captionFree':True,'backgroundRemoval':'not applied: source line art preserved','imageCaption':caption};newassets[a['src']]=a;return a
 for s in profile['systems']:
  new=[]
  for n in s['sourcePages']:
   old=[t for t in s['specTables']if t['sourcePages']==[n]]
   if n not in PAGES:new.extend(old);continue
   bands=layouts[n]['bands'];headings=[]
   for b in bands:
    found=[]
    for ci,c in enumerate(b['cells']):
     name=clean(c['officialText']or c['texts']['Vision'])
     if name not in TITLES:continue
     left=c['bounds'][0]
     if ci and c['bounds'][2]-left<1.5*(b['cells'][ci-1]['bounds'][2]-b['cells'][ci-1]['bounds'][0]):left=b['cells'][ci-1]['bounds'][0]
     found.append({'name':name,'left':left,'top':b['bounds'][1],'bottom':b['bounds'][3],'right':b['bounds'][2],'band':b})
    for i,h in enumerate(found):
     if i+1<len(found):h['right']=found[i+1]['left']
     headings.append(h)
   if n==75:headings.append({'name':'Wirepass burs','left':.315,'right':.812,'top':.16,'bottom':.204,'band':bands[0]})
   groups={}
   for t in old:
    for row,source in zip(t['rows'],t['rowSources']):
     ident=source['codeEvidence'][0]['id']
     if ident in exclusions:continue
     b=source['bounds'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;eligible=[h for h in headings if h['top']<cy and h['left']-.005<=cx<=h['right']+.005]
     assert eligible,(n,ident,cx,cy);h=max(eligible,key=lambda h:h['top']);name=h['name'];values={};evidence={};guard=''
     body=next(bb for bb in bands if any(c.get('id')==ident for c in bb['cells']))
     for c in body['cells']:
      cb=c['bounds'];v=text(c)
      if cb[2]<=b[0]+.003 and cb[0]>=h['left']-.02 and re.search(r'1375-|7020-|E9011-',v):guard=v
     if n==77:
      guard='';working=text(body['cells'][0]);values['Working Length']=working;evidence['Working Length']=body['cells'][0]['bounds']
     else:values['Guard']=guard
     for hb in sorted(bands,key=lambda bb:-bb['bounds'][1]):
      if not h['top']<=hb['bounds'][1]<b[1]-.001:continue
      vc=next((c for c in hb['cells']if c['bounds'][0]-.001<=cx<=c['bounds'][2]+.001),None)
      if not vc or(vc.get('id')and not records.get(vc['id'],{}).get('excludedReason')):continue
      v=text(vc)
      if not v or re.search(r'[A-Za-z]{2,}',v)and not re.fullmatch(r'\d+\s*Type',v):continue
      labels=[c for c in hb['cells']if c['bounds'][0]<cx and c['bounds'][2]>=h['left']-.01 and field(c['officialText']or c['texts']['Vision'])]
      label=field((labels[-1]['officialText']or labels[-1]['texts']['Vision']))if labels else None
      if n==75 and name=='Wirepass burs'and .20<hb['bounds'][1]<.23:label='Diameter'
      if label and label not in values:values[label]=v;evidence[label]=vc['bounds']
     # A few adjacent grids omit horizontal rule segments: pair source OCR labels and numbers spatially.
     for label in layouts[n]['vision']:
      lb=label['bounds'];kind=field(label['text'])
      if not kind or kind in values or not(h['top']<=lb[1]<b[1] and h['left']-.01<=lb[0]<b[0]):continue
      nums=[a for a in layouts[n]['vision']if b[0]-.003<=(a['bounds'][0]+a['bounds'][2])/2<=b[2]+.003 and abs((a['bounds'][1]+a['bounds'][3])/2-(lb[1]+lb[3])/2)<.011 and re.fullmatch(r'\d+(?:\.\d+)?',a['text'])]
      if nums:
       value=nums[0]['text'];values[kind]=value;evidence[kind]=nums[0]['bounds']
     gid=f'page-{n:03}-'+re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-');group=groups.setdefault(gid,{'name':name,'entries':[]});dc=next((c for c in h['band']['cells']if c['bounds'][0]<=cx<=c['bounds'][2]),None);image=None
     if dc and not re.search(r'N\s*/\s*A',dc['officialText']or dc['texts']['Vision'],re.I):
      db=dc['bounds'];image=drawing(n,[db[0]+.002,db[1]+.001,db[2]-.002,db[3]-.001],row[1],bi(TITLES[name],name))
     group['entries'].append({'row':row,'source':source,'values':values,'image':image});audit.append({'id':ident,'code':row[1],'pdfPage':n,'subgroup':name,'parameters':values,'parameterBounds':evidence})
   for gid,g in groups.items():
    fields=[k for k in FIELDS if any(e['values'].get(k)for e in g['entries'])];cols=[bi('Наименование','Description'),bi('Кат. №','Cat. No.')]+[bi(FIELDS[k]+(' (мм)'if k in ['Diameter','Bur Head Length','Length','Working Length']else''),('Compatible Bur Guard'if k=='Guard'else k)+(' (mm)'if k in ['Diameter','Bur Head Length','Length','Working Length']else''))for k in fields];nt={'id':gid,'groupId':gid,'title':bi(TITLES[g['name']],g['name']),'unit':'mm','columns':cols,'rows':[],'rowSources':[],'rowImages':[],'rowDimensions':[],'images':[],'sourcePages':[n]}
    for entry in g['entries']:
     values=entry['values'];params=[bi('Тип '+v.split()[0],v)if re.fullmatch(r'\d+\s*Type',v)else bi(re.sub(r'\bor\b','или',re.sub(r'\band\b','и',v)),v)for v in [values.get(k,'')for k in fields]];nt['rows'].append([bi(TITLES[g['name']],g['name']),entry['row'][1],*params]);source=entry['source'];source['codeEvidence']=[{**e,'tableId':gid,'row':len(nt['rows'])}for e in source['codeEvidence']];nt['rowSources'].append(source);nt['rowImages'].append(entry['image']);nt['rowDimensions'].append({'width':values.get('Diameter',''),'length':values.get('Length',values.get('Working Length',values.get('Bur Head Length','')))})
     if entry['image']:s['imageDimensions'][entry['image']['src']]={'width':entry['image']['width'],'height':entry['image']['height']}
    new.append(nt)
  s['specTables']=new;s['refCodes']=list(dict.fromkeys(row[1]for t in new for row in t['rows']));s['reviewFlags']=[f for f in s['reviewFlags']if f['code']!='source-dimension-conflict'];imgs=[a for t in new for a in t.get('images',[])];draws=[a for t in new for a in t.get('rowImages',[])if a];s['gallery']=list({a['src']:a for a in imgs or draws}.values())[:8]
  if s['gallery']:a=s['gallery'][0];s['heroImage']=a['src'];s['imageType']='cutout'if a.get('drawing')else a['imageType']
 profile['assets']=list({a['src']:a for a in profile['assets']+list(newassets.values())}.values());(F/'bur-matrix-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');return profile
if __name__=='__main__':
 p=R/'scripts/profiles/conmed-hall-powered-instruments.json';profile=refine(json.loads(p.read_text()));from hall_source_review import apply
 profile=apply(profile);p.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
 for s in profile['systems']:
  path=R/'content/products/conmed'/(s['slug']+'.json');old=json.loads(path.read_text())
  for k in ['specTables','refCodes','relatedSystemSlugs','imageDimensions','gallery','heroImage','imageType']:old[k]=s[k]
  old['review']['flags']=s['reviewFlags'];path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
 print('Reviewed bur rows; total ordering rows',sum(len(t['rows'])for s in profile['systems']for t in s['specTables']))
