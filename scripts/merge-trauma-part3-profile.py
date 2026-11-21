"""Deduplicate reviewed Part 3 families against every existing name and REF."""
import json,re,collections,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'scripts/profiles/double-medical-trauma-part3.json';F=R/'reports/double-medical/trauma-catalogue-part3';p=json.loads(P.read_text())
baseline=json.loads((F/'existing-system-hashes.json').read_text())
existing=[]
for file in (R/'content/products').rglob('*.json'):
    backup=R/'reports/double-medical/trauma-catalogue/merge-backups'/p['sha256']/file.name
    source=backup if str(file.relative_to(R))in baseline and backup.exists()else file
    existing.append(json.loads(source.read_text()))
existing=[s for s in existing if s['brand']=='double-medical'and s.get('importPartition')!='trauma-part3']
def canonical(v):
    v=re.sub(r'\buhn\b','',v.casefold());return tuple(sorted(re.findall(r'[a-z]+|\d+(?:\.\d+)?',v)))
byname=collections.defaultdict(list);byref=collections.defaultdict(list);byset=collections.defaultdict(list)
for s in existing:
    byname[canonical(s['name']['en'])].append(s)
    for code in set(s.get('setCodes',[])+re.findall(r'\d{9}',s.get('setCode',''))):byset[code].append(s)
    if s.get('category')not in ['trauma-instrument-sets','spine-instrument-sets','arthroplasty-instrument-sets']:
        for code in s.get('refCodes',[]):byref[code].append(s)
merges=[];new=[];overlaps=[];rename={}
for s in p['systems']:
    exact=[x for x in byname[canonical(s['name']['en'])]if (x.get('category')=='trauma-instrument-sets')==(s['category']=='trauma-instrument-sets')]
    codes=collections.Counter(x['slug']for code in s.get('refCodes',[])for x in byref[code])if s['category']=='trauma-implants'else collections.Counter(x['slug']for code in s.get('setCodes',[])for x in byset[code])
    targets={x['slug']:x for x in exact}
    if codes:
        overlaps.append({'sourceName':s['name'],'sourcePages':s['sourcePages'],'refMatches':dict(codes)})
        if len(codes)==1:
            slug=next(iter(codes));targets[slug]=next(x for x in existing if x['slug']==slug)
    if len(targets)>1:raise ValueError('Ambiguous existing system matches: '+s['slug']+' '+str(list(targets)))
    if not targets:new.append(s);continue
    old=next(iter(targets.values()));rename[s['slug']]=old['slug']
    # Keep primary text, publication and all original sections untouched.
    patch={k:copy.deepcopy(s[k])for k in ['brand','sourcePages','refCodes','gallery','imageDimensions','relatedSystemSlugs','reviewFlags','availabilityNote']}
    patch['slug']=old['slug'];patch['referenceTables']=copy.deepcopy(s['specTables'])
    patch['category']=s['category'];patch['subcategory']=old.get('subcategory')or s['subcategory'];patch['subcategories']=list(dict.fromkeys(old.get('subcategories',[])+[old['subcategory']]if old.get('subcategory')else old.get('subcategories',[])))
    patch['subcategories']=list(dict.fromkeys(patch['subcategories']+s['subcategories']));patch['specialty']=list(dict.fromkeys(old.get('specialty',[])+s['specialty']))
    patch['matchedBy']='name + REF'if exact and codes else'name'if exact else'REF';patch['name']=old['name'];merges.append(patch)
for s in new+merges:s['relatedSystemSlugs']=list(dict.fromkeys(rename.get(slug,slug)for slug in s.get('relatedSystemSlugs',[])if rename.get(slug,slug)!=s['slug']))
p['systems']=new;p['merges']=merges;p['catalogTitle']={'ru':'Double Medical Trauma Catalogue — каталог продукции','en':'Double Medical Trauma Catalogue — product catalog'};p['existingMatchAudit']={'method':'Compare every family against all existing Double Medical names (normalized tokens) and all implant REF codes; shared tools alone do not merge instrument sets','overlaps':overlaps,'merged':[{'slug':s['slug'],'name':s['name'],'matchedBy':s['matchedBy'],'sourcePages':s['sourcePages']}for s in merges]}
P.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(F/'deduplication-audit.json').write_text(json.dumps(p['existingMatchAudit'],ensure_ascii=False,indent=2)+'\n');print('New',len(new),'merged',[(s['slug'],s['matchedBy'])for s in merges])
