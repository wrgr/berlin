# Analysis pipeline — proofreader behavior & competency (minnie65 / MICrONS)

Working scripts behind the talk (current deck `../berlin_deck_v12.pptx`), the methodology/provenance
log (`../methodology_provenance.md`), the figure legends (`../figure_descriptions.md`), and the
paper draft (`../nature_comms_draft.md`). Handles are suppressed in all committed figures; the
per-annotator CSVs (which carry handles) are deliberately **not committed**. The canonical
sequencer is **`run_all.py`** — start there.

## Quick start
- `python run_all.py` — full pipeline, the 6 core stages in order (needs `.nv_tokens.json`, `.cave_token`).
- `python run_all.py --offline` — regenerate the core figures from cached CSVs (no creds, ~9 s).
- `python run_all.py --list` — list stages; `--stages 4-6` / `--stages 5,6` to select.

## Core pipeline (sequenced by `run_all.py`)
| # | stage | script | key output |
|---|---|---|---|
| 1 | tiers | `mine_tiers.py` | naive → designed → **learned** (k-means motif dictionary) reps from dense `multiSomaId` telemetry → `tiers_data.csv`; expertise AUC 0.75 / 0.95 / 0.90 |
| 2 | fullyproof | `mine_fullyproofread.py` | per-annotator categorical label accuracy vs grader GT (exact `(seg,label,pos)` match) → `fullyproofread_accuracy.csv` |
| 3 | separability | `mine_predictive_separability.py` | simple-behavior competence separability (LOO) + per-task GT-free uncertainty → `separability_{annotator,task}.csv` |
| 4 | prospective | `prospective_flagging.py` | GT-free error-flagging deployment curve → `fig_prospective_flagging.png` |
| 5 | figures | `make_figures.py` | core talk figures (handles suppressed) → `fig_*.png` |
| 6 | morefigs | `make_more_figures.py` | kinematics / grammar / RF importance / PCA / motif usage / 3-group / uncertainty |

## Deck build chain (run separately, not via `run_all.py`)
The current deck is built from the human-edited base `berlin_deck_v5.pptx` by an ordered,
reversible chain — each script reads the prior deck and writes the next (`BERLIN_TALK` overrides paths):
`build_v6.py → … → build_v11.py` (review pass) `→ build_v12.py` (point-agreement footnotes on
slides 8 & 17). `add_speaker_notes.py` completes the per-slide speaker notes on v11 (idempotent;
source `../talk_script.md`) before `build_v12.py` reads it. The base and all intermediate decks now live in `../archive/decks/`,
so re-running the chain means staging those decks into a working `talk/` dir (point `BERLIN_TALK`
at it). Superseded early builders (`build_deck.py` v2→v3, `build_v5.py` v4→v5) are archived in
`../archive/analysis/` as a historical record — the decks they produced are in `../archive/decks/`.

## Risk & grammar / morphology figures
- **Risk:** `enrich_fullyproofread.py` (per-task assignee/duration/accuracy → `enriched_task.csv`)
  + `explore_task_risk_prediction.py` → `fig_task_risk.png` (GT-free task risk, AUC 0.76 grouped CV).
- **Grammar / morphology:** `extract_streams.py` + `grammar_probe.py` (Markov action grammar) and
  `cave_morphology.py` → `fig_grammar_morphology.png`.

## Annotator comparison (NeuVue; two-handle, on demand)
Compare any two annotators (e.g. an expert vs the grader Pat / `rivlipk1`):
- `compare_annotators.py` — **behavioral style** on a shared task type (action-mix, navigate↔segment
  grammar, tempo, 3-D rotation) from differstacks.
- `compare_points.py` — **per-point label agreement** on shared segments (forced-choice point
  classification); `--users a,b,c` for cohort tables, `--confusion` for the matrix, `--raw` to skip
  label normalization.
- `make_point_agreement_figure.py` → `../fig_point_agreement.png` — agreement-with-grader by cohort
  (expert / promoted / unpromoted) + a representative confusion matrix.
These need NeuVue creds (`.nv_tokens.json` / env / cfg) + the `neuvue-client` checkout; the CAVE
token does **not** work for NeuVue. Per-annotator outputs (handles) cache to `live_out/` (not committed).

## Exploratory / honest-negative scripts (not in the core pipeline)
These produced the negative results recorded in `../transparency_failure_modes.md`:
`explore_accuracy_predictability.py` (the LOO AUC 0.14 honest negative),
`explore_accuracy_confound_and_target.py` (difficulty-confound control),
`explore_distance_regression.py` (continuous distance-from-GT — unpredictable),
`cave_difficulty.py` (structural difficulty vs cell error rate — inconclusive, stale roots).

## Running the network stages
Each `mine_*` / `enrich_*` script refreshes a NeuVue token and queries `queue.neuvue.io` + CAVE
(`minnie65_phase3_v1`). They expect, in the working directory:
- `.nv_tokens.json` (NeuVue refresh token) — **not committed**
- `.cave_token` (CAVE auth token) — **not committed**
- a `neuvue-client/` checkout on the path, and `live_out/` for outputs.

Dependencies: `numpy pandas scipy scikit-learn matplotlib diff-match-patch caveclient
cloud-volume python-pptx pypdf` (install with `pip install --ignore-installed packaging <pkg>`).

## Provenance & honesty
- The "designed" tier is hand-built; only RandomForest importance is learned. The motif
  dictionary in `mine_tiers.py` is the genuine unsupervised representation.
- Accuracy ceiling-clusters across two task types; annotator-level simple behavior does **not**
  predict competence (LOO AUC 0.14, reported as an honest negative within the 0.45±0.20 null).
- The surviving signal is per-decision and ground-truth-free (uncertainty AUC 0.59; task-risk
  AUC 0.76 grouped CV). See `../methodology_provenance.md` §10–14.
