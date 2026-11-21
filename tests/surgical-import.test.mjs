import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import {loadSystems}from '../src/catalog-data.mjs';import {renderSystem}from '../src/system-page.mjs';
const systems=(await loadSystems()).filter(s=>s.sourcePdf?.includes('/advanced-surgical-product-catalog/'));
const verification=JSON.parse(await fs.readFile('reports/conmed/advanced-surgical-product-catalog/verification.json'));
test('Surgical import covers exactly the supplied product pages and preserves every independently read code',()=>{
 assert.equal(systems.length,25);assert.equal(verification.records.length,352);
 assert.deepEqual([...new Set(systems.flatMap(s=>s.sourcePages))].sort((a,b)=>a-b),[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,41,42]);
 const actual=systems.flatMap(s=>s.specTables.flatMap(t=>t.rowSources.flatMap((source,i)=>source.codeEvidence.map(e=>({pdfPage:e.pdfPage,value:t.rows[i][2],candidate:e.printedCandidate,matched:e.verificationStatus})))));
 assert.equal(actual.length,352);
 const sort=rows=>rows.map(r=>JSON.stringify([r.pdfPage,r.candidate,r.value])).sort();assert.deepEqual(sort(actual),sort(verification.records.map(r=>({pdfPage:r.pdfPage,candidate:r.visualReading,value:r.value}))));
 for(const r of verification.records.filter(r=>r.value)){assert.equal(r.value,r.visualReading);if(r.verificationStatus==='verified (owner source review)'){assert.equal(r.resolution.basis,'Explicit owner verification against source PDF');}else{assert.ok(r.matchedReaders.length);assert.equal(r.verificationStatus,'verified (visual + OCR)');}}
 for(const s of systems){assert.deepEqual(s.specialty,['surgery']);assert.ok(!s.name.en.includes('OUS Only'));assert.equal(s.catalogType,'list');}
 assert.equal(systems.filter(s=>s.category==='access-insufflation').length,4);assert.equal(systems.filter(s=>s.category==='smoke-evacuation').length,8);assert.equal(systems.filter(s=>s.category==='electrosurgery').length,11);assert.equal(systems.filter(s=>s.category==='laparoscopic-instruments').length,2);
});
test('Packaging is bilingual data, never a selectable or copyable catalog number',()=>{
 const airseal=systems.find(s=>s.slug==='airseal-tube-sets-access-ports');const row=airseal.specTables[0].rows[0];assert.equal(row[1].en,'6/Box');assert.ok(!row[0].en.includes('6/Box'));assert.equal(row[2],'ASM-EVAC1');
 for(const lang of ['ru','en']){const html=renderSystem(airseal,lang);assert.ok(html.includes(lang==='ru'?'Упаковка':'Pack'));assert.ok(html.includes('lc-detail-cell'));assert.ok(!html.includes('[object Object]'));assert.ok(!html.includes('data-copy-code="6/Box"'));assert.ok(!html.includes('data-section="components"'));}
});
test('Surgical publication includes only systems with zero real flags',async()=>{
 const index=JSON.parse(await fs.readFile('dist/catalog-index.json'));for(const s of systems){assert.equal(s.status,s.review.flags.length?'draft':'published');assert.equal(index.some(item=>item.slug===s.slug&&item.brand===s.brand),s.status==='published');assert.ok(s.heroImage);assert.ok(s.gallery.length);for(const image of s.gallery){assert.equal(image.imageEnhancement.scale,2);assert.deepEqual(image.imageEnhancement.enhancedSize,image.imageEnhancement.originalSize.map(n=>n*2));assert.ok(image.captionFree);assert.ok(s.imageDimensions[image.src]);}}
});

test('Owner resolutions publish all Surgical systems with exact codes and bilingual lengths',()=>{
 assert.equal(systems.filter(s=>s.status==='published').length,25);assert.ok(systems.every(s=>s.review.flags.length===0));
 const rows=systems.flatMap(s=>s.specTables.flatMap(t=>t.rows));
 for(const code of ['iAS5-75LP','VV120','VV220','VV220NF','VVWM01','PP012SEO'])assert.ok(rows.some(r=>r[2]===code));
 const forceps=rows.find(r=>r[2]==='130187');assert.ok(forceps[0].ru.includes('15 см (6″)'));assert.ok(forceps[0].en.includes('6″ (15 cm)'));
 const adapter=rows.find(r=>r[2]==='PA2010');assert.ok(adapter[0].ru.includes('1,22 м (4′)'));assert.ok(adapter[0].en.includes('4′ (1.22 m)'));
 const tube=rows.find(r=>r[2]==='VTESU05');assert.ok(tube[0].ru.includes('0,6 м (2′)'));
});
