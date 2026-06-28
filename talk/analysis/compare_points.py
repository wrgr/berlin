#!/usr/bin/env python3
"""Compare two annotators' RAW POINTS (not behavior) on the segments they both annotated.

These grading tasks are forced-choice POINT CLASSIFICATION: the same points are pre-placed on a
cell, and each annotator labels every point (spine / axon / dendrite / soma / nucleus / ...) via
the annotation `description`. So the points are co-located across people; the relationship that
matters is whether they put the SAME LABEL on the SAME POINT. This tool, for segments both
annotated:

  - matches each of A's points to the co-located GT point (same segment, within MATCH_NM)
  - reports per-point LABEL AGREEMENT (A vs GT) — i.e. classification agreement
  - breaks down the disagreements (which label A used where GT used another)
  - checks point coverage (did A label the same set of points GT did?)

This is the per-point view behind the deck's fullyProofread accuracy. Default pairing is chris
(fullyProofread) vs the grader Pat / rivlipk1 (patProofread GT) on the 28-cell benchmark.

Needs NeuVue creds (.nv_tokens.json / env / cfg) + the neuvueclient checkout, like the other tools.
Coordinates are mip0 voxels; nm uses VOXEL_NM = (4,4,40) for minnie65_phase3_v1.
"""
import os, sys, json, ast, http.client, argparse, collections
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "live_out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE / "neuvue-client"))
VOXEL_NM = np.array([4.0, 4.0, 40.0])
MATCH_NM = 1000.0  # a GT point this close (same segment) counts as the "same" annotation

def neuvue_queue():
    from neuvueclient import NeuvueQueue
    acc, ref = os.getenv("NEUVUEQUEUE_ACCESS_TOKEN"), os.getenv("NEUVUEQUEUE_REFRESH_TOKEN")
    if acc and ref:
        return NeuvueQueue("https://queue.neuvue.io", token=True, access_token=acc, refresh_token=ref)
    nvfile = HERE / ".nv_tokens.json"
    if nvfile.exists():
        tok = json.loads(nvfile.read_text())
        c = http.client.HTTPSConnection("queue.neuvue.io", timeout=25)
        c.request("POST", "/auth/tokens", json.dumps({"code": tok["refresh_token"], "code_type": "refresh"}), {"content-type": "application/json"})
        raw = c.getresponse().read().decode()
        try: tok["access_token"] = json.loads(raw)["access_token"]
        except Exception: tok["access_token"] = ast.literal_eval(raw)["access_token"]
        return NeuvueQueue("https://queue.neuvue.io", token=True, access_token=tok["access_token"], refresh_token=tok["refresh_token"])
    raise SystemExit("No NeuVue credentials (CAVE token does not work for NeuVue).")

def parse_pts(ngval, seg):
    """[(seg_id, label, np.array([x,y,z])), ...] from one task's ng_state.
    label = the per-point annotation `description` (the forced-choice class: spine/axon/...)."""
    out = []
    try: v = json.loads(ngval) if isinstance(ngval, str) else ngval
    except Exception: return out
    if isinstance(v, dict) and "value" in v and isinstance(v["value"], dict): v = v["value"]
    layers = v.get("layers", []) if isinstance(v, dict) else []
    if isinstance(layers, dict): layers = list(layers.values())
    for L in layers:
        if not isinstance(L, dict): continue
        anns = L.get("annotations", [])
        if not isinstance(anns, list): continue
        for a in anns:
            if not isinstance(a, dict): continue
            pt = a.get("point") or a.get("pointA") or a.get("center")
            if not pt or len(pt) < 3: continue
            lb = (a.get("description", "") or "").strip().lower()
            if not lb: continue
            out.append((str(seg), lb, np.array([float(pt[0]), float(pt[1]), float(pt[2])])))
    return out

def grab(nq, assignee, ns, lim):
    tk = nq.get_tasks(sieve={"assignee": assignee, "namespace": ns, "status": "closed"},
                      select=["seg_id", "ng_state"], convert_states_to_json=False, limit=lim, pageSize=lim)
    by_seg = collections.defaultdict(list)
    for _, r in tk.reset_index().iterrows():
        for seg, lb, pos in parse_pts(r.get("ng_state"), str(r.get("seg_id"))):
            by_seg[seg].append((lb, pos))
    return by_seg

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", default="chris"); ap.add_argument("--user-ns", default="fullyProofread")
    ap.add_argument("--gt", default="rivlipk1"); ap.add_argument("--gt-ns", default="patProofread")
    ap.add_argument("--limit", type=int, default=600)
    a = ap.parse_args()

    nq = neuvue_queue()
    A = grab(nq, a.user, a.user_ns, a.limit)
    G = grab(nq, a.gt, a.gt_ns, a.limit)
    shared = sorted(set(A) & set(G))
    print(f"\n=== raw point relationship: {a.user}/{a.user_ns}  vs  {a.gt}/{a.gt_ns} ===")
    print(f"{a.user}: {len(A)} segments, {sum(len(v) for v in A.values())} points")
    print(f"{a.gt}: {len(G)} segments, {sum(len(v) for v in G.values())} points")
    print(f"shared segments: {len(shared)}")
    if not shared:
        print("No shared segments — nothing to compare."); return

    matched, agree, disagree = 0, 0, collections.Counter()
    a_only, g_only = 0, 0
    a_lab_tot, g_lab_tot = collections.Counter(), collections.Counter()
    seg_agree = []
    for seg in shared:
        ap_, gp_ = A[seg], G[seg]
        for l, _ in ap_: a_lab_tot[l] += 1
        for l, _ in gp_: g_lab_tot[l] += 1
        gpos = np.array([p * VOXEL_NM for _, p in gp_])
        used = set(); seg_ok = seg_n = 0
        for lb, pos in ap_:
            d = np.linalg.norm(gpos - pos * VOXEL_NM, axis=1) if len(gpos) else np.array([])
            j = int(np.argmin(d)) if len(d) else -1
            if j >= 0 and d[j] <= MATCH_NM:
                matched += 1; used.add(j); seg_n += 1
                glab = gp_[j][0]
                if glab == lb: agree += 1; seg_ok += 1
                else: disagree[f"{lb} -> {glab}"] += 1   # A said {lb}, GT said {glab}
            else:
                a_only += 1
        g_only += sum(1 for k in range(len(gp_)) if k not in used)
        if seg_n: seg_agree.append(seg_ok / seg_n)

    print(f"\nco-located points compared: {matched}")
    print(f"LABEL AGREEMENT ({a.user} vs {a.gt}): {100*agree/max(1,matched):.1f}%  ({agree}/{matched})")
    if seg_agree:
        print(f"per-segment agreement: median {100*np.median(seg_agree):.0f}%, "
              f"range {100*min(seg_agree):.0f}-{100*max(seg_agree):.0f}%  (n={len(seg_agree)} segs)")
    print(f"points only {a.user} labeled: {a_only}   |   only {a.gt} labeled: {g_only}")
    if disagree:
        print(f"\ntop disagreements  ({a.user} label -> {a.gt} label):")
        for k, n in disagree.most_common(10): print(f"    {n:3d}  {k}")
    print(f"\nlabel mix {a.user}: {dict(a_lab_tot.most_common())}")
    print(f"label mix {a.gt}: {dict(g_lab_tot.most_common())}")
    print("\nNB: points are pre-placed (co-located); label = per-point `description`. "
          "Agreement, not proficiency.")

if __name__ == "__main__":
    main()
