"""Apply reviewed image/label refinements only to this import's unpublished drafts."""
import json,copy,subprocess
from pathlib import Path
from finalize_translation_loader import finalize_translation
R=Path(__file__).resolve().parents[1];p=json.loads((R/'scripts/profiles/double-medical-trauma-part2.json').read_text())
for source in p['systems']:
 file=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(file.read_text());assert s['status']=='draft'and s['review']['sourceSha256']==p['sha256']and s['importPartition']=='trauma-part2'
 assert s['refCodes']==source['refCodes']
 for key,value in source.items():
  if key not in ['reviewFlags','status']:s[key]=copy.deepcopy(value)
 s['review']['flags']=copy.deepcopy(source['reviewFlags']);s['review']['status']='source-reviewed';s=finalize_translation(s)
 result=subprocess.run(['node','scripts/validate-system.mjs'],input=json.dumps(s),text=True,capture_output=True,cwd=R)
 if result.returncode:raise ValueError(source['slug']+result.stdout+result.stderr)
 file.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('Reviewed draft refinements applied',len(p['systems']))
