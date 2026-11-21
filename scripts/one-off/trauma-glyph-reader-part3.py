"""Source glyph-template reader; calibrated from triple-agreeing printed values.
Never derives dimensions from REF digits or neighboring rows.
"""
import json,re,collections
from pathlib import Path
import pymupdf as f
import numpy as np
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part3';O=R/'public/catalogs/double-medical/trauma-catalogue/ocr';D=f.open(R/'catalogs-source/double-medical/trauma-catalogue.pdf');tables=json.loads((F/'tables-evidence.json').read_text());templates=collections.defaultdict(list);tokens=[];pages={};draws={}
def glyphs(rect,n):
 if n not in pages:
  for previous in pages.values():previous.close()
  pages.clear();pages[n]=Image.open(O/f'{n:03}-600dpi.png').convert('L')
 im=pages[n];sx=im.width/D[n-1].rect.width;sy=im.height/D[n-1].rect.height;box=(int(rect.x0*sx)-2,int(rect.y0*sy)-2,int(rect.x1*sx)+3,int(rect.y1*sy)+3);crop=im.crop(box);arr=np.array(crop)<100;ink=np.where(arr.any(axis=0))[0]
 if not len(ink):return []
 runs=[];start=previous=ink[0]
 for x in ink[1:]:
  if x>previous+1:runs.append((start,previous+1));start=x
  previous=x
 runs.append((start,previous+1));out=[]
 for l,r in runs:
  ys=np.where(arr[:,l:r].any(axis=1))[0]
  if not len(ys):continue
  a=arr[ys[0]:ys[-1]+1,l:r];tile=Image.fromarray((a*255).astype('uint8')).resize((32,48),Image.Resampling.BILINEAR);out.append({'array':np.asarray(tile,dtype=float)/255,'aspect':a.shape[1]/a.shape[0],'height':a.shape[0],'image':Image.fromarray((~a*255).astype('uint8'))})
 return out
for t in tables:
 n=t['pdfPage'];p=D[n-1]
 if n not in draws:draws[n]=[a for a in p.get_drawings()if a['type']=='f'and len(a['items'])>1 and .08<a['rect'].x0/p.rect.width<.9 and a['rect'].height<12]
 starts=t['headerStarts'];edges=[.08]+[x-.008 for x in starts[1:]]+[max(.55,starts[-1]+.16)]
 for ri,row in enumerate(t['rows']):
  for ci in range(1,len(starts)):
   candidates=[a for a in draws[n]if edges[ci]<=a['rect'].x0/p.rect.width<edges[ci+1]and abs((a['rect'].y0+a['rect'].y1)/2/p.rect.height-row['cy'])<.006]
   if len(candidates)!=1:continue
   a=candidates[0];g=glyphs(a['rect'],n);readings=row['evidence'][ci]['readings'];agreed=next(iter(readings.values()))
   token={'table':t['id'],'page':n,'row':ri,'column':ci,'glyphs':g,'rect':list(a['rect']),'readings':readings};tokens.append(token)
   if len(set(readings.values()))==1 and re.fullmatch(r'[0-9.×/+\-°]+',agreed or'')and len(g)==len(agreed):
    for c,glyph in zip(agreed,g):
     if len(templates[c])<50:templates[c].append(glyph)
print('Templates', {k:len(v)for k,v in templates.items()},'tokens',len(tokens),flush=True)
def distance(a,b):return float(np.mean(np.abs(a['array']-b['array'])))+min(abs(a['aspect']-b['aspect']),2)*.12
out=[];ambiguous=[];match_cache={}
seedArrays={c:np.stack([v['array']for v in seeds])for c,seeds in templates.items()}
seedAspects={c:np.array([v['aspect']for v in seeds])for c,seeds in templates.items()}
def closest(g,c):return float(np.min(np.mean(np.abs(seedArrays[c]-g['array']),axis=(1,2))+np.minimum(np.abs(seedAspects[c]-g['aspect']),2)*.12))
for tokenNumber,token in enumerate(tokens):
 if tokenNumber%200==0:print('Compared',tokenNumber,'/',len(tokens),flush=True)
 text='';scores=[]
 for glyph in token.pop('glyphs'):
  if glyph['height']<8 and glyph['aspect']>.5 and glyph['aspect']<1.6:c='.';best=0.;margin=1.
  else:
   key=(glyph['array'].tobytes(),glyph['aspect'])
   if key not in match_cache:
    matches=sorted((closest(glyph,char),char)for char,seeds in templates.items());match_cache[key]=(matches[0][0],matches[0][1],matches[1][0]-matches[0][0])
   best,c,margin=match_cache[key]
  text+=c;scores.append({'character':c,'distance':best,'margin':margin})
 token.update(text=text,scores=scores,accepted=bool(scores)and all(x['distance']<.12 and x['margin']>.025 for x in scores));out.append(token)
 if not token['accepted']:ambiguous.append(token)
# Persist only serializable evidence. Source calibration thumbnails are visually reviewed by Codex.
(F/'glyph-readings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));(F/'glyph-uncertain.json').write_text(json.dumps(ambiguous,ensure_ascii=False,indent=2));print('Accepted glyph tokens',sum(x['accepted']for x in out),'uncertain',len(ambiguous),flush=True)
sheet=Image.new('RGB',(1000,150*len(templates)),'white');draw=ImageDraw.Draw(sheet)
for i,(char,seeds)in enumerate(sorted(templates.items())):
 draw.text((2,i*150+2),repr(char),fill='black')
 for j,g in enumerate(seeds[:8]):
  im=g['image'].convert('RGB');im=ImageOps.contain(im,(90,110));sheet.paste(im,(80+j*110,i*150+25))
sheet.save('/tmp/xpmed-trauma-part3/glyph-calibration.png')
