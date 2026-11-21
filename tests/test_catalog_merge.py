import copy,json,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog_merge import prepare_merges,write_merges
class AdditiveCatalogMergeTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.path=self.root/'content/products/double-medical/existing.json';self.path.parent.mkdir(parents=True)
  self.original={'slug':'existing','brand':'double-medical','status':'published','sourcePdf':'/catalogs/double-medical/brochure/source.pdf','sourcePages':[2],'description':{'ru':'Описание','en':'Overview'},'specTables':[{'id':'sizes','columns':['Size'],'rows':[['14']]}],'variants':[{'id':'primary'}],'review':{'sourceSha256':'brochure'}};self.path.write_text(json.dumps(self.original))
  self.profile={'catalogTitle':{'ru':'Каталог','en':'Catalog'},'merges':[{'slug':'existing','brand':'double-medical','sourcePages':[8],'refCodes':['130890101S'],'relatedSystemSlugs':['tools'],'referenceTables':[{'id':'joint-refs','columns':['REF','Size'],'rows':[['130890101S',{'ru':'14 мм','en':'14 mm'}]]}]}]}
 def prepare(self):
  with patch('catalog_merge.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')):return prepare_merges(self.root,self.profile,'joint-hash','/catalogs/double-medical/joint')
 def test_merge_retains_brochure_variants_and_publication_and_backs_up_original(self):
  prepared=self.prepare();self.assertEqual(json.loads(self.path.read_text()),self.original);write_merges(self.root,prepared,'joint-hash');result=json.loads(self.path.read_text())
  for key in ['status','specTables','variants','sourcePdf','sourcePages']:self.assertEqual(result[key],self.original[key])
  self.assertEqual(result['review']['sourceSha256'],self.original['review']['sourceSha256']);self.assertIn('referenceTables.0.rows.0.1.ru',result['review']['translatedFields']);self.assertEqual(result['referenceTables'][0]['sourcePdf'],'/catalogs/double-medical/joint/source.pdf');self.assertEqual(result['refCodes'],['130890101S']);self.assertEqual(json.loads(next((self.root/'reports').rglob('existing.json')).read_text()),self.original)
 def test_same_source_cannot_be_merged_twice(self):
  write_merges(self.root,self.prepare(),'joint-hash')
  with self.assertRaisesRegex(ValueError,'already merged'):self.prepare()
 def test_conflicts_stay_internal_on_contributing_catalog_and_do_not_replace_brochure(self):
  self.profile['merges'][0]['reviewFlags']=[{'code':'source-conflict','message':{'ru':'5 или 15 мм','en':'5 or 15 mm'}}];prepared=self.prepare();result=prepared[0][1];self.assertEqual(result['catalogImports'][0]['review']['flags'][0]['code'],'source-conflict');self.assertEqual(result['specTables'],self.original['specTables'])
