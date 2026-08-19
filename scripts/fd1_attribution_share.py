"""FD1's second half — the share of attribution carried by the two pLDDT features.

⚠ This needs NO coefficients. The attributions are persisted per target and are already on the
standardized scale, so the share is read directly rather than derived. `D-041` decision 1 makes
`beta_k * x_k` the attribution basis, which is exactly what is stored.
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
    rows.append(json.loads(p[2]))

PLDDT_IDX = (2, 3)  # mean_plddt_ecd, membrane_proximal_plddt
print(f"key: the {len(rows)} target_scores rows at ranking_run_id = 2\n")

print("PER-FEATURE ATTRIBUTION MAGNITUDE, across the 56")
print(f"  {'k':<2} {'feature':<26} {'mean |attr|':>12} {'share':>8} {'max |attr|':>12}")
print("  " + "-" * 70)
means = []
for k, name in enumerate(FEATURE_NAMES):
    vals = [abs(r[k]) for r in rows]
    means.append(sum(vals) / len(vals))
total = sum(means)
for k, name in enumerate(FEATURE_NAMES):
    vals = [abs(r[k]) for r in rows]
    mark = "  <- pLDDT" if k in PLDDT_IDX else ""
    print(f"  {k:<2} {name:<26} {means[k]:>12.6f} {100*means[k]/total:>7.1f}% "
          f"{max(vals):>12.6f}{mark}")
print(f"  {'':<2} {'TOTAL':<26} {total:>12.6f} {100.0:>7.1f}%")

plddt_share = 100 * sum(means[k] for k in PLDDT_IDX) / total
print(f"\n  ⚠⚠ THE TWO pLDDT FEATURES CARRY {plddt_share:.1f}% OF TOTAL ATTRIBUTION MAGNITUDE")
print(f"     — two of six features, {plddt_share:.1f}% of the weight.")

# ⚠ per-row, not only in aggregate: a mean can hide a bimodal split
per_row = []
for r in rows:
    tot = sum(abs(v) for v in r)
    per_row.append(100 * sum(abs(r[k]) for k in PLDDT_IDX) / tot if tot else 0.0)
per_row.sort()
n = len(per_row)
print(f"\n  ⚠ per-target share, because a mean can hide a bimodal split:")
print(f"     min {per_row[0]:.1f}%  q1 {per_row[n//4]:.1f}%  median {per_row[n//2]:.1f}%  "
      f"q3 {per_row[3*n//4]:.1f}%  max {per_row[-1]:.1f}%")
print(f"     targets where pLDDT carries > 50% of attribution: "
      f"{sum(1 for x in per_row if x > 50)} of {n}")

print("\n  SIGNS of the standardized coefficients — recoverable even though the MAGNITUDES are")
print("  not, because sign(coef_k) == sign(coef_k / sd_k) and sd_k > 0 always:")
SLOPES = {0: 0.0001536014218, 1: -0.4576446602, 2: 0.003082622556,
          3: 0.01459632517, 4: -0.001590501602, 5: -0.3924876377}
for k, name in enumerate(FEATURE_NAMES):
    print(f"    {name:<26} {'+' if SLOPES[k] > 0 else '-'}")
print("\n  ⚠ Higher mean pLDDT and higher membrane-proximal pLDDT both push the score UP;")
print("    radius of gyration, normalised SASA and largest-patch fraction push it DOWN.")
