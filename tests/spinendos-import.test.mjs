import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems} from '../src/catalog-data.mjs';
import {orderedBrands} from '../src/site-settings.mjs';
import {brandName} from '../src/i18n/discovery.mjs';
import {renderSystem} from '../src/system-page.mjs';
import {excludeUnavailableSelections} from '../src/catalog-selection.js';
const systems=(await loadSystems()).filter(s=>s.brand==='spinendos');
const report=JSON.parse(await fs.readFile('reports/spinendos/endoscopic-spine-surgery-system/verification.json'));

test('SPINENDOS caption import covers all verified source entries without inventing codes',()=>{
 assert.equal(systems.length,6);assert.equal(report.records.length,283);
 const imported=systems.flatMap(s=>s.specTables.flatMap(t=>t.rowSources.flatMap((r,i)=>r.codeEvidence.map(e=>[e.id,t.rows[i][1]]))));
 assert.deepEqual(imported.sort(),report.records.map(r=>[r.id,Object.hasOwn(r,'catalogValue')?r.catalogValue:r.value]).sort());
 assert.ok(report.records.every(r=>r.value&&/^SP0\d{5}\.\d{3}[A-Z]?$/.test(r.value)));
 assert.equal(report.records.find(r=>r.pdfPage===18&&r.candidate==='SP082799.0355').value,'SP082799.035S');
 for(const s of systems){assert.ok(s.refCodes.every(code=>!/[☆★*]/.test(code)));assert.equal(s.catalogType,'list');assert.deepEqual(s.specialty,['spine']);assert.equal(s.category,'endoscopic-spine-surgery');assert.ok(!s.sourcePages.some(p=>[1,2,3,20].includes(p)));}
});

test('Owner-resolved Kerrison duplication preserves BDsys codes and disables unknown rotatable ordering rows',async()=>{
 const system=systems.find(s=>s.slug==='forceps-punches-and-scissors');assert.equal(system.status,'published');assert.deepEqual(system.review.flags,[]);
 for(const code of ['SP082700.042','SP082700.092']){
  const known=system.specTables.flatMap(t=>t.rows.map((row,i)=>({row,page:t.rowSources[i].pdfPage}))).filter(r=>r.row[1]===code);
  assert.equal(known.length,1);assert.equal(known[0].page,17);assert.match(known[0].row[0].en,/3\.5 mm.*300 mm/);
  const t=system.specTables.find(t=>t.rowSources.some(r=>r.pdfPage===18&&r.codeEvidence.some(e=>e.printedCode===code)));
  const i=t.rowSources.findIndex(r=>r.codeEvidence.some(e=>e.printedCode===code));
  assert.equal(t.rows[i][1],null);assert.match(t.rows[i][0].en,/2\.0 mm.*260 mm/);
  assert.equal(t.cellNotes.find(n=>n.row===i+1&&n.column===2).text.ru,'Каталожный номер уточняйте у менеджера');
  assert.ok(!system.components.some(c=>c.pdfPage===18&&c.refCodes.includes(code)));
  const id=`spinendos:${t.id}:${i}`;
  for(const lang of ['ru','en']){
   const html=renderSystem(system,lang);const row=html.split('<tr data-catalog-row').find(r=>r.includes(`data-catalog-select="${id}"`));
   assert.ok(row.includes('data-row-codes="[]"'));assert.match(row,/<input[^>]+data-catalog-select[^>]+ disabled>/);assert.ok(row.includes('>—</span>'));
  }
 }
 const index=JSON.parse(await fs.readFile('dist/catalog-index.json'));assert.equal(index.filter(s=>s.brand==='spinendos').length,6);
 const corrections=JSON.parse(await fs.readFile('reports/spinendos/endoscopic-spine-surgery-system/source-catalog-corrections.json'));assert.ok(corrections.some(c=>c.internalNote==='p.18 duplicate codes SP082700.042/.092 for the Ø2.0 mm rotatable irrigation Kerrison, ask SPINENDOS for the correct codes'));
});

test('Unavailable rows are removed from stored selection without discarding valid codes on this or other systems',()=>{
 const system=systems.find(s=>s.slug==='forceps-punches-and-scissors');
 const ids=system.specTables.flatMap(t=>t.rows.flatMap((row,i)=>row[1]===null?[`spinendos:${t.id}:${i}`]:[]));assert.equal(ids.length,2);
 const valid={id:'spinendos:bd:0',codes:['SP082700.042'],quantity:2};const other={id:'conmed:camera:0',codes:['IM8000'],quantity:3};
 assert.deepEqual(excludeUnavailableSelections([...ids.map(id=>({id,codes:['SP082700.042']})),valid,other],ids),[valid,other]);
});

test('SPINENDOS photos retain originals and exact 2x enhancement; dimensions are not copyable codes',async()=>{
 for(const s of systems){
  assert.equal(s.status,s.review.flags.length?'draft':'published');assert.equal(s.review.translationAuthor,'codex');assert.ok(s.review.translatedFields.length);
  for(const a of s.gallery){assert.ok(a.captionFree);assert.equal(a.imageEnhancement.scale,2);assert.deepEqual(a.imageEnhancement.enhancedSize,a.originalSize.map(n=>n*2));assert.ok(s.imageDimensions[a.src]);await fs.access('public'+a.src);}
 }
 const forceps=systems.find(s=>s.slug==='forceps-punches-and-scissors');
 for(const lang of ['ru','en']){const html=renderSystem(forceps,lang);assert.ok(!html.includes('data-copy-code="330"'));assert.ok(!html.includes('data-copy-code="2.5"'));assert.ok(!html.includes('data-section="components"'));}
});

test('SPINENDOS brand routes, bilingual labels and ordering are integrated',async()=>{
 assert.equal(brandName('spinendos'),'SPINENDOS');assert.deepEqual(orderedBrands(['spinendos','conmed','ge-healthcare','double','synimed','biotechni']),['double','conmed','synimed','biotechni','ge-healthcare','spinendos']);
 for(const prefix of ['','en/']){const html=await fs.readFile(`dist/${prefix}catalog/spinendos/index.html`,'utf8');assert.ok(html.includes('brand-spinendos.webp'));assert.ok(html.includes('https://spinendos.com/'));assert.ok(!html.includes('undefined'));}
});
