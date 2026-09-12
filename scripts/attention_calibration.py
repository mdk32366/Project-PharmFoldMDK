#!/usr/bin/env python3
"""D-075 amendment 2's calibration: does tagged PubMed undercount track FAME? 82 targets.

    python scripts/attention_calibration.py --run          # fetches; writes the CSV
    python scripts/attention_calibration.py --report       # reads the CSV, no network

!! WHAT THIS TESTS, AND IT CAN SHRINK THE AMENDMENT THAT ORDERED IT.

`D-075 amendment 2` splits the popularity proxy into a tagged and an untagged PubMed arm on a
STATED MECHANISM: that `SYMBOL[Title/Abstract]` undercounts famous targets worst, because the
community writes `HER2` and the record says `ERBB2` - making the error ANTI-CORRELATED with the
measurand and flattening the contrast the control exists to detect.

  ! That mechanism is testable BEFORE the freeze, and this is the test.
  !! If the ratio atm/tagged is FLAT against an independent attention signal, the reasoning is
     WRONG and the disagreement clause shrinks accordingly. That outcome is acceptable.
     Discovering it AFTER the freeze is not.

! THIS IS A READ ON THE QUERY, NOT A RUN B RESULT. It computes no enrichment, touches no fold,
and freezes nothing. The freeze follows this report; they are not simultaneous.

! THE QUERY IS THE FETCHER'S OWN, MINUS ONE CLAUSE. `PUBMED_ENDPOINT` and the tagged template
come from `scripts/attention_control.py` verbatim; `AND (protein OR gene)` is dropped from both
arms per the amendment. A different query would be a different pre-registration.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
from typing import Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.attention_control import PUBMED_ENDPOINT       # noqa: E402 - the fetcher's own

#: The tagged arm, which is `attention_control.PUBMED_QUERY_TEMPLATE` with the clause the
#: amendment drops. ! Written out rather than string-surgered off the original, so what is sent
#: is readable here in full.
TAGGED = "{symbol}[Title/Abstract]"
#: The untagged arm. ! No field tag at all - the point is to let MeSH Automatic Term Mapping
#: resolve the gene CONCEPT rather than match the STRING.
UNTAGGED = "{symbol}"

#: NCBI allows 3 requests/second without a key. Two requests per target, 82 targets.
DELAY_S = 0.40

MAPPING = REPO / "data" / "cohort_82_mapping.csv"
OUT = REPO / "data" / "derived" / "attention_calibration_82.csv"
COLUMNS = ["symbol", "accession", "tagged", "atm", "ratio", "n_pdb", "pdb_present"]


def _count(query: str) -> Optional[int]:
    """One esearch call returning the hit count. ! `None` on any failure, never 0.

    !! A failed fetch that returns 0 is an absent measurement wearing a value - the defect this
    project has recorded more than once. The caller must be able to tell them apart.
    """
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json",
                                     "retmax": 0})
    try:
        with urllib.request.urlopen(f"{PUBMED_ENDPOINT}?{params}", timeout=30) as r:
            doc = json.loads(r.read().decode("utf-8"))
        return int(doc["esearchresult"]["count"])
    except Exception:                                        # noqa: BLE001
        return None


def _pdb_counts() -> dict[str, int]:
    """PDB entry counts per accession, measured 2026-09-11 and carried as a dated artifact.

    ! The INDEPENDENT attention signal. It is not derived from PubMed in any way, which is what
    makes it usable as the thing the ratio is tested against.
    """
    for cand in (REPO / "data" / "derived" / "cohort82_pdb_coverage.csv",
                 pathlib.Path.home() / "Downloads" /
                 "PharmFoldMDK-cohort82-pdb-ecd-coverage-2026-09-11.csv"):
        if cand.is_file():
            with open(cand, encoding="utf-8") as fh:
                return {r["accession"]: int(r["n_pdb"]) for r in csv.DictReader(fh)}
    raise SystemExit("refusing: no PDB coverage artifact found; the ratio has nothing to be "
                     "tested against and a correlation with nothing is not a measurement.")


def run() -> int:
    pdb = _pdb_counts()
    with open(MAPPING, encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("accession")]
    print(f"{len(rows)} targets; two esearch calls each at {DELAY_S}s apart "
          f"(NCBI 3 req/s, no key)")
    print(f"tagged  : {TAGGED}")
    print(f"untagged: {UNTAGGED}")
    print("! `AND (protein OR gene)` is dropped from both arms (D-075 amendment 2)\n")

    out = []
    for i, r in enumerate(rows, 1):
        sym, acc = r["symbol"], r["accession"]
        tagged = _count(TAGGED.format(symbol=sym))
        time.sleep(DELAY_S)
        atm = _count(UNTAGGED.format(symbol=sym))
        time.sleep(DELAY_S)
        ratio = (atm / tagged) if (tagged and atm is not None) else None
        n_pdb = pdb.get(acc)
        out.append({"symbol": sym, "accession": acc, "tagged": tagged, "atm": atm,
                    "ratio": None if ratio is None else round(ratio, 3),
                    "n_pdb": n_pdb,
                    "pdb_present": None if n_pdb is None else int(n_pdb > 0)})
        if i % 10 == 0 or i == len(rows):
            print(f"  {i:>3}/{len(rows)}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out)
    print(f"\nwrote {len(out)} rows to {OUT.relative_to(REPO).as_posix()}")
    return report()


def _spearman(xs: list[float], ys: list[float]) -> float:
    """Rank correlation, stdlib only. ! Rank rather than Pearson because the claim is MONOTONE
    ('largest for famous targets'), not linear, and n_pdb has a long tail that would let three
    outliers set a Pearson coefficient."""
    def ranks(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def report() -> int:
    if not OUT.is_file():
        print(f"refusing: {OUT.relative_to(REPO).as_posix()} does not exist; run --run first.",
              file=sys.stderr)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    usable = [r for r in rows if r["ratio"] and r["n_pdb"]]
    nulls = [r["symbol"] for r in rows if not r["ratio"]]
    print(f"{len(rows)} targets; {len(usable)} with both a ratio and a PDB count")
    if nulls:
        print(f"! null ratio on {len(nulls)}: {nulls}   (None is not 0)")

    ratios = [float(r["ratio"]) for r in usable]
    npdb = [float(r["n_pdb"]) for r in usable]
    ratios.sort()
    mid = len(ratios) // 2
    median = ratios[mid] if len(ratios) % 2 else (ratios[mid - 1] + ratios[mid]) / 2
    print(f"\nratio atm/tagged: min {min(ratios):.2f}  median {median:.2f}  "
          f"max {max(ratios):.2f}")

    rho = _spearman([float(r["ratio"]) for r in usable], npdb)
    print(f"\nTWO NUMBERS, NOT ONE (the order asks for both):")
    print(f"  Spearman rho(ratio, n_pdb) = {rho:+.3f}")

    # monotone check by quartile of n_pdb - a coefficient can be nonzero without the
    # relationship being monotone, and the claim is specifically about direction across fame.
    by_pdb = sorted(usable, key=lambda r: float(r["n_pdb"]))
    q = max(1, len(by_pdb) // 4)
    quarts = [by_pdb[i * q:(i + 1) * q] for i in range(4)]
    means = [sum(float(r["ratio"]) for r in g) / len(g) for g in quarts if g]
    print(f"  mean ratio by n_pdb quartile (low->high): "
          + " ".join(f"{m:.2f}" for m in means))
    monotone = all(a <= b for a, b in zip(means, means[1:]))
    print(f"  monotone increasing across quartiles: {monotone}")

    print(f"\nTHE CLAIM UNDER TEST: tagged undercount is largest for FAMOUS targets, so the ratio")
    print(f"should RISE with n_pdb. Verdict: ", end="")
    if rho > 0.3 and monotone:
        print("SUPPORTED - the mechanism D-075 amendment 2 states is visible in the data.")
    elif rho > 0.3:
        print("PARTIALLY SUPPORTED - correlated but not monotone across quartiles.")
    elif abs(rho) <= 0.3:
        print("NOT SUPPORTED - the ratio is FLAT against fame.")
        print("  !! The amendment's stated reasoning does not hold and the disagreement clause")
        print("     shrinks accordingly. This is the outcome the calibration exists to catch")
        print("     BEFORE the freeze, and it is acceptable.")
    else:
        print("CONTRADICTED - the ratio FALLS with fame, the opposite of the stated mechanism.")

    print("\n! This is a read on the QUERY. No enrichment was computed, no fold touched, nothing")
    print("  frozen. The freeze is a separate owner-authorised window.")

    print(f"\n{'symbol':<10}{'tagged':>9}{'atm':>9}{'ratio':>8}{'n_pdb':>7}")
    for r in sorted(rows, key=lambda r: -(float(r["n_pdb"]) if r["n_pdb"] else 0))[:12]:
        print(f"{r['symbol']:<10}{r['tagged']:>9}{r['atm']:>9}{r['ratio']:>8}{r['n_pdb']:>7}")
    print("  ... (full table in the CSV)")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/attention_calibration.py")
    ap.add_argument("--run", action="store_true", help="fetch both arms for all 82 and report")
    ap.add_argument("--report", action="store_true", help="report from the CSV, no network")
    args = ap.parse_args(argv)
    if args.run:
        return run()
    if args.report:
        return report()
    ap.print_help()
    return 2


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
