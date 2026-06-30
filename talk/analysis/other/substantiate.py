import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import roc_auc_score
from scipy import stats
np.seterr(all='ignore')
T=pd.read_csv('live_out/tiers_data.csv'); y=(T.cohort=='expert').astype(int).values
motif=[c for c in T.columns if c.startswith('motif_')]; idc=['assignee','cohort','promoted']
designed=[c for c in T.columns if c not in idc+motif]
naive=['n_events','evt_per_session','pct_N','dt_med']
raw_totals=['n_events','n_sessions','total_rot_deg','n_rot','runN_max','runS_max']
rate=[c for c in designed if c not in raw_totals]
def loo(feats,yy,rows=None):
    d=T.iloc[rows] if rows is not None else T
    X=StandardScaler().fit_transform(d[feats].fillna(T[feats].median()))
    pr=cross_val_predict(LogisticRegression(max_iter=1000,class_weight='balanced'),X,yy,cv=LeaveOneOut(),method='predict_proba')[:,1]
    return roc_auc_score(yy,pr)
rng=np.random.RandomState(0)
print("=== TIER AUC + 1000-perm null + 400-bootstrap CI (LOO, n=16) ===",flush=True)
for nm,fs in [('naive(4)',naive),('designed(28)',designed),('learned(10)',motif)]:
    obs=loo(fs,y)
    null=np.array([loo(fs,rng.permutation(y)) for _ in range(1000)])
    boots=[]
    for _ in range(400):
        idx=rng.choice(len(y),len(y),replace=True)
        if len(set(y[idx]))<2: continue
        try: boots.append(loo(fs,y[idx],idx))
        except: pass
    lo,hi=np.percentile(boots,[2.5,97.5])
    print("  %-12s AUC=%.2f  95%%CI[%.2f,%.2f]  null=%.2f±%.2f p=%.3f"%(nm,obs,lo,hi,null.mean(),null.std(),(null>=obs).mean()),flush=True)
print("\n=== VOLUME vs STYLE (does separation survive stripping raw totals?) ===",flush=True)
print("  designed ALL (%d):       AUC=%.2f"%(len(designed),loo(designed,y)),flush=True)
print("  raw-TOTALS only (%d):    AUC=%.2f"%(len(raw_totals),loo(raw_totals,y)),flush=True)
print("  rate/INTENSIVE only(%d): AUC=%.2f"%(len(rate),loo(rate,y)),flush=True)
print("\n=== rotation/activity: volume confound ===",flush=True)
for c in ['total_rot_deg','n_rot','mean_rot','n_events','evt_per_session','pct_S','entropy']:
    e=T[T.cohort=='expert'][c].mean(); s=T[T.cohort=='student'][c].mean()
    print("  %-14s exp=%.2f proto=%.2f ratio=%.2f  corr_w_n_events rho=%.2f"%(c,e,s,e/s if s else float('nan'),stats.spearmanr(T[c],T.n_events)[0]),flush=True)
print("DONE",flush=True)
