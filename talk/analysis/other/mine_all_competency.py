"""Comprehensive per-task-type competency vs v18xx, all qualifying annotators.
op-types: operation_ids -> did-cut survived. axon-types: decision vs endpoints-separated.
"""
import sys, json, ast, http.client, urllib.request, collections
from pathlib import Path
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"
sys.path.insert(0,str(HERE/"neuvue-client"))
tok=json.loads((HERE/".nv_tokens.json").read_text())
c=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
c.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=c.getresponse().read().decode()
try: tok["access_token"]=json.loads(raw)["access_token"]
except: tok["access_token"]=ast.literal_eval(raw)["access_token"]
(HERE/".nv_tokens.json").write_text(json.dumps(tok))
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
ctok=(HERE/".cave_token").read_text().strip()
from caveclient import CAVEclient
cl=CAVEclient("minnie65_phase3_v1", auth_token=ctok)
from cloudvolume import CloudVolume
cv=CloudVolume("graphene://https://minnie.microns-daf.com/segmentation/table/minnie3_v1", use_https=True, secrets=ctok, agglomerate=False, fill_missing=True, progress=False)
M=pd.read_csv(OUT/"completed_per_type.csv",index_col=0); MIN=20
OPTYPES=["multiSomaId","singleSomaCleanUp","neuronOtherBodies"]
AXTYPES=["axonOnAxon","axonOnDendrite","axonOnDendriteV3"]
def q(u,ns,lim): return nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":"closed"}, select=["metadata"], convert_states_to_json=False, limit=lim, pageSize=min(lim,1000))
def resolve(u):
    r=urllib.request.Request(u,headers={"Authorization":f"Bearer {ctok}"}); return json.loads(urllib.request.urlopen(r,timeout=25).read().decode())
def path_ends(bs):
    st=resolve(bs); st=st.get("value",st)
    for L in st.get("layers",[]):
        if L.get("name")=="path" and L.get("annotations"):
            pts=[a["point"] for a in L["annotations"] if a.get("type")=="point" and "point" in a]
            if len(pts)>=2: return pts[0],pts[-1]
    return None,None
def sv_at(pt):
    try: return int(np.array(cv.download_point(list(pt), size=1, coord_resolution=[4,4,40])).flatten()[0])
    except Exception: return 0

results={}   # (user,type) -> competency
# ---------- OP TYPES: did-cut survived ----------
op2ut={}
for ns in OPTYPES:
    users=[u for u in M.index if M.loc[u,ns]>=MIN and not str(u).startswith("unassigned")]
    for u in users:
        for m in q(u,ns,150)["metadata"]:
            for o in ((m or {}).get("operation_ids") or []) if isinstance(m,dict) else []:
                try: op2ut[int(o)]=(u,ns)
                except: pass
    print(f"[op] {ns}: {len(users)} users, cum ops {len(op2ut)}",flush=True)
det={}
opids=list(op2ut)
for i in range(0,len(opids),150):
    try: det.update(cl.chunkedgraph.get_operation_details(opids[i:i+150]))
    except: pass
ope=collections.defaultdict(list); svset=set()
for o,d in det.items():
    for e in (d.get("removed_edges") or [])[:6]:
        if len(e)==2: ope[int(o)].append((int(e[0]),int(e[1]))); svset.update([int(e[0]),int(e[1])])
svr={}; svl=list(svset)
for i in range(0,len(svl),20000):
    try: svr.update({s:int(r) for s,r in zip(svl[i:i+20000], cl.chunkedgraph.get_roots(svl[i:i+20000]))})
    except: pass
opcut=collections.defaultdict(list)
for o,el in ope.items():
    v=[int(svr.get(a,0)!=svr.get(b,0)) for a,b in el if svr.get(a,0) and svr.get(b,0)]
    if v: opcut[op2ut[o]].append(int(np.mean(v)>=0.5))
for (u,ns),vals in opcut.items():
    if len(vals)>=15: results[(u,ns)]=(round(np.mean(vals),3),len(vals))
print(f"[op] filled {len(results)} cells",flush=True)
# ---------- AXON TYPES: decision vs endpoints-separated ----------
axrec=[]  # (user,type,decision_yes,sv0,sv1)
for ns in AXTYPES:
    users=[u for u in M.index if M.loc[u,ns]>=MIN and not str(u).startswith("unassigned")]
    for u in users:
        n=0
        for m in q(u,ns,60)["metadata"]:
            if not isinstance(m,dict): continue
            bs=m.get("base_state"); dec=m.get("decision")
            if not bs or dec is None: continue
            try: p0,p1=path_ends(bs)
            except Exception: continue
            if p0 is None: continue
            s0,s1=sv_at(p0),sv_at(p1)
            if s0 and s1: axrec.append([u,ns,str(dec).startswith("yes"),s0,s1]); n+=1
        print(f"[ax] {ns}/{u}: {n} usable",flush=True)
# batch roots for axon supervoxels
axsv=list({r[3] for r in axrec}|{r[4] for r in axrec}); ar={}
for i in range(0,len(axsv),20000):
    try: ar.update({s:int(rt) for s,rt in zip(axsv[i:i+20000], cl.chunkedgraph.get_roots(axsv[i:i+20000]))})
    except: pass
axc=collections.defaultdict(list)
for u,ns,yes,s0,s1 in axrec:
    r0,r1=ar.get(s0,0),ar.get(s1,0)
    if not r0 or not r1: continue
    sep=r0!=r1
    correct=int((yes and sep) or ((not yes) and (not sep)))
    axc[(u,ns)].append(correct)
for (u,ns),vals in axc.items():
    if len(vals)>=10: results[(u,ns)]=(round(np.mean(vals),3),len(vals))
# ---------- assemble ----------
rows=[{"user":u,"type":ns,"competency":v[0],"n":v[1]} for (u,ns),v in results.items()]
R=pd.DataFrame(rows)
mat=R.pivot(index="user",columns="type",values="competency")
nmat=R.pivot(index="user",columns="type",values="n")
mat.to_csv(OUT/"competency_ALL.csv"); nmat.to_csv(OUT/"competency_ALL_n.csv")
print(f"\n=== COMPLETE competency matrix: {len(R)} cells, {mat.shape[0]} users x {mat.shape[1]} types ===",flush=True)
print(mat.round(2).to_string(),flush=True)
print("\nusers in >=2 types:", int((mat.notna().sum(1)>=2).sum()),flush=True)
