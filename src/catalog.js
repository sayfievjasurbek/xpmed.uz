import {facetGroups as groups, legacyCategoryAreas, pageSize, normalize, selectCatalog} from '/catalog-engine.js';
const form = document.querySelector('#catalog-filter-form');
const search = form.elements.q;
const checkboxes = [...form.querySelectorAll('input[type="checkbox"]')];
const results = document.querySelector('#catalog-results');
const count = document.querySelector('#catalog-results-count [data-count]');
const empty = document.querySelector('.catalog-empty');
const more = document.querySelector('.catalog-more');
const loadMore = more.querySelector('button');
const sort = document.querySelector('#catalog-sort');
const grid = document.querySelector('#catalog-products');
let limit = pageSize;

// ?catalog=<id> narrows the page to one PDF, which is how a library card
// links in. It is not a facet - there is no checkbox for it and it is not
// part of the filter form - so it is applied by leaving the other tiles out
// of the set the facets count over.
const sourceCatalog = new URLSearchParams(location.search).get('catalog');

// The rest of the tiles arrive later from catalog-products.html, so the
// test has to run wherever a tile comes from, not once at load: a tile from
// another catalog is taken out of the page entirely rather than hidden,
// because nothing on this page can bring it back.
const fromThisCatalog = (element) => {
  if (!sourceCatalog) return true;
  if ((element.dataset.catalogs || '').split(' ').includes(sourceCatalog)) return true;
  element.remove();
  return false;
};

const collectTiles=()=>[...document.querySelectorAll('#catalog-products .product-tile')]
  .filter(fromThisCatalog)
  .map((element) => ({
  element,
  name: element.dataset.name,
  isNew: element.dataset.new==='true',
  keywords: normalize(element.dataset.keywords),
  facets: {
    area: [element.dataset.area],
    brand: [element.dataset.brand],
    subcategory: [element.dataset.subcategory],
    type: [element.dataset.type],
    specialty: element.dataset.specialty.split(' '),
  },
}));
let tiles=collectTiles();

function selectedFilters() {
  const values = new FormData(form);
  return Object.fromEntries(groups.map((group) => [group, values.getAll(group)]));
}

function renderResults() {
  const {matches:matching,counts:facetCounts,total:matches} = selectCatalog(tiles, {filters:selectedFilters(),query:search.value,sort:sort.value,lang:document.documentElement.lang,limit});
  for(const tile of tiles)tile.element.hidden=true;
  const fragment=document.createDocumentFragment();
  for(const [index,tile]of matching.entries()){tile.element.hidden=index>=limit;fragment.append(tile.element);}
  grid.append(fragment);
  for(const input of checkboxes){const n=facetCounts[input.name].get(input.value)||0;const label=input.closest('label');label.hidden=n===0;label.querySelector('[data-facet-count]').textContent=n;}

  for(const fieldset of form.querySelectorAll('fieldset'))fieldset.hidden=fieldset.querySelectorAll('.catalog-option:not([hidden])').length<=1;
  count.textContent = count.dataset.count.replace('{count}', matches);
  empty.hidden = matches > 0;
  more.hidden = matches <= limit;
}

function restoreFilters() {
  const query = new URLSearchParams(location.search);
  search.value = query.get('q') ?? '';
  sort.value=['new','alphabet'].includes(query.get('sort'))?query.get('sort'):'default';
  for(const value of query.getAll('specialty'))if(['knee','shoulder'].includes(value)){query.append('subcategory',value);query.delete('specialty',value);}
  for(const value of query.getAll('category')){if(legacyCategoryAreas[value])query.append('area',legacyCategoryAreas[value]);query.delete('category',value);}
  // Brand facets are slugs now; older links carried the display label.
  if (query.getAll('brand').includes('BIOTECHNI S.A.S.')) { query.delete('brand', 'BIOTECHNI S.A.S.'); query.append('brand', 'biotechni'); }
  for (const input of checkboxes) {
    input.checked = query.getAll(input.name).includes(input.value);
  }
  limit = pageSize;
  renderResults();
  updateLanguageLinks();
}

function updateLanguageLinks() {
  for (const link of document.querySelectorAll('.languages a')) {
    const url = new URL(link.href);
    link.href = url.pathname + location.search + (location.search ? '#catalog-results' : '');
  }
}

function updateFilters() {
  const url = new URL(location.href);
  url.search = '';
  if (sourceCatalog) url.searchParams.set('catalog', sourceCatalog);
  if(sort.value!=='default')url.searchParams.set('sort',sort.value);
  if (search.value.trim()) url.searchParams.set('q', search.value.trim());
  for (const input of checkboxes) {
    if (input.checked) url.searchParams.append(input.name, input.value);
  }
  history.replaceState(null, '', url);
  limit = pageSize;
  renderResults();
  updateLanguageLinks();
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  updateFilters();
});
form.addEventListener('input', updateFilters);
sort.addEventListener('change',updateFilters);
form.addEventListener('reset',event=>{event.preventDefault();search.value='';sort.value='default';for(const input of checkboxes)input.checked=false;updateFilters();});
window.addEventListener('popstate', restoreFilters);

function focusResults() {
  results.focus({ preventScroll: true });
  results.scrollIntoView({ block: 'start' });
}

document.querySelector('[data-reset-catalog]').addEventListener('click', (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
  event.preventDefault();
  form.reset();
  updateFilters();
  focusResults();
});

loadMore.addEventListener('click', () => {
  const firstHidden = limit;
  limit += pageSize;
  renderResults();
  const shown = tiles.filter(({ element }) => !element.hidden);
  shown[firstHidden]?.element.querySelector('a').focus();
});

const mobileLayout = window.matchMedia('(max-width: 820px)');
const sidebar = document.querySelector('#catalog-sidebar');
const dialog = document.querySelector('#catalog-filters');
const mobileFilters = document.querySelector('#catalog-mobile-filters');

function placeFilters() {
  if (mobileLayout.matches) {
    mobileFilters.append(form);
  } else {
    if (dialog.open) dialog.close();
    sidebar.append(form);
  }
}

mobileLayout.addEventListener('change', placeFilters);
dialog.querySelector('[data-show-catalog]').addEventListener('click', () => {
  dialog.close();
  focusResults();
});
placeFilters();
// Scopes with no more than one page of products have no rest-of-tiles file.
(grid.hasAttribute('data-rest-tiles')
  ? fetch('catalog-products.html').then(response=>{
      if(!response.ok)throw Error('Catalog tiles could not be loaded');
      return response.text();
    })
  : Promise.resolve('')
).then(html=>{
  if(html){const template=document.createElement('template');template.innerHTML=html;grid.append(template.content);}
  tiles=collectTiles();
  restoreFilters();
}).catch(error=>{console.error(error);restoreFilters();});

for (const slideshow of document.querySelectorAll('[data-brand-slideshow]')) {
  const slides = [...slideshow.querySelectorAll('figure')];
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  if (slides.length < 2) continue;

  let active = 0;
  let timer;
  let fade;
  let hovered = slideshow.matches(':hover');

  function schedule() {
    clearTimeout(timer);
    const paused = hovered || document.hidden || motion.matches;
    if (paused) {
      fade?.pause();
    } else {
      fade?.play();
      timer = setTimeout(crossfade, 6000);
    }
  }

  function crossfade() {
    const outgoing = slides[active];
    const incoming = slides[(active + 1) % slides.length];
    incoming.hidden = false;
    incoming.style.zIndex = '1';
    fade = incoming.animate([{ opacity: 0 }, { opacity: 1 }], {
      duration: 1200,
      easing: 'ease-in-out',
    });
    timer = setTimeout(crossfade, 6000);
    fade.onfinish = () => {
      outgoing.hidden = true;
      incoming.style.zIndex = '';
      active = (active + 1) % slides.length;
      fade = undefined;
    };
  }

  slideshow.addEventListener('mouseenter', () => {
    hovered = true;
    schedule();
  });
  slideshow.addEventListener('mouseleave', () => {
    hovered = false;
    schedule();
  });
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', schedule);
  schedule();
}
