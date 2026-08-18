"""Task L — the RUN analysis across the 141. Cache-only, no GPU.

⚠⚠ THE RUN/DOMAIN DISTINCTION IS THE SUBJECT, AND `D-095`'s CENTRAL QUANTITY. Every individual
domain in the ten subjects is inside the 1,026 aa trained context — the largest anywhere is 247 aa
— but domains ABUT. FAT1's cadherin repeats share exact boundaries (`35-149`, `150-257`, …), so 39
domains collapse into 9 runs, one of **2,289 aa**; FAT4's is **3,037**. ⚠ **A run has no linker to
cut at**, so the design question is not *where are the seams* but *where to sever a continuous
stack*.

⚠ `merge()` is IMPORTED from `scripts/tranche6_domain_survey.py`, not reimplemented. Its docstring
preserves the original error — reporting a merged run as a single domain — so reusing it makes the
correction load-bearing rather than commemorative. **This couples Task L to that file**, which was
slated for deletion after the equivalence run; the deletion now has a third gate, recorded here so
it is not discovered later.

⚠⚠ THE PRE-REGISTERED QUESTION: `D-095` describes TWO regimes — *one oversized run* (FAT1–4) and
*natural seams already exist* (the other six). **Ten subjects cannot establish a taxonomy for 141.**
So the classifier below can express FIVE outcomes, and the question is which of them actually
occur. A classifier with only two outcomes could not answer the question it was built for.

    python scripts/tranche6_runs.py
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import UNIPROT_CACHE, past_context_rows  # noqa: E402
from scripts.tranche6_domain_survey import merge  # noqa: E402  — see module docstring

TRAINED_CONTEXT = 1026
LABELS = REPO / "data" / "census" / "census_labels.csv"
OUT = REPO / "data" / "census" / "tranche6_runs.csv"

#: ⚠ Every outcome is NAMED. A regime the reporter cannot name is a regime that gets silently
#: bucketed into a neighbour — which is how ten subjects become a taxonomy for 141.
REGIMES = (
    "no_domains",              # ⚠ nothing to tile on. Assembly is undefined, not hard.
    "single_run_only",         # one run and nothing else — no seam anywhere, not merely none big
    "one_oversized_run",       # D-095's regime A: exactly one run past context, others in context
    "multiple_oversized_runs",  # ⚠ NOT in D-095. More than one cut needed, in more than one place.
    "all_runs_in_context",     # D-095's regime B: natural seams already exist
)


def classify_regime(*, n_domains: int, runs: list[int]) -> str:
    if n_domains == 0 or not runs:
        return "no_domains"
    if len(runs) == 1:
        return "single_run_only"
    over = sum(1 for r in runs if r > TRAINED_CONTEXT)
    if over == 0:
        return "all_runs_in_context"
    return "one_oversized_run" if over == 1 else "multiple_oversized_runs"


def domain_intervals(doc: dict, s0: int, s1: int):
    """`Domain` + `Repeat` wholly inside the span. ⚠ `Repeat` is not optional — dropping it loses
    34 LDL-receptor class B repeats from LRP1 alone (`D-095` decision 1(b))."""
    out = []
    for f in doc.get("features", []):
        if f.get("type") not in ("Domain", "Repeat"):
            continue
        a = f["location"]["start"].get("value")
        b = f["location"]["end"].get("value")
        if a is None or b is None or a < s0 or b > s1:
            continue
        out.append((int(a), int(b), f.get("description", ""), f.get("type")))
    return sorted(out)


def main() -> int:
    rows = past_context_rows()
    genes = {}
    with LABELS.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            genes[r["census_accession"]] = r["gene"]

    recs = []
    for r in rows:
        acc = r["census_accession"]
        s0, s1 = int(r["span_start"]), int(r["span_end"])
        doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
        iv = domain_intervals(doc, s0, s1)
        runs = [b - a + 1 for a, b in merge(iv)]
        recs.append({
            "acc": acc, "gene": genes.get(acc, ""), "span_aa": int(r["span_aa"]),
            "n_domains": len(iv), "n_runs": len(runs),
            "largest_run": max(runs) if runs else 0,
            "runs_over_context": sum(1 for x in runs if x > TRAINED_CONTEXT),
            "regime": classify_regime(n_domains=len(iv), runs=runs),
            "runs": runs,
        })

    print("=" * 96)
    print("TASK L — runs across the 141 (D-098 scope), Domain+Repeat merged per accession")
    print(f"key: one row per census_accession · a RUN is a maximal abutting/overlapping stretch")
    print("=" * 96)

    c = Counter(x["regime"] for x in recs)
    print("\n⚠ REGIME CENSUS — does D-095's two-regime split hold across 141?")
    print("-" * 96)
    for name in REGIMES:
        n = c.get(name, 0)
        tag = ""
        if name == "multiple_oversized_runs" and n:
            tag = "  ⚠⚠ NOT IN D-095 — a THIRD regime, unseen on ten subjects"
        if name == "no_domains" and n:
            tag = "  ⚠ nothing to tile on: assembly is UNDEFINED, not hard"
        if name == "single_run_only" and n:
            tag = "  ⚠ no seam anywhere, not merely none in the big run"
        print(f"  {name:26s} {n:4d}{tag}")
    print(f"  {'TOTAL':26s} {len(recs):4d}")

    d095_two = c.get("one_oversized_run", 0) + c.get("all_runs_in_context", 0)
    other = len(recs) - d095_two
    print(f"\n  ⚠ rows D-095's taxonomy covers : {d095_two} of {len(recs)} "
          f"({100*d095_two/len(recs):.1f}%)")
    print(f"  ⚠⚠ rows it does NOT cover      : {other} ({100*other/len(recs):.1f}%)")

    print("\n" + "=" * 96)
    print("RUNS PAST CONTEXT — how many cuts, and where")
    print("=" * 96)
    over = [x for x in recs if x["runs_over_context"] > 0]
    print(f"  rows with at least one run > {TRAINED_CONTEXT} aa : {len(over)} of {len(recs)}")
    print(f"  total oversized runs across the 141        : {sum(x['runs_over_context'] for x in recs)}")
    print(f"\n  {'acc':9s} {'gene':10s} {'span':>6s} {'doms':>5s} {'runs':>5s} {'largest':>8s} "
          f"{'>ctx':>5s}  regime")
    print("  " + "-" * 86)
    for x in sorted(over, key=lambda z: -z["largest_run"])[:20]:
        print(f"  {x['acc']:9s} {x['gene']:10s} {x['span_aa']:6d} {x['n_domains']:5d} "
              f"{x['n_runs']:5d} {x['largest_run']:8d} {x['runs_over_context']:5d}  {x['regime']}")

    print("\n" + "=" * 96)
    print("⚠ THE TEN vs THE 131 — is the taxonomy from the ten representative?")
    print("=" * 96)
    TEN = {"Q14517", "Q9NYQ8", "Q8TDW7", "Q6V0I7", "Q07954",
           "Q9NZR2", "P98164", "O75445", "Q8WXG9", "Q86WI1"}
    for label, sel in (("the ten (D-091 r3)", [x for x in recs if x["acc"] in TEN]),
                       ("the other 131", [x for x in recs if x["acc"] not in TEN])):
        cc = Counter(x["regime"] for x in sel)
        print(f"\n  {label} — n={len(sel)}")
        for name in REGIMES:
            if cc.get(name):
                print(f"    {name:26s} {cc[name]:4d}")

    # ── ⚠ THE MERGE RULE, STATED — it is a choice and it changes the answer ──────────────────
    print("\n" + "=" * 96)
    print("⚠⚠ THE MERGE RULE IS A CHOICE AND MUST BE STATED, NOT ABSORBED")
    print("=" * 96)
    print("  SHIPPED RULE: abutting OR overlapping — `start <= prev_end + 1`.")
    print("    100-200 + 201-300 -> ONE run of 201 aa.  100-200 + 202-300 -> TWO runs.")
    print("  ⚠ The alternative — overlapping ONLY (`start <= prev_end`) — gives a different")
    print("    answer, and on abutting cadherin repeats it gives a WILDLY different one.")
    print()

    def merge_overlap_only(intervals):
        runs = []
        for a, b, *_ in intervals:
            if runs and a <= runs[-1][1]:
                runs[-1][1] = max(runs[-1][1], b)
            else:
                runs.append([a, b])
        return runs

    print(f"  {'rule':28s} {'total runs':>11s} {'rows w/ run>ctx':>16s} {'FAT1 runs':>10s}")
    print("  " + "-" * 70)
    fat1 = next((x for x in recs if x["acc"] == "Q14517"), None)
    tot_shipped = sum(x["n_runs"] for x in recs)
    over_shipped = sum(1 for x in recs if x["runs_over_context"] > 0)
    print(f"  {'abutting OR overlapping':28s} {tot_shipped:11d} {over_shipped:16d} "
          f"{fat1['n_runs'] if fat1 else 0:10d}   <- SHIPPED")

    tot_ov = over_ov = 0
    fat1_ov = 0
    for r in rows:
        acc = r["census_accession"]
        s0, s1 = int(r["span_start"]), int(r["span_end"])
        doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
        rr = [b - a + 1 for a, b in merge_overlap_only(domain_intervals(doc, s0, s1))]
        tot_ov += len(rr)
        if any(x > TRAINED_CONTEXT for x in rr):
            over_ov += 1
        if acc == "Q14517":
            fat1_ov = len(rr)
    print(f"  {'overlapping ONLY':28s} {tot_ov:11d} {over_ov:16d} {fat1_ov:10d}")
    print(f"\n  ⚠ FAT1: {fat1['n_runs'] if fat1 else 0} runs under the shipped rule, {fat1_ov} "
          f"under overlap-only. **The abutment IS the phenomenon** — a rule that")
    print("    does not join abutting intervals cannot see a cadherin stack at all.")

    # ── residues in runs vs outside ──────────────────────────────────────────────────────────
    print("\n" + "=" * 96)
    print("RESIDUES IN RUNS vs OUTSIDE (within the V2 span)")
    print("=" * 96)
    tot_span = tot_in = 0
    for x, r in zip(recs, rows):
        tot_span += x["span_aa"]
        tot_in += sum(x["runs"])
    print(f"  span residues total : {tot_span:,}")
    print(f"  inside a run        : {tot_in:,} ({100*tot_in/tot_span:.1f}%)")
    print(f"  ⚠ outside every run : {tot_span-tot_in:,} ({100*(tot_span-tot_in)/tot_span:.1f}%)")

    # ── distribution of largest run ──────────────────────────────────────────────────────────
    print("\n" + "=" * 96)
    print("DISTRIBUTION OF LARGEST RUN — ⚠ the 10 zero-domain rows carry NO run")
    print("   (a category with a cause, not a largest-run of zero)")
    print("=" * 96)
    bands = [(0, 0), (1, 200), (201, 400), (401, 700), (701, 1026), (1027, 2000), (2001, 99999)]
    for lo, hi in bands:
        if lo == 0 and hi == 0:
            n = sum(1 for x in recs if x["n_domains"] == 0)
            print(f"  {'no domains at all':>18s} : {n:4d}   ⚠ category, not a zero")
            continue
        n = sum(1 for x in recs if x["n_domains"] > 0 and lo <= x["largest_run"] <= hi)
        label = f"{lo:,}-{hi:,}" if hi < 99999 else f"{lo:,}+"
        mark = "   ⚠ past the trained context" if lo > TRAINED_CONTEXT else ""
        print(f"  {label:>18s} : {n:4d}{mark}")

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["acc", "gene", "span_aa", "n_domains", "n_runs",
                                           "largest_run", "runs_over_context", "regime"])
        w.writeheader()
        for x in recs:
            w.writerow({k: x[k] for k in w.fieldnames})
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
