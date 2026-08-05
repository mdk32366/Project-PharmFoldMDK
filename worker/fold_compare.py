"""Exact comparison of two fold outputs — the instrument D-077 decision 2 reads.

WHAT THIS DECIDES. D-077 decision 2 asks whether ESMFold's chunked trunk is
output-invariant: fold one fixed sequence at chunk_size 64, 32 and 16, and compare.
Both readings were frozen before any fold ran —

    byte-identical across all three -> chunk_size is a memory/time knob only. The
        local ceiling is a CURVE, folds across chunk sizes are commensurable, and
        Arm B of the bisection (probing at chunk 16/32) is legitimate.

    different at all, by any margin -> chunk_size is a RECIPE DIMENSION. The ceiling
        is defined only at chunk 64, folds across chunk sizes are NOT commensurable,
        and Arm B is abandoned, not deferred. The divergence is then a reportable
        finding in its own right, and the first-divergence location is its evidence.

WHY THERE IS NO TOLERANCE, AND WHY THAT IS THE WHOLE POINT. There is no third
reading and no threshold may be invented after seeing a diff (D-041 decision 4).
"Nearly identical" is the DIFFER branch. A tolerant comparator would not merely be
imprecise -- it would silently select the *invariant* branch, unlock Arm B, and let
folds produced at different memory settings be ranked against each other. That is
why `tests/test_chunk_invariance.py::test_comparator_is_exact_not_tolerant` asserts
the absence of tolerance twice, behaviourally and statically over this source.

WHAT IT DOES NOT DO. It reports; it does not judge. It returns a verdict and a
location, never a "close enough" opinion, and it never mutates its inputs. Reading
the verdict against decision 2's frozen table is the caller's act, and the table is
already written.

Pure. No GPU, no network, no database, no imports beyond the standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

_AXES = ("x", "y", "z")


@dataclass(frozen=True)
class Divergence:
    """Where two folds first differ.

    `field` is one of "x", "y", "z", "plddt", or "length". For "length" the
    residue_index is the count at which the shorter output ended.
    """

    residue_index: int
    field: str
    left: Any
    right: Any

    def describe(self) -> str:
        if self.field == "length":
            return (f"residue count differs: {self.left} vs {self.right} "
                    f"(first missing index {self.residue_index})")
        return (f"residue {self.residue_index} field {self.field}: "
                f"{self.left!r} vs {self.right!r}")


@dataclass(frozen=True)
class ComparisonResult:
    """`identical` is the verdict decision 2's table is read against.

    `divergence` is None exactly when `identical` is True.
    """

    identical: bool
    divergence: Optional[Divergence]

    def describe(self) -> str:
        if self.identical:
            return "identical"
        return f"NOT identical -- {self.divergence.describe()}"


def _coords(fold: Mapping[str, Any]) -> Sequence[Sequence[float]]:
    return fold["coords"]


def _plddt(fold: Mapping[str, Any]) -> Sequence[float]:
    return fold["plddt"]


def compare_folds(a: Mapping[str, Any], b: Mapping[str, Any]) -> ComparisonResult:
    """Compare two fold outputs for EXACT equality of CA coordinates and pLDDT.

    Each argument is a mapping with "coords" (a sequence of (x, y, z) triples, in
    residue order) and "plddt" (per-residue confidence). Comparison is `!=` on the
    values as given -- no tolerance, no rounding, no normalisation, no sorting.

    Returns the first divergence in scan order: residue count first, then per
    residue, coordinates x/y/z before pLDDT. "First" is load-bearing -- if the
    differ branch fires, this location is the evidence that goes in the F-entry.
    """
    ca, cb = _coords(a), _coords(b)
    pa, pb = _plddt(a), _plddt(b)

    # Length first: a truncating chunk_size is the most dramatic possible
    # non-invariance, and it must report rather than die inside a zip().
    if len(ca) != len(cb):
        return ComparisonResult(False, Divergence(min(len(ca), len(cb)), "length", len(ca), len(cb)))
    if len(pa) != len(pb):
        return ComparisonResult(False, Divergence(min(len(pa), len(pb)), "length", len(pa), len(pb)))

    for i in range(len(ca)):
        for axis, field in enumerate(_AXES):
            left, right = ca[i][axis], cb[i][axis]
            if left != right:
                return ComparisonResult(False, Divergence(i, field, left, right))
        if pa[i] != pb[i]:
            return ComparisonResult(False, Divergence(i, "plddt", pa[i], pb[i]))

    return ComparisonResult(True, None)


def fold_from_pdb(pdb_text: str, plddt: Sequence[float]) -> dict:
    """Build a comparator input from a raw PDB string and its pLDDT array.

    Takes CA atoms in file order -- the order ESMFold emits them, which is residue
    order. Deliberately does NOT sort or renumber: a chunk_size that changed residue
    ORDER is a non-invariance, and normalising here would hide it.

    Parsing is delegated to `core.features.parse_pdb`, whose `Atom` carries no
    b_factor field (D-075 decision 2 addendum), so this path cannot read the
    confidence column out of the PDB even accidentally -- pLDDT arrives only through
    the explicit argument.
    """
    from core.features import parse_pdb  # noqa: PLC0415 -- keeps the comparator core stdlib-only

    cas = [at for at in parse_pdb(pdb_text) if at.is_ca]
    return {"coords": [(at.x, at.y, at.z) for at in cas], "plddt": list(plddt)}
