"""A SECOND INSTRUMENT on the claim the whole census rests on — `D-103`.

⚠⚠ THE CLAIM AND ITS SINGLE SOURCE. Every one of the 3,467 manifest rows asserts an extracellular
span, and every one was decided the same way: `boundary_method: sliced_ecd`, `span_rule: vocabulary`
(3,342) or `gpi_rule_A` (125). **That is UniProt topology annotation — ONE instrument, never
independently checked.** In a project whose most-repeated defect class is *two paths to one quantity,
never compared*, the most load-bearing claim on the platform had only one path.

⚠ THE SECOND INSTRUMENT IS GENUINELY DIFFERENT, WHICH IS THE ENTIRE VALUE. HPA's subcellular data is
**immunofluorescence imaging** — antibodies photographed in fixed cells. UniProt topology is
**sequence and annotation**. They can fail in completely different ways, so agreement is evidence and
disagreement is informative. Two readings of the same sequence would have been neither.

⚠⚠ AND THE HARD PART, STATED FIRST BECAUSE IT IS WHERE THIS GOES WRONG: A GOLGI OR VESICLE CALL DOES
NOT REFUTE A SURFACE ASSIGNMENT. The secretory route IS ribosome -> ER -> Golgi -> vesicle -> plasma
membrane. A genuine surface protein can sit predominantly in that pipeline at steady state. Reading
"not plasma membrane" as "not a surface protein" would produce a confident, plausible, wrong
answer — `F-047`'s class, and the third such trap found in a single day. **So the route is its own
category, and it is NOT counted as disagreement.**

⚠ NOTHING HERE IS A SCORE, A CONFIDENCE, OR A QUALITY. The output is a CATEGORY with a cause, in the
`D-079` tradition: it says what the two instruments did, never whether the protein is good. There is
no ordering defined on these categories and none may be invented.
"""
from __future__ import annotations

from typing import Iterable, NamedTuple, Optional

#: ⚠⚠ THE SECRETORY ROUTE — a surface protein legitimately shows here. NOT disagreement.
ROUTE_COMPARTMENTS = frozenset({
    "Plasma membrane", "Vesicles", "Golgi apparatus", "Endoplasmic reticulum",
    "Cell Junctions", "Focal adhesion sites", "Endosomes", "Lysosomes", "Peroxisomes",
})

#: Compartments a protein whose main signal sits there is hard to reconcile with a surface
#: assignment. ⚠ "Hard to reconcile" is deliberately not "wrong" — see `UNRECONCILED_CAUSES`.
UNRECONCILED_COMPARTMENTS = frozenset({
    "Nucleoli", "Nucleoli fibrillar center", "Nucleoli rim", "Nuclear bodies",
    "Nuclear speckles", "Mitochondria", "Kinetochore", "Mitotic chromosome",
})

#: ⚠⚠ THREE CAUSES, AND WE CANNOT TELL THEM APART FROM HERE. Naming all three is what keeps the
#: category from being read as a verdict on the protein.
UNRECONCILED_CAUSES = (
    "the UniProt topology annotation may be wrong",
    "the HPA antibody may be non-specific, or the cell line may not express the protein",
    "the protein may genuinely do both, at different times or in different tissues",
)

#: The categories. ⚠ NO ORDERING IS DEFINED and none may be invented — these are kinds, not grades.
CATEGORIES = (
    "corroborated_membrane",   # HPA main location includes Plasma membrane
    "corroborated_route",      # main location is on the secretory route, but not the membrane
    "mixed",                   # main locations span route and unreconciled compartments
    "unreconciled",            # main locations are ONLY hard-to-reconcile compartments
    "if_not_attempted",        # ⚠ HPA has the gene but made no subcellular call — NOBODY LOOKED
    "gene_absent_from_supplier",
    "no_gene_symbol",
    # ⚠ one identifier, several supplier rows that DISAGREE about the reading
    "supplier_row_ambiguous",
)

#: ⚠ HPA's OWN confidence in its imaging call, carried verbatim and labelled as theirs. It is not
#: our judgement and must never be presented as one.
IF_RELIABILITY = ("Enhanced", "Supported", "Approved", "Uncertain")


class SurfaceCheck(NamedTuple):
    category: str
    main_locations: tuple[str, ...]
    if_reliability: Optional[str]      # ⚠ HPA's, not ours
    on_membrane: bool
    route_locations: tuple[str, ...]
    unreconciled_locations: tuple[str, ...]

    @property
    def corroborates(self) -> bool:
        """⚠ True only where the second instrument SUPPORTS the surface assignment.

        ⚠⚠ `False` is NOT refutation — `if_not_attempted` returns False and means nobody looked.
        Any consumer reading this as a negative finding is making the error this module exists to
        prevent, which is why `category` is the field that renders and this is a convenience.
        """
        return self.category in ("corroborated_membrane", "corroborated_route")


def check(main_locations: Iterable[str], if_reliability: Optional[str] = None,
          gene_present: bool = True, gene_symbol: Optional[str] = "x") -> SurfaceCheck:
    """Compare HPA's imaging call against the census's topology-derived surface assignment.

    ⚠⚠ ABSENCE IS THREE DIFFERENT THINGS and they are never pooled: the census row has no gene
    symbol to look up; the gene is absent from the supplier entirely; or the gene is present and
    **HPA made no subcellular call** — 1,420 of 2,598, so the common case by far. *"Nobody looked"*
    is not *"looked and found nothing"*, and a single empty value would say the wrong one.
    """
    if not gene_symbol:
        return SurfaceCheck("no_gene_symbol", (), None, False, (), ())
    if not gene_present:
        return SurfaceCheck("gene_absent_from_supplier", (), None, False, (), ())

    mains = tuple(m.strip() for m in main_locations if m and m.strip())
    if not mains:
        return SurfaceCheck("if_not_attempted", (), if_reliability, False, (), ())

    route = tuple(m for m in mains if m in ROUTE_COMPARTMENTS)
    hard = tuple(m for m in mains if m in UNRECONCILED_COMPARTMENTS)
    on_membrane = "Plasma membrane" in mains

    if on_membrane:
        cat = "corroborated_membrane"
    elif route and hard:
        cat = "mixed"
    elif route:
        cat = "corroborated_route"
    elif hard:
        cat = "unreconciled"
    else:
        # ⚠ compartments in neither set (Cytosol, Nucleoplasm, Microtubules…). NOT unreconciled:
        # a cytosolic call on a membrane protein is ambiguous, not contradictory, and inventing a
        # verdict for it would be exactly the overreach this module refuses.
        cat = "mixed"

    return SurfaceCheck(cat, mains, if_reliability, on_membrane, route, hard)


# ────────────────────────────────────────────────────────────────────────────────────────────
# Loading the second instrument's readings, and joining them to the census.

import csv as _csv          # noqa: E402
import functools as _ft     # noqa: E402
import pathlib as _pl       # noqa: E402

SOURCE_CSV = _pl.Path("data/census/surface_confirmation.v1.csv")

#: What the two instruments ARE, carried to the surface so no reader has to be told separately.
INSTRUMENTS = {
    "census": "UniProt topology annotation — sequence and curation",
    "hpa_if": "HPA immunofluorescence — antibodies imaged in fixed cells",
}


@_ft.lru_cache(maxsize=1)
def _index(path: str | None = None) -> tuple[dict, dict]:
    """(by accession, by gene symbol). ⚠ Two indexes so the join can be COMPARED, not assumed."""
    p = _pl.Path(path) if path else SOURCE_CSV
    if not p.exists():
        return {}, {}
    # ⚠⚠ LISTS, NOT FIRST-WINS. One UniProt accession can appear on SEVERAL supplier rows —
    # `Q6IEY1` is carried by both `OR4F16` and `OR4F3`, olfactory receptor paralogues that share a
    # UniProt entry. `setdefault` silently took whichever row came first, which is the
    # two-paths-to-one-identifier defect this project hits most. It was caught only because a test
    # COMPARED the accession path against the symbol path instead of trusting either.
    by_acc: dict[str, list[dict]] = {}
    by_sym: dict[str, list[dict]] = {}
    with p.open(encoding="utf-8") as fh:
        for row in _csv.DictReader(fh):
            for acc in (row.get("uniprot") or "").split(","):
                if acc.strip():
                    by_acc.setdefault(acc.strip(), []).append(row)
            if row.get("gene_symbol"):
                by_sym.setdefault(row["gene_symbol"], []).append(row)
    return by_acc, by_sym


def _one(rows):
    """(the row, whether the choice was AMBIGUOUS in a way that changes the answer).

    ⚠ Several rows for one identifier only matter if they DISAGREE about the reading. Where every
    candidate carries the same location call, picking any of them is not a choice at all.
    """
    if not rows:
        return None, False
    calls = {(r.get("main_location") or "").strip() for r in rows}
    return rows[0], len(calls) > 1


def check_for(accession: str | None, gene_symbol: str | None,
              path: str | None = None) -> SurfaceCheck:
    """The second instrument's verdict for one census protein.

    ⚠⚠ ACCESSION FIRST, SYMBOL AS FALLBACK — and NEITHER PATH DOMINATES. The census is keyed on
    accession and `D-093` decision 6 item (3) disqualifies a join through a lossy intermediate, so
    accession leads on principle. But measured over the 2,690 folded census proteins, it does NOT
    reach further: **2,579 resolve both ways, 16 by accession only, 20 by symbol only.**

    ⚠ An earlier version of this docstring claimed accession reached MORE rows (1,185 vs 1,179).
    **That was measured against a build that silently dropped rows with no imaging call**, and it
    stopped being true the moment that bug was fixed. *Corrected here rather than deleted, because
    a number that was right about the wrong artifact is the failure worth remembering.*

    ⚠⚠ And where both resolve they agree on the reading **except once**: `Q6IEY1` is carried by two
    supplier rows, `OR4F16` and `OR4F3` — paralogues sharing one UniProt entry. See `_one`.
    """
    by_acc, by_sym = _index(path)
    row, ambiguous = _one(by_acc.get(accession) if accession else None)
    if row is None:
        row, ambiguous = _one(by_sym.get(gene_symbol) if gene_symbol else None)
    # ⚠⚠ An identifier naming several DIFFERENT readings is a category, never a coin toss.
    if row is not None and ambiguous:
        return SurfaceCheck("supplier_row_ambiguous", (), None, False, (), ())
    if row is None:
        return check((), None, gene_present=False, gene_symbol=gene_symbol)
    mains = [m.strip() for m in (row.get("main_location") or "").split(",") if m.strip()]
    return check(mains, (row.get("if_reliability") or "").strip() or None,
                 gene_present=True, gene_symbol=gene_symbol)


def payload_for(accession: str | None, gene_symbol: str | None,
                path: str | None = None) -> dict:
    """The renderable block. ⚠ Carries the CAUSES, so the surface cannot show a bare category."""
    v = check_for(accession, gene_symbol, path)
    # ⚠⚠ THIS SURFACE RENDERS HPA VALUES TOO — subcellular locations and HPA's own Reliability (IF),
    # both from `proteinatlas.tsv`. It was built on 2026-08-20, AFTER the audit that found the
    # attribution gap, and it shipped without attribution. `F-052`: a convention obeyed by every
    # caller except the newest one.
    from core.hpa_attribution import attribution_block
    return {
        "attribution": attribution_block(gene_symbol, "protein"),
        "category": v.category,
        "main_locations": list(v.main_locations),
        "if_reliability": v.if_reliability,           # ⚠ HPA's own confidence, labelled as theirs
        "unreconciled_locations": list(v.unreconciled_locations),
        "instruments": dict(INSTRUMENTS),
        # ⚠⚠ carried on every unreconciled payload so a reader never sees the category alone
        "unreconciled_causes": list(UNRECONCILED_CAUSES) if v.category == "unreconciled" else [],
    }
