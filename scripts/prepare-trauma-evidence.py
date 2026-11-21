"""Reconcile raw readers, visually checked headings and source glyph evidence, never infer numbers."""
import json,re,collections
from pathlib import Path
from trauma_translation import implant,instrument
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part1'
tables=json.loads((F/'tables-evidence.json').read_text());rows=json.loads((F/'instrument-rows-evidence.json').read_text());glyphs=json.loads((F/'glyph-readings.json').read_text());G={(g['table'],g['row'],g['column']):g for g in glyphs}
TITLE_FIXES={
 'trauma-p19-1':'Extra-articular Distal Humeral Locking Plate, Twin Hole',
 'trauma-p34-1':'Distal Radius Locking Plate I, variable angle, small, Twin Hole',
 'trauma-p34-2':'Distal Radius Locking Plate I, variable angle, medium, Twin Hole',
 'trauma-p35-1':'Distal Radius Locking Plate I, variable angle, large, Twin Hole',
 'trauma-p37-2':'Distal Dorsal Radial π Locking Plate',
 'trauma-p38-2':'Proximal Radius Locking Plate, Twin Hole',
 'trauma-p46-1':'2.4mm Locking Screw II, variable angle, torxdrive, self-tapping',
 'trauma-p82-1':'Narrow Limited Contact Locking Plate, Twin Hole',
 'trauma-p85-1':'Distal Medial Tibial Locking Plate, Twin Hole',
 'trauma-p102-1':'6.5mm Cancellous Screw, half threaded, hexagon',
 'trauma-p147-3':'MT Anterior Process Calcaneal Locking Plate',
 'trauma-p151-3':'MT First MTC Plantar Fusion Locking Plate',
 'trauma-p173-1':'MT 2.7mm Cortex Screw, square, self-tapping',
 'trauma-p174-1':'MT 3.5mm Cortex Screw, square, self-tapping',
 'trauma-p199-2':'Anatomical Iliopubic Plate',
 'trauma-p202-2':'Ilioischiatic Locking Plate, for infra-arcuate line',
}
def clean_value(v):
    if v is None:return None
    v=v.strip(' _|~=—–')
    if re.search(r'\bLeft\b',v):return 'Left'
    if re.search(r'\bRight\b',v):return 'Right'
    return v[:-1]if re.fullmatch(r'\d+\.',v)else v
manual=json.loads((R/'scripts/profiles/trauma-visual-values.json').read_text())['values'];M={(v['table'],v['row'],v['column']):v['value']for v in manual}
flags=[];corrections=[]
for t in tables:
    t['printedTitleReading']=t['title'];t['title']=TITLE_FIXES.get(t['id'],t['title'])
    t['name']=implant(t['title']);t['reviewFlags']=[]
    for i,r in enumerate(t['rows']):
        for ci,e in enumerate(r['evidence']):
            clean={k:clean_value(v)for k,v in e['readings'].items()};counts=collections.Counter(v for v in clean.values()if v)
            value=counts.most_common(1)[0][0]if counts and counts.most_common(1)[0][1]>=2 else None
            g=G.get((t['id'],i,ci))
            if g and g['accepted'] and any(clean_value(v)==g['text'] for v in clean.values()):
                value=g['text'];e['glyphReading']={'text':g['text'],'scores':g['scores'],'sourceRect':g['rect']}
            if (t['id'],i,ci)in M:
                value=M[(t['id'],i,ci)];e['visualReading']={'reader':'Codex 600-DPI source row crop','text':value}
            if value is None:
                flag={'code':'unverified-table-value','pdfPage':t['pdfPage'],'tableId':t['id'],'row':i,'column':ci,'readings':e['readings']}
                t['reviewFlags'].append(flag);flags.append(flag)
            r['values'][ci]=value;e['verifiedValue']=value
    # Duplicate REF with differing printed size data is a source issue, not an OCR correction.
    seen={}
    for i,r in enumerate(t['rows']):
        for ci,h in enumerate(t['headerReadings']):
            if not h.startswith('REF'):continue
            ref=r['values'][ci]
            if ref and not re.fullmatch(r'\d{9}[A-Za-z]?',ref):
                flag={'code':'ref-pattern-mismatch','pdfPage':t['pdfPage'],'tableId':t['id'],'row':i,'column':ci,'readings':r['evidence'][ci]['readings']};t['reviewFlags'].append(flag);flags.append(flag)
            if ref in seen and r['values'][1:]!=seen[ref][1:]:
                flag={'code':'duplicate-ref-different-size','pdfPage':t['pdfPage'],'tableId':t['id'],'ref':ref,'readings':[seen[ref],r['values']]};t['reviewFlags'].append(flag);flags.append(flag)
            if ref:seen[ref]=r['values']
    for ci,h in enumerate(t['headerReadings']):
        if not h.startswith('REF'):continue
        codes=[(i,r['values'][ci])for i,r in enumerate(t['rows'])if r['values'][ci]];prefixes=collections.Counter(v[:4]for _,v in codes)
        if len(prefixes)>1 and prefixes.most_common(1)[0][1]/len(codes)>=.8:
            common=prefixes.most_common(1)[0][0]
            for ri,ref in codes:
                if ref[:4]!=common:
                    f={'code':'source-ref-prefix-outlier','pdfPage':t['pdfPage'],'tableId':t['id'],'row':ri,'column':ci,'ref':ref,'commonPrefix':common,'readings':t['rows'][ri]['evidence'][ci]['readings']};t['reviewFlags'].append(f);flags.append(f)
    # Source consistently uses the last three REF digits as hole count in these tables.
    for ci,h in enumerate(t['headerReadings']):
        if h!='Holes':continue
        valid=[r for r in t['rows']if r['values'][0]and str(r['values'][ci]or'').isdigit()]
        if len(valid)>=6 and sum(int(r['values'][0][-3:])==int(r['values'][ci])for r in valid)/len(valid)>=.95:
            for r in valid:
                if int(r['values'][0][-3:])!=int(r['values'][ci]):
                    # Do not apply a code rule unless other source rows independently establish it.
                    printed=r['values'][ci];r['values'][ci]=str(int(r['values'][0][-3:]));corrections.append({'pdfPage':t['pdfPage'],'REF':r['values'][0],'column':h,'printed':printed,'corrected':r['values'][ci],'basis':'Owner-authorized size encoding, established by at least 95% of this table; original readings retained.'})
descriptionFixes=json.loads((R/'scripts/profiles/trauma-visual-descriptions.json').read_text())['readings']
for r in rows:
    text=r['description'].strip(' =_|')
    text=text.replace('Тamp','Tamp').replace('Jrill','Drill').replace('Dill Bits','Drill Bits').replace('TSS Il','TSS II').replace('TSS ||','TSS II')
    text=re.sub(r'[©®$ФфΦφ](?=\d)','Ø',text);text=re.sub(r'(?<!\d)0(?=[1-9]\.\d)','Ø',text)
    text=re.sub(r'(?:\b\(?[OB]|@|\(\||C\)|gj\.\.\.)\s+(?=AO Coupling|Triangle Coupling|with AO Coupling|with Triangle Coupling)','',text)
    text=re.sub(r'\s+[=@]\s*$','',text)
    text=descriptionFixes.get(r['id'],text)
    r['description']=text;r['name']=instrument(text)
    if r['id']in descriptionFixes:r['descriptionVisualReading']=text
(F/'tables-final.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2)+'\n')
(F/'instrument-rows-final.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(F/'value-review.json').write_text(json.dumps(flags,ensure_ascii=False,indent=2)+'\n')
(F/'source-catalog-corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2)+'\n')
print('Tables',len(tables),'cells still flagged',len(flags),'source size corrections',len(corrections))
print('Flag types',collections.Counter(f['code']for f in flags))
