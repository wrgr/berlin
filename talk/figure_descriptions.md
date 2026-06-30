# Figure descriptions — synced to the analysis

Each figure is the exact artifact embedded in `berlin_deck_v12` (the current deck). The numbers are
computed by the analysis pipeline's **network stages** (`analysis/run_all.py` stages 1–3) from
NeuVue + CAVE (credentials required); the resulting per-annotator CSVs carry annotator **handles**
and are deliberately **not committed** — the same privacy reason handles are suppressed in every
figure. The repo ships the figures and the pipeline: re-run the network stages with credentials to
regenerate the CSVs in `live_out/`, after which the offline stages reproduce these figures exactly.
Handles are suppressed; every figure carries the *"Preliminary analysis — MICrONS proofreading
annotators"* stamp. **Cohorts:** *expert* = 8 part-time expert proofreaders (Janelia-trained); *proto-expert* =
the agreement-promoted students. In the dense-telemetry figures (`multiSomaId`) the proto-expert
group is the 8 promoted students who have dense logs; in the grading-task figures it is split into
*promoted* (7) vs *unpromoted* (19). Feature tiers defined in `methodology_provenance.md` §10–13.

---

## Slide 13 — the two evidence panels

### `fig_expertise_evidence.png` — Experts explore ~2.18× more; honest AUC ladder (replaces fig_tier_auc)
- **Left:** total camera rotation per annotator — experts accumulate ~2.18× more (1014° vs 466°), a
  model-free difference.
- **Right (LOO, cross-validated):** **designed** 28 hand-built features **0.98** (engineered post-hoc
  on n=16 — an exploratory ceiling); **naive** 4 counts **0.81** and **learned** 10-motif dictionary
  with k-means refit *in-fold* **0.81** (the robust floor); **28 pure-noise features 0.45** and the
  **permuted-label null 0.46** (chance — CV catches trivial fit). n = 16 (8 + 8).
- **Reads as:** a real, broad ~0.81 expertise signal anchored in 3-D exploration; only the post-hoc
  designed bank reaches 0.98, and CV rules out trivial overfit.
- **Caveat:** small n; the leaky 0.90/0.95 once reported for the learned tier (k-means fit on *all*
  annotators) is **retired**. Separates *expertise*, not *correctness*; confirmation = the prospective test.

### `fig_prospective_flagging.png` — Ground-truth-free error flagging
- **Plots:** deployment curve. Rank fullyProofread tasks by a **label-free anomaly score** (how
  slow a task was *for that annotator* — within-person z-scored duration) and re-review the most
  anomalous. X = % tasks flagged, Y = % true errors caught; red = flag-by-anomaly, dashed = random.
  764 tasks, 36 annotators, 194 errors (25% base rate), curve **AUC 0.59**.
- **Marked point:** **flag 20% → catch ~28%** of all errors (≈1.4× lift over random).
- **Reads as:** with no ground truth, behavior still concentrates errors — you can prioritize
  re-review. This is the prospective value proposition.
- **Caveat:** modest lift; a screening prior, not a verdict.

---

## Slide 14 — `fig_kinematics.png` — the 3-D exploration mechanism
- **Plots:** four boxplots (expert vs proto-expert, n = 8 each; medians + jittered points) on the
  dense `multiSomaId` telemetry —
  - total camera rotation **1014° vs 466°** (~2.2×)
  - # rotations / distinct viewpoints **14.2 vs 6.0** (~2.4×)
  - events per annotator **3033 vs 1426** (~2.1×)
  - events / session (tempo) **30.9 vs 23.1** (~1.3×)
- **Reads as:** the mechanism behind the AUC — experts inspect a neuron from ~2× more viewpoints
  and do more, faster. Skill is in *how* the work is done.
- **Caveat:** per-differstack rotation (cross-session camera jumps removed — the corrected metric);
  dense-telemetry cohorts only.

---

## Slide 15 — `fig_action_grammar.png` — the language of proofreading
- **Plots:** (left) action-mix bars — fraction of events that are navigate / segment / annotate /
  other; (center & right) the row-normalized **navigate↔segment transition grammar** (2×2) per
  cohort.
  - Action mix (expert / proto): navigate **0.38 / 0.46**, segment **0.57 / 0.50**, other 0.05/0.05.
  - Grammar: experts show stronger **segment→segment persistence** (S→S ≈ 0.69 vs 0.60) — longer
    uninterrupted editing runs; proto-experts navigate more and switch more.
- **Reads as:** the behavioral "grammar" — which actions, in what order — differs by cohort, the
  JIGSAWS "language of surgery" analogy made literal. Experts edit in sustained runs; proto-experts hop.
- **Caveat:** descriptive (cohort means); annotate ≈ 0 here because annotation lives in other task types.

---

## Slide 16 — three structure panels
### `fig_rf_importance_new.png` — RandomForest importance (designed features)
- Top-12 feature importances (RandomForest, 800 trees, n = 16) for expert vs proto-expert. The
  **highest-importance features are the 3-D exploration kinematics** (total rotation, # viewpoints,
  event volume) — converging with slide 16.

### `fig_feature_pca.png` — designed feature space (PCA)
- 2-D PCA of the standardized designed features; expert (red) vs proto-expert (blue), **promoted
  students circled green**. Cohorts separate along PC1; promoted students sit among the experts.

### `fig_motif_usage.png` — learned-motif "dialect"
- Mean usage of the 10 learned motifs by cohort. Proto-experts over-use **navigate-dominated
  motifs** (m0, m7 — centroids ~0.5–0.8 navigate); experts spread into segment/rotation motifs
  (e.g., m1). A behavioral dialect in the unsupervised space.

---

## Slide 17 — two calibration panels
### `fig_accuracy_threegroup.png` — calibration converges
- multiSomaSplit **distance-to-ground-truth (nm, lower = better)** for three groups: **expert
  median 309**, **promoted 312**, **unpromoted 460** (n = 8 / 7 / 19; expert vs unpromoted p ≈ 0.07).
  Agreement-gated promotion selected expert-level performers: **promoted ≈ expert < unpromoted**.
- **Reads as:** the calibration mechanism works — promotion picks people who perform at expert
  level; outcome variance is compressed (ceiling), which is *why* achieved accuracy alone can't
  rank skill.

### `fig_uncertainty_calibration.png` — uncertainty stays legible
- fullyProofread **error rate by within-person duration quintile** (Q1 fast → Q5 slow):
  **0.16, 0.21, 0.29, 0.25, 0.36** vs **0.25** base rate (dashed). Slowest-for-this-person quintile
  fails ~2.2× more than the fastest. 764 tasks, GT-free, AUC 0.59.
- **Reads as:** even after calibration compresses *who* is better, *which* individual decisions are
  risky stays readable from behavior — the surviving, deployable signal.

---

## Risk slide — `fig_task_risk.png` — two ground-truth-free ways to flag a risky decision
*Long-form, acronym-free legend (for vetting). "Ground-truth-free" = the prediction uses only
information available before review; the correct answer is used afterward, only to check it.*

- **Data.** 764 completed point-labeling tasks by 16 calibrated annotators across 28 distinct neurons.
  A task is an "error" if the annotator's labels did not exactly match the expert grader's. 25% of all
  tasks were errors (the dashed base-rate line in both panels).
- **Left panel — behavior ("a task slow *for that person*").** For each task we compared how long the
  annotator took to that *same* annotator's own average time (removing person-to-person speed
  differences). Tasks split into four equal groups, fastest-relative-to-self to slowest; the real error
  rate per group is **16% / 27% / 25% / 34%**. Ranking-accuracy score = **0.59** (0.5 = chance, 1.0 =
  perfect: the chance a random error-task ranks slower-for-that-person than a random correct one).
  Significance: 2,000 random shuffles of the error labels scored 0.50 ± 0.02; the real 0.59 beat
  essentially all — **p<0.001**.
- **Right panel — task structure ("from the task's own composition").** No behavior used. Each labeled
  point is an anatomical category (spine, nucleus, dendrite, axon, cell body); we predict error from the
  task's *fraction in each category*, training and testing on **disjoint neurons (whole cells held out)**
  so the model can't memorize a neuron's typical error rate. Tasks split into four groups by predicted
  risk; real error rate per group is **16% / 10% / 25% / 51%**. Ranking-accuracy score = **0.76**;
  1,000 shuffles preserving the held-out-neuron rule scored 0.47 ± 0.02 — **p<0.001**. Strongest drivers:
  fraction of axon points (axon-heavy tasks were *safer*, 17% vs 25%) and dendrite points.
- **Honesty note.** An earlier 0.92 let the model see other tasks from the same neuron (it memorized
  per-neuron error rates); holding out whole neurons removes that and gives the honest 0.76. Only the
  honest number is shown.
- **Claims / limits.** Two independent no-answer-key signals each beat chance, both significant. NOT large
  or deploy-ready: pilot scale (764 decisions, 28 neurons, 16 annotators); the behavioral effect is modest.
  The signals are complementary at different levels — behavior ranks *individual decisions*, structure ranks
  *whole tasks/neurons*; adding structure to the per-decision behavioral model did not improve per-decision
  ranking. "Error" = disagreement with the grader on this one task, not absolute biological correctness.
  (`make_risk_fig.py`; numbers via `explore_task_risk_prediction.py`.)

## Point-agreement evidence — `fig_point_agreement.png` (backup slide 24; cited in slides 8 & 17 footnotes)
- **Plots:** (left) per-annotator **point-label agreement with the expert grader** (Pat / `rivlipk1`)
  on the shared fullyProofread / patProofread benchmark cells, by cohort — each dot one annotator
  (handles suppressed), bar = group median: **expert 98%, promoted 100%, unpromoted 94%** (the
  unpromoted group is bimodal, with a low tail down to ~27%). (right) the per-point **confusion
  matrix** for a representative expert (chris) — near-identity, **99.3% (141/142)**, one off-diagonal
  (a `spine` vs `axon`).
- **Reads as:** calibration **converges outcomes at the level of individual decisions** — promoted ≈
  expert, both matching the grader on ~99% of point classifications, while the variance lives in the
  unpromoted tail. This is the outcome/agreement companion to the behavioral evidence, and it
  operationalizes "converged agreement" (slide 8) and "per-decision, not per-person" (slide 17).
- **Caveat:** agreement vs **one grader** (Pat) as the competence surrogate; free-text labels
  normalized to canonical classes (`compare_points.py --raw` for exact strings). Two experts sit
  lower (gary 76%, michael 74%) — possible labeling-convention or cell-subset effects; behavioral
  Pat-likeness ≠ label agreement (style ≠ proficiency). Built by `make_point_agreement_figure.py`.

## Spare figures (in repo, not embedded in the deck)
- **`fig_two_task_quality.png`** — scatter of multiSomaSplit distance vs fullyProofread accuracy;
  both **ceiling-clustered**, the single best split placement is a novice, promoted circled. (The
  "convergence" evidence in one frame.)
- **`fig_motif_dictionary.png`** — 10×8 z-scored heatmap of the k-means motif centroids (the
  "gestures" over label + timing + rotation windows) — the dictionary behind the learned tier.
- **`fig_separability.png`** — per-annotator competence bars (the bad tail < 0.90 that simple
  behavior can't predict; **annotator-level LOO AUC 0.14**, the honest negative) + the GT-free
  uncertainty histogram (AUC 0.59).
- **`fig_accuracy_unpredictable.png`** (backup slide 23) — *why* per-annotator accuracy isn't
  predictable, in 3 panels: (1) accuracy is ceiling-clustered (31 at ceiling + a 5-point tail);
  (2) the 0.14 LOO AUC sits **inside** the permutation null (0.45 ± 0.20, p≈0.07) — not "worse than
  chance"; (3) the expertise axis (rotation) tilts the **wrong way** for accuracy among calibrated
  annotators (ρ=−0.44). Companion checks: variance-rich distance-to-GT also unpredictable (Ridge
  ρ=0.07, and no scale transform/model recovers it); the per-decision signal survives task-size
  control (3-D structural difficulty: a follow-up).

---

### Honest negatives (apply across all figures)
Annotator-level *accuracy* is **not** behaviorally predictable — and the careful version matters: the
LOO AUC 0.14 is **within the permutation null** (0.45 ± 0.20, p≈0.07) — *no signal*, not "worse than
chance" — and it holds on **both** ceiling-bound label accuracy **and** the variance-rich
distance-to-GT (Ridge ρ=0.07, p=0.71); different classifiers/weights don't recover it (sweep
0.00–0.34) — nor do scale transforms or flexible regressors on the continuous distance target (best
Spearman 0.26, p=0.25). The deployable signal is **per-decision and ground-truth-free** (AUC 0.59) and is *not* a
task-size artifact (survives task-size control; holds within every size stratum). So competence is
legible **per-decision, not per-person** (see `fig_accuracy_unpredictable.png`). The figures show
*expertise is legible* and *calibration converges* — not that accuracy can be predicted per person.
Prospective test pre-registered for this summer.
