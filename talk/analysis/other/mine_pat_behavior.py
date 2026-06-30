"""Per (user, task-type) behavioral signature -> distance to Pat (the proficiency model)."""
import sys, json, ast, http.client, re, urllib.parse, collections
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
ANN={"description","tagId","tagIds","tags","annotation","annotations","point","pointA","pointB","parentId"}
NAV={"position","voxelCoordinates","projectionOrientation","crossSectionOrientation","projectionScale","crossSectionScale","zoomFactor","perspectiveOrientation","perspectiveZoom","pose"}
def lab(patch):
    d=urllib.parse.unquote(str(patch)); add=rm=hexid=0
    for ln in d.split("\n"):
        if ln[:1] in ("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); add+=n if ln[:1]=="+" else 0; rm+=n if ln[:1]=="-" else 0
            if re.search(r"[0-9a-f]{32,40}",ln): hexid+=1
    kset=set(re.findall(r'"([A-Za-z_]\w*)"\s*:',d))
    if add or rm: return "segment"
    if (kset&ANN) or hexid: return "annotate"
    if (kset&NAV): return "navigate"
    body=re.sub(r"@@[^@]*@@","",d); return "navigate" if len(re.sub(r"[^A-Za-z]","",body))<=4 else "other"
TYPES=["multiSomaId","singleSomaCleanUp","neuronOtherBodies","axonOnAxon","axonOnDendriteV3","axonOnDendrite"]
M=pd.read_csv(OUT/"completed_per_type.csv",index_col=0)
TOK=["navigate","segment","annotate","other"]; idx={t:i for i,t in enumerate(TOK)}
def signature(sessions):
    allb=[b for s in sessions for (b,t) in s]; n=len(allb)
    if n<60: return None
    mix=np.array([allb.count(t)/n for t in TOK])
    Mt=np.zeros((4,4))
    for s in sessions:
        b=[x for x,_ in s]
        for a,cc in zip(b,b[1:]):
            if a in idx and cc in idx: Mt[idx[a],idx[cc]]+=1
    r=Mt.sum(1,keepdims=True); T=np.divide(Mt,r,out=np.zeros_like(Mt),where=r>0).flatten()
    dts=[]
    for s in sessions:
        ts=sorted(t for _,t in s); dts+=[b-a for a,b in zip(ts,ts[1:]) if 0.05<b-a<120]
    tempo=np.log(np.median(dts)) if dts else 0.0
    return np.concatenate([mix,T,[tempo]])
def user_type_sig(u,ns):
    try: tk=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee"], convert_states_to_json=False, limit=60, pageSize=60)
    except Exception: return None
    if tk.empty: return None
    ids=[str(x) for x in tk.reset_index(names="tid")["tid"]]; sessions=[]
    for i in range(0,len(ids),20):
        try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except: continue
        for did,row in ds.iterrows():
            st=row["differ_stack"]
            if isinstance(st,list) and len(st)>=3:
                ev=[(lab(e.get("patch","")), (e.get("timestamp",0) or 0)/1000.0) for e in st if isinstance(e,dict)]
                if ev: sessions.append(ev)
    return signature(sessions)
rows=[]
for ns in TYPES:
    users=set(M.index[(M[ns]>=20)]) ; users={u for u in users if not str(u).startswith("unassigned")}; users.add("rivlipk1")
    sigs={}
    for u in users:
        s=user_type_sig(u,ns)
        if s is not None: sigs[u]=s
    print(f"{ns}: {len(sigs)} user-sigs (Pat {'OK' if 'rivlipk1' in sigs else 'MISSING'})",flush=True)
    if "rivlipk1" not in sigs or len(sigs)<3: continue
    X=np.array([sigs[u] for u in sigs]); mu,sd=X.mean(0),X.std(0); sd[sd==0]=1
    Z={u:(sigs[u]-mu)/sd for u in sigs}; pv=Z["rivlipk1"]
    for u in sigs:
        if u!="rivlipk1": rows.append({"user":u,"type":ns,"pat_dist":round(float(np.linalg.norm(Z[u]-pv)),2)})
D=pd.DataFrame(rows); mat=D.pivot(index="user",columns="type",values="pat_dist")
mat.to_csv(OUT/"pat_distance_per_type.csv")
print("\n=== behavioral distance to Pat per task type (lower=more Pat-like) ===",flush=True)
print(mat.round(1).to_string(),flush=True)
C=pd.read_csv(OUT/"competency_ALL.csv",index_col=0)
print("\n=== validation: does Pat-likeness track v18xx competency? (Spearman per type) ===",flush=True)
for ns in TYPES:
    if ns in mat.columns and ns in C.columns:
        j=pd.DataFrame({"d":mat[ns],"c":C[ns]}).dropna()
        if len(j)>=5:
            rho,p=stats.spearmanr(j["d"],j["c"]); print(f"  {ns:18s} n={len(j)} rho={rho:+.2f} p={p:.2f} (neg=Pat-like->correct)",flush=True)
