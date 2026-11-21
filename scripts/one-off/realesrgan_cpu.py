"""Run the existing Real-ESRGAN x4plus NCNN weights on the CPU via OpenCV DNN.
A minimal ONNX graph is serialized from the original layer definitions and weights;
no model training, replacement weights or GPU access are involved.
"""
import struct,hashlib,json,time
from pathlib import Path
import numpy as np,cv2
from PIL import Image

def varint(n):
 n=int(n);out=bytearray()
 while n>127:out.append((n&127)|128);n>>=7
 out.append(n);return bytes(out)
def integer(k,n):return varint(k<<3)+varint(n)
def blob(k,s):
 if isinstance(s,str):s=s.encode()
 return varint((k<<3)|2)+varint(len(s))+s
def tensor(name,array):
 a=np.asarray(array,dtype='<f4');return b''.join(integer(1,d)for d in a.shape)+integer(2,1)+blob(8,name)+blob(9,a.tobytes())
def attribute(name,value):
 b=blob(1,name)
 if isinstance(value,int):return b+integer(3,value)+integer(20,2)
 if isinstance(value,float):return b+varint((2<<3)|5)+struct.pack('<f',value)+integer(20,1)
 if isinstance(value,str):return b+blob(4,value)+integer(20,3)
 return b+blob(8,b''.join(varint(v)for v in value))+integer(20,7)
def node(op,ins,outs,name,**attrs):return b''.join(blob(1,v)for v in ins)+b''.join(blob(2,v)for v in outs)+blob(3,name)+blob(4,op)+b''.join(blob(5,attribute(k,v))for k,v in attrs.items())
def value_info(name,shape):
 dims=b''.join(blob(1,integer(1,d)if isinstance(d,int)else blob(2,d))for d in shape);typ=blob(1,integer(1,1)+blob(2,dims));return blob(1,name)+blob(2,typ)

def convert(model_dir,destination):
 param=Path(model_dir)/'realesrgan-x4plus.param';binary=Path(model_dir)/'realesrgan-x4plus.bin';raw=binary.read_bytes();offset=0;nodes=[];initializers=[];aliases={};count=0
 def resolve(s):
  while s in aliases:s=aliases[s]
  return s
 def weights(size):
  nonlocal offset
  tag=struct.unpack_from('<I',raw,offset)[0];offset+=4
  if tag==0x01306B47:
   a=np.frombuffer(raw,dtype='<f2',count=size,offset=offset).astype(np.float32);offset+=(size*2+3)//4*4
  elif tag==0:
   a=np.frombuffer(raw,dtype='<f4',count=size,offset=offset).copy();offset+=size*4
  else:raise ValueError(f'Unsupported weight encoding {tag:x}')
  return a
 for line in param.read_text().splitlines()[2:]:
  fields=line.split();kind,name=fields[:2];nb,nt=map(int,fields[2:4]);bottom=[resolve(s)for s in fields[4:4+nb]];top=fields[4+nb:4+nb+nt];p={}
  for item in fields[4+nb+nt:]:
   key,value=item.split('=');key=int(key)
   if key<=-23300:p[-key-23300]=[float(v)for v in value.split(',')[1:]]
   else:p[key]=float(value)
  if kind=='Input':continue
  if kind=='Split':
   for t in top:aliases[t]=bottom[0]
   continue
  if kind=='Convolution':
   out=int(p[0]);kernel=int(p[1]);size=int(p[6]);w=weights(size).reshape(out,size//out//kernel//kernel,kernel,kernel);wname=name+'_w';initializers.append(tensor(wname,w));inputs=bottom+[wname]
   if int(p.get(5,0)):
    bias=np.frombuffer(raw,dtype='<f4',count=out,offset=offset).copy();offset+=out*4;bname=name+'_b';initializers.append(tensor(bname,bias));inputs.append(bname)
   active=int(p.get(9,0));result=top if not active else[top[0]+'_conv'];nodes.append(node('Conv',inputs,result,name,kernel_shape=[kernel,kernel],pads=[int(p.get(4,0))]*4,strides=[int(p.get(3,1))]*2))
   if active:
    assert active==2;nodes.append(node('LeakyRelu',result,top,name+'_activation',alpha=float(p[10][0])))
  elif kind=='Concat':nodes.append(node('Concat',bottom,top,name,axis=1))
  elif kind=='Eltwise':
   assert int(p[0])==1;scaled=[]
   for i,(b,coefficient)in enumerate(zip(bottom,p.get(1,[1.0]*len(bottom)))):
    if coefficient==1:scaled.append(b);continue
    c=name+f'_coefficient{i}';t=name+f'_scaled{i}';initializers.append(tensor(c,np.array([coefficient],np.float32)));nodes.append(node('Mul',[b,c],[t],t));scaled.append(t)
   assert len(scaled)==2;nodes.append(node('Add',scaled,top,name))
  elif kind=='BinaryOp':assert int(p.get(0,0))==0;nodes.append(node('Add',bottom,top,name))
  elif kind=='Interp':
   assert int(p[0])==1;scales=name+'_scales';initializers.append(tensor(scales,np.array([1,1,p[1],p[2]],np.float32)));nodes.append(node('Upsample',bottom+[scales],top,name,mode='nearest'))
  else:raise ValueError('Unsupported original layer: '+kind)
 assert offset==len(raw),(offset,len(raw))
 graph=b''.join(blob(1,n)for n in nodes)+blob(2,'Original Real-ESRGAN x4plus')+b''.join(blob(5,t)for t in initializers)+blob(11,value_info('data',[1,3,'height','width']))+blob(12,value_info('output',[1,3,'height4','width4']))
 model=integer(1,7)+blob(2,'XPMED source-preserving NCNN conversion')+blob(7,graph)+blob(8,integer(2,9));Path(destination).write_bytes(model);return {'ncnnWeightsSha256':hashlib.sha256(raw).hexdigest(),'onnxSha256':hashlib.sha256(model).hexdigest(),'layers':len(nodes)}
class CPUUpscaler:
 def __init__(self,model_dir='/tmp/xpmed-realesrgan/models',tile=96):
  self.path=Path('/tmp/xpmed-realesrgan/realesrgan-x4plus-cpu.onnx');self.tile=tile
  metadata=self.path.with_suffix('.json');weightHash=hashlib.sha256((Path(model_dir)/'realesrgan-x4plus.bin').read_bytes()).hexdigest()
  if not self.path.exists()or not metadata.exists()or json.loads(metadata.read_text()).get('ncnnWeightsSha256')!=weightHash:
   proof=convert(model_dir,self.path);metadata.write_text(json.dumps(proof,indent=2));print('Converting original NCNN graph',proof,flush=True)
  cv2.setNumThreads(4);self.net=cv2.dnn.readNetFromONNX(str(self.path));self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV);self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
 def process(self,image):
  a=np.asarray(image.convert('RGB'));h,w=a.shape[:2];pad=10;source=np.pad(a,((pad,pad),(pad,pad),(0,0)),mode='reflect');out=np.zeros((h*4,w*4,3),np.uint8)
  for y in range(0,h,self.tile):
   for x in range(0,w,self.tile):
    th=min(self.tile,h-y);tw=min(self.tile,w-x);crop=source[y:y+th+2*pad,x:x+tw+2*pad];data=np.transpose(crop.astype(np.float32)/255,(2,0,1))[None];self.net.setInput(data);result=self.net.forward('output')[0];result=np.transpose(result,(1,2,0))[pad*4:(pad+th)*4,pad*4:(pad+tw)*4];out[y*4:(y+th)*4,x*4:(x+tw)*4]=np.clip(result*255,0,255).round().astype('uint8')
  return Image.fromarray(out)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args();start=time.time();cpu=CPUUpscaler();cpu.process(Image.open(a.input)).save(a.output);print('CPU seconds',time.time()-start)
