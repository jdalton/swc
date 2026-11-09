import os,fcntl,struct,time,hashlib,json,subprocess,statistics,pathlib
root=pathlib.Path('/bench');mount=pathlib.Path('/mnt/benchmark')
raw=(root/'swc.linux-arm64-gnu.node').read_bytes();expected=hashlib.sha256(raw).hexdigest()
results=[]
for trial in range(10):
 for codec,name in ([(1,'zlib'),(3,'zstd')] if trial%2==0 else [(3,'zstd'),(1,'zlib')]):
  path=mount/(name+'.node')
  with path.open('wb',buffering=0) as f:
   f.write(raw)
   os.fsync(f.fileno()) # SWC replace() flushes staging before compress().
   start=time.perf_counter_ns()
   flags=bytearray(8);fcntl.ioctl(f,0x80086601,flags,True)
   flags=struct.pack('l',(struct.unpack('l',flags)[0]|4)&~0x400)
   fcntl.ioctl(f,0x40086602,flags)
   fcntl.ioctl(f,0x40309410,struct.pack('QQQII4I',0,2**64-1,3,1,codec,0,0,0,0))
   os.fsync(f.fileno())
   compress_ms=(time.perf_counter_ns()-start)/1e6
  disk=subprocess.check_output(['compsize','-b',str(path)],text=True)
  assert any(line.startswith(name+' ') for line in disk.splitlines()), disk
  reads=[];loads=[]
  for _ in range(7):
   with path.open('rb',buffering=0) as f:
    os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
    start=time.perf_counter_ns();decoded=f.read();reads.append((time.perf_counter_ns()-start)/1e6)
   assert hashlib.sha256(decoded).hexdigest()==expected
  for _ in range(7):
   with path.open('rb',buffering=0) as f:os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
   out=subprocess.check_output(['node','-e','const t=process.hrtime.bigint();require(process.argv[1]);console.log(Number(process.hrtime.bigint()-t)/1e6)',str(path)],text=True)
   loads.append(float(out))
  item=dict(trial=trial,codec=name,compress_ms=compress_ms,read_ms=reads,require_ms=loads,compsize=disk)
  results.append(item)
  print(json.dumps({k:v for k,v in item.items() if k!='compsize'}),flush=True)
  path.unlink()
(root/'results.json').write_text(json.dumps(dict(environment=subprocess.check_output(['uname','-a'],text=True).strip(),node=subprocess.check_output(['node','--version'],text=True).strip(),input=json.loads((root/'input.json').read_text()),results=results),indent=2))
