# Rich behavioral language: encodes expertise, not per-task accuracy

The talk's core result — a **cross-task, learned** representation, the right way.

## Design (solves the telemetry/GT mismatch)
- **Features**: rich behavioral bank learned from the **dense `multiSomaId`** telemetry
  (task-controlled; 2,600–4,000 events/annotator) — behavior-mix, transition grammar,
  motif n-grams, run-lengths, interval distributions, entropy, and **3D kinematics**
  (per-patch quaternion/pan recovery → total rotation, #rotations, viewpoint diversity).
- **Targets**: the validated **`multiSomaSplit` distance-to-GT** quality, and the
  expert/student cohort. n = 15 annotators (8 expert, 7 student) with both.
- Held-out CV; QC outlier drop (>2000 nm).

## Result
- **[A] Behavior → expert vs student: CV ROC-AUC = 0.90 (±0.20).** Top features are
  3D-exploration kinematics: `n_rot` (experts 14 vs proto-experts 6), `total_rot_deg`
  (1014° vs 466° — **~2× more viewpoints**; per-differstack rotation, corrected), `n_events` (3033 vs 1426). Experts
  examine structure from far more angles and are far more thorough.
- **[B] Behavior → per-split accuracy (distance-to-GT): CV R² = −5.1.** No signal;
  weak univariate hints only (`pct_annotate` −0.44, `tg_SSN` +0.51).

## Interpretation (the headline)
The rich behavioral "language of proofreading" **encodes *expertise*** — who is
trained/experienced — **strongly and interpretably (3D exploration), but it does NOT
encode per-task *accuracy***. Consistent with experts and students achieving similar
distance-to-GT (302 vs 295 nm, p=0.98) while being 0.90-separable by *how* they work,
and with experts being ~2× faster. **Expertise is a behavioral style; achieved
accuracy is similar across levels.**

Connections: experts here include **Natalie Smith (N. Smith — #1 acknowledged
proofreader, 24,101 edits)**. The 3D-exploration signature echoes surgical-skill
assessment ("language of surgery"): experts move/inspect differently, but trained
novices reach comparable outcomes.

## Caveats
n=15 (AUC CI wide ±0.20); the n_events gap partly reflects telemetry volume — the
per-session rate (32 vs 21) and rotation counts mitigate but don't eliminate this.
Cross-task: behavior on `multiSomaId`, quality on `multiSomaSplit` (same annotators).
Next: expand N (more annotators with both), add time-warp-invariant motif dictionaries,
and a second dense task to test task-generality of the expertise signature.
