import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems,systemRoute} from '../src/catalog-data.mjs';
import {areaKeys,areaRoute,classifySystem,clinicalAreas} from '../src/clinical-taxonomy.mjs';

const systems=(await loadSystems()).filter(system=>system.status==='published');

test('Every published system belongs to exactly one of eight clinical areas, a subcategory and a product type',()=>{
  assert.equal(areaKeys.length,8);
  for(const system of systems){
    const taxonomy=classifySystem(system);
    assert(areaKeys.includes(taxonomy.area),system.slug);
    assert(clinicalAreas[taxonomy.area].subcategories.includes(taxonomy.subcategory),system.slug);
    assert(['implants','instruments','equipment'].includes(taxonomy.type),system.slug);
  }
  assert.equal(systems.length,814);
});

test('Area, subcategory and brand pages are bilingual and use clean routes',async()=>{
  for(const lang of ['ru','en'])for(const area of areaKeys){
    await fs.access('dist'+areaRoute(lang,area)+'index.html');
    for(const subcategory of clinicalAreas[area].subcategories){
      const count=systems.filter(system=>{const taxonomy=classifySystem(system);return taxonomy.area===area&&taxonomy.subcategory===subcategory}).length;
      if(count)await fs.access('dist'+areaRoute(lang,area,subcategory)+'index.html');
    }
  }
  for(const path of ['dist/brands/index.html','dist/en/brands/index.html'])await fs.access(path);
});

test('Mega-menu is area-led, counted and product breadcrumbs follow the taxonomy',async()=>{
  for(const [lang,prefix] of [['ru','dist'],['en','dist/en']]){
    const home=await fs.readFile(prefix+'/index.html','utf8');
    assert.equal((home.match(/role="tab" aria-controls="area-panel-/g)||[]).length,8);
    assert.equal((home.match(/class="area-menu__header"/g)||[]).length,8);
    assert(home.includes(lang==='ru'?'73 продукта':'73 products'));
    assert(home.includes((lang==='ru'?'Каталоги PDF':'PDF catalogs')));
    assert(home.includes((lang==='ru'?'Бренды':'Brands')));
    const product=systems.find(system=>system.slug==='cynthia-knee-system');
    const html=await fs.readFile('dist'+systemRoute(product,lang)+'index.html','utf8');
    const taxonomy=classifySystem(product);
    assert(html.includes(areaRoute(lang,taxonomy.area)));
    assert(html.includes(areaRoute(lang,taxonomy.area,taxonomy.subcategory)));
  }
});

test('Legacy category query URLs have permanent redirects to the clinical areas',async()=>{
  const redirects=await fs.readFile('dist/_redirects','utf8');
  for(const [legacy,area] of [['trauma-implants','trauma'],['spine-implants','spine'],['shoulder-arthroscopy','sports-arthroscopy'],['hall-powered-instruments','powered-instruments']]){
    assert(redirects.includes(`/catalog/?category=${legacy} /catalog/${area}/ 301`));
    assert(redirects.includes(`/en/catalog/?category=${legacy} /en/catalog/${area}/ 301`));
  }
});
