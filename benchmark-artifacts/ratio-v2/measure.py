import subprocess,pathlib,json,re,hashlib,statistics
p=pathlib.Path('/tmp/swc-ratio-v2');exe='/tmp/swc-native-focused-checks/release/examples/compare_compression'
inputs=[('SWC','1.16.2','/tmp/swc-compression-bench/swc-1.16.2.node'),('Rspack','1.7.0','/Users/jdalton/projects/swc-native-improvements/node_modules/@rspack/binding-darwin-arm64/rspack.darwin-arm64.node')]
data=[]
for name,version,path in inputs:
 raw=pathlib.Path(path).read_bytes();item=dict(name=name,version=version,raw_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),runs=[])
 for trial in range(3):
  for variant in (['baseline','candidate'] if trial%2==0 else ['candidate','baseline']):
   r=subprocess.run(['/usr/bin/time','-l',exe,path,'--'+variant],capture_output=True,text=True,check=True)
   metrics=dict(re.findall(r'(\w+)=([^\s]+)',r.stdout))
   run=dict(trial=trial,variant=variant,compressed_bytes=int(metrics['compressed_bytes']),pack_seconds=float(metrics['pack_seconds']),decode_ms=float(metrics['decode_ms']),peak_process_bytes=int(re.search(r'(\d+)\s+maximum resident set size',r.stderr).group(1)))
   item['runs'].append(run);print(name,json.dumps(run),flush=True)
   (p/'progress.json').write_text(json.dumps(data+[item],indent=2))
 data.append(item)
(p/'results.json').write_text(json.dumps(data,indent=2)+'\n')
