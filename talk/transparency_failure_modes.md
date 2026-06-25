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
     the null). The sub-0.5 estimate reflects the *expertise* axis being weakly **opposed** to
     accuracy among calibrated annotators (rotation ρ≈−0.44). **The signal that survives is
     per-decision and ground-truth-free** (AUC 0.59) and is *not* a difficulty artifact: `dur_z` is
     uncorrelated with task size and holds within every size stratum (0.57 / 0.52 / 0.69). (See
     `analysis/explore_accuracy_predictability.py`, `explore_accuracy_confound_and_target.py`,
     `fig_accuracy_unpredictable.png`.)

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

## What survived
Expertise AUC 0.90 (naive/designed/learned 0.75/0.95/0.90); accuracy ceiling-clustering on two
tasks; promoted ≈ expert < unpromoted; annotator-level accuracy **not predictable** (AUC 0.14, but
within the LOO null 0.45±0.20 — *no signal*, not "worse than chance"; also null on variance-rich
distance-to-GT); per-task GT-free uncertainty (AUC 0.59, flag-20%→catch-28%, difficulty-robust). All
passed the sanity checks above.
