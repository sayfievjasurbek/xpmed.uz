import {escape as e} from './html.mjs';
import {icon} from './icons.mjs';
import {discovery} from './i18n/discovery.mjs';
import {shortCatalogTitle} from './catalog-title.mjs';
import {catalogRoute} from './navigation.mjs';

// Five is what fits under the meta line without the card growing past its
// neighbours; the rest is one click away. Beyond this many the expanded list
// scrolls inside the card instead of running down the page.
const PREVIEW_ITEMS = 5;
const SCROLL_ITEMS = 30;

function catalogCard(lang, d, c) {
  const title = c.title[lang];
  const short = shortCatalogTitle(title);
  const items = c.systems;
  const extra = Math.max(0, items.length - PREVIEW_ITEMS);
  const item = (s, index) => `<li${index >= PREVIEW_ITEMS ? ' data-extra-item hidden' : ''}>
      <a href="${e(lang === 'en' ? s.url_en : s.url)}" title="${e(s.name[lang])}"><span>${e(s.name[lang])}</span>${icon('arrow')}</a>
    </li>`;
  return `<article class="library-card" data-catalog-brand="${e(c.brand)}">
    <button class="library-cover" data-open-catalog="${e(c.id)}" aria-label="${e(d.open + ' · ' + title)}">
      <img src="${e(c.coverImage || c.cover)}" alt="" loading="lazy">
      <span>${e(d.openShort)} ${icon('circleArrow')}</span>
    </button>
    <div class="library-card__copy">
      <span class="eyebrow">${e(c.brandLabel)}</span>
      <h2 title="${e(title)}">${e(short)}</h2>
      <p class="library-card__meta">${c.edition ? e(d.edition + ' ' + c.edition) + ' · ' : ''}${c.pages} ${e(d.pages)} · ${(c.bytes / 1048576).toFixed(1)} MB</p>
      <div class="library-card__actions">
        <button class="button" type="button" data-open-catalog="${e(c.id)}">${e(d.openShort)}</button>
        <a class="button library-card__download" href="${e(c.file)}" download>${e(d.download)} ↓</a>
      </div>
      ${items.length ? `<div class="library-card__products">
        <h3>${e(d.extracted)}</h3>
        <ul class="library-items${items.length > SCROLL_ITEMS ? ' library-items--scroll' : ''}" data-catalog-items>${items.map(item).join('')}</ul>
        ${extra ? `<button class="library-more" type="button" data-expand-catalog aria-expanded="false"
          data-show-all="${e(d.showAll(items.length))}" data-collapse="${e(d.collapse)}">${e(d.showAll(items.length))} <span aria-hidden="true">↓</span></button>` : ''}
      </div>` : ''}
      <a class="text-link library-card__browse" href="${e(catalogRoute(lang, 'all', {catalog: c.id}))}">${e(d.browseCatalog)}${icon('circleArrow')}</a>
    </div>
  </article>`;
}
export function renderLibrary(lang,t,catalogs){const d=discovery[lang];return `<section class="catalog-banner section--dark hex-pattern"><img class="catalog-banner__image" src="/assets/home/hero-devices.webp" alt=""><div class="container catalog-banner__inner"><nav class="catalog-crumbs"><a href="${lang==='en'?'/en/':'/'}">${e(t.home)}</a> / ${e(d.catalogs)}</nav><div><h1>${d.library}</h1><p>${d.intro}</p></div></div></section><section class="library-section"><div class="container"><div class="library-tabs" role="tablist" aria-label="${e(t.catalog.brand)}">${[['all',d.all],...new Map(catalogs.map(c=>[c.brand,c.brandLabel]))].map(([id,name],i)=>`<button role="tab" tabindex="${i===0?0:-1}" aria-controls="catalog-library-panel" aria-selected="${i===0}" data-library-brand="${e(id)}">${e(name)}</button>`).join('')}</div><div class="library-grid" role="tabpanel" id="catalog-library-panel" aria-label="${e(d.catalogs)}">${catalogs.map(c=>catalogCard(lang,d,c)).join('')||`<p>${d.unavailable}</p>`}</div></div></section>`;}
export function renderDiscoveryDialogs(lang){const d=discovery[lang];return `<dialog class="global-search section--dark" id="search-dialog" aria-labelledby="search-title"><div class="discovery-top"><h2 id="search-title">${d.search}</h2><div class="search-close"><kbd>${e(d.escapeKey)}</kbd><button class="icon-button" data-close aria-label="${d.close}">${icon('close')}</button></div></div><div class="global-search__body"><label class="global-search__field">${icon('search')}<input autofocus type="search" autocomplete="off" placeholder="${d.placeholder}" aria-label="${d.search}" aria-controls="global-search-results" aria-autocomplete="list"></label><p class="global-search__status" role="status">${d.hint}</p><div id="global-search-results"></div></div></dialog><dialog class="pdf-viewer section--dark" id="pdf-viewer" aria-labelledby="pdf-viewer-title"><div class="pdf-toolbar"><h2 id="pdf-viewer-title"></h2><div class="pdf-controls"><button data-pdf="zoomOut" aria-label="${d.zoomOut}">−</button><output data-pdf-zoom>100%</output><button data-pdf="zoomIn" aria-label="${d.zoomIn}">+</button><button data-pdf="spread">${d.spread}</button><a class="button" data-pdf-download data-keep-dialog download>${d.download}</a><button class="icon-button" data-close aria-label="${d.close}">${icon('close')}</button></div></div><div class="pdf-stage"><p role="status" data-pdf-status>${d.loading}</p><div class="pdf-pages"></div></div><div class="pdf-navigation"><button data-pdf="previous" aria-label="${d.previous}">←</button><label>${d.page} <input data-pdf-page type="number" min="1" value="1" aria-label="${d.page}"></label><span data-pdf-total></span><button data-pdf="next" aria-label="${d.next}">→</button></div><div class="pdf-thumbnails" aria-label="${d.pages}"></div></dialog>`;}
