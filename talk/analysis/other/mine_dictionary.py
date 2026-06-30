"""Mine a dictionary of proofreading behaviors from differstack patches.

Each event's `patch` is a diff-match-patch over the URL-encoded Neuroglancer
state. We read the diff lines directly:
  - 15-20 digit ints on +/- lines  -> segment IDs added/removed (merge/split-type)
  - 32-40 hex ids                  -> annotation/object ids
  - decimals                       -> coordinates (navigation)
  - JSON keys "<key>":             -> the NG state field that changed
and map NG fields -> human-readable behaviors.
"""
import sys, json, ast, base64, http.client, urllib.parse, re, collections
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE/"live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE/"neuvue-client"))
pd.set_option("display.width",200); pd.set_option("display.max_colwidth",60)

# refresh token + client
tok = json.loads((HERE/".nv_tokens.json").read_text())
conn = http.client.HTTPSConnection("queue.neuvue.io", timeout=25)
conn.request("POST","/auth/tokens", json.dumps({"code":tok["refresh_token"],"code_type":"refresh"}), {"content-type":"application/json"})
raw=conn.getresponse().read().decode(); new=json.loads(raw) if raw.strip().startswith("{") else ast.literal_eval(raw)
tok["access_token"]=new["access_token"]; (HERE/".nv_tokens.json").write_text(json.dumps(tok))
from neuvueclient import NeuvueQueue
c = NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])

KEY_BEHAVIOR = {
 "position":"navigate (pan)","voxelCoordinates":"navigate (pan)","crossSectionScale":"zoom (2D)",
 "projectionScale":"zoom (3D)","zoomFactor":"zoom","projectionOrientation":"rotate (3D)",
 "crossSectionOrientation":"rotate (2D)","perspectiveOrientation":"rotate (3D)","perspectiveZoom":"zoom (3D)",
 "segments":"segment select","hiddenSegments":"hide segment","equivalences":"merge group",
 "annotations":"annotation","annotation":"annotation","description":"annotation note","tagId":"annotation tag",
 "tags":"annotation tag","annotationColor":"annotation color","selectedAlpha":"opacity",
 "notSelectedAlpha":"opacity","objectAlpha":"opacity","visible":"toggle layer","archived":"archive layer",
 "colorSeed":"recolor","crossSectionBackgroundColor":"background","tab":"switch panel","tool":"switch tool",
 "selectedLayer":"select layer","layers":"layer change","name":"rename layer","title":"rename",
 "layout":"change layout","showSlices":"toggle slices","showDefaultAnnotations":"toggle annotations",
 "toolBindings":"tool binding","selectedSegments":"segment select",
}
ANN={"description","tagId","tagIds","tags","annotation","annotations","annotationColor","point","pointA","pointB","parentId"}
NAV={"position","voxelCoordinates","projectionOrientation","crossSectionOrientation","projectionScale",
     "crossSectionScale","zoomFactor","perspectiveOrientation","perspectiveZoom","pose"}
PATH={"hasPath","pathFinder","pathObject","annotationPath","source","target","childrenVisible","pathFinderState"}
DISP={"selectedAlpha","notSelectedAlpha","objectAlpha","visible","colorSeed","crossSectionBackgroundColor","tab",
      "skeletonRendering","showSlices","showAxisLines","mode2d","mode3d"}
SEGRE=re.compile(r'(?<![\d.])\d{15,20}(?![\d.])'); HEXRE=re.compile(r'\b[0-9a-f]{32,40}\b')
DECRE=re.compile(r'-?\d+\.\d+'); KEYRE=re.compile(r'"([A-Za-z_]\w*)"\s*:')

def analyze(patch):
    d=urllib.parse.unquote(str(patch))
    add=rm=hexid=dec=0
    for ln in d.split("\n"):
        h=ln[:1]
        if h in "+-":
            n=len(SEGRE.findall(ln))
            if h=="+": add+=n
            else: rm+=n
            if HEXRE.search(ln): hexid+=1
            if DECRE.search(ln): dec+=1
    keys=KEYRE.findall(d); kset=set(keys)
    is_ann = bool(kset & ANN) or hexid or ({"type","id"} <= kset)
    if add or rm:
        beh = "segment: swap (merge/split)" if (add and rm) else ("segment: add (select/merge)" if add else "segment: remove (split/deselect)")
    elif is_ann: beh="annotate (point/tag/note)"
    elif (kset & PATH): beh="trace / pathfinder"
    elif (kset & NAV) or (dec and not kset): beh="navigate (pan/zoom/rotate)"
    elif "hiddenSegments" in kset: beh="segment: hide"
    elif (kset & DISP): beh="display (opacity/visibility)"
    else:
        body=re.sub(r"@@[^@]*@@","",d)                      # strip hunk headers
        beh="navigate (pan/zoom/rotate)" if len(re.sub(r"[^A-Za-z]","",body))<=4 else "other"
    return beh, keys, add, rm

def fetch(ns, max_tasks=2000, patch_cap=5000, chunk=20):
    tk=c.get_tasks(sieve={"namespace":ns,"status":{"$in":["closed","errored"]}}, select=["assignee"],
                   convert_states_to_json=False, limit=max_tasks, pageSize=1000)
    if tk.empty: return []
    tk=tk.reset_index(names="task_id"); tk["task_id"]=tk["task_id"].astype(str)
    a={str(r.task_id):r.assignee for r in tk.itertuples()}
    ids=list(a); rows=[]
    for i in range(0,len(ids),chunk):
        try: ds=c.get_differ_stacks(sieve={"task_id":{"$in":ids[i:i+chunk]},"active":True}, pageSize=1000)
        except Exception: continue
        for did,row in ds.iterrows():
            st=row["differ_stack"]
            if not isinstance(st,list): continue
            for o,ev in enumerate(st):
                if not isinstance(ev,dict): continue
                beh,keys,add,rm=analyze(ev.get("patch",""))
                rows.append({"namespace":ns,"assignee":a.get(str(row["task_id"])),"differ_id":str(did),
                             "order":o,"behavior":beh,"keys":keys,"seg_add":add,"seg_rm":rm})
        if len(rows)>=patch_cap: break
    return rows

allrows=[]
for ns in ["multiSomaSplit","somaSomaSplit","fullyProofread","patProofread","somaSplit","somaSomaReview"]:
    r=fetch(ns); print(f"{ns:24s} events={len(r):5d} sessions={len({x['differ_id'] for x in r})} users={len({x['assignee'] for x in r})}")
    allrows+=r
ev=pd.DataFrame(allrows)
print(f"\nCORPUS: {len(ev):,} events | {ev['differ_id'].nunique()} sessions | {ev['assignee'].nunique()} proofreaders | {ev['namespace'].nunique()} namespaces")

# ---- THE BEHAVIOR DICTIONARY ----
print("\n================ DICTIONARY OF PROOFREADING BEHAVIORS ================")
bd=ev["behavior"].value_counts()
bdt=pd.DataFrame({"events":bd, "pct":(bd/len(ev)*100).round(1)})
print(bdt.to_string())
bdt.to_csv(OUT/"behavior_dictionary.csv")

# ---- empirical FIELD dictionary (NG keys that change) ----
kc=collections.Counter(k for ks in ev["keys"] for k in ks)
fd=pd.DataFrame([(k,n,KEY_BEHAVIOR.get(k,"(unmapped)")) for k,n in kc.most_common(40)],
                columns=["ng_state_key","events_seen","behavior"])
print("\n---- NG state fields observed changing (top 40) ----")
print(fd.to_string(index=False))
fd.to_csv(OUT/"field_dictionary.csv", index=False)

# ---- per-namespace behavior mix ----
mix=ev.groupby(["namespace","behavior"]).size().unstack(fill_value=0)
mixn=(mix.div(mix.sum(axis=1),axis=0)*100).round(1)
print("\n---- behavior mix by namespace (%) ----")
print(mixn.to_string())
mixn.to_csv(OUT/"behavior_by_namespace.csv")

# segment add/remove totals (merge/split proxy)
seg=ev.groupby("namespace")[["seg_add","seg_rm"]].sum()
seg["sessions"]=ev.groupby("namespace")["differ_id"].nunique()
print("\n---- segment IDs added vs removed per namespace (merge/split signal) ----")
print(seg.to_string())
seg.to_csv(OUT/"segment_add_remove.csv")

# per-user dialect (top 12 by events)
top=ev["assignee"].value_counts().head(12).index
um=ev[ev["assignee"].isin(top)].groupby(["assignee","behavior"]).size().unstack(fill_value=0)
umn=(um.div(um.sum(axis=1),axis=0)*100).round(0).astype(int)
print("\n---- behavior mix by proofreader (top 12, %) ----")
print(umn.to_string())
umn.to_csv(OUT/"behavior_by_user.csv")

# ---- figures ----
plt.figure(figsize=(9,4)); bd.head(12).iloc[::-1].plot(kind="barh", color="teal")
plt.title("Dictionary of proofreading behaviors (all namespaces)"); plt.xlabel("events"); plt.tight_layout()
plt.savefig(OUT/"behavior_dictionary.png", dpi=130); plt.close()

top_beh=bd.head(7).index
mplot=mixn.reindex(columns=top_beh, fill_value=0)
mplot.plot(kind="bar", stacked=True, figsize=(10,5), colormap="tab20")
plt.title("Behavior mix by namespace"); plt.ylabel("% of events"); plt.legend(bbox_to_anchor=(1.01,1), fontsize=8)
plt.tight_layout(); plt.savefig(OUT/"behavior_by_namespace.png", dpi=130); plt.close()

ev.drop(columns=["keys"]).to_csv(OUT/"behavior_events.csv", index=False)
print("\nsaved:", sorted(p.name for p in OUT.glob("behavior*")) + ["field_dictionary.csv","segment_add_remove.csv"])
