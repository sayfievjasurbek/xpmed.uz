#!/usr/bin/env python3
"""Loopback-only review server. Never packaged in dist. Run from any directory."""
import re
import argparse,hashlib,json,mimetypes,os,secrets,subprocess,tempfile,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs,unquote
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];CONTENT=ROOT/'content/products';TOKEN=secrets.token_urlsafe(32);LOCK=threading.Lock()
def version(data):return hashlib.sha256(data).hexdigest()
def system_path(key):
 if not isinstance(key,str) or len(key.split('/'))!=2:raise ValueError('Invalid system ID')
 p=(CONTENT/(key+'.json')).resolve()
 if not p.is_relative_to(CONTENT.resolve()) or not p.is_file():raise ValueError('Unknown system')
 return p
class Handler(BaseHTTPRequestHandler):
 def respond(self,data,status=200,kind='application/json; charset=utf-8'):
  if not isinstance(data,bytes):data=json.dumps(data,ensure_ascii=False).encode()
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','SAMEORIGIN');self.end_headers();self.wfile.write(data)
 def serve_file(self,target):
  size=target.stat().st_size;start=0;end=size-1;partial=False
  requested=self.headers.get('Range')
  if requested:
   match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested.strip())
   if not match or not any(match.groups()):
    self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return
   left,right=match.groups()
   if left:start=int(left);end=min(int(right) if right else size-1,size-1)
   else:start=max(0,size-int(right))
   if start>=size or end<start:
    self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return
   partial=True
  self.send_response(206 if partial else 200);self.send_header('Content-Type',mimetypes.guess_type(target)[0] or 'application/octet-stream');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1));self.send_header('Cache-Control','no-cache');self.send_header('X-Content-Type-Options','nosniff')
  if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  if self.command=='HEAD':return
  try:
   with target.open('rb') as stream:
    stream.seek(start);remaining=end-start+1
    while remaining:
     chunk=stream.read(min(65536,remaining))
     if not chunk:break
     self.wfile.write(chunk);remaining-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
 def do_HEAD(self):self.do_GET()
 def do_GET(self):
  try:
   req=urlparse(self.path);p=unquote(req.path);q=parse_qs(req.query)
   if p=='/admin/review' or p=='/admin/review/':return self.respond((ROOT/'admin/review.html').read_text().replace('__REVIEW_TOKEN__',TOKEN).encode(),kind='text/html; charset=utf-8')
   if p=='/admin/api/systems':
    systems=[]
    for path in sorted(CONTENT.glob('*/*.json')):
     data=path.read_bytes();s=json.loads(data)
     if s['status']=='draft':systems.append({'id':s['brand']+'/'+s['slug'],'name':s['name'],'flags':s.get('review',{}).get('flags',[]),'skipped':s.get('review',{}).get('skipped',False),'version':version(data)})
    return self.respond(systems)
   if p=='/admin/api/system':
    data=system_path(q.get('id',[''])[0]).read_bytes();return self.respond({'system':json.loads(data),'version':version(data)})
   if p=='/admin/preview':
    path=system_path(q.get('id',[''])[0]);lang=q.get('lang',['ru'])[0];r=subprocess.run(['node','scripts/render-system.mjs',str(path),lang],capture_output=True,cwd=ROOT)
    if r.returncode:return self.respond({'error':r.stderr.decode()},500)
    return self.respond(r.stdout,kind='text/html; charset=utf-8')
   if p.startswith('/admin/'):return self.respond({'error':'Not found'},404)
   base=ROOT/'public' if p.startswith('/images/products/') or (p.startswith('/catalogs/') and Path(p).suffix.lower() in ('.pdf','.webp','.png','.jpg','.jpeg')) else ROOT/'dist'
   target=(base/p.lstrip('/')).resolve()
   if not target.is_relative_to(base.resolve()):return self.respond({'error':'Forbidden'},403)
   if target.is_dir():target=target/'index.html'
   if not target.is_file():return self.respond({'error':'Not found'},404)
   return self.serve_file(target)
  except (ValueError,KeyError,json.JSONDecodeError) as e:self.respond({'error':str(e)},400)
 def do_POST(self):
  try:
   # A per-process token and exact Origin prevent other websites mutating localhost.
   origin=self.headers.get('Origin');allowed=f'http://127.0.0.1:{self.server.server_port}'
   if self.headers.get('X-Review-Token')!=TOKEN or origin!=allowed:return self.respond({'error':'Invalid local review origin/token'},403)
   if self.headers.get('Content-Type')!='application/json':return self.respond({'error':'JSON required'},415)
   length=int(self.headers.get('Content-Length','0'))
   if length<1 or length>4_000_000:return self.respond({'error':'Invalid request size'},413)
   body=json.loads(self.rfile.read(length));path=system_path(body.get('id'));action=urlparse(self.path).path.rsplit('/',1)[-1]
   if action not in ['save','publish','skip']:return self.respond({'error':'Not found'},404)
   with LOCK:
    previous=path.read_bytes()
    if body.get('version')!=version(previous):return self.respond({'error':'JSON changed; reload before saving.'},409)
    old=json.loads(previous);s=body.get('system') if action=='save' else old
    if not isinstance(s,dict) or s.get('brand')!=old['brand'] or s.get('slug')!=old['slug']:raise ValueError('Brand/slug identity cannot be edited here')
    if action=='save':s['status']='draft';s.setdefault('review',{})['editedAt']=datetime.now(timezone.utc).isoformat()
    if action=='skip':s.setdefault('review',{})['skipped']=True
    if action=='publish':
     if s.get('review',{}).get('flags') and not body.get('acknowledgeFlags'):raise ValueError('Review and acknowledge flagged fields first')
     if not all(s.get('name',{}).get(l,'').strip() for l in ['ru','en']):raise ValueError('Both RU and EN names are required')
     s['status']='published';s.setdefault('review',{})['publishedAt']=datetime.now(timezone.utc).isoformat()
    check=subprocess.run(['node','scripts/validate-system.mjs'],input=json.dumps(s),capture_output=True,text=True,cwd=ROOT)
    if check.returncode:return self.respond({'error':check.stdout+check.stderr},422)
    temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');os.replace(temp,path)
    if action=='publish':
     build=subprocess.run(['node','build.mjs'],cwd=ROOT,capture_output=True,text=True)
     if build.returncode:path.write_bytes(previous);subprocess.run(['node','build.mjs'],cwd=ROOT,capture_output=True);return self.respond({'error':build.stderr},500)
    return self.respond({'ok':True,'version':version(path.read_bytes())})
  except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.respond({'error':str(e)},400)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=4180);a=ap.parse_args();server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);print(f'Local review: http://127.0.0.1:{a.port}/admin/review',flush=True);server.serve_forever()
