"""NAIVE vs DESIGNED vs LEARNED behavioral representations -> recover cohort & PROMOTED labels.
- naive    = a few obvious counts (n_events, rate, %navigate, median interval)
- designed = the full hand-built rich bank (behavior-mix, grammar, motifs, runs, entropy, 3D kinematics)
- learned  = UNSUPERVISED motif dictionary: k-means 'gestures' over windowed event streams
             (timing+label+rotation), each annotator = histogram over learned motifs.
             This is the 'language of surgery' analog (learned surgemes), not hand-picked.
One pass over the dense common task (multiSomaId) for all annotators.
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
STUDENTS=["aashi","clara","dylan","emma","emily","joey","jonas","katie","krutal","luzhou","mia","oji","rachel","rupa","sarah","sean_sebastian","shruthi","taylor","titus","vivia","makayla","maryam","tina","luke","trystan","cindy","lydia","donovan9","maggie"]
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
    except: return ""
def qval(w):
    m=QRE.search(w)
    if m:
        v=[float(x) for x in m.groups()]
        if all(abs(x)<=1.01 for x in v): return np.array(v)
    return None
def qang(a,b):
    d=abs(float(np.dot(a/np.linalg.norm(a),b/np.linalg.norm(b)))); return math.degrees(2*math.acos(min(1,d)))
# ---- 1) extract per-annotator event streams: list of sessions, each = [(label, ts, rot_deg)] ----
DATA={}
for u in EXPERTS+STUDENTS:
    try:
        df=nq.get_tasks(sieve={"assignee":u,"namespace":"multiSomaId","status":"closed"}, select=["seg_id"], convert_states_to_json=False, limit=40, pageSize=40)
    except Exception as e:
        print(f"{u}: query err {e}",flush=True); continue
    if df.empty: print(f"{u}: 0 tasks",flush=True); continue
    ids=[str(x) for x in df.reset_index(names="t")["t"]]; S=[]; ev=0; Q=[]
    for i in range(0,len(ids),20):
        try: ds=nq.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except: continue
        for _,row in ds.iterrows():
            st=row["differ_stack"]
            if not isinstance(st,list) or len(st)<3: continue
            seq=[]
            for e in sorted([x for x in st if isinstance(x,dict)],key=lambda z:z.get("timestamp",0)):
                lb=lab(e.get("patch","")); ts=(e.get("timestamp",0) or 0)/1000.0; rot=0.0
                if lb=="N":
                    qv=qval(newwin(e.get("patch","")))
                    if qv is not None:
                        if Q: rot=qang(Q[-1],qv)
                        Q.append(qv)
                seq.append((lb,ts,rot)); ev+=1
            if seq: S.append(seq)
        if ev>=2200: break
    if ev>=120 and len(S)>=3: DATA[u]=S; print(f"{u}: {ev} events, {len(S)} sessions ok",flush=True)
    else: print(f"{u}: insufficient ({ev} ev / {len(S)} sess)",flush=True)
# ---- 2) naive + designed features ----
def feats(S):
    seqs=["".join(t for t,_,_ in s) for s in S]; allb="".join(seqs); n=len(allb)
    f={"n_events":n,"n_sessions":len(S),"evt_per_session":n/len(S)}
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
    dts=[]
    for s in S:
        ts=[t for _,t,_ in s]; dts+=[b-a for a,b in zip(ts,ts[1:]) if 0.05<b-a<120]
    f["dt_med"]=float(np.median(dts)) if dts else np.nan; f["dt_longfrac"]=float(np.mean([d>5 for d in dts])) if dts else np.nan
    rots=[r for s in S for _,_,r in s if r>0]
    f["total_rot_deg"]=float(np.sum(rots)); f["n_rot"]=len(rots); f["mean_rot"]=float(np.mean(rots)) if rots else 0
    return f
# ---- 3) LEARNED motif dictionary: window the event stream, k-means gestures ----
def windows(S,W=5):
    out=[]
    for s in S:
        ev=[]
        for j,(lb,ts,rot) in enumerate(s):
            oh=[1.0 if lb==t else 0.0 for t in "NSAO"]
            dt=0.0
            if j>0: dt=max(0.0,min(120.0,s[j][1]-s[j-1][1]))
            ev.append(oh+[math.log1p(dt),min(rot,180)/180.0])
        a=np.array(ev)
        for i in range(len(a)-W+1):
            win=a[i:i+W]; lbls=[int(np.argmax(win[t,:4])) for t in range(W)]
            out.append(list(win[:,:4].mean(0))+[float(win[:,4].mean()),float(win[:,4].std()),float(win[:,5].mean()),sum(1 for x,y in zip(lbls,lbls[1:]) if x!=y)/(W-1)])
    return out
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
allwin=[]; idx={}
for u,S in DATA.items():
    w=windows(S); idx[u]=(len(allwin),len(allwin)+len(w)); allwin+=w
K=10; sc=StandardScaler().fit(np.array(allwin)); Xs=sc.transform(np.array(allwin))
km=KMeans(K,n_init=10,random_state=0).fit(Xs); LB=km.labels_
learned={}
for u,(a,b) in idx.items():
    h=np.bincount(LB[a:b],minlength=K).astype(float); s=h.sum(); h=h/s if s else h
    learned[u]={f"motif_{k}":h[k] for k in range(K)}
# motif interpretation (centroid in original feature space)
cent=sc.inverse_transform(km.cluster_centers_)
cols=["fN","fS","fA","fO","meanlogdt","stdlogdt","meanrot","changefrac"]
print("\n=== learned motif dictionary (centroids) ===",flush=True)
print(pd.DataFrame(cent,columns=cols).round(2).to_string(),flush=True)
# ---- 4) assemble + three-tier comparison ----
rows=[]
for u,S in DATA.items():
    f=feats(S); f.update(learned[u]); f["assignee"]=u
    f["cohort"]="expert" if u in EXPERTS else "student"; f["promoted"]=int(u in PROMOTED); rows.append(f)
M=pd.DataFrame(rows); M.to_csv(OUT/"tiers_data.csv",index=False)
NAIVE=["n_events","evt_per_session","pct_N","dt_med"]
LEARNED=[c for c in M.columns if c.startswith("motif_")]
DESIGNED=[c for c in M.columns if c not in ("assignee","cohort","promoted") and not c.startswith("motif_")]
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
def auc(fe,y,sub):
    Xx=sub[fe].fillna(sub[fe].median())
    if y.nunique()<2 or min(y.value_counts())<3: return None
    rf=RandomForestClassifier(400,min_samples_leaf=2,random_state=0)
    return cross_val_score(rf,Xx,y,cv=StratifiedKFold(min(5,min(y.value_counts())),shuffle=True,random_state=0),scoring="roc_auc").mean()
print(f"\n=== THREE-TIER recovery (CV ROC-AUC). N={len(M)} ({(M.cohort=='expert').sum()}E/{(M.cohort=='student').sum()}S) ===",flush=True)
ST=M[M.cohort=="student"]
print(f"promoted students with features: {sorted(ST[ST.promoted==1].assignee.tolist())}",flush=True)
print(f"non-promoted students with features: {sorted(ST[ST.promoted==0].assignee.tolist())}",flush=True)
for name,y,sub in [("expert_vs_student",(M.cohort=='expert').astype(int),M),("promoted_within_students",ST["promoted"],ST)]:
    print(f"\n[{name}] n={len(sub)} pos={int(y.sum())}",flush=True)
    for nm,fe in [("naive",NAIVE),("designed",DESIGNED),("learned",LEARNED)]:
        a=auc(fe,y,sub); print(f"   {nm:9s} ({len(fe):2d} feats): AUC={a:.2f}" if a is not None else f"   {nm:9s}: too few in a class",flush=True)
print("\nsaved tiers_data.csv",flush=True)
