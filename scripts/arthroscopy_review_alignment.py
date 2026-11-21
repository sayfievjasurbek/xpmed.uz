"""Keep review page images, code coordinates and public component links aligned with final tables."""
def align(s):
 ref=s['sourcePdf'].rsplit('/',1)[0]
 s['sourcePageImages']=[ref+f'/pages/{p:03}.webp'for p in s['sourcePages']]
 s['documentCover']=ref+'/pages/001.webp'
 for p,d in s.get('sourcePageDimensions',{}).items():
  if isinstance(d,list):s['sourcePageDimensions'][p]={'width':d[0],'height':d[1]}
 for component in s.get('components',[]):
  codes=set(component.get('refCodes',[]))
  matches=[(t,i,row)for t in s.get('specTables',[])for i,row in enumerate(t['rows'])if codes and codes.issubset({c for c in row[1:]if isinstance(c,str)})]
  match=next((m for m in matches if m[2][0]==component.get('name')),matches[0]if len(matches)==1 else None)
  if match:
   table,i,row=match;source=table['rowSources'][i];component.update(groupId=table['groupId'],name=row[0],sourceBounds=source.get('bounds',source.get('sourceBounds')),coordinateSpace='normalized',pdfPage=source['pdfPage'],codeEvidence=source['codeEvidence'])
 for flag in s.get('review',{}).get('flags',[]):
  flag['path']=flag.get('path')or flag.get('field')or 'specTables';flag['pdfPage']=flag.get('pdfPage')or flag.get('sourcePages',[None])[0]
  readings=flag.get('readings',[])
  target=next(iter(readings.values()),None)if isinstance(readings,dict)else readings[0]if readings else None
  if not isinstance(target,str):target=None
  if flag['code']=='manufacturer-description-conflict':target='Y1802'
  for ti,t in enumerate(s.get('specTables',[])):
   for ri,row in enumerate(t['rows']):
    if target and target in row[1:]:
     source=t['rowSources'][ri];flag.update(path=f'specTables.{ti}.rows.{ri}',sourceBounds=source.get('bounds',source.get('sourceBounds')));break
 return s
