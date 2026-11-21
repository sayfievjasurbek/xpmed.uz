import path from 'node:path';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {createCanvas} from '@napi-rs/canvas';
export function detectCoverCrop(width,height) {
  const panels = width > height ? (width/height >= 2.1 ? 3 : 2) : 1;
  return {x:(panels-1)/panels,y:0,width:1/panels,height:1};
}
export function validateCoverCrop(crop) {
  return crop && ['x','y','width','height'].every(k=>Number.isFinite(crop[k])) && crop.x>=0 && crop.y>=0 && crop.width>0 && crop.height>0 && crop.x+crop.width<=1.000001 && crop.y+crop.height<=1.000001;
}
export async function prepareCatalogCover(pdf,system,catalogId) {
  const slug=catalogId.slice(system.brand.length+2);
  const dataFile=path.join('content/catalogs',system.brand,slug+'.json');
  let metadata={};try{metadata=JSON.parse(await readFile(dataFile,'utf8'));}catch(error){if(error.code!=='ENOENT')throw error;}
  const first=await pdf.getPage(1),size=first.getViewport({scale:1});
  const detected=detectCoverCrop(size.width,size.height),crop=metadata.coverCrop||detected;
  if(!validateCoverCrop(crop))throw Error('Invalid coverCrop in '+dataFile);
  const generated='/images/catalog-covers/'+catalogId+'.webp';
  const coverImage=metadata.coverImage||generated;
  if(!/^\/(?:images|assets)\/[a-zA-Z0-9_./%-]+$/.test(coverImage)||coverImage.includes('..'))throw Error('Invalid coverImage in '+dataFile);
  if(coverImage===generated){
    const scale=Math.min(640/(size.width*crop.width),1000/(size.height*crop.height));
    const viewport=first.getViewport({scale});
    const pageCanvas=createCanvas(Math.ceil(viewport.width),Math.ceil(viewport.height));
    await first.render({canvasContext:pageCanvas.getContext('2d'),viewport}).promise;
    const canvas=createCanvas(Math.max(1,Math.round(viewport.width*crop.width)),Math.max(1,Math.round(viewport.height*crop.height)));
    canvas.getContext('2d').drawImage(pageCanvas,viewport.width*crop.x,viewport.height*crop.y,viewport.width*crop.width,viewport.height*crop.height,0,0,canvas.width,canvas.height);
    await mkdir(path.dirname('public'+coverImage),{recursive:true});await writeFile('public'+coverImage,await canvas.encode('webp',86));
  }
  const source=coverImage.startsWith('/assets/')?'src'+coverImage:'public'+coverImage;
  await mkdir(path.dirname('dist'+coverImage),{recursive:true});await copyFile(source,'dist'+coverImage);
  metadata={...metadata,sourcePdf:system.sourcePdf,coverImage,coverSourcePage:1,coverCrop:crop,coverDetection:metadata.coverDetection||(size.width>size.height?(detected.width<.4?'landscape-right-third':'landscape-right-half'):'portrait-full-page')};
  await mkdir(path.dirname(dataFile),{recursive:true});await writeFile(dataFile,JSON.stringify(metadata,null,2)+'\n');
  return {coverImage,coverCrop:crop};
}
