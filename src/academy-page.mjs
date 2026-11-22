import {academyPhoto, clubLogo, partnerLogo} from './academy-media.mjs';
import {renderBrandMark} from './brand-media.mjs';
import {brandName} from './i18n/discovery.mjs';
import {contact} from './navigation.mjs';
import {escape} from './html.mjs';
import {icon} from './icons.mjs';

// The academy runs its courses on these manufacturers' instruments. The first
// four already have a wordmark on the site; the last two are academy-only, so
// their logo comes from content/academy/partners/ and falls back to the name.
const partners = [
  {brand: 'double-medical'},
  {brand: 'conmed'},
  {brand: 'synimed'},
  {brand: 'spinendos'},
  {id: 'bojin', name: 'Bojin'},
  {id: 'bns-neo-science', name: 'BNS Neo Science'},
];

const siteButton = (t, className = 'button') =>
  `<a class="${className}" href="${escape(t.academy.site)}" target="_blank" rel="noopener">${escape(t.academy.siteAction)} →</a>`;

const photo = (src, alt, extra = '') =>
  `<img src="${escape(src)}" alt="${escape(alt)}" loading="lazy" decoding="async"${extra}>`;

// A club with no logo yet gets its initials in the same frame, so the row of
// four keeps its rhythm instead of showing a gap.
function clubMark(club) {
  const logo = clubLogo(club.id);
  if (logo) return `<img src="${escape(logo)}" alt="${escape(club.name)}" loading="lazy" decoding="async">`;
  const initials = club.name.split(/\s+/).map(word => word[0]).join('').slice(0, 2).toUpperCase();
  return `<span class="academy-club__monogram" aria-hidden="true">${escape(initials)}</span>`;
}

function partnerCard(partner) {
  if (partner.brand) {
    const name = brandName(partner.brand);
    return `<div class="logo-card academy-partner" title="${escape(name)}">${renderBrandMark(partner.brand, name, escape)}</div>`;
  }
  const logo = partnerLogo(partner.id);
  return `<div class="logo-card academy-partner" title="${escape(partner.name)}">${logo
    ? `<img src="${escape(logo)}" alt="${escape(partner.name)}" loading="lazy" decoding="async">`
    : `<strong>${escape(partner.name)}</strong>`}</div>`;
}

export function renderAcademyPage(lang, t) {
  const c = t.academy;

  const stats = c.stats.map((stat, index) => `<div class="academy-stat" style="--stat-index:${index}">
    <strong data-count-to="${stat.value}">${stat.value}${escape(stat.suffix)}</strong>
    <span>${escape(stat.label)}</span>
  </div>`).join('');

  const pointIcons = ['award', 'spark', 'book'];
  const points = c.about.points.map((point, index) => `<li style="--point-index:${index}">
    <span class="academy-point__icon">${icon(pointIcons[index] || 'award')}</span>
    <strong>${escape(point.title)}</strong>
    <span>${escape(point.text)}</span>
  </li>`).join('');

  const clubs = c.clubs.items.map((club, index) => `<article class="academy-club" style="--club-index:${index}">
    <span class="academy-club__mark">${clubMark(club)}</span>
    <h3>${escape(club.name)}</h3>
    <p>${escape(club.text)}</p>
  </article>`).join('');

  const heroPhoto = academyPhoto.hero();
  return `<section class="academy-hero sp-dark${heroPhoto ? '' : ' academy-hero--designed'}" aria-labelledby="academy-title">
    ${heroPhoto ? `<img class="academy-hero__photo" src="${escape(heroPhoto)}" alt="" fetchpriority="high">` : ''}
    <div class="container academy-hero__inner">
      <p class="eyebrow">${escape(c.hero.eyebrow)}</p>
      <h1 id="academy-title">${escape(c.hero.title)}</h1>
      <p class="academy-hero__subtitle">${escape(c.hero.subtitle)}</p>
      <p class="academy-hero__text">${escape(c.hero.text)}</p>
      ${siteButton(t)}
    </div>
    <div class="container"><div class="academy-stats">${stats}</div></div>
  </section>

  <section class="section academy-about" aria-labelledby="academy-about-title">
    <div class="container academy-about__grid">
      <div>
        <p class="eyebrow">${escape(c.about.eyebrow)}</p>
        <h2 id="academy-about-title">${escape(c.about.title)}</h2>
        ${c.about.paragraphs.map(text => `<p>${escape(text)}</p>`).join('')}
        <ul class="academy-points">${points}</ul>
      </div>
      ${photo(academyPhoto.about(), c.about.image, ' class="academy-about__photo"')}
    </div>
  </section>

  <section class="section sp-dark hex-pattern academy-courses" aria-labelledby="academy-courses-title">
    <div class="container academy-courses__grid">
      <div class="academy-courses__photos">
        ${c.courses.images.map((alt, index) => photo(academyPhoto.course(index), alt)).join('')}
      </div>
      <div>
        <p class="eyebrow">${escape(c.courses.eyebrow)}</p>
        <h2 id="academy-courses-title">${escape(c.courses.title)}</h2>
        <p>${escape(c.courses.intro)}</p>
        <h3>${escape(c.courses.listTitle)}</h3>
        <ul class="academy-course-list">${c.courses.items.map(item => `<li>${escape(item)}</li>`).join('')}</ul>
      </div>
    </div>
  </section>

  <section class="section academy-mission" aria-labelledby="academy-mission-title">
    <div class="container academy-mission__grid">
      <div>
        <p class="eyebrow">${escape(c.mission.eyebrow)}</p>
        <h2 id="academy-mission-title">${escape(c.mission.title)}</h2>
        <p class="academy-mission__lead">${escape(c.mission.text)}</p>
        <h3>${escape(c.mission.valuesTitle)}</h3>
        <ul class="academy-values">${c.mission.values.map(value => `<li>${escape(value)}</li>`).join('')}</ul>
      </div>
      ${photo(academyPhoto.mission(), c.mission.image, ' class="academy-mission__photo"')}
    </div>
  </section>

  <section class="section sp-dark academy-community" aria-labelledby="academy-clubs-title">
    <div class="container">
      <p class="eyebrow">${escape(c.clubs.eyebrow)}</p>
      <h2 id="academy-clubs-title">${escape(c.clubs.title)}</h2>
      <p class="academy-community__intro">${escape(c.clubs.intro)}</p>
      <div class="academy-clubs">${clubs}</div>
    </div>
  </section>

  <section class="section academy-partners" aria-labelledby="academy-partners-title">
    <div class="container">
      <p class="eyebrow">${escape(c.partners.eyebrow)}</p>
      <h2 id="academy-partners-title">${escape(c.partners.title)}</h2>
      <p>${escape(c.partners.intro)}</p>
      <div class="academy-partner-grid">${partners.map(partnerCard).join('')}</div>
    </div>
  </section>

  <section class="academy-cta" aria-labelledby="academy-cta-title">
    <div class="container academy-cta__inner">
      <div>
        <h2 id="academy-cta-title">${escape(c.cta.title)}</h2>
        <p>${escape(c.cta.text)}</p>
        ${siteButton(t, 'button academy-cta__button')}
      </div>
      <dl class="academy-cta__contacts">
        <div><dt>${escape(c.cta.phonesLabel)}</dt><dd>${contact.phones.map(p => `<a href="tel:${p.tel}">${escape(p.label)}</a>`).join('')}</dd></div>
        <div><dt>${escape(c.cta.emailLabel)}</dt><dd><a href="mailto:${contact.email}">${contact.email}</a></dd></div>
      </dl>
    </div>
  </section>`;
}
