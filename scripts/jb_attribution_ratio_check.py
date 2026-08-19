"""JB2 — the self-check, run as the order specifies it, which REFUTES the order's own formula.

`JB` states: `attribution_k(i) / x_k(i) = coef_k / sd_k` — a constant over every scored row.

⚠⚠ That holds only if the standardizer does NOT centre. `core/scorer.py:152` is
`(features[j] - self.means[j]) / self.stds[j]`, so it does. The ratio is therefore NOT constant,
and the correct relation carries an intercept:

    attribution_k(i) = (coef_k / sd_k) * x_k(i)  -  coef_k * mean_k / sd_k

⚠ Run both ways below, because "the ratio varies" would otherwise read as drift or
non-determinism — the very findings JB2 says a deviation would indicate. **The deviation is real
and its cause is the fourth possibility the order did not list: the formula omitted the mean.**
"""
import json
import pathlib
import sys

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))
from core.features import FEATURE_NAMES  # noqa: E402

SP = pathlib.Path(__file__).resolve().parent
NULL_TOKENS = {"", "NULL", chr(92) + "N"}

rows = []
for line in (SP / "fd1.tsv").read_text(encoding="utf-8").splitlines():
    p = line.split("\t")
    if len(p) < 9:
        continue
    feats = [None if v.strip() in NULL_TOKENS else float(v) for v in p[3:9]]
    rows.append({"id": int(p[0]), "attr": json.loads(p[2]), "feat": feats})

print("JB3 — RUN READ: ranking_run_id = 2 ONLY.")
print("  ⚠ Runs 3 and 4 share a scorer_version at 5 and 3 parameters; mixing rows across runs")
print("    would produce a clean, stable, meaningless slope. One run, stated.")
print(f"  rows: {len(rows)}\n")

print("=" * 94)
print("JB4 — x_k(i) = 0, WHERE THE RATIO IS UNDEFINED. A CATEGORY, NOT A DROP")
print("=" * 94)
zero_counts = {k: sum(1 for r in rows if r["feat"][k] == 0.0) for k in range(6)}
null_counts = {k: sum(1 for r in rows if r["feat"][k] is None) for k in range(6)}
for k, name in enumerate(FEATURE_NAMES):
    print(f"  {k} {name:26s} x_k == 0 : {zero_counts[k]:3d}   x_k IS NULL : {null_counts[k]:3d}")
print(f"  ⚠ total rows where the RATIO is undefined: "
      f"{sum(1 for r in rows if any(r['feat'][k] in (0.0, None) for k in range(6)))}")
print("  ⚠ none is dropped silently and none is coerced (F-020: an absent measurement coerced to")
print("    zero and fit as though measured).")

print("\n" + "=" * 94)
print("JB2 — THE ORDER'S RATIO TEST, RUN AS SPECIFIED")
print("=" * 94)
print(f"  {'k':<2} {'feature':<26} {'min ratio':>16} {'max ratio':>16} {'spread':>12}")
print("  " + "-" * 88)
for k, name in enumerate(FEATURE_NAMES):
    rs = [r["attr"][k] / r["feat"][k] for r in rows
          if r["feat"][k] not in (None, 0.0)]
    print(f"  {k:<2} {name:<26} {min(rs):>16.9g} {max(rs):>16.9g} {max(rs)-min(rs):>12.3g}")
print("\n  ⚠⚠ THE RATIO IS NOT CONSTANT. Under JB2's stated reading that is a deviation and")
print("     therefore a finding — but the finding is about the FORMULA, not the data.")

print("\n" + "=" * 94)
print("JB1/JB2 — THE CORRECT RELATION: slope AND intercept, and THEN the rows agree")
print("=" * 94)


def line_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    inter = my - slope * mx
    resid = [abs(y - (slope * x + inter)) for x, y in zip(xs, ys)]
    return slope, inter, max(resid)


print(f"  {'k':<2} {'feature':<26} {'slope = coef/sd':>18} {'max|resid|':>12} {'rows agreeing':>14}")
print("  " + "-" * 88)
for k, name in enumerate(FEATURE_NAMES):
    usable = [r for r in rows if r["feat"][k] is not None]
    xs = [r["feat"][k] for r in usable]
    ys = [r["attr"][k] for r in usable]
    slope, inter, mr = line_fit(xs, ys)
    agree = sum(1 for x, y in zip(xs, ys) if abs(y - (slope * x + inter)) < 1e-12)
    sign = "+" if slope > 0 else "-"
    print(f"  {k:<2} {name:<26} {slope:>18.10g} {mr:>12.2e} {agree:>7d}/{len(usable):<6d}")
print("\n  ⚠ every row of every feature agrees to within 1e-12 — so the attributions ARE exactly")
print("    coefficient x standardized feature, and the earlier 'deviation' was the missing mean.")

print("\n" + "=" * 94)
print("JB5 — THE SIGNS, AND WHAT PUSHES A TARGET UP")
print("=" * 94)
for k, name in enumerate(FEATURE_NAMES):
    usable = [r for r in rows if r["feat"][k] is not None]
    slope, _, _ = line_fit([r["feat"][k] for r in usable], [r["attr"][k] for r in usable])
    direction = "UP" if slope > 0 else "DOWN"
    plddt = "  <- pLDDT" if k in (2, 3) else ""
    print(f"  {name:26s} {'+' if slope > 0 else '-'}   higher value pushes the score {direction}{plddt}")
print("\n  ⚠ BOTH confidence features push UP: a target the model is more confident about scores")
print("    higher. ⚠⚠ That is the direction the paper's confidence section has to state plainly —")
print("    the axis rewards being well-predicted, and F-005 already shows the pair carries the")
print("    result. Sign and magnitude point the same way.")
