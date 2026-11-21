"""Run with the catalog virtualenv; OCR results are evidence, never corrected codes."""
import unittest,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from catalog_ocr import compare_code
from import_ocr_catalog import audit_code,issue
class OCRTests(unittest.TestCase):
 def test_ambiguous_characters_are_never_substituted(self):
  for a,b in [('OC4601','0C4601'),('IM8120','1M8120'),('LS8000','L58000'),('HD4300','HD43OO'),('VP8500','VPB500')]:
   result=compare_code({'text':a,'confidence':99},{'text':b,'confidence':99});self.assertTrue(result['flagged']);self.assertIsNone(result['value']);self.assertEqual(result['pass1'],a);self.assertEqual(result['pass2'],b)
 def test_low_confidence_and_missing_pass_are_empty(self):
  for second in [{'text':'IM8000','confidence':89.9},{'text':'','confidence':-1}]:self.assertIsNone(compare_code({'text':'IM8000','confidence':99},second)['value'])
  self.assertEqual(compare_code({'text':'IM8000','confidence':99},{'text':'IM8000','confidence':90})['value'],'IM8000')
 def test_manual_candidate_cannot_override_ocr(self):
  record={'page':4,'printedPage':2,'passes':{str(n):{'words':[{'text':'IM8000','confidence':99,'bounds':[.85,.32,.9,.33]}]}for n in [3,11]}}
  result=audit_code(record,'IM8OOO',[.4,.315,.92,.335],[.83,.92]);self.assertIsNone(result['value']);self.assertIn('source-transcription-disagreement',result['reasons'])
 def test_review_flag_retains_exact_path_and_position(self):
  f=issue('specTables.2.rows.5.1','ocr-code-review','Проверка',13,[.84,.5,.9,.51]);self.assertEqual(f['path'],'specTables.2.rows.5.1');self.assertEqual(f['pdfPage'],13);self.assertEqual(f['sourceBounds'],[.84,.5,.9,.51])
 def test_import_is_draft_only_and_every_uncertain_cell_is_null(self):
  report=json.loads((ROOT/'reports/conmed/advanced-visualization-system.json').read_text());self.assertEqual(report['systemsFound'],10);self.assertEqual(report['componentsFound'],238);self.assertEqual(report['catalogNumberOccurrences'],257);self.assertEqual(report['nonProductPages'],[1,2,3,17,18,19,20])
  systems={p.stem:json.loads(p.read_text())for p in (ROOT/'content/products/conmed').glob('*.json')if json.loads(p.read_text()).get('catalogType')=='list' and '/advanced-visualization-system/'in json.loads(p.read_text()).get('sourcePdf','')}
  for s in systems.values():
   self.assertIn(s['status'],['draft','published']);self.assertFalse(s['review']['flags'])if s['status']=='published'else None;self.assertTrue(set(s['sourcePages']).issubset(set(range(4,17))));self.assertTrue(s['review']['translatedFields']);self.assertEqual(s['availabilityNote']['en'],'All products may not be available in all markets')
  for f in report['flaggedCodes']:
   s=systems[f['system']];table=next(t for t in s['specTables']if t['id']==f['tableId']);self.assertIsNone(table['rows'][f['row']-1][f['column']-1]);self.assertTrue(all(0<=v<=1 for v in f['sourceBounds']))
  self.assertEqual(len({link['url']for s in systems.values()for link in s['manufacturerLinks']}),2)
  sheath=systems['cannulas'];self.assertEqual(sheath['sourcePages'],[13]);table=next(t for t in sheath['specTables']if t['id']=='pressure-sensing-cannula');self.assertEqual(table['rows'][1][1],'')
if __name__=='__main__':unittest.main()
