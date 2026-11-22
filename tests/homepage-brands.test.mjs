// The brand switcher over the homepage area tiles. Every brand's grid is
// rendered into the page and the script only decides which one is shown, so
// what matters here is that each grid holds the right areas, the right counts
// and links, that only the "all brands" grid is visible in the markup, and
// that the bar itself is hidden until the script unhides it - otherwise a
// visitor without JavaScript would be left with a row of dead buttons.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems, listing, legacyListing} from '../src/catalog-data.mjs';
import {publicProductContent} from '../src/public-product-content.mjs';
import ru from '../src/i18n/home-ru.mjs';
import en from '../src/i18n/home-en.mjs';

const page = lang => fs.readFile(`dist${lang === 'en' ? '/en' : ''}/index.html`, 'utf8');
const section = html => html.slice(html.indexOf('class="home-areas"'), html.indexOf('home-contact-strip'));
const grid = (html, brand) => {
  const start = html.indexOf(`data-brand-tiles="${brand}"`);
  assert.notEqual(start, -1, `no grid for ${brand}`);
  return html.slice(start, html.indexOf('<div class="area-tiles"', start + 1) + 1 || undefined);
};

const products = (await loadSystems()).filter(s => s.status === 'published')
  .map(publicProductContent).map(listing).map(legacyListing);
const brands = [...new Set(products.map(p => p.brand))].filter(b => !['unassigned', 'unspecified'].includes(b));

test('Every brand has its own grid and only "all brands" is visible without script', async () => {
  for (const lang of ['ru', 'en']) {
    const html = section(await page(lang));
    assert.match(html, /<div class="brand-tabs"[^>]*hidden>/, `${lang}: the bar must start hidden`);
    assert.ok(html.includes('data-brand-tiles="all"'), `${lang}: no all-brands grid`);
    for (const brand of brands) {
      assert.ok(html.includes(`data-brand-tiles="${brand}"`), `${lang}: no grid for ${brand}`);
      assert.ok(html.includes(`data-brand-tiles="${brand}" hidden`), `${lang}: ${brand}'s grid is not hidden`);
    }
    // The visible grid is the one with all eight clinical areas.
    assert.equal((grid(html, 'all').match(/class="area-tile"/g) || []).length, 8);
  }
});

test('A brand grid holds exactly the areas that brand sells into, with its own counts', async () => {
  const html = section(await page('ru'));
  for (const brand of brands) {
    const areas = new Map();
    for (const product of products.filter(p => p.brand === brand)) areas.set(product.area, (areas.get(product.area) || 0) + 1);
    const markup = grid(html, brand);
    assert.equal((markup.match(/class="area-tile"/g) || []).length, areas.size, `${brand}: tile count`);
    for (const [area, count] of areas) {
      assert.ok(markup.includes(`?area=${area}#catalog-results`), `${brand}: no tile linking to ${area}`);
      const plural = count % 10 === 1 && count % 100 !== 11 ? 'продукт'
        : count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14) ? 'продукта' : 'продуктов';
      assert.ok(markup.includes(`${count} ${plural}`), `${brand}/${area}: expected ${count} ${plural}`);
    }
    // The tab already names the brand, so the tiles do not repeat it.
    assert.ok(!markup.includes('area-tile__brands'), `${brand}: tiles still carry the brand line`);
  }
  // The all-brands grid is the one that keeps the brand line on the tile.
  assert.ok(grid(html, 'all').includes('area-tile__brands'));
});

test('Each brand gets a line with its mark, country and a link to its catalog', async () => {
  for (const [lang, copy] of [['ru', ru], ['en', en]]) {
    const html = section(await page(lang));
    for (const brand of brands) {
      const start = html.indexOf(`data-brand-line="${brand}"`);
      assert.notEqual(start, -1, `${lang}: no brand line for ${brand}`);
      const line = html.slice(start, start + 900);
      assert.ok(line.startsWith(`data-brand-line="${brand}" hidden`), `${lang}: ${brand}'s line is not hidden`);
      const profile = copy.brandFilter.profiles[brand];
      assert.ok(profile, `${lang}: ${brand} has no profile`);
      assert.ok(line.includes(profile.country) && line.includes(profile.text), `${lang}: ${brand} copy missing`);
    }
  }
});

test('Brand profiles are translated and cover every brand on the site', () => {
  assert.deepEqual(Object.keys(ru.brandFilter.profiles).sort(), Object.keys(en.brandFilter.profiles).sort());
  for (const brand of brands) assert.ok(ru.brandFilter.profiles[brand], `${brand} has no Russian profile`);
  for (const [brand, profile] of Object.entries(ru.brandFilter.profiles)) {
    assert.notEqual(profile.text, en.brandFilter.profiles[brand].text, `${brand} was left untranslated`);
    assert.ok(!/[а-яё]/i.test(en.brandFilter.profiles[brand].text), `${brand}: Russian in the English profile`);
  }
  assert.notEqual(ru.brandFilter.all, en.brandFilter.all);
});
