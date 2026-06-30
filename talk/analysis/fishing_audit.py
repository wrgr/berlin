"""FISHING AUDIT for the expertise classifier (expert vs proto-expert, n=16).
The 28 'designed' features and 10 'learned' motifs were engineered on this same small
sample (post-hoc, not preregistered). This script quantifies how much of the high AUC is
real vs an artifact of (a) combining many made-up features at p>>n, (b) in-sample fitting.

Three checks:
  1) HISTOGRAM OF ITEMS: each single feature's own expert-vs-proto AUC -> most are modest;
     the multivariate AUC comes from COMBINING them.
  2) TRIVIAL-FIT LADDER: in-sample (no CV) is ~1.0 trivially; honest LOO is lower; and 28
     RANDOM features (pure noise) separate in-sample but collapse under LOO -> CV catches the
     trivial fit, so the real LOO signal is NOT just dimensionality. The label-permutation null
     is the matching control (random labels, same features -> ~0.5).
  3) ANCHOR: the rawest un-fished fact (experts rotate ~2x more) needs no classifier.

Offline; reads live_out CSVs. Override with BERLIN_DATA / writes fig to BERLIN_TALK."""
import os
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
TALK=Path(os.environ.get("BERLIN_TALK", HERE.parent))
EXP="#E45756"; STU="#4C78A8"
T=pd.read_csv(OUT/"tiers_data.csv"); y=(T.cohort=="expert").astype(int).values
idc=["assignee","cohort","promoted"]
motif=[c for c in T.columns if c.startswith("motif_")]
designed=[c for c in T.columns if c not in idc+motif]
naive=["n_events","evt_per_session","pct_N","dt_med"]

def loo(X,yy):
    pr=cross_val_predict(LogisticRegression(max_iter=1000,class_weight="balanced"),X,yy,
                         cv=LeaveOneOut(),method="predict_proba")[:,1]
    return roc_auc_score(yy,pr)
def insample(X,yy):
    m=LogisticRegression(max_iter=1000,class_weight="balanced").fit(X,yy)
    return roc_auc_score(yy,m.predict_proba(X)[:,1])

# ---- 1) single-feature AUCs (the "items") ----
allfeat=designed+motif
single=[]
for c in allfeat:
    v=T[c].fillna(T[c].median()).values
    if np.std(v)==0: continue
    a=roc_auc_score(y,v); single.append((c,max(a,1-a)))
single_auc=np.array([a for _,a in single])

# ---- 2) trivial-fit ladder ----
Xd=StandardScaler().fit_transform(T[designed].fillna(T[designed].median()))
Xn=StandardScaler().fit_transform(T[naive].fillna(T[naive].median()))
Xm=StandardScaler().fit_transform(T[motif].fillna(T[motif].median()))
d_in, d_loo = insample(Xd,y), loo(Xd,y)
n_loo, m_loo = loo(Xn,y), loo(Xm,y)
rng=np.random.RandomState(0)
rand_in=[]; rand_loo=[]
for _ in range(50):
    Xr=rng.randn(len(y),len(designed))         # 28 PURE-NOISE features, same shape as 'designed'
    rand_in.append(insample(Xr,y)); rand_loo.append(loo(Xr,y))
perm=[]
for _ in range(300):
    yp=rng.permutation(y)
    if yp.sum()>=2: perm.append(loo(Xd,yp))     # real features, RANDOM labels
rand_in=np.array(rand_in); rand_loo=np.array(rand_loo); perm=np.array(perm)

print("=== FISHING AUDIT (expert vs proto, n=%d) ==="%len(T))
print("single-feature AUCs (%d items): median=%.2f  90th=%.2f  max=%.2f"%(
    len(single_auc),np.median(single_auc),np.percentile(single_auc,90),single_auc.max()))
print("TRIVIAL-FIT LADDER:")
print("  designed IN-SAMPLE (no CV):      %.2f   <- trivially ~1.0 (28 feats / 16 pts)"%d_in)
print("  designed LOO (features fixed):   %.2f"%d_loo)
print("  learned/motif LOO (leaky kmeans):%.2f"%m_loo)
print("  naive LOO (4 un-fished counts):  %.2f   <- conservative anchor"%n_loo)
print("  28 RANDOM feats IN-SAMPLE:       %.2f±%.2f  <- noise also fits in-sample"%(rand_in.mean(),rand_in.std()))
print("  28 RANDOM feats LOO:             %.2f±%.2f  <- but COLLAPSES under CV"%(rand_loo.mean(),rand_loo.std()))
print("  label-permutation null (LOO):    %.2f±%.2f  <- matching control"%(perm.mean(),perm.std()))
print("ANCHOR (no classifier): total_rot_deg expert=%.0f vs proto=%.0f (ratio %.2f)"%(
    T[T.cohort=='expert'].total_rot_deg.mean(),T[T.cohort=='student'].total_rot_deg.mean(),
    T[T.cohort=='expert'].total_rot_deg.mean()/T[T.cohort=='student'].total_rot_deg.mean()))

# ---- figure ----
fig,ax=plt.subplots(1,3,figsize=(14,4))
ax[0].hist(single_auc,bins=np.arange(0.5,1.02,0.05),color="#bdbdbd",edgecolor="k",lw=.3)
ax[0].axvline(d_loo,c=EXP,lw=2.2,label="all 28 combined (LOO %.2f)"%d_loo)
ax[0].axvline(np.median(single_auc),c="k",ls=":",lw=1,label="median single feat %.2f"%np.median(single_auc))
ax[0].set_title("Most single 'items' are modest;\nthe AUC comes from combining %d made-up features"%len(single_auc),fontsize=9.5)
ax[0].set_xlabel("single-feature expert-vs-proto AUC"); ax[0].set_ylabel("# features"); ax[0].legend(fontsize=7.5)

labels=["in-sample\n(no CV)","designed\nLOO","motif\nLOO","naive\nLOO","28 RANDOM\nfeats LOO","perm null\n(rand labels)"]
vals=[d_in,d_loo,m_loo,n_loo,rand_loo.mean(),perm.mean()]
errs=[0,0,0,0,rand_loo.std(),perm.std()]
cols=["#999999",EXP,EXP,"#59A14F","#B07AA1","#666666"]
ax[1].bar(range(6),vals,yerr=errs,color=cols,edgecolor="k",lw=.4,capsize=3)
ax[1].axhline(0.5,ls=":",c="k",lw=1)
ax[1].set_xticks(range(6)); ax[1].set_xticklabels(labels,fontsize=7.5)
ax[1].set_ylim(0,1.05); ax[1].set_ylabel("ROC-AUC")
ax[1].set_title("Trivial fit is caught by CV: random features fit\nin-sample but collapse to chance under LOO",fontsize=9.5)

for coh,c,lb in [("expert",EXP,"expert"),("student",STU,"proto-expert")]:
    s=T[T.cohort==coh].total_rot_deg
    ax[2].scatter(np.random.RandomState(1).normal(0 if coh=="expert" else 1,0.05,len(s)),s,c=c,s=40,edgecolor="k",lw=.3,label=lb)
ax[2].set_xticks([0,1]); ax[2].set_xticklabels(["expert","proto-expert"],fontsize=8)
ax[2].set_title("The un-fished anchor: experts explore ~2x more\n(total camera rotation; no classifier)",fontsize=9.5)
ax[2].set_ylabel("total camera rotation (deg)"); ax[2].legend(fontsize=7.5)
plt.figtext(0.995,0.004,"Preliminary analysis — MICrONS proofreading annotators (n=16 pilot, post-hoc features)",
            ha="right",va="bottom",fontsize=6,style="italic",color="0.5")
plt.tight_layout(); plt.savefig(TALK/"fig_fishing_audit.png",dpi=150)
print("saved fig_fishing_audit.png")
