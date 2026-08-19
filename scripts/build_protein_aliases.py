"""Build the protein alias index from the PINNED UniProt cache — never from recall.

⚠⚠ WHY THIS EXISTS. The platform is keyed on HGNC gene symbols. The ADC field is not: it talks in
CD numbers (CD30), receptor families (HER2, HER3) and trade shorthand (TROP2). Three of the most
famous ADC targets in medicine read as MISSING from the surfaces when two of them are present —
`HER2` is on the target surface as `ERBB2`, `CD30` is in the census as `TNFRSF8`. A search that
matches only accession, gene and full protein name cannot find either.

⚠ THE ALIASES ARE DERIVED, NOT TYPED. `data/census/spancache/` is the same pinned instrument
`D-093` decision 6 item (3) used for the accession join — already in the tree, already versioned.
Typing `HER2 -> ERBB2` by hand would be recall, and *a licence was recalled rather than read* is the
reason `D-093 amendment 1` exists. Every alias here carries the field it came from.

⚠⚠ A COLLIDING ALIAS IS A CATEGORY, NOT A TIE TO BREAK. One alias string can name two proteins.
Silently picking one is the two-paths-to-one-identifier defect this project hits most often, and an
alias index is exactly where it hides. Collisions are EMITTED, marked, and resolve to *all* their
accessions — the surface shows the ambiguity rather than guessing.

Kinds emitted, in the order a reader would trust them:
  `gene_synonym`   — genes[].synonyms[].value           (HER2, MPF)
  `cd_antigen`     — proteinDescription.cdAntigenNames  (CD30, CD340)
  `alt_short`      — alternativeNames[].shortNames      (MLN 19)
  `alt_full`       — alternativeNames[].fullName        (Ki-1 antigen)

⚠ The PRIMARY gene symbol and the accession are NOT emitted as aliases: the surface already matches
them, and re-emitting them would inflate the index with rows that change no search result.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
from collections import defaultdict

CACHE = pathlib.Path("data/census/spancache")
OUT = pathlib.Path("data/census/protein_aliases.v1.csv")

#: ⚠ An alias shorter than this is noise, not a name — it matches half the census as a substring.
MIN_ALIAS = 2


def _aliases_of(doc: dict) -> list[tuple[str, str]]:
    """(alias, kind) pairs for one UniProt entry, primary symbol excluded."""
    out: list[tuple[str, str]] = []
    primary = set()

    for g in doc.get("genes") or []:
        gn = (g.get("geneName") or {}).get("value")
        if gn:
            primary.add(gn.upper())
        for syn in g.get("synonyms") or []:
            v = (syn or {}).get("value")
            if v:
                out.append((v, "gene_synonym"))

    pd = doc.get("proteinDescription") or {}
    for cd in pd.get("cdAntigenNames") or []:
        v = (cd or {}).get("value")
        if v:
            out.append((v, "cd_antigen"))

    for alt in pd.get("alternativeNames") or []:
        fn = ((alt or {}).get("fullName") or {}).get("value")
        if fn:
            out.append((fn, "alt_full"))
        for sn in (alt or {}).get("shortNames") or []:
            v = (sn or {}).get("value")
            if v:
                out.append((v, "alt_short"))

    # ⚠ drop anything that merely restates the primary symbol — it changes no search result
    return [(a, k) for a, k in out if a.upper() not in primary and len(a) >= MIN_ALIAS]


def build() -> list[dict]:
    if not CACHE.is_dir():
        raise SystemExit("REFUSED: %s is absent — the pinned instrument is not in the tree" % CACHE)

    by_alias: dict[str, set[str]] = defaultdict(set)
    rows: list[dict] = []
    for f in sorted(CACHE.glob("*.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        acc = doc.get("primaryAccession")
        if not acc:
            continue
        gene = None
        for g in doc.get("genes") or []:
            gene = (g.get("geneName") or {}).get("value")
            if gene:
                break
        seen: set[str] = set()
        for alias, kind in _aliases_of(doc):
            key = alias.upper()
            if key in seen:            # same alias twice in one entry adds nothing
                continue
            seen.add(key)
            by_alias[key].add(acc)
            rows.append({"alias": alias, "alias_upper": key, "accession": acc,
                         "gene": gene or "", "kind": kind})

    # ⚠⚠ mark collisions rather than resolving them
    for r in rows:
        r["ambiguous"] = "yes" if len(by_alias[r["alias_upper"]]) > 1 else "no"
    return rows


def main() -> int:
    rows = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # ⚠ `lineterminator="\n"` is NOT redundant with `newline="\n"`. `csv.writer` emits CRLF by
    # dialect on every platform, and `newline="\n"` only stops Python translating it further — so
    # the first version of this file landed CRLF while every other data artifact in the tree is LF.
    # Deterministic, but inconsistent, and inconsistency is what makes a hash mismatch ambiguous.
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=["alias", "alias_upper", "accession", "gene", "kind",
                                           "ambiguous"], lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["alias_upper"], r["accession"])):
            w.writerow(r)

    amb = {r["alias_upper"] for r in rows if r["ambiguous"] == "yes"}
    print("aliases written : %d over %d accessions" % (len(rows), len({r['accession'] for r in rows})))
    print("distinct aliases: %d" % len({r["alias_upper"] for r in rows}))
    print("AMBIGUOUS       : %d distinct alias strings name more than one accession" % len(amb))
    for k in sorted(amb)[:10]:
        print("   %-14s -> %s" % (k, sorted({r["accession"] for r in rows
                                             if r["alias_upper"] == k})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
