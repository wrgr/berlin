"""#2a extract raw multiSomaId behavioral event streams -> live_out/streams.json, so a GRAMMAR /
sequence model can be fit on the actual action sequences (token = label + timing + rotation).
Network stage: needs .nv_tokens.json + neuvue-client alongside this script."""
import sys, json, ast, http.client, re, urllib.parse, math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; OUT.mkdir(exist_ok=True); sys.path.insert(0,str(HERE/"neuvue-client"))
import diff_match_patch as dmpmod; dmp=dmpmod.diff_match_patch()
tok=json.loads((HERE/".nv_tokens.json").read_text())
c=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
c.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=c.getresponse().read().decode()
try: tok["access_token"]=json.loads(raw)["access_token"]
except: tok["access_token"]=ast.literal_eval(raw)["access_token"]
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io",token=True,access_token=tok["access_token"],refresh_token=tok["refresh_token"])
EXPERTS=["chris","christopher","claire","erika","gary","michael","natalie","phillips"]
STUDENTS=["aashi","clara","donovan9","dylan","emma","emily","joey","jonas","katie","krutal","luzhou","mia","oji","rachel","rupa","sarah","sean_sebastian","shruthi","taylor","titus","vivia","stella","maggie","makayla","maryam","tina","luke","trystan","cindy"]
PROMOTED={"dylan","vivia","taylor","clara","rachel","shruthi","sarah","lydia"}
ANN={"description","tagId","tagIds","tags","annotation","annotations","point","pointA","pointB","parentId"}
NAVK={"position","voxelCoordinates","perspectiveOrientation","projectionOrientation","crossSectionOrientation","perspectiveZoom","projectionScale","crossSectionScale","pose"}
def lab(p):
    d=urllib.parse.unquote(str(p)); add=rm=hexid=0
    for ln in d.split("\n"):
        if ln[:1] in("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); add+=n if ln[:1]=="+" else 0; rm+=n if ln[:1]=="-" else 0
            if re.search(r"[0-9a-f]{32,40}",ln): hexid+=1
    k=set(re.findall(r'"([A-Za-z_]\w*)"\s*:',d))
    if add or rm: return "S"
    if (k&ANN) or hexid: return "A"
    if (k&NAVK): return "N"
    b=re.sub(r"@@[^@]*@@","",d); return "N" if len(re.sub(r"[^A-Za-z]","",b))<=4 else "O"
QRE=re.compile(r"(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,})")
def newwin(p):
    try: return urllib.parse.unquote("".join(t for pp in dmp.patch_fromText(str(p)) for op,t in pp.diffs if op>=0))
    except Exception: return ""
def qval(w):
    mm=QRE.search(w)
    if mm:
        v=[float(x) for x in mm.groups()]
        if all(abs(x)<=1.01 for x in v): return np.array(v)
    return None
def qang(a,b):
    d=abs(float(np.dot(a/np.linalg.norm(a),b/np.linalg.norm(b)))); return math.degrees(2*math.acos(min(1,d)))
DATA={}
for u in EXPERTS+STUDENTS:
    try: df=nq.get_tasks(sieve={"assignee":u,"namespace":"multiSomaId","status":"closed"}, select=["seg_id"], convert_states_to_json=False, limit=40, pageSize=40)
    except Exception: continue
    if df.empty: continue
    ids=[str(x) for x in df.reset_index(names="t")["t"]]; sessions=[]; ev=0
    for i in range(0,len(ids),20):
        try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except Exception: continue
        for _,row in ds.iterrows():
            st=row["differ_stack"]
            if not isinstance(st,list) or len(st)<3: continue
            seq=[]; prevq=None; pts=None
            for e in sorted([x for x in st if isinstance(x,dict)],key=lambda z:z.get("timestamp",0)):
                lb=lab(e.get("patch","")); ts=(e.get("timestamp",0) or 0)/1000.0; rot=0.0
                if lb=="N":
                    qv=qval(newwin(e.get("patch","")))
                    if qv is not None:
                        if prevq is not None: rot=qang(prevq,qv)
                        prevq=qv
                dt=0.0 if pts is None else max(0.0,ts-pts); pts=ts
                seq.append([lb,round(dt,2),round(rot,1)]); ev+=1
            if len(seq)>=3: sessions.append(seq)
        if ev>=2200: break
    if sessions: DATA[u]={"cohort":"expert" if u in EXPERTS else "student","promoted":int(u in PROMOTED),"sessions":sessions}
json.dump(DATA,open(OUT/'streams.json','w'))
print("saved streams.json: %d annotators, %d total events"%(len(DATA),sum(len(s) for d in DATA.values() for s in d["sessions"])))
