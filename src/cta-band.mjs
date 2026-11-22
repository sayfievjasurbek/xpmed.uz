import {CONTACT_DIALOG_ID} from './contact-panel.mjs';
import {contact} from './navigation.mjs';
import {escape} from './html.mjs';

// The band that closes a page: catalog listings, product pages, the brand
// pages, About and the Academy. One component, so the ivory is defined once
// and a change lands everywhere. The Academy passes its own title, text and
// link; everything else takes the sales-desk default.
export function renderCtaBand(lang, t, options = {}) {
  const copy = t.catalog;
  const {
    id = 'cta-band-title',
    eyebrow = t.ctaBand.eyebrow,
    title = copy.contactTitle,
    text = copy.contactDescription,
    action = null,          // {href, label} for a link, otherwise the panel
    phone = contact.phone,
    tel = contact.tel,
  } = options;

  const button = action
    ? `<a class="button cta-band__action" href="${escape(action.href)}"${action.external ? ' target="_blank" rel="noopener"' : ''}>${escape(action.label)}</a>`
    : `<button class="button cta-band__action" type="button" data-open="${CONTACT_DIALOG_ID}" aria-haspopup="dialog">${escape(t.utilitySales)}</button>`;

  return `<section class="cta-band" aria-labelledby="${id}" data-cta-band>
    <div class="container cta-band__inner">
      <div class="cta-band__copy">
        <p class="eyebrow">${escape(eyebrow)}</p>
        <h2 id="${id}">${escape(title)}</h2>
        <p class="cta-band__text">${escape(text)}</p>
      </div>
      <div class="cta-band__actions">
        ${button}
        <a class="cta-band__phone" href="tel:${tel}">${escape(phone)}</a>
      </div>
    </div>
  </section>`;
}
