import unittest,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from catalog_code_verification import pattern_candidates,verify_visual
class CodeVerificationTests(unittest.TestCase):
 def test_visual_agreement_is_required(self):
  readings=[{'reader':'ocr','text':'14731'}];candidates=pattern_candidates(readings,['T4732','T4931'])
  self.assertEqual(candidates[0]['value'],'T4731')
  self.assertTrue(verify_visual(None,readings,candidates)['flagged'])
  self.assertTrue(verify_visual({'reading':'T4731','confidence':'uncertain'},readings,candidates)['flagged'])
  self.assertEqual(verify_visual({'reading':'T4731','confidence':'clear'},readings,candidates)['value'],'T4731')
 def test_patterns_cannot_change_digits_or_use_one_seed(self):
  r=[{'reader':'ocr','text':'14731'}]
  self.assertEqual(pattern_candidates(r,['T4732']),[])
  candidates=pattern_candidates(r,['T4732','T4931'])
  self.assertIsNone(verify_visual({'reading':'T4732','confidence':'clear'},r,candidates)['value'])
  self.assertEqual(pattern_candidates([{'reader':'ocr','text':'1490'}],['T4906','T4907']),[])
 def test_visual_and_raw_ocr_can_resolve_low_confidence(self):
  self.assertEqual(verify_visual({'reading':'IM8120','confidence':'clear'},[{'reader':'ocr','text':'...IM8120','confidence':40}],[])['value'],'IM8120')
 def test_every_applied_cell_has_auditable_evidence_and_publication_clearance(self):
  report=json.loads((ROOT/'reports/conmed/verification-600/verification.json').read_text());self.assertEqual(report['visuallyRead'],212);self.assertEqual(report['verified']+report['stillFlagged'],257)
  self.assertEqual(sum(bool(r.get('officialEvidence'))for r in report['records']),report['confirmedOnConmedCom'])
  for r in report['records']:
   candidates=[json.loads(p.read_text())for p in (ROOT/'content/products/conmed').glob('*.json')];matched=[(s,t,i)for s in candidates for t in s.get('specTables',[])for i,row in enumerate(t.get('rowSources',[]))if any(e['tableId']==r['tableId']and e['row']==r['row']and e['column']==r['column']for e in row.get('codeEvidence',[]))];self.assertEqual(len(matched),1);s,t,i=matched[0];self.assertIn(s['status'],['draft','published']);self.assertFalse(s['review']['flags'])if s['status']=='published'else None;self.assertEqual(t['rows'][i][r['column']-1],r['value'])
   if 'userCorrection'in r:
    self.assertEqual(r['value'],'T4907');self.assertEqual(r['corroboratingSource']['pdfPage'],10);self.assertEqual(r['userCorrection']['visibility'],'internal-only')
   elif 'visualReading'in r:
    self.assertTrue((ROOT/r['lineCrop']).exists());checked=verify_visual(r['visualReading'],r['ocrReadings'],r['patternCandidates']);self.assertEqual(checked['value'],r['value'])
   if r.get('officialEvidence'):
    self.assertTrue(r['value']);self.assertTrue(all(e['code']==r['value']and e['url'].startswith('https://www.conmed.com/')for e in r['officialEvidence']))
if __name__=='__main__':unittest.main()
