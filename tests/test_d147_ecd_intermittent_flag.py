"""D-147 — `ecd_intermittent` on the census structural ranking surface.

Five things are under test, and the last two are the ones that would actually let the defect back:

1. **The flag**: `intermittent` gets it, `contiguous` does not, and ⚠⚠ `no_accepted_segment` does
   **not** — the GO's hard stop against collapsing 125 GPI-architecture rows into the multi-loop
   category, asserted as a count that moves by exactly 125 if it is broken.
2. **The served row and the served count**: the four `F-037` field names, and
   `component_counts.by_flag.ecd_intermittent` **counted from the rows that were served** rather
   than transcribed from the derivation's provenance file (`F-026`: a verification sharing an
   implementation with its subject agrees with it).
3. **⚠⚠ THE SCORE DID NOT MOVE.** Every pinned row's `structural_score` is asserted to the value
   the formula produced before this entry existed, `formula_version()` is asserted to be the same
   `c859da97f73d` the **live** run recorded, and `core/census_structural.py` is asserted never to
   have learned the word `topology` at all.
4. **The honesty**: the served `flag_meaning` denies score composition and denies internalization
   **by name**, `formula.excluded_factors` still calls internalization never-measured, and the
   MethodNote paragraph carries both denials.
5. **The absences**: a **stale** or **absent** derivation withholds every topology and flags
   nothing, rather than serving a silent `contiguous` — because *"a wrong topology is worse than a
   missing one, because a missing one is visible."*

⚠ **What this suite CANNOT establish, stated here rather than discovered later: no test here
contacts the deployed application.** The served count is proved against a seeded SQLite run plus
the committed CSV; the deployed answer becomes true on release, not on merge. The bridge between
the two is the **bijection** and the **content-hash** checks below, which are properties of two
committed files rather than observations of production.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from app import census_structural_read as reader  # noqa: E402
from app.main import create_app  # noqa: E402
from core import census_segments as segs  # noqa: E402
from core import census_structural as cs  # noqa: E402
from db.models import Base  # noqa: E402
from scripts import census_structural_rank as loader  # noqa: E402

LOG = (REPO / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (REPO / "ARCHITECTURE.md").read_text(encoding="utf-8")
RESERVED = (REPO / "docs" / "RESERVED.md").read_text(encoding="utf-8")
FORMULA_SRC = (REPO / "core" / "census_structural.py").read_text(encoding="utf-8")
SEGMENTS_SRC = (REPO / "core" / "census_segments.py").read_text(encoding="utf-8")
READ_SRC = (REPO / "app" / "census_structural_read.py").read_text(encoding="utf-8")
LOADER_SRC = (REPO / "scripts" / "census_structural_rank.py").read_text(encoding="utf-8")
METHOD_NOTE = (REPO / "ui" / "src" / "components" / "MethodNote.jsx").read_text(encoding="utf-8")

CENSUS = REPO / "data" / "census"
MANIFEST_CSV = CENSUS / "census_manifest.v7.csv"
SEGMENTS_CSV = CENSUS / "span_segments.csv"
SEGMENTS_PROVENANCE = CENSUS / "span_segments.provenance.json"

TOKEN = "test-token"

#: ⚠⚠ **REAL ACCESSIONS, DELIBERATELY, AND THIS IS `A-017`.** A fixture of invented ids
#: (`P00001`…) would have no row in the committed `span_segments.csv`, so the join would return
#: `unknown` for every one of them and **every flag assertion below would pass against a payload in
#: which the flag never appears.** The fixture must reach the code under test, so the population is
#: five accessions whose real topologies cover all three words plus the reference sink.
#:
#: `(accession, census_class, span_aa, tranche, mean_plddt or None, expected topology)`
FIXTURE_POPULATION = (
    # rank 1 of the LIVE census structural rank, and it is intermittent — 4 segments, 442 of 494 aa
    ("O75899", "surface", 442, 5, 84.43, segs.TOPOLOGY_INTERMITTENT),
    # intermittent AND well below the 200 aa cap, so score_ecd is a fraction rather than saturated
    ("P51677", "surface", 34, 1, 90.0, segs.TOPOLOGY_INTERMITTENT),
    # one unbroken stretch: the span IS the ectodomain
    ("P05362", "surface", 453, 5, 70.0, segs.TOPOLOGY_CONTIGUOUS),
    # ⚠ GPI architecture: no topological domains BY DESIGN, and never folded here
    ("Q9Y2I2", "surface", 481, 5, None, segs.TOPOLOGY_NO_ACCEPTED_SEGMENT),
    # NECTIN4 — the reference sink, and contiguous
    ("Q96NY8", "surface", 318, 4, 95.0, segs.TOPOLOGY_CONTIGUOUS),
)

#: ⚠⚠ THE SCORES, PINNED TO WHAT THE FORMULA PRODUCED **BEFORE** THIS ENTRY EXISTED. Computed by
#: hand from `score_membrane × score_ecd × score_model`, not read back out of the code under test —
#: a pin derived from the implementation cannot detect the implementation changing (`F-026`).
PINNED_SCORES = {
    "O75899": 1.0 * 1.0 * 0.8443,            # 442 aa saturates the cap; pLDDT 84.43 — the live row
    "P51677": 1.0 * (34 / 200) * 0.90,       # 0.153 — a fraction of the cap, so a penalty WOULD show
    "P05362": 1.0 * 1.0 * 0.70,
    "Q9Y2I2": 1.0 * 1.0 * 0.30,              # no fold at all: the 0.3 penalty
    "Q96NY8": 1.0 * 1.0 * 0.95,              # highest score in the population, and it still sinks
}


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


def _fixture_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "manifest.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["census_accession", "census_class", "span_aa",
                                           "tranche"])
        w.writeheader()
        for acc, klass, span, tranche, _plddt, _topo in FIXTURE_POPULATION:
            w.writerow({"census_accession": acc, "census_class": klass,
                        "span_aa": str(span), "tranche": str(tranche)})
    return path


def _seed_folds(engine) -> None:
    from sqlalchemy.orm import Session

    from db.models import ProteinAnalysis

    with Session(engine) as s:
        for acc, _klass, _span, tranche, plddt, _topo in FIXTURE_POPULATION:
            if plddt is None:
                continue                       # Q9Y2I2 has no analysis row at all — never folded
            s.add(ProteinAnalysis(input_type="uniprot", input_value=acc,
                                  cohort_tranche=tranche, pdb_path=f"/a/{acc}.pdb",
                                  mean_plddt=plddt, meta={}))
        s.commit()


def _load(engine, tmp_path) -> int:
    _seed_folds(engine)
    manifest = _fixture_manifest(tmp_path)
    rows = loader.compute_rows(loader.fold_facts(engine), manifest=manifest)
    return loader.persist(engine, rows, manifest=manifest)


def _payload(engine, tmp_path) -> dict:
    _load(engine, tmp_path)
    r = _client(engine, tmp_path).get("/api/census-structural-ranking")
    assert r.status_code == 200
    return r.json()


def _committed_topologies() -> dict[str, str]:
    with SEGMENTS_CSV.open(encoding="utf-8", newline="") as fh:
        return {r["census_accession"].strip().upper(): r["topology"].strip()
                for r in csv.DictReader(fh)}


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


# ───────────────────────── 1. the flag, and the hard stop ─────────────────────


def test_an_intermittent_row_carries_the_flag():
    join = segs.segment_join()
    for acc, _k, _s, _t, _p, topology in FIXTURE_POPULATION:
        if topology != segs.TOPOLOGY_INTERMITTENT:
            continue
        assert join.topology_for(acc) == segs.TOPOLOGY_INTERMITTENT, acc
        assert join.flags_for(acc) == (segs.FLAG_ECD_INTERMITTENT,), acc


def test_a_contiguous_row_carries_no_flag():
    """⚠ There is nothing to disclose about a single unbroken stretch: the span IS the ectodomain,
    so a flag there would be noise that trains readers to ignore the flag that matters."""
    join = segs.segment_join()
    for acc, _k, _s, _t, _p, topology in FIXTURE_POPULATION:
        if topology != segs.TOPOLOGY_CONTIGUOUS:
            continue
        assert join.topology_for(acc) == segs.TOPOLOGY_CONTIGUOUS, acc
        assert join.flags_for(acc) == (), acc


def test_a_no_accepted_segment_row_is_not_intermittent_and_wears_no_flag():
    """⚠⚠ THE GO'S HARD STOP, AS A PROPERTY. GPI-anchored proteins carry no topological domains
    **by design** (`F-025`) — the whole mature chain is outward-facing. In the Census legend's own
    words the absence is *"not missing data, and not an intermittent surface"*, so pooling them in
    would assert a multi-loop surface for 125 proteins that have none."""
    join = segs.segment_join()
    assert join.topology_for("Q9Y2I2") == segs.TOPOLOGY_NO_ACCEPTED_SEGMENT
    assert join.flags_for("Q9Y2I2") == ()
    # and the three words stay three words
    assert segs.TOPOLOGY_NO_ACCEPTED_SEGMENT != segs.TOPOLOGY_INTERMITTENT
    assert len(set(segs.TOPOLOGIES)) == 3


def test_the_three_topologies_are_counted_separately_and_reconcile():
    """⚠ A three-way breakdown that does not sum to the population is how a fourth silent
    category hides. Measured from the committed CSV: 1,649 / 1,693 / 125 = 3,467."""
    committed = _committed_topologies()
    counts = {word: sum(1 for w in committed.values() if w == word) for word in segs.TOPOLOGIES}
    assert counts == {segs.TOPOLOGY_INTERMITTENT: 1649,
                      segs.TOPOLOGY_CONTIGUOUS: 1693,
                      segs.TOPOLOGY_NO_ACCEPTED_SEGMENT: 125}
    assert sum(counts.values()) == len(committed) == 3467
    # ⚠ no word outside the declared three reached the artifact
    assert set(committed.values()) == set(segs.TOPOLOGIES)


def test_the_committed_derivation_is_a_bijection_with_the_population():
    """⚠⚠ THE QUERY THAT COULD HAVE DISQUALIFIED THE WHOLE COMPUTE-AT-SERVE DESIGN. A partial join
    would mean some rows carry a topology and the rest carry an absence indistinguishable from
    `contiguous`, and the right build would then have been a named `topology_unrecorded` category
    rather than a flag."""
    with MANIFEST_CSV.open(encoding="utf-8", newline="") as fh:
        population = {r["census_accession"].strip().upper() for r in csv.DictReader(fh)}
    derived = set(_committed_topologies())
    assert len(population) == len(derived) == 3467
    assert sorted(population - derived) == []
    assert sorted(derived - population) == []


def test_the_derivation_is_stamped_against_the_same_population_the_run_serves():
    """⚠⚠ THE SAME POPULATION BY CONTENT HASH, NOT BY FILENAME — `core/derived_freshness.py`'s own
    rule, and the reason a serve-time join can be trusted at all.

    `D-146` recorded the live run's `population_sha256: fd80d65d…3f970d07`. The stamp on the
    topology derivation and the manifest on disk must both be that value, or the flag describes a
    population the route is not serving.
    """
    stamp = json.loads(SEGMENTS_PROVENANCE.read_text(encoding="utf-8"))
    expected = "fd80d65df8b3acf59ce9faa135275dc75eac6caf7f4fc2a2cbc5399d3f970d07"
    on_disk = hashlib.sha256(MANIFEST_CSV.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    assert stamp["source_manifest_sha256"] == expected
    assert on_disk == expected, "the manifest moved — re-run scripts/span_segments.py"
    assert stamp["source_manifest"] == MANIFEST_CSV.name
    # ⚠ and the module agrees it is fresh, through the shared checker rather than a re-derivation
    from core.derived_freshness import FRESH

    assert segs.segment_join().verdict == FRESH


def test_the_top_of_the_live_rank_is_an_intermittent_row():
    """⚠⚠ THE DISQUALIFYING FACT OF `### D-147`, AS AN ASSERTION. `D-146`'s live read put
    `GABBR2` / `O75899` at rank 1 with `structural_score` 0.8443 and `flags: ["ecd_saturated"]`.
    It is a **four-segment** ECD: 442 aa folded of 494 aa, 52 discarded. The row every reader
    trusts most is the row that was least honest, and if this stops being true the entry's opening
    paragraph is stale."""
    facts = segs.segment_join().facts["O75899"]
    assert facts.topology == segs.TOPOLOGY_INTERMITTENT
    assert facts.segment_count == 4
    assert facts.extracellular_total_aa == 494
    assert facts.discarded_aa == 52
    assert facts.segments == "42-483;544-551;619-654;713-720"
    # ⚠ and the flag changes nothing about its score: 442 and 494 both saturate the 200 aa cap
    assert cs.score_ecd(442) == cs.score_ecd(494) == 1.0


def test_zero_is_a_measurement_and_a_blank_cell_is_not():
    """⚠ `segment_count = 0` is what `no_accepted_segment` MEANS and `discarded_aa = 0` is what
    `contiguous` means, so `whole_number` admits 0 where the formula's `_whole_residues` refuses
    it. A blank cell stays `None`, so the two are never printed the same."""
    assert segs.whole_number("0") == 0
    assert segs.whole_number(0) == 0
    assert segs.whole_number("") is None
    assert segs.whole_number("   ") is None
    assert segs.whole_number(None) is None
    assert segs.whole_number(True) is None and segs.whole_number(False) is None
    assert segs.whole_number("-3") is None
    assert segs.whole_number(4.0) == 4 and segs.whole_number(4.5) is None
    gpi = segs.segment_join().facts["Q9Y2I2"]
    assert gpi.segment_count == 0 and gpi.discarded_aa == 0 and gpi.segments is None


# ─────────────────────── 2. the served row and the count ──────────────────────


def test_the_flag_rides_on_the_served_ranking_row(engine, tmp_path):
    body = _payload(engine, tmp_path)
    by_acc = {r["accession"]: r for r in body["rows"]}
    for acc, _k, _s, _t, _p, topology in FIXTURE_POPULATION:
        wears = segs.FLAG_ECD_INTERMITTENT in by_acc[acc]["flags"]
        assert wears is (topology == segs.TOPOLOGY_INTERMITTENT), acc
        assert by_acc[acc]["topology"] == topology, acc


def test_the_served_row_carries_the_same_four_field_names_as_the_census_card(engine, tmp_path):
    """⚠ `topology` / `segment_count` / `extracellular_total_aa` / `discarded_aa` — the names
    `/api/census/{id}` has served since `F-037`. A ranking row and a census card describing one
    protein's segment structure in two vocabularies is the drift `D-133 am. 1` extracted
    `topologyBadgeKey` to prevent, one tier up."""
    body = _payload(engine, tmp_path)
    row = next(r for r in body["rows"] if r["accession"] == "O75899")
    assert row["segment_count"] == 4
    assert row["extracellular_total_aa"] == 494
    assert row["discarded_aa"] == 52
    # the same four keys the census projection emits, read off its source rather than retyped
    census_src = (REPO / "app" / "reads.py").read_text(encoding="utf-8")
    for key in ("topology", "segment_count", "extracellular_total_aa", "discarded_aa"):
        assert f'"{key}":' in census_src, f"/api/census stopped serving {key}"
        assert key in row, f"the ranking row does not serve {key}"


def test_the_by_flag_count_equals_the_rows_that_wear_the_flag(engine, tmp_path):
    """⚠⚠ THE COUNT AND THE ROWS CANNOT DISAGREE, BY CONSTRUCTION. If the count is ever taken from
    somewhere other than the served rows, this is the assertion that reddens — and it is the one
    that moves by exactly 125 if `no_accepted_segment` is collapsed in."""
    body = _payload(engine, tmp_path)
    wearing = [r["accession"] for r in body["rows"]
               if segs.FLAG_ECD_INTERMITTENT in r["flags"]]
    assert sorted(wearing) == ["O75899", "P51677"]
    served = body["run"]["component_counts"]["by_flag"][segs.FLAG_ECD_INTERMITTENT]
    assert served == len(wearing) == 2
    assert body["segment_topology"]["served_by_flag_count"] == 2
    # ⚠ and the persisted breakdown is reported beside it rather than replaced silently
    assert body["segment_topology"]["persisted_by_flag_count"] is None
    assert body["segment_topology"]["agrees_with_persisted"] is True


def test_the_by_flag_count_is_counted_from_the_rows_and_not_read_from_the_provenance_file(
        engine, tmp_path):
    """⚠⚠ `F-026`: a verification that shares an implementation with its subject agrees with it.

    `span_segments.provenance.json` already records `"intermittent": 1649`. Serving **that**
    integer beside rows flagged by a different traversal would report a number nothing in the
    payload can check — and over this five-row population it would be off by 1,647.
    """
    stamp = json.loads(SEGMENTS_PROVENANCE.read_text(encoding="utf-8"))
    assert stamp["intermittent"] == 1649, "the provenance file is the tempting shortcut"
    body = _payload(engine, tmp_path)
    served = body["run"]["component_counts"]["by_flag"][segs.FLAG_ECD_INTERMITTENT]
    assert served == 2, "the count follows the served rows, never the derivation's own total"
    # ⚠ and the integer is not a literal anywhere in either module — a copied constant is the
    # same defect with the file read removed
    for src, label in ((SEGMENTS_SRC, "core/census_segments.py"), (READ_SRC, "the reader")):
        numbers = [n.value for n in ast.walk(ast.parse(src))
                   if isinstance(n, ast.Constant) and isinstance(n.value, int)
                   and not isinstance(n.value, bool)]
        assert 1649 not in numbers, f"{label} carries the count as a constant"


def test_the_served_count_matches_the_committed_csv_over_the_real_population():
    """The bridge between the fixture-sized proof above and the 3,467-row population the route
    actually serves. ⚠ It is a property of two committed files, **not** an observation of the
    deployed route — nothing in this suite contacts Fly."""
    join = segs.segment_join()
    flagged = [acc for acc in join.facts if join.flags_for(acc)]
    assert len(flagged) == 1649
    committed = _committed_topologies()
    assert sorted(flagged) == sorted(a for a, w in committed.items()
                                     if w == segs.TOPOLOGY_INTERMITTENT)


def test_the_join_never_drops_or_reorders_a_persisted_flag(engine, tmp_path):
    """⚠ The overlay may only LENGTHEN the list. A reader diffing yesterday's payload against
    today's must see an append, and a bug in this join must not be able to retract `no_fold`."""
    body = _payload(engine, tmp_path)
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import CensusStructuralScore

    with Session(engine) as s:
        persisted = {r.accession: list(r.flags or [])
                     for r in s.scalars(select(CensusStructuralScore)).all()}
    for row in body["rows"]:
        was = persisted[row["accession"]]
        assert row["flags"][:len(was)] == was, row["accession"]
        extra = row["flags"][len(was):]
        assert extra in ([], [segs.FLAG_ECD_INTERMITTENT]), row["accession"]
    # ⚠⚠ the fixture actually exercises the append (A-017): O75899 keeps `ecd_saturated` AND gains
    # the new flag, so "persisted flags survive" is proved on a row that has one
    o75899 = next(r for r in body["rows"] if r["accession"] == "O75899")
    assert o75899["flags"] == [cs.FLAG_ECD_SATURATED, segs.FLAG_ECD_INTERMITTENT]


def test_the_flag_is_never_emitted_twice_if_a_loader_ever_persists_it(engine, tmp_path):
    """⚠ A set union rather than a bare append. Nothing persists the flag today; if something ever
    does, the row must not carry it twice and the count must not double."""
    _load(engine, tmp_path)
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import CensusStructuralScore

    with Session(engine) as s:
        row = s.scalars(select(CensusStructuralScore)
                        .where(CensusStructuralScore.accession == "O75899")).one()
        row.flags = list(row.flags or []) + [segs.FLAG_ECD_INTERMITTENT]
        s.commit()
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    served = next(r for r in body["rows"] if r["accession"] == "O75899")
    assert served["flags"].count(segs.FLAG_ECD_INTERMITTENT) == 1
    topology = body["segment_topology"]
    assert topology["served_by_flag_count"] == 2
    # ⚠⚠ AND THE DISAGREEMENT IS VISIBLE RATHER THAN OVERWRITTEN: the persisted breakdown said
    # nothing about this flag, the row now carries it, and `agrees_with_persisted` is the field
    # that would say so if a loader ever wrote a different total.
    assert topology["persisted_by_flag_count"] is None
    assert topology["agrees_with_persisted"] is True


def test_the_payload_names_the_source_and_the_posture_of_the_join(engine, tmp_path):
    body = _payload(engine, tmp_path)
    block = body["segment_topology"]
    assert block["source"] == "data/census/span_segments.csv"
    assert block["n_rows"] == 5 and block["n_joined"] == 5
    assert block["by_topology"] == {segs.TOPOLOGY_INTERMITTENT: 2,
                                    segs.TOPOLOGY_CONTIGUOUS: 2,
                                    segs.TOPOLOGY_NO_ACCEPTED_SEGMENT: 1}
    posture = _flat(block["posture"]).lower()
    assert "committed file" in posture
    assert "--load" in posture and "supersede" in posture
    assert "deployed tree" in posture
    # ⚠ every count states its key (method-note item 2), and this one's key says it is serve-time
    key = body["population_key"]["component_counts.by_flag.ecd_intermittent"]
    assert key["kind"] == "SERVE_TIME_JOIN_AGAINST_COMMITTED_FILE"
    assert "counted from the rows that were served" in _flat(key["text"]).lower()


def test_the_not_run_payload_still_carries_the_segment_topology_block(engine, tmp_path):
    """⚠ A block that appeared only alongside rows would read as an optional extra. A not-run panel
    is exactly where a reader reaches for numbers from somewhere else."""
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert body["result_status"] == "not_run"
    block = body["segment_topology"]
    assert block["served_by_flag_count"] == 0
    assert block["n_rows"] == 0 and block["by_topology"] == {}
    assert block["derivation_status"] == "fresh"
    assert block["enters_score"] is False and block["is_internalization"] is False
    # ⚠ and the flag's meaning is still served, because a not-run payload must not read as though
    # the disclosure were conditional on there being rows
    assert segs.FLAG_ECD_INTERMITTENT in body["formula"]["flag_meaning"]


# ───────────────────── 3. the score did not move. at all. ────────────────────


def test_the_structural_score_is_unchanged_for_every_pinned_row(engine, tmp_path):
    """⚠⚠ THE HARD STOP THE WHOLE ENTRY RESTS ON. The pins are computed by hand from
    `membrane × ecd × model`, never read back out of the code under test, and `P51677` is in the
    set precisely because its 34 aa span is **below** the cap — a penalty applied to an
    intermittent row would show there and be invisible on a saturated one."""
    body = _payload(engine, tmp_path)
    for row in body["rows"]:
        assert row["structural_score"] == pytest.approx(PINNED_SCORES[row["accession"]]), \
            row["accession"]
    # the flagged rows are in the pinned set, so this is not a vacuous pass (A-017)
    flagged = {r["accession"] for r in body["rows"]
               if segs.FLAG_ECD_INTERMITTENT in r["flags"]}
    assert flagged == {"O75899", "P51677"}
    # ⚠ and the ORDER is untouched: descending score with the reference sunk to the end. ⚠⚠ Note
    # what this ordering says — the highest-scoring CANDIDATE is an intermittent row and the
    # second is contiguous, so a penalty on the flag would have reordered the top of the list.
    assert [r["accession"] for r in body["rows"]] == [
        "O75899", "P05362", "Q9Y2I2", "P51677", "Q96NY8"]
    assert [r["rank"] for r in body["rows"]] == [1, 2, 3, 4, 5]


def test_the_served_score_is_the_persisted_score_for_every_factor_and_the_rank(engine, tmp_path):
    """⚠⚠ THIS TEST EXISTS BECAUSE A REVERT PROOF FOUND THE HOLE IT FILLS, AND THE HOLE IS WORTH
    NAMING (`### D-147` records it).

    The first draft of this suite proved score-immobility two ways — hand-computed pins on the
    served rows, and `D-144`'s AST guard on the **formula's** expression. A revert that multiplied
    `score_ecd` by `0.9` **in the reader**, for flagged rows only, was caught by the pins and by
    two sha256 pins and by **nothing else**: the AST guard reads `core/census_structural.py`, which
    that revert never touched, and `test_the_flag_does_not_reach_the_score_for_the_real_population`
    calls the formula directly rather than the route. ⚠ **A serve-time join is a serve-time place
    to apply a penalty**, so the guard belongs at the seam the join is on: the served numbers must
    equal the persisted ones, field by field, for every row.
    """
    _load(engine, tmp_path)
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import CensusStructuralScore

    with Session(engine) as s:
        stored = {r.accession: r for r in s.scalars(select(CensusStructuralScore)).all()}
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    assert len(body["rows"]) == len(stored) == 5
    flagged = 0
    for row in body["rows"]:
        was = stored[row["accession"]]
        for field in ("score_membrane", "score_ecd", "score_model", "structural_score",
                      "span_aa", "rank", "mean_plddt", "has_fold", "is_reference",
                      "census_class", "tranche", "gene"):
            assert row[field] == getattr(was, field), f"{row['accession']}.{field}"
        flagged += segs.FLAG_ECD_INTERMITTENT in row["flags"]
    # ⚠ A-017: the comparison has to run over rows that actually wear the flag, or it proves that
    # unflagged rows are unchanged — which nothing was threatening.
    assert flagged == 2


def test_the_flag_does_not_reach_the_score_for_the_real_population():
    """⚠ Over the whole committed population: for every accession, the score computed with the
    topology known and the score computed by the formula alone are the same object, because the
    formula cannot see a topology at all. Asserted as a value comparison so a future wiring shows
    up here and not only in the AST test below."""
    join = segs.segment_join()
    with MANIFEST_CSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    checked = 0
    for r in rows:
        acc = r["census_accession"].strip().upper()
        if not join.flags_for(acc):
            continue
        scored = cs.structural_score(r["census_class"], r["span_aa"],
                                     has_pdb=True, mean_plddt=90.0)
        expected = cs.score_membrane(r["census_class"]) * cs.score_ecd(r["span_aa"]) * 0.9
        assert scored.structural_score == pytest.approx(expected), acc
        assert segs.FLAG_ECD_INTERMITTENT not in scored.flags, acc
        checked += 1
    assert checked == 1649, "the loop must actually visit every flagged row (A-017)"


def test_the_formula_module_never_learns_what_a_topology_is():
    """⚠⚠ ONE PATH, SO THERE IS NOTHING TO DRIFT. `core/census_structural.py` must not mention a
    topology, must not import the segment supplier, and `structural_score` must take no parameter
    that could carry one — checked on the AST, because a docstring mentioning `topology` would
    satisfy a grep in either direction (`F-044`'s shape)."""
    tree = ast.parse(FORMULA_SRC)
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    imported |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not any("census_segments" in (m or "") for m in imported), \
        "the formula must not import the segment supplier"
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "structural_score")
    params = [a.arg for a in list(fn.args.args) + list(fn.args.kwonlyargs)]
    assert params == ["census_class", "span_aa", "has_pdb", "mean_plddt", "is_reference"]
    assert "topology" not in params
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert "topology" not in names and "segment_join" not in names
    # ⚠ and the flag is not declared there either: the D-144 guard pairs that module's FLAG_* names
    # against its own FLAG_MEANING, and a flag this entry owns belongs in this entry's mapping
    assert not hasattr(cs, "FLAG_ECD_INTERMITTENT")
    assert segs.FLAG_ECD_INTERMITTENT not in cs.FLAG_MEANING


def test_the_formula_version_pin_did_not_move_and_matches_the_live_run():
    """⚠⚠ THE REASON THE SEGMENT SUPPLIER IS A SEPARATE FILE, AS A MEASUREMENT.

    `formula_version()` is a sha256 of `core/census_structural.py`'s own source (`D-027`'s
    pattern): *a run persisted under a formula that has since changed is then detectable rather
    than silent.* `D-146`'s live read recorded `formula_version: c859da97f73d` on
    `census_structural_runs` id=1. Putting a display category in that file would have moved the
    value for a change that alters no arithmetic — **a detector that fires on a comment is a
    detector its readers learn to ignore.**
    """
    assert cs.formula_version() == "c859da97f73d"
    raw = (REPO / "core" / "census_structural.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(raw).hexdigest() == \
        "c859da97f73d9da2628a59dc091f7fbcbd8944d0eebba9096e6b011b62ba12c7"


def test_no_load_no_migration_and_no_loader_edit_ships_here():
    """⚠ Hard stops from the GO, as properties of the tree: no Fly `--load`, no schema change."""
    raw = (REPO / "scripts" / "census_structural_rank.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(raw).hexdigest() == \
        "ef222d19b2c15777ee65736bdc8f7b57b9ed65be990a1ae71a260dbbc7bbafe0", \
        "the loader moved — D-147 is a serve-time join, and persisting the flag is another entry"
    versions = REPO / "db" / "migrations" / "versions"
    assert sorted(p.name for p in versions.glob("00*.py"))[-1].startswith("0012"), \
        "D-147 adds no migration"
    # ⚠ and the loader does not learn the flag: `summarise`'s by_flag counts persisted flags only
    assert "census_segments" not in LOADER_SRC
    assert segs.FLAG_ECD_INTERMITTENT not in LOADER_SRC


def test_the_learned_cohort_82_scorer_is_not_reachable_from_the_segment_supplier():
    """⚠ `D-079` amendment 1 ruling 5's wall, extended to the new module rather than assumed of
    it: a census supplier may not import the learned scorer or its fitter."""
    for forbidden in ("core.scorer", "core scorer", "scripts.fit_scorer", "ranking_runs",
                      "target_scores", "ranking_results"):
        assert forbidden not in SEGMENTS_SRC, forbidden
    tree = ast.parse(SEGMENTS_SRC)
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    imported |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert imported <= {"__future__", "csv", "functools", "pathlib", "dataclasses", "typing",
                        "core.census_structural", "core.derived_freshness"}, sorted(imported)


# ─────────────────── 4. the honesty: two denials, by name ────────────────────


def test_the_flag_meaning_denies_score_composition_and_internalization(engine, tmp_path):
    """⚠⚠ THE TWO DENIALS THE GO ASKED FOR BY NAME, asserted individually. A copy pass that keeps
    the largest-segment sentence and drops *not internalisation* is exactly the plausible edit."""
    body = _payload(engine, tmp_path)
    meaning = _flat(body["formula"]["flag_meaning"][segs.FLAG_ECD_INTERMITTENT]).lower()
    assert "more than one segment" in meaning
    assert "multi-loop" in meaning
    assert "largest" in meaning and "not the extracellular total" in meaning
    assert "f-037" in meaning
    assert "does not enter structural_score" in meaning
    assert "min(1.0, span_aa / 200)" in meaning
    assert "not internalization" in meaning
    assert "never measured by this project for any protein" in meaning
    assert "no_accepted_segment" in meaning and "by design" in meaning


def test_the_excluded_factors_still_call_internalization_never_measured(engine, tmp_path):
    """⚠ The two sentences must stand in the SAME payload: *this flag is not internalization*, and
    *internalization was never measured*. Either alone lets the other be inferred away."""
    body = _payload(engine, tmp_path)
    excluded = {f["factor"]: f["why"] for f in body["formula"]["excluded_factors"]}
    assert list(excluded) == ["cancer", "normal_risk", "internalization", "density"]
    assert excluded["internalization"] == \
        "never measured by this project for any protein"
    block = body["segment_topology"]
    assert block["is_internalization"] is False
    assert "never measured" in _flat(block["not_internalization_note"])
    assert block["enters_score"] is False


def test_every_flag_that_can_reach_a_served_row_has_a_meaning_in_the_payload(engine, tmp_path):
    """⚠⚠ THE UNION, NOT EITHER HALF. Two suppliers now own flags, and a consumer must not have to
    know which module produced one in order to look up what it means."""
    body = _payload(engine, tmp_path)
    meanings = body["formula"]["flag_meaning"]
    seen = {f for row in body["rows"] for f in row["flags"]}
    assert seen, "the fixture must actually produce flags (A-017)"
    assert seen <= set(meanings), sorted(seen - set(meanings))
    assert set(meanings) == set(cs.FLAG_MEANING) | set(segs.FLAG_MEANING)
    assert all(str(v).strip() for v in meanings.values())


def test_the_method_note_paragraph_carries_the_denials_and_types_no_count():
    """⚠⚠ `D-050` / `D-051` **Constraint A**: a number on a surface is derived from a payload or it
    is not on the surface at all. No component fetches this route, so the paragraph names WHERE the
    count lives instead of typing it — and `### D-147` records that this reversed the entry's own
    first draft."""
    start = METHOD_NOTE.index('data-testid="census-structural-rank-addendum"')
    end = METHOD_NOTE.index('<h3 id="non-goals">', start)
    section = _flat(METHOD_NOTE[start:end])
    assert 'data-testid="census-structural-intermittent"' in section
    assert "largest single segment" in section
    assert "several separate segments" in section
    assert "does not change the score</strong>" in section
    assert "not internalisation</strong>" in section
    assert "GPI / no segment" in section and "by design" in section
    assert "component_counts.by_flag.ecd_intermittent" in section
    assert "D-147" in section
    # ⚠ no population-sized number is typed anywhere in the section (D-144's own guard, kept)
    assert not re.search(r"\b\d{1,3},\d{3}\b|\b\d{4,}\b", section)


def test_the_census_table_still_has_no_rank_column_and_no_ranking_table_shipped():
    """⚠⚠ THE BADGE THE GO CONDITIONED ON A TABLE THAT DOES NOT EXIST. `D-079` dec 1 as narrowed by
    `D-144` left *"no rank column on `/census`"* standing, and no component fetches the ranking
    route — so the honesty lands as `/method` prose and a badge would have had to ship a ranking
    table with it."""
    census_table = (REPO / "ui" / "src" / "components" / "CensusTable.jsx").read_text(
        encoding="utf-8")
    for barred in ("structural_score", "'rank'", '"rank"'):
        assert barred not in census_table, barred
    consumers = []
    for path in (REPO / "ui" / "src").rglob("*.js*"):
        if ".test." in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        if "census-structural-ranking" in text or "censusStructural" in text:
            consumers.append(str(path.relative_to(REPO / "ui" / "src")).replace("\\", "/"))
    assert sorted(consumers) == ["aboutPaper.js", "components/MethodNote.jsx",
                                 "system-model.json"], sorted(consumers)


# ───────────── 5. the absences: stale and absent are not `contiguous` ────────


def _stale_join(tmp_path: Path, *, stamp: str | None) -> segs.SegmentJoin:
    """A fixture derivation whose provenance names a manifest hash that is not the one on disk."""
    csv_path = tmp_path / "segments.csv"
    csv_path.write_text(
        "census_accession,span_aa,segment_count,extracellular_total_aa,discarded_aa,"
        "folded_fraction,topology,segments\n"
        "O75899,442,4,494,52,0.895,intermittent,42-483\n",
        encoding="utf-8")
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("census_accession,census_class,span_aa,tranche\nO75899,surface,442,5\n",
                        encoding="utf-8")
    if stamp is not None:
        (tmp_path / "segments.provenance.json").write_text(
            json.dumps({"source_manifest": manifest.name, "source_manifest_sha256": stamp}),
            encoding="utf-8")
    segs.segment_join.cache_clear()
    try:
        return segs.segment_join(path=str(csv_path), manifest=str(manifest))
    finally:
        segs.segment_join.cache_clear()


def test_a_stale_derivation_withholds_the_flag_rather_than_guessing(tmp_path):
    """⚠⚠ *A wrong topology is worse than a missing one, because a missing one is visible.* A
    derivation stamped against another manifest is DROPPED whole — not partially trusted, and
    never silently reported as `contiguous`."""
    join = _stale_join(tmp_path, stamp="0" * 64)
    assert join.verdict == "derivation_stale"
    assert join.facts == {}
    assert join.flags_for("O75899") == ()
    # ⚠ the row reports the VERDICT, not `unknown`: *nobody derived this* and *it was derived
    # against a different manifest* have different causes and different fixes
    assert join.topology_for("O75899") == "derivation_stale"


def test_an_unstamped_derivation_is_neither_fresh_nor_stale_and_still_flags_nothing(tmp_path):
    join = _stale_join(tmp_path, stamp=None)
    assert join.verdict == "derivation_absent"
    assert join.flags_for("O75899") == ()
    assert join.topology_for("O75899") == "derivation_absent"


def test_a_stale_derivation_is_reported_on_the_payload_and_flags_nothing(engine, tmp_path,
                                                                        monkeypatch):
    """⚠ `A-017`: the route must actually consult the join, so the stale verdict has to reach the
    payload rather than only the module."""
    _load(engine, tmp_path)
    stale = segs.SegmentJoin(verdict="derivation_stale",
                             note="derived from census_manifest.v7.csv @ deadbeef…, but the file "
                                  "on disk is @ cafebabe…",
                             facts={})
    monkeypatch.setattr(reader, "segment_join", lambda *a, **k: stale)
    body = _client(engine, tmp_path).get("/api/census-structural-ranking").json()
    block = body["segment_topology"]
    assert block["derivation_status"] == "derivation_stale"
    assert "RE-RUN" in block["derivation_note"] or "on disk is" in block["derivation_note"]
    assert block["served_by_flag_count"] == 0
    assert block["n_joined"] == 0
    assert block["by_topology"] == {"derivation_stale": 5}
    assert all(segs.FLAG_ECD_INTERMITTENT not in r["flags"] for r in body["rows"])
    assert all(r["topology"] == "derivation_stale" for r in body["rows"])
    assert all(r["segment_count"] is None for r in body["rows"])
    # ⚠⚠ AND THE SCORES ARE STILL THERE. A withheld topology must not withhold the rank.
    for row in body["rows"]:
        assert row["structural_score"] == pytest.approx(PINNED_SCORES[row["accession"]])


# ────────────────────────── the entry, and the ids ──────────────────────────


def _d147_entry() -> str:
    start = LOG.index("### D-147 —")
    return LOG[start:LOG.index("\n### D-146", start)]


def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠⚠ THE CHECK IS THE HEADING, NEVER A CITATION OF ONE (D-062 / method-note item 7). A commit
    message naming this decision does not discharge the living-documentation rule."""
    assert LOG.count("\n### D-147 —") == 1
    assert LOG.index("\n### D-147") < LOG.index("\n### D-146")
    assert re.search(r"^## Log \(newest first\)\s*\n\s*### D-147 —", LOG, re.M)


def test_the_entry_leads_with_the_disqualifying_fact_about_its_own_surface():
    lowered = _flat(_d147_entry()).replace("**", "").lower()
    head = lowered[:2600]
    assert "disqualifying fact" in head
    assert "rank 1" in head and "gabbr2" in head and "o75899" in head
    assert "intermittent" in head


def test_the_entry_records_the_measured_composition_and_the_join_it_rests_on():
    lowered = _flat(_d147_entry()).replace("**", "").lower()
    for claim in ("1,649", "1,693", "125", "3,467", "bijection",
                  "fd80d65df8b3acf59ce9faa135275dc75eac6caf7f4fc2a2cbc5399d3f970d07",
                  "92,709"):
        assert claim in lowered, claim
    assert "provenance (d-016)" in lowered


def test_the_entry_keeps_the_hard_stops_from_the_go():
    lowered = _flat(_d147_entry()).replace("**", "").lower()
    assert "structural_score` does not move" in lowered or \
        "structural_score does not move" in lowered
    assert "no migration runs" in lowered
    assert "no `--load` runs" in lowered or "no --load runs" in lowered
    assert "no adc-readiness claim" in lowered
    assert "is not collapsed into" in lowered
    assert "no formula" in lowered or "the formula gains no factor" in lowered


def test_the_entry_carries_a_deep_learning_justification_that_names_the_model():
    lowered = _flat(_d147_entry()).replace("**", "").lower()
    assert "deep-learning justification" in lowered
    assert "esmfold" in lowered and "plddt" in lowered and "score_model" in lowered
    assert "adds no deep learning" in lowered
    # ⚠ the half that makes it a justification rather than a citation: what the network was GIVEN
    assert "confident about" in lowered
    assert "epitope" in lowered


def test_the_entry_states_what_this_build_could_not_verify():
    lowered = _flat(_d147_entry()).replace("**", "").lower()
    assert "could not verify" in lowered
    assert "nothing here contacted fly" in lowered
    assert "internalis" in lowered or "internaliz" in lowered


def test_the_entry_records_the_reversed_decision_rather_than_rewriting_it():
    """⚠ `D-129-C`: a decision that quietly acquired the opposite content is a decision nobody can
    check. The MethodNote paragraph was drafted to name `1,649` and Constraint A forbade it."""
    lowered = _flat(_d147_entry()).replace("**", "").lower()
    assert "constraint a" in lowered
    assert "does not type" in lowered or "deliberately does not type" in lowered
    assert "d-129-c" in lowered


def test_the_next_free_integer_is_named_and_barred_across_every_guard():
    """⚠⚠ The TWELFTH pass through this resolution, and the FOURTH reserved integer SPENT rather
    than skipped (`D-142`, `D-145` and `D-146` were the first three, all the same day).

    **Bar OR name, never neither.** Every enumerated guard must NAME the entry that spent 147 and
    BAR the bare `### D-148`. The third state — an integer neither barred nor named — is how the
    #266/#267 collision got in.

    ⚠ The bar is matched WITH its newline (`\\n### D-148" not in`), because several of these files
    hold such patterns as *data* in order to check the others; a newline-less match would find a
    "bar" in the file whose job is to look for one. That is `D-145`'s recorded mistake.

    ⚠⚠ **AND THIS SUITE IS ITSELF ONE OF THE ENUMERATED GUARDS NOW**, added to
    `tests/test_d146_track_b_live_api_copy.py`'s list in the same commit — so it must NAME 146 as
    well as 147. That is the rule applied to the file that applies it, and it reddened on the first
    full run of this branch precisely because the rule was written before this file was.
    """
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     LOG, re.M), (
        "D-146 is the recorded predecessor id; it must be the Track B live-route copy entry, "
        "not some other entry that took the number"
    )
    assert "\n### D-148" not in LOG, (
        "D-148 is the next free integer and must stay unspent until an entry claims it by name "
        "— never admitted by a `>=`"
    )
    guards = (
        "tests/test_d129_phase5_named_refuse_spec.py",
        "tests/test_d130_residual_rmsd_spec.py",
        "tests/test_d136_cancer_type.py",
        "tests/test_d139_served_path_flip.py",
        "tests/test_d140_pipeline_programme.py",
        "tests/test_d141_land_confidence_kabsch.py",
        "tests/test_d143_track_b_structural_only.py",
        "tests/test_d144_census_structural_rank.py",
        "tests/test_d145_bake_structural_loader.py",
        "tests/test_d146_track_b_live_api_copy.py",
    )
    for rel in guards:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "D-147 — The census rank stops presenting a loop as an ectodomain" in text, (
            f"{rel} does not NAME the entry that spent 147"
        )
        assert r'\n### D-148" not in' in text, f"{rel} does not bar the next free integer"


def test_the_reserved_row_is_retired_marker_safe_and_148_has_a_row():
    """⚠⚠ MARKER-SAFE, and the reason is another suite rather than a style preference.

    `tests/test_d146_track_b_live_api_copy.py` locates the D-147 row with
    `re.search(r"^\\| \\*\\*D-147\\*\\*", …)`, so striking the marker to `~~**D-147**~~` — the
    convention `~~**D-143**~~` uses — would break that guard instead of satisfying it. The
    `D-142`, `D-145` and `D-146` rows record the same trap of themselves.
    """
    assert re.search(r"^\| \*\*D-147\*\*", RESERVED, re.M)
    assert "~~**D-147**~~" not in RESERVED
    row = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-147**"))
    assert "WRITTEN" in row
    assert "Original reservation text" in row
    assert re.search(r"^\| \*\*D-148\*\*", RESERVED, re.M), (
        "D-148 is cited in order to bar it, so it must be a RESERVED row or the citation "
        "invariant has a hole indistinguishable from D-062's"
    )
    assert "Next free `D-` integer: **`D-148`**" in RESERVED


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ `RESERVED.md`'s own command, run rather than quoted. **Read the output, not an exit
    code**: the only passing result is that nothing new is unresolved."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}"
    )


def test_the_architecture_doc_records_the_shipped_shape():
    assert "core/census_segments.py" in ARCH
    flat = _flat(ARCH)
    assert "ecd_intermittent" in flat
    assert "D-147" in flat
    assert "span_segments.csv" in flat


def test_the_test_plan_carries_the_d147_addendum_on_an_id_nobody_else_holds():
    """⚠ T-ids have collided four times here. The check is that this addendum's id appears in NO
    other addendum, not merely that a number was chosen."""
    plan = (REPO / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
    start = plan.index("### D-147 (this PR;")
    nxt = plan.index("## Addendum", start)
    mine, others = plan[start:nxt], plan[:start] + plan[nxt:]
    assert "(this PR; T-1254)" in mine
    assert "| **T-1254** |" in mine
    assert "| **T-1254** |" not in others
    assert "no test here contacts the deployed application" in _flat(mine).lower()
