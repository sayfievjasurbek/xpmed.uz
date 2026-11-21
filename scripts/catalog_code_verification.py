"""Auditable code verification; neither a pattern nor a manufacturer hit can replace visual+OCR agreement."""
import re
from collections import Counter

def code_tokens(text):
    # Strip separators, never replace characters or case inside a code.
    return re.findall(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',text or '')

def shape(code):
    return ''.join('9'if c.isdigit()else c for c in code)

def pattern_candidates(readings,confirmed_codes):
    counts=Counter(shape(code)for code in set(confirmed_codes))
    # At least two different confirmed codes support a shape in this same table.
    patterns={s for s,n in counts.items()if n>=2}
    confusions={'T':set('17Il'), 'O':{'0'}, 'I':{'1','l'}, '7':{'1'},'1':{'I','l'},'S':{'5'},'B':{'8'}}
    out=[]
    for reading in readings:
        for token in code_tokens(reading['text']):
            for pattern in patterns:
                first=pattern[0]
                if token and token[0]in confusions.get(first,set()):
                    candidate=first+token[1:]
                    if shape(candidate)==pattern:
                        out.append({'value':candidate,'raw':token,'reader':reading['reader'],'pattern':pattern,'basis':sorted(c for c in set(confirmed_codes)if shape(c)==pattern),'rule':'first-character substitution only; all remaining characters unchanged'})
    return out

def verify_visual(visual,readings,candidates):
    if not visual or visual.get('confidence')!='clear' or not visual.get('reading'):
        return {'value':None,'flagged':True,'verificationStatus':'unresolved','matchedReaders':[]}
    value=visual['reading'];matches=[r['reader']for r in readings if value in code_tokens(r['text'])]
    patterns=[c for c in candidates if c['value']==value]
    accepted=bool(matches or patterns)
    return {'value':value if accepted else None,'flagged':not accepted,'verificationStatus':'verified (visual + OCR)'if accepted else 'unresolved','matchedReaders':matches,'matchedPatternCandidates':patterns}
