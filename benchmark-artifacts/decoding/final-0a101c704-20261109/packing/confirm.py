"""Build with cargo build --release --bin tune.
Run: python3 repeat.py ./target/release/tune swc-1.16.2.node rspack-1.7.0.node
Uses macOS /usr/bin/time -lp. Frames are written beside the input binaries.
Inputs must be the Darwin ARM64 npm binaries at the versions named above.
"""
import subprocess,json,pathlib,re,hashlib,sys,datetime,time
p=pathlib.Path(__file__).resolve().parent
exe=pathlib.Path(sys.argv[1]).resolve()
inputs=[('SWC',pathlib.Path(sys.argv[2]).resolve(),'01053e9b9792e8c1c433ac7feeeecdb5e552fb92d58de6e35b084521eae6f04a'),('Rspack',pathlib.Path(sys.argv[3]).resolve(),'2d0320114bcacefe361be27c0e301d40201ab57bc61162e83dd3c0f1f611a955')]
for name,path,sha in inputs:
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha, 'Input does not match recorded '+name+' binary'
rows=[]
for name,path,sha in inputs:
 for trial in range(3):
  for variant in (['memory21',sys.argv[4]] if trial%2==0 else [sys.argv[4],'memory21']):
   if time.time()>datetime.datetime.fromisoformat('2026-11-09T20:40:30+00:00').timestamp()-120:
    raise SystemExit('Stop before guarded indexer restoration')
   host=subprocess.check_output(['top','-l','2','-s','1','-n','0'],text=True)
   idle=float(re.findall(r'([0-9.]+)% idle',host)[-1])
   r=subprocess.run(['/usr/bin/time','-lp',str(exe),str(path),variant],capture_output=True,text=True,check=True)
   metrics=dict(re.findall(r'(\w+)=([^\s]+)',r.stdout))
   cpu=sum(float(re.search(r'^'+key+r'\s+(\S+)',r.stderr,re.M).group(1)) for key in ['user','sys'])
   row=dict(cpu_idle_before=idle,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),input=name,trial=trial,variant=variant,bytes=int(metrics['bytes']),pack_seconds=float(metrics['pack_s']),cpu_seconds=cpu,peak_process_bytes=int(re.search(r'(\d+)\s+maximum resident set size',r.stderr).group(1)),frame_sha256=hashlib.sha256(pathlib.Path(str(path)+'.'+variant+'.zst').read_bytes()).hexdigest())
   rows.append(row);print(json.dumps(row),flush=True);(p/'confirmation.json').write_text(json.dumps(rows,indent=2)+'\n')
