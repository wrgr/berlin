# Random-forest model: do behaviors predict correctness?

RF regression, behavioral features (per user × task type) → v18xx competency.
**68 cells, 36 users, 6 task types.** Features: pct_navigate/segment/annotate,
nav:seg ratio, seg→nav (verify-rhythm), seg→seg (batching), events/session,
tempo, total_events.

## Result — behavior does NOT robustly predict correctness
| Model | target | CV R² |
|---|---|---:|
| behavior only | relative competency (within task type) | **−0.37** |
| behavior only, within axonOnDendrite (n=20) | competency | −1.28 |
| behavior only, within multiSomaId (n=17) | competency | −1.25 |
| behavior + task-type one-hot | raw competency | +0.58 |

Every **within-type cross-validated R² is negative** — worse than predicting the
mean. The only predictive model (+0.58) leans on **task type** (some types are
easier: soma did-cut is high-ceiling, axon is hard) plus raw **activity**
(`total_events`), not nuanced behavior.

## Most important features (permutation importance)
`pct_annotate` (negative), `total_events`/activity, `seg_to_nav` (verify-rhythm).
Interpretable directions that *associate* with being correct (univariate-significant
in soma types, but NOT cross-validated): **less annotation**, **fewer actions
(efficiency)**, **re-inspecting after each edit** (seg→nav). These are suggestive,
not predictive at this N.

## Bottom line
Across every method — navigate:edit style, grammar transitions, 3D trajectory,
distance-to-Pat, and now a cross-validated RF — **how someone proofreads does not
tell you whether they are right.** Competency must be graded on outcomes (v18xx),
not inferred from behavior. Behavior remains valuable as the *descriptive* "language
of proofreading," and for distinguishing task types — just not as a skill proxy.

Caveats: N is small per type (7–20); a much larger labeled set could surface weak
but real behavioral signal that CV can't confirm here.
