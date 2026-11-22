const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if ('IntersectionObserver' in window && !reducedMotion.matches) {
  const observer = new IntersectionObserver((entries) => {
    for (const { target, isIntersecting } of entries) {
      if (!isIntersecting) continue;
      observer.unobserve(target);
      if (reducedMotion.matches) continue;
      target.animate([
        { opacity: 0.65, transform: 'translateY(12px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 400, easing: 'ease-out' });
    }
  }, { threshold: 0.08 });
  for (const section of document.querySelectorAll('[data-reveal]')) observer.observe(section);
}

// Clinical-area tiles. The CSS holds the keyframes and the spring easing; the
// only job here is to mark the section once it comes into view, so the tiles
// are never hidden when scripting is off or motion is reduced.
const areasSection = document.querySelector('.home-areas');
if (areasSection && 'IntersectionObserver' in window && !reducedMotion.matches) {
  areasSection.classList.add('js-reveal');
  const reveal = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    reveal.disconnect();
    areasSection.classList.add('is-in');
    // The animations carry the tiles from opacity 0. If they never run - a
    // throttled background tab, a browser that skips them - the tiles must
    // not stay invisible, so the hiding class comes off once they are due.
    setTimeout(() => areasSection.classList.remove('js-reveal'), 2600);
  }, { threshold: 0.12 });
  reveal.observe(areasSection);
}

// Brand switcher above the area tiles. Every grid is already in the page; this only
// decides which one is shown, slides the underline and keeps ?brand= in the
// URL so a filtered view can be shared. The bar itself is hidden in the
// markup, so without this script the page keeps all eight area tiles.
const brandBar = document.querySelector('[data-brand-bar]');
if (brandBar) {
  const tabs = [...brandBar.querySelectorAll('[data-brand-tab]')];
  const grids = [...document.querySelectorAll('[data-brand-tiles]')];
  const lines = [...document.querySelectorAll('[data-brand-line]')];
  const underline = brandBar.querySelector('.brand-tabs__underline');
  const more = brandBar.querySelector('.brand-tabs__more');
  const moreLabel = brandBar.querySelector('[data-more-label]');
  const moreDefault = moreLabel?.textContent;
  const known = new Set(grids.map(grid => grid.dataset.brandTiles));
  let current = 'all';

  brandBar.hidden = false;

  const moveUnderline = (tab) => {
    const anchorEl = more?.contains(tab) ? more.querySelector('summary') : tab;
    const bar = brandBar.getBoundingClientRect();
    const box = anchorEl.getBoundingClientRect();
    underline.style.setProperty('--tab-x', `${box.left - bar.left}px`);
    underline.style.setProperty('--tab-width', `${box.width}px`);
  };

  const show = (brand, {push = true} = {}) => {
    if (!known.has(brand) || brand === current) return;
    const outgoing = grids.find(grid => !grid.hidden);
    const incoming = grids.find(grid => grid.dataset.brandTiles === brand);
    const swap = () => {
      for (const grid of grids) {
        grid.hidden = grid !== incoming;
        grid.classList.remove('is-leaving');
      }
      incoming.classList.remove('is-entering');
      void incoming.offsetWidth;          // restart the stagger
      incoming.classList.add('is-entering');
      for (const line of lines) line.hidden = line.dataset.brandLine !== brand;
    };
    if (outgoing && outgoing !== incoming && !reducedMotion.matches) {
      outgoing.classList.add('is-leaving');
      setTimeout(swap, 180);
    } else swap();

    current = brand;
    for (const tab of tabs) {
      const active = tab.dataset.brandTab === brand;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-pressed', String(active));
      if (active) moveUnderline(tab);
    }
    if (more) {
      const inMenu = more.querySelector(`[data-brand-tab="${CSS.escape(brand)}"]`);
      more.toggleAttribute('data-active', Boolean(inMenu));
      if (moreLabel) moreLabel.textContent = inMenu ? inMenu.textContent : moreDefault;
      more.open = false;
    }
    if (push) {
      const url = new URL(location.href);
      if (brand === 'all') url.searchParams.delete('brand'); else url.searchParams.set('brand', brand);
      history.replaceState(null, '', url);
    }
  };

  for (const tab of tabs) tab.addEventListener('click', () => show(tab.dataset.brandTab));
  // A brand named in the address wins over the default view.
  const requested = new URLSearchParams(location.search).get('brand');
  if (requested && known.has(requested)) show(requested, {push: false});
  else moveUnderline(tabs[0]);
  addEventListener('resize', () => {
    const active = tabs.find(tab => tab.dataset.brandTab === current);
    if (active) moveUnderline(active);
  });
}

const testimonials = document.querySelector('#testimonials-dialog');
let activeVideo;

function stopVideo() {
  if (!activeVideo) return;
  const { frame, link } = activeVideo;
  frame.replaceChildren(link);
  activeVideo = undefined;
}

document.querySelector('[data-open="testimonials-dialog"]').addEventListener('click', stopVideo);
testimonials.addEventListener('close', stopVideo);

for (const link of document.querySelectorAll('[data-testimonial]')) {
  link.addEventListener('click', (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    stopVideo();
    const frame = link.closest('[data-video-frame]');
    const video = document.createElement('iframe');
    const { testimonial, videoTitle, watchLabel } = link.dataset;
    video.src = `https://www.youtube-nocookie.com/embed/${testimonial}?autoplay=1&hl=${document.documentElement.lang}`;
    video.title = videoTitle;
    video.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    video.referrerPolicy = 'strict-origin-when-cross-origin';
    video.allowFullscreen = true;
    const watch = document.createElement('a');
    watch.className = 'video-frame__fallback';
    watch.href = link.href;
    watch.textContent = watchLabel;
    frame.replaceChildren(video, watch);
    activeVideo = { frame, link };
    video.focus();
  });
}
