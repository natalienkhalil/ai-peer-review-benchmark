"""Match model findings to ground truth errors using LLM judge with prompt caching."""

import asyncio
import csv
import json
from pathlib import Path

import anthropic

from config import GROUND_TRUTH_CSV, RESULTS_DIR
from models import GroundTruthError, IssueFinding, MatchResult

_judge_cache_path = RESULTS_DIR / "_judge_cache_v2.json"
_judge_cache: dict[str, str] = {}


def _load_judge_cache():
    global _judge_cache
    if _judge_cache_path.exists():
        _judge_cache = json.loads(_judge_cache_path.read_text())


def _save_judge_cache():
    _judge_cache_path.parent.mkdir(parents=True, exist_ok=True)
    _judge_cache_path.write_text(json.dumps(_judge_cache))


def _cache_key(paper_id: int, finding_desc: str, finding_quote: str) -> str:
    return f"v2|{paper_id}|{hash((finding_desc[:150], finding_quote[:150]))}"


def _build_errors_block(errors: list[GroundTruthError]) -> str:
    """Build the cacheable block listing all ground truth errors for a paper."""
    lines = []
    for i, e in enumerate(errors, 1):
        lines.append(f"""ERROR {i}:
- Category: {e.category} / {e.subcategory}
- What was changed: {e.description}
- Original text (before modification): {e.original_snippet[:400]}
- Modified text (what's in the paper now): {e.modified_snippet[:400]}
""")
    return "\n".join(lines)


JUDGE_SYSTEM = """You are a strict matching judge. You will be given a list of known errors that were inserted into a scientific paper, and a single reviewer finding. Your job is to determine if the reviewer's finding identifies the SAME SPECIFIC issue as any of the known errors.

IMPORTANT: A match requires that the reviewer identified the SPECIFIC problem that was introduced — not just that they commented on the same topic or section. For example:
- If the error was "changed between-subjects to within-subjects", the reviewer must flag the within-subjects design as wrong. Simply discussing the experimental design is NOT a match.
- If the error was "removed the robustness check", the reviewer must note that the robustness check is MISSING. Commenting on robustness in general is NOT a match.
- If the error was "added exclusion criteria", the reviewer must flag those specific exclusions as problematic. Discussing exclusion criteria in general is NOT a match.
- If the error was "reversed the effect direction", the reviewer must notice the direction is inconsistent. Discussing effect sizes in general is NOT a match.

The reviewer doesn't need to use the same words, but they must have noticed the same specific defect — not merely discussed the same topic area.

Respond with ONLY the error number (1-10) if there's a clear match, or "none" if the finding merely discusses a related topic without identifying the specific inserted problem. When in doubt, say "none"."""


async def judge_finding(
    client: anthropic.AsyncAnthropic,
    paper_id: int,
    errors_block: str,
    finding: IssueFinding,
) -> str | None:
    """Ask LLM which error (if any) this finding matches. Returns error index (0-based) or None."""
    key = _cache_key(paper_id, finding.description, finding.quote)
    if key in _judge_cache:
        return _judge_cache[key]

    user_content = [
        {
            "type": "text",
            "text": f"Here are the 10 known errors inserted into this paper:\n\n{errors_block}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"""Now evaluate this reviewer finding:

FINDING:
- Category: {finding.category}
- Subcategory: {finding.subcategory or 'not specified'}
- Description: {finding.description[:600]}
- Quote from paper: {finding.quote[:400] if finding.quote else 'none provided'}
- Location: {finding.location or 'not specified'}

Which error number (1-10) does this finding match, if any? Answer with ONLY the number or "none".""",
        },
    ]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            temperature=0,
            system=JUDGE_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
        )
        answer = response.content[0].text.strip().lower()

        # Parse response
        if answer == "none" or "none" in answer:
            result = "none"
        else:
            # Extract number
            import re
            nums = re.findall(r'\b(\d+)\b', answer)
            if nums and 1 <= int(nums[0]) <= 10:
                result = nums[0]
            else:
                result = "none"
    except Exception as e:
        result = "none"

    _judge_cache[key] = result
    _save_judge_cache()
    return result


def load_ground_truth() -> list[GroundTruthError]:
    errors = []
    with open(GROUND_TRUTH_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            errors.append(GroundTruthError(
                paper=int(row["paper"]),
                category=row["category"],
                subcategory=row["subcategory"],
                difficulty=int(row["difficulty"]),
                difficulty_rationale=row["difficulty_rationale"],
                original_snippet=row["original_snippet"],
                modified_snippet=row["modified_snippet"],
                description=row["description"],
            ))
    return errors


def get_paper_errors(paper_id: int) -> list[GroundTruthError]:
    return [e for e in load_ground_truth() if e.paper == paper_id]


async def match_findings_to_errors_async(
    findings: list[IssueFinding],
    errors: list[GroundTruthError],
) -> list[MatchResult]:
    """Match findings to errors using LLM judge with prompt caching."""
    _load_judge_cache()

    if not findings:
        return [MatchResult(ground_truth=e, matched=False) for e in errors]

    paper_id = errors[0].paper
    errors_block = _build_errors_block(errors)
    client = anthropic.AsyncAnthropic()

    # Judge each finding (prompt cache kicks in after first call)
    # Process in batches to respect rate limits
    batch_size = 30
    finding_matches: list[tuple[int, str | None]] = []  # (finding_idx, error_num_or_none)

    for batch_start in range(0, len(findings), batch_size):
        batch = findings[batch_start:batch_start + batch_size]
        tasks = [
            judge_finding(client, paper_id, errors_block, f)
            for f in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for k, result in enumerate(results):
            fidx = batch_start + k
            if isinstance(result, str) and result != "none":
                finding_matches.append((fidx, result))
            else:
                finding_matches.append((fidx, None))

    # Build one-to-one assignment: first finding to claim each error wins
    error_claimed: dict[int, tuple[int, IssueFinding]] = {}  # error_idx -> (finding_idx, finding)
    for fidx, error_num in finding_matches:
        if error_num is None:
            continue
        eidx = int(error_num) - 1  # Convert 1-based to 0-based
        if 0 <= eidx < len(errors):
            if eidx not in error_claimed:
                error_claimed[eidx] = (fidx, findings[fidx])

    # Build results
    results = []
    for i, error in enumerate(errors):
        if i in error_claimed:
            fidx, finding = error_claimed[i]
            results.append(MatchResult(
                ground_truth=error,
                matched=True,
                match_confidence=1.0,
                matched_finding=finding,
                match_method="llm_judge_cached",
            ))
        else:
            results.append(MatchResult(
                ground_truth=error,
                matched=False,
                match_confidence=0.0,
            ))

    _save_judge_cache()
    return results
