"""Read-only audit of generated public HTML routes and asset references."""
from collections import Counter,defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json,re
R=Path(__file__).resolve().parents[1];D=R/'dist'
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.href=[];self.img=[];self.title='';self.desc='';self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a':self.href.append(a.get('href',''))
  if tag=='img':self.img.append(a)
  if tag=='title':self.in_title=True
  if tag=='meta' and a.get('name')=='description':self.desc=a.get('content','')
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,text):
  if self.in_title:self.title+=text
pages=[p for p in D.rglob('*.html') if p.name=='index.html' or p.name=='404.html'];missing_assets=[];missing_links=[];missing_alt=[];empty_alt=[];seen=defaultdict(list);descs=defaultdict(list);links=0;images=0
for p in pages:
 q=Parser();q.feed(p.read_text());route='/' + p.relative_to(D).as_posix().removesuffix('index.html')
 seen[(route.startswith('/en/'),q.title)].append(route);descs[(route.startswith('/en/'),q.desc)].append(route)
 for image in q.img:
  images+=1;src=image.get('src','')
  if 'alt' not in image:missing_alt.append([route,src])
  elif not image['alt']:empty_alt.append([route,src])
  if src.startswith('/') and not (D/unquote(src).lstrip('/')).exists():missing_assets.append([route,src])
 for href in q.href:
  links+=1
  if not href.startswith('/') or href.startswith('//'):continue
  target=unquote(urlsplit(href).path)
  if not target:continue
  file=D/target.lstrip('/')
  if not (file.is_file() or (file/'index.html').is_file()):missing_links.append([route,href])
report={'pages':len(pages),'images':images,'links':links,'missingAssets':missing_assets[:100],'missingAssetCount':len(missing_assets),'missingLinks':missing_links[:100],'missingLinkCount':len(missing_links),'imagesWithoutAlt':missing_alt[:100],'imagesWithoutAltCount':len(missing_alt),'emptyAltCount':len(empty_alt),'duplicateTitles':{str(k):v[:10] for k,v in seen.items() if len(v)>1},'duplicateDescriptions':{str(k):v[:10] for k,v in descs.items() if len(v)>1},'emptyDescriptions':[v for (lang,d),v in descs.items() if not d]}
(R/'reports/final-quality-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['pages','images','links','missingAssetCount','missingLinkCount','imagesWithoutAltCount','emptyAltCount']},ensure_ascii=False));print('dupe title',len(report['duplicateTitles']),'dupe desc',len(report['duplicateDescriptions']));print('missing links',missing_links[:12]);print('missing assets',missing_assets[:8]);print('alt',missing_alt[:8])
