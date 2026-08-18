"""Tasks M / N / O of `ORDERS-Code-2026-08-19` — the three straddle rules, measured side by side.

⚠⚠ **THERE ARE THREE RULES, NOT TWO**, and the third is the one that produced `D-095`'s founding
numbers:

| rule | behaviour | pre-reconciliation home (at `7011e24`) |
|---|---|---|
| `admit_raw` | admits straddlers **UNCLIPPED** | `scripts/tranche6_domain_survey.py:67` |
| `drop`      | wholly-inside only, **drops** straddlers | `scripts/tranche6_runs.py:64` |
| `clip`      | admits straddlers **CLIPPED** to the span | ⚠ ruled but unimplemented |

⚠ `admit_raw` had never been named anywhere in this project. A two-column table has already lost it.

⚠⚠ **THE THREE ARE NOW ONE FUNCTION**, `scripts/tranche6_domain_census.domain_intervals`, taking
`straddle` as a **keyword-only argument with no default** — a caller that omits it gets a
`TypeError`, not a behaviour. The divergence is recorded at `7591164` (measured against the
divergent code, per `R3`'s sequence) and closed by the commit carrying this line. Byte-identity
against all three pre-change implementations is proven cache-wide by
`scripts/tranche6_domain_intervals_equivalence.py`, on hashes of serialised intervals rather than
on counts.

The ruling (`CLOSEOUT-2026-08-18.md` §5, given a number by `D-095 amendment 1`) is **CLIP**.
⚠ **This script still does not apply it** — it reports all three side by side. Reconciling the
implementations is not the same as choosing between the rules, and only the second is a decision.

⚠ Nothing is reimplemented. `domain_intervals`, `merge` and `classify_regime` are IMPORTED from the
modules that ship them, so if any of them moves this measurement moves too. Only
`merge_overlap_only` is defined here, because nothing ships it.

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

from scripts.tranche6_domain_census import (  # noqa: E402
    MANIFEST,
    SPAN_RELATIONS,
    STRADDLE_RULES,
    UNIPROT_CACHE,
    domain_intervals,
    past_context_rows,
    span_relation,
)
from scripts.tranche6_domain_survey import merge  # noqa: E402
from scripts.tranche6_runs import TRAINED_CONTEXT, classify_regime  # noqa: E402

LABELS = REPO / "data" / "census" / "census_labels.csv"
W = 100

#: The ten `D-095` subjects, as named in `scripts/tranche6_runs.py`.
TEN = ("Q14517", "Q9NYQ8", "Q8TDW7", "Q6V0I7", "Q07954",
       "Q9NZR2", "P98164", "O75445", "Q8WXG9", "Q86WI1")

REGIMES = ("no_domains", "single_run_only", "one_oversized_run",
           "multiple_oversized_runs", "all_runs_in_context")


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
    """The FOUR-WAY partition of admitted features against the span, with residue magnitudes.

    ⚠⚠ **This replaces a three-column `past s1 / before s0 / both` shape, and the fourth column is
    not a refinement — it is a different object.** *"Both ends"* reads as *two overhangs*, but a
    feature crossing both boundaries has **no edge inside the span at all**: it is a claim that one
    annotation covers the entire span and then some. `clip` maps it onto exactly `[s0, s1]`, which
    is the unruled case (`UnruledEngulfingFeature`).

    ⚠ **Past `s1` and before `s0` remain different mistakes** and are never summed together.
    Admission is `admit_raw`'s predicate — the rule that produced `D-095`'s founding numbers.
    """
    o = {"n_admitted": 0, "residues_before_s0": 0, "residues_past_s1": 0}
    o.update({f"n_{k}": 0 for k in SPAN_RELATIONS})
    for a, b, *_ in domain_intervals(doc, s0, s1, straddle="admit_raw"):
        o["n_admitted"] += 1
        if a < s0:
            o["residues_before_s0"] += s0 - a
        if b > s1:
            o["residues_past_s1"] += b - s1
        o[f"n_{span_relation(a, b, s0, s1)}"] += 1
    return o


def no_domains_cause(doc: dict, s0: int, s1: int) -> str | None:
    """Why a row has no domains UNDER `drop` — a category, never a bare zero.

    ⚠⚠ One of these causes is new and is the reason this exists: a protein whose only overlapping
    features **engulf** the span reports `no_domains` under `drop` **because its features were
    dropped**, not because it carries no annotation. *An absence and a rejection are different
    facts and they were arriving under one label.*
    """
    if domain_intervals(doc, s0, s1, straddle="drop"):
        return None
    domainlike = [f for f in doc.get("features", []) if f.get("type") in ("Domain", "Repeat")]
    if not domainlike:
        return "no_domainlike_features_in_the_chain"
    admitted = domain_intervals(doc, s0, s1, straddle="admit_raw")
    if not admitted:
        return "features_exist_but_none_overlaps_the_span"
    rels = {span_relation(a, b, s0, s1) for a, b, *_ in admitted}
    if rels == {"engulfing"}:
        return "all_overlapping_features_ENGULF_the_span"
    if "engulfing" in rels:
        return "dropped_mixed_engulfing_and_overhang"
    return "all_overlapping_features_overhang_a_boundary"


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


#: ⚠ Three NAMES against ONE function. Before the reconciliation these were three separate
#: callables in two modules; the divergence is recorded at 7591164 and closed here.
INTERVAL_RULES = tuple((r, r) for r in STRADDLE_RULES)
MERGE_RULES = (("abutting OR overlapping", merge), ("overlapping ONLY", merge_overlap_only))


def _doc(acc: str) -> dict:
    return json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))


def _manifest_rows() -> list[dict]:
    with MANIFEST.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _build(rows, genes, rule, merge_fn) -> list[dict]:
    out = []
    for r in rows:
        acc = r["census_accession"]
        s0, s1 = int(r["span_start"]), int(r["span_end"])
        out.append(record(acc, genes.get(acc, ""), int(r["span_aa"]),
                          domain_intervals(_doc(acc), s0, s1, straddle=rule), merge_fn))
    return out


# ══════════════════════════════════════════════════════════════════════════════════ the report ══

def task_m1() -> None:
    print("=" * W)
    print("TASK M1 — PROVENANCE. Which `domain_intervals` does each column use?")
    print("=" * W)
    print("  ⚠ The import lines in this file, quoted verbatim, not described:")
    src = pathlib.Path(__file__).read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(src, 1):
        s = line.strip()
        # ⚠ Only the import statements themselves — a looser match quotes this matcher's own
        # source back at the reader, which is a disclosure that names the wrong lines.
        if s.startswith("from scripts.tranche6") or s in ("domain_intervals,",):
            print(f"      {i:4d} | {line}")

    print("\n  ⚠⚠ POST-RECONCILIATION: all three columns are ONE function under three NAMES.")
    print(f"      {'module':44s} {'line':>5s}  signature")
    print("      " + "-" * (W - 8))
    sig = inspect.signature(domain_intervals)
    print(f"      {domain_intervals.__module__:44s} "
          f"{inspect.getsourcelines(domain_intervals)[1]:5d}  domain_intervals{sig}")
    print(f"      rules: {STRADDLE_RULES}")

    # ⚠ The contract is asserted at run time, not asserted in prose. A default would silently
    # restore exactly the ambiguity this task exists to close.
    has_default = sig.parameters["straddle"].default is not inspect.Parameter.empty
    kw_only = sig.parameters["straddle"].kind is inspect.Parameter.KEYWORD_ONLY
    try:
        domain_intervals({}, 1, 10)
        omitted = "RETURNED A VALUE  *** the argument is optional ***"
    except TypeError as exc:
        omitted = f"TypeError: {exc}"
    try:
        domain_intervals({}, 1, 10, straddle="nonsense")
        unknown = "RETURNED A VALUE  *** an unknown rule was coerced ***"
    except ValueError as exc:
        unknown = f"{type(exc).__name__}: {exc}"
    print(f"\n      straddle is keyword-only : {kw_only}")
    print(f"      straddle has a default   : {has_default}   (⚠ must be False)")
    print(f"      omitting it              : {omitted}")
    print(f"      an unrecognised rule     : {unknown}")
    print("\n  ⚠ Before 7591164 the DROP column came from `scripts.tranche6_runs` and the")
    print("    ADMIT_RAW column from `scripts.tranche6_domain_survey`, and the measurement at")
    print("    that commit was taken against those two divergent functions, by R3's sequence.")


def task_m2(genes) -> None:
    print("\n" + "=" * W)
    print("TASK M2 / U2 — THE FOUR-WAY PARTITION under `admit_raw`, three populations")
    print("=" * W)
    print("  ⚠ `engulfing` is NOT a refinement of `both ends` — a feature crossing both boundaries")
    print("    has no edge inside the span, and `clip` has no ruling for it (it REFUSES).")
    print("  ⚠ features AND the distinct accessions they touch: 58 features on 58 proteins and")
    print("    58 features on 6 proteins would be different findings.")
    all_rows = _manifest_rows()
    the_141 = past_context_rows()
    the_ten = [r for r in all_rows if r["census_accession"] in TEN]
    pops = (("(a) the 141  [tranche=5 AND span_aa>1026 strictly, D-098]", the_141),
            ("(b) the ten  [D-095 subjects, D-091 r3]", the_ten),
            ("(c) full census  [census_manifest.v7.csv, every row]", all_rows))

    print(f"\n  {'population':52s} {'rows':>5s} {'feats':>6s} "
          + " ".join(f"{r:>11s}" for r in SPAN_RELATIONS))
    print("  " + "-" * (W - 4))
    for label, rows in pops:
        tot = Counter()
        accs = {r: set() for r in SPAN_RELATIONS}
        for r in rows:
            o = straddle_overhang(_doc(r["census_accession"]),
                                  int(r["span_start"]), int(r["span_end"]))
            tot.update(o)
            for rel in SPAN_RELATIONS:
                if o[f"n_{rel}"]:
                    accs[rel].add(r["census_accession"])
        print(f"  {label:52s} {len(rows):5d} {tot['n_admitted']:6d} "
              + " ".join(f"{tot['n_' + r]:11d}" for r in SPAN_RELATIONS))
        print(f"  {'':52s} {'':5s} {'accs:':>6s} "
              + " ".join(f"{len(accs[r]):11d}" for r in SPAN_RELATIONS))
        print(f"  {'':52s} residues before s0 {tot['residues_before_s0']:6d}   "
              f"past s1 {tot['residues_past_s1']:6d}")
    print("\n  ⚠ CACHE COVERAGE, stated rather than assumed — an absence would be a category:")
    cached = {p.stem for p in UNIPROT_CACHE.glob('*.json')}
    absent = [r['census_accession'] for r in all_rows if r['census_accession'] not in cached]
    print(f"      manifest rows with a cached UniProt doc : {len(all_rows) - len(absent)} "
          f"of {len(all_rows)}   absent: {len(absent)}  {absent[:5] if absent else ''}")


def task_u3(genes) -> None:
    print("\n" + "=" * W)
    print("TASK U3 — WHAT THE ENGULFING FEATURES ACTUALLY ARE")
    print("=" * W)
    eng = []
    for r in _manifest_rows():
        acc = r["census_accession"]
        s0, s1 = int(r["span_start"]), int(r["span_end"])
        for a, b, desc, typ in domain_intervals(_doc(acc), s0, s1, straddle="admit_raw"):
            if span_relation(a, b, s0, s1) == "engulfing":
                eng.append((acc, s0, s1, a, b, typ, desc))
    print(f"  engulfing features: {len(eng)}   distinct accessions: {len({e[0] for e in eng})}"
          f"   -> {'one each' if len(eng) == len({e[0] for e in eng}) else 'CONCENTRATED'}")
    print(f"  type: {dict(Counter(e[5] for e in eng))}")
    print(f"  flush at s0 (a == s0): {sum(1 for e in eng if e[3] == e[1])}    "
          f"flush at s1 (b == s1): {sum(1 for e in eng if e[4] == e[2])}    "
          f"strictly beyond both: {sum(1 for e in eng if e[3] < e[1] and e[4] > e[2])}")
    lens = sorted(e[2] - e[1] + 1 for e in eng)
    print(f"  span length of the affected rows: min {lens[0]}  median {lens[len(lens)//2]}  "
          f"max {lens[-1]}")
    print(f"  ⚠⚠ any of them past the {TRAINED_CONTEXT} aa trained context? "
          f"{sum(1 for x in lens if x > TRAINED_CONTEXT)}  — so none can enter tranche 6 today")
    print("\n  top descriptions:")
    for d, n in Counter(e[6] for e in eng).most_common(8):
        print(f"    {n:3d}  {d[:64]}")
    print("\n  ⚠ Read the descriptions: MARVEL, ABC transmembrane, Cytochrome b561, KASH, HIG1,")
    print("    UPAR/Ly6 are POLYTOPIC MEMBRANE domains. The V2 span here is a short extracellular")
    print("    loop INSIDE a larger transmembrane domain — so engulfment is not an annotation")
    print("    artifact, it is what a loop in a multi-pass protein looks like. ⚠⚠ That is an")
    print("    argument for a rule, and the rule is the owner's; this reports it, nothing more.")


def task_u5(genes) -> None:
    print("\n" + "=" * W)
    print("TASK U5 — `no_domains` IS A CATEGORY WITH A CAUSE, AND ONE CAUSE IS NEW")
    print("=" * W)
    print("  ⚠ A row whose only overlapping features ENGULF the span reports `no_domains` under")
    print("    `drop` because they were DROPPED, not because it carries no annotation.")
    for label, rows in (("the 141", past_context_rows()), ("full census", _manifest_rows())):
        causes = Counter()
        rows_by_cause = {}
        for r in rows:
            acc = r["census_accession"]
            c = no_domains_cause(_doc(acc), int(r["span_start"]), int(r["span_end"]))
            if c:
                causes[c] += 1
                rows_by_cause.setdefault(c, []).append(acc)
        print(f"\n  {label} — rows with no domains under `drop`: {sum(causes.values())} "
              f"of {len(rows)}")
        for c in ("no_domainlike_features_in_the_chain",
                  "features_exist_but_none_overlaps_the_span",
                  "all_overlapping_features_overhang_a_boundary",
                  "all_overlapping_features_ENGULF_the_span",
                  "dropped_mixed_engulfing_and_overhang"):
            n = causes.get(c, 0)
            mark = "   ⚠⚠ the new cause" if c.endswith("ENGULF_the_span") and n else ""
            print(f"    {c:46s} {n:5d}{mark}")
            if n and c != "no_domainlike_features_in_the_chain" and label == "the 141":
                print(f"      {rows_by_cause[c]}")
        # ⚠ The partition check must compare against an INDEPENDENTLY counted total. `sum ==
        # sum` is a tautology that prints True whatever the causes do, which is a check-shaped
        # object rather than a check.
        independent = sum(1 for r in rows
                          if not domain_intervals(_doc(r["census_accession"]),
                                                  int(r["span_start"]), int(r["span_end"]),
                                                  straddle="drop"))
        print(f"    {'TOTAL':46s} {sum(causes.values()):5d}   ⚠ causes sum to the "
              f"independently counted {independent} no-domain rows: "
              f"{sum(causes.values()) == independent}")


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
        d_iv = domain_intervals(doc, s0, s1, straddle="drop")
        c_iv = domain_intervals(doc, s0, s1, straddle="clip")
        added = [iv for iv in c_iv if (iv[0], iv[1]) not in {(x[0], x[1]) for x in d_iv}]
        print(f"\n  {acc} / {genes.get(acc, '')}   span {s0}-{s1}")
        print(f"    intervals: drop {len(d_iv)} -> clip {len(c_iv)}  (+{len(c_iv) - len(d_iv)})")
        for a, b, desc, typ in added:
            src = next(iv for iv in domain_intervals(doc, s0, s1, straddle="admit_raw")
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
                    print(f"      {m_label:24s} {a}-{b} became its OWN run (touches nothing)")
                elif len(touch) == 1:
                    absorbed += 1
                    # ⚠ NAME the run it merged into. "absorbed 1" is a count; the order asked
                    # which interval, and a count cannot be checked against the molecule.
                    print(f"      {m_label:24s} {a}-{b} ABSORBED into run "
                          f"{touch[0][0]}-{touch[0][1]}")
                else:
                    bridged += len(touch) - 1
                    print(f"      {m_label:24s} {a}-{b} BRIDGED {len(touch)} runs: "
                          f"{[f'{r[0]}-{r[1]}' for r in touch]}")
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
    task_u3(genes)
    task_u5(genes)
    task_m3(genes)
    task_m4(genes)
    task_n(genes)
    task_o2(genes)
    task_regimes(genes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
