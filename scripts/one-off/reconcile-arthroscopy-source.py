#!/usr/bin/env python3
"""Use provided-source OCR item lines as the primary inventory; official edition supplies corroboration only."""
import json,re,pathlib,difflib,copy,collections
from PIL import Image
R=pathlib.Path(__file__).resolve().parents[1];F=R/'reports/conmed/arthroscopy-product-catalog';out=F/'layout-source';out.mkdir(exist_ok=True);allrecords=[];omissions=[];unassigned=[];officialtext=(F/'official/text.txt').read_text();sourceRef=R/'public/catalogs/conmed/arthroscopy-product-catalog'
def norm(s):return s.strip(' .,:;|_').replace('®','').replace('™','')
def cleaned(s):return re.sub(r'[^a-z0-9]','',s.lower())
for f in sorted((F/'layout').glob('*.json')):
 page=json.loads(f.read_text());n=page['pdfPage'];vision=json.loads((F/'vision'/f'{n:03}.json').read_text());e=json.loads((sourceRef/'ocr'/f'{n:03}.json').read_text());candidates=[];expected=[]
 for gi,g in enumerate(page['groups']):
  for ri,row in enumerate(g['rows']):
   for ci,c in enumerate(row['codes']):expected.append({'gi':gi,'ri':ri,'ci':ci,'code':c['candidate'],'row':row})
 known={x['code']for x in expected}
 for vi,line in enumerate(vision):
  text=line['text'];b=line['bounds'];tokens=text.split()
  if not .12<b[1]<.915 or not tokens or 'Customer Service' in text:continue
  raw=norm(tokens[-1]);raw=re.sub(r'^[^A-Za-z0-9]+','',raw)
  if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.*-]*',raw):continue
  if not ((any(c.isdigit()for c in raw)and len(raw)>=4)or raw in known):continue
  if re.search(r'(mm|cm|rpm|kg|lbs|oz|ml|Volt|Box|Pk)$',raw,re.I):continue
  if raw not in known and max([difflib.SequenceMatcher(None,raw,c).ratio()for c in known]+[0])<.65:continue
  # Caption/model tokens alone need a neighboring item description or printed dotted leader.
  codeOnly=len(tokens)<=2 or bool(re.fullmatch(r'[. …]*'+re.escape(raw),text.strip()))
  if not codeOnly and not re.search(r'\.{2,}|…',text):continue
  if b[2]<.35:continue
  candidates.append({'visionIndex':vi,'text':raw,'line':text,'bounds':b,'confidence':line['confidence']})
 # Recover item codes omitted by Vision only when both independent 600-DPI Tesseract passes print the exact code in the catalog-number column.
 for code in known:
  if any(c['text']==code for c in candidates):continue
  matches=[]
  for mode in ['3','11']:
   matches.append([w for w in e['passes'][mode]['words']if norm(w['text'])==code and .12<w['bounds'][1]<.915 and w['bounds'][0]>.35])
  pairs2=[(a,b)for a in matches[0]for b in matches[1]if abs(a['bounds'][1]-b['bounds'][1])<.006 and abs(a['bounds'][0]-b['bounds'][0])<.015]
  if pairs2:
   a,b=pairs2[0];already=any(abs(c['bounds'][1]-a['bounds'][1])<.008 and difflib.SequenceMatcher(None,c['text'],code).ratio()>.7 for c in candidates)
   if not already:candidates.append({'visionIndex':None,'text':code,'line':'','bounds':a['bounds'],'confidence':0,'sourceTesseractRecovery':True})
 # Deduplicate the same printed code repeated in photo captions, favor dotted source item lines.
 unique={}
 for c in candidates:
  k=c['text'];score=(2 if re.search(r'\.{2,}',c['line'])else 0)+(1 if c['bounds'][2]>.75 else 0)
  if k not in unique or score>unique[k][0]:unique[k]=(score,c)
 candidates=[v[1]for v in unique.values()]
 # One-to-one matches prevent an extra official-edition row from consuming another printed source item.
 pairs=[]
 for i,c in enumerate(candidates):
  b=c['bounds'];cy=(b[1]+b[3])/2
  context=' '.join(l['text']for l in vision if abs((l['bounds'][1]+l['bounds'][3])/2-cy)<.012 and l['bounds'][0]<b[0]-.01)
  c['sourceDescriptionOCR']=context
  for j,x in enumerate(expected):
   ratio=difflib.SequenceMatcher(None,c['text'],x['code']).ratio()
   if ratio<.65:continue
   desc=difflib.SequenceMatcher(None,cleaned(context),cleaned(x['row']['description'])).ratio()if context else 0
   pairs.append((ratio*5+desc*.4,i,j))
 usedc=set();usede=set();assign={}
 for score,i,j in sorted(pairs,reverse=True):
  if i in usedc or j in usede:continue
  usedc.add(i);usede.add(j);assign[j]=candidates[i]
 # Match is a proposal; acceptance requires independent source OCR agreement, not official similarity.
 groups=[];im=None
 for gi,g in enumerate(page['groups']):
  ng=copy.deepcopy(g);ng['rows']=[];ng['columnCount']=max([len(r['codes'])for r in g['rows']]+[1])
  for ri,row in enumerate(g['rows']):
   codes=[];rowbounds=[];rowEvidence=[]
   for ci,old in enumerate(row['codes']):
    ei=next(i for i,x in enumerate(expected)if x['gi']==gi and x['ri']==ri and x['ci']==ci)
    if ei not in assign:
     omissions.append({'pdfPage':n,'description':row['description'],'officialCandidate':old['candidate'],'reason':'Not matched to an item line in supplied-source OCR; official-edition item not imported'});continue
    c=assign[ei];b=c['bounds'];cy=(b[1]+b[3])/2;readings=[]
    for mode in ['3','11']:
     words=[w for w in e['passes'][mode]['words']if abs((w['bounds'][1]+w['bounds'][3])/2-cy)<.008 and w['bounds'][2]>max(b[0]-.02,.36)and w['bounds'][0]<b[2]+.012]
     readings.append({'reader':'Tesseract-600dpi-PSM'+mode,'text':' '.join(w['text']for w in sorted(words,key=lambda w:w['bounds'][0])),'confidence':min((w['confidence']for w in words),default=0)})
    readings.append({'reader':'Apple-Vision-accurate','text':c['line'],'confidence':c['confidence']})
    def has(t,val):return any(norm(x)==val for x in re.split(r'\s+|\.{2,}',t))
    # Prefer the official exact spelling only when two independent source readers agree with it.
    options=[old['candidate'],c['text']];counts={v:sum(has(r['text'],v)for r in readings)for v in options};best=max(options,key=lambda v:counts[v]);agreed=counts[best]>=2 and best==old['candidate'] and not c.get('sourceTesseractRecovery');value=best if agreed else None
    ident=f'{n:03}-{len(groups)+1:02}-{len(ng["rows"])+1:02}-{len(codes)+1}';rb=[min(.095,b[0]),max(.12,cy-.013),min(.96,b[2]+.01),min(.92,cy+.009)];code={'printedColumn':ci,'candidate':best,'sourceBounds':b,'officialCode':old['candidate'],'officialBounds':old['officialBounds']};codes.append(code);rowbounds.append(rb)
    found=bool(re.search(r'(?<![A-Za-z0-9-])'+re.escape(best)+r'(?![A-Za-z0-9-])',officialtext));crop=F/'line-crops-source'/(ident+'.png');crop.parent.mkdir(exist_ok=True)
    if im is None:im=Image.open(sourceRef/'ocr'/f'{n:03}-600dpi.png').convert('RGB');w,h=im.size
    im.crop([int(rb[0]*w),int(rb[1]*h),int(rb[2]*w),int(rb[3]*h)]).save(crop)
    allrecords.append({'id':ident,'pdfPage':n,'groupIndex':len(groups),'rowIndex':len(ng['rows']),'columnIndex':len(codes)-1,'expectedOfficialCode':old['candidate'],'candidate':best,'value':value,'sourceDescription':row['description'],'sourceDescriptionOCR':c['sourceDescriptionOCR'],'sourceBounds':b,'rowBounds':rb,'readings':readings,'matchedReaders':[r['reader']for r in readings if has(r['text'],best)],'verificationStatus':'verified (independent OCR readers)'if agreed else'requires visual source reading','officialEvidence':[{'url':'https://www.conmed.com/-/media/conmed/documents/catalog/arthroscopy_catalog.ashx#page='+str(page['officialPage']),'code':best,'officialPdfPage':page['officialPage']}]if found else[],'lineCrop':str(crop.relative_to(R))})
   if codes:
    nr=copy.deepcopy(row);nr['codes']=codes;nr['rowBounds']=[min(x[0]for x in rowbounds),min(x[1]for x in rowbounds),max(x[2]for x in rowbounds),max(x[3]for x in rowbounds)];ng['rows'].append(nr)
  if ng['rows'] or n==69:groups.append(ng)
 for i,c in enumerate(candidates):
  if i not in usedc:unassigned.append({'pdfPage':n,**c})
 page['groups']=groups;page['dottedRows']=sum(len(g['rows'])for g in groups);(out/f.name).write_text(json.dumps(page,ensure_ascii=False,indent=2)+'\n')
report={'found':len(allrecords),'verified':sum(r['value']is not None for r in allrecords),'confirmedOnConmedCom':sum(bool(r['officialEvidence'])for r in allrecords),'flagged':sum(r['value']is None for r in allrecords),'records':allrecords}
(F/'verification-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(F/'official-edition-exclusions.json').write_text(json.dumps({'excludedOfficialItems':omissions,'unassignedSourceTokens':unassigned},ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in report.items()if k!='records'});print('excluded',len(omissions),'unassigned',len(unassigned))
