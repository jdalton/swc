import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079','ytick.color':'#526079'})
combined=json.loads((p/'summary.json').read_text());carriers=json.loads((p/'combined-carriers.json').read_text())
profile=json.loads((p/'combined-metadata.json').read_text())['final_variant']
fig,axes=plt.subplots(1,3,figsize=(15,6.3),dpi=180);fig.patch.set_facecolor('#f8fafc');fig.subplots_adjust(left=.055,right=.98,top=.73,bottom=.25,wspace=.34)
fig.text(.045,.93,'8–10% smaller addon files, 11–12% less decoding time',fontsize=24,weight='bold')
fig.text(.045,.87,'Original level 16 + streaming → current level 22 + bounded bulk decoding + batched writes',fontsize=12,color='#526079')
for ax,metric,title,unit in zip(axes,['carrier','wall_ms','peak_process_bytes'],['Complete .node file','Verified decoding elapsed','Peak benchmark process memory'],['MB, decimal','Milliseconds','MB, decimal']):
 ax.set_facecolor('#f8fafc');values=[]
 for i,name in enumerate(['SWC','Rspack']):
  before=carriers[name]['original_bytes']/1e6 if metric=='carrier' else combined[name]['original16_stream'][metric]/(1e6 if metric=='peak_process_bytes' else 1)
  after=carriers[name]['final_bytes']/1e6 if metric=='carrier' else combined[name][profile][metric]/(1e6 if metric=='peak_process_bytes' else 1)
  values.extend([before,after])
  for offset,val,color,label in [(-.18,before,'#9aaac1','Original control'),(.18,after,'#087f8c','Current result')]:
   ax.bar(i+offset,val,width=.30,color=color,label=label if i==0 else None,zorder=3)
   ax.text(i+offset,val*1.025,f'{val:.3f}' if metric=='carrier' else f'{val:.2f}',ha='center',fontsize=10)
 ax.set_ylim(0,max(values)*1.20);ax.set_xticks([0,1],['SWC 1.16.2','Rspack 1.7.0']);ax.set_title(title,pad=15);ax.set_ylabel(unit+' · lower is better');ax.grid(axis='y',color='#e0e6ee',zorder=0)
 for spine in ax.spines.values():spine.set_visible(False)
axes[0].legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.19),ncol=2,fontsize=10)
fig.text(.045,.10,'Built .node files; runtime values are medians of 5 process medians/input, 12 measured rounds/process after 2 warmups.',fontsize=10,color='#526079')
fig.text(.045,.055,'Darwin ARM64 · all output bytes verified · guarded indexer suspension; other work remained active · not cold-start latency.',fontsize=10,color='#526079')
fig.savefig(p/'native-cumulative-result.png',facecolor=fig.get_facecolor());plt.close(fig)
