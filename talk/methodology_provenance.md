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
