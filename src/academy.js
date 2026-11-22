// XPMED Academy page. Two jobs: mark each section as it scrolls into view so
// the CSS keyframes can run, and count the hero stats up once. Both are off
// under prefers-reduced-motion, and the markup already carries the final
// numbers, so without this script the page is simply static.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
// The hero is the largest contentful paint; it is never hidden and never
// animated in. Everything below it reveals on scroll.
const sections = document.querySelectorAll('.academy-page > section:not(.academy-hero)');

if (sections.length && 'IntersectionObserver' in window && !reducedMotion.matches) {
  for (const section of sections) section.classList.add('js-reveal');
  const reveal = new IntersectionObserver((entries) => {
    for (const { target, isIntersecting } of entries) {
      if (!isIntersecting) continue;
      reveal.unobserve(target);
      target.classList.add('is-in');
      // If the keyframes never run - a throttled tab, say - the section must
      // not stay invisible, so the hiding class comes off once they are due.
      setTimeout(() => target.classList.remove('js-reveal'), 2600);
    }
  }, { threshold: 0.12 });
  for (const section of sections) reveal.observe(section);
}

// The hero stats are on screen from the first paint, so they count straight
// away rather than waiting for a scroll.
if (!reducedMotion.matches) for (const value of document.querySelectorAll('[data-count-to]')) countUp(value);

function countUp(element) {
  const target = Number(element.dataset.countTo);
  const suffix = element.textContent.replace(/[\d\s]/g, '');
  if (!Number.isFinite(target) || element.dataset.counted) return;
  element.dataset.counted = '1';
  const duration = 1100;
  const start = performance.now();
  const step = (now) => {
    const progress = Math.min(1, (now - start) / duration);
    // The same expo-out the CSS uses, so the numbers settle with the section.
    const eased = 1 - Math.pow(1 - progress, 4);
    element.textContent = Math.round(target * eased) + suffix;
    if (progress < 1) requestAnimationFrame(step);
  };
  element.textContent = '0' + suffix;
  requestAnimationFrame(step);
}
