# Encoding the proofreading "grammar" + learning expert-likeness

Goal (per user direction): **regress a continuous "expert-likeness", not classify**
(there is only one expert, `rivlipk1` / Pat Rivlin — she is the reference), and
**compare every user to Pat**. Crucially: competence is **not** captured by distance
or time scalars — it is the **reasoning process** and **how a person explores and
thinks in 3D**. The features below aim at that.

## 1. The reasoning process — action grammar
- **Tokens** (behavior dictionary): `navigate, segment, annotate, other` (+`trace`).
- **Within-type grammar** = transition matrix `P(next | current)` over consecutive
  events within a session, computed **per (user, task-type)** — 4×4 = 16 features
  that capture *rhythm/reasoning*, not just the unigram mix.
- **Across-type** = stack/aggregate per-type matrices (+ task-type indicator).

**Finding:** `P(next|current)` differs by tier (`grammar_transitions.png`):
expert `segment→navigate` = **0.64**, `segment→segment` = **0.26** → *edit, then
re-inspect* (she verifies every cut); students/core `segment→segment` ≈ **0.48** →
*batch edits*. This rhythm is the reasoning loop, and is a natural RF feature.

## 2. Thinking in 3D — exploration trajectory  (the key axis)
Navigation is not one thing. Split it into **rotate / pan / zoom** and, better,
extract the actual camera **trajectory** per event (the per-patch quaternion /
position / zoom extraction is proven to work). Candidate features:
- **viewpoint diversity** — how many distinct orientations she rotates through
  (examining structure from multiple angles = 3D reasoning);
- **pan-path structure** — does the camera *follow the neurite* (directed) or jump
  (scattered); path length vs displacement;
- **zoom cycles** — overview↔detail oscillations; **zoom level at decision points**
  (does she drill in before committing an edit);
- **coupling** — rotate-while-zoomed-in (inspecting 3D detail) vs pan-at-overview.

Status: a quick *shape-heuristic* rotate/pan/zoom split is extractable but **leaky**
(large unclassified "navOther", ~37% for Pat) — not reliable on its own. The real
signal needs **value-based trajectory features** from the per-patch extraction, not
event-type counts. This is the recommended next build.

## 3. Compare-to-Pat profile (per user)
Two blocks (`compare_to_pat.png`): **moves-like-Pat** (behavior/grammar/tempo
similarity) vs **decides-like-Pat** (decision agreement, split durability). They
**diverge**: `natalie` is unlike Pat in style yet matches her judgment (0.96);
`christopher` is mid-style, low decision-agreement (0.55), yet top durability (1.00).
→ style similarity ≠ competence; keep the blocks separate.

## 4. Learning plan (regression)
- **Target** = ground-truth competence (decision-agreement vs Pat, and/or split
  durability vs latest seg) — continuous.
- **Features** = grammar transitions (16) + 3D trajectory features (above) + tempo +
  per-task-type variants.
- **Model** = random-forest / gradient-boost **regression**; read feature
  importances to learn *which* exploration/reasoning patterns predict competence.
- **Blocker = labels, not features.** Only ~9 users currently have a competence
  label. **Enabling step:** scale labels to ~25–30 (decision-agreement for all
  co-deciders; durability for all `multiSomaId` annotators) before fitting. Until
  then a fit overfits and is not reported.

## Correction (correlation audit)
An earlier note claimed style↔decision-agreement correlation **≈ 0.00 ("style ≠
accuracy")**. That was an **outlier + small-N artifact**, driven entirely by
`natalie`. Excluding her, Spearman ρ = **−0.74 (p=0.03, n=8)** between
style-distance and decision-agreement — i.e. **more expert-like style does weakly
predict better decisions**, with natalie a genuine exception. Robust takeaway:
style is a *weak, noisy* predictor; ground-truth decisions/outcomes are the
reliable competence axis — which is why §2 (3D reasoning) and the
durability/decision labels matter most.
