"""Combined ground-truth-free RISK figure for the deck (replaces the leakage-bar fig_task_risk).
Two parallel GT-free signals, each: x = a signal known WITHOUT ground truth, y = observed error rate.
  LEFT  — behavior: a task slower than the annotator's OWN average is more error-prone (dur_z, AUC ~0.59).
  RIGHT — task structure: predicted risk from the task's point-category mix tracks real error
          (grouped-by-cell CV, AUC ~0.76; the inflated 0.92 was cell-identity leakage — not shown).
No cell-leakage bars. Offline; reads enriched_task.csv. Override paths with BERLIN_DATA / BERLIN_TALK."""
import os
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
TALK=Path(os.environ.get("BERLIN_TALK", HERE.parent))
BEH="#4C78A8"; STR="#E45756"

T=pd.read_csv(OUT/"enriched_task.csv").dropna(subset=["dur"]).copy()
T=T[T.groupby("assignee")["assignee"].transform("size")>=10].copy()
T["dur_z"]=T.groupby("assignee")["dur"].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
catf=["f_spine","f_nucleus","f_dendrite","f_axon","f_soma"]
y=T.err.values; base=y.mean(); rng=np.random.RandomState(0)

# LEFT: error rate by within-annotator duration quartile (GT-free behavior)
qb=pd.qcut(T.dur_z.rank(method="first"),4,labels=False)
beh=[T.err[qb==k].mean() for k in range(4)]
auc_beh=roc_auc_score(y,T.dur_z.values)
nb=np.array([roc_auc_score(rng.permutation(y),T.dur_z.values) for _ in range(2000)])
p_beh=(nb>=auc_beh).mean(); p_beh_s="p<0.001" if p_beh<0.001 else "p=%.3f"%p_beh

# RIGHT: observed error by PREDICTED-RISK quartile from the point-category mix (grouped-by-cell CV)
X=StandardScaler().fit_transform(T[catf].fillna(0))
pr=cross_val_predict(GradientBoostingClassifier(random_state=0),X,y,cv=GroupKFold(5),
                     groups=T.seg_id.values,method="predict_proba")[:,1]
auc_str=roc_auc_score(y,pr)
rb=pd.qcut(pd.Series(pr).rank(method="first"),4,labels=False).values
strk=[y[rb==k].mean() for k in range(4)]

fig,ax=plt.subplots(1,2,figsize=(11.4,4.3))
def panel(a,vals,color,xt,title,foot):
    a.bar(range(4),vals,color=color,edgecolor="k",lw=.5,width=.72,zorder=3)
    for i,v in enumerate(vals): a.text(i,v+.006,"%.0f%%"%(100*v),ha="center",va="bottom",fontsize=10,weight="bold")
    a.axhline(base,ls="--",c="k",lw=1,zorder=2,label="base error rate %.0f%%"%(100*base))
    a.set_xticks(range(4)); a.set_xticklabels(xt,fontsize=9.5)
    a.set_ylim(0,max(max(vals),base)*1.25); a.set_ylabel("observed error rate",fontsize=10)
    a.set_title(title,fontsize=11,weight="bold"); a.legend(fontsize=8,loc="upper left")
    a.text(0.5,-0.26,foot,transform=a.transAxes,ha="center",va="top",fontsize=8.2,style="italic",color="0.3")
panel(ax[0],beh,BEH,["fastest","","","slowest"],
      "Behavior: a task slow *for that person*\nis more error-prone   (AUC %.2f, %s)"%(auc_beh,p_beh_s),
      "x = the task's duration vs the annotator's OWN average  ·  no ground truth")
ax[0].text(1.5,-0.155,"task duration relative to that annotator →",transform=ax[0].transData if False else ax[0].transAxes,
           ha="center",va="top",fontsize=9)
panel(ax[1],strk,STR,["lowest","","","highest"],
      "Task structure: risk from its point-category\nmix tracks real error   (AUC %.2f, p<0.001)"%auc_str,
      "x = risk predicted from %% spine/dendrite/axon/... points  ·  held-out cells, no ground truth")
ax[1].text(0.5,-0.155,"predicted risk from task properties →",transform=ax[1].transAxes,ha="center",va="top",fontsize=9)
fig.suptitle("Two ground-truth-free ways to flag a risky decision — before any expert looks",
             fontsize=12.5,weight="bold",y=1.02)
plt.figtext(0.995,0.005,"Preliminary — MICrONS (764 decisions, 28 cells). Permutation tests: behavior 2000-perm pooled null 0.50±0.02; structure 1000-perm grouped-by-cell null 0.47±0.02; both p<0.001.",
            ha="right",va="bottom",fontsize=5.6,style="italic",color="0.5")
plt.tight_layout(rect=[0,0.04,1,0.99]); plt.savefig(TALK/"fig_task_risk.png",dpi=200,bbox_inches="tight")
print("beh err by dur-quartile:",[round(v,2) for v in beh]," AUC=%.2f"%auc_beh)
print("structural err by predicted-risk quartile:",[round(v,2) for v in strk]," AUC=%.2f"%auc_str)
print("saved fig_task_risk.png")
