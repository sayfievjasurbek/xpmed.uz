import { about, brands, contact, destination, socialLinks, specialties } from './navigation.mjs';
import { icon } from './icons.mjs';

const brandKeys = Object.keys(brands);
const sections = ['products', 'specialties', 'about'];
const languageLabels = { ru: 'RU', en: 'EN' };
const routes = { ru: '/', en: '/en/' };

const escape = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[character]);

export function render(lang, t, year) {
  const { labels } = t;
  const home = routes[lang];
  const link = (key, className = '') => `<a href="${escape(destination(key, lang))}"${className ? ` class="${className}"` : ''}>${escape(labels[key])}</a>`;
  const list = (keys) => `<ul class="link-list">${keys.map((key) => `<li>${link(key)}</li>`).join('')}</ul>`;
  const logo = (footer = false) => `<a class="logo${footer ? ' logo--footer' : ''}" href="${home}" aria-label="XPMED · ${escape(t.home)}"><span aria-hidden="true"></span></a>`;
  const languages = () => `<nav class="languages" aria-label="${escape(t.language)}">
    ${Object.entries(languageLabels).map(([code, label], index) => `${index ? '<span aria-hidden="true">/</span>' : ''}<a href="${routes[code]}" lang="${code}" hreflang="${code}"${code === lang ? ' aria-current="page"' : ''}>${label}</a>`).join('')}
  </nav>`;
  const contactButton = () => `<a class="button button--primary" href="#contacts">${escape(t.contactUs)}</a>`;
  const iconButton = (name, label, attributes) => `<button class="icon-button" type="button" aria-label="${escape(label)}" ${attributes}>${icon(name)}</button>`;
  const brandGroups = () => brandKeys.map((key) => `<div class="brand-group">
    <h2>${link(key)}</h2>${list(brands[key])}
  </div>`).join('');
  const catalogLink = () => `<a class="text-link" href="${escape(destination('catalog', lang))}">${escape(labels.catalog)}${icon('arrow')}</a>`;
  const panelContent = (key) => key === 'products'
    ? `<div class="product-groups">${brandGroups()}</div>${catalogLink()}`
    : list(key === 'specialties' ? specialties : about);

  const desktopNav = sections.map((key) => `<div class="nav-item">
    <button class="nav-trigger" type="button" aria-expanded="false" aria-controls="panel-${key}">${escape(labels[key])}${icon('down')}</button>
    <div class="mega-panel mega-panel--${key}" id="panel-${key}" hidden>
      <div class="container mega-panel__inner">${panelContent(key)}</div>
    </div>
  </div>`).join('');

  const mobileNav = sections.map((key) => `<details name="mobile-sections">
    <summary>${escape(labels[key])}${icon('plus')}</summary>
    <div class="accordion-body">${panelContent(key)}</div>
  </details>`).join('');

  const footerColumn = (key, keys) => `<section class="footer-column">
    <h2>${escape(labels[key])}</h2>${list(keys)}
  </section>`;

  const searchEntries = [
    ...brandKeys.flatMap((key) => [[key, 'products'], ...brands[key].map((item) => [item, key])]),
    ['catalog', 'products'],
    ...specialties.map((key) => [key, 'specialties']),
    ...about.map((key) => [key, 'about']),
    ['contacts', null],
  ];

  const searchItems = searchEntries.map(([key, parent]) => `<li data-search-result>
    <a href="${escape(key === 'contacts' ? '#contacts' : destination(key, lang))}">
      <span>${escape(labels[key])}${parent ? `<small>${escape(labels[parent])}</small>` : ''}</span>
      ${icon('arrow')}
    </a>
  </li>`).join('');

  const dialogHead = (title, id) => `<div class="dialog-heading">
    <h2 id="${id}">${escape(title)}</h2>${iconButton('close', t.close, 'data-close')}
  </div>`;

  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${escape(t.description)}">
  <title>${escape(t.title)}</title>
  <link rel="alternate" hreflang="ru" href="/">
  <link rel="alternate" hreflang="en" href="/en/">
  <link rel="alternate" hreflang="x-default" href="/">
  <link rel="icon" href="/assets/favicon.png">
  <link rel="stylesheet" href="/styles.css">
  <script type="module" src="/client.js"></script>
</head>
<body>
  <a class="skip-link button button--secondary" href="#main">${escape(t.skip)}</a>
  <header class="site-header">
    <div class="container header-bar">
      ${logo()}
      <nav class="desktop-nav" aria-label="${escape(t.primaryNav)}">
        ${desktopNav}
        <a class="nav-trigger" href="#contacts">${escape(labels.contacts)}</a>
      </nav>
      <div class="header-actions">
        ${iconButton('search', t.search, 'data-open="search-dialog" aria-haspopup="dialog"')}
        ${languages()}
        <div class="desktop-contact">${contactButton()}</div>
        ${iconButton('menu', t.menu, 'data-open="mobile-menu" aria-haspopup="dialog" aria-controls="mobile-menu"')}
      </div>
    </div>
  </header>

  <main id="main" class="homepage" tabindex="-1"></main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          ${logo(true)}
          <p>${escape(t.description)}</p>
        </div>
        <ul class="social-links" aria-label="${escape(t.socials)}">
          ${Object.entries(socialLinks).map(([key, href]) => `<li><a href="${escape(href)}" aria-label="${escape(t.platforms[key])}">${icon(key)}</a></li>`).join('')}
        </ul>
      </div>
      <nav class="footer-columns" aria-label="${escape(t.footerNav)}">
        ${footerColumn('products', brandKeys)}
        ${footerColumn('specialties', specialties)}
        ${footerColumn('about', about)}
        <section id="contacts" class="footer-column contacts" tabindex="-1">
          <h2>${escape(labels.contacts)}</h2>
          <address>
            <div>${icon('pin')}<span>${t.address.map(escape).join('<br>')}</span></div>
            <div>${icon('phone')}<a href="tel:${contact.tel}">${contact.phone}</a></div>
            <div>${icon('mail')}<a href="mailto:${contact.email}">${contact.email}</a></div>
          </address>
        </section>
      </nav>
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
      <a class="mobile-nav__link" href="#contacts">${escape(labels.contacts)}${icon('arrow')}</a>
      ${contactButton()}
    </nav>
  </dialog>

  <dialog class="dialog" id="search-dialog" aria-labelledby="search-title">
    ${dialogHead(t.search, 'search-title')}
    <label class="search-field">${icon('search')}
      <input type="search" autocomplete="off" autofocus aria-label="${escape(t.searchPrompt)}" placeholder="${escape(t.searchPrompt)}">
    </label>
    <p class="sr-only" role="status" data-search-status data-count="${escape(t.searchResults('{count}'))}"></p>
    <p class="search-empty" data-search-empty hidden>${escape(t.searchEmpty)}</p>
    <ul class="search-results">${searchItems}</ul>
  </dialog>

  <dialog class="dialog" id="privacy-dialog" aria-labelledby="privacy-title">
    ${dialogHead(labels.privacy, 'privacy-title')}
    <p>${escape(t.privacyNotice)}</p>
    <a class="text-link" href="mailto:${contact.email}">${contact.email}${icon('arrow')}</a>
  </dialog>

  <dialog class="dialog" id="sitemap-dialog" aria-labelledby="sitemap-title">
    ${dialogHead(labels.sitemap, 'sitemap-title')}
    <nav class="sitemap">
      <a href="${home}">${escape(t.home)}</a>
      ${sections.map((key) => `<details><summary>${escape(labels[key])}</summary>${panelContent(key)}</details>`).join('')}
      <a href="#contacts">${escape(labels.contacts)}</a>
    </nav>
  </dialog>
</body>
</html>
`;
}
