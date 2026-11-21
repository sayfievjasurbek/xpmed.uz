const identity=s=>`${s.brand}/${s.slug}`;
const subcategories=s=>new Set([s.subcategory,...(s.subcategories||[])].filter(Boolean));
export function selectRelatedSystems(system,systems,limit=4){
 const current=identity(system),selected=[],seen=new Set([current]);
 const eligible=systems.filter(s=>identity(s)!==current&&(s.status==='published'||system.status==='draft'));
 const add=s=>{if(s&&!seen.has(identity(s))&&selected.length<limit){seen.add(identity(s));selected.push(s);}};
 // Explicit entries retain editorial order. Qualified brand/slug references also work.
 for(const ref of system.relatedSystemSlugs||[]){
  const key=typeof ref==='string'?ref:`${ref.brand||system.brand}/${ref.slug}`;
  add(eligible.find(s=>key.includes('/')?identity(s)===key:s.brand===system.brand&&s.slug===key)||eligible.find(s=>s.slug===key));
 }
 const subs=subcategories(system);
 for(const s of eligible)if([...subcategories(s)].some(k=>subs.has(k)))add(s);
 for(const s of eligible)if(system.category&&s.category===system.category)add(s);
 for(const s of eligible)if(s.brand===system.brand)add(s);
 return selected;
}
