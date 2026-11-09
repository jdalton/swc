import subprocess,pathlib,json,re,hashlib,sys
p=pathlib.Path(__file__).resolve().parent;data=[]
exe=sys.argv[1]
for name,raw in [('SWC',pathlib.Path(sys.argv[2]).resolve()),('Rspack',pathlib.Path(sys.argv[3]).resolve())]:
 for trial in range(5):
  for variant in (['selected','search8'] if trial%2==0 else ['search8','selected']):
   frame=pathlib.Path(str(raw)+'.'+variant+'.zst')
   r=subprocess.run(['/usr/bin/time','-lp',exe,str(raw),str(frame)],capture_output=True,text=True,check=True)
   samples=[]
   for line in r.stdout.splitlines():
    d=dict(re.findall(r'(\w+)=([^\s]+)',line));samples.append(dict(round=int(d['round']),wall_ms=float(d['decode_ms']),cpu_ms=float(d['cpu_ms'])))
   row=dict(input=name,trial=trial,variant=variant,frame_sha256=hashlib.sha256(frame.read_bytes()).hexdigest(),peak_process_bytes=int(re.search(r'(\d+)\s+maximum resident set size',r.stderr).group(1)),samples=samples)
   data.append(row);(p/'frame-results.json').write_text(json.dumps(data,indent=2)+'\n');print(name,trial,variant,'done',flush=True)
