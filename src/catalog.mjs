import {brandName} from './i18n/discovery.mjs';
import {discovery} from './i18n/discovery.mjs';
import { catalogRoute, homeRoute } from './navigation.mjs';
import { escape } from './html.mjs';
import { icon } from './icons.mjs';
import { brandMedia } from './brand-media.mjs';
import { renderProductTile, renderTileImage } from './product-tile.mjs';
import {createHash} from 'node:crypto';
import {areaRoute,clinicalAreas,parseTaxonomyScope,productTypeLabels,subcategoryLabels,taxonomyLabel} from './clinical-taxonomy.mjs';

const bannerImages = {
  all: 'hero-devices',
  double: 'hero-devices',
  conmed: 'operating-room',
  synimed: 'synicem',
  new: 'surgery-suite',
};

const categoryImages = {
  'joint-replacement': 'pbg',
  trauma: 'uhn',
  spine: 'tina',
  'sports-medicine': 'sequent',
  arthroscopy: 'anchor',
  'bone-cements': 'synicem',
};
export const categoryImageProduct=(key,products,matching)=>products.find(product=>product.id===categoryImages[key]&&product.image)??matching.find(product=>product.image)??matching[0];
export const categoryThumbnailPath=image=>'/assets/catalog/category-'+createHash('sha1').update(image).digest('hex').slice(0,12)+'.webp';

const introProducts = { double: 'pbg', conmed: 'sequent', synimed: 'cannula' };

export function catalogHeading(scope, t) {
  const taxonomy=parseTaxonomyScope(scope);
  if(taxonomy)return taxonomyLabel(t.home==='Home'?'en':'ru',taxonomy.subcategory||taxonomy.area);
  if (scope === 'all') return t.catalog.title;
  if (scope === 'new') return t.catalog.newTitle;
  return t.labels[scope]||brandName(scope);
}

export function catalogDescription(scope, t) {
  const taxonomy=parseTaxonomyScope(scope);
  if(taxonomy)return clinicalAreas[taxonomy.area].description[t.home==='Home'?'en':'ru'];
  if (scope === 'all') return t.catalog.allDescription;
  if (scope === 'new') return t.catalog.newDescription;
  return t.homepage.features[scope]?.description||t.catalog.allDescription;
}

export function renderCatalogTileArray(lang,t,products,otherLanguage){
  const copy=t.catalog;
  const brandLabels={...t.labels,...copy.extraBrands};
  return products.map(product=>{
    const {brand,specialty}=product;
    const search=[product['name_'+lang],product['name_'+otherLanguage.lang],product['tagline_'+lang],product.searchText,...(product.refCodes||[]),product['tagline_'+otherLanguage.lang],product['description_'+lang],brandLabels[brand]??(brand==='unspecified'?'':brand),taxonomyLabel(lang,product.area),taxonomyLabel(otherLanguage.lang,product.area),taxonomyLabel(lang,product.taxonomySubcategory),taxonomyLabel(otherLanguage.lang,product.taxonomySubcategory),productTypeLabels[product.productType]?.[lang],...specialty.flatMap(key=>[t.labels[key],otherLanguage.t.labels[key]])].join(' ');
    return renderProductTile(product,lang,t.homepage.learnMore,search);
  });
}

export function renderCatalog(lang, t, scope, products, otherLanguage) {
  const copy = t.catalog;
  const d = discovery[lang];
  const heading = catalogHeading(scope, t);
  const description = catalogDescription(scope, t);
  const taxonomyScope=parseTaxonomyScope(scope);
  const brandPage = !['all','new'].includes(scope)&&!taxonomyScope;
  const hasBrandIntro=Object.hasOwn(copy.brandIntro,scope);
  const route = catalogRoute(lang, scope);
  const scopedProducts = products.filter((product) => (
    scope === 'all' || (scope === 'new' ? product.isNew : taxonomyScope ? product.area===taxonomyScope.area&&(!taxonomyScope.subcategory||product.taxonomySubcategory===taxonomyScope.subcategory) : product.brand === scope)
  ));

  const introProduct = scopedProducts.find(({ id }) => id === introProducts[scope]) ?? scopedProducts[0];
  const categoryFacet=taxonomyScope?.area?'taxonomySubcategory':'area';
  const categories = [...new Set(scopedProducts.map(p=>p[categoryFacet]))].flatMap(key => {
    const matching = scopedProducts.filter((product) => product[categoryFacet] === key);
    if (!matching.length) return [];
    const imageProduct = categoryImageProduct(key,products,matching);
    const target=taxonomyScope?.area?areaRoute(lang,taxonomyScope.area,key):areaRoute(lang,key);
    return `<a class="category-tile" data-category-tile="${key}" data-facet="${taxonomyScope?.area?'subcategory':'area'}" href="${escape(target)}">
      ${renderTileImage({...imageProduct,image:categoryThumbnailPath(imageProduct.image),imageDimensions:{}}, 'category-tile__image')}
      <div class="category-tile__caption">
        <div><h3>${escape(taxonomyLabel(lang,key))}</h3><p>${escape(copy.categoryCount(matching.length))}</p></div>
        ${icon('circleArrow')}
      </div>
    </a>`;
  });

  const brandLabels = { ...t.labels, ...copy.extraBrands };
  const facets = [
    ['area', copy.area, Object.fromEntries(Object.keys(clinicalAreas).map(key=>[key,taxonomyLabel(lang,key)])), scopedProducts.map(({area})=>area)],
    ['subcategory', d.subcategory, Object.fromEntries(Object.keys(subcategoryLabels).map(key=>[key,taxonomyLabel(lang,key)])), scopedProducts.map(p=>p.taxonomySubcategory)],
    ['brand', copy.brand, brandLabels,scopedProducts.map(({ brand }) => brand).filter((brand) => brand && !['unspecified','unassigned'].includes(brand))],
    ['type',copy.type,Object.fromEntries(Object.keys(productTypeLabels).map(key=>[key,productTypeLabels[key][lang]])),scopedProducts.map(p=>p.productType)],
    ['specialty', copy.specialty, t.labels, scopedProducts.flatMap(({ specialty }) => specialty)],
  ];
  const checkboxes = facets.filter(([, , , values]) => new Set(values).size>1).map(([key, title, labels, values]) => `<fieldset>
    <legend>${escape(title)}</legend>
    ${[...new Set(values)].map((value) => `<label class="catalog-option"><input type="checkbox"
      name="${key}" value="${escape(value)}"><span>${escape(labels[value] ?? value)}</span><small data-facet-count>${values.filter(v=>v===value).length}</small></label>`).join('')}
  </fieldset>`).join('');

  const tiles=renderCatalogTileArray(lang,t,scopedProducts,otherLanguage).slice(0,24).join('');
  const brandAreaGroups=brandPage?[...new Set(scopedProducts.map(p=>p.area))].map(area=>{
    const members=scopedProducts.filter(p=>p.area===area);
    return `<details class="brand-area-group"><summary><span>${escape(taxonomyLabel(lang,area))}</span><small>${escape(copy.categoryCount(members.length))}</small></summary><ul>${members.map(product=>`<li><a href="${escape(product.documents.find(d=>d.type==='product-page')[lang])}">${escape(product['name_'+lang])}</a></li>`).join('')}</ul></details>`;
  }).join(''):'';

  return `<section class="catalog-banner section--dark hex-pattern" aria-labelledby="catalog-title">
    <img class="catalog-banner__image catalog-banner__image--${scope}" src="/assets/home/${bannerImages[scope]||'hero-devices'}.webp" alt="" fetchpriority="high">
    <div class="container catalog-banner__inner">
      <nav class="catalog-crumbs" aria-label="${escape(copy.breadcrumbLabel)}">
        <ol><li><a href="${homeRoute(lang)}">${escape(t.home)}</a></li>
        ${scope === 'all' ? `<li aria-current="page">${escape(t.labels.products)}</li>`
          : taxonomyScope ? `<li><a href="${catalogRoute(lang)}">${escape(t.labels.products)}</a></li>${taxonomyScope.subcategory?`<li><a href="${escape(areaRoute(lang,taxonomyScope.area))}">${escape(taxonomyLabel(lang,taxonomyScope.area))}</a></li>`:''}<li aria-current="page">${escape(heading)}</li>`
          : `<li><a href="${catalogRoute(lang)}">${escape(t.labels.products)}</a></li><li aria-current="page">${escape(heading)}</li>`}</ol>
      </nav>
      <div>
      <h1 id="catalog-title">${escape(heading)}</h1>
      <p${brandPage ? ' class="catalog-banner__description"' : ''}>${escape(description)}</p>
      ${t.homepage.features[scope] ? `<p class="catalog-banner__summary">${escape(t.homepage.features[scope].title)}</p>` : ''}
    </div>
    </div>
  </section>

  ${hasBrandIntro ? renderBrandIntro(lang, copy, scope, heading, introProduct) : ''}

  ${brandAreaGroups?`<section class="brand-area-directory section" aria-labelledby="brand-area-title"><div class="container"><h2 id="brand-area-title">${escape(copy.categoriesTitle)}</h2><div class="brand-area-directory__grid">${brandAreaGroups}</div></div></section>`:''}

  ${categories.length > 1&&!brandPage ? `<section class="catalog-categories section" aria-labelledby="catalog-categories-title">
    <div class="container">
      <h2 id="catalog-categories-title">${escape(copy.categoriesTitle)}</h2>
      <div class="category-grid" data-columns="${Math.min(3, categories.length)}">${categories.join('')}</div>
    </div>
  </section>` : ''}

  <section class="catalog-list section--dark" id="catalog-results" tabindex="-1" aria-labelledby="catalog-results-count">
    <div class="container catalog-list__layout">
      <aside class="catalog-sidebar" id="catalog-sidebar">
        <h2>${escape(copy.filters)}</h2>
        <form class="catalog-filter-form" id="catalog-filter-form" action="${route}" autocomplete="off">
          <label class="catalog-search">
            <span class="sr-only">${escape(copy.search)}</span>
            ${icon('search')}<input type="search" name="q" placeholder="${escape(copy.search)}">
          </label>
          ${checkboxes}
          <button class="catalog-reset" type="reset">${escape(d.reset)}</button>
        </form>
      </aside>
      <div class="catalog-results">
        <div class="catalog-results__toolbar">
          <h2 id="catalog-results-count"><span role="status" data-count="${escape(copy.results('{count}'))}">${escape(copy.results(scopedProducts.length))}</span></h2>
          <label class="catalog-sort"><span class="sr-only">${escape(d.sort)}</span><select id="catalog-sort" aria-label="${escape(d.sort)}"><option value="default">${escape(d.default)}</option><option value="new">${escape(d.new)}</option><option value="alphabet">${escape(d.alphabet)}</option></select></label>
          <button class="button catalog-filter-toggle" type="button" data-open="catalog-filters" aria-haspopup="dialog" aria-controls="catalog-filters">${escape(copy.filters)}</button>
        </div>
        <div class="catalog-products" id="catalog-products">${tiles}</div>
        <div class="catalog-empty" hidden>
          <p>${escape(copy.empty)}</p>
          <a class="text-link" href="${route}#catalog-results" data-reset-catalog>${escape(copy.reset)}${icon('circleArrow')}</a>
        </div>
        <div class="catalog-more" hidden>
          <button class="button" type="button" aria-controls="catalog-products" data-load-more>${escape(copy.loadMore)}</button>
        </div>
      </div>
    </div>
  </section>

  <section class="catalog-contact" aria-labelledby="catalog-contact-title">
    <div class="container catalog-contact__layout">
      <div><h2 id="catalog-contact-title">${escape(copy.contactTitle)}</h2><p>${escape(copy.contactDescription)}</p></div>
      <a class="button" href="#office">${escape(t.utilitySales)}</a>
    </div>
  </section>`;
}

function renderBrandIntro(lang, copy, scope, heading, product) {
  const { website, images } = brandMedia[scope];
  const slides = images.map(({ file, imageCaption }, index) => `<figure class="catalog-intro__slide"${index ? ' hidden' : ''}>
    <img src="${escape(file)}" alt="" decoding="async">
    <figcaption>${escape(imageCaption[lang])}</figcaption>
  </figure>`).join('');

  return `<section class="catalog-intro" aria-label="${escape(heading)}">
    <div class="catalog-intro__copy">
      <div class="catalog-brand-logo" role="img" aria-label="${escape(heading)}"
        style="--catalog-brand-mark: url('/assets/home/brand-${scope}.webp')"></div>
      <p>${escape(copy.brandIntro[scope])}</p>
      <a class="button" href="${escape(website)}" target="_blank" rel="noopener noreferrer">${escape(copy.manufacturerSite)}</a>
    </div>
    ${slides ? `<div class="catalog-intro__image" data-brand-slideshow>${slides}</div>`
      : product ? `<div class="catalog-intro__image catalog-intro__image--fallback">
        <img src="${escape(product.image)}" alt="${escape(product['name_' + lang])}" loading="lazy" decoding="async">
      </div>` : ''}
  </section>`;
}

export function renderCatalogDialog(t) {
  return `<dialog class="catalog-filter-dialog section--dark" id="catalog-filters" aria-labelledby="catalog-filters-title">
    <div class="dialog-heading">
      <h2 id="catalog-filters-title">${escape(t.catalog.filters)}</h2>
      <button type="button" class="icon-button" data-close aria-label="${escape(t.close)}">${icon('close')}</button>
    </div>
    <div id="catalog-mobile-filters"></div>
    <button class="button" type="button" data-show-catalog>${escape(t.catalog.showResults)}</button>
  </dialog>`;
}
