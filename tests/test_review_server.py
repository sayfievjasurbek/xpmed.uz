import importlib.util,unittest,tempfile,threading,json,urllib.request,urllib.error
from pathlib import Path
spec=importlib.util.spec_from_file_location('review',Path(__file__).resolve().parents[1]/'scripts/review-server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.real=m.ROOT;cls.temp=tempfile.TemporaryDirectory();m.ROOT=Path(cls.temp.name);m.CONTENT=m.ROOT/'content/products';(m.CONTENT/'test-brand').mkdir(parents=True)
  (m.ROOT/'scripts').mkdir();(m.ROOT/'scripts/validate-system.mjs').symlink_to(cls.real/'scripts/validate-system.mjs')
  (m.ROOT/'build.mjs').write_text("import fs from 'node:fs';fs.writeFileSync('build-ran','ok');")
  cls.fixture=json.loads((cls.real/'content/products/double-medical/cynthia-knee-system.json').read_text());cls.fixture.update(brand='test-brand',slug='test-system',status='draft');cls.path=m.CONTENT/'test-brand/test-system.json'
  cls.server=m.ThreadingHTTPServer(('127.0.0.1',0),m.Handler);cls.origin='http://127.0.0.1:'+str(cls.server.server_port);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.temp.cleanup();m.ROOT=cls.real;m.CONTENT=cls.real/'content/products'
 def setUp(self):self.path.write_text(json.dumps(self.fixture))
 def post(self,action,**kwargs):
  body={'id':'test-brand/test-system','version':m.version(self.path.read_bytes()),**kwargs};headers={'Content-Type':'application/json','X-Review-Token':m.TOKEN,'Origin':self.origin};request=urllib.request.Request(self.origin+'/admin/api/'+action,data=json.dumps(body).encode(),headers=headers)
  try:
   with urllib.request.urlopen(request)as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_mutation_rejects_foreign_origin(self):
  request=urllib.request.Request(self.origin+'/admin/api/skip',data=b'{}',headers={'Content-Type':'application/json','Origin':'https://other.example'})
  with self.assertRaises(urllib.error.HTTPError)as e:urllib.request.urlopen(request)
  self.assertEqual(e.exception.code,403)
 def test_save_validation_conflict_and_skip(self):
  altered=json.loads(json.dumps(self.fixture));altered['name']['ru']='Изменённый черновик';old=m.version(self.path.read_bytes());status,_=self.post('save',system=altered);self.assertEqual(status,200);self.assertEqual(json.loads(self.path.read_text())['status'],'draft');self.assertEqual(self.post('skip',version=old)[0],409);self.assertEqual(self.post('skip')[0],200);self.assertTrue(json.loads(self.path.read_text())['review']['skipped'])
  self.assertEqual(self.post('save',system={'slug':'test-system','brand':'test-brand'})[0],422)
 def test_publish_requires_ack_and_runs_local_build(self):
  self.assertEqual(self.post('publish')[0],400);self.assertEqual(self.post('publish',acknowledgeFlags=True)[0],200);self.assertEqual(json.loads(self.path.read_text())['status'],'published');self.assertTrue((m.ROOT/'build-ran').exists())
 def test_path_traversal_rejected(self):
  for key in ['../secret','test-brand/../../../secret','/etc/passwd']:
   with self.assertRaises(ValueError):m.system_path(key)
 def test_pdf_range_requests_and_library_route(self):
  source=m.ROOT/'public/catalogs/test/source.pdf';source.parent.mkdir(parents=True,exist_ok=True);data=b'%PDF-'+bytes(range(256))*8;source.write_bytes(data)
  library=m.ROOT/'dist/catalogs/index.html';library.parent.mkdir(parents=True,exist_ok=True);library.write_text('<h1>Catalog library</h1>')
  with urllib.request.urlopen(self.origin+'/catalogs/') as r:self.assertIn(b'Catalog library',r.read())
  request=urllib.request.Request(self.origin+'/catalogs/test/source.pdf',headers={'Range':'bytes=0-63'})
  with urllib.request.urlopen(request) as r:
   self.assertEqual(r.status,206);self.assertEqual(r.read(),data[:64]);self.assertEqual(r.headers['Content-Range'],f'bytes 0-63/{len(data)}')
  request=urllib.request.Request(self.origin+'/catalogs/test/source.pdf',headers={'Range':'bytes=-12'})
  with urllib.request.urlopen(request) as r:self.assertEqual(r.read(),data[-12:])
  with urllib.request.urlopen(urllib.request.Request(self.origin+'/catalogs/test/source.pdf',method='HEAD')) as r:self.assertEqual(int(r.headers['Content-Length']),len(data));self.assertEqual(r.headers['Accept-Ranges'],'bytes');self.assertEqual(r.read(),b'')
  with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(urllib.request.Request(self.origin+'/catalogs/test/source.pdf',headers={'Range':'bytes=999999-'}))
  self.assertEqual(error.exception.code,416)
if __name__=='__main__':unittest.main()
