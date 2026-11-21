const label = value => String(value || '').normalize('NFKC').trim().toLocaleLowerCase();
export function isSelfComponent(system, component) {
  return component?.isProduct === true || ['ru','en'].some(lang => label(system.name?.[lang]) && label(system.name[lang]) === label(component.name?.[lang]));
}
export function hasSeparateComponents(system, components = []) {
  return components.length > 1 || (components.length === 1 && !isSelfComponent(system, components[0]));
}
export function isCompactSystem(system, views) {
  return !(system.variants?.length) && views.every(v => v.features.length < 3 && v.tables.length < 2 && (!hasSeparateComponents(system,v.components) || v.components.length < 3) && Math.max(...['ru','en'].map(lang => (v.description?.[lang] || '').length)) < 1600) && Boolean(system.legacyId || views.some(v => v.description?.ru || v.description?.en));
}
