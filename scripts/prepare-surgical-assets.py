import sys,json,io,subprocess,pathlib,math
sys.path.insert(0,'scripts')
from PIL import Image
import pymupdf as fitz
from pdf_product_images import extract_product_photo
root=pathlib.Path('.');pdf=root/'catalogs-source/conmed/advanced-surgical-product-catalog.pdf';doc=fitz.open(pdf);folder=root/'public/images/products/conmed/advanced-surgical';orig=folder/'_originals';orig.mkdir(parents=True,exist_ok=True);inp=pathlib.Path('/tmp/conmed-surgical/esrgan-input');out=pathlib.Path('/tmp/conmed-surgical/esrgan-output');inp.mkdir(exist_ok=True);out.mkdir(exist_ok=True);records=[]
for n in list(range(5,9))+list(range(10,22))+list(range(23,40))+[41,42]:
 page=doc[n-1];w,h=page.rect.width,page.rect.height
 for info in page.get_image_info(xrefs=True):
  b=info['bbox'];box=[b[0]/w,b[1]/h,b[2]/w,b[3]/h];x0,y0,x1,y1=box
  if not info['xref']or x0>.5 or y0<.1 or y1>.89 or(y0>.75 and abs((x1-x0)*w-(y1-y0)*h)<30):continue
  result=extract_product_photo(pdf,n,box)
  if not result:continue
  im,meta=result;name=f'page-{n:03}-xref-{info["xref"]}';im.save(orig/(name+'.png'));rgb=Image.new('RGB',im.size,'white');rgb.paste(im,mask=im.getchannel('A')if im.mode=='RGBA'else None);rgb.save(inp/(name+'.png'))
  records.append({'name':name,'page':n,'bounds':box,'originalSize':list(im.size),**meta})
pathlib.Path('/tmp/conmed-surgical/assets.json').write_text(json.dumps(records,indent=2));print('Native product images',len(records),flush=True)
cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(inp),'-o',str(out),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png']
with open('/tmp/conmed-surgical/esrgan.log','w')as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
print('Real-ESRGAN inference complete',flush=True)
