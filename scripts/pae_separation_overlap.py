"""Task H — does an intra/inter separation-overlap window exist? Over the 20 matrices on disk.

⚠⚠ WHY THIS GATES THE COMPARISON. PAE rises with sequence separation in every structure, domain
boundaries or not — two residues 800 apart have high PAE because they are 800 apart. So
"inter-domain PAE is higher than intra-domain PAE" is confounded with separation unless the two
populations are compared **at the same separation**. That requires an overlap window, and whether
one exists is a property of the data, not of the design.

⚠ If domains run ~100 aa, intra separations top out near 100 and inter separations start there.
The window may be empty or too narrow to compare in. **That is a result, not a failure** — it means
the within-structure contrast is unavailable and the arm confound must be handled another way.

No GPU. No new folds. Reads `data/control/d099/*/pae.json`, which are gitignored but regenerable
from the committed sample plus `scripts/d099_control_fold.py`.

    python scripts/pae_separation_overlap.py
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
from collections import Counter
from typing import Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import (  # noqa: E402
    UNIPROT_CACHE, domain_like_features,
)

SAMPLE = REPO / "data" / "census" / "d099_control_sample.csv"
MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
ARTIFACTS = REPO / "data" / "control" / "d099"

#: ⚠ A residue in no annotated domain. NOT domain 0 — defaulting would fold linker residues into
#: the first domain and inflate the intra population with pairs that are not intra anything.
UNASSIGNED = "unassigned"


def domain_index(*, span_start: int, span_len: int, domains: list[tuple[int, int]]):
    """Map each SPAN-LOCAL index to a domain id, or `UNASSIGNED`.

    ⚠ Domains arrive in CHAIN coordinates (1-based, inclusive) and the PAE matrix is span-local
    (0-based). The subtraction is where an off-by-one would silently shift every classification.
    """
    idx: list = [UNASSIGNED] * span_len
    for d, (a, b) in enumerate(domains):
        for pos in range(a, b + 1):
            local = pos - span_start
            if 0 <= local < span_len:
                idx[local] = d
    return idx


def classify_pair(i: int, j: int, idx) -> str:
    """`"intra"`, `"inter"`, or `UNASSIGNED`. Symmetric."""
    a, b = idx[i], idx[j]
    if a is UNASSIGNED or b is UNASSIGNED:
        return UNASSIGNED
    return "intra" if a == b else "inter"


def overlap_window(intra: dict[int, int], inter: dict[int, int]
                   ) -> Optional[tuple[int, int, int, int]]:
    """(lo, hi, n_intra_in_window, n_inter_in_window), or **None** when no separation carries both.

    ⚠ None rather than an empty range: the failure case must read as an answer, not a measurement.
    """
    shared = sorted(set(intra) & set(inter))
    if not shared:
        return None
    lo, hi = shared[0], shared[-1]
    n_intra = sum(v for k, v in intra.items() if lo <= k <= hi)
    n_inter = sum(v for k, v in inter.items() if lo <= k <= hi)
    return (lo, hi, n_intra, n_inter)


def domains_in_span(acc: str, span_start: int, span_end: int) -> list[tuple[int, int]]:
    """UniProt `Domain` features wholly inside the span — D-099's eligibility measure, same
    definition as Task C (`Domain` only, not `Domain`+`Repeat`)."""
    doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
    out = []
    for f in domain_like_features(doc):
        if f.get("type") != "Domain":
            continue
        loc = f["location"]
        a, b = loc["start"].get("value"), loc["end"].get("value")
        if a is None or b is None:
            continue
        if a >= span_start and b <= span_end:
            out.append((int(a), int(b)))
    return sorted(out)


def main() -> int:
    with SAMPLE.open(encoding="utf-8") as fh:
        sample = [r for r in csv.DictReader(fh) if r["arm"] == "multi"]
    with MANIFEST.open(encoding="utf-8") as fh:
        man = {r["census_accession"]: r for r in csv.DictReader(fh)}

    print("=" * 96)
    print("TASK H — intra/inter separation overlap, over the 20 multi-domain control matrices")
    print("key: one residue PAIR (i<j); separation = j - i, in span-local residues")
    print("=" * 96)
    print(f"  {'acc':9s} {'span':>5s} {'dom':>4s} {'intra_pairs':>12s} {'inter_pairs':>12s} "
          f"{'intra_sep':>12s} {'inter_sep':>12s} {'overlap':>14s}")
    print("  " + "-" * 88)

    pooled_intra: Counter = Counter()
    pooled_inter: Counter = Counter()
    no_overlap = []
    missing = []

    for s in sample:
        acc = s["acc"]
        pae_path = ARTIFACTS / acc / "pae.json"
        if not pae_path.is_file():
            missing.append(acc)
            continue
        m = man[acc]
        s0, s1 = int(m["span_start"]), int(m["span_end"])
        n = s1 - s0 + 1
        doms = domains_in_span(acc, s0, s1)
        idx = domain_index(span_start=s0, span_len=n, domains=doms)

        intra: Counter = Counter()
        inter: Counter = Counter()
        for i in range(n):
            ai = idx[i]
            if ai is UNASSIGNED:
                continue
            for j in range(i + 1, n):
                aj = idx[j]
                if aj is UNASSIGNED:
                    continue
                (intra if ai == aj else inter)[j - i] += 1

        pooled_intra.update(intra)
        pooled_inter.update(inter)

        win = overlap_window(intra, inter)
        if win is None:
            no_overlap.append(acc)
            wtxt = "⚠ NONE"
        else:
            wtxt = f"{win[0]}-{win[1]}"
        isep = f"{min(intra)}-{max(intra)}" if intra else "-"
        xsep = f"{min(inter)}-{max(inter)}" if inter else "-"
        print(f"  {acc:9s} {n:5d} {len(doms):4d} {sum(intra.values()):12,d} "
              f"{sum(inter.values()):12,d} {isep:>12s} {xsep:>12s} {wtxt:>14s}")

    if missing:
        print(f"\n⚠ {len(missing)} matrices absent (gitignored; regenerate with "
              f"scripts/d099_control_fold.py): {missing}")

    print("\n" + "=" * 96)
    print("POOLED ACROSS ALL 20 — the number that decides the design")
    print("=" * 96)
    win = overlap_window(pooled_intra, pooled_inter)
    ti, tx = sum(pooled_intra.values()), sum(pooled_inter.values())
    print(f"  intra pairs total : {ti:,}   separations {min(pooled_intra)}-{max(pooled_intra)}")
    print(f"  inter pairs total : {tx:,}   separations {min(pooled_inter)}-{max(pooled_inter)}")
    if win is None:
        print("\n  ⚠⚠ NO OVERLAP. The within-structure contrast is UNAVAILABLE at every separation.")
        print("     The arm confound must be handled another way; more rows will not help.")
        return 0

    lo, hi, ni, nx = win
    print(f"\n  ⚠ OVERLAP WINDOW: separations {lo}-{hi}")
    print(f"     intra pairs inside : {ni:,} ({100*ni/ti:.1f}% of all intra)")
    print(f"     inter pairs inside : {nx:,} ({100*nx/tx:.1f}% of all inter)")

    both = sorted(set(pooled_intra) & set(pooled_inter))
    print(f"     separations carrying BOTH populations: {len(both):,} of "
          f"{max(pooled_inter) - min(pooled_intra) + 1:,} in range")

    print("\n  distribution inside the window (deciles of separation):")
    step = max(1, len(both) // 10)
    print(f"      {'sep':>6s} {'intra':>10s} {'inter':>10s}")
    for k in both[::step]:
        print(f"      {k:6d} {pooled_intra[k]:10,d} {pooled_inter[k]:10,d}")

    print(f"\n  ⚠ {len(no_overlap)} of {len(sample)} proteins have NO overlap individually"
          + (f": {no_overlap}" if no_overlap else ""))
    print("  ⚠⚠ A pooled window does not license a pooled comparison — pooling across proteins")
    print("     reintroduces between-structure variation, which is what the design excludes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
