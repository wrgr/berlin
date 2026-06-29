# Talk & analysis — proofreader behavior & competency (minnie65 / MICrONS)

Current deliverables for the *language of proofreading* talk and the Nature Communications draft.
Everything in this directory is current; superseded material lives in `archive/` (reversible).

## The result, in one line
Behavioral telemetry encodes **expertise as a working style** (a robust ~0.81 CV signal; experts explore ~2.18× more) but **not achieved accuracy**
(a calibrated workforce converges); competence is legible **per-decision, not per-person** — and
per-task **risk is estimable ground-truth-free at AUC 0.76**, the deployable basis for an impact×risk
allocation of expert effort.

## Deck
- **`Calibrate_the_Humans_v14.pptx`** — current talk (**19 main + 5 backup** slides; "Calibrate the
  Humans, Not Just the Microscope"). The Evidence slide leads with the model-free **~2.18× exploration**
  anchor + the **CV AUC ladder** (`fig_expertise_evidence.png`, learned tier CV-correct at 0.81, designed
  0.98 an exploratory ceiling); the per-decision slide frames ρ=−0.44 as a selection artifact. Pipeline:
  `build_v14.py` (apply reframe to the rebaselined base) → `convert_deck_png_to_jpeg.py` (photos→JPEG,
  27→6.4 MB) → `trim_tighten_v14.py` (merge mechanism+grammar and ecosystem+outreach, RF/PCA/motif →
  backup, condense exposition) → `merge_s3_s4.py` (agents+routing → one slide) → `merge_s8_s9.py` (language-question + JIGSAWS →
  one slide). **`berlin_deck_v11.pptx`** — prior line (`build_v6.py … build_v11.py`).

## Documents
- `nature_comms_draft.md` — paper draft (per-decision-not-per-person → GT-free risk → grammar → scale-up).
- `methodology_provenance.md` — methods & provenance: every claim with the analysis behind it.
- `transparency_failure_modes.md` — retractions, dead ends, robustness checks, honest negatives.
- `figure_descriptions.md` — per-figure legends synced to the analysis (mapped to v10 slides).
- `deck_coherence_review.md`, `deck_v5_changes.md` — deck change logs.

## Figures (in deck + spares)
In-deck: `fig_expertise_evidence` (honest AUC ladder + 2.18× anchor, S13), `fig_prospective_flagging`,
`fig_kinematics`, `fig_action_grammar`, `fig_rf_importance_new`, `fig_feature_pca`, `fig_motif_usage`,
`fig_accuracy_threegroup`, `fig_uncertainty_calibration`, `fig_task_risk`, `fig_accuracy_unpredictable`
(backup). Methods/audit: `fig_fishing_audit` (single-feature histogram + trivial-fit ladder),
`fig_grammar_morphology`. Spares: `fig_tier_auc` (superseded), `fig_motif_dictionary`,
`fig_two_task_quality`, `fig_separability`. All carry a *"Preliminary — MICrONS annotators"* stamp; handles suppressed.

## Analysis (`analysis/`)
Reproducible pipeline. **Core figures + CSVs:** `run_all.py` — network stages 1–3 mine NeuVue + CAVE;
offline stages 4–6 rebuild the core figures from cached CSVs (`--offline`). **The current deck**
(`Calibrate_the_Humans_v14`) is built by `build_v14.py` from the rebaselined base (`build_v6.py … build_v11.py`
is the prior `v5` line); the S13 evidence figure is `make_expertise_evidence_fig.py`, the fishing
audit is `fishing_audit.py` + `motif_cv.py`, and the ρ=−0.44 check is `rho_robustness.py`. **The risk / grammar figures** come from `enrich_fullyproofread.py` +
`explore_task_risk_prediction.py` (risk) and `extract_streams.py` + `grammar_probe.py` +
`cave_morphology.py` (grammar / morphology). Network stages need NeuVue + CAVE credentials (not
committed); per-annotator CSVs carry annotator handles and are deliberately not committed. See
`analysis/README.md`.

## Archive (`archive/`)
Superseded decks (v2–v4, v6–v10), early plots (incl. the retracted axon-GT figure), and early analysis
notes — moved out so the main directory is all-current. Nothing deleted; see `archive/README.md`.
