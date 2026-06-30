"""Feature-level: which behaviors predict v18xx competency, WITHIN each task type."""
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
def lab(p):
    d=urllib.parse.unquote(str(p)); add=rm=hexid=0
    for ln in d.split("\n"):
        if ln[:1] in ("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); add+=n if ln[:1]=="+" else 0; rm+=n if ln[:1]=="-" else 0
            if re.search(r"[0-9a-f]{32,40}",ln): hexid+=1
    k=set(re.findall(r'"([A-Za-z_]\w*)"\s*:',d))
    if add or rm: return "segment"
    if (k&ANN) or hexid: return "annotate"
    if (k&NAV): return "navigate"
    b=re.sub(r"@@[^@]*@@","",d); return "navigate" if len(re.sub(r"[^A-Za-z]","",b))<=4 else "other"
def feats(sessions):
    allb=[b for s in sessions for b,_ in s]; n=len(allb)
    if n<60 or len(sessions)<3: return None
    pn=allb.count("navigate")/n; ps=allb.count("segment")/n; pa=allb.count("annotate")/n
    sn=ss=segc=0
    for s in sessions:
        b=[x for x,_ in s]
        for a,cc in zip(b,b[1:]):
            if a=="segment":
                segc+=1; sn+= (cc=="navigate"); ss+=(cc=="segment")
    dts=[]
    for s in sessions:
        ts=sorted(t for _,t in s); dts+=[y-x for x,y in zip(ts,ts[1:]) if 0.05<y-x<120]
    return {"pct_navigate":pn,"pct_segment":ps,"pct_annotate":pa,"nav_seg_ratio":pn/ps if ps>0 else np.nan,
            "seg_to_nav":sn/segc if segc else np.nan,"seg_to_seg":ss/segc if segc else np.nan,
            "events_per_session":n/len(sessions),"log_tempo":float(np.log(np.median(dts))) if dts else np.nan,"total_events":n}
def user_feats(u,ns):
    try: tk=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee"], convert_states_to_json=False, limit=50, pageSize=50)
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
    return feats(S)
C=pd.read_csv(OUT/"competency_ALL6.csv",index_col=0)
FEATS=["pct_navigate","pct_segment","pct_annotate","nav_seg_ratio","seg_to_nav","seg_to_seg","events_per_session","log_tempo","total_events"]
rows=[]
for ns in C.columns:
    users=[u for u in C.index if pd.notna(C.loc[u,ns])]
    if len(users)<7: continue
    recs=[]
    for u in users:
        f=user_feats(u,ns)
        if f: f.update({"user":u,"type":ns,"competency":C.loc[u,ns]}); recs.append(f)
    F=pd.DataFrame(recs)
    print(f"\n=== {ns}: {len(F)} users with features+competency ===",flush=True)
    if len(F)<7: continue
    res=[]
    for ft in FEATS:
        d=F[[ft,"competency"]].dropna()
        if len(d)>=7:
            rho,p=stats.spearmanr(d[ft],d["competency"]); res.append((ft,rho,p))
    for ft,rho,p in sorted(res,key=lambda x:-abs(x[1])):
        star="*" if p<0.05 else (" " if p<0.1 else "")
        print(f"  {ft:20s} rho={rho:+.2f} p={p:.2f} {star}",flush=True)
    rows+=recs
pd.DataFrame(rows).to_csv(OUT/"feature_competency.csv",index=False)
print("\nsaved feature_competency.csv",flush=True)
