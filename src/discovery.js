import {discovery} from '/discovery-i18n.js';
const lang=document.documentElement.lang==='en'?'en':'ru';
const d=discovery[lang];
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const search=document.querySelector('#search-dialog');
search.classList.add('global-search','section--dark');
const input=search.querySelector('input');
input.setAttribute('role','combobox');input.setAttribute('aria-expanded','false');input.placeholder=d.placeholder;input.setAttribute('aria-label',d.placeholder);input.setAttribute('aria-controls','global-search-results');
const results=search.querySelector('#global-search-results');results.className='global-search-results';results.setAttribute('role','listbox');results.setAttribute('aria-label',d.search);
const message=search.querySelector('.global-search__status');
const status=document.createElement('p');status.className='sr-only';status.setAttribute('role','status');search.append(status);
let engine,load,items,active=-1,links=[];
function ensureSearch(){return load??=Promise.all([import('/vendor/fuse.mjs'),fetch('/search-index.json').then(r=>{if(!r.ok)throw Error('Search index');return r.json();})]).then(([{default:Fuse},data])=>{items=data.items;engine=new Fuse(items,{keys:data.keys,threshold:.32,ignoreLocation:true,minMatchCharLength:1},Fuse.parseIndex(data.index));});}
function activate(index){active=index;input.setAttribute('aria-activedescendant',links[index].id);links.forEach((link,i)=>{link.classList.toggle('is-active',i===active);link.setAttribute('aria-selected',String(i===active));if(i===active)link.scrollIntoView({block:'nearest'});});}
let revision=0;
async function runSearch(){const ticket=++revision;active=-1;shown={systems:6,components:6,catalogs:6};const query=input.value.trim();results.replaceChildren();links=[];input.removeAttribute('aria-activedescendant');input.setAttribute('aria-expanded','false');message.hidden=false;message.textContent=query?d.loading:d.hint;status.textContent='';if(!query)return;
 try{await ensureSearch();if(ticket!==revision||!search.open)return;const matches=engine.search(query).map(x=>x.item);message.hidden=matches.length>0;message.textContent=d.empty;status.textContent=d.count+matches.length;
 cachedMatches=matches;drawSearch();
 }catch{if(ticket===revision)message.textContent=d.searchError;}}
let cachedMatches=[],shown={systems:6,components:6,catalogs:6};
function drawSearch(){const matches=cachedMatches;
 results.innerHTML=['systems','components','catalogs'].map(group=>{const list=matches.filter(item=>item.group===group).slice(0,shown[group]);return list.length?`<section data-search-group="${group}"><h3>${escape(d[group])}</h3><ul>${list.map(item=>`<li><a href="${escape(lang==='en'?item.url_en:item.url)}"><img src="${escape(item.thumbnail)}" alt="" loading="lazy"><span>${escape(item.name?.[lang]||item.name?.en)}<small>${item.brandLabel?escape(item.brandLabel)+' · ':''}${escape(item.categoryLabel?.[lang])}</small></span><span aria-hidden="true">↗</span></a></li>`).join('')}</ul>${matches.filter(item=>item.group===group).length>shown[group]?`<button class="search-more" type="button" data-search-more="${group}">${escape(d.more)}</button>`:''}</section>`:'';}).join('');links=[...results.querySelectorAll('a')];links.forEach((link,i)=>{link.id='search-option-'+i;link.setAttribute('role','option');link.setAttribute('aria-selected','false');});input.setAttribute('aria-expanded',String(links.length>0));
}
results.addEventListener('click',event=>{const button=event.target.closest('[data-search-more]');if(!button)return;const group=button.dataset.searchMore;shown[group]+=6;active=-1;input.removeAttribute('aria-activedescendant');drawSearch();(results.querySelector(`[data-search-more="${group}"]`)||results.querySelector(`[data-search-group="${group}"] a:last-of-type`))?.focus();});
input.addEventListener('input',runSearch);
search.addEventListener('keydown',event=>{if(event.key==='Escape')return;if(event.key==='ArrowDown'||event.key==='ArrowUp'){if(!links.length)return;event.preventDefault();activate(active<0?(event.key==='ArrowDown'?0:links.length-1):(active+(event.key==='ArrowDown'?1:-1)+links.length)%links.length);input.focus();}else if(event.key==='Enter'&&links.length&&event.target===input){event.preventDefault();links[Math.max(active,0)].click();}});
search.addEventListener('close',()=>{revision++;input.value='';input.removeAttribute('aria-activedescendant');input.setAttribute('aria-expanded','false');results.replaceChildren();links=[];message.textContent=d.hint;message.hidden=false;});
new MutationObserver(()=>{if(search.open){input.focus();ensureSearch().catch(()=>{});}}).observe(search,{attributes:true,attributeFilter:['open']});
const tabs=[...document.querySelectorAll('[data-library-brand]')];
for(const tab of tabs)tab.addEventListener('click',()=>{tabs.forEach(t=>{const selected=t===tab;t.setAttribute('aria-selected',selected);t.tabIndex=selected?0:-1;});document.querySelectorAll('[data-catalog-brand]').forEach(card=>card.hidden=tab.dataset.libraryBrand!=='all'&&card.dataset.catalogBrand!==tab.dataset.libraryBrand);});
for(const [i,tab]of tabs.entries())tab.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;tabs[n].focus();tabs[n].click();});
let viewer;
async function openCatalog(id,options){viewer??=import('/pdf-viewer.js');const module=await viewer;await module.openCatalog(id,options);}
for(const button of document.querySelectorAll('[data-open-catalog]'))button.addEventListener('click',()=>openCatalog(button.dataset.openCatalog));
for(const link of document.querySelectorAll('[data-open-pdf]'))link.addEventListener('click',event=>{
 if(!link.dataset.pdfViewOnly&&(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey))return;
 event.preventDefault();
 openCatalog(null,{page:Number(link.dataset.pdfPage)||1,catalog:{file:link.dataset.openPdf,title:{[lang]:link.dataset.pdfTitle},viewOnly:link.dataset.pdfViewOnly==='true'}});
});
const id=new URLSearchParams(location.search).get('catalog');if(id&&document.querySelector('.library-section'))openCatalog(id);

// Library cards: the first five products are in the page, the rest are
// hidden until asked for. The height animates from the measured height to
// the new one and is handed back to the layout when it settles, so a long
// list that scrolls inside the card keeps working.
for (const button of document.querySelectorAll('[data-expand-catalog]')) {
  const list = button.parentElement.querySelector('[data-catalog-items]');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  button.addEventListener('click', () => {
    const expanded = button.getAttribute('aria-expanded') === 'true';
    const from = list.getBoundingClientRect().height;
    for (const item of list.querySelectorAll('[data-extra-item]')) item.hidden = expanded;
    button.setAttribute('aria-expanded', String(!expanded));
    button.innerHTML = `${expanded ? button.dataset.showAll : button.dataset.collapse} <span aria-hidden="true">${expanded ? '↓' : '↑'}</span>`;
    if (reduced.matches) return;
    const to = list.getBoundingClientRect().height;
    const animation = list.animate([{height: from + 'px'}, {height: to + 'px'}],
      {duration: Math.min(420, 160 + Math.abs(to - from) * 0.35), easing: 'cubic-bezier(.16, 1, .3, 1)'});
    animation.addEventListener('finish', () => list.style.height = '');
  });
}
