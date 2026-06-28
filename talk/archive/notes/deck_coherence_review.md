# Deck coherence pass — v5 (your edit) → v6

Read end-to-end against `figure_descriptions.md`. The narrative arc is sound; the coherence
issues are localized. **No length was cut** — edits trade repetition for forward motion.

## Story arc (as it currently reads)
1–2  **Problem.** Trust/sufficiency is an *optimization problem under constraints* — you're testing a specific inference, against a finite, noisy expert budget.
3    **Route work to the right agent** (difficulty × impact): machine vs expert vs skip.
4    **The budget** is limited, noisy, heterogeneous — and consequence is *skewed* (the tail rewrites the answer).
5    **Prior work** circled sufficiency; what's missing is an operational way to spend effort *against an inference*.
6    **Correction vs validation** — two products of the same budget.
7    **Allocate by impact × risk, set by the inference** — the allocation structure.
8    To allocate, you must **price judgment = calibrate the annotators**.
9    The **real workforce** (8 experts + 36 novices).
10   **Agreement-gated promotion** — the calibration mechanism.
11   **Reframe:** promotion ad hoc → a *learning diagnostic* (skill is in the *how*; JIGSAWS).
12   **What behavior reveals** (the signals) — sets up the evidence.
13–17 **Evidence:** expertise legible + GT-free flag → mechanism → grammar → structure → convergence.
18–19 **Ecosystem** + students as a method.
20   **Acknowledgments.**

## Fixed in v6 (scripted in `analysis/build_v6.py`, reversible)
1. **Slides 11 & 12 both opened with "promotion is noisy/slow/ad hoc."** Two consecutive slides
   making the same point stalls the story. Now **slide 11 owns the reframe** and **slide 12
   advances**: retitled *"What behavior already reveals,"* and its opening bridges from 11
   (*"Skill lives in the how — so we can read it as the work happens, instead of waiting on
   outcomes"*) instead of repeating it. All evidence bullets kept.
2. **Two impact-grids (slides 3 & 7) read as near-duplicates** (both have impact on the y-axis).
   Slide 7's subtitle is now *"…— WHERE THE BUDGET GOES"* (vs slide 3's *"WHO HANDLES IT"*), and a
   speaker-note spells out the relationship: slide 3 routes each decision to human-or-machine by
   *difficulty*; slide 7 spends the human budget itself by *risk / disagreement*.
3. **Slide 17's caption read backwards.** *"Promoted ≈ expert < unpromoted accuracy"* implies the
   unpromoted are *more* accurate. The figure is distance-to-GT (lower = better), so it now reads
   *"Promoted ≈ expert < unpromoted — split distance-to-GT (lower = better),"* matching the axis and
   `figure_descriptions.md`.

## Applied in v7 (`analysis/build_v7.py`)
- **Restored a closing slide** — a bookend of the title slide (same layout/fonts), so the thesis
  lands at the end: *"Proofreading is an optimization problem. / The missing piece is the price of
  human judgment. / Calibrate the people, not just the microscope.  ·  Thank you."* (now 21 slides).
- **Slide 18 separator** — *"Science & Engineering"* now uses the same 3-space label gap as the
  other rows.
- **Slide 18 wording** — *"intersectional ecosystem" → "interconnected ecosystem."*
