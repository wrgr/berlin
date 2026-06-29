# Claims audit & trim proposal — baseline cut (27 slides)

Purpose: (1) verify the figures are accurate and every on-slide claim is **substantiated** by the
analysis that builds it, and (2) propose how to **trim and streamline** the story. Sources checked:
the 27-slide baseline, the `fig_*.png` images, the build scripts in `analysis/`, and
`methodology_provenance.md` / `transparency_failure_modes.md` / `figure_descriptions.md`.

Bottom line: **the figures are honest** — the hard caveats are baked into the figure titles
themselves ("the 0.92 was cell-identity leakage", "3 'killer' cells drive the risk signal",
"n=16", "'worse than chance' is within the noise"). No wrong numbers or arithmetic errors were
found; deck text matches the figures. The real issues are **strength-of-claim vs. evidence** and
**internal coherence** — and they point the same way the trim should go.

---

## The one structural problem (fix this first)

**The deck spends the most slides on its least-substantiated result and the fewest on its
best-substantiated one.**

| Result | Slides | Evidence quality |
|---|---|---|
| "Language of proofreading" — behavior separates experts (AUC 0.95/0.90) | **14–17 (4 slides)** | **Weakest.** n=16, 28 features, no CI, no permutation null; volume-confounded |
| Calibration converges per-decision (~99% point agreement) | 9 (footnote) + 18 (footnote) + 21 (backup) | Strong, descriptive |
| Per-person accuracy is NOT predictable (honest negative) | 20 (backup) | Strong, careful (this is the rigorous one) |
| GT-free task **risk** predictable (AUC 0.76) | **19 (1 slide)** | **Strongest.** Grouped-by-cell CV + 1000-perm null, p<0.001 |

Rebalancing toward what survives scrutiny is simultaneously the **streamline** and the
**substantiation** fix.

---

## Three substantiation risks (in priority order)

### 1. The flagship AUCs (0.75 / 0.95 / 0.90) have no uncertainty and n=16
`mine_tiers.py` reports `cross_val_score(...).mean()` — a single point per tier, **no CI, no
permutation null**, on **n=16** (8 experts vs 8 proto-experts) with **28 features** in the
"designed" tier. At n=16 a 5-fold CV AUC has very wide confidence intervals; 0.95 is not a robust
point estimate, and 28 features / 16 samples invites optimism. The figure prints "n=16" but the
three clean bars read as settled.
- **Figure_descriptions already concedes this**: "small n; the 0.95 is a pilot point (confirmatory
  data = the summer test)."
- **Fix (substantiation):** report uncertainty. Add a permutation null and a per-fold/bootstrap
  spread to `mine_tiers.py`, and draw the bars with error bars or annotate "pilot, n=16". Ready-to-
  paste patch at the bottom of this file.
- **Fix (slide):** title it as a **pilot** and state n on the slide, not just the axis. Until the
  confirmatory ("summer") run lands, the honest verb is "**separates** in a pilot," not "is
  diagnostic of."

### 2. The behavior signal is partly a *volume* signal, not pure *style*
Several "designed" features are **extensive** (totals that grow with how much telemetry was
captured): `n_events`, `evt_per_session`, `total_rot_deg`, `n_rot`. In `fig_kinematics` experts show
~2× **events** *and* ~2× **rotation** *and* ~2× **viewpoints** — these move together. So "experts
accumulate ~2× more camera rotation / inspect from more viewpoints" may substantially reduce to
"experts logged ~2× more activity," not an independent claim about richer 3-D *exploration*.
- **Why it matters:** the slide-15/16 story ("skill is in *how* the work is done") is weakened if
  the separating features are mostly "how *much*."
- **Fix:** re-run the tier AUC on **intensive (rate) features only** — `pct_*`, transition-grammar
  `bg_*`, `mean_rot` (rotation **per event**), `dt_med`, run-length *means*, entropy — dropping the
  raw totals. If separation survives on intensive-only features, the "style" claim is earned; if it
  collapses toward the naive 0.75, say "experts do more," which is still true and still useful.
- **Word fix now:** `fig_kinematics` says experts inspect "more **thoroughly**." "Thoroughly"
  editorializes that more rotation = better inspection; the accuracy data (next point) say it isn't.
  Prefer "experts explore from ~2× more viewpoints and log ~2× more activity" — describe, don't
  valorize.

### 3. The "expertise" axis points the WRONG way for accuracy (coherence, not just strength)
This is the most important one for telling a *cohesive* story. `fig_accuracy_unpredictable`
panel 3 (and `transparency_failure_modes.md`) show that **total camera rotation — the headline
"expertise signal" — weakly *anti*-correlates with fullyProofread accuracy: ρ = −0.44.** The two
low-accuracy points are experts (gary, michael — also the two ~75% point-agreement outliers).

So the implicit chain the audience will assemble — *expert style → richer exploration → better
work* — is **contradicted by your own data**. The deck half-addresses this ("style ≠ proficiency")
but "≠" undersells it: among calibrated annotators the style axis is *opposed* to accuracy.
- **This is a feature, not a bug — if you frame it.** The sharper, more provocative, and
  better-substantiated story is: *behavioral style cleanly tags the expert **cohort**, but a
  calibrated workforce **converges** on accuracy — so style is **not** proficiency, and the
  deployable signal is **per-decision risk** (GT-free, 0.76), not per-person skill.* That reframing
  turns the awkward ρ=−0.44 into the hinge of the talk.

---

## Per-slide verdicts (claims that need attention)

Only slides with a substantiation note are listed; everything else checked out.

- **S1 "Calibrate the humans, not just the microscope"** — fine. (Note: S1 of the *automatic* deck
  says "students"; you changed it to "humans". Consistent with the agent-agnostic framing.)
- **S14 "behavior separates experts from proto-experts"** — true **in a pilot (n=16)**. Add the
  pilot/n caveat to the slide. ✅ with hedge.
- **S15 "~2× more camera rotation … inspect from more viewpoints … move faster"** — numbers match
  `fig_kinematics` (rot 1014 vs 466, viewpoints 14.2 vs 6.0, events 3033 vs 1426, tempo 30.9 vs
  23.1). But see risk #2 (volume confound) and #3 ("more thoroughly" overclaims). ⚠️ reword.
- **S16/S17 grammar, RF importance, PCA, motif "dialect"** — descriptive and accurate, but all on
  the same n=16. RF importance highlighting the kinematic *totals* is partly the volume confound
  (#2). Candidate to demote to backup (see trim). ⚠️
- **S18 "Promoted ≈ expert < unpromoted (distance-to-GT)"** — ordering is real (309/312/460) but the
  promoted<unpromoted gap is **not significant** (p≈0.21, n=7/19). The slide doesn't claim
  significance and the caption hedges ("lower = better"), so this is OK — just don't *say*
  "significantly". ✅
- **S19 "risk predictable at AUC 0.76 … 0.92 was leakage … per-person ~0.55"** — **fully
  substantiated** (grouped CV + 1000-perm null, p<0.001). One nuance the figure shows but the text
  doesn't: the signal is largely "flag the **3 of 28** intrinsically-hard cells." Fine as-is
  because the figure is on the slide, but if you ever quote 0.76 without the figure, carry the
  "few-killer-cells" caveat. ✅
- **S20 (backup) "accuracy not predictable; 0.14 within the null 0.45±0.20; per-decision 0.59"** —
  this is the **most rigorous slide in the deck**. Keep it; consider promoting one line of it into
  the main line so the honest negative is heard, not buried. ✅
- **S21 (backup) point agreement** — accurate (expert med 98%, promoted 100%, unpromoted 94%
  bimodal; chris 99.3%). Two experts (gary 76%, michael 74%) sit low — the figure shows it
  honestly. This convergence result deserves to be in the **main** line, not backup (see trim). ✅
- **S25 "students became co-authors … several were top-throughput proofreaders credited in
  MICrONS"** — partly resting on handle→identity work that `methodology_provenance.md` §11 and
  `transparency_failure_modes.md` flag as **unreliable** (CAVE `user` = executor, not assignee;
  gary/christopher both map to uid 1833). Daniel Xenes (co-author, leads NeuVue) is solid and
  specific — lead with that; keep the "top-throughput credited" claim **general** (don't attach
  specific edit-count rankings to specific student handles in public). ⚠️

---

## Trim / streamline proposal (27 → ~21 main slides)

Cut where the evidence is thinnest and the slides repeat; keep the rigorous results. This *is* the
"less hard results, integrated story" the brief asks for.

**Cut or merge (−6):**
1. **S5 (prior-work prose) — cut.** S7 ("PROBLEM LINEAGE" graphic) is the same content, better. −1
2. **One of the two section dividers S12/S13 — cut.** "Can we learn a language?" and "What behavior
   reveals" do the same job. Keep one. −1
3. **Compress the 4-slide behavior montage (S14–S17) → 2.** Keep S14 (separation + GT-free flag)
   and **one** mechanism slide (kinematics *or* grammar). Move the RF/PCA/motif montage (S17) and
   the second mechanism slide to **backup**. This is the weakest-substantiated block; it should not
   be the largest. −2
4. **Merge ecosystem (S24) + outreach (S25) → 1** "where this lives / students as a method." −1

**Promote into the main line (no count change, big coherence gain):**
- Pull the **point-agreement convergence** (currently backup S21) and **one line of the honest
  negative** (S20) into the main arc, right after the behavior slide. The sequence *behavior tags
  the cohort → but accuracy converges → so it's per-decision risk, not per-person skill* is the
  spine that resolves the ρ=−0.44 tension and lands the GT-free risk result as the payoff.

**Resulting arc (tight, builds fast, ends on the invitation):**
1. Hook — calibrate the human, not just the microscope (S1, +the "humans aren't needed??"
   provocation S6 folded in)
2. The real question: trust under a finite, noisy expert budget → optimization (S2)
3. Everyone's an agent; route by impact × risk (S3 + S4)
4. To route you must **price** judgment (S8 + S9)
5. Prior work circled it but didn't operationalize (S7 graphic) — quick
6. **Learned ①** there's a *language* — style tags the expert cohort (S14, **pilot n=16**) + the
   JIGSAWS analogy (S11)
7. **Learned ②** but calibration converges — promoted ≈ expert ~99%; **style ≠ proficiency** (point
   agreement, promoted from backup)
8. **Learned ③** so measure **decisions, not people** — per-person accuracy isn't predictable
   (honest negative, one line) (S18 + S20-line)
9. **Learned ④** and risk is predictable **GT-free, before you spend** — AUC 0.76 (S19) ← the payoff
10. The bottleneck today: promotion is selection-on-outcome → can we predict it early? (S10)
11. **Invitation** — predict promotion from early behavior; train the data-starved "language model
    of proofreading"; deploy per-decision risk routing live
12. The double win: pricing the budget = developing the workforce; students as a method (S24+S25
    merged; S22/S23 workforce kept tight)
13. Close — optimization problem; missing piece = price of human judgment; come build it (S27)

Backup: kinematics/grammar mechanism, RF/PCA/motif, accuracy-unpredictable detail, point-agreement
confusion matrix.

---

## Ready-to-paste: add uncertainty to the tier AUCs (`mine_tiers.py`)

Drop-in replacement for the `auc()` helper so the headline numbers ship with a CI and a permutation
p-value. Requires a credentialed network run to regenerate `tiers_data.csv`.

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
def auc(fe, y, sub, n_boot=2000, n_perm=1000, seed=0):
    Xx = sub[fe].fillna(sub[fe].median()).values
    yv = y.values
    if y.nunique() < 2 or min(y.value_counts()) < 3:
        return None
    rf = RandomForestClassifier(400, min_samples_leaf=2, random_state=0)
    cv = StratifiedKFold(min(5, min(y.value_counts())), shuffle=True, random_state=0)
    obs = cross_val_score(rf, Xx, yv, cv=cv, scoring="roc_auc").mean()
    rng = np.random.RandomState(seed)
    # permutation null: shuffle labels, re-run CV
    null = np.array([cross_val_score(rf, Xx, rng.permutation(yv), cv=cv,
                                     scoring="roc_auc").mean() for _ in range(n_perm)])
    p = (int((null >= obs).sum()) + 1) / (n_perm + 1)
    # bootstrap CI over annotators (resample rows, recompute CV AUC)
    boots = []
    for _ in range(n_boot):
        idx = rng.randint(0, len(yv), len(yv))
        if len(set(yv[idx])) < 2:
            continue
        boots.append(cross_val_score(rf, Xx[idx], yv[idx], cv=cv, scoring="roc_auc").mean())
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan)
    return {"auc": obs, "ci": (lo, hi), "null": (null.mean(), null.std()), "p": p}
```
Then print `auc / ci / p` per tier and draw the bars in `make_figures.py` with `yerr` from the CI.
At n=16 expect wide intervals — that honesty is the point, and it pre-empts the obvious referee
question.
