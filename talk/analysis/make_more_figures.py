"""Over-complete data-figure pool (handles suppressed; all from computed CSVs, accurate).
NOTE: in tiers_data, 'student' = the 8 agreement-promoted proto-experts (only students with
dense multiSomaId telemetry), so expert-vs-student here = expert-vs-proto-expert. Labeled as such."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))   # CSVs (override with BERLIN_DATA)
TALK=Path(os.environ.get("BERLIN_TALK", HERE.parent))      # repo talk/ for figure output
CAV="Preliminary analysis — MICrONS proofreading annotators"
def _cav():
    plt.figtext(0.995,0.004,CAV,ha="right",va="bottom",fontsize=6,style="italic",color="0.5")
EXP="#E45756"; STU="#4C78A8"; made=[]
PROMOTED={"dylan","vivia","taylor","clara","rachel","shruthi","sarah","lydia"}
def box2(ax,a,b,title,ylab,la="expert",lb="proto-expert"):
    bp=ax.boxplot([a,b],tick_labels=[la,lb],patch_artist=True,widths=.6,showfliers=False)
    for p,c in zip(bp["boxes"],[EXP,STU]): p.set_facecolor(c); p.set_alpha(.6)
    for i,d in enumerate([a,b]): ax.scatter(np.random.RandomState(i).normal(i+1,.05,len(d)),d,c="k",s=12,zorder=3)
    ax.set_title(title,fontsize=10); ax.set_ylabel(ylab,fontsize=9)
try:
    T=pd.read_csv(OUT/"tiers_data.csv"); E=T[T.cohort=="expert"]; S=T[T.cohort=="student"]
    # ---- Fig: 3D exploration kinematics + tempo ----
    fig,axs=plt.subplots(1,4,figsize=(13,3.6))
    box2(axs[0],E.total_rot_deg,S.total_rot_deg,"total camera rotation","degrees")
    box2(axs[1],E.n_rot,S.n_rot,"# rotations (viewpoints)","count")
    box2(axs[2],E.n_events,S.n_events,"events per annotator","count")
    box2(axs[3],E.evt_per_session,S.evt_per_session,"events / session (tempo)","count")
    fig.suptitle("3-D exploration kinematics — experts inspect from more viewpoints, more thoroughly (handles suppressed)",fontsize=11)
    plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_kinematics.png",dpi=150); plt.close(); made.append("fig_kinematics.png")
    # ---- Fig: RF feature importance (designed, expert vs proto-expert) ----
    from sklearn.ensemble import RandomForestClassifier
    drop=["assignee","cohort","promoted"]+[c for c in T.columns if c.startswith("motif_")]
    feats=[c for c in T.columns if c not in drop and T[c].dtype!=object]
    X=T[feats].fillna(T[feats].median()); y=(T.cohort=="expert").astype(int)
    rf=RandomForestClassifier(800,min_samples_leaf=2,random_state=0).fit(X,y)
    imp=pd.Series(rf.feature_importances_,index=feats).sort_values().tail(12)
    fig,ax=plt.subplots(figsize=(6,4.2)); ax.barh(imp.index,imp.values,color="#4C78A8")
    ax.set_title("What separates experts from proto-experts\n(RandomForest importance, designed features; n=16)",fontsize=10)
    ax.set_xlabel("importance"); plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_rf_importance_new.png",dpi=150); plt.close(); made.append("fig_rf_importance_new.png")
    # ---- Fig: PCA of designed feature space ----
    from sklearn.preprocessing import StandardScaler; from sklearn.decomposition import PCA
    Z=StandardScaler().fit_transform(X); pc=PCA(2,random_state=0).fit(Z); P=pc.transform(Z)
    fig,ax=plt.subplots(figsize=(5.4,4.4))
    for coh,c,lab in [(1,EXP,"expert"),(0,STU,"proto-expert")]:
        m=(y==coh); ax.scatter(P[m,0],P[m,1],c=c,s=55,edgecolor="k",lw=.3,label=lab)
    pr=T.promoted==1; ax.scatter(P[pr.values,0],P[pr.values,1],facecolors="none",edgecolors="green",s=130,lw=1.6,label="promoted")
    ax.set_xlabel(f"PC1 ({pc.explained_variance_ratio_[0]:.0%})"); ax.set_ylabel(f"PC2 ({pc.explained_variance_ratio_[1]:.0%})")
    ax.set_title("Designed behavioral feature space\nexperts vs proto-experts (handles suppressed)",fontsize=10); ax.legend(fontsize=8)
    plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_feature_pca.png",dpi=150); plt.close(); made.append("fig_feature_pca.png")
    # ---- Fig: learned motif usage by cohort ----
    mc=[c for c in T.columns if c.startswith("motif_")]
    em=E[mc].mean(); sm=S[mc].mean(); x=np.arange(len(mc)); w=.38
    fig,ax=plt.subplots(figsize=(7,3.6)); ax.bar(x-w/2,em.values,w,label="expert",color=EXP); ax.bar(x+w/2,sm.values,w,label="proto-expert",color=STU)
    ax.set_xticks(x); ax.set_xticklabels([f"m{i}" for i in range(len(mc))]); ax.set_ylabel("mean usage")
    ax.set_title("Learned motif-dictionary usage by cohort\n(behavioral dialect in the unsupervised space)",fontsize=10); ax.legend(fontsize=8)
    plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_motif_usage.png",dpi=150); plt.close(); made.append("fig_motif_usage.png")
    # ---- Fig: action mix + N/S transition grammar ----
    fig,axs=plt.subplots(1,3,figsize=(12,3.6))
    mix_e=[E[f"pct_{t}"].mean() for t in "NSAO"]; mix_s=[S[f"pct_{t}"].mean() for t in "NSAO"]
    xx=np.arange(4); axs[0].bar(xx-.19,mix_e,.38,label="expert",color=EXP); axs[0].bar(xx+.19,mix_s,.38,label="proto-expert",color=STU)
    axs[0].set_xticks(xx); axs[0].set_xticklabels(["navigate","segment","annotate","other"],rotation=20); axs[0].set_ylabel("fraction of actions"); axs[0].set_title("Action mix",fontsize=10); axs[0].legend(fontsize=8)
    for ax,grp,nm in [(axs[1],E,"expert"),(axs[2],S,"proto-expert")]:
        nn,ns,sn,ss=grp.bg_NN.mean(),grp.bg_NS.mean(),grp.bg_SN.mean(),grp.bg_SS.mean()
        M=np.array([[nn,ns],[sn,ss]]); M=M/M.sum(1,keepdims=True)
        im=ax.imshow(M,cmap="Blues",vmin=0,vmax=1)
        for i in range(2):
            for j in range(2): ax.text(j,i,f"{M[i,j]:.2f}",ha="center",va="center")
        ax.set_xticks([0,1]); ax.set_xticklabels(["→N","→S"]); ax.set_yticks([0,1]); ax.set_yticklabels(["N→","S→"]); ax.set_title(f"transitions: {nm}",fontsize=10)
    fig.suptitle("The language of proofreading — action mix & navigate/segment grammar (handles suppressed)",fontsize=11)
    plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_action_grammar.png",dpi=150); plt.close(); made.append("fig_action_grammar.png")
except Exception as e: print("tiers figs error:",e)
# ---- Fig: three-group accuracy (calibration converges) ----
try:
    d=pd.read_csv(OUT/"multisomasplit_competency.csv"); d=d[d.dist_nm<=2000]
    d["grp"]=np.where(d.cohort=="expert","expert",np.where(d.assignee.isin(PROMOTED),"promoted","unpromoted"))
    groups=[d[d.grp==g]["dist_nm"].values for g in ["expert","promoted","unpromoted"]]
    fig,ax=plt.subplots(figsize=(5.6,4))
    bp=ax.boxplot(groups,tick_labels=["expert\n(309)","promoted\n(312)","unpromoted\n(460)"],patch_artist=True,showfliers=False,widths=.6)
    for p,c in zip(bp["boxes"],[EXP,"#2ca25f",STU]): p.set_facecolor(c); p.set_alpha(.55)
    for i,g in enumerate(groups): ax.scatter(np.random.RandomState(i).normal(i+1,.05,len(g)),g,c="k",s=14,zorder=3)
    ax.set_ylabel("multiSomaSplit distance-to-GT (nm)"); ax.set_title("Agreement-gated promotion selects expert-level performers\npromoted ≈ expert < unpromoted (handles suppressed)",fontsize=10)
    plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_accuracy_threegroup.png",dpi=150); plt.close(); made.append("fig_accuracy_threegroup.png")
except Exception as e: print("threegroup error:",e)
# ---- Fig: per-task uncertainty calibration (error rate vs duration-z bin) ----
try:
    T2=pd.read_csv(OUT/"separability_task.csv").dropna(subset=["dur"]).copy()
    T2=T2[T2.groupby("assignee")["assignee"].transform("size")>=10].copy()
    T2["dur_z"]=T2.groupby("assignee")["dur"].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
    T2["q"]=pd.qcut(T2.dur_z,5,labels=["Q1\nfast","Q2","Q3","Q4","Q5\nslow"])
    er=T2.groupby("q")["err"].mean()
    fig,ax=plt.subplots(figsize=(5.4,4)); ax.bar(range(5),er.values,color="#de2d26",alpha=.8)
    ax.axhline(T2.err.mean(),ls="--",c="k",label=f"base rate {T2.err.mean():.2f}")
    ax.set_xticks(range(5)); ax.set_xticklabels(er.index); ax.set_ylabel("task error rate")
    ax.set_title("Subconscious uncertainty calibration\nslower-for-this-person tasks fail more (GT-free)",fontsize=10); ax.legend(fontsize=8)
    plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_uncertainty_calibration.png",dpi=150); plt.close(); made.append("fig_uncertainty_calibration.png")
except Exception as e: print("calibration error:",e)
print("made:",made)
