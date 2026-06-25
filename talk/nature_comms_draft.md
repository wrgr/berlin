# The language of proofreading: behavioral telemetry encodes expertise, not achieved accuracy, in a calibrated connectomics workforce

**Authors.** W. R. Gray-Roncal\*, [co-authors TBD], D. Xenes, [NeuVue team], L. Kitchell,
P. Rivlin, [MICrONS proofreading leads] (\*corresponding). *Affiliations: Johns Hopkins
University Applied Physics Laboratory; Johns Hopkins University; Janelia Research Campus;
Allen Institute.* — **author list and order to be finalized.**

> First draft. Numbers are from the analyses in `methodology_provenance.md` (§1–13) and the
> scripts under the project scratchpad. Individual proofreader handles are suppressed
> throughout; contributors are named only in Acknowledgments.

---

## Abstract
Large-scale connectome reconstruction depends on a scarce, expensive resource: expert human
proofreading judgment. Deciding *when enough has been spent to trust an inference* requires
**pricing** that judgment — characterizing who is competent, at what, and how confident a
given decision is. We ask whether the **behavior** of proofreaders ("the language of
proofreading"), captured as per-event viewer telemetry during the minnie65 MICrONS campaign,
predicts the **quality** of their work. Using a graded series of representations (naive
counts → a hand-designed behavioral grammar → an unsupervised motif dictionary), we find that
behavior **encodes expertise as a working style** — separating experts from agreement-promoted
"proto-experts" at ROC-AUC 0.90 — driven by three-dimensional exploration kinematics (experts
inspect structure from ~2× more viewpoints). Yet **achieved accuracy does not separate skill
levels**: across two independent grading tasks the trained workforce converges to a ceiling
(experts and novices place split points equally well; per-category label accuracy is
statistically indistinguishable), and coarse per-annotator behavior fails to predict
competence (leave-one-out AUC 0.14). Critically, a **ground-truth-free, per-decision**
signal survives: a task that is anomalously slow *for that individual* is significantly more
error-prone (AUC 0.59, p<0.001), so flagging the most behaviorally-anomalous 20% of tasks
recovers 28% of errors (1.4× over chance) with no reference annotation. We interpret these
results through surgical-skill assessment (the "language of surgery", JIGSAWS) and tacit
knowledge: in a workforce deliberately *calibrated to converge*, outcome variance is removed,
and the legible signal moves from achieved accuracy to (i) expertise style and (ii) per-task
subconscious uncertainty. We propose a pre-registered prospective test: predict competence and
flag risky decisions from early behavior, before outcomes are known.

---

## Introduction
Petascale electron-microscopy connectomics now yields reconstructions whose remaining errors
are corrected by human **proofreaders**, whose judgment is the rate- and cost-limiting input
to the final connectome [MICrONS Consortium, Nature 2025 — confirm]. Because expert judgment
is finite and even experts disagree, "is the connectome done?" is better posed as a
constrained-optimization question: **have we spent enough trusted judgment to support the
specific inference we care about?** Answering it requires *pricing* the judgment — measuring
per-task, per-region competence and inter-annotator agreement — i.e. **calibrating the
annotators, not just the microscope**.

The minnie65 campaign provides an unusually rich substrate. Proofreading was routed and
recorded on **NeuVue** [Xenes et al. — confirm], which logged not only each final decision but
**per-event viewer telemetry** (a stream of navigate / segment-edit / annotate actions with
timestamps and 3-D camera state). The campaign also ran, in effect, a workforce-calibration
experiment: a small expert cohort trained at Janelia worked alongside a larger novice cohort
of undergraduates, and **novices whose decisions agreed with experts were promoted** to a
"proto-expert" tier with write access to expert-level tasks. This staged promotion is a
real-world instance of systematic learning engineering.

We ask a single question with broad implications for connectomics quality control and for
human-in-the-loop annotation generally: **does proofreader behavior predict proofreader
competence?** We draw explicitly on **surgical-skill assessment**, where motion telemetry is
decomposed into a vocabulary of gestures ("surgemes") and used to classify skill (the JIGSAWS
benchmark [Gao et al. 2014 — confirm]; the "language of surgery" [Bejar/Lin/Vidal/Hager —
confirm]), and on **tacit knowledge** (Polanyi: "we know more than we can tell") — the idea
that expertise lives in *how* a task is performed, not only in the stated result.

## Results

### A behavioral vocabulary for proofreading
We reconstructed each proofreading session as a sequence over a five-symbol action alphabet
(navigate, segment-edit, annotate, trace, other), classified from the diff-match-patch viewer
telemetry, and recovered per-event 3-D camera kinematics (quaternion orientation, pan, and
zoom) from the same patches (Methods). This yields, per annotator and task type, a transition
grammar, motif n-grams, run-length and inter-event-interval distributions, action entropy,
and exploration kinematics — the components of a "language of proofreading."

### Behavior encodes expertise as a working style
On the dense common task (`multiSomaId`), we compared three representations of increasing
sophistication for separating experts from proto-experts (n=16; held-out cross-validation):
a **naive** tier (four obvious counts), a **designed** tier (the full hand-built grammar +
kinematics, 28 features), and a **learned** tier (an unsupervised k-means **motif
dictionary** of windowed label+timing+rotation "gestures", the surgical-surgeme analog).
ROC-AUC rose **0.75 → 0.95 → 0.90** (Fig. 1). The discriminative signal is concentrated in
**3-D exploration kinematics**: experts accumulate ~2× more total camera rotation and examine
each object from many more viewpoints, and they work ~2× faster. We note honestly that only
the motif dictionary is a *learned representation*; in the designed tier, "learning" is
limited to feature-importance selection.

A structural observation reinforces the interpretation: among students, **only the
agreement-promoted proto-experts ever performed the dense expert task at all** — so the
separation above is between experts and the *best* students, a conservative comparison, and
mere participation in the task is itself a marker of demonstrated competence.

### Achieved accuracy converges across two independent tasks
We measured outcome quality two ways against the same expert graders. On `multiSomaSplit`
(place one split point; quality = distance to the grader consensus point), expert and novice
per-annotator accuracy are **statistically indistinguishable** (medians 309 vs 399 nm,
Mann-Whitney p=0.092) and the single most accurate annotator is a **novice**. On
`fullyProofread` (categorical labeling; quality = exact match of (segment, label, position)
against grader ground truth), accuracy is again indistinguishable (expert vs student medians
0.98 vs 0.97, p=0.63) — a **ceiling effect** (Fig. 3). Consistent with the promotion
mechanism, agreement-promoted students perform at **expert-level accuracy** (median 312 ≈
expert 309 nm) while unpromoted students are more dispersed (median 460 nm). In a workforce
calibrated to agree, the *outcome* has little variance left to predict.

### Coarse per-annotator behavior does not predict competence (a negative result)
Using `fullyProofread` accuracy — which has a discriminating bad tail — as the competence
target, simple telemetry-free per-annotator features (duration statistics, throughput,
thoroughness) show no rank correlation with accuracy (|ρ|≤0.24, all n.s.), and a
leave-one-out good-vs-bad classifier returns AUC 0.14 — but this is **within the leave-one-out
permutation null** (0.45 ± 0.20, p≈0.07), i.e. *no signal*, not a true anti-signal. The negative is
robust: it holds on both ceiling-bound label accuracy and the variance-rich `multiSomaSplit`
distance-to-ground-truth (Ridge ρ=0.07), and survives scale transforms (log, rank) and flexible
regressors (best held-out ρ=0.26, p=0.25). Competence is not legible in coarse per-person summaries —
a result we report plainly, because it bounds what behavioral calibration can and cannot do
retrospectively.

### A ground-truth-free, per-decision uncertainty signal
The signal that *does* survive is at the level of the individual decision and requires **no
ground truth**. Pooling 764 tasks (error base-rate 0.25), a task that is anomalously slow
**for that individual** (within-annotator duration z-score) is significantly more error-prone
(AUC 0.595, ρ=+0.14, p<0.001; raw duration carries nothing, AUC 0.50). Deployed as a
re-review trigger, flagging the most behaviorally-anomalous **20% of tasks recovers 28% of
errors** (1.4× over chance), and the top 10% recovers 15% (1.55×) — using only the
annotator's own behavior (Fig. 4). We read this as a measurable correlate of **subconscious
uncertainty**: hesitation that the annotator does not flag but that their behavior betrays —
the proofreading analog of tacit, motion-legible surgical skill.

### Task risk is predictable, ground-truth-free; the language is a learnable grammar
The corollary of the per-decision result is that competence is legible **per-decision, not
per-person** — and pushing on the *representation*, rather than the model, makes the per-decision case
much stronger. Re-mining the same `fullyProofread` tasks with a richer ground-truth-free description —
within-annotator duration/throughput plus the **point-category composition** of each task — a
gradient-boosted model predicts which tasks are error-prone at **AUC 0.76 on held-out cells** (honest
grouped-by-cell cross-validation; permutation null 0.47 ± 0.02, p<0.001), up from 0.50 for duration
alone. (A naive random split inflates this to 0.92 by memorizing the 28 benchmark cells; grouping by
cell removes the leak.) This is precisely the **risk axis** of an impact×risk allocation: a task's
error-proneness can be scored from its structure *before* any expert time is spent. The same gain does
**not** transfer to per-person ranking — within a fixed cell, behavior separates which annotator erred
at only AUC 0.55 — reinforcing *per-decision, not per-person*.

The behavioral vocabulary is moreover a genuine **grammar**: a first-order Markov model over the
action stream (navigate↔segment↔annotate transitions) recovers expert-vs-proto-expert at LOO AUC 0.95,
matching the hand-built features — the "language of proofreading" is learnable, not merely a metaphor.
More expressive models do not yet pay off at this scale: an unsupervised hidden-Markov grammar collapses
to AUC 0.39–0.59 across 15 annotators, and morphological task-difficulty descriptors (caliber,
branching) do not predict error in the 28-cell benchmark. We read these as **data-limited, not
falsified** — representation learning (HMM→transformer) and structural difficulty become tractable as
dense telemetry is logged on *graded* tasks and the annotator pool scales, which is exactly what the
prospective test and the training pipeline provide. The program is therefore to learn two
representations — behavioral (a sequence grammar) and structural (morphological difficulty) — and let
them meet at the decision: the learnable form of the impact×risk allocation.

## Discussion
Behavior is a strong, interpretable readout of **expertise as a style**, but in this campaign
it is a weak readout of **achieved accuracy** — because the workforce was deliberately
**calibrated to converge**. Agreement-gated promotion compressed outcome variance (proto-
experts perform like experts), so the variance that surgical-skill studies exploit is largely
gone, and the legible behavioral signal moves to (i) who works like an expert and (ii) which
individual decisions carry hidden uncertainty. This reconciles the apparently paradoxical pair
of findings — AUC 0.90 for expertise, no signal for accuracy — and turns a "negative" result
into a statement about calibration: *successful calibration is exactly what makes outcomes
hard to predict from behavior.*

The actionable contribution is prospective and ground-truth-free. A per-decision anomaly
trigger that recovers errors at >1.4× chance, with no reference annotation, is directly
deployable for **adaptive re-review allocation** — spend scarce expert validation where
behavior signals risk. This reframes "calibrate the annotators" as an online, label-free
control problem rather than a retrospective audit.

**Limitations.** Cohorts are small (expertise n=16; per-annotator competence n=36) and effect
estimates are wide; the expertise comparison is retrospective (selection on known outcome) and
is experts-vs-proto-experts, not experts-vs-arbitrary-novices; the poorest performers lack
dense telemetry entirely, so the rich behavioral test cannot yet reach them; identity linkage
through the chunkedgraph operation `user` field is unreliable (executor ≠ assignee) and was
not used for any claim. Two distinct quality tasks show the same ceiling, which strengthens the
convergence interpretation but limits accuracy-prediction power.

**The prospective test.** We pre-register the decisive experiment for the next campaign:
predict competence and flag risky decisions **from early behavior, before outcomes are known**,
on held-out annotators and tasks — promoting and re-reviewing *prospectively* rather than
selecting on outcome after the fact. If early behavior does not predict, we will report that;
the framework's value is that the prediction is now operational and falsifiable.

## Methods
**Data.** NeuVue queue (`queue.neuvue.io`): tasks (assignee, namespace, status, duration,
`ng_state`, `seg_id`, metadata) and **differstacks** (per-event diff-match-patch patches of the
spelunker viewer state + timestamps). CAVE (`minnie65_phase3_v1`): chunkedgraph and
materialization (v18xx) for outcome validation. Grader ground truth from the `patProofread`
namespace (two expert graders).

**Cohorts.** 8 part-time expert proofreaders (prior neuroanatomical-EM training, Janelia;
Nov 2021–Sep 2022) and 36 novice undergraduates (JHU; 26 founders trained Nov 2021, full-time
Jan 2022, part-time to Aug 2022; +10 from Jun 2022). Agreement-promoted "proto-experts" were
granted write access to expert-level tasks.

**Behavioral features.** Action labels from changed JSON keys, hex IDs, and 15–20-digit
segment-ID add/remove in each patch. Grammar: per-(annotator, task) transition matrix, motif
n-grams, run-lengths, inter-event intervals, entropy. Kinematics: per-event quaternion / pan /
zoom recovered from diff-match-patch new-side windows → total rotation, viewpoint diversity,
pan path. **Naive** = {events, events/session, %navigate, median interval}. **Designed** =
the full bank (28). **Learned** = k-means (K=10) over standardized 5-event windows of
[label one-hot, log Δt, rotation], each annotator represented as a normalized histogram over
the learned motifs.

**Targets & statistics.** Expertise = expert vs proto-expert (RandomForest, stratified k-fold
ROC-AUC). Accuracy = `multiSomaSplit` distance-to-consensus and `fullyProofread` exact-match
label accuracy; cohort comparisons by Mann-Whitney. Per-annotator competence classification by
leave-one-out logistic regression with confusion (false-positive and false-negative cases
reported). Per-task uncertainty = within-annotator duration z-score vs per-task error
(ROC-AUC, Spearman); prospective flagging = error recall vs fraction flagged. QC: per-task
distances >2000 nm rejected as detectable bad data.

**Reproducibility.** Analysis scripts (`mine_tiers.py`, `mine_fullyproofread.py`,
`mine_predictive_separability.py`, `prospective_flagging.py`, `make_figures.py`) and a
provenance log (`methodology_provenance.md`, §1–13) accompany this manuscript; a failure-mode
appendix documents approaches tried and retracted.

## Data and code availability
Derived feature tables and figures are provided. Raw telemetry is governed by the MICrONS /
NeuVue data agreements. Code is released with the manuscript.

## Acknowledgments
The NeuVue platform and task-routing infrastructure — **Daniel Xenes** and the NeuVue team —
made this analysis possible; many contributors here began as students we hired and became
co-authors and project members. We thank the expert graders (P. Rivlin, L. Kitchell), the
8-person expert cohort, and the 36-person novice proofreading cohort (top acknowledged
contributors include N. Smith — 24,101 edits — D. Panchal, M. Cook, C. Ordish, C. Knecht,
E. Phillips). We thank the MICrONS Consortium; J. Matelsky and W. Gray-Roncal
(consequence-of-edits / motif census); and the APL NeuroTrailblazers / Research Incubator and
MERIT learning-engineering program.

## References (to finalize)
1. MICrONS Consortium. *Functional connectomics … mouse visual cortex.* Nature (2025). [confirm]
2. D. Xenes et al. *NeuVue: … proofreading workflows.* [confirm]
3. M. Sanchez, D. Moore, E. C. Johnson, B. Wester, J. W. Lichtman, W. Gray-Roncal.
   *Connectomics Annotation Metadata Standardization …* Front. Neuroinform. 16:828458 (2022).
4. Y. Gao et al. *JHU-ISI Gesture and Skill Assessment Working Set (JIGSAWS).* MICCAI MMA (2014). [confirm]
5. Bejar/Lin/Vidal/Hager et al. *The language of surgery / surgeme analysis.* [confirm]
6. M. Polanyi. *The Tacit Dimension* (1966).
7. J. Matelsky, W. Gray-Roncal et al. *Motif-level consequence of proofreading edits.* [confirm]
8. S. Dorkenwald et al. *CAVE / ChunkedGraph proofreading infrastructure.* [confirm]
9. Cervantes, Floryanzia, Johnson, Gray-Roncal et al. *Workforce development (MERIT / Research Incubator).* ASEE/IEEE (2023–2024).
