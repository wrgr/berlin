# Deck v4 → v5 — changes & copy-edit pass

Base: your redone **berlin_deck_v4.pptx** (23 slides, 16:9). Output: **berlin_deck_v5.pptx**.
Build is scripted (`analysis/build_v5.py`) so every edit is reversible.

## Applied in v5

**1. Inference added as the mediator of impact (slide 8)** — your PhD core idea: the inference
defines what counts as impact.
- Title: "Allocate by impact × risk" → **"Allocate by impact × risk — set by the inference"**
- Y-axis: "impact ↑" → **"impact on the inference ↑"**
- New banner above the grid: *"▲ The inference under test sets the impact axis — the hypothesis
  mediates what's worth the budget."*
- Takeaway: appended *"Impact is defined by the inference you're testing."*

**2. "Language of proofreading" bound to the evidence (slide 15)**
- Title: "The evidence (handles suppressed)" → **"The evidence — the language of proofreading
  (handles suppressed)"**
- The phrase now lands four times as a through-line: **slide 13** (JIGSAWS/surgery analogy),
  **slide 14** (section header), **slide 15** (evidence), **slide 17** (title). Well covered — say
  the word and it's reinforced everywhere the behavior shows up.

**3. Header order fix (slide 7)** — header was "VALIDATION VS. CORRECTION" but the body reads
Correction then Validation → header now **"CORRECTION VS. VALIDATION"** (matches reading order).

## Copy-edit pass — suggested (not yet applied; say the word and I'll roll a v6)

The copy is already tight; these are the genuine clarity/marketing wins:

- **Slide 9 — finish the placeholders.** "Given **XX** expert-hours and **YY** dollars … to **ZZ**"
  reads unfinished in an otherwise polished deck. Either fill the live numbers, or template it:
  *"Given a fixed expert-hour and dollar budget, we can take this connectome to a stated confidence —
  enough (or not) to validate or reject the hypothesis."*
- **Slide 14 — thin the density.** Seven bullets is the heaviest slide. Suggested cut to five, with
  the AUC detail moved to notes:
  1. Promoting a proofreader today is noisy, hand-judged, after the fact.
  2. Competence is legible in behavior — dense per-event telemetry, 3-D camera motion.
  3. Label-free: a task slow *for that person* is more error-prone (AUC 0.59, p<0.001) — no GT needed.
  4. Cohorts separate from behavior (pilot, n=16): naive 0.75 → hand-tuned 0.95 → learned 0.90.
  5. Mechanism: experts inspect from ~2× more viewpoints — skill is in *how*, not *what*.
- **Slide 20 — "intersectional" → "interconnected."** "One node in an intersectional ecosystem" can
  be misread; *"interconnected"* says sits-at-the-intersection without the connotation.
- **Slides 3 & 8 — two 2×2s.** Slide 3 is difficulty×impact (who handles it); slide 8 is
  impact×risk (where to spend). Consider a half-line on slide 8 ("difficulty routed *who*; now route
  *budget*") so the second grid reads as a deliberate escalation, not a repeat.
- **Consistency.** Figures and slides both use **proto-expert** for promoted students — good; keep
  "student" only for the untrained novice cohort.

## Companion deliverable
`figure_descriptions.md` — a synced description of every figure (exact numbers/methods from the
CSVs), mapped to slides 15–19, usable as captions, speaker notes, or a figure legend appendix.
