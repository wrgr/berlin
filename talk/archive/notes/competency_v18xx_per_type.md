# Objective competency vs the v18xx connectome — per task type

The decisive competency measure: take each operation an annotator actually
performed and ask whether it **survived into the latest segmentation (v18xx)** —
graded **per task type**, because skill is type-specific.

## Method
- Three task types store the CAVE link directly: `multiSomaId`, `singleSomaCleanUp`,
  `neuronOtherBodies` store `operation_ids`; `somaSomaSplit` stores supervoxel pairs.
  (Axon types store only `cut_id` → would need cloudvolume point→supervoxel; deferred.)
- `operation_ids → get_operation_details → removed_edges` (the supervoxel pairs the
  annotator cut). Look up each supervoxel's **current root in v18xx** (`get_roots`).
- **Approximate "did the cut survive?"** (per request — supervoxel-exact persistence
  is too strict; refinement re-splits supervoxels): an operation counts as held if a
  **majority of its cut edges are still in different roots**. Per (user, task type) =
  fraction of their operations that held.

## Finding: competency is task-type-specific
1,977 operations, three task types. Overall survival ≈ 0.91–0.94, but it **varies by
type within a person** (`competency_per_type.png`):
- `chris`: multiSomaId 0.94 vs neuronOtherBodies 0.74 (0.20 spread)
- `christopher`: neuronOtherBodies 1.00 vs singleSomaCleanUp 0.80 (0.20 spread)
- `natalie`: 0.95 / 0.93 / 0.82

A single competency scalar hides this. Proficiency, competency, and learning must all
be computed **per task type**.

## Why this is the right ground truth
- **Objective** — the final connectome, not consensus (consensus agreement was
  near-ceiling 0.92–1.00 and circular).
- **Robust** — approximate (gross cut), not supervoxel-perfect.
- **Rich** — thousands of operations across types; scales to all operation-bearing
  task types.

## Next
- Install cloudvolume to extend to the axon task types (point→supervoxel for the
  `cut_id`-only types) — adds the largest decision datasets (`axonOnDendrite` 2.5k).
- Use this per-type survival as the **regression target** (objective, per-type) for
  learning expert-likeness from behavior/grammar/3D features.
- Learning = improvement in this measure over time **within a task type**.

## Complete matrix (all qualifying annotators × all task types)
Expanded to **18 users × 5 task types, 48 cells** (`competency_ALL_anon.png`), graded
vs v18xx, two ground-truth methods:
- **soma/cleanup types** (`multiSomaId, neuronOtherBodies, singleSomaCleanUp`):
  operation did-cut survived — **high-ceiling** (0.91–0.99), little discrimination.
- **axon types** (`axonOnAxon, axonOnDendriteV3`): decision vs whether the merge-path
  endpoints are **separated in v18xx** (cloudvolume point→supervoxel→root) —
  **discriminating** (0.45–0.88).

Competency is strongly **task-type-specific**: e.g. `christopher` 0.45 (axonV3) →
0.98 (neuronOtherBodies); `natalie` 0.59 (axonOnAxon) → 0.97 (singleSomaCleanUp).

**Caveats on the axon scores** (weaker than soma did-cut): the endpoint-separation
truth is approximate, and decisions were collapsed to yes-family vs no-family
(`yesPartial/yesConditional` forced to "expect separated"), which can misgrade
nuanced annotators — so e.g. Pat (`rivlipk1`) scoring mid on axon is likely a
collapse/case-difficulty artifact, not low skill. The **soma did-cut** remains the
most reliable measure; axon adds spread but needs the graded-decision refinement.
`axonOnDendrite` (richest, 20 users) lacks `base_state` but is recoverable via the
reconstructed `nglstate/api/v1/{apl_id_with_syn}` URL (add-on run).

## Refined axon grading + a validity caveat (important)
Re-graded axon on **clear yes vs no/noError only** (dropping `yesPartial`/
`yesConditional`: 8% of axonOnAxon, 44% of axonOnDendriteV3, **67% of
axonOnDendrite** were ambiguous). Result:
- Pat stays **0.58 on axonOnAxon** even on clear cases (and drops out of
  axonOnDendriteV3 for too-few-clear), so her mid axon score was **not** a
  collapse artifact — it's real.
- Refined **axonOnDendrite mean = 0.42 — below chance**. An expert-≈-chance,
  population-below-chance "truth" is **not measuring decision correctness**: for
  axon-on-dendrite the corrected cut is *local*, so the far merge-path endpoints
  don't separate even when the decision is right. **The endpoint-separation proxy
  is invalid for the axon types.**

**Conclusion: trust the soma did-cut (operation survival) as the competency ground
truth** (0.92–0.97; high-ceiling, low discrimination). Treat the axon
decision-vs-endpoint columns as unreliable. A proper axon ground truth would need
the *local* cut supervoxels (from the split-suggestion table), not path endpoints.

RF re-fit on the refined target is unchanged: within-type behavior→competency CV
R² = −0.24 (axonOnDendrite −0.89, multiSomaId −1.25). Behavior does not predict
correctness regardless of grading.
