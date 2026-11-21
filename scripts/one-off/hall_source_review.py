"""Real source conflicts stay open; only canonical codes are indexed/requestable."""
import json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/conmed/hall-powered-instruments'
def bi(ru,en):return {'ru':ru,'en':en}
def apply(profile):
 from hall_source_notes import apply_notes
 systems=apply_notes(profile['systems']);by={s['slug']:s for s in systems};flags=[
 ('hall-pro-blades',15,[15,22],['5071-185 / 5071-195: p.15 Thickness 0.09 mm','5071-185 / 5071-195: p.22 Material Thickness 0.90 mm; Cut Thickness 0.90 mm'],'Для одинаковых кодов указана разная толщина: 0.09 мм и 0.90 мм. Уточните у производителя.','The same codes have conflicting thicknesses: 0.09 mm versus 0.90 mm. Manufacturer clarification required.'),
 ('hall-pin-and-wire-drivers',12,[12],['PRO6132 / PRO6232 / PRO6232-4: 2.0–3.2 mm (0.078–01.25")'],'В исходнике диапазон 2.0–3.2 мм сопровождается несовместимым дюймовым значением 0.078–01.25". Оставлено как напечатано.','The printed 2.0–3.2 mm range has an inconsistent 0.078–01.25" equivalent. Retained as printed.'),
 ('hall-sternum-saws',59,[59],['5059-006: 2.25" (5.72mm)','5059-011: 3.12" (7.92mm)'],'Напечатанные дюймовые размеры ограничителей не соответствуют значениям в мм. Уточните единицу у производителя.','The printed inch and mm guard dimensions are inconsistent. Manufacturer unit clarification required.'),
 ('hall-micro-burs',56,[56],['Bur Shank Diameter 2.34mm (0.82")'],'Значение 2.34 мм и напечатанный эквивалент 0.82" не соответствуют друг другу. Уточните у производителя.','The printed 2.34 mm and 0.82" equivalents are inconsistent. Manufacturer clarification required.'),
 ('hall-micro-sagittal-saw-blades',48,[47,48,52,60],['5080-023: p.48 length 0.60; p.60 length 60.00','5080-024: p.47 W 7.0 / L 18.5 / material 0.40; p.48 W 18.5 / L 7.00 / material .040','5080-025: p.47 W 13.0 / L 39.0; p.48 W 39.0 / L 13.0','5080-022: p.48 W 32.0 / L 19.0; p.52 W 19.50 / L 32.00'],'Повторные строки одинаковых кодов содержат несовместимые размеры. Значения сохранены по каждому месту печати; требуется уточнение производителя.','Repeated codes have conflicting dimensions. Each occurrence is retained as printed; manufacturer clarification required.')]
 for slug,page,pages,readings,ru,en in flags:
  s=by[slug];s['reviewFlags'].append({'code':'source-dimension-conflict','status':'open','pdfPage':page,'sourcePages':pages,'path':'specTables','readings':readings,'message':bi(ru,en)})
 # Canonical ownership: an existing published system wins, then a clean incoming family.
 owners={}
 for p in sorted((R/'content/products/conmed').glob('*.json')):
  s=json.loads(p.read_text())
  if s['status']=='published'and not s['slug'].startswith('hall-'):
   for code in s.get('refCodes',[]):owners.setdefault(code,s['slug'])
 existing=set(owners);cross=[];within=[]
 for s in sorted(systems,key=lambda s:(bool(s['reviewFlags']),systems.index(s))):
  for code in s['refCodes']:owners.setdefault(code,s['slug'])
 for s in systems:
  related=[]
  for t in s['specTables']:
   t['codeLinks']=[]
   for i,row in enumerate(t['rows']):
    code=row[1];owner=owners.get(code)
    if owner and owner!=s['slug']:
     t['codeLinks'].append({'row':i+1,'column':2,'url':'/catalog/conmed/'+owner+'/','code':code});related.append(owner);item={'code':code,'sourceSystem':s['slug'],'canonicalSystem':owner,'pdfPage':t['rowSources'][i]['pdfPage']};(cross if code in existing else within).append(item)
  s['refCodes']=[c for c in s['refCodes']if owners[c]==s['slug']];s['relatedSystemSlugs']=list(dict.fromkeys('conmed/'+x for x in related));s['sourceDocumentNotes']={'correctionsVisibility':'internal-only'}
 report={'existingPublishedSystems':cross,'withinCatalog':within};F.mkdir(parents=True,exist_ok=True);(F/'overlaps.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 decisionPath=F/'publication-decision.json'
 if decisionPath.exists():
  decision=json.loads(decisionPath.read_text())
  if decision.get('sourceSha256')==profile['sha256'] and decision.get('approvedBy')=='owner':
   for s in systems:
    if s['slug']in decision['approvedSystemSlugs']:s['reviewFlags']=[]
 return profile
