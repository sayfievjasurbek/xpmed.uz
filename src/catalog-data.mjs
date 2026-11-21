import {selectRelatedSystems} from './related-systems.mjs';
import {validateTableSpans} from './system-tables.mjs';
import {normalizeTaxonomy} from './taxonomy.mjs';
import {catalogSearchText} from './catalog-engine.js';
import {classifySystem} from './clinical-taxonomy.mjs';
import {readdir,readFile} from 'node:fs/promises';
import path from 'node:path';
export function normalizeSystem(s){return normalizeTaxonomy({category:'unclassified',subcategory:'',specialty:[],shortDescription:{ru:'',en:''},description:{ru:'',en:''},heroImage:'',imageType:'cutout',gallery:[],variants:[],features:[],hotspots:[],components:[],specTables:[],referenceTables:[],refCodes:[],sourcePdf:null,sourcePages:[],catalogEdition:null,isNew:false,status:'draft',...s});}
export function validateSystem(s){
 const errors=[];
 if(!s||typeof s!=='object'||Array.isArray(s))return ['System must be an object'];
 s=normalizeSystem(s);
 for(const k of ['slug','brand','category'])if(typeof s[k]!=='string'||!s[k])errors.push(k+' is required');
 if(!/^[a-z0-9][a-z0-9-]*$/.test(s.slug||'')||!/^[a-z0-9][a-z0-9-]*$/.test(s.brand||''))errors.push('Unsafe brand or slug');
 const bilingual=(v,p)=>{for(const l of ['ru','en'])if(typeof v?.[l]!=='string')errors.push(p+'.'+l+' must be text');};
 for(const k of ['name','shortDescription','description'])bilingual(s[k],k);
 if(!['draft','published'].includes(s.status))errors.push('Invalid status');
 if(!['cutout','scene'].includes(s.imageType))errors.push('Invalid imageType');
 for(const k of ['specialty','gallery','features','components','specTables','refCodes','sourcePages'])if(!Array.isArray(s[k]))errors.push(k+' must be an array');
 if(s.variants!==undefined&&!Array.isArray(s.variants))errors.push('variants must be an array');
 const table=(t)=>{if(!t||!Array.isArray(t.columns)||!Array.isArray(t.rows))errors.push('Table columns/rows must be arrays');else {let valid=true;for(const r of t.rows)if(!Array.isArray(r)||(t.columns.length>0&&r.length!==t.columns.length)){errors.push('Table row width mismatch');valid=false;}if(valid)errors.push(...validateTableSpans(t));if(t.headerRows){if(!Array.isArray(t.headerRows)||t.headerRows.some(r=>!Array.isArray(r)||r.length!==t.columns.length))errors.push('Table header width mismatch');else errors.push(...validateTableSpans({...t,rows:t.headerRows}));}}};
 const arrays=(a)=>Array.isArray(a)?a:[];
 for(const t of [...arrays(s.specTables),...arrays(s.referenceTables)])table(t);
 for(const v of arrays(s.variants)){bilingual(v.name,'variant.name');for(const t of arrays(v.specTables))table(t);}
 const technique=(value)=>{if(value===undefined)return;const chapters=arrays(value?.chapters);if(!value||(!Array.isArray(value.steps)&&!chapters.length)){errors.push('Surgical technique requires steps or chapters');return;}for(const chapter of chapters){bilingual(chapter.title,'surgicalTechnique.chapter.title');if(!Array.isArray(chapter.steps))errors.push('Chapter steps must be an array');}for(const step of chapters.length?chapters.flatMap(c=>arrays(c.steps)):value.steps){bilingual(step.title,'surgicalTechnique.step.title');bilingual(step.text,'surgicalTechnique.step.text');for(const k of ['images','notes','checklist','tables'])if(step[k]!==undefined&&!Array.isArray(step[k]))errors.push('Surgical technique '+k+' must be an array');for(const t of arrays(step.tables))table(t);}};technique(s.surgicalTechnique);for(const v of arrays(s.variants))technique(v.surgicalTechnique);
 const walk=(v,key='')=>{
   if(typeof v==='string'&&['heroImage','image','src'].includes(key)&&v&&(!/^\/(?:assets|images|catalogs)\/[a-zA-Z0-9_./%\-]+$/.test(v)||v.includes('..')))errors.push('Invalid image path');
   if(key==='sourcePdf'&&v!==null&&typeof v==='string'&&(!/^\/catalogs\/[a-zA-Z0-9_./%\-]+$/.test(v)||v.includes('..')))errors.push('Invalid PDF path');
   if(s.status==='published'&&v&&typeof v==='object'&&typeof v.en==='string'&&v.en.trim()&&typeof v.ru==='string'&&!v.ru.trim())errors.push('Published bilingual prose is missing Russian text');
   if(Array.isArray(v))v.forEach(x=>walk(x,key));else if(v&&typeof v==='object')for(const [k,x]of Object.entries(v))walk(x,k);
 };walk(s);
 if(s.status==='published')for(const l of ['ru','en'])if(!s.name?.[l]?.trim())errors.push('Published name.'+l+' cannot be empty');
 return errors;
}
export async function loadSystems(root='content/products'){
 const result=[];
 for(const brand of (await readdir(root,{withFileTypes:true})).filter(x=>x.isDirectory()).sort((a,b)=>a.name.localeCompare(b.name))){for(const name of (await readdir(path.join(root,brand.name))).filter(x=>x.endsWith('.json')).sort()){
 const s=normalizeSystem(JSON.parse(await readFile(path.join(root,brand.name,name),'utf8')));const errors=validateSystem(s);if(errors.length)throw Error(`${brand.name}/${name}: ${errors.join('; ')}`);if(s.brand!==brand.name||name!==s.slug+'.json')throw Error('System path does not match identity');result.push(s);
 }}return result;
}
export function systemRoute(s,lang='ru'){return (lang==='en'?'/en':'')+'/catalog/'+s.brand+'/'+s.slug+'/';}
export function listing(s){const taxonomy=classifySystem(s);return {id:s.legacyId||s.slug,listingBrand:s.brand==='double-medical'?'double':s.legacyBrand||s.brand,imageDimensions:s.imageDimensions?.[s.heroImage]?{[s.heroImage]:s.imageDimensions[s.heroImage]}:{},searchText:catalogSearchText(s),slug:s.slug,brand:s.brand,category:s.category,subcategory:s.subcategory,subcategories:s.subcategories||[s.subcategory].filter(Boolean),area:taxonomy.area,taxonomySubcategory:taxonomy.subcategory,productType:taxonomy.type,specialty:s.specialty,name:s.name,shortDescription:s.shortDescription,heroImage:s.heroImage,imageType:s.imageType,isNew:s.isNew,publishedAt:s.publishedAt||s.review?.publishedAt||null,refCodes:[...new Set([...s.refCodes,...s.components.flatMap(c=>c.refCodes||[])])],url:systemRoute(s),url_en:systemRoute(s,'en')};}
export function legacyListing(s){return {id:s.legacyId||s.id||s.slug,slug:s.slug,imageDimensions:s.imageDimensions||{},refCodes:s.refCodes||[],searchText:s.searchText||'',brand:s.listingBrand||(s.brand==='double-medical'?'double':s.legacyBrand||s.brand),category:s.category,subcategory:s.subcategory,subcategories:s.subcategories||[s.subcategory].filter(Boolean),area:s.area,taxonomySubcategory:s.taxonomySubcategory,productType:s.productType,specialty:s.specialty,name_ru:s.name.ru,name_en:s.name.en,tagline_ru:s.shortDescription.ru,tagline_en:s.shortDescription.en,description_ru:(s.description||s.shortDescription).ru,description_en:(s.description||s.shortDescription).en,image:s.heroImage,imageType:s.imageType,gallery:s.gallery||[],features:s.features||[],specs:{},documents:[{type:'product-page',ru:systemRoute(s),en:systemRoute(s,'en')}],video:null,isNew:s.isNew,publishedAt:s.publishedAt||null};}

export async function prepareSystem(system, systems = []) {
 if (system.sourcePdf) {
  const {stat} = await import('node:fs/promises');
  try { const info = await stat(path.resolve('public', '.' + system.sourcePdf)); system.documentMeta = {bytes:info.size,sizeLabel:(info.size/1048576).toFixed(1)+' MB',cover:system.documentCover||system.sourcePageImages?.[0]||null}; }
  catch(error) { if(system.status==='published')throw error; }
 }
 for(const source of system.catalogImports||[]){const {stat}=await import('node:fs/promises');const info=await stat(path.resolve('public','.'+source.sourcePdf));source.documentMeta={bytes:info.size,sizeLabel:(info.size/1048576).toFixed(1)+' MB',cover:source.documentCover||source.sourcePageImages?.[0]};}
 system.instrumentSetLinks=systems.filter(candidate=>candidate.brand===system.brand&&['arthroplasty-instrument-sets','spine-instrument-sets','trauma-instrument-sets'].includes(candidate.category)&&(candidate.status==='published'||system.status==='draft')&&(system.relatedSystemSlugs||[]).includes(candidate.slug)).map(candidate=>({name:candidate.name,url:systemRoute(candidate),url_en:systemRoute(candidate,'en')}));
 system.relatedSystems=selectRelatedSystems(system,systems).map(candidate=>({name:candidate.name,shortDescription:candidate.shortDescription,heroImage:candidate.heroImage,imageType:candidate.imageType,imageDimensions:candidate.imageDimensions,brand:candidate.brand,slug:candidate.slug,status:candidate.status}));

 return system;
}
