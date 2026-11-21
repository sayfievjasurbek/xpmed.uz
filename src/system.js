import {matchesDimensionFilters} from './catalog-engine.js';
import {SELECTION_KEY,readSelection,validSelection,selectionMessage,excludeUnavailableSelections} from './catalog-selection.js';
const root = document.querySelector('[data-system-page]');
if (root) {
 if(window.parent!==window&&root.querySelector('[data-review-page]')){
  const sendSource=element=>{try{window.parent.postMessage({type:'xpmed-source',pdfPage:Number(element.dataset.reviewPage),sourceBounds:JSON.parse(element.dataset.reviewBounds),path:element.dataset.reviewPath},location.origin);}catch{}};
  root.addEventListener('click',event=>{const element=event.target.closest('[data-review-page]');if(!event.target.closest('a,button,input,select,textarea,label')&&element){event.preventDefault();sendSource(element);}});
  root.addEventListener('keydown',event=>{if(!['Enter',' '].includes(event.key))return;const element=event.target.closest('[data-review-page]');if(!event.target.closest('a,button,input,select,textarea,label')&&element){event.preventDefault();sendSource(element);}});
 }
 const reduce = matchMedia('(prefers-reduced-motion: reduce)');
 const header = document.querySelector('.site-header');
 const updateHeader = () => root.style.setProperty('--header-height', `${header?.getBoundingClientRect().height || 0}px`);
 updateHeader(); if (header && 'ResizeObserver' in window) new ResizeObserver(updateHeader).observe(header);
 const reveal = element => { if (element.dataset.revealed) return; element.dataset.revealed = 'true'; element.classList.add('sp-revealed'); if (element.matches('[data-exploded]')) element.classList.add('is-separated'); };
 if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => { for (const entry of entries) if (entry.isIntersecting) { reveal(entry.target); observer.unobserve(entry.target); } }, { threshold: .08 });
  for (const element of root.querySelectorAll('[data-reveal], [data-exploded]')) { if (!reduce.matches) element.classList.add('sp-reveal-ready'); observer.observe(element); }
 } else root.querySelectorAll('[data-reveal], [data-exploded]').forEach(reveal);
 reduce.addEventListener('change', () => { if (reduce.matches) root.querySelectorAll('.sp-reveal-ready').forEach(reveal); });
 for (const image of root.querySelectorAll('.sp-hero-image')) image.addEventListener('animationend', () => image.style.animation = 'none', { once: true });
 const buttons = [...root.querySelectorAll('[data-variant-select]')];
 const views = [...root.querySelectorAll('[data-variant-view]')];
 let active = views[0]?.dataset.variantView;
 function selectVariant(id, historyMode = 'none') {
  if (!views.some(v => v.dataset.variantView === id)) id = views[0]?.dataset.variantView;
  active = id;
  views.forEach(v => v.hidden = v.dataset.variantView !== id);
  root.querySelectorAll('[data-variant-hero]').forEach(v => v.hidden = v.dataset.variantHero !== id);
  buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.variantSelect === id)));
  root.querySelectorAll('[data-document-variant]').forEach(card=>card.hidden=card.dataset.documentVariant!==id);
  root.querySelectorAll('[data-reference-variant]').forEach(section=>section.hidden=section.dataset.referenceVariant!==id);
  const current = views.find(v => !v.hidden);
  root.querySelectorAll('[data-section-tab]').forEach(link => {
   const key = link.dataset.sectionTab, section = ['documents','refs'].includes(key) ? root.querySelector('#'+key) : current?.querySelector(`[data-section="${key}"]`) || (root.classList.contains('sp-compact') ? root.querySelector(`[data-section="${key}"]`) : null);
   link.hidden = !section || section.hidden; if (section) link.href = `#${section.id}`;
   link.removeAttribute('aria-current');
  });
  const variant = root.querySelector('[data-request-variant]'); if (variant) variant.value = buttons.find(b => b.dataset.variantSelect === id)?.dataset.variantName || '';
  document.querySelectorAll('.languages a').forEach(a => { const url = new URL(a.href); if (buttons.length) url.searchParams.set('variant', id); a.href = url.pathname + url.search; });
  if (historyMode !== 'none' && buttons.length) { const url = new URL(location.href); url.searchParams.set('variant', id); const hash = url.hash.slice(1); for (const key of ['overview','features','technique','components','sizes']) if (hash.startsWith(key+'-')) url.hash = key+'-'+id; history[historyMode+'State']({}, '', url); }
  requestAnimationFrame(() => root.querySelectorAll('[data-hotspot-view]').forEach(view=>drawConnector(view,false)));
 }
 selectVariant(new URLSearchParams(location.search).get('variant') || active);
 buttons.forEach(button => button.addEventListener('click', () => selectVariant(button.dataset.variantSelect, 'push')));
 addEventListener('popstate', () => selectVariant(new URLSearchParams(location.search).get('variant') || views[0]?.dataset.variantView));
 for (const gallery of root.querySelectorAll('[data-gallery]')) {
  const main = gallery.querySelector('.sp-gallery-main img');
  gallery.querySelectorAll('[data-gallery-image]').forEach(button => button.addEventListener('click', () => {
   main.classList.toggle('scene',button.dataset.galleryImageType==='scene');main.classList.toggle('cutout',button.dataset.galleryImageType!=='scene');
   const caption=gallery.querySelector('[data-gallery-caption]');if(caption)caption.textContent=button.dataset.galleryCaption||'';
   main.src = button.dataset.galleryImage; main.removeAttribute('width'); main.removeAttribute('height'); main.style.removeProperty('--native-w'); main.style.removeProperty('--native-h');
   main.onload = () => { main.style.setProperty('--native-w', main.naturalWidth+'px'); main.style.setProperty('--native-h', main.naturalHeight+'px'); };
   gallery.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  }));
 }
 function drawConnector(view, animate = true) {
  if (!view || view.closest('[hidden]')) return;
  const point = view.querySelector('.sp-hotspot-image:not([hidden]) .sp-hotspot[aria-pressed="true"]');
  const card = view.querySelector('.sp-feature[data-active="true"]');
  const svg = view.querySelector('svg'), path = svg?.querySelector('path');
  if (!point || !card || !path) { if (path) path.setAttribute('d',''); return; }
  const bounds = svg.getBoundingClientRect(), p = point.getBoundingClientRect(), c = card.getBoundingClientRect();
  const x1 = p.x + p.width/2 - bounds.x, y1 = p.y+p.height/2-bounds.y, x2=c.x-bounds.x, y2=c.y+Math.min(c.height/2,120)-bounds.y;
  path.setAttribute('d', `M${x1},${y1} L${(x1+x2)/2},${y1} L${x2},${y2}`);
  const length = path.getTotalLength(); path.style.strokeDasharray = length; path.style.transition = animate && !reduce.matches ? '' : 'none'; path.style.strokeDashoffset = reduce.matches || !animate ? '0' : String(length);
  requestAnimationFrame(() => path.style.strokeDashoffset = '0');
 }
 for (const view of root.querySelectorAll('[data-hotspot-view]')) {
  const points = [...view.querySelectorAll('[data-hotspot]')];
  function activate(id, changeAngle = false, bringCard = false) {
   if (changeAngle) { const p = points.find(p => p.dataset.hotspot === id); if (p) angle(p.closest('[data-hotspot-image]').dataset.hotspotImage, false); }
   view.querySelectorAll('[data-feature]').forEach(card => card.dataset.active = String(card.dataset.feature === id));
   points.forEach(point => point.setAttribute('aria-pressed', String(point.dataset.hotspot === id)));
   view.querySelectorAll('[data-select-feature]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.selectFeature === id)));
   if(bringCard)view.querySelector('.sp-feature[data-active="true"]')?.scrollIntoView({block:'nearest',behavior:reduce.matches?'instant':'smooth'});
   requestAnimationFrame(() => drawConnector(view));
  }
  function angle(id, selectFirst=true) {
   view.querySelectorAll('[data-hotspot-image]').forEach(image => image.hidden=image.dataset.hotspotImage!==id);
   view.querySelectorAll('[data-angle]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.angle===id)));
   if (selectFirst) { const point=view.querySelector('.sp-hotspot-image:not([hidden]) [data-hotspot]'); if(point)activate(point.dataset.hotspot); }
  }
  points.forEach(point => { for (const event of ['mouseenter','focus','click']) point.addEventListener(event,()=>activate(point.dataset.hotspot,false,event==='click')); });
  view.querySelectorAll('[data-select-feature]').forEach(button => button.addEventListener('click',()=>activate(button.dataset.selectFeature,true,true)));
  view.querySelectorAll('[data-angle]').forEach(button => button.addEventListener('click',()=>angle(button.dataset.angle)));
  const point=points[0]; if(point)activate(point.dataset.hotspot);
  view.querySelectorAll('img').forEach(image=>image.addEventListener('load',()=>drawConnector(view)));
 }
 let resizeFrame;
 addEventListener('scroll',()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>root.querySelectorAll('[data-hotspot-view]').forEach(view=>drawConnector(view,false)));},{passive:true});
 addEventListener('resize',()=>{ cancelAnimationFrame(resizeFrame); resizeFrame=requestAnimationFrame(()=>root.querySelectorAll('[data-hotspot-view]').forEach(view=>drawConnector(view,false))); });
 for(const table of root.querySelectorAll('table')) {
  let column=-1;
  table.addEventListener('pointerover',event=>{const cell=event.target.closest('td,th');if(!cell)return;const next=Number(cell.dataset.tableColumn??cell.cellIndex);if(next===column)return;column=next;for(const row of table.rows)for(const item of row.cells){const start=Number(item.dataset.tableColumn??item.cellIndex),span=Number(item.dataset.tableColspan||item.colSpan||1);item.classList.toggle('sp-column-hover',start<=column&&column<start+span);}});
  table.addEventListener('pointerleave',()=>{column=-1;table.querySelectorAll('.sp-column-hover').forEach(c=>c.classList.remove('sp-column-hover'));});
 }
 if('IntersectionObserver'in window){const spy=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting&&!entry.target.closest('[hidden]')){const key=entry.target.dataset.section;root.querySelectorAll('[data-section-tab]').forEach(link=>link.setAttribute('aria-current',String(link.dataset.sectionTab===key)));}},{rootMargin:'-20% 0px -65% 0px'});root.querySelectorAll('[data-section]').forEach(s=>spy.observe(s));}

 if(root.querySelector('[data-catalog-ui]')){
  const ui=JSON.parse(root.querySelector('[data-catalog-ui]').textContent),lang=root.lang||'ru';
  const allRows=[...root.querySelectorAll('[data-catalog-row]')],groups=[...root.querySelectorAll('[data-catalog-group]')];
  const links=[...root.querySelectorAll('[data-group-link]')];
  const announce=document.createElement('p');announce.className='lc-copy-status sr-only';announce.setAttribute('role','status');root.append(announce);
  function setGroup(id){links.forEach(link=>{if(link.dataset.groupLink===id)link.setAttribute('aria-current','true');else link.removeAttribute('aria-current');});root.querySelectorAll('[data-group-jump]').forEach(select=>select.value=id);}
  root.querySelectorAll('[data-group-jump]').forEach(select=>select.addEventListener('change',()=>{const target=document.getElementById(select.value);if(target){target.scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'start'});setGroup(target.id);}}));
  links.forEach(link=>link.addEventListener('click',()=>setGroup(link.dataset.groupLink)));
  let spyFrame;
  const spy=()=>{cancelAnimationFrame(spyFrame);spyFrame=requestAnimationFrame(()=>{const line=(header?.getBoundingClientRect().height||0)+160;const visible=groups.filter(g=>!g.hidden&&g.getBoundingClientRect().bottom>line);const current=visible.filter(g=>g.getBoundingClientRect().top<=line).at(-1)||visible[0];if(current)setGroup(current.id);});};
  addEventListener('scroll',spy,{passive:true});addEventListener('resize',spy);spy();
  const originals=new WeakMap();
  function highlight(cell,query){if(!originals.has(cell))originals.set(cell,[...cell.childNodes].map(n=>n.cloneNode(true)));cell.replaceChildren(...originals.get(cell).map(n=>n.cloneNode(true)));if(!query)return;const walker=document.createTreeWalker(cell,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);for(const node of nodes){const text=node.textContent,lower=text.toLocaleLowerCase(),fragment=document.createDocumentFragment();let from=0,index=lower.indexOf(query);if(index<0)continue;while(index>=0){fragment.append(text.slice(from,index));const mark=document.createElement('mark');mark.textContent=text.slice(index,index+query.length);fragment.append(mark);from=index+query.length;index=lower.indexOf(query,from);}fragment.append(text.slice(from));node.replaceWith(fragment);}}
  const activeDimensions={};
  function applyRowFilters(){const query=(root.querySelector('[data-catalog-row-search]')?.value||'').trim().toLocaleLowerCase();let count=0;for(const row of allRows){const name=row.dataset.rowNameRu+' '+row.dataset.rowNameEn+' '+row.dataset.rowCodes;row.hidden=!!query&&!name.toLocaleLowerCase().includes(query)||!matchesDimensionFilters(JSON.parse(row.dataset.rowDimensions||'{}'),activeDimensions);if(!row.hidden)count++;row.querySelectorAll('[data-searchable]').forEach(cell=>highlight(cell,query));}for(const group of groups){group.hidden=![...group.querySelectorAll('[data-catalog-row]')].some(row=>!row.hidden);links.filter(link=>link.dataset.groupLink===group.id).forEach(link=>link.hidden=group.hidden);root.querySelectorAll('[data-group-jump] option').forEach(option=>{if(option.value===group.id){option.hidden=group.hidden;option.disabled=group.hidden;}});}root.querySelector('[data-catalog-row-count]').textContent=ui.foundRows+': '+count;root.querySelector('[data-catalog-no-results]').hidden=!!count;spy();}
  root.querySelectorAll('[data-catalog-row-search]').forEach(input=>input.addEventListener('input',applyRowFilters));
  root.querySelectorAll('[data-dimension-filter]').forEach(button=>button.addEventListener('click',()=>{const field=button.dataset.dimensionFilter,value=button.dataset.dimensionValue;let values=activeDimensions[field]||[];values=value?(values.includes(value)?values.filter(v=>v!==value):[...values,value]):[];activeDimensions[field]=values;root.querySelectorAll('[data-dimension-filter]').forEach(b=>{if(b.dataset.dimensionFilter===field)b.setAttribute('aria-pressed',String(b.dataset.dimensionValue?values.includes(b.dataset.dimensionValue):!values.length));});applyRowFilters();}));
  root.querySelectorAll('[data-drawing-open]').forEach(button=>button.addEventListener('click',()=>{const dialog=button.closest('.sp-list-catalog').querySelector('[data-drawing-dialog]'),image=dialog.querySelector('img');image.src=button.dataset.drawingOpen;image.alt=button.dataset.drawingCaption;dialog.querySelector('figcaption').textContent=button.dataset.drawingCaption;dialog.showModal();}));
  root.querySelectorAll('[data-drawing-dialog]').forEach(dialog=>{dialog.querySelector('[data-drawing-close]').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});});
  root.querySelector('[data-catalog-row-count]').textContent=ui.foundRows+': '+allRows.length;
  root.querySelectorAll('[data-copy-code]').forEach(button=>button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(button.dataset.copyCode);button.classList.add('is-copied');button.title=ui.copiedCode;announce.textContent=ui.copiedCode+': '+button.dataset.copyCode;setTimeout(()=>{button.classList.remove('is-copied');button.title=ui.copyCode;},1600);}catch{announce.textContent=ui.copyFailed;}}));
  let storage;try{storage=localStorage;}catch{}
  let selection=storage?readSelection(storage):[];
  const form=root.querySelector('[data-system-request]'),message=form?.elements.message;let generated='';
  const selectedBox=root.querySelector('[data-selected-request]'),selectedList=root.querySelector('[data-selected-request-items]'),bar=root.querySelector('[data-selection-bar]');
  const hidden=document.createElement('input');hidden.type='hidden';hidden.name='selectedItems';form?.append(hidden);
  const persist=()=>{try{if(!storage)throw Error();storage.setItem(SELECTION_KEY,JSON.stringify(selection));}catch{announce.textContent=ui.selectionUnavailable;}};
  const unavailableIds=[...root.querySelectorAll('[data-catalog-select]:disabled')].map(box=>box.dataset.catalogSelect);
  function renderSelection(renderItems=true){
   const eligible=excludeUnavailableSelections(selection,unavailableIds);if(eligible.length!==selection.length){selection=eligible;persist();}
   bar.hidden=!selection.length;selectedBox.hidden=!selection.length;const count=selection.length,word=lang==='ru'?(count%10===1&&count%100!==11?ui.itemOne:count%10>=2&&count%10<=4&&(count%100<12||count%100>14)?ui.itemFew:ui.items):(count===1?ui.itemOne:ui.items);root.querySelector('[data-selection-count]').textContent=ui.selectedItems+': '+count+' '+word;
   root.querySelectorAll('[data-catalog-select]').forEach(box=>box.checked=!box.disabled&&selection.some(item=>item.id===box.dataset.catalogSelect));
   if(renderItems){selectedList.replaceChildren();for(const item of selection){const row=document.createElement('div');row.className='lc-request-item';const name=document.createElement('span');name.textContent=(item.name[lang]||item.name.en)+' · '+item.codes.join(' / ');const label=document.createElement('label');const caption=document.createElement('span');caption.textContent=ui.itemQuantity;const input=document.createElement('input');input.type='number';input.min='1';input.step='1';input.required=true;input.value=item.quantity;input.dataset.itemQuantity=item.id;input.setAttribute('aria-label',ui.itemQuantity+' '+(item.name[lang]||item.name.en));label.append(caption,input);const remove=document.createElement('button');remove.type='button';remove.className='lc-remove';remove.textContent='×';remove.dataset.removeSelection=item.id;remove.setAttribute('aria-label',ui.removeItem+' '+(item.name[lang]||item.name.en));row.append(name,label,remove);selectedList.append(row);}}
   const next=selectionMessage(selection,lang,ui.selectionMessage);
   if(message){const own=generated&&message.value.includes(generated)?message.value.replace(generated,'').trim():message.value.trim();message.value=[own,next].filter(Boolean).join('\n\n');generated=next;}
   hidden.value=JSON.stringify(selection);
  }
  root.querySelectorAll('[data-catalog-select]').forEach(box=>box.addEventListener('change',()=>{selection=selection.filter(item=>item.id!==box.dataset.catalogSelect);if(box.checked&&!box.disabled){const row=box.closest('[data-catalog-row]');selection.push({id:box.dataset.catalogSelect,name:{ru:row.dataset.rowNameRu,en:row.dataset.rowNameEn},codes:JSON.parse(row.dataset.rowCodes),quantity:1,system:root.dataset.systemSlug});}persist();renderSelection();}));
  selectedList.addEventListener('input',event=>{const input=event.target.closest('[data-item-quantity]');if(!input)return;const item=selection.find(item=>item.id===input.dataset.itemQuantity);if(item&&input.validity.valid&&Number.isSafeInteger(Number(input.value))&&Number(input.value)>0){item.quantity=Number(input.value);persist();renderSelection(false);}});
  selectedList.addEventListener('click',event=>{const button=event.target.closest('[data-remove-selection]');if(!button)return;selection=selection.filter(item=>item.id!==button.dataset.removeSelection);persist();renderSelection();});
  root.querySelector('[data-clear-selection]').addEventListener('click',()=>{selection=[];persist();renderSelection();});
  root.querySelector('[data-request-selected]').addEventListener('click',()=>{form.hidden=false;root.querySelector('.sp-thanks').hidden=true;renderSelection();});
  addEventListener('storage',event=>{if(event.key===SELECTION_KEY){try{selection=validSelection(JSON.parse(event.newValue||'[]'));renderSelection();}catch{}}});
  renderSelection();
 }
 root.querySelectorAll('[data-technique-step-link]').forEach(link=>link.addEventListener('click',event=>{const target=document.getElementById(link.dataset.techniqueStepLink);if(!target)return;event.preventDefault();const chapter=target.closest('details');if(chapter)chapter.open=true;history.replaceState({},'',link.getAttribute('href'));target.scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'start'});}));
 const techniqueHash=document.getElementById(location.hash.slice(1));if(techniqueHash?.classList.contains('sp-technique-step')){const chapter=techniqueHash.closest('details');if(chapter)chapter.open=true;requestAnimationFrame(()=>techniqueHash.scrollIntoView({block:'start'}));}
 if('IntersectionObserver'in window){const indexSpy=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting&&!entry.target.closest('[hidden]'))root.querySelectorAll('[data-technique-step-link]').forEach(link=>link.setAttribute('aria-current',String(link.dataset.techniqueStepLink===entry.target.id)));},{rootMargin:'-20% 0px -60% 0px'});root.querySelectorAll('.sp-technique-chapter .sp-technique-step').forEach(step=>indexSpy.observe(step));}
 const form=root.querySelector('[data-system-request]');
 form?.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity())return;console.log('XPMED product inquiry',Object.fromEntries(new FormData(form)));form.hidden=true;const thanks=root.querySelector('.sp-thanks');thanks.hidden=false;thanks.tabIndex=-1;thanks.focus({preventScroll:true});});
}
