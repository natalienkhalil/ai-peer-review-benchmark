#!/usr/bin/env python3
"""Reproduce every quantitative claim in EVAL_WRITEUP.md from the saved results.

Reads only the existing `results/<provider>/paper_*_{review,matched}.json` files
(no judge re-run, no API calls), so it's fast and deterministic. Each block prints
numbers labeled with the writeup section they appear in. Run:

    uv run writeup_numbers.py

If a printed number ever drifts from the writeup, one of them is wrong — fix it.
"""

import csv
import json
from pathlib import Path

from config import RESULTS_DIR, GROUND_TRUTH_CSV

# --- the systems shown on the leaderboard (display, results-dir, $/paper) ---
LEADERBOARD = [
    ("GPT-5.5 high reasoning", "openai_gpt55_high_reasoning", 0.30),
    ("GPT-5.5 no reasoning",   "openai_gpt55_no_reasoning",   0.30),
    ("GPT-5.4 no reasoning",   "openai_gpt54_no_reasoning",   0.13),
    ("Sonnet 4.6",             "claude_sonnet_no_thinking",   0.18),
    ("Opus 4.6",               "claude_opus_no_thinking",     0.25),
    ("Refine.ink",             "refine_ink",                  50.0),
    ("GPT-5.4 high reasoning", "openai_gpt54_high_reasoning", 0.32),
    ("Opus 4.8 thinking",      "claude_opus48_high_thinking", 0.40),
    ("Gemini 3.1 Pro",         "gemini_pro",                  0.03),
    ("Gemini 3 Flash",         "gemini_flash",                0.004),
    ("Reviewer3",              "reviewer3",                   None),
]


def main_configs() -> list[str]:
    """Every primary run (excludes baselines, repeats, and prompt variants)."""
    skip = ("_originals", "_open", "_run2", "_run3")
    out = []
    for d in sorted(RESULTS_DIR.iterdir()):
        if d.is_dir() and not d.name.endswith(skip) and any(d.glob("paper_*_matched.json")):
            out.append(d.name)
    return out


def detection_set(prov: str) -> set:
    """{(paper, error_index)} this provider matched."""
    s = set()
    for mp in (RESULTS_DIR / prov).glob("paper_*_matched.json"):
        pid = int(mp.stem.split("_")[1])
        for i, m in enumerate(json.loads(mp.read_text())):
            if m.get("matched"):
                s.add((pid, i))
    return s


def caught(prov: str) -> int:
    return len(detection_set(prov))


def findings(prov: str) -> int:
    n = 0
    for rp in (RESULTS_DIR / prov).glob("paper_*_review.json"):
        n += len(json.loads(rp.read_text()).get("issues", []))
    return n


def by_category(prov: str) -> dict:
    d = {}
    for mp in (RESULTS_DIR / prov).glob("paper_*_matched.json"):
        for m in json.loads(mp.read_text()):
            if m.get("matched"):
                c = m["ground_truth"]["category"]
                d[c] = d.get(c, 0) + 1
    return d


def by_tier(prov: str) -> dict:
    d = {1: 0, 2: 0, 3: 0}
    for mp in (RESULTS_DIR / prov).glob("paper_*_matched.json"):
        for m in json.loads(mp.read_text()):
            if m.get("matched"):
                d[m["ground_truth"]["difficulty"]] += 1
    return d


def hr(t):
    print("\n" + "=" * 72 + f"\n{t}\n" + "=" * 72)


# ===================================================================== #
def cost_per_error(cost_per_paper: float, caught_n: int) -> float:
    """USD per planted error caught = (10 papers x $/paper) / errors caught."""
    return cost_per_paper * 10 / caught_n


def report():
  gt = list(csv.DictReader(open(GROUND_TRUTH_CSV, encoding="utf-8")))
  TIER_TOTALS = {1: 0, 2: 0, 3: 0}
  for r in gt:
    TIER_TOTALS[int(r["difficulty"])] += 1

  hr("DATASET (Methods)")
  print(f"errors: {len(gt)}  | per paper: {len(gt)//10}  | "
      f"categories: {len({r['category'] for r in gt})}")
  print(f"tiers  T1/T2/T3 = {TIER_TOTALS[1]}/{TIER_TOTALS[2]}/{TIER_TOTALS[3]}   (writeup: 13/63/24)")

  hr("LEADERBOARD (Results) — Caught /100 | Findings | $/paper | $/error")
  for name, prov, cost in LEADERBOARD:
    k = caught(prov)
    cp = f"${cost:g}" if cost is not None else "subscription"
    ce = f"${cost_per_error(cost, k):.3f}" if cost is not None else "n/a"
    print(f"  {name:24} {k:>3} {findings(prov):>6}   {cp:>12} {ce:>9}")

  hr("REASONING DELTAS (Results: 'reasoning is what did it')")
  print(f"  GPT-5.4: no-reasoning {caught('openai_gpt54_no_reasoning')}  ->  "
        f"high-reasoning {caught('openai_gpt54_high_reasoning')}   (writeup: 60 -> 56)")
  print(f"  GPT-5.5: no-reasoning {caught('openai_gpt55_no_reasoning')}  ->  "
        f"high-reasoning {caught('openai_gpt55_high_reasoning')}   (writeup: 66 -> 71)")

  hr("OPEN-PROMPT DELTAS (Fairness: taxonomy hint vs no categories)")
  for prov, label in [("openai_gpt55_high_reasoning", "GPT-5.5 high reas (leader)"),
                      ("claude_opus48_high_thinking", "Opus 4.8 thinking"),
                      ("openai_gpt54_no_reasoning", "GPT-5.4 no reas")]:
    op = prov + "_open"
    if (RESULTS_DIR / op).exists():
      print(f"  {label:26} taxonomy={caught(prov)} (T3 {by_tier(prov)[3]})  "
            f"open={caught(op)} (T3 {by_tier(op)[3]})  delta={caught(prov)-caught(op):+d}")
  print("  writeup: GPT-5.5 71->66 (-5, T3 13 unchanged); Opus 4.8 52->51 (-1); GPT-5.4 60->47 (-13)")

  hr("COST/ERROR + PARETO FRONTIER (Results leaderboard + scatter)")
  pts = [(name, cost, caught(prov)) for name, prov, cost in LEADERBOARD if cost is not None]
  def on_frontier(p):
    return not any(q[1] <= p[1] and q[2] >= p[2] and (q[1] < p[1] or q[2] > p[2])
                   for q in pts if q is not p)
  for name, cost, k in sorted(pts, key=lambda x: x[1]):
    print(f"  {name:24} ${cost:<6g} caught={k:>3}  $/err={cost_per_error(cost,k):.3f}"
          f"{'   <- FRONTIER' if on_frontier((name,cost,k)) else ''}")
  print("  writeup: frontier = Flash, Gemini Pro, GPT-5.4 no-reas, GPT-5.5 high; Refine $8.77/err, far off")

  MAIN = main_configs()
  hr(f"TIER DETECTION (Verification) — {len(MAIN)} main configs")
  union = set()
  for p in MAIN:
    union |= detection_set(p)
  diff_by_pe = {}
  for pid in range(1, 11):
    arr = json.loads((RESULTS_DIR / MAIN[0] / f"paper_{pid}_matched.json").read_text())
    for i, m in enumerate(arr):
      diff_by_pe[(pid, i)] = m["ground_truth"]["difficulty"]
  union_tier = {1: 0, 2: 0, 3: 0}
  for pe in union:
    union_tier[diff_by_pe[pe]] += 1
  sysset = [p for _, p, _ in LEADERBOARD]
  avg = {t: sum(by_tier(p)[t] for p in sysset) / len(sysset) for t in (1, 2, 3)}
  print(f"{'tier':6}{'total':>7}{'avg single (lb systems)':>26}{'union of all main':>20}")
  for t in (1, 2, 3):
    tot = TIER_TOTALS[t]
    print(f"  T{t}  {tot:>5}{avg[t]/tot*100:>22.0f}%{union_tier[t]/tot*100:>18.0f}%")
  print("  writeup table: avg 73/57/33,  union 100/95/83")

  hr("COVERAGE CEILING + NEVER-CAUGHT (Verification)")
  print(f"  union of all {len(MAIN)} systems: {len(union)}/100   (writeup: 93)")
  never = [r for r in gt
           if (int(r["paper"]),
               [i for i, x in enumerate(
                   json.loads((RESULTS_DIR / MAIN[0] / f"paper_{r['paper']}_matched.json").read_text()))
                if x["ground_truth"]["subcategory"] == r["subcategory"]][0]) not in union]
  print(f"  caught by NO system: {len(never)}   (writeup: 7)")
  for r in never:
    print(f"     P{r['paper']} T{r['difficulty']} {r['category']}/{r['subcategory']}")

  hr("GREEDY COVERAGE CURVE (Verification: '71 -> 80 -> 85 -> 90 -> 93')")
  sets = {p: detection_set(p) for p in MAIN}
  u, remaining, step = set(), set(MAIN), 0
  while remaining:
    step += 1
    best = max(remaining, key=lambda p: len(u | sets[p]))
    gain = len(u | sets[best]) - len(u)
    u |= sets[best]
    remaining.remove(best)
    print(f"  {step:>2}. +{best:30} union={len(u):>3}  (+{gain})")

  hr("BEST COMPLEMENT TO TOP MODEL (Results: Refine '+9, next-best +7')")
  top = detection_set("openai_gpt55_high_reasoning")
  comp = sorted(
      ((len(top | sets[p]) - len(top), p) for p in MAIN if p != "openai_gpt55_high_reasoning"),
      reverse=True)
  print(f"  GPT-5.5 high reasoning alone = {len(top)}")
  for g, p in comp[:4]:
    print(f"     + {g:>2}  {p}")
  print("  writeup: Refine +9 (union 71->80), next-best single complement +7")

  hr("UNPLANTED FINDINGS SHARE (Verification: '84%')")
  tot_f = sum(findings(p) for _, p, _ in LEADERBOARD)
  tot_m = sum(caught(p) for _, p, _ in LEADERBOARD)
  print(f"  leaderboard systems: {tot_f} findings, {tot_m} match a planted error")
  print(f"  unplanted share = {100*(tot_f-tot_m)/tot_f:.0f}%   (writeup: 84%)")

  hr("REFINE BIMODALITY + HEADROOM (Results: Refine paragraph)")
  rc = by_category("refine_ink")
  cats_strong = ["methodological_design", "statistical_errors", "internal_consistency"]
  cats_weak = ["causal_inference", "reporting_completeness", "generalizability"]
  for c in cats_strong + cats_weak:
    print(f"  {c:24} Refine={rc.get(c,0)}")
  field_best = {c: max(by_category(p).get(c, 0) for _, p, _ in LEADERBOARD) for c in cats_weak}
  refine_total = caught("refine_ink")
  refine_weak = sum(rc.get(c, 0) for c in cats_weak)
  best_weak = sum(field_best.values())
  print(f"  Refine on its 3 weak cats: {refine_weak}  | field-best sum: {best_weak} {field_best}")
  print(f"  headroom: {refine_total} - {refine_weak} + {best_weak} = "
        f"{refine_total - refine_weak + best_weak}   (writeup: 57 -> ~70)")

  hr("NOT REPRODUCED HERE (inputs / manual)")
  print("  - $/paper costs: hardcoded in LEADERBOARD from the token-usage logs (Run 5e),")
  print("    not recomputed from API metering. $/error is derived from them.")
  print("  - reliability ranges (+-1 to +-18): need the run2/run3 repeat dirs; see ANALYSIS_LOG.")
  print("  - judge validation (20 hand-checked decisions): manual, not scriptable.")
  print("  - 'avg single system' is the mean over the 11 LEADERBOARD systems (documented set).")


if __name__ == "__main__":
    report()
