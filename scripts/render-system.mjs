import fs from 'node:fs';
import {render} from '../src/render.mjs';
import ru from '../src/i18n/ru.mjs';import en from '../src/i18n/en.mjs';
import {validateSystem,normalizeSystem,loadSystems,prepareSystem,systemRoute} from '../src/catalog-data.mjs';
const s=normalizeSystem(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));await prepareSystem(s,await loadSystems());const errors=validateSystem(s);if(errors.length)throw Error(errors.join('; '));const lang=process.argv[3]==='en'?'en':'ru';
s.relatedSystems=s.relatedSystems.map(x=>({...x,url:x.status==='draft'?'/admin/review?system='+encodeURIComponent(x.brand+'/'+x.slug):systemRoute(x,lang)}));
process.stdout.write(render(lang,lang==='ru'?ru:en,new Date().getFullYear(),[],null,{lang:lang==='ru'?'en':'ru',t:lang==='ru'?en:ru},s));
