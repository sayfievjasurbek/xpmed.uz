"""Use the identical Real-ESRGAN weights on CPU, from the end of the source batch."""
import json,os,time
from pathlib import Path
from PIL import Image
from realesrgan_cpu import CPUUpscaler
R=Path(__file__).resolve().parents[1];F=R/'reports/double-medical/trauma-catalogue-part3';A=R/'public/images/products/double-medical/trauma-catalogue-part3';W=Path('/tmp/xpmed-trauma-part3/native-artwork')
assets=json.loads((F/'source-images.json').read_text());record=F/'cpu-enhancement-assists.json';done=json.loads(record.read_text())if record.exists()else{};cpu=CPUUpscaler();start=time.time()
for name in sorted(assets,key=lambda key:assets[key]['originalSize'][0]*assets[key]['originalSize'][1]):
    if assets[name]['originalSize'][0]*assets[name]['originalSize'][1]>60000:continue
    ready=json.loads((A/'prepared-assets.json').read_text())if(A/'prepared-assets.json').exists()else{}
    if name in ready or (W/'output'/(name+'.png')).exists():continue
    output=cpu.process(Image.open(A/'_originals'/(name+'.png')))
    done[name]={'executionProvider':'OpenCV DNN CPU, unchanged original Real-ESRGAN x4plus NCNN weights','weightsSha256':'713ee713b0353afaa27976f0563a64a5043bd70b9bd8936c2e26e25ebcdbcddf'}
    record.write_text(json.dumps(done,indent=2)+'\n');temp=W/'output'/(name+'.cpu.png');output.save(temp);os.replace(temp,W/'output'/(name+'.png'))
    print('CPU assists',len(done),'seconds',round(time.time()-start),flush=True)
