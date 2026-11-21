"""Import one reviewed system-type OCR recipe through the standard catalog entry point."""
import copy,json,hashlib,subprocess
from pathlib import Path
from finalize_translation_loader import finalize_translation

def import_system_profile(root,pdf,brand,pdfslug,digest,evidence,profile):
 s=copy.deepcopy(profile['system']);ref='/catalogs/'+brand+'/'+pdfslug
 if s['brand']!=brand:raise ValueError('System recipe brand differs from input')
 if any(p['dpi']!=600 for p in evidence):raise ValueError('Reviewed system recipe requires 600-DPI evidence')
 s.update(sourcePdf=ref+'/source.pdf',sourcePageImages=[ref+f'/pages/{page:03}.webp'for page in s['sourcePages']],sourcePageDimensions={str(p['page']):{'width':p['pixelSize'][0],'height':p['pixelSize'][1]}for p in evidence})
 for page in s['sourcePages']:
  if page in profile['nonProductPages']:raise ValueError('Non-product page assigned to system')
 s['review']={'sourceSha256':digest,'importMethod':profile['method'],'flags':copy.deepcopy(profile.get('flags',[])),'status':'source-reviewed','layoutReviewed':bool(profile.get('layoutReviewed')),'skippedSourcePages':profile['nonProductPages'],'ocrDpi':600,'ocrSettings':[3,11]}
 s=finalize_translation(s)
 check=subprocess.run(['node',str(root/'scripts/validate-system.mjs')],input=json.dumps(s),text=True,capture_output=True,cwd=root)
 if check.returncode:raise ValueError(check.stdout+check.stderr)
 dest=root/'content/products'/brand/(s['slug']+'.json');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 tables={t['id']:t for t in s.get('specTables',[])+s.get('referenceTables',[])}
 for v in s.get('variants',[]):
  for t in v.get('specTables',[]):
   if t['id']in tables and tables[t['id']]!=t:raise ValueError('Conflicting shared table identity')
   tables[t['id']]=t
 report={'pdf':str(pdf.relative_to(root)),'sha256':digest,'method':profile['method'],'ocr':{'dpi':600,'settings':[3,11]},'systemsCreated':1,'systems':[{'slug':s['slug'],'status':'draft','flags':s['review']['flags']}],'variantsCreated':len(s.get('variants',[])),'tablesCreated':len(tables),'tableIds':list(tables),'imagesExtracted':len(profile.get('assets',[])),'nonProductPages':profile['nonProductPages'],'openRealFlags':s['review']['flags']}
 folder=root/'reports'/brand;folder.mkdir(parents=True,exist_ok=True);(folder/(pdfslug+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['systemsCreated','variantsCreated','tablesCreated','imagesExtracted','openRealFlags']},ensure_ascii=False,indent=2))
