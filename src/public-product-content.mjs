// Editorial instructions belong in source records and local review, not sales pages.
const editorialNotice = /уточня(?:йте|ть)[^.!?\n]*(?:менеджер|производител)|(?:требует|требуется)\s+проверк[аи]|(?:проверка|проверьте)[^.!?\n]*(?:OCR|перевод)|(?:confirm|check|consult)[^.!?\n]*(?:manager|sales representative|account representative)|(?:awaiting|pending|needs?|requires?)\s+(?:manual\s+|translation\s+|OCR\s+)?(?:review|verification)/iu;
const noticeFields = new Set(['note', 'legend', 'cellNotes', 'reviewNotice']);
const internalFields = new Set(['review', 'rowSources', 'codeEvidence', 'sourceCorrections']);
const hiddenManufacturerPdfs = new Set([
 '/catalogs/double-medical/cynthia-knee-system/source.pdf',
 '/catalogs/double-medical/cynthia-revision-surgical-guide/source.pdf',
]);

function isEditorial(value) {
 if (typeof value === 'string') return editorialNotice.test(value);
 if (value && typeof value === 'object') return Object.values(value).some(isEditorial);
 return false;
}

export function publicProductContent(system) {
 if (system.status !== 'published') return system;
 function clean(value) {
  if (Array.isArray(value)) return value.map(clean);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.entries(value).flatMap(([key, entry]) => {
   if (key === 'sourcePdf' && hiddenManufacturerPdfs.has(entry)) return [];
   if (key === 'catalogImports' && Array.isArray(entry)) return [[key,entry.filter(item=>!hiddenManufacturerPdfs.has(item.sourcePdf)).map(clean)]];
   if (internalFields.has(key)) return [[key, entry]];
   if (['description', 'shortDescription'].includes(key) && isEditorial(entry)) {
    const prose = text => typeof text === 'string' ? text.split(/\n\s*\n/).filter(paragraph => !isEditorial(paragraph)).join('\n\n') : text;
    return [[key, typeof entry === 'string' ? prose(entry) : Object.fromEntries(Object.entries(entry).map(([lang, text]) => [lang, prose(text)]))]];
   }
   if (noticeFields.has(key)) {
    if (Array.isArray(entry)) return [[key, entry.filter(item => !isEditorial(item)).map(clean)]];
    if (isEditorial(entry)) return [];
   }
   return [[key, clean(entry)]];
  }));
 }
 return clean(system);
}
