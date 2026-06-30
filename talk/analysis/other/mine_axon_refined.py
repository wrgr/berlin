"""Refined axon competency: clear yes vs no/noError only (drop partial/conditional).
Saves raw records (user,type,decision,separated) so grading is flexible later.
Covers axonOnAxon, axonOnDendriteV3 (base_state) and axonOnDendrite (reconstructed URL).
"""
import sys, json, ast, http.client, urllib.request, collections
from pathlib import Path
import numpy as np, pandas as pd
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
M=pd.read_csv(OUT/"completed_per_type.csv",index_col=0); MIN=20
AX=["axonOnAxon","axonOnDendriteV3","axonOnDendrite"]
def resolve(u):
    r=urllib.request.Request(u,headers={"Authorization":f"Bearer {ctok}"}); return json.loads(urllib.request.urlopen(r,timeout=25).read().decode())
def path_ends(m):
    bs=m.get("base_state")
    if not bs and m.get("apl_id_with_syn"): bs=f"https://global.daf-apis.com/nglstate/api/v1/{m['apl_id_with_syn']}"
    if not bs: return None,None
    try: st=resolve(bs)
    except Exception: return None,None
    st=st.get("value",st)
    for L in st.get("layers",[]):
        if L.get("name")=="path" and L.get("annotations"):
            pts=[a["point"] for a in L["annotations"] if a.get("type")=="point" and "point" in a]
            if len(pts)>=2: return pts[0],pts[-1]
    return None,None
def sv_at(pt):
    try: return int(np.array(cv.download_point(list(pt), size=1, coord_resolution=[4,4,40])).flatten()[0])
    except Exception: return 0
recs=[]
for ns in AX:
    users=[u for u in M.index if M.loc[u,ns]>=MIN and not str(u).startswith("unassigned")]+["rivlipk1"]
    for u in set(users):
        try: df=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":"closed"}, select=["metadata"], convert_states_to_json=False, limit=80, pageSize=80)
        except Exception: continue
        n=0
        for m in df["metadata"]:
            if not isinstance(m,dict): continue
            dec=m.get("decision")
            if dec is None: continue
            p0,p1=path_ends(m)
            if p0 is None: continue
            s0,s1=sv_at(p0),sv_at(p1)
            if s0 and s1: recs.append([u,ns,str(dec),s0,s1]); n+=1
        print(f"{ns}/{u}: {n} usable",flush=True)
sv=list({r[3] for r in recs}|{r[4] for r in recs}); rt={}
for i in range(0,len(sv),20000):
    try: rt.update({s:int(x) for s,x in zip(sv[i:i+20000], cl.chunkedgraph.get_roots(sv[i:i+20000]))})
    except: pass
raw_rows=[]
for u,ns,dec,s0,s1 in recs:
    r0,r1=rt.get(s0,0),rt.get(s1,0)
    if not r0 or not r1: continue
    raw_rows.append({"user":u,"type":ns,"decision":dec,"separated":int(r0!=r1)})
RAW=pd.DataFrame(raw_rows); RAW.to_csv(OUT/"axon_raw_records.csv",index=False)
# REFINED grading: clear yes vs no/noError only
def clear_correct(row):
    d=row["decision"]
    if d=="yes": return int(row["separated"]==1)
    if d in ("no","noError"): return int(row["separated"]==0)
    return np.nan
RAW["correct"]=RAW.apply(clear_correct,axis=1)
clear=RAW.dropna(subset=["correct"])
g=clear.groupby(["user","type"])["correct"].agg(["mean","size"]).reset_index(); g=g[g["size"]>=10]
mat=g.pivot(index="user",columns="type",values="mean").round(2)
mat.to_csv(OUT/"competency_axon_refined.csv")
print("\n=== REFINED axon competency (clear yes/no only) ===",flush=True)
print(mat.to_string(),flush=True)
print("\ndropped-ambiguous share per type:",flush=True)
print((1-RAW.groupby("type")["correct"].apply(lambda s:s.notna().mean())).round(2).to_dict(),flush=True)
print("Pat refined:", mat.loc["rivlipk1"].to_dict() if "rivlipk1" in mat.index else "n/a",flush=True)
