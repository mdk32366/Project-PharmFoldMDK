"""D-144 — the census STRUCTURAL rank: the formula, the load, the route, and the wall.

Four things are under test and the fourth is the one that matters most:

1. **The formula**, at its edges: non-surface, no fold, a fold with no pLDDT, the ECD cap at
   200 aa, a missing span, the reference sink, and the unit-swap refusal.
2. **The load path**: compute from a population file joined to `protein_analyses`, persist, and
   **replace idempotently** — after any number of loads there is exactly one VALID run.
3. **The route**: `GET /api/census-structural-ranking` serves the latest VALID run with its
   disclaimer and `n_candidates`, and `not_run` (200, empty) when none exists.
4. **⚠⚠ THE SEPARATION FROM THE COHORT-82 LEARNED SCORER.** `/api/ranking` and its three tables
   are the pre-registered `D-041` / `D-060` result. Nothing here may touch them, and "nothing
   touches them" is asserted — by import list, by AST, by the migration's operations, and by
   serving both routes off one app and checking the ranking payload is byte-identical to what it
   was before this population existed.
"""

from __future__ import annotations

import ast
import csv
import os
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from app.main import create_app  # noqa: E402
from core import census_structural as cs  # noqa: E402
from db.models import (  # noqa: E402
    Base,
    CensusStructuralRun,
    CensusStructuralScore,
    ProteinAnalysis,
    RankingResult,
    RankingRun,
    TargetScore,
)
from scripts import census_structural_rank as loader  # noqa: E402

LOG = (REPO / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (REPO / "ARCHITECTURE.md").read_text(encoding="utf-8")
CORE_SRC = (REPO / "core" / "census_structural.py").read_text(encoding="utf-8")
LOADER_SRC = (REPO / "scripts" / "census_structural_rank.py").read_text(encoding="utf-8")
READ_SRC = (REPO / "app" / "census_structural_read.py").read_text(encoding="utf-8")
MIGRATION = REPO / "db" / "migrations" / "versions" / "0012_census_structural_rank.py"

#: The three tables the LEARNED cohort-82 scorer owns. ⚠ Named once, here, and every
#: separation test reads this tuple — a per-test list would let one of them fall behind.
SCORER_TABLES = ("ranking_runs", "target_scores", "ranking_results")

TOKEN = "test-token"


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover - a read must never touch it
        raise AssertionError("a read route touched the queue")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _client(engine, tmp_path) -> TestClient:
    app = create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN,
                     queue=_DummyQueue())
    return TestClient(app, raise_server_exceptions=True)


# ─────────────────────────────── 1. the formula ───────────────────────────────


def test_surface_earns_the_full_membrane_factor_and_everything_else_earns_02():
    assert cs.score_membrane("surface") == 1.0
    for other in ("non_surface", "unclassified", "class_conflict", "", None, "SURFACES"):
        assert cs.score_membrane(other) == 0.2, other
    # ⚠ case and whitespace are the same claim, not a different one
    assert cs.score_membrane("  Surface ") == 1.0


def test_the_ecd_factor_saturates_at_200_and_is_a_cap_not_a_threshold():
    assert cs.score_ecd(200) == 1.0
    assert cs.score_ecd(442) == 1.0                       # GABBR2's span: capped, not rewarded
    assert cs.score_ecd(199) == pytest.approx(0.995)       # ⚠ NOT 0 — a cap, not a cutoff
    assert cs.score_ecd(100) == pytest.approx(0.5)
    assert cs.score_ecd(1) == pytest.approx(0.005)


def test_a_missing_or_zero_span_scores_zero_and_is_never_imputed():
    for absent in (None, 0, "", "  ", "n/a", -12, 12.5, True, False):
        assert cs.score_ecd(absent) == 0.0, absent
    # a JSON `meta` may hold the measurement as a string or a whole float — both are the span
    assert cs.score_ecd("442") == 1.0
    assert cs.score_ecd(442.0) == 1.0


def test_score_model_has_three_cases_and_no_fold_is_a_penalty_not_a_neutral():
    assert cs.score_model(True, 84.43) == pytest.approx(0.8443)
    assert cs.score_model(True, None) == 0.8               # F-042: a fold whose pLDDT was lost
    assert cs.score_model(False, None) == 0.3              # no fold at all
    # ⚠⚠ the no-fold penalty is NOT the mid-point of anything, and it is not 0.5
    assert cs.score_model(False, None) != 0.5
    # ⚠ a pLDDT on a row with no structure cannot rescue it: the fold is what is absent
    assert cs.score_model(False, 99.0) == 0.3


def test_a_zero_to_one_plddt_is_refused_rather_than_divided_again():
    """⚠⚠ THE UNIT SWAP. 0.84 on a 0–100 field would score 0.0084 and rank an excellent fold
    last — a wrong-but-plausible number (F-047), which is worse than an error."""
    for bad in (0.84, 1.0, 0.001):
        with pytest.raises(cs.ImplausiblePlddt):
            cs.score_model(True, bad)
    for out_of_range in (-1.0, 100.1, 1000):
        with pytest.raises(cs.ImplausiblePlddt):
            cs.score_model(True, out_of_range)
    # ⚠ a persisted 0.0 is a MEASUREMENT this module has no licence to reinterpret
    assert cs.score_model(True, 0.0) == 0.0
    with pytest.raises(cs.ImplausiblePlddt):
        cs.score_model(True, "84.43")                      # a string is not a number


def test_the_golden_row_reproduces_the_offline_value_for_gabbr2():
    """⚠ The offline `structural_census_ranked_all.csv` puts GABBR2 (`O75899`) at ≈0.8443.

    ⚠⚠ PROVENANCE, STATED PRECISELY (D-016). Two of the three inputs are read from a
    COMMITTED file and one is not:
      * `census_class = surface` and `span_aa = 442` are row 1286 of
        `data/census/census_manifest.v7.csv` — checked below, from the file, not typed here.
      * `mean_plddt = 84.43` is **not on disk in this repository**: O75899 is tranche 5, and
        `census_features.v1.jsonl` (2,690 rows) holds no tranche-5 fold and no `mean_plddt`
        field at all. It comes from the GO's own quoted figure.
    So this test proves *the formula reproduces the offline number given that pLDDT*; it does
    **not** independently verify the pLDDT. A test that claimed both would be claiming a
    measurement this build cannot make.
    """
    row = next(r for r in cs.census_population() if r["accession"] == "O75899")
    assert row["census_class"] == "surface" and row["span_aa"] == 442

    scored = cs.structural_score(row["census_class"], row["span_aa"],
                                 has_pdb=True, mean_plddt=84.43)
    assert scored.score_membrane == 1.0
    assert scored.score_ecd == 1.0                         # 442 aa saturates the cap
    assert scored.score_model == pytest.approx(0.8443)
    assert scored.structural_score == pytest.approx(0.8443, abs=1e-9)
    assert cs.FLAG_ECD_SATURATED in scored.flags


def test_every_flag_is_a_stated_category_with_a_meaning():
    """⚠ D-079 amendment 1 ruling 2's rule applied to flags: a category, never an absence a
    reader has to infer from a missing field."""
    declared = {v for k, v in vars(cs).items() if k.startswith("FLAG_") and isinstance(v, str)}
    assert declared == set(cs.FLAG_MEANING), "every flag must carry its meaning, and vice versa"
    no_fold = cs.structural_score("surface", 300, has_pdb=False)
    assert cs.FLAG_NO_FOLD in no_fold.flags and no_fold.has_fold is False
    lost_plddt = cs.structural_score("surface", 300, has_pdb=True, mean_plddt=None)
    assert cs.FLAG_FOLD_WITHOUT_PLDDT in lost_plddt.flags
    no_span = cs.structural_score("surface", None, has_pdb=True, mean_plddt=90.0)
    assert cs.FLAG_SPAN_UNRECORDED in no_span.flags and no_span.structural_score == 0.0
    annex = cs.structural_score("non_surface", 300, has_pdb=True, mean_plddt=90.0)
    assert cs.FLAG_NON_SURFACE in annex.flags


def test_the_reference_flag_never_enters_the_score():
    """⚠⚠ A yardstick must stay comparable to what it is a yardstick for."""
    plain = cs.structural_score("surface", 318, has_pdb=True, mean_plddt=90.0)
    flagged = cs.structural_score("surface", 318, has_pdb=True, mean_plddt=90.0,
                                  is_reference=True)
    assert flagged.structural_score == plain.structural_score
    assert flagged.score_membrane == plain.score_membrane
    assert flagged.score_ecd == plain.score_ecd
    assert flagged.score_model == plain.score_model
    assert cs.FLAG_REFERENCE in flagged.flags and cs.FLAG_REFERENCE not in plain.flags


def test_the_scored_product_is_exactly_the_three_factors_and_nothing_else():
    """⚠⚠ THE GUARD ABOVE DID NOT BITE, AND THIS IS WHY THIS ONE EXISTS (A-016's class).

    Wiring `is_reference` into the score as `× (1.0 if is_reference else 1.0)` — a no-op — left
    the whole suite green: comparing two products cannot see an arithmetic path that changes
    nothing *today*, and the next edit to that expression is the one that matters. So the check
    is the **expression itself**, read off the AST: the value assigned to `structural_score` must
    be exactly `membrane * ecd * model`. Any fourth term reddens, whether or not it is a no-op.
    """
    fn = next(n for n in ast.walk(ast.parse(CORE_SRC))
              if isinstance(n, ast.FunctionDef) and n.name == "structural_score")
    calls = [n for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "StructuralScore"]
    assert len(calls) == 1, "one construction site, so there is one expression to check"
    product = next(kw.value for kw in calls[0].keywords if kw.arg == "structural_score")
    assert ast.unparse(product) == "membrane * ecd * model", ast.unparse(product)
    # ⚠ and `is_reference` reaches the flag list and nothing else: its only use inside the
    # function body is the `if` that appends the flag.
    uses = [n for n in ast.walk(fn)
            if isinstance(n, ast.Name) and n.id == "is_reference"]
    assert len(uses) == 1, (
        f"`is_reference` is read {len(uses)} times in structural_score; it may be read exactly "
        f"once, by the branch that appends the flag")


def test_references_sink_below_every_candidate_however_high_they_score():
    rows = [
        {"accession": "REF-TOP", "structural_score": 0.99, "is_reference": True},
        {"accession": "CAND-LOW", "structural_score": 0.01, "is_reference": False},
        {"accession": "CAND-TOP", "structural_score": 0.98, "is_reference": False},
        {"accession": "REF-LOW", "structural_score": 0.02, "is_reference": True},
    ]
    ordered = cs.rank_rows(rows)
    assert [r["accession"] for r in ordered] == ["CAND-TOP", "CAND-LOW", "REF-TOP", "REF-LOW"]
    # ⚠ rank is assigned AFTER the sink, so the top candidate is rank 1
    assert ordered[0]["rank"] == 1 and ordered[-1]["rank"] == 4


def test_ties_are_broken_by_accession_so_two_runs_agree():
    """⚠ 1,998 of 3,467 manifest spans are under 200 aa, so products collide in the thousands.
    Without a total order the idempotent replace would look like a change every time."""
    rows = [{"accession": a, "structural_score": 0.3, "is_reference": False}
            for a in ("Q9ZZZ9", "A0AAA1", "P12345")]
    assert [r["accession"] for r in cs.rank_rows(rows)] == ["A0AAA1", "P12345", "Q9ZZZ9"]
    assert [r["accession"] for r in cs.rank_rows(list(reversed(rows)))] == \
           ["A0AAA1", "P12345", "Q9ZZZ9"]


def test_no_half_neutral_is_a_numeric_constant_anywhere_in_the_formula_or_the_loader():
    """⚠⚠ THE CHECK IS THE AST, NOT THE SOURCE TEXT. Both files *discuss* the 0.5 neutrals the
    offline draft carried, so a grep for `0.5` is satisfied by the paragraph explaining why they
    are gone — F-044's shape, *a reference that resolves, to the wrong thing*."""
    for src, label in ((CORE_SRC, "core/census_structural.py"),
                       (LOADER_SRC, "scripts/census_structural_rank.py"),
                       (READ_SRC, "app/census_structural_read.py")):
        numbers = [n.value for n in ast.walk(ast.parse(src))
                   if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                   and not isinstance(n.value, bool)]
        assert 0.5 not in numbers, f"{label} carries a 0.5 numeric constant"


def test_the_four_excluded_factors_are_named_with_reasons_and_are_not_computed():
    names = [name for name, _why in cs.EXCLUDED_FACTORS]
    assert names == ["cancer", "normal_risk", "internalization", "density"]
    for name, why in cs.EXCLUDED_FACTORS:
        assert why.strip(), name
    # ⚠ and none of them is a component: the product has exactly THREE factors, so a
    # reintroduced factor cannot hide as an extra field on the result
    import dataclasses
    fields = [f.name for f in dataclasses.fields(cs.StructuralScore)]
    assert fields == ["score_membrane", "score_ecd", "score_model", "structural_score",
                      "has_fold", "flags"]
    for factor, _why in cs.EXCLUDED_FACTORS:
        assert f"score_{factor}" not in fields


def test_the_disclaimer_says_all_three_things_the_go_requires():
    assert cs.STRUCTURAL_ONLY == "STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready"
    lowered = cs.DISCLAIMER.lower()
    for claim in ("structural_only", "not hpa-weighted", "not adc-ready", "/api/ranking"):
        assert claim in lowered, claim


def test_the_formula_version_is_derived_from_the_source_not_typed():
    assert re.fullmatch(r"[0-9a-f]{12}", cs.formula_version())
    assert "formula_version" not in {"v1", "1.0"}
    # a hand-typed version string would not change when the formula changes; the pin is a hash
    import hashlib
    assert cs.formula_version() == hashlib.sha256(
        (REPO / "core" / "census_structural.py").read_bytes()).hexdigest()[:12]


def test_the_reference_sink_is_joined_from_the_curated_file_and_never_typed_here():
    """⚠⚠ A second copy of a curation is the D-062 shape. The accessions must appear NOWHERE in
    this module's source — the join is the definition."""
    refs = cs.reference_accessions()
    assert "Q96NY8" in refs, "NECTIN4 must be in the reference sink"
    assert len(refs) == 12, refs
    for acc in refs:
        assert acc not in CORE_SRC or acc == "Q96NY8", (
            f"{acc} is typed into core/census_structural.py; the sink is a JOIN")
    # ⚠ Q96NY8 appears only in PROSE (the docstring's named example), never in a data structure
    typed = [n.value for n in ast.walk(ast.parse(CORE_SRC))
             if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and re.fullmatch(r"[A-NR-Z0-9]{6,10}", n.value)]
    assert [t for t in typed if t in refs] == [], typed


def test_every_reference_antigen_is_actually_in_the_population():
    """⚠ Measured, not assumed: a sink that named accessions outside the census would sink
    nothing and nobody would see it fail."""
    population = {r["accession"] for r in cs.census_population()}
    missing = sorted(cs.reference_accessions() - population)
    assert missing == [], f"reference antigens absent from the census manifest: {missing}"


def test_the_population_is_the_manifest_and_carries_class_span_and_tranche():
    rows = cs.census_population()
    assert len(rows) == 3467, len(rows)
    assert all(r["accession"] for r in rows)
    assert {r["census_class"] for r in rows} == {"surface", "non_surface"}
    assert {r["tranche"] for r in rows} == {1, 2, 3, 4, 5}
    # ⚠ every manifest row carries a measured span — that is what makes it manifest-eligible
    assert all(isinstance(r["span_aa"], int) and r["span_aa"] > 0 for r in rows)


# ─────────────────────────── 2. the load path ─────────────────────────────────


def _fixture_manifest(tmp_path: Path) -> Path:
    """Six proteins, chosen so every branch of the formula is exercised by a row that is
    actually loaded — and `Q96NY8` so the reference sink is exercised end to end."""
    path = tmp_path / "manifest.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["census_accession", "census_class", "span_aa",
                                           "tranche"])
        w.writeheader()
        w.writerows([
            {"census_accession": "P00001", "census_class": "surface",
             "span_aa": "400", "tranche": "4"},        # folded, high pLDDT -> top
            {"census_accession": "P00002", "census_class": "surface",
             "span_aa": "100", "tranche": "2"},        # folded, half the ECD factor
            {"census_accession": "P00003", "census_class": "non_surface",
             "span_aa": "400", "tranche": "4"},        # annex class
            {"census_accession": "P00004", "census_class": "surface",
             "span_aa": "400", "tranche": "5"},        # never folded -> 0.3
            {"census_accession": "P00005", "census_class": "surface",
             "span_aa": "400", "tranche": "3"},        # folded, pLDDT not persisted -> 0.8
            {"census_accession": "Q96NY8", "census_class": "surface",
             "span_aa": "318", "tranche": "4"},        # NECTIN4 — the reference sink
        ])
    return path


def _seed_census_folds(engine) -> None:
    """Census rows in `protein_analyses` — tranche > 0, joined by `input_value`."""
    with Session(engine) as s:
        s.add_all([
            ProteinAnalysis(input_type="uniprot", input_value="P00001", cohort_tranche=4,
                            pdb_path="/a/P00001.pdb", mean_plddt=90.0, meta={}),
            ProteinAnalysis(input_type="uniprot", input_value="P00002", cohort_tranche=2,
                            pdb_path="/a/P00002.pdb", mean_plddt=80.0, meta={}),
            ProteinAnalysis(input_type="uniprot", input_value="P00003", cohort_tranche=4,
                            pdb_path="/a/P00003.pdb", mean_plddt=90.0, meta={}),
            # P00004 has NO analysis row at all — never folded
            ProteinAnalysis(input_type="uniprot", input_value="P00005", cohort_tranche=3,
                            pdb_path="/a/P00005.pdb", mean_plddt=None, meta={}),
            ProteinAnalysis(input_type="uniprot", input_value="Q96NY8", cohort_tranche=4,
                            pdb_path="/a/Q96NY8.pdb", mean_plddt=95.0, meta={}),
            # ⚠ A COHORT row for one of the same accessions. It must NOT supply the fold: the
            # two populations are measured under different span definitions (D-081).
            ProteinAnalysis(input_type="uniprot", input_value="P00004", cohort_tranche=0,
                            pdb_path="/a/cohort.pdb", mean_plddt=99.0, meta={}),
        ])
        s.commit()


def test_the_load_computes_from_the_db_join_and_ranks_the_whole_population(engine, tmp_path):
    _seed_census_folds(engine)
    rows = loader.compute_rows(loader.fold_facts(engine),
                               manifest=_fixture_manifest(tmp_path))
    by_acc = {r["accession"]: r for r in rows}
    assert len(rows) == 6, "every population row is ranked, folded or not"

    assert by_acc["P00001"]["structural_score"] == pytest.approx(0.9)     # 1.0 × 1.0 × 0.90
    assert by_acc["P00002"]["structural_score"] == pytest.approx(0.4)     # 1.0 × 0.5 × 0.80
    assert by_acc["P00003"]["structural_score"] == pytest.approx(0.18)    # 0.2 × 1.0 × 0.90
    assert by_acc["P00004"]["structural_score"] == pytest.approx(0.3)     # 1.0 × 1.0 × 0.30
    assert by_acc["P00005"]["structural_score"] == pytest.approx(0.8)     # 1.0 × 1.0 × 0.80

    # ⚠⚠ THE COHORT ROW DID NOT SUPPLY A FOLD. P00004's only structure is a tranche-0 row.
    assert by_acc["P00004"]["has_fold"] is False
    assert by_acc["P00004"]["analysis_id"] is None
    assert cs.FLAG_NO_FOLD in by_acc["P00004"]["flags"]

    # ⚠⚠ THE REFERENCE SINKS DESPITE HOLDING THE HIGHEST SCORE IN THE POPULATION. NECTIN4's
    # 318 aa span saturates the cap and its fold is the most confident here, so 1.0 × 1.0 × 0.95
    # would put it at rank 1 on score alone — and an approved ADC target at the top of a list
    # read as "next targets" is the whole reason the sink exists.
    assert by_acc["Q96NY8"]["structural_score"] == pytest.approx(0.95)
    assert by_acc["Q96NY8"]["structural_score"] > by_acc["P00001"]["structural_score"]
    assert by_acc["Q96NY8"]["is_reference"] is True
    assert cs.FLAG_REFERENCE in by_acc["Q96NY8"]["flags"]
    assert by_acc["Q96NY8"]["rank"] == 6
    assert [r["accession"] for r in rows][:5] == ["P00001", "P00005", "P00002", "P00004",
                                                  "P00003"]


def test_a_fold_with_no_persisted_plddt_is_08_and_not_pooled_with_no_fold(engine, tmp_path):
    _seed_census_folds(engine)
    rows = {r["accession"]: r for r in
            loader.compute_rows(loader.fold_facts(engine),
                                manifest=_fixture_manifest(tmp_path))}
    assert rows["P00005"]["has_fold"] is True                 # a structure IS held
    assert rows["P00005"]["mean_plddt"] is None               # its confidence is not
    assert rows["P00005"]["score_model"] == 0.8
    assert rows["P00004"]["score_model"] == 0.3
    assert rows["P00005"]["score_model"] != rows["P00004"]["score_model"], (
        "a fold we hold and a fold we never made must not score the same")


def test_the_summary_separates_candidates_from_references_and_carries_breakdowns(engine,
                                                                                 tmp_path):
    _seed_census_folds(engine)
    rows = loader.compute_rows(loader.fold_facts(engine),
                               manifest=_fixture_manifest(tmp_path))
    counts = loader.summarise(rows)
    assert counts["n_population"] == 6
    assert counts["n_candidates"] == 5 and counts["n_reference"] == 1
    assert counts["n_with_fold"] == 5 and counts["n_without_fold"] == 1
    assert counts["n_with_fold"] + counts["n_without_fold"] == counts["n_population"], (
        "the fold split must partition the population exactly — a third state would be a row "
        "neither counted as folded nor as unfolded")
    assert counts["by_census_class"] == {"surface": 5, "non_surface": 1}
    assert counts["by_tranche"] == {"2": 1, "3": 1, "4": 3, "5": 1}
    assert counts["reference_accessions"] == ["Q96NY8"]
    assert counts["by_flag"][cs.FLAG_NO_FOLD] == 1


def test_an_unreadable_plddt_refuses_the_run_instead_of_scoring_it_as_unfolded(engine,
                                                                               tmp_path):
    """⚠⚠ F-020's shape refused: a 0–1 pLDDT scored as `no fold` would become a 0.3 that looks
    like a measurement. The loader names the accession and stops."""
    with Session(engine) as s:
        s.add(ProteinAnalysis(input_type="uniprot", input_value="P00001", cohort_tranche=4,
                              pdb_path="/a/P00001.pdb", mean_plddt=0.9, meta={}))
        s.commit()
    with pytest.raises(SystemExit) as exc:
        loader.compute_rows(loader.fold_facts(engine), manifest=_fixture_manifest(tmp_path))
    assert "P00001" in str(exc.value)


def test_persisting_twice_leaves_exactly_one_valid_run_and_the_same_ranks(engine, tmp_path):
    """⚠⚠ THE IDEMPOTENT REPLACE. F-021: a loader's pure INSERT took `protein_features` from 80
    rows to 160 across two generations and nothing was red."""
    _seed_census_folds(engine)
    manifest = _fixture_manifest(tmp_path)
    rows = loader.compute_rows(loader.fold_facts(engine), manifest=manifest)

    first = loader.persist(engine, rows, manifest=manifest)
    second = loader.persist(engine, loader.compute_rows(loader.fold_facts(engine),
                                                        manifest=manifest), manifest=manifest)
    assert second != first

    with Session(engine) as s:
        valid = s.scalars(select(CensusStructuralRun)
                          .where(CensusStructuralRun.run_status == loader.RUN_VALID)).all()
        assert [r.id for r in valid] == [second], "exactly one VALID run after two loads"
        superseded = s.scalars(select(CensusStructuralRun)
                               .where(CensusStructuralRun.run_status
                                      == loader.RUN_SUPERSEDED)).all()
        # ⚠ the replaced run is KEPT and NAMES its replacement
        assert [r.id for r in superseded] == [first]
        assert f"id={second}" in superseded[0].status_detail
        # one row per protein per run, both times — the UNIQUE constraint's property, measured
        assert s.query(CensusStructuralScore).count() == 12
        ranks = {r.accession: r.rank for r in s.scalars(
            select(CensusStructuralScore)
            .where(CensusStructuralScore.run_id == second)).all()}
        assert ranks == {r["accession"]: r["rank"] for r in rows}


def test_the_run_row_records_its_population_by_path_and_hash(engine, tmp_path):
    _seed_census_folds(engine)
    manifest = _fixture_manifest(tmp_path)
    run_id = loader.persist(engine, loader.compute_rows(loader.fold_facts(engine),
                                                        manifest=manifest), manifest=manifest)
    with Session(engine) as s:
        run = s.get(CensusStructuralRun, run_id)
    assert run.formula_version == cs.formula_version()
    assert run.span_definition == "v2-ruled-vocabulary-2026-08-07"
    assert run.population_source.endswith("manifest.csv")
    assert re.fullmatch(r"[0-9a-f]{64}", run.population_sha256)
    assert run.status_detail == cs.DISCLAIMER
    assert run.component_counts["n_candidates"] == 5


def test_pruning_is_explicit_and_a_load_never_deletes_a_superseded_run(engine, tmp_path):
    _seed_census_folds(engine)
    manifest = _fixture_manifest(tmp_path)
    rows = loader.compute_rows(loader.fold_facts(engine), manifest=manifest)
    loader.persist(engine, rows, manifest=manifest)
    loader.persist(engine, rows, manifest=manifest)
    with Session(engine) as s:
        assert s.query(CensusStructuralRun).count() == 2      # ⚠ the load kept both

    runs, scores = loader.prune_superseded(engine)
    assert (runs, scores) == (1, 6)
    with Session(engine) as s:
        assert s.query(CensusStructuralRun).count() == 1
        assert s.query(CensusStructuralScore).count() == 6
    assert loader.prune_superseded(engine) == (0, 0)          # idempotent


def test_a_tiles_only_representative_is_not_counted_as_a_fold(engine, tmp_path):
    """⚠ `STRUCTURE_KINDS_WITH_A_FOLD` is the census surface's own definition (D-118). A looser
    one here would give `plddt/100` to a protein /api/census reports as not folded."""
    with Session(engine) as s:
        parent = ProteinAnalysis(input_type="uniprot", input_value="P00001", cohort_tranche=4,
                                 pdb_path=None, mean_plddt=None,
                                 meta={"hold48_kind": "parent"})
        s.add(parent)
        s.flush()
        s.add(ProteinAnalysis(input_type="uniprot", input_value="P00001", cohort_tranche=4,
                              pdb_path="/a/tile.pdb", mean_plddt=88.0,
                              meta={"hold48_kind": "tile", "parent_job_id": parent.id,
                                    "tile_start": 1}))
        s.commit()
    facts = loader.fold_facts(engine)
    assert facts["P00001"]["structure_kind"] == "tiles_only"
    assert facts["P00001"]["has_fold"] is False
    rows = {r["accession"]: r
            for r in loader.compute_rows(facts, manifest=_fixture_manifest(tmp_path))}
    assert rows["P00001"]["score_model"] == 0.3


# ──────────────────────────────── 3. the route ────────────────────────────────


def _load_run(engine, tmp_path) -> int:
    _seed_census_folds(engine)
    manifest = _fixture_manifest(tmp_path)
    return loader.persist(engine, loader.compute_rows(loader.fold_facts(engine),
                                                      manifest=manifest), manifest=manifest)


def test_the_route_is_open_and_serves_the_latest_valid_run(engine, tmp_path):
    run_id = _load_run(engine, tmp_path)
    r = _client(engine, tmp_path).get("/api/census-structural-ranking")   # no auth (D-034)
    assert r.status_code == 200
    body = r.json()
    assert body["result_status"] == "valid"
    assert body["run"]["id"] == run_id
    assert [row["rank"] for row in body["rows"]] == [1, 2, 3, 4, 5, 6]
    assert body["rows"][0]["accession"] == "P00001"


def test_the_payload_carries_the_disclaimer_and_n_candidates(engine, tmp_path):
    _load_run(engine, tmp_path)
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert body["structural_only"] == cs.STRUCTURAL_ONLY
    assert "STRUCTURAL_ONLY" in body["disclaimer"]
    assert "not HPA-weighted" in body["disclaimer"]
    assert "not ADC-ready" in body["disclaimer"]
    assert body["n_candidates"] == 5 and body["run"]["n_candidates"] == 5
    assert body["run"]["n_reference"] == 1
    # ⚠⚠ ON EVERY ROW, so a row lifted into a slide takes the sentence with it
    assert all(row["disclaimer"] == cs.STRUCTURAL_ONLY for row in body["rows"])


def test_every_served_row_carries_its_three_factors(engine, tmp_path):
    _load_run(engine, tmp_path)
    rows = _client(engine, tmp_path).get("/api/census-structural-ranking").json()["rows"]
    for row in rows:
        for key in ("score_membrane", "score_ecd", "score_model", "structural_score",
                    "has_fold", "flags", "census_class", "span_aa", "tranche", "is_reference"):
            assert key in row, key
        assert row["structural_score"] == pytest.approx(
            row["score_membrane"] * row["score_ecd"] * row["score_model"])
    # ⚠ NO analysis_id on the wire: 75 of the 82 cohort accessions are also census rows, and an
    # id here is one careless render from a census fold under a cohort target's link
    assert all("analysis_id" not in row for row in rows)
    assert rows[0]["census_url"] == "/api/census/P00001"


def test_the_population_key_names_the_other_route_by_name(engine, tmp_path):
    """⚠⚠ F-049's third instance: two routes used the word `ranked` for two populations and
    neither payload said which."""
    _load_run(engine, tmp_path)
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert "/api/ranking" in body["separation"]
    assert "/api/ranking" in body["population_key"]["n_candidates"]["text"]
    assert "D-041" in body["separation"] and "D-081" in body["separation"]
    for key in ("n_candidates", "n_reference", "n_with_fold", "n_without_fold", "rank"):
        assert body["population_key"][key]["kind"], key
        assert body["population_key"][key]["text"].strip(), key


def test_the_formula_and_its_exclusions_are_served_not_typed_on_a_surface(engine, tmp_path):
    _load_run(engine, tmp_path)
    formula = _client(engine, tmp_path).get("/api/census-structural-ranking").json()["formula"]
    assert formula["expression"] == "structural_score = score_membrane × score_ecd × score_model"
    assert [f["factor"] for f in formula["excluded_factors"]] == [
        "cancer", "normal_risk", "internalization", "density"]
    assert all(f["why"].strip() for f in formula["excluded_factors"])
    assert set(formula["flag_meaning"]) == set(cs.FLAG_MEANING)


def test_no_run_reports_not_run_with_the_disclaimer_still_present(engine, tmp_path):
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert body["result_status"] == "not_run"
    assert body["rows"] == [] and body["run"] is None
    assert body["n_candidates"] == 0                       # stated as 0, never omitted
    assert "STRUCTURAL_ONLY" in body["disclaimer"]
    assert "/api/ranking" in body["separation"]


def test_a_superseded_run_is_never_served(engine, tmp_path):
    _seed_census_folds(engine)
    manifest = _fixture_manifest(tmp_path)
    rows = loader.compute_rows(loader.fold_facts(engine), manifest=manifest)
    first = loader.persist(engine, rows, manifest=manifest)
    second = loader.persist(engine, rows, manifest=manifest)
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert body["run"]["id"] == second and body["run"]["id"] != first


def test_an_invalid_run_is_never_served(engine, tmp_path):
    """⚠ The predicate is `run_status == 'valid'`, not `!= 'superseded'` — a run the loader
    refused to certify must not reach the surface by not being superseded."""
    run_id = _load_run(engine, tmp_path)
    with Session(engine) as s:
        s.get(CensusStructuralRun, run_id).run_status = loader.RUN_INVALID
        s.commit()
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert body["result_status"] == "not_run"


# ───────────────── 4. the wall between this and the learned scorer ────────────


def _seed_cohort_82_scorer(engine) -> None:
    """A valid pre-registered cohort-82 run, exactly as `tests/test_ranking_route.py` seeds it."""
    with Session(engine) as s:
        run = RankingRun(target_list_version="v", scorer_version="cohort82-good",
                         run_kind="preregistered")
        s.add(run)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=run.id, n_fit_positives=3, n_ranking_set=7, spearman=0.123,
            spearman_n=1, structural_percentiles=[0.71],
            lambda_per_fold=[{"symbol": "GENE_HI", "lam": 1.0, "converged": True}],
            excluded=[], loo_status="complete", fulldata_status="converged",
            status_detail="all pre-registered statistics produced",
        ))
        a = ProteinAnalysis(input_type="uniprot", input_value="ACC-HI", cohort_tranche=0,
                            meta={"gene": "GENE_HI"})
        s.add(a)
        s.flush()
        s.add(TargetScore(ranking_run_id=run.id, analysis_id=a.id, score=0.91,
                          attributions=[0.1] * 6, rank=1))
        s.commit()


def test_the_cohort_82_ranking_route_is_unchanged_by_a_census_structural_run(engine, tmp_path):
    """⚠⚠ THE REGRESSION THE GO ASKS FOR, AS A PROPERTY: the ranking payload is captured BEFORE
    any census structural run exists and asserted byte-identical after one has been loaded."""
    _seed_cohort_82_scorer(engine)
    client = _client(engine, tmp_path)
    before = client.get("/api/ranking").json()
    assert before["result_status"] == "complete" and before["rows"][0]["gene"] == "GENE_HI"

    _load_run(engine, tmp_path)
    after = client.get("/api/ranking").json()
    assert after == before, "a census structural run changed /api/ranking"
    assert after["run"]["scorer_version"] == "cohort82-good"


def test_a_census_structural_row_never_reaches_the_cohort_82_tables(engine, tmp_path):
    _seed_cohort_82_scorer(engine)
    _load_run(engine, tmp_path)
    with Session(engine) as s:
        assert s.query(RankingRun).count() == 1               # the one cohort run, unchanged
        assert s.query(TargetScore).count() == 1
        assert s.query(RankingResult).count() == 1
        assert s.query(CensusStructuralScore).count() == 6    # and the census rows are elsewhere
        # ⚠ no census accession acquired a `ranking_run_id` — D-079: census rows are not scored
        # by the learned scorer, and this rank does not change that
        census = s.scalars(select(ProteinAnalysis)
                           .where(ProteinAnalysis.cohort_tranche > 0)).all()
        assert [r.ranking_run_id for r in census] == [None] * len(census)


def test_neither_the_formula_nor_the_loader_nor_the_reader_names_the_scorer_tables():
    """⚠ The check is the SOURCE of the three new files: a module that never mentions
    `ranking_results` cannot mutate it."""
    for src, label in ((CORE_SRC, "core/census_structural.py"),
                       (LOADER_SRC, "scripts/census_structural_rank.py"),
                       (READ_SRC, "app/census_structural_read.py")):
        for table in SCORER_TABLES:
            # ⚠ the reader names them in PROSE (its separation statement), so the check is the
            # AST's string constants and imported names — never the raw text.
            tree = ast.parse(src)
            imported = {n.name for node in ast.walk(tree)
                        if isinstance(node, ast.ImportFrom)
                        for n in node.names}
            assert "RankingRun" not in imported, label
            assert "TargetScore" not in imported, label
            assert "RankingResult" not in imported, label
            assert "run_kind" not in [
                n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)], (
                f"{label} types `run_kind` — this path must not reuse the scorer's discriminator")
            assert table not in [
                n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)], (
                f"{label} names the table {table} as a value")


def test_no_census_structural_path_imports_the_learned_scorer_or_the_fitter():
    """⚠ D-079 decision 1: *no census path imports `core/scorer.py` or the fitter.* This rank is
    arithmetic, and it must stay unable to reach the model that is not."""
    for src, label in ((CORE_SRC, "core/census_structural.py"),
                       (LOADER_SRC, "scripts/census_structural_rank.py"),
                       (READ_SRC, "app/census_structural_read.py")):
        modules = set()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                modules |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        for banned in ("core.scorer", "scripts.fit_scorer", "sklearn", "numpy"):
            assert banned not in modules, f"{label} imports {banned}"


def test_the_learned_scorer_cannot_reach_the_census_structural_formula():
    """⚠ The other direction, and it is the one that would matter: `core/scorer.py` and
    `core/features.py` reaching this module would put a compute-and-annotation product inside a
    pre-registered feature path (the `tests/test_foldability.py` guard, one module along)."""
    for name in ("scorer", "features"):
        src = (REPO / "core" / f"{name}.py").read_text(encoding="utf-8")
        assert "census_structural" not in src, f"core/{name}.py reaches the census rank"


def test_app_reads_and_the_census_structural_reader_do_not_import_each_other():
    """⚠ D-079 amendment 1 ruling 5's wall, checkable at file granularity — the same shape
    `census_profile_read.py` and `census_cost_read.py` already keep."""
    reads = (REPO / "app" / "reads.py").read_text(encoding="utf-8")
    assert "census_structural" not in reads, "app/reads.py must not learn this score"
    assert "from app.reads import" not in READ_SRC and "app.reads" not in READ_SRC


def test_the_migration_is_additive_and_rewrites_nothing(engine):
    """⚠⚠ `alembic` OPERATIONS, read off the migration's AST — not a grep. A `drop_table` on
    `ranking_results` would be the one unrecoverable mistake available here."""
    src = MIGRATION.read_text(encoding="utf-8")
    ops = [node.func.attr for node in ast.walk(ast.parse(src))
           if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
           and isinstance(node.func.value, ast.Name) and node.func.value.id == "op"]
    upgrade_ops = [o for o in ops if o in ("create_table", "create_index", "add_column",
                                           "alter_column", "drop_column", "drop_table",
                                           "drop_index", "execute", "rename_table")]
    assert "alter_column" not in upgrade_ops and "drop_column" not in upgrade_ops
    assert "rename_table" not in upgrade_ops and "execute" not in upgrade_ops
    # the only tables it creates are the two new ones, and the only ones it drops are the same
    created = [node.args[0].value for node in ast.walk(ast.parse(src))
               if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
               and node.func.attr == "create_table" and node.args
               and isinstance(node.args[0], ast.Constant)]
    dropped = [node.args[0].value for node in ast.walk(ast.parse(src))
               if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
               and node.func.attr == "drop_table" and node.args
               and isinstance(node.args[0], ast.Constant)]
    assert sorted(created) == ["census_structural_runs", "census_structural_scores"]
    assert sorted(dropped) == ["census_structural_runs", "census_structural_scores"]
    for table in SCORER_TABLES:
        assert table not in created and table not in dropped


def test_the_migration_declares_the_unique_grain_the_orm_declares(engine):
    """⚠ F-021 / 0010's lesson: a constraint that exists only in the migration is untested by
    every test we run, and one that exists only in the ORM is absent from production."""
    src = MIGRATION.read_text(encoding="utf-8")
    assert "uq_census_structural_scores_run_accession" in src
    names = {c.name for c in CensusStructuralScore.__table__.constraints if c.name}
    assert "uq_census_structural_scores_run_accession" in names


def test_the_migration_renders_valid_postgres_ddl_without_a_database():
    """⚠⚠ THE TEST SUBSTRATE IS SQLITE AND PRODUCTION IS POSTGRES — `F-056`: the suite runs on a
    database that forgives exactly what production rejects. Alembic's **offline** mode renders
    this migration against the real Postgres dialect with no server, so a `JSONB`, a
    `server_default` or a constraint that only works on SQLite reddens on the CPU gate instead of
    at `alembic upgrade head` in the `postgres` job."""
    import subprocess

    out = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade",
         "0011_clinical_edges:0012_census_structural_rank", "--sql"],
        cwd=REPO, capture_output=True, text=True,
        env={**os.environ, "DATABASE_URL": "postgresql+psycopg://u:p@localhost/offline"},
    )
    assert out.returncode == 0, out.stderr[-2000:]
    sql = out.stdout
    assert "CREATE TABLE census_structural_runs" in sql
    assert "CREATE TABLE census_structural_scores" in sql
    assert "JSONB" in sql, "the JSON columns must render as JSONB on Postgres, not JSON"
    assert "CONSTRAINT uq_census_structural_scores_run_accession UNIQUE (run_id, accession)" in sql
    # ⚠ additive, on the wire as well as in the source: no statement touches the scorer's tables
    for table in SCORER_TABLES:
        assert table not in sql, f"the rendered DDL mentions {table}"
    for destructive in ("DROP TABLE", "ALTER TABLE", "DELETE FROM", "TRUNCATE"):
        assert destructive not in sql.upper(), destructive


def test_the_migration_chain_is_linear_and_this_is_its_head():
    """⚠ A second migration claiming `0011_clinical_edges` as its parent would leave two heads
    and `alembic upgrade head` would refuse — caught here, not in the Postgres CI job."""
    versions = REPO / "db" / "migrations" / "versions"
    downs = {}
    for path in versions.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        rev = re.search(r'^revision: str = "([^"]+)"', text, re.M).group(1)
        down = re.search(r'^down_revision: Union\[str, None\] = (?:"([^"]+)"|None)', text, re.M)
        downs[rev] = down.group(1) if down and down.group(1) else None
    assert downs["0012_census_structural_rank"] == "0011_clinical_edges"
    parents = [d for d in downs.values() if d]
    assert len(parents) == len(set(parents)), f"two migrations share a parent: {downs}"
    heads = set(downs) - set(parents)
    assert heads == {"0012_census_structural_rank"}, heads


# ──────────────────────── the living log and the docs ─────────────────────────


def _d144_entry() -> str:
    """The D-144 entry only, bounded by the next `### ` heading whatever it is — an unmerged
    neighbour may land between this entry and D-141 (the D-141 boundary lesson)."""
    start = LOG.index("\n### D-144 —") + 1
    nxt = re.search(r"^### (?!D-144\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_log_entry_exists_and_leads_the_log():
    """⚠⚠ THE CHECK IS THE `### D-144` HEADING, NEVER A CITATION OF IT (D-062 / method-note
    item 7). PR #90 was titled for a decision whose entry its diff never added."""
    assert re.search(r"^### D-144 — ", LOG, re.M), "no ### D-144 entry in docs/README.md"
    assert len(re.findall(r"^### D-144\b", LOG, re.M)) == 1, "exactly one D-144 entry"
    assert LOG.index("### D-144 —") < LOG.index("### D-141 —"), "newest first"


def test_the_log_entry_carries_the_locked_formula_and_its_exclusions():
    entry = _d144_entry()
    flat = " ".join(entry.split())
    assert "score_membrane × score_ecd × score_model" in flat
    for factor in ("cancer", "normal_risk", "internalization", "density"):
        assert factor in flat, factor
    for number in ("0.2", "200", "0.8", "0.3"):
        assert number in flat, number
    lowered = flat.lower()
    assert "structural_only" in lowered
    assert "not hpa-weighted" in lowered and "not adc-ready" in lowered
    # ⚠ the sheet is a LENS, not the source of truth — the ruling this entry lands
    assert "source of truth" in lowered and "sheet" in lowered
    assert "0.5" in flat, "the neutral it refuses must be named, not silently absent"


def test_the_log_entry_names_the_go_and_the_separation_from_the_learned_scorer():
    lowered = " ".join(_d144_entry().split()).lower()
    assert "matt" in lowered and "go" in lowered
    assert "2026-09-08" in lowered
    for cite in ("d-041", "d-060", "/api/ranking", "preregistered"):
        assert cite in lowered, cite
    assert "census_structural_runs" in lowered and "census_structural_scores" in lowered


def test_the_log_entry_states_the_d079_supersession_precisely():
    """⚠⚠ D-079 dec 1 barred a census row being RANKED. This entry lifts that half on the GO,
    and a vague supersession is worse than none — so the entry must say which clause moved and
    which stands (D-129-C: a superseded claim never stands alone)."""
    entry = _d144_entry()
    flat = " ".join(entry.split())
    lowered = flat.lower()
    assert "d-079" in lowered, "the ruling this narrows must be named"
    assert "supersede" in lowered
    for standing in ("core/scorer.py", "ranking_run_id", "scored: false", "accession"):
        assert standing in flat, standing
    # ⚠ the clause that moved, and the clause that did not, must both be present
    assert "lifted" in lowered and "stands" in lowered


def test_the_log_entry_carries_a_deep_learning_justification():
    """⚠ CLAUDE.md's prime directive: every substantive decision states one."""
    entry = _d144_entry()
    assert "Deep-learning justification" in entry
    lowered = " ".join(entry.split()).lower()
    assert "esmfold" in lowered and "plddt" in lowered


def test_the_log_entry_states_what_it_could_not_verify():
    """⚠⚠ D-016. The disqualifying facts lead: no database was reachable from this build, so no
    run was loaded and the served rank is `not_run` until someone runs the script."""
    lowered = " ".join(_d144_entry().split()).lower()
    assert "no database_url" in lowered or "no database" in lowered
    assert "not_run" in lowered
    assert "pqr" in lowered, "the unresolved reference name from the GO must be named, not dropped"


def test_the_next_free_integer_is_named_and_barred():
    """⚠ The seventh pass through this resolution, by ADDING and never by a `>=`. D-142 and
    D-143 are spent by concurrent Matt-assigned work that has not landed here, so the hole is
    recorded in `docs/RESERVED.md` rather than smoothed over."""
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 144 in ids
    # ⚠⚠ 145 IS NOW WRITTEN, AND THIS BAR REDDENED EXACTLY AS THE ENTRY ABOVE SAID IT WOULD
    # (*"when 142 and 143 land, the enumerations redden by design and the resolution is to ADD
    # them by name"* — the same rule, one integer later). `D-145` bakes THIS entry's loader,
    # `scripts/census_structural_rank.py`, into the Fly serving image as one explicit `COPY`
    # beside the ingest: image permanence for the instrument D-144 shipped, and **no formula, no
    # route, no schema and no `--load`**, so nothing this suite measures moves. The bar is
    # REPLACED BY A NAME — never deleted — and `### D-146` takes the next-free bar. Never a `>=`.
    assert re.search(r"^### D-145 — The D-144 loader stops living on the production host",
                     LOG, re.M), (
        "D-145 must be the image-permanence entry that bakes this entry's loader into the "
        "serving image, not some other entry that took the number")
    # ⚠⚠ 146 IS NOW WRITTEN, AND THIS BAR REDDENED EXACTLY AS THE ONE ABOVE IT DID ONE INTEGER
    # AGO. `D-146` retires the Track B copy clause that denied THIS entry's route existed —
    # *"it runs offline: it is not a ranked surface in this application"* — now that
    # `GET /api/census-structural-ranking` answers `result_status: valid`. It is copy only: **no
    # formula, no schema, no migration, no route and no loader byte moves**, so nothing this
    # suite measures changes. The bar is REPLACED BY A NAME — never deleted — and `### D-147`
    # takes the next-free bar. Never a `>=`.
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     LOG, re.M), (
        "D-146 must be the Track B live-route copy entry, not some other entry that took "
        "the number")
    assert "\n### D-147" not in LOG, (
        "D-147 is the next free integer and must stay unspent until an entry claims it by name")
    # ⚠⚠ 142 AND 143 ARE NOW WRITTEN ON `main`, AND THAT IS WHY THIS ASSERTION CHANGED SHAPE.
    # This entry's first draft reserved both in `docs/RESERVED.md`, because at `30f402f` neither
    # had a heading, an open PR or a branch. Both then merged (`f243f93` / `22ce1d7` / `b7d933f`)
    # while D-144 was open. **A cited integer must resolve to a `### ` entry OR to a RESERVED
    # row** — that is the invariant — so now that they resolve to entries, requiring a
    # reservation as well would be requiring the hole to stay open.
    for spent in ("D-142", "D-143"):
        assert re.search(rf"^### {spent} — ", LOG, re.M), (
            f"{spent} is cited by the D-144 entry; it must resolve to a `### ` entry now that "
            f"it is written, or to a RESERVED row while it is not")
    reserved = (REPO / "docs" / "RESERVED.md").read_text(encoding="utf-8")
    # ⚠⚠ THE MARKER IS THE POINT OF THIS ASSERTION, AND D-145 RETIRED ITS ROW WITHOUT MOVING IT.
    # `re.search` on the literal `| **D-145** |` row is how this test resolves the citation; a
    # strike-through (`~~**D-145**~~`) would have satisfied `docs/RESERVED.md`'s own convention
    # and broken THIS guard — the exact trap the `D-142` row records of itself. So the row stays
    # marker-safe and records ✅ WRITTEN inside the cell, and this assertion is UNCHANGED: while
    # 145 was unwritten the row was what kept it resolved, and now that it is written the row is
    # its retirement record. Either way it must exist.
    assert re.search(r"^\| \*\*D-145\*\*", reserved, re.M), (
        "D-145 is cited by the D-144 entry; its RESERVED row must survive as a row — retired "
        "marker-safe, never struck or deleted — or this citation resolves through nothing")
    # ⚠ And the next free integer must carry a row of its own, for the same reason 145 did.
    # ⚠⚠ UNCHANGED AT D-146, DELIBERATELY, AND THE ROW IS NOW A RETIREMENT RECORD RATHER THAN A
    # RESERVATION. `D-146` was spent by the Track B live-route copy entry and its row was retired
    # **marker-safe** — this `re.search` on the literal `| **D-146** |` is exactly why a strike to
    # `~~**D-146**~~` was refused there, the same trap the `D-142` and `D-145` rows record of
    # themselves. Either way the row must exist: while 146 was unwritten it was what kept the
    # citation resolved, and now that it is written it is what records the spend.
    assert re.search(r"^\| \*\*D-146\*\*", reserved, re.M), (
        "D-146 is cited by this entry; its RESERVED row must survive as a row — retired "
        "marker-safe, never struck or deleted — or this citation resolves through nothing")
    # ⚠ the retired reservation is STRUCK, not deleted (D-129-C): it records what was reserved
    assert "~~**D-143**~~" in reserved, (
        "the D-143 reservation must be retired in place, so a reader can tell 'written' from "
        "'never reserved'")


def test_the_architecture_doc_records_the_shipped_shape():
    """⚠ CLAUDE.md rule 2: a PR that changes structure updates ARCHITECTURE.md in the same PR."""
    flat = " ".join(ARCH.split())
    assert "census_structural_runs" in flat and "census_structural_scores" in flat
    assert "/api/census-structural-ranking" in flat
    assert "scripts/census_structural_rank.py" in flat
    assert "STRUCTURAL_ONLY" in flat


def test_the_log_entry_records_the_ids_that_merged_mid_flight():
    """⚠⚠ 142 and 143 were unwritten, unpublished and unbranched when this entry was drafted at
    `30f402f`; all three of #266 / #268 / #267 then merged while the PR was open, and the bars
    this branch had placed on `### D-142` / `### D-143` reddened on the rebase.

    D-129-C: the original reading is left standing and the amendment is added beside it. The
    D-141 precedent test (`…records_why_140_was_not_taken_and_that_263_then_merged`) is the
    shape — the merge commits must be NAMED, not alluded to, or a later reader cannot check
    which tree the claim was true of.
    """
    entry = _d144_entry()
    flat = " ".join(entry.split())
    lowered = flat.lower()
    assert "amended in place" in lowered, "the mid-flight merges must be recorded, not smoothed"
    for sha in ("30f402f", "f243f93", "22ce1d7", "b7d933f"):
        assert sha in flat, f"the commit {sha} must be named, not alluded to"
    assert "gh pr list --state open" in lowered, "the id must be checked, not assumed"
    # ⚠ the resolution direction is the load-bearing part: ADD a name, never relax to a `>=`
    assert "relaxed to a `>=`" in lowered, "the ADD-never-loosen direction must be stated"
    assert "no bar was deleted" in lowered
    assert "d-145" in lowered, "the next free integer must be named as barred"
    # ⚠ and the T-id renumber is recorded rather than silently applied
    assert "t-1225" in lowered and "t-1243" in lowered


def test_the_method_surface_carries_the_section_and_its_banner():
    """⚠ The GO's UI minimum: a Method one-liner that this is a STRUCTURAL_ONLY full-census rank,
    distinct from the cohort-82 scorer, and that the Sheet is a lens. Asserted from Python as
    well as from vitest, the `test_both_method_surfaces_…` shape — the copy obligation is the
    decision's, not the UI suite's."""
    method = (REPO / "ui" / "src" / "components" / "MethodNote.jsx").read_text(encoding="utf-8")
    assert 'id="census-structural-rank"' in method, (
        "the section must carry an id or it drops out of D-138's derived contents rail")
    assert "STRUCTURAL_ONLY" in method
    assert "not HPA-weighted" in method and "not ADC-ready" in method
    assert "source of\n            truth" in method or "source of truth" in method
    assert "review lens" in method
    assert "/api/census-structural-ranking" in method
    # ⚠ it must say it is NOT the learned scorer, by name
    assert "not the learned scorer" in method
    # and the census table's own honesty is restated where a reader will be
    assert "no score and no rank" in method
    assert (REPO / "ui" / "src" / "components"
            / "MethodNote.censusStructural.test.jsx").is_file()


def test_the_test_plan_carries_the_d144_addendum_on_ids_nobody_else_holds():
    """⚠⚠ THE T-ID COLLISION, AS A PROPERTY. This addendum was written on T-1225–T-1233 against
    `30f402f`; D-143 then took **T-1225–T-1229**, its amendment **T-1234**, and D-142
    **T-1235–T-1242**. The nine ids moved to T-1243–T-1251, and the check is that **no id this
    addendum claims appears in anyone else's addendum** — not merely that the numbers changed."""
    plan = (REPO / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
    assert "D-144" in plan
    assert "census-structural-ranking" in plan

    start = plan.index("### D-144 (this PR;")
    nxt = plan.index("## Addendum", start)
    mine = plan[start:nxt]
    ours = [f"T-{n}" for n in range(1243, 1252)]
    assert "(this PR; T-1243–T-1251)" in mine
    for tid in ours:
        assert f"| **{tid}** |" in mine, f"{tid} has no row in the D-144 addendum"
    others = plan[:start] + plan[nxt:]
    for tid in ours:
        assert f"| **{tid}** |" not in others, (
            f"{tid} is claimed by another addendum as well — the collision is not resolved")
    # ⚠ the renumber is RECORDED, and the gap it declines to back-fill is named
    assert "T-1225–T-1233 → T-1243–T-1251" in mine
    assert "T-1230–T-1233 are left" in mine
    for spent_elsewhere in ("T-1225", "T-1234", "T-1242"):
        assert f"| **{spent_elsewhere}** |" not in mine, spent_elsewhere
