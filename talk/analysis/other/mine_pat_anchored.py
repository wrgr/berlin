"""Pat-anchored controlled experiment on axonOnDendriteV3 (same 20 objects, 9 students + Pat).
Competency = agreement-with-Pat. Test behavior->competency and behavioral-distance-to-Pat.
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
def md(m,k): return (m or {}).get(k) if isinstance(m,dict) else None
def fam(d): s=str(d); return "ERR" if s.startswith("yes") else ("NOERR" if "no" in s else None)
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
    seqs=["".join(t for t,_ in s) for s in sessions]; allb="".join(seqs); n=len(allb)
    if n<40: return None
    f={}
    for t in "NSAO": f[f"u_{t}"]=allb.count(t)/n
    bg=collections.Counter(); tg=collections.Counter(); tb=tt=0
    for s in seqs:
        for i in range(len(s)-1): bg[s[i:i+2]]+=1; tb+=1
        for i in range(len(s)-2): tg[s[i:i+3]]+=1; tt+=1
    for m in ["NN","NS","SN","SS"]: f[f"bg_{m}"]=bg[m]/tb if tb else 0
    for m in ["NSN","SNS","NNN","SSS","NSS","SSN"]: f[f"tg_{m}"]=tg[m]/tt if tt else 0
    def runs(ch):
        L=[len(r) for r in re.findall(ch+"+",allb)]; return (np.mean(L),np.max(L)) if L else (0,0)
    f["runN_mean"],f["runN_max"]=runs("N"); f["runS_mean"],f["runS_max"]=runs("S")
    dts=[]
    for s in sessions:
        ts=sorted(t for _,t in s); dts+=[b-a for a,b in zip(ts,ts[1:]) if 0.02<b-a<300]
    if dts: f["dt_med"]=float(np.median(dts)); f["dt_longfrac"]=float(np.mean([d>5 for d in dts]))
    ps=[allb.count(t)/n for t in "NSAO" if allb.count(t)]; f["entropy"]=-sum(p*math.log(p) for p in ps); f["evt_per_task"]=n/len(sessions)
    return f
def behav(u):
    tk=nq.get_tasks(sieve={"assignee":u,"namespace":"axonOnDendriteV3","status":{"$in":["closed","errored"]}}, select=["assignee"], convert_states_to_json=False, limit=60, pageSize=60)
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
# decisions
df=nq.get_tasks(sieve={"namespace":"axonOnDendriteV3","status":"closed"}, convert_states_to_json=False, limit=2000, pageSize=1000)
df["key"]=df["metadata"].apply(lambda m: f"{md(m,'starting_seg_id')}_{md(m,'cut_id')}")
df["fam"]=df["metadata"].apply(lambda m: fam(md(m,"decision")))
patf=df[df.assignee=="rivlipk1"].dropna(subset=["fam"]).groupby("key")["fam"].first()
print(f"Pat objects: {len(patf)} | Pat says ERR on {int((patf=='ERR').sum())}, NOERR on {int((patf=='NOERR').sum())}",flush=True)
rows=[]
for u,g in df[df.assignee!="rivlipk1"].groupby("assignee"):
    gg=g.dropna(subset=["fam"]); gg=gg[gg.key.isin(patf.index)]
    if gg["key"].nunique()<12: continue
    m=gg.drop_duplicates("key").set_index("key")
    agree=(m["fam"]==patf.reindex(m.index)).mean()
    # balanced: agreement on Pat-ERR objs and Pat-NOERR objs separately
    errk=patf[patf=="ERR"].index; nok=patf[patf=="NOERR"].index
    ea=(m.reindex(m.index.intersection(errk))["fam"]=="ERR").mean()
    na=(m.reindex(m.index.intersection(nok))["fam"]=="NOERR").mean() if len(m.index.intersection(nok)) else np.nan
    rows.append({"student":u,"agree_pat":round(agree,2),"n_obj":m.shape[0],"err_recall":round(ea,2),"noerr_recall":round(na,2) if na==na else np.nan})
A=pd.DataFrame(rows).set_index("student").sort_values("agree_pat")
print("\n=== Pat-anchored competency (agreement-with-Pat on identical 20 objects) ===",flush=True)
print(A.to_string(),flush=True)
# behavior for Pat + students -> distance-to-Pat + feature corr
B={}
for u in ["rivlipk1"]+list(A.index):
    f=behav(u);
    if f: B[u]=f
F=pd.DataFrame(B).T
print(f"\nbehavior signatures: {len(F)} users (Pat {'ok' if 'rivlipk1' in F.index else 'MISSING'})",flush=True)
if "rivlipk1" in F.index and len(F)>=8:
    Z=(F-F.mean())/F.std(ddof=0).replace(0,1); pv=Z.loc["rivlipk1"]
    dist=Z.drop("rivlipk1").apply(lambda r: float(np.linalg.norm(r.values-pv.values)),axis=1)
    M=A.join(dist.rename("behav_dist_to_pat"))
    d=M[["behav_dist_to_pat","agree_pat"]].dropna()
    print(f"\n(B) behavioral-distance-to-Pat vs decision-agreement-with-Pat: rho={stats.spearmanr(d['behav_dist_to_pat'],d['agree_pat'])[0]:+.2f} p={stats.spearmanr(d['behav_dist_to_pat'],d['agree_pat'])[1]:.2f} (n={len(d)})",flush=True)
    print("   (negative rho = behave like Pat -> decide like Pat)",flush=True)
    print("\n(A) which behaviors predict agreement-with-Pat:",flush=True)
    MM=A.join(F.drop(index="rivlipk1",errors="ignore"))
    res=[]
    for ft in F.columns:
        dd=MM[[ft,"agree_pat"]].dropna()
        if len(dd)>=8 and dd[ft].std()>0: res.append((ft,*stats.spearmanr(dd[ft],dd["agree_pat"])))
    for ft,rho,p in sorted(res,key=lambda x:-abs(x[1]))[:10]:
        print(f"   {ft:12s} rho={rho:+.2f} p={p:.2f} {'*' if p<0.05 else ''}",flush=True)
    M.join(F).to_csv(OUT/"pat_anchored_v3.csv")
