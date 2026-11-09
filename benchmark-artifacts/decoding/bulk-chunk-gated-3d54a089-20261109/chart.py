import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).parent;d=json.loads((p/'final-summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,axes=plt.subplots(1,2,figsize=(12,6.4),dpi=180)
fig.patch.set_facecolor('#f8fafc');fig.subplots_adjust(left=.08,right=.96,top=.73,bottom=.25,wspace=.32)
fig.text(.05,.92,'Bulk decoding + chunked writes: not adopted',fontsize=22,weight='bold',color='#18263b')
fig.text(.05,.86,'Final gated candidate used less memory but took longer on both inputs',fontsize=12,color='#526079')
for ax,metric,title in zip(axes,['wall_ms','peak_process_bytes'],['Elapsed decoding time','Peak benchmark process memory']):
 ax.set_facecolor('#f8fafc')
 for i,name in enumerate(['SWC','Rspack']):
  for offset,v,color,label in [(-.18,'before','#8b9bb2','Current streaming'),(.18,'after','#af6a40','Bulk + chunked experiment')]:
   val=d[name][v][metric]/(1e6 if metric=='peak_process_bytes' else 1)
   ax.bar(i+offset,val,width=.30,color=color,label=label if i==0 else None,zorder=3)
   ax.text(i+offset,val+(7 if metric=='wall_ms' else 2.5),f'{val:.1f}' if metric=='wall_ms' else f'{val:.2f}',ha='center',fontsize=10)
 ax.set_xticks([0,1],['SWC 1.16.2','Rspack 1.7.0']);ax.set_ylim(0,380 if metric=='wall_ms' else 125);ax.set_title(title,pad=14)
 ax.set_ylabel('Milliseconds · lower is better' if metric=='wall_ms' else 'MB, decimal · lower is better');ax.grid(axis='y',color='#e0e6ee',zorder=0)
 for spine in ax.spines.values():spine.set_visible(False)
axes[0].legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.19),ncol=2,fontsize=9)
fig.text(.05,.095,'Darwin ARM64 · final confirmation only · 5 process pairs/input · median of process medians',fontsize=10,color='#526079')
fig.text(.05,.055,'Same SearchLog 8 frames. Full BLAKE3 + tempfile writes. Host contention; no startup or cross-platform claim.',fontsize=9,color='#526079')
fig.savefig(p/'bulk-chunk-confirmation.png',facecolor=fig.get_facecolor())
