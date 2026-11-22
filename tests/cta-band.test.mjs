// The closing band. One component rendered from render.mjs, so the thing to
// guard is where it appears and where it must not: the homepage has its own
// contact strip, Contacts is already the contact page, and 404 and the PDF
// library close on their own. Its ivory is also the one colour reserved for
// this band, so a second user of it would be a mistake.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

const read = path => fs.readFile('dist/' + path, 'utf8');
const withBand = ['catalog/index.html', 'catalog/conmed/index.html', 'about/index.html', 'brands/index.html', 'academy/index.html',
  'en/catalog/index.html', 'en/about/index.html', 'en/brands/index.html', 'en/academy/index.html'];
const withoutBand = ['index.html', 'en/index.html', 'contacts/index.html', 'en/contacts/index.html', '404/index.html', 'catalogs/index.html'];

test('The band closes every page that should have one, and no others', async () => {
  for (const page of withBand) assert.equal((await read(page)).match(/data-cta-band/g)?.length, 1, `${page} should carry exactly one band`);
  for (const page of withoutBand) assert.ok(!(await read(page)).includes('data-cta-band'), `${page} must not carry the band`);
  // Product pages too: take the first one the catalog links to.
  const catalog = await read('catalog/index.html');
  const product = catalog.match(/href="(\/catalog\/[a-z0-9-]+\/[a-z0-9-]+\/)"/)?.[1];
  assert.ok(product, 'no product link found on the catalog page');
  assert.ok((await read(product.slice(1) + 'index.html')).includes('data-cta-band'), `${product} has no band`);
});

test('The band carries the sales copy, the button and the phone', async () => {
  for (const [page, title, phone] of [['catalog/index.html', 'Не нашли нужный продукт?', '+998 95 476 66 60'],
    ['en/catalog/index.html', 'Looking for a product you couldn’t find?', '+998 95 476 66 60']]) {
    const html = await read(page);
    const band = html.slice(html.indexOf('data-cta-band'));
    assert.ok(band.includes(title), `${page}: title`);
    assert.ok(band.includes('cta-band__action'), `${page}: button`);
    assert.ok(band.includes('href="tel:+998954766660"') && band.includes(phone), `${page}: phone`);
    assert.ok(band.includes('class="eyebrow"'), `${page}: eyebrow`);
  }
});

test('The Academy band keeps its own copy and links out to the academy', async () => {
  const html = await read('academy/index.html');
  const band = html.slice(html.indexOf('data-cta-band'));
  assert.ok(band.includes('Станьте участником XPMED Academy'));
  assert.ok(band.includes('href="https://xpmedacademy.com" target="_blank" rel="noopener"'));
  assert.ok(!band.includes('Не нашли нужный продукт'), 'the sales copy leaked into the academy band');
});

test('The band ivory is defined once and used by nothing else', async () => {
  const css = await fs.readFile('dist/styles.css', 'utf8');
  for (const colour of ['#F5F1E8', '#E9E3D6', '#E2DACB']) {
    assert.equal(css.match(new RegExp(colour, 'gi'))?.length, 1, `${colour} should appear once, as a band token`);
  }
  for (const sheet of ['catalog.css', 'homepage.css', 'system.css', 'academy.css', 'discovery.css']) {
    const other = await fs.readFile('dist/' + sheet, 'utf8');
    assert.ok(!/#F5F1E8/i.test(other), `${sheet} uses the band's ivory`);
  }
});
