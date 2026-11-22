// A fresh clone has to build. Two Vercel deploys failed because files the
// build reads were on the developer's disk but not in the repository: first
// the Git LFS PDFs, then the catalog page scans a .gitignore rule had removed.
// Working locally proves nothing, so this checks what git actually carries.
import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs/promises';
import {loadSystems} from '../src/catalog-data.mjs';
import {publicProductContent} from '../src/public-product-content.mjs';
import {loadAboutData, clientLogo, certificateThumb, certificateDocument} from '../src/about-sections.mjs';

function trackedFiles() {
  try {
    return new Set(execFileSync('git', ['ls-files', 'public', 'catalogs-source'],
      {encoding: 'utf8', maxBuffer: 1 << 30}).split('\n').filter(Boolean));
  } catch { return null; }   // not a git checkout: nothing to assert
}

const slug = stem => stem.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 100);

async function referencedAssets() {
  const systems = (await loadSystems()).filter(s => s.status === 'published').map(publicProductContent);
  const assets = new Set();
  const collect = value => {
    if (typeof value === 'string' && /^\/(images\/products|catalogs)\//.test(value)) assets.add(value);
    else if (Array.isArray(value)) value.forEach(collect);
    else if (value && typeof value === 'object') Object.values(value).forEach(collect);
  };
  systems.forEach(collect);
  const about = await loadAboutData();
  for (const client of about.clients) assets.add(clientLogo(client.id));
  for (const record of about.certificates) { assets.add(certificateThumb(record.id)); assets.add(certificateDocument(record.id)); }
  return assets;
}

test('Every asset the build copies is in the repository, or restorable by the build', async () => {
  const tracked = trackedFiles();
  if (!tracked) return;

  // build.mjs recreates these from the tracked originals in catalogs-source/.
  const restorable = new Set();
  for (const brand of await fs.readdir('catalogs-source', {withFileTypes: true})) {
    if (!brand.isDirectory()) continue;
    for (const name of await fs.readdir(`catalogs-source/${brand.name}`)) {
      if (!name.toLowerCase().endsWith('.pdf')) continue;
      assert.ok(tracked.has(`catalogs-source/${brand.name}/${name}`), `catalogs-source/${brand.name}/${name} is not tracked`);
      restorable.add(`/catalogs/${brand.name}/${slug(name.replace(/\.pdf$/i, ''))}/source.pdf`);
    }
  }

  const missing = [...await referencedAssets()]
    .filter(asset => !tracked.has(`public${asset}`) && !restorable.has(asset));
  assert.deepEqual(missing.slice(0, 10), [],
    `${missing.length} referenced assets are missing from git, so a fresh clone cannot build`);
});

test('Tracked source PDFs are real PDFs or Git LFS pointers the build can resolve', async () => {
  const tracked = trackedFiles();
  if (!tracked) return;
  const pdfs = [...tracked].filter(path => path.startsWith('catalogs-source/') && path.endsWith('.pdf'));
  assert.ok(pdfs.length >= 14, `expected the source catalogs, found ${pdfs.length}`);

  let pointers = 0;
  for (const path of pdfs) {
    const handle = await fs.open(path);
    const head = Buffer.alloc(42);
    try { await handle.read(head, 0, 42, 0); } finally { await handle.close(); }
    const text = head.toString('latin1');
    if (text.startsWith('%PDF-')) continue;
    // A pointer is fine: build.mjs fetches the object and verifies its sha256.
    assert.ok(text.startsWith('version https://git-lfs.github.com/spec/v1'),
      `${path} is neither a PDF nor a Git LFS pointer`);
    pointers++;
  }
  // Whatever the checkout looks like, the build must end up with real PDFs.
  for (const path of pdfs) {
    const copy = `public/catalogs/${path.split('/')[1]}/${slug(path.split('/')[2].replace(/\.pdf$/i, ''))}/source.pdf`;
    const handle = await fs.open(copy);
    const head = Buffer.alloc(5);
    try { await handle.read(head, 0, 5, 0); } finally { await handle.close(); }
    assert.equal(head.toString('latin1'), '%PDF-', `${copy} is not a PDF after the build`);
  }
  assert.ok(pointers <= 3, `unexpected number of LFS pointers: ${pointers}`);
});
