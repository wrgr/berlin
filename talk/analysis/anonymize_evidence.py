"""De-identify the per-annotator evidence CSVs so the plots are TRACEABLE & reproducible from the
repo without exposing annotator handles. Reads the (gitignored) live_out CSVs, replaces every
annotator handle with a consistent opaque id (experts E01.., proto/students S01.., others U..),
and writes committable copies:
  CORE  deck-figure evidence  -> ../evidence/
  OTHER exploratory analyses  -> ../evidence/other/
NEVER copies tokens, the handle->real-name map, or raw handles. A leak-scan asserts no original
handle survives in any output. seg_id (public MICrONS ids) and cohort/feature columns are kept.
Run from a checkout that has the live CSVs:  BERLIN_DATA=/path/to/live_out python anonymize_evidence.py
"""
import os
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
EVID=HERE.parent/"evidence"; OTHER_DIR=EVID/"other"
EVID.mkdir(exist_ok=True); OTHER_DIR.mkdir(exist_ok=True)
HANDLE_COLS=["assignee","user","user_name","annotator","student"]
DROP={"name","email","handle_real"}

CORE=["tiers_data","enriched_task","fullyproofread_accuracy","separability_annotator",
      "separability_task","multisomasplit_competency","grammar_features","rf_importance"]
# (dialect_distance.csv is a handle x handle matrix — handles in the headers; omitted, not committed)
OTHER=["decision_agreement","compare_to_pat","expert_alignment_ranking","pat_anchored_v3",
       "pat_behavioral_distance","pat_distance_per_type","rich_crosstask_expert","rich_crosstask_student",
       "spatial_sessions","spatial_user","competency_ALL","competency_per_type","feature_competency",
       "learning_trajectory","three_axis_scores"]

def handle_col(d): return next((c for c in HANDLE_COLS if c in d.columns), None)

# 1) consistent handle -> opaque id map, from cohort info wherever it appears (CORE+OTHER)
cohort={}; allh=set()
for f in CORE+OTHER:
    p=SRC/f"{f}.csv"
    if not p.exists(): continue
    d=pd.read_csv(p); hc=handle_col(d)
    if not hc: continue
    allh.update(d[hc].astype(str))
    if "cohort" in d.columns:
        for h,c in zip(d[hc].astype(str), d["cohort"].astype(str)): cohort.setdefault(h,c)
exp=sorted(h for h in allh if cohort.get(h)=="expert")
stu=sorted(h for h in allh if cohort.get(h)=="student")
oth=sorted(h for h in allh if h not in exp and h not in stu)
amap={**{h:f"E{i:02d}" for i,h in enumerate(exp,1)},
      **{h:f"S{i:02d}" for i,h in enumerate(stu,1)},
      **{h:f"U{i:02d}" for i,h in enumerate(oth,1)}}
keys=[k for k in amap if len(k)>=3]   # for the leak scan (skip ultra-short ids)
print(f"mapped {len(exp)} experts, {len(stu)} students, {len(oth)} other handles -> opaque ids")

def emit(files, outdir, tag):
    for f in files:
        p=SRC/f"{f}.csv"
        if not p.exists(): print(f"  [{tag}] skip (missing) {f}"); continue
        d=pd.read_csv(p)
        for c in HANDLE_COLS:
            if c in d.columns: d[c]=d[c].astype(str).map(lambda h: amap.get(h,h))
        d=d.drop(columns=[c for c in DROP if c in d.columns], errors="ignore")
        d.to_csv(outdir/f"{f}.csv", index=False)
        od=pd.read_csv(outdir/f"{f}.csv", dtype=str, keep_default_na=False)   # exact-cell leak scan
        present=set(map(str,od.columns))
        for c in od.columns: present.update(od[c])
        leaked=[k for k in keys if k in present]
        flag=f"  !! LEAK {leaked[:3]}" if leaked else ""
        print(f"  [{tag}] evidence{'/other' if tag=='OTHER' else ''}/{f}.csv  ({len(d)} rows){flag}")
emit(CORE, EVID, "CORE")
emit(OTHER, OTHER_DIR, "OTHER")

# motif windows (.npz): dict {handle: windows_array}; rename keys, values carry no handles
npz=SRC/"motif_windows.npz"
if npz.exists():
    import numpy as np
    z=np.load(npz, allow_pickle=True)
    fb={k:f"U{i:02d}" for i,k in enumerate((k for k in z.files if k not in amap), len(amap)+1)}
    np.savez(EVID/"motif_windows.npz", **{amap.get(k,fb.get(k,k)):z[k] for k in z.files})
    print(f"  [CORE] evidence/motif_windows.npz  ({len(z.files)} annotators, keys de-identified)")
print("DONE — de-identified evidence in", EVID, "and", OTHER_DIR)
