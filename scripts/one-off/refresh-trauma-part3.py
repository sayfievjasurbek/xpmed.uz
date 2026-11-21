"""Apply reviewed recipe refinements only to this partition's already imported systems."""
import copy,json
from pathlib import Path
from finalize_translation_loader import finalize_translation
from arthroscopy_review_alignment import align
R=Path(__file__).resolve().parents[1];p=json.loads((R/'scripts/profiles/double-medical-trauma-part3.json').read_text())
for source in p['systems']:
 path=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(path.read_text());assert s['importPartition']=='trauma-part3';assert s['refCodes']==source['refCodes'];assert s['sourcePages']==source['sourcePages']
 for key in ['specTables','components','gallery','imageDimensions','relatedSystemSlugs']:s[key]=copy.deepcopy(source[key])
 s=finalize_translation(align(s));path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('Refreshed current partition only:',len(p['systems']))
