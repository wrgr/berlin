# Talk & analysis — proofreader behavior & competency (minnie65 / MICrONS)

Current deliverables for the *language of proofreading* talk and the Nature Communications draft.
Everything in this directory is current; superseded material lives in `archive/` (reversible).

## The result, in one line
Behavioral telemetry encodes **expertise as a working style** (a robust ~0.81 CV signal; experts explore ~2.18× more) but **not achieved accuracy**
(a calibrated workforce converges); competence is legible **per-decision, not per-person** — and
per-task **risk is estimable ground-truth-free at AUC 0.76**, the deployable basis for an impact×risk
allocation of expert effort.

## Deck
- **`Calibrate_the_Humans_v15_presented.pptx`** — **the talk as presented** (17 slides; canonical record).
- **`Calibrate_the_Humans_v14.pptx`** — the last *reproducible, scripted* build (19 main + 5 backup);
  v15 is this plus final manual edits made live in PowerPoint. The Evidence slide leads with the
  model-free **~2.18× exploration** anchor + the **CV AUC ladder** (`fig_expertise_evidence.png`,
  learned tier CV-correct at 0.81, designed 0.98 an exploratory ceiling); the Risk slide shows two
  ground-truth-free signals (`fig_task_risk.png`); the per-decision slide frames ρ=−0.44 as a selection
  artifact. Build pipeline: `build_v14.py` → `convert_deck_png_to_jpeg.py` → `trim_tighten_v14.py` →
  `merge_s3_s4.py` → `merge_s8_s9.py`.

## Documents
- `nature_comms_draft.md` — paper draft (per-decision-not-per-person → GT-free risk → grammar → scale-up).
- `methodology_provenance.md` — methods & provenance: every claim with the analysis behind it.
- `transparency_failure_modes.md` — retractions, dead ends, robustness checks, honest negatives.
- `figure_descriptions.md` — per-figure legends synced to the analysis (incl. the long-form, acronym-free risk legend).
- `talk_script.md` — per-slide speaker script (beats + takeaways); the source for the deck's speaker notes.
- `PROVENANCE.md` — end-to-end trace: NeuVue/CAVE calls → mining scripts → evidence → figures → slides.
  (Deck change logs for the superseded transitions are in `archive/notes/`.)

## Evidence (`evidence/`) — traceable & reproducible
De-identified copies of the per-annotator data behind every figure (handles → opaque ids `E01..`/`S01..`;
no tokens, no name map), so the plots reproduce from this repo **with no credentials** — e.g.
`cd analysis && BERLIN_DATA=../evidence python make_risk_fig.py` (regenerates `fig_task_risk.png`,
AUC 0.59/0.76 bit-for-bit). Produced by `analysis/anonymize_evidence.py`; see `evidence/README.md`.

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
`cave_morphology.py` (grammar / morphology). **Annotator comparison (NeuVue):**
`compare_annotators.py` (behavioral style), `compare_points.py` (per-point label agreement), and
`make_point_agreement_figure.py` (→ `fig_point_agreement.png`). Network stages need NeuVue + CAVE
credentials (not committed); raw per-annotator CSVs carry handles and stay uncommitted, but
**de-identified copies live in `evidence/`** so every figure reproduces offline
(`anonymize_evidence.py`; `PROVENANCE.md`).

## Archive (`archive/`)
Superseded decks (the full `berlin_deck` v2–v11 line, incl. the human-edited `v5` base), superseded
build scripts (`build_deck.py`, `build_v5.py`), deck change logs, early plots (incl. the retracted
axon-GT figure), and early analysis notes — moved out so the main directory is all-current. Nothing
deleted; see `archive/README.md`.
