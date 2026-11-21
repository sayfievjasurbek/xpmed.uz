// Native focus-visible heuristics are retained; pointer clicks never draw an outline.
document.addEventListener('pointerdown',()=>{document.documentElement.dataset.inputMode='pointer';},{capture:true});
document.addEventListener('keydown',event=>{if(event.key==='Tab'||event.key.startsWith('Arrow')||['Home','End','PageUp','PageDown'].includes(event.key))document.documentElement.dataset.inputMode='keyboard';},{capture:true});
const header = document.querySelector('.site-header');
const desktopNav = header.querySelector('.desktop-nav');
const desktopQuery = window.matchMedia('(min-width: 1051px)');
const mobileMenu = document.querySelector('#mobile-menu');
const triggers = [...desktopNav.querySelectorAll(':scope > .nav-item > button[aria-controls]')];
let activeTrigger;
let openedByHover = false;

for(const menu of document.querySelectorAll('.area-menu')){
  const tabs=[...menu.querySelectorAll('[role="tab"]')];
  const select=tab=>{for(const candidate of tabs){const active=candidate===tab;candidate.setAttribute('aria-selected',String(active));candidate.tabIndex=active?0:-1;document.getElementById(candidate.getAttribute('aria-controls')).hidden=!active;}};
  for(const tab of tabs){tab.addEventListener('pointerenter',event=>{if(event.pointerType==='mouse')select(tab)});tab.addEventListener('click',()=>select(tab));tab.addEventListener('keydown',event=>{if(!['ArrowDown','ArrowUp','Home','End'].includes(event.key))return;event.preventDefault();const index=tabs.indexOf(tab),next=event.key==='Home'?tabs[0]:event.key==='End'?tabs.at(-1):tabs[(index+(event.key==='ArrowDown'?1:-1)+tabs.length)%tabs.length];select(next);next.focus();});}
}

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
    if (event.target.closest('[data-close], a[href]:not([data-testimonial]):not([data-keep-dialog])')) dialog.close();
    else if (event.target === dialog && dialog !== mobileMenu) {
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom) {
        dialog.close();
      }
    }
  });
}
