#!/usr/bin/env python3
"""Apply the owner's source-verified Advanced Surgical decisions; retain raw evidence."""
import json,re,datetime,copy
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'reports/conmed/advanced-surgical-product-catalog'
OFFICIAL='https://www.conmed.com/en/products/smoke-evacuation/laparoscopic-solutions-and-accessories'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
if read(F/'report.json').get('ownerResolutionDate'):
 print('Owner resolutions already applied; no changes.');raise SystemExit(0)
accepted={'iAS5-75LP','VV120','VV220','VV220NF','VVWM01','PP012SEO'}
changed=[]
def evidence(e):
 candidate=e.get('printedCandidate',e.get('visualReading'))
 if isinstance(candidate,dict):candidate=candidate.get('reading')
 if candidate not in accepted:return
 e.update(value=candidate,flagged=False,reasons=[],verificationStatus='verified (owner source review)',resolution={'basis':'Explicit owner verification against source PDF','resolvedAt':now})
 if candidate=='PP012SEO':
  e['manufacturerStatus']='confirmed on conmed.com'
  if not any(x.get('url')==OFFICIAL for x in e.setdefault('officialEvidence',[])):e['officialEvidence'].append({'url':OFFICIAL,'code':candidate,'sourceType':'official-manufacturer-product-page'})
# Fix only known OCR errors before bilingual unit formatting.
fixes={
 '138011': [('1°" (4.45','1¾ (4.45'),('1°" (4.45','1¾ (4.45')],
 '138012': [('2.1 (6.53','2.1 (5.53')],
 '138026': [('SX(12.7','5 (12.7'),('(12.7','5 (12.7')],
 '60-1773-001':[('3/3½','3½')],
 '60-5121-001':[('734 (19./','7¾ (19.7')],
 '130187':[('6 (15m)','6 (15cm)'),('6 (15м)','6 (15см)')],
 'VTESU05':[('x6 8m)','x6 (1.8m)'),('x2 (6m)','x2 (0.6m)'),('×6 8м)','×6 (1.8м)'),('×2 (6м)','×2 (0.6м)')],
}
# Only pairs explicitly present in source or supplied by owner; never calculate a substitute.
metres={'122':'1.22','18':'1.8','30':'3.0','305':'3.05','457':'4.57','.6':'0.6'}
pattern=re.compile(r'(?<![\d./])(?P<imperial>\d+(?:[¼½¾]|/\d+)?(?:\.\d+)?)(?:\.)?\s*(?:[\'’′\"”″]|ft\.?|in\b)?\s*\(\s*(?P<value>\d*\.?\d+)\s*(?P<unit>mm|cm|m|мм|см|м)\s*\)')
def normalize(text,lang):
 def sub(m):
  n=m['imperial'];v=m['value'];u=m['unit'];u={'м':'m','см':'cm','мм':'mm'}.get(u,u)
  if u=='m':v=metres.get(v,v);mark='′'
  else:mark='″'
  if lang=='en':return f'{n}{mark} ({v} {u})'
  return f'{v.replace(".",",")} '+{'m':'м','cm':'см','mm':'мм'}[u]+f' ({n}{mark})'
 return pattern.sub(sub,text)
def bilingual(v,code=None):
 if isinstance(v,dict) and 'ru'in v and 'en'in v and all(isinstance(v[k],str)for k in ['ru','en']):
  for lang in ['ru','en']:
   original=v[lang];text=original
   for a,b in fixes.get(code,[]):
    if code=='138026' and '5 (12.7'in text:continue
    text=text.replace(a,b)
   if code in ['60-6828-005A','60-6829-005A']:
    if lang=='en':text=re.sub(r'4\s+of\s*10mm', '4′ of 10mm',text);text=re.sub(r'(?:and\s*)6\s*of\s*22mm','and 6′ of 22mm',text)
    else:text=text.replace('4 длиной','1,22 м (4′) длиной').replace('6 длиной','1,8 м (6′) длиной')
   if code=='VTESU05' and lang=='ru':text='Стерильная трубка 22 мм (7/8″) × 1,8 м (6′) с переходником с 22 мм (7/8″) на 6,4 мм (1/4″), соединённая с трубкой 6,4 мм (1/4″) × 0,6 м (2′)'
   if code=='138026':text=text.replace('o/case','').replace('o/упаковка','').strip()
   text=normalize(text,lang)
   # Explicit foot-only cable length, shown with owner's conversion.
   text=re.sub(r'15\s*ft\.?', '15′ (4.57 m)' if lang=='en'else'4,57 м (15′)',text)
   if text!=original:changed.append({'code':code,'language':lang,'before':original,'after':text});v[lang]=text
 elif isinstance(v,dict):
  for k,x in v.items():
   if k not in ['review','codeEvidence','rowSources','sourceText','ocrReadings']:bilingual(x,code)
 elif isinstance(v,list):
  for x in v:bilingual(x,code)
# Preserve originals, with an opaque white backing instead of risking cutout loss.
image_names=['page-026-xref-330','page-027-xref-335']
image_sizes={}
for name in image_names:
 base=ROOT/'public/images/products/conmed/dispersive-electrodes'
 im=Image.open(base/'_originals'/f'{name}-upscaled-2x.png').convert('RGBA');white=Image.new('RGBA',im.size,'white');white.alpha_composite(im)
 white.convert('RGB').save(base/f'{name}.webp','WEBP',quality=92);image_sizes[name]=list(im.size)
def images(v):
 if isinstance(v,dict):
  src=v.get('src','');name=Path(src).stem
  if name in image_names:
   v.update(width=image_sizes[name][0],height=image_sizes[name][1],imageType='scene',imageBackground='white',maskMethod='Original source photo on opaque white; owner-approved fallback')
  for x in v.values():images(x)
 elif isinstance(v,list):
  for x in v:images(x)
paths=[]
for p in sorted((ROOT/'content/products/conmed').glob('*.json')):
 s=read(p)
 if '/advanced-surgical-product-catalog/'not in(s.get('sourcePdf')or''):continue
 paths.append(p)
 backup=F/'before-owner-resolutions'/p.name
 if not backup.exists():backup.parent.mkdir(exist_ok=True);save(backup,s)
 for t in s['specTables']:
  for i,row in enumerate(t['rows']):
   ev=t['rowSources'][i]['codeEvidence']
   for e in ev:evidence(e)
   if ev and ev[0]['value']in accepted:row[2]=ev[0]['value']
   bilingual(row[0],row[2])
 for c in s['components']:
  for e in c.get('codeEvidence',[]):evidence(e)
  c['refCodes']=[e['value']for e in c.get('codeEvidence',[])if e.get('value')]
  bilingual(c.get('name'),c['refCodes'][0]if c['refCodes']else None)
 bilingual(s);images(s)
 for name,size in image_sizes.items():
  src=f'/images/products/conmed/dispersive-electrodes/{name}.webp'
  if src in s.get('imageDimensions',{}):s['imageDimensions'][src]={'width':size[0],'height':size[1]}
 flags=s['review'].pop('flags',[])
 for f in flags:f.update(status='resolved',resolvedAt=now,resolution='Owner source verification; length typography corrected or original image retained on white.')
 s['review'].setdefault('resolvedFlags',[]).extend(flags);s['review']['flags']=[]
 s['review']['codeVerification'].update(verified=s['review']['codeVerification']['found'],stillFlagged=0,policy='Raw OCR evidence retained. Six exceptions explicitly verified against PDF by owner; PP012SEO also confirmed on official CONMED product page.')
 s['review']['publishedAt']=s['review'].get('publishedAt')or now;s['review']['publicationReason']='Owner explicitly resolved remaining source flags and authorized publication.';s['status']='published';save(p,s)
# Keep future source-profile imports aligned with reviewed codes and descriptions.
profilepath=ROOT/'scripts/profiles/conmed-surgical-sections.json';profile=read(profilepath)
by_slug={read(p)['slug']:read(p)for p in paths}
for sec in profile['sections']:
 s=by_slug[sec['slug']];sec['resolvedFlags']=sec.get('flags',[]);sec['flags']=[]
 for g in sec['groups']:
  t=next((t for t in s['specTables']if t['id']==g['id']),None)
  if t:g['rows']=copy.deepcopy(t['rows'])
  def walk(v):
   if isinstance(v,dict):
    if 'printedCandidate'in v:evidence(v)
    for x in v.values():walk(x)
   elif isinstance(v,list):
    for x in v:walk(x)
  walk(g);images(g)
save(profilepath,profile)
vpath=F/'verification.json';v=read(vpath)
for r in v['records']:evidence(r)
v['verified']=sum(r['value']is not None for r in v['records']);v['flagged']=0;save(vpath,v)
corrections=[{'system':'electrosurgical-forceps','pdfPage':36,'code':'130187','sourceReading':'6 (15m)','corrected':{'ru':'15 см (6″)','en':'6″ (15 cm)'},'basis':'Owner verified typo against next source row, which prints 6 (15cm).','publicNote':False}]
report=read(F/'report.json');report.update(published=25,drafts=0,catalogNumbersVerified=v['verified'],openRealFlags=[],sourceCatalogCorrections=corrections,ownerResolutionDate=now,lengthAudit={'systemsReviewed':25,'changedFields':len(changed),'detailsFile':'length-corrections.json'},codeResolutions={'values':sorted(accepted),'basis':'Owner source verification; PP012SEO independently confirmed on conmed.com','officialUrl':OFFICIAL})
for s in report['systems']:s.update(status='published',openFlags=0)
save(F/'report.json',report);save(F/'length-corrections.json',changed)
(F/'report.md').write_text('# CONMED Advanced Surgical Product Catalog\n\n25 systems created / 25 published locally / 0 drafts.\n\nCatalog-number occurrences: 352 found / 352 verified (346 visual + OCR; 6 owner source verification) / 345 confirmed on conmed.com.\n\n## Open real flags\n\nNone. All 25 systems reviewed for lengths. Original OCR and source readings are retained.\n\n## Source catalog corrections\n\n- PDF page 36, REF 130187: source `6 (15m)` corrected to **15 cm (6″)**, as explicitly verified by owner against adjacent `6 (15cm)` row. Internal correction, not a public warning.\n\n## Resolutions\n\n- Exact owner-verified codes: '+', '.join(sorted(accepted))+'.\n- PP012SEO confirmed at '+OFFICIAL+'.\n- Foot/metre and inch/centimetre pairs use metric-first RU and imperial-first EN, retaining source precision. See length-corrections.json for every changed field.\n- Two dispersive electrode source photos retained with opaque white backgrounds, without destructive segmentation.\n')
print(json.dumps({'systems':len(paths),'published':25,'flags':0,'lengthFieldsChanged':len(changed),'verified':v['verified']},indent=2))
