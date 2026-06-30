"""Derived proofreading kinematics (temporal/sequence; no reconstruction needed).

Per session: treat segment-edit events as 'clicks'. Compute inter-click time,
navigation effort before each click, tempo, think-time. Aggregate per user and
per task type, and quantify how much users vary.
"""
import sys, json, urllib.parse, re, collections
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE/"neuvue-client")); pd.set_option("display.width",220); pd.set_option("display.max_columns",30)
tok=json.loads((HERE/".nv_tokens.json").read_text())
from neuvueclient import NeuvueQueue
c=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok.get("refresh_token",""))

ANN={"description","tagId","tagIds","tags","annotation","annotations","annotationColor","point","pointA","pointB","parentId"}
NAV={"position","voxelCoordinates","projectionOrientation","crossSectionOrientation","projectionScale","crossSectionScale","zoomFactor","perspectiveOrientation","perspectiveZoom","pose"}
PATH={"hasPath","pathFinder","pathObject","annotationPath","source","target"}
def label(patch):
    d=urllib.parse.unquote(str(patch)); add=rm=hexid=dec=0
    for ln in d.split("\n"):
        if ln[:1] in ("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); add,rm=(add+n,rm) if ln[:1]=="+" else (add,rm+n)
            if re.search(r"[0-9a-f]{32,40}",ln): hexid+=1
            if re.search(r"-?\d+\.\d+",ln): dec+=1
    kset=set(re.findall(r'"([A-Za-z_]\w*)"\s*:',d))
    if add or rm: return "segment"
    if (kset&ANN) or hexid or ({"type","id"}<=kset): return "annotate"
    if kset&PATH: return "trace"
    if (kset&NAV) or (dec and not kset): return "navigate"
    body=re.sub(r"@@[^@]*@@","",d); return "navigate" if len(re.sub(r"[^A-Za-z]","",body))<=4 else "other"

def fetch(ns, max_tasks=2500, cap=8000, chunk=20):
    tk=c.get_tasks(sieve={"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee"],
                   convert_states_to_json=False, limit=max_tasks, pageSize=1000)
    if tk.empty: return []
    tk=tk.reset_index(names="task_id"); tk["task_id"]=tk["task_id"].astype(str)
    a={r.task_id:r.assignee for r in tk.itertuples()}; ids=list(a); rows=[]
    for i in range(0,len(ids),chunk):
        try: ds=c.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+chunk]},"active":True}, pageSize=1000)
        except Exception: continue
        for did,row in ds.iterrows():
            st=row["differ_stack"]
            if not isinstance(st,list): continue
            for o,ev in enumerate(st):
                if not isinstance(ev,dict): continue
                rows.append({"ns":ns,"assignee":a.get(str(row["task_id"])),"sid":str(did),"order":o,
                             "ts":ev.get("timestamp"),"label":label(ev.get("patch",""))})
        if len(rows)>=cap: break
    return rows

rows=[]
for ns in ["multiSomaSplit","somaSomaSplit","somaSomaReview","fullyProofread"]:
    r=fetch(ns); print(f"{ns:16s} events={len(r)} sessions={len({x['sid'] for x in r})} users={len({x['assignee'] for x in r})}"); rows+=r
ev=pd.DataFrame(rows); ev["t"]=pd.to_numeric(ev["ts"],errors="coerce")/1000.0
ev=ev.dropna(subset=["t"]).sort_values(["sid","t"])

FCOLS=["n_edits","span_s","inter_click_s","nav_before_click","frac_nav","edits_per_min","think_to_first_click_s","click_burstiness"]
def feats(g):
    t=g["t"].values; lab=g["label"].values; n=len(g)
    is_e=np.array([x=="segment" for x in lab]); is_n=np.array([x=="navigate" for x in lab])
    span=float(t[-1]-t[0]) if n>1 else 0.0; ei=np.where(is_e)[0]
    f={k:np.nan for k in FCOLS}
    f["n_edits"]=int(is_e.sum()); f["span_s"]=span; f["frac_nav"]=float(is_n.mean()) if n else np.nan
    if span>5: f["edits_per_min"]=is_e.sum()/(span/60.0)
    if len(ei)>=2:
        et=t[ei]; inter=np.diff(et); f["inter_click_s"]=float(np.median(inter))
        f["nav_before_click"]=float(np.mean([is_n[ei[k]+1:ei[k+1]].sum() for k in range(len(ei)-1)]))
        f["click_burstiness"]=float(np.std(inter)/np.mean(inter)) if np.mean(inter)>0 else np.nan
    if len(ei)>=1: f["think_to_first_click_s"]=float(t[ei[0]]-t[0])
    return pd.Series(f, index=FCOLS)

S=ev.groupby(["ns","assignee","sid"], sort=False).apply(feats, include_groups=False).reset_index()
print(f"\nsessions with features: {len(S)} | users: {S['assignee'].nunique()}")

# per-user (>=3 sessions) median features
cnt=S.groupby("assignee")["sid"].count(); keep=cnt[cnt>=3].index
U=S[S["assignee"].isin(keep)].groupby("assignee")[FCOLS].median().round(2)
U["n_sessions"]=cnt[keep]
U=U.sort_values("n_sessions",ascending=False)
print(f"\n==== PER-USER median features (users with >=3 sessions: {len(U)}) ====")
print(U.head(16).to_string())
U.to_csv(OUT/"user_features.csv")

# how much do users vary? cross-user CV per feature
print("\n==== cross-user variation (median feature across users) ====")
var=pd.DataFrame({"median":U[FCOLS].median().round(2),"p10":U[FCOLS].quantile(.1).round(2),
                  "p90":U[FCOLS].quantile(.9).round(2)})
var["spread_p90/p10"]=(var["p90"]/var["p10"].replace(0,np.nan)).round(1)
print(var.to_string())
var.to_csv(OUT/"feature_variation.csv")

# task-type separation
print("\n==== feature medians by task type ====")
print(S.groupby("ns")[FCOLS].median().round(2).to_string())
S.groupby("ns")[FCOLS].median().to_csv(OUT/"feature_by_namespace.csv")
S.to_csv(OUT/"session_features.csv", index=False)

# figure: users in (inter_click_s, nav_before_click) space
sub=U.dropna(subset=["inter_click_s","nav_before_click"])
plt.figure(figsize=(7,5))
plt.scatter(sub["inter_click_s"],sub["nav_before_click"],s=sub["n_sessions"]*3,alpha=0.6,color="purple")
for u,r in sub.iterrows(): plt.annotate(u,(r["inter_click_s"],r["nav_before_click"]),fontsize=7,alpha=0.7)
plt.xlabel("median time between clicks (s)"); plt.ylabel("nav events before each click")
plt.title("Proofreader kinematics (size = # sessions)"); plt.tight_layout(); plt.savefig(OUT/"user_kinematics.png",dpi=130); plt.close()
print("\nsaved user_features.csv, feature_variation.csv, session_features.csv, user_kinematics.png")
