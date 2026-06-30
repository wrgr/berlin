"""Random-forest regression: behavioral features -> v18xx competency. Feature importance."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import cross_val_score, KFold
    from sklearn.inspection import permutation_importance
except Exception as e:
    print("sklearn missing:",e); sys.exit(1)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F=pd.read_csv(OUT/"feature_competency.csv").dropna(subset=["competency"])
FEATS=["pct_navigate","pct_segment","pct_annotate","nav_seg_ratio","seg_to_nav","seg_to_seg","events_per_session","log_tempo","total_events"]
F[FEATS]=F[FEATS].apply(lambda c:c.fillna(c.median()))
print(f"cells: {len(F)} | types: {F['type'].nunique()} | users: {F['user'].nunique()}")
# target 1: within-type standardized competency ("relative skill at your task type")
F["comp_z"]=F.groupby("type")["competency"].transform(lambda s:(s-s.mean())/(s.std(ddof=0)+1e-9))
def run(y, name, X):
    rf=RandomForestRegressor(n_estimators=600,min_samples_leaf=2,max_features=0.6,random_state=0)
    r2=cross_val_score(rf,X,y,cv=KFold(5,shuffle=True,random_state=0),scoring="r2")
    rf.fit(X,y)
    pi=permutation_importance(rf,X,y,n_repeats=30,random_state=0)
    imp=pd.DataFrame({"feature":X.columns,"gini":rf.feature_importances_,"perm":pi.importances_mean}).sort_values("perm",ascending=False)
    print(f"\n=== {name} ===  CV R2 = {r2.mean():+.2f} (+/-{r2.std():.2f})")
    print(imp.round(3).to_string(index=False))
    return imp
# A) behavioral features only -> relative (within-type) competency
impA=run(F["comp_z"],"behavioral feats -> within-type competency (relative skill)",F[FEATS])
# B) behavioral + task-type one-hot -> raw competency
Xb=pd.concat([F[FEATS],pd.get_dummies(F["type"],prefix="type")],axis=1)
impB=run(F["competency"],"behavioral + task-type -> raw competency",Xb)
# C) richest single type
for ns in F["type"].value_counts().index[:2]:
    sub=F[F["type"]==ns]
    if len(sub)>=12:
        run(sub["competency"],f"within {ns} only (n={len(sub)})",sub[FEATS])
# figure: permutation importance for model A
fig,ax=plt.subplots(figsize=(7,4)); d=impA.sort_values("perm")
ax.barh(d["feature"],d["perm"],color="#4c78a8"); ax.set_xlabel("permutation importance")
ax.set_title("Which behaviors predict relative competency (within task type)\nRF regression, behavioral features only")
fig.tight_layout(); fig.savefig(OUT/"rf_importance.png",dpi=130); plt.close()
impA.to_csv(OUT/"rf_importance.csv",index=False)
print("\nsaved rf_importance.csv + rf_importance.png")
