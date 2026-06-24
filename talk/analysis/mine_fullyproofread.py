"""fullyProofread per-annotator label accuracy vs patProofread GT (graders rivlipk1,kitchlm1).
Replicates the notebook metric (exact match on seg_id,label,position) AND a proximity-relaxed
variant (same label within radius), because exact float-position match can be degenerate.
A categorical label-accuracy target -> potentially more discriminating than the multiSomaSplit
one-point distance (which is heavily clustered).
"""
import sys, json, ast, http.client, collections, difflib
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
CATEGORIES=["spine","nucleus","dendrite","axon","soma"]
GRADERS=["rivlipk1","kitchlm1"]
EXPERTS=["chris","christopher","claire","erika","gary","michael","natalie","phillips"]
STUDENTS=["aashi","clara","donovan9","dylan","emma","emily","joey","jonas","katie","krutal","luzhou","mia","oji","rachel","rupa","sarah","sean_sebastian","shruthi","taylor","titus","vivia","stella","maggie","makayla","maryam","tina","luke","trystan","cindy"]
PROMOTED={"dylan","vivia","taylor","clara","rachel","shruthi","sarah","lydia"}
def catof(name,desc):
    for s in [str(name).lower(),str(desc).lower()]:
        m=difflib.get_close_matches(s,CATEGORIES,n=1,cutoff=0.6)
        if m: return m[0]
        for cc in CATEGORIES:
            if cc in s: return cc
    return None
def parse_pts(ngval, seg):
    """return list of (seg_id, label, (x,y,z)) from an ng_state value dict."""
    out=[]
    try:
        v=json.loads(ngval) if isinstance(ngval,str) else ngval
    except Exception:
        return out
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
def pull(users):
    rec={}
    for u in users:
        try:
            tk=nq.get_tasks(sieve={"assignee":u,"namespace":"fullyProofread","status":"closed"}, select=["seg_id","ng_state"], convert_states_to_json=False, limit=300, pageSize=300)
        except Exception as e:
            print(f"{u}: err {e}",flush=True); continue
        if tk.empty: print(f"{u}: 0 fullyProofread",flush=True); continue
        pts=[]
        for _,r in tk.reset_index().iterrows():
            seg=r.get("seg_id"); pts+=parse_pts(r.get("ng_state"),seg)
        rec[u]=pts; print(f"{u}: {len(tk)} tasks -> {len(pts)} labeled pts",flush=True)
    return rec
# ground truth from graders on patProofread
GT=[]
for g in GRADERS:
    try:
        tk=nq.get_tasks(sieve={"assignee":g,"namespace":"patProofread","status":"closed"}, select=["seg_id","ng_state"], convert_states_to_json=False, limit=600, pageSize=600)
    except Exception as e:
        print(f"GT {g}: err {e}",flush=True); continue
    if tk.empty: print(f"GT {g}: 0 patProofread",flush=True); continue
    for _,r in tk.reset_index().iterrows(): GT+=parse_pts(r.get("ng_state"),r.get("seg_id"))
print(f"\nGT labeled points: {len(GT)}",flush=True)
gt_strict=set(GT)
gt_by_seglab=collections.defaultdict(list)
for seg,lb,pos in GT: gt_by_seglab[(seg,lb)].append(np.array(pos))
def score(pts):
    if not pts: return None
    strict=sum(1 for t in pts if t in gt_strict)
    relax=0
    for seg,lb,pos in pts:
        cand=gt_by_seglab.get((seg,lb),[])
        if cand and min(np.linalg.norm(np.array(pos)-c) for c in cand)<=50: relax+=1  # ~50 vx
    return {"n_pts":len(pts),"strict":strict,"relax":relax,"acc_strict":strict/len(pts),"acc_relax":relax/len(pts)}
rows=[]
for grp,users in [("expert",EXPERTS),("student",STUDENTS)]:
    rec=pull(users)
    for u,pts in rec.items():
        sc=score(pts)
        if sc: sc.update({"assignee":u,"cohort":grp,"promoted":int(u in PROMOTED)}); rows.append(sc)
A=pd.DataFrame(rows).sort_values("acc_relax",ascending=False)
A.to_csv(OUT/"fullyproofread_accuracy.csv",index=False)
print("\n=== fullyProofread per-annotator accuracy ===",flush=True)
print(A.to_string(index=False),flush=True)
if len(A):
    e=A[A.cohort=="expert"]["acc_relax"]; s=A[A.cohort=="student"]["acc_relax"]
    print(f"\nrelaxed acc: expert median={e.median():.2f} (n={len(e)}), student median={s.median():.2f} (n={len(s)})",flush=True)
    if len(e)>=3 and len(s)>=3:
        print(f"Mann-Whitney p={stats.mannwhitneyu(e,s,alternative='two-sided')[1]:.3f}",flush=True)
    print(f"strict-match total: {A['strict'].sum()} / {A['n_pts'].sum()} pts (if ~0, positions are free-placed -> use relaxed)",flush=True)
