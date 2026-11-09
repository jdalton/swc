import subprocess,pathlib,json,re,hashlib,datetime,time
p=pathlib.Path(__file__).parent;src=pathlib.Path('/tmp/swc-compression-bench');orig=pathlib.Path('/tmp/swc-decoding-quiet-final');rows=[];snapshots=[]
variants=['original16_stream','hash21_bulk','hash20_batch256']
orders=[variants[i:]+variants[:i] for i in range(3)]+[list(reversed(variants)),[variants[1],variants[0],variants[2]]]
for name,raw in [('SWC',src/'swc-1.16.2.node'),('Rspack',src/'rspack-1.7.0.node')]:
 for trial,order in enumerate(orders):
  host=subprocess.check_output(['top','-l','2','-s','1','-n','0'],text=True)
  snapshots.append(dict(input=name,trial=trial,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cpu_idle_percent=float(re.findall(r'([0-9.]+)% idle',host)[-1]),raw=host));(p/'host.json').write_text(json.dumps(snapshots,indent=2)+'\n')
  for variant in order:
   if time.time()>datetime.datetime.fromisoformat('2026-11-09T21:01:30+00:00').timestamp()-30:raise SystemExit('Stop before guarded indexer restoration')
   exe=pathlib.Path('/tmp/swc-combined-final' if variant=='hash20_batch256' else '/tmp/swc-quiet-final-before' if variant=='original16_stream' else '/tmp/swc-quiet-final-after')
   frame=orig/(name+'-original16.zst') if variant=='original16_stream' else pathlib.Path(str(raw)+('.memory21.zst' if variant=='hash21_bulk' else '.hash20.zst'))
   r=subprocess.run(['/usr/bin/time','-lp',str(exe),str(raw),str(frame)],capture_output=True,text=True,check=True)
   samples=[]
   for line in r.stdout.splitlines():
    d=dict(re.findall(r'(\w+)=([^\s]+)',line));samples.append(dict(round=int(d['round']),wall_ms=float(d['decode_ms']),cpu_ms=float(d['cpu_ms'])))
   assert len(samples)==14
   row=dict(input=name,trial=trial,variant=variant,frame_sha256=hashlib.sha256(frame.read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),peak_process_bytes=int(re.search(r'(\d+)\s+maximum resident set size',r.stderr).group(1)),samples=samples)
   rows.append(row);(p/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(name,trial,variant,'done',flush=True)
