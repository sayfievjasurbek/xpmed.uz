"""Reconcile source prose after Codex visual review; keep exact raw readings."""
import json,re,difflib,collections
from spine_instrument_resolutions import resolve_row
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/spine-catalogue-instruments';rows=json.loads((F/'rows-evidence.json').read_text());manual=json.loads((R/'scripts/profiles/spine-instruments-visual-descriptions.json').read_text())['readings'];review=[]
def clean(text):
 text=text.replace('СТ Tap','CT Tap')
 text=text.replace('СТ Tap','CT Tap').replace('CТ Tap','CT Tap').replace('СT Tap','CT Tap').replace('Тaр','Tap').replace('ОCТ','OCT').replace('СТ Tap','CT Tap').replace('НОВВІТ','HOBBIT').replace('HOBВІТ','HOBBIT').replace('Тap','Tap').replace('Тар','Tap').replace('Тap','Tap').replace('DeviCE','Device').replace('Diill','Drill').replace('Temolate','Template').replace('TINAAwl','TINA Awl').replace('Opending','Opening');text=re.sub(r'[ФфΦφ$©®@](?=\d)','Ø',text);text=text.replace('×','×');return text.replace('СТ Tap','CT Tap').strip(' _|=')
sourceIssues=json.loads((R/'scripts/profiles/spine-instrument-source-issues.json').read_text())
for row in rows:
 original=row['description'];text=manual.get(row['id'])or row['descriptionReadings'].get('Vision')or original;text=clean(text)
 if row['id']=='344-06':
  # The source caption is physically clipped, not an OCR failure. Keep it verbatim and flag the suffix.
  text='Curette, rectangular, angled, left, bayc';row['realFlags']=[{'code':'source-caption-truncated','sourcePages':[344],'message':{'ru':'Окончание описания кюретки REF 111781400 обрезано в самом PDF: «bayc». Требуется подтверждение полного наименования.','en':'The source physically clips the curette description for REF 111781400 at “bayc”. Confirm the full designation.'},'readings':row['descriptionReadings']}]
 if row['id']=='344-07':row['realFlags']=[{'code':'source-caption-truncated','sourcePages':[344],'message':{'ru':'Окончание описания правой кюретки обрезано в PDF: «bay».','en':'The right curette caption is clipped in the source at “bay”.'},'readings':row['descriptionReadings']}]
 if row['id']in sourceIssues:row.setdefault('realFlags',[]).append(sourceIssues[row['id']])
 row['printedDescriptionReadings']=row['descriptionReadings'];row['description']=text;row['descriptionVerification']='Codex visual source crop'if row['id']in manual else'Independent source readers; typography normalized, raw readings retained';row['descriptionVisualReading']=manual.get(row['id']);row['codeVerification']='verified (three independent reads compared; at least two agree exactly)'
 visualCodes={'211-02':'111600700','237-06':'110475200','237-10':'110471700','287-05':'115351100','349-03':'113731400'}
 if row['id']in visualCodes:
  assert row['value']==visualCodes[row['id']]
  row['readings']['Codex visual 600-DPI crop']=visualCodes[row['id']];row['codeVerification']='verified (visual + OCR)'
 # Preserve all three machine readings even where one disagrees.
 resolve_row(row)
 row['descriptionVerification']=row['descriptionVerification'];review.extend({'id':row['id'],**f}for f in row.get('realFlags',[]))
 # The image marks and serial stamps are not part of the instrument caption.
 if re.search(r'[A-Za-z]{2}\d{6}|\d{6}[A-Za-z]',text):review.append({'id':row['id'],'code':'description-artifact-check','description':text})
(F/'rows-final.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(F/'prose-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2));print('Final source rows',len(rows),'manual captions',sum(bool(r['descriptionVisualReading'])for r in rows),'prose flags',len(review));print(review)
