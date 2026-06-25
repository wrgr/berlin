"""Re-mine fullyProofread with a RICHER GT-free per-task representation -> enriched_task.csv.
Per closed fullyProofread task: assignee/cohort, seg_id, duration, n_pts, accuracy & error vs the
grader GT (patProofread points), AND the point-category MIX (spine/nucleus/dendrite/axon/soma
fractions, from the annotator's own annotations — GT-free). Feeds explore_task_risk_prediction.py
(which finds GT-free task RISK is predictable ~0.76 on held-out cells; per-person competence is not).
Network stage: needs .nv_tokens.json + neuvue-client alongside this script."""
import sys, json, ast, http.client, difflib
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; OUT.mkdir(exist_ok=True); sys.path.insert(0,str(HERE/"neuvue-client"))
tok=json.loads((HERE/".nv_tokens.json").read_text())
c=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
c.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=c.getresponse().read().decode()
try: tok["access_token"]=json.loads(raw)["access_token"]
except: tok["access_token"]=ast.literal_eval(raw)["access_token"]
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io",token=True,access_token=tok["access_token"],refresh_token=tok["refresh_token"])
CATEGORIES=["spine","nucleus","dendrite","axon","soma"]; GRADERS=["rivlipk1","kitchlm1"]
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
def dur_of(r):
    for k in ["duration","duration_s","time_taken"]:
        v=r.get(k) if hasattr(r,"get") else None
        try:
            if v is not None and not pd.isna(v): return float(v)
        except Exception: pass
    return np.nan
GT=[]
for g in GRADERS:
    try: tk=nq.get_tasks(sieve={"assignee":g,"namespace":"patProofread","status":"closed"}, select=["seg_id","ng_state"], convert_states_to_json=False, limit=600, pageSize=600)
    except Exception: continue
    if tk.empty: continue
    for _,r in tk.reset_index().iterrows(): GT+=parse_pts(r.get("ng_state"),r.get("seg_id"))
gt=set(GT); print("GT pts",len(gt),flush=True)
TASK=[]
for grp,users in [("expert",EXPERTS),("student",STUDENTS)]:
  for u in users:
    try: tk=nq.get_tasks(sieve={"assignee":u,"namespace":"fullyProofread","status":"closed"}, select=["seg_id","ng_state","duration"], convert_states_to_json=False, limit=300, pageSize=300)
    except Exception: continue
    if tk.empty: continue
    for _,r in tk.reset_index().iterrows():
        seg=r.get("seg_id"); pts=parse_pts(r.get("ng_state"),seg)
        if not pts: continue
        m=sum(1 for t in pts if t in gt); cats=Counter(l for _,l,_ in pts)
        row={"assignee":u,"cohort":grp,"promoted":int(u in PROMOTED),"seg_id":str(seg),"n_pts":len(pts),
             "acc":m/len(pts),"err":int(m/len(pts)<0.999),"dur":dur_of(r)}
        for cc in CATEGORIES: row["f_"+cc]=cats[cc]/len(pts)
        TASK.append(row)
T=pd.DataFrame(TASK); T.to_csv(OUT/"enriched_task.csv",index=False)
print("saved enriched_task.csv: tasks=%d  unique seg_ids=%d"%(len(T),T.seg_id.nunique()),flush=True)
