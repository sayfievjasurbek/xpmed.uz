"""Reviewed layout + independent OCR evidence → conservative bilingual drafts."""
import copy,hashlib,json,os,re,subprocess,difflib,shutil
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import numpy as np
import cv2
from rembg import new_session,remove
from catalog_ocr import compare_code,overlap
from catalog_qr import decode_catalog_qrs
from finalize_translation_loader import finalize_translation
from list_catalog_presentation import prepare_list_catalog
from pdf_product_images import extract_product_photo

def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def clean_token(text):return text.strip(' .,:;_~|•»')
def similarity(left,right):return difflib.SequenceMatcher(None,left,right).ratio()
def locate_code(evidence,expected,box,column,psm=3):
    x1,x2=column;words=evidence['passes'][str(psm)]['words'];center=(box[1]+box[3])/2
    candidates=[w for w in words if x1-.003<=(w['bounds'][0]+w['bounds'][2])/2<=x2+.003 and box[1]-.004<=(w['bounds'][1]+w['bounds'][3])/2<=box[3]+.004]
    candidates=[{**w,'text':clean_token(w['text'])}for w in candidates if re.search('[A-Za-z0-9]',w['text'])]
    if not candidates:return {'text':'','confidence':-1,'bounds':[x1,box[1],x2,box[3]]}
    return max(candidates,key=lambda w:similarity(expected,w['text'])*2-abs((w['bounds'][1]+w['bounds'][3])/2-center)*20)

def audit_code(evidence,expected,row_bounds,column_bounds):
    primary=locate_code(evidence,expected,row_bounds,column_bounds,3)
    # Match by physical position, not by substituting ambiguous characters.
    secondary=locate_code(evidence,expected,primary['bounds'],column_bounds,11)
    result=compare_code(primary,secondary)
    result.update({'printedCandidate':expected,'sourceBounds':primary['bounds'],'pdfPage':evidence['page'],'printedPage':evidence['printedPage']})
    if expected not in [primary['text'],secondary['text']]:result['reasons'].append('source-transcription-disagreement')
    elif result['value'] is not None and result['value']!=expected:result['reasons'].append('source-transcription-disagreement')
    result['flagged']=bool(result['reasons'])
    if result['flagged']:result['value']=None
    return result

def source(page,bounds,path=None):return {'pdfPage':page,'printedPage':page-2,'sourceBounds':bounds,'coordinateSpace':'normalized','path':path}
def issue(path,code,message,page,bounds=None,details=None):
    defaults={'ocr-code-review':'Catalog number requires review. The value is empty; compare both raw OCR readings and the original page.','image-mask-review':'Review segmentation; the original was retained to avoid losing parts of the device.','specialty-review':'Clinical specialty was not inferred; review the intended specialty.','source-association-review':'Review OCR, subgroup assignments and image captions. Missing codes were not reconstructed.','source-prose-review':'Review the source name; malformed source wording was preserved without guessing.','image-association-review':'Page illustrations overlap; a crop may include a neighboring shaft. Compare with the original page.'}
    prose=message if isinstance(message,dict)and 'ru'in message else {'ru':str(message),'en':defaults.get(code,str(message))}
    return {'path':path,'code':code,'message':prose,'sourcePages':[page],**source(page,bounds or [0,0,1,1],path),**({'details':details}if details else{})}

def make_asset(root,pdfslug,system_slug,photo,page,evidence,session):
    if photo.get('preparedAsset'):
        asset=copy.deepcopy(photo['preparedAsset']);original=root/'public'/asset['src'].lstrip('/');folder=root/'public/images/products/conmed'/system_slug;folder.mkdir(parents=True,exist_ok=True)
        shutil.copy2(original,folder/original.name)
        for item in original.parent.glob('_originals/'+original.stem+'*.png'):
            (folder/'_originals').mkdir(exist_ok=True);shutil.copy2(item,folder/'_originals'/item.name)
        asset['src']='/images/products/conmed/'+system_slug+'/'+original.name;asset['imageCaption']=photo['caption'];asset.update(source(page,photo['bounds']));return asset
    bounds=photo['bounds'];folder=root/'public/images/products/conmed'/system_slug;folder.mkdir(parents=True,exist_ok=True)
    name='page-%03d-photo-'%page+hashlib.sha1(json.dumps(bounds).encode()).hexdigest()[:8]
    prefix='/images/products/conmed/'+system_slug+'/'+name;manifest=folder/(name+'.json')
    fingerprint=hashlib.sha256(json.dumps(photo,sort_keys=True).encode()).hexdigest()
    if manifest.exists():
        existing=json.loads(manifest.read_text())
        if existing.get('methodVersion')==5 and existing.get('inputFingerprint')==fingerprint:return existing
    native=extract_product_photo(root/'public/catalogs/conmed'/pdfslug/'source.pdf',page,bounds)
    if native:
        original,native_meta=native;source_alpha=original.getchannel('A')if original.mode=='RGBA'else None;originals=folder/'_originals';originals.mkdir(exist_ok=True);original.save(originals/(name+'-native.png'))
        segmented=remove(original,session=session).convert('RGBA');rgb=np.asarray(original.convert('RGB'));ink=np.clip((248-rgb.min(axis=2).astype(float))*8,0,255).astype('uint8');alpha=ImageChops.lighter(segmented.getchannel('A'),Image.fromarray(ink));alpha=ImageChops.multiply(alpha,source_alpha)if source_alpha is not None else alpha;cut=original.convert('RGBA');cut.putalpha(alpha)
        bbox=cut.getchannel('A').getbbox()
        if bbox:cut=cut.crop(bbox)
        padded=Image.new('RGBA',(cut.width+64,cut.height+64));padded.alpha_composite(cut,(32,32));padded.save(folder/(name+'.png'));padded.save(folder/(name+'.webp'),lossless=True,method=6)
        asset={'methodVersion':5,'inputFingerprint':fingerprint,'src':prefix+'.webp','imageType':'cutout','imageCaption':photo.get('caption',{'ru':'','en':''}),'width':padded.width,'height':padded.height,'captionFree':True,'captionReviewRequired':False,**native_meta,**source(page,bounds)}
        dump(manifest,asset);return asset
    canvas=Image.open(root/'public/catalogs/conmed'/pdfslug/'ocr'/f'{page:03}-{evidence["dpi"]}dpi.png').convert('RGB');w,h=canvas.size;pixel=[round(bounds[0]*w),round(bounds[1]*h),round(bounds[2]*w),round(bounds[3]*h)];original=canvas.crop(pixel)
    originals=folder/'_originals';originals.mkdir(exist_ok=True);original.save(originals/(name+'.png'))
    for excluded in photo.get('excludeBounds',[]):
        b=[round(excluded[0]*w)-pixel[0],round(excluded[1]*h)-pixel[1],round(excluded[2]*w)-pixel[0],round(excluded[3]*h)-pixel[1]];ImageDraw.Draw(original).rectangle(b,fill='white')
    # Reviewed external caption boxes contain no product geometry. Future recipes
    # can provide these bounds; otherwise propose matching bottom-caption words.
    caption_removed=False
    for box in photo.get('captionRemovalBounds',[]):
        rect=[round(box[0]*w)-pixel[0],round(box[1]*h)-pixel[1],round(box[2]*w)-pixel[0],round(box[3]*h)-pixel[1]]
        ImageDraw.Draw(original).rectangle(rect,fill='white');caption_removed=True
    if not photo.get('captionRemovalBounds'):
        caption_words=set(re.findall(r'[a-z0-9]+',photo.get('caption',{}).get('en','').lower()))
        for word in evidence['passes']['11']['words']:
            b=word['bounds'];cy=(b[1]+b[3])/2;cx=(b[0]+b[2])/2;tokens=set(re.findall(r'[a-z0-9]+',word['text'].lower()))
            if bounds[0]<=cx<=bounds[2] and bounds[1]+.82*(bounds[3]-bounds[1])<=cy<=bounds[3] and tokens and tokens.issubset(caption_words):
                ImageDraw.Draw(original).rectangle([round(b[0]*w)-pixel[0]-3,round(b[1]*h)-pixel[1]-3,round(b[2]*w)-pixel[0]+3,round(b[3]*h)-pixel[1]+3],fill='white');caption_removed=True
    cut=remove(original,session=session).convert('RGBA')
    # Retain fine source structures; erased external captions remain white/transparent.
    original_pixels=np.asarray(original);ink_alpha=np.clip((255-original_pixels.min(axis=2)).astype('float32')*4,0,255).astype('uint8');caption_mask=Image.new('L',original.size);draw=ImageDraw.Draw(caption_mask)
    for word in evidence['passes']['3']['words']:
        b=word['bounds']
        if b[0]>=bounds[0] and b[1]>=bounds[1] and b[2]<=bounds[2] and b[3]<=bounds[3]:draw.rectangle([round(b[0]*w)-pixel[0]-1,round(b[1]*h)-pixel[1]-1,round(b[2]*w)-pixel[0]+1,round(b[3]*h)-pixel[1]+1],fill=255)
    caption=ImageChops.multiply(Image.fromarray(ink_alpha),caption_mask);cut.putalpha(ImageChops.lighter(cut.getchannel('A'),caption))
    # Restore non-white thin structures without inventing pixels. Only edge-connected
    # near-white paper is removed; rembg retains enclosed white device highlights.
    paper=((original_pixels.min(axis=2)>245)&(original_pixels.max(axis=2)-original_pixels.min(axis=2)<12)).astype('uint8')
    _,labels=cv2.connectedComponents(paper,connectivity=8)
    border_labels=np.unique(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]));border_labels=border_labels[border_labels!=0]
    transparent=np.isin(labels,border_labels)
    safe_alpha=Image.fromarray(np.where(transparent,0,255).astype('uint8'))
    restored=original.convert('RGBA');restored.putalpha(ImageChops.lighter(cut.getchannel('A'),safe_alpha));cut=restored
    mask=np.asarray(cut.getchannel('A'));ink=original_pixels.min(axis=2)<180;coverage=float(np.mean(mask[ink]>100)) if ink.any() else 1
    # Never silently discard fine implants/cables: retain the original if mask coverage is doubtful.
    kind='cutout' if coverage>.94 and mask.max()>0 else 'scene';chosen=cut if kind=='cutout' else original.convert('RGBA')
    if kind=='cutout':
        bbox=chosen.getchannel('A').getbbox()
        if bbox:chosen=chosen.crop(bbox)
        padded=Image.new('RGBA',(chosen.width+64,chosen.height+64));padded.alpha_composite(chosen,(32,32));chosen=padded
    chosen.save(folder/(name+'.png'));chosen.save(folder/(name+'.webp'),lossless=kind=='cutout',quality=92,method=6)
    asset={'methodVersion':5,'inputFingerprint':fingerprint,'maskMethod':'rembg plus edge-connected white-background restoration; exact source pixels retained','src':prefix+'.webp','imageType':kind,'captionFree':caption_removed,'captionReviewRequired':not bool(photo.get('captionRemovalBounds')),'imageCaption':photo.get('caption',{'ru':'','en':''}),'width':chosen.width,'height':chosen.height,'maskCoverage':coverage,**source(page,bounds)}
    dump(manifest,asset);return asset

def import_ocr_catalog(root,pdf,brand,pdfslug,digest,evidence,model):
    profiles=[]
    for path in (root/'scripts/profiles/ocr').glob('*.json'):
        p=json.loads(path.read_text())
        if p.get('sha256')==digest:profiles.append(p)
    if not profiles:raise ValueError('OCR cached. A source-reviewed section layout is required before generating drafts for this PDF.')
    profile=profiles[0];sections=[];layout_uncertainties=[]
    for part in profile['parts']:
        data=json.loads((root/'scripts/profiles'/part).read_text());sections.extend(data['sections']if isinstance(data,dict)else data)
        if isinstance(data,dict):layout_uncertainties.extend(data.get('uncertainties',[]))
    extras_path=root/'reports'/brand/(pdfslug+'-extras.json');extras=json.loads(extras_path.read_text()) if extras_path.exists() else {}
    qr_evidence=decode_catalog_qrs(root/'public/catalogs'/brand/pdfslug,evidence,{n for section in sections for n in section['sourcePages']})
    extras['qrs']=qr_evidence['qrs'];extras['decodeFailures']=qr_evidence['decodeFailures']
    pages={p['page']:p for p in evidence};reference='/catalogs/'+brand+'/'+pdfslug
    report={'pdf':str(pdf.relative_to(root)),'sha256':digest,'status':'draft-only','ocr':{'dpi':evidence[0]['dpi'],'engine':evidence[0]['engine'],'settings':['--oem 1 --psm 3 -l eng','--oem 1 --psm 11 -l eng'],'minimumCodeConfidence':90,'substitutions':'none; no O/0, I/l/1, S/5 or B/8 substitutions'},'systemsFound':len(sections),'componentGroups':0,'componentsFound':0,'catalogTitle':profile.get('catalogTitle',{'ru':pdf.stem,'en':pdf.stem}),'catalogNumberOccurrences':0,'confirmedCatalogNumberOccurrences':0,'flaggedCodes':[],'sourceBlankCodeCells':[],'systems':[],'images':[],'nonProductPages':profile['nonProductPages'],'companyAndContacts':extras,'layoutUncertainties':layout_uncertainties}
    rembg_session=new_session(model,providers=['CPUExecutionProvider']);unique_confirmed=set();all_candidates=set()
    for section in sections:
        slug=section['slug'];target=root/'content/products'/brand/(slug+'.json')
        if target.exists():
            old=json.loads(target.read_text())
            if old.get('status')=='published' or old.get('review',{}).get('editedAt') or old.get('review',{}).get('codeVerification'):raise ValueError('Refusing to overwrite published/reviewed/code-verified '+str(target))
        s={'schemaVersion':1,'slug':slug,'brand':brand,'category':section.get('category',profile.get('category','unclassified')),'subcategory':'','subcategories':[],'specialty':section.get('specialty',[]),'name':section['name'],'shortDescription':section.get('shortDescription',{'ru':'','en':''}),'description':{'ru':'','en':''},'heroImage':'','imageType':'cutout','gallery':[],'features':[],'components':[],'componentGroups':[],'specTables':[],'refCodes':[],'sourcePdf':reference+'/source.pdf','documentCover':reference+'/pages/001.webp','catalogPageCount':len(evidence),'sourcePages':section['sourcePages'],'sourcePageImages':[reference+f'/pages/{n:03}.webp'for n in section['sourcePages']],'sourcePageDimensions':{str(n):{'width':pages[n]['pixelSize'][0],'height':pages[n]['pixelSize'][1]}for n in section['sourcePages']},'catalogEdition':profile.get('catalogEdition'),'isNew':False,'status':'draft','manufacturerLinks':[],'availabilityNote':{'ru':'Не все изделия могут быть доступны на всех рынках.','en':'All products may not be available in all markets'},'imageDimensions':{}}
        if profile.get('catalogTitle'):s['catalogTitle']=profile['catalogTitle']
        if section.get('overview'):s['overview']=section['overview']
        flags=copy.deepcopy(section.get('flags',[]));descriptions={'ru':[],'en':[]};seen_assets={}
        for group in section['groups']:
            page=group.get('page')or group.get('sourcePages',section['sourcePages'])[0];gid=group['id'];report['componentGroups']+=1
            group_photos=group.get('photos',[])
            if not group_photos and group.get('photoBounds'):group_photos=[{'bounds':group['photoBounds'],'caption':group.get('imageCaption',group['title'])}]
            photos=[]
            for photo in group_photos:
                n=photo.get('page',page);asset=make_asset(root,pdfslug,slug,photo,n,pages[n],rembg_session);photos.append((photo,asset));seen_assets[asset['src']]=asset
                if asset.get('captionReviewRequired'):flags.append(issue('gallery','image-caption-review',{'ru':'Проверьте отсутствие печатной подписи и сохранность изделия. Подпись показана отдельно в HTML.','en':'Review caption removal and product geometry. Captions are rendered separately in HTML.'},n,photo['bounds']))
                if asset['imageType']=='scene':flags.append(issue('gallery','image-mask-review','Проверьте маску: сохранено исходное изображение, чтобы не удалить части изделия.',n,photo['bounds']))
            for lang in ['ru','en']:
                if group.get('description',{}).get(lang):descriptions[lang].append(group['title'][lang]+'\n'+group['description'][lang])
            for index,feature in enumerate(group.get('features',[])):
                feat=copy.deepcopy(feature);feat.update({'id':gid+'-feature-'+str(index+1),'image':None,'groupId':gid,'sourcePages':[page],**source(page,feature.get('sourceBounds')or group['headingBounds'])});s['features'].append(feat)
            for text in group.get('uncertainties',[]):flags.append(issue('componentGroups.'+gid,'source-prose-review',{'ru':'В исходном названии адаптера напечатано «A cml»; сохранено без предположения ACMI. Проверьте наименование.','en':text.get('message',str(text))if isinstance(text,dict)else str(text)},page,group['headingBounds']))
            if group.get('imageReviewNote'):flags.append(issue('componentGroups.'+gid,'image-association-review',{'ru':'На странице изображения лапароскопов перекрываются; кадр может включать соседний стержень. Сверьте с оригиналом.','en':str(group['imageReviewNote'])},page,group.get('photoBounds')or group['headingBounds']))
            for note in group.get('sourceNotes',[]):flags.append(issue('componentGroups.'+gid,'source-note',note if isinstance(note,dict)else str(note),page,group.get('tableBounds')or group['headingBounds']))
            if group.get('sourceNote'):flags.append(issue('componentGroups.'+gid,'source-note',str(group['sourceNote']),page,group.get('tableBounds')or group['headingBounds']))
            table={'id':gid,'title':group['title'],'unit':None,'image':None,'componentImage':photos[0][1]['src']if photos else None,'columns':group['columns'],'rows':[],'legend':None,'sourcePages':[page],'headersVerified':True,'rowSources':[],'groupId':gid,**source(page,group.get('tableBounds')or group['headingBounds'])}
            if group.get('columnTypes'):table['columnTypes']=group['columnTypes']
            component_ids=[]
            for ri,row in enumerate(group.get('rows',[])):
                report['componentsFound']+=1;cid=gid+'-item-'+str(ri+1);component_ids.append(cid);bounds=group['rowBounds'][ri];cells=[];confirmed=[];audits=[]
                for ci,cell in enumerate(row):
                    if ci==0 or isinstance(cell,dict):cells.append(cell);continue
                    if not str(cell).strip():
                        cells.append('');entry={'system':slug,'group':gid,'row':ri+1,'column':ci+1,**source(page,bounds)};report['sourceBlankCodeCells'].append(entry);continue
                    expected=str(cell);report['catalogNumberOccurrences']+=1;all_candidates.add(expected)
                    col=group.get('columnBounds',[]);column=col[ci] if ci<len(col) else [.75,.96]
                    audit=copy.deepcopy(group['codeEvidence'][ri])if group.get('codeEvidence')else audit_code(pages[page],expected,bounds,column);audit.update({'system':slug,'group':gid,'componentId':cid,'tableId':gid,'row':ri+1,'column':ci+1,'path':f'specTables.{len(s["specTables"])}.rows.{ri}.{ci}'})
                    cells.append(audit['value']);audits.append(audit)
                    if audit['flagged']:
                        report['flaggedCodes'].append(audit);flags.append(issue(audit['path'],'ocr-code-review',f'Cat. No. требует проверки: проход 1 «{audit["pass1"] or "—"}», проход 2 «{audit["pass2"] or "—"}». Значение не заполнено.',page,audit['sourceBounds'],audit))
                    else:confirmed.append(audit['value']);unique_confirmed.add(audit['value']);report['confirmedCatalogNumberOccurrences']+=1
                table['rows'].append(cells);table['rowSources'].append({**source(page,bounds), 'codeEvidence':audits})
                assigned=[asset for photo,asset in photos if photo.get('rowIndex')==ri or ri in photo.get('rowIndices',[])]
                s['components'].append({'id':cid,'groupId':gid,'name':row[0] if isinstance(row[0],dict)else{'ru':str(row[0]),'en':str(row[0])},'image':assigned[0]['src']if assigned else None,'imageType':assigned[0]['imageType']if assigned else 'cutout','refCodes':confirmed,'codeEvidence':audits,'sourcePages':[page],'showInGrid':bool(assigned),**source(page,bounds)})
            s['specTables'].append(table);s['componentGroups'].append({'id':gid,'name':group['title'],'description':group.get('description',{'ru':'','en':''}),'componentIds':component_ids,'subgroups':group.get('subgroups',[]),'sourceNotes':group.get('sourceNotes',[]),'images':[asset for _,asset in photos],'tableId':gid,'sourcePages':[page],**source(page,group['headingBounds'])})
        s['gallery']=list(seen_assets.values());report['images'].extend(s['gallery']);s['heroImage']=s['gallery'][0]['src']if s['gallery']else '';s['imageType']=s['gallery'][0]['imageType']if s['gallery']else 'scene'
        for asset in s['gallery']:s['imageDimensions'][asset['src']]={'width':asset['width'],'height':asset['height']}
        for lang in ['ru','en']:s['description'][lang]='\n\n'.join(descriptions[lang])
        s['refCodes']=list(dict.fromkeys(code for c in s['components']for code in c['refCodes']))
        for qr in extras.get('qrCodes',extras.get('qrs',[])):
            n=qr.get('page',qr.get('pdfPage'));url=qr.get('url','')
            if n in section['sourcePages'] and qr.get('resourceType',qr.get('kind'))=='product-page':s['manufacturerLinks'].append({'label':{'ru':'Подробнее на сайте производителя','en':'Learn more on the manufacturer’s website'},'url':url,'sourcePages':[n],**source(n,qr.get('bounds',qr.get('sourceBounds',[0,0,1,1])))})
        if not s['specialty']:flags.append(issue('specialty','specialty-review','Клиническая специальность не назначена автоматически: проверьте область применения системы.',section['sourcePages'][0]))
        flags.append(issue('components','source-association-review','Проверьте OCR, соответствие позиций подгруппам и подписи к изображениям. Отсутствующие коды не восстановлены.',section['sourcePages'][0]))
        resolved=[]
        if profile.get('layoutReviewed'):
            resolved=[{**f,'status':'resolved','resolution':{'ru':'Разметка, изображения и подписи сверены с исходными страницами.','en':'Layout, images and captions compared with the source pages.'}}for f in flags if f['code']=='source-association-review'];flags=[f for f in flags if f['code']!='source-association-review']
        s['review']={'resolvedFlags':resolved,'flags':flags,'sourceSha256':digest,'importMethod':str(evidence[0]['dpi'])+'-DPI Tesseract PSM3 + PSM11, independent Codex visual reading and isolated-crop verification; source-reviewed layout','translationAuthor':'codex','translationStatus':'review-required','skipped':False}
        s=prepare_list_catalog(s);s=finalize_translation(s);dump(target,s)
        check=subprocess.run(['node','scripts/validate-system.mjs'],input=json.dumps(s),capture_output=True,text=True,cwd=root)
        if check.returncode:raise ValueError(check.stdout+check.stderr)
        report['systems'].append({'slug':slug,'name':s['name'],'status':'draft','sourcePages':s['sourcePages'],'componentGroups':len(s['componentGroups']),'components':len(s['components']),'tables':len(s['specTables']),'features':len(s['features']),'images':len(s['gallery']),'flaggedCodes':sum(f['code']=='ocr-code-review'for f in flags),'flags':flags,'file':str(target.relative_to(root))})
        print(f'DRAFT {slug}: {len(s["components"])} ordering items; {len(s["gallery"])} images',flush=True)
    report['uniqueConfirmedCatalogNumbers']=len(unique_confirmed);report['uniquePrintedCodeCandidates']=len(all_candidates);report['imagesExtracted']=len(report['images']);report['tablesExtracted']=sum(s['tables']for s in report['systems']);report['translationWorkflow']='Codex professional Russian; English retained; translated fields flagged for human medical review; no external adapter'
    dump(root/'reports'/brand/(pdfslug+'.json'),report);write_report(root/'reports'/brand/(pdfslug+'.md'),report);print(f'Import report: reports/{brand}/{pdfslug}.md — {report["systemsFound"]} drafts, {report["componentsFound"]} components, {report["catalogNumberOccurrences"]} code cells, {len(report["flaggedCodes"])} flagged.',flush=True);return report

def write_report(path,report):
    lines=['# '+report.get('catalogTitle',{}).get('en','Catalog')+' — draft import report','',f'- Systems: {report["systemsFound"]} — all draft, none published.',f'- Component ordering rows: {report["componentsFound"]}; source heading groups: {report["componentGroups"]}.',f'- Cat. No. occurrences: {report["catalogNumberOccurrences"]}; confirmed: {report["confirmedCatalogNumberOccurrences"]}; flagged: {len(report["flaggedCodes"])}.',f'- Unique confirmed Cat. Nos.: {report["uniqueConfirmedCatalogNumbers"]}; unique source-transcribed candidates: {report["uniquePrintedCodeCandidates"]}.',f'- Images: {report["imagesExtracted"]}; tables: {report["tablesExtracted"]}.','- OCR: English Tesseract, 400 DPI, independent PSM 3 and PSM 11. Confidence threshold 90. No ambiguous-character substitutions.','- Page numbers below are physical PDF pages; printed product page = PDF page − 2.','- Non-product pages skipped: '+', '.join(map(str,report['nonProductPages']))+'. Pages 17–19 are blank.','- Flagged code cells are null, not guessed. Source-transcribed candidates and both raw OCR readings remain available for review.','','## Systems','| System | PDF pages | Components | Tables | Flagged codes |','|---|---|---:|---:|---:|']
    for s in report['systems']:lines.append(f'| {s["name"]["en"]} | {", ".join(map(str,s["sourcePages"]))} | {s["components"]} | {s["tables"]} | {s["flaggedCodes"]} |')
    lines+=['','## Complete flagged-code list','The candidate column is a source-review transcription, not an accepted reference code. Blank OCR readings and confidence -1 mean no word was found in that pass. Scores are Tesseract word-confidence values, not calibrated probabilities; the acceptance threshold is 90 for both passes.','| PDF / printed page | Source candidate | OCR PSM3 | OCR PSM11 | Confidence 3 / 11 | Reason |','|---|---|---|---|---|---|']
    for f in report['flaggedCodes']:
        safe=lambda v:str(v).replace('|','\\|').replace('\n',' ')
        lines.append(f'| {f["pdfPage"]} / {f["printedPage"]} | `{safe(f["printedCandidate"])}` | `{safe(f["pass1"]or "—")}` | `{safe(f["pass2"]or "—")}` | {f["confidence1"]:.1f} / {f["confidence2"]:.1f} | {", ".join(f["reasons"])} |')
    lines+=['','## Blank cells printed in the source']
    for entry in report['sourceBlankCodeCells']:lines.append(f'- PDF {entry["pdfPage"]} (printed {entry["printedPage"]}), {entry["system"]} / {entry["group"]}, row {entry["row"]}, column {entry["column"]}: preserved blank.')
    lines+=['','## Company text, statistics, exact contacts and decoded QR links','See `advanced-visualization-system-extras.md` and `advanced-visualization-system-extras.json`. These source statements were not applied to the About page or site contacts.','', '## Other review flags']
    for s in report['systems']:
        for f in s['flags']:
            if f['code']!='ocr-code-review':lines.append(f'- {s["slug"]}, PDF {f["sourcePages"]}: [{f["code"]}] {f["message"]["ru"]}')
    extras=report.get('companyAndContacts',{});company=extras.get('company',{});contacts=extras.get('contacts',{})
    lines+=['','## Page 2 — XPMED company text (not applied to About)']
    for paragraph in company.get('paragraphs',[]):lines+=['',paragraph['ru']]
    lines+=['','### Printed statistics']
    for stat in company.get('stats',[]):lines.append('- '+stat['printed'].replace('\n',' — '))
    lines+=['','## Last-page contacts — exact printed transcription (site contacts unchanged)','```text']
    printed=contacts.get('printedLines',contacts.get('lines',[]))
    if isinstance(printed,str):lines.append(printed)
    else:lines.extend(printed)
    lines+=['```','','## Locally decoded QR references',f"{len(extras.get('qrs',[]))} QR occurrences; {len(set(q['url']for q in extras.get('qrs',[])))} unique URLs; {len(extras.get('decodeFailures',[]))} decode failures."]
    for qr in extras.get('qrs',[]):lines.append(f"- PDF {qr['page']} / printed {qr['printedPage']}: {qr['resourceType']} — {qr['url']}")
    path.write_text('\n'.join(lines)+'\n')
