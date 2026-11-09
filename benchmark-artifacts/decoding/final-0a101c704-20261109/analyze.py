import json,statistics,pathlib
p=pathlib.Path(__file__).parent;rows=json.loads((p/'results.json').read_text());summary={}
for name in ['SWC','Rspack']:
 summary[name]={}
 for variant in ['original16_stream','hash21_bulk','hash20_batch256']:
  selected=[r for r in rows if r['input']==name and r['variant']==variant];assert len(selected)==5
  medians=[dict(trial=r['trial'],**{k:statistics.median(s[k] for s in r['samples'][2:]) for k in ['wall_ms','cpu_ms']}) for r in selected]
  summary[name][variant]={'process_medians':medians,**{k:statistics.median(r[k] for r in medians) for k in ['wall_ms','cpu_ms']},'peak_process_bytes':statistics.median(r['peak_process_bytes'] for r in selected)}
(p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
