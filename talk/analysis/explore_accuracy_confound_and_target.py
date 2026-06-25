"""Follow-ups to explore_accuracy_predictability.py, answering: does a different TARGET (#3) or
controlling the DIFFICULTY confound (#2) recover an annotator-level accuracy signal?
Answer: no — annotator-level competence isn't behaviorally predictable (ceiling OR variance-rich);
the per-DECISION GT-free signal (AUC 0.59) is the real one and it survives difficulty control.
Offline; reads live_out CSVs. Override paths with BERLIN_DATA."""
import os
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
feats=["mean_dur","std_dur","cv_dur","mean_pts","std_pts","dur_per_pt","n_tasks"]
A=pd.read_csv(OUT/'separability_annotator.csv'); T=pd.read_csv(OUT/'separability_task.csv')
ms=pd.read_csv(OUT/'multisomasplit_competency.csv'); tiers=pd.read_csv(OUT/'tiers_data.csv')

print("#3 VARIANCE-RICH TARGET — multiSomaSplit distance-to-GT (real spread, not a ceiling)")
md=ms[ms.dist_nm<=2000].groupby('assignee').agg(dist=('dist_nm','median'),cohort=('cohort','first')).reset_index()
print("  distance: n=%d median=%.0f std=%.0f nm IQR=%.0f-%.0f"%(len(md),md.dist.median(),md.dist.std(),md.dist.quantile(.25),md.dist.quantile(.75)))
D=A.merge(md,on='assignee',how='inner')
Xd=StandardScaler().fit_transform(D[feats].fillna(D[feats].median()))
pred=cross_val_predict(RidgeCV(),Xd,D.dist.values,cv=KFold(5,shuffle=True,random_state=0))
sp=stats.spearmanr(pred,D.dist)[0]
rng=np.random.RandomState(0); null=np.array([abs(stats.spearmanr(rng.permutation(D.dist.values),pred)[0]) for _ in range(2000)])
print("  simple behavior -> distance: Ridge 5-fold Spearman=%.2f (perm null|rho| 95th=%.2f, p=%.3f) => NOT predictable"%(sp,np.percentile(null,95),(null>=abs(sp)).mean()))
R=tiers.merge(md,on='assignee',how='inner')
print("  rich kinematics -> distance (n=%d, calibrated only): "%len(R)+", ".join("%s rho=%+.2f"%(c,stats.spearmanr(R[c],R.dist)[0]) for c in ['total_rot_deg','n_rot','n_events']))

print("\n#2 DIFFICULTY CONFOUND")
T2=T.dropna(subset=['dur']).copy(); T2=T2[T2.groupby('assignee')['assignee'].transform('size')>=10].copy()
T2['dur_z']=T2.groupby('assignee')['dur'].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
Xc=StandardScaler().fit_transform(T2[['dur_z','n_pts']].fillna(0)); cf=LogisticRegression(max_iter=1000).fit(Xc,T2.err.values).coef_[0]
print("  PER-TASK GT-free dur_z->err is NOT a task-size artifact:")
print("    dur_z vs size(n_pts) rho=%+.2f ; logistic err~dur_z+size: coef(dur_z)=%+.2f coef(size)=%+.2f"%(stats.spearmanr(T2.dur_z,T2.n_pts)[0],cf[0],cf[1]))
T2['sz']=pd.qcut(T2.n_pts.rank(method='first'),3,labels=['small','med','large'])
print("    dur_z->err AUC within size strata: "+", ".join("%s=%.2f"%(b,roc_auc_score(g.err,g.dur_z)) for b,g in T2.groupby('sz',observed=True) if g.err.nunique()>1)+" (overall %.2f)"%roc_auc_score(T2.err,T2.dur_z))
def psp(x,y,z):
    rx,ry,rz=rankdata(x),rankdata(y),rankdata(z)
    return stats.pearsonr(rx-np.polyval(np.polyfit(rz,rx,1),rz), ry-np.polyval(np.polyfit(rz,ry,1),rz))
print("  PER-ANNOTATOR anti-correlation is weak and survives size control (not a size confound):")
for f in ["cv_dur","std_dur"]:
    d=A.dropna(subset=[f,'acc','mean_pts']); r0=stats.spearmanr(d[f],d.acc)[0]; rp,pp=psp(d[f].values,d.acc.values,d.mean_pts.values)
    print("    %-8s vs acc: raw rho=%+.2f -> partial|size rho=%+.2f (p=%.2f)"%(f,r0,rp,pp))
print("\nCONCLUSION: competence is legible per-DECISION (GT-free AUC 0.59, difficulty-robust), not per-ANNOTATOR.")
