#!/usr/bin/env python3
"""Categorize the UNPLANTED findings (everything a system flagged that did NOT match one
of our 100 inserted errors) onto the refine_taxonomy_v4 subcategories.

Goal: read the empirical distribution of issue types these reviewers surface in the papers,
so we can compare it to our flat planted distribution (10/category) and, optionally, reweight.

We do NOT claim these findings are correct — there's no non-circular way to verify them, which
is why they're not in the eval. Under an on-average-correct assumption, the distribution is
informative. Findings that map to nothing are logged to an `unmapped` bucket.
"""

import asyncio
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from config import RESULTS_DIR, ENV_FILE

load_dotenv(ENV_FILE)

# --- canonical taxonomy (refine_taxonomy_v4.md): category -> [(subcode, desc)] ---
TAXO = {
"statistical_errors": [
 ("calculation_mismatch","reported values don't compute from given inputs"),
 ("df_error","degrees of freedom inconsistent with design/N"),
 ("test_parameter_error","wrong test for design, wrong parameters reported"),
 ("table_data_error","values in tables inconsistent or misplaced")],
"methodological_design": [
 ("pooling_heterogeneous_data","combining data across procedures without justification"),
 ("multiple_comparisons_uncorrected","many tests without correction or acknowledgment"),
 ("randomization_unclear","random assignment claimed but procedure not described"),
 ("underpowered_subgroups","subgroup analyses with very small cell sizes"),
 ("missing_key_analysis","obvious analysis omitted (e.g. no main effects)"),
 ("blinding_inadequate","assessors/participants unblinded when blinding feasible"),
 ("allocation_concealment_unclear","randomization not protected from foreknowledge"),
 ("demand_characteristics_likely","design lets participants guess hypothesis"),
 ("control_condition_inadequate","control doesn't isolate the manipulation"),
 ("measurement_timing_problematic","assessment at wrong timepoint for construct")],
"construct_validity": [
 ("manipulation_spillover","induction affects unintended constructs"),
 ("measure_conflation","DV mixes distinct processes"),
 ("construct_operationalization_mismatch","measure doesn't match construct definition"),
 ("confound_with_alternative_construct","effect could be a related but distinct construct")],
"causal_inference": [
 ("mechanism_unmeasured","causal mechanism claimed but mediator not measured"),
 ("causal_chain_incomplete","only some links in proposed chain tested"),
 ("correlation_causation_conflation","causal language for correlational design"),
 ("reverse_causation_unaddressed","plausible reverse direction not discussed"),
 ("confound_unaddressed","obvious third variable not discussed"),
 ("temporal_precedence_unclear","IV may not precede DV"),
 ("third_variable_likely","plausible common cause not acknowledged")],
"internal_consistency": [
 ("cross_section_contradiction","intro claims contradict discussion claims"),
 ("cross_experiment_heterogeneity","different experiments show different patterns"),
 ("statistic_text_table_mismatch","numbers in text don't match tables"),
 ("definition_inconsistency","term used differently in different sections")],
"reporting_completeness": [
 ("missing_parameters","can't verify computation (missing df, N, etc.)"),
 ("unclear_procedure","procedure not described in replicable detail"),
 ("missing_subgroup_data","subgroups mentioned but data not shown"),
 ("incomplete_manipulation_check","manipulation check missing or incomplete"),
 ("intervention_not_replicable","insufficient detail to reproduce intervention"),
 ("materials_not_available","stimuli/measures not provided or accessible"),
 ("participant_flow_unclear","can't reconstruct N through study phases"),
 ("primary_outcome_not_specified","no clear hierarchy among outcomes"),
 ("analysis_plan_absent","no indication of pre-specification")],
"generalizability": [
 ("external_validity_overclaim","claims extend beyond what design supports"),
 ("context_dependent_unacknowledged","effect likely context-specific but not noted"),
 ("sample_limitation_unaddressed","sample constraints not discussed"),
 ("ecological_validity_assumption","lab task assumed to map to real behavior")],
"theoretical_conceptual": [
 ("term_misuse","established term used non-standardly"),
 ("framework_misapplication","theory applied incorrectly"),
 ("classification_error","construct placed in wrong category"),
 ("citation_error","malformed or incorrect citation / mischaracterized source")],
"analytic_flexibility": [
 ("many_dvs_no_primary","multiple outcomes without designated primary or correction"),
 ("complex_design_incomplete_reporting","not all cells/conditions accounted for"),
 ("vague_exclusion_criteria","exclusions could be applied flexibly"),
 ("covariate_justification_absent","controls included without rationale"),
 ("subgroup_analyses_unmarked","exploratory subgroups presented as planned"),
 ("all_predictions_confirmed","every hypothesis supported, no disconfirmations"),
 ("no_null_results","no non-significant findings reported anywhere"),
 ("interaction_without_main_effects","moderation reported but simpler effects absent"),
 ("harking_language","post-hoc framing presented as a priori"),
 ("hypothesis_specificity_mismatch","vague intro hypothesis, specific discussion claim"),
 ("results_dependent_framing","theoretical framing tracks results too closely")],
"attrition_missing_data": [
 ("differential_attrition","dropout rate differs by condition"),
 ("high_overall_attrition",">20% dropout without justification"),
 ("missing_data_handling_unclear","no description of how missingness addressed"),
 ("per_protocol_only","no ITT analysis when appropriate"),
 ("attrition_not_by_condition","can't assess differential dropout from report")],
}
SUB2CAT = {sub: cat for cat, subs in TAXO.items() for sub, _ in subs}
ALL_SUBS = list(SUB2CAT.keys())

TAXO_BLOCK = "\n".join(
    f"[{cat}]\n" + "\n".join(f"  {sub}: {desc}" for sub, desc in subs)
    for cat, subs in TAXO.items()
)

SYSTEM = """You label a single peer-review finding with the ONE taxonomy subcategory that best
captures the methodological issue it raises. Use the subcategory code exactly as written.
If the finding does not fit ANY subcategory (e.g. it is about grammar/typos, formatting,
positive praise, an ethics/IRB issue, an open-science/data-availability gripe, or anything
outside these methodological categories), answer exactly: unmapped
Answer with ONLY the subcategory code or the word unmapped. No other text."""

_cache_path = Path("/private/tmp/claude-501/-Users-paullitvak-Documents-GitHub-review-benchmark/73090433-a143-4ab8-9893-1006c7cc419c/scratchpad/cat_cache.json")
_cache = json.loads(_cache_path.read_text()) if _cache_path.exists() else {}

DIVERSE = [
    "openai_gpt55_high_reasoning", "openai_gpt54_no_reasoning",
    "claude_opus48_high_thinking", "claude_sonnet_no_thinking",
    "gemini_pro", "refine_ink", "reviewer3",
]


def matched_keys(prov: str) -> set:
    """(_desc,_quote) of findings that matched a planted error -> to exclude."""
    keys = set()
    d = RESULTS_DIR / prov
    for pid in range(1, 11):
        mp = d / f"paper_{pid}_matched.json"
        if not mp.exists():
            continue
        for m in json.loads(mp.read_text()):
            if m.get("matched") and m.get("matched_finding"):
                f = m["matched_finding"]
                keys.add((f.get("description", "")[:200], (f.get("quote") or "")[:200]))
    return keys


def unplanted_findings(prov: str) -> list[dict]:
    excl = matched_keys(prov)
    out = []
    d = RESULTS_DIR / prov
    for pid in range(1, 11):
        rp = d / f"paper_{pid}_review.json"
        if not rp.exists():
            continue
        for it in json.loads(rp.read_text())["issues"]:
            k = (it.get("description", "")[:200], (it.get("quote") or "")[:200])
            if k in excl:
                continue
            out.append({"prov": prov, "paper": pid, **it})
    return out


async def classify(client, sem, f) -> str:
    desc = (f.get("description") or "")[:500]
    quote = (f.get("quote") or "")[:250]
    ckey = f"v1|{hash((desc, quote))}"
    if ckey in _cache:
        return _cache[ckey]
    user = [
        {"type": "text", "text": "TAXONOMY:\n" + TAXO_BLOCK,
         "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": f"FINDING:\nsubcategory_label: {f.get('subcategory')}\n"
                                  f"description: {desc}\nquote: {quote}\n\nSubcategory code or 'unmapped':"},
    ]
    async with sem:
        try:
            r = await client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=15, temperature=0,
                system=SYSTEM, messages=[{"role": "user", "content": user}])
            ans = r.content[0].text.strip().split()[0].strip(".,").lower()
        except Exception:
            ans = "unmapped"
    ans = ans if (ans in SUB2CAT or ans == "unmapped") else "unmapped"
    _cache[ckey] = ans
    return ans


async def main():
    client = anthropic.AsyncAnthropic()
    sem = asyncio.Semaphore(20)
    all_findings = []
    for prov in DIVERSE:
        fs = unplanted_findings(prov)
        all_findings += fs
        print(f"  {prov:30} {len(fs)} unplanted findings")
    print(f"\nClassifying {len(all_findings)} findings...")
    results = await asyncio.gather(*[classify(client, sem, f) for f in all_findings])
    _cache_path.write_text(json.dumps(_cache))

    for f, lab in zip(all_findings, results):
        f["_label"] = lab

    # ---- aggregate ----
    cat_count = Counter()
    sub_count = Counter()
    per_sys_cat = defaultdict(Counter)
    unmapped = []
    for f in all_findings:
        lab = f["_label"]
        if lab == "unmapped":
            cat_count["UNMAPPED"] += 1
            per_sys_cat[f["prov"]]["UNMAPPED"] += 1
            unmapped.append(f)
            continue
        cat = SUB2CAT[lab]
        cat_count[cat] += 1
        sub_count[lab] += 1
        per_sys_cat[f["prov"]][cat] += 1

    total = len(all_findings)
    mapped = total - cat_count["UNMAPPED"]
    print("\n" + "=" * 70)
    print(f"EMPIRICAL DISTRIBUTION of unplanted findings (n={total}, {DIVERSE.__len__()} systems)")
    print("=" * 70)
    print(f"{'category':26}{'raw':>6}{'% of mapped':>13}{'planted%':>10}")
    planted_pct = 10.0  # flat: 10 per category
    for cat in list(TAXO.keys()):
        c = cat_count[cat]
        print(f"{cat:26}{c:>6}{100*c/mapped:>12.1f}%{planted_pct:>9.0f}%")
    print(f"{'UNMAPPED':26}{cat_count['UNMAPPED']:>6}{100*cat_count['UNMAPPED']/total:>12.1f}% (of all)")

    print("\n-- top 20 subcategories --")
    for sub, c in sub_count.most_common(20):
        print(f"  {c:>4}  {SUB2CAT[sub]:24} {sub}")

    print("\n-- per-system category share (% of that system's mapped findings) --")
    cats = list(TAXO.keys())
    print(f"{'system':30}" + "".join(f"{c[:10]:>11}" for c in cats))
    for prov in DIVERSE:
        m = sum(v for k, v in per_sys_cat[prov].items() if k != "UNMAPPED") or 1
        print(f"{prov:30}" + "".join(f"{100*per_sys_cat[prov][c]/m:>10.0f}%" for c in cats))

    out = {"distribution_category": dict(cat_count),
           "distribution_subcategory": dict(sub_count),
           "per_system_category": {k: dict(v) for k, v in per_sys_cat.items()},
           "n_total": total, "n_unmapped": cat_count["UNMAPPED"]}
    Path("reports/empirical_distribution.json").write_text(json.dumps(out, indent=2))
    sc = Path("/private/tmp/claude-501/-Users-paullitvak-Documents-GitHub-review-benchmark/73090433-a143-4ab8-9893-1006c7cc419c/scratchpad")
    (sc / "unmapped_findings.json").write_text(json.dumps(
        [{"prov": f["prov"], "paper": f["paper"], "sub": f.get("subcategory"),
          "desc": (f.get("description") or "")[:300]} for f in unmapped], indent=2))
    print(f"\nUNMAPPED: {len(unmapped)} findings saved for review.")


if __name__ == "__main__":
    asyncio.run(main())
