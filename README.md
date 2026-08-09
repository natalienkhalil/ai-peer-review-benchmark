# AI Peer Review Benchmark

A planted-error benchmark for AI peer review systems. We hand-inserted 100 known methodological and statistical errors into 10 open-access psychology papers, then measured how many each AI reviewer catches.

> **⚠️ The files in `modified papers/` are deliberately corrupted.** Each is a real published manuscript into which 10 errors were intentionally inserted. They exist only as benchmark inputs, are watermarked as such, and must not be cited or mistaken for the originals (which are in `original papers/`, unmodified).

## What's here

- **`refine_taxonomy_v4.md`** — a 10-category, 62-subcategory taxonomy of detectable issues in scientific papers, weighted by empirical evidence linking each category to replication failure. The planted errors cover 50 of the subcategories.
- **`error_insertions.csv`** — the ground truth: all 100 errors with original text, modified text, category, and description.
- **`error_insertion_plan.md`** — design philosophy, coverage matrix, and per-paper error inventory.
- **`candidate_papers_for_error_insertion.md`** — the 10 source papers, with OSF links and licenses.
- **`original papers/`, `modified papers/`** — the manuscripts (see warning above).
- **`benchmark/`** — the harness: providers for Anthropic/OpenAI/Google plus the commercial tools Refine.ink and Reviewer3, scoring via fuzzy matching + LLM judge, report builders, and all results.
- **`benchmark/EVAL_WRITEUP.md`** — the full writeup. **`benchmark/ANALYSIS_LOG.md`** — the working log of how the analysis actually unfolded, kept so the process is inspectable.

## Headline results

The best single system (GPT-5.5, high reasoning) catches 71/100. The union of all 14 tested configurations reaches 93/100. Detection splits sharply by error type: systems reliably catch errors that are *present and wrong* (a flipped effect direction, a statistic that contradicts its conclusion) and miss what is *absent* (a deleted exclusion criterion, a dropped disclosure). All 7 errors that no system caught are omissions. Every number in the writeup is reproduced by `benchmark/writeup_numbers.py`.

## Running it

```
cd benchmark
uv run writeup_numbers.py        # reproduce all writeup numbers from stored results
uv run run_reviews.py --help     # run a provider against the papers (needs API keys)
```

API keys go in `benchmark/.env` (gitignored): `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, and for the commercial tools `REFINE_API_KEY`, `REVIEWER3_API_KEY` + `REVIEWER3_USER_ID`.

The text extractor (`docx_extract.py`) strips the watermark notice from the modified papers, so re-runs see exactly the text the benchmarked systems saw.

## A note on contamination

The ground truth is public, so these papers and errors may appear in future model training data. Scores for models trained after this release (August 2026) should be interpreted accordingly — this benchmark is a demonstration of the method (which is portable to any field with open-access papers) rather than a permanent leaderboard.

## Licensing

The code and documentation are MIT-licensed (see `LICENSE`). The manuscripts in `original papers/` and `modified papers/` are CC-BY 4.0 works by their original authors; see `candidate_papers_for_error_insertion.md` for sources and attribution. The modified versions are derivative works distributed under the same license, with changes marked (watermark in each file, full change list in `error_insertions.csv`).
