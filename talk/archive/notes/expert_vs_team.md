# Expert vs. core team vs. students — behavioral signature

Tiering (per user direction): **expert = `rivlipk1`** (ground truth);
**core team = `kitchlm1`, `dxenes1`** (skilled, not benchmark); **students = the
rest**. Users with **<100 differstack events excluded** (49 → 43 users).

All **other staff-handle annotators are excluded** from the student pool (the
`lastname+initials+digit` convention: `bishoca1, brodsrf1, …, wiltml1`, 17 total).
In practice the ≥100-event filter already removed all of them — they carried
little or no differstack data — so the 40-user student tier is genuine
proofreaders, uncontaminated by staff.

## Headline: competence = inspection-per-edit, not speed
Event-weighted behavior mix (≥100-event users):

| Tier | navigate | segment(edit) | annotate | navigate:edit |
|---|---:|---:|---:|---:|
| Expert (rivlipk1) | 69.8 | 16.0 | 1.2 | **4.4** |
| Core (kitch/dxenes) | 57.4 | 33.2 | 2.9 | 1.7 |
| Students (40) | 62.5 | 28.0 | 2.1 | 2.2 |

The expert **navigates far more per edit** — deliberate, surgical. Core team are
the heaviest *editors* (workhorses). The pattern **survives namespace control**:
within `neuronOtherBodies`+`axonOnDendriteV3` (all three tiers present), expert
navigate:edit ≈ 3.4 vs core 1.1, students 2.3.

**Tempo is flat** across tiers (median inter-event ≈ 1.3–1.7 s), so the separator
is the *behavior mix*, not raw pace. See `tier_comparison.png`.

## Caveats
- Expert is **n = 1** (`rivlipk1`), core **n = 2** — this is one expert's
  signature, not a population statistic. Treat as an interpretable axis, not a
  significance test.
- Fair-comparison overlap is limited: the expert and students co-occur with
  ≥30 events in only 4 namespaces (`agentsExpert`, `axonOnAxon`,
  `axonOnDendriteV3`, `neuronOtherBodies`).
