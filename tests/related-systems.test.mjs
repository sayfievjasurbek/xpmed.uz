import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import {selectRelatedSystems}from '../src/related-systems.mjs';import {loadSystems,prepareSystem,systemRoute}from '../src/catalog-data.mjs';import {renderSystem}from '../src/system-page.mjs';
import {areaRoute,classifySystem}from '../src/clinical-taxonomy.mjs';
const base={brand:'a',slug:'current',status:'published',category:'joint',subcategory:'hip',subcategories:['hip']};
const item=(slug,overrides={})=>({...base,slug,subcategory:'other',subcategories:['other'],...overrides});
test('Related ranking fills explicit, subcategory, category and brand in order without duplicates or self',()=>{
 const explicit=item('explicit',{brand:'b',category:'other'}),sub=item('sub',{brand:'c',subcategory:'hip',subcategories:['hip']}),category=item('category'),brand=item('brand',{category:'other'}),hidden=item('draft',{status:'draft'});
 const current={...base,relatedSystemSlugs:['a/current','b/explicit','b/explicit']};
 assert.deepEqual(selectRelatedSystems(current,[current,brand,category,sub,hidden,explicit]).map(s=>s.slug),['explicit','sub','category','brand']);
 assert.equal(selectRelatedSystems({...base,relatedSystemSlugs:['missing']},[base]).length,0);
 assert.deepEqual(selectRelatedSystems(base,[base,brand,brand]).map(s=>s.slug),['brand']);
});
test('Explicit editorial order, secondary subcategories and public draft exclusion are preserved',()=>{
 const a=item('one'),b=item('two'),sub=item('secondary',{brand:'b',category:'other',subcategory:'knee',subcategories:['knee','hip']});
 assert.deepEqual(selectRelatedSystems({...base,relatedSystemSlugs:['two','one']},[a,b,sub]).map(s=>s.slug),['two','one','secondary']);
 assert.equal(selectRelatedSystems(base,[item('draft',{status:'draft'})]).length,0);
 assert.equal(selectRelatedSystems({...base,status:'draft'},[item('draft',{status:'draft'})]).length,1);
});
test('Requested system pages have four localized cards and a category-filtered catalog link',async()=>{
 const systems=await loadSystems();
 for(const slug of ['anty-f-series','cynthia-knee-system','angel-shoulder-system','system-5000']){
  const s=await prepareSystem(structuredClone(systems.find(s=>s.slug===slug)),systems);assert.equal(s.relatedSystems.length,4);assert.ok(s.relatedSystems.every(r=>r.slug!==s.slug||r.brand!==s.brand));
  for(const lang of ['ru','en']){const html=await fs.readFile('dist'+systemRoute(s,lang)+'index.html','utf8');const section=html.slice(html.indexOf('class="sp-section sp-dark sp-related'),html.indexOf('</section>',html.indexOf('class="sp-section sp-dark sp-related')));assert.equal((section.match(/class="sp-related-tile"/g)||[]).length,4);assert.equal((section.match(/class="sp-related-caption"/g)||[]).length,4);assert.ok(section.includes(areaRoute(lang,classifySystem(s).area)));assert.ok(section.includes(lang==='ru'?'Все системы категории':'All systems in this category'));for(const r of s.relatedSystems)assert.ok(section.includes(systemRoute(r,lang)));}
 }
});
test('Empty related sections disappear and sparse selections stay limited to eligible systems',()=>{
 const s={...base,name:{ru:'Система',en:'System'},heroImage:'/images/test.webp',features:[],components:[],specTables:[],relatedSystems:[]};assert.ok(!renderSystem(s).includes('sp-related-grid'));
 const sparse=selectRelatedSystems(s,[s,item('eligible'),item('unrelated',{brand:'b',category:'other'})]);assert.equal(sparse.length,1);s.relatedSystems=sparse.map(r=>({...r,name:{ru:'Связанная',en:'Related'},heroImage:'/images/test.webp',url:systemRoute(r)}));assert.equal((renderSystem(s).match(/class="sp-related-tile"/g)||[]).length,1);
});
