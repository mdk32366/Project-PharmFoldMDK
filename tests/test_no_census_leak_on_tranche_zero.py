"""⚠⚠ NO CENSUS ROW MAY REACH A TRANCHE-ZERO SURFACE. A named stop condition, made structural.

**Why this file exists, measured before a single census row was written:** 75 of the 82 cohort
accessions also appear in the census manifest — `P04626` HER2, `P00533` EGFR, `Q13421` MSLN,
`P11717` IGF2R, `Q8WXI7` MUC16 among them; all 82 appear in the census roster.

`app/reads.py:coverage_payload` iterates the 82 from `build_manifest()` and looks each accession up
in a dict built from the database. ⚠ **Two of those dict-builders were NOT tranche-filtered**, so
the first census fold of `P04626` would have put a census `analysis_id` under HER2's accession —
and the cohort's coverage row would then point at a fold measured under a **different span
definition**. ⚠ **There is no `ORDER BY`, so which row wins is whatever the database returns last:
nondeterministic, and silently so.**

⚠ **The class matters more than the two instances.** Any unfiltered read of `protein_analyses` in
`app/` is a latent leak, including one in a function nobody has written yet — so the guard
enumerates them rather than naming them.
"""

from __future__ import annotations

import csv
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent


def test_the_overlap_that_makes_this_necessary_is_real():
    """⚠ A-017 clause (c). If the cohort and the census shared no accession, every assertion below
    would pass for the wrong reason — there would be nothing to leak.

    Prove it bites by pointing this at two disjoint files: the premise evaporates and the guard
    below becomes untested."""
    cohort = {l.split()[0] for l in (REPO / "data" / "cohort_82_accessions.txt")
              .read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}
    with (REPO / "data" / "census" / "census_manifest.v7.csv").open(encoding="utf-8", newline="") as fh:
        census = {r["census_accession"] for r in csv.DictReader(fh)}
    overlap = cohort & census
    assert len(overlap) >= 50, (
        f"only {len(overlap)} accessions overlap — if this has genuinely collapsed, the leak this "
        f"file guards may no longer be reachable and the guard needs re-justifying, not deleting")
    for known in ("P04626", "P00533", "Q13421"):
        assert known in overlap, f"{known} is no longer in both populations"


def _selects_in(path: pathlib.Path) -> list[tuple[str, str]]:
    """(function name, the statement text) for every `select(ProteinAnalysis…)` in a module."""
    src = path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"select\(\s*ProteinAnalysis", src):
        fn_start = src.rfind("\ndef ", 0, m.start())
        name = src[fn_start + 5: src.index("(", fn_start + 5)] if fn_start != -1 else "<module>"
        # the statement runs to the closing `).all()` / `).scalar…` / `)\n` at the same depth;
        # a generous window is fine — we only ask whether the filter appears inside it.
        out.append((name.strip(), src[m.start(): m.start() + 1200]))
    return out


def test_every_select_of_protein_analyses_in_app_is_tranche_filtered():
    """⚠⚠ THE CLASS GUARD. Enumerated, not named — so a leak in a function written next month reds
    here rather than surfacing as a wrong coverage number six weeks later.

    Prove it bites by removing `.where(ProteinAnalysis.cohort_tranche == COHORT_TRANCHE)` from any
    of them: the function is named in the failure, not merely counted.

    ⚠⚠ THE EXEMPTION IS NARROW, EXPLICIT, AND IT IS NOT A LOOPHOLE: a read scoped by a PRIMARY KEY
    — `ProteinAnalysis.id == …` or `JobRecord.id == …` — is exempt, because it already addresses
    exactly one row and a caller holding that id reached it through a filtered surface.

    ⚠ **Filtering those would BREAK CENSUS FOLDING, not protect it.** `artifacts_present` is the
    server-side proof `/complete` requires before flipping a job's status, and census jobs must
    complete too. A tranche filter there would make every census fold un-completable — a guard
    doing the opposite of its purpose.

    The distinction is between a SURFACE (which must never show a census row beside the 82) and an
    OPERATIONAL LOOKUP on one addressed row (which must work for every row there is)."""
    unfiltered = []
    for path in sorted((REPO / "app").glob("*.py")):
        for fn, stmt in _selects_in(path):
            if "cohort_tranche" in stmt:
                continue
            if re.search(r"(ProteinAnalysis|JobRecord)\.id\s*==", stmt):
                continue      # ⚠ by-primary-key operational lookup — exempt, and stated above
            unfiltered.append(f"{path.name}:{fn}")
    assert not unfiltered, (
        "unfiltered select(ProteinAnalysis) — a census row can reach a tranche-zero surface "
        f"through: {unfiltered}")


def test_the_scan_actually_finds_selects_rather_than_passing_on_an_empty_list():
    """⚠ A-017 clause (a). A scan that matches nothing passes perfectly and guards nothing — which
    is how three revert proofs proved nothing on 2026-08-06."""
    found = [(p.name, fn) for p in sorted((REPO / "app").glob("*.py")) for fn, _ in _selects_in(p)]
    assert len(found) >= 3, f"the scan found only {found} — it is not reaching the real reads"
    names = {fn for _, fn in found}
    assert "list_analyses" in names and "_folded_accessions" in names


def test_the_cohort_tranche_constant_is_zero_and_the_filter_is_equality():
    """⚠ `== COHORT_TRANCHE`, never `!= something` and never `IS NULL OR == 0`. An untagged row
    must be INVISIBLE to the cohort surface, not included by a negation that treats NULL as safe.

    Prove it bites by rewriting any filter as `!= 1`: a NULL-tranche row then passes."""
    from app.reads import COHORT_TRANCHE
    assert COHORT_TRANCHE == 0
    src = (REPO / "app" / "reads.py").read_text(encoding="utf-8")
    assert "cohort_tranche == COHORT_TRANCHE" in src
    assert "cohort_tranche !=" not in src, (
        "a BARE NEGATION is banned on BOTH surfaces. The cohort filter must be `== COHORT_TRANCHE`; "
        "the census filter must be `> COHORT_TRANCHE`. `!=` reads as 'everything that is not the "
        "cohort' while silently excluding NULL under three-valued logic — so an untagged row would "
        "be invisible on both surfaces at once.")
    # ⚠ The census surface exists now (D-087) and must use the POSITIVE form.
    assert "cohort_tranche > COHORT_TRANCHE" in src, "the census filter is missing or negated"
    # ⚠ And the rows that fall through BOTH filters must be counted, not left to be inferred from a
    # total that does not add up.
    assert "def census_untranched_count" in src, (
        "nothing counts NULL-tranche rows — they are invisible on both surfaces by construction, "
        "which is correct only if something reports them")
