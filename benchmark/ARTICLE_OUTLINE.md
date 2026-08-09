# Substack Article Outline — "Can AI actually do peer review? We built an answer key."

*Detailed outline of methods, results, and conclusions. All numbers verified against the saved
`matched.json` data and `analyze_ensemble.py` on 2026-06-25. Fix the tier denominators (13/63/24,
not 13/56/31) before publishing — see Appendix note.*

---

## 0. Hook / Lede (½ page)

- AI peer-review tools are everywhere (Refine.ink, Reviewer3, Paper Wizard, raw GPT/Claude calls).
  They all promise to catch methodological errors. Nobody has measured whether they work.
- Why nobody has: **peer review has no answer key.** Reviewers disagree, miss obvious things,
  flag irrelevant ones. You can't score a reviewer without knowing the right answers.
- So we made an answer key: 10 real psychology papers, 100 known errors planted by hand, every
  major AI system scored on the same errors.
- One-sentence punchline to promise up front: *the $50 commercial tool is genuinely good — but a
  30-cent API call to the newest model now beats it, and the gap just widened with one release.*

---

## 1. The core idea: a planted-error benchmark (1 page)

- **The move:** take published papers, insert errors you fully understand, measure detection.
  Recall against ground truth instead of subjective "review quality."
- **The design constraint that makes it hard:** errors must not be shallow. Not typos, not missing
  p-values. Each error has to require understanding *why a methodological choice matters* — the kind
  of thing a good Reviewer 2 catches.
- **The counterintuitive consequence:** most modified papers are *shorter* than the originals.
  We're not adding nonsense — we're **removing the safeguards** that protect the conclusions. A
  deleted sentence, a swapped denominator, a changed design label. The paper still reads fine; you
  just can't trust it anymore. (This is the single most quotable framing in the piece.)

---

## 2. Methods

### 2.1 The papers (½ page + table)

- 10 open-access psychology papers, all CC-BY 4.0, .docx manuscripts hosted on OSF (unmodified
  ground truth in `original papers/`).
- Chosen to span methodological diversity: cross-lagged panels, RCTs, meta-analysis, diary studies,
  registered reports, eye-tracking, corpus methods. (Reuse the 10-row table from EVAL_WRITEUP.)
- The point of the spread: *if an AI reviewer only works on one kind of paper, this finds out.*

### 2.2 The taxonomy: 10 categories of problem (½ page)

- One error per category per paper → 10 errors × 10 papers = 100, every category represented
  equally. (Verified: exactly 10/paper, 10/category.)
- List the 10 categories (statistical, methodological design, construct validity, causal inference,
  internal consistency, reporting completeness, generalizability, theoretical/conceptual, analytic
  flexibility, attrition/missing data).
- Connect to the broader project: this taxonomy (`refine_taxonomy_v4.md`) is meant to feed a
  replication-prediction model (Evidence.Guide). Brief, one paragraph — don't lose the reader.

### 2.3 Difficulty tiers (½ page) — **the conceptual spine of the results**

- **Tier 1 — internal contradictions (13 errors).** Spottable from adjacent text: numbers that
  don't add up, a claim that contradicts data in the same paragraph. The floor — any competent
  system should catch these.
- **Tier 2 — needs methodological knowledge (63 errors).** Why autoregressive controls matter, why
  within-subjects breaks a particular manipulation, why a specific confound check is needed. Where
  the interesting variation lives.
- **Tier 3 — notice what's *missing* (24 errors).** Requires generating an expectation of what
  *should* be in the paper and registering its absence — a deleted transformation, a removed
  safeguard, an absent justification. The hardest tier and, as it turns out, everyone's ceiling.
- ⚠️ **Use 13 / 63 / 24.** The code/reports currently mislabel these as 13/56/31 (stale denominators).

### 2.4 What the errors actually look like (1–1.5 pages — the most engaging section)

Show, don't tell. Walk through 3–4 examples across the difficulty range (all verified in the CSV):
- **Easy / T1 — P4 suicide-risk safety-check reversal:** post-assessment mean changed 0.61 → 1.03,
  so the numbers now show desire-to-die *increasing* while the text still says "decreased slightly."
- **Easy / T1 — P2 identifiable-victim design swap:** "between-subject" → "within-subject," which is
  impossible here (the manipulation teaches the effect; you can't un-know it) and makes the ANOVA df
  wrong. *(Note: writeup currently files this under "hard"; data rates it T1 — pick one.)*
- **Hard / T2 — P6 nurse incivility:** removed the autoregressive controls from a 4-wave
  longitudinal mediation. Results unchanged, prose unchanged, causal claims now uninterpretable.
- **Hard / T2 — P8 memory conformity:** flipped intervention timing "after" → "before" misinformation
  exposure — tests a completely different cognitive mechanism; reads just as natural.
- **Very hard / T3 — P5 Fisher z:** deleted the one sentence converting r→z before meta-analytic
  pooling. (Verified: modified snippet is empty.) Nothing looks wrong; a reviewer has to
  independently think "wait, did they transform r to z?"
- **Very hard / T3 — P3 failed wheels:** deleted "Wheels that did not go down were attributed a
  speed of 0." Now you can't tell whether speed "increased" or failures just dropped out.

### 2.5 Scoring: the hard part (1 page)

- **Problem:** how do you decide a finding matches a planted error when they use different words?
- **Solution:** an LLM judge (Claude Haiku 4.5) with prompt caching. Per paper, all 10 ground-truth
  errors are loaded as a cached prefix; each reviewer finding is a cheap incremental query: "which of
  these 10, if any?" One-to-one assignment, first finding to claim an error wins. (`matching.py`.)
- **The judge had to be made strict.** Early versions matched on *topic overlap* — a model commenting
  on robustness checks that *were present* got credited for "robustness check removed." The strict
  prompt requires identifying the *specific defect*, not discussing the topic. (Show the before/after;
  it's a credibility moment — we caught ourselves inflating scores.)
- **Scoring evolution as a cautionary tale** (great mini-section): fuzzy string matching gave
  82–94/100 (≈35 points of false credit); LLM judge with a pre-filter gave 49–60 but silently dropped
  valid matches; cached judge, no pre-filter, strict prompt → the real spread. *Lesson: the scoring
  method moved scores more than the models did.*

### 2.6 Three things that make the numbers honest (½ page)

- **False-positive baseline.** Run every system on the *original, unmodified* papers. 13–21% of
  "detections" are incidental overlap between real paper issues and our error descriptions. We
  subtract this: **adjusted = modified − originals.** This is *the* headline metric.
- **Reliability.** Each LLM run 3×; range from ±1 (GPT-5.4, near-deterministic) to ±18 (Opus+thinking).
  Single-run comparisons get a caveat.
- **Judge validation.** 20 random decisions hand-checked, all accurate. (Note honestly: not a large
  human-calibration set; flagged as a limitation.)

### 2.7 Keeping the commercial comparison fair (½ page)

- The whole motivating question: Refine.ink charges ~$50/review; a raw API call costs cents. Are you
  paying for better detection or for the product around the model?
- **Content-equal input.** Feed the commercial tools a PDF rendered from the *same* `extract_text()`
  the LLMs see (`docx_to_pdf.py`, fpdf2). Isolates *review ability* from *document-parsing ability*.
- **State the caveat loudly:** that means reflowed text, no native layout/tables. Refine's real
  product might do better on a publisher PDF. **Read its number as a floor, not a ceiling.**

---

## 3. Results

### 3.1 The leaderboard (1 page + the 8-to-12 system table)

- Lead with the adjusted-score table (GPT-5.5 high-reasoning **+47** → Gemini Flash **+20**). Verified.
- **Finding 1 — the frontier jumped.** GPT-5.5 high reasoning is the new #1 at **+47**: 71/100 caught,
  24 FP, and — the headline within the headline — the **best Tier-3 score of any system (13/24)**,
  cracking the "notice what's missing" tier that had been everyone's ceiling. Reasoning, which barely
  helped GPT-5.4, now earns its keep.
- **Finding 2 — volume ≠ signal.** GPT-5.5 *no*-reasoning is a firehose: 704 findings (most of
  anything), 66 caught raw — but 34 FP drag it to +32. Reasoning is what converts volume into signal.
- **Finding 3 — Opus 4.8 hid its skill behind thinking.** No-thinking *regressed* vs Opus 4.6
  (+27 vs +33); high-thinking *improved* (+36) and is the **most precise LLM** (16 FP).
- **Finding 4 — cost.** Best model is ~$0.30/paper. Keep a cost-per-error column; it sets up the
  commercial comparison.

### 3.2 The Tier-3 ceiling — the real scientific finding (½–1 page)

- Every system catches *what's there and wrong* far better than *what's absent.* Tier-3 detection
  rates are low across the board; even the new #1 only gets 13/24.
- This is the genuinely interesting result for a research audience: **"noticing that something should
  be in a paper and isn't" is the frontier capability.** It's also exactly what replication often
  hinges on (the missing transformation, the undisclosed flexibility).
- Tie back to the error-design philosophy: we built Tier 3 specifically to test reasoning-from-first-
  principles vs. red-flag-scanning, and it separated the systems.

### 3.3 The commercial tools (1.5 pages — the piece's center of gravity)

**Refine.ink — the exhaustive reviewer.**
- Genuinely strong: against the *previous* generation it posted the **best** adjusted score we
  measured (+38), and did it with the **cleanest precision** of any strong system (19 FP). Not a
  wrapper coasting on a model.
- Then the frontier moved: GPT-5.5 reasoning clears it by 9 points (+47 vs +38), catching *more* and
  cracking Tier-3 better. Refine drops from #1 to a strong #2.
- Its weakness is the universal one, harder: Tier-3 **5/24**, vs GPT-5.4's 11. Excellent on Tier 1–2
  (design changes, swapped constructs, contradictory numbers), nearly blind to deletions.

**Reviewer3 — the selective journal reviewer.**
- Opposite design philosophy. ~12 comments/paper (everyone else: 20–70). Ranked, severity-tagged,
  like a real journal review.
- **Most precise system in the whole benchmark:** 9 FP, lowest of anything. But terseness costs
  recall — 30/100, +21, near the bottom.
- **The honest caveat — state it plainly:** *our benchmark rewards catching planted errors, which is
  not the same as writing a useful review.* A tight 8-comment review may help an author more than a
  50-item firehose. Reviewer3 optimizes for the former; we measure the latter. Read its score as "low
  recall on a recall test," not "bad reviewer." (This is the intellectual-honesty high point — don't
  cut it.)

### 3.4 Does a second reviewer help? It used to. (1 page)

- Averages hide *which* errors each system catches. Refine and the LLMs don't fully overlap → pool them?
- **Against GPT-5.4: clearly yes.** Jaccard 0.54; GPT-5.4 + Refine = **+45**, the best config of the
  whole previous generation, 7 points clear of any solo system. Refine contributed 6 errors *no* LLM
  caught, 4 of them from the "never caught by anyone" list.
- **Against GPT-5.5: the second reviewer stopped mattering.** Jaccard rose to 0.60; GPT-5.5r + Refine
  = **+47**, same as GPT-5.5r alone. Refine still adds 9 true catches — but 9 false positives come
  with them. The stronger model **absorbed the complementary coverage.**
- **Two durable lessons:**
  1. *Pooling everything is a trap.* All 12 LLMs union = 85–91 raw but FP balloons to 60 → +31,
     *worse* than the best single model. Small diverse panels beat crowds; correlated reviewers grow
     the FP union faster than the TP union.
  2. *The value of a same-content second opinion shrinks as the lead model improves.* A moving target.
- **The best configuration found:** GPT-5.5 reasoning + Refine + Reviewer3 = **+49**. Reviewer3 adds
  +2 with *zero* added FP — exactly what a high-precision specialist should do. The strongest setup
  isn't any single tool; it's a lean panel of three readers who fail differently.

---

## 4. Conclusions (1 page)

- **On the $50 question:** the premium isn't buying error detection a good prompt wouldn't get you.
  Same content in, the best raw API call beats Refine by 9 points for ~1/150th the price. The $50 buys
  the *product* — upload, formatting, comment triage, the chat, not writing the prompt or wiring an
  API. For many researchers that's worth real money. Just don't believe it's finding things the models
  can't. (Be fair, not dismissive — Refine is the cleanest strong reviewer we tested.)
- **On where AI peer review actually stands (mid-2026):** the frontier can now catch a majority of
  deliberately planted methodological errors, including — for the first time — a real chunk of the
  "what's missing" tier. But that tier is still the ceiling, and it's the one that matters most for
  replication.
- **On how to use these tools today:** not "pick the winner" but "assemble a lean panel that fails
  differently" — a frontier model + an exhaustive reviewer + a precise one. Diversity over raw ceiling.
- **On benchmarking itself (meta-lesson):** the scoring method moved the scores more than the models
  did. Fuzzy matching inflated by 35 points; a loose judge inflated false positives; a missing FP
  baseline would have flattered everyone. Most "AI does X" claims die on exactly these details.
- **What we still can't measure:** useful-review quality vs. planted-error recall (the Reviewer3
  problem); generalization beyond psychology; whether models saw these papers in training.

---

## 5. Limitations & honesty box (½ page — a sidebar, not buried)

- Psychology only; unclear if it generalizes to other fields.
- Possible training-data contamination (originals are public); mitigated by moderate scores, not ruled out.
- AI judging AI; only 20 human-validated judge decisions.
- Content-equal (reflowed) PDFs disadvantage commercial tools built for native layout — their numbers
  are a floor.
- Recall-on-planted-errors ≠ review quality (undervalues selective reviewers like Reviewer3).
- Reliability is model-dependent; some single-run numbers carry ±10+ noise.

---

## 6. Optional appendices / "for the nerds"

- Full 12-system table with reliability ranges, FP baselines, cost/paper, findings count.
- Per-category and per-paper detection heatmaps (`reports/by_category.csv`, `by_paper.csv`).
- The 16-errors-never-caught list (Run 3 ceiling) and which the new frontier finally cracked.
- Reproducibility: code, `error_insertions.csv`, providers, the cached-judge design.

---

## Appendix note to self before publishing (verification, 2026-06-25)

- **FIX the tier denominators.** True split is **13 / 63 / 24** (T1/T2/T3), confirmed from the
  `difficulty` column. The reports and several log tables print `/13 /56 /31` (stale — 7 errors were
  re-rated T3→T2 and `score_reviews.py:71-73,139` was never updated). Numerators are correct; only the
  denominators and the derived "/31" Tier-3 phrasings are wrong. So "13/31" → **13/24**, "5 of 31" →
  **5 of 24**. The Tier-3-is-the-ceiling story is unchanged (and 13/24 = 54% is a cleaner stat).
- **P2 tier label:** EVAL_WRITEUP files the between→within swap under "hard"; the data rates it T1.
  Reconcile.
- All headline and ensemble numbers reproduce exactly from saved data — safe to quote as-is:
  +47 / +38 / +37 / +36 / +21 singles; +45 (GPT-5.4+Refine), +49 (3-way best), +31 (kitchen sink).
- GPT-5.4 high-reasoning *originals* baseline is only 4/10 papers — keep it out of head-to-heads
  (already handled).
