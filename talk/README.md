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
  numbers, centered figure legends, NIH disclaimer). The only deck in this directory; all
  superseded versions (the human-edited base `v5` and intermediates `v2–v4`, `v6–v10`) live in
  `archive/decks/`. Derivation is scripted: `analysis/build_v6.py … build_v11.py` (each reads the
  prior deck, starting from the `v5` base); per-slide speaker notes are completed by
  `analysis/add_speaker_notes.py` (source: `talk_script.md`).
- **`berlin_deck_short.pptx`** — a ~7-slide condensation (the main point + the big idea), themed on
  *an agent is agnostic to human or machine*. Built by `analysis/build_short_deck.py` from `v11`
  (scripted/reversible); story arc in `talk_short_story.md`.

## Documents
- `nature_comms_draft.md` — paper draft (per-decision-not-per-person → GT-free risk → grammar → scale-up).
- `methodology_provenance.md` — methods & provenance: every claim with the analysis behind it.
- `transparency_failure_modes.md` — retractions, dead ends, robustness checks, honest negatives.
- `figure_descriptions.md` — per-figure legends synced to the analysis (mapped to v11 slides).
- `talk_script.md` — per-slide speaker script (beats + takeaways); the source for the deck's speaker notes.
  (Deck change logs for the superseded transitions are in `archive/notes/`.)

## Figures (in deck + spares)
In-deck: `fig_tier_auc`, `fig_prospective_flagging`, `fig_kinematics`, `fig_action_grammar`,
`fig_rf_importance_new`, `fig_feature_pca`, `fig_motif_usage`, `fig_accuracy_threegroup`,
`fig_uncertainty_calibration`, `fig_task_risk`, `fig_accuracy_unpredictable` (backup).
Methods: `fig_grammar_morphology`. Spares: `fig_motif_dictionary`, `fig_two_task_quality`,
`fig_separability`. All carry a *"Preliminary — MICrONS annotators"* stamp; handles suppressed.

## Analysis (`analysis/`)
Reproducible pipeline. **Core figures + CSVs:** `run_all.py` — network stages 1–3 mine NeuVue + CAVE;
offline stages 4–6 rebuild the core figures from cached CSVs (`--offline`). **The current deck**
(`berlin_deck_v11`) is built by the `build_v6.py … build_v11.py` chain from the `berlin_deck_v5` base
(each reads the prior deck; the base + intermediates are staged from `archive/decks/`).
**The risk / grammar figures** come from `enrich_fullyproofread.py` +
`explore_task_risk_prediction.py` (risk) and `extract_streams.py` + `grammar_probe.py` +
`cave_morphology.py` (grammar / morphology). Network stages need NeuVue + CAVE credentials (not
committed); per-annotator CSVs carry annotator handles and are deliberately not committed. See
`analysis/README.md`.

## Archive (`archive/`)
Superseded decks (v2–v10, incl. the human-edited `v5` base), superseded build scripts
(`build_deck.py`, `build_v5.py`), deck change logs, early plots (incl. the retracted axon-GT
figure), and early analysis notes — moved out so the main directory is all-current. Nothing
deleted; see `archive/README.md`.
