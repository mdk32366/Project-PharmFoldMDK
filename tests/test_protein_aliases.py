"""The alias index — the names a person types, resolved to the proteins we hold.

⚠⚠ THE OWNER'S OWN CASES ARE THE TEST. `HER2`, `HER3` and `CD30` were reported as missing from the
surfaces. Two of the three were present under a different name. Those three queries are asserted by
name, because a regression here does not look like a bug — it looks like the protein is absent.
"""
from __future__ import annotations

import ast
import csv
import json
import pathlib

import pytest

from core.protein_aliases import (
    aliases_by_accession,
    collisions_introduced_by_normalisation,
    load_aliases,
    normalize,
    resolve,
)

ALIAS_CSV = pathlib.Path("data/census/protein_aliases.v1.csv")
CACHE = pathlib.Path("data/census/spancache")

pytestmark = pytest.mark.skipif(not ALIAS_CSV.exists(), reason="alias index not built")


# ⚠⚠ The three the owner searched for and could not find.
@pytest.mark.parametrize("query,gene,accession", [
    ("HER2", "ERBB2", "P04626"),
    ("HER3", "ERBB3", "P21860"),
    ("CD30", "TNFRSF8", "P28908"),
    ("TROP2", "TACSTD2", "P09758"),
])
def test_the_names_people_actually_type_resolve(query, gene, accession):
    hits = resolve(query)
    assert hits, "%s resolved to nothing — it reads as an absent protein" % query
    assert accession in {h.accession for h in hits}
    assert gene in {h.gene for h in hits}


# ⚠ punctuation, on both sides of the comparison
@pytest.mark.parametrize("typed,accession", [
    ("her-2", "P04626"),
    ("HER 2", "P04626"),
    ("cd 340", "P04626"),
    ("PD-L1", "Q9NZQ7"),
    ("pdl1", "Q9NZQ7"),
])
def test_punctuation_and_case_do_not_hide_a_protein(typed, accession):
    assert accession in {h.accession for h in resolve(typed)}


def test_a_query_that_names_nothing_returns_empty_not_a_guess():
    assert resolve("nonsense-not-a-protein-123") == ()
    assert resolve("") == ()
    assert resolve("---") == ()


# ⚠⚠ THE DEFECT CLASS THIS INDEX IS MOST LIKELY TO INTRODUCE.
def test_an_ambiguous_alias_returns_every_accession_and_is_flagged():
    ambiguous = [k for k, v in load_aliases().items() if len({h.accession for h in v}) > 1]
    assert ambiguous, "no ambiguous alias in the index — the fixture cannot exercise the case"
    for key in ambiguous[:25]:
        hits = load_aliases()[key]
        assert len({h.accession for h in hits}) > 1
        # every hit says so — the caller cannot read one of them as unambiguous
        assert all(h.ambiguous for h in hits), key


def test_normalisation_collisions_are_measured_not_assumed():
    introduced = collisions_introduced_by_normalisation()
    # ⚠ The number itself is the point: stripping punctuation is not free, and the price is
    # recorded. A change here is a real change in behaviour and must be looked at, not re-baselined.
    assert len(introduced) == 28, (
        "punctuation-stripping now merges %d alias keys, not 28 — re-read the new ones before "
        "changing this number" % len(introduced))
    for accs in introduced.values():
        assert len(accs) > 1


# ⚠⚠ DERIVED, NEVER TYPED. This is the guarantee that matters most: `D-093 amendment 1` exists
# because a licence was RECALLED rather than READ, and an alias map is exactly the artifact someone
# would hand-write from memory.
def test_every_alias_is_present_in_the_pinned_uniprot_cache():
    if not CACHE.is_dir():
        pytest.skip("spancache absent")
    rows = list(csv.DictReader(ALIAS_CSV.open(encoding="utf-8")))
    assert len(rows) > 10_000
    sample = rows[::250]                       # a spread across the whole file, not the head
    checked = 0
    for row in sample:
        f = CACHE / ("%s.json" % row["accession"])
        if not f.exists():
            continue
        blob = f.read_text(encoding="utf-8")
        doc = json.loads(blob)
        assert doc.get("primaryAccession") == row["accession"]
        # the alias string must literally occur in the entry it claims to come from
        assert row["alias"] in blob, "%s not found in %s — typed, not derived" % (
            row["alias"], row["accession"])
        checked += 1
    assert checked >= 40, "only %d aliases checked against the cache" % checked


def test_the_primary_gene_symbol_is_never_emitted_as_an_alias_of_itself():
    for row in list(csv.DictReader(ALIAS_CSV.open(encoding="utf-8")))[::100]:
        if row["gene"]:
            assert normalize(row["alias"]) != normalize(row["gene"]), row


def test_accession_lookup_orders_gene_synonyms_before_descriptions():
    names = aliases_by_accession()["P28908"]
    assert names[0] == "CD30", names          # the name on the drug label comes first
    assert "Ki-1 antigen" in names
    assert names.index("CD30") < names.index("Ki-1 antigen")


# ⚠⚠ A RESOLVER THAT ALSO RANKED WOULD BE `D-079` DECISION 1 WEARING A SEARCH BOX.
def test_the_alias_module_neither_scores_nor_ranks():
    src = pathlib.Path("core/protein_aliases.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = {
        n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module
    } | {
        a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
    }
    assert not any("scorer" in (m or "") for m in imported), imported
    assert not any("structural_profile" in (m or "") for m in imported), imported


# ⚠⚠ THE INDEX REACHED ONE SURFACE OF THE TWO. `D-101` built the alias index for the census and
# wired it there; `/targets` never got it, so the owner searching `HER2` found nothing while `ERBB2`
# sat in that very list, folded and ranked. **`F-052`'s shape**: a convention that exists, is
# documented, and is obeyed by every caller except the one nobody revisited.
def test_the_cohort_payload_carries_aliases_too():
    src = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "list_analyses")
    code = "\n".join(ast.dump(n) for n in fn.body)
    assert "aliases_by_accession" in code, (
        "the cohort list must carry aliases or `/targets` cannot find ERBB2 by the name HER2")
    assert "'aliases'" in code or '"aliases"' in code


def test_an_alias_failure_costs_the_aliases_and_not_the_rows():
    """⚠⚠ `F-054`: a guard wider than the optional thing it guards deletes data.

    The rows are built and only then decorated, so a missing index degrades the search to
    gene/accession matching — it does not empty the cohort."""
    src = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "list_analyses")

    def mentions(node, name):
        return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(node))

    for t in (n for n in ast.walk(fn) if isinstance(n, ast.Try)):
        if not mentions(t, "aliases_by_accession"):
            continue
        for stmt in t.body:
            assert "list_projection" not in ast.dump(stmt), (
                "row construction is inside the alias guard: one failure there empties /targets")


# ⚠ Both surfaces must share ONE matcher. Two copies is how they diverged in the first place.
def test_one_matcher_serves_both_surfaces():
    shared = pathlib.Path("ui/src/searchRows.js").read_text(encoding="utf-8")
    assert "export function filterRows" in shared
    assert "export function normalizeQuery" in shared
    for surface in ("ui/src/components/CensusTable.jsx", "ui/src/components/TargetList.jsx"):
        text = pathlib.Path(surface).read_text(encoding="utf-8")
        assert "from '../searchRows.js'" in text, surface
        assert "function filterRows" not in text, f"{surface} defines a SECOND matcher"
