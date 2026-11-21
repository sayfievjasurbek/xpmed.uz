#!/usr/bin/env python3
"""Retain printed source captions separately from native product rasters."""
import pathlib,json,re,difflib
from arthroscopy_ru import translate,unknown
R=pathlib.Path(__file__).resolve().parents[1];F=R/'reports/conmed/arthroscopy-product-catalog';a=json.load(open(R/'public/images/products/conmed/arthroscopy/prepared-assets.json'));out={}
for name,img in a.items():
 n=img['pdfPage'];lines=json.load(open(F/'vision'/f'{n:03}.json'));b=img['sourceBounds'];candidates=[]
 for l in lines:
  text=l['text'];lb=l['bounds'];cy=(lb[1]+lb[3])/2;cx=(lb[0]+lb[2])/2
  if len(text)>100 or len(text)<4 or text.startswith(('»','The ','This ','For use','For Use','Customer','All products'))or re.search(r'\.{2,}|Cat\.|\b(Products|PRODUCTS)\b',text):continue
  if not b[0]-.06<cx<b[2]+.06:continue
  below=lb[1]-b[3];above=b[1]-lb[3]
  if 0<=below<.055:score=below
  elif 0<=above<.04:score=above+.012
  else:continue
  candidates.append((score,text,lb))
 selected=min(candidates)if candidates else None
 out[name]={'caption':{'ru':translate(selected[1]),'en':selected[1]}if selected else None,'sourceCaptionBounds':selected[2]if selected else None,'candidates':[{'text':x[1],'bounds':x[2]}for x in sorted(candidates)[:3]],'unknownTerminology':unknown(selected[1])if selected else[]}
(F/'caption-proposals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('captions',sum(bool(x['caption'])for x in out.values()),'of',len(out));print('unknown',[(k,x['caption']['en'],x['unknownTerminology'])for k,x in out.items()if x['unknownTerminology']])
