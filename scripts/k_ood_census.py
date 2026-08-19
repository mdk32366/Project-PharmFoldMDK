"""KA/KB/KC — the out-of-distribution measurement that decides D-079 amendment ruling 1 vs ruling 3.

⚠⚠ READ-ONLY. Nothing is fitted, refitted, standardized into a scorer, or written.
The order (§6) bars reconstructing the standardizer. §2 KB2 nonetheless asks for a ±3
STANDARDIZED-unit bar. This script resolves that tension explicitly rather than quietly:
see METHOD, printed in full at KA3.
"""
import csv
import json
import math
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))
from core.features import FEATURE_NAMES  # noqa: E402

SP = pathlib.Path(__file__).resolve().parent
NULL = {"", "NULL", "\\N"}

# raw-scale slopes r_k = coef_k / sd_k and implied means, recovered in FD1 from persisted values
FD1_SLOPE = [+0.0001536014218, -0.4576446602, +0.003082622556,
             +0.01459632517, -0.001590501602, -0.3924876377]
FD1_MEAN = [413.26786, 0.15600094, 69.002672, 66.002025, 71.020666, 0.73453592]


def f(v):
    v = (v or "").strip()
    return None if v in NULL else float(v)


def pct(sorted_xs, q):
    """Linear-interpolated percentile on the sorted sample (the numpy 'linear' method).
    Stated because a percentile without its interpolation rule is three different numbers."""
    if not sorted_xs:
        return None
    if len(sorted_xs) == 1:
        return sorted_xs[0]
    pos = q * (len(sorted_xs) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_xs[lo]
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (pos - lo)


def stats(xs):
    s = sorted(xs)
    return dict(n=len(s), min=s[0], p05=pct(s, .05), p25=pct(s, .25), med=pct(s, .50),
                p75=pct(s, .75), p95=pct(s, .95), max=s[-1],
                mean=sum(s) / len(s))


def sd(xs, ddof=0):
    n = len(xs)
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - ddof))


bar = "=" * 100

# ── load ─────────────────────────────────────────────────────────────────────
cohort = []
for row in csv.reader((SP / "cohort56.csv").open(encoding="utf-8")):
    if len(row) < 8:
        continue
    cohort.append({"acc": row[0], "attr": json.loads(row[1]),
                   "x": [f(v) for v in row[2:8]]})

census = []
for row in csv.reader((SP / "census.csv").open(encoding="utf-8")):
    if len(row) < 11:
        continue
    census.append({"id": int(row[0]), "acc": row[1], "tranche": int(row[2]),
                   "folded": row[3] == "t", "has_row": row[4] == "t",
                   "x": [f(v) for v in row[5:11]]})

print(bar)
print("KA1 — THE COHORT'S RANGE, FROM THE FIT POPULATION'S RAW FEATURES")
print(bar)
print("  key      : the 56 rows of target_scores at ranking_run_id = 2")
print("  joined   : protein_features.analysis_id = target_scores.analysis_id")
print("  columns  : the six D-027 FEATURE_NAMES, raw scale, read as the pharmfold-readonly role")
print("  percentile method: linear interpolation on the sorted sample (numpy 'linear')")
print(f"  rows loaded: {len(cohort)}   rows with a complete six-vector: "
      f"{sum(1 for r in cohort if all(v is not None for v in r['x']))}")
print()
print(f"  {'k':<2} {'feature':<26} {'min':>11} {'p05':>11} {'p25':>11} {'median':>11} "
      f"{'p75':>11} {'p95':>11} {'max':>11}")
print("  " + "-" * 96)
COH = {}
for k, name in enumerate(FEATURE_NAMES):
    xs = [r["x"][k] for r in cohort if r["x"][k] is not None]
    st = stats(xs)
    COH[k] = st
    COH[k]["values"] = xs
    print(f"  {k:<2} {name:<26} {st['min']:>11.5g} {st['p05']:>11.5g} {st['p25']:>11.5g} "
          f"{st['med']:>11.5g} {st['p75']:>11.5g} {st['p95']:>11.5g} {st['max']:>11.5g}")

print()
print(bar)
print("KA2 — TWO PATHS TO ONE QUANTITY: FD1's IMPLIED MEANS vs THE DIRECT MEANS OF THE 56")
print(bar)
print("  ⚠ If any disagrees, the fit population is NOT the 56 and every F-050 number needs re-keying.")
print()
print(f"  {'k':<2} {'feature':<26} {'FD1 implied':>16} {'direct mean/56':>16} "
      f"{'abs diff':>12} {'rel diff':>11}  verdict")
print("  " + "-" * 96)
ka2_ok = True
for k, name in enumerate(FEATURE_NAMES):
    direct = COH[k]["mean"]
    implied = FD1_MEAN[k]
    d = abs(direct - implied)
    rel = d / abs(implied) if implied else float("inf")
    ok = rel < 5e-6          # FD1's means were reported to ~8 significant figures
    ka2_ok &= ok
    print(f"  {k:<2} {name:<26} {implied:>16.8g} {direct:>16.8g} {d:>12.2e} {rel:>11.2e}"
          f"  {'AGREE' if ok else '⚠⚠ DISAGREE'}")
print(f"\n  {'ALL SIX AGREE — the fit population IS these 56.' if ka2_ok else '⚠⚠ STOP AND REPORT'}")

print()
print(bar)
print("KA3 — THE ±3 STANDARDIZED-UNIT BAR: THE METHOD, AND WHY IT IS NOT FITTING")
print(bar)
print("""  ⚠⚠ I FIRST WROTE THIS AS TWO INDEPENDENT PATHS AGREEING. THAT WAS WRONG, AND THE
     CORRECTION IS RECORDED HERE RATHER THAN PATCHED AWAY.

  The claimed recovery was:
    attribution_k(i) = coef_k * xhat_k(i)                        (proven exact in JB/FD1)
    "the standardizer was fit on these 56, so sd(xhat_k over 56) = 1"
    therefore sd(attribution_k) = |coef_k|,  and  sd_k = |coef_k| / |r_k|

  ⚠⚠ Work it through without assuming that middle step and it collapses to an IDENTITY:
    xhat_i    = (x_i - mean) / sd_k
    sd(xhat)  = sd_raw(56) / sd_k
    sd(attr)  = |coef_k| * sd_raw(56) / sd_k = |r_k| * sd_raw(56)
    so   sd(attr)/|r_k|  ==  sd_raw(56),  ALWAYS, whatever sd_k actually is.

  ⚠ "Path A" and "Path B" are therefore THE SAME PATH written twice. Their agreement below
     is arithmetic, not evidence, and it would have agreed to 1e-10 even if the standardizer
     had been fit on a different population entirely. Printed anyway, labelled as what it is.

  ⚠⚠ SO sd_k IS NOT RECOVERED, and F-049 amendment 1's surviving half STANDS: coef_k and
     sd_k remain entangled and only their ratio r_k is determined. What IS established is
     KA2 — the six MEANS match the raw means of these 56 exactly — which is real evidence
     the standardizer was fit on this population, but says nothing about the ddof used.

  THEREFORE the third bar is reported as: mean_k +/- 3 * sd_raw(56), and it equals a true
  +/-3 standardized units IF AND ONLY IF the standardizer used ddof=0 on these same 56.
  ⚠ ddof=1 moves it by ~0.9% (both printed). No model is fit; no value is standardized into
     any scorer; the bar is a descriptive threshold over a population KA1 already describes.""")
print()
print(f"  {'k':<2} {'feature':<26} {'sd(attr)/|r_k|':>17} {'sd raw ddof0':>17} "
      f"{'rel diff':>11}  {'B ddof1':>13}")
print("  " + "-" * 96)
SD = {}
a_b_agree = True
for k, name in enumerate(FEATURE_NAMES):
    attrs = [r["attr"][k] for r in cohort]
    coef_abs = sd(attrs, ddof=0)
    sd_a = coef_abs / abs(FD1_SLOPE[k])
    sd_b0 = sd(COH[k]["values"], ddof=0)
    sd_b1 = sd(COH[k]["values"], ddof=1)
    rel = abs(sd_a - sd_b0) / sd_b0
    a_b_agree &= rel < 1e-6
    SD[k] = sd_a
    print(f"  {k:<2} {name:<26} {sd_a:>17.9g} {sd_b0:>17.9g} {rel:>11.2e}  {sd_b1:>13.7g}")
print(f"\n  {'⚠ the two columns agree to ~1e-10 — as they MUST, algebraically. NOT a confirmation.' if a_b_agree else '⚠⚠ the columns DISAGREE, which under the identity above means a data error — REPORT.'}")
print("  ⚠ The ±3 bar below is mean_k +/- 3*sd_raw(56) at ddof=0, with the caveat above.")

# ── the census population ────────────────────────────────────────────────────
folded = [r for r in census if r["folded"]]
complete = [r for r in folded if all(v is not None for v in r["x"])]

print()
print(bar)
print("KC3 — HOW MANY OF THE CENSUS HAVE A COMPLETE SIX-FEATURE ROW AT ALL")
print(bar)
print(f"  census analyses (cohort_tranche > 0)              : {len(census)}")
print(f"  ⚠ of those, FOLDED (pdb_path IS NOT NULL)          : {len(folded)}   <- the denominator")
print(f"    not folded                                      : {len(census) - len(folded)}")
print(f"  ⚠⚠ folded AND carrying a complete six-vector       : {len(complete)}")
print(f"     shortfall                                      : {len(folded) - len(complete)}")
print("\n  the shortfall BY CAUSE — an absence is a category, never a zero:")
cause = Counter()
for r in folded:
    if not r["has_row"]:
        cause["no protein_features ROW at all"] += 1
    elif all(v is None for v in r["x"]):
        cause["features row exists, all six NULL"] += 1
    elif any(v is None for v in r["x"]):
        cause["features row exists, SOME of the six NULL"] += 1
    else:
        cause["complete six-vector"] += 1
for kk, v in cause.most_common():
    print(f"    {kk:44s} {v:5d}")
print(f"    {'TOTAL':44s} {sum(cause.values()):5d}")
partial = [r for r in folded if r["has_row"] and any(v is None for v in r["x"])
           and not all(v is None for v in r["x"])]
if partial:
    print("\n  ⚠ which columns are NULL in the partial rows:")
    pc = Counter()
    for r in partial:
        for k, v in enumerate(r["x"]):
            if v is None:
                pc[FEATURE_NAMES[k]] += 1
    for kk, v in pc.most_common():
        print(f"    {kk:30s} {v:5d}")

print()
print(bar)
print("KB1 — THE CENSUS DISTRIBUTION, SAME SIX STATISTICS")
print(bar)
print(f"  key        : protein_analyses.cohort_tranche IN (1,2,3,4), pdb_path IS NOT NULL")
print(f"  ⚠ DENOMINATOR: {len(folded)} folded — NOT 3,467 manifest, NOT {len(census)} census rows.")
print(f"  ⚠ statistics computed over the {len(complete)} rows carrying the feature; per-feature n stated.")
print()
print(f"  {'k':<2} {'feature':<26} {'n':>5} {'min':>11} {'p05':>11} {'median':>11} "
      f"{'p95':>11} {'max':>11}")
print("  " + "-" * 96)
CEN = {}
for k, name in enumerate(FEATURE_NAMES):
    xs = [r["x"][k] for r in folded if r["x"][k] is not None]
    if not xs:
        print(f"  {k:<2} {name:<26} {0:>5d}   NO VALUES EXIST — no census row carries this feature")
        continue
    st = stats(xs)
    CEN[k] = st
    print(f"  {k:<2} {name:<26} {st['n']:>5d} {st['min']:>11.5g} {st['p05']:>11.5g} "
          f"{st['med']:>11.5g} {st['p95']:>11.5g} {st['max']:>11.5g}")

print()
print(bar)
print("KB2 — THE OUT-OF-RANGE COUNT, AT THREE BARS, NOT ONE")
print(bar)
print(f"  ⚠ evaluated over the {len(complete)} folded census rows with a COMPLETE six-vector.")
print("  ⚠ 'no_features_row' is NOT 'out_of_range' and is reported separately at KC2/KC3.")
print()
if not complete:
    print("  " + "⚠" * 46)
    print("  KB2, KB3 AND KB4 HAVE NO DENOMINATOR, AND THAT IS THE ANSWER TO THE ORDER.")
    print("  " + "⚠" * 46)
    print(f"""
  Not one of the {len(folded)} folded census rows carries a protein_features row, so there is
  no census feature value to place inside or outside the cohort's range. The out-of-range
  count is not 0%, not 100%, and not small: it is UNDEFINED, because the input to the test
  does not exist.

  ⚠⚠ The order pre-registered two outcomes — 'largely inside the fit range' (ruling 1
     operative) and 'largely outside' (ruling 3 operative, refusal at scale). ⚠ THE MEASURED
     OUTCOME IS NEITHER. It is a third state the pre-registration did not enumerate: the
     question cannot be asked yet.

  ⚠ Reported rather than worked around. Extracting features over 2,690 census rows to make
     the test runnable is compute and is not ordered (§6), and inferring the distribution
     from the cohort would be inventing the measurement this order exists to take.

  ⚠ The Planner's recorded expectation — 'ecd_length the worst offender, mean_plddt_ecd the
     mildest, a MINORITY out of range on the strict test' — is NEITHER confirmed NOR
     contradicted. It stands untested, and the pre-registration that recorded it is intact.

  The one feature that CAN be placed without extraction is ecd_length, because it is the
  span length and the span is in the committed manifest. That is done at KC1.""")
    print()
    raise SystemExit(0)
print(f"  {'k':<2} {'feature':<26} {'strict min-max':>18} {'p05-p95':>16} {'+/-3 sd':>16}")
print("  " + "-" * 96)
FAIL = {k: {"strict": set(), "p0595": set(), "sd3": set()} for k in range(6)}
for k, name in enumerate(FEATURE_NAMES):
    lo_s, hi_s = COH[k]["min"], COH[k]["max"]
    lo_p, hi_p = COH[k]["p05"], COH[k]["p95"]
    lo_3, hi_3 = FD1_MEAN[k] - 3 * SD[k], FD1_MEAN[k] + 3 * SD[k]
    for r in complete:
        v = r["x"][k]
        if v < lo_s or v > hi_s:
            FAIL[k]["strict"].add(r["id"])
        if v < lo_p or v > hi_p:
            FAIL[k]["p0595"].add(r["id"])
        if v < lo_3 or v > hi_3:
            FAIL[k]["sd3"].add(r["id"])
    n = len(complete)
    print(f"  {k:<2} {name:<26} "
          f"{len(FAIL[k]['strict']):>7d} ({100*len(FAIL[k]['strict'])/n:5.1f}%) "
          f"{len(FAIL[k]['p0595']):>7d} ({100*len(FAIL[k]['p0595'])/n:4.1f}%) "
          f"{len(FAIL[k]['sd3']):>7d} ({100*len(FAIL[k]['sd3'])/n:4.1f}%)")
print()
print("  the bars themselves, in raw units:")
print(f"  {'k':<2} {'feature':<26} {'strict lo':>12} {'strict hi':>12} {'-3sd':>12} {'+3sd':>12}")
print("  " + "-" * 96)
for k, name in enumerate(FEATURE_NAMES):
    print(f"  {k:<2} {name:<26} {COH[k]['min']:>12.5g} {COH[k]['max']:>12.5g} "
          f"{FD1_MEAN[k]-3*SD[k]:>12.5g} {FD1_MEAN[k]+3*SD[k]:>12.5g}")

print()
print(bar)
print("KB3 — ⚠⚠ THE UNION. THIS IS THE NUMBER THAT DECIDES THE AMENDMENT")
print(bar)
n = len(complete)
for label, key in (("STRICT (cohort observed min-max)", "strict"),
                   ("p05-p95", "p0595"),
                   ("+/-3 standardized units", "sd3")):
    any_ = set()
    for k in range(6):
        any_ |= FAIL[k][key]
    all_ = set(r["id"] for r in complete)
    for k in range(6):
        all_ &= FAIL[k][key]
    print(f"  {label}")
    print(f"    out of range on AT LEAST ONE feature : {len(any_):5d} / {n}  = {100*len(any_)/n:5.1f}%"
          f"   -> a profile REFUSED for these")
    print(f"    out of range on ALL SIX              : {len(all_):5d} / {n}  = {100*len(all_)/n:5.1f}%")
    print(f"    ⚠ profile COMPUTABLE (in range on all six): {n-len(any_):5d} / {n}"
          f"  = {100*(n-len(any_))/n:5.1f}%")
    print()

print(bar)
print("KB4 — HOW MANY FEATURES EACH ROW FAILS: 0..6, SUMMING TO THE DENOMINATOR")
print(bar)
for label, key in (("STRICT", "strict"), ("p05-p95", "p0595"), ("+/-3 sd", "sd3")):
    dist = Counter()
    for r in complete:
        dist[sum(1 for k in range(6) if r["id"] in FAIL[k][key])] += 1
    print(f"  {label}:")
    for i in range(7):
        print(f"    fails {i} feature{'s' if i != 1 else ' '} : {dist.get(i, 0):5d}"
              f"   {100*dist.get(i,0)/n:5.1f}%")
    print(f"    {'TOTAL':17s}: {sum(dist.values()):5d}")
    print()

# stash for KC
import pickle  # noqa: E402
(SP / "k_state.pkl").write_bytes(pickle.dumps(
    {"FAIL": {k: {kk: vv for kk, vv in v.items()} for k, v in FAIL.items()},
     "complete_ids": [r["id"] for r in complete],
     "acc_by_id": {r["id"]: r["acc"] for r in census},
     "census": census, "COH": {k: {kk: vv for kk, vv in v.items() if kk != "values"}
                               for k, v in COH.items()}, "SD": SD}))
print("  (state written for KC)")
