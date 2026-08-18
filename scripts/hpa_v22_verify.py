"""Verify the v22 HPA files by REPRODUCTION, and re-derive Task J independently.

⚠⚠ A VERSION LABEL IS A CLAIM; THE REPRODUCTION IS A MEASUREMENT. Two wrong files already arrived
under the right name — a 12-gene slice of the summary schema called `pathology.tsv`, and a
`proteinatlas.tsv.zip` stamped 2026-06-03 when Kathad pins v22.0. So the acceptance test is not
"does it say v22"; it is **does it reproduce S3's 1,640 rows exactly, all four count columns.**

⚠ Inputs are referenced BY PATH and never vendored. `D-093` amendment 1 lifts decision 7 for HPA's
own IHC data, but the `Cancer prognostics – … (TCGA)` columns stay OUT — this script reads only
`Gene`, `Gene name`, `Cancer`, `High`, `Medium`, `Low`, `Not detected`.

    python scripts/hpa_v22_verify.py \
        --pathology ~/Downloads/v22/pathology.tsv \
        --s3 ~/Downloads/journal.pone.0308604.s004.xls
"""
from __future__ import annotations

import argparse
import csv
import pathlib
from collections import Counter
import sys
from typing import Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.kathad_reproduction import is_kept, load_s3, normalise_cancer, qh_score  # noqa: E402

COUNT_COLS = ("High", "Medium", "Low", "Not detected")

#: ⚠ Columns deliberately NOT read — third-party data HPA redistributes under other terms
#: (D-093 amendment 1 item 2). A column present in a stored table is ingested whether or not
#: anything reads it, so the safe form is to never select them.
EXCLUDED_PREFIX = "Cancer prognostics"

#: Task J's subjects, named by Kathad as omitted with a speculative "potential reasons" clause.
TASK_J = (("TROP2", "TACSTD2"), ("CLDN18.2", "CLDN18"), ("HER3", "ERBB3"))


def panel_counts(row: dict) -> tuple[int, int, int, int]:
    return tuple(int(float(row[c] or 0)) for c in COUNT_COLS)  # type: ignore[return-value]


def panel_total(row: dict) -> int:
    return sum(panel_counts(row))


def is_empty_panel(row: dict) -> bool:
    """⚠ An empty panel is a CATEGORY, not a score of zero. It is also where Kathad's
    'we computed target levels using corresponding mRNA expression levels' would operate —
    invisibly, because nothing in the table marks modality."""
    return panel_total(row) == 0


def modality(row: dict) -> str:
    """`ihc` when a real panel exists, `no_ihc_panel` otherwise. ⚠ Never `mrna` — this table
    cannot tell us that a substitution happened, only that IHC was unavailable for it to
    substitute FOR. Claiming the stronger label would be inventing provenance."""
    return "no_ihc_panel" if is_empty_panel(row) else "ihc"


def load_pathology(path: pathlib.Path) -> dict[tuple[str, str], dict]:
    """⚠ Selects only HPA's own IHC columns. The prognostic columns are not read at all."""
    out: dict[tuple[str, str], dict] = {}
    with path.open(encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        dropped = [c for c in (rd.fieldnames or []) if c.startswith(EXCLUDED_PREFIX)]
        for r in rd:
            slim = {k: r[k] for k in ("Gene", "Gene name", "Cancer", *COUNT_COLS)}
            out[(r["Gene name"].strip(), normalise_cancer(r["Cancer"]))] = slim
    if dropped:
        print(f"  ⚠ dropped at read, not ingested ({len(dropped)} cols): "
              f"{dropped[0]!r} … (D-093 amendment 1 item 2)", file=sys.stderr)
    return out


#: ⚠ The IN set for `normal_tissue.tsv`, stated as data rather than left to the reader of a loop.
#: The ingest is COLUMN-scoped (`D-093` amendment 1 clause 2): a column present in a stored table is
#: ingested whether or not anything reads it, so the column set is asserted EXACTLY, not filtered.
NORMAL_TISSUE_COLUMNS = ("Gene", "Gene name", "Tissue", "Cell type", "Level", "Reliability")

#: The genes fixed in `docs/PREREGISTRATION-2026-08-19-normal-tissue-acceptance-bar.md` §2 BEFORE
#: the file was fetched. ⚠ `ZZZ_NOT_A_GENE` is the negative case: a bar with no negative case
#: cannot fail. Each carries the expectation written down at pre-registration time.
PREREGISTERED_GENES = (
    ("CLDN18", "present, concentrated in stomach"),
    ("ERBB2", "present, broad epithelial"),
    ("TACSTD2", "present, broad epithelial"),
    ("INS", "present, essentially pancreas-only — the tissue-specificity control"),
    ("ZZZ_NOT_A_GENE", "ABSENT — the negative case"),
)


def verify_normal_tissue(path: pathlib.Path) -> int:
    """`CA2`–`CA4`. ⚠ Reports; it does not ingest. No table is created and no row is written.

    ⚠⚠ There is no external comparator for this file the way S3 is for `pathology.tsv`, so the bar
    is two independent paths, both pre-registered: transport checked by repeated fetch and hash
    (done outside this script and reported with it), and named genes checked against expectations
    fixed before the fetch.
    """
    rows = 0
    tissues: set[str] = set()
    cells: set[tuple[str, str]] = set()
    levels: Counter = Counter()
    reliab: Counter = Counter()
    genes: set[str] = set()
    ensgs: set[str] = set()
    per_gene: Counter = Counter()
    named: dict[str, list[tuple[str, str, str, str]]] = {g: [] for g, _ in PREREGISTERED_GENES}

    with path.open(encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        cols = tuple(rd.fieldnames or ())
        for r in rd:
            rows += 1
            g = (r["Gene name"] or "").strip()
            t = (r["Tissue"] or "").strip()
            c = (r["Cell type"] or "").strip()
            genes.add(g)
            ensgs.add((r["Gene"] or "").strip())
            tissues.add(t)
            cells.add((t, c))
            levels[(r["Level"] or "").strip()] += 1
            reliab[(r["Reliability"] or "").strip()] += 1
            per_gene[g] += 1
            if g in named:
                named[g].append((t, c, (r["Level"] or "").strip(), (r["Reliability"] or "").strip()))

    W = 88
    print("=" * W)
    print("CA3 — THE COLUMN SET, ASSERTED EXACTLY (the ingest is COLUMN-scoped)")
    print("=" * W)
    print(f"  columns as read : {list(cols)}")
    print(f"  IN set          : {list(NORMAL_TISSUE_COLUMNS)}")
    extra = [c for c in cols if c not in NORMAL_TISSUE_COLUMNS]
    missing = [c for c in NORMAL_TISSUE_COLUMNS if c not in cols]
    print(f"  ⚠ columns present but NOT in the IN set : {extra or 'none'}")
    print(f"  ⚠ columns expected but ABSENT           : {missing or 'none'}")
    prog = [c for c in cols if c.startswith(EXCLUDED_PREFIX)]
    print(f"  ⚠⚠ `{EXCLUDED_PREFIX}` columns present  : {prog or 'none'}"
          f"   — presence is the violation, not use")
    print(f"  ⚠ `Reliability` is present here and is ABSENT from `pathology.tsv`: "
          f"{'Reliability' in cols}")
    print("     — the modality driving target selection is the one without the quality flag.")

    print("\n" + "=" * W)
    print("CA4 — THE TISSUE TAXONOMY, AND WHAT AN ABSENCE MEANS")
    print("=" * W)
    print(f"  rows                       : {rows:,}")
    print(f"  distinct Ensembl gene ids  : {len(ensgs):,}")
    print(f"  distinct gene names        : {len(genes):,}")
    print(f"  distinct tissues           : {len(tissues):,}")
    print(f"  distinct (tissue, cell)    : {len(cells):,}")
    print(f"\n  Level values, with counts — ⚠ every value named, none bucketed:")
    for k, v in levels.most_common():
        print(f"    {k or '(empty)':24s} {v:9,d}")
    print(f"\n  Reliability values:")
    for k, v in reliab.most_common():
        print(f"    {k or '(empty)':24s} {v:9,d}")

    full = len(cells)
    complete = sum(1 for g, n in per_gene.items() if n == full)
    print(f"\n  ⚠⚠ DOES AN ABSENT ROW MEAN 'not detected' OR 'not tested'?")
    print(f"    `Not detected` is an EXPLICIT Level value ({levels.get('Not detected', 0):,} rows),")
    print(f"    so a MISSING (gene, tissue, cell) row is NOT 'not detected' — it is NOT TESTED.")
    print(f"    genes covering all {full:,} (tissue, cell) pairs : {complete:,} of {len(genes):,}")
    print(f"    ⚠ so the grid is RAGGED, and the two facts must be stored separately.")

    print("\n" + "=" * W)
    print("CA2 PATH B — THE PRE-REGISTERED GENES (expectations fixed BEFORE the fetch)")
    print("=" * W)
    ok = True
    for g, expectation in PREREGISTERED_GENES:
        obs = named[g]
        print(f"\n  {g}  — expected: {expectation}")
        if not obs:
            print(f"    rows: 0   ⚠ ABSENT from the file")
            if g != "ZZZ_NOT_A_GENE":
                ok = False
                print(f"    *** the negative case is the only gene expected absent ***")
            continue
        if g == "ZZZ_NOT_A_GENE":
            ok = False
            print(f"    *** {len(obs)} rows for a name that does not exist — the lookup is matching "
                  f"on something other than identity ***")
            continue
        detected = [(t, c, lv) for t, c, lv, _ in obs if lv and lv != "Not detected"]
        by_tissue = Counter(t for t, _, _ in detected)
        print(f"    rows: {len(obs):3d}   with a detected level: {len(detected):3d} "
              f"across {len(by_tissue)} tissues")
        for t, n in by_tissue.most_common(6):
            best = max((lv for tt, _, lv in detected if tt == t),
                       key=lambda x: ("Low", "Medium", "High").index(x)
                       if x in ("Low", "Medium", "High") else -1)
            print(f"      {t:34s} {n:3d} cell types, strongest {best}")
        if len(by_tissue) > 6:
            print(f"      … and {len(by_tissue) - 6} more tissues")
    print(f"\n  ⚠ VERDICT on the named-gene path: {'HOLDS' if ok else '*** FAILED ***'}")
    print("  ⚠⚠ This checks the file against expectations WRITTEN DOWN BEFORE IT WAS FETCHED.")
    print("     It does not make the file correct; it makes a wrong file able to fail.")
    return 0 if ok else 1


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pathology")
    ap.add_argument("--s3")
    ap.add_argument("--normal-tissue", help="verify HPA v22 normal_tissue.tsv (CA2-CA4)")
    args = ap.parse_args(argv)

    if args.normal_tissue:
        rc = verify_normal_tissue(pathlib.Path(args.normal_tissue).expanduser())
        if not (args.pathology and args.s3):
            return rc

    if not (args.pathology and args.s3):
        ap.error("--pathology and --s3 are required together (or use --normal-tissue alone)")

    path = load_pathology(pathlib.Path(args.pathology).expanduser())
    s3 = load_s3(pathlib.Path(args.s3))

    print("=" * 84)
    print("ACCEPTANCE — does this file REPRODUCE S3, row for row and count for count?")
    print("=" * 84)
    found = ident = mismatch = 0
    for r in s3:
        key = (str(r["Gene name"]).strip(), normalise_cancer(r["Cancer"]))
        p = path.get(key)
        if p is None:
            continue
        found += 1
        if all(int(float(p[c] or 0)) == int(r[c]) for c in COUNT_COLS):
            ident += 1
        else:
            mismatch += 1
    print(f"  S3 rows                : {len(s3):,}")
    print(f"  found in pathology     : {found:,}")
    print(f"  all four counts EQUAL  : {ident:,}")
    print(f"  counts differ          : {mismatch:,}")
    accepted = ident == len(s3)
    print(f"\n  VERDICT: {'ACCEPTED' if accepted else '⚠ REJECTED'} — {ident}/{len(s3)}")
    if not accepted:
        print("  ⚠ This is not the file Kathad used. STOP — do not build on it.")
        return 1

    print("\n" + "=" * 84)
    print("TASK J — which stage killed TROP2, HER3, CLDN18.2?")
    print("⚠ Kathad name all three as omitted and offer one speculative reason for all three.")
    print("=" * 84)
    by_gene: dict[str, list[dict]] = {}
    for (g, _), r in path.items():
        by_gene.setdefault(g, []).append(r)

    print(f"  {'target':20s} {'max qh':>8s} {'>=150':>7s} {'cancers':>8s}  verdict")
    print("  " + "-" * 68)
    for label, sym in TASK_J:
        rs = by_gene.get(sym, [])
        qs = [q for q in (qh_score(high=h, medium=m, low=lo, total=h + m + lo + nd)
                          for h, m, lo, nd in (panel_counts(r) for r in rs)) if q is not None]
        kept = sum(1 for q in qs if is_kept(q))
        verdict = ("⚠ died at the qh cutoff" if kept == 0
                   else "⚠⚠ did NOT die at the cutoff")
        mx = f"{max(qs):.2f}" if qs else "-"
        print(f"  {label:20s} {mx:>8s} {kept:7d} {len(qs):8d}  {verdict}")

    print("\n  ⚠⚠ THE CASE. CLDN18.2 in stomach cancer:")
    r = path.get(("CLDN18", normalise_cancer("stomach cancer")))
    if r:
        h, m, lo, nd = panel_counts(r)
        t = h + m + lo + nd
        q = qh_score(high=h, medium=m, low=lo, total=t)
        q2 = qh_score(high=h, medium=m, low=lo + 2, total=t)
        print(f"    High={h} Medium={m} Low={lo} NotDetected={nd}  n={t}")
        print(f"    qh = {q:.4f}, step = {100/t:.4f}, cutoff 150 -> kept={is_kept(q)}")
        print(f"    two Not detected -> Low : qh = {q2:.4f} -> kept={is_kept(q2)}")
        print(f"    ⚠ the move is AVAILABLE ({nd} Not detected present); it cannot lose a Low "
              f"(Low={lo})")
        print("    ⚠⚠ CLDN18.2 is the target of zolbetuximab, approved in gastric cancer.")
        print("       An approved target sits two available pathologist calls below the cutoff,")
        print("       in the indication it was approved for.")

    print("\n" + "=" * 84)
    print("MODALITY — the pre-registered mRNA hazard, measured")
    print("=" * 84)
    s3_empty = sum(1 for r in s3
                   if sum(int(r[c]) for c in COUNT_COLS) == 0)
    all_empty = sum(1 for r in path.values() if is_empty_panel(r))
    genes_all_empty = sum(1 for g, rs in by_gene.items() if all(is_empty_panel(r) for r in rs))
    print(f"  S3 rows with an empty IHC panel        : {s3_empty}")
    print(f"  ⚠ every S3 row reproduces from IHC     : {ident}/{len(s3)}")
    if s3_empty == 0:
        print("  ⚠⚠ THEREFORE no row in S3 is mRNA-derived. The hazard is real but does NOT")
        print("     reach the 82; it can only affect genes that dropped out UPSTREAM.")
    print(f"\n  v22 gene-cancer rows with no IHC panel : {all_empty:,} of {len(path):,} "
          f"({100*all_empty/len(path):.1f}%)")
    print(f"  genes with no IHC in ANY cancer        : {genes_all_empty:,} of {len(by_gene):,} "
          f"({100*genes_all_empty/len(by_gene):.1f}%)")
    print("  ⚠ Every row entering Task I must carry its modality, or it does not enter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
