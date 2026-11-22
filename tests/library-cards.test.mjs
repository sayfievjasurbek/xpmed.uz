// The /catalogs library cards. Every card has the same parts in the same
// order so a row of them lines up, the titles are the printed ones with the
// brand and the "— каталог продукции" tail taken off, only the first five
// products are in the page, and each card can hand the catalog page a filter
// for its own PDF.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {shortCatalogTitle} from '../src/catalog-title.mjs';

const page = lang => fs.readFile(`dist${lang === 'en' ? '/en' : ''}/catalogs/index.html`, 'utf8');
const catalogs = JSON.parse(await fs.readFile('dist/catalog-library-index.json', 'utf8'));
// Each card on its own: the last one would otherwise run to the end of the
// page and pull the footer's lists in with it.
const cards = html => html.split('<article class="library-card"').slice(1).map(card => card.slice(0, card.indexOf('</article>')));

test('Every card carries the same parts in the same order', async () => {
  for (const lang of ['ru', 'en']) {
    const list = cards(await page(lang));
    assert.equal(list.length, catalogs.length);
    for (const card of list) {
      const order = ['library-cover', 'class="eyebrow"', '<h2 title=', 'library-card__meta', 'library-card__actions', 'library-card__browse']
        .map(part => card.indexOf(part));
      assert.ok(order.every(index => index > -1), `${lang}: a card is missing a part`);
      assert.deepEqual(order, [...order].sort((a, b) => a - b), `${lang}: card parts are out of order`);
      assert.ok(card.includes('data-open-catalog') && / href="\/catalogs\/[^"]+\.pdf" download/.test(card),
        `${lang}: a card is missing the open or download button`);
    }
  }
});

test('Titles lose the brand and the boilerplate but keep the printed one as a tooltip', async () => {
  const html = await page('ru');
  for (const catalog of catalogs) {
    const short = shortCatalogTitle(catalog.title.ru);
    assert.ok(html.includes(`<h2 title="${catalog.title.ru.replaceAll('&', '&amp;')}">${short}</h2>`),
      `${catalog.id}: expected the short title "${short}" with the full one as the tooltip`);
    assert.ok(!/каталог продукции$/i.test(short), `${catalog.id}: the tail is still there`);
  }
  // A title that is nothing but the brand is left alone rather than emptied,
  // and one that is brand plus boilerplate keeps the boilerplate, since that
  // is all the card would otherwise have to show.
  assert.equal(shortCatalogTitle('CONMED'), 'CONMED');
  assert.equal(shortCatalogTitle('Double Medical — каталог продукции'), 'Каталог продукции');
});

test('Only the first five products are shown, and long lists scroll', async () => {
  const html = await page('ru');
  for (const [index, card] of cards(html).entries()) {
    const catalog = catalogs[index];
    const items = (card.match(/<li/g) || []).length;
    const hidden = (card.match(/data-extra-item hidden/g) || []).length;
    assert.equal(items, catalog.systems.length, `${catalog.id}: every product should be in the page`);
    assert.equal(hidden, Math.max(0, catalog.systems.length - 5), `${catalog.id}: all but five should start hidden`);
    assert.equal(card.includes('data-expand-catalog'), catalog.systems.length > 5, `${catalog.id}: expand button`);
    assert.equal(card.includes('library-items--scroll'), catalog.systems.length > 30, `${catalog.id}: scrolling list`);
  }
});

test('Each card links to the catalog page filtered to its own PDF', async () => {
  for (const [lang, prefix] of [['ru', ''], ['en', '/en']]) {
    const html = await page(lang);
    for (const catalog of catalogs) {
      assert.ok(html.includes(`href="${prefix}/catalog/?catalog=${catalog.id}#catalog-results"`), `${lang}: ${catalog.id}`);
    }
  }
  // And the products carry the ids that filter answers to.
  const listing = await fs.readFile('dist/catalog/index.html', 'utf8');
  const tagged = [...listing.matchAll(/data-catalogs="([^"]+)"/g)].flatMap(match => match[1].split(' '));
  assert.ok(tagged.length > 0, 'no product tile carries a catalog id');
  const known = new Set(catalogs.map(c => c.id));
  for (const id of new Set(tagged)) assert.ok(known.has(id), `a tile points at an unknown catalog: ${id}`);
});
