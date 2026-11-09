import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from pathlib import Path
p=Path('/tmp/swc-pr-charts')
data=[dict(name='SWC',version='1.16.2',raw_bytes=26612480,before=8446098,after=8326319),dict(name='Rspack',version='1.7.0',raw_bytes=40506208,before=12406049,after=12090180)]
(p/'measurements.json').write_text(json.dumps(dict(platform='Darwin ARM64',metric='zstd payload bytes (excludes carrier header)',compression_level=16,results=data),indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079'})
fig,ax=plt.subplots(figsize=(12,6.5),dpi=180)
fig.patch.set_facecolor('#f8fafc'); ax.set_facecolor('#f8fafc')
fig.subplots_adjust(left=.17,right=.81,top=.72,bottom=.24)
fig.text(.07,.91,'Smaller native payloads',fontsize=26,weight='bold')
fig.text(.07,.845,'Long-distance matching · same zstd compression level (16)',fontsize=13,color='#526079')
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
fig.savefig(p/'native-payload-sizes.png',facecolor=fig.get_facecolor())
