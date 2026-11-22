// XPMED Academy. The page is built from i18n data in both languages and links
// out to a separate site, so the things worth guarding are: both routes exist
// and carry all seven sections, the copy is translated rather than copied,
// the contacts are XPMED's own (not the academy site's info@xpmed.uz), and the
// page is reachable from the navigation and the footer.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import ru from '../src/i18n/academy-ru.mjs';
import en from '../src/i18n/academy-en.mjs';

const page = lang => fs.readFile(`dist${lang === 'en' ? '/en' : ''}/academy/index.html`, 'utf8');
const sections = ['academy-hero', 'academy-about', 'academy-courses', 'academy-mission', 'academy-partners', 'academy-cta'];

test('Both academy routes are built with every section and no missing copy', async () => {
  for (const lang of ['ru', 'en']) {
    const html = await page(lang);
    for (const section of sections) assert.ok(html.includes(section), `${lang}: ${section} is missing`);
    assert.ok(!html.includes('undefined'), `${lang}: the page rendered "undefined"`);
    assert.ok(html.includes('/academy.css') && html.includes('/academy.js'), `${lang}: page assets are not linked`);
    assert.match(html, /<html lang="(ru|en)">/);
  }
});

test('Academy copy is translated, not duplicated, and the stats match', () => {
  assert.equal(ru.stats.length, en.stats.length);
  assert.deepEqual(ru.stats.map(s => s.value + s.suffix), ['8+', '15+', '100+', '20+']);
  assert.deepEqual(en.stats.map(s => s.value + s.suffix), ru.stats.map(s => s.value + s.suffix));
  assert.equal(ru.courses.items.length, 6);
  assert.equal(en.courses.items.length, ru.courses.items.length);
  for (const [key, value] of [['hero.text', [ru.hero.text, en.hero.text]], ['mission.text', [ru.mission.text, en.mission.text]], ['courses.intro', [ru.courses.intro, en.courses.intro]]]) {
    assert.notEqual(value[0], value[1], `${key} was left untranslated`);
    assert.ok(/[а-яё]/i.test(value[0]), `${key} is not Russian`);
    assert.ok(!/[а-яё]/i.test(value[1]), `${key} still has Russian in the English copy`);
  }
});

test('The academy links out to its own site and back to XPMED contacts', async () => {
  for (const lang of ['ru', 'en']) {
    const html = await page(lang);
    assert.ok(html.includes('href="https://xpmedacademy.com" target="_blank" rel="noopener"'), `${lang}: academy link`);
    assert.ok(html.includes('mailto:info@xpmed.com'), `${lang}: XPMED email`);
    assert.ok(!html.includes('info@xpmed.uz'), `${lang}: the academy site's address leaked in`);
    for (const tel of ['+998954766660', '+998773716660', '+998990226660']) assert.ok(html.includes('tel:' + tel), `${lang}: ${tel}`);
  }
});

test('Every page links to the academy from the navigation and the footer', async () => {
  for (const [lang, home, route] of [['ru', 'dist/index.html', '/academy/'], ['en', 'dist/en/index.html', '/en/academy/']]) {
    const html = await fs.readFile(home, 'utf8');
    const label = lang === 'ru' ? 'Академия' : 'Academy';
    assert.ok(html.includes(`class="nav-trigger" href="${route}">${label}`), `${lang}: top-level navigation link`);
    assert.ok(html.split('<footer').pop().includes(`href="${route}"`), `${lang}: footer link`);
  }
  // And the route the navigation points at is in the sitemap.
  const sitemap = await fs.readFile('dist/sitemap.xml', 'utf8');
  for (const route of ['/academy/', '/en/academy/']) assert.ok(sitemap.includes('https://www.xpmed.uz' + route), route);
});

test('Artwork that has not been supplied falls back instead of breaking', async () => {
  const html = await page('ru');
  const sources = [...html.matchAll(/<img[^>]+src="([^"]+)"/g)].map(m => m[1]);
  assert.ok(sources.length >= 5, `expected the page photographs, found ${sources.length}`);
  for (const src of sources) {
    assert.ok(src.startsWith('/images/academy/') || src.startsWith('/assets/'), `unexpected image source ${src}`);
    await fs.access('dist' + src);   // whatever it resolved to has to exist
  }
  // Both course photographs are the academy's own now, not a fallback.
  assert.ok(sources.filter(src => src.startsWith('/images/academy/course-')).length === 2,
    'the cadaver-course photographs are not the supplied ones');
});
