# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **research project** (not a software codebase) for benchmarking AI peer review systems. The goal is to evaluate how well AI tools can detect methodological and statistical issues in scientific manuscripts.

## Key Components

- **refine_taxonomy_v4.md** — The central artifact: a 10-category, 62-subcategory taxonomy (the 100 planted errors cover 50 of the subcategories) of detectable issues in scientific papers, designed for integration with the Evidence.Guide replication prediction model. Includes a JSON schema for structured output and replication-risk rankings (CRITICAL → LOW).
- **candidate_papers_for_error_insertion.md** — 10 open-access psychology papers (with OSF-hosted .docx files) selected to cover all 10 taxonomy categories. Each paper is mapped to specific categories/subcategories it's best suited for.
- **original papers/** — Downloaded .docx manuscripts from OSF (1.docx through 10.docx), unmodified ground truth.
- **modified papers/** — Same manuscripts with 10 inserted errors each (100 total), covering all 10 taxonomy categories and 50 unique subcategories. Tables and formatting preserved.
- **error_insertions.csv** — Tracking file with paper, category, subcategory, original text, modified text, and description for all 100 errors.
- **error_insertion_plan.md** — Coverage matrix, per-paper inventory, and evaluation protocol.

## Architecture & Workflow

The taxonomy feeds into two systems:
- **Refine.ink** — AI reviewer that detects paper-only issues (no external data needed)
- **Evidence.Guide** — Replication prediction model that combines Refine.ink output with statistical checks (statcheck, GRIM/DEBIT, p-curve, effect sizes, preregistration fidelity)

The benchmarking pipeline: select papers → insert known errors matching taxonomy subcategories → run AI review → compare detected issues against ground truth.

## Key Design Principles

1. All taxonomy categories must be detectable from reading the manuscript alone
2. No overlap with Evidence.Guide's automated checks (statcheck, GRIM, etc.)
3. Categories are weighted by empirical evidence linking them to replication failure
4. Honest framing: categories describe observables, not inferred intent

## Working with the Taxonomy

The taxonomy JSON schema (`RefineInkQualityAssessment`) defines the structured output format with: summary scores (0-1), issue counts by category and risk level, boolean replication risk indicators, derived features for model input, and detailed issue arrays with quotes and locations.

## Status

- Taxonomy v4 complete. Open questions remain about detection granularity, score calibration, batch consistency, and which features to use for model training.
- Benchmark dataset complete: 100 errors inserted across 10 papers.
- **8 LLM configurations benchmarked** (Claude Opus/Sonnet ±thinking, GPT-5.4 ±reasoning, Gemini 3.1 Pro/Flash) with modified + originals + 3 reliability runs + open-prompt variants. See `benchmark/ANALYSIS_LOG.md` (Runs 1–6) and `benchmark/EVAL_WRITEUP.md`.
- **Refine.ink benchmarked (2026-06-24, Run 7):** 57/100 modified, 19/100 false-positive baseline, **+38 adjusted** — was the best adjusted score against the 4.x/5.4-era models, lowest false-positive rate of any strong system, at ~$50/paper vs $0.13–0.40 for an LLM call. Strong on Tier 1–2 errors, weak on "notice what's missing" (Tier 3). Integrated via `benchmark/providers/refine_provider.py`.
- **Model refresh (2026-06-25, Run 8):** added GPT-5.5 (±reasoning) and Opus 4.8 (±thinking); Sonnet 4.8 not yet on the API (newest is 4.6). **GPT-5.5 high reasoning is the new #1 at +47 adjusted** (71/100, best Tier-3 score 13/31), pushing Refine to #2. Opus 4.8 thinking is the most precise system (16 FP, +36); Opus 4.8 no-thinking regressed (+27). Note: Opus 4.8 dropped `temperature` and uses adaptive thinking (`output_config.effort`).
- **Complementarity finding (Run 7e/8b):** Refine catches *different* errors than the LLMs. Against GPT-5.4 the lean ensemble GPT-5.4 + Refine = +45 (best config found, beat any single system). Against GPT-5.5 reasoning the pairing no longer helps (+47 either way) — the new frontier absorbed Refine's complementary coverage. Naive all-LLM pooling is worse (+31) — false positives compound. See `benchmark/analyze_ensemble.py`.
- **Reviewer3 benchmarked (2026-06-25, Run 9):** runs against a registered account's `userId` (set in `.env`). Journal mode: **30/100 modified, 9/100 false positives, +21 adjusted** — near the bottom on recall but the **most precise and lowest-volume system in the benchmark** (~12 comments/paper; behaves like a real selective journal reviewer). Adds +2 to the best ensemble with zero false positives. Best config overall: **GPT-5.5 reasoning + Refine + Reviewer3 = +49**. Runner: `reviewer3_batch.py`.
- Next: investigate the Tier-3 ceiling (no system reliably detects deleted/missing elements); benchmark caveat — it scores recall on planted errors, which undervalues Reviewer3's selective journal-style reviews.

## Substack writeup (`benchmark/EVAL_WRITEUP.md`)

- The published draft **dropped the false-positive/adjusted-score framing entirely** (the originals "false positives" were mostly the models catching real issues in the papers, so subtracting them is wrong). It now reports **raw catches /100 + findings count** (findings count = the precision lens), and is framed around the *method* (build a planted-error benchmark per field) rather than a tool verdict. The analytical climax is **"the bottleneck is verification"** (tier collapse: systems catch present-and-wrong, miss absent; generation is cheap, verification isn't).
- **Every quantitative claim in the writeup is reproduced by `benchmark/writeup_numbers.py`** (reads existing `matched.json`/`review.json`, no judge re-run; report runs under `__main__`, helpers/`LEADERBOARD` are importable). Run `uv run writeup_numbers.py` after any re-scoring to catch drift. Includes leaderboard, cost/error, Pareto frontier, tier table, greedy coverage curve, best-complement, never-caught. Not reproduced there (documented in its footer): $/paper costs (hardcoded from token logs — $/error is derived from them), reliability ranges (need run2/run3 dirs), the 20 hand-checked judge decisions.
- **Taxonomy-in-prompt fairness check (resolved):** ran the open-ended prompt (`--open-prompt`) on the two current frontier models. **GPT-5.5 high reas 71→66 (−5), Opus 4.8 think 52→51 (−1)** — vs GPT-5.4's −13. GPT-5.5's lead survives (66 still tops the table) and its Tier-3 score (13/24) is identical with/without categories; the whole −5 is Tier 2. So the category hint is a modest OpenAI-family effect, not a frontier-wide one. Caveat lives in the writeup's "Keeping the commercial comparison fair" section; deltas reproduced in `writeup_numbers.py`.
- **Cost/coverage scatter:** `benchmark/plot_cost_coverage.py` → `reports/cost_coverage.png` (imports `caught`/`LEADERBOARD` from `writeup_numbers`; needs **matplotlib**, now a dep). Frontier = Flash, Gemini Pro, GPT-5.4 no-reas, GPT-5.5 high; Refine is the far outlier at ~$8.77/error (~200× the frontier).
- Greedy coverage curve (union, no adjusted): 1 sys=71 → +Refine=80 → +LLM=85 → 5 sys=90 → 8 sys=93 ceiling; 7 errors caught by no system (all absent-type). `analyze_ensemble.py` is now **stale** (it still uses the dropped adjusted/originals metric) — use `writeup_numbers.py` instead. `categorize_findings.py` (empirical error-type distribution) backs a section that was **cut** from the writeup but is kept for a possible companion piece.

## Commercial-tool benchmark mechanics

- Keys live in `benchmark/.env` (gitignored): `REFINE_API_KEY`, `REVIEWER3_API_KEY` (+ `REVIEWER3_USER_ID`, `REVIEWER3_MODE` when available).
- Both tools are fed PDFs rendered from the same `extract_text()` the LLMs get (`benchmark/docx_to_pdf.py`, fpdf2) — content-equal comparison; caveat is reflowed text, no original layout.
- Run with `uv run run_api_tools.py -p refine_ink --skip-existing` (concurrent) or the kill-resilient `uv run refine_batch.py` (submit-then-poll). Score with `score_reviews.py`; rebuild report CSVs with `build_reports.py` (the judge cache does not persist across runs — keys use per-process `hash()`).
