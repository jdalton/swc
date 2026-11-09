import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from pathlib import Path
p=Path('/tmp/swc-ratio-v2')
data=[]
import statistics
observations=json.loads((p/'results.json').read_text())
summary=[]
for item in observations:
 before=[r for r in item['runs'] if r['variant']=='baseline']
 after=[r for r in item['runs'] if r['variant']=='candidate']
 assert len({r['compressed_bytes'] for r in before})==1
 assert len({r['compressed_bytes'] for r in after})==1
 data.append(dict(name=item['name'],version=item['version'],raw_bytes=item['raw_bytes'],before=before[0]['compressed_bytes'],after=after[0]['compressed_bytes']))
 entry=dict(name=item['name'],sha256=item['sha256'])
 for variant,runs in [('baseline',before),('candidate',after)]:
  entry[variant]={key:{'median':statistics.median(r[key] for r in runs),'min':min(r[key] for r in runs),'max':max(r[key] for r in runs)} for key in ['pack_seconds','decode_ms','peak_process_bytes']}
 summary.append(entry)
(p/'costs.json').write_text(json.dumps(summary,indent=2)+'\n')
(p/'measurements.json').write_text(json.dumps(dict(platform='Darwin ARM64',metric='zstd payload bytes (excludes carrier header)',baseline_level=16,candidate_level=19,candidate_long_distance_matching=True,results=data),indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079'})
fig,ax=plt.subplots(figsize=(12,6.5),dpi=180)
fig.patch.set_facecolor('#f8fafc'); ax.set_facecolor('#f8fafc')
fig.subplots_adjust(left=.17,right=.81,top=.72,bottom=.24)
fig.text(.07,.91,'Smaller native payloads',fontsize=26,weight='bold')
fig.text(.07,.845,'Level 16 → level 19 + long-distance matching',fontsize=13,color='#526079')
for i,d in enumerate(data):
 y=1-i
 ax.barh(y+.16,d['before']/1e6,height=.24,color='#9aaac1',label='Before' if i==0 else None,zorder=3)
 ax.barh(y-.16,d['after']/1e6,height=.24,color='#087f8c',label='After' if i==0 else None,zorder=3)
 for offset,key in [(.16,'before'),(-.16,'after')]:
  ax.text(d[key]/1e6-.16,y+offset,f"{d[key]/1e6:.3f} MB",va='center',ha='right',weight='bold',color='white',fontsize=11)
 pct=(1-d['after']/d['before'])*100
 ax.text(13.1,y+.06,f'−{pct:.2f}%',ha='left',va='center',fontsize=23,color='#087f8c',weight='bold')
 ax.text(13.1,y-.19,f"{(d['before']-d['after'])/1000:.1f} kB saved",ha='left',va='center',fontsize=10,color='#526079')
ax.set_yticks([1,0],['SWC 1.16.2','Rspack 1.7.0']);ax.tick_params(axis='y',length=0,pad=15)
ax.set_xlim(0,13);ax.set_ylim(-.55,1.55);ax.set_xticks([0,3,6,9,12]);ax.set_xlabel('Compressed payload size (MB, decimal) · lower is better',labelpad=12)
ax.grid(axis='x',color='#e0e6ee',zorder=0)
for s in ax.spines.values():s.set_visible(False)
ax.legend(loc='upper left',bbox_to_anchor=(0,1.23),frameon=False,ncol=2)
fig.text(.07,.095,'Measured Darwin ARM64 binaries · repeated sizes matched; decoded bytes verified',fontsize=10,color='#526079')
fig.text(.07,.055,'Payload size only. Not npm download size, startup speed, or total disk use. Two inputs; results may vary.',fontsize=9,color='#526079')
fig.savefig(p/'native-payload-sizes-v2.png',facecolor=fig.get_facecolor())
