# Evidence — de-identified data behind the talk figures

De-identified copies of the per-annotator data that produce the talk's figures, committed so every
plot is **traceable and reproducible from this repo** without exposing annotator handles.

- Annotator handles → **opaque ids**, consistent across files: experts `E01–E08`, proto-experts /
  students `S01–S30`, other handles `U…`.
- `seg_id` are **public MICrONS segment ids** (not personal); kept so grouped-by-cell CV reproduces.
- **No** tokens, **no** handle→real-name map, **no** raw handles. Produced by
  `../analysis/anonymize_evidence.py` from the (gitignored, credentialed) live mining output.

## Reproduce the figures from this evidence — no credentials needed
```
cd ../analysis
BERLIN_DATA=../evidence python make_risk_fig.py                # fig_task_risk.png        (AUC 0.59 / 0.76)
BERLIN_DATA=../evidence python make_expertise_evidence_fig.py  # fig_expertise_evidence.png (naive/learned 0.81, designed 0.98)
BERLIN_DATA=../evidence python fishing_audit.py                # fig_fishing_audit.png
BERLIN_DATA=../evidence python rho_robustness.py               # rho=-0.44 = selection artifact
BERLIN_DATA=../evidence python explore_task_risk_prediction.py # risk 0.76 grouped, p<0.001
```

## Files
| file | rows | what |
|---|---|---|
| `tiers_data.csv` | 16 | calibrated annotators × 41 behavioral features (expertise tiers, motifs) |
| `enriched_task.csv` | 772 | per fullyProofread task: behavior + point-category mix + error vs grader |
| `fullyproofread_accuracy.csv` | 37 | per-annotator categorical-label accuracy vs grader |
| `separability_annotator.csv` | 36 | per-annotator duration/throughput summaries + accuracy |
| `separability_task.csv` | 772 | per-task duration + error (per-decision flagging) |
| `multisomasplit_competency.csv` | 35 | per-annotator split distance-to-GT (variance-rich target) |
| `grammar_features.csv` | 43 | per-annotator n-gram grammar distance by tier |
| `rf_importance.csv` | 9 | RandomForest / permutation feature importances (no handles) |
| `motif_windows.npz` | 16 | windowed gesture features per annotator (learned-motif CV; keys de-identified) |

The upstream NeuVue/CAVE → CSV chain (which needs credentials) is documented in `../PROVENANCE.md`.
