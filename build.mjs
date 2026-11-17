import { copyFile, cp, mkdir, writeFile } from 'node:fs/promises';
import { render } from './src/render.mjs';
import ru from './src/i18n/ru.mjs';
import en from './src/i18n/en.mjs';

const source = new URL('./src/', import.meta.url);
const output = new URL('./dist/', import.meta.url);

function translationKeys(value, prefix = '') {
  return Object.entries(value).flatMap(([key, entry]) => {
    const path = prefix + key;
    if (typeof entry === 'object') return translationKeys(entry, path + '.');
    return path + ':' + typeof entry;
  }).sort();
}

if (translationKeys(ru).join('\n') !== translationKeys(en).join('\n')) {
  throw new Error('Russian and English must define the same translation keys.');
}

await mkdir(new URL('en/', output), { recursive: true });
const year = new Date().getUTCFullYear();

await Promise.all([
  writeFile(new URL('index.html', output), render('ru', ru, year)),
  writeFile(new URL('en/index.html', output), render('en', en, year)),
  copyFile(new URL('styles.css', source), new URL('styles.css', output)),
  copyFile(new URL('client.js', source), new URL('client.js', output)),
  cp(new URL('assets/', source), new URL('assets/', output), { recursive: true }),
]);
