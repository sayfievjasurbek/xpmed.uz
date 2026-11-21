import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog_partition import disjoint_partition,validate_partition_evidence
class CatalogPartitionTests(unittest.TestCase):
 def setUp(self):self.p={'partition':'instruments','authorizedPhysicalPages':[210,211],'systems':[{'sourcePages':[210,211]}]}
 def test_disjoint_existing_implants_are_preserved(self):self.assertTrue(disjoint_partition('instruments',self.p,{'sourcePages':[4,209]}))
 def test_unknown_overlap_and_unscoped_content_are_protected(self):
  for section,p,previous in [(None,self.p,{'sourcePages':[4]}),('other',self.p,{'sourcePages':[4]}),('instruments',self.p,{'sourcePages':[209,210]}),('instruments',self.p,{'sourcePages':[]})]:self.assertFalse(disjoint_partition(section,p,previous))
 def test_partial_or_out_of_scope_evidence_is_rejected(self):
  validate_partition_evidence(self.p,[{'page':210},{'page':211}])
  for pages in [[210],[209,210,211],[210,211,412]]:
   with self.assertRaises(ValueError):validate_partition_evidence(self.p,[{'page':p}for p in pages])
