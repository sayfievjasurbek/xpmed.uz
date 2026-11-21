"""Explicit transcription of visually checked tables, retaining source REF/row order."""
import json,collections,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/joint-catalogue';p=F/'rows-evidence.json';rs=json.loads(p.read_text())
def put(n,values):
 rows=[r for r in rs if r['pdfPage']==n];assert len(rows)==len(values),(n,len(rows),len(values))
 for r,v in zip(rows,values):r['itemValue']=v;r['itemVerification']='Codex visual full-table comparison at 600 DPI';r['visualReading']=v
put(4,[f'{s} / {l}'for _ in range(2)for s,l in zip(range(1,9),[125,130,135,140,145,150,155,160])])
put(5,[f'{s} / {l}'for _ in range(2)for s,l in zip(range(1,10),[95,110,120,125,130,135,140,145,150])])
put(6,[f'{s} / {l}'for s,l in zip([0,1,4,6,8,9,10],[120,125,130,135,140,145,150])]+list(map(str,[8,10,12,14]))+[f'{s} / {l}'for s,l in zip(range(1,11),[96,98,100,102,104,105,107,109,111,113])])
put(16,[f'φ6.5×{length}'for length in range(20,69,2)])
put(14,['24mm+0','24mm+3.5','28mm+1.5','28mm+5','28mm+8.5','28mm+12','28mm+15.5','32mm-2','32mm+1','32mm+5','32mm+9','32mm+13','28/S','28/M','28/L','32/S','32/M','32/L','32/XL','36/S','36/M','36/L','36/XL'])
put(7,[f'{s} / {l}'for s,l in zip(range(6),[120,135,135,135,135,135])]+['11','13.5','16'])
for n in [17,20]:put(n,[f'{s} / {side}'for side in ['Left','Right']for s in range(10,19)])
thicknesses=[6,7,8,9,10,11,12,14,16]
for n,start,end in [(18,10,14),(19,14,19),(21,10,14),(22,14,19)]:put(n,[f'{size} / {thick}'for size in range(start,end)for thick in thicknesses])
for n,start,end in [(23,10,15),(24,15,19)]:put(n,[f'{size}# {thick}mm'for size in range(start,end)for thick in thicknesses])
for r in rs:
 if r['value']=='131020007S':r['itemValue']='7# 115mm×135°'
 if r['value']=='13Y010001S':r['itemValue']='107mm×6.7m'
 if r['value']=='13Y010004S':r['itemValue']='122mm×13mm'
 if r['pdfPage']in [26,27,28,29]:r['itemValue']=re.sub(r'([0-4])4(?=\s+\dmm)',r'\1#',r['itemValue'])
p.write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
# Brochure matches concern nominal sizes and lengths; different measurements are not conflicts.
anty=json.loads((R/'content/products/double-medical/anty-f-series.json').read_text());matrix=anty['specTables'][0];matches=[]
for r in rs:
 if r['pdfPage']==8 and r['value'].startswith('13089'):
  m=re.search(r'(\d+)#\s*(\d+)mm[x×](\d+)mm',r['itemValue']);assert m,r
  size,length,diam=map(int,m.groups());row=next(row for row in matrix['rows']if str(row[0]).startswith(str(size)+'# /'));assert int(re.search(r'/\s*(\d+)',row[0]).group(1))==diam
  col=next(i for i,c in enumerate(matrix['columns'])if str(length)in str(c)and i in range(1,5));matches.append({'REF':r['value'],'system':'anty-f-series','jointPage':8,'brochureTable':matrix['id'],'brochureRow':size,'brochureColumn':col,'nominalSize':size,'stemLength':length,'nominalDiameter':diam,'availabilityMarker':row[col],'status':'matched: nominal size and stem length'})
for r in rs:
 if 17<=r['pdfPage']<=25:
  nums=re.findall(r'\d+',r['itemValue']);page=r['pdfPage'];size=int(nums[0]);valid=(29<=size<=41)if page==25 and r['value'].startswith('13551')else 10<=size<=18
  assert valid,r
  if page in [18,19,21,22,23,24]:assert 6<=int(nums[1])<=16
  matches.append({'REF':r['value'],'system':'cynthia-knee-system','jointPage':page,'variant':'primary','status':'matched: brochure size/thickness range; omitted thicknesses are not conflicts'})
(F/'brochure-size-matches.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2));print('Brochure size matches',len(matches))
