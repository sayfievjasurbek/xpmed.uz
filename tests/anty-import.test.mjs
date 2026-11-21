import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import {loadSystems,prepareSystem,validateSystem}from '../src/catalog-data.mjs';import {renderSystem}from '../src/system-page.mjs';import {validateTableSpans,renderTableRows}from '../src/system-tables.mjs';
const all=await loadSystems(),s=all.find(x=>x.slug==='anty-f-series'),t=s.specTables[0];
test('Anty retains every source size, exact dimensions and all three symbols without size 11',()=>{
 assert.equal(s.status,'published');assert.equal(s.catalogType,'system');assert.equal(s.subcategory,'hip');assert.deepEqual(s.specialty,['orthopedics']);assert.equal(s.review.flags.length,0);assert.equal(t.rows.length,11);assert.deepEqual(t.rows.map(r=>r[0]),['1# / 14mm','2# / 15mm','3# / 16mm','4# / 17mm','5# / 18mm','6# / 19mm','7# / 20mm','8# / 21mm','9# / 22mm','10# / 23mm','12# / 25mm']);
 assert.deepEqual(t.rows[0].slice(1),['●','●','●','○','42','22','13','14','15','16','14','9']);assert.deepEqual(t.rows[8].slice(1),['×','●','●','○','46','26','×','22','21','21','22','17']);assert.deepEqual(t.rows[10].slice(1),['×','×','×','○','46','26','×','×','×','25','25','20']);assert.deepEqual(validateSystem(s),[]);
});
test('Anty renders both real header levels with merged cells and localized units',()=>{
 assert.equal(t.headerRows.length,2);assert.equal(t.headerRows[0][0].rowspan,2);assert.equal(t.headerRows[0][1].colspan,4);assert.equal(t.headerRows[0][7].colspan,4);assert.deepEqual(validateTableSpans({...t,rows:t.headerRows}),[]);
 const head=renderTableRows({...t,rows:t.headerRows},{cell:v=>typeof v==='object'?v.en:String(v),header:true});assert.ok(head.includes('scope="colgroup" colspan="4"'));assert.ok(head.includes('scope="col" rowspan="2"'));assert.ok(!head.includes('<td'));
 for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.ok(html.includes(lang==='ru'?'Проксимальный наружный диаметр':'Proximal outer diameter'));assert.ok(html.includes(lang==='ru'?'Единицы измерения: мм':'Units: mm'));assert.ok(html.includes('sp-cross'));assert.ok(html.includes('aria-label="○"'));assert.ok(!html.includes('[object Object]'));assert.ok(!html.includes('11#'));}
});
test('Anty maps six source callouts to the stem and keeps the technical drawing on white',async()=>{
 assert.equal(s.hotspots.length,6);assert.deepEqual(s.hotspots.map(h=>h.featureId),s.features.map(f=>f.id));
 for(const h of s.hotspots){assert.equal(h.pdfPage,2);assert.ok(h.x>0&&h.x<100&&h.y>0&&h.y<100);await fs.access('public'+h.image);}
 assert.equal(s.gallery[0].imageType,'scene');assert.equal(s.gallery[0].pdfPage,2);assert.ok(s.gallery[0].sourceMethod.includes('600 DPI'));assert.ok(s.heroImage.endsWith('/hero-stem.webp'));
 const report=JSON.parse(await fs.readFile('reports/double-medical/anty-f-series/sample-20.json'));assert.equal(report.samples.length,20);assert.equal(new Set(report.samples.map(x=>x.row+':'+x.columnIndex)).size,20);for(const x of report.samples){assert.equal(x.value,t.rows[x.row-1][x.columnIndex-1]);assert.equal(x.size,t.rows[x.row-1][0]);}
});
test('Anty and the existing PBG hip system link to each other',async()=>{
 const a=await prepareSystem(structuredClone(s),all),b=await prepareSystem(structuredClone(all.find(x=>x.slug==='pbg-proximal-bone-growth-cementless-stem')),all);assert.ok(a.relatedSystems.some(x=>x.slug===b.slug));assert.ok(b.relatedSystems.some(x=>x.slug===a.slug));
 const html=await fs.readFile('dist/catalog/double-medical/anty-f-series/index.html','utf8');assert.ok(html.includes('/catalog/double-medical/'+b.slug+'/'));assert.ok(html.includes('Тазобедренный сустав')||html.includes('Anty F-series'));await fs.access('dist/en/catalog/double-medical/anty-f-series/index.html');
});
