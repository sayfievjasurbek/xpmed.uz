// Shared pure catalog operations. The browser and scale tests use the same logic.
export const facetGroups = ['area', 'subcategory', 'brand', 'type', 'specialty'];
// The single category -> clinical area mapping. classifySystem() in
// clinical-taxonomy.mjs derives every system's area from this map, and
// build.mjs derives the /catalog/?category=... redirects from it, so a new
// category only ever has to be added here. It lives in this browser-safe
// module because src/catalog.js upgrades old ?category= links at runtime.
export const legacyCategoryAreas={
  'joint-replacement':'joint-replacement','arthroplasty-instrument-sets':'joint-replacement','trauma-implants':'trauma','trauma-instrument-sets':'trauma','spine-implants':'spine','spine-instrument-sets':'spine','endoscopic-spine-surgery':'spine',
  'sports-medicine':'sports-arthroscopy','sports-instrument-sets':'sports-arthroscopy',arthroscopy:'sports-arthroscopy','shoulder-arthroscopy':'sports-arthroscopy','knee-arthroscopy':'sports-arthroscopy','hip-arthroscopy':'sports-arthroscopy','small-joint-arthroscopy':'sports-arthroscopy','arthroscopy-resection':'sports-arthroscopy','arthroscopy-fluid-management':'sports-arthroscopy','arthroscopy-electrosurgery':'sports-arthroscopy','arthroscopy-manual-instruments':'sports-arthroscopy',
  'endoscopy-visualization':'endoscopy-visualization',imaging:'endoscopy-visualization','access-insufflation':'general-surgery','laparoscopic-instruments':'general-surgery','smoke-evacuation':'general-surgery',electrosurgery:'general-surgery','hall-powered-instruments':'powered-instruments','bone-cements':'bone-cements',spine:'spine',
};
export const pageSize = 24;
export const normalize = value => String(value || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replaceAll('ё', 'е');
export function selectCatalog(tiles, { filters = {}, query = '', sort = 'default', lang = 'ru', limit = pageSize } = {}) {
  const terms = normalize(query).split(/\s+/).filter(Boolean);
  const passes = (tile, except) => terms.every(term => tile.keywords.includes(term)) && facetGroups.every(group => group === except || !filters[group]?.length || filters[group].some(value => tile.facets[group].includes(value)));
  const matches = tiles.filter(tile => passes(tile));
  if (sort === 'new') matches.sort((a, b) => Number(b.isNew) - Number(a.isNew));
  if (sort === 'alphabet') matches.sort((a, b) => a.name.localeCompare(b.name, lang));
  const counts = Object.fromEntries(facetGroups.map(group => [group, new Map()]));
  for (const group of facetGroups) for (const tile of tiles) if (passes(tile, group)) for (const value of new Set(tile.facets[group])) if (value) counts[group].set(value, (counts[group].get(value) || 0) + 1);
  return { matches, visible: matches.slice(0, limit), counts, total: matches.length, hasMore: matches.length > limit };
}
// Deduplicate repeated table values and prose, and omit image/source metadata.
export function catalogSearchText(system) {
  const values = new Set();
  const visit = value => {
    if (typeof value === 'string' && value && !/^\/(?:assets|images|catalogs)\//.test(value)) values.add(value);
    else if (typeof value === 'number') values.add(String(value));
    else if (Array.isArray(value)) value.forEach(visit);
    else if (value && typeof value === 'object') for (const [key, entry] of Object.entries(value)) if (!['image','images','heroImage','gallery','hotspots','id','sourcePages','sourcePdf','componentId','imageType','review','rowSources','codeEvidence','sourceBounds','pdfPage','printedPage','path','coordinateSpace','imageDimensions','sourcePageImages','sourcePageDimensions'].includes(key)) visit(entry);
  };
  visit([system.description,system.shortDescription,system.features,system.components,system.specTables,system.referenceTables,system.surgicalTechnique,system.variants,system.refCodes]);
  return [...values].join(' ');
}

export function matchesDimensionFilters(row,filters){
 const canonical=value=>/^\d+(?:[.,]\d+)?$/.test(String(value))?String(Number(String(value).replace(',','.'))):String(value||'');
 return Object.entries(filters).every(([field,values])=>!values.length||values.includes(canonical(row?.[field])));
}
