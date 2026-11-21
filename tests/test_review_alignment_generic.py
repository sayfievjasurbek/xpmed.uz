import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from arthroscopy_review_alignment import align

class GenericAlignmentTests(unittest.TestCase):
    def test_duplicate_refs_keep_distinct_names_and_dictionary_readings_accept_normalized_bounds(self):
        source={'pdfPage':205,'sourceBounds':[.1,.2,.5,.3],'codeEvidence':[]}
        s={'sourcePdf':'/catalogs/brand/file/source.pdf','sourcePages':[205],
           'specTables':[{'id':'a','groupId':'a','rows':[['Pliers','110021300'],['Hook','110021300']], 'rowSources':[source,source]}],
           'components':[{'name':'Pliers','refCodes':['110021300']},{'name':'Hook','refCodes':['110021300']}],
           'review':{'flags':[{'code':'source-ref-prefix-outlier','readings':{'PSM3':'110021300'},'sourcePages':[205]}]}}
        actual=align(s)
        self.assertEqual([c['name']for c in actual['components']],['Pliers','Hook'])
        self.assertEqual(actual['components'][1]['sourceBounds'],source['sourceBounds'])
        self.assertEqual(actual['review']['flags'][0]['sourceBounds'],source['sourceBounds'])
