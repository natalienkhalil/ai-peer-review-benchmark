# AI Peer Review Benchmark — Analysis Log

## Project Summary

Benchmark evaluating how well frontier AI models detect methodological and statistical errors in scientific manuscripts. 100 deeply structural errors inserted across 10 open-access psychology papers (10 per paper, one per taxonomy category). Errors target load-bearing methodological elements — removing safeguards, changing constructs, altering designs — not surface-level word swaps.

---

## Run 1: Initial Eval with Fuzzy Matching (2026-03-19)

**Models tested:** Claude Sonnet 4.6, Claude Opus 4.6, GPT-5.4 (each with and without thinking/reasoning)

**Matching method:** rapidfuzz token_set_ratio with 0.35 threshold + Hungarian assignment

**Results (inflated due to loose matching):**

| Model | Score /100 |
|-------|-----------|
| GPT-5.4 (No Reasoning) | 94 |
| Claude Sonnet 4.6 (No Thinking) | 90 |
| Claude Opus 4.6 (No Thinking) | 87 |
| GPT-5.4 (High Reasoning) | 85 |
| Claude Opus 4.6 (High Thinking) | 84 |
| Claude Sonnet 4.6 (High Thinking) | 82 |

**Key finding:** Scores clearly inflated — fuzzy matching gave ~35 points of false credit. More findings = higher score (no-thinking models produce 2x more findings, getting more fuzzy-match hits). Thinking/reasoning appeared to hurt, but this was an artifact.

---

## Run 2: LLM Judge with Pre-filter (2026-03-19)

**Matching method:** rapidfuzz pre-filter (quote_sim > 0.25 OR desc_sim > 0.3) → Haiku yes/no judge per pair → Hungarian assignment

**Results:**

| Model | Score /100 |
|-------|-----------|
| GPT-5.4 (No Reasoning) | 60 |
| Claude Sonnet 4.6 (No Thinking) | 56 |
| GPT-5.4 (High Reasoning) | 56 |
| Claude Opus 4.6 (No Thinking) | 54 |
| Claude Sonnet 4.6 (High Thinking) | 53 |
| Claude Opus 4.6 (High Thinking) | 49 |

**Pooled union:** 81/100

**Issues identified:** Pre-filter was silently dropping valid matches where models described issues in different language. Pairwise yes/no judging couldn't pick the BEST match among 10 candidates.

---

## Run 3: Cached Judge, No Pre-filter (2026-03-19) ← CURRENT BEST

**Matching method:** All 10 ground truth errors sent as cached prompt prefix → Haiku picks which error (1-10) each finding matches, or "none" → first-claim assignment

**Key improvement:** No pre-filter. Every finding gets judged against all 10 errors simultaneously. Prompt caching (Anthropic ephemeral cache) means the 10-error context is sent once per paper, then each finding is a cheap incremental call.

**Results:**

| Model | Score /100 | Findings | T1 /13 | T2 /63 | T3 /24 |
|-------|-----------|----------|--------|--------|--------|
| Claude Opus 4.6 (High Thinking) | **61** | 293 | 12 (92%) | 40 (63%) | 9 (38%) |
| GPT-5.4 (No Reasoning) | **54** | 421 | 7 (54%) | 36 (57%) | 11 (46%) |
| Claude Sonnet 4.6 (No Thinking) | **49** | 356 | 9 (69%) | 32 (51%) | 8 (33%) |
| GPT-5.4 (High Reasoning) | **48** | 278 | 7 (54%) | 33 (52%) | 8 (33%) |
| Claude Opus 4.6 (No Thinking) | **46** | 310 | 11 (85%) | 27 (43%) | 8 (33%) |
| Claude Sonnet 4.6 (High Thinking) | **37** | 241 | 7 (54%) | 24 (38%) | 6 (25%) |

**Pooled union:** 84/100 (16 errors uncaught by any model)

**Key findings:**

1. **Opus+Thinking is the clear winner (61).** The pre-filter had been disproportionately hurting it because Opus writes nuanced descriptions that don't text-match well. Without the pre-filter, its deeper analysis gets properly credited.

2. **Spread is 37–61 (24 points)** — excellent discrimination between models. Much better than the 11-point spread with the pre-filter.

3. **Thinking/reasoning helps Opus dramatically (+15)** but hurts Sonnet (-12). Opus's thinking produces genuinely better analysis; Sonnet may overthink or lose focus.

4. **GPT-5.4 no-reasoning is strong (54)** largely through volume — 421 findings gives more chances to match. Its precision is lower but recall is high.

5. **The benchmark discriminates well:** range of 37-61, clear tier separation, different models have different strengths by category.

### Detection by Category (avg across 6 models, /10)

| Category | Avg | Best Model |
|----------|-----|------------|
| analytic_flexibility | 5.8 | Opus+Think, GPT5.4, GPT5.4+Reason (7) |
| construct_validity | 5.5 | Opus+Think (8) |
| methodological_design | 5.7 | GPT5.4 (7), Opus+Think (7) |
| causal_inference | 4.2 | Opus (6), Opus+Think (6) |
| reporting_completeness | 4.7 | Opus+Think (6), GPT5.4 (6), Sonnet (6) |
| theoretical_conceptual | 4.7 | GPT5.4+Reason (6) |
| attrition_missing_data | 4.5 | Sonnet (6), GPT5.4 (6) |
| generalizability | 4.5 | Sonnet (6), GPT5.4+Reason (6) |
| internal_consistency | 5.0 | Opus+Think (8), Opus (8) |
| statistical_errors | 4.2 | Opus+Think (6), GPT5.4 (6) |

### Detection by Paper (avg across 6 models, /10)

| Paper | Avg | Topic |
|-------|-----|-------|
| P1 | 6.2 | SDO & Environmentalism (cross-lagged panel) |
| P2 | 4.8 | Identifiable Victim Effect (replication) |
| P3 | 4.2 | Cultural Evolution (wheel experiment) |
| P4 | 5.5 | Text Messages & Suicide Risk |
| P5 | 4.7 | Self-Esteem & Facebook (meta-analysis) |
| P6 | 5.2 | Incivility in Nursing (diary study) |
| P7 | 4.7 | Short-Term Memory Illusions (4 experiments) |
| P8 | 4.5 | Memory Conformity (registered report) |
| P9 | 4.8 | Moral Incongruence & Addiction |
| P10 | 4.7 | Statistical Info in English Writing |

### Errors Never Caught (16/100)

These represent the current hard ceiling for frontier models on single-pass review:

- P2: affect_measures_replaced, effect_size_misreported, exclusion_criteria_added, transparency_statement_removed
- P3: coder_count_changed, confidence_interval_changed, hypothesis_mischaracterized, information_constraint_removed, understanding_measure_changed
- P5: adaptation_detail_removed, centering_removed, institutional_diversity_reduced
- P6: scale_items_changed
- P7: implausible_stimulus_size, temporal_inference_removed
- P9: moderator_roles_swapped

---

## Methodology Notes

### Error Design Philosophy
- 100 errors, 10 per paper, one per taxonomy category
- Deep structural modifications: removing safeguards, changing constructs, altering designs
- Most modified papers are SHORTER than originals (deletions of protective elements)
- 8 initially uncatchable errors (detectable only by comparing to original) were replaced with errors creating internal contradictions
- Difficulty rated T1 (easy, internal contradiction), T2 (hard, requires methodological knowledge), T3 (very hard, requires generating expectations)

### Scoring Evolution
The scoring method matters enormously:
- Fuzzy matching (threshold 0.35): 82-94 range — nearly useless, inflated by false matches
- LLM judge with pre-filter: 49-60 range — better but pre-filter silently drops valid matches
- LLM judge, no pre-filter, cached: 37-61 range — best discrimination, reveals true model differences

### Key Methodological Concerns
1. **No false positive baseline** — haven't run on original papers yet
2. **N=1 run per model** — no test-retest reliability
3. **Taxonomy in prompt** — tells models what to look for (vs. open-ended review)
4. **Training data contamination** — models may have seen original papers (but scores are moderate, suggesting this isn't dominant)
5. **AI judging AI** — Haiku as judge may have systematic biases
6. **All psychology papers** — unclear if results generalize to other fields

### Next Steps
- [ ] Run on original (unmodified) papers for false positive baseline
- [ ] Run each model 3x for reliability estimates
- [ ] Test with open-ended prompt (no taxonomy categories)
- [ ] Investigate the 16 uncaught errors — are they genuinely uncatchable?
- [ ] Add more review systems (Refine.ink, manual reviewers)

---

## Run 4: Robustness Checks — SUPERSEDED by Run 5

See Run 5 below. Run 4 used the loose judge prompt which inflated false positive baselines (25-34/100 on originals). Run 5 fixed the judge to require specific rather than topical matches.

## Run 5: Robustness Checks with Strict Judge (2026-03-20) ← CURRENT BEST

Tightened the LLM judge prompt after discovering it was matching on topic overlap rather than specific error identification. For example, a model commenting on robustness checks that ARE present in the original was being matched to the "robustness check removed" error. The strict prompt requires the finding to identify the SPECIFIC defect, not just discuss the same topic.

All 30 provider variants re-scored (6 models × 5 conditions: main, originals, run2, run3, open).

**Total API calls:** ~275/300 (GPT-5.4 High Reasoning hit quota limits at 4/10 papers for run2/run3/open/originals conditions)

### 4a. False Positive Baseline (Original Papers)

Ran all 6 models on the 10 ORIGINAL (unmodified) papers to measure how many "errors" the judge matches even when no errors are present.

| Model | Modified | Original | Delta (signal) | Findings (Mod) | Findings (Orig) |
|-------|----------|----------|---------------|----------------|-----------------|
| Opus+Think | 61 | 27 | **+34** | 293 | 286 |
| Opus | 45 | 25 | **+20** | 310 | 310 |
| Sonnet+Think | 40 | 24 | **+16** | 241 | 243 |
| Sonnet | 49 | 34 | **+15** | 356 | 410 |
| GPT5.4+Reason | 49 | 9* | **+40** | 278 | 103 |
| GPT5.4 | 53 | 33 | **+20** | 421 | 427 |

**Key finding: False positive rates are HIGH (9-34/100).** This means a substantial portion of what we're counting as "detections" on modified papers are things the model would have flagged anyway. The models produce roughly the same NUMBER of findings on original and modified papers (e.g., Opus: 310 vs 310, GPT5.4: 421 vs 427) — they just happen to match different ground truth errors.

**The true signal (Delta) is the difference:** Opus+Think has the highest signal at +34, meaning 34 of its 61 detections are genuinely due to the inserted errors. Sonnet has the lowest signal at +15. This changes the ranking:

| Model | Adjusted Score (Modified - Original) |
|-------|--------------------------------------|
| GPT5.4+Reason | +40* (incomplete originals) |
| Opus+Think | **+34** |
| Opus | +20 |
| GPT5.4 | +20 |
| Sonnet+Think | +16 |
| Sonnet | +15 |

**Opus+Think is the clear winner on adjusted scores.** Its high raw score isn't just from producing more findings — it genuinely detects more of the inserted errors above baseline.

### 4b. Test-Retest Reliability (3 Runs)

| Model | Run 1 | Run 2 | Run 3 | Mean | Range |
|-------|-------|-------|-------|------|-------|
| Opus+Think | 61 | 46 | 42 | **50** | ±19 |
| Opus | 45 | 49 | 59 | **51** | ±14 |
| Sonnet+Think | 40 | 34 | 43 | **39** | ±9 |
| Sonnet | 49 | 40 | 46 | **45** | ±9 |
| GPT5.4+Reason | 49 | 18* | 21* | 29* | ±31* |
| GPT5.4 | 53 | 54 | 56 | **54** | ±3 |

**Key finding: Reliability varies enormously across models.**

- **GPT-5.4 no-reasoning is by far the most reliable** (±3 range, scores 53-56). Deterministic behavior with temperature=0.
- **Claude models show moderate variance** (±9 to ±19). Opus+Think has the widest swing (42-61), suggesting its thinking process introduces stochasticity.
- **Sonnet is more reliable than Opus** across both thinking conditions (±9 vs ±14-19).
- **GPT-5.4 high reasoning data is incomplete** due to quota limits (only 4/10 papers for runs 2-3), so its apparent ±31 range is unreliable.

**The mean scores (averaging 3 runs) change the ranking:**

| Model | Mean (3 runs) |
|-------|--------------|
| GPT5.4 | **54** |
| Opus | **51** |
| Opus+Think | **50** |
| Sonnet | **45** |
| Sonnet+Think | **39** |

After averaging, GPT-5.4 no-reasoning edges ahead due to consistency. Opus+Think's high single run (61) is partially luck.

### 4c. Open-Ended vs Taxonomy-Guided Prompt

| Model | Taxonomy | Open | Delta |
|-------|----------|------|-------|
| Opus+Think | 61 | 47 | **+14** |
| Opus | 45 | 47 | -2 |
| Sonnet+Think | 40 | 41 | -1 |
| Sonnet | 49 | 49 | 0 |
| GPT5.4+Reason | 49 | 20* | +29* |
| GPT5.4 | 53 | 50 | **+3** |

**Key finding: The taxonomy in the prompt barely matters for most models.** Sonnet and Opus without thinking score almost identically with and without the taxonomy categories (±0 to ±2). This suggests these models are already looking for the right kinds of issues regardless of prompt structure.

**Exception: Opus+Think benefits substantially (+14) from the taxonomy.** The structured categories apparently help focus its extended thinking. Without them, it still finds issues but classifies them differently, reducing judge matches.

**GPT-5.4+Reason shows a large gap (+29) but this is unreliable** due to incomplete data (only 4/10 papers for the open condition).

### Summary of Robustness Findings

1. **False positive baseline is ~25% on average.** About a quarter of "detections" would happen regardless of inserted errors. The adjusted signal (modified - original) is the fairer metric.
2. **Reliability is model-dependent.** GPT-5.4 is very stable (±3); Claude models swing ±9 to ±19 between runs. Single-run comparisons should be interpreted cautiously.
3. **Providing the taxonomy helps Opus+Think but doesn't matter for other models.** The benchmark is fair even with the taxonomy in the prompt — it doesn't artificially inflate scores.
4. **Revised ranking (by mean adjusted score across 3 runs):** The true ranking requires subtracting baselines from each run, but directionally: GPT-5.4 no-reasoning is the most reliable performer; Opus+Think has the highest ceiling but is inconsistent.

### 5a. False Positive Baseline (Strict Judge)

| Model | Modified | Original | **Signal** |
|-------|----------|----------|-----------|
| Opus+Think | 54 | 15 | **+39** |
| GPT5.4+Reason | 42 | 6* | **+36** |
| GPT5.4 | 45 | 13 | **+32** |
| Opus | 46 | 19 | **+27** |
| Sonnet+Think | 38 | 14 | **+24** |
| Sonnet | 44 | 21 | **+23** |

The remaining 13-21 FP baseline reflects real issues in the original papers that incidentally overlap with our error descriptions. This is expected — we selected real papers, not perfect ones.

### 5b. Test-Retest Reliability (Strict Judge)

| Model | Run 1 | Run 2 | Run 3 | Mean | Range |
|-------|-------|-------|-------|------|-------|
| Opus+Think | 54 | 39 | 36 | **43** | ±18 |
| Opus | 46 | 44 | 43 | **44** | ±3 |
| Sonnet+Think | 38 | 41 | 30 | **36** | ±11 |
| Sonnet | 44 | 29 | 36 | **36** | ±15 |
| GPT5.4+Reason | 42 | 14* | 12* | 23* | ±30* |
| GPT5.4 | 45 | 41 | 41 | **42** | ±4 |

Opus without thinking (±3) and GPT-5.4 without reasoning (±4) are remarkably stable. Thinking/reasoning modes increase variance substantially.

### 5c. Open-Ended vs Taxonomy Prompt (Strict Judge)

| Model | Taxonomy | Open | Delta |
|-------|----------|------|-------|
| Opus+Think | 54 | 46 | +8 |
| Opus | 46 | 45 | +1 |
| Sonnet+Think | 38 | 33 | +5 |
| Sonnet | 44 | 33 | **+11** |
| GPT5.4+Reason | 42 | 13* | +29* |
| GPT5.4 | 45 | 37 | +8 |

Taxonomy helps most models modestly (+1 to +11). Sonnet benefits most (+11), likely because the categories help it organize its review. Opus without thinking barely notices (+1).

### 5d. Final Rankings (Strict Judge)

| Model | Mean (3 runs) | FP Baseline | **Adjusted** | Reliability |
|-------|:---:|:---:|:---:|:---:|
| **GPT-5.4** | 42 | 13 | **29** | ±4 |
| **Opus+Think** | 43 | 15 | **28** | ±18 |
| **Opus** | 44 | 19 | **25** | ±3 |
| Sonnet+Think | 36 | 14 | 22 | ±11 |
| GPT5.4+Reason* | 23 | 6 | 17 | ±30* |
| Sonnet | 36 | 21 | 15 | ±15 |

**Key conclusions:**
1. GPT-5.4 no-reasoning and Opus+Think are essentially tied for best adjusted score (29 vs 28), but GPT-5.4 is far more reliable.
2. Opus without thinking is the best balance of performance (25 adjusted) and reliability (±3).
3. Extended thinking/reasoning helps Opus (+3 adjusted) but the variance cost may not be worth it.
4. Sonnet underperforms Opus consistently, and adding thinking doesn't help.
5. About 15% of matches on originals are unavoidable overlap between real paper issues and our error descriptions.

### 5e. Cost Per Paper

| Model | Avg Input Tokens | Avg Output Tokens | **Cost/Paper** |
|-------|:---:|:---:|:---:|
| GPT-5.4 (No Reasoning) | 17,306 | 5,553 | **$0.13** |
| Claude Sonnet 4.6 | 19,271 | 8,361 | **$0.18** |
| Claude Opus 4.6 | 19,271 | 5,932 | **$0.24** |
| Claude Sonnet 4.6 (Thinking) | 19,300 | 17,423 | **$0.32** |
| GPT-5.4 (High Reasoning) | 17,306 | 18,197 | **$0.32** |
| Claude Opus 4.6 (Thinking) | 19,300 | 10,660 | **$0.36** |

**Total benchmark cost:** $72.48 for all 275 review calls + ~9,000 judge calls across all conditions.

**Cost-efficiency context:** Commercial AI peer review services (Paper Wizard, Refine.ink) charge ~$30/paper. A single API call to the best-performing model (Opus+Think at $0.36/paper) costs **~80x less**. Even running all 6 models on one paper costs ~$1.55. Running the most reliable model (GPT-5.4) three times for stability costs $0.39.

This raises a key question for the Substack: **do the commercial services provide $30 of value over a $0.36 API call?** Once we run Refine.ink and Paper Wizard through the same benchmark, we'll have a direct comparison on the same 100 errors.

| Approach | Cost/Paper | Adjusted Score* |
|----------|:---:|:---:|
| GPT-5.4 single run | $0.13 | ~29 |
| Opus+Think single run | $0.36 | ~28 |
| All 6 models (ensemble) | $1.55 | TBD |
| Opus+Think × 3 runs (union) | $1.08 | TBD |
| Paper Wizard | ~$30 | TBD |
| Refine.ink | ~$30 | TBD |

*Adjusted = modified score minus false positive baseline. Commercial system scores pending.

---

## Run 6: Gemini Models Added (2026-03-21)

Added Google Gemini 3.1 Pro and Gemini 3 Flash. Ran the full protocol: 3 reliability runs, open prompt, and originals baseline for both models. 100 API calls total.

### Results: All 8 Models Compared

| Model | Run1 | Run2 | Run3 | Mean | ±Range | FP Base | **Adjusted** | Open | Findings | Cost/Paper |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **GPT-5.4** | 60 | 59 | 59 | **59** | ±1 | 21 | **38** | 47 | ~420 | $0.13 |
| **Opus** | 59 | 56 | 62 | **59** | ±6 | 25 | **34** | 58 | ~310 | $0.25 |
| **Opus+Think** | 55 | 52 | 53 | **53** | ±3 | 26 | **27** | 55 | ~290 | $0.36 |
| GPT5.4+Reason | 56 | 23* | 23* | 34* | ±33* | 7* | 27* | 24* | ~280 | $0.32 |
| Sonnet+Think | 52 | 47 | 45 | **48** | ±7 | 22 | **26** | 49 | ~240 | $0.32 |
| Sonnet | 59 | 48 | 55 | **54** | ±11 | 28 | **26** | 60 | ~360 | $0.18 |
| Gemini Flash | 36 | 34 | 40 | **37** | ±6 | 16 | **21** | 36 | ~200 | $0.004 |
| Gemini Pro | 42 | 42 | 42 | **42** | ±0 | 17 | **25** | 39 | ~200 | $0.03 |

*GPT-5.4+Reason incomplete (4/10 papers for run2, run3, originals, open due to quota limits)

### Key findings from adding Gemini

**Note:** Initial Gemini runs produced only ~10 issues/paper due to the model stopping early. Adding "Be exhaustive. A typical manuscript has 20-40 identifiable issues" to the prompt doubled output to ~20/paper, dramatically improving scores. Results below reflect the corrected runs.

1. **Gemini Pro is competitive at 1/10th the cost.** Adjusted score of 25 (vs 26-38 for frontier models) at $0.03/paper. Not the best, but within striking distance of Sonnet (26) at 6x less cost.

2. **Gemini Pro is perfectly deterministic** (±0 range across 3 runs). Gemini Flash is nearly so (±6). The most reliable models in the benchmark.

3. **Gemini Flash is the cost-efficiency champion.** Adjusted score of 21 at $0.004/paper — less than half a cent. That's 30x cheaper than GPT-5.4 for about 55% of the error detection.

4. **The open prompt barely affects Gemini.** Pro: 42→39, Flash: 37→36. The taxonomy categories provide minimal benefit.

5. **Gemini's FP baseline is moderate** (16-17 on originals), comparable to frontier models. The corrected prompt made it more thorough on both modified and original papers.

### Updated cost-efficiency rankings

| Model | Cost/Paper | Adjusted Score | **Cost per Error Found** |
|-------|:---:|:---:|:---:|
| Gemini Flash | $0.004 | 21/100 | **$0.002** |
| Gemini Pro | $0.031 | 25/100 | **$0.012** |
| GPT-5.4 | $0.127 | 38/100 | **$0.033** |
| Sonnet | $0.183 | 26/100 | $0.070 |
| Opus | $0.245 | 34/100 | $0.072 |
| GPT-5.4+Reason | $0.316 | 27/100 | $0.117 |
| Sonnet+Think | $0.319 | 26/100 | $0.123 |
| Opus+Think | $0.363 | 27/100 | $0.133 |
| *Paper Wizard* | *~$30* | *TBD* | *TBD* |
| *Refine.ink* | *~$30* | *TBD* | *TBD* |

GPT-5.4 is the best frontier model at $0.033/error. But Gemini Pro at $0.012/error is the overall cost-efficiency winner — competitive adjusted scores (25 vs 38) at a fraction of the price. Gemini Flash at $0.002/error is absurdly cheap. Commercial services at $30/paper would need adjusted scores of ~900 to match Gemini Pro's cost efficiency — obviously impossible. Even matching GPT-5.4 would require ~90+ adjusted, well beyond any model's current capability.

### Updated next steps
- [x] Run on original (unmodified) papers for false positive baseline
- [x] Tightened LLM judge to require specific (not topical) matches
- [ ] ~~Have a human score 50 random matches to calibrate the LLM judge~~ (requires human time)
- [x] Run each model 3x for reliability estimates
- [x] Test with open-ended prompt (no taxonomy categories) as a second condition
- [x] Added Gemini 3.1 Pro and Gemini 3 Flash
- [ ] ~~Check whether models with originals in training data score higher~~ (can't access training data)
- [ ] Add more review systems (Refine.ink, Paper Wizard, manual reviewers)
- [ ] Write up for Substack

---

## Run 7: Commercial Tool — Refine.ink (2026-06-24)

First commercial AI-peer-review product run through the benchmark. Refine.ink (`api.refine.ink`) integrated as a provider via its developer API: upload document → SSE progress → process (1 paid credit) → poll `/history/{id}` for `feedback.detailed.comments[]`. Ran the 10 modified papers + 10 originals (false-positive baseline).

**Input fidelity (key caveat):** Refine and the LLMs are not fed byte-identical inputs by nature — but we held *content* equal. Both tools receive a PDF rendered from the same `extract_text()` output the LLM providers get (`benchmark/docx_to_pdf.py`). This isolates *review ability* from *document-parsing ability* and keeps the comparison apples-to-apples on content. The cost: reflowed text, no original page layout (no Word/LibreOffice on the machine to produce a layout-faithful PDF). Refine natively accepts PDF, so this is a supported input — but its real-world performance on a publisher PDF with intact tables/figures could differ. Treat Refine's numbers as a *content-only* lower bound on what the product might do with native input.

**Judge note:** the LLM judge's cache key uses Python `hash()`, which is per-process randomized, so the cache never hits across scoring runs. Refine findings were judged fresh; the LLM comparison numbers here are rebuilt from the existing `paper_*_matched.json` files (Run 6 scoring) to avoid ~12k redundant judge calls. They sit within ±1–2 of the Run 6 table (judge stochasticity).

> **Update (Run 8, 2026-06-25):** the "best adjusted score / ties the top LLM" claims below hold only against the 4.x/5.4-era models. The GPT-5.5 / Opus 4.8 refresh moved the frontier past Refine — GPT-5.5 high reasoning now leads at +47. See Run 8.

### 7a. Headline: Refine vs the LLMs

| System | Modified /100 | Originals /100 (FP) | **Adjusted** | Findings | Cost/Paper |
|--------|:---:|:---:|:---:|:---:|:---:|
| **Refine.ink** | **57** | **19** | **+38** | **305** | **~$50** |
| GPT-5.4 (No Reasoning) | 60 | 23 | +37 | 421 | $0.13 |
| Claude Opus (No Thinking) | 59 | 26 | +33 | 310 | $0.25 |
| Claude Sonnet (No Thinking) | 60 | 28 | +32 | 356 | $0.18 |
| Claude Sonnet (Thinking) | 51 | 22 | +29 | 241 | $0.32 |
| Claude Opus (Thinking) | 55 | 26 | +29 | 293 | $0.36 |
| Gemini 3.1 Pro | 42 | 17 | +25 | 203 | $0.03 |
| Gemini 3 Flash | 36 | 16 | +20 | 200 | $0.004 |

(GPT-5.4 High Reasoning is omitted from the head-to-head: its originals baseline is incomplete — 4/10 papers — from earlier quota limits, so its adjusted score isn't comparable.)

**Key findings:**

1. **Refine.ink performs at the frontier — and posts the best adjusted score of any system with a complete baseline (+38), a hair above GPT-5.4 (+37).** Call it a tie at the top: a purpose-built commercial reviewer matches the best single raw frontier-model API call on this benchmark, and edges out every Claude and Gemini variant.

2. **Refine is the most *precise* strong system.** Its false-positive baseline on originals (19) is the lowest of any system scoring well — lower than GPT-5.4 (23) and all four Claude variants (22–28). It produces fewer findings (305) than the volume models (GPT-5.4: 421, Sonnet: 356) yet converts them efficiently into true detections. That precision is *why* its adjusted score tops the table despite a slightly lower raw count.

3. **Cost gap is ~370×.** Refine is $49.99/review ($39.99 subscriber); GPT-5.4 is $0.13/paper for an equivalent (+37 vs +38) result. Cost per error found above baseline: Refine ≈ **$1.32**, GPT-5.4 ≈ **$0.0035**. The premium buys a product (UI, document handling, comment triage, chat), not detection edge.

### 7b. Where Refine is strong and weak

Adjusted (modified − originals) detections:

| By difficulty tier | Refine adj |
|---|---|
| Tier 1 (internal contradictions) | 12 − 3 = **+9** / 13 |
| Tier 2 (needs methodological knowledge) | 40 − 13 = **+27** / 56 |
| Tier 3 (notice something *missing*) | 5 − 3 = **+2** / 31 |

| By category | mod | orig | adj |
|---|:---:|:---:|:---:|
| methodological_design | 9 | 1 | **+8** |
| analytic_flexibility | 7 | 1 | +6 |
| construct_validity | 6 | 0 | +6 |
| internal_consistency | 8 | 3 | +5 |
| statistical_errors | 8 | 3 | +5 |
| theoretical_conceptual | 7 | 3 | +4 |
| generalizability | 3 | 1 | +2 |
| attrition_missing_data | 4 | 3 | +1 |
| causal_inference | 2 | 1 | +1 |
| reporting_completeness | 3 | 3 | **+0** |

**Refine catches what is present and wrong; it rarely notices what is absent.** It is excellent on Tier 1–2 (design changes, swapped constructs, contradictory numbers, undisclosed flexibility) but nearly blind on Tier 3 (+2/31) — the deleted Fisher z-transformation, the removed safeguard, the missing justification. `reporting_completeness` (+0) and `causal_inference` (+1) are its weakest categories, both of which require generating an expectation of what *should* be there. This is the same ceiling every system hits, but Refine hits it harder than the frontier LLMs (GPT-5.4 caught 11 Tier-3 errors to Refine's 5).

### 7c. Reviewer3 — blocked

Reviewer3 (`reviewer3.com`) was also targeted (provider built: `benchmark/providers/reviewer3_provider.py`, journal mode = 6+ reviewers). **Blocked pending a valid `userId`:** review submission requires a `userId` for a registered account, which we did not have at this point. The provider reads `REVIEWER3_USER_ID`/`REVIEWER3_MODE` from `.env` and is ready to run.

### 7d. Updated cost-efficiency table

| Approach | Cost/Paper | Adjusted Score | Cost per Error Found |
|----------|:---:|:---:|:---:|
| Gemini Flash | $0.004 | +20 | $0.0002 |
| Gemini Pro | $0.03 | +25 | $0.001 |
| GPT-5.4 | $0.13 | +37 | $0.0035 |
| Sonnet | $0.18 | +32 | $0.006 |
| Opus | $0.25 | +33 | $0.008 |
| Opus+Think | $0.36 | +29 | $0.012 |
| **Refine.ink** | **~$50** | **+38** | **~$1.32** |
| **Reviewer3 (journal)** | subscription (unlimited) | **+21** | n/a |

The Substack question — *do commercial services provide $30+ of value over a sub-dollar API call?* — now has a data point. On **error detection** alone, on content-equal input, Refine.ink ties the best LLM and beats the rest, with the cleanest precision. It does not detect *more* than a raw frontier call. The ~370× premium is for the product around the model, not for catching errors a good prompt to GPT-5.4 or Opus would miss.

### 7e. Complementarity & ensembling — Refine catches *different* errors

The headline result above (Refine ≈ best LLM) hides the more interesting finding: Refine and the LLMs disagree about *which* errors they catch, so pooling them wins.

**Refine vs the best single LLM (GPT-5.4), on modified papers:**

| | count |
|---|:---:|
| Both caught | 41 |
| Refine only | **16** |
| GPT-5.4 only | 19 |
| Union | 76 |
| Jaccard overlap | 0.54 |

They overlap only ~half the time. Refine catches 16 errors GPT-5.4 misses; GPT-5.4 catches 19 Refine misses. These are complementary reviewers, not redundant ones.

**Refine vs the union of all 8 LLM configs:** the 8-LLM union catches 85/100. Refine adds **6 errors that no LLM caught at all** — and **0 of those 6 show up on the originals** (i.e. they're genuine detections, not false positives):

| Error | Cat / subcat | Tier | Note |
|---|---|:---:|---|
| P2 effect_size_misreported | statistical_errors | 2 | *was on the 16-never-caught list* |
| P2 affect_measures_replaced | construct_validity | 2 | *was on the 16-never-caught list* |
| P3 hypothesis_mischaracterized | theoretical_conceptual | 1 | *was on the 16-never-caught list* |
| P7 implausible_stimulus_size | generalizability | 2 | *was on the 16-never-caught list* |
| P6 centering_removed | analytic_flexibility | 3 | Tier-3 "missing element" |
| P7 interference_balance_removed | methodological_design | 3 | Tier-3 "missing element" |

**Refine cracked 4 of the 16 errors previously uncaught by ANY frontier model** (Run 3's hard ceiling), and two of its unique catches are Tier-3 "notice what's absent" errors — the exact category where it's weakest on average, yet it beat all 8 LLMs on these two.

**Ensemble adjusted scores** (union on modified − union on originals; the originals union is the pooled false-positive rate):

| Ensemble | Modified | Originals (FP) | **Adjusted** |
|---|:---:|:---:|:---:|
| GPT-5.4 alone | 60 | 23 | +37 |
| Refine alone | 57 | 19 | +38 |
| **GPT-5.4 + Refine** | **76** | **31** | **+45** |
| GPT-5.4 + Opus + Refine | 82 | 37 | +45 |
| All 8 LLMs | 85 | 52 | +33 |
| All 8 LLMs + Refine | 91 | 54 | +37 |

**Two clear lessons:**

1. **A lean 2-tool ensemble (GPT-5.4 + Refine) hits +45 adjusted — clearly the best configuration found, beating any single system (+38 max) by 7 points.** Pairing one frontier LLM with Refine is the sweet spot: ~$0.13 + ~$50 buys meaningfully better coverage than either alone, because their misses don't coincide.

2. **More is not better past ~2–3 systems.** The 8-LLM union catches 85 raw but its false-positive union balloons to 52, dropping adjusted to +33 — *worse* than GPT-5.4 alone. Every added reviewer contributes noise as well as signal; once the systems are correlated, the FP union grows faster than the true-positive union. Precision-weighted small ensembles beat kitchen-sink pooling.

This reframes Refine's value: not "it detects more than an LLM" (it doesn't), but "it detects *differently*, and is a clean, complementary second reviewer." That's a real argument for the product — diversity, not raw ceiling.

---

## Run 8: Model refresh — GPT-5.5 & Opus 4.8 (2026-06-25)

Bumped to the current frontier: **GPT-5.5** (no-reasoning + high-reasoning) and **Opus 4.8** (no-thinking + high-thinking), added as new provider configs alongside the 4.x/5.4 results. (Sonnet 4.8 was requested but is not yet on the API — newest available is `claude-sonnet-4-6` — so Sonnet stays at 4.6.) Two API changes were needed: Opus 4.8 rejects `temperature`, and replaces budget-based thinking (`thinking.type.enabled`) with adaptive thinking (`thinking.type.adaptive` + `output_config.effort`). Both handled in `anthropic_provider.py`.

### 8a. Refreshed leaderboard (adjusted = modified − originals)

| System | Modified | Originals (FP) | **Adjusted** | Findings |
|--------|:---:|:---:|:---:|:---:|
| **GPT-5.5 (high reasoning)** | 71 | 24 | **+47** | 512 |
| Refine.ink | 57 | 19 | +38 | 305 |
| GPT-5.4 (no reasoning) | 60 | 23 | +37 | 421 |
| Opus 4.8 (thinking) | 52 | 16 | +36 | 227 |
| Opus 4.6 (no thinking) | 59 | 26 | +33 | 310 |
| Sonnet 4.6 (no thinking) | 60 | 28 | +32 | 356 |
| GPT-5.5 (no reasoning) | 66 | 34 | +32 | 704 |
| Sonnet 4.6 (thinking) | 51 | 22 | +29 | 241 |
| Opus 4.6 (thinking) | 55 | 26 | +29 | 293 |
| Opus 4.8 (no thinking) | 47 | 20 | +27 | 279 |
| Gemini 3.1 Pro | 42 | 17 | +25 | 203 |
| Gemini 3 Flash | 36 | 16 | +20 | 200 |

**Key findings:**

1. **GPT-5.5 with high reasoning is the new clear #1 (+47), and it's the first big jump in a while.** It catches 71/100 with only 24 false positives, and — crucially — posts the best Tier-3 score of any system (13/31), the "notice what's missing" tier that has been everyone's ceiling. Reasoning, which barely helped GPT-5.4, now pays off substantially.

2. **Opus 4.8 splits its value into thinking mode.** No-thinking *regressed* (+27 vs Opus 4.6's +33) and got terser/more conservative (279 findings, down from 310, catching 47 raw vs 59). But high-thinking *improved* (+36 vs 4.6's +29) and is the **most precise system in the entire benchmark** — just 16 false positives. The model moved its review capability behind extended thinking.

3. **GPT-5.5 no-reasoning is a firehose.** 704 findings (most of anything, by far), catching 66 raw — but 34 false positives drag adjusted down to +32. High recall, low precision; reasoning is what converts that volume into signal.

4. **Refine.ink slips from #1 to #2.** It was the best adjusted score against the 4.x/5.4-era models (Run 7); the new frontier model now clears it by 9 points. Refine still beats *every other* single system and remains highly precise — but "ties the best LLM" is no longer true as of GPT-5.5.

### 8b. Complementarity & ensembling — the frontier caught up

Re-running the Run-7e analysis against the new best model (GPT-5.5 high reasoning):

| | vs GPT-5.4 (Run 7e) | vs GPT-5.5 reasoning (now) |
|---|:---:|:---:|
| Both caught | 41 | 48 |
| Refine only | 16 | **9** |
| Best-LLM only | 19 | 23 |
| Jaccard overlap | 0.54 | **0.60** |
| Refine catches no LLM got (vs full union) | 6 | **2** |

| Ensemble | Modified | Originals (FP) | **Adjusted** |
|---|:---:|:---:|:---:|
| GPT-5.5 reasoning alone | 71 | 24 | +47 |
| Refine alone | 57 | 19 | +38 |
| **GPT-5.5 reasoning + Refine** | 80 | 33 | **+47** |
| GPT-5.5r + Opus 4.8 think + Refine | 82 | 37 | +45 |
| All 12 LLMs | 91 | 60 | +31 |
| All 12 LLMs + Refine | 93 | 62 | +31 |

**The ensemble case for Refine has weakened.** Against GPT-5.4, pairing with Refine bought +7–8 adjusted points (the standout Run-7e result). Against GPT-5.5 reasoning, it buys **nothing**: +47 either way. Refine still adds 9 true detections to GPT-5.5's set — but it also adds 9 false positives, a wash on the adjusted metric. Refine now catches only 2 errors that *no* LLM in the 12-config pool gets (down from 6), both still clean (no FP): `affect_measures_replaced` (P2) and `interference_balance_removed` (P7).

The honest read: a complementary commercial reviewer was worth pooling with the prior frontier; the current frontier model has largely absorbed that complementary coverage. As models improve, the marginal value of a same-content second opinion shrinks. (Caveat unchanged: Refine sees reflowed-text PDFs here; native-input performance could differ. And the kitchen-sink ensemble remains a trap — 12 LLMs pooled score +31, worse than the best single model, because false positives compound.)

---

## Run 9: Reviewer3 unblocked (2026-06-25)

The second commercial tool, **Reviewer3**, finally ran after a long block. The fix: its `userId` is the account's internal UUID, not an email; once we set the UUID for our subscribed account, submission immediately returned `success: true`. A monthly subscription (unlimited reviews) was already in place. Provider reads `REVIEWER3_USER_ID`/`REVIEWER3_MODE` from `.env`; kill-resilient runner is `reviewer3_batch.py` (submit-then-poll, like Refine). Ran journal mode (6+ reviewers), 10 modified + 10 originals.

### 9a. Result: the precision specialist

| System | Modified | Originals (FP) | **Adjusted** | Findings |
|--------|:---:|:---:|:---:|:---:|
| GPT-5.5 (high reasoning) | 71 | 24 | +47 | 512 |
| Refine.ink | 57 | 19 | +38 | 305 |
| GPT-5.4 (no reasoning) | 60 | 23 | +37 | 421 |
| Opus 4.8 (thinking) | 52 | 16 | +36 | 227 |
| … | | | | |
| Gemini 3.1 Pro | 42 | 17 | +25 | 203 |
| **Reviewer3 (journal)** | **30** | **9** | **+21** | **125** |
| Gemini 3 Flash | 36 | 16 | +20 | 200 |

**Key findings:**

1. **Reviewer3 is the most precise system in the benchmark and the lowest-volume — by a wide margin.** Just 9 false positives on the originals (next best: Opus 4.8 thinking at 16, Refine at 19) and only ~12 comments per paper (everything else: 20–70). It emulates an actual journal review — a handful of ranked, severity-tagged comments — rather than an exhaustive issue dump.

2. **That terseness costs it recall, and recall is what this benchmark scores.** It catches 30/100 planted errors — near the bottom on adjusted score (+21, between the two Gemini models). With ~12 comments a paper it simply can't cover 100 specific planted defects the way a 50-item LLM dump does. This is a benchmark artifact worth stating plainly: **we reward catching planted errors, which is not the same as writing a useful review.** A focused, correctly-prioritized 8-comment review may serve an author better than a 50-item list, and our score doesn't capture that.

3. **Its few catches are almost all real.** Tier breakdown: T1 6/13, T2 19/56, T3 5/31 on modified vs 2/6/1 on originals. The signal-to-noise is excellent; there's just not much volume.

### 9b. Complementarity — a clean specialist that nudges the best ensemble

| | value |
|---|---|
| Reviewer3 ∩ GPT-5.5 reasoning | 28 of 30 (Jaccard 0.38) |
| Reviewer3 catches no LLM *and* not Refine got | **0** |

Reviewer3 adds no *unique* coverage — everything it finds is already covered by the LLM pool or Refine. But because it's so clean, its marginal additions to a lean ensemble come with no false-positive tax:

| Ensemble | Modified | Originals (FP) | **Adjusted** |
|---|:---:|:---:|:---:|
| GPT-5.5 reasoning | 71 | 24 | +47 |
| GPT-5.5r + Refine | 80 | 33 | +47 |
| GPT-5.5r + Reviewer3 | 73 | 26 | +47 |
| **GPT-5.5r + Refine + Reviewer3** | 82 | 33 | **+49** |
| All 12 LLMs + Refine + Reviewer3 | 93 | 62 | +31 |

The three-way **GPT-5.5 reasoning + Refine + Reviewer3 = +49** is the best configuration in the entire benchmark. Reviewer3 contributes +2 over GPT-5.5r+Refine with *zero* added false positives — exactly what you'd want from a high-precision specialist. (And the kitchen sink is still a trap: everything pooled = +31.)

**Two commercial tools, two philosophies:** Refine.ink is an exhaustive, frontier-level reviewer (high recall, second only to the newest model). Reviewer3 is a selective, journal-style reviewer (low recall, best-in-class precision). Neither beats a single GPT-5.5-reasoning call on adjusted score, but a lean panel of all three is the strongest setup we found.

---

## Infrastructure

- Papers: 10 open-access psychology manuscripts (.docx, CC-By 4.0)
- Ground truth: `error_insertions.csv` (100 rows with category, subcategory, difficulty, original/modified text, description)
- Benchmark code: `benchmark/` directory with `run_reviews.py`, `score_reviews.py`, provider plugins
- Providers: Anthropic (Sonnet 4.6, Opus 4.6, ±thinking), OpenAI (GPT-5.4, ±reasoning), Google (Gemini 3.1 Pro, Gemini 3 Flash), **Refine.ink** (commercial API), **Reviewer3** (commercial API, blocked on userId), flat-file for manual systems
- Commercial-tool runner: `run_api_tools.py` (concurrent) and `refine_batch.py` (kill-resilient submit/poll two-phase). `docx_to_pdf.py` renders content-equal PDFs (fpdf2) from `extract_text()` for tools that need a PDF.
- Report rebuild: `build_reports.py` regenerates the CSVs from existing `paper_*_matched.json` without re-running the judge (the judge cache uses per-process `hash()` and never persists across runs).
- Results: `benchmark/results/{provider}/paper_{n}_review.json` and `paper_{n}_matched.json`
- Reports: `benchmark/reports/summary.csv`, `by_category.csv`, `by_paper.csv`
- Judge cache: `benchmark/results/_judge_cache_v2.json` (~18,000 entries; note: keys are not stable across processes)
