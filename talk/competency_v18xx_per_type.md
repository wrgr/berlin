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
