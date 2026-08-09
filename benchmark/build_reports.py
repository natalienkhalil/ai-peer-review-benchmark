#!/usr/bin/env python3
"""Rebuild reports from existing paper_*_matched.json + paper_*_review.json.

Avoids re-running the LLM judge (its cache uses per-process hash() so it never
hits across runs). Reads the already-computed match decisions instead.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

from config import RESULTS_DIR, REPORTS_DIR
from matching import load_ground_truth

GT = load_ground_truth()
CATEGORIES = sorted(set(e.category for e in GT))


def provider_stats(pdir: Path):
    """Return (total, {tier:detected}, {cat:detected}, {paper:detected}, findings) or None."""
    matched_files = sorted(pdir.glob("paper_*_matched.json"))
    if not matched_files:
        return None
    total = 0
    tier = {1: 0, 2: 0, 3: 0}
    cat = defaultdict(int)
    paper = {}
    findings = 0
    for mf in matched_files:
        pid = int(mf.stem.split("_")[1])
        matches = json.loads(mf.read_text())
        det = 0
        for m in matches:
            if m.get("matched"):
                det += 1
                gt = m["ground_truth"]
                tier[gt["difficulty"]] += 1
                cat[gt["category"]] += 1
        paper[pid] = det
        total += det
        rf = pdir / f"paper_{pid}_review.json"
        if rf.exists():
            findings += len(json.loads(rf.read_text()).get("issues", []))
    return total, tier, cat, paper, findings


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = {}
    for pdir in sorted(RESULTS_DIR.iterdir()):
        if not pdir.is_dir():
            continue
        st = provider_stats(pdir)
        if st:
            rows[pdir.name] = st

    with open(REPORTS_DIR / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provider", "total_detected", "total_100", "tier1_13", "tier2_63", "tier3_24", "total_findings"])
        for name, (total, tier, cat, paper, findings) in sorted(rows.items()):
            w.writerow([name, total, 100, tier[1], tier[2], tier[3], findings])

    with open(REPORTS_DIR / "by_category.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provider"] + CATEGORIES)
        for name, (total, tier, cat, paper, findings) in sorted(rows.items()):
            w.writerow([name] + [cat.get(c, 0) for c in CATEGORIES])

    with open(REPORTS_DIR / "by_paper.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provider"] + [f"paper_{p}" for p in range(1, 11)] + ["total"])
        for name, (total, tier, cat, paper, findings) in sorted(rows.items()):
            w.writerow([name] + [paper.get(p, 0) for p in range(1, 11)] + [total])

    print(f"Rebuilt reports for {len(rows)} providers -> {REPORTS_DIR}")


if __name__ == "__main__":
    main()
