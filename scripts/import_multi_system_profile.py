"""Import a reviewed multi-family source recipe without conflating publication with extraction."""
import copy,json,subprocess,collections
from pathlib import Path
from finalize_translation_loader import finalize_translation
from arthroscopy_review_alignment import align

def import_multi_system_profile(root,pdf,brand,pdfslug,digest,evidence,profile):
 from catalog_partition import validate_partition_evidence
 validate_partition_evidence(profile,evidence)
 if any(p['dpi']!=600 for p in evidence):raise ValueError('Reviewed OCR recipes require 600-DPI source evidence')
 ref='/catalogs/'+brand+'/'+pdfslug;systems=[];prepared=[]
 from catalog_merge import prepare_merges,write_merges
 merges=prepare_merges(root,profile,digest,ref)
 for source in profile['systems']:
  s=copy.deepcopy(source)
  if s['brand']!=brand:raise ValueError('Recipe brand mismatch')
  if any(p in profile['nonProductPages']for p in s['sourcePages']):raise ValueError('Non-product page assigned to system')
  flags=s.pop('reviewFlags',[])
  # Publication follows the separate, explicit source-review step, never the extraction step.
  s['status']='draft';s['sourcePdf']=ref+'/source.pdf';s['sourcePageImages']=[ref+f'/pages/{p:03}.webp'for p in s['sourcePages']]
  s['sourcePageDimensions']={str(p['page']):{'width':p['pixelSize'][0],'height':p['pixelSize'][1]}for p in evidence}
  s['review']={'sourceSha256':digest,'importMethod':profile['method'],'flags':flags,'status':'source-reviewed-with-open-items'if flags else'source-reviewed','layoutReviewed':True,'ocrDpi':600,'ocrSettings':[3,11],'independentReader':'Apple Vision accurate','skippedSourcePages':profile['nonProductPages']}
  s=align(s) if s.get('catalogType')=='list' else s
  s=finalize_translation(s)
  check=subprocess.run(['node',str(root/'scripts/validate-system.mjs')],input=json.dumps(s),text=True,capture_output=True,cwd=root)
  if check.returncode:raise ValueError(s['slug']+': '+check.stdout+check.stderr)
  dest=root/'content/products'/brand/(s['slug']+'.json')
  if dest.exists():
   old=json.loads(dest.read_text())
   if old.get('review',{}).get('sourceSha256')!=digest:raise ValueError('Refusing to overwrite another source: '+str(dest))
   if old.get('status')=='published':raise ValueError('Refusing to replace a published system with a draft: '+str(dest))
  prepared.append((dest,s));systems.append({'slug':s['slug'],'name':s['name'],'category':s['category'],'status':'draft','sourcePages':s['sourcePages'],'tables':len(s['specTables'])+len(s.get('referenceTables',[])),'rows':sum(len(t['rows'])for t in s['specTables']+s.get('referenceTables',[])),'flags':flags})
 # Validate the entire batch before writing any family.
 expected={dest for dest,s in prepared}
 for stale in (root/'content/products'/brand).glob('*.json'):
  if stale in expected:continue
  old=json.loads(stale.read_text())
  if old.get('status')=='draft' and old.get('review',{}).get('sourceSha256')==digest and (not profile.get('authorizedPhysicalPages')or(bool(old.get('sourcePages'))and set(old['sourcePages'])<=set(profile['authorizedPhysicalPages']))):stale.unlink()
 for dest,s in prepared:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 merged=write_merges(root,merges,digest)
 report={'mergedIntoExisting':merged,'pdf':str(pdf.relative_to(root)),'sha256':digest,'method':profile['method'],'systemsCreated':len(systems),'systems':systems,'nonProductPages':profile['nonProductPages'],'tablesCreated':sum(s['tables']for s in systems),'imagesExtracted':len(profile.get('assets',[])),'uncertainties':[f for s in systems for f in s['flags']],'translationWorkflow':'Codex-authored medical Russian; retained English; every translated field marked for medical review; no external adapter'}
 folder=root/'reports'/brand;folder.mkdir(parents=True,exist_ok=True);(folder/(profile.get('reportSlug',pdfslug)+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'systemsCreated':len(systems),'tablesCreated':report['tablesCreated'],'imagesExtracted':report['imagesExtracted'],'openFlagsByType':dict(collections.Counter(f['code']for f in report['uncertainties']))},ensure_ascii=False))
 return report
