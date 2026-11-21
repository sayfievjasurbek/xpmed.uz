// Clients and certificates on the About page, in both languages.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadAboutData, renderClients, renderCertificates, clientLogo, certificateThumb, certificateDocument} from '../src/about-sections.mjs';
import {brandMarks, renderBrandMark} from '../src/brand-media.mjs';
import ru from '../src/i18n/ru.mjs';
import en from '../src/i18n/en.mjs';

const {clients, certificates} = await loadAboutData();

test('Every client logo and certificate asset is built and shipped', async () => {
  assert.equal(clients.length, 9, 'expected the nine clinics');
  assert.equal(certificates.length, 3, 'expected the three certificates');
  for (const client of clients) {
    await fs.access(`public${clientLogo(client.id)}`);
    await fs.access(`dist${clientLogo(client.id)}`);
    await fs.access(`content/clients/${client.id}.jpg`);
  }
  for (const record of certificates) {
    for (const asset of [certificateThumb(record.id), certificateDocument(record.id)]) {
      await fs.access(`public${asset}`);
      await fs.access(`dist${asset}`);
    }
    await fs.access(`content/certificates/${record.id}.jpg`);
    const pdf = await fs.readFile(`dist${certificateDocument(record.id)}`);
    assert.equal(pdf.subarray(0, 4).toString(), '%PDF', `${record.id} is not a PDF`);
  }
});

test('The marquee carries each client once for screen readers and twice for the loop', () => {
  for (const [lang, t] of [['ru', ru], ['en', en]]) {
    const html = renderClients(lang, t, clients);
    const rows = html.match(/class="client-marquee__row/g) || [];
    assert.equal(rows.length, 2, `${lang}: expected two rows`);
    assert.ok(html.includes('client-marquee__row--reverse'), `${lang}: second row must run the other way`);
    // Four sets in total: two per row, so translating -50% loops seamlessly.
    assert.equal((html.match(/client-marquee__set/g) || []).length, 4, `${lang}: expected two sets per row`);
    assert.equal((html.match(/data-marquee-clone/g) || []).length, 2, `${lang}: each row needs one clone`);
    assert.equal((html.match(/class="logo-card client-card"/g) || []).length, clients.length * 4, `${lang}: card count`);

    for (const client of clients) {
      assert.ok(html.includes(clientLogo(client.id)), `${lang}: ${client.id} logo missing`);
      // The full clinic name is the tooltip and the alt text.
      assert.ok(html.includes(`title="${client.name[lang].replace(/&/g, '&amp;')}"`), `${lang}: ${client.id} tooltip`);
      assert.ok(html.includes(`alt="${client.name[lang].replace(/&/g, '&amp;')}"`), `${lang}: ${client.id} alt`);
    }
    // Only the nine real cards are announced; every duplicate is hidden.
    const named = [...html.matchAll(/<img [^>]*alt="([^"]+)"/g)].length;
    assert.equal(named, clients.length, `${lang}: ${named} cards carry a name, expected ${clients.length}`);
    assert.ok(html.includes(t.info.clientsCount), `${lang}: client count label`);
    assert.ok(html.includes('500+'), `${lang}: client count`);
  }
});

test('Reduced motion replaces the marquee with a static grid', async () => {
  const css = await fs.readFile('dist/styles.css', 'utf8');
  const block = css.slice(css.indexOf('@media (prefers-reduced-motion: reduce) {\n  .client-marquee'));
  assert.ok(block, 'no reduced-motion block for the marquee');
  const rule = block.slice(0, block.indexOf('\n}\n'));
  assert.match(rule, /\.client-marquee__track\s*{[^}]*animation:\s*none/, 'the track must stop animating');
  assert.match(rule, /\.client-marquee__row--reverse[^{]*{\s*display:\s*none/, 'the second row must go');
  assert.match(rule, /data-marquee-clone[^{]*{\s*display:\s*none/, 'the clones must go');
  assert.match(rule, /\.client-marquee__set\s*{[^}]*grid-template-columns:\s*repeat\(3/, 'a 3-wide grid must remain');
});

test('Certificates show their source values and open in the PDF viewer', () => {
  for (const [lang, t] of [['ru', ru], ['en', en]]) {
    const html = renderCertificates(lang, t, certificates);
    assert.equal((html.match(/class="certificate-card"/g) || []).length, 3, `${lang}: three cards`);
    for (const record of certificates) {
      assert.ok(html.includes(record.number), `${lang}: ${record.id} number`);
      assert.ok(html.includes(record.product[lang]), `${lang}: ${record.id} product`);
      assert.ok(html.includes(record.holder[lang]), `${lang}: ${record.id} holder`);
      assert.ok(html.includes(certificateThumb(record.id)), `${lang}: ${record.id} thumbnail`);
      // The existing viewer only accepts /catalogs/**.pdf.
      assert.match(certificateDocument(record.id), /^\/catalogs\/[a-zA-Z0-9_./%-]+\.pdf$/);
      assert.ok(html.includes(`data-open-pdf="${certificateDocument(record.id)}"`), `${lang}: ${record.id} viewer link`);
    }
    const year = lang === 'ru' ? '2019' : '2019';
    assert.ok(html.includes(year), `${lang}: registration year`);
    assert.ok(html.includes(t.info.certificatesNote), `${lang}: request note`);
    assert.ok(html.includes(t.info.requestDocuments), `${lang}: request button`);
    assert.match(html, /data-open="contact-dialog"/, `${lang}: the button must open the contact panel`);
  }
});

test('Registration dates are formatted per language, not pasted', async () => {
  const pages = {ru: await fs.readFile('dist/about/index.html', 'utf8'), en: await fs.readFile('dist/en/about/index.html', 'utf8')};
  assert.ok(pages.ru.includes('14 июня 2019'), 'Russian date');
  assert.ok(pages.en.includes('14 June 2019'), 'English date');
  assert.ok(!pages.ru.includes('2019-06-14') && !pages.en.includes('2019-06-14'), 'raw ISO dates must not reach the page');
});

test('White brand wordmarks are inverted on light cards, colour ones are not', async () => {
  assert.equal(renderBrandMark('conmed', 'CONMED', s => s).includes('is-light-mark'), true);
  assert.equal(renderBrandMark('spinendos', 'SPINENDOS', s => s).includes('is-light-mark'), false);
  assert.equal(renderBrandMark('nope', 'Nope', s => s), '<strong>Nope</strong>');
  for (const [brand, mark] of Object.entries(brandMarks)) {
    await fs.access(`src/assets${mark.file.replace('/assets', '')}`);
    assert.equal(typeof mark.light, 'boolean', `${brand} must say whether its mark is light`);
  }
  const css = await fs.readFile('dist/styles.css', 'utf8');
  assert.match(css, /img\.is-light-mark\s*{[^}]*invert\(1\)/);
  // The placeholder brand must not appear as a card on either page.
  for (const page of ['dist/about/index.html', 'dist/brands/index.html', 'dist/en/about/index.html']) {
    const html = await fs.readFile(page, 'utf8');
    assert.ok(!html.includes('>unspecified<'), `${page} shows the placeholder brand`);
  }
});

test('Bad About records are rejected rather than published', async () => {
  await assert.rejects(loadAboutData('tests/fixtures-that-do-not-exist'));
  // Every shipped record passes the same checks the loader applies.
  for (const record of certificates) {
    assert.match(record.registeredAt, /^\d{4}-\d{2}-\d{2}$/);
    assert.match(record.id, /^[a-z0-9][a-z0-9-]*$/);
    assert.ok(record.number.trim());
  }
  for (const client of clients) assert.match(client.id, /^[a-z0-9][a-z0-9-]*$/);
});
