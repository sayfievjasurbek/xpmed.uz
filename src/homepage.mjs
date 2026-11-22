import {CONTACT_DIALOG_ID} from './contact-panel.mjs';
import { catalogRoute, destination, contact } from './navigation.mjs';
import { icon } from './icons.mjs';
import { escape } from './html.mjs';
import { areaKeys, areaRoute, productCount, taxonomyLabel } from './clinical-taxonomy.mjs';
import { orderedBrands } from './site-settings.mjs';
import { brandName } from './i18n/discovery.mjs';

const assets = '/assets/home/';
const videoIds = ['E3vn7Gq2PFI', 'mHY8uwnrGh4'];

// The product chosen to represent each clinical area: the sharpest, most
// recognisable item rather than the first in the list. A tile image is never
// below this width; an area with nothing that large falls back to its best
// image on a soft gradient instead.
const MIN_TILE_IMAGE_WIDTH = 800;
const areaShowcase = {
  'joint-replacement': 'cynthia-knee-system',
  trauma: 'distal-femoral-locking-plate-instrument-set',
  spine: 'hobbit-5-5-6-0-instrument-set',
  'sports-arthroscopy': 'hip-arthroscopy-anchors',
  'endoscopy-visualization': 'camera-systems',
  'general-surgery': 'airseal-intelligent-flow-system',
  'powered-instruments': 'hall-sternum-saws',
  'bone-cements': 'synicem-bone-cements',
};

// The manufacturer behind each area, named on the tile. The catalogue's full
// legal names are too long for one line, so the tile uses the trading name.
const shortBrand = {'double-medical': 'Double Medical', double: 'Double Medical', biotechni: 'BIOTECHNI'};
const tileBrands = members => orderedBrands(members.map(p => p.brand)
  .filter(brand => brand && !['unassigned', 'unspecified'].includes(brand)))
  .map(brand => shortBrand[brand] || brandName(brand));

function areaArtwork(area, products) {
  const members = products.filter(product => product.area === area);
  const size = product => product.imageDimensions?.[product.image] || {};
  const curated = members.find(product => product.slug === areaShowcase[area]);
  const widest = members
    .filter(product => product.imageType === 'cutout' && (size(product).width || 0) >= MIN_TILE_IMAGE_WIDTH)
    .sort((a, b) => (size(b).width * size(b).height) - (size(a).width * size(a).height));
  const pick = (curated && (size(curated).width || 0) >= MIN_TILE_IMAGE_WIDTH ? curated : widest[0])
    || [...members].sort((a, b) => (size(b).width || 0) - (size(a).width || 0))[0];
  if (!pick?.image) return null;
  const {width = 0, height = 0} = size(pick);
  return {src: pick.image, width, height, soft: width < MIN_TILE_IMAGE_WIDTH};
}

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

  const tiles = areaKeys.map((area, index) => {
    const members = products.filter(product => product.area === area);
    const art = areaArtwork(area, products);
    const label = taxonomyLabel(lang, area);
    const brands = tileBrands(members);
    const shown = brands.slice(0, 2);
    const rest = brands.length - shown.length;
    return `<a class="area-tile" href="${escape(areaRoute(lang, area))}" style="--tile-index:${index}">
      <span class="area-tile__index" aria-hidden="true">${String(index + 1).padStart(2, '0')}</span>
      <span class="area-tile__art${art?.soft ? ' area-tile__art--soft' : ''}">${art ? `<img src="${escape(art.src)}" alt="" width="${art.width}" height="${art.height}" loading="lazy" decoding="async">` : ''}</span>
      <span class="area-tile__name">${escape(label)}</span>
      ${brands.length ? `<span class="area-tile__brands">${shown.map(escape).join('<i aria-hidden="true">·</i>')}${rest ? `<i aria-hidden="true">·</i>+${rest}` : ''}</span>` : ''}
      <span class="area-tile__foot">
        <span class="area-tile__count">${escape(productCount(lang, members.length))}</span>
        <span class="area-tile__go" aria-hidden="true">${escape(copy.areasView)} →</span>
      </span>
    </a>`;
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

    <section class="section home-feature hex-pattern" aria-labelledby="video-feature-title">
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

    <section class="home-areas" id="featured-products" aria-labelledby="products-title">
      <div class="container">
        <header class="home-areas__head">
          <p class="eyebrow">${escape(t.labels.products)}</p>
          <h2 id="products-title">${escape(copy.areasTitle)}</h2>
          ${textLink(catalogRoute(lang), copy.areasLink)}
        </header>
        <div class="area-tiles">${tiles}</div>
      </div>
    </section>

    <section class="home-contact-strip"><div class="container">
      <p class="eyebrow">XPMED</p>
      <h2>${escape(t.labels.contacts)}</h2>
      <dl class="home-contact-strip__grid">
        <div><dt>${escape(t.info.addressLabel)}</dt><dd>${t.address.map(escape).join('<br>')}</dd></div>
        <div><dt>${escape(t.info.phonesLabel)}</dt><dd>${contact.phones.map(p=>`<a href="tel:${p.tel}">${escape(p.label)}</a>`).join('')}</dd></div>
        <div><dt>${escape(t.info.emailShortLabel)}</dt><dd><a href="mailto:${contact.email}">${contact.email}</a><span class="home-contact-strip__hours">${copy.office.schedule.map(escape).join('<br>')}</span></dd></div>
      </dl>
      <button class="button" type="button" data-open="${CONTACT_DIALOG_ID}" aria-haspopup="dialog">${escape(t.contactUs)}</button>
    </div></section>`;
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
