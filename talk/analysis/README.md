# Analysis pipeline — proofreader behavior & competency

Working scripts behind the talk (`../berlin_deck_v3.pptx`), the methodology/provenance log
(`../methodology_provenance.md`), and the paper draft (`../nature_comms_draft.md`).
Handles are suppressed in all figures. A single cleaned end-to-end runner with full comments
is a planned follow-up (see methodology §10–13).

## Scripts
| script | what it does | key output |
|---|---|---|
| `mine_tiers.py` | naive → designed → **learned** (k-means motif dictionary) behavioral reps from the dense `multiSomaId` telemetry; recover expert-vs-proto-expert | `tiers_data.csv`; AUC 0.75 / 0.95 / 0.90 |
| `mine_fullyproofread.py` | per-annotator categorical label accuracy vs `patProofread` grader GT (exact (seg,label,pos) match) | `fullyproofread_accuracy.csv` |
| `mine_predictive_separability.py` | item 1: simple-behavior competence separability (LOO, FP/FN) + per-task GT-free uncertainty signal; dense-telemetry availability | `separability_{annotator,task}.csv` |
| `prospective_flagging.py` | deployment view: rank tasks by GT-free behavioral anomaly → error-catch vs fraction flagged | `fig_prospective_flagging.png` |
| `make_figures.py` | all talk figures (handles suppressed) | `fig_*.png` |
| `build_deck.py` | expands `berlin_deck_v2.pptx` → `berlin_deck_v3.pptx` (workforce / learning-engineering / evidence / outreach / acknowledgments / backup slides) | `../berlin_deck_v3.pptx` |

## Running
Each `mine_*` script refreshes a NeuVue token and queries `queue.neuvue.io` + CAVE
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
  predict competence (LOO AUC 0.14, reported as an honest negative).
- The surviving signal is per-decision and ground-truth-free (AUC 0.59). See methodology §13.
