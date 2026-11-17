const paths = {
  down: '<path d="m6 9 6 6 6-6"/>',
  arrow: '<path d="M4 12h15m-6-6 6 6-6 6"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  plus: '<path d="M5 12h14m-7-7v14"/>',
  pin: '<path d="M20 10c0 5-8 11-8 11s-8-6-8-11a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
  phone: '<path d="M8 3H4a1 1 0 0 0-1 1 17 17 0 0 0 17 17 1 1 0 0 0 1-1v-4l-5-2-2 2a12 12 0 0 1-6-6l2-2-2-5Z"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
  telegram: '<path fill="currentColor" stroke="none" d="M21.3 3.5 2.6 10.8c-.9.4-.8 1 .2 1.3l4.8 1.5 1.8 5.5c.2.6.5.8 1.1.3l2.5-2.4 5 3.7c.8.5 1.3.2 1.5-.7l3-15.2c.2-1-.3-1.7-1.2-1.3Zm-3.1 3.7-8.1 7.3-.3 3.1-1.4-4.4 9.3-5.9c.5-.3.7-.3.5-.1Z"/>',
  instagram: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.6" r="1" fill="currentColor" stroke="none"/>',
  facebook: '<path fill="currentColor" stroke="none" d="M14 22v-8.9h3l.5-3.4H14V7.5c0-1 .3-1.7 1.8-1.7h1.9v-3A25 25 0 0 0 15 2.6c-2.7 0-4.6 1.6-4.6 4.7v2.4H7.3v3.4h3.1V22H14Z"/>',
  youtube: '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path fill="currentColor" stroke="none" d="m10 9 5 3-5 3V9Z"/>',
};

export function icon(name) {
  return `<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">${paths[name]}</svg>`;
}
