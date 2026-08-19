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


# ── the marker fits its column ──────────────────────────────────────────────

def test_every_marker_field_the_INGEST_WRITES_fits_its_declared_width(engine, monkeypatch):
    """⚠⚠ THIS FAILED IN PRODUCTION AND THE DATABASE CAUGHT IT, NOT A TEST.

    `ingest_markers.source_sha256` is `String(64)` — sized for ONE digest. The first version joined
    the two source hashes with `+`, produced 129 characters, and died on
    `StringDataRightTruncation` at the LAST statement of the transaction. ⚠ 247,552 rows and a
    passing `D-100` bar were discarded because a marker would not fit.

    ⚠⚠ AND THE FIRST VERSION OF THIS TEST DID NOT CATCH IT EITHER. It recomputed the digest with
    its own `hashlib.sha256(...)` and asserted THAT was 64 chars — so flipping the script back to
    the broken concatenation left it green. **A test that reimplements the thing it checks is
    checking itself.** This one runs the real `ingest()` and reads what actually landed.

    ⚠ SQLite does not enforce `VARCHAR` length and Postgres does, which is why production found
    this and the local suite did not. So the widths are asserted HERE, in Python, against the
    values the code really wrote.
    """
    widths = {"ingest_name": 80, "source_path": 400, "source_sha256": 64, "code_revision": 64}
    rows = [{"Gene": "ENSG1", "Gene name": "AAA", "Cancer": "c", "High": "0", "Medium": "0",
             "Low": "0", "Not detected": "0"}]
    norm = [{"Gene": "ENSG1", "Gene name": "AAA", "Tissue": "t", "Cell type": "ct",
             "Level": "High", "Reliability": "Enhanced"}]
    monkeypatch.setattr(CE, "our_genes", lambda: {"AAA"})
    monkeypatch.setattr(CE, "read_source",
                        lambda p, s, m, k: rows if "pathology" in str(p) else norm)
    # ⚠ The D-100 grid bar is neutralised HERE and only here: this fixture has one synthetic gene,
    # so the grid is empty and the bar correctly refuses it. The subject of THIS test is the marker
    # width; the bar has its own test, and leaving it armed would make this test fail for a reason
    # that is not its claim.
    import core.clinical_ingest as ci
    monkeypatch.setattr(ci, "assert_grid_or_refuse", lambda a, b: type("V", (), {
        "rows": 0, "kept": 0, "excluded": 0, "ok": True})())
    CE.ingest(engine, dry_run=False, downloads=pathlib.Path("."))

    with Session(engine) as s:
        got = s.execute(text(
            "SELECT ingest_name, source_path, source_sha256, code_revision, detail"
            " FROM ingest_markers WHERE ingest_name = :n"), {"n": CE.INGEST_NAME}).first()
    assert got is not None, "the ingest wrote no marker"
    values = dict(zip(("ingest_name", "source_path", "source_sha256", "code_revision"), got[:4]))
    over = {k: (len(v or ""), widths[k]) for k, v in values.items() if len(v or "") > widths[k]}
    assert not over, f"the ingest wrote values exceeding their column width: {over}"


def test_the_individual_source_hashes_survive_in_detail():
    """⚠ A pair identity that cannot name its members would be worse than the bug it fixed. Both
    hashes must remain recoverable from the marker's free-text `detail` (a TEXT column)."""
    import ast

    src = (REPO / "scripts" / "clinical_ingest_edges.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "ingest")
    body = ast.unparse(fn)
    assert "sources:" in body, "detail no longer records the individual source hashes"


# ── the surface supplier: both cards, both edges ────────────────────────────

def _seed_edges(engine, gene="AAA"):
    with Session(engine) as s:
        s.add(ClinicalPathology(gene="ENSG1", gene_name=gene, cancer="ovarian cancer",
                                high=3, medium=7, low=1, not_detected=2))
        s.add(ClinicalPathology(gene="ENSG1", gene_name=gene, cancer="stomach cancer",
                                high=0, medium=0, low=0, not_detected=6))
        s.add(ClinicalNormalTissue(gene="ENSG1", gene_name=gene, tissue="bronchus",
                                   cell_type="respiratory epithelial cells", level="High",
                                   reliability="Enhanced"))
        s.add(ClinicalNormalTissue(gene="ENSG1", gene_name=gene, tissue="bronchus",
                                   cell_type="ciliated cells", level="Not detected",
                                   reliability="Enhanced"))
        s.commit()


def test_the_block_carries_both_edges_and_NO_burden_field(engine):
    """⚠ `D-093` decision 5: co-equal. A block with tumours and no normal tissues would be the
    flattering half, and ruling 1's burden slot must be present even though nothing fills it."""
    from app.clinical_read import clinical_block
    _seed_edges(engine)
    b = clinical_block(engine, "AAA")
    assert b["status"] == "ihc_present"
    assert [t["cancer"] for t in b["tumours"]][0] == "ovarian cancer"   # ordered by stained share
    assert b["tumours"][0]["patients_positive"] == 11
    assert b["tumours"][0]["patients_tested"] == 13
    assert [n["tissue"] for n in b["normal_tissues"]] == ["bronchus"]
    # ⚠⚠ AND THE BLOCK CARRIES NO BURDEN FIELD — D-093 decision 1 bars one on a protein payload.
    # The refusal renders from the COMPONENT (ruling 1 is a surface obligation, not a data one).
    assert not [k for k in b if "burden" in k.lower()], b.keys()


def test_an_uncovered_gene_is_a_category_not_an_empty_block(engine):
    """⚠⚠ 960 of 2,687 folded census genes are absent from HPA's IHC. *Nobody looked* and *looked
    and found nothing* are different facts, and the common case must not read as the rare one."""
    from app.clinical_read import clinical_block
    b = clinical_block(engine, "NOSUCHGENE")
    assert b["status"] == "ihc_gene_absent"
    assert b["layers"] == ("mapped_one_gene", "row_absent", "no_ihc_available")


def test_the_block_computes_no_ratio_between_the_edges(engine):
    """⚠ Ruling 4: the edges are not commensurable, and `tumour_normal_ratio()` raises by design.
    The payload must carry no key that divides one by the other."""
    from app.clinical_read import clinical_block
    _seed_edges(engine)
    b = clinical_block(engine, "AAA")
    bad = [k for k in b if "ratio" in k.lower() or "score" in k.lower()]
    assert not bad, f"the block carries a combined figure: {bad}"


def test_a_non_ordinal_level_never_becomes_the_highest(engine):
    """⚠⚠ `Ascending`, `Descending`, `N/A` and `Not representative` are OUTSIDE the ordinal scale.
    Ranking one against `High` is exactly what `IncomparableEdges` forbids."""
    from app.clinical_read import clinical_block
    with Session(engine) as s:
        s.add(ClinicalNormalTissue(gene="E", gene_name="BBB", tissue="liver",
                                   cell_type="hepatocytes", level="Ascending",
                                   reliability="Approved"))
        s.add(ClinicalNormalTissue(gene="E", gene_name="BBB", tissue="liver",
                                   cell_type="bile duct cells", level="Low",
                                   reliability="Approved"))
        s.commit()
    b = clinical_block(engine, "BBB")
    liver = [n for n in b["normal_tissues"] if n["tissue"] == "liver"]
    assert liver and liver[0]["highest"] == "Low", liver
