import json,statistics,pathlib
p=pathlib.Path(__file__).parent
rows=json.loads((p/'frame-results.json').read_text()); summary={}
for name in ['SWC']:
 summary[name]={}
 for variant in ['search8','memory21']:
  selected=[r for r in rows if r['input']==name and r['variant']==variant]
  process_medians=[{metric:statistics.median(s[metric] for s in r['samples'][2:]) for metric in ['wall_ms','cpu_ms']} for r in selected]
  summary[name][variant]={'process_medians':process_medians,**{metric:statistics.median(r[metric] for r in process_medians) for metric in ['wall_ms','cpu_ms']},'peak_process_bytes':statistics.median(r['peak_process_bytes'] for r in selected)}
 print(name,summary[name])
(p/'frame-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
