#!/usr/bin/env python3
import json,re,math
from pathlib import Path
import pymupdf as fitz
from collections import Counter,defaultdict
R=Path(__file__).resolve().parents[1];folder=R/'reports/conmed/arthroscopy-product-catalog';D=fitz.open(folder/'official/arthroscopy-catalog.pdf')
def token(s):return re.sub(r'[^A-Za-z0-9-]','',s).lower()
def tokens(text):return {t for t in map(token,re.split(r'[\s.]+',text))if len(t)>=4 and t not in ['conmed','products','customer','service','phone','outside','within']}
off=[]
for n,p in enumerate(D,1):
 text=p.get_text();off.append({'page':n,'text':text,'tokens':tokens(text)})
df=Counter(t for p in off for t in p['tokens']);idf={t:math.log(1+len(off)/n)for t,n in df.items()};rows=[]
skip=set(range(1,9))|{28,51,60,68,87,105,110,113,114,115,116}
for n in range(9,113):
 if n in skip:continue
 f=R/f'public/catalogs/conmed/arthroscopy-product-catalog/ocr/{n:03}.json'
 if not f.exists():continue
 e=json.loads(f.read_text());text=' '.join(w['text']for w in e['passes']['11']['words']if .1<w['bounds'][1]<.91);source=tokens(text)
 scores=sorted([(sum(idf[t]for t in source&p['tokens'])/(sum(idf.get(t,1)for t in source)+.01),p['page'])for p in off],reverse=True)
 row={'pdfPage':n,'officialPage':scores[0][1],'score':round(scores[0][0],4),'margin':round(scores[0][0]-scores[1][0],4),'alternatives':scores[:3]};rows.append(row)
(folder/'page-mapping.json').write_text(json.dumps(rows,indent=2)+'\n');print('\n'.join(f"{r['pdfPage']:3} -> {r['officialPage']:3} {r['score']:.2f} margin {r['margin']:.2f}"for r in rows))
