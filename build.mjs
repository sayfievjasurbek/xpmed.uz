import {buildDiscovery} from './src/discovery-data.mjs';
import {loadAboutData, clientLogo, certificateThumb, certificateDocument} from './src/about-sections.mjs';
import {publicProductContent} from './src/public-product-content.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadSystems, listing, legacyListing, systemRoute, prepareSystem } from './src/catalog-data.mjs';
import { copyFile, cp, mkdir, open, readdir, readFile, writeFile, rm, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execSync } from 'node:child_process';
import { render } from './src/render.mjs';
import { renderCatalogTileArray,categoryImageProduct,categoryThumbnailPath } from './src/catalog.mjs';
import {createCanvas,loadImage} from '@napi-rs/canvas';
import { catalogSlugs, catalogRoute, homeRoute } from './src/navigation.mjs';
import ru from './src/i18n/ru.mjs';
import en from './src/i18n/en.mjs';
import {areaKeys,clinicalAreas,parseTaxonomyScope} from './src/clinical-taxonomy.mjs';
import {legacyCategoryAreas} from './src/catalog-engine.js';
import {existsSync} from 'node:fs';
import {ACADEMY_IMAGES} from './src/academy-media.mjs';

// The public/catalogs/<brand>/<name>/source.pdf copies are byte-identical to the
// originals in catalogs-source/, so only the originals are in version control.
// Restore any that are missing before anything reads them, which keeps a fresh
// clone buildable. scripts/import-catalog.py writes the same copies.
//
// Three originals are over 50 MB and live in Git LFS. Vercel clones without
// fetching LFS, so on a deploy those paths hold a 134-byte pointer instead of a
// PDF; copying one through produced "InvalidPDFException: Invalid PDF
// structure" the moment pdf.js opened it. When a pointer is found the real
// object is pulled from media.githubusercontent.com, which serves LFS content
// for public repositories without authentication, and verified against the
// sha256 and byte count the pointer declares.
{
  const slug = stem => stem.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 100);
  const sourceRoot = new URL('./catalogs-source/', import.meta.url);
  const LFS_POINTER = 'version https://git-lfs.github.com/spec/v1';

  const repoSlug = () => {
    const {VERCEL_GIT_REPO_OWNER: owner, VERCEL_GIT_REPO_SLUG: repo} = process.env;
    if (owner && repo) return `${owner}/${repo}`;
    try {
      const remote = execSync('git remote get-url origin', {encoding: 'utf8'}).trim();
      return remote.replace(/^.*github\.com[:/]/, '').replace(/\.git$/, '');
    } catch { return null; }
  };

  async function resolvePointer(file, relative) {
    const text = (await readFile(file)).toString('latin1');
    if (!text.startsWith(LFS_POINTER)) return null;          // a real file already
    const oid = text.match(/^oid sha256:([0-9a-f]{64})$/m)?.[1];
    const size = Number(text.match(/^size (\d+)$/m)?.[1]);
    const slugged = repoSlug();
    if (!oid || !size || !slugged) throw Error(`${relative} is a Git LFS pointer and cannot be resolved (repo unknown)`);
    const ref = process.env.VERCEL_GIT_COMMIT_SHA || process.env.VERCEL_GIT_COMMIT_REF || 'main';
    const url = `https://media.githubusercontent.com/media/${slugged}/${ref}/${relative.split('/').map(encodeURIComponent).join('/')}`;
    const response = await fetch(url);
    if (!response.ok) throw Error(`${relative}: Git LFS object fetch failed, ${response.status} from ${url}`);
    const bytes = Buffer.from(await response.arrayBuffer());
    if (bytes.length !== size) throw Error(`${relative}: expected ${size} bytes from LFS, received ${bytes.length}`);
    const digest = createHash('sha256').update(bytes).digest('hex');
    if (digest !== oid) throw Error(`${relative}: LFS sha256 mismatch, expected ${oid}, received ${digest}`);
    console.log(`Fetched ${relative} from Git LFS (${(size / 1048576).toFixed(0)} MB)`);
    return bytes;
  }

  for (const brand of (await readdir(sourceRoot, {withFileTypes: true})).filter(entry => entry.isDirectory())) {
    for (const name of (await readdir(new URL(brand.name + '/', sourceRoot))).filter(file => file.toLowerCase().endsWith('.pdf'))) {
      const relative = `catalogs-source/${brand.name}/${name}`;
      const original = new URL(`${brand.name}/${name}`, sourceRoot);
      const copy = new URL(`./public/catalogs/${brand.name}/${slug(name.replace(/\.pdf$/i, ''))}/source.pdf`, import.meta.url);

      // A pointer in the checkout is replaced in place, so both paths end up real.
      const resolved = await resolvePointer(original, relative);
      if (resolved) await writeFile(original, resolved);

      try { await stat(copy); } catch {
        await mkdir(new URL('.', copy), {recursive: true});
        await copyFile(original, copy);
        console.log(`Restored ${brand.name}/${name} into public/catalogs/`);
      }

      // Fail here, naming the file, rather than inside pdf.js later.
      const head = Buffer.alloc(5);
      const handle = await open(copy);
      try { await handle.read(head, 0, 5, 0); } finally { await handle.close(); }
      if (head.toString('latin1') !== '%PDF-') throw Error(`${copy.pathname} is not a PDF (starts with ${JSON.stringify(head.toString('latin1'))})`);
    }
  }
}

const source = new URL('./src/', import.meta.url);
const output = new URL('./dist/', import.meta.url);

function translationKeys(value, prefix = '') {
  return Object.entries(value).flatMap(([key, entry]) => {
    const path = prefix + key;
    if (typeof entry === 'object') return translationKeys(entry, path + '.');
    return path + ':' + typeof entry;
  }).sort();
}

if (translationKeys(ru).join('\n') !== translationKeys(en).join('\n')) {
  throw new Error('Russian and English must define the same translation keys.');
}

const systems = (await loadSystems()).filter(s => s.status === 'published').map(publicProductContent);
const index = systems.map(listing);
const products = index.map(legacyListing);
// catalogSlugs is shared with the page renderer, and catalogRoute() reads it,
// so it must not be mutated here. A new brand is a deliberate one-line edit in
// src/navigation.mjs; until then the build stops rather than emitting /catalog/undefined/.
for(const item of index)if(!['unassigned','unspecified'].includes(item.brand)&&!Object.hasOwn(catalogSlugs,item.listingBrand))
 throw new Error(`Brand "${item.listingBrand}" has no catalog scope. Add it to catalogSlugs in src/navigation.mjs.`);
// Recreate generated output so unpublishing cannot leave stale detail pages or assets.
await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
await writeFile(new URL('catalog-index.json', output), JSON.stringify(index));

// Category cards use small derivatives so the catalog never downloads full-size source renders above the fold.
const thumbs=new Map();
const taxonomyScopes=areaKeys.flatMap(area=>[area,...clinicalAreas[area].subcategories.map(sub=>area+'/'+sub)]);
const filterScope=(scope,product)=>{const taxonomy=parseTaxonomyScope(scope);return scope==='all'||(scope==='new'?product.isNew:taxonomy?product.area===taxonomy.area&&(!taxonomy.subcategory||product.taxonomySubcategory===taxonomy.subcategory):product.brand===scope);};
for(const scope of ['all','new',...Object.keys(catalogSlugs),...taxonomyScopes]){
  const scoped=products.filter(product=>filterScope(scope,product));
  const taxonomy=parseTaxonomyScope(scope);
  const facet=taxonomy?.area?'taxonomySubcategory':'area';
  for(const category of new Set(scoped.map(product=>product[facet]))){
    const matching=scoped.filter(product=>product[facet]===category);
    if(matching.length) {const selected=categoryImageProduct(category,products,matching);thumbs.set(selected.image,categoryThumbnailPath(selected.image));}
  }
}
await mkdir(new URL('assets/catalog/',output),{recursive:true});
for(const [src,dest] of thumbs){
  const image=await loadImage((src.startsWith('/assets/')?'src':'public')+src);
  const scale=Math.min(1,800/Math.max(image.width,image.height));
  const canvas=createCanvas(Math.round(image.width*scale),Math.round(image.height*scale));
  canvas.getContext('2d').drawImage(image,0,0,canvas.width,canvas.height);
  await writeFile(new URL('.'+dest,output),canvas.toBuffer('image/webp'));
}

const year = new Date().getUTCFullYear();
const translations = { ru, en };

const discovery = await buildDiscovery(systems, translations);
const about = await loadAboutData();
const siteData = {...discovery, ...about};
await writeFile(new URL('catalog-library-index.json', output), JSON.stringify(discovery.catalogs));
await writeFile(new URL('search-index.json', output), JSON.stringify(discovery.search));

const pages = Object.entries(translations).flatMap(([lang, t]) => {
  const alternate = lang === 'ru' ? 'en' : 'ru';
  const otherLanguage = { lang: alternate, t: translations[alternate] };
  return [null, ...Object.keys(catalogSlugs), ...taxonomyScopes, 'library', 'about-page', 'contacts-page', 'brands-page', 'academy-page', 'not-found'].map(async (scope) => {
    const route = scope === 'academy-page' ? homeRoute(lang)+'academy/' : scope === 'about-page' ? homeRoute(lang)+'about/' : scope === 'contacts-page' ? homeRoute(lang)+'contacts/' : scope === 'brands-page' ? homeRoute(lang)+'brands/' : scope === 'not-found' ? homeRoute(lang)+'404/' : scope === 'library' ? homeRoute(lang) + 'catalogs/' : scope ? catalogRoute(lang, scope) : homeRoute(lang);
    const directory = new URL('.' + route, output);
    await mkdir(directory, { recursive: true });
    await writeFile(new URL('index.html', directory), render(lang, t, year, products, scope, otherLanguage, null, siteData));
    // Only catalog listings have a tile grid, and only those with more than one
    // page of products need the rest of the tiles as a separate fragment.
    if(scope && !['library','about-page','contacts-page','brands-page','academy-page','not-found'].includes(scope)){
      const scoped=products.filter(product=>filterScope(scope,product));
      const rest=renderCatalogTileArray(lang,t,scoped,otherLanguage).slice(24);
      if(rest.length)await writeFile(new URL('catalog-products.html',directory),rest.join(''));
    }
  });
});

await Promise.all([
  ...pages,
  ...['styles.css', 'homepage.css', 'catalog.css', 'home.js', 'catalog.js', 'client.js', 'system.css', 'system.js', 'catalog-selection.js', 'catalog-engine.js', 'discovery.css', 'discovery.js', 'pdf-viewer.js', 'academy.css', 'academy.js']
    .map((file) => copyFile(new URL(file, source), new URL(file, output))),
  cp(new URL('./public/images/brands/', import.meta.url), new URL('images/brands/', output), { recursive: true }),
  // Academy photographs and club logos, once content/academy/ has been
  // prepared; the page falls back to XPMED's own photographs until then.
  existsSync(ACADEMY_IMAGES) ? cp(ACADEMY_IMAGES, new URL('images/academy/', output), { recursive: true }) : null,
  cp(new URL('assets/', source), new URL('assets/', output), { recursive: true }),
]);

for(const asset of [...about.clients.map(c=>clientLogo(c.id)),...about.certificates.flatMap(c=>[certificateThumb(c.id),certificateDocument(c.id)])]){
  const target=new URL('.'+asset,output);
  await mkdir(new URL('.',target),{recursive:true});
  await copyFile(path.resolve('public','.'+asset),target);
}

const copiedSystemAssets = new Set();
for (const system of systems) {
  await prepareSystem(system, systems);
  for (const [lang, t] of Object.entries(translations)) {
    system.relatedSystems = system.relatedSystems.map(candidate => ({ ...candidate, url: systemRoute(candidate, lang) }));
    const alternate = lang === 'ru' ? 'en' : 'ru';
    const directory = new URL('.' + systemRoute(system, lang), output);
    await mkdir(directory, { recursive: true });
    await writeFile(new URL('index.html', directory), render(lang, t, year, products, null, { lang: alternate, t: translations[alternate] }, system, siteData));
  }
  // Only assets referenced by published systems are copied. Draft PDFs and page scans stay local.
  const assets = new Set();
  const collect = value => { if (typeof value === 'string' && /^\/(images\/products|catalogs)\//.test(value)) assets.add(value); else if (Array.isArray(value)) value.forEach(collect); else if (value && typeof value === 'object') Object.values(value).forEach(collect); };
  collect(system);
  for (const asset of assets) {
    if (copiedSystemAssets.has(asset)) continue;
    const src = path.resolve('public', '.' + asset);
    if (!src.startsWith(path.resolve('public') + path.sep)) throw Error('Invalid asset path');
    const target = new URL('.' + asset, output);
    await mkdir(new URL('.', target), { recursive: true });
    await copyFile(src, target);
    copiedSystemAssets.add(asset);
  }
}
const routes = new Set();
for (const lang of ['ru','en']) {
  routes.add(homeRoute(lang));
  for (const scope of Object.keys(catalogSlugs)) routes.add(catalogRoute(lang,scope));
  for (const extra of ['catalogs/','about/','contacts/','brands/','academy/']) routes.add(homeRoute(lang)+extra);
  for(const scope of taxonomyScopes)routes.add(catalogRoute(lang,scope));
  for (const system of systems) routes.add(systemRoute(system,lang));
}
const xml = text => String(text).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
await writeFile(new URL('sitemap.xml',output),'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+[...routes].sort().map(route=>`  <url><loc>${xml('https://www.xpmed.uz'+route)}</loc></url>`).join('\n')+'\n</urlset>\n');
await writeFile(new URL('robots.txt',output),'User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: https://www.xpmed.uz/sitemap.xml\n');
await copyFile(new URL('404/index.html',output),new URL('404.html',output));
const oldRoutes = new Map([
 ['/o-nas/','/about/'],['/about-us/','/en/about/'],['/kontakty/','/contacts/'],['/contacts/','/contacts/'],['/homepage/','/en/'],
]);
for(const system of systems)for(const source of system.legacySources||[]){
 if(!source.url)continue;
 try { const old=new URL(source.url); if(old.hostname==='xpmed.uz'||old.hostname==='www.xpmed.uz') oldRoutes.set(old.pathname,systemRoute(system,source.language==='en'?'en':'ru')); } catch {}
}
// A renamed system keeps its old URL working in both languages.
for(const system of systems)for(const previous of system.previousSlugs||[])for(const lang of ['ru','en'])
 oldRoutes.set((lang==='en'?'/en':'')+'/catalog/'+system.brand+'/'+previous+'/',systemRoute(system,lang));
for(const [legacy,area] of Object.entries(legacyCategoryAreas)){
 oldRoutes.set('/catalog/?category='+legacy,'/catalog/'+area+'/');
 oldRoutes.set('/en/catalog/?category='+legacy,'/en/catalog/'+area+'/');
 for(const brand of ['double-medical','conmed','synimed','biotechni','ge-healthcare','spinendos']){
  oldRoutes.set('/catalog/'+brand+'/?category='+legacy,'/catalog/'+area+'/');
  oldRoutes.set('/en/catalog/'+brand+'/?category='+legacy,'/en/catalog/'+area+'/');
 }
}
await writeFile(new URL('_redirects',output),[...oldRoutes].filter(([from,to])=>from!==to).map(([from,to])=>`${from} ${to} 301`).join('\n')+'\n');
console.log(`Built ${systems.length} published systems; drafts and admin excluded.`);

await mkdir(new URL('vendor/pdfjs/',output),{recursive:true});
for(const file of ['pdf.min.mjs','pdf.worker.min.mjs'])await copyFile('node_modules/pdfjs-dist/build/'+file,new URL('vendor/pdfjs/'+file,output));
for(const dir of ['cmaps','standard_fonts','wasm'])await cp('node_modules/pdfjs-dist/'+dir,new URL('vendor/pdfjs/'+dir,output),{recursive:true});
await copyFile('node_modules/fuse.js/dist/fuse.min.mjs',new URL('vendor/fuse.mjs',output));
await copyFile('node_modules/pdfjs-dist/LICENSE',new URL('vendor/pdfjs/LICENSE',output));
await copyFile('node_modules/fuse.js/LICENSE',new URL('vendor/FUSE-LICENSE',output));

await copyFile(new URL('i18n/discovery.mjs',source),new URL('discovery-i18n.js',output));
