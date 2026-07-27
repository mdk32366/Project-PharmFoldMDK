"""D-053 — the cancer-associations supplier: cited, validated, grouped, cohort-joined.

Fixtures use distinctive values; the last test pins the REAL committed file so a careless edit to
`data/cancer_associations.csv` reddens the gate (337 pairs / 82 targets / zero unmatched).
"""

from __future__ import annotations

import pytest

from core.cancer_associations import (
    ASSOCIATIONS,
    COHORT_MAPPING,
    AssociationError,
    load_associations,
)

CITE = "Kathad-2024-S3"  # comma-free so the fixture CSV needs no quoting


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def _cohort(tmp_path, symbols):
    body = "symbol,accession\n" + "\n".join(f"{s},ACC{i}" for i, s in enumerate(symbols)) + "\n"
    return _write(tmp_path, "cohort.csv", body)


def _assoc(tmp_path, body):
    return _write(tmp_path, "assoc.csv", "symbol,cancer,qh_score,source_citation\n" + body)


def test_uncited_row_is_rejected(tmp_path):
    a = _assoc(tmp_path, f"AAA,Lung,200,{CITE}\nBBB,Colon,180,\n")  # BBB uncited
    with pytest.raises(AssociationError, match="source_citation"):
        load_associations(a, _cohort(tmp_path, ["AAA", "BBB"]))


def test_non_numeric_qh_score_rejected(tmp_path):
    a = _assoc(tmp_path, f"AAA,Lung,high,{CITE}\n")
    with pytest.raises(AssociationError, match="qh_score"):
        load_associations(a, _cohort(tmp_path, ["AAA"]))


def test_out_of_range_qh_score_rejected(tmp_path):
    a = _assoc(tmp_path, f"AAA,Lung,500,{CITE}\n")  # >300
    with pytest.raises(AssociationError, match="range"):
        load_associations(a, _cohort(tmp_path, ["AAA"]))


def test_groups_sorted_by_qh_score_descending(tmp_path):
    # out-of-order input, distinctive scores -> must come back highest-first (a data contract)
    a = _assoc(tmp_path, f"AAA,Low,120,{CITE}\nAAA,High,290,{CITE}\nAAA,Mid,200,{CITE}\n")
    out = load_associations(a, _cohort(tmp_path, ["AAA"]))
    assert [x["qh_score"] for x in out["associations"]["AAA"]] == [290, 200, 120]


def test_unmatched_symbol_is_flagged_not_dropped(tmp_path):
    a = _assoc(tmp_path, f"AAA,Lung,200,{CITE}\nZZZ,Colon,180,{CITE}\n")
    out = load_associations(a, _cohort(tmp_path, ["AAA"]))  # ZZZ is not in the cohort
    assert out["unmatched_symbols"] == ["ZZZ"]
    assert "ZZZ" in out["associations"]      # flagged AND still present — never silently dropped
    assert out["pair_count"] == 2


def test_pair_count_is_rows_loaded_not_a_constant(tmp_path):
    body = "".join(f"S{i},C{i},{100 + i},{CITE}\n" for i in range(5))
    out = load_associations(_assoc(tmp_path, body), _cohort(tmp_path, [f"S{i}" for i in range(5)]))
    assert out["pair_count"] == 5
    assert out["targets_covered"] == 5


def test_real_file_loads_clean():
    """The pin: the committed derivation reproduces (D-053) — 337 pairs, all 82 targets, none
    unmatched. Reddens if the CSV is edited carelessly."""
    out = load_associations(ASSOCIATIONS, COHORT_MAPPING)
    assert out["pair_count"] == 337
    assert out["targets_covered"] == 82
    assert out["cohort_size"] == 82
    assert out["unmatched_symbols"] == []
