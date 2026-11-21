#!/usr/bin/env python3
"""Record Codex-authored RU text as fields requiring human medical review.
No translation API, external adapter, or automated transliteration is used.
"""
import argparse,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def finalize(s):
 fields=[];missing=[];mismatch=[]
 def walk(v,path=''):
  if isinstance(v,dict):
   if set(v)=={'ru','en'} and isinstance(v['en'],str) and v['en']:
    fields.append(path+'.ru')
    if not v['ru'].strip():missing.append(path+'.ru')
    elif sorted(re.findall(r'\d+(?:[.,]\d+)?',v['ru']))!=sorted(re.findall(r'\d+(?:[.,]\d+)?',v['en'])):mismatch.append(path)
   else:
    for k,x in v.items():
     if k!='review':walk(x,path+'.'+k if path else k)
  elif isinstance(v,list):
   for i,x in enumerate(v):walk(x,path+'.'+str(i))
 walk(s)
 if missing:raise ValueError('Missing Russian translation: '+', '.join(missing))
 # Changed numbers in prose are never silently accepted.
 if mismatch:raise ValueError('Numeric tokens differ between RU/EN: '+', '.join(mismatch))
 r=s.setdefault('review',{});r['translatedFields']=fields;r['translationAuthor']='codex';r['translationStatus']='review-required';r['flags']=[f for f in r.get('flags',[]) if f['code']!='translation-required'];return s
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('system',type=Path);a=ap.parse_args();p=a.system.resolve()
 if not p.is_relative_to((ROOT/'content/products').resolve()):raise ValueError('Expected content/products system file')
 s=finalize(json.loads(p.read_text()));p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(f"{len(s['review']['translatedFields'])} Codex-translated fields marked for review")
 source=s.get('sourcePdf') or ''
 if source:
  report=ROOT/'reports'/s['brand']/(source.split('/')[-2]+'.json')
  if report.exists():
   data=json.loads(report.read_text())
   for entry in data.get('systems',[]):
    if entry['slug']==s['slug']:entry['flags']=s['review']['flags'];entry['translatedFields']=s['review']['translatedFields']
   data['uncertainties']=[f for entry in data.get('systems',[]) for f in entry.get('flags',[])]
   data['translationWorkflow']='Codex-authored professional Russian, retained English, translated fields require medical review; no external adapter'
   report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
