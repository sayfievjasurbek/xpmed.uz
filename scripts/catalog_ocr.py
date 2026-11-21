"""600-DPI, two-setting OCR evidence. No character substitutions in article codes."""
import csv,io,json,os,subprocess,hashlib
from pathlib import Path
from collections import defaultdict
import pymupdf as fitz
from PIL import Image

def tesseract_words(png,psm,lang='eng',dpi=400):
    # stdin avoids Leptonica's macOS /tmp symlink filename handling.
    result=subprocess.run(['tesseract','stdin','stdout','-l',lang,'--oem','1','--psm',str(psm),'--dpi',str(dpi),'tsv'],input=png,capture_output=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace'))
    text=result.stdout.decode('utf8');words=[]
    for row in csv.DictReader(io.StringIO(text),delimiter='\t',quoting=csv.QUOTE_NONE):
        if row.get('level')!='5' or not (row.get('text') or '').strip():continue
        words.append({'text':row['text'],'confidence':float(row['conf']),'pixelBounds':[int(row['left']),int(row['top']),int(row['left'])+int(row['width']),int(row['top'])+int(row['height'])],'lineId':'.'.join(row[k] for k in ['block_num','par_num','line_num'])})
    return text,words

def lines_from_words(words):
    lines=defaultdict(list)
    for word in words:lines[word['lineId']].append(word)
    result=[]
    for ident,items in lines.items():
        items.sort(key=lambda w:w['pixelBounds'][0]);box=[min(w['bounds'][0]for w in items),min(w['bounds'][1]for w in items),max(w['bounds'][2]for w in items),max(w['bounds'][3]for w in items)]
        result.append({'text':' '.join(w['text']for w in items),'bounds':box,'confidence':min(w['confidence']for w in items),'words':items})
    return sorted(result,key=lambda x:(round(x['bounds'][1],3),x['bounds'][0]))

def _extract_page(task):
    pdf,reference,digest,dpi,version,number=task
    reference=Path(reference);cache=reference/'ocr'
    doc=fitz.open(pdf);page=doc[number-1]
    output=cache/f'{number:03}.json'
    if output.exists():
        saved=json.loads(output.read_text())
        if saved.get('sourceSha256')==digest and saved.get('dpi')==dpi and saved.get('engine')==version and set(saved.get('passes',{}))=={'3','11'}:
            return saved
    old=json.loads(output.read_text()) if output.exists() else {}
    png_path=cache/f'{number:03}-{dpi}dpi.png'
    if old.get('sourceSha256')==digest and old.get('dpi')==dpi and png_path.exists():
        png=png_path.read_bytes();image=Image.open(io.BytesIO(png)).convert('RGB');pixel_width,pixel_height=image.size
    else:
        pix=page.get_pixmap(dpi=dpi,alpha=False);png=pix.tobytes('png');image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);pixel_width,pixel_height=image.size
    # Full-resolution rendered source is retained for exact item crops and audit.
    (cache/f'{number:03}-{dpi}dpi.png').write_bytes(png);image.save(reference/'pages'/f'{number:03}.webp',quality=91)
    record={'page':number,'printedPage':None,'dpi':dpi,'engine':version,'sourceSha256':digest,'pageSize':[page.rect.width,page.rect.height],'pixelSize':[pixel_width,pixel_height],'passes':{}}
    for psm in [3,11]:
        if psm==3 and old.get('sourceSha256')==digest and old.get('dpi')==dpi and old.get('passes',{}).get('3'):
            record['passes']['3']=old['passes']['3'];continue
        raw,words=tesseract_words(png,psm,dpi=dpi)
        (cache/f'{number:03}-psm{psm}.tsv').write_text(raw)
        for word in words:word['bounds']=[word['pixelBounds'][0]/pixel_width,word['pixelBounds'][1]/pixel_height,word['pixelBounds'][2]/pixel_width,word['pixelBounds'][3]/pixel_height]
        record['passes'][str(psm)]={'words':words,'lines':lines_from_words(words)}
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');return record

def extract_ocr(pdf,reference,dpi=600,workers=1,page_numbers=None,manifest_name="manifest.json"):
    if dpi<400:raise ValueError('Catalog OCR requires at least 400 DPI')
    if not 1<=workers<=8:raise ValueError('OCR workers must be between 1 and 8')
    reference=Path(reference);cache=reference/'ocr';cache.mkdir(parents=True,exist_ok=True);(reference/'pages').mkdir(exist_ok=True)
    digest=hashlib.sha256(Path(pdf).read_bytes()).hexdigest()
    with fitz.open(pdf) as doc:page_count=len(doc)
    version=subprocess.run(['tesseract','--version'],capture_output=True,text=True).stdout.splitlines()[0]
    selected=sorted(set(page_numbers)) if page_numbers is not None else list(range(1,page_count+1))
    if not selected or any(not isinstance(n,int) or n<1 or n>page_count for n in selected):raise ValueError('OCR page range is outside the source PDF')
    tasks=[(str(pdf),str(reference),digest,dpi,version,n)for n in selected]
    pages=[]
    if workers==1:
        for task in tasks:
            pages.append(_extract_page(task));print(f'OCR page {task[-1]}/{page_count}: two passes ready',flush=True)
    else:
        # MuPDF documents are process-local; sharing documents between threads is unsafe.
        from concurrent.futures import ProcessPoolExecutor,as_completed
        import multiprocessing
        with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            futures={pool.submit(_extract_page,task):task[-1]for task in tasks}
            for future in as_completed(futures):
                pages.append(future.result());print(f'OCR page {futures[future]}/{page_count}: two passes ready ({len(pages)}/{page_count})',flush=True)
    pages.sort(key=lambda p:p['page'])
    (cache/manifest_name).write_text(json.dumps({'sourceSha256':digest,'dpi':dpi,'engine':version,'settings':[3,11],'pages':[p['page']for p in pages]},indent=2)+'\n')
    return pages

def overlap(a,b):
    return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))

def compare_code(primary,secondary,threshold=90):
    """Keep exact evidence and return null unless both independent reads agree confidently."""
    left=primary.get('text','').strip();right=secondary.get('text','').strip()
    reasons=[]
    if not left or not right:reasons.append('missing-in-one-pass')
    elif left!=right:reasons.append('ocr-disagreement')
    if min(primary.get('confidence',-1),secondary.get('confidence',-1))<threshold:reasons.append('low-confidence')
    return {'value':left if not reasons else None,'pass1':left,'pass2':right,'confidence1':primary.get('confidence',-1),'confidence2':secondary.get('confidence',-1),'flagged':bool(reasons),'reasons':reasons}
