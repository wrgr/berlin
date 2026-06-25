# Speaker script — "Calibrate the students, not just the microscope"

~9 minutes · 23 slides. For each slide: **the beats to hit** (don't read — these are landing points,
expand naturally) and **the takeaway** (the one line they should leave the slide with). Rough pacing
in the section headers.

---

## ACT I — The problem is an optimization (slides 1–8, ~3.5 min)

### 1 · Calibrate the students, not just the microscope
- One deceptively simple question: you have a volume and a limited number of proofreaders — *when do
  you stop, and how do you know the answer you get is one you can trust?*
- Reframe up front: this isn't a quality problem, it's an **optimization** problem. That framing is
  the whole talk.
- **Takeaway:** the right question isn't "is the connectome done?" — it's "have we **spent enough to
  trust** it?"

### 2 · The problem is a decision, not a dataset
- Engineering = problem-solving under constraints. Our problem: test a **specific inference**, not
  "reconstruct everything."
- The constraint: a finite supply of **noisy, expensive expert judgment** — experts disagree, so
  there's no free ground truth to check against.
- **Takeaway:** "done" is a property of the dataset; "trustworthy enough" is a decision about resources.

### 3 · Route the work to the right agent
- Two axes — how *hard* a decision is, how much it *matters*. Easy+low → let the machine do it
  (NEURD); easy+high → automate then verify; hard+high → the precious expert budget; hard+low → skip.
- The reframe: experts, students, and ML are **all agents in the loop**. It's not human-vs-machine.
- **Takeaway:** match each decision to the agent that should make it.

### 4 · The budget is finite, noisy, and unevenly demanding
- The resource we optimize is expert judgment: **limited** (person-years), **noisy** (experts
  disagree → ground truth is itself something you buy), **heterogeneous** (decisions differ wildly).
- And consequence is **skewed** — most edits barely move the inference; a few (frankenmerges,
  thin-axon mistakes) rewrite it, and we know which.
- **Takeaway:** "enough" can't be one global threshold when the decisions aren't interchangeable —
  the tail is where the inference lives.

### 5 · Prior work circled the sufficiency question
- Three honest lineages: defined "enough" *globally* (completeness proxies — incl. my own, which
  treated all connectivity as fungible — that's the part I got wrong); made each edit *cheaper*
  (focused proofreading, NEURD, RoboEM); used *analysis outcome* as the metric (RoboEM, our motif work).
- **Takeaway:** task-relativity is in the air — what's missing is an **operational way to spend
  limited expert effort against an inference**, while it's happening.

### 6 · Two things resources buy — correction vs. validation
- **Correction** changes the connectome (fix merges/splits). **Validation** tells you whether to
  trust it (CONFIRMS / MICrONS — assessment, no editing). Same scarce pool, different products.
- **Takeaway:** how you split the budget between *fixing* and *certifying* is part of the problem, not
  a detail.

### 7 · Allocate by impact × risk — set by the inference
- Spend the expert budget where **impact** (how much it moves the inference) and **risk** (how much
  annotators disagree) are both high. High-impact-but-agreed → validate, don't over-edit; low-impact
  → automate or skip.
- The lever that mediates everything: **the inference under test defines what counts as impact.**
  Change the question, the map changes. *(This was my PhD core idea.)*
- **Takeaway:** the hypothesis sets the map; then route effort — and the right annotator — to the
  top-right.

### 8 · You can't allocate resources you can't measure
- To allocate expert judgment you have to **price** it — characterize proofreaders: per-task,
  per-region competence, and how much they agree. This is *measuring the task*, not judging people.
- And it forces a precise definition of "reliable": not matching a gold standard (there isn't one) —
  **converged agreement on the decisions the inference depends on.**
- **Takeaway:** we calibrate the microscope obsessively; the uncharacterized term is **the person** —
  so calibrate the people too.

---

## ACT II — We calibrated a real workforce (slides 9–12, ~2 min)

### 9 · Who we calibrated: the proofreading workforce
- 8 part-time **experts** (Janelia EM training) + 36 **JHU undergraduate novices**, one curriculum,
  routed and recorded on NeuVue.
- **Takeaway:** "calibrate the annotators" isn't a metaphor — it's 44 people and a training pipeline.

### 10 · Learning engineering: agreement-gated promotion
- Students whose decisions agreed with experts were **promoted to a proto-expert tier** with
  write-access to expert tasks: train → practice → measure agreement → promote → widen scope.
- Same thesis as APL's learning-engineering work: assessment *as* a learning diagnostic.
- **Takeaway:** promotion-by-agreement works — but it's **selection on outcome**. Can we predict it
  *early* instead?

### 11 · Promotion: from ad hoc to a learning diagnostic
- Today promotion is the bottleneck — noisy, slow, judged by hand after the fact (expert time spent
  *watching*). The goal: turn it into a diagnostic with formative + summative signals.
- The analogy: **the language of proofreading ↔ the language of surgery (JIGSAWS)** — skill is
  assessable from *how* the work is done, not just the outcome.
- **Takeaway:** if skill lives in the *how*, we can read it as the work happens.

### 12 · What behavior already reveals
- Dense per-event telemetry — every navigate / edit / annotate, with 3-D camera motion. A label-free
  signal already works: a task slow *for that person* is more error-prone (no ground truth needed).
- Cohorts separate from behavior (pilot, n=16): **naive 0.75 → designed 0.95 → learned-grammar 0.90.**
- **Takeaway:** competence is **legible in behavior** — next five slides are the evidence.

---

## ACT III — The evidence (slides 13–18, ~2.5 min)

### 13 · The evidence — the language of proofreading
- Left: behavior separates experts from proto-experts (naive → designed → learned). Right: a
  **ground-truth-free** flag — re-review the most behaviorally-anomalous tasks, catch errors above chance.
- **Takeaway:** expertise is legible in *style*; risky decisions can be flagged with **no answer key**.

### 14 · Behavioral mechanism — 3-D exploration & tempo
- The mechanism behind the AUC: experts accumulate **~2× more camera rotation**, inspect from more
  viewpoints, do more, move faster.
- **Takeaway:** skill is a 3-D exploration *style* — it's in the *how*.

### 15 · The language of proofreading — action mix & grammar
- Which actions, in what order: action-mix and the navigate↔segment **transition grammar** differ by
  cohort — experts edit in sustained runs; proto-experts hop.
- **Takeaway:** there's a real **grammar** to proofreading, and it encodes expertise.

### 16 · What separates experts from proto-experts
- Three views — RandomForest importance, low-dimensional PCA, learned-motif "dialect" — all point to
  the same thing: **3-D exploration kinematics.**
- **Takeaway:** the signal is robust across methods, not an artifact of one.

### 17 · Competence is legible per-decision, not per-person
- Calibration **converges** outcomes — promoted ≈ expert — so achieved accuracy can't rank people.
  What survives is **per-decision**: slower-for-this-person tasks fail more, ground-truth-free.
- **Takeaway:** **don't rank people — flag risky decisions.**

### 18 · Risk is estimable, ground-truth-free
- Push the representation and the *risk* axis becomes deployable: from a task's structure alone we
  predict error-proneness at **AUC 0.76 on held-out cells** (the inflated 0.92 was cell-memorization;
  grouped CV is honest).
- **Takeaway:** you can **score risk before you spend** — exactly what "route to where risk is high"
  needs.

---

## ACT IV — Why it matters (slides 19–22, ~1 min)

### 19 · One node in an interconnected ecosystem
- This serves the HI-MC connectome (Lichtman UM1); the Master's program trains the workforce;
  computer vision supplies the automated agents; outreach makes calibrated student judgment a method.
- **Takeaway:** a trustworthy connectome, a calibrated workforce, **and people who stay in the field.**

### 20 · Outreach: students as a method, not just a mission
- Calibrated student judgment **IS** the method that built the connectome — MICrONS relied on this
  workforce; students we hired became co-authors (Daniel Xenes, now leading NeuVue, is the exemplar).
- **Takeaway:** the measurement that **prices the budget** is the same measurement that **develops the
  workforce** — talent development and mission acceleration are the same act.

### 21 · Acknowledgments & contributions
- NeuVue (Daniel Xenes & team), the graders (Pat Rivlin, Lindsey Kitchell), the 8 experts and 36
  novices, the workforce model, and the institutions. *(NIH BRAIN CONNECTS, UM1NS132250.)*
- **Takeaway:** a team effort — name the people.

### 22 · Close
- **Proofreading is an optimization problem. The missing piece is the price of human judgment.**
- **Takeaway / land here:** *Calibrate the people, not just the microscope.* Thank you.

### 23 · Backup — competence is per-decision, not per-person
- *Only if asked.* We pressure-tested it: per-**person** accuracy is **not** predictable (robust to
  target/transform/model — the 0.14 is within the null); per-**decision** risk **is** (0.76, p<0.001).
- **Takeaway:** the honest line — flag decisions, don't rank people.

---

## Leave the audience with
Three sentences, in order:
1. **The right question about a connectome isn't whether it's done — it's whether we've spent our
   limited, noisy expert budget well enough to trust the answer to a specific question.**
2. **That makes the uncharacterized term the *person*: price human judgment, and you can allocate it —
   per-decision, where impact and risk are highest.**
3. **And the same measurement that prices the budget develops the workforce — so "calibrate the
   people, not just the microscope" is both the method and the mission.**

*If you remember one line: **calibrate the people, not just the microscope.***
