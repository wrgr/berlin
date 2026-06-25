"""#1 caliber/branches: morphological difficulty for the 28 fullyProofread cells, robust to stale
roots (latest-root -> largest fragment). Caliber via L2-cache distance-transform (thin = the
thin-axon science); branches via the level-2 chunk graph. Tested vs per-cell error rate.

RESULT: in this 28-cell benchmark, caliber/branches/size do NOT predict per-cell error (all p>0.09;
thin-fraction +0.16, right direction but n.s.). The GT-free risk signal is annotation-category
difficulty, not cell morphology here; 17/28 cells had stale roots. A clean test needs more cells and a
morphology-sensitive task. Needs .cave_token + enriched_task.csv (live_out)."""
import os
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
ct=(HERE/'.cave_token').read_text().strip()
from caveclient import CAVEclient
cl=CAVEclient('minnie65_phase3_v1',auth_token=ct)
T=pd.read_csv(OUT/'enriched_task.csv')
segs=sorted(set(int(s) for s in T.seg_id.astype(str) if s.strip().isdigit() and int(s)>0))
def current_root(rid):
    try:
        if cl.chunkedgraph.is_latest_roots([rid])[0]: return rid
        lr=np.atleast_1d(cl.chunkedgraph.get_latest_roots(rid))
        if len(lr)==0: return rid
        if len(lr)==1: return int(lr[0])
        best,bn=rid,-1
        for r in lr[:6]:
            try: n=len(cl.chunkedgraph.get_leaves(int(r),stop_layer=2))
            except Exception: n=0
            if n>bn: bn,best=n,int(r)
        return best
    except Exception: return rid
rows=[]
for rid in segs:
    root=current_root(rid); d={"seg_id":str(rid),"root":str(root)}
    try: l2=[int(x) for x in cl.chunkedgraph.get_leaves(root,stop_layer=2)]; d["n_l2"]=len(l2)
    except Exception: l2=[]; d["n_l2"]=np.nan
    try:
        l2d=cl.l2cache.get_l2data(l2,attributes=['size_nm3','area_nm2','max_dt_nm','mean_dt_nm'])
        cal=np.array([v.get('mean_dt_nm') for v in l2d.values() if v.get('mean_dt_nm')],float)
        sz=np.array([v.get('size_nm3') for v in l2d.values() if v.get('size_nm3')],float)
        if len(cal): d.update(cal_mean=np.mean(cal),cal_med=np.median(cal),cal_p10=np.percentile(cal,10),frac_thin=float(np.mean(cal<150)))
        if len(sz): d["tot_size"]=float(np.sum(sz))
    except Exception as e: d["l2err"]=str(e)[:30]
    try:
        edges=cl.chunkedgraph.level2_chunk_graph(root); deg=Counter()
        for a,b in edges: deg[a]+=1; deg[b]+=1
        d.update(n_branch=sum(1 for v in deg.values() if v>=3),n_nodes=len(deg),n_edges=len(edges),
                 branch_frac=(sum(1 for v in deg.values() if v>=3)/max(1,len(deg))))
    except Exception: pass
    rows.append(d)
D=pd.DataFrame(rows); D.to_csv(OUT/'seg_morphology.csv',index=False)
cell=T.groupby('seg_id').agg(err=('err','mean')).reset_index(); cell['seg_id']=cell.seg_id.astype(str)
M=cell.merge(D,on='seg_id')
print("PER-CELL morphology vs error-rate (n=%d cells):"%len(M))
for c in ['n_l2','tot_size','cal_mean','cal_med','cal_p10','frac_thin','n_branch','branch_frac','n_nodes']:
    if c in M and M[c].notna().sum()>=10:
        rho,p=stats.spearmanr(M[c],M.err,nan_policy='omit'); print("  %-11s rho=%+.2f p=%.2f"%(c,rho,p))
