#!/usr/bin/env python3
"""Run AI peer review models against modified papers."""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from config import MODIFIED_PAPERS_DIR, ORIGINAL_PAPERS_DIR, RESULTS_DIR, ENV_FILE
from docx_extract import extract_text
from prompts import REVIEW_PROMPT, OPEN_REVIEW_PROMPT
from providers import get_all_providers, get_provider_by_name
from providers.base import ReviewProvider

console = Console()


async def run_single(provider: ReviewProvider, paper_id: int, paper_text: str,
                     prompt: str, skip_existing: bool) -> dict | None:
    if skip_existing and provider.has_result(paper_id):
        console.print(f"  [dim]Paper {paper_id}: cached[/dim]")
        return None

    console.print(f"  Paper {paper_id}: running...", end="")
    start = time.time()
    try:
        result = await provider.review_paper(paper_id, paper_text, prompt)
        elapsed = time.time() - start

        out_path = provider.result_path(paper_id)
        out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

        n = len(result.issues)
        tokens = result.token_usage or {}
        console.print(f" [green]{n} issues[/green] ({elapsed:.0f}s, {tokens.get('input_tokens', '?')}+{tokens.get('output_tokens', '?')} tokens)")
        return {"paper_id": paper_id, "issues": n, "elapsed": elapsed}

    except Exception as e:
        elapsed = time.time() - start
        console.print(f" [red]ERROR: {e}[/red] ({elapsed:.0f}s)")
        return {"paper_id": paper_id, "error": str(e)}


async def run_provider(provider: ReviewProvider, paper_ids: list[int],
                       paper_texts: dict[int, str], prompt: str, skip_existing: bool):
    console.print(f"\n[bold]{provider.display_name}[/bold] ({provider.name})")
    for pid in paper_ids:
        await run_single(provider, pid, paper_texts[pid], prompt, skip_existing)


def make_suffixed_provider(provider: ReviewProvider, suffix: str) -> ReviewProvider:
    """Clone a provider with a name suffix for variant runs."""
    import copy
    p = copy.copy(provider)
    p.name = f"{provider.name}_{suffix}"
    p.display_name = f"{provider.display_name} [{suffix}]"
    return p


def main():
    parser = argparse.ArgumentParser(description="Run AI peer review benchmark")
    parser.add_argument("--provider", "-p", help="Run only this provider (by name)")
    parser.add_argument("--paper", "-n", type=int, help="Run only this paper (1-10)")
    parser.add_argument("--skip-existing", "-s", action="store_true")
    parser.add_argument("--list", "-l", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    # Variant flags
    parser.add_argument("--originals", action="store_true",
                        help="Run on original (unmodified) papers for false positive baseline")
    parser.add_argument("--run-id", type=int, default=None,
                        help="Run ID for reliability testing (2, 3, etc.)")
    parser.add_argument("--open-prompt", action="store_true",
                        help="Use open-ended prompt without taxonomy categories")
    args = parser.parse_args()

    load_dotenv(ENV_FILE)

    if args.list:
        for p in get_all_providers():
            console.print(f"  {p.name:<40s} {p.display_name}")
        return

    # Determine paper source
    paper_dir = ORIGINAL_PAPERS_DIR if args.originals else MODIFIED_PAPERS_DIR
    prompt = OPEN_REVIEW_PROMPT if args.open_prompt else REVIEW_PROMPT

    # Build suffix for result directory naming
    suffix_parts = []
    if args.originals:
        suffix_parts.append("originals")
    if args.open_prompt:
        suffix_parts.append("open")
    if args.run_id:
        suffix_parts.append(f"run{args.run_id}")
    suffix = "_".join(suffix_parts) if suffix_parts else None

    # Load papers
    paper_ids = [args.paper] if args.paper else list(range(1, 11))
    paper_texts: dict[int, str] = {}
    for pid in paper_ids:
        path = paper_dir / f"{pid}.docx"
        if not path.exists():
            console.print(f"[red]Missing: {path}[/red]")
            sys.exit(1)
        paper_texts[pid] = extract_text(path)
    console.print(f"Loaded {len(paper_ids)} papers from {'originals' if args.originals else 'modified'}")
    console.print(f"Prompt: {'open-ended' if args.open_prompt else 'taxonomy-guided'}")
    if suffix:
        console.print(f"Suffix: {suffix}")

    # Get providers, apply suffix
    if args.provider:
        base_providers = [get_provider_by_name(args.provider)]
    else:
        base_providers = get_all_providers()

    providers = [make_suffixed_provider(p, suffix) if suffix else p for p in base_providers]

    if args.dry_run:
        console.print("\n[bold]Would run:[/bold]")
        for p in providers:
            for pid in paper_ids:
                skip = "SKIP" if args.skip_existing and p.has_result(pid) else "RUN"
                console.print(f"  {p.name} / paper {pid}: {skip}")
        return

    async def go():
        for provider in providers:
            await run_provider(provider, paper_ids, paper_texts, prompt, args.skip_existing)

    asyncio.run(go())
    console.print("\n[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
