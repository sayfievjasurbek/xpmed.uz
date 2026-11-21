export const catalogSlugs = {
  spinendos: 'spinendos/',
  all: '',
  double: 'double-medical/',
  conmed: 'conmed/',
  synimed: 'synimed/',
  new: 'new/',
  'BIOTECHNI S.A.S.': 'biotechni/',
  'ge-healthcare': 'ge-healthcare/',
};

export function homeRoute(lang) {
  return lang === 'en' ? '/en/' : '/';
}

export function catalogRoute(lang, scope = 'all', filters = {}) {
  const query = new URLSearchParams(filters).toString();
  const taxonomy=parseTaxonomyScope(scope);
  const path = taxonomy ? areaRoute(lang,taxonomy.area,taxonomy.subcategory) : homeRoute(lang) + 'catalog/' + catalogSlugs[scope];
  return query ? path + '?' + query + '#catalog-results' : path;
}

const categoryDestinations = {
  trauma: ['double', { category: 'trauma' }],
  hip: ['double', { category: 'joint-replacement' }],
  spineSystems: ['double', { category: 'spine' }],
  conmedImplants: ['conmed', { category: 'arthroscopy' }],
  knee: ['conmed', { subcategory: 'knee' }],
  shoulder: ['conmed', { subcategory: 'shoulder' }],
  cement: ['synimed', { category: 'bone-cements' }],
  needles: ['synimed', { q: 'cannula' }],
};

export const specialties = ['orthopedics', 'traumatology', 'spine', 'sports', 'surgery'];

export function destination(key, lang) {
  if (key === 'contacts') return homeRoute(lang) + 'contacts/';
  if (key === 'catalogs') return homeRoute(lang) + 'catalogs/';
  if (key === 'catalog') return catalogRoute(lang);
  if (key === 'brands') return homeRoute(lang)+'brands/';
  if (specialties.includes(key)) return catalogRoute(lang, 'all', { specialty: key });
  if (areaKeys.includes(key)) return areaRoute(lang,key);
  if (Object.hasOwn(catalogSlugs, key)) return catalogRoute(lang, key);
  if (Object.hasOwn(categoryDestinations, key)) return catalogRoute(lang, ...categoryDestinations[key]);
  if (key === 'certificates' || key === 'clients') return homeRoute(lang) + 'about/#' + key;
  if (key === 'partners') return homeRoute(lang) + 'contacts/#partnership';
  if (key === 'company') return homeRoute(lang) + 'about/';
  return homeRoute(lang) + 'contacts/';
}

export const brands = {
  double: ['trauma', 'hip', 'spineSystems'],
  conmed: ['conmedImplants', 'knee', 'shoulder'],
  synimed: ['cement', 'needles'],
};

export const about = ['company', 'certificates', 'clients', 'partners'];

export const contact = {
  phones: [
    { label: '+998 95 476 66 60', tel: '+998954766660' },
    { label: '+998 77 371 66 60', tel: '+998773716660' },
    { label: '+998 99 022 66 60', tel: '+998990226660' },
  ],
  phone: '+998 95 476 66 60',
  tel: '+998954766660',
  email: 'info@xpmed.com',
  website: 'https://www.xpmed.uz',
  coordinates: { latitude: 41.269680, longitude: 69.240328 },
};

export const socialLinks = {
  telegram: null,
  instagram: null,
  facebook: null,
  youtube: 'https://www.youtube.com/watch?v=E3vn7Gq2PFI',
};

export function brandCatalogRoute(lang,brand){if(['unassigned','unspecified'].includes(brand))return catalogRoute(lang);const key=brand==='double-medical'?'double':brand==='biotechni'?'BIOTECHNI S.A.S.':brand;return Object.hasOwn(catalogSlugs,key)?catalogRoute(lang,key):homeRoute(lang)+'catalog/'+encodeURIComponent(brand)+'/';}
import {areaKeys,areaRoute,parseTaxonomyScope} from './clinical-taxonomy.mjs';
