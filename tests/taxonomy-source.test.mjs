// legacyCategoryAreas is the one category -> area mapping. classifySystem()
// derives every area from it and build.mjs derives every redirect from it, so
// a category can never exist in one place and be missing from another.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSystems} from '../src/catalog-data.mjs';
import {classifySystem, legacyCategoryAreas, systemOverrides, clinicalAreas, areaKeys} from '../src/clinical-taxonomy.mjs';

const stub = (category, extra = {}) => ({brand: 'brand', slug: 'slug', category, specialty: [], name: {ru: '', en: ''}, ...extra});

test('Every known category maps to a real clinical area and a real subcategory', () => {
  const categories = Object.keys(legacyCategoryAreas);
  assert.ok(categories.length >= 27, `only ${categories.length} categories`);
  for (const category of categories) {
    const area = legacyCategoryAreas[category];
    assert.ok(clinicalAreas[area], `${category} -> "${area}" is not a clinical area`);
    const taxonomy = classifySystem(stub(category));
    assert.equal(taxonomy.area, area, `${category}: classifySystem disagrees with the map`);
    assert.ok(clinicalAreas[area].subcategories.includes(taxonomy.subcategory),
      `${category} -> subcategory "${taxonomy.subcategory}" is not in ${area}`);
    assert.ok(['implants', 'instruments', 'equipment'].includes(taxonomy.type), `${category}: bad type`);
  }
});

test('Every category used by a published system is in the map', async () => {
  const systems = (await loadSystems()).filter(s => s.status === 'published');
  const used = [...new Set(systems.map(s => s.category))];
  for (const category of used) {
    assert.ok(category in legacyCategoryAreas, `category "${category}" is used but unmapped`);
  }
  for (const system of systems) {
    const taxonomy = classifySystem(system);
    assert.ok(areaKeys.includes(taxonomy.area), `${system.brand}/${system.slug} has no area`);
  }
});

test('Every category has a redirect in both languages', async () => {
  const redirects = await fs.readFile('dist/_redirects', 'utf8');
  const sources = new Set(redirects.split('\n').filter(Boolean).map(line => line.split(' ')[0]));
  for (const [category, area] of Object.entries(legacyCategoryAreas)) {
    for (const prefix of ['', '/en']) {
      const from = `${prefix}/catalog/?category=${category}`;
      assert.ok(sources.has(from), `no redirect for ${from}`);
      const target = redirects.split('\n').find(line => line.startsWith(from + ' '));
      assert.ok(target.includes(`${prefix}/catalog/${area}/`), `${from} does not land in ${area}: ${target}`);
    }
  }
});

test("Category 'spine' goes to the Spine area, and the cannula keeps its own mapping", async () => {
  // The trap this replaces: 'spine' used to send every future import to Bone cements.
  assert.equal(legacyCategoryAreas.spine, 'spine');
  assert.equal(classifySystem(stub('spine')).area, 'spine');

  const override = systemOverrides['synimed/synicem-vertebroplasty-cannula'];
  assert.deepEqual(override, {area: 'bone-cements', subcategory: 'cement-instruments', type: 'instruments'});

  const systems = await loadSystems();
  for (const key of Object.keys(systemOverrides)) {
    assert.ok(systems.some(s => `${s.brand}/${s.slug}` === key), `override ${key} has no system`);
  }
  const cannula = systems.find(s => s.slug === 'synicem-vertebroplasty-cannula');
  assert.equal(cannula.category, 'spine');
  assert.deepEqual(classifySystem(cannula), override);
});

test('A renamed system keeps its old URL working in both languages', async () => {
  const systems = await loadSystems();
  const redirects = await fs.readFile('dist/_redirects', 'utf8');
  const renamed = systems.filter(s => s.previousSlugs?.length);
  assert.ok(renamed.length >= 1, 'expected at least one renamed system');
  for (const system of renamed) {
    for (const previous of system.previousSlugs) {
      assert.ok(!/[^a-z0-9-]/.test(previous), `${previous} is not a safe slug`);
      for (const [prefix, lang] of [['', 'ru'], ['/en', 'en']]) {
        const line = `${prefix}/catalog/${system.brand}/${previous}/ ${prefix}/catalog/${system.brand}/${system.slug}/ 301`;
        assert.ok(redirects.includes(line), `missing ${lang} redirect:\n${line}`);
      }
    }
  }
  // The Uzbek slug is gone from the built site.
  await assert.rejects(fs.access('dist/catalog/synimed/vertebroplastiya-uchun-sinicem-steril-punching-kanulasi/index.html'));
  await fs.access('dist/catalog/synimed/synicem-vertebroplasty-cannula/index.html');
  await fs.access('dist/en/catalog/synimed/synicem-vertebroplasty-cannula/index.html');
});
