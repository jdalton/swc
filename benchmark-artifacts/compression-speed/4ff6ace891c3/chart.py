import json,statistics,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).parent
rows=json.loads((p/'results.json').read_text());summary={}
for name in ['SWC','Rspack']:
 summary[name]={}
 for variant in ['search8','memory21']:
  r=[r for r in rows if r['input']==name and r['variant']==variant]
  assert len(r)==3
  summary[name][variant]={k:{'median':statistics.median(x[k] for x in r),'min':min(x[k] for x in r),'max':max(x[k] for x in r)} for k in ['bytes','pack_seconds','cpu_seconds','peak_process_bytes']}
 pairs=[]
 for trial in range(3):
  a=next(r for r in rows if r['input']==name and r['variant']=='search8' and r['trial']==trial)
  b=next(r for r in rows if r['input']==name and r['variant']=='memory21' and r['trial']==trial)
  pairs.append({'trial':trial,'rss_decrease_bytes':a['peak_process_bytes']-b['peak_process_bytes'],'rss_decrease_percent':(1-b['peak_process_bytes']/a['peak_process_bytes'])*100})
 summary[name]['pairs']=pairs
(p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079'})
fig,ax=plt.subplots(figsize=(12,6.8),dpi=180);fig.patch.set_facecolor('#f8fafc');ax.set_facecolor('#f8fafc');fig.subplots_adjust(left=.17,right=.79,top=.70,bottom=.28)
fig.text(.07,.91,'25.17 MB smaller compression lookup table',fontsize=24,weight='bold')
fig.text(.07,.85,'Hash log 23 → 21: table 33.55 → 8.39 MB · neither payload grows',fontsize=12,color='#526079')
expected=(2**25-2**23)/1e6
ax.axvline(expected,color='#94a3b8',linestyle='--',linewidth=1.8,label='Table allocation saving',zorder=2)
for i,(name,d) in enumerate(summary.items()):
 y=1-i;values=[r['rss_decrease_bytes']/1e6 for r in d['pairs']]
 for j,v in enumerate(values):
  ax.scatter([v],[y+(j-1)*.14],s=90,color='#087f8c',edgecolor='white',linewidth=.6,zorder=4,label='Measured paired peak-memory decrease' if i==0 and j==0 else None)
 ax.text(77,y+.07,f'{statistics.median(values):.2f} MB',ha='left',va='center',fontsize=20,color='#087f8c',weight='bold')
 ax.text(77,y-.17,'median paired decrease',ha='left',va='center',fontsize=9,color='#526079')
ax.set_yticks([1,0],['SWC 1.16.2','Rspack 1.7.0']);ax.tick_params(axis='y',length=0,pad=15);ax.set_xlim(0,75);ax.set_ylim(-.5,1.5)
ax.set_xticks([0,25,50,75]);ax.set_xlabel('Observed reduction in peak benchmark memory (MB, decimal)',labelpad=12)
ax.grid(axis='x',color='#e0e6ee',zorder=0)
for s in ax.spines.values():s.set_visible(False)
ax.legend(loc='upper left',bbox_to_anchor=(0,1.23),frameon=False,ncol=2,fontsize=10)
fig.text(.07,.16,'3 alternating fresh-process pairs/input · other host work made Rspack readings noisy',fontsize=10,color='#526079')
fig.text(.07,.115,'Extra measured reductions beyond 25.17 MB are not attributed to the table change.',fontsize=10,color='#526079')
fig.text(.07,.07,'Compression + exact round-trip; context retained. Not runtime memory or direct production-packer RSS.',fontsize=9,color='#526079')
fig.text(.07,.035,'Benchmark CPU cost: +8.98% SWC / +8.65% Rspack. No compression-speed improvement claimed.',fontsize=9,color='#526079')
fig.savefig(p/'native-memory21.png',facecolor=fig.get_facecolor())
