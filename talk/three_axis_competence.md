# Three measurable axes of proofreader competence

End-to-end, the neuvue + CAVE data supports **three independent ways to score an
annotator**, spanning behavior → judgment → outcome:

| Axis | What it measures | Source | Discrimination |
|---|---|---|---|
| **Behavioral style** | *how* they work (navigate:edit signature vs expert) | differstacks | distinguishes expert, cheap/scalable |
| **Decision agreement** | *what* they conclude (split/merge call vs expert `rivlipk1`) | `metadata.decision` on co-decided objects | wide (0.54–0.96) |
| **Outcome durability** | whether their edits *survive* (cut supervoxels still in different roots in latest v1817) | `multiSomaId.operation_ids` → `removed_edges` → `get_roots(latest)` | high-ceiling (0.85–1.00, overall 93.7% hold) |

## Key finding: the axes diverge
For the 5 annotators measured on all three, the scores do **not** track each other
(corr: style↔decision −0.04, style↔durability −0.47, decision↔durability −0.70).
Concretely:
- the annotator with the **least expert-like style** had the **highest** decision
  agreement (0.96);
- the annotator with the **lowest** decision agreement (0.55) had the **highest**
  split durability (1.00).

So "competence" is **multi-dimensional and task-specific** — a single proxy
(especially behavioral kinematics) misleads. (n = 5 on all three axes; the
correlations are illustrative, not statistically significant. The three axes also
draw on different task types, so divergence partly reflects task-specific skill.)

## Implication for scoring
- **Outcome durability vs the latest connectome** is the most objective ground
  truth (your "agree with the later data") and is now computable at scale via the
  stored `operation_ids`/`removed_edges` — no cloudvolume needed. Caveat: high
  ceiling (most splits hold; a wrong split survives if unreviewed).
- **Decision agreement** discriminates more but needs an expert reference.
- **Behavioral style** is cheap and scalable but measures manner, not merit — use
  only as a proxy after calibrating against durability/decisions.

Recommended primary metric: **split durability vs latest data**, back-stopped by
decision agreement on the harder, higher-disagreement task types
(`axonOnDendriteV3`).
