import pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).parent
a=json.loads((p/'allocation-chart-input.json').read_text());s=json.loads((p/'packing-summary.json').read_text())
before=a['lookup_table']['hash23_reference']/1e6;after=a['lookup_table']['hash20_candidate']/1e6;saved=before-after
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079'})
fig,ax=plt.subplots(figsize=(12,6.8),dpi=180);fig.patch.set_facecolor('#f8fafc');ax.set_facecolor('#f8fafc');fig.subplots_adjust(left=.23,right=.80,top=.72,bottom=.39)
fig.text(.07,.91,f'{saved:.2f} MB less compression lookup-table memory',fontsize=23,weight='bold')
fig.text(.07,.85,'Large-table control (hash log 23) → final table (hash log 20)',fontsize=12,color='#526079')
for y,v,color in [(1,before,'#9aaac1'),(0,after,'#087f8c')]:
 ax.barh(y,v,height=.35,color=color,zorder=3)
 ax.text(v+.5,y,f'{v:.2f} MB',ha='left',va='center',fontsize=12,weight='bold',color='#18263b')
ax.set_xlim(0,40);ax.set_ylim(-.6,1.6);ax.set_yticks([1,0],['Reference table','Final table']);ax.tick_params(axis='y',length=0,pad=15)
ax.set_xticks([0,10,20,30,40]);ax.set_xlabel('Compression lookup-table allocation (MB, decimal)',labelpad=12);ax.grid(axis='x',color='#e0e6ee',zorder=0)
for spine in ax.spines.values():spine.set_visible(False)
fig.text(.83,.58,'−87.5%',fontsize=22,color='#087f8c',weight='bold');fig.text(.83,.535,'table allocation',fontsize=10,color='#526079')
fig.text(.07,.235,'Hash 21 control → Hash 20 comparison: 4.19 MB less table memory and median benchmark RSS on both inputs.',fontsize=11,color='#18263b')
fig.text(.07,.18,'Quiet paired CPU cost for that step: SWC +9.00% · Rspack +5.02% (whole benchmark process).',fontsize=10,color='#526079')
fig.text(.07,.125,'Table allocation is not total packing memory. Hash 23 is the large-table control, not zstd’s default.',fontsize=10,color='#526079')
fig.text(.07,.075,'RSS check: 3 alternating fresh-process pairs/input; compressor retained through exact round-trip verification.',fontsize=9,color='#526079')
fig.text(.07,.035,'No claim of application/runtime memory savings from this packing table change.',fontsize=9,color='#526079')
fig.savefig(p/'packing-memory-final.png',facecolor=fig.get_facecolor())
