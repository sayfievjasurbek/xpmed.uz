import {orderedBrands} from './site-settings.mjs';
import {brandCatalogRoute} from './navigation.mjs';
import {renderLibrary, renderDiscoveryDialogs} from './discovery.mjs';
import {renderContactPanel, CONTACT_DIALOG_ID} from './contact-panel.mjs';
import {discovery, brandName} from './i18n/discovery.mjs';
import { renderSystem } from './system-page.mjs';
import { systemRoute, normalizeSystem } from './catalog-data.mjs';
import { about, brands, catalogRoute, contact, destination, homeRoute, socialLinks, specialties } from './navigation.mjs';
import { icon } from './icons.mjs';
import { escape } from './html.mjs';
import { renderHomepage, renderHomeDialogs } from './homepage.mjs';
import { catalogDescription, catalogDocumentTitle, renderCatalog, renderCatalogDialog } from './catalog.mjs';
import {renderInfoPage} from './info-pages.mjs';
import {areaKeys,areaRoute,clinicalAreas,parseTaxonomyScope,subcategoryLabels,taxonomyLabel} from './clinical-taxonomy.mjs';

const sections = ['products', 'specialties', 'about'];
const languageLabels = { ru: 'RU', en: 'EN' };

export function render(lang, t, year, products, scope, otherLanguage, system = null, siteData = {}) {
  const d = discovery[lang];
  const library = scope === 'library';
  const infoPage = scope === 'about-page' || scope === 'contacts-page' || scope === 'brands-page' || scope === 'not-found';
  if (system) system = normalizeSystem(system);
  const { labels } = t;
  const home = homeRoute(lang);
  const pageRoute = (code) => system ? systemRoute(system, code) : infoPage ? homeRoute(code)+(scope==='about-page'?'about/':scope==='contacts-page'?'contacts/':scope==='brands-page'?'brands/':'404/') : library ? homeRoute(code) + 'catalogs/' : scope ? catalogRoute(code, scope) : homeRoute(code);
  const repeatedName = system && products.filter(p=>p['name_'+lang]===system.name[lang]).length>1;
  const identifier = system?.setCode || system?.refCodes?.[0] || system?.sourcePages?.[0];
  const systemTitle = system ? system.name[lang]+(repeatedName?` — ${t.catalog.categories[system.category]||system.brand}${identifier?` · ${identifier}`:''}`:'')+' | XPMED' : '';
  const title = system ? systemTitle : infoPage ? (scope==='about-page'?t.info.aboutTitle:scope==='contacts-page'?t.info.contactsTitle:scope==='brands-page'?t.info.brandsPageTitle:t.info.notFoundTitle)+' | XPMED' : library ? d.library + ' | XPMED' : scope ? catalogDocumentTitle(scope, t) + ' | XPMED' : t.title;
  const description = system ? `${system.name[lang]}. ${system.shortDescription[lang]||system.description[lang]||''}${repeatedName&&identifier?` · ${identifier}`:''}` : infoPage ? scope==='about-page'?t.info.aboutDescription:scope==='contacts-page'?t.info.contactsDescription:scope==='brands-page'?t.info.brandsPageDescription:t.info.notFoundDescription : library ? d.intro : scope ? `${catalogDocumentTitle(scope,t)}. ${catalogDescription(scope,t)}` : t.description;
  const navigationLabels = { ...labels, catalogs: d.library, new: t.catalog.newTitle };
  // discovery.js is always loaded below for the global search dialog, so the
  // library page must not ask for it a second time.
  // catalog.js drives the filter form, which only the catalog listings have.
  // It used to load on the info pages too and threw on every one of them.
  const pageScript = system ? '/system.js' : library || infoPage ? null : scope ? '/catalog.js' : '/home.js';
  const link = (key, className = '') => `<a href="${escape(destination(key, lang))}"${className ? ` class="${className}"` : ''}>${escape(navigationLabels[key])}</a>`;
  const list = (keys) => `<ul class="link-list">${keys.map((key) => `<li>${link(key)}</li>`).join('')}</ul>`;
  const logo = (footer = false) => `<a class="logo${footer ? ' logo--footer' : ''}" href="${home}" aria-label="XPMED · ${escape(t.home)}"><span aria-hidden="true"></span></a>`;
  const languages = () => `<nav class="languages" aria-label="${escape(t.language)}">
    ${Object.entries(languageLabels).map(([code, label], index) => `${index ? '<span aria-hidden="true">/</span>' : ''}<a href="${pageRoute(code)}" lang="${code}" hreflang="${code}"${code === lang ? ' aria-current="page"' : ''}>${label}</a>`).join('')}
  </nav>`;
  const socialItems = () => Object.entries(socialLinks).map(([key, href]) => `<li>${href
    ? `<a href="${escape(href)}" target="_blank" rel="noopener" aria-label="${escape(t.platforms[key])}">${icon(key)}</a>`
    : `<span class="social-placeholder" role="img" aria-label="${escape(t.platforms[key]+' · '+t.info.socialPending)}" title="${escape(t.info.socialPending)}">${icon(key)}</span>`}</li>`).join('');
  const contactButton = () => `<button class="button" type="button" data-open="${CONTACT_DIALOG_ID}" aria-haspopup="dialog">${escape(t.contactUs)}</button>`;
  const iconButton = (name, label, attributes) => `<button class="icon-button" type="button" aria-label="${escape(label)}" ${attributes}>${icon(name)}</button>`;
  const catalogLink = () => `<div class="catalog-menu-links">
    <a class="text-link" href="${home}catalogs/">${escape(lang==='ru'?'Каталоги PDF':'PDF catalogs')}${icon('circleArrow')}</a>
    <a class="text-link" href="${catalogRoute(lang)}">${escape(labels.catalog)}${icon('circleArrow')}</a>
    <a class="text-link" href="${catalogRoute(lang, 'new')}">${escape(t.catalog.newTitle)}${icon('circleArrow')}</a>
    <a class="text-link" href="${home}brands/">${escape(labels.brands)}${icon('circleArrow')}</a>
  </div>`;
  const productCount = count => lang === 'en' ? `${count} ${count===1?'product':'products'}` : `${count} ${count%10===1&&count%100!==11?'продукт':count%10>=2&&count%10<=4&&(count%100<12||count%100>14)?'продукта':'продуктов'}`;
  const areaIcon=key=>`<svg class="area-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${({
    'joint-replacement':'M8 4v5m8-5v5M8 15v5m8-5v5M7 9h10v6H7z',trauma:'M6 4h12v4H6zM8 8v12m8-12v12M5 13h14',spine:'M12 3c-2 2-2 4 0 6s2 4 0 6-2 4 0 6M8 5h8M8 19h8','sports-arthroscopy':'M12 3a9 9 0 1 0 9 9M8 12h8m-4-4v8','endoscopy-visualization':'M3 8h12v8H3zM15 10l6-3v10l-6-3z','general-surgery':'M4 12h16M12 4v16M7 7l10 10m0-10L7 17','powered-instruments':'M4 9h10v6H4zM14 11h6v2h-6zM7 6v3m4-3v3','bone-cements':'M8 3h8v4l2 3v11H6V10l2-3zM9 13h6'})[key]}"/></svg>`;
  const brandChip=(brand,area)=>`<a class="area-brand" href="${escape(brandCatalogRoute(lang,brand)+'?area='+encodeURIComponent(area)+'#catalog-results')}">${escape(brandName(brand))}</a>`;
  const areaPanels=areaKeys.map((area,index)=>{const members=products.filter(p=>p.area===area);const subs=clinicalAreas[area].subcategories.filter(sub=>members.some(p=>p.taxonomySubcategory===sub));const areaBrands=orderedBrands(members.map(p=>p.brand).filter(brand=>brand&&!['unassigned','unspecified'].includes(brand)));return `<section class="area-menu__panel" id="area-panel-${area}" role="tabpanel" aria-labelledby="area-tab-${area}"${index?' hidden':''}><header class="area-menu__header"><div><h3>${escape(taxonomyLabel(lang,area))}</h3><p>${escape(clinicalAreas[area].description[lang])}</p></div><small>${escape(productCount(members.length))}</small></header><div class="area-menu__subcategories">${subs.map(sub=>{const count=members.filter(p=>p.taxonomySubcategory===sub).length;return `<a href="${escape(areaRoute(lang,area,sub))}"><span>${escape(taxonomyLabel(lang,sub))}</span><small>${escape(String(count))}</small></a>`}).join('')}</div><footer class="area-menu__footer"><div class="area-menu__brands"><span>${escape(lang==='ru'?'Бренды:':'Brands:')}</span>${areaBrands.map(brand=>brandChip(brand,area)).join('')}</div><a class="button area-menu__all" href="${escape(areaRoute(lang,area))}">${escape(lang==='ru'?'Все продукты раздела →':'All products in this area →')}</a></footer></section>`}).join('');
  const productMenu=`<div class="product-menu-shell"><div class="area-menu"><div class="area-menu__areas" role="tablist" aria-label="${escape(labels.products)}">${areaKeys.map((area,index)=>`<button id="area-tab-${area}" role="tab" aria-controls="area-panel-${area}" aria-selected="${!index}" tabindex="${index?'-1':'0'}">${areaIcon(area)}<span>${escape(taxonomyLabel(lang,area))}</span></button>`).join('')}</div><div class="area-menu__panels">${areaPanels}</div></div>${catalogLink()}</div>`;
  const mobileProductMenu=`<div class="mobile-area-menu">${areaKeys.map(area=>{const members=products.filter(p=>p.area===area),subs=clinicalAreas[area].subcategories.filter(sub=>members.some(p=>p.taxonomySubcategory===sub));return `<details><summary>${areaIcon(area)}<span>${escape(taxonomyLabel(lang,area))}</span><small>${escape(String(members.length))}</small>${icon('plus')}</summary><div><p>${escape(clinicalAreas[area].description[lang])}</p><ul class="link-list">${subs.map(sub=>{const count=members.filter(p=>p.taxonomySubcategory===sub).length;return `<li><a href="${escape(areaRoute(lang,area,sub))}"><span>${escape(taxonomyLabel(lang,sub))}</span><small>${escape(String(count))}</small></a></li>`}).join('')}</ul><a class="text-link" href="${escape(areaRoute(lang,area))}">${escape(lang==='ru'?'Все продукты раздела':'All products in this area')}${icon('circleArrow')}</a></div></details>`}).join('')}</div>${catalogLink()}`;
  const panelContent = (key) => key === 'products'
    ? productMenu
    : list(key === 'specialties' ? specialties : about);

  const desktopNav = sections.map((key) => `<div class="nav-item">
    <button class="nav-trigger" type="button" aria-expanded="false" aria-controls="panel-${key}">${escape(navigationLabels[key])}${icon('down')}</button>
    <div class="mega-panel mega-panel--${key}" id="panel-${key}" hidden>
      <div class="container mega-panel__inner">${panelContent(key)}</div>
    </div>
  </div>`).join('');

  const mobileNav = sections.map((key) => `<details name="mobile-sections">
    <summary>${escape(navigationLabels[key])}${icon('plus')}</summary>
    <div class="accordion-body">${key==='products'?mobileProductMenu:panelContent(key)}</div>
  </details>`).join('');

  const footerGroup = (key, keys) => `<div class="footer-nav__group">
    <p>${escape(navigationLabels[key])}</p>${list(keys)}
  </div>`;


  const dialogHead = (label,id) => `<div class="dialog-heading"><h2 id="${id}">${escape(label)}</h2>${iconButton('close',t.close,'data-close')}</div>`;
  const schema = { '@context':'https://schema.org', '@type':'MedicalBusiness', name:'XPMED', url:contact.website, email:contact.email, telephone:contact.phones.map(p=>p.label), address:{'@type':'PostalAddress',streetAddress:lang==='ru'?'ул. Солар, 12':'Solar Street, 12',addressLocality:'Tashkent',addressRegion:'Yakkasaray District',addressCountry:'UZ'}, geo:{'@type':'GeoCoordinates',latitude:contact.coordinates.latitude,longitude:contact.coordinates.longitude}, sameAs:Object.values(socialLinks).filter(Boolean) };
  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${escape(description)}">
  ${scope==='not-found'?'<meta name="robots" content="noindex,follow">':''}
  <title>${escape(title)}</title>
  <link rel="canonical" href="${escape(contact.website+pageRoute(lang))}">
  <script type="application/ld+json">${JSON.stringify(schema).replaceAll('<','\\u003c')}</script>
  <link rel="alternate" hreflang="ru" href="${escape(contact.website+pageRoute('ru'))}">
  <link rel="alternate" hreflang="en" href="${escape(contact.website+pageRoute('en'))}">
  <link rel="alternate" hreflang="x-default" href="${escape(contact.website+pageRoute('ru'))}">
  <link rel="icon" href="/assets/favicon.png">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/homepage.css">
${system ? '  <link rel="stylesheet" href="/system.css">\n' : ''}${scope && !infoPage ? '  <link rel="stylesheet" href="/catalog.css">\n' : ''}  <script type="module" src="/client.js"></script>
${pageScript ? `  <script type="module" src="${pageScript}"></script>\n` : ''}  <link rel="stylesheet" href="/discovery.css">
  <script type="module" src="/discovery.js"></script>
</head>
<body>
  <a class="skip-link button" href="#main">${escape(t.skip)}</a>
  <header class="site-header">
    <div class="container header-bar">
      ${logo()}
      <div class="header-side">
        <div class="header-actions">
          <a href="${destination('partners', lang)}">${escape(t.utilityPartners)}</a>
          <a href="${escape(destination('contacts',lang))}">${escape(t.utilitySales)}</a>
          <ul class="social-links social-links--header" aria-label="${escape(t.socials)}">${socialItems()}</ul>
          ${languages()}
          ${iconButton('search', t.search, 'data-open="search-dialog" aria-haspopup="dialog"')}
        </div>
        <nav class="desktop-nav" aria-label="${escape(t.primaryNav)}">
          ${desktopNav}
          <a class="nav-trigger" href="${escape(destination('contacts',lang))}">${escape(labels.contacts)}</a>
        </nav>
      </div>
      ${iconButton('menu', t.menu, 'data-open="mobile-menu" aria-haspopup="dialog" aria-controls="mobile-menu"')}
    </div>
  </header>

  <main id="main" class="${scope ? 'catalog-page' : 'homepage'}" tabindex="-1">
    ${system ? renderSystem(system, lang) : infoPage ? renderInfoPage(lang,t,products,scope,siteData) : library ? renderLibrary(lang,t,siteData.catalogs||[]) : scope ? renderCatalog(lang, t, scope, products, otherLanguage) : renderHomepage(lang, t, products)}
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          ${logo(true)}
          <p>${escape(t.description)}</p>
          <ul class="social-links" aria-label="${escape(t.socials)}">
            ${socialItems()}
          </ul>
        </div>
        <nav class="footer-nav" aria-label="${escape(t.footerNav)}">
          ${footerGroup('products', ['catalog', 'catalogs', 'brands', 'new'])}
          ${footerGroup('specialties', specialties)}
          ${footerGroup('about', about)}
        </nav>
      </div>
      <div class="footer-bottom">
        <small>${escape(t.copyright(year))}</small>
        <ul>
          <li><button type="button" data-open="privacy-dialog" aria-haspopup="dialog">${escape(labels.privacy)}</button></li>
          <li><button type="button" data-open="sitemap-dialog" aria-haspopup="dialog">${escape(labels.sitemap)}</button></li>
        </ul>
        <small>${escape(t.disclaimer)}</small>
      </div>
    </div>
  </footer>

  <dialog class="mobile-menu" id="mobile-menu" aria-label="${escape(t.primaryNav)}">
    <div class="mobile-menu__header container">
      ${logo()}
      ${languages()}
      ${iconButton('close', t.close, 'data-close autofocus')}
    </div>
    <nav class="mobile-nav container" aria-label="${escape(t.primaryNav)}">
      ${mobileNav}
      <a class="mobile-nav__link" href="${escape(destination('contacts',lang))}">${escape(labels.contacts)}${icon('arrow')}</a>
      ${contactButton()}
    </nav>
  </dialog>

  ${renderDiscoveryDialogs(lang)}

  <dialog class="dialog" id="privacy-dialog" aria-labelledby="privacy-title">
    ${dialogHead(labels.privacy, 'privacy-title')}
    <p>${escape(t.privacyNotice)}</p>
    <a class="text-link" href="mailto:${contact.email}">${contact.email}${icon('circleArrow')}</a>
  </dialog>

  <dialog class="dialog" id="sitemap-dialog" aria-labelledby="sitemap-title">
    ${dialogHead(labels.sitemap, 'sitemap-title')}
    <nav class="sitemap">
      <a href="${home}">${escape(t.home)}</a>
      ${sections.map((key) => `<details><summary>${escape(navigationLabels[key])}</summary>${key==='products'?mobileProductMenu:panelContent(key)}</details>`).join('')}
      <a href="${escape(destination('contacts',lang))}">${escape(labels.contacts)}</a>
    </nav>
  </dialog>
  ${renderContactPanel(lang, t)}
  ${scope && !library && !infoPage ? renderCatalogDialog(t) : !scope ? renderHomeDialogs(t) : ''}
</body>
</html>
`;
}
