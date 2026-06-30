"""Exploration: WHY simple behavior doesn't predict per-annotator fullyProofread accuracy
(the 'AUC 0.14' honest-negative), and whether a different classifier/weights/target recovers it.

Findings (see ../deck_coherence_review.md / transparency_failure_modes.md):
- The 0.14 LOO AUC is NOT robustly below chance: the permutation null for this estimator
  (LOO + balanced logistic + 5-of-36 positive class) is ~0.45 +/- 0.20; observed 0.135 sits at
  one-sided p ~ 0.07. Honest statement: 'no reliable annotator-level accuracy signal.'
- Classifier/weight sweep (LR weighted/unweighted, C-sweep, RF) spans 0.00-0.34 — instability
  inside the null, not a tunable signal. The target, not the model, is the problem.
- The point estimate dips below 0.5 only as noise: the total_rot_deg rho ~ -0.44 behind it is n.s.
  (p=0.10, 95% CI [-0.83,+0.20]) and is the largest of 29 chance-level coefficients (0/29 p<0.05,
  sign 17-/12+) — a max-of-a-null-field on a ceiling target, NOT a difficulty confound (it survives
  partialling task size/axon-fraction, which are equal across cohorts). See rho_robustness.py.
- Constructive paths: per-task unit (AUC 0.59), task-difficulty controls, a variance-rich target.

Offline; reads the CSVs in live_out/. Run with BERLIN_DATA / BERLIN_TALK to override paths."""
import os
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LogisticRegression, RidgeCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_predict, KFold
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
TALK=Path(os.environ.get("BERLIN_TALK", HERE.parent))
EXP="#E45756"; STU="#4C78A8"
feats=["mean_dur","std_dur","cv_dur","mean_pts","std_pts","dur_per_pt","n_tasks"]

A=pd.read_csv(OUT/"separability_annotator.csv").dropna(subset=["acc"]).copy()
X=StandardScaler().fit_transform(A[feats].fillna(A[feats].median())); y=A.bad.values.astype(int)
print("n=%d  bad(acc<0.90)=%d  acc std=%.3f (bimodal: ceiling + tail)"%(len(A),y.sum(),A.acc.std()))

def loo(X,y,fac=lambda:LogisticRegression(max_iter=1000,class_weight="balanced")):
    pr=np.zeros(len(y))
    for tr,te in LeaveOneOut().split(X):
        pr[te]=fac().fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
    return roc_auc_score(y,pr)
obs=loo(X,y)
rng=np.random.RandomState(1); null=[]            # permutation null for THIS estimator (not 0.5)
while len(null)<1000:
    yp=rng.permutation(y)
    if yp.sum()>=2: null.append(loo(X,yp))
null=np.array(null)
print("OBSERVED LOO AUC=%.3f | permutation null=%.2f+/-%.2f (95%% %.2f-%.2f) one-sided p=%.3f"%(
    obs,null.mean(),null.std(),*np.percentile(null,[2.5,97.5]),(null<=obs).mean()))
print("classifier/weight sweep (same target):")
for nm,fac in [("LR balanced",lambda:LogisticRegression(max_iter=1000,class_weight="balanced")),
               ("LR no-weight",lambda:LogisticRegression(max_iter=1000)),
               ("LR C=0.1",lambda:LogisticRegression(max_iter=1000,C=0.1,class_weight="balanced")),
               ("LR C=10",lambda:LogisticRegression(max_iter=1000,C=10,class_weight="balanced")),
               ("RF",lambda:RandomForestClassifier(400,random_state=0,class_weight="balanced"))]:
    print("   %-12s %.2f"%(nm,loo(X,y,fac)))
print("continuous-acc Ridge 5-fold Spearman=%.2f"%stats.spearmanr(
    cross_val_predict(RidgeCV(),X,A.acc.values,cv=KFold(5,shuffle=True,random_state=0)),A.acc.values)[0])

# expertise axis vs accuracy (calibrated cohort with dense telemetry)
T=pd.read_csv(OUT/"tiers_data.csv"); fp=pd.read_csv(OUT/"fullyproofread_accuracy.csv")[["assignee","acc_relax"]]
M=T.merge(fp,on="assignee",how="inner"); rho,pp=stats.spearmanr(M.total_rot_deg,M.acc_relax)
print("expertise axis vs accuracy (n=%d): total_rot_deg rho=%.2f p=%.2f (n.s.; selection-confounded between-cohort comparison — see rho_robustness.py)"%(len(M),rho,pp))

# ---- 3-panel diagnostic figure ----
fig,ax=plt.subplots(1,3,figsize=(13.8,4))
ax[0].hist(A.acc,bins=np.arange(0.2,1.02,0.05),color="#7a7a7a",edgecolor="k",lw=.4)
ax[0].axvline(0.90,ls="--",c="#de2d26",label="'bad' cutoff 0.90")
ax[0].set_title("Accuracy is ceiling-clustered\nceiling cluster + a %d-point tail (n=%d)"%(int(y.sum()),len(A)),fontsize=10)
ax[0].set_xlabel("fullyProofread accuracy"); ax[0].set_ylabel("# annotators"); ax[0].legend(fontsize=8)
ax[1].hist(null,bins=24,color="#bdbdbd",edgecolor="k",lw=.3,density=True)
ax[1].axvline(null.mean(),c="k",lw=1,label="null mean %.2f"%null.mean())
ax[1].axvline(obs,c="#de2d26",lw=2.2,label="observed %.2f"%obs); ax[1].axvline(0.5,ls=":",c="#888",label="0.5")
ax[1].set_title("'Worse than chance' is within the noise\nLOO null %.2f±%.2f; one-sided p=%.2f"%(null.mean(),null.std(),(null<=obs).mean()),fontsize=10)
ax[1].set_xlabel("leave-one-out AUC (annotator accuracy)"); ax[1].set_ylabel("density"); ax[1].legend(fontsize=8)
# the -0.44 is a BETWEEN-COHORT SELECTION effect: proto-experts were promoted FOR grader-agreement,
# and fullyProofread accuracy IS grader-agreement -> the comparison group is selected on the outcome.
for coh,c,lb in [("expert",EXP,"expert"),("student",STU,"proto-expert")]:
    s=M[M.cohort==coh]
    ax[2].scatter(s.total_rot_deg,s.acc_relax,c=c,s=46,edgecolor="k",lw=.3,label="%s (mean acc %.2f)"%(lb,s.acc_relax.mean()))
xs=np.linspace(M.total_rot_deg.min(),M.total_rot_deg.max(),50)
ax[2].plot(xs,np.polyval(np.polyfit(M.total_rot_deg,M.acc_relax,1),xs),ls="--",c="0.6",lw=1,label="pooled ρ=%.2f (confounded, n.s.)"%rho)
ax[2].set_title("Expertise↔accuracy is a selection artifact, not 'skill hurts'\nproto-experts promoted FOR grader-agreement = the accuracy metric",fontsize=9.5)
ax[2].set_xlabel("total camera rotation (expertise signal) →"); ax[2].set_ylabel("fullyProofread accuracy"); ax[2].legend(fontsize=7.5)
plt.figtext(0.995,0.004,"Preliminary analysis — MICrONS proofreading annotators",ha="right",va="bottom",fontsize=6,style="italic",color="0.5")
plt.tight_layout(); plt.savefig(TALK/"fig_accuracy_unpredictable.png",dpi=150)
print("saved fig_accuracy_unpredictable.png")
