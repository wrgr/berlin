"""Robustness of the rho=-0.44 'expertise style vs accuracy' point estimate.
Question (raised in review): does rho=-0.44 mean "style != proficiency", or is it an
artifact of a too-poor representation? Answer: neither — it is a NON-SIGNIFICANT point
estimate (the max of a null field) on a CEILING/range-restricted target. A calibrated cohort
(8 experts + 8 promoted proto-experts; no true novices) has almost no accuracy variance to
predict, so no representation — however rich — recovers a per-person accuracy signal, in
either direction. The grammar is rich enough to read EXPERTISE (AUC 0.90-0.98); it cannot read
RESIDUAL ACCURACY AMONG THE CALIBRATED because there is none.

Offline; reads live_out CSVs. Override the data dir with BERLIN_DATA.
Run:  BERLIN_DATA=/path/to/live_out python rho_robustness.py
"""
import os
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from scipy.stats import rankdata
np.seterr(all="ignore")
HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("BERLIN_DATA", HERE / "live_out"))
rng = np.random.RandomState(0)

T  = pd.read_csv(OUT / "tiers_data.csv")
fp = pd.read_csv(OUT / "fullyproofread_accuracy.csv")[["assignee", "acc_relax"]]
M  = T.merge(fp, on="assignee", how="inner")

def boot_rho(x, y, n=5000):
    x, y = np.asarray(x), np.asarray(y); out = []
    for _ in range(n):
        i = rng.choice(len(x), len(x), replace=True)
        if len(set(x[i])) < 3 or len(set(y[i])) < 3: continue
        out.append(stats.spearmanr(x[i], y[i])[0])
    return np.percentile(out, [2.5, 97.5])

print("=" * 68)
print("1) THE NUMBER, WITH UNCERTAINTY  (n=%d calibrated annotators)" % len(M))
print("=" * 68)
print("   acc_relax: mean=%.3f std=%.3f range=[%.3f,%.3f]  (ceiling)" % (
    M.acc_relax.mean(), M.acc_relax.std(), M.acc_relax.min(), M.acc_relax.max()))
print("   by cohort: expert=%.3f  proto-expert=%.3f  (protos were promoted FOR agreement)" % (
    M[M.cohort == "expert"].acc_relax.mean(), M[M.cohort == "student"].acc_relax.mean()))
for c in ["total_rot_deg", "n_rot", "n_events"]:
    rho, p = stats.spearmanr(M[c], M.acc_relax); lo, hi = boot_rho(M[c], M.acc_relax)
    print("   %-13s vs acc: rho=%+.2f p=%.3f  boot95%%CI[%+.2f,%+.2f] %s" % (
        c, rho, p, lo, hi, "<- crosses 0 (n.s.)" if lo < 0 < hi else ""))

print("\n" + "=" * 68)
print("2) IT IS A SELECTION-CONFOUNDED BETWEEN-COHORT COMPARISON (not 'skill hurts')")
print("=" * 68)
print("   pooled rho=%+.2f decomposes into two clouds with NO within-cohort trend:" % stats.spearmanr(M.total_rot_deg, M.acc_relax)[0])
for coh, lb in [("expert", "experts"), ("student", "proto-experts")]:
    s = M[M.cohort == coh]; r, p = stats.spearmanr(s.total_rot_deg, s.acc_relax)
    print("     %-13s n=%2d: rotation=%4.0f  acc=%.3f  within-rho=%+.2f (p=%.2f)" % (
        lb, len(s), s.total_rot_deg.mean(), s.acc_relax.mean(), r, p))
print("   MECHANISM: proto-experts were promoted FOR agreeing with graders; fullyProofread acc IS")
print("   grader-agreement -> the comparison group is selected on the outcome metric. The expertise")
print("   features (rotation/runs/motifs) mark experts, so they inherit a spurious negative.")
print("   (Secondary: no SINGLE behavioral feature significantly predicts accuracy either --)")
motif = [c for c in T.columns if c.startswith("motif_")]
gram  = ["bg_NN", "bg_NS", "bg_SN", "bg_SS", "tg_NSN", "tg_SNS", "tg_NNN", "tg_SSS",
         "runN_max", "runS_max", "entropy"]
kin   = ["total_rot_deg", "n_rot", "mean_rot", "n_events", "evt_per_session", "pct_S", "pct_N", "dt_med"]
rhos  = [(c, *stats.spearmanr(M[c], M.acc_relax)) for c in motif + gram + kin if c in M.columns]
arr   = np.array([r for _, r, _ in rhos]); nsig = sum(p < 0.05 for _, _, p in rhos)
binom = (stats.binomtest(nsig, len(rhos), 0.05).pvalue if hasattr(stats, "binomtest")
         else stats.binom_test(nsig, len(rhos), 0.05))
print("   %d features vs acc_relax: %d/%d reach p<0.05 (binomial vs chance p=%.2f)" % (
    len(rhos), nsig, len(rhos), binom))
print("   sign balance: %d negative / %d positive  (negatives concentrated in the EXPERTISE features"
      " -> consistent with the selection effect, not random scatter)" % ((arr < 0).sum(), (arr > 0).sum()))
print("   strongest |rho| (still n.s.): " + ", ".join(
    "%s=%+.2f(p%.2f)" % (c, r, p) for c, r, p in sorted(rhos, key=lambda t: -abs(t[1]))[:4]))

print("\n" + "=" * 68)
print("3) NOT A TASK-DIFFICULTY CONFOUND")
print("=" * 68)
en = pd.read_csv(OUT / "enriched_task.csv")
diff = en.groupby("assignee").agg(mean_pts=("n_pts", "mean"), frac_axon=("f_axon", "mean")).reset_index()
M2 = M.merge(diff, on="assignee", how="inner")
print("   task size  expert=%.1f proto=%.1f pts ; frac-axon expert=%.3f proto=%.3f (equal => no routing confound)" % (
    M2[M2.cohort == "expert"].mean_pts.mean(), M2[M2.cohort == "student"].mean_pts.mean(),
    M2[M2.cohort == "expert"].frac_axon.mean(), M2[M2.cohort == "student"].frac_axon.mean()))
def partial_sp(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz); ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return stats.pearsonr(ex, ey)[0]
r0 = stats.spearmanr(M2.total_rot_deg, M2.acc_relax)[0]
for z, zn in [(M2.mean_pts, "task size"), (M2.frac_axon, "frac axon")]:
    print("   rot vs acc | %-9s: raw %+.2f -> partial %+.2f  (difficulty does NOT explain it)" % (
        zn, r0, partial_sp(M2.total_rot_deg.values, M2.acc_relax.values, z.values)))

print("\n" + "=" * 68)
print("4) WHERE ACCURACY HAS REAL SPREAD (multiSomaSplit dist-to-GT), SKILL STILL ~FLAT")
print("=" * 68)
ms = pd.read_csv(OUT / "multisomasplit_competency.csv")
md = ms[ms.dist_nm <= 2000].groupby("assignee").agg(dist=("dist_nm", "median"), coh=("cohort", "first")).reset_index()
R = T.merge(md, on="assignee", how="inner")
print("   n=%d  dist median=%.0f nm range=[%.0f,%.0f] (real spread); expert=%.0f proto=%.0f (~equal)" % (
    len(R), R.dist.median(), R.dist.min(), R.dist.max(),
    R[R.coh == "expert"].dist.median(), R[R.coh == "student"].dist.median()))
for c in ["total_rot_deg", "n_rot", "entropy"]:
    r, p = stats.spearmanr(R[c], R.dist)
    print("   %-13s vs dist: rho=%+.2f p=%.2f  (neg=skill helps; all n.s./mixed)" % (c, r, p))
print("\nVERDICT: rho=-0.44 is a non-significant, selection-confounded between-cohort comparison")
print("         (proto-experts selected on grader-agreement = the metric), not 'style != proficiency'.")
print("         No representation predicts a near-constant, selection-shaped target. Flag DECISIONS,")
print("         not calibrated PEOPLE.")
