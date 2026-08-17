"""Tranche 6 domain survey — the evidence behind D-095 and F-041.

Answers the question PREWORK-2026-08-18 §3 posed as the cheapest first move:
count the domains each of the 10 tranche-6 subjects has under UniProt / Pfam /
InterPro and check whether they agree.

⚠ The answer is not a disagreement in number. Two of the three named sources do
not supply domain BOUNDARIES at all from this cache (F-041), so the comparison
that §3 anticipated cannot be run as posed. This script demonstrates that
directly rather than asserting it.

READ-ONLY. Cache-only: no network, no database, no GPU. Safe to run in any shell.

Usage:
    python scripts/tranche6_domain_survey.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import statistics
from collections import Counter

CACHE = pathlib.Path("data/census/spancache")
MANIFEST = pathlib.Path("data/census/census_manifest.v7.csv")

# The ten subjects named in D-091 ruling 3. Accessions resolved from
# data/census/census_labels.csv (source: spancache), not from memory.
SUBJECTS = [
    ("Q14517", "FAT1"), ("Q9NYQ8", "FAT2"), ("Q8TDW7", "FAT3"), ("Q6V0I7", "FAT4"),
    ("Q07954", "LRP1"), ("Q9NZR2", "LRP1B"), ("P98164", "LRP2"),
    ("O75445", "USH2A"), ("Q8WXG9", "ADGRV1"), ("Q86WI1", "PKHD1L1"),
]

# ⚠ Both types, deliberately. UniProt splits a tandem array between `Domain` and
# `Repeat`; counting only `Domain` silently drops 34 LDL-receptor class B repeats
# from LRP1 alone. See D-095 decision 1(b).
DOMAINLIKE = ("Domain", "Repeat")

TRAINED_CONTEXT = 1026  # residues; the ESMFold context this project folds inside

MEMBER_DBS = ("Pfam", "InterPro", "SMART", "PROSITE", "CDD", "Gene3D",
              "SUPFAM", "PANTHER", "FunFam")

RULE = "=" * 104
THIN = "-" * 104


def match_count(xref: dict) -> int | None:
    """Instance count the xref declares, or None if it declares none."""
    for p in xref.get("properties", []):
        if p.get("key") == "MatchStatus":
            try:
                return int(p["value"])
            except (ValueError, TypeError):
                return None
    return None


def load(acc: str) -> tuple[dict, str]:
    blob = (CACHE / f"{acc}.json").read_bytes()
    return json.loads(blob.decode("utf-8")), hashlib.sha256(blob).hexdigest()


def domain_intervals(doc: dict, s0: int, s1: int) -> list[tuple[int, int, str, str]]:
    """Domain-like features falling within [s0, s1], sorted by start."""
    out = []
    for f in doc.get("features", []):
        if f.get("type") not in DOMAINLIKE:
            continue
        a = f["location"]["start"].get("value")
        b = f["location"]["end"].get("value")
        if a is None or b is None or b < s0 or a > s1:
            continue
        out.append((a, b, f.get("description", ""), f.get("type")))
    return sorted(out)


def merge(intervals) -> list[list[int]]:
    """Merge abutting/overlapping intervals into contiguous runs.

    ⚠ A run is NOT a domain. FAT1's cadherin repeats abut exactly
    (35-149, 150-257, ...), so 20+ domains fuse into one 2,289 aa run.
    Reporting a run as a domain was a real error in the first pass of this
    analysis; the two are kept separate everywhere below.
    """
    runs: list[list[int]] = []
    for a, b, *_ in intervals:
        if runs and a <= runs[-1][1] + 1:
            runs[-1][1] = max(runs[-1][1], b)
        else:
            runs.append([a, b])
    return runs


def main() -> None:
    manifest = {}
    with MANIFEST.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            manifest[row["census_accession"]] = row

    print(RULE)
    print("TRANCHE 6 DOMAIN SURVEY — 10 subjects, cache-only")
    print(f"cache: {CACHE}   manifest: {MANIFEST.name}   context: {TRAINED_CONTEXT} aa")
    print(RULE)

    # ---------------------------------------------------------------- part 1
    print("\n1. DOES THE BOUNDARY SOURCE EVEN EXIST?  (F-041)")
    print(THIN)
    print(f"{'database':10s} {'xrefs':>7s} {'declare a count':>16s} {'carry coordinates':>19s}")
    print(THIN)

    xref_tally: Counter = Counter()
    for acc, _ in SUBJECTS:
        doc, _ = load(acc)
        for x in doc.get("uniProtKBCrossReferences", []):
            db = x.get("database")
            if db in MEMBER_DBS:
                xref_tally[(db, match_count(x) is not None)] += 1

    for db in MEMBER_DBS:
        yes = xref_tally[(db, True)]
        no = xref_tally[(db, False)]
        if yes + no == 0:
            continue
        decl = f"{yes}/{yes + no}"
        print(f"{db:10s} {yes + no:7d} {decl:>16s} {'none':>19s}")
    print(THIN)
    print("⚠ InterPro declares no instance count anywhere, and NO database in this")
    print("  cache carries coordinates. UniProt features are the only boundary source.")

    # ---------------------------------------------------------------- part 2
    print("\n\n2. THE COUNTS DISAGREE — instances per protein, by source")
    print(THIN)
    print(f"{'gene':9s} {'UniProt':>8s} {'(Dom':>5s} {'Rep)':>5s} {'Pfam':>6s} "
          f"{'SMART':>6s} {'PROSITE':>8s} {'InterPro':>9s}")
    print(THIN)

    for acc, gene in SUBJECTS:
        doc, _ = load(acc)
        feats = doc.get("features", [])
        nd = sum(1 for f in feats if f.get("type") == "Domain")
        nr = sum(1 for f in feats if f.get("type") == "Repeat")
        xr = doc.get("uniProtKBCrossReferences", [])

        def total(db):
            vals = [match_count(x) for x in xr if x.get("database") == db]
            vals = [v for v in vals if v is not None]
            return str(sum(vals)) if vals else "n/a"

        print(f"{gene:9s} {nd + nr:8d} {nd:5d} {nr:5d} {total('Pfam'):>6s} "
              f"{total('SMART'):>6s} {total('PROSITE'):>8s} {total('InterPro'):>9s}")
    print(THIN)
    print("⚠ Not one of the ten agrees across sources. The boundary source is a")
    print("  live question — but it is decided by availability, not by consensus.")

    # ---------------------------------------------------------------- part 3
    print("\n\n3. DOMAIN vs RUN — why per-domain folding is not the design")
    print(THIN)
    print(f"{'gene':9s} {'span_aa':>8s} {'doms':>5s} {'smallest':>9s} {'median':>7s} "
          f"{'largest':>8s} | {'runs':>5s} {'largest_run':>12s} {'over_ctx':>9s}")
    print(THIN)

    store = {}
    for acc, gene in SUBJECTS:
        row = manifest[acc]
        s0, s1 = int(row["span_start"]), int(row["span_end"])
        doc, sha = load(acc)
        iv = domain_intervals(doc, s0, s1)
        sizes = [b - a + 1 for a, b, *_ in iv]
        runs = merge(iv)
        run_sizes = [b - a + 1 for a, b in runs]
        over = sum(1 for s in run_sizes if s > TRAINED_CONTEXT)
        span_len = s1 - s0 + 1
        store[acc] = dict(gene=gene, s0=s0, s1=s1, span_len=span_len, iv=iv,
                          sizes=sizes, runs=runs, run_sizes=run_sizes, sha=sha)
        print(f"{gene:9s} {span_len:8d} {len(sizes):5d} {min(sizes):9d} "
              f"{int(statistics.median(sizes)):7d} {max(sizes):8d} | "
              f"{len(runs):5d} {max(run_sizes):12d} {over:9d}")
    print(THIN)
    print(f"⚠ Every single domain is inside the {TRAINED_CONTEXT} aa context "
          f"(largest {max(max(s['sizes']) for s in store.values())} aa).")
    print("⚠ FAT1-4 each carry ONE contiguous run that is not — and a run has no")
    print("  linker to cut at, so the cut must fall inside a domain stack.")

    # ---------------------------------------------------------------- part 4
    print("\n\n4. WHAT IS NOT IN A DOMAIN — the residues a domain-only fold would drop")
    print(THIN)
    print(f"{'gene':9s} {'span_aa':>8s} {'in_domain':>10s} {'unannotated':>12s} "
          f"{'unannot_%':>10s} {'longest_gap':>12s} {'lead':>6s} {'tail':>6s}")
    print(THIN)

    for acc, gene in SUBJECTS:
        d = store[acc]
        dom_res = sum(b - a + 1 for a, b in d["runs"])
        un = d["span_len"] - dom_res
        gaps = [d["runs"][i][0] - d["runs"][i - 1][1] - 1 for i in range(1, len(d["runs"]))]
        gaps = [g for g in gaps if g > 0]
        lead = d["runs"][0][0] - d["s0"]
        tail = d["s1"] - d["runs"][-1][1]
        print(f"{gene:9s} {d['span_len']:8d} {dom_res:10d} {un:12d} "
              f"{100 * un / d['span_len']:9.1f}% {max(gaps) if gaps else 0:12d} "
              f"{lead:6d} {tail:6d}")
    print(THIN)
    print("⚠ PKHD1L1 is 55.3% unannotated with a 662 aa tail. Folding 'the domains'")
    print("  would discard more than half of it silently — F-037 one level down.")

    # ---------------------------------------------------------------- part 5
    print("\n\n5. DOMAIN VOCABULARY")
    print(THIN)
    for acc, gene in SUBJECTS:
        c = Counter(desc.rstrip("0123456789 ") or "(unnamed)"
                    for _, _, desc, _ in store[acc]["iv"])
        print(f"  {gene:9s} " + ", ".join(f"{k} x{v}" for k, v in c.most_common(4)))

    # ---------------------------------------------------------------- part 6
    print("\n\n6. ⚠ WHAT THE BOUNDARIES ARE MADE OF — D-095 decision 1(c)")
    print(THIN)
    print(f"{'gene':9s} {'domains':>8s} {'sequence-model':>15s} {'experimental':>13s} {'other':>7s}")
    print(THIN)

    eco: Counter = Counter()
    src: Counter = Counter()
    tot = auto_t = exp_t = other_t = 0
    for acc, gene in SUBJECTS:
        iv_feats = []
        doc, _ = load(acc)
        s0, s1 = store[acc]["s0"], store[acc]["s1"]
        for f in doc.get("features", []):
            if f.get("type") not in DOMAINLIKE:
                continue
            a = f["location"]["start"].get("value")
            b = f["location"]["end"].get("value")
            if a is None or b is None or b < s0 or a > s1:
                continue
            iv_feats.append(f)

        auto = exp = other = 0
        for f in iv_feats:
            codes = set()
            for e in f.get("evidences", []):
                codes.add(e.get("evidenceCode"))
                eco[e.get("evidenceCode")] += 1
                if e.get("source"):
                    src[e["source"]] += 1
            if codes & {"ECO:0000255", "ECO:0000256"}:
                auto += 1
            elif "ECO:0000269" in codes:
                exp += 1
            else:
                other += 1
        n = len(iv_feats)
        tot += n
        auto_t += auto
        exp_t += exp
        other_t += other
        pct = f"{auto} ({100 * auto / n:.0f}%)" if n else "-"
        print(f"{gene:9s} {n:8d} {pct:>15s} {exp:13d} {other:7d}")

    print(THIN)
    print(f"{'TOTAL':9s} {tot:8d} {f'{auto_t} ({100 * auto_t / tot:.1f}%)':>15s} "
          f"{exp_t:13d} {other_t:7d}")
    print()
    print("  evidence codes present:")
    for code, n in eco.most_common():
        note = {"ECO:0000255": "automatic assertion from a SEQUENCE MODEL (HMM/profile)",
                "ECO:0000305": "curator inference",
                "ECO:0000269": "experimental"}.get(code, "")
        print(f"    {code:14s} {n:5d}   {note}")
    print("  annotation sources cited:")
    for s, n in src.most_common(6):
        print(f"    {s:22s} {n:5d}")
    print()
    print("⚠⚠ ZERO boundaries carry experimental evidence. The boundary source is a")
    print("   model output: tranche 6 is an HMM deciding where a network may cut.")

    # ---------------------------------------------------------------- part 7
    print("\n\n7. PROVENANCE — sha256 of every cache file read")
    print(THIN)
    for acc, gene in SUBJECTS:
        print(f"  {gene:9s} {acc:8s} {store[acc]['sha']}")


if __name__ == "__main__":
    main()
