"""Owner-confirmed catalog errata; preserve printed readings separately from ordering codes."""
CODES=('SP082700.042','SP082700.092')
NOTE={'ru':'Каталожный номер уточняйте у менеджера','en':'Confirm the catalog number with your sales representative'}
CORRECTION={'id':'p18-duplicate-kerrison-codes','pdfPage':18,'printed':'SP082700.042 / SP082700.092','corrected':'— / —','code':'SP082700.042 / SP082700.092','internalNote':'p.18 duplicate codes SP082700.042/.092 for the Ø2.0 mm rotatable irrigation Kerrison, ask SPINENDOS for the correct codes','visibility':'internal-only','basis':'Explicit owner source-catalog review; page 17 BDsys assignments retained'}
def apply_system(s):
 if s['brand']!='spinendos' or s['slug']!='forceps-punches-and-scissors':return s
 for t in s['specTables']:
  for i,row in enumerate(t['rows']):
   src=t['rowSources'][i];evidence=src.get('codeEvidence',[])
   printed=row[1] or next((e.get('printedCode')for e in evidence if e.get('printedCode')in CODES),None)
   if src['pdfPage']!=18 or printed not in CODES:continue
   row[1]=None
   t.setdefault('cellNotes',[])
   if not any(n['row']==i+1 and n['column']==2 for n in t['cellNotes']):t['cellNotes'].append({'row':i+1,'column':2,'text':NOTE.copy()})
   for e in evidence:e.update(printedCode=printed,value=None,sourceCorrectionId=CORRECTION['id'],verificationStatus='unavailable (source duplicate; owner confirmed)')
 for c in s.get('components',[]):
  if c.get('pdfPage')==18 and any(v in CODES for v in c.get('refCodes',[])):
   c['refCodes']=[]
   for e in c.get('codeEvidence',[]):e.update(printedCode=e.get('value'),value=None,sourceCorrectionId=CORRECTION['id'],verificationStatus='unavailable (source duplicate; owner confirmed)')
 if 'reviewFlags'in s:s['reviewFlags']=[f for f in s['reviewFlags']if f['code']!='source-specification-conflict']
 if 'review'in s:s['review']['flags']=[f for f in s['review']['flags']if f['code']!='source-specification-conflict']
 return s

def apply_verification(report):
 for r in report['records']:
  if r['pdfPage']==18 and r['value']in CODES:r.update(catalogValue=None,sourceCorrectionId=CORRECTION['id'],catalogValueStatus='unavailable (source duplicate; owner confirmed)')
 return report
