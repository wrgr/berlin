# A Dictionary of Proofreading Behaviors

Derived from real NeuVue `differ_stack` history (the "language of proofreading").
Each differstack event is a diff-match-patch over the Neuroglancer state; we read
the diff lines to label what the proofreader did.

**Provenance.** Pulled live from `queue.neuvue.io` (2026-06). Corpus: **17,237
events across 526 sessions, 22 proofreaders, 4 human namespaces**
(`multiSomaSplit`, `somaSomaSplit`, `somaSomaReview`, `fullyProofread`).
Reproducible from the notebook (`classify_patch()` in
`posthoc_proofreader_differstack_analysis.ipynb`).

---

## 1. The behavior dictionary (what proofreaders do)

Event-weighted, whole corpus:

| Behavior | Events | % | What it is (in the NG state diff) |
|---|---:|---:|---|
| **navigate** (pan / zoom / rotate) | 7,992 | 46.4% | camera/position/orientation/scale change |
| **segment: remove** (split / deselect) | 3,763 | 21.8% | a uint64 segment ID removed from the selection |
| **segment: swap** (merge / split) | 2,882 | 16.7% | segment IDs both added *and* removed (relabel after an edit) |
| **other** | 1,156 | 6.7% | diff too small to attribute a field (see caveats) |
| **annotate** (point / tag / note) | 922 | 5.3% | point/line annotation, tag, or description added |
| **segment: add** (select / merge) | 481 | 2.8% | a uint64 segment ID added to the selection |
| **display** (opacity / visibility) | 40 | 0.2% | layer alpha / visibility / panel toggles |
| **segment: hide** | 1 | 0.0% | segment moved to hidden set |

Segment edits together = **41.3%**; navigation = **46.4%**. Proofreading is mostly
*looking*, punctuated by segment edits.

## 2. The captured fields (what Neuroglancer records)

The NG state keys that actually change, grouped into behaviors — this is the raw
"vocabulary" the differstack captures:

| NG state key(s) | Behavior |
|---|---|
| `position`, `voxelCoordinates` | navigate — pan |
| `projectionOrientation`, `crossSectionOrientation`, `perspectiveOrientation` | navigate — rotate |
| `projectionScale`, `crossSectionScale`, `zoomFactor`, `perspectiveZoom` | navigate — zoom |
| `segments` (+id / −id) | segment select / merge / split |
| `hiddenSegments` | hide segment |
| `point`, `pointA`, `pointB`, `type`, `id` | annotate — point / line geometry |
| `description` | annotate — note |
| `tagIds`, `tags` | annotate — tag |
| `parentId`, `annotations` | annotate — group / collection |
| `hasPath`, `pathFinder`, `pathObject`, `annotationPath`, `source`, `target` | trace / pathfinder tool |
| `selectedAlpha`, `objectAlpha`, `notSelectedAlpha`, `visible` | display — opacity / visibility |
| `colorSeed`, `crossSectionBackgroundColor` | display — recolor / background |
| `tab`, `tool`, `name`, `layout`, `showSlices`, `mode2d`, `mode3d` | UI — panel / tool / layer |

## 3. Task-type signatures (behavior mix by namespace)

Different task types speak different sub-languages:

| Namespace | navigate | seg remove | seg swap | annotate | other |
|---|---:|---:|---:|---:|---:|
| `fullyProofread` (validation) | 53.7% | 1.0% | 20.2% | **15.5%** | 8.2% |
| `multiSomaSplit` | 50.3% | 1.5% | **31.8%** | 2.3% | 12.0% |
| `somaSomaReview` | 37.1% | **30.2%** | 16.9% | 0.0% | 8.2% |
| `somaSomaSplit` (split) | 44.4% | **40.2%** | 10.1% | 0.0% | 3.3% |

Split/review work is dominated by **segment removal**; validation
(`fullyProofread`) is the only namespace with meaningful **annotation** (marking
spines/somas). The add-vs-remove asymmetry confirms it: in `somaSomaSplit`,
**8,470 segment IDs removed vs 1,823 added** (4.6×) — splitting, not merging.

## 4. Proofreader dialects (per-person behavior mix)

Distinct, measurable behavioral signatures (anonymized; names live in the
gitignored CSV). % of each proofreader's events:

| | navigate | seg remove | seg swap | annotate |
|---|---:|---:|---:|---:|
| P1 (navigator) | **85** | 0 | 3 | 9 |
| P2 (navigator) | **64** | 1 | 16 | 12 |
| P3 (splitter) | 31 | **40** | 17 | 0 |
| P4 (splitter) | 52 | **41** | 6 | 0 |
| P5 (splitter) | 53 | **37** | 5 | 0 |
| P6 (swapper) | 15 | 1 | **40** | 11 |
| P7 (swapper) | 30 | 3 | **41** | 19 |
| P8 (mixed/annotator) | 49 | 1 | 24 | **17** |

Three rough archetypes emerge — **navigators** (mostly look/validate),
**splitters** (segment removal), **swappers** (merge/split relabels) — plus
annotation-leaning proofreaders. This is exactly the raw material for "calibrate
the people": these signatures are computable from a proofreader's first sessions.

## 5. Honest caveats

- **Byte-level diffs.** `patch` is a diff-match-patch; the changed field name is
  often outside the diff window, so ~7% of events land in **other**. Numeric-only
  diffs are attributed to navigation.
- **Selection ≠ graph op.** A `segments` change conflates *selecting* a segment
  with an actual graph **merge/split**. `add`/`remove`/`swap` are proxies; a
  verified merge/split count needs reconstructing and diffing the segment sets
  (and cross-referencing the PCG edit log).
- **Partial coverage.** Differstacks exist for only a fraction of tasks (some
  workflows don't emit them); this corpus is a sample, not a census.
- **Two weightings.** Behavior % is event-weighted; the field table is
  occurrence-weighted (one big annotation patch contributes many `point` keys).
- **Automated namespaces excluded** (`automatedSplit*` are agent-generated, not
  human behavior).

## 6. Next steps to harden it

1. Reconstruct before/after NG state (apply the diff-match-patch chain from the
   task `ng_state`) and diff the `segments` sets → true merge vs split.
2. Cross-reference the PythonChunkedGraph / CAVE edit log to confirm graph ops.
3. Add bigram "grammar" per archetype and test whether early-session dialect
   predicts later agreement (the slide-10 pre-registered question).
