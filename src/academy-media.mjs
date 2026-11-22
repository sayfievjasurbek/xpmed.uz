// Academy artwork. The photographs and club logos are dropped into
// content/academy/ and normalised into public/images/academy/ by
// scripts/prepare-academy-assets.py (see content/academy/README.md), which
// build.mjs copies into the site whole.
//
// Nothing here fails when a file has not been supplied yet: a photograph falls
// back to an existing XPMED photograph, and a logo that is missing is drawn as
// a monogram instead, so the page builds either way.
import {existsSync} from 'node:fs';

export const ACADEMY_IMAGES = new URL('../public/images/academy/', import.meta.url);

function resolve(name, fallback = null) {
  return existsSync(new URL(name + '.webp', ACADEMY_IMAGES)) ? '/images/academy/' + name + '.webp' : fallback;
}

// Photographs: the academy's own when supplied, otherwise XPMED's. The hero
// has no fallback photograph on purpose - every environment photograph the
// site owns is already on the homepage, and the academy hero should not be
// the same picture - so until content/academy/hero lands it is a designed
// gradient field instead (.academy-hero--designed in academy.css).
export const academyPhoto = {
  hero: () => resolve('hero'),
  about: () => resolve('about', '/assets/home/mission-clinicians.webp'),
  mission: () => resolve('mission', '/assets/home/surgery-suite.webp'),
  course: index => resolve('course-' + (index + 1), ['/assets/home/surgery-suite.webp', '/assets/home/hero-devices.webp'][index]),
};

export const clubLogo = id => resolve('clubs/' + id);
export const partnerLogo = id => resolve('partners/' + id);
