import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {loadSystems,prepareSystem,validateSystem} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';
import ru from '../src/i18n/catalog-ru.mjs';
import en from '../src/i18n/catalog-en.mjs';
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const profile=await read('scripts/profiles/double-medical-spine-instruments.json');
const systems=(await loadSystems()).filter(s=>s.importPartition==='spine-instruments');
const report=await read('reports/double-medical/spine-catalogue-instruments.json');
test('Part 2 has its own bounded 600-DPI evidence and never imports the back cover',async()=>{
 const part1=await read('public/catalogs/double-medical/spine-catalogue/ocr/manifest.json');
 const part2=await read('public/catalogs/double-medical/spine-catalogue/ocr/manifest-instruments.json');
 assert.deepEqual(part1.pages,Array.from({length:207},(_,i)=>i+3));assert.deepEqual(part2.pages,Array.from({length:202},(_,i)=>i+210));assert.equal(part2.dpi,600);assert.equal(profile.partition,'instruments');assert.ok(profile.nonProductPages.includes(412));
 assert.equal(systems.length,49);assert.equal(new Set(systems.map(s=>s.setCode)).size,49);for(const s of systems){assert.ok(s.sourcePages.every(p=>p>=210&&p<=411));assert.deepEqual(validateSystem(s),[]);assert.equal(s.category,'spine-instrument-sets');assert.equal(s.catalogType,'list');assert.ok(s.setCodeEvidence.length);assert.ok(ru.subcategories[s.subcategory]);assert.ok(en.subcategories[s.subcategory]);}
});
test('All 1420 instrument REF occurrences retain independent readings, visual tie-breaks and translated numeric values',async()=>{
 const rows=systems.flatMap(s=>s.specTables.flatMap(t=>t.rows.map((row,i)=>({row,source:t.rowSources[i]}))));assert.equal(rows.length,1420);assert.equal(new Set(rows.map(r=>r.row[1])).size,1206);let visuallyRead=0;
 for(const{row,source}of rows){assert.match(row[1],/^\d{9}$/);const readings=Object.fromEntries(source.codeEvidence[0].readings.map(r=>[r.reader,r.text]));assert.ok(Object.values(readings).filter(r=>r===row[1]).length>=2);if(readings['Codex visual 600-DPI crop']){assert.equal(readings['Codex visual 600-DPI crop'],row[1]);visuallyRead++;}assert.deepEqual([...row[0].ru.matchAll(/\d+(?:[.,]\d+)?/g)].map(x=>x[0]).sort(),[...row[0].en.matchAll(/\d+(?:[.,]\d+)?/g)].map(x=>x[0]).sort());assert.ok(row[0].ru);}
 assert.equal(visuallyRead,5);assert.equal(report.codesVerified,1420);assert.equal(report.setCodesVerified,49);
});
test('Owner-confirmed caption corrections publish all 49 sets without mismatched photos or REF changes',async()=>{
 assert.equal(systems.filter(s=>s.status==='draft').length,0);assert.equal(report.setsPublished,49);assert.equal(report.setsDraft,0);assert.deepEqual(report.uncertainties,[]);
 const tlif=systems.find(s=>s.setCode==='111840000'),cervical=systems.find(s=>s.setCode==='113294600');
 for(const [ref,direction,ruDirection]of [['111781400','left','левая'],['111781500','right','правая']]){const table=tlif.specTables.find(t=>t.rows.some(r=>r[1]===ref));const i=table.rows.findIndex(r=>r[1]===ref);assert.deepEqual(table.rows[i][0],{en:`Curette, rectangular, angled, ${direction}, bayoneted`,ru:`Кюретка, прямоугольная, угловая, ${ruDirection}, байонетная`});assert.deepEqual(table.rowImages[i].imageCaption,table.rows[i][0]);}
 const removed=[5,6,7].map(n=>`/images/products/double-medical/spine-instruments/art-214-0${n}.webp`);
 for(const t of cervical.specTables)for(const [i,row]of t.rows.entries())if(['110477900','113290100','113290300'].includes(row[1]))assert.equal(t.rowImages[i],null);
 assert.ok(cervical.gallery.every(g=>!removed.includes(g.src)));assert.ok(removed.every(src=>!cervical.imageDimensions[src]));
 const sleeve=cervical.specTables.flatMap(t=>t.rows).find(r=>r[1]==='110042500');assert.equal(sleeve[0].en,'Holding Sleeve for Torque Indicating…');assert.ok(sleeve[0].ru.endsWith('…'));assert.ok(!sleeve[0].en.includes('Handle'));
 for(const s of [tlif,cervical]){const before=await read(`reports/double-medical/spine-catalogue-instruments/owner-resolution-backups/${s.slug}.json`);assert.deepEqual(s.refCodes,before.refCodes);assert.deepEqual(s.specTables.flatMap(t=>t.rows.map(r=>r[1])),before.specTables.flatMap(t=>t.rows.map(r=>r[1])));assert.ok(s.review.resolvedFlags.length);}
 assert.equal(report.sourceCatalogCorrections.length,6);
 for(const s of systems){assert.equal(s.status,'published');assert.deepEqual(s.review.flags,[]);for(const lang of ['ru','en']){const html=await readFile(`dist/${lang==='en'?'en/':''}catalog/double-medical/${s.slug}/index.html`,'utf8');if(s===cervical)for(const src of removed)assert.ok(!html.includes(src));assert.ok(!html.includes('Source catalog corrections'));}}
 const index=await read('dist/catalog-index.json');for(const s of [tlif,cervical])assert.ok(index.some(i=>i.slug===s.slug));
});
test('Reciprocal instrument links preserve every implant field except the related links array',async()=>{
 const all=await loadSystems();
 for(const slug of report.reciprocalImplantLinks){const current=all.find(s=>s.brand==='double-medical'&&s.slug===slug),before=await read(`reports/double-medical/spine-catalogue-instruments/implant-link-backups/${slug}.json`);const raw=await read(`content/products/double-medical/${slug}.json`);for(const key of new Set([...Object.keys(before),...Object.keys(raw)]))if(key!=='relatedSystemSlugs')assert.deepEqual(raw[key],before[key],`${slug}: ${key}`);for(const s of systems.filter(s=>s.relatedSystemSlugs.includes(slug)))assert.ok(current.relatedSystemSlugs.includes(s.slug));const prepared=await prepareSystem(current,all);for(const link of prepared.instrumentSetLinks)assert.ok(systems.some(s=>s.status==='published'&&link.url.includes('/'+s.slug+'/'))||link.url.includes('arthroplasty'));}
});
test('Set pages have request-by-REF rows, native-size caption-free art and a genuinely image-free FC fallback',async()=>{
 const repair=await read('reports/double-medical/spine-catalogue-instruments/cpu-repaired-images.json');assert.equal(Object.keys(repair).length,158);assert.ok(Object.values(repair).every(r=>r.meanAbsoluteError<40&&r.sourceOriginalUnchanged));
 const assets=await read('public/images/products/double-medical/spine-instruments/artwork-assets.json');assert.ok(Object.keys(assets).length>1100);
 for(const a of Object.values(assets)){assert.equal(a.captionFree,true);assert.equal(a.imageEnhancement.scale,2);assert.deepEqual(a.imageEnhancement.enhancedSize,a.originalSize.map(v=>v*2));await access('public'+a.src);await access(`public/images/products/double-medical/spine-instruments/_originals/${a.name}.png`);}
 const fc=systems.find(s=>s.setCode==='113791700');assert.equal(fc.heroImage,'');assert.ok(fc.specTables.length);
 const tina=systems.find(s=>s.setCode==='112516500');for(const lang of ['ru','en']){const html=renderSystem(tina,lang);assert.ok(html.includes(tina.setCode));assert.match(html,/data-catalog-select=/);assert.match(html,/sp-breadcrumbs/);assert.ok(!html.includes('undefined'));}
 assert.equal(report.randomSample.length,20);for(const r of report.randomSample)assert.ok(systems.some(s=>s.slug===r.slug&&s.specTables.some(t=>t.sourcePage===r.pdfPage&&t.rows.some(row=>row[1]===r.REF))));
});
