"""D-058 / D-027 — the feature extractor's test surface, written to bite.

Every constant D-058 fixed by convention (0.25, 8 Å, 92 points, 1.4 Å) is pinned here so a
silent edit reddens the gate rather than passing; the SASA kernel is checked against a
CLOSED FORM (an isolated atom is exactly `4π(r+probe)²`), never against another implementation;
the feature COUNT is asserted at exactly six (D-027's pre-registration — "the test that makes
this entry real"); and a failed/malformed fold is asserted to produce null-with-a-reason,
never an imputed mean.

The all-atom premise (features 5–6 need side chains) is asserted on a REAL stored structure —
`tests/fixtures/gpbar1_id16.pdb`, GPBAR1's ECD fold pulled from the public read API — so the
premise is captured permanently instead of checked once by hand (D-058 consequences).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from core import features
from core.features import (
    CONTIGUITY_CA_ANGSTROM,
    FEATURE_NAMES,
    REL_SASA_ACCESSIBLE,
    SASA_PROBE_RADIUS,
    SASA_SAMPLE_POINTS,
    Atom,
    extract_features,
    feature_version,
    parse_pdb,
    shrake_rupley,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
REAL_PDB = (FIXTURES / "gpbar1_id16.pdb").read_text(encoding="utf-8")
REAL_PLDDT = json.loads((FIXTURES / "gpbar1_id16.plddt.json").read_text(encoding="utf-8"))


# ── SASA kernel: closed form, NOT self-consistency (D-058 §3) ────────────────
def test_isolated_atom_returns_the_closed_form_sphere():
    """A single atom has no neighbours, so every sample point is accessible and its SASA is
    exactly 4π(r+probe)² — the D-058 anchor, an independent expectation, not the code's own output."""
    atom = Atom("CB", "C", 7, "LEU", "A", 3.14, -2.72, 1.41)  # distinctive coords, no zeros
    r = atom.radius + SASA_PROBE_RADIUS
    expected = 4.0 * math.pi * r * r
    (got,) = shrake_rupley([atom])
    assert got == pytest.approx(expected, rel=1e-9)


def test_two_well_separated_atoms_are_exactly_twice_one():
    """Two atoms farther apart than 2(r+probe) cannot bury each other's points, so the total is
    exactly twice the single-atom sphere. Separation chosen well beyond the interaction cutoff."""
    r = features.DEFAULT_VDW + SASA_PROBE_RADIUS
    one = 4.0 * math.pi * r * r
    atoms = [Atom("C", "C", 1, "ALA", "A", 0.0, 0.0, 0.0),
             Atom("C", "C", 2, "ALA", "A", 47.3, 0.0, 0.0)]  # >> 2(r+probe)
    assert sum(shrake_rupley(atoms)) == pytest.approx(2.0 * one, rel=1e-9)


# ── the pre-registration: six features, fixed (D-027 / D-058 §3) ─────────────
def test_exactly_six_features_are_named():
    assert len(FEATURE_NAMES) == 6, "D-027 fixed the feature count at six; a seventh needs a new entry"


def test_extractor_emits_exactly_six_features():
    row = extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd")
    feats = row.as_feature_dict()
    assert len(feats) == 6
    assert set(feats) == set(FEATURE_NAMES)


def test_the_convention_parameters_are_pinned():
    """0.25, 8 Å, 92 points, 1.4 Å are external conventions fixed BEFORE any fit (D-058 dec 2);
    changing one must redden the gate rather than silently move feature 6 or the SASA scale."""
    assert REL_SASA_ACCESSIBLE == 0.25          # exposed/buried cutoff
    assert CONTIGUITY_CA_ANGSTROM == 8.0        # CA–CA contact distance
    assert SASA_SAMPLE_POINTS == 92             # Shrake & Rupley's published value
    assert SASA_PROBE_RADIUS == 1.4             # water probe


# ── correctness + honesty ────────────────────────────────────────────────────
def test_all_six_features_compute_on_a_real_fold():
    row = extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd")
    for name in FEATURE_NAMES:
        assert getattr(row, name) is not None, f"{name} should compute on a real all-atom fold"
    assert row.null_reasons == {}, "no feature is null on a healthy fold, so no reasons"
    assert 0.0 <= row.largest_patch_fraction <= 1.0  # it is a fraction of total SASA


def test_features_are_deterministic_byte_identical():
    a = extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd").as_feature_dict()
    b = extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd").as_feature_dict()
    assert a == b, "identical inputs must yield identical features (D-027 determinism)"


def test_stored_structure_is_all_atom():
    """D-058: features 5 and 6 require side-chain atoms. Asserted on a REAL stored structure so the
    premise cannot decay into an assumption — distinct side-chain atom names beyond the N/CA/C/O
    backbone must be present. If this ever fails, features 5 and 6 need a D-058 amendment."""
    atoms = parse_pdb(REAL_PDB)
    names = {a.name for a in atoms}
    backbone = {"N", "CA", "C", "O"}
    side_chain = names - backbone
    assert {"CB", "CG"} <= names, "expected common side-chain atoms (CB, CG) in an all-atom fold"
    assert len(side_chain) >= 5, f"expected several distinct side-chain atom names, saw {side_chain}"


def test_hand_checkable_radius_of_gyration():
    """A synthetic four-CA structure whose radius of gyration is computed by hand. Four CAs at
    (±d, 0, 0) and (0, ±d, 0) with d chosen distinctive: the centroid is the origin, so
    Rg = sqrt(mean(|r|²)) = d, and the stored feature is d / n_residues (length-normalised)."""
    d = 3.7
    coords = [(d, 0.0, 0.0), (-d, 0.0, 0.0), (0.0, d, 0.0), (0.0, -d, 0.0)]
    pdb_lines = []
    for i, (x, y, z) in enumerate(coords, start=1):
        pdb_lines.append(
            f"ATOM  {i:>5}  CA  ALA A{i:>4}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.50           C  "
        )
    pdb = "\n".join(pdb_lines) + "\n"
    row = extract_features(pdb, [61.0, 62.0, 63.0, 64.0], boundary_method="sliced_ecd")
    expected_rg = d          # centroid at origin, all points at distance d
    assert row.radius_of_gyration == pytest.approx(expected_rg / 4, rel=1e-9)


def test_membrane_proximal_derives_from_span_length_not_a_fixed_count():
    """Feature 4 is the mean over the C-terminal 25% of the folded span, and 25% is taken of the
    ACTUAL span length (D-027/D-058 §2.4), so a longer and a shorter fold use different windows
    and give different results — never a fixed residue count."""
    # Distinctive per-residue values: a low N-terminal block, a high C-terminal block.
    short = [10.1, 10.2, 10.3, 90.7, 90.9, 91.1, 91.3, 91.5]           # len 8  -> k=ceil(2.0)=2
    long_ = short + [10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 11.4, 11.5]  # len 20 -> k=5
    r_short = extract_features(None, short, boundary_method="sliced_ecd")
    r_long = extract_features(None, long_, boundary_method="sliced_ecd")
    # short: last 2 of the high block; long: last 5 (all low tail) — materially different windows.
    assert r_short.membrane_proximal_plddt == pytest.approx(sum(short[-2:]) / 2)
    assert r_long.membrane_proximal_plddt == pytest.approx(sum(long_[-5:]) / 5)
    assert r_short.membrane_proximal_plddt != pytest.approx(r_long.membrane_proximal_plddt)


def test_boundary_method_travels_with_the_row():
    """Feature 4 is cross-method incomparable (D-021/D-027); the boundary method must ride on the
    row so a `whole` value is never silently compared to a `sliced_ecd` one downstream."""
    assert extract_features(REAL_PDB, REAL_PLDDT, boundary_method="whole").boundary_method == "whole"
    assert extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd").boundary_method == "sliced_ecd"


def test_malformed_structure_is_null_with_reason_never_imputed():
    """A structure with no parseable atoms yields nulls WITH reasons for the structural features —
    and no mean is ever substituted (D-027: imputing a mean is the worst available option)."""
    row = extract_features("this is not a pdb\nGARBAGE\n", REAL_PLDDT, boundary_method="sliced_ecd")
    for name in ("radius_of_gyration", "sasa_normalized", "largest_patch_fraction"):
        assert getattr(row, name) is None
        assert name in row.null_reasons and row.null_reasons[name]
    # The pLDDT-derived features still compute — a malformed PDB does not poison good pLDDT.
    assert row.mean_plddt_ecd is not None


def test_missing_structure_records_the_failure_not_a_skip():
    """A failed fold has an analysis row but no structure (IGF2R — D-058 Addendum 2 §1). All three
    structural features are null with a reason naming the fold failure — distinct from a skipped
    row and never an imputed value; the reason must NOT read as 'malformed'."""
    row = extract_features(None, None, boundary_method="whole", mean_plddt=None)
    for name in FEATURE_NAMES:
        assert getattr(row, name) is None
    assert set(FEATURE_NAMES) <= set(row.null_reasons)
    assert "no structure" in row.null_reasons["sasa_normalized"]
    assert row.below_plddt_floor is None  # no pLDDT → floor undecidable, not defaulted to a bool


def test_below_floor_is_recorded_from_the_stored_mean():
    """The D-041 §5 floor (50) is stored as read, not recomputed. A just-under target reads
    below-floor; a just-over one does not — CXCR5 at 47.63 is the floor working (Addendum §4)."""
    under = extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd", mean_plddt=47.63)
    over = extract_features(REAL_PDB, REAL_PLDDT, boundary_method="sliced_ecd", mean_plddt=52.01)
    assert under.below_plddt_floor is True
    assert over.below_plddt_floor is False


def test_feature_version_is_the_source_hash_not_a_constant():
    """feature_version is DERIVED from this module's source (D-027), so a refit against changed
    feature code is detectable. Recomputed here independently: a hand-typed literal in place of the
    derivation would fail this (D-009 red-on-change)."""
    source = Path(features.__file__).read_bytes()
    expected = hashlib.sha256(source).hexdigest()[:12]
    assert feature_version() == expected
    assert len(feature_version()) == 12


# ── the ORM model builds under the SQLite test path (D-005) ──────────────────
def test_protein_features_orm_builds_on_sqlite():
    from sqlalchemy import create_engine, inspect

    from db.models import Base

    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    cols = {c["name"] for c in inspect(engine).get_columns("protein_features")}
    for name in FEATURE_NAMES:
        assert name in cols, f"protein_features must carry the {name} column"
    assert {"null_reasons", "mean_plddt", "below_plddt_floor", "feature_version",
            "analysis_id", "ranking_run_id", "computed_at"} <= cols


# ── migration 0003 proven by QUERY, not by alembic's exit code (D-058 §1.1) ──
@pytest.mark.postgres
def test_migration_0003_created_protein_features(pg_engine):
    """`docs/HAZARD-search-path-seams.md`: `alembic upgrade head` can exit 0 while the DDL rolls
    back. So the table's existence is proven by querying `information_schema.tables` after the
    CI job's `alembic upgrade head`, never inferred from the exit code."""
    from sqlalchemy import text

    with pg_engine.connect() as c:
        present = c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'protein_features'"
        )).scalar()
        assert present == "protein_features", "0003 must create protein_features (proven by query)"
        colnames = {r[0] for r in c.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'protein_features'"
        ))}
    for name in FEATURE_NAMES:
        assert name in colnames
    assert {"null_reasons", "mean_plddt", "below_plddt_floor", "feature_version"} <= colnames
