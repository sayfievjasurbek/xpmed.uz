"""Explicit, additive catalog imports; never replace an existing system/brochure."""
import copy,json,hashlib,subprocess
from pathlib import Path
from finalize_translation_loader import finalize_translation

def prepare_merges(root,profile,digest,source_ref):
 prepared=[]
 for patch in profile.get('merges',[]):
  dest=root/'content/products'/patch['brand']/(patch['slug']+'.json');raw=dest.read_bytes();old=json.loads(raw);s=copy.deepcopy(old)
  if old['brand']!=patch['brand']or old['slug']!=patch['slug']:raise ValueError('Merge identity mismatch')
  previous=next((x for x in s.get('catalogImports',[])if x.get('sourceSha256')==digest),None)
  if previous:raise ValueError('This catalog is already merged into '+patch['slug'])
  tables=copy.deepcopy(patch['referenceTables'])
  for t in tables:t['sourcePdf']=source_ref+'/source.pdf'
  existing_ids={t['id']for t in s.get('referenceTables',[])}
  if any(t['id']in existing_ids for t in tables):raise ValueError('Duplicate reference table ID')
  if patch.get('referenceVariantId'):s['referenceVariantId']=patch['referenceVariantId']
  s['referenceTables']=s.get('referenceTables',[])+tables
  s['refCodes']=list(dict.fromkeys(s.get('refCodes',[])+patch.get('refCodes',[])))
  s['relatedSystemSlugs']=list(dict.fromkeys(s.get('relatedSystemSlugs',[])+patch.get('relatedSystemSlugs',[])))
  source={'sourceSha256':digest,'sourcePdf':source_ref+'/source.pdf','catalogTitle':profile['catalogTitle'],'sourcePages':patch['sourcePages'],'documentCover':source_ref+'/pages/001.webp','review':{'flags':patch.get('reviewFlags',[]),'status':'review-required'if patch.get('reviewFlags')else'verified'}}
  s['catalogImports']=s.get('catalogImports',[])+[source]
  # A reviewed additive import may supply photos and taxonomy without replacing clinical prose.
  for key in ['category','subcategory','subcategories','specialty','availabilityNote']:
   if key in patch:s[key]=copy.deepcopy(patch[key])
  for image in patch.get('gallery',[]):
   src=image if isinstance(image,str)else image['src']
   if not any((item if isinstance(item,str)else item['src'])==src for item in s.get('gallery',[])):s.setdefault('gallery',[]).append(copy.deepcopy(image))
  s.setdefault('imageDimensions',{}).update(copy.deepcopy(patch.get('imageDimensions',{})))
  # The primary source, publication state and all clinical/brochure sections are protected.
  for key in ['status','sourcePdf','sourcePages','variants','specTables','features','hotspots','description','heroImage']:
   if s.get(key)!=old.get(key):raise ValueError('Protected merge field changed: '+key)
  s=finalize_translation(s)
  check=subprocess.run(['node',str(root/'scripts/validate-system.mjs')],input=json.dumps(s),text=True,capture_output=True,cwd=root)
  if check.returncode:raise ValueError(check.stdout+check.stderr)
  prepared.append((dest,s,raw))
 return prepared

def write_merges(root,prepared,digest):
 for dest,s,raw in prepared:
  pdfslug=s['catalogImports'][-1]['sourcePdf'].split('/')[-2];backup=root/'reports'/s['brand']/pdfslug/'merge-backups'/digest
  backup.mkdir(parents=True,exist_ok=True);(backup/dest.name).write_bytes(raw)
  dest.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 return [{'slug':s['slug'],'tablesAdded':len(s['referenceTables']),'status':s['status']}for dest,s,raw in prepared]
