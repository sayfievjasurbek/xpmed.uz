#!/usr/bin/env python3
import subprocess,time,os,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];work=Path('/tmp/conmed-arthroscopy/assets');log=(work/'upscale.log').open('w');cmd=['/tmp/xpmed-realesrgan/realesrgan-ncnn-vulkan','-i',str(work/'input'),'-o',str(work/'output'),'-n','realesrgan-x4plus','-s','4','-m','/tmp/xpmed-realesrgan/models','-j','1:1:1','-t','128','-f','png'];gpu=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
while True:
 subprocess.run(['/tmp/xpmed-rembg-venv/bin/python',str(R/'scripts/process-arthroscopy-assets.py')],cwd=R,check=True,env={**os.environ,'U2NET_HOME':'/tmp/xpmed-rembg-models','OMP_NUM_THREADS':'1'})
 if gpu.poll()is not None:break
 time.sleep(4)
if gpu.returncode:raise SystemExit(gpu.returncode)
print('Real-ESRGAN + rembg completed',flush=True)
