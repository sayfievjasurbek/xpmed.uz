const header = document.querySelector('.site-header');
const desktopNav = header.querySelector('.desktop-nav');
const desktopQuery = window.matchMedia('(min-width: 1051px)');
const mobileMenu = document.querySelector('#mobile-menu');
const triggers = [...desktopNav.querySelectorAll('button[aria-controls]')];
let activeTrigger;
let openedByHover = false;

function setPanel(trigger, openFromHover = false) {
  if (activeTrigger && activeTrigger !== trigger) {
    activeTrigger.setAttribute('aria-expanded', 'false');
    document.getElementById(activeTrigger.getAttribute('aria-controls')).hidden = true;
  }

  activeTrigger = trigger;
  openedByHover = openFromHover;

  if (trigger) {
    trigger.setAttribute('aria-expanded', 'true');
    document.getElementById(trigger.getAttribute('aria-controls')).hidden = false;
  }
}

for (const trigger of triggers) {
  trigger.addEventListener('pointerenter', (event) => {
    if (event.pointerType === 'mouse' && desktopQuery.matches && activeTrigger !== trigger) {
      const focusedPanel = document.activeElement.closest('.mega-panel');
      if (!focusedPanel) setPanel(trigger, true);
    }
  });

  trigger.addEventListener('click', () => {
    setPanel(activeTrigger === trigger && !openedByHover ? undefined : trigger);
  });

  trigger.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowDown') return;
    event.preventDefault();
    setPanel(trigger);
    document.getElementById(trigger.getAttribute('aria-controls')).querySelector('a').focus();
  });
}

function closeHoverPanel(event) {
  const focusInPanel = document.activeElement.closest('.mega-panel');
  if (event.pointerType === 'mouse' && openedByHover && !focusInPanel) setPanel();
}

header.addEventListener('pointerleave', closeHoverPanel);
desktopNav.querySelector(':scope > a').addEventListener('pointerenter', closeHoverPanel);
header.querySelector('.header-actions').addEventListener('pointerenter', closeHoverPanel);

desktopNav.addEventListener('focusout', (event) => {
  if (!activeTrigger) return;
  const item = activeTrigger.closest('.nav-item');
  if (item.contains(event.target) && !item.contains(event.relatedTarget)) setPanel();
});

document.addEventListener('pointerdown', (event) => {
  if (!header.contains(event.target)) setPanel();
});

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape' || !activeTrigger) return;
  const trigger = activeTrigger;
  const hadFocus = trigger.closest('.nav-item').contains(document.activeElement);
  setPanel();
  if (hadFocus) trigger.focus();
});

desktopQuery.addEventListener('change', (event) => {
  if (event.matches && mobileMenu.open) mobileMenu.close();
  setPanel();
});

for (const opener of document.querySelectorAll('[data-open]')) {
  opener.addEventListener('click', () => {
    setPanel();
    document.getElementById(opener.dataset.open).showModal();
  });
}

for (const dialog of document.querySelectorAll('dialog')) {
  dialog.addEventListener('click', (event) => {
    if (event.target.closest('[data-close], a[href]')) dialog.close();
    else if (event.target === dialog && dialog !== mobileMenu) {
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom) {
        dialog.close();
      }
    }
  });
}

const search = document.querySelector('#search-dialog');
const field = search.querySelector('input');
const empty = search.querySelector('[data-search-empty]');
const status = search.querySelector('[data-search-status]');
const normalize = (value) => value.toLocaleLowerCase(document.documentElement.lang).replaceAll('ё', 'е');
const entries = [...search.querySelectorAll('[data-search-result]')].map((element) => ({
  element,
  label: normalize(element.textContent.replace(/\s+/g, ' ')),
}));

function filterSearch() {
  const terms = normalize(field.value.trim()).split(/\s+/).filter(Boolean);
  let count = 0;

  for (const { element, label } of entries) {
    const matches = terms.every((term) => label.includes(term));
    element.hidden = !matches;
    if (matches) count += 1;
  }

  empty.hidden = count > 0;
  status.textContent = terms.length ? status.dataset.count.replace('{count}', count) : '';
}

field.addEventListener('input', filterSearch);
field.addEventListener('keydown', (event) => {
  if (!['Enter', 'ArrowDown'].includes(event.key)) return;
  const first = search.querySelector('[data-search-result]:not([hidden]) a');
  if (!first) return;
  event.preventDefault();
  if (event.key === 'Enter') first.click();
  else first.focus();
});

search.addEventListener('close', () => {
  field.value = '';
  filterSearch();
});
