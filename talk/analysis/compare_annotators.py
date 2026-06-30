#!/usr/bin/env python3
"""Compare two annotators' proofreading STYLE / LANGUAGE on a shared task type.

Pulls each annotator's per-event behavioral streams from NeuVue (differstacks) and prints a
side-by-side behavioral fingerprint: activity, action-mix, the navigate<->segment transition
grammar, tempo, and 3-D exploration kinematics. Same feature definitions as the deck figures
(see ../figure_descriptions.md) and the same extraction logic as extract_streams.py.

EXAMPLE
  python compare_annotators.py --users chris rivlipk1 --task axonOnDendriteV3

IMPORTANT — style/language lives in NeuVue, not CAVE. This needs, in THIS directory:
  .nv_tokens.json    NeuVue *refresh* token (NOT the 32-hex CAVE token) — not committed
  neuvue-client/     the aplbrain/neuvue-client checkout on the import path
and network egress to queue.neuvue.io. The CAVE token only unlocks morphology (cave_*.py),
which is not where proofreading style is measured.

CAVEAT — overlap. A within-task-type comparison is only valid if BOTH annotators have dense
telemetry in the SAME task type. Pat (`rivlipk1`, a grader) has differstacks only in
axonOnAxon / axonOnDendriteV3 / neuronOtherBodies; chris is documented heavy on
singleSomaCleanUp (where Pat has none). Pick a type both actually worked, or the script reports
"no shared telemetry" rather than comparing apples to oranges.
"""
import os, sys, json, ast, http.client, re, urllib.parse, math, argparse
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE / "neuvue-client"))

# ---- behavior labeling + quaternion helpers (identical to extract_streams.py) ----
import diff_match_patch as dmpmod; dmp = dmpmod.diff_match_patch()
ANN = {"description","tagId","tagIds","tags","annotation","annotations","point","pointA","pointB","parentId"}
NAVK = {"position","voxelCoordinates","perspectiveOrientation","projectionOrientation","crossSectionOrientation","perspectiveZoom","projectionScale","crossSectionScale","pose"}
QRE = re.compile(r"(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,}),(-?\d?\.\d{3,})")

def lab(p):
    d = urllib.parse.unquote(str(p)); add = rm = hexid = 0
    for ln in d.split("\n"):
        if ln[:1] in ("+", "-"):
            n = len(re.findall(r"(?<![\d.])\d{15,20}(?![\d.])", ln)); add += n if ln[:1] == "+" else 0; rm += n if ln[:1] == "-" else 0
            if re.search(r"[0-9a-f]{32,40}", ln): hexid += 1
    k = set(re.findall(r'"([A-Za-z_]\w*)"\s*:', d))
    if add or rm: return "S"
    if (k & ANN) or hexid: return "A"
    if (k & NAVK): return "N"
    b = re.sub(r"@@[^@]*@@", "", d); return "N" if len(re.sub(r"[^A-Za-z]", "", b)) <= 4 else "O"

def newwin(p):
    try: return urllib.parse.unquote("".join(t for pp in dmp.patch_fromText(str(p)) for op, t in pp.diffs if op >= 0))
    except Exception: return ""

def qval(w):
    mm = QRE.search(w)
    if mm:
        v = [float(x) for x in mm.groups()]
        if all(abs(x) <= 1.01 for x in v): return np.array(v)
    return None

def qang(a, b):
    d = abs(float(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b)))); return math.degrees(2 * math.acos(min(1, d)))

# ---- NeuVue access (accepts any of the three credential conventions) ----
QUEUE_URL = os.getenv("NEUVUE_QUEUE_URL", "https://queue.neuvue.io")

def neuvue_queue():
    """Authenticate via, in order of preference:
      1. NEUVUEQUEUE_ACCESS_TOKEN + NEUVUEQUEUE_REFRESH_TOKEN env vars  (notebook convention)
      2. ~/.neuvuequeue/neuvuequeue.cfg                                  (interactive login() output)
      3. ./.nv_tokens.json {refresh_token}                              (run_all.py convention)
    NB: the 32-hex CAVE token is NOT a NeuVue credential and will not work here.
    """
    from neuvueclient import NeuvueQueue  # needs the aplbrain/neuvue-client checkout on sys.path
    acc, ref = os.getenv("NEUVUEQUEUE_ACCESS_TOKEN"), os.getenv("NEUVUEQUEUE_REFRESH_TOKEN")
    if acc and ref:
        return NeuvueQueue(QUEUE_URL, token=True, access_token=acc, refresh_token=ref)
    if (Path.home() / ".neuvuequeue" / "neuvuequeue.cfg").exists():
        return NeuvueQueue(QUEUE_URL)  # client reads the cfg itself
    nvfile = HERE / ".nv_tokens.json"
    if nvfile.exists():
        tok = json.loads(nvfile.read_text())
        c = http.client.HTTPSConnection("queue.neuvue.io", timeout=25)
        c.request("POST", "/auth/tokens", json.dumps({"code": tok["refresh_token"], "code_type": "refresh"}), {"content-type": "application/json"})
        raw = c.getresponse().read().decode()
        try: tok["access_token"] = json.loads(raw)["access_token"]
        except Exception: tok["access_token"] = ast.literal_eval(raw)["access_token"]
        return NeuvueQueue(QUEUE_URL, token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
    raise SystemExit("No NeuVue credentials found (env vars / cfg / .nv_tokens.json). "
                     "The CAVE token does not work for NeuVue.")

def pull_sessions(nq, user, task, limit):
    """List of sessions; each session = [[label, dt_s, rot_deg], ...]."""
    try:
        df = nq.get_tasks(sieve={"assignee": user, "namespace": task, "status": "closed"},
                          select=["seg_id"], convert_states_to_json=False, limit=limit, pageSize=limit)
    except Exception as e:
        print(f"  !! {user}: get_tasks failed: {e}"); return []
    if df.empty: return []
    ids = [str(x) for x in df.reset_index(names="t")["t"]]; sessions = []; ev = 0
    for i in range(0, len(ids), 20):
        try: ds = nq.get_differ_stacks(sieve={"task_id": {"$in": ids[i:i+20]}, "active": True}, pageSize=1000)
        except Exception: continue
        for _, row in ds.iterrows():
            st = row["differ_stack"]
            if not isinstance(st, list) or len(st) < 3: continue
            seq = []; prevq = None; pts = None
            for e in sorted([x for x in st if isinstance(x, dict)], key=lambda z: z.get("timestamp", 0)):
                lb = lab(e.get("patch", "")); ts = (e.get("timestamp", 0) or 0) / 1000.0; rot = 0.0
                if lb == "N":
                    qv = qval(newwin(e.get("patch", "")))
                    if qv is not None:
                        if prevq is not None: rot = qang(prevq, qv)
                        prevq = qv
                dt = 0.0 if pts is None else max(0.0, ts - pts); pts = ts
                seq.append([lb, round(dt, 2), round(rot, 1)]); ev += 1
            if len(seq) >= 3: sessions.append(seq)
        if ev >= 4000: break
    return sessions

# ---- the behavioral fingerprint ----
def fingerprint(sessions):
    evs = [e for s in sessions for e in s]
    n = len(evs)
    if not n: return None
    labs = [e[0] for e in evs]
    mix = {k: labs.count(k) / n for k in "NSAO"}
    # transition grammar over N/S (the deck's navigate<->segment grammar)
    T = {a: {b: 0 for b in "NS"} for a in "NS"}
    for s in sessions:
        ls = [e[0] for e in s if e[0] in "NS"]
        for a, b in zip(ls, ls[1:]): T[a][b] += 1
    def rownorm(a):
        tot = sum(T[a].values()); return {b: (T[a][b] / tot if tot else float("nan")) for b in "NS"}
    gram = {a: rownorm(a) for a in "NS"}
    dts = [e[1] for s in sessions for e in s[1:] if e[1] > 0]
    rots = [e[2] for e in evs if e[2] > 0]
    return {
        "tasks_sessions": len(sessions), "events": n,
        "events_per_session": n / len(sessions),
        "mix": mix,
        "SS_persist": gram["S"]["S"], "NN_persist": gram["N"]["N"], "switch_rate": gram["N"]["S"],
        "median_dt_s": float(np.median(dts)) if dts else float("nan"),
        "total_rotation_deg": float(np.sum(rots)),
        "n_rotation_events": len(rots),
        "rotation_per_session": float(np.sum(rots)) / len(sessions),
    }

def fmt(v): return "  n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:6.2f}"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--users", nargs=2, default=["chris", "rivlipk1"], help="two NeuVue handles")
    ap.add_argument("--task", default="axonOnDendriteV3", help="task-type namespace BOTH worked")
    ap.add_argument("--limit", type=int, default=60, help="max tasks per user")
    ap.add_argument("--offline", action="store_true", help=f"load {OUT}/compare_<task>.json instead of querying")
    a = ap.parse_args()
    u1, u2 = a.users
    cache = OUT / f"compare_{a.task}.json"

    if a.offline:
        data = json.loads(cache.read_text())
    else:
        nq = neuvue_queue()
        data = {u: pull_sessions(nq, u, a.task, a.limit) for u in (u1, u2)}
        cache.write_text(json.dumps(data))
        print(f"cached streams -> {cache.name}")

    fps = {u: fingerprint(data.get(u, [])) for u in (u1, u2)}
    print(f"\n=== proofreading style: {u1}  vs  {u2}   (task type: {a.task}) ===")
    for u in (u1, u2):
        if not fps[u]:
            print(f"  {u}: NO dense telemetry on {a.task} — can't compare on this task type.")
    if not (fps[u1] and fps[u2]):
        print("\nPick a task type both annotators actually worked (with differstacks).")
        return
    rows = [
        ("sessions (tasks)",       "tasks_sessions"),
        ("events",                 "events"),
        ("events / session",       "events_per_session"),
        ("%navigate",              ("mix", "N")), ("%segment(edit)", ("mix", "S")),
        ("%annotate",              ("mix", "A")), ("%other", ("mix", "O")),
        ("grammar S->S (persist)", "SS_persist"),
        ("grammar N->N (persist)", "NN_persist"),
        ("grammar N->S (switch)",  "switch_rate"),
        ("median dt (s, tempo)",   "median_dt_s"),
        ("total rotation (deg)",   "total_rotation_deg"),
        ("# rotation events",      "n_rotation_events"),
        ("rotation / session",     "rotation_per_session"),
    ]
    print(f"\n  {'metric':24s} {u1[:9]:>9s} {u2[:9]:>9s}")
    for label, key in rows:
        def get(fp):
            return fp[key[0]][key[1]] if isinstance(key, tuple) else fp[key]
        v1, v2 = get(fps[u1]), get(fps[u2])
        scale = 100 if isinstance(key, tuple) else 1  # show mix as %
        print(f"  {label:24s} {fmt(v1*scale):>9s} {fmt(v2*scale):>9s}")
    print("\nInterpretation: higher S->S persistence + more rotation/viewpoints = the expert"
          "\n'explore-hard, edit-in-runs' style; higher N->S switching = navigate-hop style.")
    print("NB: behavioral similarity is STYLE, not proficiency (see archive/notes/pat_proficiency_model.md).")

if __name__ == "__main__":
    main()
