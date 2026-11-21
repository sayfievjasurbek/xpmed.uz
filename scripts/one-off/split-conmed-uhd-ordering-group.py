"""Separate the mixed page-9 ordering group without changing any catalog number."""
import json,copy
from pathlib import Path
root=Path(__file__).resolve().parents[1];folder=root/'content/products/conmed'
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
a=json.loads((folder/'conmed-arthroscopes.json').read_text());b=json.loads((folder/'sheath-and-bridge-systems.json').read_text())
t=next(t for t in a['specTables']if t['id']=='uhd-4mm-arthroscope');g=next(g for g in a['componentGroups']if g['id']==t['id'])
if len(t['rows'])==19:
 nt=copy.deepcopy(t);ng=copy.deepcopy(g);gid='uhd-4mm-sheath-bridge';name={'ru':'Тубусы и мосты QuickLatch® для UHD-артроскопов 4 мм','en':'QuickLatch® sheaths and bridges for 4 mm UHD arthroscopes'};nt.update(id=gid,groupId=gid,title=name);ng.update(id=gid,tableId=gid,name=name)
 nt['rows']=nt['rows'][4:];nt['rowSources']=nt['rowSources'][4:];t['rows']=t['rows'][:4];t['rowSources']=t['rowSources'][:4]
 moved=[c for c in a['components']if c['groupId']==g['id']and int(c['id'].split('-')[-1])>4]
 for c in moved:c['groupId']=gid
 b['components'].extend(moved);a['components']=[c for c in a['components']if c not in moved];ng['componentIds']=[c['id']for c in moved];g['componentIds']=[c['id']for c in a['components']if c['groupId']==g['id']]
 bridge=[i for i in g['images']if 'c988e0eb'in i['src']];ng['images']=bridge;nt['images']=bridge;g['images']=[i for i in g['images']if i not in bridge];t['images']=g['images'];a['gallery']=[i for i in a['gallery']if i not in bridge];b['gallery'].extend(bridge)
 g['keyParameters']=[];t['keyParameters']=[];b['specTables'].append(nt);b['componentGroups'].append(ng)
 moved_features=[f for f in a['features']if f.get('groupId')==g['id']]
 for f in moved_features:f['groupId']=gid
 b['features'].extend(moved_features);a['features']=[f for f in a['features']if f not in moved_features]
 for s in [a,b]:
  s['refCodes']=list(dict.fromkeys(code for c in s['components']for code in c['refCodes']));s['sourcePages']=sorted({n for t in s['specTables']for n in t['sourcePages']});s['sourcePageImages']=[f'/catalogs/conmed/advanced-visualization-system/pages-600/{n:03}.webp'for n in s['sourcePages']]
 dump(folder/'conmed-arthroscopes.json',a);dump(folder/'sheath-and-bridge-systems.json',b)
