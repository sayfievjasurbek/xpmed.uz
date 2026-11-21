"""Reconcile exact readings, retaining all disagreements for source review."""
import json,re,collections
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue';O=R/'public/catalogs/double-medical/spine-catalogue/ocr';T=json.loads((F/'tables-evidence.json').read_text());G={(g['table'],g['row'],g['column']):g for g in json.loads((F/'glyph-readings.json').read_text())};pending=[];changes=[];allcodes=[]
for t in T:
 for ri,row in enumerate(t['rows']):
  for ci,cell in enumerate(row['values']):
   ev=row['evidence'][ci];glyph=G.get((t['id'],ri,ci));reads=ev['readings'];iscode=t['headerReadings'][ci].startswith('REF')
   if glyph:ev['sourceGlyphReading']={k:v for k,v in glyph.items()if k not in ['readings']}
   if not iscode and glyph and glyph['accepted']:
    candidate=glyph['text'];agreements=[k for k,v in reads.items()if re.sub(r'\s+','',v)==candidate]
    if agreements:
     if cell!=candidate:changes.append({'id':f"{t['id']}:{ri}:{ci}",'previous':cell,'value':candidate,'readings':reads})
     row['values'][ci]=candidate;ev['value']=candidate;ev['verification']='source glyph + '+', '.join(agreements)
    elif cell!=candidate:cell=None;row['values'][ci]=None
   value=row['values'][ci]
   if iscode:
    agreed=[k for k,v in reads.items()if v==value]
    ev['verification']='verified (three readers compared; exact agreement)'if value and len(agreed)>=2 else'requires visual review';allcodes.append({'table':t['id'],'row':ri,'column':ci,'pdfPage':t['pdfPage'],'value':value,'readings':reads,'verification':ev['verification']})
   needs=value is None
   # A confident glyph disagreement is real even when the two Tesseract settings agree.
   if glyph and glyph['accepted']and not iscode and cell!=glyph['text']and not any(re.sub(r'\s+','',v)==glyph['text']for v in reads.values()):needs=True
   if needs:pending.append({'id':f"{t['id']}:{ri}:{ci}",'pdfPage':t['pdfPage'],'table':t['title'],'row':ri,'column':t['headerReadings'][ci],'readings':reads,'glyph':glyph['text']if glyph else None,'bounds':row['sourceBounds'],'columnStart':t['headerStarts'][ci],'columnEnd':t['headerStarts'][ci+1]if ci+1<len(t['headerStarts'])else min(.93,t['headerStarts'][ci]+.15)})
(F/'tables-reviewed.json').write_text(json.dumps(T,ensure_ascii=False,indent=2));(F/'glyph-improvements.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2));(F/'verification.json').write_text(json.dumps({'found':len(allcodes),'verified':sum(bool(c['value'])for c in allcodes),'records':allcodes},ensure_ascii=False,indent=2));(F/'pending-values.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2));print('Code occurrences',len(allcodes),'verified',sum(bool(c['value'])for c in allcodes),'glyph improvements',len(changes),'pending cells',len(pending))
# Compact crops include REF plus parameter, so a visual decision stays associated with the right item.
for start in range(0,len(pending),30):
 sheet=Image.new('RGB',(1800,10*155),'white');d=ImageDraw.Draw(sheet)
 for i,item in enumerate(pending[start:start+30]):
  im=Image.open(O/f"{item['pdfPage']:03}-600dpi.png");w,h=im.size;b=item['bounds'];crop=im.crop((max(0,int(item['columnStart']*w)-12),int(b[1]*h)-4,min(w,int(item['columnEnd']*w)-2),int(b[3]*h)+4));crop.thumbnail((560,95));x=i%3*600;y=i//3*155;sheet.paste(crop,(x,y+30));d.text((x,y),item['id']+' '+item['column'],fill='black');d.text((x,y+130),' / '.join(item['readings'].values())+' | glyph '+str(item['glyph']),fill='black')
 sheet.save(f'/tmp/xpmed-spine/values-{start//30:02}.png')
