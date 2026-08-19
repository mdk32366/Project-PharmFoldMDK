"""FD1 — recover the raw-scale coefficients from PERSISTED values. This is a reproduction, not a fit.

attribution_k(i) = coef_k * xhat_k(i) = coef_k * (x_k(i) - mean_k) / sd_k

which is exactly linear in the raw feature x_k, with

    slope_k     = coef_k / sd_k          <- the RAW-SCALE coefficient
    intercept_k = -coef_k * mean_k / sd_k
    -intercept_k / slope_k = mean_k      <- the standardizer's mean falls out

⚠ sd_k and coef_k remain entangled: only their ratio is determined. Recovering sd_k by computing
it over the fit set would be reconstructing the standardizer, which GE3 forbids as fitting.
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
    rows.append({"id": int(p[0]), "score": float(p[1]),
                 "attr": json.loads(p[2]), "feat": feats})

print(f"rows: {len(rows)}   attribution vector length: {len(rows[0]['attr'])}")
complete = [r for r in rows if all(f is not None for f in r["feat"])]
print(f"rows with all six features non-null: {len(complete)}")
print(f"⚠ rows dropped for a null feature: {len(rows) - len(complete)}"
      f"  — a null is a category (D-027 null-with-a-reason), never an imputed mean")


def line_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    inter = my - slope * mx
    resid = max(abs(y - (slope * x + inter)) for x, y in zip(xs, ys))
    scale = max(abs(y) for y in ys) or 1.0
    return slope, inter, resid, resid / scale


print("\n" + "=" * 92)
print("STEP 1 — ⚠ THE PAIRING IS TESTED, NOT ASSUMED")
print("=" * 92)
print("  max |residual| of attribution[j] against feature[k]. The documented ordering is")
print("  accepted only if the DIAGONAL is the one that fits.\n")
print("         " + "".join(f"{k:>11d}" for k in range(6)))
best = {}
for j in range(6):
    cells, fits = [], []
    for k in range(6):
        f = line_fit([r["feat"][k] for r in complete], [r["attr"][j] for r in complete])
        fits.append(f)
        cells.append(f"{f[2]:11.1e}" if f else f"{'flat':>11s}")
    print(f"  attr{j}  " + "".join(cells))
    best[j] = min(range(6), key=lambda k: fits[k][2] if fits[k] else float("inf"))
print(f"\n  best-fitting feature per attribution index: {best}")
print(f"  ⚠ diagonal (j == k) for every index: {all(best[j] == j for j in range(6))}")

print("\n" + "=" * 92)
print("STEP 2 — ⚠⚠ DO ALL 56 ROWS AGREE? (GE2 — the self-check IS the point)")
print("=" * 92)
print(f"  {'k':<2} {'feature':<26} {'slope = coef/sd':>18} {'max|resid|':>12} {'rel':>10}")
print("  " + "-" * 86)
slopes, inters = {}, {}
for k, name in enumerate(FEATURE_NAMES):
    xs = [r["feat"][k] for r in complete]
    ys = [r["attr"][k] for r in complete]
    slope, inter, resid, rel = line_fit(xs, ys)
    slopes[k], inters[k] = slope, inter
    print(f"  {k:<2} {name:<26} {slope:>18.10g} {resid:>12.2e} {rel:>10.1e}")
print("\n  ⚠ a residual at float-noise level (~1e-16) means EVERY row lies on one line —")
print("    the attributions are exactly coefficient x standardized feature, as documented.")

print("\n" + "=" * 92)
print("STEP 3 — WHAT IS RECOVERED, AND WHAT IS NOT")
print("=" * 92)
print(f"  {'k':<2} {'feature':<26} {'raw-scale coef':>18} {'implied mean_k':>18}")
print("  " + "-" * 86)
for k, name in enumerate(FEATURE_NAMES):
    implied_mean = -inters[k] / slopes[k] if slopes[k] else float("nan")
    print(f"  {k:<2} {name:<26} {slopes[k]:>18.10g} {implied_mean:>18.8g}")
print("\n  ⚠⚠ NOT RECOVERED: the STANDARDIZED coefficient, which is what D-041 decision 1 makes")
print("     the attribution basis and what FD1 asked for. slope = coef_k / sd_k, and sd_k is not")
print("     persisted. Computing sd over the fit set would reconstruct the standardizer — that is")
print("     fitting, and GE3 forbids it.")

print("\n" + "=" * 92)
print("STEP 4 — ⚠ THE INTERCEPT, checked rather than assumed")
print("=" * 92)
print("  score = sigmoid(intercept + sum_k attribution_k) if the attributions are the full")
print("  linear predictor. Solving for the intercept from each row and asking whether they agree:")
import math
recovered = []
for r in complete:
    s = min(max(r["score"], 1e-12), 1 - 1e-12)
    logit = math.log(s / (1 - s))
    recovered.append(logit - sum(r["attr"]))
lo, hi = min(recovered), max(recovered)
print(f"    implied intercept  min {lo:.10g}   max {hi:.10g}   spread {hi - lo:.2e}")
if hi - lo < 1e-9:
    print(f"    ⚠⚠ ALL {len(complete)} ROWS AGREE -> the intercept is recovered exactly: {lo:.10g}")
    print("    So SEVEN parameters are now known on the raw scale: six slopes and this intercept.")
else:
    print("    ⚠ the rows DISAGREE, so `score` is not sigmoid(intercept + sum(attributions)).")
    print("      That is a finding about what `attributions` are, not a failure of the recovery.")
