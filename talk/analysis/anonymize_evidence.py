"""De-identify the per-annotator evidence CSVs so the plots are TRACEABLE & reproducible from the
repo without exposing annotator handles. Reads the (gitignored) live_out CSVs, replaces every
annotator handle with a consistent opaque id (experts E01.., proto/students S01..), and writes
committable copies to ../evidence/. NEVER copies tokens, the handle->real-name map, or raw handles.
seg_id (public MICrONS segment ids) and cohort/feature columns are kept for reproducibility.
Run from a checkout that has the live CSVs:  BERLIN_DATA=/path/to/live_out python anonymize_evidence.py
"""
import os
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
OUT=HERE.parent/"evidence"; OUT.mkdir(exist_ok=True)
FILES=["tiers_data","enriched_task","fullyproofread_accuracy","separability_annotator",
       "separability_task","multisomasplit_competency","grammar_features","rf_importance"]
HANDLE_COLS=["assignee","user","user_name","annotator"]

# 1) build a consistent handle -> opaque id map from cohort info wherever it appears
cohort={}
for f in FILES:
    p=SRC/f"{f}.csv"
    if not p.exists(): continue
    d=pd.read_csv(p)
    hc=next((c for c in HANDLE_COLS if c in d.columns), None)
    if hc and "cohort" in d.columns:
        for h,c in zip(d[hc].astype(str), d["cohort"].astype(str)):
            cohort.setdefault(h, c)
allh=set()
for f in FILES:
    p=SRC/f"{f}.csv"
    if not p.exists(): continue
    d=pd.read_csv(p); hc=next((c for c in HANDLE_COLS if c in d.columns), None)
    if hc: allh.update(d[hc].astype(str).tolist())
exp=sorted(h for h in allh if cohort.get(h)=="expert")
stu=sorted(h for h in allh if cohort.get(h)=="student")
oth=sorted(h for h in allh if h not in exp and h not in stu)
amap={}
amap.update({h:f"E{i:02d}" for i,h in enumerate(exp,1)})
amap.update({h:f"S{i:02d}" for i,h in enumerate(stu,1)})
amap.update({h:f"U{i:02d}" for i,h in enumerate(oth,1)})
print(f"mapped {len(exp)} experts, {len(stu)} students, {len(oth)} other handles -> opaque ids")

# 2) rewrite each CSV with handles replaced; drop any stray name columns
DROP={"user","user_name","name","email","handle_real"}
for f in FILES:
    p=SRC/f"{f}.csv"
    if not p.exists(): print(f"  skip (missing) {f}"); continue
    d=pd.read_csv(p)
    for c in HANDLE_COLS:
        if c in d.columns: d[c]=d[c].astype(str).map(lambda h: amap.get(h,h))
    d=d.drop(columns=[c for c in DROP if c in d.columns], errors="ignore")
    d.to_csv(OUT/f"{f}.csv", index=False)
    print(f"  wrote evidence/{f}.csv  ({len(d)} rows, {len(d.columns)} cols)")

# motif windows (.npz): dict {handle: windows_array}; rename keys, values carry no handles
npz=SRC/"motif_windows.npz"
if npz.exists():
    import numpy as np
    z=np.load(npz, allow_pickle=True)
    fb={k:f"U{i:02d}" for i,k in enumerate((k for k in z.files if k not in amap), len(amap)+1)}
    np.savez(OUT/"motif_windows.npz", **{amap.get(k,fb.get(k,k)):z[k] for k in z.files})
    print(f"  wrote evidence/motif_windows.npz  ({len(z.files)} annotators, keys de-identified)")
print("DONE — de-identified evidence in", OUT)
