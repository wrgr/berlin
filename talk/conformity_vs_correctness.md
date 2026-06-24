# Resolving "behavior shows ~0 correlation with competency"

The flat correlation was suspicious — and interrogating it gives the central result.

## It was never really zero — it was the wrong target (and bad labels)
The controlled axonOnDendrite experiment (shared objects, valid path-vs-dendrite GT,
n=11 annotators) shows the **same behavioral features predict CONFORMITY strongly but
CORRECTNESS not at all**:

| feature | ρ vs CONFORMITY (agree w/ group) | ρ vs CORRECTNESS (v18xx truth) |
|---|---:|---:|
| pct_navigate | −0.58 | −0.13 |
| pct_segment | +0.57 | +0.01 |
| nav_seg_ratio | −0.58 | 0.00 |
| seg_to_seg | +0.51 | −0.08 |
| pct_annotate | −0.15 | **−0.50** |

Earlier "0 correlation" runs were against the **axon endpoint GT, which we proved is
≈chance** — i.e. behavior was being correlated against noise. Against a target that
varies (conformity), behavior correlates ~0.58. Behavior is not inert.

## But conformity ≠ correctness
- Inter-annotator **conformity** ranges 0.73–0.91; **balanced accuracy vs v18xx truth**
  ranges 0.42–0.71 (0.5 = chance). Most annotators are **near chance** on the hard
  (non-error) cases — they ride the 70% "say-yes" base rate.
- `corr(conformity, correctness) = +0.31` — weak. **Agreement is not validity.**
- The editing/navigation features that predict *agreeing with the group* drop to ~0
  against *being right*. So **behavior predicts being typical, not being correct.**

Interpretation: annotators converge on a shared style (plausibly common training under
the expert) and largely agree with each other, yet are collectively near chance versus
the final connectome on the hard cases.

## The one real behavioral signal of skill
`pct_annotate` is the exception: **fewer annotation marks → higher correctness**
(−0.50 here; −0.55\* multiSomaId; −0.89\* neuronOtherBodies). The only behavior that
tracks correctness across task types — more marking likely signals
confusion/uncertainty.

## Bottom line (with caveats)
With valid labels + a controlled design + richer order-tolerant features, **behavior
robustly predicts conformity but not correctness** (only `pct_annotate` weakly does).
You cannot read proofreading *skill* from behavior or from inter-annotator agreement —
only from outcome-based ground truth. Caveats: n=11; balanced accuracy is noisy (6–19
negatives/annotator); "near chance" is tentative and GT-dependent. See
`conformity_vs_correctness.png`.
