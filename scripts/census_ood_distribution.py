"""KB1-KB4 re-run against the extracted artifact — `D-079` amendment 1 ruling 3's measurement.

⚠ Yesterday this returned UNDEFINED: no census row carried a feature vector. The artifact
  produced by `scripts/census_extract_features.py` is the input that was missing.

⚠⚠ READ-ONLY over committed files. Nothing is fitted, standardized into a scorer, or written.
   The cohort's range is the FIT POPULATION's raw feature range (`KA1`), re-derived here from
   the committed cohort baseline rather than quoted.

⚠ The +/-3 bar is `mean_k +/- 3*sd_raw(56)` at ddof=0. It equals a true +/-3 STANDARDIZED units
   only if the standardizer used ddof=0 on these same 56 -- `sd_k` itself is NOT recoverable
   (`F-049` amendment 1), and the "two paths" argument that appeared to recover it is an
   algebraic identity, not evidence. Stated at every use, never silently.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from core.features import FEATURE_NAMES  # noqa: E402

ART = REPO / "data" / "census" / "census_features.v1.jsonl"
BASE = REPO / "data" / "census" / "cohort_feature_baseline.json"


def pct(s, q):
    if not s:
        return None
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] if lo == hi else s[lo] + (s[hi] - s[lo]) * (pos - lo)


def stats(xs):
    s = sorted(xs)
    return dict(n=len(s), min=s[0], p05=pct(s, .05), p25=pct(s, .25), med=pct(s, .50),
                p75=pct(s, .75), p95=pct(s, .95), max=s[-1], mean=sum(s) / len(s))


def sd0(xs):
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


bar = "=" * 100
COH = json.loads(BASE.read_text(encoding="utf-8"))
print(f"  cohort baseline: {BASE.name}  (n={COH['n']}, key: {COH['key']})")

recs = [json.loads(l) for l in ART.read_text(encoding="utf-8").splitlines() if l.strip()]
man = json.loads((REPO / "data/census/census_features.v1.manifest.json").read_text(encoding="utf-8"))
print(f"  artifact: {ART.name}  lines {len(recs)}  partial={man['partial']}  "
      f"sha256 {man['sha256'][:16]}...")
if man["partial"]:
    print("  ⚠⚠ THE ARTIFACT IS PARTIAL. Every count below is keyed to what it contains, and")
    print("     is NOT a census-wide statistic (D-079 decision 6: no census-wide statistic from")
    print("     a partial tranche). Reported anyway, labelled, never presented as complete.")
print()

print(bar)
print("KC3 / LC3 — OUTCOMES, AND THEY SUM TO THE ARTIFACT WITH ITS KEY STATED")
print(bar)
oc = Counter(r["outcome"] for r in recs)
for k, v in oc.most_common():
    print(f"    {k:30s} {v:5d}")
print(f"    {'TOTAL':30s} {sum(oc.values()):5d}   (census rows expected: {man['census_rows_expected']})")

ok = [r for r in recs if r["outcome"] == "ok"]
complete = [r for r in ok if all(r["features"].get(k) is not None for k in FEATURE_NAMES)]
print(f"\n  ⚠ of the 'ok' rows, carrying a COMPLETE six-vector: {len(complete)} / {len(ok)}")
partials = [r for r in ok if r not in complete]
if partials:
    pc = Counter()
    for r in partials:
        for k in FEATURE_NAMES:
            if r["features"].get(k) is None:
                pc[k] += 1
    print("  ⚠ null columns among the incomplete — a category, never a zero:")
    for k, v in pc.most_common():
        print(f"    {k:30s} {v:5d}")
    rc = Counter()
    for r in partials:
        for k, v in (r.get("null_reasons") or {}).items():
            rc[f"{k}: {v}"] += 1
    for k, v in rc.most_common(8):
        print(f"      {k[:76]:78s} {v:4d}")

print()
print(bar)
print("KB1 — THE CENSUS DISTRIBUTION, SIX STATISTICS, AGAINST THE COHORT'S")
print(bar)
print(f"  ⚠ DENOMINATOR: {len(complete)} rows with a complete six-vector, out of {len(recs)} in the artifact.")
print()
CEN = {}
for k, name in enumerate(FEATURE_NAMES):
    xs = [r["features"][name] for r in complete]
    CEN[k] = stats(xs)
    c = COH["features"][name]
    print(f"  {name}")
    print(f"    cohort  n {COH['n']:>5}   min {c['min']:>11.5g}  p05 {c['p05']:>11.5g}  "
          f"med {c['med']:>11.5g}  p95 {c['p95']:>11.5g}  max {c['max']:>11.5g}")
    print(f"    census  n {CEN[k]['n']:>5}   min {CEN[k]['min']:>11.5g}  p05 {CEN[k]['p05']:>11.5g}  "
          f"med {CEN[k]['med']:>11.5g}  p95 {CEN[k]['p95']:>11.5g}  max {CEN[k]['max']:>11.5g}")

print()
print(bar)
print("KB2 — THE OUT-OF-RANGE COUNT, AT THREE BARS, NOT ONE")
print(bar)
FAIL = {k: {"strict": set(), "p0595": set(), "sd3": set()} for k in range(6)}
for k, name in enumerate(FEATURE_NAMES):
    c = COH["features"][name]
    lo3, hi3 = c["mean"] - 3 * c["sd_ddof0"], c["mean"] + 3 * c["sd_ddof0"]
    for r in complete:
        v = r["features"][name]
        if v < c["min"] or v > c["max"]:
            FAIL[k]["strict"].add(r["analysis_id"])
        if v < c["p05"] or v > c["p95"]:
            FAIL[k]["p0595"].add(r["analysis_id"])
        if v < lo3 or v > hi3:
            FAIL[k]["sd3"].add(r["analysis_id"])
n = len(complete)
print(f"  {'k':<2} {'feature':<26} {'strict min-max':>18} {'p05-p95':>17} {'+/-3 sd':>17}")
print("  " + "-" * 92)
for k, name in enumerate(FEATURE_NAMES):
    print(f"  {k:<2} {name:<26} "
          f"{len(FAIL[k]['strict']):>8d} ({100*len(FAIL[k]['strict'])/n:5.1f}%) "
          f"{len(FAIL[k]['p0595']):>8d} ({100*len(FAIL[k]['p0595'])/n:4.1f}%) "
          f"{len(FAIL[k]['sd3']):>8d} ({100*len(FAIL[k]['sd3'])/n:4.1f}%)")

print()
print(bar)
print("KB3 — ⚠⚠ THE UNION. THIS IS THE NUMBER THAT DECIDES THE AMENDMENT")
print(bar)
for label, key in (("STRICT (cohort observed min-max)", "strict"),
                   ("p05-p95", "p0595"), ("+/-3 standardized units", "sd3")):
    any_ = set()
    all_ = {r["analysis_id"] for r in complete}
    for k in range(6):
        any_ |= FAIL[k][key]
        all_ &= FAIL[k][key]
    print(f"  {label}")
    print(f"    out of range on AT LEAST ONE feature -> REFUSED : {len(any_):5d} / {n} = {100*len(any_)/n:5.1f}%")
    print(f"    out of range on ALL SIX                        : {len(all_):5d} / {n} = {100*len(all_)/n:5.1f}%")
    print(f"    ⚠ profile COMPUTABLE (in range on all six)      : {n-len(any_):5d} / {n} = {100*(n-len(any_))/n:5.1f}%")
    print()

print(bar)
print("KB4 — HOW MANY FEATURES EACH ROW FAILS: 0..6, SUMMING TO THE DENOMINATOR")
print(bar)
for label, key in (("STRICT", "strict"), ("p05-p95", "p0595"), ("+/-3 sd", "sd3")):
    dist = Counter(sum(1 for k in range(6) if r["analysis_id"] in FAIL[k][key]) for r in complete)
    print(f"  {label}:")
    for i in range(7):
        print(f"    fails {i} feature{'s' if i != 1 else ' '} : {dist.get(i,0):5d}   {100*dist.get(i,0)/n:5.1f}%")
    print(f"    {'TOTAL':17s}: {sum(dist.values()):5d}\n")

print(bar)
print("⚠ THE PLANNER'S PRE-REGISTERED EXPECTATION, SCORED AGAINST THE RESULT")
print(bar)
print("  recorded before the measurement existed: 'ecd_length the worst offender,")
print("  mean_plddt_ecd the mildest, and a MINORITY of the census out of range on the strict test.'")
worst = max(range(6), key=lambda k: len(FAIL[k]["strict"]))
mild = min(range(6), key=lambda k: len(FAIL[k]["strict"]))
any_s = set()
for k in range(6):
    any_s |= FAIL[k]["strict"]
print(f"    worst offender on strict : {FEATURE_NAMES[worst]}  "
      f"({len(FAIL[worst]['strict'])} rows)  -> expectation {'HELD' if worst == 0 else 'MISSED'}")
print(f"    mildest on strict        : {FEATURE_NAMES[mild]}  "
      f"({len(FAIL[mild]['strict'])} rows)  -> expectation {'HELD' if mild == 2 else 'MISSED'}")
print(f"    minority out of range    : {len(any_s)}/{n} = {100*len(any_s)/n:.1f}%  "
      f"-> expectation {'HELD' if len(any_s) < n/2 else 'MISSED'}")
print("\n  ⚠ Scored, not adjusted. The expectation was written down before the number existed,")
print("    which is the only thing that makes this line worth printing (F-022).")
