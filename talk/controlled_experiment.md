# Controlling for task type + item: the within-experiment view

To remove the task-type (and item-difficulty) confound, restrict to a **controlled
experiment**: a task type where many annotators did the **same objects**.

## Which task types qualify
Only the axon decision tasks have redundancy; the soma types have **none** (each
object done once — they cannot serve as a controlled experiment):

| task type | annotators | objects by ≥3 | pairwise agreement |
|---|---:|---:|---:|
| **axonOnDendrite** | 14 | **733** | 81% |
| neuronScreeningV2 | 32 | 89 | 60% |
| axonOnDendriteV3 | 11 | 24 | 68% |
| axonOnAxon | 8 | 22 | 100% (no spread) |
| multiSomaId / neuronOtherBodies / singleSomaCleanUp | — | **0** | — |

## Result (axonOnDendrite, 733 objects ×≥3 annotators, 11 annotators)
**Controlled competency = agreement-with-consensus on identical objects** — and it
*discriminates*: 0.73 → 0.91 across annotators (median object consensus 0.75; 368
contested objects).

**Controlling surfaced behavioral signal that pooling hid** (Spearman, n=11):
- `pct_navigate` −0.58, `nav_seg_ratio` −0.58, `pct_segment` +0.57 (all p≈0.06).

→ more navigation associates with **lower** consensus-agreement; more editing with
**higher**.

## Interpretation (important)
Agreement-with-consensus is **conformity, not correctness**. The sign is the giveaway:
heavy *navigators* (examine more — the expert signature) **disagree** with the
consensus. That likely means careful examiners make nuanced **minority** calls, not
that they're wrong. So even here, behavior predicts being-**typical**, not being-
**right**.

## The core data limitation, stated cleanly
**No task type has both redundancy (controlled experiment) and a valid v18xx ground
truth.** Soma = valid truth, zero redundancy. Axon = redundant, invalid endpoint
proxy (conformity only). The fix is the same one flagged earlier: a **proper local
axon ground truth** (split-suggestion cut supervoxels, not path endpoints) graded on
the 733 shared objects — that would give a controlled experiment *with* real
correctness, the one design that could settle whether behavior predicts skill.
