import subprocess,shutil
subprocess.run(['cargo','build','-p','swc_native_addon','--release','--example','compare_decoding','--target-dir','/tmp/swc-decode-pass-target'],cwd='/Users/jdalton/projects/swc-native-decode-pass',check=True)
shutil.copy2('/tmp/swc-decode-pass-target/release/examples/compare_decoding','/tmp/swc-bulk-chunk-decode-after')
import subprocess,pathlib,json,re,hashlib
p=pathlib.Path('/tmp/swc-decoding-bulk-chunk-confirm');data=[];src=pathlib.Path('/tmp/swc-compression-bench')
for name,raw in [('SWC',src/'swc-1.16.2.node'),('Rspack',src/'rspack-1.7.0.node')]:
 frame=pathlib.Path(str(raw)+'.search8.zst')
 for trial in range(5):
  for variant in (['before','after'] if trial%2==1 else ['after','before']):
   r=subprocess.run(['/usr/bin/time','-lp','/tmp/swc-bulk-chunk-decode-'+variant,str(raw),str(frame)],capture_output=True,text=True,check=True)
   samples=[]
   for line in r.stdout.splitlines():
    d=dict(re.findall(r'(\w+)=([^\s]+)',line));samples.append(dict(round=int(d['round']),wall_ms=float(d['decode_ms']),cpu_ms=float(d['cpu_ms'])))
   row=dict(input=name,trial=trial,variant=variant,frame_sha256=hashlib.sha256(frame.read_bytes()).hexdigest(),peak_process_bytes=int(re.search(r'(\d+)\s+maximum resident set size',r.stderr).group(1)),samples=samples)
   data.append(row);(p/'results.json').write_text(json.dumps(data,indent=2)+'\n');print(name,trial,variant,'done',flush=True)
