#!/usr/bin/env python3
"""Score AI review results against ground truth errors."""

import argparse
import asyncio
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from config import RESULTS_DIR, REPORTS_DIR, ENV_FILE
from matching import load_ground_truth, get_paper_errors, match_findings_to_errors_async
from models import IssueFinding, MatchResult, PaperScore, ReviewOutput

console = Console()


def load_review(path: Path) -> ReviewOutput:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReviewOutput(**data)


async def score_provider(provider_name: str) -> list[PaperScore]:
    provider_dir = RESULTS_DIR / provider_name
    if not provider_dir.exists():
        return []

    scores = []
    for paper_id in range(1, 11):
        review_path = provider_dir / f"paper_{paper_id}_review.json"
        if not review_path.exists():
            continue

        review = load_review(review_path)
        errors = get_paper_errors(paper_id)
        matches = await match_findings_to_errors_async(review.issues, errors)

        detected = sum(1 for m in matches if m.matched)
        score = PaperScore(
            paper_id=paper_id,
            provider_name=provider_name,
            errors_detected=detected,
            errors_missed=len(errors) - detected,
            total_findings=len(review.issues),
            matches=matches,
        )
        scores.append(score)

        # Save matched results
        matched_path = provider_dir / f"paper_{paper_id}_matched.json"
        matched_path.write_text(
            json.dumps([m.model_dump() for m in matches], indent=2, default=str),
            encoding="utf-8",
        )

    return scores


def print_summary(all_scores: dict[str, list[PaperScore]]):
    gt = load_ground_truth()

    # Summary table
    table = Table(title="Benchmark Results: Errors Detected / 100")
    table.add_column("Provider", style="bold")
    table.add_column("Total /100", justify="right")
    table.add_column("T1 /13", justify="right", style="green")
    table.add_column("T2 /63", justify="right", style="yellow")
    table.add_column("T3 /24", justify="right", style="red")
    table.add_column("Findings", justify="right", style="dim")

    for provider_name, scores in sorted(all_scores.items()):
        total = sum(s.errors_detected for s in scores)
        total_findings = sum(s.total_findings for s in scores)

        # By difficulty tier
        tier_detected = {1: 0, 2: 0, 3: 0}
        for s in scores:
            for m in s.matches:
                if m.matched:
                    tier_detected[m.ground_truth.difficulty] += 1

        table.add_row(
            provider_name,
            f"{total}",
            f"{tier_detected[1]}",
            f"{tier_detected[2]}",
            f"{tier_detected[3]}",
            f"{total_findings}",
        )

    console.print(table)

    # By category
    cat_table = Table(title="Detection by Category")
    cat_table.add_column("Provider", style="bold")
    categories = sorted(set(e.category for e in gt))
    for cat in categories:
        cat_table.add_column(cat[:12], justify="right")

    for provider_name, scores in sorted(all_scores.items()):
        cat_detected = defaultdict(int)
        for s in scores:
            for m in s.matches:
                if m.matched:
                    cat_detected[m.ground_truth.category] += 1
        row = [provider_name] + [str(cat_detected[c]) for c in categories]
        cat_table.add_row(*row)

    console.print(cat_table)

    # By paper
    paper_table = Table(title="Detection by Paper")
    paper_table.add_column("Provider", style="bold")
    for pid in range(1, 11):
        paper_table.add_column(f"P{pid}", justify="right")
    paper_table.add_column("Total", justify="right", style="bold")

    for provider_name, scores in sorted(all_scores.items()):
        paper_scores = {s.paper_id: s.errors_detected for s in scores}
        row = [provider_name] + [str(paper_scores.get(pid, "-")) for pid in range(1, 11)]
        row.append(str(sum(paper_scores.values())))
        paper_table.add_row(*row)

    console.print(paper_table)


def write_reports(all_scores: dict[str, list[PaperScore]]):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    gt = load_ground_truth()

    # Summary CSV
    with open(REPORTS_DIR / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provider", "total_detected", "total_100", "tier1_13", "tier2_63", "tier3_24", "total_findings"])
        for provider_name, scores in sorted(all_scores.items()):
            total = sum(s.errors_detected for s in scores)
            total_findings = sum(s.total_findings for s in scores)
            tier = {1: 0, 2: 0, 3: 0}
            for s in scores:
                for m in s.matches:
                    if m.matched:
                        tier[m.ground_truth.difficulty] += 1
            w.writerow([provider_name, total, 100, tier[1], tier[2], tier[3], total_findings])

    # By category CSV
    categories = sorted(set(e.category for e in gt))
    with open(REPORTS_DIR / "by_category.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provider"] + categories)
        for provider_name, scores in sorted(all_scores.items()):
            cat_detected = defaultdict(int)
            for s in scores:
                for m in s.matches:
                    if m.matched:
                        cat_detected[m.ground_truth.category] += 1
            w.writerow([provider_name] + [cat_detected[c] for c in categories])

    # By paper CSV
    with open(REPORTS_DIR / "by_paper.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provider"] + [f"paper_{pid}" for pid in range(1, 11)] + ["total"])
        for provider_name, scores in sorted(all_scores.items()):
            ps = {s.paper_id: s.errors_detected for s in scores}
            w.writerow([provider_name] + [ps.get(pid, 0) for pid in range(1, 11)] + [sum(ps.values())])

    console.print(f"\n[dim]Reports written to {REPORTS_DIR}/[/dim]")


async def async_main():
    parser = argparse.ArgumentParser(description="Score review results against ground truth")
    parser.add_argument("--provider", "-p", help="Score only this provider")
    args = parser.parse_args()

    load_dotenv(ENV_FILE)

    # Find all providers with results
    if args.provider:
        provider_names = [args.provider]
    else:
        provider_names = [
            d.name for d in RESULTS_DIR.iterdir()
            if d.is_dir() and any(d.glob("paper_*_review.json"))
        ]

    if not provider_names:
        console.print("[red]No results found. Run `uv run run_reviews.py` first.[/red]")
        sys.exit(1)

    console.print(f"Scoring {len(provider_names)} provider(s) with LLM judge...\n")

    all_scores: dict[str, list[PaperScore]] = {}
    for name in sorted(provider_names):
        console.print(f"  {name}...", end="")
        scores = await score_provider(name)
        if scores:
            all_scores[name] = scores
            total = sum(s.errors_detected for s in scores)
            console.print(f" [bold]{total}/100[/bold]")
        else:
            console.print(" no results")

    print_summary(all_scores)
    write_reports(all_scores)


if __name__ == "__main__":
    asyncio.run(async_main())
