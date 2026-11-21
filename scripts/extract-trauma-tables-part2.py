"""Position-preserving three-reader extraction for the explicitly scoped Trauma pages."""
import json,re,collections
import pymupdf as fitz
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part2';O=R/'public/catalogs/double-medical/trauma-catalogue/ocr'
scope=json.loads((F/'scope.json').read_text());tables=[];instruments=[];headers=[];issues=[]
def cy(w):return sum(w['bounds'][1::2])/2
def norm(s):return re.sub(r'\s+','',s).replace('×','x').replace('mm','').strip('|_=,;').casefold()
def choose(reads):
    counts=collections.Counter(norm(v) for v in reads.values() if norm(v))
    if not counts:return None
    best,n=counts.most_common(1)[0]
    return next(v for v in reads.values()if norm(v)==best) if n>=2 else None
def code(s):
    s=s.strip('|_,;:')
    return s if re.fullmatch(r'[0-9OIl][0-9OIl]{7,10}[A-Za-z]?',s) else None
def join(words):
    lines=[]
    for w in sorted(words,key=lambda w:w['bounds'][1]):
        group=next((g for g in lines if abs(g[0]['bounds'][1]-w['bounds'][1])<.006),None)
        if group is None:lines.append([w])
        else:group.append(w)
    return ' '.join(w['text']for line in lines for w in sorted(line,key=lambda w:w['bounds'][0]))
D=fitz.open(R/'catalogs-source/double-medical/trauma-catalogue.pdf')
for n in scope['authorizedPhysicalPages']:
    if not(O/f'{n:03}.json').exists()or not(F/'vision'/f'{n:03}.json').exists():continue
    j=json.loads((O/f'{n:03}.json').read_text());v=json.loads((F/'vision'/f'{n:03}.json').read_text());readers={'PSM3':j['passes']['3']['words'],'PSM11':j['passes']['11']['words'],'Vision':list(v)}
    for w in v:
        for m in re.finditer(r'(?<![A-Za-z0-9])[0-9]{9}(?![0-9])',w['text']):
            if m.group()!=w['text']:
                b=w['bounds'];span=b[2]-b[0];readers['Vision'].append({**w,'text':m.group(),'bounds':[b[0]+span*m.start()/len(w['text']),b[1],b[0]+span*m.end()/len(w['text']),b[3]],'sourceLine':w['text']})
    section=next(s for s in scope['scope']if s['physicalPages'][0]<=n<=s['physicalPages'][1]);printed=f"{section['section']}/{n-section['indexPage']+1}";isInstrument=n>=({5:238,6:298,7:312,8:380}[section['section']])
    refs=[]
    for reader,words in readers.items():
        for w in words:
            if re.match(r'^REF(?:$|[.(])',w['text'],re.I) and .08<w['bounds'][0]<.23 and .12<cy(w)<.93:
                if not any(abs(cy(h)-cy(w))<.008 for h in refs):refs.append(w)
    refs.sort(key=cy)
    instrumentHeadingY=next((cy(w)for w in v if w['text'].strip()=='Instruments' and .09<cy(w)<.22),.13)
    codes=[];setCodes=[]
    for reader,words in readers.items():
        for w in words:
            c=code(w['text']);b=w['bounds']
            if not c or not(.08<b[0]<( .6 if isInstrument and abs(cy(w)-instrumentHeadingY)<.012 else .24 if isInstrument else .88) and .095<cy(w)<.935):continue
            dest=setCodes if isInstrument and abs(cy(w)-instrumentHeadingY)<.012 else codes
            group=next((g for g in dest if abs(g['cy']-cy(w))<.005),None)
            if group is None:group={'cy':cy(w),'bounds':b,'readings':{},'codeWords':[]};dest.append(group)
            group['codeWords'].append({'reader':reader,'text':c,'bounds':b})
            if b[0]<.24 or dest is setCodes:group['readings'][reader]=c
    codes.sort(key=lambda x:x['cy'])
    hw=[w for w in v if .03<cy(w)<.09 and re.search(r'Instrument|Set|Cartilage',w['text'],re.I)]
    right=bool(hw and hw[0]['bounds'][0]>.45)
    title=join([w for w in v if .03<cy(w)<.09 and ((w['bounds'][0]>.45)if right else(w['bounds'][0]<.53)) and not re.search(r'XPmed|X.Pmed|DOUBLE|MEDICAL|Fah|Dedicat',w['text'],re.I)]) if hw else ''
    if isInstrument:
        pg=D[n-1]
        captionRects=[a['rect']for a in pg.get_drawings()if a['type']=='f' and 2<a['rect'].height<13 and .22<a['rect'].x0/pg.rect.width<.72]
        def printed_caption(w):
            b=w['bounds'];cx=(b[0]+b[2])/2*pg.rect.width;yy=(b[1]+b[3])/2*pg.rect.height
            return any((q+(-1,-1,1,1)).contains(fitz.Point(cx,yy))or(q+(-1,-1,1,1)).intersects(fitz.Rect(b[0]*pg.rect.width,b[1]*pg.rect.height,b[2]*pg.rect.width,b[3]*pg.rect.height))for q in captionRects)
        rules=sorted({a['rect'].y0/pg.rect.height for a in pg.get_drawings()if .25<a['rect'].width/pg.rect.width<.5 and a['rect'].height<.8 and .08<a['rect'].x0/pg.rect.width<.2 and .14<a['rect'].y0/pg.rect.height<.93})
        headers.append({'pdfPage':n,'printedPage':printed,'section':section['section'],'title':title,'setCodes':[{**c,'value':choose(c['readings'])} for c in setCodes]})
        for i,c in enumerate(codes):
            lower=max(.14,c['bounds'][1]-.006);upper=min([q for q in rules if q>c['cy']+.005]+([codes[i+1]['bounds'][1]-.003]if i+1<len(codes)else[.93]))
            readings={reader:join([w for w in words if .22<w['bounds'][0]<.72 and .005<w['bounds'][3]-w['bounds'][1]<.028 and lower<cy(w)<upper and printed_caption(w)]) for reader,words in readers.items()}
            instruments.append({'id':f'{n:03}-{i+1:02}','pdfPage':n,'printedPage':printed,'section':section['section'],'value':choose(c['readings']),'candidate':next(iter(c['readings'].values()),None),'readings':c['readings'],'description':choose(readings)or readings['Vision']or readings['PSM3'],'descriptionReadings':readings,'descriptionAgreement':choose(readings)is not None,'codeBounds':c['bounds'],'sourceBounds':[.08,lower,.56,upper],'cy':c['cy']})
        continue
    if not refs:
        issues.append({'pdfPage':n,'issue':'No REF header detected','codes':len(codes)});continue
    pg=D[n-1]
    textRects=[a['rect']for a in pg.get_drawings()if a['type']=='f'and 1<a['rect'].height<14 and len(a['items'])>1]
    def outlined(w):
        b=w['bounds'];x=(b[0]+min(b[2],.55))/2*pg.rect.width;y=cy(w)*pg.rect.height
        return any((q+(-2,-2,2,2)).contains(fitz.Point(x,y))for q in textRects)
    previous=.13
    for ti,h in enumerate(refs):
        hy=cy(h);limit=cy(refs[ti+1])if ti+1<len(refs)else .93;rows=[c for c in codes if hy<c['cy']<limit]
        if not rows:issues.append({'pdfPage':n,'issue':'REF table without rows','bounds':h['bounds']});continue
        # Independent Vision recognizes whole column labels; Tesseract backs up missing labels.
        heads=[]
        pattern=r'^(?:REF|Holes|Length|Direction|Diameter|Height|Angle|Width|Thickness|Size|Thread|Type|Model|Spec|Color|Colour|Distance)'
        for reader in ['Vision','PSM3','PSM11']:
            for w in readers[reader]:
                if abs(cy(w)-hy)<.009 and .08<w['bounds'][0]<.9 and re.match(pattern,w['text'],re.I):
                    if not any(abs(x['bounds'][0]-w['bounds'][0])<.035 for x in heads):heads.append(w)
        heads=[{**head,'text':re.sub(r'^ref','REF',head['text'],flags=re.I)}for head in heads]
        heads.sort(key=lambda w:w['bounds'][0])
        if n==279 and ti==0:
            heads[1]['text']='Head Holes'
        # Multi-line REF labels distinguish proximal nail diameters.
        for head in heads:
            if head['text'].startswith('REF'):
                notes=[w['text']for w in v if hy+.006<cy(w)<min(c['cy']for c in rows)-.004 and abs(w['bounds'][0]-head['bounds'][0])<.025 and re.search(r'Proximal|dia\.',w['text'],re.I)]
                if notes:head['text']='REF — '+' '.join(notes)
        starts=[x['bounds'][0]for x in heads]
        if not heads or not heads[0]['text'].startswith('REF'):heads.insert(0,h);starts.insert(0,h['bounds'][0])
        # Midpoints between starts incorrectly swallow right-aligned numbers; printed column starts form the boundaries.
        edges=[.08]+[x-.008 for x in starts[1:]]+[max(.55,starts[-1]+.16)]
        refIndices=[i for i,head in enumerate(heads)if head['text'].startswith('REF')]
        rows=[c for c in rows if any(any(edges[i]<=w['bounds'][0]<edges[i+1]for i in refIndices)for w in c['codeWords'])]
        if not rows:continue
        before=sorted([w for w in v if previous<cy(w)<hy-.01 and .08<w['bounds'][0]<.55 and outlined(w)],key=lambda w:(round(cy(w)/.01),w['bounds'][0]));prose=[w for w in before if re.search('[A-Za-z]{2}',w['text'])]
        firstSpec=next((i for i,w in enumerate(prose)if ':'in w['text']),len(prose));name=join(prose[:firstSpec])
        firstSpecY=cy(prose[firstSpec])if firstSpec<len(prose)else hy-.01
        if not name:
            name=join([w for w in readers['PSM3'] if previous<cy(w)<firstSpecY-.005 and .08<w['bounds'][0]<.55 and re.search('[A-Za-z]',w['text'])])
        preamble=[w['text']for w in prose[firstSpec:]]
        out=[]
        for ri,c in enumerate(rows):
            firstReads={w['reader']:w['text']for w in c['codeWords']if edges[0]<=w['bounds'][0]<edges[1]}
            values=[choose(firstReads)];evidence=[{'readings':firstReads,'value':values[0],'bounds':c['bounds'],'sourceBlank':not firstReads}]
            for ci in range(1,len(heads)):
                reads={}
                for reader,words in readers.items():
                    chosen=[w for w in words if edges[ci]<=w['bounds'][0]<edges[ci+1] and abs(cy(w)-c['cy'])<.0055]
                    reads[reader]=join(chosen).strip(' _|')
                val=choose(reads);values.append(val);evidence.append({'readings':reads,'value':val})
            out.append({'values':values,'evidence':evidence,'cy':c['cy'],'sourceBounds':[.08,c['bounds'][1]-.003,edges[-1],c['bounds'][3]+.003]})
        tables.append({'id':f'trauma-p{n}-{ti+1}','pdfPage':n,'printedPage':printed,'section':section['section'],'title':name,'titleY':min((w['bounds'][1]for w in prose[:firstSpec]),default=previous+.02),'preamble':preamble,'headerReadings':[x['text']for x in heads],'headerStarts':starts,'headerY':hy,'rows':out})
        previous=max(c['bounds'][3]for c in rows)+.004
F.mkdir(exist_ok=True,parents=True)
for name,data in [('tables-evidence.json',tables),('instrument-rows-evidence.json',instruments),('page-headers.json',headers),('table-detection-issues.json',issues)]: (F/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(F/'headings.txt').write_text('\n'.join(f"{t['pdfPage']:03} | {t['title']} | {'; '.join(t['preamble'])} | {t['headerReadings']} | {len(t['rows'])}"for t in tables))
print('Tables',len(tables),'implant rows',sum(len(t['rows'])for t in tables),'instruments',len(instruments),'set headers',len(headers),'unresolved codes',sum(r['values'][0]is None for t in tables for r in t['rows'])+sum(r['value']is None for r in instruments),'issues',issues)
