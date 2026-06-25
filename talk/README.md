# Talk & analysis — proofreader behavior & competency (minnie65 / MICrONS)

Current deliverables for the *language of proofreading* talk and the Nature Communications draft.
Everything in this directory is current; superseded material lives in `archive/` (reversible).

## The result, in one line
Behavioral telemetry encodes **expertise as a working style** (AUC 0.90) but **not achieved accuracy**
(a calibrated workforce converges); competence is legible **per-decision, not per-person** — and
per-task **risk is estimable ground-truth-free at AUC 0.76**, the deployable basis for an impact×risk
allocation of expert effort.

## Deck
- **`berlin_deck_v11.pptx`** — current talk (23 slides; incorporates a review pass — page
  numbers, centered figure legends, NIH disclaimer). **`berlin_deck_v5.pptx`** — human-edited base.
  Derivation is scripted: `analysis/build_v6.py … build_v11.py` (each reads the prior deck from `v5`).

## Documents
- `nature_comms_draft.md` — paper draft (per-decision-not-per-person → GT-free risk → grammar → scale-up).
- `methodology_provenance.md` — methods & provenance: every claim with the analysis behind it.
- `transparency_failure_modes.md` — retractions, dead ends, robustness checks, honest negatives.
- `figure_descriptions.md` — per-figure legends synced to the analysis (mapped to v10 slides).
- `deck_coherence_review.md`, `deck_v5_changes.md` — deck change logs.

## Figures (in deck + spares)
In-deck: `fig_tier_auc`, `fig_prospective_flagging`, `fig_kinematics`, `fig_action_grammar`,
`fig_rf_importance_new`, `fig_feature_pca`, `fig_motif_usage`, `fig_accuracy_threegroup`,
`fig_uncertainty_calibration`, `fig_task_risk`, `fig_accuracy_unpredictable` (backup).
Methods: `fig_grammar_morphology`. Spares: `fig_motif_dictionary`, `fig_two_task_quality`,
`fig_separability`. All carry a *"Preliminary — MICrONS annotators"* stamp; handles suppressed.

## Analysis (`analysis/`)
Reproducible pipeline. `run_all.py` orchestrates the stages (`--offline` rebuilds figures + deck from
cached CSVs). Network stages need NeuVue + CAVE credentials (not committed); per-annotator CSVs carry
annotator handles and are deliberately not committed. See `analysis/README.md`.

## Archive (`archive/`)
Superseded decks (v2–v4, v6–v10), early plots (incl. the retracted axon-GT figure), and early analysis
notes — moved out so the main directory is all-current. Nothing deleted; see `archive/README.md`.
