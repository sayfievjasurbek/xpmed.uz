"""Read placed PDF product photos, retaining source transparency and rotation."""
import io,math
import pymupdf as fitz
from PIL import Image

def extract_product_photo(pdf,page_number,bounds):
 with fitz.open(pdf)as doc:
  page=doc[page_number-1];w,h=page.rect.width,page.rect.height;target=fitz.Rect(bounds[0]*w,bounds[1]*h,bounds[2]*w,bounds[3]*h);candidates=[]
  for info in page.get_image_info(xrefs=True):
   if not info['xref']:continue
   rect=fitz.Rect(info['bbox']);area=rect.get_area();overlap=(rect&target).get_area()
   if area and overlap/area>.4 and area<target.get_area()*2.5:candidates.append((overlap,info))
  if not candidates:return None
  _,info=max(candidates,key=lambda pair:pair[0]);blob=doc.extract_image(info['xref']);image=Image.open(io.BytesIO(blob['image'])).convert('RGB');native_size=list(image.size)
  if blob.get('smask'):
   mask=Image.open(io.BytesIO(doc.extract_image(blob['smask'])['image'])).convert('L');image=image.convert('RGBA');mask=mask.resize(image.size,Image.Resampling.LANCZOS)if mask.size!=image.size else mask;image.putalpha(mask)
  angle=math.degrees(math.atan2(info['transform'][1],info['transform'][0]))
  if abs(angle)>1:image=image.rotate(-angle,expand=True,resample=Image.Resampling.BICUBIC,fillcolor=(255,255,255,0)if image.mode=='RGBA'else 'white')
  return image,{'sourceRotation':angle,'pdfImageXref':info['xref'],'nativeSourceSize':native_size,'pdfAlphaMask':blob.get('smask',0),'sourceMethod':'Original embedded PDF image; vector captions excluded'}
