"""3D-exploration trajectory features (rich) + trivial baseline scalars, per user.
Reconstructs camera (orientation/position/zoom) sequence from per-patch windows.
"""
import sys, json, re, urllib.parse, math, ast, http.client, collections
from pathlib import Path
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE/"neuvue-client"))
import diff_match_patch as dmpmod
tok=json.loads((HERE/".nv_tokens.json").read_text())
# refresh access token
conn=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
conn.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=conn.getresponse().read().decode()
try: new=json.loads(raw)
except: new=ast.literal_eval(raw)
tok["access_token"]=new.get("access_token",tok["access_token"]); (HERE/".nv_tokens.json").write_text(json.dumps(tok))
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
dmp=dmpmod.diff_match_patch()

TARGETS=["rivlipk1","natalie","phillips","gary","chris","claire","dxenes1","michael","christopher","erika","clara","kitchlm1"]
ANN=re.compile(r'[0-9a-f]{32}|"description"|"tagId"|"annotation"|"pointA"')
QRE=re.compile(r"(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,})")
PRE=re.compile(r"(\d{4,7}(?:\.\d+)?),(\d{4,7}(?:\.\d+)?),(\d{3,6}(?:\.\d+)?)")
ZRE=re.compile(r"(?:crossSectionScale|perspectiveZoom|projectionScale)[^0-9]{0,6}(\d+\.\d+)")
def newwin(patch):
    try: ps=dmp.patch_fromText(str(patch))
    except: return ""
    return urllib.parse.unquote("".join(t for p in ps for op,t in p.diffs if op>=0))
def extract(win):
    out={}
    for m in QRE.finditer(win):
        v=[float(x) for x in m.groups()]
        if all(abs(x)<=1.01 for x in v): out["q"]=np.array(v); break
    m=PRE.search(win)
    if m: out["pos"]=np.array([float(x) for x in m.groups()])
    m=ZRE.search(win)
    if m: out["zoom"]=float(m.group(1))
    if "zoom" not in out and "q" not in out and "pos" not in out:
        fl=re.findall(r"-?\d+\.\d+", win)      # lone float, no rotation/position -> likely a zoom change
        if len(fl)==1:
            try: out["zoom"]=float(fl[0])
            except: pass
    return out
def qang(a,b):
    d=abs(float(np.dot(a/np.linalg.norm(a), b/np.linalg.norm(b)))); d=min(1,d); return math.degrees(2*math.acos(d))
def classify(patch):
    d=urllib.parse.unquote(str(patch))
    if ANN.search(d): return "edit"
    return "nav"

def session_feats(evs):
    # evs: list of (ts, patch) sorted
    Q=[]; P=[]; Z=[]; editZ=[]; navZ=[]; cur={"q":None,"pos":None,"zoom":None}
    rot=pan=zoom=0
    for ts,patch in evs:
        kind=classify(patch); w=newwin(patch); nv=extract(w)
        if "q" in nv: cur["q"]=nv["q"]; rot+=1; Q.append(nv["q"])
        if "pos" in nv: cur["pos"]=nv["pos"]; pan+=1; P.append(nv["pos"])
        if "zoom" in nv: cur["zoom"]=nv["zoom"]; zoom+=1; Z.append(nv["zoom"])
        if kind=="edit" and cur["zoom"] is not None: editZ.append(cur["zoom"])
        elif cur["zoom"] is not None: navZ.append(cur["zoom"])
    f={}
    # trivial
    f["n_rot"]=rot; f["n_pan"]=pan; f["n_zoom"]=zoom
    f["total_rot_deg"]=float(np.sum([qang(Q[i],Q[i+1]) for i in range(len(Q)-1)])) if len(Q)>1 else 0
    f["total_pan"]=float(np.sum([np.linalg.norm(P[i+1]-P[i]) for i in range(len(P)-1)])) if len(P)>1 else 0
    f["zoom_logrange"]=float(np.log((max(Z)+1e-9)/(min(Z)+1e-9))) if len(Z)>1 else 0
    # rich
    if len(Q)>2:
        # viewpoint diversity: mean pairwise angle among sampled orientations
        idx=np.linspace(0,len(Q)-1,min(len(Q),12)).astype(int); qs=[Q[i] for i in idx]
        f["viewpoint_diversity"]=float(np.mean([qang(qs[i],qs[j]) for i in range(len(qs)) for j in range(i+1,len(qs))]))
    else: f["viewpoint_diversity"]=0
    if len(P)>2:
        path=float(np.sum([np.linalg.norm(P[i+1]-P[i]) for i in range(len(P)-1)]))
        net=float(np.linalg.norm(P[-1]-P[0]))
        f["pan_directedness"]=net/path if path>0 else 0   # 1=follow path, ~0=scattered
    else: f["pan_directedness"]=np.nan
    f["zoom_at_edit_ratio"]=float(np.median(editZ)/ (np.median(navZ)+1e-9)) if editZ and navZ else np.nan
    return f

DSNS=["singleSomaCleanUp","neuronOtherBodies","axonOnAxon","axonOnDendrite","axonOnDendriteV3",
      "multiSomaId","functionalCellClean","dendExtensionLevel3","dendExtensionLevel2","dendExtensionLevel4",
      "axonExtension","reverseExtension","neuronScreening","agentsExpert","somaSomaReview","axonOnDendriteV2"]
rows=[]
for ui,u in enumerate(TARGETS):
    sess=[]; ev=0
    for ns in DSNS:
        if ev>=2500: break
        try:
            tk=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":{"$in":["closed","errored"]}},
                            select=["assignee"], convert_states_to_json=False, limit=40, pageSize=40)
        except Exception: continue
        if tk.empty: continue
        ids=[str(x) for x in tk.reset_index(names="tid")["tid"]]
        for i in range(0,len(ids),20):
            try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
            except: continue
            for did,row in ds.iterrows():
                st=row["differ_stack"]
                if not isinstance(st,list) or len(st)<3: continue
                evs=[(e.get("timestamp",0),e.get("patch","")) for e in st if isinstance(e,dict)]
                evs.sort(key=lambda x:x[0])
                sess.append(session_feats(evs)); ev+=len(evs)
            if ev>=2500: break
    if not sess: print(f"{u}: no sessions",flush=True); continue
    S=pd.DataFrame(sess)
    agg={"assignee":u,"n_sessions":len(S),"n_events":ev}
    for c in S.columns: agg[c]=round(float(np.nanmean(S[c])),3)
    rows.append(agg); print(f"[{ui+1}/{len(TARGETS)}] {u}: sessions={len(S)} events={ev}",flush=True)

F=pd.DataFrame(rows)
# attach competency labels
lab=pd.read_csv(OUT/"competency_labels.csv")[["assignee","decision_vs_Pat","durability"]]
F=F.merge(lab,on="assignee",how="left")
F.to_csv(OUT/"features_3d.csv",index=False)
print("\n=== 3D + trivial features per user ===",flush=True)
trivial=["n_rot","n_pan","n_zoom","total_rot_deg","total_pan","zoom_logrange"]
rich=["viewpoint_diversity","pan_directedness","zoom_at_edit_ratio"]
print(F[["assignee","n_sessions"]+trivial+rich+["decision_vs_Pat","durability"]].to_string(index=False),flush=True)
print("\nsaved features_3d.csv",flush=True)
