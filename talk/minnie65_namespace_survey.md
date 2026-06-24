# Minnie65 namespace survey + comprehensive behavior language

Full sweep of the minnie65 proofreading campaign on `queue.neuvue.io` (pulled
2026-06). Annotator handles and per-user profiles are in the delivered CSVs
(kept out of git); this doc holds the non-PII survey.

## Scope
- **38 minnie65 task namespaces** (only `pinkyTest`/`pinkyTest`-style and
  `nucleiZero` are non-minnie65). Discovered by unioning the namespaces of the
  most prolific annotators (no enumeration API exists).
- **104 distinct annotators** total; **49** have differstack behavior data.
- **124,604 differstack events / 2,633 sessions** mined across 30 namespaces
  with differstacks.
- Activity spans **2021-11 → 2025-05**, with the bulk of human proofreading in
  **2021–2022**.

## The proofreading "language" across the whole campaign
Behavior mix over all minnie65 differstacks (event-weighted):

| Behavior | % |
|---|---:|
| navigate (pan/zoom/rotate) | 62.3 |
| segment edit (merge/split/select) | 27.9 |
| other | 7.7 |
| annotate (point/tag/note) | 2.1 |

It varies sharply by task type (see `language_by_tasktype.png`): split/extension
namespaces are segment-edit-heavy; screening/validation namespaces are
navigation- and annotation-heavy. Experts (staff handles) skew more navigation /
less raw editing than students — a measurable behavioral signature.

## Real vs. test (from dates + users + volume)
`span_days` of sustained activity, distinct users, and task volume separate real
production from one-off pilots. Single-day namespaces with **many** users are
real coordinated sprints (e.g. `neuronScreeningV2`/`VR` — 34 users in a day), not
tests. Full table in `minnie65_namespace_master.csv`.

| read | count | examples |
|---|---:|---|
| **real** | 28 | multiSomaSplit (393d), fullyProofread (188d), automatedSplit (182d), multiSomaId (171d), dendExtensionLevel2/3, functionalCellClean, neuronScreeningV2/VR (single-day, 30+ users) |
| pilot/test | 5 | split (4 tasks), dendExtensionSelection (3), crimsonGocTraining, patProofread, axonOnDendriteV3_review |
| ambiguous | 4 | neuronScreening, agentsTraining, axonOnDendrite, dendExtensionLevel1 |

## Notes / caveats
- Per-namespace **event counts in the mining are capped samples** (≤700 tasks,
  ≤~2k events) — use them for *presence*, not true volume; `task_volume` (hit the
  700 cap = "large") and dates are the reliable scale signals.
- Differstack coverage is partial (some tasks/workflows emit none) — agent
  namespaces (`automatedSplit*`) are agent-generated and carry little human
  differstack.

## Toward scoring (expert surrogate)
Expert annotators are identifiable by the **staff handle** convention
(lastname+initials+digit, e.g. Pat Rivlin = `rivlipk1`; also `kitchlm1`,
`dxenes1`, `graywr1`). They can serve as a ground-truth surrogate. **Limitation
found:** only ~3 experts have rich differstack data, and they largely worked
*different* namespaces than the students — so same-task expert-vs-student
agreement is sparse. Cleanest path remains: join the **external promotion-study
scores** (`assignee → score/role`) to the per-user behavior+kinematic profiles.
