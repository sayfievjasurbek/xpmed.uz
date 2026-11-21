"""Source footnotes and compatibility information stay with their ordering subgroups."""
def bi(ru,en):return {'ru':ru,'en':en}
def apply_notes(systems):
 for s in systems:
  for t in s['specTables']:
   n=t['sourcePages'][0]
   if n==48:t['description']=bi('Лезвия для сагиттальных пил, совместимые с соединением Stryker.','Stryker hub compatible sagittal saw blades.')
   if n==53:t['description']=bi('Внутриротовые лезвия. Не предназначены для использования с Micro 100.','Intra-oral blades. Not for use with Micro 100.')
   if n in [74,75]:
    t['note']=bi('Эти боры допускают несколько вариантов защитного тубуса для изменения рабочей длины бора.','These burs may be used with multiple bur guard options to change the working length of the bur.')
   if n==74 and t['id']==next(x['id']for x in s['specTables']if x['sourcePages']==[74]):t['compatibilityNotes']=[{'title':bi('Рабочая длина и защитные тубусы','Working lengths and bur guards'),'text':bi('На схеме: E9011-1 — 30 мм / E9011-2 — 13 мм; E9011-1 — 38 мм / E9011-2 — 21 мм; E9011-1 — 48 мм / E9011-2 — 31 мм.','Diagram: E9011-1 — 30 mm / E9011-2 — 13 mm; E9011-1 — 38 mm / E9011-2 — 21 mm; E9011-1 — 48 mm / E9011-2 — 31 mm.')}]
   if n==56 and 'Dermabrader'in t['title']['en']:t['note']=bi('Диаметр хвостовика бора: 2.34 мм (0.82").','Bur shank diameter: 2.34 mm (0.82").')
   for i,row in enumerate(t['rows']):
    code=row[1];note=None
    if n==55 and code=='5080-007':note=bi('Совместимый сменный рашпиль Stryker.','Stryker rasp replacement.')
    if n==60 and code in ['5059-235','5080-006']:note=bi('Для использования со стернальной пилой Stryker.','For use with Stryker Sternum Saw.')
    if note and not any(x['row']==i+1 and x['column']==2 and x['text']==note for x in t.get('cellNotes',[])):t.setdefault('cellNotes',[]).append({'row':i+1,'column':2,'text':note})
 return systems
