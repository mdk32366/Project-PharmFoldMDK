"""Pre-fit intersection check — D-041 §5 floor cost, and the labelled-and-folded set.

Run from the repo root, against the LIVE deployment:

    python scripts/intersection_check.py

Reads nothing but the public read API and two committed CSVs. Standard library only.
Every number it prints is a pre-registered finding (D-041) — record it whatever it says.

CORRECTED per ORDERS-Code-2026-07-27-ADDENDUM-intersection.md: the ranking denominator is
`folded AND disposition == "ranked" AND mean_plddt >= 50`, NOT `folded AND mean_plddt >= 50`.
held_out (D-021 §1a / D-024) targets are boundary-method incomparable and must not be counted.

CORRECTED AGAIN per D-073, closing the two errors F-002 recorded against this instrument on
2026-07-27 but never fixed in it:

  1. `/api/analyses` is the ENQUEUED set, not the folded set — `core/enqueue.py` writes a
     `protein_analyses` row at enqueue time. Report A used to print its row count under the
     label "folded". The folded set comes from `/api/coverage`, the D-038 honest-denominator
     supplier, whose rows carry a per-target `fold_status`.
  2. A FAILED fold is not a low-confidence one. The below-floor predicate used to be
     `plddt is None or plddt < FLOOR`, which absorbed IGF2R (`fold_status=failed`, null pLDDT)
     into the below-floor bucket — the D-043 error class reproduced inside the instrument
     built to measure it. Failed folds are now reported separately.

No dated figure is hardcoded here, so re-running this after the cohort moves produces the new
truth rather than re-asserting the old one.
"""

import csv
import json
import urllib.request

API = "https://pharmfoldmdk.fly.dev"
FLOOR = 50.0  # D-041 §5, D-039 bands


def read_csv_skipping_comments(path):
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def fetch(path):
    with urllib.request.urlopen(f"{API}{path}", timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---- the fold partition, from /api/coverage (F-002 error 1: this, not /api/analyses) ----
cov = fetch("/api/coverage")
cov_rows = cov.get("rows", [])
fold_status = {r["gene"]: r.get("fold_status") for r in cov_rows if r.get("gene")}

folded_genes = {g for g, s in fold_status.items() if s == "folded"}
failed_genes = {g for g, s in fold_status.items() if s == "failed"}
not_folded_genes = {g for g, s in fold_status.items() if s == "not_folded"}

# ---- the enqueued set, from /api/analyses (a row exists from ENQUEUE time onward) ----
payload = fetch("/api/analyses")
rows = payload if isinstance(payload, list) else payload.get("analyses", payload.get("items", []))

enqueued = {}
for r in rows:
    gene = r.get("gene")
    if gene:
        enqueued[gene] = (r.get("mean_plddt"), r.get("disposition"), r.get("held_out"))


def ok(v):
    plddt, disp, _ = v
    return plddt is not None and plddt >= FLOOR and disp == "ranked"


ranked = {g: v for g, v in enqueued.items() if v[1] == "ranked"}
rankable = {g: v for g, v in enqueued.items() if ok(v)}  # D = folded AND ranked AND >= floor
held_out = {g for g, v in enqueued.items() if v[1] == "held_out"}

# Below the floor, over FOLDED targets only — a failed fold has no confidence to be below it.
below = {
    g: v[0]
    for g, v in enqueued.items()
    if g in folded_genes and (v[0] is None or v[0] < FLOOR)
}

# F-002 Finding 1 was "every ranked target is folded, 67 of 67". That is an observation about
# the cohort, not a guarantee — assert it so a future divergence is announced rather than
# silently changing what the ranking denominator D means.
ranked_not_folded = sorted(set(ranked) - folded_genes)
if ranked_not_folded:
    print(f"!! F-002 Finding 1 NO LONGER HOLDS: ranked but not folded -> {ranked_not_folded}\n")

# The partition must reconcile (F-002). If it stops reconciling, the reports below are unsafe.
c = cov["coverage"]
assert c["ranked"] + c["held_out"] + c["excluded"] == c["denominator"], c
assert len(folded_genes) + len(failed_genes) + len(not_folded_genes) == c["denominator"], (
    len(folded_genes), len(failed_genes), len(not_folded_genes), c["denominator"]
)

# ---- the label candidates and the comparator, from committed files ---------
review = read_csv_skipping_comments("data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv")
probable = {r["symbol"] for r in review if r["curation_status"] == "review_as_probable_group_b"}
needs_check = {r["symbol"] for r in review if r["curation_status"] == "needs_literature_check"}

evidence = {r["symbol"] for r in read_csv_skipping_comments("data/evidence_scores.csv")}

# ---- the reports A-I -------------------------------------------------------
n_folded = len(folded_genes)
print("== ORDERS ADDENDUM reports A-I ==")
print(f"   enqueued rows (/api/analyses) ....... {len(enqueued)}   [NOT a fold count — F-002 error 1]")
print(f"A. folded (/api/coverage fold_status) . {n_folded} of {c['denominator']}"
      f"   (+{len(failed_genes)} failed, +{len(not_folded_genes)} not folded)")
pct = 100.0 * len(below) / n_folded if n_folded else 0.0
print(f"B. folded AND pLDDT < 50 .............. {len(below)} of {n_folded}  ({pct:.1f}%)  [supersedes D-041 sec5 ~24% on 42]")
print(f"   failed folds, reported separately ... {len(failed_genes)}  -> {sorted(failed_genes)}   [F-002 error 2]")
print(f"C. folded AND disposition==ranked .... {len(ranked)}  (before the floor)")
print(f"D. folded AND ranked AND pLDDT >= 50 . {len(rankable)}  <== THE RANKING DENOMINATOR")

fit_set = sorted(probable & set(rankable))
print(f"E. probable positives AND D .......... {len(fit_set)} of {len(probable)} candidates (provisional fit set)")
print(f"   -> {fit_set}")

prob_held_out = sorted(probable & held_out)
print(f"F. probable positives that are held_out {len(prob_held_out)}  (silently included by the old script)")
print(f"   -> {prob_held_out}")

comparator = sorted(evidence & set(rankable))
print(f"G. evidence score AND D .............. {len(comparator)} of {len(evidence)}  (D-059 denominator)")
print(f"   -> {comparator}")

head_to_head = sorted(set(fit_set) & set(comparator))
print(f"H. E intersect G ..................... {len(head_to_head)}  (D-041 dec-3 head-to-head denominator)")
print(f"   -> {head_to_head}")

unchecked_rankable = sorted(needs_check & set(rankable))
print(f"I. needs_literature_check AND D ...... {len(unchecked_rankable)}  (owner's live curation headroom)")
print(f"   -> {unchecked_rankable}")

# ---- probable positives that fall out entirely (context, not a report) -----
lost = sorted(probable - set(rankable))
print(f"\n   probable positives NOT in D: {len(lost)}")
for g in lost:
    if g in held_out:
        print(f"   {g:10s} held_out (mean pLDDT {enqueued[g][0]})")
    elif g in failed_genes:
        print(f"   {g:10s} fold FAILED (no pLDDT) — not a confidence result")
    elif g in below:
        print(f"   {g:10s} below floor (mean pLDDT {below[g]})")
    elif g not in folded_genes:
        print(f"   {g:10s} not folded")
    else:
        print(f"   {g:10s} disposition={enqueued[g][1]}")

# ---- the partition, printed so it can be read against F-002 ----------------
print("\n== the partition (F-002) ==")
print(f"{c['denominator']} = {c['ranked']} ranked + {c['held_out']} held_out + {c['excluded']} excluded")
print(f"{n_folded} folded + {len(failed_genes)} failed + {len(not_folded_genes)} not_folded"
      f" = {c['denominator']}")
print(f"   failed     -> {sorted(failed_genes)}")
print(f"   not_folded -> {sorted(not_folded_genes)}")
