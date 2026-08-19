"""The clinical edge ingest, on the `GC` pattern — `D-093` amendment 2.

⚠⚠ THE TWO PROPERTIES THAT MATTER MOST, and both are asserted against behaviour rather than intent:
  1. **No prognostic column reaches a stored table.** Presence is the violation (`D-093` am 1
     clause 2) — HPA redistributes TCGA-derived prognostics under bespoke terms nobody here read.
  2. **The `D-100` reproduction crosses the write.** `reproduce_d100` compares rows read back OUT
     of the database against the published grid; comparing the file to itself proves nothing.
"""

from __future__ import annotations

import pathlib

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from db.models import Base, ClinicalNormalTissue, ClinicalPathology
from scripts import clinical_ingest_edges as CE

REPO = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    with eng.begin() as c:
        c.execute(text(
            "CREATE TABLE ingest_markers (id INTEGER PRIMARY KEY, ingest_name TEXT NOT NULL,"
            " source_path TEXT NOT NULL, source_sha256 TEXT NOT NULL, rows_written INTEGER NOT"
            " NULL, code_revision TEXT DEFAULT '', completed_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            " detail TEXT DEFAULT '', UNIQUE (ingest_name, source_path))"))
    return eng


# ── 1. the licence rule, made structural ────────────────────────────────────

def test_no_prognostic_column_exists_on_either_model():
    """⚠ The four `prognostic-*` columns of `pathology.tsv` must not be reachable at all. Asserted
    on the MODEL, so a future migration adding one reddens here as well as in the file scan."""
    for model in (ClinicalPathology, ClinicalNormalTissue):
        bad = [c.name for c in model.__table__.columns if "prognos" in c.name.lower()]
        assert not bad, f"{model.__tablename__} carries {bad}"


def test_the_kept_columns_are_seven_of_eleven_and_the_refused_four_are_named():
    """⚠⚠ The omission is a DECISION and must be legible as one. A reader who sees only seven
    columns cannot tell whether four were refused or never existed."""
    assert len(CE.PATHOLOGY_KEEP) == 7
    assert len(CE.PATHOLOGY_REFUSED) == 4
    for c in CE.PATHOLOGY_REFUSED:
        assert "prognos" in c.lower()
        assert c not in CE.PATHOLOGY_KEEP


def test_the_reader_asserts_the_filter_rather_than_trusting_it():
    """⚠ `read_source` carries an assertion that no kept column matches the token. Pinned by AST so
    a future edit that drops the check is visible — it is the last line of defence before a
    prognostic column reaches a row."""
    import ast

    src = (REPO / "scripts" / "clinical_ingest_edges.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "read_source")
    assert any(isinstance(n, ast.Assert) for n in ast.walk(fn)), (
        "read_source no longer asserts that the prognostic filter worked")


# ── 2. the source pin ───────────────────────────────────────────────────────

def test_an_absent_source_is_refused_with_its_own_message(tmp_path):
    from core.source_pin import IngestRefused
    with pytest.raises(IngestRefused, match="ABSENT"):
        CE.read_source(tmp_path / "nope.zip", "0" * 64, "x.tsv", ("Gene",))


def test_a_hash_mismatch_is_refused_and_names_both_hashes(tmp_path):
    import zipfile

    from core.source_pin import IngestRefused
    z = tmp_path / "f.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("x.tsv", "Gene\tA\nENSG1\t1\n")
    with pytest.raises(IngestRefused, match="does not match its pinned sha256"):
        CE.read_source(z, "f" * 64, "x.tsv", ("Gene",))


def test_both_sources_are_pinned_by_sha256():
    assert set(CE.SOURCES) == {"pathology.tsv.zip", "normal_tissue.tsv.zip"}
    for name, sha in CE.SOURCES.items():
        assert len(sha) == 64 and all(c in "0123456789abcdef" for c in sha), name


# ── 3. the edges ship together ──────────────────────────────────────────────

def test_one_transaction_covers_both_edges(engine, monkeypatch):
    """⚠⚠ `D-093` amendment 2 ruling 2 and decision 5's co-equality: a failure on edge 2 must roll
    edge 1 back. A tumour signal without its normal-tissue differential is the half that flatters
    a target, and shipping it alone would be a deviation from a ruling."""
    path_rows = [{"Gene": "ENSG1", "Gene name": "AAA", "Cancer": "breast cancer",
                  "High": "1", "Medium": "0", "Low": "0", "Not detected": "0"}]
    norm_rows = [{"Gene": "ENSG1", "Gene name": "AAA", "Tissue": "breast",
                  "Cell type": "glandular cells", "Level": "High", "Reliability": "Enhanced"}]
    monkeypatch.setattr(CE, "our_genes", lambda: {"AAA"})
    monkeypatch.setattr(CE, "read_source",
                        lambda p, s, m, k: path_rows if "pathology" in str(p) else norm_rows)
    # force the bar to fail after both writes
    monkeypatch.setattr(CE, "assert_grid_or_refuse", None, raising=False)
    import core.clinical_ingest as ci
    monkeypatch.setattr(ci, "assert_grid_or_refuse",
                        lambda a, b: (_ for _ in ()).throw(AssertionError("forced")))
    with pytest.raises(CE.BarFailed) as e:
        CE.ingest(engine, dry_run=False, downloads=pathlib.Path("."))
    assert "ROLLED BACK" in str(e.value)
    with Session(engine) as s:
        assert s.execute(select(func.count()).select_from(ClinicalPathology)).scalar_one() == 0
        assert s.execute(select(func.count()).select_from(ClinicalNormalTissue)).scalar_one() == 0


def test_an_unknown_level_is_refused_against_the_module_not_a_local_list(engine, monkeypatch):
    """⚠ A ninth `Level` is a measurement that changed, not a lookup miss. Validated against
    `core.clinical_layer.LEVEL_VALUES` so the vocabulary has exactly one home."""
    from core.source_pin import IngestRefused
    monkeypatch.setattr(CE, "our_genes", lambda: {"AAA"})
    monkeypatch.setattr(CE, "read_source", lambda p, s, m, k: (
        [{"Gene": "E", "Gene name": "AAA", "Cancer": "c", "High": "0", "Medium": "0",
          "Low": "0", "Not detected": "0"}] if "pathology" in str(p) else
        [{"Gene": "E", "Gene name": "AAA", "Tissue": "t", "Cell type": "c",
          "Level": "Extremely High", "Reliability": "Enhanced"}]))
    with pytest.raises(IngestRefused, match="does not handle"):
        CE.ingest(engine, dry_run=False, downloads=pathlib.Path("."))


def test_the_grain_prevents_a_duplicate_normal_tissue_row(engine):
    """⚠ (gene, tissue, cell type) is the grain that distinguishes `tested_not_detected` from
    `not_tested`. Tested with a RAW insert — through the ingest it would prove nothing."""
    from sqlalchemy.exc import IntegrityError
    with Session(engine) as s:
        s.add(ClinicalNormalTissue(gene="E", gene_name="AAA", tissue="t", cell_type="c",
                                   level="High", reliability="Enhanced"))
        s.commit()
    with Session(engine) as s:
        s.add(ClinicalNormalTissue(gene="E", gene_name="AAA", tissue="t", cell_type="c",
                                   level="Low", reliability="Enhanced"))
        with pytest.raises(IntegrityError):
            s.commit()
