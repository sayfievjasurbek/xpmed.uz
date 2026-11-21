import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems,prepareSystem} from '../src/catalog-data.mjs';
import {escape as escapeHtml} from '../src/html.mjs';
import {renderSystem} from '../src/system-page.mjs';
import {matchesDimensionFilters} from '../src/catalog-engine.js';
const read=async p=>JSON.parse(await fs.readFile(p));
const all=await loadSystems(),systems=all.filter(s=>s.sourcePdf?.includes('/hall-powered-instruments/'));
const report=await read('reports/conmed/hall-powered-instruments/report.json');
const verification=await read('reports/conmed/hall-powered-instruments/verification.json');
const rows=systems.flatMap(s=>s.specTables.flatMap(t=>t.rows.map((row,i)=>({system:s,table:t,row,source:t.rowSources[i]}))));
test('HALL imports the 30 contents families, preserves source codes and never orders OCR aliases',()=>{
 assert.equal(systems.length,30);assert.equal(rows.length,report.catalogNumbersFound);
 for(const {row,source}of rows){const audit=source.codeEvidence[0],record=verification.records.find(r=>r.id===audit.id);assert.ok(record&&!record.excludedReason);assert.equal(row[1],record.value);assert.equal(audit.value,record.value);assert.ok(record.readings.length>=3);assert.ok(source.bounds.length===4);}
 for(const r of verification.records.filter(r=>!r.excludedReason))assert.ok(rows.some(x=>x.source.pdfPage===r.pdfPage&&x.row[1]===r.value),r.id);
 for(const bad of ['PROS125','PROD6232','PR06232','55059-007','5059-07','E9011'])assert.ok(!rows.some(x=>x.row[1]===bad));
 assert.ok(rows.some(x=>x.row[1]==='8703'));
 for(const suffix of [1,2,3,7,8,9])assert.ok(rows.some(x=>x.row[1]===`E9011-${suffix}`));
});
test('Owner-approved HALL publication clears flags and preserves printed dimensions',async()=>{
 assert.equal(systems.filter(s=>s.status==='published').length,30);assert.equal(systems.filter(s=>s.status==='draft').length,0);
 assert.deepEqual((await read('reports/conmed/hall-powered-instruments.json')).uncertainties,[]);
 const index=await read('dist/catalog-index.json');
 for(const s of systems){const open=s.review.flags.filter(f=>!['resolved','dismissed'].includes(f.status));assert.equal(s.status==='published',!open.length);assert.equal(index.some(x=>x.brand==='conmed'&&x.slug===s.slug),s.status==='published');}
 const find=(code,page)=>rows.find(x=>x.row[1]===code&&x.source.pdfPage===page);
 assert.equal(find('5071-185',15).row[5].en,'0.09');assert.equal(find('5071-185',22).row[4].en,'0.90');
 assert.equal(find('5080-023',48).row[4].en,'0.60');assert.equal(find('5080-023',60).row[3].en,'60.00');
});
test('Every HALL saw-row drawing remains white source line art and opens an enlarged view',()=>{
 for(const s of systems){for(const t of s.specTables){assert.ok(t.rows.every(r=>r.length===t.columns.length));if(t.rowImages?.some(Boolean)){assert.equal(t.rowImages.length,t.rows.length);for(const image of t.rowImages.filter(Boolean)){assert.equal(image.drawing,true);assert.match(image.backgroundRemoval,/not applied/);assert.ok(image.width>0&&image.height>0);}}}
 if(s.specTables.some(t=>t.rowImages?.some(Boolean)))for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.match(html,/data-drawing-dialog/);assert.match(html,/data-drawing-open/);assert.match(html,new RegExp(lang==='ru'?'Единицы измерения: мм':'Units: mm'));}
 }
 const pro=systems.find(s=>s.slug==='hall-pro-blades');const get=code=>pro.specTables.flatMap(t=>t.rows).find(r=>r[1]===code).at(-1).en;assert.equal(get('5071-263'),'Yes');assert.equal(get('5071-185'),'No');
});
test('Dimension filters combine widths with thickness and preserve printed decimal precision',()=>{
 const source={width:'12.70',length:'90.00',thickness:'0.89'};
 assert.equal(matchesDimensionFilters(source,{width:['12.7','19.5'],thickness:['0.89']}),true);
 assert.equal(matchesDimensionFilters(source,{width:['19.5'],thickness:['0.89']}),false);
 assert.equal(matchesDimensionFilters(source,{width:['12.7'],length:['75']}),false);
 assert.deepEqual(source,{width:'12.70',length:'90.00',thickness:'0.89'});
 const s=systems.find(s=>s.slug==='hall-large-bone-knee-blades');for(const lang of ['ru','en']){const html=renderSystem(s,lang);for(const field of ['width','length','thickness'])assert.ok(html.includes(`data-dimension-filter="${field}"`));}
});
test('Existing ordering owners are linked in both languages and cannot be selected again',()=>{
 const overlaps=report.overlaps.existingPublishedSystems;assert.equal(new Set(overlaps.map(x=>x.code)).size,16);
 for(const item of overlaps){const s=systems.find(s=>s.slug===item.sourceSystem);assert.ok(!s.refCodes.includes(item.code));const table=s.specTables.find(t=>t.codeLinks?.some(l=>l.code===item.code));assert.ok(table);for(const lang of ['ru','en'])assert.ok(renderSystem(s,lang).includes(`href="${lang==='en'?'/en':''}/catalog/conmed/${item.canonicalSystem}/"`));}
 const s=systems.find(s=>s.slug==='hall-electric-consoles-and-accessories');assert.equal(s.refCodes.length,0);const html=renderSystem(s,'en');assert.ok(!html.includes('data-copy-code'));assert.equal((html.match(/data-catalog-select="[^"]+"[^>]* disabled/g)||[]).length,4);
});
test('HALL indications and clinical specialties are complete in RU and EN',async()=>{
 const expected={'hall-sternum-saws':['cardiothoracic'],'hall-sternum-saw-blades':['cardiothoracic'],'hall-osteon':['ent'],'hall-e9000-system':['ent','spine','neurosurgery']};
 for(const [slug,specialties]of Object.entries(expected)){const s=systems.find(s=>s.slug===slug);assert.deepEqual(s.specialty,specialties);assert.ok(s.indications.ru&&s.indications.en);for(const lang of ['ru','en'])assert.ok(renderSystem(s,lang).includes(escapeHtml(s.indications[lang])));}
 const prepared=await prepareSystem(structuredClone(systems.find(s=>s.slug==='hall-sternum-saw-blades')),all);assert.ok(prepared.relatedSystems.length);
 for(const s of systems){assert.ok(s.heroImage);assert.ok(s.name.ru&&s.name.en&&s.description.ru&&s.description.en);assert.notEqual(s.shortDescription.en,s.description.en);assert.ok(s.sourcePages.every(n=>n>=8&&n<=78));}
});
test('Adjacent bur matrices retain their own names, dimensions and grit parameters',()=>{
 const micro=systems.find(s=>s.slug==='hall-micro-burs'),table=name=>micro.specTables.find(t=>t.title.en===name);
 assert.ok(table('Swanson Reamers'));assert.ok(table('Barrel Burs'));assert.ok(table('Oval Burs'));
 const lindemann=table('Lindemann Burs');assert.equal(lindemann.rows[0].at(-1).en,'31.00');
 const cylinder=table('Cylindrical'),cylinderRow=cylinder.rows.find(r=>r[1]==='5092-291');
 assert.equal(cylinderRow[cylinder.columns.findIndex(c=>c.en==='Diameter (mm)')].en,'3.00');
 assert.equal(cylinderRow[cylinder.columns.findIndex(c=>c.en==='Flutes')].en,'2.00');
 assert.equal(cylinderRow[cylinder.columns.findIndex(c=>c.en==='Compatible Bur Guard')].en,'1375-011');
 const heavy=table('Heavy Grit Diamond- Microbur. X-Long');assert.ok(heavy.rows.some(r=>r[heavy.columns.findIndex(c=>c.en==='Grit')].en==='60-70'));
 assert.ok(!rows.some(x=>['60-70','40-45'].includes(x.row[1])));
 const e=systems.find(s=>s.slug==='hall-e-burs'),wire=e.specTables.find(t=>t.title.en==='Wirepass burs');assert.equal(wire.rows[0].at(-1).en,'38.00');
});
