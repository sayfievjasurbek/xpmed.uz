import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateSystem} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';
import {techniqueSteps} from '../src/surgical-technique.mjs';
const read=async path=>JSON.parse(await readFile(path,'utf8'));
const system=await read('content/products/double-medical/cynthia-knee-system.json');
const before=await read('reports/double-medical/cynthia-revision-surgical-guide/before-cynthia.json');
const technique=system.variants.find(v=>v.id==='revision').surgicalTechnique;
test('Guide is additive to Revision only, with all original Cynthia measurements, Primary data and publication unchanged',()=>{
 assert.deepEqual(validateSystem(system),[]);assert.equal(system.status,before.status);assert.deepEqual(system.variants[0],before.variants[0]);for(const key of ['specTables','referenceTables','features','components','hotspots','sourcePdf','sourcePages'])assert.deepEqual(system[key],before[key]);for(const[key,value]of Object.entries(before.variants[1]))assert.deepEqual(system.variants[1][key],value);
});
test('Technique retains all 21 numbered bilingual steps, seven warnings and complete precautions in five chapters',()=>{
 assert.equal(technique.chapters.length,5);const steps=techniqueSteps(technique);assert.deepEqual(steps.map(s=>s.number),['1',...Array.from({length:8},(_,i)=>`2.${i+1}`),...Array.from({length:9},(_,i)=>`3.${i+1}`),'4','5.1','5.2']);assert.equal(steps.flatMap(s=>s.notes).length,7);assert.equal(steps.find(s=>s.number==='5.1').checklist.length,7);assert.equal(steps.find(s=>s.number==='5.2').checklist.length,3);for(const step of steps){assert.ok(step.title.ru&&step.title.en);assert.ok(step.sourceBlocks.length);assert.ok(step.text.en||step.checklist?.length);}
});
test('Both guide tables retain their exact merged values and covered blank cells',()=>{
 const tables=techniqueSteps(technique).flatMap(s=>s.tables||[]);assert.equal(tables.length,2);for(const [i,t]of tables.entries()){assert.equal(t.unit,'mm');assert.deepEqual(t.rows.map(r=>r.slice(0,2)),[['80','25'],['120','65'],['160','105']]);assert.equal(t.rows[0][2].value,'30');assert.equal(t.rows[0][2].rowspan,3);assert.equal(t.rows[0][3].value,i?'55':'25');assert.equal(t.rows[0][3].rowspan,3);assert.deepEqual(t.rows[1].slice(2),['','']);assert.deepEqual(t.sourcePages,[i?9:3]);}
});
test('82 native source photographs/illustrations are preserved without background removal and with native dimensions',async()=>{
 const images=await read('public/images/products/double-medical/cynthia-revision-technique/assets.json');assert.equal(images.length,82);for(const image of images){assert.match(image.sourceMethod,/no OCR, no rembg/);assert.equal(image.imageType,'scene');assert.deepEqual(system.imageDimensions[image.src],{width:image.width,height:image.height});await readFile('public'+image.src);}const steps=techniqueSteps(technique);assert.equal(steps.flatMap(s=>s.images).length,80);assert.equal(steps.flatMap(s=>s.tables||[]).filter(t=>t.rows[0][2].image).length,2);
});
test('Both languages retain Revision technique while the two manufacturer PDFs are hidden',()=>{
 for(const lang of ['ru','en']){const html=renderSystem(system,lang);assert.ok(html.includes('id="technique-revision"'));assert.ok(!html.includes('id="technique-primary"'));assert.equal((html.match(/class="sp-technique-chapter"/g)||[]).length,5);assert.equal((html.match(/class="sp-technique-chapter" open/g)||[]).length,1);assert.equal((html.match(/data-technique-step-link=/g)||[]).length,21);assert.equal((html.match(/rowspan="3"/g)||[]).length>=4,true);assert.ok(!html.includes('cynthia-knee-system/source.pdf'));assert.ok(!html.includes('cynthia-revision-surgical-guide/source.pdf'));assert.ok(html.includes('joint-catalogue/source.pdf'));assert.match(html,lang==='ru'?/Единицы: мм|Единица измерения: мм|мм<\/p>/:/mm<\/p>/);}
});
test('Guide import is a direct-text supplement and viewer suppresses stale download controls while resolving metadata',async()=>{
 const report=await read('reports/double-medical/cynthia-revision-surgical-guide.json');assert.equal(report.systemsCreated,0);assert.equal(report.steps,21);assert.equal(report.images,82);assert.equal(report.existingProductDataUnchanged,true);assert.match(report.method,/no OCR/);const script=await readFile('src/pdf-viewer.js','utf8');assert.ok(script.indexOf('downloadControl.hidden=true')<script.indexOf('let catalog=providedCatalog'));assert.match(script,/download.hidden=catalog.viewOnly===true/);
});
