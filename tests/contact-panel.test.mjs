// The site is static and has no endpoint. Nothing may look like it sends a
// message, and every "request" action must land on the shared contact panel.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {loadSystems} from '../src/catalog-data.mjs';

async function htmlFiles(dir = 'dist') {
  const out = [];
  for (const entry of await fs.readdir(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await htmlFiles(full));
    else if (entry.name.endsWith('.html')) out.push(full);
  }
  return out;
}

const PHONES = ['+998954766660', '+998773716660', '+998990226660'];
const PAGE_SAMPLE = [
  'dist/index.html', 'dist/en/index.html',
  'dist/catalog/index.html', 'dist/en/catalog/index.html',
  'dist/catalogs/index.html', 'dist/about/index.html', 'dist/contacts/index.html',
  'dist/brands/index.html', 'dist/404/index.html',
  'dist/catalog/conmed/cannulas/index.html', 'dist/en/catalog/conmed/cannulas/index.html',
];

test('No page pretends to send a request', async () => {
  const files = await htmlFiles();
  assert.ok(files.length > 1700, `expected the full build, found ${files.length} pages`);
  const offenders = {form: [], thanks: [], demo: [], submit: [], anchor: []};
  for (const file of files) {
    const html = await fs.readFile(file, 'utf8');
    if (html.includes('data-system-request')) offenders.form.push(file);
    if (html.includes('sp-thanks')) offenders.thanks.push(file);
    if (/Демонстрационная форма|Demo form/.test(html)) offenders.demo.push(file);
    if (html.includes('type="submit"')) offenders.submit.push(file);
    if (html.includes('href="#request"')) offenders.anchor.push(file);
  }
  for (const [kind, list] of Object.entries(offenders)) {
    assert.deepEqual(list, [], `${kind}: ${list.slice(0, 3).join(', ')}`);
  }
});

test('Every page carries the contact panel with the real contact details', async () => {
  for (const file of PAGE_SAMPLE) {
    const html = await fs.readFile(file, 'utf8');
    assert.ok(html.includes('id="contact-dialog"'), file);
    for (const tel of PHONES) assert.ok(html.includes(`href="tel:${tel}"`), `${file} is missing ${tel}`);
    assert.ok(html.includes('href="mailto:info@xpmed.com"'), file);
    const panel = html.slice(html.indexOf('id="contact-dialog"'), html.indexOf('</dialog>', html.indexOf('id="contact-dialog"')));
    assert.ok(/Солар|Solar Street/.test(panel), `${file} is missing the address`);
    assert.ok(!panel.includes('<form'), `${file} must not put a form in the panel`);
  }
});

test('Request actions open the panel, in both languages', async () => {
  for (const [file, price, contactUs] of [
    ['dist/catalog/conmed/cannulas/index.html', 'Запросить цену', 'Связаться с нами'],
    ['dist/en/catalog/conmed/cannulas/index.html', 'Request a quote', 'Contact us'],
  ]) {
    const html = await fs.readFile(file, 'utf8');
    const triggers = [...html.matchAll(/<button[^>]*data-open="contact-dialog"[^>]*>(.*?)<\/button>/g)]
      .map(match => match[1].replace(/<[^>]+>/g, '').trim());
    assert.ok(triggers.length >= 3, `${file}: ${triggers.length} triggers`);
    assert.ok(triggers.some(label => label.startsWith(price)), `${file}: no "${price}" trigger`);
    assert.ok(triggers.includes(contactUs), `${file}: no "${contactUs}" trigger`);
    // The sticky selection bar opens the same panel and asks for the list.
    assert.match(html, /data-open="contact-dialog"[^>]*data-request-selected/);
  }
});

test('The panel offers copy and mailto for the selected catalog numbers', async () => {
  const html = await fs.readFile('dist/catalog/conmed/cannulas/index.html', 'utf8');
  const panel = html.slice(html.indexOf('id="contact-dialog"'), html.indexOf('</dialog>', html.indexOf('id="contact-dialog"')));
  assert.ok(panel.includes('data-contact-selection'), 'selection block missing');
  assert.ok(panel.includes('data-contact-selection-list'), 'selection list missing');
  assert.ok(panel.includes('data-copy-selection'), 'copy button missing');
  assert.match(panel, /data-email-selection[^>]*|href="mailto:info@xpmed\.com"/);
  assert.ok(panel.includes('Скопировать список'), 'copy label missing');
  assert.ok(panel.includes('Отправить по email'), 'email label missing');
  const ui = JSON.parse(panel.match(/data-contact-ui>(.*?)<\/script>/s)[1]);
  for (const key of ['emailSubject', 'emailIntro', 'copied', 'copyFailed', 'selectionTitle']) {
    assert.equal(typeof ui[key], 'string', `${key} missing from the panel ui payload`);
    assert.ok(ui[key].trim(), `${key} is empty`);
  }
});

test('The retired form stays in the source for a future endpoint', async () => {
  const page = await fs.readFile('src/system-page.mjs', 'utf8');
  assert.ok(page.includes('retiredRequestForm'), 'the form markup should be kept, renamed');
  assert.ok(/RETIRED/.test(page), 'the retired form should say so');
  assert.ok(!page.includes('t.demo'), 'the demo note must be gone');
  const script = await fs.readFile('src/system.js', 'utf8');
  assert.ok(script.includes("root.querySelector('[data-system-request]')"), 'handler should be kept');
  const ru = await fs.readFile('src/i18n/system-ru.mjs', 'utf8');
  const en = await fs.readFile('src/i18n/system-en.mjs', 'utf8');
  for (const [name, text] of [['ru', ru], ['en', en]]) assert.ok(!/\bdemo:/.test(text), `demo string still in ${name}`);
});

test('Published systems with selectable codes all get the panel and the sticky bar', async () => {
  const systems = (await loadSystems()).filter(s => s.status === 'published');
  let withBar = 0;
  for (const system of systems) {
    const html = await fs.readFile(`dist/catalog/${system.brand}/${system.slug}/index.html`, 'utf8');
    assert.ok(html.includes('id="contact-dialog"'), `${system.slug} has no panel`);
    if (!html.includes('data-selection-bar')) continue;
    withBar++;
    assert.match(html, /data-open="contact-dialog"[^>]*data-request-selected/, `${system.slug} bar does not open the panel`);
  }
  assert.ok(withBar > 100, `expected many code catalogs, found ${withBar}`);
});
