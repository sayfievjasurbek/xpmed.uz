import {readFileSync} from 'node:fs';
import {brandName} from './i18n/discovery.mjs';
export const siteSettings = JSON.parse(readFileSync(new URL('../content/settings.json', import.meta.url), 'utf8'));
export const canonicalBrand = key => key === 'double' ? 'double-medical' : key === 'BIOTECHNI S.A.S.' ? 'biotechni' : key;
export function orderedBrands(keys, order = siteSettings.brandOrder) {
  const priority = new Map(order.map((key, i) => [canonicalBrand(key), i]));
  return [...new Set(keys)].sort((a,b) => (priority.get(canonicalBrand(a)) ?? Infinity) - (priority.get(canonicalBrand(b)) ?? Infinity) || brandName(a).localeCompare(brandName(b), 'en'));
}
export function newestProduct(products) {
  return products.filter(p => p.isNew).sort((a,b) => (Date.parse(b.publishedAt) || 0) - (Date.parse(a.publishedAt) || 0) || a.slug.localeCompare(b.slug))[0];
}
