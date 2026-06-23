# The Language of Proofreading — talk frame

A frame to add to *"When have we proofread enough to trust the answer?"*
(`berlin_deck_v2.pptx`). It does **not** claim a publishable result. It adds a
concept — *the language of proofreading* — and a **data anchor**: the behavioral
signal already exists, at scale, and we can read it today.

The companion notebook
`notebooks/posthoc_proofreader_differstack_analysis.ipynb` produces every number
and figure referenced below.

---

## 1. The one-sentence frame

> Every proofreading session leaves a behavioral trace — the Neuroglancer
> `differ_stack`. Treat that trace as a **language**: it has a **vocabulary**
> (the kinds of edits), a **grammar** (how edits follow one another), **dialects**
> (how proofreaders systematically differ), and **fluency** (rhythm and timing).
> Reading this language is how we *price expert judgment* and *calibrate the
> people* — the missing piece the rest of the talk is reaching for.

## 2. Why it belongs in *this* talk

The deck already lands here on its own logic:

- **Slide 9 — "Pricing the budget = calibrating the annotators."** "Characterize
  proofreaders: per-task, per-region competence, and how much they agree… this is
  why some learn to see a neuron and others don't — not a verdict on people, a
  measurement of the task."
- **Slide 10 — "We've already run a version of this."** Staged promotion by
  agreement on Minnie65 (NeuVue). *This summer:* "Predict competence from early
  behavior, pre-registered — not promote after the fact."

Slides 9–10 *assert* that competence is measurable and that early behavior might
predict it — but the deck never says **what you actually measure**. The language
of proofreading is the answer: the `differ_stack` is the early behavior, and its
vocabulary/grammar/dialect/fluency are the features. It converts "calibrate the
people" from a slogan into a concrete, already-collected measurement.

**Placement:** insert as **Slide 9.5**, between "calibrate the annotators" (9) and
"the predictive test" (10). It's the bridge: *here is the substance of the
measurement; therefore the predictive test in slide 10 is well-posed.*

## 3. The two slides to add

### Slide 9.5 — "Proofreading has a language"

- **Vocabulary** — the kinds of edits a proofreader makes (merge, split, set
  segment, navigate, flag…). The "tokens."
- **Grammar** — the order they come in. Which action follows which, within a
  session. Workflows have syntax.
- **Dialects** — proofreaders differ, systematically, in vocabulary and grammar.
  Measurable distance between people — not a ranking of worth.
- **Fluency** — rhythm: bursts of work, deliberate pauses, idle gaps. The real
  expert *minutes* a decision costs.
- *Bottom line:* "Calibrate the people" = read this language. It's already
  recorded on every NeuVue task.

> **Speaker note.** Don't oversell. The point isn't "we have a model." It's that
> the thing we kept saying we'd measure — competence, agreement, the price of a
> judgment — has a concrete, already-collected substrate. Promotion-by-agreement
> (slide 10) used the *outcome*. The language is the *behavior* underneath it,
> and it's there from the first session.

### Slide 9.6 (optional) — "We can already read it, at scale"

A single data-anchor slide. Fill the brackets by running Sections 3 and 14 of the
notebook against the live queue:

- **[N] proofreaders · [M] edit events · [K] action types** across **[P]**
  namespaces on NeuVue (Section 3 survey).
- **Vocabulary is skewed** — a Zipf-like rank/frequency of actions (Section 14a).
- **Grammar is real** — action→next-action transition structure, not uniform
  (Section 14b).
- **Dialects are measurable** — a Jensen-Shannon "dialect-distance" map separates
  proofreaders (Section 14c).
- *Caption:* "All from `differ_stack` history — no new instrumentation."

> **Speaker note.** This is the honest version of a data slide: it shows the
> signal is extractable and structured, and that people differ in it. It does not
> claim the signal predicts competence yet — that's slide 10's pre-registered
> test. Stating that limit out loud matches the deck's tone (slide 10: "if not,
> the idea fails, and I'll say so").

## 4. How each claim is anchored (notebook map)

| Slide claim | Notebook section | Output |
|---|---|---|
| "Lots of data, lots of users" | **3. Survey** | namespaces × users × volume × date span |
| Vocabulary exists and is skewed | **14a** | action counts + Zipf rank-frequency plot |
| Proofreading has grammar | **14b** | P(next \| current) transition matrix + heatmap |
| Proofreaders have dialects | **14c** | per-user entropy/vocab + JS-divergence map |
| Fluency / real cost of a decision | **16. Session timing** | inter-event gaps, active vs. idle time |
| Behavior scales with effort | **13 / 17** | events-per-task, Kruskal-Wallis, Spearman |

## 5. Data-anchor checklist (to do with credentials, ~30 min)

1. Run the notebook where NeuVue creds live (config file or `NEUVUEQUEUE_*` env
   tokens). It cannot authenticate on a headless box — the login is an
   interactive Auth0/Google flow.
2. **Section 3** with `SURVEY_LIMIT` raised (e.g. 100k): record N users, P
   namespaces, date span → the headline numbers for Slide 9.6.
3. Pick 1–2 high-volume namespaces (`NAMESPACE`, `ASSIGNEES = []`), set a date
   range, run end to end.
4. **Section 11** — read the real differstack keys. If the actual edits live under
   different fields (e.g. added vs. removed segment sets = merges vs. splits),
   edit `classify_action()` in Section 14 once; everything downstream follows.
5. Export the three figures from **14a/14b/14c** and the **Section 3** table.
   Total tokens (M) and action types (K) print at the top of 14a.

## 6. Honest limits (keep these on the record)

- This is a **frame plus an access demonstration**, not a validated predictor.
- The differstack reflects what a given Neuroglancer build emits; some workflows
  (e.g. spelunker mode) send little or nothing. Coverage is reported in Section 9.
- "Dialect distance" measures behavioral difference, **not** correctness. Tying it
  to competence is exactly slide 10's open, pre-registered question.
