"""Parallel thread: alignment-robust / motif-level behavioral features vs competency.
Tests whether richer, order-tolerant features correlate better than simple proportions.
"""
import sys, json, ast, http.client, re, urllib.parse, collections, math
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
def lab(p):
    d=urllib.parse.unquote(str(p)); add=rm=hexid=0
    for ln in d.split("\n"):
        if ln[:1] in ("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); add+=n if ln[:1]=="+" else 0; rm+=n if ln[:1]=="-" else 0
            if re.search(r"[0-9a-f]{32,40}",ln): hexid+=1
    k=set(re.findall(r'"([A-Za-z_]\w*)"\s*:',d))
    if add or rm: return "S"
    if (k&ANN) or hexid: return "A"
    if (k&NAV): return "N"
    b=re.sub(r"@@[^@]*@@","",d); return "N" if len(re.sub(r"[^A-Za-z]","",b))<=4 else "O"
def richfeats(sessions):
    seqs=[ "".join(t for t,_ in s) for s in sessions ]
    allb="".join(seqs); n=len(allb)
    if n<60: return None
    f={}
    for t in "NSAO": f[f"u_{t}"]=allb.count(t)/n
    # bigrams & trigrams (position-free motif frequencies)
    bg=collections.Counter(); tg=collections.Counter(); tot_b=tot_t=0
    for s in seqs:
        for i in range(len(s)-1): bg[s[i:i+2]]+=1; tot_b+=1
        for i in range(len(s)-2): tg[s[i:i+3]]+=1; tot_t+=1
    for m in ["NN","NS","SN","SS"]: f[f"bg_{m}"]=bg[m]/tot_b if tot_b else 0
    for m in ["NSN","SNS","NNN","SSS","NSS","SSN","NNS"]: f[f"tg_{m}"]=tg[m]/tot_t if tot_t else 0
    # run-lengths (alignment-free)
    def runs(ch):
        L=[len(r) for r in re.findall(ch+"+", allb)]; return (np.mean(L),np.max(L)) if L else (0,0)
    f["runN_mean"],f["runN_max"]=runs("N"); f["runS_mean"],f["runS_max"]=runs("S")
    # interval distribution
    dts=[]
    for s in sessions:
        ts=sorted(t for _,t in s); dts+=[b-a for a,b in zip(ts,ts[1:]) if 0.02<b-a<300]
    if dts:
        f["dt_med"]=float(np.median(dts)); f["dt_iqr"]=float(np.subtract(*np.percentile(dts,[75,25])))
        f["dt_longfrac"]=float(np.mean([d>5 for d in dts]))
    # entropy of action distribution
    ps=[allb.count(t)/n for t in "NSAO" if allb.count(t)]; f["entropy"]=-sum(p*math.log(p) for p in ps)
    f["evt_per_task"]=n/len(sessions)
    return f
def get(u,ns):
    try: tk=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee"], convert_states_to_json=False, limit=55, pageSize=55)
    except Exception: return None
    if tk.empty: return None
    ids=[str(x) for x in tk.reset_index(names="tid")["tid"]]; S=[]
    for i in range(0,len(ids),20):
        try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except: continue
        for did,row in ds.iterrows():
            st=row["differ_stack"]
            if isinstance(st,list) and len(st)>=3:
                ev=[(lab(e.get("patch","")),(e.get("timestamp",0) or 0)/1000.0) for e in st if isinstance(e,dict)]
                if ev: S.append(ev)
    return richfeats(S)
# conformity competency (varies) on axonOnDendrite
conf=pd.read_csv(OUT/"controlled_axondend.csv",index_col=0)["mean"]
recs=[]
for u in conf.index:
    f=get(u,"axonOnDendrite")
    if f: f.update({"user":u,"conformity":conf[u]}); recs.append(f); print(f"  {u}: features ok",flush=True)
F=pd.DataFrame(recs); F.to_csv(OUT/"richer_features.csv",index=False)
feats=[c for c in F.columns if c not in ("user","conformity")]
print(f"\n=== RICHER features vs conformity competency (n={len(F)}) ===",flush=True)
res=[]
for ft in feats:
    d=F[[ft,"conformity"]].dropna()
    if len(d)>=8 and d[ft].std()>0: res.append((ft,*stats.spearmanr(d[ft],d["conformity"])))
for ft,rho,p in sorted(res,key=lambda x:-abs(x[1]))[:14]:
    print(f"  {ft:14s} rho={rho:+.2f} p={p:.2f} {'*' if p<0.05 else ''}",flush=True)
print(f"\nsimple-feature best |rho| was ~0.58 (pct_navigate). Compare above.",flush=True)
