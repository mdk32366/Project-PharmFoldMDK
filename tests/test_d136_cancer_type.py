"""D-136 — the ADC Approved Cancer type column, and the guards that make it a finding.

Hermetic: the committed file plus tmp fixtures. No network. The live openFDA SPL
queries dated ``data/adcs/adcs.v1.json`` on 2026-09-08; they are not this suite
(D-029: a live FDA call must not redden the gate).

The two tests this suite exists for:

* :func:`test_a_tumour_type_absent_from_the_label_text_is_refused` — a category
  typed from memory reddens, because a word FDA's stored text does not contain
  cannot pass a substring test. This is what makes D-122's *"do not type PADCEV
  → urothelial from memory"* mechanical.
* :func:`test_an_hpa_staining_source_is_refused` — an HPA / staining / census
  join reddens, naming D-093.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from core.adc_catalog import (
    CANCER_TYPE_CONFIDENCES,
    CATALOG_V1,
    FIELD_KEYS,
    INDICATION_AUTHORITIES,
    PIPELINE_CANCER_TYPE_CONFIDENCES,
    PIPELINE_FIELDS,
    STAINING_SOURCE_TOKENS,
    CatalogError,
    load_catalog,
    load_pipeline,
)
from tests.test_adc_catalog import (
    FIXTURE_LABEL_SOURCE,
    FIXTURE_LABEL_TEXT,
    _envelope,
    _minimal_catalog,
    _minimal_row,
    _write,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS_README = ROOT / "docs" / "README.md"


def _normalise(text):
    """The loader's own normalisation, restated so the test does not inherit a bug."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


# ---------------------------------------------------------------- committed file


def test_every_approved_row_carries_both_indication_envelopes():
    for row in load_catalog()["adcs"]:
        brand = row["brand_name"]["value"]
        for name in ("cancer_type", "label_indications_verbatim"):
            assert set(row[name]) == set(FIELD_KEYS), (brand, name)
        assert row["cancer_type"]["confidence"] in CANCER_TYPE_CONFIDENCES, brand
        assert row["label_indications_verbatim"]["confidence"] == "official", brand


def test_all_fifteen_rows_gained_a_cancer_type_and_none_is_a_named_absence():
    """The reportable count. ⚠ A pin of THIS file on 2026-09-08, not a constant."""
    rows = load_catalog()["adcs"]
    filled = [r for r in rows if r["cancer_type"]["value"]]
    absent = [r for r in rows if not r["cancer_type"]["value"]]
    assert len(rows) == 15
    assert len(filled) == 15
    assert absent == []
    assert sum(len(r["cancer_type"]["value"]) for r in filled) == 28


def test_every_committed_tumour_type_is_in_its_own_rows_label_text():
    """⚠⚠ The audit re-run against the committed file, not just the fixtures.

    The loader already refuses a violation, so this test would be redundant if
    the loader were the only reader. It is not: it states the property in one
    place a human can read, and it fails loudly if the loader's check is ever
    softened while the data stays put.
    """
    for row in load_catalog()["adcs"]:
        haystack = _normalise(row["label_indications_verbatim"]["value"])
        for token in row["cancer_type"]["value"]:
            assert _normalise(token) in haystack, (row["brand_name"]["value"], token)


def test_committed_cancer_type_sources_name_an_fda_authority_and_never_staining():
    for row in load_catalog()["adcs"]:
        for name in ("cancer_type", "label_indications_verbatim"):
            source = row[name]["source"].lower()
            assert any(a in source for a in INDICATION_AUTHORITIES), (name, source[:80])
            for token in STAINING_SOURCE_TOKENS:
                assert token not in source, (row["brand_name"]["value"], name, token)


def test_each_label_citation_names_the_application_it_belongs_to():
    """The disqualifying check, kept live.

    A label record is matched by BRAND, so nothing guarantees it belongs to the
    application D-119 recorded. If it did not, the cell would still look
    plausible — which is the whole reason this is asserted rather than trusted.
    """
    for row in load_catalog()["adcs"]:
        application = row["application_number"]["value"]
        assert application in row["cancer_type"]["source"], row["brand_name"]["value"]


def test_the_third_date_is_distinct_and_not_collapsed():
    data = load_catalog()
    assert data["indications_reviewed_as_of"]["value"] == "2026-09-08"
    assert data["approvals_reconciled_as_of"]["value"] == "2026-09-05"
    assert (
        data["indications_reviewed_as_of"]["value"]
        != data["approvals_reconciled_as_of"]["value"]
    )
    for row in load_catalog()["adcs"]:
        assert row["cancer_type"]["as_of"] == "2026-09-08"


def test_padcev_names_the_two_tumour_types_its_own_label_states():
    """⚠ Not a memory check — an assertion about the stored text.

    The point is the pairing: `urothelial cancer` AND `muscle invasive bladder
    cancer` are both on PADCEV's 2026-08-04 label. `AdcMechanismPanels` already
    warns that these two names get confused; here both are cited, which is why
    naming both is correct rather than a hedge.
    """
    by_id = {r["id"]["value"]: r for r in load_catalog()["adcs"]}
    row = by_id["enfortumab-vedotin"]
    assert row["cancer_type"]["value"] == ["Urothelial cancer", "Muscle invasive bladder cancer"]
    text = _normalise(row["label_indications_verbatim"]["value"])
    assert "urothelial cancer" in text
    assert "muscle invasive bladder cancer" in text


def test_no_invented_science_arrived_with_the_indications():
    """D-119 decision 8 stands: an indication is not a licence to add efficacy."""
    raw = json.loads(CATALOG_V1.read_text(encoding="utf-8"))
    text = json.dumps(raw).lower()
    for banned in ('"dar"', '"ic50"', '"orr"', '"pfs"', '"os"', '"payload"',
                   '"linker"', '"indication"', '"efficacy"', '"response_rate"'):
        assert banned not in text, banned


def test_the_committed_file_never_cites_hpa_or_the_association_map():
    """A file-wide read, so a staining citation cannot hide in a header field."""
    blob = CATALOG_V1.read_text(encoding="utf-8").lower()
    for token in ("proteinatlas", "pathology.tsv", "normal_tissue.tsv", "quasi-h"):
        assert token not in blob, token


# ------------------------------------------------------- the guards, going red


def test_a_tumour_type_absent_from_the_label_text_is_refused(tmp_path):
    """⚠⚠ THE INVENTED-STRING TEST. A cancer type typed from memory fails the gate."""
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=["Urothelial cancer"], source=FIXTURE_LABEL_SOURCE
    )
    with pytest.raises(CatalogError, match="not in this row"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_a_plausible_indication_on_the_wrong_row_is_refused(tmp_path):
    """The realistic version of the same mistake: right drug class, wrong drug.

    `Multiple myeloma` is a true ADC indication — BLENREP's. On a row whose
    stored label text is about a fixture carcinoma it is a fabrication, and the
    loader cannot be talked out of that by the string being real somewhere else.
    """
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma", "Multiple myeloma"], source=FIXTURE_LABEL_SOURCE
    )
    with pytest.raises(CatalogError, match="Multiple myeloma"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_an_hpa_staining_source_is_refused(tmp_path):
    """⚠⚠ THE D-093 JOIN TEST. HPA staining may not fill an FDA indication column."""
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"],
        source=(
            "HPA v22 pathology.tsv IHC High/Medium staining share for this antigen, "
            "read 2026-09-08 from https://v22.proteinatlas.org/about/download"
        ),
    )
    with pytest.raises(CatalogError, match="D-093"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


@pytest.mark.parametrize(
    "source",
    [
        "derived from GET /api/associations for this antigen, 2026-09-08",
        "census quasi-H score for the best single cancer, 2026-09-08",
        "strongest staining cancer in the supplier survey, 2026-09-08",
    ],
)
def test_every_staining_flavoured_source_is_refused(tmp_path, source):
    """Not just HPA by name: the derived association map and the census too.

    Each of these is a real table in this repo, each would render a plausible
    cancer name, and none of them is an FDA indication.
    """
    row = _minimal_row()
    row["cancer_type"] = _envelope(value=["Fixture carcinoma"], source=source)
    with pytest.raises(CatalogError, match="D-093"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_an_uncited_cancer_type_is_refused(tmp_path):
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"], source="widely known to treat this"
    )
    with pytest.raises(CatalogError, match="no FDA indication authority"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_a_bare_string_cancer_type_is_refused(tmp_path):
    """A bare string is not data (D-119 decision 2) — at either level."""
    row = _minimal_row()
    row["cancer_type"] = "Fixture carcinoma"
    with pytest.raises(CatalogError, match="not a"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))

    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value="Fixture carcinoma", source=FIXTURE_LABEL_SOURCE
    )
    with pytest.raises(CatalogError, match="non-empty list"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_derived_confidence_is_refused_for_a_cancer_type(tmp_path):
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"], source=FIXTURE_LABEL_SOURCE, confidence="derived"
    )
    with pytest.raises(CatalogError, match="cannot be derived"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_a_cancer_type_with_no_label_text_to_audit_against_is_refused(tmp_path):
    """D-136 decision 2's corollary — the hole the strict rule closes.

    Null the verbatim field, keep a plausible dated source, and the category
    would be unfalsifiable. That is refused, not downgraded to `reviewed`.
    """
    row = _minimal_row()
    row["label_indications_verbatim"] = _envelope(
        value=None, source=FIXTURE_LABEL_SOURCE, confidence="official"
    )
    with pytest.raises(CatalogError, match="no official text to audit"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_a_blank_cancer_type_with_no_stated_reason_is_refused(tmp_path):
    """Missing stays a NAMED absence, never a blank that looks like data."""
    row = _minimal_row()
    row["cancer_type"] = _envelope(value=None, source="")
    with pytest.raises(CatalogError, match="missing source"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))

    row = _minimal_row()
    row["cancer_type"] = _envelope(value=None, source="none found")
    with pytest.raises(CatalogError, match="no FDA indication authority"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_a_named_absence_loads(tmp_path):
    """⚠ Fixture only. No committed row exercises this branch (D-136 decision 6).

    All 15 rows resolved on 2026-09-08, so the absence path has no live subject.
    It is real code with a red test either way, because the next approval that
    arrives without label text must not be able to render as a blank.
    """
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=None,
        source=(
            "openFDA SPL GET https://api.fda.gov/drug/label.json?search="
            'openfda.brand_name:"FIXTURE" retrieved 2026-09-08 returned no '
            "indications_and_usage for this application"
        ),
    )
    row["label_indications_verbatim"] = _envelope(
        value=None, source=row["cancer_type"]["source"], confidence="official"
    )
    data = load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))
    assert data["adcs"][0]["cancer_type"]["value"] is None
    assert "returned no indications_and_usage" in data["adcs"][0]["cancer_type"]["source"]


def test_a_repeated_tumour_type_is_refused(tmp_path):
    row = _minimal_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma", "fixture carcinoma"], source=FIXTURE_LABEL_SOURCE
    )
    with pytest.raises(CatalogError, match="repeats"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


def test_verbatim_text_may_not_claim_official_for_a_human_summary(tmp_path):
    row = _minimal_row()
    row["label_indications_verbatim"] = _envelope(
        value=FIXTURE_LABEL_TEXT, source=FIXTURE_LABEL_SOURCE, confidence="reviewed"
    )
    with pytest.raises(CatalogError, match="must be 'official'"):
        load_catalog(_write(tmp_path / "c.json", _minimal_catalog([row])))


# ------------------------------- the pipeline keeps the FDA label out (D-139 am.)


def test_the_pipeline_schema_admits_no_fda_label_field():
    """⚠ **Amended at D-139, and the amendment is where the teeth moved.**

    D-136 decision 8 held the pipeline schema shut entirely: *"filling Approved is
    not licence for Pipeline."* That was right while no Spec authorised a pipeline
    programme field, and it said so — *"a later GO"*. **D-139 is that GO**, so the
    first form of this test (``"cancer_type" not in PIPELINE_FIELDS``) reddened BY
    DESIGN when D-139 landed. It was **not** deleted: what D-136 actually needed to
    protect is that a pipeline row may not carry an **FDA label**, and that is
    asserted here and enforced in the loader's own source check below.
    """
    assert "label_indications_verbatim" not in PIPELINE_FIELDS
    # D-139 amends the other half: the pipeline now has a cancer type of its own,
    # from the trial registry, on its own stricter confidence vocab.
    assert "cancer_type" in PIPELINE_FIELDS
    assert PIPELINE_CANCER_TYPE_CONFIDENCES == ("reviewed",)
    assert "official" in CANCER_TYPE_CONFIDENCES
    for row in load_pipeline()["pipeline"]:
        assert "label_indications_verbatim" not in row


def test_a_label_indications_field_on_a_pipeline_row_is_refused(tmp_path):
    """The half of D-136 decision 8 that D-139 does not touch."""
    raw = json.loads((ROOT / "data" / "adcs" / "adcs.pipeline.v1.json").read_text("utf-8"))
    raw["pipeline"][0]["label_indications_verbatim"] = _envelope(
        value=FIXTURE_LABEL_TEXT, source=FIXTURE_LABEL_SOURCE, confidence="official"
    )
    with pytest.raises(CatalogError, match="extra keys"):
        load_pipeline(_write(tmp_path / "p.json", raw))


def test_an_fda_label_source_on_a_pipeline_cancer_type_is_refused(tmp_path):
    """⚠⚠ The D-136 refusal, relocated rather than retired.

    An investigational agent has no FDA indication, so citing one for its cancer
    type is a promotion to approved performed in a source string. Before D-139 the
    schema made this unreachable; now the field exists, so the loader has to refuse
    the *source* — and this test is the reason the relocation is not a loosening.
    """
    raw = json.loads((ROOT / "data" / "adcs" / "adcs.pipeline.v1.json").read_text("utf-8"))
    raw["pipeline"][0]["cancer_type"] = _envelope(
        value=["Fixture carcinoma"], source=FIXTURE_LABEL_SOURCE
    )
    with pytest.raises(CatalogError, match="FDA label authority"):
        load_pipeline(_write(tmp_path / "p.json", raw))


# ------------------------------------------------------------- the log leads it


def test_d136_entry_exists_in_the_living_log():
    """The check is the HEADING, not a citation of it (D-062 / method-note item 7).

    PR #90 named D-062 in its title and shipped no `### D-062`; thirteen later
    citations then pointed at nothing. So this asserts the entry, and names its
    successor rather than accepting anything `>=`.

    ⚠ **Widened at D-137 — from "137 does not exist" to "137 is the census
    sortable Cost column and 138 does not exist"** — by naming, not by loosening.
    Spending D-137 reddened the previous form **BY DESIGN**: that is this guard
    working. D-137 was authored while this PR (#260) was still open and took 137
    deliberately, leaving 136 to it, so the ids are contiguous and neither was
    assumed free. A bare `### D-138` still reddens here.

    ⚠ **Widened again at D-138 — to "138 is the `/method` contents rail and 139
    does not exist"** — the same way, and the fourth live two-branch collision in
    a row. D-138 (#262) was opened at tip `1b0251b` while #261 (D-137) was still
    open and took 138 deliberately, leaving 137 to it — read off the open-PR list,
    not assumed. #261 then squash-merged at `68fe0228` and this assertion reddened
    **exactly as the comment above predicted it would**. ⚠ **The successor is
    named, never admitted by a `>=`:** an entry that merely *takes* 138 still
    fails, and a bare `### D-139` still reddens.

    ⚠ **Widened again at D-139 — to "139 is the served-path flip"** — the same way,
    and the fifth time this guard has been widened rather than relaxed. D-139 hands
    the recorded D-126 PASS seventeen the confidence-Kabsch structure and leaves
    everyone else on the assembler.

    ⚠⚠ **Widened again at D-140 — to "140 is the pipeline programme fields and 141
    does not exist" — and this widening is the record of a DUPLICATE, not a
    successor.** Two branches cut from `dd06e9c` each read `gh pr list --state open`,
    each found no `D-1NN` spender, and each wrote `### D-139`: the served-path flip
    and the ADC Pipeline programme fields. They could not see each other because the
    pipeline branch was not yet an open PR. The served-path work merged first
    (`1e9777c`) and assigned the loser in its commit message — *"Pipeline #263 takes
    D-140."* ⚠ **D-140 is the entry that amends this very suite's D-136 decision 8**,
    so an entry that merely *takes* 140 would leave that amendment pointing at
    nothing (the D-062 failure mode). Both ids are named; `### D-141` still reddens.

    ⚠ **Widened again at D-141 — to "141 is the confidence-Kabsch lander and 142
    does not exist"** — the sixth widening, and the duplicate above resolving one
    branch later. D-141 lands the D-126 OPS trees on the serving volume so D-139's
    gate has bytes to answer with. Cut from `1e9777c`, it ran the open-PR check
    **after** #263 was published, saw 140 held, and took 141 rather than a second
    duplicate — the D-138 precedent, applied with the benefit of the lesson the
    paragraph above records. #263 merged at `578f5ac` while it was open, this
    assertion reddened by design, and the rebase inserted 140 beside 141. **All
    three ids are named;** `### D-144` still reddens.

    ⚠ **Widened again at D-143 — "143 is the Track B structural-only copy entry, 142 is
    HELD, and 144 does not exist"** — the seventh widening. That branch was cut from
    `30f402f`, `grep`ed the log for the highest written entry (141), read
    `gh pr list --state open` (#222 / #200 / #197, none spending a `D-1NN`) and took
    **142**; the owner then ruled the id to **143** (2026-09-09). Nothing visible in the
    tree spends 142, so it is registered in `docs/RESERVED.md` and its bar STAYS rather
    than being dropped. ⚠ **D-143 does not touch this suite's subject** — the ADC
    catalog, the pipeline shelf and the `cancer_type` envelopes are untouched by it; it
    is named here only because this is one of the enumerated id guards.
    """
    log = DOCS_README.read_text(encoding="utf-8")
    assert "\n### D-136 —" in log
    assert re.search(r"^### D-137 — The census gains a sortable Cost column", log, re.M), (
        "D-137 is the recorded successor id; it must be the census sortable-Cost-column "
        "entry, not some other entry that took the number"
    )
    assert re.search(r"^### D-138 — `/method` gets a contents rail", log, re.M), (
        "D-138 is the recorded successor id; it must be the /method contents-rail "
        "entry, not some other entry that took the number"
    )
    assert re.search(r"^### D-139 — The served PDB stops being a constant", log, re.M), (
        "D-139 is the recorded successor id; it must be the served-path flip entry, "
        "not some other entry that took the number"
    )
    assert re.search(r"^### D-140 — The ADC Pipeline shelf gets a cancer type", log, re.M), (
        "D-140 is the recorded successor id; it must be the pipeline programme-fields "
        "entry, not some other entry that took the number"
    )
    assert re.search(r"^### D-141 — The gate had nothing to answer with", log, re.M), (
        "D-141 is the recorded successor id; it must be the confidence-Kabsch lander "
        "entry, not some other entry that took the number"
    )
    assert re.search(r"^### D-143 — Track B stops claiming a composite", log, re.M), (
        "D-143 is the recorded successor id; it must be the Track B structural-only "
        "copy entry, not some other entry that took the number"
    )
    # ⚠⚠ 142 IS NOW WRITTEN, AND THE BAR ON IT REDDENED EXACTLY AS ITS OWN MESSAGE PREDICTED.
    # `docs/RESERVED.md` reserved 142 after the Track B copy work was renumbered off it, with the
    # unblock recorded as *"whoever holds it writes `### D-142`"* and the resolution pre-committed:
    # *"if a holder writes it, this reddens BY DESIGN and 142 is ADDED beside 143."* The holder is
    # the `/targets` columns entry (Emma CoS assignment, 2026-09-09), so the bar is REPLACED BY A
    # NAME rather than deleted, and 142 is ADDED to the enumeration beside 143. ⚠ Never a `>=`:
    # this is the eighth widening and the eighth resolution by adding.
    # ⚠ A reserved integer that is later spent must be NAMED here, not merely un-barred — an
    # un-barred integer with no name is exactly what the D-062 defect looked like.
    assert re.search(r"^### D-142 — `/targets` gains a Cancer association", log, re.M), (
        "D-142 is the recorded holder of the reserved integer; it must be the target-list "
        "columns entry, not some other entry that took the number"
    )
    # ⚠ Widened again at **D-144** — to `[…, 141, 142, 143, 144]` — for the NINTH time, and
    # by ADDING as every pass before it. D-144 lands the census STRUCTURAL rank in the DB and on
    # its own route (`/api/census-structural-ranking`): the DB/API half of the same
    # structural-only ruling D-143's copy lane describes, and neither of them the cohort-82
    # learned scorer. ⚠⚠ Its GO **assigned** it 144 while 142 and 143 were both unwritten and
    # unpublished, so its own first draft barred `### D-142` and `### D-143` — and both then
    # merged mid-flight (`f243f93` / `22ce1d7` / `b7d933f`), reddening those bars **exactly as
    # they said they would**. The rebase ADDED 142, 143 and 144 by name. Nothing was relaxed to
    # a `>=`, and `### D-145` now takes the next-free bar.
    assert re.search(r"^### D-144 — The offline census ranking stops being a spreadsheet",
                     log, re.M), (
        "D-144 must be the census structural-rank entry, not some other entry that took "
        "the number"
    )
    # ⚠ Widened again at **D-145** — "145 is the image-permanence entry and 146 takes the bar" —
    # for the TENTH time, and by ADDING as every pass before it. ⚠⚠ **The SECOND reserved integer
    # to be SPENT rather than skipped** (142 was the first, the same day): 145 sat in
    # `docs/RESERVED.md` as the next free `D-`, `D-144` cited it in order to bar it, and this bar
    # reddened **by design** when an entry claimed it. D-145 bakes the D-144 structural-rank
    # loader into the Fly serving image as one explicit `COPY` — image permanence only, and it
    # **does not touch this suite's subject** (the ADC cancer-type columns). It is named here
    # because this is one of the enumerated id checks, not because it changes anything.
    assert re.search(r"^### D-145 — The D-144 loader stops living on the production host",
                     log, re.M), (
        "D-145 must be the image-permanence entry that bakes the structural-rank loader in, "
        "not some other entry that took the number"
    )
    # ⚠ Widened again at **D-146** — "146 is the Track B live-route copy entry and 147 takes the
    # bar" — for the ELEVENTH time, and by ADDING as every pass before it. ⚠⚠ **The THIRD
    # reserved integer to be SPENT rather than skipped** (142 and 145 were the first two, both the
    # same day): 146 sat in `docs/RESERVED.md` as the next free `D-`, `D-145` cited it in order to
    # bar it, and this bar reddened **by design** when an entry claimed it. D-146 retires Track B's
    # offline clause now that `GET /api/census-structural-ranking` answers `valid` — copy only,
    # and it **does not touch this suite's subject** (the ADC cancer-type columns). It is named
    # here because this is one of the enumerated id checks, not because it changes anything.
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     log, re.M), (
        "D-146 must be the Track B live-route copy entry, not some other entry that took "
        "the number"
    )
    assert "\n### D-147" not in log, (
        "D-147 is the next free integer and must stay unspent until an entry claims it "
        "by name here — never admitted by a `>=`"
    )


def test_every_entry_slice_in_this_suite_is_anchored_to_a_line_start():
    """⚠⚠ D-136 amendment 1 — the fix is in the SLICING, not in the prose.

    A first draft of this test asserted the opposite: that no entry may quote a
    ``### D-NNN`` token mid-line. **That was a misdiagnosis, and it failed against
    ~130 pre-existing occurrences.** Quoting a heading inline is this log's
    established evidence-of-provenance habit — method-note item 7 asks an entry to
    show it confirmed the heading exists, and entries do that by naming it. A guard
    that condemned the practice would have been a rule invented here and back-dated
    over the whole history.

    What is actually wrong is locating an entry with an **unanchored** index lookup,
    which cannot tell a heading from a citation of one. So the property worth pinning
    is that a slice returns exactly one entry: D-136's own text, with its neighbour's
    kept out.
    """
    log = DOCS_README.read_text(encoding="utf-8")

    # Anchored, the way the helpers now do it.
    d136 = re.search(r"^### D-136 —", log, re.M)
    d135 = re.search(r"^### D-135 —", log, re.M)
    assert d136 and d135
    # Newest-first: D-136 is above D-135, and neither slice reaches the other.
    assert d136.start() < d135.start()
    assert "Coverage gains a SECOND population" not in log[d136.start(): d135.start()]

    # Unanchored, the way they used to: this PR's own entry cites D-135's heading as
    # evidence, so a bare index lookup lands INSIDE D-136 rather than on D-135.
    assert log.index("### D-135") < d135.start(), (
        "this assertion documents WHY the helpers are anchored; if it ever fails, the "
        "citation was removed and the anchoring is no longer load-bearing here"
    )


def test_the_log_entry_records_the_count_it_reports():
    """⚠ Bounded by the NEXT heading, whatever it is — not by a named neighbour.

    The first draft ended the slice at ``\\n### D-134``, which was D-136's
    neighbour on a branch cut before D-135 merged. That is a hidden dependency
    on merge order: D-135 landing between them silently widened the slice, so
    the assertions below would have started passing on someone else's entry.
    """
    log = DOCS_README.read_text(encoding="utf-8")
    rest = log.split("\n### D-136 —", 1)[1]
    next_heading = re.search(r"\n### D-\d", rest)
    entry = rest[: next_heading.start()] if next_heading else rest
    assert "15 of 15" in entry
    assert "D-093" in entry
    assert "D-122 decision 3" in entry
    # The slice really is only D-136's own entry.
    assert "Coverage gains a SECOND population" not in entry
