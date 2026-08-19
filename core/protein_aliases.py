"""Resolve a name a person would actually type to the accessions it could mean.

⚠⚠ THE PROBLEM THIS SOLVES, STATED PLAINLY. The platform is keyed on HGNC gene symbols; the ADC
field is not. `HER2` is on the target surface as `ERBB2` and `CD30` is in the census as `TNFRSF8`,
and a search over accession/gene/label finds NEITHER — the two most recognisable ADC antigens in
medicine read as absent while being present. The owner hit this directly.

⚠ PUNCTUATION IS PART OF THE PROBLEM, NOT A DETAIL. UniProt stores `PDL1`, `NECTIN4`, `HER2`;
people type `PD-L1`, `NECTIN-4`, `HER-2`. Matching raw strings answers "no such protein" to a query
that names one we hold. So both sides are normalised to alphanumerics before comparison.

⚠⚠ AN AMBIGUOUS ALIAS RESOLVES TO ALL OF ITS ACCESSIONS AND SAYS SO. One alias string can name
several proteins — 201 do. Picking the first is the two-paths-to-one-identifier defect, and an alias
index is exactly where it hides. `resolve()` returns every match with `ambiguous` set; the caller
shows the ambiguity rather than guessing which one the user meant.

⚠ NORMALISATION CAN CREATE COLLISIONS THAT THE RAW STRINGS DO NOT HAVE. `collisions_introduced_by_
normalisation()` measures how many, so the cost of the punctuation fix is a number in the record
rather than an assumption. It is asserted in the tests, not left to inspection.

⚠ This module RESOLVES names. It does not rank, order, score or filter proteins by any property —
a resolver that also sorted would be `D-079` decision 1's problem wearing a search box.
"""
from __future__ import annotations

import csv
import functools
import pathlib
import re
from collections import defaultdict
from typing import NamedTuple

ALIAS_CSV = pathlib.Path("data/census/protein_aliases.v1.csv")

#: ⚠ The kinds, most trustworthy first. A gene synonym is a name the gene HAS; an alt_full is a
#: description of what the protein DOES, which is why the collisions cluster there.
KIND_ORDER = ("gene_synonym", "cd_antigen", "alt_short", "alt_full")

_NON_ALNUM = re.compile(r"[^A-Z0-9]+")


def normalize(text: str) -> str:
    """`PD-L1` and `pd l1` both become `PDL1`. Empty for anything with no alphanumerics."""
    return _NON_ALNUM.sub("", (text or "").upper())


class AliasHit(NamedTuple):
    alias: str
    accession: str
    gene: str
    kind: str
    ambiguous: bool


@functools.lru_cache(maxsize=1)
def load_aliases(path: str | None = None) -> dict[str, tuple[AliasHit, ...]]:
    """Normalised alias -> the hits it names. Empty dict if the index has not been built."""
    p = pathlib.Path(path) if path else ALIAS_CSV
    if not p.exists():
        return {}
    raw: dict[str, list[AliasHit]] = defaultdict(list)
    with p.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = normalize(row["alias"])
            if not key:
                continue
            raw[key].append(AliasHit(row["alias"], row["accession"], row["gene"], row["kind"],
                                     row["ambiguous"] == "yes"))
    out: dict[str, tuple[AliasHit, ...]] = {}
    for key, hits in raw.items():
        # ⚠ recomputed AFTER normalisation — the CSV's flag is over raw strings, and normalising
        # can merge two distinct raw aliases into one key. The flag must describe what is returned.
        accs = {h.accession for h in hits}
        amb = len(accs) > 1
        out[key] = tuple(sorted((h._replace(ambiguous=amb) for h in hits),
                                key=lambda h: (KIND_ORDER.index(h.kind)
                                               if h.kind in KIND_ORDER else 9, h.accession)))
    return out


def resolve(query: str, path: str | None = None) -> tuple[AliasHit, ...]:
    """Every accession the typed name could mean. Empty tuple is a clean 'not an alias'."""
    return load_aliases(path).get(normalize(query), ())


def collisions_introduced_by_normalisation(path: str | None = None) -> dict[str, set[str]]:
    """Alias keys that name >1 accession ONLY because punctuation was stripped.

    ⚠ The price of the punctuation fix, measured rather than assumed.
    """
    p = pathlib.Path(path) if path else ALIAS_CSV
    if not p.exists():
        return {}
    raw_map: dict[str, set[str]] = defaultdict(set)
    norm_map: dict[str, set[str]] = defaultdict(set)
    with p.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            raw_map[row["alias"].upper()].add(row["accession"])
            norm_map[normalize(row["alias"])].add(row["accession"])
    introduced: dict[str, set[str]] = {}
    for key, accs in norm_map.items():
        if len(accs) <= 1:
            continue
        # was every raw spelling that folds to this key already ambiguous on its own?
        contributing = [r for r in raw_map if normalize(r) == key]
        if all(len(raw_map[r]) == 1 for r in contributing) and len(contributing) > 1:
            introduced[key] = accs
    return introduced


@functools.lru_cache(maxsize=1)
def aliases_by_accession(path: str | None = None) -> dict[str, list[str]]:
    """Accession -> the other names it goes by, most trustworthy kind first.

    ⚠ For the SURFACE, which searches an accession's own names. `resolve()` goes the other way.
    ⚠ Ambiguous aliases are included: a protein does not stop being called `ALP1` because another
    protein is too. The ambiguity belongs to the query, and `resolve()` is where it is reported.
    """
    p = pathlib.Path(path) if path else ALIAS_CSV
    if not p.exists():
        return {}
    grouped: dict[str, list[tuple[int, str]]] = defaultdict(list)
    with p.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rank = KIND_ORDER.index(row["kind"]) if row["kind"] in KIND_ORDER else 9
            grouped[row["accession"]].append((rank, row["alias"]))
    out: dict[str, list[str]] = {}
    for acc, items in grouped.items():
        seen: set[str] = set()
        names: list[str] = []
        for _, alias in sorted(items):
            if alias.upper() in seen:
                continue
            seen.add(alias.upper())
            names.append(alias)
        out[acc] = names
    return out
