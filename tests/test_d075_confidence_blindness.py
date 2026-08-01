"""D-075 — feature 7 (membrane-proximal SASA) is CONFIDENCE-BLIND, proven by a biting fixture.

D-075 Decision 2 is the load-bearing test of the whole entry: `geom_proxy` is only worth running
if feature 7 carries **zero** pLDDT information. A proxy that silently leaked confidence would
look clean while reproducing the exact confound D-075 exists to exclude — the
"function exists != function does what it claims" failure class, and the same family as D-074
(an instrument diverging from its written record).

Two arms, both required, because they catch different leaks:

  ARM A — VALUES.  Identical backbone coordinates, DIFFERENT pLDDT/B-factor column values
                   -> byte-identical membrane-proximal SASA.
                   Catches: reading the B-factor column, confidence weighting, pLDDT-based
                   residue filtering.

  ARM B — SHAPE.   Identical coordinates, DIFFERING-LENGTH pLDDT array
                   -> byte-identical membrane-proximal SASA.
                   Catches: sizing the window off `len(plddt)`. Arm A CANNOT catch this — a
                   same-length/different-values fixture passes while the impl still reads the
                   pLDDT file's shape. This arm is why D-075 strengthened the drafted order.

⚠ WHY THIS FILE ALSO CONTAINS A CONTAMINATED IMPLEMENTATION.  D-075 Decision 2 requires the
fixture to be shown RED on a contaminated impl — otherwise "the fixture is not biting and the
proxy's confidence-blindness is unproven." Demonstrating that once, by hand, in a transcript,
proves it for one afternoon. So the contaminated impl lives here permanently and
`test_fixture_bites_*` asserts that BOTH ARMS SEPARATE IT. The red-then-green ritual therefore
re-runs on every gate, and a future refactor that quietly defangs an arm reddens rather than
passing. This is D-074's rule applied to a test: the instrument carries, in itself, the proof
that it works.

⚠ A STRUCTURAL NOTE ON ARM A'S STRENGTH (recorded, not hidden).  `core.features.Atom` carries no
`b_factor` field and `parse_pdb` never reads columns 60-66, so a feature built on parsed `Atom`s
cannot reach the confidence column at all. Arm A therefore passes *structurally* for any
implementation that goes through `Atom` — its real bite is against an impl that re-parses the raw
PDB text itself (the live contamination route, exercised below). `test_atom_type_cannot_carry_confidence`
pins that structural guarantee directly, so the guard is asserted rather than assumed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core import features
from core.features import MEMBRANE_PROXIMAL_FRACTION, Atom, parse_pdb, shrake_rupley

FIXTURES = Path(__file__).resolve().parent / "fixtures"
REAL_PDB = (FIXTURES / "gpbar1_id16.pdb").read_text(encoding="utf-8")
REAL_PLDDT = json.loads((FIXTURES / "gpbar1_id16.plddt.json").read_text(encoding="utf-8"))


# ── fixture builders ─────────────────────────────────────────────────────────
def _pdb_with_bfactors(bfactors: list[float]) -> str:
    """An all-atom-ish PDB whose COORDINATES are fixed and whose B-factor column is caller-set.

    One residue per entry in `bfactors`, each with CA + CB (feature 7 needs side-chain atoms to
    have any SASA to speak of). Coordinates come from a deterministic helix-ish walk so the
    structure is identical across calls — only the B-factor column varies.
    """
    lines = []
    serial = 1
    for i, b in enumerate(bfactors, start=1):
        # Deterministic, coordinate-only: depends on i, never on b.
        t = 0.6 * i
        cx, cy, cz = 6.0 * math.cos(t), 6.0 * math.sin(t), 1.5 * i
        for name, elem, off in (("CA", "C", 0.0), ("CB", "C", 1.6)):
            lines.append(
                f"ATOM  {serial:>5}  {name:<3} ALA A{i:>4}    "
                f"{cx + off:8.3f}{cy:8.3f}{cz:8.3f}  1.00{b:6.2f}           {elem}  "
            )
            serial += 1
    return "\n".join(lines) + "\n"


N_RES = 20
COORDS_FIXED_LOW = _pdb_with_bfactors([12.34] * N_RES)          # uniform low confidence
COORDS_FIXED_HIGH = _pdb_with_bfactors([97.65] * N_RES)         # uniform high confidence
COORDS_FIXED_RAMP = _pdb_with_bfactors(
    [10.0 + 4.0 * i for i in range(N_RES)]                      # a steep N->C confidence ramp
)

PLDDT_20 = [50.0] * N_RES                                        # matches the structure
PLDDT_8 = [50.0] * 8                                            # SHORTER than the structure
PLDDT_44 = [50.0] * 44                                           # LONGER than the structure


# ── the contaminated implementation (kept so the fixture keeps proving it bites) ──
def _contaminated_membrane_proximal_sasa(
    pdb_text: str, plddt: list[float] | None
) -> float | None:
    """A DELIBERATELY WRONG feature 7. Two contaminations, one per arm:

    1. (arm A) confidence-weights each residue's SASA by its B-factor, re-parsed from the raw
       text — the leak `Atom` structurally prevents but a hand-rolled parse reintroduces;
    2. (arm B) sizes the C-terminal window off `len(plddt)` instead of the coordinate residue
       count — the easy, plausible mistake, since feature 4 legitimately does exactly that.

    This function is NEVER imported by `core/`. It exists only so the fixture can prove it
    separates a contaminated impl from a clean one, on every gate run.
    """
    atoms = parse_pdb(pdb_text)
    if not atoms:
        return None
    per_atom = shrake_rupley(atoms)

    # contamination 1: re-parse the confidence column the clean path cannot see
    bfac: dict[int, float] = {}
    for line in pdb_text.splitlines():
        if line.startswith(("ATOM", "HETATM")) and len(line) >= 66:
            try:
                bfac[int(line[22:26])] = float(line[60:66])
            except ValueError:
                continue

    by_res: dict[int, float] = {}
    for atom, sasa in zip(atoms, per_atom):
        weight = bfac.get(atom.res_seq, 100.0) / 100.0          # confidence weighting
        by_res[atom.res_seq] = by_res.get(atom.res_seq, 0.0) + sasa * weight

    order = sorted(by_res)
    # contamination 2: window sized off the pLDDT array, not the coordinates
    n_for_window = len(plddt) if plddt else len(order)
    k = max(1, math.ceil(MEMBRANE_PROXIMAL_FRACTION * n_for_window))
    window = order[-k:]
    return sum(by_res[r] for r in window) / len(window)


def _clean(pdb_text: str, plddt: list[float] | None) -> float | None:
    """The real implementation under test, via the public extractor."""
    row = features.extract_features(pdb_text, plddt, boundary_method="sliced_ecd")
    return getattr(row, "membrane_proximal_sasa")


# ── ARM A — differing confidence VALUES, identical coordinates ───────────────
def test_arm_a_differing_plddt_values_give_identical_membrane_proximal_sasa():
    """D-075 Decision 2, arm A. Same backbone, three different B-factor columns (uniform low,
    uniform high, a steep ramp) -> BYTE-IDENTICAL feature 7. Not approx-equal: identical, because
    a confidence-blind computation never touched the column that differs."""
    low = _clean(COORDS_FIXED_LOW, PLDDT_20)
    high = _clean(COORDS_FIXED_HIGH, PLDDT_20)
    ramp = _clean(COORDS_FIXED_RAMP, PLDDT_20)
    assert low is not None, "feature 7 did not compute on a well-formed structure"
    assert low == high == ramp, (
        "feature 7 changed when only the pLDDT/B-factor column changed - it is NOT "
        f"confidence-blind (low={low!r} high={high!r} ramp={ramp!r})"
    )


# ── ARM B — differing pLDDT array LENGTH, identical coordinates ──────────────
def test_arm_b_differing_plddt_length_gives_identical_membrane_proximal_sasa():
    """D-075 Decision 2, arm B — the arm that actually bites. `n_res` for feature 7's window MUST
    come from the parsed coordinate residues, never `len(plddt)`. Feature 4 legitimately sizes off
    the pLDDT array, so reusing that variable is the plausible mistake; this asserts it wasn't."""
    matched = _clean(COORDS_FIXED_LOW, PLDDT_20)
    shorter = _clean(COORDS_FIXED_LOW, PLDDT_8)
    longer = _clean(COORDS_FIXED_LOW, PLDDT_44)
    none_at_all = _clean(COORDS_FIXED_LOW, None)
    assert matched is not None, "feature 7 did not compute on a well-formed structure"
    assert matched == shorter == longer == none_at_all, (
        "feature 7 changed with the LENGTH of the pLDDT array - its window is sized off "
        f"len(plddt), not the coordinates (matched={matched!r} short={shorter!r} "
        f"long={longer!r} no_plddt={none_at_all!r})"
    )


# ── the meta-tests: prove BOTH arms separate a contaminated implementation ───
def test_fixture_bites_arm_a_separates_a_contaminated_implementation():
    """⚠ D-075 Decision 2's stop-and-report condition, asserted permanently. If arm A cannot tell
    a confidence-weighting impl apart from a clean one, arm A is decoration and feature 7's
    blindness is unproven. This is the red half of red-then-green, kept green forever by asserting
    the contaminated impl FAILS the property."""
    low = _contaminated_membrane_proximal_sasa(COORDS_FIXED_LOW, PLDDT_20)
    high = _contaminated_membrane_proximal_sasa(COORDS_FIXED_HIGH, PLDDT_20)
    assert low != high, (
        "arm A does not bite: the contaminated (confidence-weighting) implementation produced "
        "the same value under different B-factor columns, so the fixture cannot detect a leak"
    )


def test_fixture_bites_arm_b_separates_a_contaminated_implementation():
    """⚠ Same, for arm B. A contaminated impl that sizes its window off `len(plddt)` must be
    separated by the differing-length fixture, or arm B proves nothing."""
    matched = _contaminated_membrane_proximal_sasa(COORDS_FIXED_LOW, PLDDT_20)
    shorter = _contaminated_membrane_proximal_sasa(COORDS_FIXED_LOW, PLDDT_8)
    assert matched != shorter, (
        "arm B does not bite: the contaminated (len(plddt)-windowed) implementation produced the "
        "same value for a 20-residue structure against 20- and 8-length pLDDT arrays"
    )


# ── structural guard that gives arm A its teeth ──────────────────────────────
def test_atom_type_cannot_carry_confidence():
    """Arm A passes structurally for anything built on `Atom`, because `Atom` has no b_factor and
    `parse_pdb` never reads columns 60-66. That guarantee is the real guard, so it is asserted
    directly rather than assumed (D-074: state the check so its inadequacy is discoverable). If a
    `b_factor` field is ever added to `Atom`, this reddens and arm A must be re-argued."""
    assert not hasattr(Atom("CA", "C", 1, "ALA", "A", 0.0, 0.0, 0.0), "b_factor"), (
        "Atom gained a b_factor field - feature 7's confidence-blindness can no longer be "
        "argued structurally and arm A's strength must be re-established"
    )
    parsed = parse_pdb(COORDS_FIXED_RAMP)
    assert parsed, "fixture PDB did not parse"
    assert not any(97.65 in (getattr(a, f, None),) for a in parsed for f in ("b_factor", "bfactor"))


# ── the window rule is REUSED, not redefined ────────────────────────────────
def test_feature7_window_reuses_feature4_rule_at_the_coordinate_count():
    """D-075 Decision 2: same window RULE as feature 4 — `k = max(1, ceil(0.25 * n_res))`,
    C-terminal — but `n_res` is the coordinate residue count. Asserted by construction: a
    structure whose C-terminal quarter has distinctive geometry must move feature 7, and the
    window must be computed from the 20 coordinate residues (k=5), not from an 8-long pLDDT
    array (k=2)."""
    assert MEMBRANE_PROXIMAL_FRACTION == 0.25, "the shared window fraction moved"
    k_from_coords = max(1, math.ceil(MEMBRANE_PROXIMAL_FRACTION * N_RES))
    k_from_short_plddt = max(1, math.ceil(MEMBRANE_PROXIMAL_FRACTION * len(PLDDT_8)))
    assert k_from_coords == 5 and k_from_short_plddt == 2, "fixture no longer distinguishes the two"
    # If the impl used len(plddt), these two would differ; arm B asserts they do not.
    assert _clean(COORDS_FIXED_LOW, PLDDT_20) == _clean(COORDS_FIXED_LOW, PLDDT_8)


# ── null-with-a-reason, never imputed (D-027 discipline extends to feature 7) ─
def test_feature7_is_null_with_a_reason_when_there_is_no_structure():
    """A failed fold (no PDB) yields feature 7 null WITH a reason — never zero, never imputed."""
    row = features.extract_features(None, REAL_PLDDT, boundary_method="sliced_ecd")
    assert getattr(row, "membrane_proximal_sasa") is None
    assert "membrane_proximal_sasa" in row.null_reasons
    assert row.null_reasons["membrane_proximal_sasa"]


def test_feature7_computes_on_the_real_stored_structure():
    """Feature 7 computes a positive area on a real ESMFold structure — the fixture PDBs are
    synthetic, so the real fold is the check that the feature is not an artefact of the builder."""
    row = features.extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd")
    value = getattr(row, "membrane_proximal_sasa")
    assert value is not None and value > 0.0, f"expected a positive area, got {value!r}"


# ── the pre-registered path is untouched (D-065 dec 5 / D-075 dec 5) ─────────
def test_preregistered_feature_count_is_still_exactly_six():
    """⚠ Feature 7 must NOT enter the pre-registered set. D-027's count is the pre-registration
    and D-075 dec 5 says a reddening here means the ablation leaked into the graded path."""
    assert len(features.FEATURE_NAMES) == 6, (
        f"the pre-registered feature set is no longer six: {features.FEATURE_NAMES}"
    )
    assert "membrane_proximal_sasa" not in features.FEATURE_NAMES
