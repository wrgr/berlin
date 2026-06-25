# Pat-anchored competency — the methodologically valid version

## Why we needed it (the v18xx GT failed the Pat gate)
Sanity check: a correct competency must score the expert (Pat) ≈ 1. The v18xx axon
GT does NOT — Pat scores **0.57** on axonOnDendriteV3. Diagnosis: 95% of objects read
"separated" in v18xx (3 yrs + many edits downstream), so the truth almost always says
"error exists" and Pat's correct `noError` calls are marked wrong. The downstream
confound makes v18xx invalid for grading individual decisions. **The earlier
"behavior predicts conformity not correctness" conclusion used this broken correctness
side and is retracted.**

## The fix: anchor on Pat directly (shared objects)
`axonOnDendriteV3` has a clean controlled experiment: **Pat + 9 students all decided
the same 20 objects.** Competency = **agreement-with-Pat** (family ERR vs NOERR).
Passes Pat≈1 by construction; immune to v18xx.

Result — it discriminates (0.42–0.95): erika 0.42, christopher 0.55, michael 0.74,
chris/dxenes1/claire 0.79, gary 0.84, phillips 0.89, **natalie 0.95**.

## Behavior still does not predict it (but underpowered)
- **Behaving like Pat ≠ deciding like Pat**: behavioral-distance-to-Pat vs
  agreement-with-Pat ρ=−0.19 (p=0.63, n=9). `natalie` decides most like Pat yet is
  behaviorally among the farthest from her.
- **No single behavior significant** (n=9): best `u_O` +0.49 (p=0.18), batching
  `bg_SS` +0.32 (the conformity echo).

## Status & the path the user wants
We now have a **valid, discriminating competency target** (agreement-with-Pat) that
the hand-crafted features fail to predict — the right setup for a **learned, invariant,
surgery-style representation** (motif dictionaries, time-warp-invariant kinematics,
held-out validation). BUT the hard limit is **N**: Pat decided only ~20 objects per
type, capping this anchor at ~9–16 students — likely too few to *learn* a
high-dimensional representation without overfitting. Scaling requires more
expert-anchored data (more Pat/expert decisions on shared objects), or a second
expert to widen the anchor.

Caveats: n=9; agreement-with-one-expert is itself noisy; ERR base rate 17/20 so
err-recall dominates raw agreement (noerr-recall on 3 objects is the discriminator).
