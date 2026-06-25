"""Stage B (attempted): pull CAVE morphological difficulty (L2 size, synapse counts) for the 28
fullyProofread benchmark cells, to test whether STRUCTURAL difficulty predicts cell error-rate and
adds beyond the point-category mix.

RESULT: inconclusive — a DATA-QUALITY limitation, not a clean negative. 17/28 cells carry stale
2021-22 root IDs; `get_latest_roots` fragments split cells, so L2/synapse counts are corrupted
(l2 vs cell-error rho≈-0.03; synapse queries mostly fail). A proper test needs either a historical
materialization version near the task time, or supervoxel->current-root mapping from the annotators'
own point coordinates. The category-mix risk signal (explore_task_risk_prediction.py, AUC≈0.76,
p<0.001) stands on its own and is itself a GT-free structural descriptor.

Network stage: needs .cave_token alongside this script + enriched_task.csv in live_out/."""
import os
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
ct=(HERE/'.cave_token').read_text().strip()
from caveclient import CAVEclient
cl=CAVEclient('minnie65_phase3_v1',auth_token=ct)
T=pd.read_csv(OUT/'enriched_task.csv')
segs=sorted(set(int(s) for s in T.seg_id.astype(str) if s.strip().isdigit() and int(s)>0))
print("unique cells:",len(segs),flush=True)
rows=[]
for rid in segs:
    use=rid; latest=True
    try:
        if not cl.chunkedgraph.is_latest_roots([rid])[0]:
            latest=False; lr=cl.chunkedgraph.get_latest_roots(rid); use=int(np.atleast_1d(lr)[0]) if len(np.atleast_1d(lr)) else rid
    except Exception: pass
    d={"seg_id":str(rid),"latest":int(latest)}
    try: d["l2"]=len(cl.chunkedgraph.get_leaves(use,stop_layer=2))
    except Exception: d["l2"]=np.nan
    for side in ["pre","post"]:
        try: d["n_"+side]=len(cl.materialize.query_table("synapses_pni_2",filter_equal_dict={side+"_pt_root_id":use},select_columns=["id"],limit=8000))
        except Exception: d["n_"+side]=np.nan
    rows.append(d)
D=pd.DataFrame(rows); D.to_csv(OUT/'seg_difficulty.csv',index=False)
print("latest-root (usable) cells: %d/%d  <- staleness limits this analysis"%(D.latest.sum(),len(D)),flush=True)
cell=T.groupby('seg_id').agg(err=('err','mean'),npts=('n_pts','mean')).reset_index(); cell['seg_id']=cell.seg_id.astype(str)
M=cell.merge(D,on='seg_id')
for c in ['l2','n_pre','n_post','npts']:
    if c in M and M[c].notna().sum()>=8:
        rho,p=stats.spearmanr(M[c],M.err,nan_policy='omit'); print("  %-6s vs cell-err: rho=%+.2f p=%.2f"%(c,rho,p),flush=True)
print("(inconclusive due to stale roots; see docstring)",flush=True)
