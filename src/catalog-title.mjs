// Catalog titles as the library cards show them.
//
// The titles in the data are the full printed ones - "Double Medical Trauma
// Catalogue — каталог продукции" - and on a card the brand is already on the
// line above and every card ends in the same two words, so the eye has to
// walk past the boilerplate to reach the one word that differs. The card
// shows what is left after the brand and that tail come off, and keeps the
// printed title in the tooltip.
const TAIL = [
  /\s*[—–-]\s*каталог продукции\s*$/i,
  /\s*[—–-]\s*product catalog(ue)?\s*$/i,
  /\s*[—–-]\s*catalog(ue)?\s*$/i,
];

const BRANDS = ['Double Medical Technology', 'Double Medical', 'CONMED', 'Synimed', 'SPINENDOS', 'BIOTECHNI S.A.S.', 'BIOTECHNI', 'GE HealthCare'];

export function shortCatalogTitle(title) {
  let text = String(title || '').trim();
  for (const brand of BRANDS) {
    if (text.toLowerCase().startsWith(brand.toLowerCase())) {
      text = text.slice(brand.length).replace(/^\s*[—–-]\s*/, '').trim();
      break;
    }
  }
  for (const tail of TAIL) text = text.replace(tail, '').trim();
  if (!text) return String(title || '').trim();   // nothing but boilerplate: keep it
  return text[0].toUpperCase() + text.slice(1);
}
