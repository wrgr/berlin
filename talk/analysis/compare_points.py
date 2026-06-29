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
import os, sys, json, ast, re, http.client, argparse, collections
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

def canon(lb):
    """Collapse free-text descriptions to a canonical class so phrasing variants agree.
    Keeps genuine class differences (e.g. spine vs axon). Error flags take priority over anatomy."""
    s = re.sub(r"[^a-z0-9 ]", " ", lb.lower()); toks = set(s.split())
    if toks & {"falsely", "false", "split", "merge", "merged", "merger", "error", "missing", "extra"}:
        for kw in ("falsely split", "falsely merged", "merge", "split", "missing", "error"):
            if all(t in s for t in kw.split()): return kw
    if "apical" in toks: return "apical dendrite"
    for kw in ("nucleus", "soma", "cilia", "spine", "axon", "dendrite"):
        if kw in toks: return kw
    return s.strip()

def grab(nq, assignee, ns, lim):
    tk = nq.get_tasks(sieve={"assignee": assignee, "namespace": ns, "status": "closed"},
                      select=["seg_id", "ng_state"], convert_states_to_json=False, limit=lim, pageSize=lim)
    by_seg = collections.defaultdict(list)
    for _, r in tk.reset_index().iterrows():
        for seg, lb, pos in parse_pts(r.get("ng_state"), str(r.get("seg_id"))):
            by_seg[seg].append((lb, pos))
    return by_seg

def compare_one(A, G, normalize=True):
    """Match co-located points on shared segments; return agreement metrics + confusion."""
    norm = canon if normalize else (lambda x: x)
    shared = sorted(set(A) & set(G))
    matched = agree = a_only = g_only = 0
    disagree, confusion, seg_agree = collections.Counter(), collections.Counter(), []
    for seg in shared:
        ap_, gp_ = A[seg], G[seg]
        gpos = np.array([p * VOXEL_NM for _, p in gp_])
        used = set(); ok = n = 0
        for lb, pos in ap_:
            d = np.linalg.norm(gpos - pos * VOXEL_NM, axis=1) if len(gpos) else np.array([])
            j = int(np.argmin(d)) if len(d) else -1
            if j >= 0 and d[j] <= MATCH_NM:
                matched += 1; used.add(j); n += 1
                al, gl = norm(lb), norm(gp_[j][0]); confusion[(gl, al)] += 1
                if al == gl: agree += 1; ok += 1
                else: disagree[f"{al} -> {gl}"] += 1
            else: a_only += 1
        g_only += sum(1 for k in range(len(gp_)) if k not in used)
        if n: seg_agree.append(ok / n)
    return dict(shared=len(shared), matched=matched, agree=agree, a_only=a_only, g_only=g_only,
                disagree=disagree, confusion=confusion, seg_agree=seg_agree)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--users", default="chris", help="comma-separated handles")
    ap.add_argument("--user-ns", default="fullyProofread")
    ap.add_argument("--gt", default="rivlipk1"); ap.add_argument("--gt-ns", default="patProofread")
    ap.add_argument("--group", default="", help="optional label for a cohort run")
    ap.add_argument("--raw", action="store_true", help="exact-string labels (no normalization)")
    ap.add_argument("--confusion", action="store_true", help="print the confusion matrix")
    ap.add_argument("--limit", type=int, default=600)
    a = ap.parse_args()
    users = [u.strip() for u in a.users.split(",") if u.strip()]
    nq = neuvue_queue()
    G = grab(nq, a.gt, a.gt_ns, a.limit)

    print(f"\n=== point-label agreement vs {a.gt}/{a.gt_ns}"
          f"{' ['+a.group+']' if a.group else ''}  (labels: {'raw' if a.raw else 'normalized'}) ===")
    rows, agg_conf, agg_dis = [], collections.Counter(), collections.Counter()
    accs = []
    for u in users:
        A = grab(nq, u, a.user_ns, a.limit)
        m = compare_one(A, G, normalize=not a.raw)
        if not m["matched"]:
            print(f"  {u:14s} no shared points"); continue
        acc = 100 * m["agree"] / m["matched"]; accs.append(acc)
        rows.append((u, acc, m["agree"], m["matched"], m["shared"]))
        agg_conf.update(m["confusion"]); agg_dis.update(m["disagree"])
    print(f"\n  {'handle':14s} {'agree%':>7s} {'pts':>9s} {'segs':>5s}")
    for u, acc, ag, mt, sh in rows:
        print(f"  {u:14s} {acc:7.1f} {f'{ag}/{mt}':>9s} {sh:5d}")
    if len(accs) > 1:
        print(f"  {'— mean —':14s} {np.mean(accs):7.1f}  (n={len(accs)} annotators)")
    if agg_dis:
        print(f"\n  disagreements (annotator -> {a.gt}):")
        for k, n in agg_dis.most_common(12): print(f"    {n:3d}  {k}")
    if a.confusion:
        labs = sorted({l for (g, p) in agg_conf for l in (g, p)})
        print(f"\n  confusion (rows = {a.gt} truth, cols = annotator):")
        print("    " + "".join(f"{l[:7]:>8s}" for l in labs))
        for g in labs:
            print(f"  {g[:9]:9s} " + "".join(f"{agg_conf.get((g,p),0):8d}" for p in labs))
    print("\nNB: points are pre-placed (co-located); label = per-point `description`. Agreement, not proficiency.")

if __name__ == "__main__":
    main()
