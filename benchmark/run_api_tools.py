#!/usr/bin/env python3
"""Concurrent runner for the slow API-based review tools (Refine.ink, Reviewer3).

These providers spend minutes per paper waiting on async server-side review jobs,
so we fan papers out concurrently (asyncio.gather + a semaphore) rather than the
sequential loop in run_reviews.py. Results are written to the same result_path
JSON layout, so score_reviews.py picks them up unchanged.

Usage:
  uv run run_api_tools.py -p refine_ink --skip-existing
  uv run run_api_tools.py -p refine_ink --originals --skip-existing
  uv run run_api_tools.py -p reviewer3 --skip-existing
"""

import argparse
import asyncio
import time

from dotenv import load_dotenv
from rich.console import Console

from config import MODIFIED_PAPERS_DIR, ORIGINAL_PAPERS_DIR, ENV_FILE
from docx_extract import extract_text
from prompts import REVIEW_PROMPT
from providers import get_provider_by_name
from run_reviews import make_suffixed_provider

console = Console()


async def run_one(provider, pid, text, skip_existing, attempts=3):
    if skip_existing and provider.has_result(pid):
        console.print(f"  [dim]paper {pid}: cached[/dim]")
        return
    for attempt in range(1, attempts + 1):
        start = time.time()
        try:
            res = await provider.review_paper(pid, text, REVIEW_PROMPT)
            provider.result_path(pid).write_text(res.model_dump_json(indent=2), encoding="utf-8")
            console.print(f"  paper {pid}: [green]{len(res.issues)} issues[/green] ({time.time()-start:.0f}s)")
            return
        except Exception as e:
            console.print(f"  paper {pid}: [red]ERROR {e}[/red] ({time.time()-start:.0f}s, attempt {attempt}/{attempts})")
            if attempt < attempts:
                await asyncio.sleep(10)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", "-p", required=True)
    ap.add_argument("--originals", action="store_true")
    ap.add_argument("--concurrency", "-c", type=int, default=5)
    ap.add_argument("--skip-existing", "-s", action="store_true")
    ap.add_argument("--papers", help="comma-separated paper ids, default 1-10")
    args = ap.parse_args()

    load_dotenv(ENV_FILE)

    paper_dir = ORIGINAL_PAPERS_DIR if args.originals else MODIFIED_PAPERS_DIR
    ids = [int(x) for x in args.papers.split(",")] if args.papers else list(range(1, 11))

    base = get_provider_by_name(args.provider)
    provider = make_suffixed_provider(base, "originals") if args.originals else base

    texts = {pid: extract_text(paper_dir / f"{pid}.docx") for pid in ids}
    console.print(f"[bold]{provider.display_name}[/bold] ({provider.name}) — "
                  f"{'originals' if args.originals else 'modified'}, {len(ids)} papers, "
                  f"concurrency={args.concurrency}")

    sem = asyncio.Semaphore(args.concurrency)

    async def guarded(pid):
        async with sem:
            await run_one(provider, pid, texts[pid], args.skip_existing)

    await asyncio.gather(*(guarded(pid) for pid in ids))
    console.print("[bold green]Done.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
