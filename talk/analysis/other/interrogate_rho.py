"""Interrogate the rho=-0.44 'expertise axis vs accuracy' claim.
Q: is style really ANTI-correlated with proficiency, or is that (a) noise at n=16,
   (b) a ceiling/range-restriction artifact, (c) a task-difficulty routing confound
   (experts get the hard tasks), (d) an artifact of a too-poor representation?"""
import numpy as np, pandas as pd
from scipy import stats
from scipy.stats import rankdata
np.seterr(all="ignore")
D="/tmp/claude-0/-home-user-berlin/eb94da13-135d-5ec6-9497-7a16104e77d6/scratchpad/live_out/"
T=pd.read_csv(D+"tiers_data.csv")
fp=pd.read_csv(D+"fullyproofread_accuracy.csv")[["assignee","acc_relax","acc_strict","n_pts"]]
M=T.merge(fp,on="assignee",how="inner")
rng=np.random.RandomState(0)

def boot_rho(x,y,n=5000):
    x=np.asarray(x); y=np.asarray(y); out=[]
    for _ in range(n):
        i=rng.choice(len(x),len(x),replace=True)
        if len(set(x[i]))<3 or len(set(y[i]))<3: continue
        out.append(stats.spearmanr(x[i],y[i])[0])
    return np.percentile(out,[2.5,50,97.5])

print("="*70)
print("1) THE HEADLINE NUMBER, with uncertainty (n=%d calibrated annotators)"%len(M))
print("="*70)
print("  acc_relax: mean=%.3f  std=%.3f  min=%.3f  max=%.3f  (ceiling? range=%.3f)"%(
    M.acc_relax.mean(),M.acc_relax.std(),M.acc_relax.min(),M.acc_relax.max(),M.acc_relax.max()-M.acc_relax.min()))
print("  acc_relax by cohort: expert=%.3f  proto=%.3f"%(
    M[M.cohort=='expert'].acc_relax.mean(),M[M.cohort=='student'].acc_relax.mean()))
for col in ["total_rot_deg","n_rot","mean_rot","n_events"]:
    rho,p=stats.spearmanr(M[col],M.acc_relax)
    lo,med,hi=boot_rho(M[col],M.acc_relax)
    print("  %-14s vs acc_relax: rho=%+.2f p=%.3f  boot95%%CI[%+.2f,%+.2f]  %s"%(
        col,rho,p,lo,hi,"** crosses 0 (n.s.)" if lo<0<hi else ""))

print("\n"+"="*70)
print("2) DIFFICULTY CONFOUND — do experts get routed the HARDER tasks?")
print("="*70)
en=pd.read_csv(D+"enriched_task.csv")
diff=en.groupby("assignee").agg(mean_pts=("n_pts","mean"),frac_axon=("f_axon","mean"),
        frac_dend=("f_dendrite","mean"),task_acc=("acc","mean"),n_tasks=("acc","size")).reset_index()
M2=M.merge(diff,on="assignee",how="inner")
print("  task SIZE (mean_pts)   expert=%.1f proto=%.1f"%(M2[M2.cohort=='expert'].mean_pts.mean(),M2[M2.cohort=='student'].mean_pts.mean()))
print("  frac AXON points       expert=%.3f proto=%.3f  (axon = the hard, error-prone category)"%(
    M2[M2.cohort=='expert'].frac_axon.mean(),M2[M2.cohort=='student'].frac_axon.mean()))
print("  rotation vs task-difficulty: total_rot_deg~mean_pts rho=%+.2f ; ~frac_axon rho=%+.2f"%(
    stats.spearmanr(M2.total_rot_deg,M2.mean_pts)[0],stats.spearmanr(M2.total_rot_deg,M2.frac_axon)[0]))

def partial_sp(x,y,z):
    rx,ry,rz=rankdata(x),rankdata(y),rankdata(z)
    ex=rx-np.polyval(np.polyfit(rz,rx,1),rz); ey=ry-np.polyval(np.polyfit(rz,ry,1),rz)
    return stats.pearsonr(ex,ey)
for z,zn in [(M2.mean_pts,"task size"),(M2.frac_axon,"frac axon")]:
    r0=stats.spearmanr(M2.total_rot_deg,M2.acc_relax)[0]; rp,pp=partial_sp(M2.total_rot_deg.values,M2.acc_relax.values,z.values)
    print("  rot vs acc | controlling %-10s: raw rho=%+.2f -> partial=%+.2f (p=%.2f)  %s"%(
        zn,r0,rp,pp,"<- negative DISSOLVES" if abs(rp)<abs(r0)*0.6 else ""))

print("\n"+"="*70)
print("3) IS IT THE REPRESENTATION? does a RICHER grammar relate to acc sensibly,")
print("   or is EVERY behavioral feature null vs accuracy (=> it's the ceiling target)?")
print("="*70)
motif=[c for c in T.columns if c.startswith("motif_")]
gram=["bg_NN","bg_NS","bg_SN","bg_SS","tg_NSN","tg_SNS","tg_NNN","tg_SSS","runN_max","runS_max","entropy"]
kin=["total_rot_deg","n_rot","mean_rot","n_events","evt_per_session","pct_S","pct_N","dt_med"]
rhos=[]
for c in motif+gram+kin:
    if c in M.columns:
        r,p=stats.spearmanr(M[c],M.acc_relax); rhos.append((c,r,p))
arr=np.array([r for _,r,_ in rhos])
nsig=sum(1 for _,_,p in rhos if p<0.05)
print("  %d behavioral features vs acc_relax: |rho| mean=%.2f max=%.2f ; %d/%d reach p<0.05"%(
    len(rhos),np.abs(arr).mean(),np.abs(arr).max(),nsig,len(rhos)))
print("  sign balance: %d negative, %d positive (if ~50/50 => scatter, not a real axis)"%((arr<0).sum(),(arr>0).sum()))
exp=stats.binom_test(nsig,len(rhos),0.05) if hasattr(stats,'binom_test') else stats.binomtest(nsig,len(rhos),0.05).pvalue
print("  # significant vs chance (binomial p)=%.2f  => %s"%(exp,"no more than chance" if exp>0.05 else "above chance"))
strongest=sorted(rhos,key=lambda t:-abs(t[1]))[:5]
print("  strongest |rho| (still n=16, uncorrected): "+", ".join("%s=%+.2f(p%.2f)"%(c,r,p) for c,r,p in strongest))

print("\n"+"="*70)
print("4) VARIANCE-RICH TARGET — where accuracy ISN'T at ceiling (multiSomaSplit dist-to-GT),")
print("   do richer kinematics line up the LOGICAL way (more skill -> smaller error)?")
print("="*70)
try:
    ms=pd.read_csv(D+"multisomasplit_competency.csv")
    md=ms[ms.dist_nm<=2000].groupby("assignee").agg(dist=("dist_nm","median"),cohort=("cohort","first")).reset_index()
    R=T.merge(md,on="assignee",how="inner")
    print("  n=%d  dist median=%.0f std=%.0f nm (real spread, NOT a ceiling)"%(len(R),R.dist.median(),R.dist.std()))
    print("  dist by cohort: expert=%.0f proto=%.0f nm  (lower=better; expert better?=%s)"%(
        R[R.cohort=='expert'].dist.median(),R[R.cohort=='student'].dist.median(),
        R[R.cohort=='expert'].dist.median()<R[R.cohort=='student'].dist.median()))
    for c in ["total_rot_deg","n_rot","n_events","entropy"]:
        r,p=stats.spearmanr(R[c],R.dist)
        print("    %-14s vs dist: rho=%+.2f p=%.2f  (NEG => more of it -> smaller error -> skill helps)"%(c,r,p))
except Exception as e:
    print("  (multisoma target unavailable: %s)"%e)
print("\nDONE")
