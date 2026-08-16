"""Three paths to one quantity, compared — at enqueue and again after the fold.

⚠ **NO `assert` ANYWHERE IN THIS MODULE, AND THAT IS A RULE, NOT A STYLE.** `assert` vanishes under
`python -O`, so a guard written as one is *a comment that occasionally runs*. Every check whose
failure would produce a wrong artifact raises an explicit exception. `assert` is for internal
invariants whose violation is a crash — never for a guard standing between a claim and a result.

⚠ **WHY BOTH ENDS.** The enqueue-time check proves the slice was correct **when it was cut**. It
cannot see corruption in transit — serialisation, a DB round-trip, a truncated payload — and the
fold record is what gets read six months from now. The post-fold check compares the structure the
fold **actually produced** against the manifest, which is the only comparison that is end-to-end.

⚠ **NEITHER NEEDS A WORKER CHANGE.** The first runs beside `_fold_input`; the second reads the
residue count out of a PDB that already exists.

**The context:** on 2026-08-07 the census manifest carried `span_aa` — a length — and **no
coordinates**, while `core/enqueue.py` fell through to folding the whole sequence for any
unrecognised `boundary_method`. Every artifact would have been internally consistent while
describing the wrong molecule 3,468 times. **These checks are what make "it sliced correctly" a
measurement instead of an expectation.**
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class FoldLengthMismatch(ValueError):
    """⚠ A sliced sequence, or a folded structure, whose length disagrees with its manifest span.

    Raised, never asserted, never warned. **A mismatch halts the crank** — the alternative is a
    plausible, dated, provenanced artifact of the wrong molecule.
    """


def check_sliced_length(accession: str, boundary_method: str, span: Optional[int],
                        fold_seq: str, full_length: int) -> int:
    """Enqueue-time. Returns the sliced length; raises on disagreement.

    ⚠ **Both branches are checked, not just the sliced one.** A guard that only runs on the path
    already believed correct guards nothing — the same shape as a guard placed downstream of the
    filter it guards. For `whole` the claim is *"the whole sequence was folded"*, and that is
    equally checkable.
    """
    n = len(fold_seq)
    if boundary_method == "sliced_ecd":
        if span is None:
            raise FoldLengthMismatch(
                f"{accession}: boundary_method is 'sliced_ecd' with no span to check against")
        if n != span:
            raise FoldLengthMismatch(
                f"{accession}: sliced {n} residues but the manifest span is {span}. "
                f"⚠ span and the coordinates are two paths to one quantity and they disagree.")
    elif boundary_method == "whole":
        if n != full_length:
            raise FoldLengthMismatch(
                f"{accession}: boundary_method is 'whole' but {n} residues were taken from a "
                f"sequence of {full_length}")
    else:
        raise FoldLengthMismatch(
            f"{accession}: unrecognised boundary_method {boundary_method!r} reached the length "
            f"check — there is no claim to verify")
    return n


def residues_in_pdb(pdb_text: str) -> int:
    """Distinct `(chain, res_seq)` in the structure. ⚠ Counted from the artifact itself.

    Deliberately NOT `len(plddt)` or a stored field: the point is to read the thing the fold
    produced, not a number recorded alongside it. A count taken from the same record as the claim
    cannot disagree with it.
    """
    from core.features import parse_pdb
    return len({(a.chain, a.res_seq) for a in parse_pdb(pdb_text)})


@dataclass
class Reconciliation:
    accession: str
    span_aa: Optional[int]
    enqueue_length: Optional[int]
    structure_residues: int
    agrees: bool
    detail: str


def reconcile_fold(accession: str, span_aa: Optional[int], enqueue_length: Optional[int],
                   pdb_text: str, *, strict: bool = True) -> Reconciliation:
    """Post-fold. ⚠ THREE NUMBERS THAT MUST AGREE: the manifest's `span_aa`, the length recorded at
    enqueue, and the residue count read out of the produced structure.

    `strict=False` returns the disagreement instead of raising — for a survey over folds that have
    already happened, where the finding is the report rather than a halt.
    """
    n = residues_in_pdb(pdb_text)
    claims = [c for c in (span_aa, enqueue_length) if c is not None]
    agrees = bool(claims) and all(c == n for c in claims)
    detail = (f"span_aa={span_aa} enqueue_length={enqueue_length} structure_residues={n}")
    if not agrees and strict:
        raise FoldLengthMismatch(
            f"{accession}: the folded structure does not reconcile with the manifest. {detail}. "
            f"⚠ The structure is the only end-to-end evidence; a disagreement here means the "
            f"artifact describes a different molecule from the one the manifest pre-registered.")
    return Reconciliation(accession, span_aa, enqueue_length, n, agrees, detail)
