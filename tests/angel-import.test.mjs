import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import {loadSystems,validateSystem} from '../src/catalog-data.mjs';import {renderSystem} from '../src/system-page.mjs';import {renderTableRows,validateTableSpans} from '../src/system-tables.mjs';
const s=(await loadSystems()).find(x=>x.slug==='angel-shoulder-system');
const tables=new Map(s.variants.flatMap(v=>v.specTables).map(t=>[t.id,t]));
test('Angel has four system variants, complete bilingual content and six exact source tables',()=>{
 assert.equal(s.catalogType,'system');assert.equal(s.status,'published');assert.deepEqual(s.specialty,['orthopedics','traumatology']);assert.equal(s.subcategory,'shoulder');assert.equal(s.variants.length,4);assert.equal(tables.size,6);assert.equal(s.review.flags.length,0);assert.deepEqual(s.sourcePages,[3,4,5,6,7,8,9]);
 for(const v of s.variants){assert.ok(v.features.length);assert.ok(v.specTables.length);assert.equal(v.gallery.length,6);for(const f of v.features){assert.ok(f.title.ru&&f.title.en&&f.text.ru&&f.text.en);}}
 assert.deepEqual(validateSystem(s),[]);
 const reverse=tables.get('reverse-shoulder-set'),anatomic=tables.get('anatomic-shoulder-set');assert.equal(reverse.rows[3][2].value,'7.5');assert.equal(reverse.rows[3][2].colspan,2);assert.equal(reverse.rows[3][3],'');assert.equal(anatomic.rows[3][2].value,'8');assert.equal(anatomic.rows[3][4].value,'9');assert.equal(reverse.rows[3][12].value,'/');assert.equal(anatomic.rows[4][17].rowspan,2);
 assert.deepEqual(tables.get('cemented-stem-dimensions').rows[1].slice(1),['100','105','110','115','120','125']);
});
test('Merged tables retain source geometry and reject values written into covered cells',()=>{
 for(const t of tables.values())assert.deepEqual(validateTableSpans(t),[]);
 const t={columns:['a','b','c'],rows:[[{value:'one',rowspan:2,colspan:2},'','third'],['','','last']]};
 const html=renderTableRows(t,{cell:String});assert.ok(html.includes('rowspan="2" colspan="2"'));assert.equal((html.match(/>one</g)||[]).length,1);assert.equal((html.match(/<t[dh][ >]/g)||[]).length,3);
 assert.deepEqual(validateTableSpans(t),[]);t.rows[1][1]='one';assert.ok(validateTableSpans(t).length);t.rows[1][1]='';t.rows[0][0].colspan=4;assert.ok(validateTableSpans(t).length);
});
test('Angel compatibility has exact coloured zones, slash cells and 16 compatible marks',()=>{
 const t=tables.get('head-glenoid-compatibility');assert.equal(t.rows.length,12);assert.deepEqual(t.rows[0].slice(2),['38','41','44','47','50','53']);assert.equal(t.rows[4][2].colspan,3);assert.equal(t.rows[4][2].tone,'alpha');assert.equal(t.rows[4][5].tone,'beta');assert.equal(t.rows[7][2].value,'/');
 const marks=t.rows.slice(8).map(row=>row.slice(2).map(c=>c?.value==='●'));
 assert.deepEqual(marks,[[true,true,true,true,false,false],[false,true,true,true,true,false],[false,false,true,true,true,true],[false,false,true,true,true,true]]);
 for(const lang of ['ru','en']){const html=renderSystem(s,lang);assert.ok(html.includes('sp-zone-alpha'));assert.ok(html.includes('sp-zone-beta'));assert.ok(html.includes('sp-zone-compatible'));assert.ok(html.includes('rowspan="4"'));assert.ok(!html.includes('[object Object]'));assert.ok(html.includes('data-gallery-caption'));assert.ok(html.includes(lang==='ru'?'мм':'mm'));}
});
test('Angel source images and random audit sample exist and match actual anchor cells',async()=>{
 for(const [src,dim]of Object.entries(s.imageDimensions)){await fs.access('public'+src);assert.ok(dim.width>0&&dim.height>0);}
 const report=JSON.parse(await fs.readFile('reports/double-medical/angel-shoulder-system/sample-20.json'));assert.equal(report.samples.length,20);
 for(const item of report.samples){const t=tables.get(item.tableId),entry=t.rows[item.row-1][item.gridColumn-1],value=entry&&typeof entry==='object'&&Object.hasOwn(entry,'value')?entry.value:entry;assert.equal(item.value,value);assert.equal(item.pdfPage,t.sourcePages[0]);assert.ok(value!==''&&value!==null);}
});
