#!/usr/bin/env python3
"""Complementarity + ensembling analysis from existing matched.json files.

Does Refine catch DIFFERENT errors than the LLMs, and does pooling help?
We build a per-error detection matrix (100 errors x providers) on both modified
and original papers, then report overlap, unique contribution, and ensemble
scores (union) adjusted for the false-positive union on originals.
"""

import json
from pathlib import Path

from config import RESULTS_DIR

# Canonical "main run" configs (one dir each) + their originals baseline.
# Includes the 2026-06 model refresh (GPT-5.5, Opus 4.8).
LLMS = [
    "openai_gpt55_no_reasoning",
    "openai_gpt55_high_reasoning",
    "openai_gpt54_no_reasoning",
    "openai_gpt54_high_reasoning",
    "claude_opus48_no_thinking",
    "claude_opus48_high_thinking",
    "claude_opus_no_thinking",
    "claude_opus_high_thinking",
    "claude_sonnet_no_thinking",
    "claude_sonnet_high_thinking",
    "gemini_pro",
    "gemini_flash",
]
BEST_LLM = "openai_gpt55_high_reasoning"  # top adjusted single config
REFINE = "refine_ink"
REVIEWER3 = "reviewer3"


def detection_set(provider: str) -> set:
    """Set of (paper, error_idx) this provider matched."""
    d = RESULTS_DIR / provider
    caught = set()
    for mf in d.glob("paper_*_matched.json"):
        pid = int(mf.stem.split("_")[1])
        for i, m in enumerate(json.loads(mf.read_text())):
            if m.get("matched"):
                caught.add((pid, i))
    return caught


def union(providers, suffix="") -> set:
    s = set()
    for p in providers:
        s |= detection_set(p + suffix)
    return s


def main():
    refine_mod = detection_set(REFINE)
    refine_orig = detection_set(REFINE + "_originals")
    gpt = detection_set(BEST_LLM)

    print("=" * 64)
    print("REFINE vs BEST SINGLE LLM (GPT-5.5 high reasoning) — modified")
    print("=" * 64)
    both = refine_mod & gpt
    refine_only = refine_mod - gpt
    gpt_only = gpt - refine_mod
    print(f"  Refine caught:        {len(refine_mod)}")
    print(f"  Best LLM caught:      {len(gpt)}")
    print(f"  Both:                 {len(both)}")
    print(f"  Refine only:          {len(refine_only)}")
    print(f"  Best LLM only:        {len(gpt_only)}")
    print(f"  Union:                {len(refine_mod | gpt)}")
    print(f"  Jaccard overlap:      {len(both)/len(refine_mod | gpt):.2f}")

    print("\n" + "=" * 64)
    print("REFINE vs UNION-OF-ALL-12-LLMs — modified")
    print("=" * 64)
    llm_union = union(LLMS)
    refine_unique = refine_mod - llm_union
    print(f"  Any-LLM union caught: {len(llm_union)}")
    print(f"  Refine caught:        {len(refine_mod)}")
    print(f"  Refine ∩ LLM-union:   {len(refine_mod & llm_union)}")
    print(f"  Refine catches that NO LLM caught: {len(refine_unique)}")
    if refine_unique:
        print("    -> " + ", ".join(f"P{p}#{i}" for p, i in sorted(refine_unique)))

    print("\n" + "=" * 64)
    print("ENSEMBLE ADJUSTED SCORES (union_modified - union_originals)")
    print("=" * 64)

    def report(label, provs):
        m = union(provs)
        o = union([p + "_originals" for p in provs])
        print(f"  {label:34s} mod={len(m):>3}  orig={len(o):>3}  adj={len(m)-len(o):>+3}")
        return m, o

    report("Best LLM alone (GPT-5.5 reas.)", [BEST_LLM])
    report("Refine alone", [REFINE])
    report("Reviewer3 alone", [REVIEWER3])
    report("Best LLM + Refine", [BEST_LLM, REFINE])
    report("Best LLM + Reviewer3", [BEST_LLM, REVIEWER3])
    report("Best LLM + Refine + Reviewer3", [BEST_LLM, REFINE, REVIEWER3])
    report("All LLMs", LLMS)
    report("All LLMs + Refine + Reviewer3", LLMS + [REFINE, REVIEWER3])

    print("\n" + "=" * 64)
    print("WHAT REFINE ADDS TO THE LLM ENSEMBLE (adjusted view)")
    print("=" * 64)
    llm_o = union([p + "_originals" for p in LLMS])
    ens = union(LLMS)
    ens_r = ens | refine_mod
    ens_r_o = llm_o | refine_orig
    print(f"  LLM ensemble:         mod={len(ens)} orig={len(llm_o)} adj={len(ens)-len(llm_o):+d}")
    print(f"  LLM ensemble + Refine:mod={len(ens_r)} orig={len(ens_r_o)} adj={len(ens_r)-len(ens_r_o):+d}")
    print(f"  Net errors Refine adds to union (mod): {len(refine_unique)}")
    print(f"  Of those, also flagged on originals (likely FP): "
          f"{len(refine_unique & refine_orig)}")


if __name__ == "__main__":
    main()
