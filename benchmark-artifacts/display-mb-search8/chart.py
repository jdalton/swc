import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).parent
rows=json.loads((p/'screen.json').read_text())
rows=[dict(variant='compact',bytes=7698922)]+[r for r in rows if r['input']=='SWC']
labels={'compact':'Smaller tree (chain 25)','search4':'Fewer searches (search 4)','min4':'Longer minimum match (4)','target64':'Earlier match cutoff (64)','search8':'More searches (search 8)'}
base=7698505
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#18263b','axes.labelcolor':'#526079','xtick.color':'#526079'})
fig,ax=plt.subplots(figsize=(12,6.8),dpi=180);fig.patch.set_facecolor('#f8fafc');ax.set_facecolor('#f8fafc');fig.subplots_adjust(left=.30,right=.83,top=.74,bottom=.23)
fig.text(.07,.91,'Size remains the first gate',fontsize=25,weight='bold')
fig.text(.07,.85,'Compression experiments compared with the current SWC payload',fontsize=12,color='#526079')
ax.axvline(base/1e6,color='#087f8c',linewidth=2,label='Reference: 7.6985 MB')
for i,r in enumerate(rows):
 y=len(rows)-1-i;v=r['bytes']/1e6
 ax.plot([base/1e6,v],[y,y],color='#c2cbd8',linewidth=3)
 ax.scatter([v],[y],s=85,color='#c57236',zorder=4)
 ax.text(8.025,y,f"{(r['bytes']-base)/1e6:+.4f} MB",va='center',fontsize=11,weight='bold',color='#9a5626')
ax.set_yticks(range(len(rows)),[labels[r['variant']] for r in reversed(rows)]);ax.tick_params(axis='y',length=0,pad=12)
ax.set_xlim(7.68,8.02);ax.set_ylim(-.6,len(rows)-.4);ax.set_xticks([7.7,7.8,7.9,8.0]);ax.set_xlabel('Compressed payload size (MB, decimal) · lower is better',labelpad=12)
ax.grid(axis='x',color='#e0e6ee',zorder=0)
for s in ax.spines.values():s.set_visible(False)
ax.legend(loc='upper left',bbox_to_anchor=(0,1.18),frameon=False)
fig.text(.07,.10,'@swc/core-darwin-arm64 1.16.2 · each completed run passed exact decoded-byte equality',fontsize=10,color='#526079')
fig.text(.07,.055,'Screening results only. Candidates that increase either input were rejected; no compression-speed claim.',fontsize=9,color='#526079')
fig.savefig(p/'rejected-size-tradeoffs.png',facecolor=fig.get_facecolor())
