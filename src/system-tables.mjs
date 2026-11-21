// Rectangular source grids retain covered coordinates as empty strings, never copies.
export function renderTableRows(table,{cell,sourceAttrs=()=>'',path='',header=false}) {
 const covered=new Set();
 return table.rows.map((row,r)=>`<tr${sourceAttrs(table.rowSources?.[r],`${path}.rows.${r}`)}>${row.map((entry,c)=>{
  if(covered.has(`${r}:${c}`))return '';
  const structured=entry&&typeof entry==='object'&&!Array.isArray(entry)&&Object.hasOwn(entry,'value');
  const value=structured?entry.value:entry;
  const rs=structured?Number(entry.rowspan||1):1,cs=structured?Number(entry.colspan||1):1;
  for(let y=r;y<r+rs;y++)for(let x=c;x<c+cs;x++)if(y!==r||x!==c)covered.add(`${y}:${x}`);
  const tone=structured&&['alpha','beta','compatible'].includes(entry.tone)?` class="sp-zone-${entry.tone}"`:'';
  const tag=header||c===0?'th':'td';
  return `<${tag}${header?` scope="${cs>1?'colgroup':'col'}"`:c===0?` scope="${rs>1?'rowgroup':'row'}"`:''}${rs>1?` rowspan="${rs}"`:''}${cs>1?` colspan="${cs}"`:''}${tone} data-table-column="${c}" data-table-colspan="${cs}"${sourceAttrs(table.rowSources?.[r]?.codeEvidence?.find(e=>e.column===c+1),`${path}.rows.${r}.${c}`)}>${cell(value,{entry,row:r,column:c})}</${tag}>`;
 }).join('')}</tr>`).join('');
}
export function validateTableSpans(t){
 const errors=[],covered=new Set();
 for(let r=0;r<t.rows.length;r++)for(let c=0;c<t.columns.length;c++){
  const entry=t.rows[r][c];
  if(covered.has(`${r}:${c}`)){if(entry!=='' )errors.push('Merged table covered cell must be empty');continue;}
  if(!entry||typeof entry!=='object'||!Object.hasOwn(entry,'value'))continue;
  const rs=entry.rowspan??1,cs=entry.colspan??1;
  if(!Number.isInteger(rs)||!Number.isInteger(cs)||rs<1||cs<1||r+rs>t.rows.length||c+cs>t.columns.length){errors.push('Invalid merged table span');continue;}
  for(let y=r;y<r+rs;y++)for(let x=c;x<c+cs;x++)if(y!==r||x!==c){if(covered.has(`${y}:${x}`))errors.push('Overlapping merged table cells');covered.add(`${y}:${x}`);}
 }
 return errors;
}
