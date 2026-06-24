# Validating proofreading against CAVE + decision agreement

Two distinct questions (per user framing):
1. **Is there a link?** — does a task's edit trace to a committed CAVE operation?
2. **Does the annotator agree with the later/latest data?** — is the decision
   *correct* against ground truth?

## What CAVE/neuvue actually expose (probed live, minnie65_phase3_v1)
- **CAVE chunkedgraph change log is accessible** with the token. Per root it
  returns every split/merge: `operation_id, timestamp, user_id, user_name,
  user_affiliation, is_merge, before/after_root_ids`. Materialization is at
  **v1817** ("17XX"). Synapses are a separate table (ignored, as intended).
- **Decisions are stored on the task** (`metadata.decision`): axon tasks use a
  rich vocabulary — `yes / yesConditional / yesPartial / no / noError`.
- **Some namespaces pre-store the CAVE link**: `multiSomaId` → `operation_ids`;
  `somaSomaSplit` → `nuclei_supervoxel_ids`. So traceability (Q1) is often a
  direct field lookup; otherwise match by time-window + `user_name` in the
  lineage change log.
- The start-root's change log is *prior* history; the annotator's own edit lives
  in the lineage going forward (`is_latest_roots=False` + descendant roots).

## Q2 today, without heavy plumbing: inter-annotator / expert agreement
The same object is decided by many people — `axonOnDendrite` has **739** objects
decided by ≥2 annotators (69% pairwise agreement); `axonOnDendriteV3` has balanced
decisions with only **34%** agreement (38% expert-vs-student) — i.e. real
disagreement where skill shows. Using the expert (`rivlipk1`) as ground truth on
co-decided objects, 9 students had ≥5 shared objects; expert-agreement ranged
**0.54–0.96**.

## Headline finding: **style ≠ accuracy**
Correlation between *behavioral* distance-to-expert (navigate:edit signature) and
*decision* agreement-with-expert is **≈ 0.00** (n=9; see
`style_vs_accuracy_anon.png`). The most edit-heavy student — behaviorally the
*least* expert-like — had the **highest** decision agreement (0.96). So:
- the navigate:edit "signature" is a **style** axis, not competence;
- **decision agreement** (vs expert / latest data) is the competence axis.

This is the argument for grounding any competence score in decisions/outcomes,
not movement kinematics.

## Stronger next layer: agreement vs the *latest* connectome (Q2, ground truth)
For each decided cut, look up whether its two sides are **separate roots in the
latest data** (split executed = truth says "error") vs the stored decision.
Mechanics: take the merge-path endpoints (in the task base state) or the stored
`nuclei_supervoxel_ids`/`operation_ids` → point→supervoxel→root via cloudvolume →
compare to `decision`. Needs a segmentation lookup (extra dep) but is standard;
yields an objective "agrees with the final connectome" score per annotator.
