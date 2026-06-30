"""Add-on: axonOnDendrite competency via reconstructed state URL (no base_state stored)."""
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
(HERE/".nv_tokens.json").write_text(json.dumps(tok))
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
ctok=(HERE/".cave_token").read_text().strip()
from caveclient import CAVEclient
cl=CAVEclient("minnie65_phase3_v1", auth_token=ctok)
from cloudvolume import CloudVolume
cv=CloudVolume("graphene://https://minnie.microns-daf.com/segmentation/table/minnie3_v1", use_https=True, secrets=ctok, agglomerate=False, fill_missing=True, progress=False)
M=pd.read_csv(OUT/"completed_per_type.csv",index_col=0); MIN=20
def resolve(u):
    r=urllib.request.Request(u,headers={"Authorization":f"Bearer {ctok}"}); return json.loads(urllib.request.urlopen(r,timeout=25).read().decode())
def path_ends(apl):
    st=resolve(f"https://global.daf-apis.com/nglstate/api/v1/{apl}"); st=st.get("value",st)
    for L in st.get("layers",[]):
        if L.get("name")=="path" and L.get("annotations"):
            pts=[a["point"] for a in L["annotations"] if a.get("type")=="point" and "point" in a]
            if len(pts)>=2: return pts[0],pts[-1]
    return None,None
def sv_at(pt):
    try: return int(np.array(cv.download_point(list(pt), size=1, coord_resolution=[4,4,40])).flatten()[0])
    except Exception: return 0
users=[u for u in M.index if M.loc[u,"axonOnDendrite"]>=MIN and not str(u).startswith("unassigned")]
recs=[]
for u in users:
    df=nq.get_tasks(sieve={"assignee":u,"namespace":"axonOnDendrite","status":"closed"}, select=["metadata"], convert_states_to_json=False, limit=70, pageSize=70)
    n=0
    for m in df["metadata"]:
        if not isinstance(m,dict): continue
        apl=m.get("apl_id_with_syn"); dec=m.get("decision")
        if not apl or dec is None: continue
        try: p0,p1=path_ends(apl)
        except Exception: continue
        if p0 is None: continue
        s0,s1=sv_at(p0),sv_at(p1)
        if s0 and s1: recs.append([u,str(dec).startswith("yes"),s0,s1]); n+=1
    print(f"axonOnDendrite/{u}: {n} usable",flush=True)
sv=list({r[2] for r in recs}|{r[3] for r in recs}); rt={}
for i in range(0,len(sv),20000):
    try: rt.update({s:int(x) for s,x in zip(sv[i:i+20000], cl.chunkedgraph.get_roots(sv[i:i+20000]))})
    except: pass
acc=collections.defaultdict(list)
for u,yes,s0,s1 in recs:
    r0,r1=rt.get(s0,0),rt.get(s1,0)
    if not r0 or not r1: continue
    sep=r0!=r1; acc[u].append(int((yes and sep) or ((not yes) and (not sep))))
rows=[{"user":u,"axonOnDendrite":round(np.mean(v),3),"n":len(v)} for u,v in acc.items() if len(v)>=15]
R=pd.DataFrame(rows); R.to_csv(OUT/"competency_axondend.csv",index=False)
print("\n=== axonOnDendrite competency ===",flush=True); print(R.sort_values("axonOnDendrite").to_string(index=False),flush=True)
