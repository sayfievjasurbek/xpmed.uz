"""Owner-approved source errata; original OCR and visual readings remain unchanged."""
BROCHURE='https://www.conmed.com/-/media/conmed/documents/literature/y-knotflex_productbrochure.ashx'
RESECTION='https://www.conmed.com/en/products/resection-fluid-management-and-ablation/resection/conmed-arthroscopic-resection'
CORRECTIONS=[
 {'id':'p16-blue-suture','pdfPage':16,'printedCodes':['Y1802'],'correctedCodes':['Y1802A'],'internalNote':'p.16 Y1802 → Y1802A (blue suture), confirm with XPMED sales','verificationStatus':'confirmed in CONMED brochure','manufacturerUrl':BROCHURE},
 {'id':'p94-missing-footnote','pdfPage':94,'printedCodes':['EL9299U*','EL9299D**'],'correctedCodes':['EL9299U','EL9299D'],'internalNote':'p.94 missing footnote: * / ** are footnote markers, not part of the catalog numbers. Add a legend for EL9299U (concave) and EL9299D (convex); no footnote was printed.','verificationStatus':'confirmed on conmed.com','manufacturerUrl':RESECTION}
]
def corrected_record(r):
 value=r.get('value')
 if r.get('pdfPage')==16 and value=='Y1802':
  r['printedCode']=value;r['value']='Y1802A';r['verificationStatus']='confirmed in CONMED brochure';r['sourceCorrectionId']='p16-blue-suture';r['confirmedOnConmedCom']=True;r['officialEvidence']=[{'url':BROCHURE,'code':'Y1802A','confirmation':'confirmed in CONMED brochure'}]
 elif r.get('pdfPage')==94 and value in ['EL9299U*','EL9299D**']:
  r['printedCode']=value;r['value']=value.rstrip('*');r['verificationStatus']='confirmed on conmed.com';r['sourceCorrectionId']='p94-missing-footnote';r['confirmedOnConmedCom']=True;r['markerInterpretation']='Footnote marker, not part of catalog number; owner confirmed';r['officialEvidence']=[{'url':RESECTION,'code':r['value'],'confirmation':'Concave configuration'if r['value'].endswith('U')else'Convex configuration'}]
 return r

def apply_system(s):
 if s.get('sourcePdf') and '/arthroscopy-product-catalog/'not in s['sourcePdf']:return s
 is_blue=s['slug']=='shoulder-arthroscopy-instability-repair'
 if is_blue:
  s['refCodes']=['Y1802A'if c=='Y1802'else c for c in s['refCodes']]
  for t in s['specTables']:
   for i,row in enumerate(t['rows']):
    if 'Y1802'in row[1:] or 'Y1802A'in row[1:]:
     row[1:]=['Y1802A'if c=='Y1802'else c for c in row[1:]]
     row[0]['ru']='Полностью шовный якорный фиксатор Y-Knot® Flex, 1.8 мм, с двумя нитями Hi-Fi №2 (синяя нить)'
     for evidence in t['rowSources'][i]['codeEvidence']:
      evidence['printedCode']='Y1802';evidence['value']='Y1802A';evidence['verificationStatus']='confirmed in CONMED brochure';evidence['officialEvidence']=[{'url':BROCHURE,'code':'Y1802A','confirmation':'confirmed in CONMED brochure'}]
  for c in s.get('components',[]):c['refCodes']=['Y1802A'if x=='Y1802'else x for x in c.get('refCodes',[])]
 if s['slug']=='arthroscopy-resection-large-hub-shaver-blades':
  ru='Удлинённые насадки Great White: EL9299U — вогнутая конфигурация, EL9299D — выпуклая; каталожные позиции представлены в связанной системе для тазобедренного сустава.'
  en='Extended-length Great White models: EL9299U is concave and EL9299D is convex; catalog entries are provided in the related Hip Blades and Burs system.'
  if 'EL9299U'not in s['description']['en']:s['description']['ru']+=' '+ru;s['description']['en']+=' '+en
 for key in ['reviewFlags']:
  if key in s:s[key]=[f for f in s[key]if f['code']not in ['manufacturer-description-conflict','unexplained-code-marker']]
 if 'review'in s:s['review']['flags']=[f for f in s['review'].get('flags',[])if f['code']not in ['manufacturer-description-conflict','unexplained-code-marker']]
 return s
