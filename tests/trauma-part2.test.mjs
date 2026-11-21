import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {loadSystems,prepareSystem} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const profile=await read('scripts/profiles/double-medical-trauma-part2.json');
const report=await read('reports/double-medical/trauma-catalogue-part2.json');
const all=await loadSystems();const systems=all.filter(s=>s.importPartition==='trauma-part2');
const protectedFields=['name','shortDescription','description','specTables','variants','features','hotspots','heroImage','status','sourcePdf','sourcePages'];

test('Trauma Part 2 is restricted to source index sections 5–8 and preserves all unrelated content',async()=>{
 assert.equal(profile.partition,'part2');assert.deepEqual(profile.scope.map(s=>s.indexPage),[211,277,307,321]);
 assert.equal(profile.authorizedPhysicalPages.length,308);
 const ownerPublication=await read('reports/double-medical/trauma-catalogue-part1/owner-publication.json');
 const manifest=await read('public/catalogs/double-medical/trauma-catalogue/ocr/manifest-part2.json');assert.equal(manifest.dpi,600);assert.deepEqual(manifest.pages,profile.authorizedPhysicalPages);
 for(const s of systems){assert.ok(s.sourcePages.every(p=>p>211&&p<528&&profile.authorizedPhysicalPages.includes(p)));assert.ok(!s.sourcePages.some(p=>profile.nonProductPages.includes(p)));assert.deepEqual(s.specialty,['traumatology','orthopedics']);}
 for(const [path,hash]of Object.entries(await read('reports/double-medical/trauma-catalogue-part2/existing-system-hashes.json'))){
  const m=profile.merges.find(m=>path.endsWith('/'+m.slug+'.json'));
  const ownerApproved=ownerPublication.systems.find(s=>s.path===path);
  if(ownerApproved){
   assert.equal(ownerApproved.beforeSha256,hash);assert.equal(createHash('sha256').update(await readFile(ownerApproved.backup)).digest('hex'),hash);
   const before=await read(ownerApproved.backup),after=await read(path);const omitPublication=({status,review,publishedAt,...clinical})=>clinical;assert.deepEqual(omitPublication(after),omitPublication(before),path);assert.equal(after.status,'published');assert.ok(after.review.flags.every(f=>f.status==='dismissed'));continue;
  }
  if(!m){
   const part3=await read('scripts/profiles/double-medical-trauma-part3.json'),later=part3.merges.find(m=>path.endsWith('/'+m.slug+'.json'));
   const sportsMerge=path.endsWith('/m-link-all-inside-meniscal-repair-system.json');
   const original=sportsMerge?`reports/double-medical/sports-medicine-catalogue/merge-backups/0564b2ce17c049fc1e77ab714414dcbe4f74e00e785b2ae3e0895b169868e09e/m-link-all-inside-meniscal-repair-system.json`:later?`reports/double-medical/trauma-catalogue/merge-backups/${part3.sha256}/${later.slug}.json`:path;
   assert.equal(createHash('sha256').update(await readFile(original)).digest('hex'),hash,path);
   if(later||sportsMerge){const before=await read(original),after=await read(path);for(const field of protectedFields)assert.deepEqual(after[field],before[field],(later?.slug||'m-link')+': '+field);}
   continue;
  }
  const backup=`reports/double-medical/trauma-catalogue/merge-backups/${profile.sha256}/${m.slug}.json`;assert.equal(createHash('sha256').update(await readFile(backup)).digest('hex'),hash,path);
  const before=await read(backup),after=await read(path);for(const field of protectedFields)assert.deepEqual(after[field],before[field],m.slug+': '+field);
 }
});

test('Trauma merges, REF selection and bilingual catalog tables retain exact reviewed source values',async()=>{
 assert.equal(systems.length,report.systemsNew);assert.equal(profile.merges.length,report.systemsMerged);assert.equal(report.instrumentSets,37);assert.equal(report.randomSample.length,20);
 assert.ok(profile.merges.some(s=>s.slug==='uhn-universal-humeral-nail'));
 for(const source of profile.systems){const s=systems.find(s=>s.slug===source.slug);assert.deepEqual(s.refCodes,source.refCodes);assert.deepEqual(s.specTables.map(t=>t.rows),source.specTables.map(t=>t.rows));const open=s.review.flags.filter(f=>!['resolved','dismissed'].includes(f.status));assert.equal(s.status,open.length?'draft':'published');}
 for(const m of profile.merges){const s=all.find(s=>s.slug===m.slug);for(const table of m.referenceTables){assert.deepEqual(s.referenceTables.find(t=>t.id===table.id).rows,table.rows);}assert.ok(s.catalogImports.some(c=>c.sourceSha256===profile.sha256&&JSON.stringify(c.sourcePages)===JSON.stringify(m.sourcePages)));}
 for(const s of systems)for(const slug of s.relatedSystemSlugs){const other=all.find(t=>t.slug===slug);assert.ok(other,slug);assert.ok(other.relatedSystemSlugs.includes(s.slug),s.slug+' ↔ '+slug);}
 const pfna=systems.find(s=>s.slug==='proximal-femoral-nail-anti-rotation-long');assert.ok(pfna);assert.equal(pfna.specTables[0].rows.length,32);assert.ok(pfna.specTables[0].rows.some(r=>r[1]===null&&r[2]));assert.match(pfna.specTables[0].columns[1].en,/16.5/);assert.match(pfna.specTables[0].columns[2].en,/17.0/);
});

test('Trauma Part 2 native photos and row-level composite splits remain traceable',async()=>{
 const qa=await read('reports/double-medical/trauma-catalogue-part2/image-qa.json');const native=await read('reports/double-medical/trauma-catalogue-part2/source-images.json');const assets=await read('public/images/products/double-medical/trauma-catalogue-part2/prepared-assets.json');assert.equal(qa.status,'reviewed');assert.deepEqual(new Set(qa.assetsReviewed),new Set(Object.keys(native)));assert.deepEqual(Object.keys(assets).sort(),Object.keys(native).sort());
 for(const [key,a]of Object.entries(assets)){assert.equal(a.captionFree,true);assert.deepEqual(a.imageEnhancement.enhancedSize,a.originalSize.map(v=>v*2));await access('public'+a.src);await access(`public/images/products/double-medical/trauma-catalogue-part2/_originals/${key}.png`);}
 const splits=Object.values(native).filter(a=>a.sourceComposite);assert.ok(splits.length>0);for(const s of splits)assert.ok(s.sourceRowId);
});

test('Published Trauma pages and catalog library expose no duplicate catalog system links',async()=>{
 const index=await read('dist/catalog-index.json');
 for(const s of systems){assert.equal(index.some(i=>i.slug===s.slug),s.status==='published');if(s.status==='published')for(const lang of ['ru','en'])await access(`dist/${lang==='en'?'en/':''}catalog/double-medical/${s.slug}/index.html`);}
 const catalogs=await read('dist/catalog-library-index.json');const trauma=catalogs.find(c=>c.file.includes('/trauma-catalogue/'));assert.ok(trauma);assert.equal(trauma.systems.length,new Set(trauma.systems.map(s=>s.url)).size);
 const set=systems.find(s=>s.category==='trauma-instrument-sets'&&s.status==='published');const prepared=await prepareSystem(set,all);for(const lang of ['ru','en']){const html=renderSystem(prepared,lang);assert.equal((html.match(/class="sp-market-note"/g)||[]).length,1);assert.match(html,/data-catalog-select=/);assert.ok(!html.includes('id="components-default"'));}
});
