#!/usr/bin/env python3
"""Native PDF geometry, transparent product cutouts and a white technical drawing."""
import json,os
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageChops
import cv2,numpy as np
from rembg import new_session,remove
R=Path(__file__).resolve().parents[1];out=R/'public/images/products/double-medical/anty-f-series';origdir=out/'_originals';origdir.mkdir(parents=True,exist_ok=True);D=fitz.open(R/'catalogs-source/double-medical/anty-f-series.pdf');session=new_session('u2net',providers=['CPUExecutionProvider']);assets=[]
def native(x,mask):
 pix=fitz.Pixmap(D,x)
 if pix.colorspace.n!=3:pix=fitz.Pixmap(fitz.csRGB,pix)
 pix=fitz.Pixmap(pix,fitz.Pixmap(D,mask));return Image.frombytes('RGBA',(pix.width,pix.height),pix.samples)
def save(name,im,page,kind='cutout',**metadata):
 im.save(out/(name+'.png'));im.save(out/(name+'.webp'),'WEBP',lossless=True,method=6);asset={'name':name,'src':'/images/products/double-medical/anty-f-series/'+name+'.webp','width':im.width,'height':im.height,'imageType':kind,'pdfPage':page,'captionFree':True,**metadata};assets.append(asset);return asset
# Stem image from page 1, retaining the placement orientation while excluding the cover.
im=native(14,15);im.save(origdir/'hero-native.png');candidate=remove(im,session=session).convert('RGBA');candidate.save(origdir/'hero-rembg-candidate.png')
# Source white layout residue is outside the implant. Remove only the near-white exterior
# and keep the largest source-alpha device region; no product structure is reconstructed.
alpha=np.array(im.getchannel('A'));rgb=np.array(im.convert('RGB'));mask=((alpha>10)&(rgb.min(axis=2)<247)).astype('uint8');n,labels,stats,cent=cv2.connectedComponentsWithStats(mask);largest=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);device=np.where(labels==largest,alpha,0).astype('uint8');device[:300,2300:]=0 # External white layout patch above the taper, outside all implant geometry.
im.putalpha(Image.fromarray(device))
# Map original pixels through the manufacturer's PDF transform; 3 pixels per PDF point.
m=np.array([[506.17474365234375/im.width,199.1895751953125/im.height,13.203826904296875],[-395.8678283691406/im.width,277.19683837890625/im.height,539.2374267578125]],dtype=np.float32)*3
warped=cv2.warpAffine(np.array(im),m,(round(D[0].rect.width*3),round(D[0].rect.height*3)),flags=cv2.INTER_CUBIC,borderValue=(0,0,0,0));hero=Image.fromarray(warped);bbox=hero.getchannel('A').getbbox();hero=hero.crop(bbox);padded=Image.new('RGBA',(hero.width+64,hero.height+64));padded.alpha_composite(hero,(32,32));save('hero-stem',padded,1,pdfImageXref=14,sourceMethod='Native embedded CMYK image converted to sRGB and transformed using PDF placement; cover excluded',maskMethod='rembg reviewed; source alpha with exterior layout residue removed')
# The page-2 stem has the same orientation as the six printed callout lines.
original=native(21,22);original.save(origdir/'hotspot-stem-native.png');size=(original.width*2,original.height*2);im=Image.open('/tmp/anty-assets/output/hotspot-stem.png').convert('RGBA').resize(size,Image.Resampling.LANCZOS);candidate=remove(im,session=session).convert('RGBA');candidate.save(origdir/'hotspot-stem-rembg-candidate.png');im.putalpha(original.getchannel('A').resize(size,Image.Resampling.LANCZOS));bbox=im.getchannel('A').getbbox();im=im.crop(bbox);padded=Image.new('RGBA',(im.width+64,im.height+64));padded.alpha_composite(im,(32,32));hot=save('hotspot-stem',padded,2,pdfImageXref=21,sourceBounds=[97.49520111083984/613.2755737304688,58.05548095703125/859.8897705078125,539.9318237304688/613.2755737304688,607.04736328125/859.8897705078125],nativeSize=list(original.size),scale=2,trimBounds=list(bbox),padding=32,maskMethod='Manufacturer alpha retained after rembg comparison; holes and fine ribs preserved',imageEnhancement={'method':'Real-ESRGAN x4plus downsampled to exactly 2x','scale':2,'originalSize':list(original.size),'enhancedSize':list(size)})
points=[('shoulder-coating',[352,118]),('cable-holes',[331.7,162.2]),('longitudinal-ribs',[258.2,253.9]),('taper',[257.3,331.2]),('circular-cross-section',[141.6,480]),('minimum-diameter',[115.7,532.8])];hotspots=[]
for name,(px,py)in points:
 x=(px-97.49520111083984)/(539.9318237304688-97.49520111083984)*size[0]-bbox[0]+32;y=(py-58.05548095703125)/(607.04736328125-58.05548095703125)*size[1]-bbox[1]+32
 hotspots.append({'featureId':name,'image':hot['src'],'x':round(x/padded.width*100,3),'y':round(y/padded.height*100,3),'pdfPage':2,'sourcePoint':[px,py],'coordinateSpace':'percent-of-padded-image'})
 crop=padded.crop((max(0,int(x)-110),max(0,int(y)-110),min(padded.width,int(x)+110),min(padded.height,int(y)+110)));save('feature-'+name,crop,2,sourceImage=hot['src'])
# Technical drawing is vector artwork: render it sharply, with its original white paper.
clip=fitz.Rect(421,411,542,592);pix=D[1].get_pixmap(dpi=600,clip=clip,alpha=False);drawing=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);drawing.save(origdir/'technical-drawing.png');save('technical-drawing',drawing,2,'scene',sourceBounds=[clip.x0/D[1].rect.width,clip.y0/D[1].rect.height,clip.x1/D[1].rect.width,clip.y1/D[1].rect.height],sourceMethod='Vector drawing rendered at 600 DPI; white background retained')
(out/'prepared-assets.json').write_text(json.dumps({'assets':assets,'hotspots':hotspots},ensure_ascii=False,indent=2)+'\n');print('Prepared',len(assets),'assets and',len(hotspots),'source-positioned hotspots')
