import {legacyCategoryAreas} from './catalog-engine.js';
export {legacyCategoryAreas};
export const productTypes=['implants','instruments','equipment'];

export const clinicalAreas={
  'joint-replacement':{
    label:{ru:'Эндопротезирование',en:'Joint replacement'},
    description:{ru:'Эндопротезы тазобедренного, коленного, плечевого суставов и лучевой кости.',en:'Hip, knee, shoulder and radial head replacement systems.'},
    subcategories:['hip','knee','shoulder','radius','instruments'],
  },
  trauma:{
    label:{ru:'Травматология',en:'Trauma'},
    description:{ru:'Пластины, винты, интрамедуллярные системы и аппараты внешней фиксации.',en:'Plates, screws, intramedullary systems and external fixation.'},
    subcategories:['plates-fixation','screws','nails','external-fixation','pediatric','patella','instruments'],
  },
  spine:{
    label:{ru:'Хирургия позвоночника',en:'Spine'},
    description:{ru:'Импланты, малоинвазивные и эндоскопические системы для хирургии позвоночника.',en:'Implants, minimally invasive and endoscopic systems for spine surgery.'},
    subcategories:['cervical','thoracolumbar','minimally-invasive','sacroiliac','mesh','endoscopic-spine','instruments'],
  },
  'sports-arthroscopy':{
    label:{ru:'Спортивная медицина и артроскопия',en:'Sports medicine & arthroscopy'},
    description:{ru:'Артроскопия, фиксация мягких тканей, резекция и управление жидкостью.',en:'Arthroscopy, soft-tissue fixation, resection and fluid management.'},
    subcategories:['shoulder','knee','hip','small-joint','anchors','meniscus','resection','fluid-management','arthroscopy-electrosurgery','manual-instruments','instruments'],
  },
  'endoscopy-visualization':{
    label:{ru:'Эндовидеохирургия и визуализация',en:'Endoscopy & visualization'},
    description:{ru:'Камеры, источники света, мониторы, эндоскопы и хирургическая визуализация.',en:'Cameras, light sources, monitors, scopes and surgical imaging.'},
    subcategories:['cameras','light-sources','monitors','scopes','video-accessories','surgical-imaging'],
  },
  'general-surgery':{
    label:{ru:'Общая и лапароскопическая хирургия',en:'General & laparoscopic surgery'},
    description:{ru:'Лапароскопический доступ, инструменты, эвакуация дыма и электрохирургия.',en:'Laparoscopic access, instruments, smoke evacuation and electrosurgery.'},
    subcategories:['access-insufflation','laparoscopic-instruments','smoke-evacuation','electrosurgery'],
  },
  'powered-instruments':{
    label:{ru:'Хирургические силовые инструменты',en:'Powered instruments'},
    description:{ru:'Силовые системы HALL, лезвия, боры и принадлежности.',en:'HALL powered systems, blades, burs and accessories.'},
    subcategories:['power-systems','blades','burs','powered-accessories'],
  },
  'bone-cements':{
    label:{ru:'Костные цементы',en:'Bone cements'},
    description:{ru:'Костные цементы и инструменты для их применения.',en:'Bone cements and application instruments.'},
    subcategories:['cements','cement-instruments'],
  },
};

export const subcategoryLabels={
  hip:{ru:'Тазобедренный сустав',en:'Hip'},knee:{ru:'Коленный сустав',en:'Knee'},shoulder:{ru:'Плечевой сустав',en:'Shoulder'},radius:{ru:'Лучевая кость',en:'Radius'},
  instruments:{ru:'Инструменты',en:'Instruments'},'plates-fixation':{ru:'Пластины и устройства фиксации',en:'Plates & fixation devices'},screws:{ru:'Винты',en:'Screws'},nails:{ru:'Интрамедуллярные системы',en:'Intramedullary systems'},'external-fixation':{ru:'Внешняя фиксация',en:'External fixation'},pediatric:{ru:'Детская травматология',en:'Pediatric trauma'},patella:{ru:'Фиксация надколенника',en:'Patella fixation'},
  cervical:{ru:'Шейный отдел',en:'Cervical'},thoracolumbar:{ru:'Грудопоясничный отдел',en:'Thoracolumbar'},'minimally-invasive':{ru:'Малоинвазивная хирургия',en:'Minimally invasive surgery'},sacroiliac:{ru:'Крестцово-подвздошное сочленение',en:'Sacroiliac'},mesh:{ru:'Сетки',en:'Mesh'},'endoscopic-spine':{ru:'Эндоскопическая хирургия',en:'Endoscopic spine surgery'},
  'small-joint':{ru:'Мелкие суставы',en:'Small joints'},anchors:{ru:'Шовные якоря и фиксация',en:'Anchors & fixation'},meniscus:{ru:'Мениск',en:'Meniscus'},resection:{ru:'Резекция: шейверы и боры',en:'Resection: shavers & burs'},'fluid-management':{ru:'Управление жидкостью',en:'Fluid management'},'arthroscopy-electrosurgery':{ru:'Электрохирургическая артроскопия',en:'Electrosurgical arthroscopy'},'manual-instruments':{ru:'Ручные инструменты',en:'Manual instruments'},
  cameras:{ru:'Камеры',en:'Cameras'},'light-sources':{ru:'Источники света',en:'Light sources'},monitors:{ru:'Мониторы',en:'Monitors'},scopes:{ru:'Эндоскопы и принадлежности',en:'Scopes & accessories'},'video-accessories':{ru:'Видеостойки и принадлежности',en:'Video carts & accessories'},'surgical-imaging':{ru:'Хирургическая визуализация',en:'Surgical imaging'},
  'access-insufflation':{ru:'Доступ и инсуффляция',en:'Access & insufflation'},'laparoscopic-instruments':{ru:'Лапароскопические инструменты',en:'Laparoscopic instruments'},'smoke-evacuation':{ru:'Эвакуация хирургического дыма',en:'Surgical smoke evacuation'},electrosurgery:{ru:'Электрохирургия',en:'Electrosurgery'},
  'power-systems':{ru:'Силовые системы',en:'Power systems'},blades:{ru:'Лезвия и пилы',en:'Blades & saws'},burs:{ru:'Боры и фрезы',en:'Burs & routers'},'powered-accessories':{ru:'Насадки и принадлежности',en:'Attachments & accessories'},
  cements:{ru:'Костные цементы',en:'Bone cements'},'cement-instruments':{ru:'Инструменты и канюли',en:'Instruments & cannulas'},
};

export const productTypeLabels={
  implants:{ru:'Импланты',en:'Implants'},instruments:{ru:'Инструменты',en:'Instruments'},equipment:{ru:'Оборудование',en:'Equipment'},
};

const textOf=s=>`${s.slug||''} ${s.name?.en||s.name_en||''}`.toLowerCase();
const originalSub=s=>(s.subcategories?.[0]||s.subcategory||'');

function traumaSubcategory(s){
  const sub=originalSub(s), text=textOf(s);
  if(s.category==='trauma-instrument-sets')return'instruments';
  if(sub.includes('external-fixation'))return'external-fixation';
  if(sub.includes('pediatric'))return'pediatric';
  if(sub.includes('patella'))return'patella';
  if(sub.includes('intramedullary'))return'nails';
  if(/\bscrew\b|bolt|washer/.test(text))return'screws';
  return'plates-fixation';
}

function spineSubcategory(s){
  if(s.category==='spine-instrument-sets')return'instruments';
  if(s.category==='endoscopic-spine-surgery')return'endoscopic-spine';
  return({cervical:'cervical',thoracolumbar:'thoracolumbar','spine-mis':'minimally-invasive',sacroiliac:'sacroiliac','spinal-mesh':'mesh'})[originalSub(s)]||'thoracolumbar';
}

function sportsSubcategory(s){
  const c=s.category, sub=originalSub(s), text=textOf(s);
  if(c==='sports-instrument-sets')return'instruments';
  if(c==='shoulder-arthroscopy'||c==='arthroscopy')return'shoulder';
  if(c==='knee-arthroscopy')return'knee';
  if(c==='hip-arthroscopy')return'hip';
  if(c==='small-joint-arthroscopy')return'small-joint';
  if(c==='arthroscopy-resection')return'resection';
  if(c==='arthroscopy-fluid-management')return'fluid-management';
  if(c==='arthroscopy-electrosurgery')return'arthroscopy-electrosurgery';
  if(c==='arthroscopy-manual-instruments')return'manual-instruments';
  if(sub.includes('meniscus')||/menisc/.test(text))return'meniscus';
  if(sub.includes('anchor')||/anchor/.test(text))return'anchors';
  if(sub==='knee'||sub.includes('knee')||/knee|cruciate|cfloop/.test(text))return'knee';
  if(sub.includes('syndesmosis')||sub.includes('ac-joint'))return'anchors';
  return'anchors';
}

function visualizationSubcategory(s){
  if(s.category==='imaging')return'surgical-imaging';
  const text=textOf(s);
  if(/camera/.test(text))return'cameras';
  if(/light source|light guide/.test(text))return'light-sources';
  if(/monitor/.test(text))return'monitors';
  if(/arthroscope|laparoscope|scope|cannula|sheath|bridge/.test(text))return'scopes';
  return'video-accessories';
}

function poweredSubcategory(s){
  const text=textOf(s);
  if(/blade|saw|rasp/.test(text))return'blades';
  if(/\bbur\b|burs|router/.test(text))return'burs';
  if(/system|console|powerpro|titan|micropower|microfree|osteon$|e9000/.test(text))return'power-systems';
  return'powered-accessories';
}

// One migrated Synimed record is a vertebroplasty puncture cannula filed under
// the generic 'spine' category. Everything else with that category belongs to
// the Spine area, so this single record carries its own mapping rather than
// bending 'spine' towards bone cements for every future import.
export const systemOverrides={
  'synimed/synicem-vertebroplasty-cannula':{area:'bone-cements',subcategory:'cement-instruments',type:'instruments'},
};

// The area always comes from legacyCategoryAreas; only the subcategory and the
// product type are decided here.
export function classifySystem(s){
  const override=systemOverrides[s.brand+'/'+s.slug];
  if(override)return{...override};
  const c=s.category,area=legacyCategoryAreas[c]||'';
  switch(area){
    case 'joint-replacement':return{area,subcategory:c==='arthroplasty-instrument-sets'?'instruments':(['hip','knee','shoulder','radius'].includes(originalSub(s))?originalSub(s):'hip'),type:c==='arthroplasty-instrument-sets'?'instruments':'implants'};
    case 'trauma':return{area,subcategory:traumaSubcategory(s),type:c==='trauma-instrument-sets'?'instruments':'implants'};
    case 'spine':return{area,subcategory:spineSubcategory(s),type:['spine-implants','spine'].includes(c)?'implants':'instruments'};
    case 'sports-arthroscopy':return{area,subcategory:sportsSubcategory(s),type:['sports-medicine','arthroscopy','shoulder-arthroscopy','knee-arthroscopy','hip-arthroscopy','small-joint-arthroscopy'].includes(c)?'implants':['arthroscopy-fluid-management','arthroscopy-electrosurgery','arthroscopy-resection'].includes(c)?'equipment':'instruments'};
    case 'endoscopy-visualization':return{area,subcategory:visualizationSubcategory(s),type:'equipment'};
    case 'general-surgery':return{area,subcategory:c,type:c==='laparoscopic-instruments'?'instruments':'equipment'};
    case 'powered-instruments':return{area,subcategory:poweredSubcategory(s),type:/blade|bur|saw|rasp|attachment/i.test(textOf(s))?'instruments':'equipment'};
    case 'bone-cements':return{area,subcategory:c==='bone-cements'?'cements':'cement-instruments',type:c==='bone-cements'?'implants':'instruments'};
    default:return{area:'',subcategory:'',type:''};
  }
}

export const areaKeys=Object.keys(clinicalAreas);
// Russian needs three forms; used by the Products menu and the homepage tiles.
export const productCount=(lang,count)=>lang==='en'
  ? `${count} ${count===1?'product':'products'}`
  : `${count} ${count%10===1&&count%100!==11?'продукт':count%10>=2&&count%10<=4&&(count%100<12||count%100>14)?'продукта':'продуктов'}`;
export const taxonomyLabel=(lang,key)=>clinicalAreas[key]?.label?.[lang]||subcategoryLabels[key]?.[lang]||productTypeLabels[key]?.[lang]||key;
export const areaRoute=(lang,area,subcategory='')=>(lang==='en'?'/en':'')+'/catalog/'+area+'/'+(subcategory?subcategory+'/':'');
export function parseTaxonomyScope(scope){
  if(typeof scope!=='string')return null;
  const [area,subcategory]=scope.split('/');
  if(!clinicalAreas[area]||subcategory&&!clinicalAreas[area].subcategories.includes(subcategory))return null;
  return{area,subcategory:subcategory||''};
}
