"""Map all cohort handles -> CAVE identity -> acknowledgment edit-count (credited axis),
expand the cohort model to full N, and test whether rich features separate
credited vs not-credited (esp. within students).
"""
import sys, json, ast, http.client, collections, re
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
def md(m,k): return (m or {}).get(k) if isinstance(m,dict) else None
F=pd.concat([pd.read_csv(OUT/"rich_crosstask_expert.csv"),pd.read_csv(OUT/"rich_crosstask_student.csv")])
handles=list(F["assignee"].unique())
# 1) handle -> dominant CAVE user_id via operation 'user'
h2ops={}
for u in handles:
    ops=[]
    for ns in ["multiSomaId","neuronOtherBodies","singleSomaCleanUp"]:
        df=nq.get_tasks(sieve={"assignee":u,"namespace":ns,"status":"closed"}, select=["seg_id","metadata"], convert_states_to_json=False, limit=30, pageSize=30)
        for m in df["metadata"]:
            for o in (md(m,"operation_ids") or []):
                try: ops.append(int(o))
                except: pass
    h2ops[u]=ops[:40]
allops=sorted({o for v in h2ops.values() for o in v}); det={}
for i in range(0,len(allops),120):
    try: det.update(cl.chunkedgraph.get_operation_details(allops[i:i+120]))
    except: pass
op2u={int(o):d.get("user") for o,d in det.items()}
h2uid={}
for u,ops in h2ops.items():
    uu=[op2u.get(o) for o in ops if op2u.get(o)]
    if uu: h2uid[u]=collections.Counter(uu).most_common(1)[0][0]
# 2) resolve uid->name from change logs
id2name={}
roots=[]
for u in handles[:18]:
    df=nq.get_tasks(sieve={"assignee":u,"namespace":"multiSomaId","status":"closed"}, select=["seg_id"], convert_states_to_json=False, limit=3, pageSize=3)
    roots+=[int(x) for x in df["seg_id"].dropna().astype(str) if x.isdigit()]
for r in roots[:30]:
    try:
        lg=cl.chunkedgraph.get_tabular_change_log([r])[r]
        for _,row in lg.iterrows():
            if pd.notna(row.get("user_id")): id2name[int(row["user_id"])]=row.get("user_name")
    except Exception: pass
# 3) acknowledgment list (initial,last,edits)
ACK=[("N","smith",24101),("D","panchal",19384),("M","cook",17088),("C","ordish",14333),("Z","sorangwala",13777),("K","shah",10570),("D","patel",10368),("A","rajput",8674),("C","smith",8281),("C","knecht",7199),("S","pal",7036),("D","rami",6850),("K","raval",5638),("D","dalal",5597),("E","phillips",5454),("G","hopkins",4505),("A","pandey",2426),("D","parodi",1007),("R","xu",947),("C","moore",828),("V","lung",804),("S","wu",746),("T","gaito",643),("J","gayk",570),("L","fozo",506),("M","baptiste",416),("E","macgregor",383),("E","miranda",354),("S","bare",220)]
def matchack(nm):
    if not nm: return (None,0)
    parts=str(nm).split()
    if len(parts)<2: return (None,0)
    fi=parts[0][0].lower(); last=parts[-1].lower()
    for I,L,ed in ACK:
        if L==last and I.lower()==fi: return (f"{I}. {L.title()}",ed)
    for I,L,ed in ACK:
        if L==last: return (f"{I}. {L.title()} (lastname-only)",ed)
    return (None,0)
rows=[]
for u in handles:
    uid=h2uid.get(u); nm=id2name.get(uid) if uid else None; ack,ed=matchack(nm)
    rows.append({"assignee":u,"cave_uid":uid,"real_name":nm,"ack_match":ack,"edit_count":ed,"credited":int(ed>0)})
ID=pd.DataFrame(rows); ID.to_csv(OUT/"handle_identities.csv",index=False)
print("=== handle -> identity -> acknowledgment ==="); print(ID.to_string(index=False),flush=True)
# 4) models on full feature N
M=F.merge(ID[["assignee","credited","edit_count","real_name"]],on="assignee")
FEATS=[c for c in F.columns if c not in ("assignee","cohort") and F[c].dtype!=object]
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
X=M[FEATS].fillna(M[FEATS].median())
print(f"\nfull feature N: {len(M)} ({(M.cohort=='expert').sum()} expert, {(M.cohort=='student').sum()} student); credited={M['credited'].sum()}",flush=True)
def clf(y,lab,Xx):
    if y.nunique()<2 or min(y.value_counts())<3: print(f"  {lab}: too few in a class"); return
    rf=RandomForestClassifier(n_estimators=600,min_samples_leaf=2,random_state=0)
    auc=cross_val_score(rf,Xx,y,cv=StratifiedKFold(5,shuffle=True,random_state=0),scoring="roc_auc")
    rf.fit(Xx,y); imp=pd.Series(rf.feature_importances_,index=Xx.columns).sort_values(ascending=False)
    print(f"  {lab}: CV ROC-AUC={auc.mean():.2f}+/-{auc.std():.2f} | top: {list(imp.head(5).index)}",flush=True)
print("\n[expert vs student] full N:"); clf((M.cohort=="expert").astype(int),"cohort",X)
print("[credited vs not] all:"); clf(M["credited"],"credited",X)
S=M[M.cohort=="student"]
print(f"[credited vs not] WITHIN students (n={len(S)}, credited={S['credited'].sum()}):")
clf(S["credited"],"credited|student",S[FEATS].fillna(S[FEATS].median()))