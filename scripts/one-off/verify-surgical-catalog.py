import sys,json,pathlib,re,io,difflib
sys.path.insert(0,'scripts');from catalog_ocr import tesseract_words
from PIL import Image
out=pathlib.Path('reports/conmed/advanced-surgical-product-catalog');out.mkdir(exist_ok=True);(out/'line-crops').mkdir(exist_ok=True);reference=pathlib.Path('public/catalogs/conmed/advanced-surgical-product-catalog');visual=json.load(open('reports/conmed/advanced-surgical-product-catalog/visual-readings.json'));official=pathlib.Path('reports/conmed/advanced-surgical-product-catalog/official/catalog-text.txt').read_text();records=[]
for pn,reads in visual.items():
 n=int(pn);p=pathlib.Path(f'reports/conmed/advanced-surgical-product-catalog/layout/parsed-{n:03}.json');data=json.loads(p.read_text());rows=[r for g in data['groups']for r in g['rows']]
 if len(rows)!=len(reads):print('ROW COUNT MISMATCH',n,len(rows),len(reads),flush=True);continue
 evidence=json.loads((reference/'ocr'/f'{n:03}.json').read_text());im=Image.open(reference/'ocr'/f'{n:03}-600dpi.png');w,h=im.size
 for i,(row,value)in enumerate(zip(rows,reads)):
  existing=out/f'code-{n:03}-{i+1:02}.json'
  if existing.exists():records.append(json.loads(existing.read_text()));continue
  b=row['bounds'];ys=[max(0,b[1]-.004),min(1,b[3]+.004)];crop=im.crop((int(w*.78),int(h*ys[0]),int(w*.938),int(h*ys[1])));blob=io.BytesIO();crop.save(blob,format='PNG');raw,words=tesseract_words(blob.getvalue(),7,dpi=600);small=' '.join(w['text']for w in words)
  readings={}
  for mode in ['3','11']:
   ww=[q for q in evidence['passes'][mode]['words']if q['bounds'][0]>.775 and abs((q['bounds'][1]+q['bounds'][3])/2-row['cy'])<.006];ww.sort(key=lambda q:q['bounds'][0]);readings['600dpi-psm'+mode]=' '.join(q['text']for q in ww)
  readings['600dpi-code-crop-psm7']=small
  def matches(raw):
   tokens=[t.strip('.,:;|_')for t in raw.split()]
   return value in tokens or value in [''.join(tokens[a:b])for a in range(len(tokens))for b in range(a+1,min(a+4,len(tokens))+1)] or value=='VS135 Series'and 'VS135'in tokens and'Series'in tokens or value=='VS353 Series'and'VS353'in tokens and'Series'in tokens
  matched=[reader for reader,raw in readings.items()if matches(raw)];found=bool(re.search(r'(?<![A-Za-z0-9-])'+re.escape(value)+r'(?![A-Za-z0-9-])',official))
  rb=row['rowBounds'];line=out/'line-crops'/f'{n:03}-{i+1:02}.png';im.crop((int(w*.5),int(h*max(0,rb[1]-.003)),int(w*.94),int(h*min(1,rb[3]+.003)))).save(line)
  rec={'pdfPage':n,'pageRow':i+1,'visualReading':value,'visualReader':'Codex independent inspection of 600-DPI source table images; source-line crops retained','ocrReadings':readings,'matchedReaders':matched,'value':value if matched else None,'verificationStatus':'verified (visual + OCR)'if matched else'unresolved','manufacturerStatus':'confirmed on conmed.com'if found else'not confirmed on conmed.com','officialEvidence':[{'url':'https://www.conmed.com/-/media/conmed/documents/catalog/advancedsurgical_catalog.ashx','code':value}]if found else[],'sourceBounds':b,'rowBounds':rb,'lineCrop':str(line)}
  existing.write_text(json.dumps(rec,ensure_ascii=False,indent=2));records.append(rec)
 print('Verified page',n,'/',len(reads),'codes',flush=True)
(out/'verification.json').write_text(json.dumps({'records':records,'found':sum(map(len,visual.values())),'verified':sum(r['value']is not None for r in records),'confirmedOnConmedCom':sum(bool(r['officialEvidence'])for r in records),'flagged':[r for r in records if r['value']is None]},ensure_ascii=False,indent=2))
print('TOTAL',len(records),'verified',sum(r['value']is not None for r in records),'flagged',sum(r['value']is None for r in records),flush=True)
