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

// Clinical-area tiles fade up once with an 80ms stagger and the heading slides
// in from the left. Nothing is hidden in CSS, so without JS — or with reduced
// motion, which the guard above already respects — everything is simply there.
const areasSection = document.querySelector('.home-areas');
if (areasSection && 'IntersectionObserver' in window && !reducedMotion.matches) {
  const reveal = new IntersectionObserver((entries) => {
    for (const { target, isIntersecting } of entries) {
      if (!isIntersecting) continue;
      reveal.unobserve(target);
      if (reducedMotion.matches) continue;
      target.querySelector('[data-reveal-left]')?.animate([
        { opacity: 0, transform: 'translateX(-28px)' },
        { opacity: 1, transform: 'none' },
      ], { duration: 500, easing: 'ease-out', fill: 'backwards' });
      target.querySelectorAll('.area-tile').forEach((tile, index) => tile.animate([
        { opacity: 0, transform: 'translateY(22px)' },
        { opacity: 1, transform: 'none' },
      ], { duration: 420, delay: index * 80, easing: 'ease-out', fill: 'backwards' }));
    }
  }, { threshold: 0.15 });
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
