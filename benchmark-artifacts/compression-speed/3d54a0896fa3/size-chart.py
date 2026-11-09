import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).resolve().parent
rows=json.loads((p/'search8.json').read_text())
summary=[dict(name=name,version=version,original_bytes=baseline,selected={'bytes':{'median':next(r['bytes'] for r in rows if r['input']==name)}}) for name,version,baseline in [('SWC','1.16.2',8446098),('Rspack','1.7.0',12406049)]]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079'})
for kind in ['size']:
 fig,ax=plt.subplots(figsize=(12,6.5),dpi=180);fig.patch.set_facecolor('#f8fafc');ax.set_facecolor('#f8fafc');fig.subplots_adjust(left=.17,right=.81,top=.72,bottom=.24)
 fig.text(.07,.91,'Smaller native payloads' if kind=='size' else 'Lower maximum-level packing memory',fontsize=25,weight='bold')
 fig.text(.07,.845,'Original level 16 → tuned level 22 + long-distance matching' if kind=='size' else 'Level 22 control → bounded probe table and search work',fontsize=12,color='#526079')
 limit=13 if kind=='size' else 850
 for i,d in enumerate(summary):
  y=1-i
  before=d['original_bytes']/1e6 if kind=='size' else d['full']['peak_process_bytes']['median']/1e6
  after=d['selected']['bytes']['median']/1e6 if kind=='size' else d['selected']['peak_process_bytes']['median']/1e6
  for offset,v,color,label,variant in [(.16,before,'#9aaac1','Before','full'),(-.16,after,'#087f8c','After','selected')]:
   ax.barh(y+offset,v,height=.24,color=color,label=label if i==0 else None,zorder=3)
   if kind=='memory':
    m=d[variant]['peak_process_bytes'];ax.errorbar(v,y+offset,xerr=[[v-m['min']/1e6],[m['max']/1e6-v]],fmt='none',ecolor='#27364c',capsize=3,zorder=4)
   ax.text(limit*.025 if kind=='memory' else v-limit*.012,y+offset,f'{v:.1f} MB' if kind=='memory' else f'{v:.3f} MB',va='center',ha='left' if kind=='memory' else 'right',weight='bold',color='white',fontsize=11)
  pct=(1-after/before)*100
  ax.text(limit*1.01,y+.06,f'−{pct:.2f}%',ha='left',va='center',fontsize=23,color='#087f8c',weight='bold')
  saved=f'{(before-after)*1000:.1f} kB saved' if kind=='size' else f'{before-after:.1f} MB saved'
  ax.text(limit*1.01,y-.19,saved,ha='left',va='center',fontsize=10,color='#526079')
 ax.set_yticks([1,0],[f"{d['name']} {d['version']}" for d in summary]);ax.tick_params(axis='y',length=0,pad=15);ax.set_xlim(0,limit);ax.set_ylim(-.55,1.55)
 ax.set_xticks([0,3,6,9,12] if kind=='size' else [0,200,400,600,800]);ax.set_xlabel(('Compressed payload size' if kind=='size' else 'Peak benchmark process memory')+' (MB, decimal) · lower is better',labelpad=12)
 ax.grid(axis='x',color='#e0e6ee',zorder=0)
 for s in ax.spines.values():s.set_visible(False)
 ax.legend(loc='upper left',bbox_to_anchor=(0,1.23),frameon=False,ncol=2)
 fig.text(.07,.095,'Darwin ARM64 binaries · probe and production sizes matched; every decoded byte verified' if kind=='size' else 'Apple M1 Max · 3 fresh processes/variant/input · median; whiskers = min–max',fontsize=10,color='#526079')
 fig.text(.07,.055,'Payload bytes only; not npm transfer size, startup speed, or total disk use.' if kind=='size' else 'Maximum-level compression + round-trip verification. Not runtime memory; no CPU-speed claim.',fontsize=9,color='#526079')
 fig.savefig(p/f'native-{kind}-search8.png',facecolor=fig.get_facecolor());plt.close(fig)
