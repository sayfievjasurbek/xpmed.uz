import copy,json,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from import_multi_system_profile import import_multi_system_profile
class MultiSystemImportTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.pdf=self.root/'source.pdf';self.pdf.write_bytes(b'fixture');self.evidence=[{'dpi':600,'page':1,'pixelSize':[100,100]}]
 def system(self,slug='one'):
  return {'slug':slug,'brand':'conmed','category':'arthroscopy','name':{'ru':'Система','en':'System'},'shortDescription':{'ru':'Описание','en':'Description'},'description':{'ru':'Описание','en':'Description'},'sourcePages':[1],'specTables':[],'reviewFlags':[],'status':'published'}
 def run_import(self,systems):
  profile={'systems':systems,'nonProductPages':[],'method':'reviewed-source','assets':[]}
  with patch('import_multi_system_profile.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')):
   return import_multi_system_profile(self.root,self.pdf,'conmed','fixture','source-digest',self.evidence,profile)
 def test_import_is_draft_and_keeps_real_flags_and_translation_review(self):
  s=self.system();s['reviewFlags']=[{'code':'source-conflict','status':'open'}];self.run_import([s]);out=json.loads((self.root/'content/products/conmed/one.json').read_text());self.assertEqual(out['status'],'draft');self.assertEqual(out['review']['flags'],s['reviewFlags']);self.assertEqual(out['review']['translationStatus'],'review-required')
 def test_batch_does_not_write_first_system_when_later_brand_is_invalid(self):
  second=self.system('two');second['brand']='other'
  with self.assertRaisesRegex(ValueError,'brand mismatch'):self.run_import([self.system(),second])
  self.assertFalse((self.root/'content/products/conmed/one.json').exists())
 def test_published_system_is_never_replaced_with_imported_draft(self):
  p=self.root/'content/products/conmed/one.json';p.parent.mkdir(parents=True);old={'status':'published','review':{'sourceSha256':'source-digest'}};p.write_text(json.dumps(old))
  with self.assertRaisesRegex(ValueError,'published system'):self.run_import([self.system()])
  self.assertEqual(json.loads(p.read_text()),old)
 def test_changed_translation_number_aborts_without_writes(self):
  s=self.system();s['description']={'ru':'Диаметр 6 мм','en':'Diameter 5 mm'}
  with self.assertRaisesRegex(ValueError,'Numeric tokens differ'):self.run_import([s])
  self.assertFalse((self.root/'content/products/conmed/one.json').exists())
 def test_review_pages_and_component_search_follow_the_final_subgroup(self):
  s=self.system();s['sourcePages']=[3,4];s['catalogType']='list';self.evidence=[{'dpi':600,'page':i,'pixelSize':[100,200]}for i in range(1,5)]
  s['specTables']=[{'id':'final-table','groupId':'final-group','columns':['Description','Cat. No.'],'rows':[[{'ru':'Инструмент','en':'Instrument'},'REF-123']], 'rowSources':[{'pdfPage':3,'bounds':[.1,.2,.8,.3],'codeEvidence':[]}]}]
  s['components']=[{'name':{'ru':'Инструмент','en':'Instrument'},'refCodes':['REF-123'],'groupId':'old-group'}]
  self.run_import([s]);out=json.loads((self.root/'content/products/conmed/one.json').read_text())
  self.assertEqual(out['sourcePageImages'],['/catalogs/conmed/fixture/pages/003.webp','/catalogs/conmed/fixture/pages/004.webp'])
  self.assertEqual(out['components'][0]['groupId'],'final-group');self.assertEqual(out['components'][0]['pdfPage'],3)
  self.assertEqual(out['sourcePageDimensions']['3'],{'width':100,'height':200})
 def test_partition_cleanup_keeps_other_part_and_unscoped_drafts(self):
  folder=self.root/'content/products/conmed';folder.mkdir(parents=True)
  for slug,pages in [('other-part',[209]),('unscoped',[]),('stale-this-part',[210])]:
   (folder/(slug+'.json')).write_text(json.dumps({'status':'draft','sourcePages':pages,'review':{'sourceSha256':'source-digest'}}))
  s=self.system();s['sourcePages']=[210];profile={'partition':'instruments','authorizedPhysicalPages':[210],'systems':[s],'nonProductPages':[],'method':'reviewed-source'}
  with patch('import_multi_system_profile.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')):
   import_multi_system_profile(self.root,self.pdf,'conmed','fixture','source-digest',[{'dpi':600,'page':210,'pixelSize':[100,100]}],profile)
  self.assertTrue((folder/'other-part.json').exists());self.assertTrue((folder/'unscoped.json').exists());self.assertFalse((folder/'stale-this-part.json').exists())
