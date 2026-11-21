"""Read positioned PDF text directly; preserve the guide's section numbering."""
import json,re
from pathlib import Path
import pymupdf as f,pdfplumber
R=Path(__file__).resolve().parents[1];D=f.open(R/'catalogs-source/double-medical/cynthia-revision-surgical-guide.pdf');F=R/'reports/double-medical/cynthia-revision-surgical-guide';steps={};current=None;rawtables=[]
with pdfplumber.open(R/'catalogs-source/double-medical/cynthia-revision-surgical-guide.pdf')as plumber:
 for n,page in enumerate(D,1):
  if n<3 or n>17:continue
  ts=plumber.pages[n-1].find_tables()if n in [3,9]else[];rawtables.extend({'pdfPage':n,'bbox':t.bbox,'rows':t.extract()}for t in ts)
  blocks=[b for b in page.get_text('blocks')if b[6]==0 and b[1]<page.rect.height*.95 and not any(f.Rect(t.bbox).contains(f.Point((b[0]+b[2])/2,(b[1]+b[3])/2))for t in ts)]
  def order(b):
   if n==6 and b[1]>page.rect.height*.65:return (1 if b[0]<page.rect.width*.5 else 2,b[1],b[0])
   return (0,b[1],b[0])
  for b in sorted(blocks,key=order):
   text=' '.join(b[4].split());m=re.match(r'^([235]\.\d)\s+(.*)',text)
   if m:current=m[1];steps[current]={'number':current,'title':m[2],'blocks':[]}
   elif text.startswith('1. Assessment and Verification'):current='1';steps[current]={'number':'1','title':'Assessment and Verification','blocks':[]}
   elif text.startswith('4. Prosthesis Range of Motion Test'):current='4';steps[current]={'number':'4','title':'Prosthesis Range of Motion Test','blocks':[]}
   elif re.match(r'^[235]\.\s+(?:Tibial Preparation|Femoral Preparation|Precautions)',text):continue
   elif current:steps[current]['blocks'].append({'pdfPage':n,'bounds':list(b[:4]),'text':b[4]})
for step in steps.values():
 paras=[];previous=None
 for b in step['blocks']:
  if previous and b['pdfPage']==previous['pdfPage']and abs(b['bounds'][0]-previous['bounds'][0])<6 and b['bounds'][1]-previous['bounds'][1]<19:
   paras[-1]+='\n'+b['text']
  else:paras.append(b['text'])
  previous=b
 cleaned=[];notes=[]
 for p in paras:
  p=re.sub(r'([A-Za-z])-\s*\n\s*([a-z])',r'\1\2',p);p=' '.join(p.split());p=p.replace('4- in-1','4-in-1')
  if 'Note:'in p:
   before,note=p.split('Note:',1);notes.append(note.strip())
   if before.strip():cleaned.append(before.strip())
  elif p=='There is a small screw—do not unscrew it.':notes.append(p)
  else:
   embedded=re.findall(r'\(note:\s*([^)]*)\)',p,re.I);notes+=embedded;p=re.sub(r'\(note:\s*[^)]*\)','',p,flags=re.I);cleaned.append(p)
 step['text']='\n\n'.join(cleaned);step['notes']=notes;step['sourcePages']=sorted({b['pdfPage']for b in step['blocks']})
(F/'direct-steps-en.json').write_text(json.dumps(list(steps.values()),ensure_ascii=False,indent=2)+'\n');(F/'direct-tables.json').write_text(json.dumps(rawtables,ensure_ascii=False,indent=2)+'\n');print('\n\n'.join(s['number']+' '+s['title']+'\n'+s['text']+'\nNOTES '+str(s['notes'])for s in steps.values()))
