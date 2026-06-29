# Speaker script — "Calibrate the Humans, Not Just the Microscope"

~9 minutes · 20 slides (+4 backup). Aligned to `Calibrate_the_Humans_v14.pptx`. For each slide:
**beats** (landing points — expand naturally, don't read) and **takeaway** (the one line to leave on).

---

## ACT I — The problem is an optimization (slides 1–7, ~3 min)

### 1 · Calibrate the Humans, Not Just the Microscope
- One deceptively simple question: a finite volume, a finite number of proofreaders — *when do you
  stop, and how do you know the answer is one you can trust?*
- Reframe up front: not a quality problem, an **optimization** problem. That framing is the talk.
- **Takeaway:** the question isn't "is the connectome done?" — it's "have we **spent enough to trust** it?"

### 2 · How do we allocate proofreading resources?
- The problem: test a **specific, bounded inference** — not proofread every pixel. Who makes which decision?
- Engineering = problem-solving under real-world limits; optimize time, proofreader count, and quality.
- **Takeaway:** "done" is a property of the dataset; "trustworthy enough" is a decision about resources.

### 3 · Proofreaders as agents — route to the right agent
- Many agents observe the map and propose revisions — from naive students catching obvious errors, to
  experts handling the hard calls, to ML — each with distinct capability, cost, and scope.
- Two axes — how *hard* a decision is, how much it *matters* (impact × risk): easy+low → the machine
  (NEURD); easy+high → automate then verify; hard+high → the precious expert budget; hard+low → skip.
- **Takeaway:** experts, students, and ML are all agents in the loop — match each decision to the one
  that should make it.

### 4 · Prior work circled sufficiency — but didn't operationalize it
- Three lineages: defined "enough" *globally* (completeness proxies — incl. my own, which treated all
  connectivity as fungible — the part I got wrong); made each edit *cheaper* (Focused Proofreading, NEURD,
  RoboEM); used *analysis outcome* as the metric (RoboEM, our motif work).
- **Takeaway:** task-relativity is in the air — what's missing is an **operational way to spend limited
  expert effort against an inference**, while it's happening.

### 5 · But… aren't humans unnecessary? The data are too big!
- Humans are messy (they tire, vary, bring hard-to-formalize judgment); machines have their own biases and
  heavy resource needs. No single agent wins everywhere.
- **Takeaway:** the framework is agnostic to human vs machine — what matters is matching capability to decision.

### 6 · Two things resources buy — correction vs. validation
- **Correction** changes the connectome (fix merges/splits). **Validation** certifies whether to trust it
  (CONFIRMS / MICrONS — assess, don't edit). Same scarce pool, different products.
- **Takeaway:** how you split the budget between *fixing* and *certifying* is part of the problem.

### 7 · You can't allocate resources you can't measure
- To allocate expert judgment you must **price** it — per-task, per-region competence, and agreement. This
  is *measuring the task*, not judging people.
- Forces a precise definition of "reliable": not a gold standard (there isn't one) — **converged agreement
  on the decisions the inference depends on.**
- **Takeaway:** we calibrate the microscope obsessively; the uncharacterized term is **the person**.

---

## ACT II — Can we read it? (slides 8–11, ~1.5 min)

### 8 · Can we learn a language of proofreading?
- A retrospective target of opportunity (MICrONS), with a planned prospective validation: read performance
  and capability from *how* the work is done, to route limited expert attention.
- **Takeaway:** if skill lives in the *how*, we can read it as the work happens.

### 9 · Inspiration: JIGSAWS (language of surgery)
- Surgery is describable as gestures and transitions — a structured "language." Experts show more efficient,
  consistent patterns and smoother motion. **The language of proofreading ↔ the language of surgery.**
- **Takeaway:** skill is assessable from the *grammar* of the work, not just the outcome.

### 10 · Promotion: from ad hoc to a learning diagnostic
- Today promotion is hand-judged after the fact (expert time spent watching). Goal: a diagnostic with
  formative signals (in training) and summative signals (at promotion).
- **Takeaway:** turn promotion into a measurement, not a bottleneck.

### 11 · What behavior already reveals
- Three things: calibration **converges** outcomes (it works); behavior **separates** experts from
  proto-experts (skill leaves a trace); competence reads **per-decision** (flag risky decisions, don't rank people).
- **Takeaway:** competence is **legible in behavior** — the next slides are the evidence.

---

## ACT III — The evidence (slides 12–15, ~2 min)

### 12 · The evidence — the language of proofreading
- Left: the rawest signal needs no model — **experts explore ~2.18× more**. The AUC ladder is honest and
  **cross-validated**: naive 4-count features and the learned 10-motif dictionary both separate at **0.81**;
  the 28-feature designed bank hits **0.98** but is engineered post-hoc on n=16 — an **exploratory ceiling**.
  CV rules out trivial fit (28 noise features → 0.45). Right: a **ground-truth-free** flag — re-review the
  most behaviorally-anomalous tasks and catch errors above chance.
- **Takeaway:** a real, broad **~0.80** expertise signal anchored in 3-D exploration; risky decisions flagged
  with **no answer key**.

### 13 · The language of proofreading — exploration & grammar
- The mechanism: experts accumulate ~2× more camera rotation, inspect from more viewpoints, work faster;
  the action-mix and the **navigate↔segment transition grammar** differ by cohort — experts edit in
  sustained runs, proto-experts hop. *(Grammar figure in backup.)*
- **Takeaway:** there's a real **grammar** to proofreading, and it encodes expertise.

### 14 · Competence is legible per-decision, not per-person
- Calibration **converges** outcomes — promoted ≈ expert (~99% point-agreement) — so achieved accuracy can't
  rank people. What survives is **per-decision**: slower-for-this-person tasks fail more, ground-truth-free.
- **Honest caveat (say it):** the calibrated cohort (n=16, no true novices) is why the rotation↔accuracy dip
  (ρ=−0.44) appears — it's a **selection artifact** (proto-experts were promoted *for* grader-agreement, the
  very metric), **not** "style ≠ proficiency."
- **Takeaway:** **don't rank people — flag risky decisions.**

### 15 · Risk is estimable, ground-truth-free
- From a task's structure alone — no labels — predict error-proneness at **AUC 0.76 on held-out cells**
  (honest grouped CV; the inflated 0.92 was cell-memorization; 1000-perm null p<0.001).
- **Takeaway:** you can **score risk before you spend** — exactly what "route to where risk is high" needs.

---

## ACT IV — The workforce & why it matters (slides 16–20, ~2 min)

### 16 · Who we calibrated: the workforce at APL
- 8 part-time **experts** (Janelia EM training) + 36 **JHU undergraduate novices**, one curriculum, routed
  and recorded on NeuVue.
- **Takeaway:** "calibrate the annotators" isn't a metaphor — it's 44 people and a training pipeline.

### 17 · Learning engineering: agreement-gated promotion
- Students whose decisions agreed with experts were **promoted to a proto-expert tier** with write-access:
  train → practice → measure agreement → promote.
- **Takeaway:** promotion-by-agreement works — but it's **selection on outcome**. Can we predict it *early*?
  *(That's the pre-registered prospective test.)*

### 18 · Where this lives — students as the method
- This serves the HI-MC connectome (Lichtman UM1); the Master's program trains the workforce; CV supplies the
  automated agents. And the payoff: **MICrONS relied on this workforce**; students became co-authors —
  **Daniel Xenes**, now leading NeuVue, is the exemplar.
- **Takeaway:** the measurement that **prices the budget** is the same one that **develops the workforce** —
  talent development and mission acceleration are the same act.

### 19 · Close — calibrate the people, not just the microscope
- **Proofreading is an optimization problem. The missing piece is a principled price for human judgment.**
- **Takeaway / land here:** *Calibrate the people, not just the microscope.*

### 20 · Thank you & acknowledgments
- NeuVue (Daniel Xenes & team), the graders (Pat Rivlin, Lindsey Kitchell), the 8 experts and 36 novices, the
  JHU/APL workforce model. *(NIH BRAIN CONNECTS, UM1NS132250.)*
- **Takeaway:** a team effort — name the people.

---

## Backup (only if asked)
- **Action Mix & Grammar (detail)** — the full action-mix bars and the navigate↔segment transition matrix by cohort.
- **What separates experts (RF / PCA / motif)** — three views (RandomForest importance, PCA, learned-motif
  "dialect") all point to 3-D exploration kinematics. *Exploratory, n=16, post-hoc features.*
- **Outreach (detail)** — demonstrated results, co-authorship pipeline, why the systems approach is rigorous.
- **Proofreaders as Agents (detail)** — the agent taxonomy diagram (naive → expert → ML; capability, cost, scope).

If pressed on the honest negatives: per-**person** accuracy is **not** predictable (the 0.14 is within the
permutation null; ρ=−0.44 is a selection artifact); per-**decision** risk **is** (0.76, p<0.001). Flag
decisions, don't rank people.

---

## Leave the audience with
1. **The right question about a connectome isn't whether it's done — it's whether we've spent our limited,
   noisy expert budget well enough to trust the answer to a specific question.**
2. **That makes the uncharacterized term the *person*: price human judgment, and you can allocate it —
   per-decision, where impact and risk are highest.**
3. **The same measurement that prices the budget develops the workforce — so "calibrate the people, not just
   the microscope" is both the method and the mission.**

*If you remember one line: **calibrate the people, not just the microscope.***
