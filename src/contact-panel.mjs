// One contact panel for the whole site. No form and no endpoint: every
// "request" action opens this panel so nothing can appear to send a message
// that is never delivered. The retired request form stays in
// src/system-page.mjs and src/system.js, unused, for a future real endpoint.
import {contact} from './navigation.mjs';
import {escape as e} from './html.mjs';
import {icon} from './icons.mjs';

export const CONTACT_DIALOG_ID = 'contact-dialog';

// Strings the browser needs for the clipboard and mailto actions. Kept beside
// the panel so every page carries them, in its own language.
const uiKeys = ['emailSubject', 'emailIntro', 'copied', 'copyFailed', 'selectionTitle'];

export function renderContactPanel(lang, t) {
  const c = t.contactPanel;
  const labels = t.info;
  const row = (label, body) => `<div class="contact-panel__row"><span class="contact-panel__label">${e(label)}</span><div class="contact-panel__value">${body}</div></div>`;
  const ui = JSON.stringify(Object.fromEntries(uiKeys.map(key => [key, c[key]]))).replaceAll('<', '\\u003c');
  return `<dialog class="dialog contact-panel" id="${CONTACT_DIALOG_ID}" aria-labelledby="contact-panel-title">
    <div class="dialog-heading">
      <h2 id="contact-panel-title">${e(c.title)}</h2>
      <button class="icon-button" type="button" aria-label="${e(t.close)}" data-close>${icon('close')}</button>
    </div>
    <p class="contact-panel__intro">${e(c.intro)}</p>
    <div class="contact-panel__rows">
      ${row(labels.phonesLabel, contact.phones.map(p => `<a href="tel:${e(p.tel)}">${e(p.label)}</a>`).join(''))}
      ${row(labels.emailLabel, `<a href="mailto:${e(contact.email)}">${e(contact.email)}</a>`)}
      ${row(labels.addressLabel, `<address>${t.address.map(e).join('<br>')}</address>`)}
      ${row(labels.hoursLabel, `<span>${t.homepage.office.schedule.map(e).join('<br>')}</span>`)}
    </div>
    <section class="contact-panel__selection" data-contact-selection hidden>
      <h3>${e(c.selectionTitle)}</h3>
      <ul class="contact-panel__items" data-contact-selection-list></ul>
      <div class="contact-panel__actions">
        <button class="button" type="button" data-copy-selection>${e(c.copyList)}</button>
        <a class="button contact-panel__email" href="mailto:${e(contact.email)}" data-email-selection>${e(c.emailList)}</a>
      </div>
      <p class="contact-panel__status" role="status" aria-live="polite" data-selection-status></p>
    </section>
    <script type="application/json" data-contact-ui>${ui}</script>
  </dialog>`;
}
