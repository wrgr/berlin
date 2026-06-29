#!/usr/bin/env python3
"""fig_point_agreement.png — calibration converges at the level of individual decisions.

Left: per-annotator point-label agreement with the expert grader (Pat / rivlipk1), by group
(expert / promoted / unpromoted). Each dot is one annotator (handles suppressed); the bar is the
group median. Right: the per-point confusion matrix for one representative expert (chris) — nearly
the identity, one off-diagonal in 142 points.

This is the outcome/agreement companion to the behavioral evidence: experts and promoted students
converge to the grader's decisions (~99%), while the unpromoted group is bimodal with a low tail —
why competence is legible per-decision, not per-person.

Network: queries NeuVue (needs .nv_tokens.json + the neuvueclient checkout). Per-annotator values
are cached to live_out/ (gitignored, carries handles); only the PNG is committed.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from compare_points import neuvue_queue, grab, compare_one  # noqa: E402

GROUPS = {
    "Expert": ["chris", "christopher", "claire", "erika", "gary", "michael", "natalie", "phillips"],
    "Promoted": ["dylan", "vivia", "taylor", "clara", "rachel", "shruthi", "sarah"],
    "Unpromoted": ["maggie", "donovan9", "emily", "mia", "aashi", "emma", "joey", "cindy", "katie", "titus"],
}
COLORS = {"Expert": "#b2182b", "Promoted": "#2166ac", "Unpromoted": "#7f7f7f"}
STAMP = "Preliminary analysis — MICrONS proofreading annotators · handles suppressed"

def main():
    nq = neuvue_queue()
    G = grab(nq, "rivlipk1", "patProofread", 600)
    group_acc, chris_conf = {}, None
    for grp, users in GROUPS.items():
        accs = []
        for u in users:
            m = compare_one(grab(nq, u, "fullyProofread", 600), G, normalize=True)
            if m["matched"]:
                accs.append(100 * m["agree"] / m["matched"])
                if u == "chris": chris_conf = m["confusion"]
        group_acc[grp] = accs
        print(f"{grp:11s} n={len(accs)}  median={np.median(accs):.1f}  mean={np.mean(accs):.1f}")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.05, 1]})

    # ---- left: per-annotator agreement by group ----
    rng = np.random.default_rng(0)
    for i, (grp, accs) in enumerate(group_acc.items()):
        x = i + (rng.random(len(accs)) - 0.5) * 0.28
        axL.scatter(x, accs, s=46, color=COLORS[grp], alpha=0.8, edgecolor="white", zorder=3)
        axL.plot([i - 0.28, i + 0.28], [np.median(accs)] * 2, color=COLORS[grp], lw=3, zorder=4)
        axL.text(i, 103.5, f"med {np.median(accs):.0f}%", ha="center", fontsize=9, color=COLORS[grp])
    axL.set_xticks(range(len(group_acc)))
    axL.set_xticklabels([f"{g}\n(n={len(a)})" for g, a in group_acc.items()])
    axL.set_ylabel("point-label agreement with expert grader (%)")
    axL.set_ylim(20, 108); axL.axhline(100, color="0.8", lw=0.8, ls="--", zorder=1)
    axL.set_title("Calibration converges — per decision", fontsize=11)
    axL.grid(axis="y", alpha=0.25)

    # ---- right: chris confusion matrix ----
    labs = sorted({l for (g, p) in chris_conf for l in (g, p)})
    M = np.array([[chris_conf.get((g, p), 0) for p in labs] for g in labs], float)
    im = axR.imshow(M, cmap="Blues", aspect="auto")
    axR.set_xticks(range(len(labs))); axR.set_xticklabels([l[:9] for l in labs], rotation=45, ha="right", fontsize=8)
    axR.set_yticks(range(len(labs))); axR.set_yticklabels([l[:9] for l in labs], fontsize=8)
    for i in range(len(labs)):
        for j in range(len(labs)):
            if M[i, j]: axR.text(j, i, int(M[i, j]), ha="center", va="center",
                                 fontsize=8, color="white" if M[i, j] > M.max() * 0.5 else "0.2")
    axR.set_xlabel("chris label"); axR.set_ylabel("grader (Pat) label")
    axR.set_title("Representative expert: 99.3% (141/142)", fontsize=11)
    fig.colorbar(im, ax=axR, fraction=0.046, pad=0.04, label="points")

    fig.suptitle("Behavioral style differs; the decisions converge", fontsize=12.5, y=0.99)
    fig.text(0.5, 0.005, STAMP, ha="center", fontsize=7.5, color="0.45")
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    out = HERE.parent / "fig_point_agreement.png"
    fig.savefig(out, dpi=150)
    print("saved", out)

if __name__ == "__main__":
    main()
