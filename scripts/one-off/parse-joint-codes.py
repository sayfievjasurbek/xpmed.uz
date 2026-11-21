"""Independent 600-DPI code readers with audited, table-aware confusion candidates."""
import json,re,collections,io
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/joint-catalogue';O=R/'public/catalogs/double-medical/joint-catalogue/ocr';PAT=re.compile(r'(?<![A-Za-z0-9])([1I4][A-Z0-9]{7,9})(?![A-Za-z0-9])');DENSE=set(range(17,30));allrecords=[];blanks=[]
def normalized(code,n):
 c=list(code.upper());expected=10 if n<40 else 9
 if len(c)!=expected:return ''.join(c)
 if n<40:c[-1]='S'
 letters={2}if n in range(28,40)and n not in [30,31]else set()
 for i in range(expected-(n<40)):
  if i in letters:continue
  c[i]={'O':'0','I':'1','L':'1','Z':'2','B':'8','G':'6','S':'5'}.get(c[i],c[i])
 return ''.join(c)
for n in range(4,96):
 j=json.loads((O/f'{n:03}.json').read_text());vision=json.loads((F/'vision'/f'{n:03}.json').read_text());readers={'PSM3':j['passes']['3']['words'],'PSM11':j['passes']['11']['words'],'Vision':vision};candidates=[]
 for reader,words in readers.items():
  for w in words:
   b=w['bounds']
   if not .065<b[1]<.92:continue
   for m in PAT.finditer(w['text']):
    code=m.group(1);x=b[0]+(b[2]-b[0])*m.start()/max(1,len(w['text']));x1=b[0]+(b[2]-b[0])*m.end()/max(1,len(w['text']))
    if x>.44:continue
    box=[x,b[1],x1,b[3]];cy=(b[1]+b[3])/2;candidates.append({'reader':reader,'text':code,'line':w['text'],'confidence':w.get('confidence'),'bounds':box,'cy':cy})
 groups=[]
 for c in sorted(candidates,key=lambda c:(c['cy'],c['bounds'][0],c['reader'])):
  g=next((g for g in groups if abs(g['cy']-c['cy'])<(.003 if n in DENSE else .005)and abs(g['bounds'][0]-c['bounds'][0])<.07 and c['reader']not in [x['reader']for x in g['readings']]),None)
  if g:g['readings'].append(c)
  else:groups.append({'cy':c['cy'],'bounds':c['bounds'],'readings':[c]})
 # Multiple partial-word aliases at the same position are retained as alternatives of one printed item.
 merged=[]
 for g in groups:
  near=next((h for h in merged if abs(h['cy']-g['cy'])<.0025 and abs(h['bounds'][0]-g['bounds'][0])<.035),None)
  if near:near['readings']+=g['readings']
  else:merged.append(g)
 for k,g in enumerate(sorted(merged,key=lambda g:(g['cy'],g['bounds'][0]))):
  norms=collections.defaultdict(set)
  for c in g['readings']:norms[normalized(c['text'],n)].add(c['reader'])
  candidate=max(norms,key=lambda x:(len(norms[x]),x.endswith('S')if n<40 else len(x)==9));agree=norms[candidate];ok=len(agree)>=2 and 'Vision'in agree;source=next((c['bounds']for c in g['readings']if c['reader']=='PSM3'),g['bounds']);r={'id':f'{n:03}-{k+1:03}','pdfPage':n,'sourceBounds':source,'candidate':candidate,'value':candidate if ok else None,'readings':g['readings'],'matchedReaders':sorted(agree),'verificationStatus':'verified (three-reader comparison with table-pattern candidates)'if ok else'requires visual review','printedPrefixException':n in [28,29,32,33,34,35,36,37,38,39]};allrecords.append(r)
 if not merged:blanks.append(n)
(F/'verification.json').write_text(json.dumps({'records':allrecords,'found':len(allrecords),'verified':sum(bool(r['value'])for r in allrecords),'blankPages':blanks},ensure_ascii=False,indent=2));print('Found',len(allrecords),'verified',sum(bool(r['value'])for r in allrecords),'flagged',sum(not r['value']for r in allrecords),'blank',blanks)
(F/'line-crops').mkdir(exist_ok=True)
flagged=[r for r in allrecords if not r['value']]
for n in sorted({r['pdfPage']for r in flagged}):
 im=Image.open(O/f'{n:03}-600dpi.png');w,h=im.size
 for r in flagged:
  if r['pdfPage']!=n:continue
  b=r['sourceBounds'];box=(max(0,int(b[0]*w)-10),max(0,int(b[1]*h)-6),min(w,int(b[2]*w)+12),min(h,int(b[3]*h)+6));crop=im.crop(box);path=F/'line-crops'/(r['id']+'.png');crop.save(path);r['lineCrop']=str(path.relative_to(R))
for start in range(0,len(flagged),40):
 sh=Image.new('RGB',(1800,8*130),'white');d=ImageDraw.Draw(sh)
 for k,r in enumerate(flagged[start:start+40]):
  im=Image.open(R/r['lineCrop']);im.thumbnail((350,95));x=k%5*360;y=k//5*130;sh.paste(im,(x,y+25));d.text((x+2,y+2),r['id']+' '+r['candidate'],fill='black')
 sh.save(f'/tmp/dm-joint/codes-{start//40}.png')
(F/'verification.json').write_text(json.dumps({'records':allrecords,'found':len(allrecords),'verified':sum(bool(r['value'])for r in allrecords),'blankPages':blanks},ensure_ascii=False,indent=2))
