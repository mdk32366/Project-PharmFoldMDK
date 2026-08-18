"""Tasks M / N / O of `ORDERS-Code-2026-08-19` — the three straddle rules, measured side by side.

⚠⚠ **THERE ARE THREE RULES, NOT TWO**, and the third is the one that produced `D-095`'s founding
numbers:

| rule | predicate | behaviour | defined in |
|---|---|---|---|
| `admit_raw` | `b < s0 or a > s1` rejects | admits straddlers **UNCLIPPED** | `scripts/tranche6_domain_survey.py` |
| `drop`      | `a < s0 or b > s1` rejects | wholly-inside only, **drops** straddlers | `scripts/tranche6_runs.py` |
| `clip`      | any overlap, truncated to the span | admits straddlers **CLIPPED** | here, mirroring `bucket_domains` |

⚠ `admit_raw` had never been named anywhere in this project. A two-column table has already lost it.

The ruling (`CLOSEOUT-2026-08-18.md` §5, given a number by `D-095 amendment 1`) is **CLIP**.
⚠ **This script does not apply it.** It measures what applying it would change, so the amendment is
written against numbers rather than against an expectation. `R2`/`R3` of the orders: no behavioural
change to either shipped `domain_intervals`, and the divergence is disclosed, not reconciled.

⚠ Nothing is reimplemented. `merge`, `classify_regime`, and BOTH shipped `domain_intervals` are
IMPORTED from the modules that ship them, so if any of them moves this measurement moves too. Only
`clip_intervals` and `merge_overlap_only` are defined here, because nothing ships them.

⚠⚠ **`classify_regime` is NOT reordered** (`O1`, and `D-074` decision 3: name the check, do not build
the framework). The misfiling path is measured and reported with its zero instead.

READ-ONLY. Cache-only: no network, no database, no GPU. Writes no repo artifact.

Usage:
    python scripts/tranche6_runs_clip_compare.py
"""
from __future__ import annotations

import csv
import inspect
import json
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import MANIFEST, UNIPROT_CACHE, past_context_rows  # noqa: E402
from scripts.tranche6_domain_survey import merge  # noqa: E402
from scripts.tranche6_domain_survey import domain_intervals as admit_raw_intervals  # noqa: E402
from scripts.tranche6_runs import (  # noqa: E402
    TRAINED_CONTEXT,
    classify_regime,
    domain_intervals as drop_intervals,
)

LABELS = REPO / "data" / "census" / "census_labels.csv"
W = 100

#: The ten `D-095` subjects, as named in `scripts/tranche6_runs.py`.
TEN = ("Q14517", "Q9NYQ8", "Q8TDW7", "Q6V0I7", "Q07954",
       "Q9NZR2", "P98164", "O75445", "Q8WXG9", "Q86WI1")

REGIMES = ("no_domains", "single_run_only", "one_oversized_run",
           "multiple_oversized_runs", "all_runs_in_context")


def clip_intervals(doc: dict, s0: int, s1: int):
    """`Domain` + `Repeat` overlapping the span, CLIPPED to it — `bucket_domains`' rule.

    ⚠ The difference from the shipped `domain_intervals` is one predicate: it rejects a feature
    whose coordinates leave the span; this admits it and truncates it. A clipped straddler occupies
    its residues; dropping it manufactures a gap at the span boundary that does not exist in the
    molecule — **and a phantom gap is a phantom cut site.**
    """
    out = []
    for f in doc.get("features", []):
        if f.get("type") not in ("Domain", "Repeat"):
            continue
        a = f["location"]["start"].get("value")
        b = f["location"]["end"].get("value")
        if a is None or b is None:
            continue
        a, b = int(a), int(b)
        if b < s0 or a > s1:
            continue
        out.append((max(a, s0), min(b, s1), f.get("description", ""), f.get("type")))
    return sorted(out)


def merge_overlap_only(intervals) -> list[list[int]]:
    """The alternative merge rule — `start <= prev_end`, abutment NOT joined.

    ⚠⚠ Crossed with the straddle rule below, because **a rule applied to one shape and not another
    is not a rule.** `scripts/tranche6_runs.py` measures this axis under `drop` alone.
    """
    runs: list[list[int]] = []
    for a, b, *_ in intervals:
        if runs and a <= runs[-1][1]:
            runs[-1][1] = max(runs[-1][1], b)
        else:
            runs.append([a, b])
    return runs


def straddle_overhang(doc: dict, s0: int, s1: int) -> dict:
    """How far admitted features reach OUTSIDE the span, bucketed by direction.

    ⚠ **Past `s1` and before `s0` are different mistakes**, so they are never summed into one
    total. A feature crossing both ends is its own bucket rather than being counted twice under a
    label that says `only`, and it contributes to BOTH residue sums because it really does overhang
    in both directions.

    ⚠ Admission here is `admit_raw`'s predicate — the rule that produced `D-095`'s founding numbers.
    """
    o = {"n_admitted": 0, "n_wholly_inside": 0, "n_before_s0_only": 0,
         "n_past_s1_only": 0, "n_both_ends": 0,
         "residues_before_s0": 0, "residues_past_s1": 0}
    for a, b, *_ in admit_raw_intervals(doc, s0, s1):
        o["n_admitted"] += 1
        before, past = a < s0, b > s1
        if before:
            o["residues_before_s0"] += s0 - a
        if past:
            o["residues_past_s1"] += b - s1
        if before and past:
            o["n_both_ends"] += 1
        elif before:
            o["n_before_s0_only"] += 1
        elif past:
            o["n_past_s1_only"] += 1
        else:
            o["n_wholly_inside"] += 1
    return o


def misfiled_single_run(runs) -> bool:
    """Would `classify_regime` file this row as `single_run_only` while its run needs a cut?

    ⚠⚠ `classify_regime` returns on `len(runs) == 1` **before** `over` is computed, so a one-run
    protein past the trained context is filed as if no cut were needed and **vanishes from the
    six**. `D-074` decision 3 says name the check rather than build the framework, so this is the
    check — the classifier is NOT reordered.

    Expected 0 across the 141 today. **The zero is the measurement.**
    """
    return len(runs) == 1 and runs[0] > TRAINED_CONTEXT


def record(acc: str, gene: str, span_aa: int, iv, merge_fn=merge) -> dict:
    runs = [b - a + 1 for a, b in merge_fn(iv)]
    return {
        "acc": acc, "gene": gene, "span_aa": span_aa,
        "n_domains": len(iv), "n_runs": len(runs),
        "largest_run": max(runs) if runs else 0,
        "runs_over_context": sum(1 for x in runs if x > TRAINED_CONTEXT),
        "regime": classify_regime(n_domains=len(iv), runs=runs),
        "runs": runs,
    }


INTERVAL_RULES = (("admit_raw", admit_raw_intervals),
                  ("drop", drop_intervals),
                  ("clip", clip_intervals))
MERGE_RULES = (("abutting OR overlapping", merge), ("overlapping ONLY", merge_overlap_only))


def _doc(acc: str) -> dict:
    return json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))


def _manifest_rows() -> list[dict]:
    with MANIFEST.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _build(rows, genes, iv_fn, merge_fn) -> list[dict]:
    out = []
    for r in rows:
        acc = r["census_accession"]
        s0, s1 = int(r["span_start"]), int(r["span_end"])
        out.append(record(acc, genes.get(acc, ""), int(r["span_aa"]),
                          iv_fn(_doc(acc), s0, s1), merge_fn))
    return out


def _predicate_of(fn) -> str:
    for line in inspect.getsourcelines(fn)[0]:
        s = line.strip()
        if s.startswith("if ") and "s0" in s and "s1" in s:
            return s
    return "(clip: any overlap, truncated — see clip_intervals)"


# ══════════════════════════════════════════════════════════════════════════════════ the report ══

def task_m1() -> None:
    print("=" * W)
    print("TASK M1 — PROVENANCE OF THE 2x2. Which `domain_intervals` does the DROP column use?")
    print("=" * W)
    print("  ⚠ The import line in this file, quoted verbatim, not described:")
    src = pathlib.Path(__file__).read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(src, 1):
        s = line.strip()
        # ⚠ Only the import statements themselves — a looser match quotes this matcher's own
        # source back at the reader, which is a disclosure that names the wrong lines.
        if s.startswith("from scripts.tranche6") or s.startswith("domain_intervals as"):
            print(f"      {i:4d} | {line}")
    print()
    print(f"  {'rule':11s} {'module':38s} {'line':>5s}  predicate")
    print("  " + "-" * (W - 4))
    for name, fn in INTERVAL_RULES:
        if name == "clip":
            print(f"  {name:11s} {'scripts.tranche6_runs_clip_compare':38s} "
                  f"{inspect.getsourcelines(fn)[1]:5d}  (any overlap, truncated to [s0, s1])")
            continue
        print(f"  {name:11s} {fn.__module__:38s} {inspect.getsourcelines(fn)[1]:5d}  "
              f"{_predicate_of(fn)}")
    print(f"\n  ⚠ drop is admit_raw? {drop_intervals is admit_raw_intervals}   "
          f"— the DROP column is genuinely DROP, so the table below stands as measured.")


def task_m2(genes) -> None:
    print("\n" + "=" * W)
    print("TASK M2 — STRADDLERS UNDER `admit_raw`, bucketed BY DIRECTION, three populations")
    print("=" * W)
    print("  ⚠ past `s1` and before `s0` are DIFFERENT MISTAKES and are never summed together.")
    all_rows = _manifest_rows()
    the_141 = past_context_rows()
    the_ten = [r for r in all_rows if r["census_accession"] in TEN]
    pops = (("(a) the 141  [tranche=5 AND span_aa>1026 strictly, D-098]", the_141),
            ("(b) the ten  [D-095 subjects, D-091 r3]", the_ten),
            ("(c) full census  [census_manifest.v7.csv, every row]", all_rows))

    print(f"\n  {'population':52s} {'rows':>6s} {'feats':>7s} {'>s1':>5s} {'<s0':>5s} "
          f"{'both':>5s} {'res>s1':>8s} {'res<s0':>8s}")
    print("  " + "-" * (W - 4))
    for label, rows in pops:
        tot = Counter()
        for r in rows:
            o = straddle_overhang(_doc(r["census_accession"]),
                                  int(r["span_start"]), int(r["span_end"]))
            tot.update(o)
        print(f"  {label:52s} {len(rows):6d} {tot['n_admitted']:7d} "
              f"{tot['n_past_s1_only']:5d} {tot['n_before_s0_only']:5d} {tot['n_both_ends']:5d} "
              f"{tot['residues_past_s1']:8d} {tot['residues_before_s0']:8d}")
    print("\n  ⚠ CACHE COVERAGE, stated rather than assumed — an absence would be a category:")
    cached = {p.stem for p in UNIPROT_CACHE.glob('*.json')}
    absent = [r['census_accession'] for r in all_rows if r['census_accession'] not in cached]
    print(f"      manifest rows with a cached UniProt doc : {len(all_rows) - len(absent)} "
          f"of {len(all_rows)}   absent: {len(absent)}  {absent[:5] if absent else ''}")


def task_m3(genes) -> None:
    print("\n" + "=" * W)
    print("TASK M3 — THE TEN `D-095` SUBJECTS UNDER ALL THREE RULES (merge rule = shipped)")
    print("=" * W)
    rows = [r for r in _manifest_rows() if r["census_accession"] in TEN]
    built = {name: {x["acc"]: x for x in _build(rows, genes, fn, merge)}
             for name, fn in INTERVAL_RULES}
    print(f"  {'acc':9s} {'gene':9s} {'rule':11s} {'doms':>5s} {'runs':>5s} "
          f"{'largest':>8s} {'>ctx':>5s}")
    print("  " + "-" * (W - 4))
    for acc in TEN:
        for name, _ in INTERVAL_RULES:
            x = built[name][acc]
            print(f"  {acc if name == 'admit_raw' else '':9s} "
                  f"{x['gene'] if name == 'admit_raw' else '':9s} {name:11s} "
                  f"{x['n_domains']:5d} {x['n_runs']:5d} {x['largest_run']:8d} "
                  f"{x['runs_over_context']:5d}")
        print()
    print("  ⚠⚠ THE TWO FOUNDING NUMBERS OF `D-095` — do they move?")
    for acc, gene, founding in (("Q14517", "FAT1", 2289), ("Q6V0I7", "FAT4", 3037)):
        vals = {name: built[name][acc]["largest_run"] for name, _ in INTERVAL_RULES}
        moved = len(set(vals.values())) > 1
        print(f"      {gene} largest_run — D-095 records {founding}.  " +
              "  ".join(f"{k}={v}" for k, v in vals.items()) +
              f"   MOVES: {moved}")
    print("      ⚠ `D-095` was computed by `tranche6_domain_survey.py`, whose rule is `admit_raw`.")


def task_m4(genes) -> None:
    print("\n" + "=" * W)
    print("TASK M4 — THE 2x3: merge_rule x straddle_rule, on the 141")
    print("=" * W)
    print("  merge_rule `abutting OR overlapping` = `start <= prev_end + 1`")
    print("    ⚠ GAP TOLERANCE IS ZERO UNCOVERED RESIDUES: 100-200 + 201-300 joins (adjacent);")
    print("      100-200 + 202-300 does not (one uncovered residue at 201).")
    rows = past_context_rows()
    print(f"\n  {'merge_rule':24s} {'straddle':10s} {'runs':>6s} {'rows>ctx':>9s} "
          f"{'FAT1':>5s}  oversized set (ACCESSIONS, not a count)")
    print("  " + "-" * (W - 4))
    for m_label, m_fn in MERGE_RULES:
        for s_label, s_fn in INTERVAL_RULES:
            recs = _build(rows, genes, s_fn, m_fn)
            over = sorted(x["acc"] for x in recs if x["runs_over_context"] > 0)
            fat1 = next(x["n_runs"] for x in recs if x["acc"] == "Q14517")
            shipped = "  <- SHIPPED" if (m_label, s_label) == (
                "abutting OR overlapping", "drop") else ""
            print(f"  {m_label:24s} {s_label:10s} {sum(x['n_runs'] for x in recs):6d} "
                  f"{len(over):9d} {fat1:5d}  {over if over else '(empty)'}{shipped}")
    print("\n  ⚠⚠ READ THE `rows>ctx` COLUMN. Under `overlapping ONLY` it is ZERO under ALL THREE")
    print("     straddle rules. The six rows needing a cut exist because abutment is joined.")
    print("  ⚠ straddle_rule moves the run TOTAL. merge_rule moves WHICH ROWS NEED A CUT.")


def task_n(genes) -> None:
    print("\n" + "=" * W)
    print("TASK N — THE +3 / +2 RECONCILIATION, by named interval")
    print("=" * W)
    rows = {r["census_accession"]: r for r in past_context_rows()}
    for acc in ("Q9Y493", "Q6V1P9"):
        r = rows[acc]
        s0, s1 = int(r["span_start"]), int(r["span_end"])
        doc = _doc(acc)
        d_iv, c_iv = drop_intervals(doc, s0, s1), clip_intervals(doc, s0, s1)
        added = [iv for iv in c_iv if (iv[0], iv[1]) not in {(x[0], x[1]) for x in d_iv}]
        print(f"\n  {acc} / {genes.get(acc, '')}   span {s0}-{s1}")
        print(f"    intervals: drop {len(d_iv)} -> clip {len(c_iv)}  (+{len(c_iv) - len(d_iv)})")
        for a, b, desc, typ in added:
            src = next(iv for iv in admit_raw_intervals(doc, s0, s1)
                       if max(iv[0], s0) == a and min(iv[1], s1) == b)
            end = "past s1" if src[1] > s1 else ("before s0" if src[0] < s0 else "?")
            print(f"      ADDED  {a}-{b}  (raw {src[0]}-{src[1]}, {end})  {typ}: {desc[:44]}")
        for m_label, m_fn in MERGE_RULES:
            rd, rc = m_fn(d_iv), m_fn(c_iv)
            delta = len(rc) - len(rd)
            # ⚠ Two paths to one quantity: predict the delta from the intervals, then compare.
            new_runs = bridged = absorbed = 0
            gap = 1 if m_label.startswith("abutting") else 0
            for a, b, *_ in added:
                touch = [run for run in rd if a <= run[1] + gap and b >= run[0] - gap]
                if not touch:
                    new_runs += 1
                elif len(touch) == 1:
                    absorbed += 1
                else:
                    bridged += len(touch) - 1
            predicted = new_runs - bridged
            ok = "OK" if predicted == delta else "*** DOES NOT RECONCILE ***"
            print(f"    {m_label:24s} runs {len(rd)} -> {len(rc)}  delta {delta:+d}   "
                  f"predicted {predicted:+d} (new {new_runs}, absorbed {absorbed}, "
                  f"bridged {bridged})  [{ok}]")
    print("\n  ⚠ The census-wide totals this accounts for: overlapping-ONLY 2,264 -> 2,266 (+2),")
    print("    abutting-OR-overlapping 1,532 -> 1,532 (+0). Three intervals arrive in both cases;")
    print("    ⚠⚠ the +0 is the stronger check, because a run count that does not move is exactly")
    print("    what an interval silently failing to arrive would also look like.")


def task_o2(genes) -> None:
    print("\n" + "=" * W)
    print("TASK O2 — THE `classify_regime` MISFILING PATH, named not built")
    print("=" * W)
    print("  ⚠ `classify_regime` returns `single_run_only` on `len(runs) == 1` BEFORE `over` is")
    print("    computed, so a one-run protein past context would vanish from the six.")
    print("    ⚠⚠ NOT REORDERED (O1). Counted, and reported with its zero:\n")
    rows = past_context_rows()
    for s_label, s_fn in INTERVAL_RULES:
        recs = _build(rows, genes, s_fn, merge)
        n = sum(1 for x in recs if misfiled_single_run(x["runs"]))
        print(f"    single_run_only rows whose single run exceeds context "
              f"[{s_label:10s}] : {n}")
    print("\n  ⚠ The disjointness of `single_run_only` from the oversized set is therefore a DATA")
    print("    FACT with a named risk, never a proof. `D-095 amendment 1` records it that way.")


def task_regimes(genes) -> None:
    print("\n" + "=" * W)
    print("REGIME CENSUS — five regimes, every outcome named including the zeros")
    print("=" * W)
    rows = past_context_rows()
    built = {name: _build(rows, genes, fn, merge) for name, fn in INTERVAL_RULES}
    print(f"  {'regime':28s} " + " ".join(f"{n:>10s}" for n, _ in INTERVAL_RULES))
    print("  " + "-" * (W - 4))
    for name in REGIMES:
        cells = [Counter(x["regime"] for x in built[r]).get(name, 0) for r, _ in INTERVAL_RULES]
        print(f"  {name:28s} " + " ".join(f"{c:10d}" for c in cells))
    print(f"  {'TOTAL':28s} " + " ".join(f"{len(built[r]):10d}" for r, _ in INTERVAL_RULES))

    print("\n  ⚠ SINGLE_RUN_ONLY, per rule — disjoint from the oversized set?")
    for r, _ in INTERVAL_RULES:
        sro = [x for x in built[r] if x["regime"] == "single_run_only"]
        print(f"    {r:10s} n={len(sro)} — " +
              " · ".join(f"{x['acc']}/{x['gene']} largest_run={x['largest_run']}" for x in sro) +
              f"   any oversized? {any(x['runs_over_context'] for x in sro)}")

    print("\n  ⚠ THE OVERSIZED SET, per rule, AS ACCESSIONS")
    for r, _ in INTERVAL_RULES:
        over = sorted(x["acc"] for x in built[r] if x["runs_over_context"] > 0)
        print(f"    {r:10s} n={len(over)}  {over}")

    print("\n  PER-ROW CHANGES, drop -> clip (every field)")
    n_changed = 0
    for a, b in zip(built["drop"], built["clip"]):
        diffs = {k: (a[k], b[k]) for k in ("n_domains", "n_runs", "largest_run",
                                           "runs_over_context", "regime") if a[k] != b[k]}
        if diffs:
            n_changed += 1
            print(f"    {a['acc']:9s} {a['gene']:10s} " +
                  "  ".join(f"{k}: {v[0]} -> {v[1]}" for k, v in diffs.items()))
    print(f"    rows changed: {n_changed} of {len(built['drop'])}   "
          f"unchanged: {len(built['drop']) - n_changed}")

    print("\n  THE 275 RESIDUES — two paths to one quantity, compared on the COUNTS")
    for r, _ in INTERVAL_RULES:
        tot_span = sum(x["span_aa"] for x in built[r])
        tot_in = sum(sum(x["runs"]) for x in built[r])
        note = ""
        if r == "admit_raw":
            note = "   ⚠ EXCEEDS the span: counts residues the span does not contain"
        print(f"    {r:10s} span {tot_span:,}  in-run {tot_in:,} "
              f"({100 * tot_in / tot_span:.1f}%)  outside {tot_span - tot_in:,}{note}")
    di = sum(sum(x["runs"]) for x in built["drop"])
    ci = sum(sum(x["runs"]) for x in built["clip"])
    print(f"    ⚠ clip - drop = {ci - di:,} residues  — and `tranche6_domains.uniprot.csv` "
          f"(Task A) records {ci:,}.")


def main() -> int:
    with LABELS.open(encoding="utf-8") as fh:
        genes = {r["census_accession"]: r["gene"] for r in csv.DictReader(fh)}
    task_m1()
    task_m2(genes)
    task_m3(genes)
    task_m4(genes)
    task_n(genes)
    task_o2(genes)
    task_regimes(genes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
