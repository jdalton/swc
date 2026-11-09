import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).parent
d=json.loads((p/'summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,axes=plt.subplots(1,2,figsize=(12,6),dpi=180)
fig.patch.set_facecolor('#f8fafc')
fig.subplots_adjust(left=.09,right=.96,top=.73,bottom=.24,wspace=.30)
fig.text(.06,.91,'128 KiB decoding buffer: not adopted',fontsize=23,weight='bold',color='#18263b')
fig.text(.06,.85,'Lower CPU time did not consistently reduce elapsed decoding time',fontsize=12,color='#526079')
for ax,metric,title in zip(axes,['wall_ms','cpu_ms'],['Elapsed decoding time','CPU consumed by decoding']):
 ax.set_facecolor('#f8fafc')
 for i,name in enumerate(['SWC','Rspack']):
  for offset,v,color,label in [(-.18,'before','#8b9bb2','64 KiB current'),(.18,'after','#af6a40','128 KiB experiment')]:
   val=d[name][v][metric];ax.bar(i+offset,val,width=.30,color=color,label=label if i==0 else None,zorder=3)
   ax.text(i+offset,val+3,f'{val:.1f}',ha='center',fontsize=10)
 ax.set_xticks([0,1],['SWC 1.16.2','Rspack 1.7.0']);ax.set_ylim(0,210 if metric=='wall_ms' else 115);ax.set_title(title,pad=14);ax.set_ylabel('Milliseconds · lower is better');ax.grid(axis='y',color='#e0e6ee',zorder=0)
 for spine in ax.spines.values():spine.set_visible(False)
axes[0].legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.18),ncol=2,fontsize=10)
fig.text(.06,.08,'Darwin ARM64 · 5 fresh processes/variant/input · median of process medians · 12 measured rounds each',fontsize=10,color='#526079')
fig.text(.06,.04,'Same SearchLog 7 zstd frame per input. Includes full BLAKE3 + temporary-file writes; excludes fsync and addon loading.',fontsize=9,color='#526079')
fig.savefig(p/'decode-buffer-experiment.png',facecolor=fig.get_facecolor())
