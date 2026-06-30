"""Rich behavioral feature bank from multiSomaId (common dense task) per annotator.
argv[1] = group (expert|student). Cross-task: features here -> multiSomaSplit quality later.
"""
import sys, json, ast, http.client, re, urllib.parse, collections, math
from pathlib import Path
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; sys.path.insert(0,str(HERE/"neuvue-client"))
import diff_match_patch as dmpmod; dmp=dmpmod.diff_match_patch()
tok=json.loads((HERE/".nv_tokens.json").read_text())
c=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
c.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=c.getresponse().read().decode()
try: tok["access_token"]=json.loads(raw)["access_token"]
except: tok["access_token"]=ast.literal_eval(raw)["access_token"]
from neuvueclient import NeuvueQueue
nq=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
EXPERTS=["chris","christopher","claire","erika","gary","michael","natalie","phillips"]
STUDENTS=["aashi","clara","dylan","emma","emily","joey","jonas","katie","krutal","luzhou","mia","oji","rachel","rupa","sarah","sean_sebastian","shruthi","taylor","titus","vivia","makayla","maryam","tina","luke","trystan","cindy"]
group=sys.argv[1] if len(sys.argv)>1 else "expert"
users=EXPERTS if group=="expert" else STUDENTS
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
PRE=re.compile(r"(\d{4,7}(?:\.\d+)?),(\d{4,7}(?:\.\d+)?),(\d{3,6}(?:\.\d+)?)")
def newwin(p):
    try: return urllib.parse.unquote("".join(t for pp in dmp.patch_fromText(str(p)) for op,t in pp.diffs if op>=0))
    except: return ""
def navval(w):
    m=QRE.search(w)
    if m:
        v=[float(x) for x in m.groups()]
        if all(abs(x)<=1.01 for x in v): return ("q",np.array(v))
    m=PRE.search(w)
    if m: return ("p",np.array([float(x) for x in m.groups()]))
    return (None,None)
def qang(a,b):
    d=abs(float(np.dot(a/np.linalg.norm(a),b/np.linalg.norm(b)))); return math.degrees(2*math.acos(min(1,d)))
def feats(sessions):
    seqs=["".join(t for t,_ in s) for s in sessions]; allb="".join(seqs); n=len(allb)
    if n<80 or len(sessions)<3: return None
    f={"n_events":n,"n_sessions":len(sessions),"evt_per_session":n/len(sessions)}
    for t in "NSAO": f[f"pct_{t}"]=allb.count(t)/n
    bg=collections.Counter(); tg=collections.Counter(); tb=tt=0
    for s in seqs:
        for i in range(len(s)-1): bg[s[i:i+2]]+=1; tb+=1
        for i in range(len(s)-2): tg[s[i:i+3]]+=1; tt+=1
    for m in ["NN","NS","SN","SS"]: f[f"bg_{m}"]=bg[m]/tb if tb else 0
    for m in ["NSN","SNS","NNN","SSS","NSS","SSN","NNS"]: f[f"tg_{m}"]=tg[m]/tt if tt else 0
    def runs(ch):
        L=[len(r) for r in re.findall(ch+"+",allb)]; return (np.mean(L),np.max(L)) if L else (0,0)
    f["runN_mean"],f["runN_max"]=runs("N"); f["runS_mean"],f["runS_max"]=runs("S")
    ps=[allb.count(t)/n for t in "NSAO" if allb.count(t)]; f["entropy"]=-sum(p*math.log(p) for p in ps)
    return f
rows=[]
for u in users:
    df=nq.get_tasks(sieve={"assignee":u,"namespace":"multiSomaId","status":"closed"}, select=["seg_id"], convert_states_to_json=False, limit=40, pageSize=40)
    if df.empty: print(f"{u}: 0 multiSomaId",flush=True); continue
    ids=[str(x) for x in df.reset_index(names="t")["t"]]; S=[]; dts=[]; Q=[]; P=[]; ev=0
    for i in range(0,len(ids),20):
        try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except: continue
        for _,row in ds.iterrows():
            st=row["differ_stack"]
            if not isinstance(st,list) or len(st)<3: continue
            seq=[]
            for e in sorted([x for x in st if isinstance(x,dict)],key=lambda z:z.get("timestamp",0)):
                lb=lab(e.get("patch","")); ts=(e.get("timestamp",0) or 0)/1000.0; seq.append((lb,ts)); ev+=1
                if lb=="N":
                    k,v=navval(newwin(e.get("patch","")))
                    if k=="q": Q.append(v)
                    elif k=="p": P.append(v)
            if seq:
                S.append(seq); ts=[t for _,t in seq]; dts+=[b-a for a,b in zip(ts,ts[1:]) if 0.05<b-a<120]
        if ev>=2500: break
    f=feats(S)
    if not f: print(f"{u}: insufficient ({ev} ev)",flush=True); continue
    f["dt_med"]=float(np.median(dts)) if dts else np.nan; f["dt_longfrac"]=float(np.mean([d>5 for d in dts])) if dts else np.nan
    f["total_rot_deg"]=float(np.sum([qang(Q[i],Q[i+1]) for i in range(len(Q)-1)])) if len(Q)>1 else 0
    f["n_rot"]=len(Q); f["viewpoint_div"]=float(np.mean([qang(Q[i],Q[j]) for i in range(min(8,len(Q))) for j in range(i+1,min(8,len(Q)))])) if len(Q)>2 else 0
    f["total_pan"]=float(np.sum([np.linalg.norm(P[i+1]-P[i]) for i in range(len(P)-1)])) if len(P)>1 else 0
    f["assignee"]=u; f["cohort"]=group; rows.append(f); print(f"{u}: {ev} events, features ok",flush=True)
pd.DataFrame(rows).to_csv(OUT/f"rich_crosstask_{group}.csv",index=False)
print(f"saved rich_crosstask_{group}.csv ({len(rows)} annotators)",flush=True)
