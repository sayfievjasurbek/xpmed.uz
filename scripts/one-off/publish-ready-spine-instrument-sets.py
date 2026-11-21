"""Apply only reviewed photograph fields to imported sets, publishing complete zero-flag sets."""
import json,subprocess,datetime,collections,sys
from pathlib import Path
from PIL import Image
from finalize_translation_loader import finalize_translation
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';A=R/'public/images/products/double-medical/spine-instruments';profile=json.loads((R/'scripts/profiles/double-medical-spine-instruments.json').read_text());rows=json.loads((F/'rows-translated.json').read_text());byRow={r['id']:r['setCode']for r in rows};expected=json.loads((F/'artwork-images.json').read_text());expected={k:a for k,a in expected.items()if not k.startswith(('art-290-','art-308-','art-383-'))};expected.update(json.loads((F/'manual-photo-images.json').read_text()));ready=json.loads((A/'artwork-assets.json').read_text());ready={k:a for k,a in ready.items()if not k.startswith(('art-290-','art-308-','art-383-'))};ready.update(json.loads((A/'manual-photo-assets.json').read_text()));required=collections.defaultdict(set)
for key,a in expected.items():
 for p in a['placements']:required[byRow[p['sourceRowId']]].add(key)
damaged=set(json.loads((F/'gpu-damaged-images.json').read_text()))if(F/'gpu-damaged-images.json').exists()else set();repaired=set(json.loads((F/'cpu-repaired-images.json').read_text()))if(F/'cpu-repaired-images.json').exists()else set();safeReady=set(ready)-(damaged-repaired)
new=[];published=[];backup=F/'implant-link-backups';backup.mkdir(exist_ok=True)
for source in profile['systems']:
 path=R/'content/products/double-medical'/(source['slug']+'.json');s=json.loads(path.read_text());assert s.get('importPartition')=='spine-instruments';assert s['setCode']==source['setCode'];assert s['review']['sourceSha256']==profile['sha256'];assert s['name']==source['name'];assert s['sourcePages']==source['sourcePages']
 for old,t in zip(s['specTables'],source['specTables']):
  assert len(old['rows'])==len(t['rows'])
  for before,after in zip(old['rows'],t['rows']):
   assert before[1:]==after[1:], 'REF values are immutable during asset review'
   before[0]=after[0]
 for flag in source.get('reviewFlags',[]):
  if not any(f['code']==flag['code']and f.get('path')==flag.get('path')for f in s['review']['flags']):s['review']['flags'].append(flag)
 s['review']['status']='source-reviewed-with-open-items'if s['review']['flags']else'source-reviewed'
 if s['review']['flags']:s['status']='draft';path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 if not required[s['setCode']]<=safeReady:continue
 for key in required[s['setCode']]:
  a=ready[key];im=Image.open(R/'public'/a['src'].lstrip('/')).convert('RGBA');b=im.getchannel('A').getbbox();assert b and min(b[:2])>=32 and b[2]<=im.width-32 and b[3]<=im.height-32;assert a['captionFree']
 if s['review'].get('imageProcessing',{}).get('status')=='cpu-repair-pending':s['review']['imageProcessing']['status']='repaired-and-source-verified'
 for key in ['heroImage','imageType','gallery','imageDimensions','subcategory','specialty','relatedSystemSlugs','relatedRelationship']:s[key]=source[key]
 for old,t in zip(s['specTables'],source['specTables']):old['rowImages']=t['rowImages']
 if source.get('sourceImageNote'):s['sourceImageNote']=source['sourceImageNote']
 else:s.pop('sourceImageNote',None)
 if not s['review']['flags']:
  if s['status']!='published':new.append(s['slug'])
  s['status']='published';s.setdefault('publishedAt',datetime.datetime.now(datetime.timezone.utc).isoformat());published.append(s['slug']);s['review']['publicationDecision']='Owner-authorized automatic publication: verified codes, complete source-aligned photographs, zero open real flags'
 s=finalize_translation(s);path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
# Related links are additive. Public templates exclude draft targets.
ownSlugs={source['slug']for source in profile['systems']};targets={target for source in profile['systems']for target in source['relatedSystemSlugs']}|{p.stem for p in backup.glob('*.json')}
for target in targets:
 path=R/'content/products/double-medical'/(target+'.json');s=json.loads(path.read_text());saved=backup/(target+'.json')
 if not saved.exists():saved.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 desired=[source['slug']for source in profile['systems']if target in source['relatedSystemSlugs']];retained=[slug for slug in s.get('relatedSystemSlugs',[])if slug not in ownSlugs];s['relatedSystemSlugs']=list(dict.fromkeys(retained+desired));path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
reportPath=R/'reports/double-medical/spine-catalogue-instruments.json';report=json.loads(reportPath.read_text());report['publicationProgress']={'imagesComplete':len(ready),'imagesExpected':len(expected),'setsPublished':len(published),'newlyPublished':new,'status':'finishing-images'}
for s in report['systems']:
 if s['slug']in published:s['status']='published'
reportPath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report['publicationProgress']))
