"""Fold-runner pure logic (D-018) — runs on the CI gate, no GPU.

Everything here exercises the runner's *record-keeping and rescaling*, which is where
correctness that matters downstream lives: the pLDDT scale (S-001), and the
slice/truncation provenance the D-015 §1a diagnostics depend on. The actual fold is
GPU-bound and lives behind `test_fold_*` (auto-skips without torch+CUDA), validated
on a GPU host — the int8 recipe is already measured (S-003/S-005).
"""

from datetime import datetime, timezone

import pytest

from worker import runner
from worker.runner import (
    SLICED_ECD,
    WHOLE,
    FoldProvenance,
    FoldResult,
    apply_length_cap,
    build_provenance,
    rescale_plddt,
    write_artifacts,
)


# ── pLDDT rescale (S-001: ESMFold returns 0–1; downstream wants 0–100) ────────

def test_rescale_lifts_0_1_scale_to_0_100():
    assert rescale_plddt([0.0, 0.5, 1.0]) == [0.0, 50.0, 100.0]


def test_rescale_leaves_0_100_scale_untouched_and_is_idempotent():
    already = [12.0, 70.7, 99.9]
    assert rescale_plddt(already) == already
    assert rescale_plddt(rescale_plddt([0.707])) == [70.7]   # double-call can't inflate


def test_rescale_empty_is_empty():
    assert rescale_plddt([]) == []


# ── length cap / truncation (a truncated fold is a different molecule — §1a) ──

def test_no_cap_never_truncates():
    seq = "M" * 700
    assert apply_length_cap(seq, None) == (seq, False)


def test_within_cap_not_truncated():
    seq = "M" * 400
    assert apply_length_cap(seq, 440) == (seq, False)


def test_over_cap_is_truncated_and_flagged():
    seq = "M" * 630
    out, truncated = apply_length_cap(seq, 440)
    assert truncated is True and len(out) == 440


# ── provenance: the record that makes §1a enforceable ─────────────────────────

def test_provenance_records_a_sliced_ecd():
    p = build_provenance("M" * 248, dtype="int8", chunk_size=64, source=SLICED_ECD,
                         ecd_start=27, ecd_end=274, length_cap=None,
                         now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert p.source == SLICED_ECD and p.ecd_start == 27 and p.ecd_end == 274
    assert p.truncated is False and p.input_length == 248 and p.original_length == 248
    assert p.dtype == "int8" and p.chunk_size == 64
    assert p.model_revision == runner.MODEL_REVISION      # weights pinned (§7)
    assert p.folded_at.startswith("2026-01-01")


def test_provenance_records_the_whole_sequence_fallback():
    # FOLR1 / GPI-anchored: no topological ECD to slice, folded whole (D-009 §2 fallback).
    p = build_provenance("M" * 257, dtype="int8", chunk_size=64, source=WHOLE,
                         ecd_start=None, ecd_end=None, length_cap=None)
    assert p.source == WHOLE and p.ecd_start is None


def test_provenance_flags_truncation_with_the_cap():
    p = build_provenance("M" * 630, dtype="int8", chunk_size=64, source=SLICED_ECD,
                         ecd_start=23, ecd_end=652, length_cap=440)
    assert p.truncated is True                      # §1a: excludable from ranking claims
    assert p.input_length == 440 and p.original_length == 630 and p.length_cap == 440


def test_provenance_rejects_an_unknown_source():
    with pytest.raises(ValueError):
        build_provenance("M" * 10, dtype="int8", chunk_size=64, source="guess",
                         ecd_start=None, ecd_end=None, length_cap=None)


# ── artifact writing (paths recorded in the DB later — runner knows no DB) ────

def test_write_artifacts_persists_all_four_and_round_trips(tmp_path):
    prov = build_provenance("M" * 3, dtype="int8", chunk_size=64, source=SLICED_ECD,
                            ecd_start=1, ecd_end=3, length_cap=None)
    prov.mean_plddt = 74.7
    result = FoldResult(pdb="ATOM  ...\nEND\n", plddt=[70.0, 75.0, 80.0],
                        pae=[[0.0, 1.0], [1.0, 0.0]], provenance=prov)
    written = write_artifacts(result, tmp_path)

    assert set(written) == {"pdb", "plddt", "pae", "provenance"}
    assert (tmp_path / "structure.pdb").read_text().startswith("ATOM")
    import json
    assert json.loads((tmp_path / "plddt.json").read_text()) == [70.0, 75.0, 80.0]
    back = json.loads((tmp_path / "provenance.json").read_text())
    assert back["source"] == SLICED_ECD and back["truncated"] is False and back["mean_plddt"] == 74.7


def test_write_artifacts_omits_pae_when_absent(tmp_path):
    result = FoldResult(pdb="END\n", plddt=[50.0], pae=None,
                        provenance=build_provenance("M", dtype="int8", chunk_size=64,
                                                     source=WHOLE, ecd_start=None,
                                                     ecd_end=None, length_cap=None))
    written = write_artifacts(result, tmp_path)
    assert "pae" not in written and not (tmp_path / "pae.json").exists()


# ── the GPU fold — boundary marker, skips without torch+CUDA (validated by owner) ──

@pytest.fixture
def gpu():
    torch = pytest.importorskip("torch", reason="fold is GPU-bound; validated on a GPU host (D-018)")
    if not torch.cuda.is_available():
        pytest.skip("no CUDA device; the ESMFold fold runs only on a GPU host")
    return torch


@pytest.mark.gpu
def test_fold_produces_structure_and_provenance(gpu):
    # Runs only on a GPU host. The int8 recipe is already measured (S-003); this is the
    # boundary marker so a GPU host CAN exercise the whole path end-to-end.
    result = runner.fold("MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVP" * 2,
                         dtype="int8", chunk_size=64, source=SLICED_ECD, ecd_start=1, ecd_end=114)
    assert result.pdb.count(" CA ") == result.provenance.ca_atom_count
    assert 0.0 <= (result.provenance.mean_plddt or 0) <= 100.0
    assert result.provenance.truncated is False
