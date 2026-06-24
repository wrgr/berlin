# Derived proofreading kinematics & per-user variance

Beyond *what* a proofreader does (the behavior dictionary), the signal is in the
*dynamics around each edit*. These are computed from differstack `timestamp` +
behavior labels — **no state reconstruction needed** (spatial distance/pan
magnitude do need it; see "Next").

**Provenance.** Live from `queue.neuvue.io` (2026-06), four **minnie65** human
namespaces. 632 sessions with ≥1 segment edit; **20 proofreaders with ≥3 sessions**.

## Features (per session, "click" = a segment edit)

| Feature | Definition |
|---|---|
| `inter_click_s` | median time between consecutive segment edits |
| `nav_before_click` | navigation events between one edit and the next (look-before-click) |
| `think_to_first_click_s` | time from session start to the first edit (deliberation) |
| `frac_nav` | fraction of events that are navigation |
| `edits_per_min` | editing tempo |
| `click_burstiness` | CV of inter-click times (steady vs bursty) |

## How much do proofreaders vary? (the headline)

Cross-user spread of the per-user median (p90 / p10):

| Feature | p10 | median | p90 | spread |
|---|---:|---:|---:|---:|
| **think_to_first_click_s** | 0.9 | 7.0 | 15.8 | **17.5×** |
| frac_nav | 0.11 | 0.38 | 0.54 | 4.9× |
| **nav_before_click** | 0.33 | 0.94 | 1.37 | 4.2× |
| edits_per_min | 3.5 | 6.3 | 11.9 | 3.4× |
| click_burstiness | 0.59 | 1.02 | 1.60 | 2.7× |
| inter_click_s | 3.1 | 4.4 | 5.3 | 1.7× |

The *deliberation* features (think-time, look-before-click, %navigation) separate
people most; raw click cadence is the most uniform. Concretely (anonymized):
one validator looks ~2.7 navigation events before every click; another clicks
with almost none (0.08). One dives in immediately (0 s); another deliberates ~30 s
before the first edit.

## Task-type signatures (median by namespace)

| Namespace | inter_click_s | nav_before_click | think_s | edits/min | burstiness |
|---|---:|---:|---:|---:|---:|
| `somaSomaReview` (review) | 2.4 | 0.33 | 2.8 | 11.6 | 0.65 |
| `somaSomaSplit` (split) | 3.3 | 0.88 | 4.4 | 10.7 | 0.93 |
| `multiSomaSplit` | 4.3 | 1.00 | 5.1 | 6.6 | 0.67 |
| `fullyProofread` (validate) | 4.6 | 0.64 | 9.3 | 5.0 | 1.06 |

Review is fast and low-effort; validation is slow, deliberate, and bursty. **So
the same feature means different things per task type — scores must be computed
within task type, not pooled.**

## The score / ground-truth substrate (where "alignment with truth" comes from)

Discovered in the metadata:
- **`fullyProofread` is the calibration namespace**: a **`gt_task` flag (363
  gold tasks)** and the **same `seg_id` done by up to 55 proofreaders** (62% by
  >1). → inter-annotator **agreement** is directly computable, and agreement on
  gold tasks is a per-person competence score.
- **`somaSomaSplit`** has `base_state` + `starting_seg_id` in metadata (34% of
  segs done by 2–3 people) — redundancy for agreement, and `base_state` enables
  trajectory reconstruction.

**Update after investigating `fullyProofread`:** the agreement design is real
(53 segs, each done by up to **55** annotators; 363 `gt_task`-linked), **but**
these are ~**0.4s binary submits** (median 0.4s, max 22s) with no stored decision
(`status` is "closed" for nearly all; metadata empty; negligible differstack). So
there is **no discriminating outcome in the queue** to score agreement on, and no
behavior to extract there. Meanwhile the rich behavior (kinematics) lives in the
**split** namespaces, which lack multi-annotator redundancy.

**Consequence:** a competence score is **not computable from the queue alone**. It
needs the **external promotion/agreement scores** (from the Minnie65 staged-
promotion study), joined by `assignee` to the per-user kinematic features here.
That join is the concrete next step: provide `assignee → score/role`, and we test
which kinematic features (think-time, %nav, look-before-click, tempo) track it,
within task type. Weak in-queue proxies (errored-rate, speed-vs-peers) are a
fallback if external scores aren't available.

## Caveats

- Timing is from differstack `timestamp`s; sessions without differstacks are not
  covered (coverage is partial).
- "click" = segment-set change, which conflates selection with a graph
  merge/split (see the behavior dictionary).
- **No spatial features yet** (distance between clicks, pan/zoom magnitude) — those
  need reconstructing positions from `base_state` + the patch chain.

## Next

1. Reconstruct positions (`base_state` + diff-match-patch) → distance between
   clicks, pan/zoom magnitude before a click, dwell vs. travel.
2. Build the agreement score on `fullyProofread` gold segs; correlate with
   kinematics within task type.
3. If external promotion/agreement scores exist, join them directly.

## Spatial reconstruction — status (attempted, not reliable yet)

Pushed hard on metric reconstruction (distance/pan/rotation magnitude). What got
solved vs. what blocks it:

**Solved:**
- `base_state` (task metadata) is the *old* NG format and does **not** match the
  differ patches (0/10 apply). The right base is the task `ng_state`, a **CAVE
  state-server URL** (`global.daf-apis.com/nglstate/…`).
- Resolving it needs a **CAVE bearer token** — confirmed working (states return
  modern JSON).
- Patch encoding is neuroglancer `quote(safe=":,")`.
- Identified the navigation fields: `perspectiveOrientation` (quaternion, 3D
  rotation), `navigation.pose.position.voxelCoordinates` (pan), `perspectiveZoom`
  / `zoomFactor` (zoom). Navigation patches "apply" at ~96%.

**Blocks it:** the differ's base is the *live spelunker workspace* state, which is
**not byte-equal** to the stored `ng_state` (key order, number formatting,
load-time setup). So diff-match-patch can't anchor exactly:
- with **fuzzy** matching, patches mis-apply and corrupt values (e.g. a
  91M-voxel "pan" — physically impossible on minnie65);
- with **strict** matching, most patches fail and the state goes stale (~0).

Reliable metric features therefore need replicating **neuroglancer's exact state
serialization** (the known `urlSafeStringify` / key-order logic in the NG source)
so the base byte-matches. That's a scoped sub-project, not a dead end — every
other piece is in place. **Until then, the count/time-based pre-click navigation
above is the robust spatial proxy, and scoring should proceed on the temporal
features.**


