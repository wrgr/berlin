"""Talk figures (item 2), HANDLES SUPPRESSED (anonymized E#/S# codes, cohort/promoted shown as category)."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))   # CSVs (override with BERLIN_DATA)
TALK=Path(os.environ.get("BERLIN_TALK", HERE.parent))      # repo talk/ for figure output
CAV="Preliminary analysis — MICrONS proofreading annotators"
def _cav():
    plt.figtext(0.995,0.004,CAV,ha="right",va="bottom",fontsize=6,style="italic",color="0.5")
made=[]
# ---- global anonymization map (handles -> E#/S#, alphabetical within cohort) ----
def build_anon():
    frames=[]
    for f in ["fullyproofread_accuracy.csv","multisomasplit_competency.csv","separability_annotator.csv"]:
        p=OUT/f
        if p.exists():
            d=pd.read_csv(p)
            if "assignee" in d.columns and "cohort" in d.columns: frames.append(d[["assignee","cohort"]])
    allann=pd.concat(frames).dropna().drop_duplicates("assignee")
    m={}
    for coh,pref in [("expert","E"),("student","S")]:
        for i,a in enumerate(sorted(allann[allann.cohort==coh]["assignee"].unique()),1): m[a]=f"{pref}{i}"
    return m
ANON=build_anon(); an=lambda a: ANON.get(a,"?")
EXP="#E45756"; STU="#4C78A8"
# ---- Fig 1: naive/designed/learned tier AUC (no handles) ----
fig,ax=plt.subplots(figsize=(5,3.4))
tiers=["naive\n(4 counts)","designed\n(28 hand-built)","learned\n(10-motif dict.)"]; auc=[0.75,0.95,0.90]
ax.bar(tiers,auc,color=["#bdbdbd",STU,EXP]); ax.set_ylim(0.5,1.0); ax.axhline(0.5,ls=":",c="k",lw=.8)
for i,a in enumerate(auc): ax.text(i,a+0.012,f"{a:.2f}",ha="center",fontweight="bold")
ax.set_ylabel("CV ROC-AUC (n=16)"); ax.set_title("Behavior separates experts from proto-experts\nnaive → designed → learned")
plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_tier_auc.png",dpi=150); plt.close(); made.append("fig_tier_auc.png")
# ---- Fig 2: learned motif dictionary (no handles) ----
# centroids from the corrected (per-differstack rotation) k-means run; see mine_tiers.py
cent=np.array([
 [0.51,0.49,0.00,0.00,1.12,0.37,0.00,0.73],[0.00,1.00,0.00,0.00,1.06,0.36,0.00,0.00],
 [0.17,0.82,0.00,0.01,1.85,1.07,0.00,0.28],[0.51,0.45,0.00,0.04,1.37,0.57,0.14,0.48],
 [0.28,0.52,0.00,0.20,1.16,0.44,0.00,0.65],[0.16,0.58,0.21,0.05,1.77,0.93,0.00,0.65],
 [0.62,0.36,0.00,0.02,1.89,1.29,0.00,0.48],[0.83,0.16,0.00,0.01,1.09,0.38,0.00,0.23],
 [0.22,0.30,0.00,0.47,1.15,0.45,0.00,0.58],[0.27,0.73,0.00,0.00,1.14,0.36,0.00,0.39]])
labels=["frac Navigate","frac Segment","frac Annotate","frac Other","mean logΔt","std logΔt","mean rotation","change-rate"]
Z=(cent-cent.mean(0))/(cent.std(0)+1e-9)
fig,ax=plt.subplots(figsize=(7.2,4.2)); im=ax.imshow(Z,aspect="auto",cmap="RdBu_r",vmin=-2,vmax=2)
ax.set_xticks(range(8)); ax.set_xticklabels(labels,rotation=30,ha="right",fontsize=8)
ax.set_yticks(range(10)); ax.set_yticklabels([f"motif {i}" for i in range(10)],fontsize=8)
ax.set_title("Learned motif dictionary — unsupervised k-means 'gestures'\nover label + timing + rotation windows (language-of-surgery analog)")
plt.colorbar(im,label="z-score per feature",fraction=0.046); plt.tight_layout()
_cav(); plt.savefig(TALK/"fig_motif_dictionary.png",dpi=150); plt.close(); made.append("fig_motif_dictionary.png")
# ---- Fig 3: two-task accuracy (HANDLES SUPPRESSED) ----
try:
    ms=pd.read_csv(OUT/"multisomasplit_competency.csv"); ms=ms[ms.dist_nm<=2000][["assignee","dist_nm","cohort"]]
    fp=pd.read_csv(OUT/"fullyproofread_accuracy.csv")[["assignee","acc_relax","promoted"]]
    M=ms.merge(fp,on="assignee",how="inner")
    fig,ax=plt.subplots(figsize=(6,4.2))
    for coh,c in [("expert",EXP),("student",STU)]:
        s=M[M.cohort==coh]; ax.scatter(s.dist_nm,s.acc_relax,c=c,label=coh,s=42,edgecolor="k",lw=.3,zorder=3)
    pr=M[M.promoted==1]; ax.scatter(pr.dist_nm,pr.acc_relax,facecolors="none",edgecolors="green",s=120,lw=1.7,label="promoted (proto-expert)",zorder=4)
    bd=M.sort_values("dist_nm").iloc[0]
    ax.annotate("best split placement\n= a novice",(bd.dist_nm,bd.acc_relax),fontsize=7,xytext=(10,-22),textcoords="offset points",arrowprops=dict(arrowstyle="->",lw=.6))
    ax.set_xlabel("multiSomaSplit distance-to-GT (nm) — lower better"); ax.set_ylabel("fullyProofread label accuracy")
    ax.set_title("Two quality metrics, both ceiling-clustered\nthe variance is in the tail   (handles suppressed)")
    ax.legend(fontsize=7,loc="lower left"); plt.tight_layout()
    _cav(); plt.savefig(TALK/"fig_two_task_quality.png",dpi=150); plt.close(); made.append("fig_two_task_quality.png")
except Exception as e: print("fig3 skipped:",e)
# ---- Fig 4: separability + GT-free uncertainty (HANDLES SUPPRESSED) ----
sa=OUT/"separability_annotator.csv"; st=OUT/"separability_task.csv"
if sa.exists() and st.exists():
    try:
        A=pd.read_csv(sa).sort_values("acc").reset_index(drop=True); T=pd.read_csv(st)
        fig,axs=plt.subplots(1,2,figsize=(11,4.4))
        cols=A.cohort.map({"expert":EXP,"student":STU}).fillna("#999")
        axs[0].barh(range(len(A)),A.acc,color=cols)
        axs[0].set_yticks(range(len(A))); axs[0].set_yticklabels([an(a) for a in A.assignee],fontsize=6)
        axs[0].axvline(0.90,ls=":",c="k"); axs[0].set_xlim(0,1.02)
        axs[0].set_xlabel("fullyProofread accuracy"); axs[0].set_title("Per-annotator competence (handles suppressed)\nbad tail < 0.90; simple behavior can't predict it")
        axs[0].legend(handles=[Patch(color=EXP,label="expert"),Patch(color=STU,label="student")],fontsize=7,loc="lower right")
        T2=T.dropna(subset=["dur"]).copy()
        T2["dur_z"]=T2.groupby("assignee")["dur"].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
        good=T2[T2.err==0]["dur_z"]; bad=T2[T2.err==1]["dur_z"]
        axs[1].hist([good.clip(-3,3),bad.clip(-3,3)],bins=18,label=["correct task","error task"],color=["#9ecae1","#de2d26"],density=True)
        axs[1].set_xlabel("within-annotator duration z  (slow-for-this-person)"); axs[1].set_ylabel("density")
        axs[1].set_title("GT-free 'subconscious uncertainty'\nanomalous tasks are more error-prone (AUC 0.59, p<0.001)"); axs[1].legend(fontsize=8)
        plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_separability.png",dpi=150); plt.close(); made.append("fig_separability.png")
    except Exception as e: print("fig4 skipped:",e)
print("anon map size:",len(ANON)); print("made:",made)
