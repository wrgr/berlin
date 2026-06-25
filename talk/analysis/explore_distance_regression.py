"""Does a SCALE TRANSFORM or a flexible MODEL recover an annotator-level signal when regressing the
continuous distance-from-GT (multiSomaSplit)?  Answer: no. Across log / rank (scale-invariant)
feature & target transforms x Ridge/RF/GBM/kNN, CV Spearman stays ~0 (best 0.26, permutation
p=0.25 -> noise). The annotator-level negative is robust to transform, model, and target.
multiSomaSplit competency is per-annotator AGGREGATED (one row/annotator), so there is no per-task
telemetry to model -> the remaining levers are DATA (dense per-decision telemetry on the weak
annotators; 3-D structural difficulty features), not modeling. Offline; override with BERLIN_DATA."""
import os
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import KFold, cross_val_predict
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent; OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
feats=["mean_dur","std_dur","cv_dur","mean_pts","std_pts","dur_per_pt","n_tasks"]
ms=pd.read_csv(OUT/'multisomasplit_competency.csv'); A=pd.read_csv(OUT/'separability_annotator.csv'); tiers=pd.read_csv(OUT/'tiers_data.csv')
md=ms[ms.dist_nm<=2000].groupby('assignee').agg(dist=('dist_nm','median')).reset_index()
D=A.merge(md,on='assignee',how='inner')
def cvs(X,y,m): return stats.spearmanr(cross_val_predict(m,X,y,cv=KFold(5,shuffle=True,random_state=0)),y)[0]
Xz=StandardScaler().fit_transform(D[feats].fillna(D[feats].median()))
Xlz=StandardScaler().fit_transform(np.column_stack([np.log1p(D[f].fillna(D[f].median())) for f in feats]))   # log (scale)
Xrank=np.column_stack([stats.rankdata(D[f].fillna(D[f].median())) for f in feats])                            # rank (scale-invariant)
models={"Ridge":RidgeCV(),"RF":RandomForestRegressor(400,random_state=0),"GBM":GradientBoostingRegressor(random_state=0),"kNN":KNeighborsRegressor(5)}
print("PER-ANNOTATOR distance-from-GT regression (n=%d, dist std=%.0f nm) — CV Spearman(pred,true):"%(len(D),D.dist.std()))
for yn,y in {"dist":D.dist.values,"log(dist)":np.log(D.dist.values)}.items():
    for xn,X in [("raw-z",Xz),("log-z",Xlz),("rank(scale-invar)",Xrank)]:
        print("  target=%-9s feat=%-17s : "%(yn,xn)+"  ".join("%s=%+.2f"%(mn,cvs(X,y,m)) for mn,m in models.items()))
y=np.log(D.dist.values); m=KNeighborsRegressor(5); ob=cvs(Xz,y,m)
rng=np.random.RandomState(0); p=np.mean([abs(cvs(Xz,rng.permutation(y),m))>=abs(ob) for _ in range(400)])
print("best-of-sweep (kNN/log-dist) Spearman=%.2f  permutation p=%.3f => %s"%(ob,p,"NOISE" if p>0.05 else "signal"))
R=tiers.merge(md,on='assignee',how='inner'); rich=[c for c in tiers.columns if c not in ('assignee','cohort','promoted') and tiers[c].dtype!=object]
Xr=StandardScaler().fit_transform(R[rich].fillna(R[rich].median()))
print("RICH features (n=%d, calibrated) -> log-distance: Ridge=%.2f RF=%.2f"%(len(R),cvs(Xr,np.log(R.dist.values),RidgeCV()),cvs(Xr,np.log(R.dist.values),RandomForestRegressor(300,random_state=0))))
print("NOTE: multiSomaSplit competency is per-annotator aggregated (no per-task telemetry); remaining levers are DATA, not modeling.")
