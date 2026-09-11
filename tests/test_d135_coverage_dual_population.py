"""D-135 — two populations on /coverage, a bridge instead of a paragraph, and a Story with a way in.

⚠⚠ **The defects these pin, and how they are known (D-016).** Matt GO 2026-09-08 via Trinity,
tracker issue #258, read against `main` at tip ``ebd7b83`` (D-134):

  1. `/coverage` states the **D-024** partition over the Kathad-82 and says **nothing** about the
     census. A reader who arrives at *"the honest denominator"* learns the shape of 82 proteins and
     leaves believing that is the whole of the work.
  2. `CoverageView.coverageNote()` returned **209 characters** of two-population prose for IGF2R in a
     ``<td>``, between a tier and a fold status — correct, and unreadable. Meanwhile **D-134** has
     just made that accession's census representative visible as ``assembled`` for the first time, so
     the thing the paragraph gestured at is now a page with an address.
  3. The Story is eleven paragraphs with no contents, no summary strip, one CTA, and **no mention at
     all** of the hold-48 tiling arc that produced the assembled structures.

⚠⚠ **And the defect the FIX could introduce, which is why half of this file is absence assertions.**
The obvious remedy for (1) is a bigger number in the headline, and that is precisely the failure
**D-024** exists to forbid: a denominator that grows with how much work has happened. So the
Python-side guards come in pairs — the census breakdown must be on the wire, **and** it must be
impossible to mistake for coverage of the cohort. The two populations are cut under **different span
definitions** (**D-081**) and cannot be summed even in principle.

⚠⚠ **The sharpest guard in the file is an absence in the payload.** ``census_sibling`` carries no
``analysis_id``, deliberately: 75 of the 82 cohort accessions are also census rows
(``tests/test_no_census_leak_on_tranche_zero.py``, measured), and a census id on a cohort surface is
a **named stop condition** — the coverage row's own Target link would then open a fold measured under
the other span definition with nothing on screen saying so. **A field that is not served cannot be
rendered by mistake.**

⚠ Hermetic throughout: the real ``core/manifest.py`` over the committed cohort CSV (so the
denominator is genuinely 82) plus in-memory SQLite. No network, no Fly, no ops, no artifact read.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.reads import (
    CENSUS_SIBLING_KEY,
    COHORT_TRANCHE,
    STRUCTURE_KIND_LABEL,
    STRUCTURE_KIND_NONE,
    STRUCTURE_KIND_NOT_RECORDED_LABEL,
    STRUCTURE_KIND_ORDER,
    STRUCTURE_KINDS_WITH_A_FOLD,
    census_structure_kinds,
    census_summary,
    coverage_payload,
)
from db.models import Base, JobRecord, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (chr(10) * 2).join((ROOT / "docs" / n).read_text(encoding="utf-8")
                      for n in ("decisions.md", "findings.md", "assumptions.md", "README.md"))
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
READS = (ROOT / "app" / "reads.py").read_text(encoding="utf-8")
UI = ROOT / "ui" / "src"
# ⚠⚠ D-155: `/coverage` MERGED INTO `/targets` and `CoverageView.jsx` is gone. It listed the
# same 82 rows; the honest denominator, the per-row facts and the census strip all render on
# the merged surface now. These guards follow their subject — not one of D-135's clauses is
# dropped, and the two `<CoverageLine>` / `<CensusPopulationStrip>` order checks below are the
# same checks against the file that now renders them.
COVERAGE_VIEW = (UI / "components" / "TargetList.jsx").read_text(encoding="utf-8")
COVERAGE_NOTE = (UI / "components" / "coverageNote.jsx").read_text(encoding="utf-8")
COVERAGE_LINE = (UI / "components" / "CoverageLine.jsx").read_text(encoding="utf-8")
STRIP = (UI / "components" / "CensusPopulationStrip.jsx").read_text(encoding="utf-8")
STORY = (UI / "components" / "Story.jsx").read_text(encoding="utf-8")
CENSUS_VIEW = (UI / "components" / "CensusView.jsx").read_text(encoding="utf-8")
CENSUS_TABLE = (UI / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
KINDS = (UI / "structureKinds.js").read_text(encoding="utf-8")

# IGF2R — the case the bridge exists for. Attempted in the cohort at tranche 0, died of CUDA OOM,
# and its census representative is an assembled parent (D-134's 45).
IGF2R = "P11717"
# HER2 — in BOTH populations and FOLDED in the cohort, on rental. The bridge must stay off it.
ERBB2 = "P04626"
# FAT2 — a named D-022 exclusion whose census representative is TILES, i.e. not a protein (D-118).
FAT2 = "Q9NYQ8"


def _plain(text: str) -> str:
    """⚠ Markdown emphasis stripped as well as whitespace: the log writes ``**Not** F-004`` and a
    substring check for ``not f-004`` would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


@pytest.fixture
def engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _census(session, *, id, acc, kind, pdb=None, plddt=None, parent_job_id=None, tile_start=None):
    """One census row (tranche 5). ``kind`` is the ``hold48_kind`` meta tag ops writes."""
    meta = {"span_aa": 2368}
    if kind is not None:
        meta["hold48_kind"] = kind
    if parent_job_id is not None:
        meta["parent_job_id"] = parent_job_id
        meta["tile_start"] = tile_start
        meta["tile_end"] = (tile_start or 1) + 1655
    session.add(ProteinAnalysis(
        id=id, input_type="uniprot", input_value=acc, cohort_tranche=5,
        pdb_path=pdb, mean_plddt=plddt, meta=meta,
    ))


def _cohort_failed(session, *, id, acc, error):
    """A cohort shell row plus a failed job — D-043's ``failed``, distinct from never-attempted."""
    pa = ProteinAnalysis(id=id, input_type="uniprot", input_value=acc,
                         cohort_tranche=COHORT_TRANCHE, structure_source="esmfold",
                         pdb_path=None, mean_plddt=None, meta={"gene": "SEED"})
    session.add(pa)
    session.flush()
    session.add(JobRecord(analysis_id=pa.id, status="failed", error=error, inference_settings={}))


def _cohort_folded(session, *, id, acc):
    session.add(ProteinAnalysis(
        id=id, input_type="uniprot", input_value=acc, cohort_tranche=COHORT_TRANCHE,
        structure_source="esmfold", mean_plddt=77.26,
        pdb_path=f"/data/artifacts/{id}/structure.pdb", meta={"gene": "SEED"},
    ))


def _seeded(engine):
    """The three interesting shapes at once: IGF2R failed here + assembled there, HER2 folded here
    + a census row too, FAT2 with tiles only."""
    with Session(engine) as s:
        _cohort_failed(s, id=57, acc=IGF2R, error="CUDA out of memory. Tried to allocate 2.00 GiB")
        _census(s, id=3356, acc=IGF2R, kind="parent_stitched",
                pdb="/data/artifacts/3356/structure.pdb", plddt=61.07)
        _cohort_folded(s, id=61, acc=ERBB2)
        _census(s, id=3400, acc=ERBB2, kind=None, pdb="/data/artifacts/3400/structure.pdb",
                plddt=70.2)
        _census(s, id=3500, acc=FAT2, kind="parent")
        _census(s, id=3501, acc=FAT2, kind="tile", pdb="/data/artifacts/3501/structure.pdb",
                plddt=55.0, parent_job_id=3500, tile_start=1)
        s.commit()
    return engine


def _row(payload, accession):
    return next(r for r in payload["rows"] if r["accession"] == accession)


# ───────────────────────── the per-kind breakdown on the summary ─────────────────────────


def test_the_breakdown_counts_kinds_present_and_omits_the_ones_absent():
    """⚠⚠ A kind with no rows gets NO entry, and that is the whole rule. ``assembled 0`` is exactly
    what the census truthfully reported for all 45 assembled parents before **D-134** repaired the
    identity check — a rendering no reader could tell from a finding.

    Prove it bites by emitting every kind in ``STRUCTURE_KIND_ORDER`` with a default of 0."""
    got = census_structure_kinds([
        {"structure_kind": "single-pass", "structure_kind_label": "single-pass"},
        {"structure_kind": "assembled", "structure_kind_label": "assembled (provisional)"},
        {"structure_kind": "assembled", "structure_kind_label": "assembled (provisional)"},
    ])
    assert got == [
        {"kind": "assembled", "label": "assembled (provisional)", "n": 2},
        {"kind": "single-pass", "label": "single-pass", "n": 1},
    ]
    assert [k["kind"] for k in got] == ["assembled", "single-pass"]
    assert "tiles_only" not in {k["kind"] for k in got}
    assert "mucin" not in {k["kind"] for k in got}


def test_a_row_with_no_kind_is_counted_as_a_stated_absence():
    """⚠ A missing ``structure_kind`` is a MISSING FIELD, never an implied single pass (D-133). It
    gets its own bucket with its own label rather than being dropped or folded into `single-pass`."""
    got = census_structure_kinds([
        {"structure_kind": None, "structure_kind_label": None},
        {"structure_kind": "single-pass", "structure_kind_label": "single-pass"},
    ])
    assert {"kind": STRUCTURE_KIND_NONE, "label": STRUCTURE_KIND_NOT_RECORDED_LABEL, "n": 1} in got
    assert STRUCTURE_KIND_NOT_RECORDED_LABEL == "not recorded"
    # ⚠ and it does not inflate the single-pass count, which is the failure the label exists for
    assert next(k for k in got if k["kind"] == "single-pass")["n"] == 1


def test_the_label_is_the_api_s_own_and_never_a_second_spelling():
    """⚠ The surface reads these labels straight through, so a second spelling here would let the
    strip name a category differently from the census column it links to."""
    got = census_structure_kinds([
        {"structure_kind": k, "structure_kind_label": v} for k, v in STRUCTURE_KIND_LABEL.items()
    ])
    assert {k["kind"]: k["label"] for k in got} == STRUCTURE_KIND_LABEL
    assert STRUCTURE_KIND_LABEL["assembled"] == "assembled (provisional)"


def test_the_order_ships_in_the_payload_and_is_not_a_ranking():
    """⚠⚠ THE ORDER IS SERVED so no component has to type a list of categories to iterate — a
    surface that decides which kinds exist stops showing one the census acquires later, which is
    Constraint A's neighbouring failure and much harder to see than a hardcoded count.

    ⚠ It is not a ranking and there is nothing here to rank (D-079 dec 1): the two folded kinds come
    first because they are what a reader came for, then the two absences, then the unrecorded rows."""
    assert STRUCTURE_KIND_ORDER == ("assembled", "single-pass", "tiles_only", "mucin", "none")
    # ⚠ every label key has a place in the order, or a real census kind would be silently dropped
    assert set(STRUCTURE_KIND_LABEL) | {STRUCTURE_KIND_NONE} == set(STRUCTURE_KIND_ORDER)
    # ⚠ the UI mirrors it rather than inventing a second order
    assert "const KIND_ORDER = ['assembled', 'single-pass', 'tiles_only', 'mucin', 'none']" in KINDS
    # ⚠ and the census table re-exports rather than keeping a private copy
    assert "export { KIND_ORDER }" in CENSUS_TABLE


def test_the_summary_serves_the_breakdown_beside_its_totals(engine):
    """⚠ Measured as a DELTA against the empty engine, not as an absolute. ``list_census`` also
    appends the never-folded manifest rows (``core/census_unfolded.py`` — the 3 mucins plus several
    hundred carrying no kind at all), which is exactly right and would make an absolute expectation
    a pin on the committed manifest rather than on this function.

    ⚠ And the breakdown must cover **every** row the totals cover: the ``none`` bucket is what keeps
    the two from silently describing different populations."""
    def kinds_of(eng):
        return {k["kind"]: k["n"] for k in census_summary(eng)["structure_kinds"]}

    before = kinds_of(engine)
    before_summary = census_summary(engine)
    with Session(engine) as s:
        _census(s, id=1, acc="Q00001", kind="parent_stitched",
                pdb="/data/artifacts/1/structure.pdb", plddt=61.0)
        _census(s, id=2, acc="Q00002", kind=None, pdb="/data/artifacts/2/structure.pdb", plddt=70.0)
        _census(s, id=3, acc="Q00003", kind="mucin")
        s.commit()
    after = kinds_of(engine)
    summary = census_summary(engine)
    for kind, added in (("assembled", 1), ("single-pass", 1), ("mucin", 1)):
        assert after.get(kind, 0) - before.get(kind, 0) == added, kind
    # ⚠ the totals moved by the two rows with a structure, and the breakdown accounts for ALL rows
    assert summary["folded"] - before_summary["folded"] == 2
    assert sum(after.values()) == summary["manifest_rows"], (
        "the per-kind breakdown must partition the same rows `manifest_rows` counts")


def test_the_breakdown_reduces_the_same_rows_as_the_totals():
    """⚠⚠ ONE DEFINITION OF WHAT A CENSUS ROW IS. A second query with its own `where` is how two
    surfaces come to disagree about one population, and this project has an entry for that. The
    existing route guard already forbids `select` inside `census_summary`; this asserts the new
    field is reduced from the same `rows` local rather than re-fetched."""
    fn = next(n for n in ast.walk(ast.parse(READS))
              if isinstance(n, ast.FunctionDef) and n.name == "census_summary")
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
    names = [n.func.id for n in calls if isinstance(n.func, ast.Name)]
    assert "list_census" in names
    assert names.count("list_census") == 1, "the summary must build the row list exactly once"
    assert "census_structure_kinds" in names
    breakdown = next(n for n in calls
                     if isinstance(n.func, ast.Name) and n.func.id == "census_structure_kinds")
    assert [a.id for a in breakdown.args if isinstance(a, ast.Name)] == ["rows"], (
        "the breakdown must reduce the rows the summary already has, not fetch its own")
    assert "select" not in ast.dump(fn)


def test_the_breakdown_states_its_key_and_disowns_the_cohort_denominator(engine):
    """⚠ Every count states its key (D-016), and this one has to say the two things a reader would
    otherwise assume: that these are census ROWS rather than D-132's 45 assembled parent JOBS, and
    that the population shares no denominator with /api/coverage."""
    key = _plain(census_summary(engine)["keys"]["structure_kinds"])
    assert "census rows" in key
    assert "45 assembled parent jobs" in key
    assert "d-081" in key
    assert "no denominator in common with /api/coverage" in key


# ───────────────────────────── the cohort → census bridge ─────────────────────────────


def test_a_failed_cohort_row_names_its_assembled_census_sibling(engine):
    """⚠⚠ THE IGF2R CASE. Attempted in the cohort and dead of CUDA OOM; a tiled assembly of the same
    accession exists in the census. Two measurements of one protein by one model, and until now the
    coverage table could describe only one of them."""
    payload = coverage_payload(_seeded(engine))
    row = _row(payload, IGF2R)
    assert row["fold_status"] == "failed", "the cohort attempt failed and still does"
    sib = row["census_sibling"]
    assert sib["structure_kind"] == "assembled"
    assert sib["structure_kind_label"] == "assembled (provisional)"
    assert sib["folded"] is True
    assert "seam not solved" in sib["assembler_note"]


def test_the_bridge_never_carries_a_census_analysis_id(engine):
    """⚠⚠ THE NAMED STOP CONDITION, AS AN ABSENCE IN THE PAYLOAD. 75 of the 82 cohort accessions are
    also census rows; a census id under a coverage row is one careless render from putting a fold
    measured under a different span definition (D-081) behind the cohort's own Target link. The link
    is built from the ACCESSION, which /api/census/{id} has resolved since D-118.

    Prove it bites by adding ``"analysis_id": row.id`` to the sibling dict."""
    payload = coverage_payload(_seeded(engine))
    for row in payload["rows"]:
        sib = row.get("census_sibling")
        if sib is None:
            continue
        assert "analysis_id" not in sib, "a census id must never travel on a cohort row"
        assert "id" not in sib
        # ⚠ `not isinstance(v, bool)` because `bool` IS an `int` in Python and `folded` is a flag,
        # not an id. The claim is that no NUMBER rides here — a flag cannot be put in a URL path.
        assert not any(isinstance(v, int) and not isinstance(v, bool) for v in sib.values()), (
            f"a number on the sibling is an id waiting to be linked: {sib}")


def test_the_cohort_row_s_own_analysis_id_is_still_the_cohort_s(engine):
    """⚠⚠ The other half of the same guarantee, and the sharper half. HER2 folded in the cohort, so
    its row carries the COHORT's id (61) and never the census row's (3400) — the leak
    ``tests/test_no_census_leak_on_tranche_zero.py`` was written about. IGF2R did not fold here at
    all, so its ``analysis_id`` stays **None**: an unfolded row has no target page, and the census
    parent's 3356 must not arrive to fill the gap.

    Prove it bites by dropping the tranche filter from ``_folded_accessions``."""
    payload = coverage_payload(_seeded(engine))
    igf2r = _row(payload, IGF2R)
    assert igf2r["analysis_id"] is None, "a failed cohort row has no cohort fold to open"
    assert igf2r["census_sibling"]["structure_kind"] == "assembled", "…and yet the census one exists"
    assert _row(payload, ERBB2)["analysis_id"] == 61
    # ⚠ no census id appears anywhere on any coverage row, under any key — walked rather than
    # spot-checked, because the field that leaks one next will not be `analysis_id`.
    census_ids = {3356, 3400, 3500, 3501}

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, (list, tuple)):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
        elif isinstance(node, int) and not isinstance(node, bool):
            assert node not in census_ids, f"census id {node} reached coverage at {path}"

    for row in payload["rows"]:
        walk(row, row["accession"])


def test_a_cohort_row_that_folded_here_gets_no_bridge(engine):
    """⚠ HER2 is in both populations and folded in the cohort. Where the cohort has its own
    measurement the census is not the interesting fact, and a note on sixty-odd rows is noise."""
    payload = coverage_payload(_seeded(engine))
    row = _row(payload, ERBB2)
    assert row["fold_status"] == "folded"
    assert "census_sibling" not in row


def test_a_tiles_only_sibling_is_served_as_not_folded(engine):
    """⚠⚠ A TILE IS A WINDOW, NOT A PROTEIN (D-118). FAT2's census representative is the tiles-only
    parent, so the sibling exists but says ``folded: False`` — and the surface reads that flag rather
    than re-deriving which kinds count as a structure, which is how a second definition of "folded"
    would drift away from the census page it links to."""
    payload = coverage_payload(_seeded(engine))
    sib = _row(payload, FAT2)["census_sibling"]
    assert sib["structure_kind"] == "tiles_only"
    assert sib["folded"] is False
    assert sib["assembler_note"] is None
    assert STRUCTURE_KINDS_WITH_A_FOLD == frozenset({"assembled", "single-pass"})


def test_the_bridge_does_not_touch_the_coverage_object_or_the_fold_vocabulary(engine):
    """⚠⚠ D-024's invariant, and D-043's three values. The census may not enter either.

    Prove it bites by counting a census sibling into ``coverage`` or by inventing a fourth
    ``fold_status`` such as ``folded_elsewhere``."""
    payload = coverage_payload(_seeded(engine))
    cov = payload["coverage"]
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == cov["denominator"]
    assert cov["denominator"] == 82, "the denominator is the manifest's, and it does not move"
    assert set(r["fold_status"] for r in payload["rows"]) <= {"folded", "failed", "not_folded"}
    # ⚠ and no census count leaked into the coverage object under any name
    assert set(cov) == {"denominator", "ranked", "held_out", "excluded", "unmeasured_tier",
                        "no_topology"}


def test_the_payload_names_the_population_the_bridge_belongs_to(engine):
    """⚠ D-016 on the wire. A JSON consumer that finds ``structure_kind: "assembled"`` on a coverage
    row and no statement of which population it describes will read it as the cohort's own fold."""
    assert CENSUS_SIBLING_KEY["kind"] == "CROSS_POPULATION_FACT"
    text = _plain(CENSUS_SIBLING_KEY["text"])
    assert "did not fold here" in text
    assert "d-081" in text
    assert "never the cohort's own fold" in text
    assert "no analysis_id" in text
    assert "by accession" in text
    assert coverage_payload(_seeded(engine))["census_sibling_key"] == CENSUS_SIBLING_KEY


def test_the_sibling_read_is_tranche_filtered_and_uses_the_shared_representative_rule():
    """⚠⚠ THE CLASS GUARD, ONE FUNCTION ALONG (see tests/test_no_census_leak_on_tranche_zero.py).
    The census filter is the POSITIVE form, and the representative comes from the same function
    ``list_census`` and ``resolve_census_accession`` use — so this cannot come to disagree with the
    census page it points at."""
    fn = next(n for n in ast.walk(ast.parse(READS))
              if isinstance(n, ast.FunctionDef) and n.name == "_attach_census_sibling")
    src = ast.dump(fn)
    assert "cohort_tranche" in src
    assert "choose_census_representative" in src
    assert "is_census_tile_row" in src, "a tile must be refused as a representative (D-118)"
    # ⚠ and nothing here writes: the whole PR is read-path
    for banned in ("session.add", "session.commit", "session.merge", "update("):
        assert banned not in ast.unparse(fn), banned


def test_a_broken_census_read_costs_the_note_and_not_the_row():
    """⚠ ADDITIVE. /coverage exists to serve the honest denominator; the bridge is a bonus on it, so
    a failure in the census read must leave the rows exactly as they arrived.

    ⚠ The attachment is exercised DIRECTLY rather than through ``coverage_payload`` with a
    counting fake engine. The counting version passed, and it would have kept passing while
    measuring the wrong session: a later refactor that opens one more session before this one would
    make the fake break an EARLIER read, and the test would go green on a case it was not written
    for. Calling the function is the check.

    Prove it bites by removing the ``except`` around the scoped query."""
    class _Down:
        def connect(self, *args, **kwargs):
            raise RuntimeError("census read is down")

    rows = [{"accession": IGF2R, "fold_status": "failed"},
            {"accession": FAT2, "fold_status": "not_folded"}]
    from app.reads import _attach_census_sibling
    _attach_census_sibling(_Down(), rows)                 # must not raise
    assert all("census_sibling" not in r for r in rows)
    assert rows == [{"accession": IGF2R, "fold_status": "failed"},
                    {"accession": FAT2, "fold_status": "not_folded"}]


def test_the_whole_coverage_page_survives_a_census_with_nothing_in_it(engine):
    """⚠ The empty case is not the error case, and both must render. A census holding no row for any
    cohort accession attaches nothing and leaves all 82 rows intact."""
    payload = coverage_payload(engine)
    assert payload["coverage"]["denominator"] == 82
    assert len(payload["rows"]) == 82
    assert all("census_sibling" not in r for r in payload["rows"])


# ─────────────────────────────── the surfaces, read as source ───────────────────────────────


def test_the_coverage_headline_is_not_given_the_census_summary():
    """⚠⚠ THE LOAD-BEARING SOURCE ASSERTION OF THE WHOLE PR. ``CoverageLine`` computes the D-024
    intersection from the cohort payload and must never be handed the census summary — a census
    count in that sentence is the self-flattering denominator D-024 forbids, and the component test
    (`CoverageView.dual.test.jsx`) asserts the rendered half.

    Prove it bites by threading ``census`` into the ``<CoverageLine>`` element."""
    element = COVERAGE_VIEW[COVERAGE_VIEW.index("<CoverageLine"):]
    element = element[: element.index("/>") + 2]
    # ⚠ D-155: the merged surface holds the coverage OBJECT and the joined rows in its own
    # state (`coverageObj` / `all`) rather than a single `data` payload. The claim is unchanged
    # and is the one that matters — the cohort partition in, the census nowhere near it.
    assert "coverage={coverageObj}" in element
    assert "rows={all}" in element
    assert "census" not in element, "CoverageLine takes the cohort payload and only the cohort payload"
    # ⚠ and the component itself still knows nothing about the census
    for banned in ("census", "structure_kind", "manifest_rows"):
        assert banned not in COVERAGE_LINE, f"CoverageLine must not learn about `{banned}`"


def test_the_second_strip_is_a_sibling_of_the_coverage_line_not_a_part_of_it():
    """⚠ Rendered after it, at the same level. A census figure inside ``.coverage-line`` would be one
    CSS change from reading as part of the headline."""
    line = COVERAGE_VIEW.index("<CoverageLine")
    strip = COVERAGE_VIEW.index("<CensusPopulationStrip")
    assert line < strip
    assert "<CensusPopulationStrip summary={census} />" in COVERAGE_VIEW
    # ⚠ D-155: and the per-row bridge kept its rule when it moved into its own module — a
    # census id may never travel on a cohort row, so the link is built from the ACCESSION.
    assert "to={`/census/${r.accession}`}" in COVERAGE_NOTE
    # ⚠⚠ COMMENTS STRIPPED FIRST — `F-024`, match the thing you mean. That module EXPLAINS at
    # length why no census id may travel on a cohort row, so a substring check over the raw
    # source fires on the file's own reasoning about itself. It did, on the first run of this.
    code = re.sub(r"//[^\n]*", "", COVERAGE_NOTE)
    assert "analysis_id" not in code, (
        "the bridge learned about a census analysis id — the named stop condition")


def test_the_strip_labels_the_population_before_it_prints_a_count():
    """⚠ A reader who stops after the first number must already have met the population — the same
    rule that puts /census's "not scored" bar above its own figures."""
    plain = _plain(STRIP)
    assert "a different population" in plain
    assert "not more of the cohort" in plain
    assert "do not extend the denominator" in plain
    assert "different span definition" in plain
    assert "not scored and not ranked" in plain
    # ⚠ the label comes first in the source, which is the render order
    assert plain.index("a different population") < plain.index("proteins in the census")


def test_the_strip_types_no_count_and_no_kind_list():
    """⚠⚠ CONSTRAINT A (D-050 / D-051), and its neighbour. No figure is typed — and no LIST OF KINDS
    is typed either, because a component that decides which categories exist quietly stops showing
    one the census acquires later. The strip iterates the payload's own order."""
    assert "summary.structure_kinds" in STRIP
    assert "kinds.map" in STRIP
    assert "KIND_ORDER" not in STRIP, "the strip iterates the payload, not a list of its own"
    body = STRIP[STRIP.index("return ("):]
    body = re.sub(r"\{/\*.*?\*/\}", "", body, flags=re.S)      # decision ids live in the comments
    # ⚠ `.length > 0` is a presence test, not a count — it asks whether there is anything to draw
    # and never reaches the page. Removed before the scan, and named rather than tolerated silently.
    body = re.sub(r"\.length\s*[<>=!]+\s*\d+", ".length", body)
    digits = re.findall(r"(?<![\w-])\d[\d,]*(?![\w])", body)
    assert digits == [], f"a typed number in the strip: {digits}"


def test_the_strip_carries_the_assembler_caveat_wherever_it_links_to_assemblies():
    """⚠ D-133 am. 1's rule, one surface along: the caveat arrives with the act. Pointing a reader at
    the assemblies from the honesty page without saying what an assembly is would spend this page's
    credibility overstating them."""
    plain = _plain(STRIP)
    assert "assembled is provisional" in plain
    assert "not superimposed" in plain
    assert "recorded, not solved" in plain
    assert "not in the ranking" in plain
    assert "/census?structure=" in STRIP


def test_the_census_url_filter_defaults_to_all_and_falls_closed():
    """⚠⚠ TWO RULES IN ONE PLACE. Absent → ``all`` is D-102's bar (a page must not arrive having
    chosen). Unrecognised → ``all`` is a different argument: an empty table under a chip nobody
    pressed reads as *"the census holds none of these"*, which is a much stronger claim than *"that
    word is not a category here"*.

    Prove it bites by returning ``requested`` unconditionally from ``resolveKind``."""
    assert "export function resolveKind" in KINDS
    assert "if (!requested || requested === 'all') return 'all'" in KINDS
    assert "present.some((k) => k.key === requested) ? requested : 'all'" in KINDS
    # ⚠ resolved where the ROWS are, because the caller does not have them when the URL is read
    assert "resolveKind(controlledKind ?? ownKind, kinds)" in CENSUS_TABLE
    # ⚠ and `?structure=all` is never written into an address a reader may share
    assert "if (key === 'all') next.delete('structure')" in CENSUS_VIEW
    assert "useSearchParams" in CENSUS_VIEW


def test_the_census_table_stays_usable_without_a_router():
    """⚠ The controlled pair is OPTIONAL. A component that only works inside a URL has a hidden
    dependency, and this table is rendered on its own wherever a caller holds rows."""
    assert "kindFilter: controlledKind, onKindFilter" in CENSUS_TABLE
    assert "controlledKind ?? ownKind" in CENSUS_TABLE
    assert "onKindFilter?.(key)" in CENSUS_TABLE


def test_the_story_derives_every_cold_strip_figure():
    """⚠ Constraint A on the most-read screen on the site. The cohort figure uses the same
    ``ranked ∧ folded`` rule as ``CoverageLine`` — not the folded total, which D-024 forbids — and
    the assembled figure is read out of the payload's own breakdown."""
    assert "rankedFolded: rows.filter((r) => r.disposition === 'ranked' && r.fold_status === 'folded')" in STORY
    assert "(census?.structure_kinds ?? []).find((k) => k.kind === 'assembled')?.n ?? null" in STORY
    strip = STORY[STORY.index("story-cold-strip"):]
    strip = strip[: strip.index("</dl>")]
    assert "{s.rankedFolded}" in strip
    assert "{s.census.folded.toLocaleString()}" in strip
    assert "{s.assembled.toLocaleString()}" in strip
    # ⚠ `null` rather than 0 when the payload holds no assembled kind: a zero would read as a
    # finding, and it is what the census showed for all 45 parents before D-134.
    assert "s.assembled != null &&" in strip


def test_the_story_beats_and_its_contents_come_off_one_list():
    """⚠⚠ AN ANCHOR WITH NO TARGET IS A SILENT DEFECT. Two hand-written lists — links here, ids
    there — drift the moment a section is renamed, and nothing renders red."""
    beats = STORY[STORY.index("const BEATS = ["):]
    beats = beats[: beats.index("]")]
    ids = re.findall(r"id: '([a-z0-9-]+)'", beats)
    assert ids == ["beat-cohort", "beat-census", "beat-hold48", "beat-scorer", "beat-open"]
    for beat_id in ids:
        assert f'<section id="{beat_id}">' in STORY, f"no section for {beat_id}"
    assert 'href={`#${b.id}`}' in STORY, "the contents links must be generated from the same list"
    # ⚠ a beat that did not render must leave the contents too
    assert "BEATS.filter((b) => !b.needsCensus || s?.census)" in STORY


def test_the_story_hold48_beat_states_every_hedge_the_arc_earned():
    """⚠⚠ SIX DECISIONS' WORTH OF CAUTION, AND NONE OF IT OPTIONAL. Drop any one clause and this beat
    becomes the overstatement the whole hold-48 arc has spent six decisions refusing to make.

    Prove each bites by deleting the clause: provisional (D-133 / D-134), not superimposed and not
    the whole span (D-118 / D-121), did not repair most seams (D-127 / D-128 OPS), recorded not
    solved (D-129 accept-refuse), closed (D-118), not in the ranking (D-109 ruling 7)."""
    beat = STORY[STORY.index('<section id="beat-hold48">'):]
    beat = beat[: beat.index("</section>")]
    plain = _plain(beat)
    for clause in (
        "too long to fold in one go",
        "overlapping tiles",
        "not the same thing as folding the whole span",
        "recorded, not solved",
        "did not repair most of the seams",
        "provisional",
        "how the structure was made, never how good it is",
        "not in the ranking",
        "closed",
    ):
        assert clause in plain, f"the hold-48 beat dropped: {clause}"
    # ⚠ and it never claims the thing the arc refuses to claim
    assert not re.search(r"seams? (are|were) (now )?(solved|fixed|repaired)", plain)
    # ⚠ Constraint A: no count is written into this copy
    rendered = re.sub(r"\{/\*.*?\*/\}", "", beat, flags=re.S)
    assert not re.search(r"(?<![\w-])\d", rendered), "a typed number in the tiling copy"


def test_the_story_cta_offers_both_populations_without_preferring_one():
    cta = STORY[STORY.index('className="story-cta"'):]
    cta = cta[: cta.index("</p>")]
    assert '<Link to="/targets">' in cta
    assert '<Link to="/census?structure=assembled">' in cta
    assert not re.search(r"best|recommend|start here|instead", cta, re.I)


# ───────────────────────────── the living documentation ─────────────────────────────


def _d135_entry() -> str:
    """The D-135 entry only — the log is 24k lines and a substring match anywhere in it proves
    nothing about the entry that is supposed to carry the claim.

    ⚠ **Anchored at a line start (D-136 amendment 1).** The unanchored ``LOG.index("### D-135")``
    this replaces also matched the id written *inside another entry's prose* — D-136 cited this
    heading as evidence the integer was unspent, and because D-136 sits above D-135 in a
    newest-first log, three assertions below silently began reading D-136's text. An entry can
    break a neighbour's test by describing it accurately; the fix is to require the heading to
    start its own line.
    """
    start = re.search(r"^### D-135", LOG, re.M).start()
    return LOG[start: LOG.index("\n### ", start + 1)]


def test_the_decision_entry_exists_and_is_the_one_named():
    """⚠⚠ METHOD-NOTE ITEM 7: THE CHECK IS THE ENTRY, NOT THE REFERENCE TO IT. A commit message
    naming D-135 does not discharge the living-documentation rule — PR #90 shipped a surface whose
    decision entry was never written, and thirteen later citations treated it as settled authority.

    Prove it bites by deleting the entry and leaving every citation of it in place."""
    assert re.search(r"^### D-135 — Coverage gains a SECOND population", LOG, re.M)
    assert len(re.findall(r"^### D-135", LOG, re.M)) == 1, "exactly one D-135 entry"


def test_the_entry_records_the_no_id_decision_and_the_headline_guarantee():
    entry = _plain(_d135_entry())
    assert "the headline does not move" in entry
    assert "a census count may never enter that sentence" in entry
    assert "carries no analysis_id" in entry
    assert "an id that is not in the payload cannot be rendered by mistake" in entry
    assert "falls closed to all" in entry


def test_the_entry_keeps_the_out_of_scope_list_closed():
    """⚠ The Spec's out-list is not the PR's to re-open, and an entry that quietly drops one of these
    is how a scope grows between a GO and a merge."""
    entry = _plain(_d135_entry())
    for phrase in ("no new route", "no ops", "no rent", "no emit", "no fly write", "no migration",
                   "no f-004 ingest", "no kabsch flip", "no rmsd-v2",
                   "no promotion of assembled out of provisional", "rental stays closed"):
        assert phrase in entry, f"the D-135 entry dropped: {phrase}"
    assert "not a second denominator" in entry
    assert "stop and ask the architect" in entry


def test_the_entry_carries_a_deep_learning_justification():
    """⚠ ARCHITECTURE §1 / CLAUDE.md: every substantive decision states how it serves the DL core."""
    entry = _d135_entry()
    assert "**Deep-learning justification.**" in entry
    plain = _plain(entry)
    assert "esmfold" in plain
    assert "per-residue confidence" in plain


def test_architecture_records_the_shipped_shape():
    """⚠ ARCHITECTURE.md is the single source of truth for system shape and must be current before
    the PR is filed (CLAUDE.md rule 2). A stale architecture doc means the PR is incomplete."""
    assert "D-135" in ARCH
    plain = _plain(ARCH)
    assert "coverage dual population + story consumability" in plain
    assert "structure_kinds" in plain
    assert "census_sibling" in plain
    assert "the sibling deliberately carries no analysis_id" in plain
    assert "?structure=" in ARCH
    # ⚠ the row names its own tests, so a reader can find what pins it
    assert "test_d135_coverage_dual_population.py" in ARCH
    assert "CoverageView.dual.test.jsx" in ARCH
    assert "Story.d135.test.jsx" in ARCH
    assert "CensusView.structureurl.test.jsx" in ARCH


def test_the_component_tests_exist_beside_the_python_ones():
    """⚠ A surface asserted only in Python is a surface no render ever exercised. The Python guards
    above read source text; these three actually mount the components."""
    # ⚠ D-155: renamed with the component it mounts — the file moved from `/coverage` to
    # `/targets` and every one of its 21 cases came with it.
    for name in ("TargetList.dual.test.jsx", "CensusView.structureurl.test.jsx",
                 "Story.d135.test.jsx"):
        path = UI / "components" / name
        assert path.exists(), f"{name} must ship with the surface it pins"
        assert "D-135" in path.read_text(encoding="utf-8")
