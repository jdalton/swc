import json,statistics,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path('/tmp/swc-btrfs-bench');data=json.loads((p/'results.json').read_text());summary={}
for codec in ['zlib','zstd']:
 r=[r for r in data['results'] if r['codec']==codec and r['trial']>=2]
 vals={'compress_ms':[x['compress_ms'] for x in r],'read_ms':[statistics.median(x['read_ms']) for x in r],'require_ms':[statistics.median(x['require_ms']) for x in r],'disk_bytes':[int(next(line for line in x['compsize'].splitlines() if line.startswith('TOTAL')).split()[2]) for x in r]}
 summary[codec]={key:{'median':statistics.median(v),'min':min(v),'max':max(v),'rounds':v} for key,v in vals.items()}
summary['reduction_percent']={key:100*(1-summary['zstd'][key]['median']/summary['zlib'][key]['median']) for key in summary['zlib']}
(p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':'#18263b','xtick.color':'#526079'})
fig,axes=plt.subplots(2,2,figsize=(12,8),dpi=180);fig.patch.set_facecolor('#f8fafc');fig.subplots_adjust(left=.09,right=.95,top=.77,bottom=.18,hspace=.9,wspace=.34)
fig.text(.06,.93,'SWC on btrfs: zlib → zstd',fontsize=25,weight='bold')
fig.text(.06,.875,'Real filesystem rewrite and native-addon loads · Linux ARM64 VM',fontsize=13,color='#526079')
for ax,(key,title,unit,scale) in zip(axes.flat,[('compress_ms','Compression + flush','ms',1),('disk_bytes','Compressed disk bytes','MB',1e6),('read_ms','Page-cache-cold file read','ms',1),('require_ms','Page-cache-cold native require()','ms',1)]):
 ax.set_facecolor('#f8fafc')
 for y,codec,color in [(1,'zlib','#9aaac1'),(0,'zstd','#087f8c')]:
  s=summary[codec][key];v=s['median']/scale
  ax.barh(y,v,height=.5,color=color,zorder=3,xerr=[[max(0,v-s['min']/scale)],[max(0,s['max']/scale-v)]],error_kw={'ecolor':'#27364c','capsize':3})
  ax.text(s['max']/scale+.025*max(summary[c][key]['max']/scale for c in ['zlib','zstd']),y,f'{v:.2f} {unit}',va='center',fontsize=10,weight='bold')
 delta=summary['reduction_percent'][key];verb='less' if key=='disk_bytes' else 'lower time'
 ax.set_title(f'{title}\n{delta:.1f}% {verb}' if delta>=0 else f'{title}\n{-delta:.1f}% increase',loc='left',pad=14,fontsize=12,weight='bold')
 ax.set_yticks([1,0],['zlib','zstd']);ax.set_ylim(-.65,1.65);ax.set_xlim(0,max(summary[c][key]['max']/scale for c in ['zlib','zstd'])*1.35)
 ax.tick_params(axis='y',length=0);ax.grid(axis='x',color='#e0e6ee',zorder=0)
 for spine in ax.spines.values():spine.set_visible(False)
fig.text(.06,.105,'SWC 1.16.2 · 8 measured rounds/codec after 2 warmups · alternating order · medians; whiskers = round min–max',fontsize=9,color='#526079')
fig.text(.06,.067,'7 reads and 7 loads per round. File page cache evicted; VM/host caches uncontrolled. Not end-to-end SWC startup.',fontsize=9,color='#526079')
fig.savefig(p/'btrfs-performance.png',facecolor=fig.get_facecolor())
print(json.dumps(summary['reduction_percent'],indent=2))
