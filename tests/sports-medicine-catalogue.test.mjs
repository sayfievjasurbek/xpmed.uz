import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, access} from 'node:fs/promises';
import {loadSystems, validateSystem} from '../src/catalog-data.mjs';
import ru from '../src/i18n/catalog-ru.mjs';
import en from '../src/i18n/catalog-en.mjs';

const read = async path => JSON.parse(await readFile(path, 'utf8'));
const report = await read('reports/double-medical/sports-medicine-catalogue.json');
const profile = await read('scripts/profiles/double-medical-sports-medicine.json');
const all = await loadSystems();
const sports = profile.systems.map(entry => all.find(system => system.brand === 'double-medical' && system.slug === entry.slug));

test('Sports Medicine import is scoped, bilingual and published under source review or owner acceptance', async () => {
  assert.equal(sports.length, 16);
  assert.ok(sports.every(Boolean));
  assert.equal(sports.filter(system => system.status === 'published').length, 16);
  assert.equal(sports.filter(system => system.status === 'draft').length, 0);
  assert.equal(report.codesFound, 198);
  assert.equal(report.codesVerified, 198);
  assert.equal(report.distinctCodes, 196);
  for (const system of sports) {
    assert.deepEqual(validateSystem(system), []);
    assert.ok(system.sourcePages.every(page => page >= 4 && page <= 38));
    assert.ok(system.name.ru && system.name.en);
    assert.ok(ru.categories[system.category] && en.categories[system.category]);
    assert.ok(ru.subcategories[system.subcategory] && en.subcategories[system.subcategory]);
    assert.deepEqual(system.review.flags, []);
    if (system.status === 'published') {
      await access(`dist/catalog/double-medical/${system.slug}/index.html`);
      await access(`dist/en/catalog/double-medical/${system.slug}/index.html`);
    }
  }
});

test('Owner-published pages omit incomplete source cells and review language', async () => {
  assert.equal(report.openRealFlags.length, 0);
  assert.equal(report.acceptedSourceLimitations.length, 9);
  for (const system of sports) {
    for (const table of system.specTables) for (const row of table.rows) {
      assert.ok(!row.some(cell => typeof cell === 'object' && ['/ #', '/ # × мм', '/ # × mm', '—'].includes(cell.en)));
    }
    for (const lang of ['ru', 'en']) {
      const html = await readFile(`dist/${lang === 'en' ? 'en/' : ''}catalog/double-medical/${system.slug}/index.html`, 'utf8');
      assert.doesNotMatch(html, /check with manager|уточняйте у менеджера|\/ #|source-incomplete-|unreadable-source-/i);
    }
  }
  const peek = sports.find(system => system.slug === 'peek-suture-anchor-instruments');
  assert.deepEqual(peek.review.excludedUnnamedRefCodes, ['111036700', '111036800']);
  assert.ok(!peek.refCodes.includes('111036700'));
});

test('All printed REF occurrences retain independent reader evidence', async () => {
  const evidence = await read('reports/double-medical/sports-medicine-catalogue/code-verification.json');
  assert.equal(evidence.length, 198);
  assert.ok(evidence.every(row => row.verification.startsWith('verified')));
  assert.ok(evidence.every(row => row.readings.Vision && row.readings.PSM11));
  assert.equal(evidence.filter(row => row.verification.includes('visual')).length, 1);
  assert.equal(report.randomSample.length, 20);
  assert.ok(report.randomSample.every(row => row.pdfPage >= 4 && row.pdfPage <= 38 && /^\d{9}S?(?: \/ \d{9}S?)*$/.test(row.REF)));
});

test('M-Link stays a single published system with an additive instrument supplement', async () => {
  const slug = 'm-link-all-inside-meniscal-repair-system';
  const before = await read(`reports/double-medical/sports-medicine-catalogue/merge-backups/${profile.sha256}/${slug}.json`);
  const after = await read(`content/products/double-medical/${slug}.json`);
  for (const key of ['name', 'shortDescription', 'description', 'status', 'sourcePdf', 'sourcePages', 'variants', 'features', 'hotspots', 'heroImage']) assert.deepEqual(after[key], before[key]);
  assert.deepEqual(new Set(after.refCodes.filter(ref => !before.refCodes.includes(ref))), new Set(['114302000', '114301200']));
  assert.ok(after.refCodes.includes('151260000S'));
  assert.equal(after.status, 'published');
});
