import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems} from '../src/catalog-data.mjs';
import {renderSystem} from '../src/system-page.mjs';

const systems = await loadSystems();
const instability = systems.find(s => s.slug === 'shoulder-arthroscopy-instability-repair');
const blades = systems.find(s => s.slug === 'arthroscopy-resection-large-hub-shaver-blades');
const rows = s => s.specTables.flatMap(t => t.rows);

test('Blue-suture correction preserves the printed source evidence and adjacent ribbon code', () => {
  const table = instability.specTables.find(t => t.rows.some(row => row.includes('Y1802A')));
  const i = table.rows.findIndex(row => row.includes('Y1802A'));
  assert.match(table.rows[i][0].en, /blue suture/);
  assert.match(table.rows[i][0].ru, /синяя нить/);
  const evidence = table.rowSources[i].codeEvidence[0];
  assert.equal(evidence.printedCode, 'Y1802');
  assert.equal(evidence.value, 'Y1802A');
  assert.equal(evidence.verificationStatus, 'confirmed in CONMED brochure');
  assert.equal(evidence.visualReading.value, 'Y1802');
  assert.ok(instability.refCodes.includes('Y1802R'));
  assert.ok(!instability.refCodes.includes('Y1802'));
  assert.ok(!instability.components.some(c => c.refCodes.includes('Y1802')));
});

test('Shaver footnote markers cannot become duplicate selectable catalog numbers', () => {
  const published = systems.filter(s => s.status === 'published');
  for (const [code, en, ru] of [['EL9299U', /Concave/, /вогнутый/], ['EL9299D', /Convex/, /выпуклый/]]) {
    const owners = published.filter(s => s.refCodes.includes(code));
    assert.equal(owners.length, 1);
    assert.ok(blades.relatedSystemSlugs.includes(`conmed/${owners[0].slug}`));
    const row = rows(owners[0]).find(row => row.includes(code));
    assert.match(row[0].en, en);
    assert.match(row[0].ru, ru);
  }
  assert.ok(published.every(s => s.refCodes.every(code => !/^EL9299[UD]\*/.test(code))));
});

test('Resolved systems are public while source-catalog correction notes remain internal', async () => {
  const corrections = JSON.parse(await fs.readFile('reports/conmed/arthroscopy-product-catalog/source-catalog-corrections.json'));
  assert.equal(corrections.length, 2);
  const index = JSON.parse(await fs.readFile('dist/catalog-index.json'));
  for (const s of [instability, blades]) {
    assert.equal(s.status, 'published');
    assert.deepEqual(s.review.flags, []);
    assert.ok(index.some(item => item.slug === s.slug));
    for (const lang of ['ru', 'en']) {
      const html = renderSystem(s, lang);
      for (const correction of corrections) assert.ok(!html.includes(correction.internalNote));
    }
  }
  const search = await fs.readFile('dist/search-index.json', 'utf8');
  assert.ok(!search.includes('confirm with XPMED sales'));
  assert.ok(!search.includes('missing footnote:'));
});
