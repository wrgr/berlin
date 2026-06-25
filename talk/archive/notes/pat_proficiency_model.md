# "Proficiency = behave like Pat" — built, and it does NOT validate

Per user direction, modeled proficiency as **behavioral distance to Pat
(`rivlipk1`), per task type**: each (user, task-type) signature = behavior-mix +
grammar transitions + tempo, standardized within the task type; proficiency =
Euclidean distance to Pat's signature in that type.

## Result
`gary` is consistently the most Pat-like, `natalie` the least, across the three
task types where Pat has enough differstack data (`axonOnAxon`, `axonOnDendriteV3`,
`neuronOtherBodies`). Pat is **missing** in `multiSomaId`/`singleSomaCleanUp`/
`axonOnDendrite` (too few differstack-bearing tasks).

## Validation — it fails
Does behaving-like-Pat predict the **objective v18xx competency**? Spearman, per type:
- neuronOtherBodies ρ=+0.18 (p=0.70)
- axonOnAxon ρ=−0.29 (p=0.53)
- axonOnDendriteV3 ρ=+0.33 (p=0.42)

**All non-significant; the sign flips across task types.** `natalie` is behaviorally
*farthest* from Pat yet among the more accurate annotators.

## Conclusion
Behavioral similarity to the expert is **style, not proficiency** — confirmed now at
the per-task-type level, not just pooled. Mimicking Pat's grammar/tempo does not make
an annotator correct. **The objective v18xx competency is the proficiency signal;**
behavior describes manner, not correctness.

Caveats: n=7–8 per type; Pat covers only 3 types; signature excludes the 3D
trajectory features (which themselves underperformed the trivial activity count).

## Implication for next steps
- Don't use Pat-likeness (or any holistic behavioral mimicry) as proficiency.
- Either treat the **objective v18xx competency as proficiency directly**, or pull
  the **real user-group labels from the app** and model those.
- If a behavioral predictor is still wanted, do **feature-level** importance (which
  specific actions predict competency) rather than distance-to-exemplar — the one
  hint so far was a trivial one (more navigation ↔ better decisions).
