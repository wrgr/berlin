# Provenance — from NeuVue/CAVE calls to every plot

The full chain behind each figure, so the evidence is **traceable end to end**:

```
NeuVue (queue.neuvue.io)        mining scripts          live_out/*.csv         anonymize_evidence.py      evidence/*.csv          figure scripts        fig_*.png         deck slide
 + CAVE (minnie65_phase3_v1)  ───────────────────►  (handles, gitignored)  ──────────────────────►  (de-identified, committed)  ─────────────────►  (committed)  ──────►  (committed)
```

- **Credentials** (`.nv_tokens.json` NeuVue refresh token, `.cave_token`) live only in the run
  directory and are **never committed**. The handle→real-name map is never committed.
- The **network** stages (mining) need those credentials; the **offline** stages (figures, stats)
  run from the committed `evidence/` with no credentials — see `evidence/README.md`.

## Per-figure trace

| Figure (deck) | NeuVue namespace / CAVE source | Mining script → live CSV | Committed evidence | Figure / stats script |
|---|---|---|---|---|
| **`fig_expertise_evidence`** (Evidence: ladder + 2.18×) | NeuVue `multiSomaId` differ-stacks — per-event action labels + 3-D camera rotation | `mine_tiers.py` → `tiers_data.csv`; windows → `motif_windows.npz` | `tiers_data.csv`, `motif_windows.npz` | `make_expertise_evidence_fig.py` |
| **`fig_task_risk`** (Risk: two GT-free signals) | NeuVue `fullyProofread` tasks + `patProofread` grader GT; per-point anatomical category (point→supervoxel via CAVE/cloudvolume) | `enrich_fullyproofread.py` → `enriched_task.csv` | `enriched_task.csv` | `make_risk_fig.py` (numbers: `explore_task_risk_prediction.py`) |
| **`fig_prospective_flagging`** (per-decision flag) | NeuVue `fullyProofread` + grader GT | `mine_predictive_separability.py` → `separability_{annotator,task}.csv` | `separability_annotator.csv`, `separability_task.csv` | `prospective_flagging.py` |
| **`fig_accuracy_threegroup` / `fig_uncertainty_calibration` / `fig_accuracy_unpredictable`** (convergence; honest negative) | NeuVue `fullyProofread` (label accuracy) + `multiSomaSplit` (distance-to-GT) | `mine_fullyproofread.py` → `fullyproofread_accuracy.csv`; `mine_*` → `multisomasplit_competency.csv` | `fullyproofread_accuracy.csv`, `multisomasplit_competency.csv`, `separability_annotator.csv` | `make_more_figures.py`, `explore_accuracy_predictability.py` |
| **`fig_kinematics` / `fig_action_grammar` / `fig_rf_importance` / `fig_feature_pca` / `fig_motif_usage`** (mechanism, backup) | NeuVue `multiSomaId` streams | `mine_tiers.py` (+ `extract_streams.py`, `grammar_probe.py`) | `tiers_data.csv`, `grammar_features.csv`, `rf_importance.csv` | `make_more_figures.py` |
| **`fig_fishing_audit`** (how much of the AUC is real) | — (offline, from tiers + windows) | — | `tiers_data.csv`, `motif_windows.npz` | `fishing_audit.py`, `motif_cv.py` |
| ρ=−0.44 selection-artifact check | — (offline) | — | `tiers_data.csv`, `fullyproofread_accuracy.csv`, `enriched_task.csv`, `multisomasplit_competency.csv` | `rho_robustness.py` |

## CAVE morphology (methods only — not a result)
Caliber (Level-2 `max_dt_nm`) and branch counts (`level2_chunk_graph`) on `minnie65_phase3_v1` were
probed as task-difficulty proxies (`cave_morphology.py`, `cave_difficulty.py`); inconclusive (stale
roots, null vs error). Documented in `transparency_failure_modes.md`; no committed figure depends on it.

## Reproduce everything offline
`evidence/README.md` lists the one-line commands (`BERLIN_DATA=../evidence python <script>`). The
network re-pull is `analysis/run_all.py` (stages 1–3) with credentials in the run directory.
