# Transparency — failure modes & approaches tried

Full disclosure of dead ends, bugs, retractions, and data limits, for reviewer trust and as
a methodology appendix. **Every claim in the main results survived these checks**, including
the expert-anchor sanity gate (the best/expert annotator must score ≈1 on any competence
metric). Companion to `methodology_provenance.md`.

## Retracted analyses
1. **v18xx axon "correctness" ground truth** (endpoint- and path-separation against the latest
   segmentation; "did the cut survive / did endpoints separate?").
   - *Why retracted:* failed the **Pat≈1 sanity gate** — the expert (Pat) scored 0.57, and
     ~95% of objects read "separated" downstream regardless of the decision, so the metric did
     not measure decision quality. Any "behavior predicts conformity, not correctness" claim
     built on it is **withdrawn**.
   - *Lesson:* a competence metric must pass the expert anchor before it is trusted.
2. **Path-local, synapse-aware separation** (axonOnDendrite). Same downstream-invariance
   problem; not discriminative. Retracted.
3. **Pat-likeness proficiency model.** Built; behavioral distance-to-Pat did not robustly track
   decision agreement. Kept as descriptive only, not a competence claim.

## Hypotheses investigated and resolved
4. **"Zero behavior↔accuracy correlation must be an order/alignment artifact."** We built
   order-tolerant features (motif n-grams, run-lengths, alignment-free descriptors). The
   near-zero correlation was partly outlier-driven (a single annotator) **and** genuinely real:
   accuracy is **ceiling-clustered** across two task types, so there is little accuracy variance
   to predict. Richer features improved *expertise* separation but not *accuracy* prediction —
   it is not an ordering artifact.
5. **Handle → real identity via CAVE** (chunkedgraph operation `user` + change-log `user_name`).
   Unreliable: the operation `user` is who *executed* the split in CAVE, not the NeuVue assignee
   (two different handles resolved to the same uid 1833; names did not resolve on a later run).
   **Not used for any claim**; we use the project lead's authoritative promoted list.

## Fishing audit — how much of the expertise AUC is real?
The 28 "designed" features and 10 k-means motifs were built on this same n=16 (post-hoc, not
preregistered), so the headline 0.90–0.98 is optimistic. We audited it three ways
(`fishing_audit.py`, `motif_cv.py`):
- **Robust floor ~0.80.** Median of 38 single-feature AUCs = 0.80; the un-fished 4-count naive tier
  = LOO 0.81; the **learned** motif dictionary refit **inside each CV fold** = **0.81** (on fresh
  windows the in-fold and leaky variants agree, premium ≈ 0.00). The 0.90/0.95 once reported for the
  learned tier fit the k-means on **all** annotators (representation leakage) and is **retired**; the
  lone high tier is the post-hoc **designed bank (0.98)**, an **exploratory ceiling**.
- **Not mere p≫n dimensionality.** 28 pure-noise features reach AUC 1.0 in-sample but collapse to
  0.45 under the same LOO, matching the label-permutation null (0.47 ± 0.19) — CV catches the
  trivial fit; the real features carry signal the noise does not.
- **Model-free anchor.** Experts rotate 1014° vs proto 466° (2.18×) — no classifier needed.
Honest claim: a real, broad **~0.80** expertise signal (naive and CV'd-learned tiers both 0.81)
anchored in 3-D exploration; the **designed 0.98 is an engineered ceiling** pending the pre-registered
prospective test.

## Targets that proved too clustered (ceiling effects)
6. **multiSomaSplit** one-point distance-to-GT: trained novices match experts (medians ~309 vs
   ~399 nm, p=0.092); little variance.
7. **fullyProofread** categorical label accuracy: expert 0.98 vs student 0.97, p=0.63; a ceiling
   with a small discriminating tail.
   - *Consequence:* annotator-level behavior→accuracy is **not predictable** — but "worse than
     chance (LOO AUC 0.14)" over-read a noisy point estimate. Against this estimator's LOO
     permutation null (**0.45 ± 0.20**, one-sided p≈0.07) the 0.14 is *no signal*, not an anti-signal;
     it holds on **both** ceiling-bound label accuracy **and** the variance-rich `multiSomaSplit`
     distance-to-GT (Ridge ρ=0.07, p=0.71), and a classifier/weight sweep spans 0.00–0.34 (all inside
     the null). The sub-0.5 point estimate is **not an anti-signal**: the rotation ρ≈−0.44 behind it
     is non-significant (p=0.10; bootstrap 95% CI **[−0.83, +0.20]**, crosses zero) AND it is a
     **selection-confounded between-cohort comparison, not "skill hurts."** It decomposes into two
     clouds — experts (high rotation, accuracy 0.92) vs proto-experts (low rotation, accuracy 0.98) —
     with no within-cohort trend (experts ρ=−0.60 n=8 n.s.; proto-experts ρ=−0.04). The proto-experts
     are exactly the students **promoted for agreeing with the graders**, while fullyProofread accuracy
     *is* agreement with grader GT — so the comparison group was selected on the outcome metric, and
     the expertise features (rotation, runs, motifs — systematically the most-negative coefficients)
     inherit a spurious negative. It is the footprint of agreement-gated promotion + range restriction
     (no true novices), not an "expertise axis pointing the wrong way." Task difficulty is not the
     driver (equal across cohorts, 8.0 vs 8.0 pts, 0.25 vs 0.24 axon-frac; partialling it leaves −0.44
     unchanged), and no per-person accuracy signal is recoverable by a richer grammar because the
     **target has almost no variance** (0.95±0.09) and is selection-shaped. **The signal
     that survives is per-decision and ground-truth-free** (AUC 0.59) and is *not* a difficulty artifact: `dur_z` is
     uncorrelated with task size and holds within every size stratum (0.57 / 0.52 / 0.69). Scale transforms (log, rank-invariant) and flexible
     regressors (RF/GBM/kNN) on the continuous distance target don't recover a signal either (best CV
     Spearman 0.26, permutation p=0.25); the only difficulty proxy controlled is task **size** —
     3-D structural difficulty (path length, branches, volume, synapse density) is a follow-up. (See
     `analysis/explore_accuracy_predictability.py`, `explore_accuracy_confound_and_target.py`,
     `explore_distance_regression.py`, `fig_accuracy_unpredictable.png`.)

## Bugs found and fixed
8. **Duration mis-scaling** — a field in *seconds* was treated as milliseconds ("0.0 min"); fixed.
9. **Supervoxel lookup returned 0** — scalar-extraction bug; fixed with
   `int(np.array(cv.download_point(...)).flatten()[0])`; `coord_resolution=[4,4,40]` confirmed.
10. **Cohort mislabeling** — an early pass labeled the *expert* cohort as "students" and compared
    them to Pat (they clustered near Pat because they *are* experts). Corrected against the
    grading notebooks; all expert/student claims re-derived.
11. **Shell cwd reset** between calls broke commits; fixed with absolute `git -C` paths.
12. **matplotlib `labels=`→`tick_labels=`** API change in figure code; fixed.

## Data-quality / QC decisions
13. **stella 8841 nm** point: detectable bad data, rejected at the 2000 nm QC threshold (notebook
    default). The pipeline rejecting well-intentioned-but-bad data is itself a deliverable.
    *Open:* distinguish a single bad point from a consistently-bad annotator.

## Engineering blockers sidestepped
14. **Byte-exact viewer-state reconstruction** required matching a moving base across
    diff-match-patch patches (brittle). Sidestepped by extracting per-event camera kinematics
    (quaternion / pan / zoom) directly from each patch's new-side window — base-matching-free.

## Telemetry-availability constraints (these bound the conclusions)
15. The grading tasks (`multiSomaSplit`, `fullyProofread`, `patProofread`, StudentLabeling) record
    **only a final `ng_state` point + duration — no differstacks**. Dense per-event telemetry
    lives in extension/cleanup tasks; `multiSomaId` is the common dense task. So rich behavioral
    models use `multiSomaId`, where **only experts + promoted proto-experts appear** — the worst
    performers have no dense telemetry, so the rich prospective test cannot yet reach them.

## A positive result from the same thread: GT-free task RISK
Pushing on *"is the representation rich enough?"* paid off — for a different target than annotator
competence. With a richer GT-free per-task representation (point-category mix), **task
error-proneness (RISK) is predictable at AUC 0.76 on held-out cells** (grouped-by-cell CV;
permutation null 0.47 ± 0.02, p<0.001) — the "risk" axis of the impact×risk allocation, scored before
any expert time is spent. Caveats: the headline 0.92 under random CV was **cell-identity leakage**
(only 28 benchmark cells, bimodal — 25 easy + 3 "killer" cells); per-annotator competence within a
fixed cell stays ~0.55; CAVE morphological confirmation is **inconclusive** (17/28 cells carry stale
2021-22 roots). See `enrich_fullyproofread.py`, `explore_task_risk_prediction.py`, `cave_difficulty.py`,
`fig_task_risk.png`.

## Principled-feature prototypes (grammars / morphology)
Two follow-ups on *"learn the features, don't hand-build them"*:
- **Behavioral grammar.** A first-order Markov (n-gram) grammar over the action stream recovers
  expertise at LOO **AUC 0.95** (≈ the designed tier) — the "language of proofreading" is real and
  learnable. But a more expressive **HMM latent grammar collapses (0.39–0.59) at n=15**: the
  expressive models (HMM, and by extension transformers) are **data-starved**, not wrong — the
  scale-up, not a present result. (`extract_streams.py`, `grammar_probe.py`, `fig_grammar_morphology.png`)
- **Morphological difficulty (caliber/branches).** In the 28-cell benchmark, caliber / branches /
  size do **not** predict per-cell error (all p>0.09; thin-fraction +0.16 — right direction, n.s.).
  The GT-free risk signal (0.76) is **annotation-category difficulty, not cell morphology** here;
  17/28 cells carried stale roots. A clean test needs more cells + a morphology-sensitive task.
  (`cave_morphology.py`)

## What survived
Expertise signal ~0.81 CV (naive and learned both 0.81; designed 0.98 engineered; the leaky 0.75/0.95/0.90 retired); accuracy ceiling-clustering on two
tasks; promoted ≈ expert < unpromoted; annotator-level accuracy **not predictable** (AUC 0.14, but
within the LOO null 0.45±0.20 — *no signal*, not "worse than chance"; also null on variance-rich
distance-to-GT); per-task GT-free uncertainty (AUC 0.59, flag-20%→catch-28%, robust to task size); GT-free task **RISK** predictable at 0.76 (grouped CV, p<0.001). All
passed the sanity checks above.
