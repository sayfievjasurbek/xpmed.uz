import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {loadSystems,prepareSystem} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const profile=await read('scripts/profiles/double-medical-trauma-part1.json');
const report=await read('reports/double-medical/trauma-catalogue-part1.json');
const all=await loadSystems();const systems=all.filter(s=>s.importPartition==='trauma-part1');

test('Trauma Part 1 imports only the four authorized sections and preserves existing systems',async()=>{
 assert.equal(systems.length,224);assert.equal(systems.filter(s=>s.category==='trauma-implants').length,205);assert.equal(systems.filter(s=>s.category==='trauma-instrument-sets').length,19);
 const manifest=await read('public/catalogs/double-medical/trauma-catalogue/ocr/manifest-part1.json');assert.equal(manifest.dpi,600);assert.deepEqual(manifest.pages,profile.authorizedPhysicalPages);assert.equal(manifest.pages.length,198);
 for(const s of systems){assert.ok(s.sourcePages.every(p=>profile.authorizedPhysicalPages.includes(p)&&p<211));assert.deepEqual(s.specialty,['traumatology','orthopedics']);assert.ok(s.heroImage);for(const slug of s.relatedSystemSlugs){const target=all.find(t=>t.slug===slug);assert.ok(target);assert.ok(target.relatedSystemSlugs.includes(s.slug));}}
 const part2=await read('scripts/profiles/double-medical-trauma-part2.json');
 for(const [path,hash]of Object.entries(await read('reports/double-medical/trauma-catalogue-part1/existing-system-hashes.json'))){
  const merged=part2.merges?.find(m=>path.endsWith('/'+m.slug+'.json'));
  const sportsMerge=path.endsWith('/m-link-all-inside-meniscal-repair-system.json');
  const original=sportsMerge?`reports/double-medical/sports-medicine-catalogue/merge-backups/0564b2ce17c049fc1e77ab714414dcbe4f74e00e785b2ae3e0895b169868e09e/m-link-all-inside-meniscal-repair-system.json`:merged?`reports/double-medical/trauma-catalogue/merge-backups/${part2.sha256}/${merged.slug}.json`:path;
  assert.equal(createHash('sha256').update(await readFile(original)).digest('hex'),hash,path);
  if(merged||sportsMerge){const before=await read(original),after=await read(path);for(const field of ['name','shortDescription','description','specTables','variants','features','hotspots','heroImage','status','sourcePdf','sourcePages'])assert.deepEqual(after[field],before[field],path+': '+field);}
 }
 assert.equal(report.systemsMerged,0);assert.equal(report.instrumentSets,19);
});

test('Trauma source values, set headings and real source issues remain traceable without guessed REF codes',async()=>{
 assert.equal(report.systemsPublished,224);assert.equal(report.systemsDraft,0);assert.equal(report.openRealFlags.length,0);assert.equal(report.sourceIssuesAcceptedByOwner.length,5);assert.equal(report.codesFound,report.codesVerified);assert.equal(report.setCodeOccurrences,22);
 assert.deepEqual(await read('reports/double-medical/trauma-catalogue-part1/code-confidence-review.json'),[]);
 for(const s of systems){const source=profile.systems.find(t=>t.slug===s.slug);const later=JSON.parse(await readFile('scripts/profiles/double-medical-trauma-part3.json','utf8')).merges.find(m=>m.slug===s.slug);assert.deepEqual(s.refCodes,[...new Set([...source.refCodes,...(later?.refCodes||[])])]);assert.deepEqual(s.specTables.map(t=>t.rows),source.specTables.map(t=>t.rows));assert.equal(s.status,s.review.flags.some(f=>!['resolved','dismissed'].includes(f.status))?'draft':'published');}
 const small=systems.find(s=>s.slug==='small-locking-instrument-set');const missing=small.specTables.flatMap(t=>t.rows).find(r=>r[1]===null);assert.match(missing[0].en,/Bone Holding Forceps/);
 const reconstruction=systems.find(s=>s.slug==='reconstruction-instrument-set');const repeated=reconstruction.components.filter(c=>c.refCodes.includes('110021300'));assert.equal(repeated.length,2);assert.notDeepEqual(repeated[0].name,repeated[1].name);
 const distal=systems.find(s=>s.slug==='distal-femoral-locking-plate-instrument-set');assert.ok(distal.setCodes.includes('111850000'));assert.ok(!distal.components.some(c=>c.refCodes.includes('111850000')));
 assert.ok(distal.specTables.some(t=>t.title.en.includes('111850000')));assert.equal(report.randomSample.length,20);
});

test('Trauma publication includes bilingual routes, native cutouts and selectable REF codes without duplicate Components',async()=>{
 const qa=await read('reports/double-medical/trauma-catalogue-part1/image-qa.json');const images=await read('public/images/products/double-medical/trauma-catalogue/prepared-assets.json');assert.equal(Object.keys(images).length,670);assert.equal(qa.status,'reviewed');assert.equal(qa.assetsReviewed.length,670);
 for(const a of Object.values(images)){assert.deepEqual(a.imageEnhancement.enhancedSize,a.originalSize.map(v=>v*2));await access('public'+a.src);}
 const index=await read('dist/catalog-index.json');for(const s of systems){assert.equal(index.some(i=>i.slug===s.slug),s.status==='published');if(s.status==='published')for(const lang of ['ru','en'])await access(`dist/${lang==='en'?'en/':''}catalog/double-medical/${s.slug}/index.html`);}
 const set=systems.find(s=>s.slug==='2-4mm-2-7mm-3-5mm-small-fragment-instrument-set');const prepared=await prepareSystem(set,all);
 for(const lang of ['ru','en']){const html=renderSystem(prepared,lang);assert.equal((html.match(/class="sp-market-note"/g)||[]).length,1);assert.match(html,/data-catalog-select=/);assert.ok(!html.includes('id="components-default"'));}
});
