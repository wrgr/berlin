# Other analyses — exploratory work behind the project (indexed & code-backed)

Exploration that is **not** in the main deck pipeline but that we don't want to lose. Each theme
below lists its **de-identified data** (`../../evidence/other/`) and the **script** that produced it.

Caveats, honestly:
- These are **as-run exploratory scripts** — hardcoded scratchpad paths and a `.nv_tokens.json`
  credential read; preserved for provenance, **not** maintained as a clean pipeline.
- A few producers were **ad-hoc** (computed inline and not retained as a script). Where that's the
  case it's marked; the **de-identified output is still committed** so the result survives and the
  figure is regenerable from the data.
- Handles are de-identified in the data (experts `E01..`, students `S01..`, others `U..`); raw
  handles, tokens, and the name map are never committed.

## Expert-to-expert / expert-anchored agreement
The empirical backbone of "experts disagree → no free ground truth."
- **`decision_agreement.csv`** — inter-expert agreement: on shared objects, experts agree with the
  expert reference at **0.54–0.96** (and with consensus 0.81–1.0). *Producer: ad-hoc (not retained).*
- **`compare_to_pat.csv`**, **`expert_alignment_ranking.csv`** — behavioral similarity / distance to
  the expert grader; ranks annotators by how "expert-like" their behavior is. *Producer: ad-hoc.*
- **`pat_anchored_v3.csv`**, **`pat_behavioral_distance.csv`**, **`pat_distance_per_type.csv`** —
  Pat-anchored controlled experiment (same objects, students + Pat); competency = agreement-with-Pat.
  Scripts: **`mine_pat_anchored.py`**, **`mine_pat_behavior.py`**.

## Competency variants
- **`competency_ALL.csv`**, **`feature_competency.csv`** — per-namespace and per-feature competency.
  Scripts: **`mine_all_competency.py`**, **`mine_feature_competency.py`**, **`rf_competency.py`**.

## Spatial effort & kinematics
- **`spatial_sessions.csv`**, **`spatial_user.csv`** — camera rotation / pan / zoom effort per click.
  Scripts: **`mine_spatial.py`**, **`mine_3d_features.py`**.

## Rich cross-task behavior
- **`rich_crosstask_expert.csv`**, **`rich_crosstask_student.csv`** — richer cross-task feature sets
  (viewpoint diversity, total pan, …). Scripts: **`mine_rich_crosstask.py`**, **`mine_richer_features.py`**.

## Learning trajectory & three-axis scores
- **`learning_trajectory.csv`** — tier progression over time (learn slope, ceiling). *Ad-hoc producer.*
- **`three_axis_scores.csv`** — style-similarity × agreement × split-durability. *Ad-hoc producer.*

## Vocabulary / dialect (behavior dictionary)
- Script: **`mine_dictionary.py`**, **`mine_features.py`**, **`mine_all_minnie65.py`**. (The
  `dialect_distance` pairwise matrix is omitted from committed evidence — handles are in its headers.)

## Axon ground-truth (RETRACTED — kept as the record of what was tried)
- Scripts: **`mine_axon_refined.py`**, **`mine_axon_valid_gt.py`**, **`mine_axondend.py`**,
  **`mine_credited_axis.py`**. The axon-correctness GT failed the expert sanity gate (Pat ≈ 0.57);
  see `../../transparency_failure_modes.md` §Retracted analyses.

## Exploratory stats (superseded by committed versions)
- **`interrogate_rho.py`** → superseded by `../rho_robustness.py` (ρ=−0.44 selection-artifact).
- **`substantiate.py`** → tier-AUC CI/permutation work folded into `../fishing_audit.py` / `methodology`.
- **`perm1000.py`** → 1000-permutation null helper.
