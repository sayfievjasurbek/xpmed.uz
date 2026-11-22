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
