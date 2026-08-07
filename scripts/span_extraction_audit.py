#!/usr/bin/env python3
"""The span-extraction audit — ORDERS-Code-2026-08-06-span-extraction-audit.md, Tasks 1-3.

⚠ READ-ONLY. Cache only, no network, no database, no write to any artifact. It changes no filter,
no term list and no extraction rule; it measures what the CURRENT filter excludes so the vocabulary
ruling has an input. Widening is owner-reserved and follows this measurement.

    python scripts/span_extraction_audit.py            # all three tasks
    python scripts/span_extraction_audit.py --task 1

⚠ GPI ANCHORS ARE NOT TOPOLOGY. UniProt records a GPI anchor as a **lipid-moiety-binding site**
(feature type `Lipidation`), never as a `Topological domain` and never as `Transmembrane`. A
GPI-anchored protein is attached by a lipid tail, crosses nothing, and has its entire mature chain
on the outer leaflet — **so it is fully extracellular and carries no topology by design.** Widening
the topology vocabulary recovers exactly nothing for it; it needs a different extraction rule.
That is Task 1's hypothesis and this script tests it rather than assuming it.

⚠ DESCRIPTIONS ARE REPORTED VERBATIM AND NEVER NORMALISED. `Lumenal` and `Lumenal, vesicle` are
different strings and the ruling is per-term; collapsing them here would make the owner's decision
for them. Terms are re-derived from the cache — the order's own list is explicitly not trusted.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "data" / "census" / "spancache"
CENSUS = REPO / "data" / "census"

#: The twelve of the 82 with `n_extracellular_spans == 0` and bucket `unknown`, measured off
#: `data/cohort_82_ecd.csv`. ⚠ Re-derived below rather than trusted — the order supplies this list
#: and the order is not the data.
ORDER_TWELVE = ("P51801", "Q9UJA9", "Q6ZNA5", "P35052", "P11717", "Q13421",
                "Q8N4M1", "O15455", "Q6UXF1", "Q9NV96", "O14798", "Q16880")


# ── cache access ────────────────────────────────────────────────────────────
def load(acc: str) -> dict | None:
    """The cached entry, or None. ⚠ A cache miss is a CATEGORY, never a silent empty entry."""
    p = CACHE / f"{acc}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None


def features(data: dict, ftype: str) -> list[dict]:
    return [f for f in (data.get("features") or []) if f.get("type") == ftype]


def bounds(feat: dict) -> tuple[int | None, int | None]:
    loc = feat.get("location") or {}
    return (loc.get("start") or {}).get("value"), (loc.get("end") or {}).get("value")


def topo(data: dict) -> list[tuple[str, int | None, int | None]]:
    """Every `Topological domain`, description VERBATIM. ⚠ NOT filtered on 'extracellular'."""
    out = []
    for f in features(data, "Topological domain"):
        s, e = bounds(f)
        out.append((f.get("description", "") or "", s, e))
    return out


def gpi_evidence(data: dict) -> list[tuple[str, str, int | None, int | None]]:
    """Any feature whose type or description mentions a GPI anchor. ⚠ Type and description are
    returned VERBATIM and unnormalised — the order requires the raw strings, because 'UniProt
    records this as a lipid-moiety-binding site, not as topology' is the claim under test."""
    out = []
    for f in data.get("features") or []:
        t = f.get("type", "") or ""
        d = f.get("description", "") or ""
        if "gpi" in f"{t} {d}".lower():
            s, e = bounds(f)
            out.append((t, d, s, e))
    return out


def gpi_anchor_strict(data: dict) -> list[tuple[str, str, int | None, int | None]]:
    """⚠ THE AUTHORITATIVE TEST, and it is narrower than `gpi_evidence`.

    A GPI anchor is a `Lipidation` feature reading `GPI-anchor amidated <residue>`. The loose scan
    also matches a `Mutagenesis` of the anchor site, a `Natural variant` near it, or a `Region`
    that merely names it — **mentions of a GPI anchor, not annotations of one.** Both counts are
    reported so the difference is visible rather than absorbed: a protein counted as GPI-anchored
    on the strength of a mutagenesis note would be an absence coerced into an affirmative.
    """
    out = []
    for f in features(data, "Lipidation"):
        d = f.get("description", "") or ""
        if "gpi-anchor" in d.lower():
            s, e = bounds(f)
            out.append((f.get("type", ""), d, s, e))
    return out


def signal(data: dict) -> list[tuple[str, int | None, int | None]]:
    out = []
    for f in data.get("features") or []:
        if f.get("type") in ("Signal", "Signal peptide"):
            s, e = bounds(f)
            out.append((f.get("type"), s, e))
    return out


def seqlen(data: dict) -> int | None:
    return (data.get("sequence") or {}).get("length")


# ── the census no_topology populations, off the committed files ─────────────
def no_topology_rows(fname: str) -> list[dict]:
    """⚠ Fetched successfully AND no sliceable span. A never-fetched or failed row is neither."""
    with (CENSUS / fname).open(encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh)
                if r["no_topology_reason"] and r["fetched_on"] and r["fetch_failed"] != "true"]


CLASSES = (("annex", "spans_annex.csv"), ("surface", "spans_surface.csv"))


# ── TASK 1 ──────────────────────────────────────────────────────────────────
def task1() -> None:
    print("=" * 78)
    print("TASK 1 — THE GATE. Does the vocabulary gap touch the 82?")
    print("=" * 78)

    # ⚠ Re-derive the twelve from the data rather than trusting the order's list.
    with (REPO / "data" / "cohort_82_ecd.csv").open(encoding="utf-8", newline="") as fh:
        ecd = list(csv.DictReader(fh))
    derived = [r for r in ecd if not r["largest_span_aa"].strip()]
    accs = [r["accession"] for r in derived]
    genes = {r["accession"]: r["gene"] for r in ecd}
    print(f"twelve | order supplies | {len(ORDER_TWELVE)}")
    print(f"twelve | re-derived from cohort_82_ecd.csv (blank largest_span_aa) | {len(accs)}")
    print(f"twelve | order list == re-derived set | {set(ORDER_TWELVE) == set(accs)}")
    missing = [a for a in accs if not (CACHE / f"{a}.json").exists()]
    print(f"twelve | in spancache | {len(accs) - len(missing)} | NOT cached | {len(missing)}"
          + (f" ⚠ {missing} — DO NOT RE-FETCH WITHOUT A WORD" if missing else ""))
    print()

    buckets: dict[str, str] = {}
    for a in accs:
        d = load(a)
        g = genes.get(a, "?")
        if d is None:
            print(f"{a} | {g} | cache | ⚠ MISS — not answerable offline")
            buckets[a] = "UNANSWERED"
            continue
        tds, tms, gpis, sigs = topo(d), features(d, "Transmembrane"), gpi_evidence(d), signal(d)

        print(f"{a} | {g} | sequence_length | {seqlen(d)}")
        if tds:
            for desc, s, e in tds:
                print(f"{a} | {g} | topological_domain | {desc!r} {s}-{e}")
        else:
            print(f"{a} | {g} | topological_domain | NONE")
        if tms:
            for f in tms:
                s, e = bounds(f)
                print(f"{a} | {g} | transmembrane | {(f.get('description') or '')!r} {s}-{e}")
        else:
            print(f"{a} | {g} | transmembrane | NONE")
        if gpis:
            for t, desc, s, e in gpis:
                # ⚠ VERBATIM. Type and description exactly as UniProt writes them.
                print(f"{a} | {g} | gpi_anchor | type={t!r} description={desc!r} {s}-{e}")
        else:
            print(f"{a} | {g} | gpi_anchor | NONE")
        for t, s, e in sigs or []:
            print(f"{a} | {g} | signal_peptide | type={t!r} {s}-{e}")
        if not sigs:
            print(f"{a} | {g} | signal_peptide | NONE")

        # ── the bucket. ⚠ FIVE, not four — see bucket 5 ──
        reach = [x for x in tds if is_reachable(x[0])]
        if incomplete_coords(d):
            # ⚠ THE ORDER'S TAXONOMY HAS NO ROW FOR THIS AND IT IS NOT VOCABULARY.
            # The description already contains "extracellular"; the CURRENT filter matches it. What
            # is missing is a coordinate: UniProt writes `modifier: "UNKNOWN"` with a null value,
            # `largest_span` cannot subtract, and the row reports `no_topology`. That is the F-020
            # shape — an absent MEASUREMENT reported as absence of the THING. Widening the term
            # list recovers nothing here; it needs a coordinate rule, and that is a separate ruling.
            b = "5 term matched, coordinate UNKNOWN — not vocabulary, needs a coordinate rule"
        elif reach:
            b = "1 lumenal-family vocabulary — widen the term list"
        elif gpi_anchor_strict(d):
            b = "3 GPI-anchored — no topology by design, needs a different extraction rule"
        elif tms:
            b = "2 TM present, faces unlabelled — a genuine annotation gap"
        elif tds:
            b = "2 topological domain present but cytoplasmic/unreachable only"
        else:
            b = "4 no membrane evidence at all — correctly excluded, on this evidence"
        buckets[a] = b
        print(f"{a} | {g} | BUCKET | {b}")
        print()

    print("-" * 78)
    print("TASK 1 — bucket assignment")
    for a in accs:
        print(f"  {a} | {genes.get(a,'?'):<9} | {buckets[a]}")
    print()
    c = Counter(b.split(" ", 1)[0] for b in buckets.values())
    for k in sorted(c):
        print(f"  bucket {k} | {c[k]}")
    moved = [a for a in accs if buckets[a].startswith("1")]
    print()
    print(f"⚠ WOULD ANY OF THE 82 MOVE UNDER A WIDENING | {'YES' if moved else 'NO'} | "
          f"{len(moved)} | {[f'{a}/{genes.get(a)}' for a in moved]}")


def incomplete_coords(data: dict) -> list[tuple[str, dict]]:
    """⚠ Topological domains the CURRENT filter already matches, whose span cannot be computed.

    UniProt encodes an uncertain terminus as `{"value": null, "modifier": "UNKNOWN"}`. The
    description still reads `Extracellular`, so `parse()` admits the feature — and then
    `largest_span` returns `None` because it cannot subtract a null. The row reports
    `no_topology`, **which is a claim about the protein made from a gap in the coordinates.**

    Found by re-deriving the twelve and getting thirteen: SDK1 (`Q7Z5N4`) carries
    `Extracellular` `?-2009` and was outside the order's list because the order selected on
    `n_extracellular_spans == 0` — and SDK1's is 1. ⚠ The selection criterion masked the case.
    """
    out = []
    for f in features(data, "Topological domain"):
        if "extracellular" not in (f.get("description", "") or "").lower():
            continue
        s, e = bounds(f)
        if s is None or e is None:
            out.append((f.get("description", "") or "", f.get("location") or {}))
    return out


REACHABLE_TERMS = ("extracellular", "lumenal", "vesicular", "vacuolar", "perinuclear space",
                   "intragranular", "exoplasmic loop")
UNREACHABLE_TERMS = ("mitochondrial", "nuclear", "peroxisomal", "mother cell")


def is_reachable(desc: str) -> bool:
    """⚠ Secretory-pathway faces only. `Perinuclear space` is tested FIRST because it contains the
    substring `nuclear`, and a widening written as 'not cytoplasmic and not nuclear' drops it."""
    dl = desc.lower()
    if "perinuclear space" in dl:
        return True
    if "cytoplasmic" in dl:
        return False
    if any(t in dl for t in UNREACHABLE_TERMS):
        return False
    return any(t in dl for t in REACHABLE_TERMS)


# ── TASK 2 ──────────────────────────────────────────────────────────────────
def task2() -> None:
    print("=" * 78)
    print("TASK 2 — the same question over the census no_topology populations")
    print("=" * 78)

    pop: dict[str, list[tuple[str, dict]]] = {}
    for cls, fname in CLASSES:
        rows = no_topology_rows(fname)
        loaded, miss = [], 0
        for r in rows:
            d = load(r["census_accession"])
            if d is None:
                miss += 1
                continue
            loaded.append((r["census_accession"], d))
        pop[cls] = loaded
        print(f"{cls} | no_topology rows | {len(rows)} | cache hits | {len(loaded)} | misses | {miss}")
    print()

    # ── 2a: the 502 with neither TM nor topological domain — how many are GPI-anchored? ──
    print("2a | the neither-TM-nor-topological-domain bucket | GPI-anchor annotation")
    total_n, total_strict, total_loose = 0, 0, 0
    for cls in ("annex", "surface"):
        neither = [(a, d) for a, d in pop[cls] if not topo(d) and not features(d, "Transmembrane")]
        strict = [(a, d) for a, d in neither if gpi_anchor_strict(d)]
        loose = [(a, d) for a, d in neither if gpi_evidence(d)]
        total_n += len(neither)
        total_strict += len(strict)
        total_loose += len(loose)
        pct = (100.0 * len(strict) / len(neither)) if neither else 0.0
        print(f"2a | {cls} | neither | {len(neither)}")
        print(f"2a | {cls} | GPI-anchored, STRICT (Lipidation 'GPI-anchor …') | {len(strict)} | "
              f"{pct:.1f}%")
        print(f"2a | {cls} | any feature MENTIONING gpi (loose, not a claim) | {len(loose)}")
        mention_only = [a for a, _ in loose] if len(loose) != len(strict) else []
        if mention_only:
            extra = sorted(set(mention_only) - {a for a, _ in strict})
            print(f"2a | {cls} | ⚠ mention-only, NOT counted as anchored | {extra}")
        types = Counter(d2 for _, d in strict for _, d2, _, _ in gpi_anchor_strict(d))
        for t, n in types.most_common():
            print(f"2a | {cls} | anchor description (verbatim) | {t!r} | {n}")
        print(f"2a | {cls} | example GPI accessions | {[a for a, _ in strict[:12]]}")
    pct = (100.0 * total_strict / total_n) if total_n else 0.0
    print(f"2a | TOTAL | neither | {total_n} | GPI-anchored STRICT | {total_strict} | {pct:.1f}% | "
          f"loose | {total_loose}")
    print()

    # ── 2b: the 931 with TM and no topological domain — characterise the gap ──
    print("2b | the TM-present-no-topological-domain bucket | distinct feature types present")
    for cls in ("annex", "surface"):
        tm_only = [(a, d) for a, d in pop[cls] if not topo(d) and features(d, "Transmembrane")]
        print(f"2b | {cls} | TM but no topological domain | {len(tm_only)}")
        types = Counter(f.get("type", "") for _, d in tm_only for f in (d.get("features") or []))
        carriers = Counter()
        for _, d in tm_only:
            for t in {f.get("type", "") for f in (d.get("features") or [])}:
                carriers[t] += 1
        for t, n in carriers.most_common(18):
            print(f"2b | {cls} | feature type | {t!r} | proteins carrying it | {n} "
                  f"| occurrences | {types[t]}")
        print(f"2b | {cls} | proteins carrying a GPI anchor | "
              f"{sum(1 for _, d in tm_only if gpi_evidence(d))}")
    print()

    # ── 2c: the recoverable bucket — PER-TERM, PER-PROTEIN ──
    print("2c | the recoverable bucket | ⚠ PER-PROTEIN counts per term, terms kept SEPARATE")
    for cls in ("annex", "surface"):
        per_term: dict[str, set[str]] = defaultdict(set)
        recoverable: set[str] = set()
        for a, d in pop[cls]:
            descs = {desc for desc, _, _ in topo(d)}
            for desc in descs:
                per_term[desc].add(a)          # one protein counted ONCE per distinct term
            if any(is_reachable(x) for x in descs):
                recoverable.add(a)
        print(f"2c | {cls} | proteins with a reachable face (the recoverable count) | "
              f"{len(recoverable)}")
        for desc, accs in sorted(per_term.items(), key=lambda kv: -len(kv[1])):
            print(f"2c | {cls} | term {desc!r} | proteins | {len(accs)} | "
                  f"reachable={is_reachable(desc)}")
    print()

    # ── 2d: ⚠ NOT IN THE ORDER. The shape SDK1 exposed, swept across the census. ──
    print("2d | ⚠ NOT ORDERED — the coordinate-incomplete shape, found via SDK1 in Task 1")
    print("2d | an ALREADY-MATCHING `Extracellular` domain whose span cannot be computed")
    grand = 0
    for cls in ("annex", "surface"):
        hits = [(a, incomplete_coords(d)) for a, d in pop[cls] if incomplete_coords(d)]
        grand += len(hits)
        print(f"2d | {cls} | proteins reporting no_topology with a matching but uncomputable "
              f"extracellular domain | {len(hits)}")
        for a, incs in hits[:15]:
            for desc, loc in incs:
                print(f"2d | {cls} | {a} | {desc!r} | {json.dumps(loc)}")
        if len(hits) > 15:
            print(f"2d | {cls} | ⚠ {len(hits) - 15} further proteins not printed — count is complete")
    print(f"2d | TOTAL | {grand} | ⚠ widening the vocabulary recovers NONE of these")
    print()


# ── TASK 3 ──────────────────────────────────────────────────────────────────
#: ⚠ COMPARTMENT ONLY — a statement of where the face sits, NOT a recommendation. The order says
#: assemble the ruling input and do not make the ruling.
COMPARTMENT = {
    "Extracellular": "cell exterior",
    "Lumenal": "secretory-pathway lumen (ER / Golgi / endosome / lysosome)",
    "Lumenal, vesicle": "secretory / transport vesicle lumen",
    "Lumenal, melanosome": "melanosome lumen (a lysosome-related organelle)",
    "Vesicular": "vesicle lumen",
    "Vacuolar": "vacuolar / lysosomal lumen",
    "Perinuclear space": "perinuclear space — continuous with the ER lumen",
    "Intragranular": "secretory granule lumen",
    "Exoplasmic loop": "exoplasmic face — a third term for the non-cytoplasmic side",
    "Mitochondrial intermembrane": "mitochondrial intermembrane space",
    "Mitochondrial matrix": "mitochondrial matrix",
    "Nuclear": "nucleoplasm",
    "Peroxisomal": "peroxisome",
    "Peroxisomal matrix": "peroxisomal matrix",
    "Mother cell cytoplasmic": "cytoplasm (sporulation-specific term)",
    "Cytoplasmic": "cytosol",
}


def task3() -> None:
    print("=" * 78)
    print("TASK 3 — the ruling input. ⚠ The table only. No term list is proposed.")
    print("=" * 78)
    per_term: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for cls, fname in CLASSES:
        for r in no_topology_rows(fname):
            d = load(r["census_accession"])
            if d is None:
                continue
            for desc in {x for x, _, _ in topo(d)}:
                per_term[desc][cls].add(r["census_accession"])

    print(f"{'Term':<30} {'annex':>7} {'surface':>8}  Compartment")
    rows = sorted(per_term.items(), key=lambda kv: -(len(kv[1]['annex']) + len(kv[1]['surface'])))
    for desc, by in rows:
        comp = COMPARTMENT.get(desc, "⚠ NOT IN THE COMPARTMENT TABLE — unruled term")
        print(f"{desc!r:<30} {len(by['annex']):>7} {len(by['surface']):>8}  {comp}")
    unruled = [d for d in per_term if d not in COMPARTMENT]
    print()
    print(f"terms observed | {len(per_term)} | ⚠ not in the compartment table | {unruled}")
    print("⚠ Counts are PROTEINS, not domains, and a protein carrying two terms is counted under "
          "each — so the columns do NOT sum to the population.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task", choices=["1", "2", "3"], default=None)
    a = ap.parse_args(argv)
    if not CACHE.exists():
        print(f"⚠ no cache at {CACHE} — this audit is cache-only and does not fetch", file=sys.stderr)
        return 2
    for t, fn in (("1", task1), ("2", task2), ("3", task3)):
        if a.task in (None, t):
            fn()
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
