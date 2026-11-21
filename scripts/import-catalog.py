#!/usr/bin/env python3
"""Conservative PDF-to-system import. Always creates drafts, never invents values.
Usage: python scripts/import-catalog.py catalogs-source/<brand>/<name>.pdf
Russian prose is completed by Codex after extraction, then finalized for medical review.
"""
import argparse,hashlib,json,os,re,subprocess,sys,copy
from pathlib import Path
import pymupdf as fitz
import pdfplumber
from PIL import Image
import numpy as np
from rembg import new_session,remove
ROOT=Path(__file__).resolve().parents[1]
def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')[:100]
def bilingual(en):return {'ru':'','en':en}
def flag(path,code,ru,en,pages):return {'path':path,'code':code,'message':{'ru':ru,'en':en},'sourcePages':pages}
def check(s):
 import jsonschema
 jsonschema.validate(s,json.loads((ROOT/'content/system.schema.json').read_text()))
 p=subprocess.run(['node',str(ROOT/'scripts/validate-system.mjs')],input=json.dumps(s),text=True,capture_output=True,cwd=ROOT)
 if p.returncode:raise ValueError('Invalid system: '+p.stdout+p.stderr)
def prepare_translation_review(s,flags):
 # This local script does not call a translation service. Codex completes the prose
 # during the import task and runs finalize-translation.py before publication.
 fields=[]
 def walk(v,path=''):
  if isinstance(v,dict):
   if set(v)=={'ru','en'} and isinstance(v['en'],str) and v['en']:
    fields.append(path+'.ru')
    if not v['ru']:flags.append(flag(path+'.ru','translation-required','Codex должен перевести этот текст на профессиональный русский медицинский язык.','Codex must supply a professional Russian medical translation.',s['sourcePages']))
   else:
    for k,x in v.items():walk(x,path+'.'+k if path else k)
  elif isinstance(v,list):
   for i,x in enumerate(v):walk(x,path+'.'+str(i))
 walk(s)
 return fields
def run():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pdf',type=Path);ap.add_argument('--section',help='Reviewed disjoint partition of an existing catalog');ap.add_argument('--model',default='u2net');ap.add_argument('--ocr',action='store_true',help='600-DPI English OCR with independent PSM3/PSM11 code comparison');ap.add_argument('--ocr-only',action='store_true',help='Cache OCR evidence without creating systems');ap.add_argument('--dpi',type=int,default=600,help='OCR rendering resolution, minimum 400 DPI');ap.add_argument('--pages',help='Physical PDF page ranges, e.g. 3-209; only these pages are rendered/OCRed');ap.add_argument('--workers',type=int,default=1,help='Independent OCR worker processes (1–8)');a=ap.parse_args();pdf=a.pdf.resolve();
 if a.ocr_only and not a.ocr:raise ValueError('--ocr-only requires --ocr')
 source=ROOT/'catalogs-source'
 if not pdf.is_relative_to(source) or pdf.parent.parent!=source or pdf.suffix.lower()!='.pdf':raise ValueError('Input must be catalogs-source/<brand>/<file>.pdf')
 brand=pdf.parent.name
 if not re.fullmatch('[a-z0-9][a-z0-9-]*',brand):raise ValueError('Invalid brand')
 digest=hashlib.sha256(pdf.read_bytes()).hexdigest();pdfslug=slug(pdf.stem);profile=None
 for p in (ROOT/'scripts/profiles').glob('*.json'):
  candidate=json.loads(p.read_text())
  if isinstance(candidate,dict) and candidate.get('sha256')==digest and candidate.get('partition')==a.section:profile=candidate;break
 publicref='/catalogs/'+brand+'/'+pdfslug
 for existing in (ROOT/'content/products').glob('*/*.json'):
  previous=json.loads(existing.read_text())
  belongs=(previous.get('sourcePdf')==publicref+'/source.pdf' or previous.get('review',{}).get('sourceSha256')==digest)
  protected=previous.get('status')=='published' or previous.get('review',{}).get('editedAt')
  if belongs and protected:
   from catalog_partition import disjoint_partition
   disjoint=disjoint_partition(a.section,profile,previous)
   if not disjoint:raise ValueError('Refusing to modify assets or data belonging to published/reviewed content: '+str(existing))

 if a.ocr and profile and profile.get('variantSupplement'):raise ValueError('This reviewed supplement must use its real text layer, without OCR')
 if a.ocr:
  from catalog_ocr import extract_ocr
  reference=ROOT/'public/catalogs'/brand/pdfslug;reference.mkdir(parents=True,exist_ok=True);(reference/'source.pdf').write_bytes(pdf.read_bytes()) if not(reference/'source.pdf').exists() else None
  page_numbers=None
  if a.pages:
   page_numbers=[]
   for part in a.pages.split(','):
    if not re.fullmatch(r'\d+(?:-\d+)?',part):raise ValueError('Invalid page range')
    limits=list(map(int,part.split('-')));page_numbers.extend(range(limits[0],limits[-1]+1))
  if a.section:
   if not profile or not profile.get('authorizedPhysicalPages'):raise ValueError('Unknown reviewed catalog partition')
   if page_numbers is None:page_numbers=profile['authorizedPhysicalPages']
   if not set(page_numbers)<=set(profile['authorizedPhysicalPages']):raise ValueError('Requested pages exceed the authorized partition')
  evidence=extract_ocr(pdf,reference,dpi=a.dpi,workers=a.workers,page_numbers=page_numbers,manifest_name='manifest-'+a.section+'.json' if a.section else 'manifest.json')
  if a.ocr_only:return
  if profile and profile.get('systems') and profile.get('layoutReviewed'):
   from import_multi_system_profile import import_multi_system_profile
   return import_multi_system_profile(ROOT,pdf,brand,pdfslug,digest,evidence,profile)
  if profile and profile.get('system') and profile.get('layoutReviewed'):
   from import_system_profile import import_system_profile
   return import_system_profile(ROOT,pdf,brand,pdfslug,digest,evidence,profile)
  from import_ocr_catalog import import_ocr_catalog
  return import_ocr_catalog(ROOT,pdf,brand,pdfslug,digest,evidence,a.model)
 doc=fitz.open(pdf);
 if not any(page.get_text().strip()for page in doc):raise ValueError('No text layer. Re-run with --ocr for dual-pass 600-DPI extraction.')
 if profile and profile.get('layoutReviewed') and profile.get('variantSupplement'):
  from import_variant_supplement import import_variant_supplement
  return import_variant_supplement(ROOT,pdf,brand,pdfslug,digest,doc,profile)
 ref=ROOT/'public/catalogs'/brand/pdfslug;ref.mkdir(parents=True,exist_ok=True);(ref/'source.pdf').write_bytes(pdf.read_bytes());publicref='/catalogs/'+brand+'/'+pdfslug
 page_text=[];raw_tables=[];source_images={};extraction_flags=[];pages=[]
 with pdfplumber.open(pdf) as plumber:
  for number,page in enumerate(doc,1):
   scan=ref/'pages'/f'{number:03}.webp';scan.parent.mkdir(exist_ok=True);pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(scan,quality=90)
   pages.append(publicref+'/pages/'+scan.name);page_text.append(page.get_text())
   for j,t in enumerate(plumber.pages[number-1].find_tables()):
    rows=t.extract();width=max(map(len,rows),default=0)
    if not width:continue
    clean=[]
    for row in rows:
     clean.append([None if c and '\ufffd' in c else c if c is not None else '' for c in row]+['']*(width-len(row)))
    crop=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(t.bbox),alpha=False);table_path=ref/f'table-{number:03}-{j+1:02}.png';crop.save(table_path)
    raw_tables.append({'id':f'table-{number}-{j+1}','title':bilingual(f'Table {number}.{j+1}'),'unit':None,'image':publicref+'/'+table_path.name,'columns':clean[0],'rows':clean[1:],'legend':None,'sourcePages':[number],'bbox':list(t.bbox)})
   for info in page.get_images(full=True):
    xref,smask=info[:2];key=(number,info[7]);pix=fitz.Pixmap(doc,xref)
    if pix.colorspace and pix.colorspace.n!=3:pix=fitz.Pixmap(fitz.csRGB,pix)
    if smask:pix=fitz.Pixmap(pix,fitz.Pixmap(doc,smask))
    mode='RGBA' if pix.alpha else 'RGB';source_images[key]=Image.frombytes(mode,(pix.width,pix.height),pix.samples).convert('RGBA')
 dump(ref/'extracted-tables.json',raw_tables);(ref/'extracted-text.txt').write_text('\n\n'.join(page_text))
 if profile:
  systems=[copy.deepcopy(profile['system'])];method=profile['method']
 else:
  # Font-aware family candidates. Group primary/revision headings; every assignment is flagged.
  families={}
  for n,page in enumerate(doc,1):
   for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
     spans=line.get('spans',[]);text=' '.join(x['text'] for x in spans).strip()
     if 5<len(text)<120 and max([s['size'] for s in spans]+[0])>=12 and re.search(r'\b(system|prosthesis|implant|cement|plate|nail)\b',text,re.I):
      family=re.sub(r'\b(primary|revision)\b','',text,flags=re.I);family=' '.join(family.split());families.setdefault(family,[]).append(n)
  if not families:families={pdf.stem:list(range(1,len(doc)+1))}
  systems=[]
  for name,nums in families.items():
   nums=sorted(set(nums));s={'schemaVersion':1,'slug':slug(name) or 'unidentified-system','brand':brand,'category':'unclassified','subcategory':'','specialty':[],'name':bilingual(name),'shortDescription':bilingual(''),'description':bilingual(''),'heroImage':'','imageType':'scene','gallery':[],'variants':[],'features':[],'hotspots':[],'components':[],'specTables':[copy.deepcopy(t) for t in raw_tables if t['sourcePages'][0] in nums],'refCodes':[],'sourcePages':nums,'isNew':False,'catalogEdition':None,'status':'draft'}
   systems.append(s)
  method='Font-aware heading candidates; family, page, table and image assignments require review.'
 report={'pdf':str(pdf.relative_to(ROOT)),'sha256':digest,'method':method,'pages':len(doc),'systemsFound':len(systems),'tablesExtracted':len(raw_tables),'imagesExtracted':len(source_images),'systems':[],'uncertainties':[],'pageImages':pages}
 session=new_session(a.model,providers=['CPUExecutionProvider'])
 for s in systems:
  s['brand']=brand;s['status']='draft';s['sourcePdf']=publicref+'/source.pdf';s['sourcePages']=sorted(set(s['sourcePages']));s['sourcePageImages']=[pages[n-1] for n in s['sourcePages']];flags=copy.deepcopy(profile['flags']) if profile else [flag('name','family-detection','Проверьте выделение семейства, категории и принадлежность изображений и таблиц.','Verify family grouping, category and image/table assignments.',s['sourcePages'])]
  target=ROOT/'content/products'/brand/(s['slug']+'.json')
  if target.exists():
   existing=json.loads(target.read_text())
   if existing.get('status')=='published' or existing.get('review',{}).get('editedAt'):raise ValueError('Refusing to overwrite published/reviewed family: '+str(target))
  folder=ROOT/'public/images/products'/brand/s['slug'];folder.mkdir(parents=True,exist_ok=True);prefix='/images/products/'+brand+'/'+s['slug']+'/'
  assets=[];image_methods={}
  for (n,name),original in source_images.items():
   if n not in s['sourcePages']:continue
   rgb=Image.new('RGB',original.size,'white');rgb.paste(original,mask=original.getchannel('A'));cut=remove(rgb,session=session).convert('RGBA')
   if original.getchannel('A').getextrema()[0]<255:chosen=original;kind='cutout';how='manufacturer-alpha-preserved-after-rembg'
   else:
    alpha=cut.getchannel('A');area=sum(v>127 for v in alpha.getdata())/(cut.width*cut.height)
    # Conservative white-background test; every automated mask still requires visual review.
    pixels=np.asarray(rgb);mask=np.asarray(alpha);frame=np.concatenate((pixels[0],pixels[-1],pixels[:,0],pixels[:,-1]));ink=np.min(pixels,axis=2)<220
    coverage=float(np.mean(mask[ink]>127)) if ink.any() else 0
    clean=float(np.mean(np.min(frame,axis=1)>245))>.97 and .02<area<.85 and coverage>.98
    chosen=cut if clean else original;kind='cutout' if clean else 'scene';how='rembg-white-background-review-required' if clean else 'scene-pending-visual-review';flags.append(flag('gallery','image-review','Проверьте фон и качество маски изображения.','Review scene/background segmentation; candidate and original are retained.',[n]))
   cut.save(folder/f'page-{n:03}-{name.lower()}-rembg.png')
   native=f'page-{n:03}-{name.lower()}.png';chosen.save(folder/native);assets.append({'file':native,'pdfPage':n,'pdfObject':name,'width':chosen.width,'height':chosen.height,'imageType':kind,'method':how});image_methods[(n,name)]=(chosen,kind)
  def save(im,name,kind):
   if kind=='cutout':
    bbox=im.getchannel('A').getbbox()
    if bbox:im=im.crop(bbox)
    pad=max(8,round(max(im.size)*.04));canvas=Image.new('RGBA',(im.width+2*pad,im.height+2*pad));canvas.alpha_composite(im,(pad,pad));im=canvas
   im.save(folder/(name+'.png'));im.save(folder/(name+'.webp'),lossless=kind=='cutout',quality=90,method=6);return prefix+name+'.webp'
  if profile:
   for asset in profile['assets']:
    original,kind=image_methods[(asset['pdfPage'],asset['pdfObject'])]
    if 'sourceCrop' in asset:original=original.crop(asset['sourceCrop'])
    if 'sourceCrops' in asset:
     crops=[original.crop(box) for box in asset['sourceCrops']];canvas=Image.new('RGBA',(sum(x.width for x in crops)+24,max(x.height for x in crops)+16));x=8
     for crop in crops:canvas.alpha_composite(crop,(x,8));x+=crop.width+8
     original=canvas
    save(original,Path(asset['file']).stem,kind)
   def replace(v):
    if isinstance(v,str):return v.replace('/images/products/cynthia/',prefix)
    if isinstance(v,list):return [replace(x) for x in v]
    if isinstance(v,dict):return {k:replace(x) for k,x in v.items()}
    return v
   s=replace(s)
   for v in s['variants']:
    for table in v['specTables']:table['image']=pages[table['sourcePages'][0]-1]
  else:
   gallery=[]
   for (n,name),(im,kind) in image_methods.items():gallery.append({'src':save(im,f'page-{n:03}-{name.lower()}',kind),'imageType':kind,'sourcePages':[n]})
   s['gallery']=gallery;s['heroImage']=gallery[0]['src'] if gallery else ''
   # Keep short callouts adjacent in the PDF as candidates, not certified claims.
   for n in s['sourcePages']:
    blocks=doc[n-1].get_text('blocks')
    for b in blocks:
     lines=[x.strip() for x in b[4].splitlines() if x.strip()]
     if 2<=len(lines)<=8 and 3<len(lines[0])<70 and any(len(x)>15 for x in lines[1:]) and not re.search(r'\d.*\d',b[4]):s['features'].append({'title':bilingual(lines[0]),'text':bilingual(' '.join(lines[1:])),'image':None,'sourcePages':[n],'sourceBounds':list(b[:4])})
   flags.append(flag('features','callout-association','Проверьте выделение характеристик и связь с иллюстрациями.','Verify callout extraction and image association.',s['sourcePages']))
   for i,t in enumerate(s['specTables']):
    if not t['unit']:flags.append(flag('specTables.'+str(i)+'.unit','missing-unit','Единицы измерения не определены автоматически.','Units not established automatically.',t['sourcePages']))
    if any(c is None for row in t['rows'] for c in row):flags.append(flag('specTables.'+str(i),'unreadable-cell','Нечитаемые значения оставлены пустыми.','Unreadable values left empty.',t['sourcePages']))
    if any('●' in str(c) or '○' in str(c) for row in t['rows'] for c in row):flags.append(flag('specTables.'+str(i)+'.legend','undefined-symbols','Проверьте легенду символов. Наличие уточняйте у менеджера.','Verify symbol legend. Confirm availability with sales.',t['sourcePages']))
  # Capture reference codes only when explicitly labelled; never treat model sizes as articles.
  if not profile:
   refs=[]
   for n in s['sourcePages']:
    refs.extend(re.findall(r'(?:\bREF(?:ERENCE)?|Article\s*(?:No\.?|Number)|Catalog\s*(?:No\.?|Number))\s*[:#.]?\s*([A-Z0-9][A-Z0-9./-]{2,})', page_text[n-1]))
   s['refCodes']=list(dict.fromkeys(refs))
   if not raw_tables:flags.append(flag('specTables','table-detection','Таблицы не найдены автоматически; проверьте страницы PDF.','No tables detected automatically; verify the PDF pages.',s['sourcePages']))
  translated_fields=prepare_translation_review(s,flags);s['review']={'translatedFields':translated_fields,'translationAuthor':'codex','translationStatus':'review-required','flags':flags,'sourceSha256':digest,'importMethod':method,'skipped':False};check(s)
  target=ROOT/'content/products'/brand/(s['slug']+'.json')
  if target.exists():
   previous=json.loads(target.read_text())
   if previous.get('status')=='published' or previous.get('review',{}).get('editedAt'):raise ValueError('Refusing to overwrite published or reviewed content: '+str(target))
  dump(target,s);dump(folder/'extraction-manifest.json',{'sourcePdf':s['sourcePdf'],'images':assets,'namedAssets':profile['assets'] if profile else []});report['systems'].append({'slug':s['slug'],'status':'draft','file':str(target.relative_to(ROOT)),'tables':sum(len(v.get('specTables',[])) for v in s.get('variants',[]))+len(s['specTables']),'features':sum(len(v.get('features',[])) for v in s.get('variants',[]))+len(s['features']),'translatedFields':translated_fields,'flags':flags});report['uncertainties']+=flags
 dump(ROOT/'reports'/brand/(pdfslug+'.json'),report)
 lines=[f'# Import report: {pdfslug}',f'- Systems found: {report["systemsFound"]} (draft only)',f'- Source pages: {len(doc)}',f'- Embedded images extracted: {len(source_images)}',f'- Raw PDF tables extracted by pdfplumber: {len(raw_tables)}',f'- Method: {method}','']
 for s in report['systems']:
  lines += [f'## {s["slug"]}',f'- Structured tables: {s["tables"]}',f'- Features: {s["features"]}']+[f'- [{f["code"]}] {f["message"]["ru"]}' for f in s['flags']]
 (ROOT/'reports'/brand/(pdfslug+'.md')).write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':
 try:run()
 except Exception as e:print('IMPORT FAILED:',e,file=sys.stderr);sys.exit(1)
