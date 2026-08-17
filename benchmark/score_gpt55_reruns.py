#!/usr/bin/env python3
"""Score the additional GPT-5.5 runs (run2 / run3, both reasoning modes).

Uses score_reviews.score_provider() and matching.py unmodified, so the match
decisions are identical to a normal `score_reviews.py -p <provider>` run. Two
things are redirected so nothing already in the repo is rewritten:

  * The judge cache is pointed at a temp file. results/_judge_cache_v2.json is
    checked in, and scoring would otherwise append to it. (It never hits across
    runs anyway — the key uses per-process hash(); see build_reports.py.)

  * Summaries are written to reports/gpt55_reruns*.csv rather than through
    score_reviews.write_reports(), which opens reports/summary.csv,
    by_category.csv and by_paper.csv in "w" mode and would truncate them to
    only the providers scored in this invocation.

Writes: paper_N_matched.json in each run directory, plus the two CSVs.

    uv run score_gpt55_reruns.py
"""

import asyncio
import csv
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from config import ENV_FILE, REPORTS_DIR

load_dotenv(ENV_FILE)

import matching  # noqa: E402  (import order matters: patch before first use)

matching._judge_cache_path = Path(tempfile.gettempdir()) / "gpt55_reruns_judge_cache.json"

from matching import load_ground_truth  # noqa: E402
from score_reviews import score_provider  # noqa: E402

PROVIDERS = [
    "openai_gpt55_high_reasoning_run2",
    "openai_gpt55_high_reasoning_run3",
    "openai_gpt55_no_reasoning_run2",
    "openai_gpt55_no_reasoning_run3",
]


async def main() -> int:
    ground_truth = load_ground_truth()
    categories = sorted({e.category for e in ground_truth})
    summary_rows: list[list] = []
    category_rows: list[list] = []

    for name in PROVIDERS:
        scores = await score_provider(name)
        if not scores:
            print(f"  {name}: no results found — run run_reviews.py --run-id first")
            return 1

        caught = sum(s.errors_detected for s in scores)
        findings = sum(s.total_findings for s in scores)
        tiers = {1: 0, 2: 0, 3: 0}
        per_category = dict.fromkeys(categories, 0)
        for score in scores:
            for match in score.matches:
                if match.matched:
                    tiers[match.ground_truth.difficulty] += 1
                    per_category[match.ground_truth.category] += 1

        summary_rows.append([name, caught, 100, tiers[1], tiers[2], tiers[3], findings])
        category_rows.append([name] + [per_category[c] for c in categories])
        print(f"  {name:38} {caught:3}/100   ({findings} findings, {len(scores)} papers)", flush=True)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "gpt55_reruns.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["provider", "total_detected", "total_100", "tier1_13", "tier2_63", "tier3_24", "total_findings"]
        )
        writer.writerows(summary_rows)

    with open(REPORTS_DIR / "gpt55_reruns_by_category.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["provider"] + categories)
        writer.writerows(category_rows)

    print(f"\n  wrote {REPORTS_DIR}/gpt55_reruns.csv")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
