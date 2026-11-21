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

const tabs = [...document.querySelectorAll('.product-tabs [role="tab"]')];

function selectTab(active) {
  if (active.getAttribute('aria-selected') === 'true') return;

  for (const tab of tabs) {
    const selected = tab === active;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    const panel = document.getElementById(tab.getAttribute('aria-controls'));
    panel.hidden = !selected;
    if (selected && !reducedMotion.matches) {
      for (const animation of panel.getAnimations()) animation.cancel();
      panel.animate([{ opacity: 0.5 }, { opacity: 1 }], { duration: 220, easing: 'ease-out' });
    }
  }
}

for (const [index, tab] of tabs.entries()) {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', (event) => {
    const nextIndex = {
      ArrowLeft: (index + tabs.length - 1) % tabs.length,
      ArrowRight: (index + 1) % tabs.length,
      Home: 0,
      End: tabs.length - 1,
    }[event.key];
    if (nextIndex === undefined) return;
    event.preventDefault();
    const next = tabs[nextIndex];
    selectTab(next);
    next.focus();
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
