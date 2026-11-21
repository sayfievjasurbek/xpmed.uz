import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {loadSystems,prepareSystem} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';
import ru from '../src/i18n/ru.mjs';
import en from '../src/i18n/en.mjs';
const read=async path=>JSON.parse(await readFile(path,'utf8'));
const profile=await read('scripts/profiles/double-medical-trauma-part3.json');
const report=await read('reports/double-medical/trauma-catalogue-part3.json');
const all=await loadSystems(),systems=all.filter(s=>s.importPartition==='trauma-part3');

test('Trauma Part 3 uses only the five source-index ranges and preserves all earlier clinical content',async()=>{
 assert.deepEqual(profile.scope.map(s=>s.physicalPages),[[530,578],[582,608],[612,617],[620,628],[632,643]]);
 assert.deepEqual(profile.scope.map(s=>s.indexPage),[529,581,611,619,631]);
 const manifest=await read('public/catalogs/double-medical/trauma-catalogue/ocr/manifest-part3.json');assert.equal(manifest.dpi,600);assert.deepEqual(manifest.pages,profile.authorizedPhysicalPages);assert.equal(manifest.pages.length,103);
 for(const s of systems){assert.ok(s.sourcePages.every(p=>profile.authorizedPhysicalPages.includes(p)));assert.ok(!s.sourcePages.some(p=>profile.nonProductPages.includes(p)));if(s.slug==='2-0mm-kirschner-wire-with-olive-head')assert.equal(s.heroImage,'');else assert.ok(s.heroImage);assert.ok(s.specialty.includes('traumatology'));assert.ok(s.specialty.includes('orthopedics'));if(s.subcategories.includes('trauma-pediatric'))assert.ok(s.specialty.includes('pediatric-orthopedics'));}
 assert.equal(ru.labels['pediatric-orthopedics'],'Детская ортопедия');assert.equal(en.labels['pediatric-orthopedics'],'Pediatric orthopedics');
 for(const [path,hash]of Object.entries(await read('reports/double-medical/trauma-catalogue-part3/existing-system-hashes.json'))){
  const merged=profile.merges.find(s=>path.endsWith('/'+s.slug+'.json'));const sportsMerge=path.endsWith('/m-link-all-inside-meniscal-repair-system.json');const original=sportsMerge?`reports/double-medical/sports-medicine-catalogue/merge-backups/0564b2ce17c049fc1e77ab714414dcbe4f74e00e785b2ae3e0895b169868e09e/m-link-all-inside-meniscal-repair-system.json`:merged?`reports/double-medical/trauma-catalogue/merge-backups/${profile.sha256}/${merged.slug}.json`:path;
  assert.equal(createHash('sha256').update(await readFile(original)).digest('hex'),hash,path);
  if(merged||sportsMerge){const before=await read(original),after=await read(path);for(const key of ['name','shortDescription','description','sourcePdf','sourcePages','status','specTables','heroImage','features','hotspots'])assert.deepEqual(after[key],before[key]);if(merged)for(const t of merged.referenceTables)assert.deepEqual(after.referenceTables.find(x=>x.id===t.id).rows,t.rows);}
 }
});

test('REF verification retains parallel HA codes and resolves the duplicate source REF by owner direction',async()=>{
 const audit=await read('reports/double-medical/trauma-catalogue-part3/code-verification.json');assert.equal(audit.bodyOccurrences,936);assert.equal(audit.setHeaderOccurrences,10);assert.equal(audit.distinctCodes,884);assert.equal(report.codesFound,946);assert.equal(report.codesVerified,946);
 for(const record of [...audit.records,...audit.setHeaders])assert.ok(Object.values(record.readings).some(v=>v.split(/\s/)[0]===record.REF)||record.visualReading);
 const cortical=systems.find(s=>s.slug==='6-0mm-cortex-bone-screw');const t=cortical.specTables.find(t=>t.sourcePages.includes(562));assert.match(t.columns[2].en,/HA Coating/);assert.ok(t.rows.some(r=>r[1]==='100130150'&&r[2]==='105190003S'));assert.ok(t.rows.some(r=>r[1]==='100230100'&&r[2]==='105210001S'&&r[3].en==='Ø6.0/Ø5.0*100/40'));
 const ring=systems.find(s=>s.slug==='numbered-ring');assert.ok(ring.refCodes.includes('100154800'));
 const pediatric=systems.find(s=>s.slug==='pediatric-hip-locking-plate-5-0');assert.equal(pediatric.status,'published');const retained=pediatric.specTables.flatMap(t=>t.rows).filter(r=>r[1]==='020940003');assert.equal(retained.length,1);assert.equal(retained[0][2].en,'150');assert.equal(retained[0][3].en,'3');assert.equal(retained[0][4].en,'89');assert.equal(pediatric.specTables[0].rows.length,32);assert.equal(report.openRealFlags.length,0);
 assert.equal(systems.filter(s=>s.status==='published').length,138);assert.equal(systems.filter(s=>s.status==='draft').length,0);
});

test('Case quantities remain separate, sets link to implants and shared tools link existing sets',()=>{
 const cases=systems.find(s=>s.slug==='locking-plate-screw-case-set');const t=cases.specTables.find(t=>t.sourcePages.includes(632));assert.equal(t.columns[2].ru,'Количество');const tray=t.rows.find(r=>r[1]==='116293830');assert.equal(tray[2].en,'3');assert.equal(tray[0].en,'Implant Tray');
 for(const s of systems.filter(s=>s.instrumentSet))for(const slug of s.relatedSystemSlugs){const target=all.find(t=>t.slug===slug);assert.ok(target);assert.ok(target.relatedSystemSlugs.includes(s.slug));}
 assert.equal(report.instrumentSets,10);assert.equal(report.instrumentCollections,3);assert.equal(profile.relatedExistingSets.length,8);
 for(const link of profile.relatedExistingSets){const s=systems.find(s=>s.slug===link.from),target=all.find(s=>s.slug===link.to);assert.ok(target);assert.ok(s.relatedSystemSlugs.includes(target.slug));assert.ok(link.sharedREF.every(code=>s.refCodes.includes(code)&&target.refCodes.includes(code)));}
});

test('Source photos retain exact enhancement, originals, reviewed scenes and separated instrument silhouettes',async()=>{
 const native=await read('reports/double-medical/trauma-catalogue-part3/source-images.json'),prepared=await read('public/images/products/double-medical/trauma-catalogue-part3/prepared-assets.json');assert.equal(Object.keys(native).length,426);assert.deepEqual(Object.keys(prepared).sort(),Object.keys(native).sort());
 for(const key of Object.keys(native)){const a=prepared[key];assert.equal(a.captionFree,true);assert.deepEqual(a.imageEnhancement.enhancedSize,a.originalSize.map(v=>v*2));await access('public'+a.src);await access(`public/images/products/double-medical/trauma-catalogue-part3/_originals/${key}.png`);}
 assert.ok(!native['page-586-art-04']);assert.ok(!native['page-587-art-03']);assert.equal(Object.values(native).filter(a=>a.sourceRowId).length,5);assert.equal(prepared['page-558-art-01'].imageType,'scene');
 const epiphyseal=systems.find(s=>s.slug==='3-0-4-5-epiphyseal-plate-instrument-set');const t=epiphyseal.specTables.find(t=>t.sourcePages.includes(607));assert.ok(t.images.some(i=>i.src.includes('page-607-art-02')));assert.ok(!t.rowImages.some(i=>i?.src.includes('page-607-art-02')));
});

test('Only cleared Part 3 systems have public bilingual pages and the twenty-row sample matches source data',async()=>{
 const index=await read('dist/catalog-index.json');for(const s of systems){assert.equal(index.some(i=>i.slug===s.slug),s.status==='published');if(s.status!=='published')continue;const prepared=await prepareSystem(s,all);for(const lang of ['ru','en']){const html=await readFile(`dist/${lang==='en'?'en/':''}catalog/double-medical/${s.slug}/index.html`,'utf8');assert.ok(html.includes('data-system-page'));assert.equal((html.match(/class="sp-market-note"/g)||[]).length,1);assert.doesNotMatch(html,/class="review-flag"|уточняйте у менеджера/);assert.ok(renderSystem(prepared,lang).includes('data-catalog-select='));}}
 assert.equal(report.randomSample.length,20);for(const sample of report.randomSample){const source=[...profile.systems,...profile.merges].find(s=>s.slug===sample.slug);assert.ok((source.specTables||source.referenceTables).some(t=>t.sourcePages.includes(sample.pdfPage)&&t.rows.some(r=>JSON.stringify(r[0])===JSON.stringify(sample.size)&&sample.REF.split(' / ').every(code=>r.includes(code)))));}
});
