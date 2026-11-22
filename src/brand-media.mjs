// Brand wordmarks. Most are white artwork drawn for a dark background, so on a
// light card they have to be inverted; Spinendos is full colour and must not be.
// renderBrandMark() is the only place that decides this.
export const brandMarks = {
  double: {file: '/assets/home/brand-double.webp', light: true},
  'double-medical': {file: '/assets/home/brand-double.webp', light: true},
  conmed: {file: '/assets/home/brand-conmed.webp', light: true},
  synimed: {file: '/assets/home/brand-synimed.webp', light: true},
  spinendos: {file: '/assets/home/brand-spinendos.webp', light: false},
  biotechni: {file: '/assets/home/brand-biotechni.webp', light: false},
  'ge-healthcare': {file: '/assets/home/brand-ge-healthcare.webp', light: false},
};

// `name` is already escaped by the caller's escape() when it reaches the alt.
export function renderBrandMark(brand, name, escape) {
  const mark = brandMarks[brand];
  if (!mark) return `<strong>${escape(name)}</strong>`;
  return `<img src="${mark.file}"${mark.light ? ' class="is-light-mark"' : ''} alt="${escape(name)}" loading="lazy" decoding="async">`;
}

export const brandMedia = {
  spinendos: {website: 'https://spinendos.com/', images: [], descriptionSource: 'https://en.spinendos.com.cn/about.html'},
  double: {
    website: 'https://www.double-medical.com/home_5.html',
    images: [
      {
        file: '/images/brands/double-medical/production-floor.webp',
        imageCaption: {
          ru: 'Производственный цех Double Medical',
          en: 'Double Medical production floor',
        },
        sourcePage: 'https://www.doublemedicalgp.com/about-us/',
      },
    ],
  },
  conmed: {
    website: 'https://www.conmed.com/',
    images: [
      {
        file: '/images/brands/conmed/largo-medical-education-center.webp',
        imageCaption: {
          ru: 'Учебный центр CONMED в Ларго, Флорида',
          en: 'CONMED Medical Education Center in Largo, Florida',
        },
        sourcePage: 'https://www.conmed.com/en/blog/articles/general/how-conmed-empowers-healthcare-providers',
      },
      {
        file: '/images/brands/conmed/clinical-education-session.webp',
        imageCaption: {
          ru: 'Обучение врачей в центре CONMED',
          en: 'Clinical education session at CONMED',
        },
        sourcePage: 'https://www.conmed.com/en/blog/articles/general/how-conmed-empowers-healthcare-providers',
      },
    ],
  },
  synimed: {
    website: 'https://www.synimed.com/',
    images: [
      {
        file: '/images/brands/synimed/biocomposites-research-laboratory.webp',
        imageCaption: {
          ru: 'Исследовательская лаборатория группы Biocomposites — владельца Synimed',
          en: 'Research laboratory of Biocomposites, Synimed’s parent group',
        },
        sourcePage: 'https://biocomposites.com/about/why-biocomposites/',
      },
      {
        file: '/images/brands/synimed/biocomposites-laboratory-team.webp',
        imageCaption: {
          ru: 'Специалисты лаборатории группы Biocomposites — владельца Synimed',
          en: 'Laboratory team at Biocomposites, Synimed’s parent group',
        },
        sourcePage: 'https://biocomposites.com/about/why-biocomposites/',
      },
    ],
  },
};
