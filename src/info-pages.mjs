import {CONTACT_DIALOG_ID} from './contact-panel.mjs';
import {renderClients, renderCertificates} from './about-sections.mjs';
import {brandCatalogRoute, contact, destination, socialLinks} from './navigation.mjs';
import {orderedBrands} from './site-settings.mjs';
import {renderBrandMark} from './brand-media.mjs';
import {brandName} from './i18n/discovery.mjs';
import {escape} from './html.mjs';

const phones = () => contact.phones.map(({label,tel}) => `<a href="tel:${tel}">${escape(label)}</a>`).join('');
const address = t => t.address.map(escape).join(', ');
const map = (t) => {
  const {latitude,longitude} = contact.coordinates;
  const bbox = [longitude - 0.007, latitude - 0.004, longitude + 0.007, latitude + 0.004].join('%2C');
  return `<div class="info-map"><iframe title="${escape(t.info.mapTitle)}" src="https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&amp;layer=mapnik&amp;marker=${latitude}%2C${longitude}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe><a class="text-link" href="https://www.openstreetmap.org/?mlat=${latitude}&amp;mlon=${longitude}#map=17/${latitude}/${longitude}" target="_blank" rel="noopener">${escape(t.info.mapLink)} ↗</a></div>`;
};

export function renderInfoPage(lang,t,products,scope,siteData={}) {
  const c=t.info,about=scope==='about-page',brandsPage=scope==='brands-page',notFound=scope==='not-found',title=notFound?c.notFoundTitle:about?c.aboutTitle:brandsPage?c.brandsPageTitle:c.contactsTitle,description=notFound?c.notFoundDescription:about?c.aboutDescription:brandsPage?c.brandsPageDescription:c.contactsDescription;
  if(notFound)return `<section class="info-hero sp-dark hex-pattern"><div class="container"><p class="eyebrow">404</p><h1>${escape(title)}</h1><p>${escape(description)}</p><a class="button" href="${escape(destination('catalog',lang))}">${escape(c.notFoundAction)}</a></div></section>`;
  const social=Object.entries(socialLinks).map(([key,url])=>`<li>${url?`<a href="${escape(url)}" target="_blank" rel="noopener">${escape(t.platforms[key])}</a>`:`<span>${escape(t.platforms[key])} · ${escape(c.socialPending)}</span>`}</li>`).join('');
  const brands=orderedBrands(products.map(p=>p.brand).filter(brand=>brand&&!['unassigned','unspecified'].includes(brand))).map(brand=>`<a class="logo-card info-brand" href="${escape(brandCatalogRoute(lang,brand))}" title="${escape(brandName(brand))}">${renderBrandMark(brand,brandName(brand),escape)}<span class="info-brand__go" aria-hidden="true">↗</span></a>`).join('');
  if(brandsPage){const tiles=orderedBrands(products.map(p=>p.brand).filter(brand=>brand&&!['unassigned','unspecified'].includes(brand))).map(brand=>`<a class="brand-tile" href="${escape(brandCatalogRoute(lang,brand))}"><span class="brand-tile__mark">${renderBrandMark(brand,brandName(brand),escape)}</span><span>${escape(c.brandProducts)} ↗</span></a>`).join('');return `<section class="info-hero sp-dark hex-pattern"><div class="container"><p class="eyebrow">XPMED</p><h1>${escape(title)}</h1><p>${escape(description)}</p></div></section><section class="section brands-page"><div class="container"><div class="brand-tile-grid">${tiles}</div></div></section>`;}
  return `<section class="info-hero sp-dark hex-pattern"><div class="container"><p class="eyebrow">XPMED</p><h1>${escape(title)}</h1><p>${escape(description)}</p></div></section>
  ${about?`<section class="info-story section"><div class="container info-story-grid"><div><p class="eyebrow">XPMED</p><h2>${escape(c.storyTitle)}</h2><p>${escape(c.story)}</p></div><img src="/assets/home/mission-clinicians.webp" alt="${escape(t.homepage.mission.image)}" loading="lazy" decoding="async"></div></section>
  <section class="info-stats sp-dark hex-pattern"><div class="container">${['8+','7000+','500+','3'].map((value,i)=>`<div><strong>${value}</strong><span>${escape(c.stats[i])}</span>${i===3?'<small>USA · France · China</small>':''}</div>`).join('')}</div></section>
  <section class="section info-brands"><div class="container"><p class="eyebrow">XPMED</p><h2>${escape(c.brandsTitle)}</h2><p>${escape(c.brandsDescription)}</p><div class="info-brand-grid">${brands}</div></div></section>
  ${renderClients(lang,t,siteData.clients)}
  ${renderCertificates(lang,t,siteData.certificates)}`
  :`<section class="section info-contacts" id="partnership"><div class="container info-contact-grid"><div><h2>${escape(c.partnershipTitle)}</h2><p>${escape(c.partnershipText)}</p><dl><dt>${escape(c.addressLabel)}</dt><dd>${address(t)}</dd><dt>${escape(c.phonesLabel)}</dt><dd class="info-phone-list">${phones()}</dd><dt>${escape(c.emailLabel)}</dt><dd><a href="mailto:${contact.email}">${contact.email}</a></dd><dt>${escape(c.websiteLabel)}</dt><dd><a href="${contact.website}">www.xpmed.uz</a></dd><dt>${escape(c.hoursLabel)}</dt><dd>${t.homepage.office.schedule.map(escape).join('<br>')}</dd></dl><ul class="info-socials">${social}</ul></div>${map(t)}</div></section>`}`;
}
