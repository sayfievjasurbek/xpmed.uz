import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {loadSystems,normalizeSystem,validateSystem} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';
import {selectionMessage} from '../src/catalog-selection.js';
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const s=await read('content/products/double-medical/m-link-all-inside-meniscal-repair-system.json');
test('M-Link retains all seven independently verified REF codes with selectable bilingual ordering rows',async()=>{
 const codes=['151250000S','151260000S','152910270S','114301400','114301300','115012500','114302600'];const added=['114302000','114301200'];assert.deepEqual(s.refCodes,[...codes,...added]);assert.equal(s.catalogType,'system');assert.equal(s.status,'published');assert.deepEqual(s.review.flags,[]);assert.equal(s.referenceTables.length,3);assert.deepEqual(s.referenceTables.flatMap(t=>t.rows.map(r=>r[1])),[...codes,...added]);
 const audit=await read('reports/double-medical/m-link-all-inside/verified-codes.json');assert.equal(audit.length,7);for(const row of audit)assert.deepEqual(new Set(row.verification.readings.map(r=>r.reader)),new Set(['PSM3','PSM11','Vision','Codex visual 600-DPI crop']));
 for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.equal((html.match(/data-catalog-select=/g)||[]).length,9);assert.match(html,/data-selected-request/);for(const code of [...codes,...added])assert.ok(html.includes(`data-row-codes="[&quot;${code}&quot;]"`));assert.doesNotMatch(html,/sp-list-system/);}
 const message=selectionMessage([{name:{ru:'Изогнутая игла, 27°',en:'Curved needle, 27°'},codes:['152910270S'],quantity:2}],'ru','Запрос');assert.ok(message.includes('152910270S × 2'));
});
test('M-Link surgical technique preserves eight complete bilingual steps, four warnings and 14 untouched illustrations',async()=>{
 const steps=s.surgicalTechnique.steps;assert.equal(steps.length,8);assert.equal(steps.flatMap(step=>step.images).length,14);assert.equal(steps.flatMap(step=>step.notes).length,4);assert.equal(steps[1].images.length,0);assert.equal(steps[3].sourcePages[0],6);assert.ok(steps[3].text.ru.includes('14 мм'));assert.ok(steps[5].text.en.includes('5 mm'));assert.ok(steps[6].text.en.includes('8–10 mm'));assert.ok(steps[6].notes[0].text.ru.includes('преждевременно'));assert.ok(steps[7].notes[0].text.en.includes('tibial side'));
 for(const step of steps)for(const image of step.images){assert.ok(/no rembg/i.test(image.sourceMethod));assert.equal(image.imageType,'scene');await readFile('public'+image.src);}
 for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.match(html,/data-section-tab="technique"/);assert.match(html,/id="technique-default" data-section="technique"/);assert.equal((html.match(/class="sp-technique-number"/g)||[]).length,8);assert.equal((html.match(/class="sp-technique-note"/g)||[]).length,4);assert.match(html,lang==='ru'?/Не заменяет инструкцию по применению/:/Does not replace the instructions for use/);}
});
test('Technique section is optional, variant-aware, escaped and validated for future systems',()=>{
 const minimal=normalizeSystem({slug:'minimal',brand:'double-medical',category:'sports-medicine',name:{ru:'Система',en:'System'}});assert.ok(!renderSystem(minimal).includes('data-section="technique"'));minimal.variants=[{id:'one',name:{ru:'Один',en:'One'},surgicalTechnique:{steps:[{title:{ru:'Название',en:'Title'},text:{ru:'<script>не выполнять</script>',en:'<script>do not execute</script>'},images:[]}]}},{id:'two',name:{ru:'Два',en:'Two'}}];const html=renderSystem(minimal);assert.match(html,/id="technique-one"/);assert.ok(!html.includes('id="technique-two"'));assert.match(html,/&lt;script&gt;не выполнять&lt;\/script&gt;/);assert.deepEqual(validateSystem(minimal),[]);minimal.variants[0].surgicalTechnique.steps[0].text={en:'Missing Russian'};assert.ok(validateSystem(minimal).some(e=>e.includes('step.text.ru')));
});
test('M-Link reuses sports-medicine taxonomy and links existing meniscal repair families both ways',async()=>{
 assert.equal(s.category,'sports-medicine');assert.equal(s.subcategory,'sports-medicine-meniscus');assert.deepEqual(s.specialty,['sports','orthopedics']);const all=await loadSystems();assert.ok(s.relatedSystemSlugs.length>=3);for(const ref of s.relatedSystemSlugs){const other=all.find(other=>`${other.brand}/${other.slug}`===ref||(ref===other.slug&&other.brand===s.brand));assert.ok(other);assert.ok(other.relatedSystemSlugs.includes(`double-medical/${s.slug}`)||other.relatedSystemSlugs.includes(s.slug));}
 assert.deepEqual(s.review.skippedSourcePages,[1,2,3,13,14,15,16]);assert.deepEqual(s.sourcePages,[4,5,6,7,8,9,10,11,12]);assert.equal(s.sourcePageImages.length,9);assert.ok(s.review.translatedFields.includes('surgicalTechnique.steps.7.notes.0.text.ru'));
});
test('Device photos retain native originals and exact 2x enhancement without applying rembg to technique art',async()=>{
 const assets=await read('public/images/products/double-medical/m-link-all-inside/prepared-assets.json');const photos=assets.filter(a=>a.imageEnhancement);assert.equal(photos.length,6);for(const asset of photos){assert.deepEqual(asset.imageEnhancement.enhancedSize,asset.nativeSize.map(n=>n*2));await readFile(`public/images/products/double-medical/m-link-all-inside/_originals/${asset.name}.png`);assert.equal(asset.imageType,'cutout');}assert.equal(assets.filter(a=>a.step).length,14);
});
