"""Clean, deck-ready 'expertise evidence' figure for the rebaselined talk (slide 13).
Two panels, honest framing:
  LEFT  — the model-free anchor: experts explore ~2.18x more (camera rotation dotplot).
  RIGHT — the AUC ladder with explicit bands: a robust ~0.80 floor (naive counts / median
          single feature), an engineered 0.95-0.98 ceiling (post-hoc features on n=16), and a
          chance band (noise features / permuted labels ~0.46) that CV correctly lands on.
Aspect ~1.47 to fit the slide image slot without distortion.
Offline; reads live_out CSVs. Override with BERLIN_DATA / writes to BERLIN_TALK."""
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
idc=["assignee","cohort","promoted"]; motif=[c for c in T.columns if c.startswith("motif_")]
designed=[c for c in T.columns if c not in idc+motif]; naive=["n_events","evt_per_session","pct_N","dt_med"]
def loo(X,yy):
    return roc_auc_score(yy,cross_val_predict(LogisticRegression(max_iter=1000,class_weight="balanced"),
                         X,yy,cv=LeaveOneOut(),method="predict_proba")[:,1])
def std(f): return StandardScaler().fit_transform(T[f].fillna(T[f].median()))
d_loo,m_loo,n_loo=loo(std(designed),y),loo(std(motif),y),loo(std(naive),y)
single=np.array([max(a,1-a) for a in (roc_auc_score(y,T[c].fillna(T[c].median())) for c in designed+motif)])
med_single=np.median(single)
rng=np.random.RandomState(0)
noise=np.mean([loo(rng.randn(len(y),len(designed)),y) for _ in range(40)])
perm=np.mean([loo(std(designed),rng.permutation(y)) for _ in range(200) ])
e_rot=T[T.cohort=="expert"].total_rot_deg; p_rot=T[T.cohort=="student"].total_rot_deg
ratio=e_rot.mean()/p_rot.mean()

# motif re-mined IN-FOLD (honest), from cached windows if present -> exposes the 0.95->0.81 swing
m_nested=None
try:
    from sklearn.cluster import KMeans
    z=np.load(OUT/"motif_windows.npz",allow_pickle=True); DAT={k:z[k] for k in z.files}
    coh=dict(zip(T.assignee,T.cohort)); mu=[u for u in T.assignee if u in DAT]
    my=np.array([1 if coh[u]=="expert" else 0 for u in mu]); K=10
    def _h(km,sc,w):
        l=km.predict(sc.transform(w)); h=np.bincount(l,minlength=K).astype(float); s=h.sum(); return h/s if s else h
    pr=np.zeros(len(mu))
    for i in range(len(mu)):
        tr=[j for j in range(len(mu)) if j!=i]
        trw=np.vstack([DAT[mu[j]] for j in tr]); sc=StandardScaler().fit(trw)
        km=KMeans(K,n_init=10,random_state=0).fit(sc.transform(trw))
        Xtr=np.array([_h(km,sc,DAT[mu[j]]) for j in tr])
        pr[i]=LogisticRegression(max_iter=1000,class_weight="balanced").fit(Xtr,my[tr]).predict_proba(_h(km,sc,DAT[mu[i]]).reshape(1,-1))[0,1]
    m_nested=roc_auc_score(my,pr)
except Exception as e:
    print("(motif re-mine unavailable -> ladder shows cached only: %s)"%e)

fig,ax=plt.subplots(1,2,figsize=(7.6,5.15),gridspec_kw={"width_ratios":[1,1.18]})
# ---- LEFT: rotation dotplot (the un-fished anchor) ----
jit=rng.RandomState if False else np.random.RandomState(1)
ax[0].scatter(jit.normal(0,0.06,len(e_rot)),e_rot,c=EXP,s=70,edgecolor="k",lw=.4,label="expert",zorder=3)
ax[0].scatter(jit.normal(1,0.06,len(p_rot)),p_rot,c=STU,s=70,edgecolor="k",lw=.4,label="proto-expert",zorder=3)
for xx,v in [(0,e_rot.mean()),(1,p_rot.mean())]:
    ax[0].plot([xx-0.18,xx+0.18],[v,v],c="k",lw=2,zorder=4)
ax[0].set_xticks([0,1]); ax[0].set_xticklabels(["expert","proto-\nexpert"],fontsize=11)
ax[0].set_xlim(-0.5,1.5); ax[0].set_ylabel("total camera rotation (deg)",fontsize=10)
ax[0].set_title("Experts explore ~%.2f× more\n(no model needed)"%ratio,fontsize=11,weight="bold")
ax[0].legend(fontsize=8,loc="upper right")
# ---- RIGHT: honest AUC ladder (motif tier is CV-based: k-means refit IN-FOLD, not on all data) ----
import matplotlib.patches as mpatches
if m_nested is None: print("WARNING: no CV motif number — omitting motif row (will NOT show leaky 0.95)")
rows=[("designed (28, post-hoc)",d_loo,EXP),("naive (4 counts)",n_loo,"#59A14F")]
if m_nested is not None: rows.append(("learned (10-motif, CV)",m_nested,"#59A14F"))
rows+=[("28 noise features",noise,"#9e9e9e"),("random labels (null)",perm,"#9e9e9e")]
yp=np.arange(len(rows))[::-1]
ax[1].barh(yp,[v for _,v,_ in rows],color=[c for *_,c in rows],edgecolor="k",lw=.5,height=0.6,zorder=3)
for yy,(lab,v,_) in zip(yp,rows):
    ax[1].text(v+0.015,yy,"%.2f"%v,va="center",ha="left",fontsize=9,weight="bold")
ax[1].axvline(0.5,ls=":",c="k",lw=1,zorder=2)
ax[1].set_yticks(yp); ax[1].set_yticklabels([r[0] for r in rows],fontsize=9)
ax[1].set_xlim(0,1.22); ax[1].set_xticks([0,0.5,1.0]); ax[1].set_xlabel("expert-vs-proto ROC-AUC (LOO)",fontsize=10)
ax[1].set_title("Honest AUC ladder (LOO, CV)",fontsize=11,weight="bold")
leg=[mpatches.Patch(color=EXP,label="engineered ceiling (28 post-hoc feat)"),
     mpatches.Patch(color="#59A14F",label="robust floor (un-fished / CV)"),
     mpatches.Patch(color="#9e9e9e",label="chance — CV catches noise")]
ax[1].legend(handles=leg,fontsize=6.6,loc="lower right",framealpha=.92,borderpad=.5)
plt.figtext(0.995,0.005,"Preliminary analysis — MICrONS proofreading annotators (n=16 pilot)",
            ha="right",va="bottom",fontsize=6,style="italic",color="0.5")
plt.tight_layout(rect=[0,0.015,1,1]); plt.savefig(TALK/"fig_expertise_evidence.png",dpi=160)
print("designed=%.2f naive=%.2f learned_leaky=%.2f learned_CV=%s median_single=%.2f noise=%.2f perm=%.2f rot_ratio=%.2f"%(
    d_loo,n_loo,m_loo,("%.2f"%m_nested if m_nested is not None else "NA"),med_single,noise,perm,ratio))
print("saved fig_expertise_evidence.png")
