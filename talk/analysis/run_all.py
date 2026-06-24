#!/usr/bin/env python3
"""
LOCKED END-TO-END PIPELINE — proofreader behavior & competency (minnie65 / MICrONS)
==================================================================================
Single entry point that reproduces the full analysis behind the talk (berlin_deck_v3.pptx),
the methodology record (methodology_provenance.md), and the Nature Communications draft
(nature_comms_draft.md).

STAGES (run in order; each is a standalone, re-runnable script — this runner just sequences
them, logs timing, and STOPS on the first failure so a broken stage is obvious):

  #  name          kind      script                          produces
  1  tiers         network   mine_tiers.py                   tiers_data.csv  (naive/designed/learned; expertise AUC 0.75/0.95/0.90)
  2  fullyproof    network   mine_fullyproofread.py          fullyproofread_accuracy.csv  (categorical label accuracy vs grader GT)
  3  separability  network   mine_predictive_separability.py separability_{annotator,task}.csv  (item-1: simple-behavior fail + GT-free per-task uncertainty)
  4  prospective   offline   prospective_flagging.py         fig_prospective_flagging.png  (GT-free error-flagging curve)
  5  figures       offline   make_figures.py                 fig_tier_auc / motif_dictionary / two_task_quality / separability  (handles suppressed)
  6  morefigs      offline   make_more_figures.py            kinematics / grammar / rf_importance / pca / motif_usage / 3-group / uncertainty  (over-complete pool)
  7  deck          offline   build_deck.py                   ../berlin_deck_v3.pptx  (v2 -> 20-slide v3)

PREREQUISITES
  Network stages (1-3) query NeuVue (queue.neuvue.io) + CAVE (minnie65_phase3_v1) and need,
  in the RUN DIRECTORY (the directory this file lives in):
      .nv_tokens.json    NeuVue refresh token   (NOT committed)
      .cave_token        CAVE auth token        (NOT committed)
      neuvue-client/     checkout on the import path
      live_out/          output dir for CSVs (created if missing)
  Offline stages (4-7) consume the cached CSVs in live_out/ + the uploaded v2 deck; no creds.
  Python deps: numpy pandas scipy scikit-learn matplotlib diff-match-patch caveclient
               cloud-volume python-pptx pypdf
               (install with: pip install --ignore-installed packaging <pkg>)

USAGE
  python run_all.py                 # every stage in order (full reproduction; needs creds)
  python run_all.py --offline       # only offline stages 4-7 (no network/creds; uses cached CSVs)
  python run_all.py --stages 4-7    # a contiguous range (1-indexed)
  python run_all.py --stages 5,7    # specific stages
  python run_all.py --list          # list stages and exit

PROVENANCE
  See ../methodology_provenance.md (§1-13) for the scientific record and
  ../transparency_failure_modes.md for approaches tried, bugs, and retractions.
  Note: the per-script paths are set for this working layout; for a clean-room run, point
  the OUT/HERE constants at the top of each script at your own data directory.
"""
import sys, subprocess, time, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (label, script, one-line description, needs_network)
STAGES = [
    ("tiers",        "mine_tiers.py",                  "naive/designed/learned reps; expert-vs-proto-expert AUC", True),
    ("fullyproof",   "mine_fullyproofread.py",         "categorical label accuracy vs grader ground truth",      True),
    ("separability", "mine_predictive_separability.py","simple-behavior separability + GT-free per-task uncertainty", True),
    ("prospective",  "prospective_flagging.py",        "GT-free error-flagging curve",                           False),
    ("figures",      "make_figures.py",                "core talk figures (handles suppressed)",                 False),
    ("morefigs",     "make_more_figures.py",           "over-complete data-figure pool",                         False),
    ("deck",         "build_deck.py",                  "build berlin_deck_v3.pptx (20 slides)",                  False),
]

def parse_stages(spec):
    """'4-7' or '5,7' -> sorted list of 1-indexed stage numbers."""
    idx = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-"); idx |= set(range(int(a), int(b) + 1))
        elif part:
            idx.add(int(part))
    return sorted(i for i in idx if 1 <= i <= len(STAGES))

def main():
    ap = argparse.ArgumentParser(description="Run the proofreader behavior/competency pipeline.")
    ap.add_argument("--stages", default=None, help="e.g. '4-7' or '5,7' (1-indexed)")
    ap.add_argument("--offline", action="store_true", help="run only offline stages (4-7); no network/creds")
    ap.add_argument("--list", action="store_true", help="list stages and exit")
    a = ap.parse_args()

    if a.list:
        for i, (n, f, d, net) in enumerate(STAGES, 1):
            print(f"{i}  {n:13s} {'[network]' if net else '[offline]'}  {d}")
        return

    selected = list(range(1, len(STAGES) + 1))
    if a.offline:
        selected = [i for i, s in enumerate(STAGES, 1) if not s[3]]
    if a.stages:
        selected = parse_stages(a.stages)

    print(f"[run_all] stages: {selected}", flush=True)
    for i in selected:
        name, script, desc, net = STAGES[i - 1]
        path = HERE / script
        if not path.exists():
            print(f"!! stage {i} ({name}): missing {script}", file=sys.stderr); sys.exit(2)
        print(f"\n=== [{i}/{len(STAGES)}] {name} ({'network' if net else 'offline'}) — {desc} ===", flush=True)
        t0 = time.time()
        rc = subprocess.run([sys.executable, str(path)], cwd=HERE).returncode
        if rc != 0:
            print(f"!! stage {i} ({name}) FAILED (exit {rc}); stopping.", file=sys.stderr); sys.exit(rc)
        print(f"=== [{i}/{len(STAGES)}] {name} done in {time.time() - t0:.0f}s ===", flush=True)
    print("\n[run_all] all requested stages complete.", flush=True)

if __name__ == "__main__":
    main()
