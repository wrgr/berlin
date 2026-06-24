"""Item 1 — behavior -> competence separability, the right way, + the prospective GT-free framing.
Target WITH variance = fullyProofread label accuracy (the bad tail), not the ceiling-clustered split task.
- Per-annotator SIMPLE (telemetry-free) behavior: duration stats, throughput, thoroughness.
- Separability good-vs-bad with LOO confusion (FP AND FN both reported).
- PROSPECTIVE / GT-FREE: per-task behavioral anomaly (slow-for-THIS-person, atypical thoroughness)
  flags a likely-erroneous task WITHOUT ground truth = 'subconscious uncertainty'
  (tacit knowledge; language of surgery; JIGSAWS).
- Checks whether the variance-rich (bad-tail / non-promoted) students have dense telemetry anywhere.
"""
import sys, json, ast, http.client, collections, difflib, math
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; sys.path.insert(0,str(HERE/"neuvue-client"))
tok=json.loads((HERE/".nv_tokens.json").read_text())
c=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
c.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=c.getresponse().read().decode()
try: tok["access_token"]=json.loads(raw)["access_token"]
except: tok["access_token"]=ast.literal_eval(raw)["access_token"]
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
CATEGORIES=["spine","nucleus","dendrite","axon","soma"]; GRADERS=["rivlipk1","kitchlm1"]
EXPERTS=["chris","christopher","claire","erika","gary","michael","natalie","phillips"]
STUDENTS=["aashi","clara","donovan9","dylan","emma","emily","joey","jonas","katie","krutal","luzhou","mia","oji","rachel","rupa","sarah","sean_sebastian","shruthi","taylor","titus","vivia","stella","maggie","makayla","maryam","tina","luke","trystan","cindy"]
PROMOTED={"dylan","vivia","taylor","clara","rachel","shruthi","sarah","lydia"}
MINTASKS=10; BAD=0.90
def catof(name,desc):
    for s in [str(name).lower(),str(desc).lower()]:
        m=difflib.get_close_matches(s,CATEGORIES,n=1,cutoff=0.6)
        if m: return m[0]
        for cc in CATEGORIES:
            if cc in s: return cc
    return None
def parse_pts(ngval,seg):
    out=[]
    try: v=json.loads(ngval) if isinstance(ngval,str) else ngval
    except Exception: return out
    if isinstance(v,dict) and "value" in v and isinstance(v["value"],dict): v=v["value"]
    layers=v.get("layers",[]) if isinstance(v,dict) else []
    if isinstance(layers,dict): layers=list(layers.values())
    for L in layers:
        if not isinstance(L,dict): continue
        nm=L.get("name",""); anns=L.get("annotations",[])
        if not isinstance(anns,list): continue
        for a in anns:
            if not isinstance(a,dict): continue
            pt=a.get("point") or a.get("pointA") or a.get("center")
            if not pt or len(pt)<3: continue
            lb=catof(nm,a.get("description",""))
            if not lb: continue
            out.append((str(seg),lb,(int(round(float(pt[0]))),int(round(float(pt[1]))),int(round(float(pt[2]))))))
    return out
# ---- GT ----
GT=[]
for g in GRADERS:
    try: tk=nq.get_tasks(sieve={"assignee":g,"namespace":"patProofread","status":"closed"}, select=["seg_id","ng_state"], convert_states_to_json=False, limit=600, pageSize=600)
    except Exception: continue
    if tk.empty: continue
    for _,r in tk.reset_index().iterrows(): GT+=parse_pts(r.get("ng_state"),r.get("seg_id"))
gt_strict=set(GT)
print(f"GT points: {len(GT)}",flush=True)
def dur_of(r):
    for k in ["duration","duration_s","time_taken"]:
        v=r.get(k) if hasattr(r,"get") else None
        try:
            if v is not None and not pd.isna(v): return float(v)
        except Exception: pass
    return np.nan
# ---- fullyProofread per task + per annotator ----
TASK=[]; ANN=[]
for grp,users in [("expert",EXPERTS),("student",STUDENTS)]:
  for u in users:
    try: tk=nq.get_tasks(sieve={"assignee":u,"namespace":"fullyProofread","status":"closed"}, select=["seg_id","ng_state","duration","metadata"], convert_states_to_json=False, limit=300, pageSize=300)
    except Exception: continue
    if tk.empty: continue
    cols=set(tk.columns); tk=tk.reset_index()
    tm=0; tp=0; durs=[]; npts=[]
    for _,r in tk.iterrows():
        seg=r.get("seg_id"); pts=parse_pts(r.get("ng_state"),seg)
        if not pts: continue
        m=sum(1 for t in pts if t in gt_strict); a=m/len(pts); d=dur_of(r)
        TASK.append({"assignee":u,"cohort":grp,"promoted":int(u in PROMOTED),"n_pts":len(pts),"acc":a,"err":int(a<0.999),"dur":d})
        tm+=m; tp+=len(pts); durs.append(d); npts.append(len(pts))
    if len(npts)>=MINTASKS:
        dd=np.array([x for x in durs if x==x])
        ANN.append({"assignee":u,"cohort":grp,"promoted":int(u in PROMOTED),"n_tasks":len(npts),
            "acc":tm/tp,"bad":int((tm/tp)<BAD),
            "mean_dur":float(np.nanmean(durs)) if len(dd) else np.nan,
            "std_dur":float(np.nanstd(durs)) if len(dd) else np.nan,
            "cv_dur":float(np.nanstd(durs)/np.nanmean(durs)) if len(dd) and np.nanmean(durs) else np.nan,
            "mean_pts":float(np.mean(npts)),"std_pts":float(np.std(npts)),
            "dur_per_pt":float(np.nanmean(durs)/np.mean(npts)) if len(dd) and np.mean(npts) else np.nan})
A=pd.DataFrame(ANN).sort_values("acc"); T=pd.DataFrame(TASK)
A.to_csv(OUT/"separability_annotator.csv",index=False); T.to_csv(OUT/"separability_task.csv",index=False)
print(f"\n=== per-annotator (n={len(A)}, MINTASKS={MINTASKS}); bad(acc<{BAD}): {A.bad.sum()} ===",flush=True)
print(A.round(3).to_string(index=False),flush=True)
# ---- (A) univariate separability of SIMPLE features vs accuracy ----
print("\n=== simple-feature separability vs fullyProofread accuracy (Spearman) ===",flush=True)
feats=["mean_dur","std_dur","cv_dur","mean_pts","std_pts","dur_per_pt","n_tasks"]
for f in feats:
    d=A[[f,"acc"]].dropna()
    if len(d)>=8 and d[f].std()>0:
        rho,p=stats.spearmanr(d[f],d["acc"]); print(f"  {f:11s} rho={rho:+.2f} p={p:.2f} {'*' if p<0.05 else ''}",flush=True)
# ---- good/bad classifier with LOO confusion (FP & FN) ----
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import roc_auc_score, confusion_matrix
Xc=A[feats].fillna(A[feats].median()); y=A["bad"].values
if y.sum()>=3 and (len(y)-y.sum())>=3:
    Xs=StandardScaler().fit_transform(Xc); pred=np.zeros(len(y)); proba=np.zeros(len(y))
    for tr,te in LeaveOneOut().split(Xs):
        clf=LogisticRegression(max_iter=1000,class_weight="balanced").fit(Xs[tr],y[tr])
        pred[te]=clf.predict(Xs[te]); proba[te]=clf.predict_proba(Xs[te])[:,1]
    cm=confusion_matrix(y,pred)
    print(f"\n=== LOO good/bad from SIMPLE behavior (bad=positive) AUC={roc_auc_score(y,proba):.2f} ===",flush=True)
    print("confusion [rows=true good/bad, cols=pred good/bad]:\n",cm,flush=True)
    fp=A[(y==0)&(pred==1)]["assignee"].tolist(); fn=A[(y==1)&(pred==0)]["assignee"].tolist()
    print(f"FALSE POSITIVES (flagged risky but actually good): {fp}",flush=True)
    print(f"FALSE NEGATIVES (missed — predicted good but actually bad): {fn}",flush=True)
else:
    print("\n[good/bad classifier] too few in a class",flush=True)
# ---- (B) PROSPECTIVE / GT-FREE per-task uncertainty: behavior anomaly -> task error ----
print("\n=== prospective GT-free signal: per-task behavioral anomaly -> error (no GT used for the feature) ===",flush=True)
T2=T.dropna(subset=["dur"]).copy()
T2=T2[T2.groupby("assignee")["assignee"].transform("size")>=MINTASKS]
# within-annotator z-scores (a task slow/odd FOR THIS PERSON)
T2["dur_z"]=T2.groupby("assignee")["dur"].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
T2["pts_z"]=T2.groupby("assignee")["n_pts"].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
print(f"tasks={len(T2)}, error base-rate={T2.err.mean():.2f}",flush=True)
for f in ["dur","dur_z","pts_z","n_pts"]:
    d=T2[[f,"err"]].dropna()
    if d["err"].nunique()>1 and d[f].std()>0:
        try: au=roc_auc_score(d["err"],d[f]) if d[f].corr(d["err"])>=0 else roc_auc_score(d["err"],-d[f])
        except Exception: au=float("nan")
        rho,p=stats.spearmanr(d[f],d["err"]); print(f"  {f:7s} -> task error: AUC~{au:.2f}  rho={rho:+.2f} p={p:.3f}",flush=True)
# pooled logistic dur_z+pts_z -> err
dd=T2.dropna(subset=["dur_z","pts_z"])
if dd["err"].nunique()>1:
    Xs=StandardScaler().fit_transform(dd[["dur_z","pts_z"]]); yy=dd["err"].values
    pr=np.zeros(len(yy))
    from sklearn.model_selection import StratifiedKFold
    for tr,te in StratifiedKFold(5,shuffle=True,random_state=0).split(Xs,yy):
        pr[te]=LogisticRegression(max_iter=1000,class_weight="balanced").fit(Xs[tr],yy[tr]).predict_proba(Xs[te])[:,1]
    print(f"  pooled (dur_z+pts_z) CV AUC -> task error = {roc_auc_score(yy,pr):.2f}",flush=True)
# ---- dense-telemetry availability for variance-rich students ----
print("\n=== dense-telemetry availability (variance-rich / bad-tail students) ===",flush=True)
DENSE=["multiSomaId","dendExtensionLevel3","dendExtensionLevel2","axonExtension","singleSomaCleanUp","neuronOtherBodies","functionalCellClean"]
CHECK=["maggie","donovan9","emily","gary","michael","cindy","joey","mia","luke","aashi","titus","jonas"]
for u in CHECK:
    hits=[]
    for ns in DENSE:
        try: t=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":"closed"}, select=["seg_id"], convert_states_to_json=False, limit=60, pageSize=60)
        except Exception: continue
        if not t.empty:
            ids=[str(x) for x in t.reset_index(names="i")["i"][:20]]; ds_ev=0
            try:
                ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids},"active":True}, pageSize=400)
                ds_ev=int(sum(len(s) for s in ds["differ_stack"] if isinstance(s,list)))
            except Exception: pass
            hits.append(f"{ns}={len(t)}tk/{ds_ev}ev")
    print(f"  {u:14s}: {', '.join(hits) if hits else 'none'}",flush=True)
print("\nsaved separability_annotator.csv, separability_task.csv",flush=True)
