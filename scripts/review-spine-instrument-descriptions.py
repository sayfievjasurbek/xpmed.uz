"""Prepare 600-DPI row crops for independent visual review, not generated readings."""
import json,re
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';O=R/'public/catalogs/double-medical/spine-catalogue/ocr';rows=json.loads((F/'rows-evidence.json').read_text());done=json.loads((R/'scripts/profiles/spine-instruments-visual-descriptions.json').read_text())['readings'];selected=[r for r in rows if r['id']not in done and (not r['descriptionAgreement']or re.search(r'[A-Za-z]{2}\d{5}|\d{6}[A-Za-z]|^\s*$|DeviCE|пишит',r['description']))];(F/'description-visual-items.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2))
for start in range(0,len(selected),24):
 S=Image.new('RGB',(2100,12*130),'white');d=ImageDraw.Draw(S)
 for i,r in enumerate(selected[start:start+24]):
  im=Image.open(O/f"{r['pdfPage']:03}-600dpi.png");w,h=im.size;siblings=[x for x in rows if x['pdfPage']==r['pdfPage']];k=siblings.index(r);top=(siblings[k-1]['cy']+r['cy'])/2 if k else max(.14,r['codeBounds'][1]-.035);bottom=(siblings[k+1]['cy']+r['cy'])/2 if k+1<len(siblings)else .93;clip=im.crop((int(.22*w),int(top*h),int(.73*w),int(bottom*h)));a=np.array(clip.convert('L'))<90;a[a.sum(axis=1)>a.shape[1]*.65]=False;yy,xx=np.where(a);clip=clip.crop((max(0,int(xx.min())-5),max(0,int(yy.min())-5),min(clip.width,int(xx.max())+6),min(clip.height,int(yy.max())+6)))if len(xx)else clip;clip.thumbnail((1030,95));x=i%2*1050;y=i//2*130;S.paste(clip,(x,y+25));d.text((x,y),r['id']+' '+r['value'],fill='black')
 S.save(f'/tmp/xpmed-spine-instruments/descriptions-{start//24:02}.png')
print('Visual rows',len(selected))
