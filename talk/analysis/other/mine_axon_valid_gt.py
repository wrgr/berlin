"""Controlled experiment WITH valid GT: axonOnDendrite shared objects.
Object truth = wrong-axon (path) separated from dendrite (postsyn body) in v18xx.
Per-annotator accuracy on identical objects -> correlate with behavior.
"""
import sys, json, ast, http.client, urllib.request, collections
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
ctok=(HERE/".cave_token").read_text().strip()
from caveclient import CAVEclient
cl=CAVEclient("minnie65_phase3_v1", auth_token=ctok)
from cloudvolume import CloudVolume
cv=CloudVolume("graphene://https://minnie.microns-daf.com/segmentation/table/minnie3_v1", use_https=True, secrets=ctok, agglomerate=False, fill_missing=True, progress=False)
def md(m,k): return (m or {}).get(k) if isinstance(m,dict) else None
def resolve(u): return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"Authorization":f"Bearer {ctok}"}),timeout=25).read().decode())
def layer(st,n):
    for L in st.get("layers",[]):
        if L.get("name")==n: return [a["point"] for a in L.get("annotations",[]) if a.get("type")=="point" and "point" in a]
    return []
def densify(path,k=3):
    pts=[]
    for a,b in zip(path,path[1:]):
        a,b=np.array(a,float),np.array(b,float)
        for t in np.linspace(0,1,k,endpoint=False): pts.append((a+(b-a)*t).tolist())
    if path: pts.append(list(map(float,path[-1])))
    return pts
def dom(pts,cap=22):
    pts=pts[:cap]; sv=[]
    for p in pts:
        try: sv.append(int(np.array(cv.download_point(list(p),size=1,coord_resolution=[4,4,40])).flatten()[0]))
        except Exception: sv.append(0)
    sv=[x for x in sv if x]
    if len(sv)<4: return None
    rt=[int(r) for r in cl.chunkedgraph.get_roots(sv)]
    cc=collections.Counter([r for r in rt if r]); return cc.most_common(1)[0][0] if cc else None
# tasks
df=nq.get_tasks(sieve={"namespace":"axonOnDendrite","status":"closed"}, convert_states_to_json=False, limit=3000, pageSize=1000)
df["key"]=df["metadata"].apply(lambda m: f"{md(m,'starting_seg_id')}_{md(m,'cut_id')}")
df["dec"]=df["metadata"].apply(lambda m: md(m,"decision"))
df["apl"]=df["metadata"].apply(lambda m: md(m,"apl_id_with_syn"))
df=df.dropna(subset=["dec","apl"])
per=df.groupby("key")["assignee"].nunique(); sharedset=set(per[per>=2].index)
# STRATIFIED: ensure every annotator's shared objects are represented (not one QC cluster)
annobj=df[df.key.isin(sharedset)].groupby("assignee")["key"].apply(lambda s:list(dict.fromkeys(s)))
sample=set()
for a,ks in annobj.items(): sample|=set(ks[:55])
objs=list(sample)[:520]
print(f"shared objects to grade: {len(objs)} (stratified across {len(annobj)} annotators)",flush=True)
truth={}
for i,k in enumerate(objs):
    apl=df[df.key==k]["apl"].iloc[0]
    try: st=resolve(f"https://global.daf-apis.com/nglstate/api/v1/{apl}"); st=st.get("value",st)
    except Exception: continue
    path=layer(st,"path"); post=layer(st,"postsyn")
    if len(path)<2 or len(post)<4: continue
    ax=dom(densify(path)); de=dom(post)
    if ax is None or de is None: continue
    truth[k]=int(ax!=de)   # 1 = separated (real merge error)
    if (i+1)%40==0: print(f"  graded {i+1}/{len(objs)} objects ({len(truth)} valid)",flush=True)
print(f"object truths: {len(truth)} | separated(real-error) rate: {np.mean(list(truth.values())):.0%}",flush=True)
# per-annotator accuracy on graded objects
G=df[df.key.isin(truth)].copy(); G["t"]=G["key"].map(truth)
G["yesfam"]=G["dec"].astype(str).str.startswith("yes")
G["correct"]=((G["yesfam"]&(G["t"]==1))|((~G["yesfam"])&(G["t"]==0))).astype(int)
def balacc(g):
    pos=g[g.t==1]; neg=g[g.t==0]
    if len(pos)<3 or len(neg)<3: return np.nan
    return round((pos["correct"].mean()+neg["correct"].mean())/2,3)
rows=[]
for a,g in G.groupby("assignee"):
    if len(g)>=15: rows.append({"assignee":a,"raw_acc":round(g["correct"].mean(),3),"bal_acc":balacc(g),"n_obj":len(g),"n_neg":int((g.t==0).sum())})
acc=pd.DataFrame(rows).set_index("assignee").sort_values("bal_acc")
acc.to_csv(OUT/"axon_valid_competency.csv")
print(f"\nbase rate (real-error): {G['t'].mean():.0%}  -> always-yes raw acc = {G['t'].mean():.0%}",flush=True)
print("\n=== CONTROLLED + VALID competency (vs v18xx truth on shared objects) ===",flush=True)
print(acc.to_string(),flush=True)
acc["mean"]=acc["bal_acc"]  # use balanced accuracy as competency for correlation
# behavior vs valid competency
F=pd.read_csv(OUT/"feature_competency.csv"); F=F[F["type"]=="axonOnDendrite"].set_index("user")
M=acc.join(F); FEATS=["pct_navigate","pct_segment","pct_annotate","nav_seg_ratio","seg_to_nav","seg_to_seg","events_per_session","log_tempo","total_events"]
print("\n=== does behavior predict CONTROLLED+VALID competency? (Spearman) ===",flush=True)
out=[]
for ft in FEATS:
    d=M[[ft,"mean"]].dropna()
    if len(d)>=8: out.append((ft,*stats.spearmanr(d[ft],d["mean"]),len(d)))
for ft,rho,p,n in sorted(out,key=lambda x:-abs(x[1])):
    print(f"  {ft:20s} rho={rho:+.2f} p={p:.2f} n={n} {'*' if p<0.05 else ''}",flush=True)
