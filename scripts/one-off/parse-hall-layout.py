"""Extract source cells and their independent readings; never substitute official values for source text."""
import json,re,sys,collections,math
from pathlib import Path
import pymupdf as f,numpy as np
from PIL import Image
from hall_grid import source_bands
from hall_sections import SECTIONS,MATRIX_BLADES,ROW_BLADES,BUR_MATRICES
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments';D=f.open(R/'catalogs-source/conmed/hall-powered-instruments.pdf');OFF=f.open(F/'official/logical.pdf');maps={r['pdfPage']:r for r in json.loads((F/'page-mapping.json').read_text())};(F/'layout').mkdir(exist_ok=True);(F/'line-crops').mkdir(exist_ok=True)
PAT=re.compile(r'(?<![A-Za-z0-9])(?:[A-Z]{0,6}\d{2,6}(?:-[A-Z0-9]{2,8})+|[A-Z]{1,6}\d{2,6}[A-Z]{0,6})(?![A-Za-z0-9])')
def codes(text):return [m.group()for m in PAT.finditer(text)if not re.fullmatch(r'\d{4}-\d{2}X',m.group())]
def clean(t):return re.sub(r'\s+',' ',t).strip(' |;')
def inside(b,cell):return cell[0]<=(b[0]+b[2])/2<=cell[2]and cell[1]<=(b[1]+b[3])/2<=cell[3]
def cell_text(reader,cell):
 arr=[]
 for line in reader:
  if inside(line['bounds'],cell):arr.append(line);continue
  # Vision merges adjacent equal-font codes. Their ordinal positions stay separate.
  if line.get('reader')=='Vision'and line['bounds'][1]<cell[3]and line['bounds'][3]>cell[1]and line['bounds'][0]<cell[2]and line['bounds'][2]>cell[0]:
   matches=list(PAT.finditer(line['text']))
   if len(matches)>1:
    for m in matches:
     b=line['bounds'];cx=b[0]+(b[2]-b[0])*(m.start()+m.end())/(2*len(line['text']))
     if cell[0]<=cx<=cell[2]:arr.append({**line,'text':m.group()})
 return clean(' '.join(x['text']for x in sorted(arr,key=lambda x:(round(x['bounds'][1],3),x['bounds'][0]))))
def num(t):
 t=clean(t).replace('mm','').strip()
 return t if re.fullmatch(r'\d+(?:[.,]\d+)?',t)else''
allrecords=[]
for n in range(8,79):
 page=D[n-1];w,h=page.rect.width,page.rect.height;e=json.loads((R/f'public/catalogs/conmed/hall-powered-instruments/ocr/{n:03}.json').read_text());v=json.loads((F/'vision'/f'{n:03}.json').read_text())if(F/'vision'/f'{n:03}.json').exists()else[];readers={'PSM3':e['passes']['3']['words'],'PSM11':e['passes']['11']['words'],'Vision':[{**x,'reader':'Vision'}for x in v]};m=maps[n];pn=27 if n==25 else m['officialPage'];op=OFF[pn-1];M=np.array(m['alignment']);ow=[]
 for word in op.get_text('words'):
  p0=np.array([word[0]/op.rect.width,word[1]/op.rect.height,1])@M.T;p1=np.array([word[2]/op.rect.width,word[3]/op.rect.height,1])@M.T;ow.append({'text':word[4],'bounds':[p0[0],p0[1],p1[0],p1[1]]})
 bands=source_bands(page);filtered=[]
 for b in bands:
  if any(a is not b and a['top']<=b['top']-.3 and a['bottom']>=b['bottom']+.3 and a['xs'][0]<=b['xs'][0]and a['xs'][-1]>=b['xs'][-1]for a in bands):continue
  cells=[]
  for ci,(x0,x1)in enumerate(zip(b['xs'],b['xs'][1:])):
   box=[x0/w,b['top']/h,x1/w,b['bottom']/h];texts={key:cell_text(rr,box)for key,rr in readers.items()};official=cell_text(ow,box);candidates=collections.Counter(c for text in texts.values()for c in set(codes(text)));oc=codes(official);candidate=next((c for c in oc if c in candidates),candidates.most_common(1)[0][0]if candidates else None)
   if candidate and n in ROW_BLADES and ci>0:candidate=None
   if candidate and n in BUR_MATRICES and ci==0:candidate=None
   cell={'bounds':box,'texts':texts,'officialText':official,'candidate':candidate,'officialCandidates':oc}
   if candidate:
    agree=[key for key,text in texts.items()if candidate in codes(text)];cell['value']=candidate if len(agree)>=2 and 'Vision'in agree else None;cell['matchedReaders']=agree
    ident=f'{n:03}-{len(filtered)+1:03}-{ci+1:02}';cell['id']=ident;record={'id':ident,'pdfPage':n,'candidate':candidate,'value':cell['value'],'sourceBounds':box,'readings':[{'reader':key,'text':text}for key,text in texts.items()],'matchedReaders':agree,'verificationStatus':'verified (three-reader comparison)'if cell['value']else'requires visual reading','officialEvidence':[{'url':'https://www.conmed.com/-/media/conmed/documents/catalog/hallpoweredinstruments_catalog.ashx','logicalPage':pn,'code':candidate}]if candidate in oc else[]};allrecords.append(record)
   cells.append(cell)
  filtered.append({'bounds':[b['xs'][0]/w,b['top']/h,b['xs'][-1]/w,b['bottom']/h],'cells':cells})
 # Dotted lists, photo captions and attachment grids without ruled ordering tables.
 if n not in MATRIX_BLADES|ROW_BLADES|BUR_MATRICES:
  existing={r['candidate']for r in allrecords if r['pdfPage']==n};sourcecodepositions=[]
  for key,rr in readers.items():
   for word in rr:
    if not .13<word['bounds'][1]<.92:continue
    for code in codes(word['text']):
     if code in existing:continue
     pos=next((a for a in sourcecodepositions if a['candidate']==code),None)
     if pos:pos['readers'].add(key);continue
     sourcecodepositions.append({'candidate':code,'bounds':word['bounds'],'readers':{key}})
  for ci,c in enumerate(sourcecodepositions):
   code=c['candidate'];box=c['bounds'];cy=(box[1]+box[3])/2;texts={key:cell_text(rr,[max(0,box[0]-.025),cy-.008,min(1,box[2]+.025),cy+.008])for key,rr in readers.items()};agree=[key for key,text in texts.items()if code in codes(text)];ident=f'{n:03}-list-{ci+1:03}';candidate_official=code in codes(op.get_text());allrecords.append({'id':ident,'pdfPage':n,'candidate':code,'value':code if len(agree)>=2 and 'Vision'in agree else None,'sourceBounds':box,'readings':[{'reader':key,'text':text}for key,text in texts.items()],'matchedReaders':agree,'verificationStatus':'verified (three-reader comparison)'if len(agree)>=2 and 'Vision'in agree else'requires visual reading','officialEvidence':[{'url':'https://www.conmed.com/-/media/conmed/documents/catalog/hallpoweredinstruments_catalog.ashx','logicalPage':pn,'code':code}]if candidate_official else[]})
 (F/'layout'/f'{n:03}.json').write_text(json.dumps({'pdfPage':n,'officialPage':pn,'bands':filtered,'vision':v},indent=2));print(n,len(filtered),'bands',sum(r['pdfPage']==n for r in allrecords),'codes',flush=True)
(F/'verification-initial.json').write_text(json.dumps({'records':allrecords,'found':len(allrecords),'verified':sum(bool(r['value'])for r in allrecords)},ensure_ascii=False,indent=2));print('TOTAL',len(allrecords),'verified',sum(bool(r['value'])for r in allrecords))
