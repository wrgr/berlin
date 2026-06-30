"""Metric spatial features via state reconstruction (CAVE-token resolved).

Navigation patches apply ~96% cleanly. We reconstruct each session and read the
navigation fields by regex on the URL-encoded state (robust to segment-patch
corruption): perspectiveOrientation (3D rotation, quaternion), voxelCoordinates
(pan), perspectiveZoom / zoomFactor (zoom). Per nav event we get rotation(deg),
pan(voxels), zoom(|log ratio|); aggregate per session/user.
"""
import sys, json, urllib.parse, urllib.request, re, math
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE/"neuvue-client")); pd.set_option("display.width",220)
tok=json.loads((HERE/".nv_tokens.json").read_text()); cave=(HERE/".cave_token").read_text().strip()
from neuvueclient import NeuvueQueue
import diff_match_patch as dmpmod
c=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok.get("refresh_token",""))
dmp=dmpmod.diff_match_patch(); dmp.Match_Threshold=1.0; dmp.Match_Distance=500000; dmp.Patch_DeleteThreshold=1.0

_cache={}
def resolve(u):
    if u not in _cache:
        try:
            b=urllib.request.urlopen(urllib.request.Request(u,headers={"content-type":"application/json","Authorization":f"Bearer {cave}"}),timeout=25).read().decode()
            v=json.loads(b); _cache[u]=v.get("value",v)
        except Exception: _cache[u]=None
    return _cache[u]
def numfix(o):
    if isinstance(o,float) and o.is_integer(): return int(o)
    if isinstance(o,dict): return {k:numfix(v) for k,v in o.items()}
    if isinstance(o,list): return [numfix(v) for v in o]
    return o
def lab(p):
    d=urllib.parse.unquote(str(p)); a=r=0
    for ln in d.split("\n"):
        if ln[:1] in ("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); a+=n if ln[:1]=="+" else 0; r+=n if ln[:1]=="-" else 0
    return "segment" if (a or r) else "navigate"
RE_ORI=re.compile(r"perspectiveOrientation%22:%5B([-0-9.,eE]+)%5D")
RE_POS=re.compile(r"voxelCoordinates%22:%5B([-0-9.,eE]+)%5D")
RE_PZ=re.compile(r"perspectiveZoom%22:([0-9.eE+-]+)")
RE_ZF=re.compile(r"zoomFactor%22:([0-9.eE+-]+)")
def fvec(m):
    if not m: return None
    try: return [float(x) for x in m.group(1).split(",")]
    except: return None
def fnum(m):
    try: return float(m.group(1)) if m else None
    except: return None
def fields(cur):
    return (fvec(RE_ORI.search(cur)), fvec(RE_POS.search(cur)), fnum(RE_PZ.search(cur)) or fnum(RE_ZF.search(cur)))
def quat_ang(a,b):
    if not a or not b or len(a)!=4 or len(b)!=4: return 0.0
    d=max(-1.0,min(1.0,abs(sum(x*y for x,y in zip(a,b))))); return math.degrees(2*math.acos(d))
def dist(a,b):
    if not a or not b or len(a)<3 or len(b)<3: return 0.0
    return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
def zlog(a,b):
    if not a or not b or a<=0 or b<=0: return 0.0
    return abs(math.log(a/b))

def collect(ns, max_tasks=900, want=22):
    tk=c.get_tasks(sieve={"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee","ng_state"],
                   convert_states_to_json=False, limit=max_tasks, pageSize=1000)
    if tk.empty: return []
    tk=tk.reset_index(names="task_id"); tk["task_id"]=tk["task_id"].astype(str)
    info={r.task_id:(r.assignee,r.ng_state) for r in tk.itertuples()}; ids=list(info); out=[]
    for i in range(0,len(ids),20):
        try: ds=c.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except Exception: continue
        for did,row in ds.iterrows():
            st=row["differ_stack"]; a,s=info.get(str(row["task_id"]),(None,None))
            if isinstance(st,list) and len(st)>=8 and isinstance(s,str) and s.startswith("http"):
                out.append((ns,a,s,st))
        if len(out)>=want: break
    return out

sessions=[]
for ns in ["somaSomaSplit","multiSomaSplit","somaSomaReview","fullyProofread"]:
    s=collect(ns); print(f"{ns:16s}: {len(s)} resolvable sessions"); sessions+=s

rows=[]
for ns,assignee,url,st in sessions:
    base=resolve(url)
    if base is None: continue
    cur=urllib.parse.quote(json.dumps(numfix(base),separators=(",",":")),safe=":,")
    ori,pos,zm=fields(cur); rot=pan=zoom=0.0; clicks=0; nav_rot_runs=[]; run=0.0
    for ev in st:
        L=lab(ev.get("patch","")); p=ev.get("patch")
        if p:
            try: cur,_=dmp.patch_apply(dmp.patch_fromText(p),cur)
            except Exception: pass
        o2,p2,z2=fields(cur)
        dr=quat_ang(ori,o2); dp=dist(pos,p2); dz=zlog(zm,z2)
        if L=="navigate": rot+=dr; pan+=dp; zoom+=dz; run+=dr+dp/100.0
        if L=="segment": clicks+=1; nav_rot_runs.append(run); run=0.0
        ori,pos,zm=o2 or ori,p2 or pos,z2 or zm
    if clicks>=1:
        rows.append({"ns":ns,"assignee":assignee,"clicks":clicks,"rot_deg":rot,"pan_vox":pan,"zoom":round(zoom,2),
                     "rot_per_click":rot/clicks,"pan_per_click":pan/clicks,
                     "effort_before_click":np.mean(nav_rot_runs) if nav_rot_runs else 0.0})
S=pd.DataFrame(rows)
print(f"\nreconstructed sessions with clicks: {len(S)} | users: {S['assignee'].nunique()}")
print("\n==== spatial features by namespace (median) ====")
print(S.groupby("ns")[["rot_deg","pan_vox","zoom","rot_per_click","pan_per_click","effort_before_click"]].median().round(2).to_string())
cnt=S.groupby("assignee")["clicks"].count(); keep=cnt[cnt>=3].index
U=S[S["assignee"].isin(keep)].groupby("assignee")[["rot_deg","pan_vox","zoom","rot_per_click","pan_per_click"]].median().round(2)
U["n"]=cnt[keep]; U=U.sort_values("n",ascending=False)
print(f"\n==== per-user spatial (>=3 sessions: {len(U)}) ====")
print(U.head(16).to_string())
S.to_csv(OUT/"spatial_sessions.csv",index=False); U.to_csv(OUT/"spatial_user.csv")
# figure: rotation vs pan per click, per user
sub=U.dropna()
if len(sub)>=2:
    plt.figure(figsize=(7,5))
    plt.scatter(sub["rot_per_click"],sub["pan_per_click"],s=sub["n"]*4,alpha=.6,color="teal")
    for u,r in sub.iterrows(): plt.annotate(u,(r["rot_per_click"],r["pan_per_click"]),fontsize=7,alpha=.7)
    plt.xlabel("rotation (deg) per click"); plt.ylabel("pan (voxels) per click")
    plt.title("Proofreader spatial navigation style (size=#sessions)"); plt.tight_layout()
    plt.savefig(OUT/"spatial_style.png",dpi=130); plt.close(); print("\nsaved spatial_style.png")
