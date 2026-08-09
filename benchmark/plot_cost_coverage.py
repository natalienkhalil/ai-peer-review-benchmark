#!/usr/bin/env python3
"""Cost-vs-coverage scatter for the writeup: $/paper (log x) vs errors caught,
with the Pareto frontier drawn. Reuses caught counts from writeup_numbers so the
plotted numbers match the leaderboard exactly.

    uv run plot_cost_coverage.py   ->   reports/cost_coverage.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import REPORTS_DIR
from writeup_numbers import LEADERBOARD, caught

# (display, $/paper) — Reviewer3 is a flat subscription, no per-paper marginal cost, so it's
# omitted from the cost axis (you can't place it sensibly).
pts = []
for name, prov, cost in LEADERBOARD:
    if cost is None:
        continue
    k = caught(prov)
    pts.append((name, cost, k, cost * 10 / k))  # last = $/error

# Pareto frontier: minimize $/paper, maximize caught.
def on_frontier(p):
    return not any(q[1] <= p[1] and q[2] >= p[2] and (q[1] < p[1] or q[2] > p[2])
                   for q in pts if q is not p)

frontier = sorted([p for p in pts if on_frontier(p)], key=lambda p: p[1])

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.set_xscale("log")

# Pareto frontier drawn as a STEP envelope: "for a budget <= $x, the most you can
# catch is y." (Not a fit or interpolation — there's no system between the steps.)
fx = [p[1] for p in frontier]
fy = [p[2] for p in frontier]
xmax = max(p[1] for p in pts) * 2
ax.step(fx + [xmax], fy + [fy[-1]], where="post", color="#1f77b4", lw=1.5,
        zorder=1, alpha=.7, label="Pareto frontier (best coverage ≤ budget)")

# per-label offset in points (dx, dy, ha) to keep the crowded $0.1–0.4 cluster legible
OFF = {
    "GPT-5.5 high reasoning": (8, 3, "left"),
    "GPT-5.5 no reasoning":   (9, -1, "left"),
    "GPT-5.4 no reasoning":   (0, -14, "center"),
    "Sonnet 4.6":             (0, 8, "center"),
    "Opus 4.6":               (9, -3, "left"),
    "GPT-5.4 high reasoning": (9, -3, "left"),
    "Opus 4.8 thinking":      (9, -2, "left"),
    "Gemini 3.1 Pro":         (9, 2, "left"),
    "Gemini 3 Flash":         (9, 2, "left"),
    "Refine.ink":             (-9, 4, "right"),
}
for name, cost, k, cpe in pts:
    fr = on_frontier((name, cost, k, cpe))
    ax.scatter(cost, k, s=70, zorder=3,
               color="#1f77b4" if fr else "#999999",
               edgecolor="black", linewidth=.5)
    dx, dy, ha = OFF.get(name, (8, 3, "left"))
    ax.annotate(name, (cost, k), textcoords="offset points", xytext=(dx, dy),
                ha=ha, fontsize=8)

ax.set_xlabel("Cost per paper (USD, log scale)")
ax.set_ylabel("Errors caught / 100")
ax.set_title("AI peer reviewers: cost vs. coverage\n(frontier = best coverage at each price)")
ax.set_ylim(30, 78)
ax.grid(True, which="both", axis="both", ls=":", alpha=.4)
ax.legend(loc="lower right", fontsize=8, frameon=False)
fig.tight_layout()
out = REPORTS_DIR / "cost_coverage.png"
fig.savefig(out, dpi=150)
print(f"wrote {out}")
print("\nfrontier:", ", ".join(f"{p[0]} (${p[1]}/{p[2]})" for p in frontier))
print("off-frontier:", ", ".join(p[0] for p in pts if not on_frontier(p)))
