"""HONEST motif tier: learn the k-means motif dictionary INSIDE the CV loop.
The reported 'learned' AUC (0.95) fits the k-means dictionary + scaler on ALL annotators'
windows before the CV split (mine_tiers.py l.117-121) -> the held-out annotator's data shapes
the representation (unsupervised leakage). Here we refit scaler+k-means on TRAINING annotators
only each fold, assign the held-out annotator to the learned motifs, then classify. The gap
between leaky and nested LOO is the representation-leakage premium.

Network (re-mines the multiSomaId gestures, same logic as mine_tiers); caches windows so reruns
are offline. Creds + neuvue-client come from BERLIN_CRED (default: this dir, else scratchpad)."""
import sys, os, json, ast, http.client, re, urllib.parse, math
from pathlib import Path
import numpy as np, pandas as pd
HERE=Path(__file__).resolve().parent
CRED=Path(os.environ.get("BERLIN_CRED", HERE))
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
CACHE=OUT/"motif_windows.npz"
EXPERTS=["chris","christopher","claire","erika","gary","michael","natalie","phillips"]
STUDENTS=["aashi","clara","dylan","emma","emily","joey","jonas","katie","krutal","luzhou","mia","oji","rachel","rupa","sarah","sean_sebastian","shruthi","taylor","titus","vivia","makayla","maryam","tina","luke","trystan","cindy","lydia","donovan9","maggie"]
ANN={"description","tagId","tagIds","tags","annotation","annotations","point","pointA","pointB","parentId"}
NAVK={"position","voxelCoordinates","perspectiveOrientation","projectionOrientation","crossSectionOrientation","perspectiveZoom","projectionScale","crossSectionScale","pose"}
QRE=re.compile(r"(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,})")

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

def windows(S,W=5):
    out=[]
    for s in S:
        ev=[]
        for j,(lbl,ts,rot) in enumerate(s):
            oh=[1.0 if lbl==t else 0.0 for t in "NSAO"]; dt=0.0
            if j>0: dt=max(0.0,min(120.0,s[j][1]-s[j-1][1]))
            ev.append(oh+[math.log1p(dt),min(rot,180)/180.0])
        a=np.array(ev)
        for i in range(len(a)-W+1):
            win=a[i:i+W]; lbls=[int(np.argmax(win[t,:4])) for t in range(W)]
            out.append(list(win[:,:4].mean(0))+[float(win[:,4].mean()),float(win[:,4].std()),float(win[:,5].mean()),sum(1 for x,y in zip(lbls,lbls[1:]) if x!=y)/(W-1)])
    return out

def extract():
    sys.path.insert(0,str(CRED/"neuvue-client"))
    import diff_match_patch as dmpmod; dmp=dmpmod.diff_match_patch()
    def newwin(p):
        try: return urllib.parse.unquote("".join(t for pp in dmp.patch_fromText(str(p)) for op,t in pp.diffs if op>=0))
        except: return ""
    def qval(w):
        m=QRE.search(w)
        if m:
            v=[float(x) for x in m.groups()]
            if all(abs(x)<=1.01 for x in v): return np.array(v)
        return None
    def qang(a,b):
        d=abs(float(np.dot(a/np.linalg.norm(a),b/np.linalg.norm(b)))); return math.degrees(2*math.acos(min(1,d)))
    tok=json.loads((CRED/".nv_tokens.json").read_text())
    c=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
    c.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
    raw=c.getresponse().read().decode()
    try: tok["access_token"]=json.loads(raw)["access_token"]
    except: tok["access_token"]=ast.literal_eval(raw)["access_token"]
    from neuvueclient import NeuvueQueue
    nq=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
    DATA={}
    for u in EXPERTS+STUDENTS:
        try:
            df=nq.get_tasks(sieve={"assignee":u,"namespace":"multiSomaId","status":"closed"}, select=["seg_id"], convert_states_to_json=False, limit=40, pageSize=40)
        except Exception as e:
            print(f"{u}: query err {e}",flush=True); continue
        if df.empty: continue
        ids=[str(x) for x in df.reset_index(names="t")["t"]]; Sx=[]; ev=0
        for i in range(0,len(ids),20):
            try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
            except: continue
            for _,row in ds.iterrows():
                st=row["differ_stack"]
                if not isinstance(st,list) or len(st)<3: continue
                seq=[]; prevq=None
                for e in sorted([x for x in st if isinstance(x,dict)],key=lambda z:z.get("timestamp",0)):
                    lb=lab(e.get("patch","")); ts=(e.get("timestamp",0) or 0)/1000.0; rot=0.0
                    if lb=="N":
                        qv=qval(newwin(e.get("patch","")))
                        if qv is not None:
                            if prevq is not None: rot=qang(prevq,qv)
                            prevq=qv
                    seq.append((lb,ts,rot)); ev+=1
                if seq: Sx.append(seq)
            if ev>=2200: break
        if ev>=120 and len(Sx)>=3:
            DATA[u]=np.array(windows(Sx)); print(f"{u}: {ev} ev, {len(Sx)} sess, {len(DATA[u])} windows",flush=True)
    return DATA

# ---- load or extract windows ----
if CACHE.exists():
    z=np.load(CACHE,allow_pickle=True); DATA={k:z[k] for k in z.files}; print("loaded cached windows (%d annotators)"%len(DATA),flush=True)
else:
    DATA=extract(); np.savez(CACHE,**DATA); print("cached windows -> %s"%CACHE,flush=True)

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
K=10
# align to the canonical tiers_data cohort if available
try:
    tiers=pd.read_csv(OUT/"tiers_data.csv"); users=[u for u in tiers.assignee if u in DATA]
except Exception:
    users=list(DATA)
y=np.array([1 if u in EXPERTS else 0 for u in users])
print("\nn=%d (%dE / %dP)"%(len(users),int(y.sum()),int((y==0).sum())),flush=True)

def histify(km,sc,w):
    l=km.predict(sc.transform(w)); h=np.bincount(l,minlength=K).astype(float); s=h.sum(); return h/s if s else h

# LEAKY: scaler+kmeans on ALL annotators, then LOO-classify
allw=np.vstack([DATA[u] for u in users]); sc=StandardScaler().fit(allw); km=KMeans(K,n_init=10,random_state=0).fit(sc.transform(allw))
Xleak=np.array([histify(km,sc,DATA[u]) for u in users])
def loo_clf(X,yy):
    pr=np.zeros(len(yy))
    for i in range(len(yy)):
        tr=[j for j in range(len(yy)) if j!=i]
        pr[i]=LogisticRegression(max_iter=1000,class_weight="balanced").fit(X[tr],yy[tr]).predict_proba(X[i:i+1])[0,1]
    return roc_auc_score(yy,pr)
leaky=loo_clf(Xleak,y)

# NESTED: refit scaler+kmeans on TRAIN annotators each fold
pr=np.zeros(len(users))
for i in range(len(users)):
    tr=[j for j in range(len(users)) if j!=i]
    trw=np.vstack([DATA[users[j]] for j in tr]); s2=StandardScaler().fit(trw); k2=KMeans(K,n_init=10,random_state=0).fit(s2.transform(trw))
    Xtr=np.array([histify(k2,s2,DATA[users[j]]) for j in tr])
    clf=LogisticRegression(max_iter=1000,class_weight="balanced").fit(Xtr,y[tr])
    pr[i]=clf.predict_proba(histify(k2,s2,DATA[users[i]]).reshape(1,-1))[0,1]
nested=roc_auc_score(y,pr)

print("\n=== MOTIF TIER: leakage premium ===",flush=True)
print("  LEAKY  (k-means on all 16, then LOO-classify): AUC=%.2f"%leaky,flush=True)
print("  NESTED (k-means refit on train fold only):     AUC=%.2f"%nested,flush=True)
print("  => representation-leakage premium = %.2f"%(leaky-nested),flush=True)
print("DONE",flush=True)
