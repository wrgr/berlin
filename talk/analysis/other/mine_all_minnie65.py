"""Comprehensive behavior mining across ALL minnie65 namespaces.
Behavior dictionary per task type (the 'language' taxonomy) + per-user profiles.
"""
import sys, json, ast, http.client, urllib.parse, re, collections
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent; OUT=HERE/"live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE/"neuvue-client")); pd.set_option("display.width",240)
tok=json.loads((HERE/".nv_tokens.json").read_text())
conn=http.client.HTTPSConnection("queue.neuvue.io",timeout=25)
conn.request("POST","/auth/tokens",json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}),{"content-type":"application/json"})
raw=conn.getresponse().read().decode(); new=json.loads(raw) if raw.strip().startswith("{") else ast.literal_eval(raw)
tok["access_token"]=new["access_token"]; (HERE/".nv_tokens.json").write_text(json.dumps(tok))
from neuvueclient import NeuvueQueue
c=NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])

NAMESPACES=["agentsExpert","agentsExpertV2","agentsTraining","automatedSplit","automatedSplitAdjustment",
"automatedSplitAdjustmentTraining","automatedSplitFind","automatedSplitGroup","automatedSplitTraining","axonExtension",
"axonOnAxon","axonOnDendrite","axonOnDendriteV2","axonOnDendriteV3","axonOnDendriteV3_review","crimsonGocTraining",
"dendExtensionLevel1","dendExtensionLevel2","dendExtensionLevel3","dendExtensionLevel4","dendExtensionSelection",
"dendExtensionTips","fullyProofread","functionalCellClean","multiSomaId","multiSomaSplit","neuronOtherBodies",
"neuronScreening","neuronScreeningV2","neuronScreeningVR","patProofread","reverseExtension","singleSomaCleanUp",
"somaSomaReview","somaSomaSplit","split"]
ANN={"description","tagId","tagIds","tags","annotation","annotations","annotationColor","point","pointA","pointB","parentId"}
NAV={"position","voxelCoordinates","projectionOrientation","crossSectionOrientation","projectionScale","crossSectionScale","zoomFactor","perspectiveOrientation","perspectiveZoom","pose"}
PATH={"hasPath","pathFinder","pathObject","annotationPath","source","target"}
def lab(patch):
    d=urllib.parse.unquote(str(patch)); add=rm=hexid=0
    for ln in d.split("\n"):
        if ln[:1] in ("+","-"):
            n=len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])",ln)); add+=n if ln[:1]=="+" else 0; rm+=n if ln[:1]=="-" else 0
            if re.search(r"[0-9a-f]{32,40}",ln): hexid+=1
    kset=set(re.findall(r'"([A-Za-z_]\w*)"\s*:',d))
    if add or rm: return "segment"
    if (kset&ANN) or hexid or ({"type","id"}<=kset): return "annotate"
    if kset&PATH: return "trace"
    if (kset&NAV): return "navigate"
    body=re.sub(r"@@[^@]*@@","",d); return "navigate" if len(re.sub(r"[^A-Za-z]","",body))<=4 else "other"

rows=[]; cov=[]
for ki,ns in enumerate(NAMESPACES):
    try:
        tk=c.get_tasks(sieve={"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee"],
                       convert_states_to_json=False, limit=700, pageSize=1000)
    except Exception as e:
        print(f"[{ki+1}/{len(NAMESPACES)}] {ns}: task query failed", flush=True); continue
    if tk.empty: print(f"[{ki+1}/{len(NAMESPACES)}] {ns}: 0 tasks", flush=True); continue
    tk=tk.reset_index(names="task_id"); tk["task_id"]=tk["task_id"].astype(str)
    a={r.task_id:r.assignee for r in tk.itertuples()}; ids=list(a); ev=0
    for i in range(0,len(ids),20):
        try: ds=c.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+20]},"active":True}, pageSize=1000)
        except Exception: continue
        for did,row in ds.iterrows():
            st=row["differ_stack"]
            if not isinstance(st,list): continue
            for o,e in enumerate(st):
                if isinstance(e,dict):
                    rows.append({"ns":ns,"assignee":a.get(str(row["task_id"])),"sid":str(did),"behavior":lab(e.get("patch","")),"ts":e.get("timestamp")}); ev+=1
        if ev>=2000: break
    cov.append({"namespace":ns,"tasks":len(tk),"events":ev}); print(f"[{ki+1}/{len(NAMESPACES)}] {ns}: tasks={len(tk)} events={ev}", flush=True)

E=pd.DataFrame(rows); pd.DataFrame(cov).to_csv(OUT/"all_ns_coverage.csv",index=False)
E.to_csv(OUT/"all_ns_events.csv",index=False)
print(f"\nTOTAL: {len(E)} events | {E['sid'].nunique()} sessions | {E['assignee'].nunique()} users | {E['ns'].nunique()} namespaces with differstacks", flush=True)
# behavior dictionary overall + by namespace
print("\n=== overall behavior dictionary ==="); print((E["behavior"].value_counts(normalize=True)*100).round(1).to_string())
mix=E.groupby(["ns","behavior"]).size().unstack(fill_value=0)
mixn=(mix.div(mix.sum(axis=1),axis=0)*100).round(1); mixn.to_csv(OUT/"all_ns_behavior_mix.csv")
# heatmap: namespace x behavior
order=E["behavior"].value_counts().index.tolist()
mh=mixn.reindex(columns=order,fill_value=0)
fig,ax=plt.subplots(figsize=(2+1.1*len(order),0.35*len(mh)+2))
im=ax.imshow(mh.values,cmap="magma",aspect="auto",vmin=0,vmax=100)
ax.set_xticks(range(len(order))); ax.set_xticklabels(order,rotation=45,ha="right")
ax.set_yticks(range(len(mh))); ax.set_yticklabels(mh.index,fontsize=7)
ax.set_title("Proofreading language by task type (minnie65 namespaces)"); fig.colorbar(im,ax=ax,label="% of events")
fig.tight_layout(); fig.savefig(OUT/"language_by_tasktype.png",dpi=130); plt.close()
# per-user across all namespaces
U=E.groupby("assignee").agg(events=("behavior","size"),sessions=("sid","nunique"),namespaces=("ns","nunique"),
    pct_segment=("behavior",lambda s:round((s=="segment").mean()*100,1)),
    pct_navigate=("behavior",lambda s:round((s=="navigate").mean()*100,1)),
    pct_annotate=("behavior",lambda s:round((s=="annotate").mean()*100,1))).sort_values("events",ascending=False)
U.to_csv(OUT/"all_ns_user_profiles.csv")
print(f"\nsaved: all_ns_coverage.csv, all_ns_behavior_mix.csv, all_ns_user_profiles.csv, language_by_tasktype.png", flush=True)
print("\ntop namespaces by events:\n", pd.DataFrame(cov).sort_values("events",ascending=False).head(12).to_string(index=False), flush=True)
