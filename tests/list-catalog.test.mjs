import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import {loadSystems,prepareSystem}from '../src/catalog-data.mjs';import {renderSystem}from '../src/system-page.mjs';import {escape as escapeHtml}from '../src/html.mjs';
import {isListCatalog,separateListComponents}from '../src/list-catalog.mjs';import {validSelection,readSelection,selectionMessage,SELECTION_KEY}from '../src/catalog-selection.js';
const all=await loadSystems(),drafts=all.filter(s=>s.brand==='conmed'&&s.catalogType==='list'&&s.sourcePdf.includes('/advanced-visualization-system/'));
test('CONMED list reorganization preserves every ordering cell, accepted code and blank',async()=>{assert.equal(drafts.length,11);assert.ok(drafts.every(s=>s.status==='draft'||(s.status==='published'&&!s.review.flags.length)));const baseline=JSON.parse(await fs.readFile('reports/conmed/list-layout/report.json'));const actual=drafts.flatMap(s=>s.specTables.flatMap(t=>t.rows.flatMap((row,i)=>row.flatMap((c,j)=>{const evidence=t.rowSources?.[i]?.codeEvidence?.find(e=>e.column===j+1);return j&&typeof c==='string'?[[evidence?.tableId||t.id,evidence?.row?evidence.row-1:i,j,c]]:[];}))));const expected=baseline.codeCellSnapshot.flatMap(row=>Array.from({length:row.at(-1)},()=>row.slice(0,-1)));const sort=rows=>rows.map(JSON.stringify).sort();assert.deepEqual(sort(actual),sort(expected));assert.equal(actual.filter(r=>r[3]).length,257);assert.equal(drafts.flatMap(s=>s.specTables).filter(t=>t.id==='quicklatch-4mm')[0].rows[8][1],'T4907');});
test('List rendering keeps specifications and subgroup descriptions at the matching table in both languages',()=>{for(const s of drafts){assert.ok(isListCatalog(s));for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.equal(html.includes('data-catalog-row-search'),s.specTables.reduce((n,t)=>n+t.rows.length,0)>=10);assert.match(html,/data-catalog-select/);assert.match(html,/data-copy-code/);assert.equal(html.includes('data-group-jump'),s.specTables.length>=2);assert.match(html,/data-selection-bar/);assert.match(html,new RegExp(lang==='ru'?'Каталожные номера':'Catalog numbers'));for(const f of s.features)assert.notEqual(f.title[lang],f.text[lang]);for(const table of s.specTables){if(table.description?.[lang])assert.ok(html.includes(escapeHtml(table.description[lang])));}}}const scopes=drafts.find(s=>s.slug==='conmed-arthroscopes');assert.ok(scopes.specTables.some(t=>t.keyParameters?.some(p=>p.value.en==='152 mm')));assert.equal(scopes.specTables.length,5);});
test('Related draft previews retain links while public indexes expose only approved systems',async()=>{for(const slug of ['conmed-arthroscopes','sheath-and-bridge-systems','cannulas']){const s={...structuredClone(drafts.find(s=>s.slug===slug)),status:'draft'};await prepareSystem(s,all);assert.equal(s.relatedSystems.length,4);assert.deepEqual(s.relatedSystems.slice(0,2).map(r=>r.slug),s.relatedSystemSlugs);}const index=JSON.parse(await fs.readFile('dist/catalog-index.json'));for(const s of drafts)assert.equal(index.some(x=>x.brand===s.brand&&x.slug===s.slug),s.status==='published');});
test('Cross-system selection retains codes verbatim, quantities and bilingual names; malformed data is ignored',()=>{const items=[{id:'conmed:a:0',name:{ru:'Артроскоп',en:'Arthroscope'},codes:['T4907','IM8120'],quantity:3},{id:'conmed:b:0',name:{ru:'Канюля',en:'Cannula'},codes:['OC4601'],quantity:2}];const storage={getItem:key=>key===SELECTION_KEY?JSON.stringify(items):null};assert.deepEqual(readSelection(storage),items);assert.match(selectionMessage(items,'ru','Запрос'),/Артроскоп — T4907 \/ IM8120 × 3/);assert.match(selectionMessage(items,'en','Inquiry'),/Cannula — OC4601 × 2/);assert.deepEqual(validSelection([{id:'x',codes:['T4907']}]),[]);assert.deepEqual(readSelection({getItem:()=>'{bad'}),[]);});

test('List polish keeps short distinct taglines, resolved specialties and catalog documents',async()=>{
 for(const source of drafts){
  const s=await prepareSystem(structuredClone(source),all);
  assert.equal(s.review.flags.some(f=>f.code==='specialty-review'),false);
  assert.ok(s.review.resolvedFlags.some(f=>f.code==='specialty-review'&&f.status==='resolved'));
  const expected=['conmed-arthroscopes','sheath-and-bridge-systems','cannulas'].includes(s.slug)?['orthopedics','sports']:['uhd-laparoscopes','hd-laparoscopes'].includes(s.slug)?['surgery']:['surgery','orthopedics','sports'];
  assert.deepEqual(s.specialty,expected);
  assert.deepEqual(separateListComponents(s,s.components,s.specTables),[]);
  for(const lang of ['ru','en']){
   assert.ok(s.shortDescription[lang].split(/\s+/).length<=12);
   assert.notEqual(s.shortDescription[lang],s.description[lang]);
   const html=renderSystem(s,lang);
   assert.ok(!html.includes('data-section-tab="components"'));
   assert.ok(!html.includes('data-section="components"'));
   assert.ok(html.includes(s.catalogTitle[lang]));
   assert.ok(html.includes(`data-open-pdf="${s.sourcePdf}"`));
   assert.ok(html.includes(`data-pdf-page="${s.sourcePages[0]}"`));
   assert.ok(html.includes((lang==='ru'?'Открыть на стр.':'Open at page')+' '+s.sourcePages[0]));
   assert.ok(!/<p>\s*·/.test(html));
   assert.ok(html.includes(s.documentMeta.sizeLabel));
  }
 }
});
test('List components retain additional items and images, and small-system controls obey boundaries',()=>{
 const s=drafts.find(s=>s.slug==='camera-systems');
 const extra={name:{ru:'Дополнительный компонент',en:'Additional component'},refCodes:['EXTRA'],image:'/images/extra.webp'};
 assert.deepEqual(separateListComponents(s,[...s.components,extra],s.specTables),[extra]);
 const uniqueImage={...s.components[0],image:'/images/another-angle.webp'};
 assert.deepEqual(separateListComponents(s,[uniqueImage],s.specTables),[uniqueImage]);
 const html=renderSystem(s);
 assert.ok(html.includes('lc-layout-single'));
 assert.ok(!html.includes('class="lc-sidebar"'));
 assert.ok(!html.includes('data-group-jump'));
 assert.ok(!html.includes('data-catalog-row-search'));
 const table=s.specTables[0],ten={...s,specTables:[{...table,rows:Array.from({length:10},()=>table.rows[0])}]};
 assert.ok(renderSystem(ten).includes('data-catalog-row-search'));
 assert.ok(!renderSystem(ten).includes('data-group-jump'));
 const nine={...s,specTables:[{...table,rows:Array.from({length:9},()=>table.rows[0])}]};
 assert.ok(!renderSystem(nine).includes('data-catalog-row-search'));
});

test('Future list drafts never repeat their overview or put long copy in the hero',()=>{const source=drafts[0];for(const lang of ['ru','en']){const s={...source,shortDescription:source.description};const html=renderSystem(s,lang),lead=html.match(/<p class="sp-lead">(.*?)<\/p>/s)[1];assert.ok(lead.split(/\s+/).length<=12);assert.ok(!lead.includes(source.description[lang]));}});

test('CONMED publication follows the flag audit without exposing real unresolved issues',async()=>{const audit=JSON.parse(await fs.readFile('reports/conmed/flag-audit/report.json'));assert.equal(audit.resolvedFlagCount,24);assert.equal(audit.openFlagCount,0);assert.equal(audit.published.length,11);for(const s of drafts){assert.equal(s.status,audit.published.includes(s.slug)?'published':'draft');assert.equal(s.review.flags.length,0);}const search=await fs.readFile('dist/search-index.json','utf8');assert.ok(!search.includes('Source PDF typo'));assert.ok(!search.includes('verificationStatus'));for(const slug of ['cannulas','looking-glass'])assert.ok(JSON.parse(search).items.some(item=>item.id==='conmed/'+slug));});

test('Final source corrections preserve codes, isolate internal notes and render the missing cannula number honestly',async()=>{const glass=drafts.find(s=>s.slug==='looking-glass'),cannulas=drafts.find(s=>s.slug==='cannulas');assert.equal(glass.status,'published');assert.equal(cannulas.status,'published');const row=glass.specTables.flatMap(t=>t.rows).find(r=>r[1]==='AVELG52');assert.deepEqual(row[0],{ru:'Адаптер ELG ACMI',en:'ELG ACMI Adapter'});assert.deepEqual(glass.components.find(c=>c.refCodes.includes('AVELG52')).name,row[0]);const pressure=cannulas.specTables.find(t=>t.id==='pressure-sensing-cannula');assert.equal(pressure.rows[1][1],'');assert.equal(pressure.rows[1][2],'83234');assert.equal(pressure.cellNotes[0].row,2);assert.equal(pressure.cellNotes[0].column,2);for(const lang of ['ru','en']){const html=renderSystem(cannulas,lang);assert.ok(html.includes('<span>—</span>'));assert.ok(!html.includes(pressure.cellNotes[0].text[lang]));assert.ok(!html.includes('data-copy-code="—"'));const glassHTML=renderSystem(glass,lang);assert.ok(glassHTML.includes(row[0][lang]));assert.ok(!glassHTML.includes('Source PDF typo'));assert.ok(!glassHTML.includes('A cml'));}const report=JSON.parse(await fs.readFile('reports/conmed/flag-audit/report.json'));assert.equal(report.sourceCatalogCorrections.length,2);assert.equal(report.sourceCatalogCorrections[0].internalNote,"Source PDF typo 'A cml' corrected to ACMI");const publicSearch=await fs.readFile('dist/search-index.json','utf8');assert.ok(!publicSearch.includes('A cml'));assert.ok(!publicSearch.includes('Source PDF typo'));});
