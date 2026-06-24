# Methodology & Provenance — Proofreader Behavior & Quality (minnie65)

Living methods/provenance record for the talk and the Nature Communications draft.
Supersedes earlier conclusions where noted (several were corrected — see §8).

## 1. Goal
Quantify proofreader **behavior** ("the language of proofreading") and **competency**
(quality of work) in the minnie65 connectome proofreading effort, and test whether
behavior predicts competency. Anchor competency in **outcome ground truth**, not
inter-annotator agreement.

## 2. Data sources
- **NeuVue queue** (`queue.neuvue.io`): tasks (assignee, namespace, status, duration,
  `ng_state`, `seg_id`, metadata) and **differstacks** (per-event spelunker telemetry:
  diff-match-patch patches of the viewer state + timestamps).
- **CAVE** (`minnie65_phase3_v1`): chunkedgraph (roots, operations, lineage),
  cloudvolume (point→supervoxel), materialization (v18xx). Token-gated.
- Task `ng_state` is inline JSON (wrapper-aware parse: `{generation, value:{layers}}`).

## 3. Cohorts (multiSomaSplit grading study) — CORRECTED
Defined by the project's grading notebooks (`multiSomaSplit_quality_figures.ipynb`):
- **Graders / ground truth**: `rivlipk1` (Pat), `kitchlm1`.
- **Experts** (8): chris, christopher, claire, erika, gary, michael, natalie, phillips.
- **Students** (29): aashi, clara, dylan, emma, emily, joey, jonas, katie, krutal,
  luzhou, mia, oji, rachel, rupa, sarah, sean_sebastian, shruthi, taylor, titus, vivia,
  stella, maggie, makayla, maryam, tina, luke, trystan, cindy.
- **Correction**: earlier analyses mislabeled the *expert* cohort as "students" and
  compared them to Pat. They clustered near Pat because they *are* experts. All
  expert/student claims prior to this doc are re-derived here.

## 4. Ground truth & competency metric (multiSomaSplit)
Task = place **one split point** (x,y,z) on a multi-soma object (`seg_id`).
- **GT point** per `seg_id` = mean of grader (Pat, kitchlm1) submitted points.
- **Competency = Euclidean distance(submission, GT)**, scaled ×4 → nm. Lower = better.
- Cohort-level agreement uses the **cohort-mean** point per `seg_id` vs GT, threshold
  300 (units) ≈ 1200 nm; per-annotator uses **median distance** over that annotator's
  GT-overlapping tasks.
- 18 `seg_id`s have grader GT; each annotator did ~6 of them.

## 5. Quality QC / edge-case rejection
Gross-outlier submissions are **detectable bad data** and are rejected, not scored as
skill. Rule: drop per-task distances **> 2000 nm** (notebook default). Example:
`stella` has an 8841 nm point — a misplaced/bad submission, flagged automatically. This
QC step is a deliverable in its own right: the pipeline can reject well-intentioned but
bad data. (Open: distinguish a single bad point from a consistently-bad annotator.)

## 6. Behavioral telemetry (differstacks) — availability & provenance
- **multiSomaSplit telemetry is expert-only and sparse.** Experts (2021-12-01) have
  1064 events total (~3/task); students (2021-11-24) have **0** — they predate the
  telemetry deployment / were a separate uninstrumented run. Confirmed by task dates
  and by absence even ignoring the `active` flag.
- Consequence: multiSomaSplit supports duration + submission-state features for all,
  but **not** a deep learned process model. For rich behavioral sequences use
  **dense-telemetry task types** (dendExtensionLevel*, singleSomaCleanUp,
  functionalCellClean, axonExtension — thousands of events each).

## 7. Behavioral feature extraction (established)
- **Behavior dictionary** from differstack patches: navigate / segment(edit) /
  annotate / trace / other (classified by changed JSON keys, hex IDs, segment-ID
  add/remove). Validated event labels.
- **Grammar**: per-(user,task-type) transition matrix P(next|current); motif n-grams;
  run-lengths; inter-event interval distributions; entropy; tempo.
- **3D trajectory** (where dense): per-patch camera reconstruction (quaternion / pan /
  zoom recovered from diff-match-patch windows) → viewpoint diversity, pan-directedness,
  zoom-at-decision.
- **Planned (rich learned set)**: motif dictionaries (clustered subsequences),
  time-warp-invariant (DTW) descriptors, kinematic descriptors — learned, not
  hand-picked, with held-out validation; informed by surgical-skill assessment
  ("language of surgery", JIGSAWS).

## 8. Findings to date (corrected) and retractions
- **multiSomaSplit per-annotator accuracy does NOT separate experts from students**
  (median 302 vs 295 nm, p=0.98). The cohort-level 33-vs-264 nm gap is a *consensus
  averaging* effect (experts agree → tight mean), not individual accuracy.
- **Duration separates cohorts**: experts 2.3 vs students 4.2 min/task (p=0.004).
- **RETRACTED**: the v18xx axon "correctness" GT (endpoint- and path-separation) —
  failed the Pat≈1 sanity check (Pat scored 0.57; 95% of objects read "separated"
  downstream regardless of the decision). Any "behavior predicts conformity not
  correctness" claim built on it is withdrawn.
- **Valid competency surrogate** where an expert shares objects: **agreement-with-Pat**
  on identical objects (axonOnDendriteV3, passes Pat≈1). Discriminates 0.42–0.95.
- Across every *valid* test so far, **behavior does not robustly predict competency**,
  but samples are small (n≈9–16) — underpowered, not settled.

## 9. Provenance (scripts/commits)
All analysis scripts under the session scratchpad; figures/docs committed to `talk/`.
Key scripts: `mine_all_minnie65.py` (behavior dictionary), `mine_axon_valid_gt.py`
(path/synapse GT — retracted), `mine_pat_anchored.py` (Pat-anchored competency),
`mine_richer_features.py` (order-tolerant features). Each run refreshes the NeuVue
token and is reproducible from cached task tables.

## 10. Open items for the paper
- Build the **rich learned feature set** on a dense-telemetry task (pair with the
  multiSomaSplit quality metric).
- Power: expert-anchored competency is inherently small-N; quantify the ceiling.
- QC: formalize bad-data rejection (single bad point vs bad annotator).

## 11. Cross-task design + handle identities (the talk's analytical core)
**Decisive telemetry finding** (verified across all 6 grading notebooks + the data):
the grading tasks (`multiSomaSplit`, `fullyProofread`, `patProofread`,
StudentLabeling) record **only a final `ng_state` point + duration — no differstacks**.
They are quick drop-a-few-labeled-points tasks (~5–8 annotations/task). Dense
behavioral telemetry lives in the **extension/cleanup tasks**: experts on
`singleSomaCleanUp` (chris ≈920 events/task), `functionalCellClean`,
`neuronOtherBodies`; students on `dendExtensionLevel3` (≈400–1000 events/task),
`axonExtension`. **`multiSomaId` is the common dense task both cohorts share.**

**Design**: extract a rich learned behavioral representation from **`multiSomaId`**
(task-controlled, dense) per annotator → predict the validated **`multiSomaSplit`
distance-to-GT** quality (and cohort, and acknowledgment edit-count). Feature bank:
behavior-mix, transition grammar, motif n-grams, run-lengths, interval distributions,
entropy, and **3D kinematics** (per-patch quaternion/pan recovery → total rotation,
viewpoint diversity, pan path). n ≈ 37 annotators with both. Held-out (annotator-
grouped) validation; surgery-skill ("language of surgery") framing.

**Handle → real identity** (via CAVE operation `user` field + change-log `user_name`):
- `natalie` → **Natalie Smith** = N. Smith (**24,101 edits — #1 acknowledged proofreader**)
- `christopher` → **Christopher Knecht** = C. Knecht (7,199 edits)
- `kitchlm1` → Lindsey Kitchell (grader); `rivlipk1` → P. Rivlin (grader); `erika` →
  Erika Neace (not acknowledged).
- **Caveat**: the operation `user` is who *executed* the split in CAVE — `gary` also
  resolved to Knecht, so an executor/reviewer can differ from the neuvue assignee.
  Identity needs corroboration (handle name + edit-volume + the project roster) before
  publication. The acknowledged top proofreaders are the expert/student top performers,
  per the project lead.

## 12. Update — authoritative cohort, promoted axis, three-tier features, fullyProofread
(This session; supersedes the cohort counts in §3.)

**Authoritative cohort (NeuVue paper).** 8 part-time expert proofreaders (prior
neuroanatomical-EM training at Janelia; Nov 2021–Sep 2022) and **36** novice proofreaders
(JHU undergraduates: 26 founders trained 3 wks Nov 2021 → full-time 3 wks Jan 2022 →
part-time to Aug 2022; +10 joined Jun 2022). Shared curriculum: neuroanatomy, EM/overlay
interpretation, the NeuVue interface, per-task decision logic. **Staged promotion**: students
whose decisions agreed with experts were promoted to a **proto-expert** tier with write
access to expert-level tasks (systematic workforce calibration). Same routing reused in
CONNECTS-Proof for H01 NEURD validation (2 experts).

**Promoted (proto-expert) handles (authoritative, project lead):** dylan, vivia, taylor,
clara, rachel, shruthi, sarah, **lydia** (lydia not in the grading-notebook student lists —
flagged). Promoted ≠ paper-credited: promotion = internal agreement-gated quality; MICrONS
acknowledgment = external edit-volume. Expected mismatch = promoted-but-not-credited (and
e.g. sean_sebastian, non-promoted, scores 1.00 on fullyProofread labels).

**Structural finding — participation is a promotion signal.** Of all students, only the 8
promoted ones have dense `multiSomaId` telemetry; non-promoted students never received that
expert-level task. So the behavioral "expert vs student" model in fact separates **experts
from proto-experts** (conservative), and *doing* the dense task is itself evidence of
promotion.

**Three-tier representation (naive → designed → learned), CV ROC-AUC, expert vs proto-expert
(n=16):** naive (4 counts) **0.75** → designed (28 hand-built) **0.95** → learned (10-motif
unsupervised k-means dictionary over windowed label+timing+rotation streams) **0.90**. Honest
status: "designed" is hand-built — only RF *importance* is learned; "learned" is the genuine
unsupervised representation (language-of-surgery analog). Both beat naive; designed ≈ learned.
(`mine_tiers.py` → `tiers_data.csv`.)

**Accuracy is ceiling-clustered across TWO task types** (so behavior can't predict it):
- multiSomaSplit distance-to-GT: expert median 309 nm vs student 399 nm, MW p=0.092; best is
  a novice (rupa 93). Promoted 312 ≈ expert 309 < unpromoted 460 (promoted vs expert p=0.46;
  vs unpromoted p=0.21 — n.s. at n=7/19, but ordering matches the promotion mechanism).
- fullyProofread categorical label accuracy vs `patProofread` GT (graders rivlipk1, kitchlm1;
  exact (seg_id,label,position) match valid — positions pre-placed, 5730/6124 strict): expert
  median 0.98 vs student 0.97, MW p=0.63. Ceiling effect, BUT a discriminating bad tail
  (maggie 0.22; experts gary 0.75 / michael 0.73; emily 0.78) → QC value. (`mine_fullyproofread.py`.)
- **Lesson:** a well-calibrated workforce converges on accuracy; *behavioral style* separates
  skill levels. Calibration worked → outcomes converged → price the process.

**CAVE identity caveat.** handle→CAVE-uid via operation `user` is unreliable: gary and
christopher both map to uid 1833 (executor ≠ neuvue assignee), and change-log `user_name` did
not resolve this run. Use the project lead's list for identity, not CAVE.

**Resolved citation.** "the Morgan–Sanchez paper" = M. Sanchez, D. Moore, E. C. Johnson,
B. Wester, J. W. Lichtman, W. Gray-Roncal, "Connectomics Annotation Metadata Standardization
for Increased Accessibility and Queryability," Front. Neuroinform. 16:828458 (2022).

**Talk framing.** Outreach reframed per the Research Incubator deck: **students as a *method***
for mission impact (not workforce-dev-as-nicety); MERIT / NeuroTrailblazers learning
engineering; "calibrate the people, not just the microscope." Deck: `berlin_deck_v3.pptx`
(+ `deck_expansion.md`).

## 13. Item 1 — prospective, GT-free competence signal (the open question)
Target with variance = **fullyProofread label accuracy** (the bad tail), not the ceiling-
clustered split task. Min 10 tasks/annotator; n=36.

**Annotator-level competence is NOT legible in simple behavior (honest negative).** Per-
annotator duration/throughput/thoroughness features show ~zero rank correlation with accuracy
(|rho|≤0.24, all n.s.); a LOO good-vs-bad classifier scores **AUC 0.14** (worse than chance) —
it missed all 5 bad annotators (FN: maggie, donovan9, gary, stella, emily) and false-flagged 5
good ones (FP: jonas, maryam, makayla, titus, clara). Coarse per-person summaries do not price
competence.

**Per-task uncertainty IS weakly legible, prospectively and GT-free.** Pooling 764 tasks (error
base-rate 0.25): a task **slow for that person** (within-annotator duration z) is significantly
more error-prone — **AUC 0.59, rho=+0.14, p<0.001** (raw duration AUC 0.50; pts n.s.; pooled
dur_z+pts_z AUC 0.58). Small but real, and uses no ground truth — it flags individual risky
decisions = **"subconscious uncertainty."**

**Framing — language of surgery / tacit knowledge / JIGSAWS.** Proofreading analog of surgical-
skill assessment: motif dictionary ↔ surgemes (JIGSAWS); behavioral kinematics ↔ surgical
motion; "skill lives in HOW, not WHAT" ↔ tacit knowledge (Polanyi, "we know more than we can
tell"). Key difference: JIGSAWS skill is strongly legible because outcomes vary; here the
workforce was **calibrated to converge**, so outcome variance is gone and the signal moves to
(a) expertise *style* (AUC 0.90) and (b) per-task *uncertainty* (AUC 0.59). The prospective
claim — flag from behavior, pre-registered, no GT — is the open work.

**Data limit.** The worst annotators (maggie, donovan9, emily, mia) have **no dense telemetry**
anywhere; rich behavior exists mainly for high-competence annotators (gary, michael on cleanup;
cindy, joey on extension — joey 15.8k events on dendExtensionLevel3). A richer prospective test
is possible for those few but cannot reach the bad tail. (`mine_predictive_separability.py` →
`separability_annotator.csv`, `separability_task.csv`; fig `fig_separability.png`.)
