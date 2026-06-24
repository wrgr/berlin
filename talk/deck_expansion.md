# Deck expansion — "When have we proofread enough to trust the answer?"

Companion spec for the expanded deck (`berlin_deck_v3.pptx`, generated from `berlin_deck_v2.pptx`).
v2 is already the reframed, mature talk: *connectomic proofreading as constrained
optimization → price the budget → calibrate the people*. Its slide 9 already names the
punchline — **staged promotion by agreement (NeuVue); predict competence from early
behavior is the open test.** This expansion grounds that arc in the real workforce, adds
the behavioral evidence, and adds learning-engineering + outreach + acknowledgments.

## The reframing in one paragraph
The rich behavioral "language of proofreading" **encodes expertise (a working style),
not per-task accuracy**. Experts and trained novices place the same split point about
equally well, but they *work* differently — experts inspect from ~3× more viewpoints and
finish faster. Meanwhile the campaign already ran a **calibration mechanism**:
agreement-gated promotion of students to a proto-expert tier. So the scientific question
is not "can we grade a point" — it's **"can we price human judgment early enough to
allocate it,"** and the behavior signal says competence *is* legible. The honest status:
this is **retrospective** (selection on known outcome); the **predictive** test is
pre-registered for this summer.

## Authoritative cohort facts (NeuVue paper — use verbatim where possible)
- **8 part-time expert proofreaders.** Prior training + proofreading experience with
  neuroanatomical EM data at **Janelia**; worked part-time **Nov 2021 – Sep 2022**.
- **36 novice proofreaders.** Undergraduates from **Johns Hopkins University**. **26**
  entered the initial cohort, received **three weeks of training in Nov 2021**, proofread
  **full-time for three weeks in Jan 2022**, then part-time through **Aug 2022**; **10**
  more joined in **June 2022**, part-time through Aug 2022.
- **Shared curriculum:** neuroanatomy, interpretation of EM imagery + segmentation
  overlays, the NeuVue interface, and the **decision logic for each task type**.
- **Staged promotion (learning engineering):** students whose task outcomes showed
  **high agreement with expert decisions** were promoted to a **proto-expert** group and
  granted **write permissions for selected expert-level tasks** — systematic workforce
  calibration.
- **CONNECTS-Proof:** the same task-routing framework was reused for expert validation of
  **NEURD-generated edits on H01**, at small scale (2 expert proofreaders).
- Built and recorded on **NeuVue** (Daniel Xenes et al.).

## Promoted (proto-expert) handles — authoritative, from the project lead
`dylan, vivia, taylor, clara, rachel, shruthi, sarah, lydia` (8).
- **`lydia` is new** — not present in the multiSomaSplit / fullyProofread grading-notebook
  student lists; flagged. (No multiSomaSplit distance row for lydia.)
- **Promoted ≠ paper-credited.** Promotion is an *internal, agreement-gated quality*
  signal; MICrONS acknowledgment is an *external, edit-volume* signal. They measure
  different things, so mismatches are expected. **Most-likely mismatch (per the lead):
  promoted but not acknowledged in the paper** — good annotations, lower raw throughput.
  Resolving exact handle→name for each promoted student needs the CAVE change-log identity
  pass (`mine_credited_axis.py`); flag any promoted student we *cannot* place in the ack
  list, and any acknowledged student who was *not* promoted.

## Honest feature-learning status — naive → designed → learned (REQUIRED framing)
The features are **not yet a truly learned representation**. State this plainly and show
all three tiers:
1. **Naive** — a few obvious counts (events, rate, %navigate, median interval).
2. **Designed** — the full hand-built rich bank (behavior-mix, transition grammar, motif
   n-grams, run-lengths, interval distributions, entropy, **3D kinematics**). What is
   "learned" here is only the **Random Forest picking which designed features matter**
   (importance) — not a learned representation.
3. **Learned** — an **unsupervised motif dictionary**: k-means "gestures" over windowed
   event streams (label + timing + rotation); each annotator = a histogram over learned
   motifs. This is the "language of surgery" analog (learned surgemes / dictemes), the
   honest next step beyond hand design. (Results from `mine_tiers.py`.)
Deliverable: one bar chart, AUC(naive) ≤ AUC(designed) ≈/≤ AUC(learned) on the same target
(expert-vs-novice and promoted-within-students). Report it even if learned ≈ designed —
the point is methodological honesty.

## Per-annotator accuracy (multiSomaSplit) — answers "are we too clustered?"
Distance-to-GT (nm), lower = better. ★ = promoted. QC drops stella (8841 nm, bad point).
- **Experts (n=8):** natalie 122 · claire 207 · erika 289 · chris 302 · phillips 315 ·
  gary 328 · michael 447 · christopher 511. **median 309, range 122–511.**
- **Students (n=26):** rupa 93 · mia 199 · makayla 212 · shruthi ★286 · dylan ★307 ·
  rachel ★309 · joey 311 · sarah ★312 · katie 315 · taylor ★352 · aashi 358 · krutal 363 ·
  jonas 373 · sean_sebastian 426 · titus 460 · clara ★461 · emily 468 · cindy 477 ·
  tina 491 · emma 536 · maryam 557 · luzhou 571 · vivia ★573 · luke 578 · oji 832 ·
  trystan 992. **median 399, range 93–992.**
- **Cohorts overlap heavily:** Mann-Whitney **p = 0.092** (not significant); the single
  best annotator is a **novice** (rupa, 93 nm); experts span the full range.
- **YES — this task is too clustered to predict accuracy.** It is one-point placement
  where trained novices match experts; distance-to-GT has little discriminating variance
  (CV ≈ 0.45, IQR ≈ 180 nm). That is *why* behavior→accuracy fails (R² = −5.1): there is
  almost no accuracy signal to predict. Behavior→**cohort** works (AUC 0.90) because the
  *style* difference is real even when the *outcome* is not separable.
- **But the promotion labels are meaningful:** promoted students cluster at **expert-level
  accuracy** (median ≈ 312 nm ≈ expert 309) while non-promoted students scatter wider
  (median ≈ 460 nm). Agreement-gated promotion picked the students who perform like
  experts — an independent validation of the labels. (Significance: see build verification.)

## Other task types — `fullyProofread` as a sharper quality target
Replicated metric (from `fullyProofread_*` notebooks): annotators label points by category
(`spine, nucleus, dendrite, axon, soma`); ground truth = graders (`rivlipk1, kitchlm1`) on
**`patProofread`**; score = match of `(seg_id, label, position)` (notebook uses exact
match; we also compute proximity-relaxed same-label matching). This is **categorical label
accuracy**, not one-point distance — potentially more discriminating than multiSomaSplit.
(Results from `mine_fullyproofread.py`.) StudentLabeling, dendExtension, axonExtension,
singleSomaCleanUp remain as further targets.

---

# New slides (insert into v3 at the marked positions)

### A — "Who we calibrated: the proofreading workforce"  (after slide 8 "calibrating")
KICKER: THE PEOPLE BEHIND THE BUDGET
- 8 part-time **expert** proofreaders — prior EM / neuroanatomy training at Janelia (Nov 2021–Sep 2022).
- 36 **novice** proofreaders — Johns Hopkins undergraduates. 26 founders (3 weeks training → full-time in January → part-time through August); 10 more joined in June 2022.
- One curriculum: neuroanatomy, EM interpretation, segmentation overlays, the NeuVue interface, per-task decision logic.
- Routed and recorded on NeuVue (Xenes et al.).
BOTTOM LINE: "Calibrate the annotators" isn't a metaphor — it's 44 people and a training pipeline.

### B — "Learning engineering: agreement-gated promotion"  (after A)
KICKER: CALIBRATION WAS DESIGNED, NOT ASSUMED
- Students whose decisions agreed with experts were promoted to a **proto-expert** tier — with write permission for expert-level tasks.
- A learning-engineering loop: train → practice → **measure agreement** → promote → widen scope. (Not a vibe — a mechanism.)
- Proto-expert cohort: dylan, vivia, taylor, clara, rachel, shruthi, sarah, lydia.
- Reused in CONNECTS-Proof to validate NEURD edits on H01.
- Same thesis as APL's MERIT / AI Pathfinding: assessment as a **learning diagnostic**; deliverables that outlive the cohort.
BOTTOM LINE: promotion-after-agreement is selection on outcome — can we predict it from early behavior instead?

### C — "Preliminary evidence: competence is legible in behavior"  (after slide 9)
KICKER: THE LANGUAGE OF PROOFREADING
- Dense per-event telemetry (multiSomaId): every navigate / edit / annotate, with 3D camera motion.
- Behavior → expert vs novice: **AUC ≈ 0.90.** Experts inspect from ~3× more viewpoints; far more thorough.
- Behavior → per-task accuracy: ~no signal — trained novices match experts on the placement itself.
- Reading: behavior encodes **expertise (style), not achieved accuracy** — the pattern surgical-skill assessment finds.
- Promoted students perform at **expert accuracy (~310 nm)**; non-promoted scatter (~460+) — the labels are real.
- Three representations, increasing honesty: **naive → designed → learned** (motif dictionary).
CAVEAT BANNER: RETROSPECTIVE — selection on a known outcome. The pre-registered predictive test is this summer.

### D — "Outreach: students as a method, not just a mission"  (before acknowledgments)
KICKER: HUMANS + OUTCOMES  (LENS)
- Calibrated student judgment IS the method that built the connectome — not a side benefit.
- **MICrONS relied on this student workforce throughout** — their proofreading underpins the MICrONS connectome (**Nature, 2025**) and downstream contributions. [confirm exact MICrONS Nature citation]
- Dual yield, **structurally identical**: a better connectome (mission) AND trained scientists (talent) — novices became top-throughput proofreaders credited in MICrONS; eight promoted to expert tasks.
- Promotion is a **mentorship ladder**, not just a permission flag — APL's AI Pathfinding / MERIT model.
- "Calibrate the people, not just the microscope" is an investment in people, **measured**.
BOTTOM LINE: the measurement that prices the budget is the same measurement that develops the workforce.

### E — "Acknowledgments & contributions"  (before "Thank you")
KICKER: A TEAM EFFORT
- **NeuVue** platform & task routing — **Daniel Xenes** and the NeuVue team (the substrate for all of this).
- **Graders / experts** — Pat Rivlin, Lindsey Kitchell; the 8-person expert cohort.
- **Proofreading team** — the 36 JHU novices; top acknowledged contributors incl. N. Smith (Natalie, 24,101 edits), D. Panchal, M. Cook, C. Ordish, C. Knecht, E. Phillips.
- **Datasets & analysis** — MICrONS Consortium; Matelsky & Gray Roncal (consequence-of-edits / motif census); Morgan & Sanchez [CONFIRM exact citation]; CONFIRMS; H01 / CONNECTS-Proof.
- **Institutions** — JHU APL · Johns Hopkins University · Janelia Research Campus · Allen Institute.

## Resolved citation
"the Morgan–Sanchez paper" = **M. Sanchez, D. Moore, E. C. Johnson, B. Wester,
J. W. Lichtman, W. Gray-Roncal — "Connectomics Annotation Metadata Standardization for
Increased Accessibility and Queryability," Frontiers in Neuroinformatics 16:828458 (2022).**
Slide E updated. Workforce-model refs: Cervantes et al. (ASEE 2023), Floryanzia et al.
(IEEE STEM 2024), Johnson et al. (IEEE STEM 2023).

## Computed results (this run) — fold into slide C / appendix
- **Three tiers, expert vs proto-expert (n=16, CV ROC-AUC):** naive **0.75** → designed
  **0.95** → learned **0.90**. Designed (hand-built bank) ≈ learned (unsupervised 10-motif
  k-means dictionary over windowed label+timing+rotation); both >> naive. Honest: in the
  designed tier only RF *importance* is learned; the motif dictionary is the genuine learned
  representation (language-of-surgery analog).
- **Participation = promotion signal:** only the 8 promoted students have dense multiSomaId
  telemetry; non-promoted students never got that expert-level task. So the AUC separates
  experts from *proto-experts* — conservative.
- **Accuracy ceiling-clusters on two tasks:** multiSomaSplit (expert 309 vs student 399 nm,
  p=0.092; promoted 312 ≈ expert 309 < unpromoted 460) and fullyProofread labels (expert
  0.98 vs student 0.97, p=0.63) — but fullyProofread surfaces a bad tail (maggie 0.22;
  gary/michael ≈0.74) = QC value, and some non-promoted students are perfect
  (sean_sebastian 1.00).
- **Net:** trained accuracy converges; behavioral style separates skill. Calibration worked,
  so you must price the *process* — which is the talk.
- Figures to add: tier-AUC bar (naive/designed/learned); learned motif-dictionary heatmap;
  per-annotator accuracy strip for both tasks, promoted highlighted.
