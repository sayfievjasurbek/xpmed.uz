import {isSelfComponent} from './system-layout.mjs';
import {isListCatalog,separateListComponents} from './list-catalog.mjs';
import {prepareCatalogCover} from './catalog-cover.mjs';
import {catalogSearchText} from './catalog-engine.js';
import path from 'node:path';
import { readFile, stat, mkdir, writeFile } from 'node:fs/promises';
import Fuse from 'fuse.js';
import { systemRoute } from './catalog-data.mjs';
import { brandName } from './i18n/discovery.mjs';
import {classifySystem,taxonomyLabel} from './clinical-taxonomy.mjs';
export const searchKeys=[{name:'name.ru',weight:4},{name:'name.en',weight:4},{name:'refCodes',weight:4},{name:'brandLabel',weight:2},'description.ru','description.en','categoryLabel.ru','categoryLabel.en','keywords'];
const flatten=v=>typeof v==='string'||typeof v==='number'?String(v):Array.isArray(v)?v.map(flatten).join(' '):v&&typeof v==='object'?Object.values(v).map(flatten).join(' '):'';
export async function buildDiscovery(systems,translations){
 const catalogs=[];
 const systemCatalogs={}; const items=[];
 for(const s of systems.filter(s=>s.status==='published')){
  const taxonomy=classifySystem(s);
  const categoryLabel=Object.fromEntries(['ru','en'].map(l=>[l,taxonomyLabel(l,taxonomy.area)]));
  const base={brand:s.brand,brandLabel:brandName(s.brand),categoryLabel,thumbnail:s.heroImage};
  const keywords=catalogSearchText(s);
  items.push({...base,id:s.brand+'/'+s.slug,group:'systems',name:s.name,description:s.description,refCodes:s.refCodes,keywords,url:systemRoute(s),url_en:systemRoute(s,'en')});
  const components=new Map();
  for(const c of s.components||[])components.set(c.id||flatten(c.name),{c,variant:s.variants?.find(v=>v.componentIds?.includes(c.id))?.id});
  for(const v of s.variants||[])for(const c of v.components||[])components.set(c.id||flatten(c.name),{c,variant:v.id});
  for(const [id,{c,variant}]of components){const section=components.size===1&&isSelfComponent(s,c)?'overview':'components';const tableOnly=isListCatalog(s)&&!separateListComponents(s,[c],s.specTables||[]).length;const anchor=tableOnly?(c.groupId?'catalog-group-'+(variant||'default')+'-'+c.groupId:'sizes-'+(variant||'default')):section+'-'+(variant||'default');const suffix=(variant?'?variant='+encodeURIComponent(variant):'')+'#'+anchor;items.push({...base,id:s.brand+'/'+s.slug+'/'+id,group:'components',name:c.name,description:c.description||s.shortDescription,thumbnail:c.image||s.heroImage,refCodes:c.refCodes||[],keywords:catalogSearchText({components:[c],specTables:[...(s.specTables||[]).filter(t=>t.componentId===c.id),...(s.variants||[]).flatMap(v=>v.specTables||[]).filter(t=>t.componentId===c.id)]}),url:systemRoute(s)+suffix,url_en:systemRoute(s,'en')+suffix});}
  for(const source of [...(s.sourcePdf?[s]:[]),...(s.catalogImports||[])]){
  let catalog=catalogs.find(c=>c.file===source.sourcePdf);
  if(!catalog){
   const {getDocument}=await import('pdfjs-dist/legacy/build/pdf.mjs');
   const catalogId=s.brand+'--'+source.sourcePdf.split('/').slice(3).join('--').replace(/\.pdf$/i,'').replace(/--source$/,'');
   const bytes=await readFile('public'+source.sourcePdf);const task=getDocument({data:new Uint8Array(bytes),isEvalSupported:false,cMapUrl:path.resolve('node_modules/pdfjs-dist/cmaps')+'/',cMapPacked:true,standardFontDataUrl:path.resolve('node_modules/pdfjs-dist/standard_fonts')+'/',wasmUrl:path.resolve('node_modules/pdfjs-dist/wasm')+'/'});const pdf=await task.promise;
   const {coverImage,coverCrop}=await prepareCatalogCover(pdf,{...s,...source},catalogId);
   catalog={id:catalogId,brand:s.brand,brandLabel:brandName(s.brand),file:source.sourcePdf,viewOnly:source.viewOnly===true,title:source.catalogTitle||s.name,edition:source.catalogEdition||'',pages:pdf.numPages,bytes:(await stat('public'+source.sourcePdf)).size,cover:coverImage,coverImage,coverCrop,systems:[],searchText:''};await pdf.destroy();catalogs.push(catalog);
  }
  catalog.searchText += ' '+flatten([s.name,s.description,keywords]);
  // The catalog a product was imported from, so the catalog page can be
  // narrowed to one PDF from the library card.
  (systemCatalogs[s.slug] ??= []).push(catalog.id);
  const link={name:s.name,url:systemRoute(s)+(source.variantId?'?variant='+encodeURIComponent(source.variantId):''),url_en:systemRoute(s,'en')+(source.variantId?'?variant='+encodeURIComponent(source.variantId):'')};
  if(!catalog.systems.some(existing=>existing.url===link.url))catalog.systems.push(link);
  }
 }
 for(const c of catalogs)items.push({id:c.id,group:'catalogs',name:c.title,brand:c.brand,brandLabel:c.brandLabel,categoryLabel:{ru:'Каталоги',en:'Catalogs'},thumbnail:c.cover,keywords:flatten([c.systems,c.searchText]),refCodes:[],url:'/catalogs/?catalog='+encodeURIComponent(c.id),url_en:'/en/catalogs/?catalog='+encodeURIComponent(c.id)});
 return {catalogs:catalogs.map(({searchText,...catalog})=>catalog),systemCatalogs,search:{items,index:Fuse.createIndex(searchKeys,items).toJSON(),keys:searchKeys}};
}
