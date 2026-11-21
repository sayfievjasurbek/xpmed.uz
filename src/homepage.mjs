import {CONTACT_DIALOG_ID} from './contact-panel.mjs';
import { catalogRoute, destination, contact } from './navigation.mjs';
import { icon } from './icons.mjs';
import { escape } from './html.mjs';
import { renderProductTile } from './product-tile.mjs';

const assets = '/assets/home/';
const productGroups = ['double', 'conmed', 'synimed', 'new'];
const videoIds = ['E3vn7Gq2PFI', 'mHY8uwnrGh4'];

const textLink = (href, label) => `<a class="text-link" href="${escape(href)}">${escape(label)}${icon('circleArrow')}</a>`;
const textLinkDialog = (dialog, label) => `<button class="text-link" type="button" data-open="${dialog}" aria-haspopup="dialog">${escape(label)}${icon('circleArrow')}</button>`;

function thumbnail(index, copy) {
  const { caption } = copy.testimonials[index];
  const video = videoIds[index];
  const href = `https://www.youtube.com/watch?v=${video}`;
  return `<div class="video-frame" data-video-frame>
    <a class="video-frame__play" href="${href}" data-testimonial="${video}"
       data-video-title="${escape(caption)}" data-watch-label="${escape(copy.watchOnYoutube)}"
       aria-label="${escape(copy.play + ' · ' + caption)}">
      <img src="${assets}testimonial-${index + 1}.webp" alt="" width="480" height="270" loading="lazy" decoding="async">
      <span class="play-icon" aria-hidden="true">${icon('play')}</span>
    </a>
  </div>`;
}

export function renderHomepage(lang, t, products) {
  const copy = t.homepage;
  const certificateUrl = destination('certificates',lang);

  const tabs = productGroups.map((group, index) => `<button class="product-tab" type="button" role="tab"
    id="tab-${group}" aria-controls="products-${group}" aria-selected="${index === 0}" tabindex="${index === 0 ? '0' : '-1'}">
    ${escape(copy.filters[group])}
  </button>`).join('');

  const panels = productGroups.map((group, index) => {
    const cards = products.filter((product) => group === 'new' ? product.isNew : product.brand === group)
      .slice(0, 4)
      .map((product) => renderProductTile(product, lang, copy.learnMore))
      .join('');

    return `<div id="products-${group}" role="tabpanel" aria-labelledby="tab-${group}"${index ? ' hidden' : ''}>
      <div class="product-grid">${cards}</div>
      <div class="home-catalog-link"><a class="button" href="${catalogRoute(lang, group)}">${escape(t.catalog.viewCollection(copy.filters[group]))}</a></div>
    </div>`;
  }).join('');

  return `<section class="home-hero" aria-labelledby="hero-title">
      <div class="hero-collage" aria-hidden="true">
        <div class="hero-collage__panel hero-collage__panel--room">
          <img src="${assets}surgery-suite.webp" alt="">
        </div>
        <div class="hero-collage__panel hero-collage__panel--surgeon">
          <img src="${assets}operating-room.webp" alt="" fetchpriority="high">
        </div>
        <div class="hero-collage__panel hero-collage__panel--devices">
          <img src="${assets}hero-devices.webp" alt="">
        </div>
      </div>
      <div class="container">
        <h1 id="hero-title">${escape(copy.hero.title)}</h1>
      </div>
    </section>

    <section class="section home-mission" aria-labelledby="mission-title">
      <div class="container home-split" data-reveal>
        <div class="home-split__copy">
          <h2 id="mission-title">${escape(copy.mission.title)}</h2>
          <p>${escape(copy.mission.description)}</p>
          <a class="button" href="${escape(destination('company', lang))}">${escape(copy.mission.action)}</a>
        </div>
        <img class="mission-photo" src="${assets}mission-clinicians.webp" alt="${escape(copy.mission.image)}" loading="lazy" decoding="async">
      </div>
    </section>

    <section class="section section--dark hex-pattern" aria-labelledby="video-feature-title">
      <div class="container home-split home-split--video" data-reveal>
        ${thumbnail(0, copy)}
        <div class="home-split__copy">
          <h2 id="video-feature-title">${escape(copy.videoFeature.title)}</h2>
          <p>${escape(copy.videoFeature.description)}</p>
          <div class="feature-actions">
            <button type="button" class="button" data-open="testimonials-dialog" aria-haspopup="dialog">${escape(copy.videoFeature.more)}</button>
            <a class="button" href="${escape(destination('catalog', lang))}">${escape(copy.videoFeature.catalog)}</a>
          </div>
        </div>
      </div>
    </section>

    <section class="home-products" id="featured-products" aria-labelledby="products-title">
      <div class="products-heading"><h2 id="products-title">${escape(copy.productsTitle)}</h2></div>
      <div class="product-tabs" role="tablist" aria-labelledby="products-title">${tabs}</div>
      ${panels}
    </section>

    <div class="home-teasers">
      <section class="home-teaser hex-pattern" id="partnership" aria-labelledby="partner-title">
        <div class="home-teaser__copy" data-reveal>
          <h2 id="partner-title">${escape(copy.partner.title)}</h2>
          <p class="eyebrow">${escape(copy.partnershipLabel)}</p>
          <p>${escape(copy.partner.description)}</p>
          ${textLinkDialog(CONTACT_DIALOG_ID, t.contactUs)}
        </div>
      </section>
      <section class="home-teaser section--dark hex-pattern" id="certificates" aria-labelledby="certificates-title">
        <div class="home-teaser__copy" data-reveal>
          <h2 id="certificates-title">${escape(copy.certificatesTeaser.title)}</h2>
          <p class="eyebrow">${escape(copy.certificatesTeaser.label)}</p>
          <p>${escape(copy.certificatesTeaser.description)}</p>
          ${textLink(certificateUrl, copy.certificatesTeaser.action)}
        </div>
      </section>
    </div>
    <section class="home-contact-strip"><div class="container"><div><p class="eyebrow">XPMED</p><h2>${escape(t.labels.contacts)}</h2><p>${t.address.map(escape).join(', ')}</p></div><div class="home-contact-strip__links">${contact.phones.map(p=>`<a href="tel:${p.tel}">${escape(p.label)}</a>`).join('')}<a href="mailto:${contact.email}">${contact.email}</a></div><button class="button" type="button" data-open="${CONTACT_DIALOG_ID}" aria-haspopup="dialog">${escape(t.contactUs)}</button></div></section>`;
}

export function renderHomeDialogs(t) {
  const copy = t.homepage;
  return `<dialog id="testimonials-dialog" class="dialog media-dialog" aria-labelledby="testimonials-title">
    <div class="dialog-heading">
      <h2 id="testimonials-title">${escape(copy.testimonialsTitle)}</h2>
      <button class="icon-button" type="button" data-close autofocus aria-label="${escape(t.close)}">${icon('close')}</button>
    </div>
    <div class="testimonial-grid">${copy.testimonials.map(({ title, caption }, index) => `<article>
      ${thumbnail(index, copy)}
      <h3>${escape(title)}</h3>
      <p>${escape(caption)}</p>
    </article>`).join('')}</div>
  </dialog>`;
}
