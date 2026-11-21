import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems} from '../src/catalog-data.mjs';
import {publicProductContent} from '../src/public-product-content.mjs';
import {renderSystem} from '../src/system-page.mjs';

test('Public product presentation removes editorial notices without changing source values or clinical notes',()=>{
 const source={slug:'test',brand:'test',status:'published',name:{ru:'Система',en:'System'},description:{ru:'Описание изделия.\n\nНаименование требует проверки соответствия.',en:'Product description.\n\nThe name requires verification against the product.'},review:{flags:['Internal review required']},specTables:[{title:{ru:'Размеры',en:'Sizes'},unit:'mm',columns:['REF','Size'],rows:[[null,'10'],['REF-1','20']],note:{ru:'Уточняйте у менеджера',en:'Please confirm with your sales representative'},legend:{ru:'● / ○ / × — наличие уточняйте у менеджера',en:'Confirm availability with your manager'},cellNotes:[{row:1,column:1,text:{ru:'Каталожный номер уточняйте у менеджера',en:'Confirm the catalog number with your manager'}}]}],features:[{title:{ru:'Особенность',en:'Feature'},text:{ru:'Описание',en:'Description'},note:{ru:'Не допускайте повреждения компонента.',en:'Avoid damage to the component.'}}]};
 const before=structuredClone(source),published=publicProductContent(source);
 assert.deepEqual(source,before);
 assert.deepEqual(published.specTables[0].rows,source.specTables[0].rows);
 assert.deepEqual(published.review,source.review);
 assert.deepEqual(published.features,source.features);
 assert.deepEqual(published.description,{ru:'Описание изделия.',en:'Product description.'});
 assert.equal(published.specTables[0].note,undefined);
 assert.equal(published.specTables[0].legend,undefined);
 assert.deepEqual(published.specTables[0].cellNotes,[]);
 for(const lang of ['ru','en']){
  const html=renderSystem(source,lang);
  assert.doesNotMatch(html,/менеджер|sales representative|review-flag|Internal review required|требует проверки|requires verification/);
  assert.match(html,/<span>—<\/span>/);
  assert.ok(html.includes(source.features[0].note[lang]));
 }
 const draft={...source,status:'draft'};
 assert.equal(publicProductContent(draft),draft);
 assert.match(renderSystem(draft),/review-flag/);
 assert.match(renderSystem(draft),/Уточняйте у менеджера/);
});

test('All published RU and EN product pages and discovery indexes are free of review and manager notices',async()=>{
 const systems=(await loadSystems()).filter(s=>s.status==='published');
 for(const s of systems)for(const lang of ['ru','en']){
  const html=await fs.readFile(`dist/${lang==='en'?'en/':''}catalog/${s.brand}/${s.slug}/index.html`,'utf8');
  assert.doesNotMatch(html,/требует проверки|requires verification|менеджер|confirm[^<>]{0,100}(?:manager|sales representative)|class="review-flag"|data-review-(?:page|bounds|path)/iu,`${s.slug} ${lang}`);
 }
 for(const file of ['catalog-index.json','search-index.json','catalog-library-index.json']){
  assert.doesNotMatch(await fs.readFile(`dist/${file}`,'utf8'),/уточняйте у менеджера|confirm[^"<>]{0,100}(?:manager|sales representative)/iu,file);
 }
});
