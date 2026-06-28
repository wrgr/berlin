# Short talk — the 7-slide story ("Calibrate the agents")

A condensation of the 23-slide deck (`berlin_deck_v11.pptx`) down to the main point and the big
idea, for a ~4-minute version. Built by `analysis/build_short_deck.py` → `berlin_deck_short.pptx`
(scripted/reversible; v11 is never modified). Speaker notes are embedded in the deck.

## The one idea this version emphasizes
**An *agent* is agnostic to human or machine.** Experts, students, and ML are interchangeable
agents in the loop. The talk is not human-vs-machine — it's about *routing each decision to the
agent that should make it*, and *pricing every agent's judgment* so you can allocate it. That
through-line runs explicitly through slides 3, 5, and 7.

## The arc (problem → big idea → method → evidence → close)

| # | slide (v11 source) | the beat | takeaway |
|---|---|---|---|
| 1 | Title (S1) | You have a volume and finite proofreaders — when do you stop, and can you trust the answer? Define **agent** = anything that makes a decision (expert / student / ML). | Calibrate the *agents*, not just the microscope. |
| 2 | Problem is a decision (S2) | It's engineering under a hard constraint: judgment is finite, expensive, ambiguous (agents disagree → no free ground truth). | "Done" is about the dataset; **"trustworthy enough" is an optimization**. |
| 3 | Route to the right agent (S3) | **The big idea.** Two axes — how hard, how much it matters. Easy+low → machine; hard+high → the precious budget. Experts, students, and ML are all agents in the loop. | It's not human-vs-machine — **match each decision to the right agent**. |
| 4 | Impact × risk (S7) | Allocate over *decisions*: spend where impact (moves the inference) and risk (agents disagree) are both high. The inference under test sets the impact axis. | Route effort to the top-right; the hypothesis sets the map. |
| 5 | Price the agents (S8) | You can't allocate what you can't measure — characterize every agent's per-task competence and agreement (you price an algorithm the same way you price a person). | Reliability = **converged agreement**, not a gold standard. |
| 6 | The evidence (S13) | Behavior alone separates expert from proto-expert agents (AUC ≈ 0.90); and a **ground-truth-free** anomaly score flags risky tasks above chance. | Competence is legible in behavior — **flag risky decisions, don't rank agents**. |
| 7 | Close (S22) | Proofreading is an optimization problem; the missing piece is the price of an agent's judgment — human or machine. | **Calibrate the agents — human or machine — not just the microscope.** |

## Rebuild
```
python analysis/build_short_deck.py        # reads berlin_deck_v11.pptx, writes berlin_deck_short.pptx
```
Editing the slide selection, the agent-agnostic text edits, or the notes is all in that one script.
