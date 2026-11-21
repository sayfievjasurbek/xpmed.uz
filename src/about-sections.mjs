// Clients and certificates for the About page. Both read their records from
// content/, so adding a clinic or replacing a certificate is a data change
// plus a run of scripts/prepare-brand-assets.py — no template edits.
import {readdir, readFile} from 'node:fs/promises';
import path from 'node:path';
import {CONTACT_DIALOG_ID} from './contact-panel.mjs';
import {escape as e} from './html.mjs';
import {renderBrandMark} from './brand-media.mjs';

const SAFE_ID = /^[a-z0-9][a-z0-9-]*$/;

export const clientLogo = id => `/images/clients/${id}.webp`;
export const certificateThumb = id => `/images/certificates/${id}.webp`;
export const certificateDocument = id => `/catalogs/certificates/${id}/source.pdf`;

export async function loadAboutData(root = 'content') {
  const clients = JSON.parse(await readFile(path.join(root, 'clients.json'), 'utf8'));
  for (const client of clients) {
    if (!SAFE_ID.test(client.id || '')) throw Error(`Unsafe client id: ${client.id}`);
    for (const lang of ['ru', 'en']) if (!client.name?.[lang]?.trim()) throw Error(`Client ${client.id} is missing name.${lang}`);
  }

  const directory = path.join(root, 'certificates');
  const names = (await readdir(directory)).filter(name => name.endsWith('.json')).sort();
  const certificates = [];
  for (const name of names) {
    const record = JSON.parse(await readFile(path.join(directory, name), 'utf8'));
    if (!SAFE_ID.test(record.id || '') || `${record.id}.json` !== name) throw Error(`Certificate id does not match its file: ${name}`);
    if (!record.number?.trim()) throw Error(`Certificate ${record.id} is missing its number`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(record.registeredAt || '')) throw Error(`Certificate ${record.id} needs registeredAt as YYYY-MM-DD`);
    for (const field of ['holder', 'product']) {
      for (const lang of ['ru', 'en']) if (!record[field]?.[lang]?.trim()) throw Error(`Certificate ${record.id} is missing ${field}.${lang}`);
    }
    certificates.push(record);
  }
  certificates.sort((a, b) => (a.order ?? 99) - (b.order ?? 99));
  return {clients, certificates};
}

const registeredOn = (iso, lang) =>
  new Intl.DateTimeFormat(lang === 'ru' ? 'ru-RU' : 'en-GB', {day: 'numeric', month: 'long', year: 'numeric'})
    .format(new Date(`${iso}T00:00:00Z`)).replace(/\s*г\.$/, '');

export function renderClients(lang, t, clients = []) {
  if (!clients.length) return '';
  const c = t.info;
  const card = (client, clone) =>
    `<figure class="logo-card client-card"${clone ? ' aria-hidden="true"' : ''} title="${e(client.name[lang])}">` +
    `<img src="${e(clientLogo(client.id))}" alt="${clone ? '' : e(client.name[lang])}" width="360" height="150" loading="lazy" decoding="async">` +
    `</figure>`;
  // Each row carries the set twice so the -50% translation loops seamlessly.
  const row = (list, modifier, hidden) =>
    `<div class="client-marquee__row${modifier}"${hidden ? ' aria-hidden="true"' : ''}>` +
    `<div class="client-marquee__track">` +
    `<div class="client-marquee__set">${list.map(client => card(client, hidden)).join('')}</div>` +
    `<div class="client-marquee__set" aria-hidden="true" data-marquee-clone>${list.map(client => card(client, true)).join('')}</div>` +
    `</div></div>`;

  return `<section class="section info-clients" id="clients">
    <div class="container info-clients__head">
      <p class="eyebrow">XPMED</p>
      <h2>${e(c.clientsTitle)}</h2>
      <p>${e(c.clientsDescription)}</p>
    </div>
    <div class="client-marquee" role="group" aria-label="${e(c.clientsTitle)}">
      ${row(clients, '', false)}
      ${row([...clients].reverse(), ' client-marquee__row--reverse', true)}
    </div>
    <div class="container"><p class="info-clients__count"><strong>500+</strong><span>${e(c.clientsCount)}</span></p></div>
  </section>`;
}

export function renderCertificates(lang, t, certificates = []) {
  if (!certificates.length) return '';
  const c = t.info;
  const cards = certificates.map(record => {
    const title = `${record.number} · ${record.holder[lang]}`;
    return `<article class="certificate-card">
      <a class="certificate-card__frame" href="${e(certificateDocument(record.id))}" data-open-pdf="${e(certificateDocument(record.id))}" data-pdf-title="${e(title)}" data-pdf-page="1" target="_blank" rel="noopener" aria-label="${e(c.openCertificate)}: ${e(title)}">
        <img src="${e(certificateThumb(record.id))}" alt="${e(c.certificateAlt)}: ${e(record.number)}" width="720" height="1018" loading="lazy" decoding="async">
        <span class="certificate-card__zoom" aria-hidden="true">${e(c.openCertificate)} ↗</span>
      </a>
      <div class="certificate-card__body">
        <span class="certificate-card__brand">${renderBrandMark(record.brand, record.holder[lang], e)}</span>
        <p class="certificate-card__number">${e(record.number)}</p>
        <h3>${e(record.product[lang])}</h3>
        <dl class="certificate-card__meta">
          <div><dt>${e(c.certificateHolder)}</dt><dd>${e(record.holder[lang])}</dd></div>
          <div><dt>${e(c.certificateRegistered)}</dt><dd>${e(registeredOn(record.registeredAt, lang))}</dd></div>
        </dl>
      </div>
    </article>`;
  }).join('');

  return `<section class="section info-certificates" id="certificates">
    <div class="container">
      <p class="eyebrow">XPMED</p>
      <h2>${e(c.certificatesTitle)}</h2>
      <p class="info-certificates__intro">${e(c.certificatesDescription)}</p>
      <div class="certificate-grid">${cards}</div>
      <div class="certificate-request">
        <p>${e(c.certificatesNote)}</p>
        <button class="button" type="button" data-open="${CONTACT_DIALOG_ID}" aria-haspopup="dialog">${e(c.requestDocuments)}</button>
      </div>
    </div>
  </section>`;
}
