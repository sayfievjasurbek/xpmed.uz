export const SELECTION_KEY='xpmed.catalog-request.v1';
export function validSelection(value){
 if(!Array.isArray(value))return [];
 return value.filter(item=>item&&typeof item.id==='string'&&item.name&&typeof item.name.ru==='string'&&typeof item.name.en==='string'&&Array.isArray(item.codes)&&item.codes.length&&item.codes.every(c=>typeof c==='string'&&c.trim())).map(item=>({...item,quantity:Number.isSafeInteger(Number(item.quantity))&&Number(item.quantity)>0?Number(item.quantity):1})).filter((item,index,array)=>array.findIndex(other=>other.id===item.id)===index);
}
export function readSelection(storage){try{return validSelection(JSON.parse(storage.getItem(SELECTION_KEY)||'[]'));}catch{return [];}}
export function selectionMessage(items,lang,label){return items.length?label+'\n'+items.map(item=>(item.name[lang]||item.name.en)+' — '+item.codes.join(' / ')+' × '+item.quantity).join('\n'):'';}

// A formerly selectable source row can become unavailable after catalog review.
export function excludeUnavailableSelections(items, unavailableIds){const unavailable=new Set(unavailableIds);return items.filter(item=>!unavailable.has(item.id));}
