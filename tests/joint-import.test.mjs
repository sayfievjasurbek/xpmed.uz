import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const read=async file=>JSON.parse(await readFile(file,'utf8'));
const root='reports/double-medical/joint-catalogue';
const profile=await read('scripts/profiles/double-medical-joint-catalogue.json');
const systems=await Promise.all([...profile.systems,...profile.merges].map(s=>read(`content/products/double-medical/${s.slug}.json`)));
test('Joint import conserves valid source REFs, pairs Apollo codes, and withholds the uncertain osteotome REF',async()=>{
 const verification=await read(root+'/verification.json');const codes=systems.flatMap(s=>[...s.specTables.filter(t=>t.id.startsWith('joint-')),...(s.referenceTables||[]).filter(t=>t.id.startsWith('joint-'))].flatMap(t=>t.rows.flatMap(row=>row.slice(1).filter(cell=>typeof cell==='string'))));codes.push(...systems.filter(s=>s.setCode).map(s=>s.setCode));assert.equal(verification.found,1580);assert.equal(verification.verified,1580);assert.deepEqual(codes.sort(),verification.records.map(r=>r.value).filter(code=>code!=='11516140').sort());assert.equal(systems.filter(s=>s.setCode).length,19);
 const anty=systems.find(s=>s.slug==='anty-f-series');assert.equal(anty.referenceTables.flatMap(t=>t.rows).length,26);assert.ok(anty.referenceTables.flatMap(t=>t.rows).every(row=>!row[2].en.includes('11#')));
});
test('Additive Joint references preserve all four published source brochures and clinical sections',async()=>{
 for(const merge of profile.merges){const actual=systems.find(s=>s.slug===merge.slug),before=await read(`${root}/merge-backups/${profile.sha256}/${merge.slug}.json`);for(const key of ['status','sourcePdf','sourcePages','variants','specTables','features','hotspots','description','heroImage'])assert.deepEqual(key==='variants'&&merge.slug==='cynthia-knee-system'?actual[key].map(({surgicalTechnique,...original})=>original):actual[key],before[key],`${merge.slug}: ${key}`);assert.ok(actual.catalogImports.some(c=>c.sourceSha256===profile.sha256));}
});
test('Owner-resolved Joint systems are all published and keep image QR graphics out of pages',async()=>{
 const newly=systems.filter(s=>profile.systems.some(p=>p.slug===s.slug));assert.equal(newly.filter(s=>s.status==='published').length,44);assert.deepEqual(newly.filter(s=>s.status==='draft').map(s=>s.slug).sort(),[]);for(const s of newly.filter(s=>s.status==='published'))assert.equal(s.review.flags.length,0);
 const ignored=await read(root+'/ignored-qr-assets.json');for(const s of systems){const renderedImages=JSON.stringify([s.heroImage,s.gallery,s.specTables.map(t=>[t.images,t.rowImages]),s.referenceTables?.map(t=>t.images)]);for(const name of ignored)assert.ok(!renderedImages.includes(name),`${s.slug} uses QR ${name}`);}
});
test('Every instrument set and implant relationship is reciprocal',()=>{
 for(const set of systems.filter(s=>s.setCode))for(const slug of set.relatedSystemSlugs){const implant=systems.find(s=>s.slug===slug);assert.ok(implant,slug);assert.ok(implant.relatedSystemSlugs.includes(set.slug),`${slug} -> ${set.slug}`);}
});
test('Unconfirmed osteotome REF is unavailable in RU/EN requests and the likely code stays internal',async()=>{
 const {renderSystem}=await import('../src/system-page.mjs');const s=systems.find(s=>s.slug==='accurate-ps-knee-instrument-set');const table=s.specTables.find(t=>t.sourcePages?.includes(59));const rowIndex=table.rows.findIndex(row=>row[0].en==='Cynthia Osteotome for Intercondylar, 18#');assert.ok(rowIndex>=0);assert.equal(table.rows[rowIndex][1],null);assert.ok(!s.refCodes.includes('11516140'));assert.ok(!s.refCodes.includes('115161400'));
 for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.match(html,/data-catalog-select="double-medical:joint-accurate-ps-knee-instrument-set-p59:8"[^>]* disabled/);assert.doesNotMatch(html,lang==='ru'?/Каталожный номер уточняйте у менеджера/:/Confirm the catalog number with your sales manager/);assert.ok(!html.includes('115161400'));assert.ok(!html.includes('11516140'));}
});
test('Apollo source pairs form exactly six selectable sizes with both codes in printed order',async()=>{
 const {renderSystem}=await import('../src/system-page.mjs');const s=systems.find(s=>s.slug==='apollo-62-72-cup-instrument-set'),t=s.specTables.find(t=>t.sourcePages?.includes(82));const pairs=[['113099200','113099300'],['113099400','113099500'],['113099600','113099700'],['115091300','115662500'],['115662600','115662700'],['115662800','115662900']];assert.equal(t.rows.length,6);assert.deepEqual(t.rows.map(row=>row.slice(1)),pairs);
 for(const [i,row]of t.rows.entries()){assert.ok(row[0].en.includes(`Ø${62+i*2}/36`));assert.equal(t.rowSources[i].sourceRows.length,2);assert.equal(t.rowSources[i].codeEvidence.length,2);}
 for(const lang of ['ru','en']){const html=renderSystem(s,lang);for(const pair of pairs)assert.ok(html.includes(`data-row-codes="[&quot;${pair[0]}&quot;,&quot;${pair[1]}&quot;]"`));assert.doesNotMatch(html,lang==='ru'?/Два каталожных номера на размер, уточняйте у менеджера/:/Two catalog numbers per size/);}
});
test('Amity and Angel corrections resolve public conflicts while all five source corrections remain internal',async()=>{
 const {renderSystem}=await import('../src/system-page.mjs');const amity=systems.find(s=>s.slug==='amity-a-ve-acetabular-liner'),angel=systems.find(s=>s.slug==='angel-shoulder-system');assert.ok(JSON.stringify(amity.referenceTables).includes('UHMWPE'));assert.ok(!renderSystem(amity).includes('Ti coating'));assert.ok(!renderSystem(amity,'en').includes('Ti coating'));
 const stem=angel.referenceTables.find(t=>t.id.endsWith('p34-1'));assert.deepEqual(stem.rows[0][2],{ru:'107 мм × 6.7 мм',en:'107 mm × 6.7 mm'});assert.equal(stem.cellNotes,undefined);const tray=angel.referenceTables.find(t=>t.id.endsWith('p36-1'));assert.equal(tray.rows[3][1],'13Y081015S');assert.deepEqual(tray.rows[3][2],{ru:'15',en:'15'});assert.equal(tray.note,undefined);assert.equal(angel.catalogImports.find(c=>c.sourceSha256===profile.sha256).review.flags.length,0);
 const report=await read('reports/double-medical/joint-catalogue.json');assert.deepEqual(report.uncertainties,[]);assert.equal(report.sourceCatalogCorrections.length,5);assert.ok(report.sourceCatalogCorrections.some(c=>c.correction.includes('probably 115161400')));assert.ok(!renderSystem(angel).includes('здесь указано 5'));
});
