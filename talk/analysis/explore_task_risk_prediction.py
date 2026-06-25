"""Is per-task QUALITY predictable from a RICHER GT-free representation? (Tests the 'the problem
wasn't set up rich enough' hypothesis.) Reads enriched_task.csv (enrich_fullyproofread.py: per
fullyProofread task = GT-free behavior + point-category mix + error vs grader GT).

Findings, under HONEST grouped-by-cell CV (no cell-identity memorization):
- GT-free TASK RISK (error-proneness) is predictable at AUC ~0.76 on held-out cells from the
  point-category mix alone (grouped permutation null 0.47±0.02, p<0.001). It GENERALIZES.
- The headline 0.92 was cell-identity LEAKAGE: only 28 unique cells, random CV lets the model
  memorize each cell's base error rate. Honest grouped AUC = 0.79 (catmix+throughput).
- Per-ANNOTATOR competence within a fixed cell stays weak (~0.55): behavior doesn't say who, among
  annotators doing the SAME cell, will err.
=> Task difficulty/RISK is GT-free predictable (feeds the deck's impact x risk allocation);
   per-person competence is not. Offline; override paths with BERLIN_DATA."""
import os
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent; OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
T=pd.read_csv(OUT/'enriched_task.csv')
T2=T.dropna(subset=['dur']).copy(); T2=T2[T2.groupby('assignee')['assignee'].transform('size')>=10].copy()
for col in ['dur','n_pts']: T2[col+'_z']=T2.groupby('assignee')[col].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
T2['dpp']=T2.dur/T2.n_pts; T2['dpp_z']=T2.groupby('assignee')['dpp'].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
catf=['f_spine','f_nucleus','f_dendrite','f_axon','f_soma']
y=T2.err.values; groups=T2.seg_id.values
print("n=%d  unique cells=%d  annotators=%d  err base=%.2f  per-cell err std=%.2f"%(
    len(T2),T2.seg_id.nunique(),T2.assignee.nunique(),y.mean(),T2.groupby('seg_id')['err'].mean().std()))
sets={"dur_z only":["dur_z"],"+throughput":["dur_z","dpp_z","n_pts_z"],"+catmix":["dur_z","dpp_z","n_pts_z"]+catf,"catmix only":catf}
def gb(fs,cv,grouped):
    X=StandardScaler().fit_transform(T2[fs].fillna(0))
    return roc_auc_score(y,cross_val_predict(GradientBoostingClassifier(random_state=0),X,y,cv=cv,groups=groups if grouped else None,method='predict_proba')[:,1])
print("RANDOM 5-fold (leaks cell identity): "+"  ".join("%s=%.2f"%(n,gb(f,StratifiedKFold(5,shuffle=True,random_state=0),False)) for n,f in sets.items()))
print("GROUPED by cell (HONEST):            "+"  ".join("%s=%.2f"%(n,gb(f,GroupKFold(5),True)) for n,f in sets.items()))
X=StandardScaler().fit_transform(T2[catf].fillna(0))
def gauc(yy): return roc_auc_score(yy,cross_val_predict(GradientBoostingClassifier(random_state=0),X,yy,cv=GroupKFold(5),groups=groups,method='predict_proba')[:,1])
obs=gauc(y); rng=np.random.RandomState(0); null=np.array([gauc(rng.permutation(y)) for _ in range(100)])
print("catmix grouped: obs=%.3f  perm-null=%.2f±%.2f  p=%.3f"%(obs,null.mean(),null.std(),(null>=obs).mean()))
rows=[(roc_auc_score(g.err,g.dur_z),len(g)) for _,g in T2.groupby('seg_id') if g.err.nunique()>1 and len(g)>=10]
print("WITHIN-CELL behavior->error (competence, difficulty fixed): dur_z weighted AUC=%.2f over %d cells"%(
    np.average([r[0] for r in rows],weights=[r[1] for r in rows]),len(rows)))
