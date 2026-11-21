"""Add a reviewed text-layer guide to one existing variant, without creating systems."""
import copy,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
from PIL import Image
import pymupdf as fitz

def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def bi(ru,en):return {'ru':ru,'en':en}
def import_variant_supplement(root,pdf,brand,pdfslug,digest,doc,profile):
 target=profile['variantSupplement'];path=root/'content/products'/brand/(target['slug']+'.json');system=json.loads(path.read_text());assert system['brand']==brand and any(v['id']==target['variantId'] for v in system['variants'])
 reportdir=root/'reports'/brand/pdfslug;reportdir.mkdir(parents=True,exist_ok=True)
 backup=reportdir/'before-cynthia.json'
 if not backup.exists():dump(backup,system)
 source='/catalogs/'+brand+'/'+pdfslug;public=root/'public'/source.lstrip('/');public.mkdir(parents=True,exist_ok=True);(public/'source.pdf').write_bytes(pdf.read_bytes())
 page_images=[]
 for n,page in enumerate(doc,1):
  destination=public/'pages'/f'{n:03}.webp';destination.parent.mkdir(exist_ok=True);pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(destination,quality=90);page_images.append(source+'/pages/'+destination.name)
 english=json.loads((reportdir/'direct-steps-en.json').read_text());russian=json.loads((root/'scripts/profiles/cynthia-revision-guide-ru.json').read_text());assets=json.loads((root/'public/images/products/double-medical/cynthia-revision-technique/assets.json').read_text())
 steps=[]
 for original in english:
  number=original['number'];ru=russian[number];step={'id':'revision-guide-'+number.replace('.','-'),'number':number,'title':bi(ru['title'],original['title']),'text':bi(ru['text'],original['text']),'sourcePages':original['sourcePages'],'sourceBlocks':original['blocks'],'images':[copy.deepcopy(a) for a in assets if a['step']==number and a['sourceXref']!=173],'notes':[{'text':bi(r,e)}for r,e in zip(ru.get('notes',[]),original['notes'])]}
  assert len(ru.get('notes',[]))==len(original['notes']),number
  if ru.get('checklist'):
   text=original['text'];starts=list(re.finditer(r'(?<!\S)([1-7])\.\s',text));items=[text[m.start():starts[i+1].start() if i+1<len(starts) else len(text)].strip().replace(' • ','\n• ')for i,m in enumerate(starts)];assert len(items)==len(ru['checklist']),(number,len(items));step['text']=bi('','');step['checklist']=[{'text':bi(r,e)}for r,e in zip(ru['checklist'],items)]
  steps.append(step)
 for number,pdfpage,last,ru,en in [('2.1',3,'25','Расчёт глубины: большеберцовая кость','Tibial length calculation'),('3.2',9,'55','Расчёт глубины: бедренная кость','Femoral length calculation')]:
  icon=next(a for a in assets if a['sourceXref']==173 and a['pdfPage']==pdfpage)
  table={'id':'guide-length-'+number,'title':bi(ru,en),'unit':'mm','columns':[bi('Длина по маркировке','Marked Length'),bi('Длина по маркировке −55','Marked Length −55'),bi('Длина вхождения офсетного соединителя','Offset Connector Engagement Length'),bi('Киль платформы','Platform Keel')],'rows':[['80','25',{'value':'30','rowspan':3,'image':icon},{'value':last,'rowspan':3}],['120','65','',''],['160','105','','']],'sourcePages':[pdfpage]}
  next(s for s in steps if s['number']==number)['tables']=[table]
 titles=[('Оценка и проверка','Assessment and Verification'),('Подготовка большеберцовой кости','Tibial Preparation'),('Подготовка бедренной кости','Femoral Preparation'),('Проверка объёма движений эндопротеза','Prosthesis Range of Motion Test'),('Меры предосторожности при работе с инструментами и компонентами эндопротеза','Precautions for Instrument and Prosthesis Implantation')]
 technique={'sourcePdf':source+'/source.pdf','sourcePages':list(range(3,18)),'catalogEdition':'2025.09','sourceSha256':digest,'chapters':[{'number':str(n),'title':bi(*titles[n-1]),'steps':[s for s in steps if s['number'].split('.')[0]==str(n)]}for n in range(1,6)],'footerNote':bi('Информация для медицинских специалистов. Не заменяет инструкцию по применению.','Information for medical professionals. Does not replace the instructions for use.')}
 next(v for v in system['variants']if v['id']==target['variantId'])['surgicalTechnique']=technique
 for asset in assets:system.setdefault('imageDimensions',{})[asset['src']]={'width':asset['width'],'height':asset['height']}
 document={'sourcePdf':source+'/source.pdf','sourceSha256':digest,'catalogTitle':bi('Руководство по хирургической технике — ревизионное эндопротезирование','Surgical technique guide — revision knee replacement'),'catalogEdition':'2025.09','sourcePages':[3],'documentCover':page_images[0],'sourcePageImages':page_images,'documentMeta':{'cover':page_images[0],'sizeLabel':f'{pdf.stat().st_size/1024/1024:.1f} MB','bytes':pdf.stat().st_size},'variantId':target['variantId'],'viewOnly':True}
 system['catalogImports']=[document]+[x for x in system.get('catalogImports',[])if x['sourcePdf']!=document['sourcePdf']]
 module=importlib.util.spec_from_file_location('finalize_translation',root/'scripts/finalize-translation.py');translation=importlib.util.module_from_spec(module);module.loader.exec_module(translation)
 # Validate new bilingual prose separately: legacy reviewed prose is left unchanged.
 translated=translation.finalize({'surgicalTechnique':technique,'document':document});review=system.setdefault('review',{});review['translatedFields']=list(dict.fromkeys(review.get('translatedFields',[])+[p.replace('surgicalTechnique.',f'variants.{next(i for i,v in enumerate(system["variants"])if v["id"]==target["variantId"])}.surgicalTechnique.',1).replace('document.','catalogImports.0.',1) for p in translated['review']['translatedFields']]));review['translationAuthor']='codex'
 import jsonschema;jsonschema.validate(system,json.loads((root/'content/system.schema.json').read_text()))
 result=subprocess.run(['node','scripts/validate-system.mjs'],cwd=root,input=json.dumps(system),text=True,capture_output=True)
 if result.returncode:raise ValueError(result.stdout+result.stderr)
 original=json.loads(backup.read_text());unchanged=['specTables','referenceTables','components','features','hotspots','sourcePdf','sourcePages','heroImage','status']
 for key in unchanged:assert system.get(key)==original.get(key),key
 assert system['variants'][0]==original['variants'][0]
 for key,value in original['variants'][1].items():assert system['variants'][1][key]==value,key
 dump(path,system)
 report={'sourcePdf':document['sourcePdf'],'sourceSha256':digest,'edition':'2025.09','method':'Direct positioned PDF text layer; no OCR; Codex-authored professional Russian','systemsCreated':0,'systemsUpdated':1,'system':system['slug'],'variant':'revision','chapters':5,'steps':len(steps),'images':len(assets),'tables':2,'notes':sum(len(s['notes'])for s in steps),'viewOnly':True,'existingProductDataUnchanged':True,'comparison':profile['comparisons'],'translationStatus':'Codex-translated fields recorded for medical review','sourceTextNotes':['Section 3.9 ends the word complications as complicatio in the source text layer; the Russian translation retains its intended medical meaning.','Section 3.6 names the tibial drill guide in the femoral preparation instructions. Wording retained without silently correcting the guide.'],'openFlags':[]}
 dump(root/'reports'/brand/(pdfslug+'.json'),report);dump(public/'direct-text.json',json.loads((reportdir/'direct-text.json').read_text()));print(json.dumps(report,ensure_ascii=False,indent=2));return report
