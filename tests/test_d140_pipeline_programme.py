"""D-140 — the ADC Pipeline Cancer type / Description columns, and the guards behind them.

Hermetic: the committed catalog, the committed registry artefact, and tmp fixtures.
**No network.** The ClinicalTrials.gov reads happened once, in
``scripts/fetch_pipeline_ctgov.py``, and dated
``data/adcs/artifacts/ctgov.pipeline.2026-09-08.json``; nothing here imports that
script (D-029: a live registry call must not redden the gate).

The tests this suite exists for, each written so it can go red:

* :func:`test_a_tumour_type_absent_from_the_stored_text_is_refused` — a tumour typed
  from memory reddens, because a word this row's own stored text does not contain
  cannot pass a substring test.
* :func:`test_an_hpa_staining_source_is_refused` — a staining / association-map join
  reddens, naming D-093.
* :func:`test_an_fda_indication_authority_is_refused_on_a_pipeline_row` — D-140's own
  refusal: an investigational row that cites an FDA label has promoted itself.
* :func:`test_a_sponsor_that_appears_in_no_source_is_refused` — the description's maker
  is audited, not trusted.
* :func:`test_every_committed_row_traces_to_the_dated_registry_artefact` — the chain
  from the raw record on disk to the rendered cell, re-walked on every run.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from core.adc_catalog import (
    PIPELINE_CANCER_TYPE_CONFIDENCES,
    PIPELINE_CONDITIONS_CONFIDENCES,
    PIPELINE_DESCRIPTION_CONFIDENCES,
    PIPELINE_DESCRIPTION_MAX_CHARS,
    PIPELINE_DESCRIPTION_SEPARATOR,
    PIPELINE_FIELDS,
    PIPELINE_V1,
    STAINING_SOURCE_TOKENS,
    CatalogError,
    load_pipeline,
)
from tests.test_adc_pipeline import (
    FIXTURE_CITATION,
    FIXTURE_CONDITIONS_SOURCE,
    _envelope,
    _minimal_pipeline,
    _minimal_pipeline_row,
    _write,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS_README = ROOT / "docs" / "README.md"


def _normalise(text):
    """The loader's own normalisation, restated so the test does not inherit a bug."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _artifact():
    data = load_pipeline()
    path = ROOT / data["registry_artifact"]["value"]
    return json.loads(path.read_text(encoding="utf-8"))


def _ncts(source):
    """Record ids named in a source string, deduplicated in first-mention order.

    A source names the same record twice — once in the URL it was fetched from and
    once in the sentence explaining why that record is this row's — so a raw
    ``findall`` would double-count it.
    """
    return list(dict.fromkeys(re.findall(r"NCT\d{8}", source)))


# ---------------------------------------------------------------- committed file


def test_every_pipeline_row_carries_all_three_programme_envelopes():
    for row in load_pipeline()["pipeline"]:
        name = row["name"]["value"]
        for field in ("cancer_type", "conditions_verbatim", "description"):
            assert field in row, (name, field)
        assert row["cancer_type"]["confidence"] in PIPELINE_CANCER_TYPE_CONFIDENCES, name
        assert row["conditions_verbatim"]["confidence"] in PIPELINE_CONDITIONS_CONFIDENCES, name
        assert row["description"]["confidence"] in PIPELINE_DESCRIPTION_CONFIDENCES, name
        assert row["cancer_type"]["as_of"] == "2026-09-08", name
        assert row["description"]["as_of"] == "2026-09-08", name


def test_the_reportable_fill_counts():
    """⚠ A pin of THIS file on 2026-09-08, not a constant — and not a total.

    The breakdown is the finding (method-note item 2): a bare "10 rows gained the
    fields" would hide that half of them gained a **named absence** instead of a
    tumour type, which is the honest outcome for six preclinical / patent rows and
    one all-comers phase 1 basket.
    """
    rows = load_pipeline()["pipeline"]
    assert len(rows) == 10

    ct_filled = [r for r in rows if r["cancer_type"]["value"]]
    ct_absent = [r for r in rows if r["cancer_type"]["value"] is None]
    assert len(ct_filled) == 5
    assert len(ct_absent) == 5
    assert sum(len(r["cancer_type"]["value"]) for r in ct_filled) == 14
    assert [r["id"]["value"] for r in ct_absent] == [
        "ly3076226",
        "rgx-019-mmae",
        "4d11-mmae",
        "anti-upk1b-adc",
        "anti-cdh11-immunoconjugate",
    ]

    desc_filled = [r for r in rows if r["description"]["value"]]
    desc_absent = [r for r in rows if r["description"]["value"] is None]
    assert len(desc_filled) == 4
    assert len(desc_absent) == 6
    # ⚠ The four that gained a maker are exactly the four with a trial in the
    # registry. No patent assignee was looked up: that is not an authority D-140
    # admits, and inventing one would be the failure this whole suite is about.
    assert [r["id"]["value"] for r in desc_filled] == [
        "ifinatamab-deruxtecan",
        "ladiratuzumab-vedotin",
        "depatuxizumab-mafodotin",
        "ly3076226",
    ]


def test_every_committed_tumour_type_is_in_its_own_rows_stored_text():
    """⚠⚠ The audit re-run against the committed file, not just the fixtures.

    The loader already refuses a violation, so this would be redundant if the loader
    were the only reader. It is not: it states the property in one place a human can
    read, and it fails loudly if the loader's check is ever softened while the data
    stays put.
    """
    for row in load_pipeline()["pipeline"]:
        if not row["cancer_type"]["value"]:
            continue
        haystack = _normalise(row["conditions_verbatim"]["value"])
        for token in row["cancer_type"]["value"]:
            assert _normalise(token) in haystack, (row["name"]["value"], token)


def test_every_quoted_verbatim_really_is_a_quote_of_the_row_citation():
    """The hole a `reviewed` verbatim would open, closed and then checked.

    A row whose anchor text is its own citation could claim anything if nobody read
    the citation back. Six rows are in that class, so this walks all of them.
    """
    quoted = [
        r for r in load_pipeline()["pipeline"]
        if r["conditions_verbatim"]["confidence"] == "reviewed"
    ]
    assert len(quoted) == 6
    for row in quoted:
        assert _normalise(row["conditions_verbatim"]["value"]) in _normalise(
            row["source_citation"]["value"]
        ), row["name"]["value"]


def test_committed_programme_sources_never_name_staining_or_an_fda_label():
    for row in load_pipeline()["pipeline"]:
        for field in ("cancer_type", "conditions_verbatim", "description"):
            source = row[field]["source"].lower()
            for token in STAINING_SOURCE_TOKENS:
                assert token not in source, (row["name"]["value"], field, token)
            for token in ("api.fda.gov", "accessdata.fda.gov", "drugsfda", "drugs@fda"):
                assert token not in source, (row["name"]["value"], field, token)


def test_the_third_pipeline_date_is_distinct_and_not_collapsed():
    data = load_pipeline()
    assert data["conditions_reviewed_as_of"]["value"] == "2026-09-08"
    assert data["mapping_sourced_as_of"]["value"] == "2026-07-27"
    assert data["catalog_assembled_as_of"]["value"] == "2026-09-05"
    assert len({
        data["conditions_reviewed_as_of"]["value"],
        data["mapping_sourced_as_of"]["value"],
        data["catalog_assembled_as_of"]["value"],
    }) == 3


def test_no_invented_science_arrived_with_the_programme_fields():
    """D-119 decision 8 stands: a cancer type is not a licence to add efficacy."""
    text = json.dumps(json.loads(PIPELINE_V1.read_text(encoding="utf-8"))).lower()
    for banned in ('"dar"', '"ic50"', '"orr"', '"pfs"', '"os"', '"payload"',
                   '"linker"', '"indication"', '"efficacy"', '"response_rate"'):
        assert banned not in text, banned


def test_the_committed_file_never_cites_hpa_or_the_association_map():
    """A file-wide read, so a staining citation cannot hide in a header field."""
    blob = PIPELINE_V1.read_text(encoding="utf-8").lower()
    for token in ("proteinatlas", "pathology.tsv", "normal_tissue.tsv", "quasi-h"):
        assert token not in blob, token


# ------------------------------------------- the chain back to the raw artefact


def test_every_committed_row_traces_to_the_dated_registry_artefact():
    """⚠⚠ THE PROVENANCE WALK (D-016). Every NCT a row cites is on disk, raw.

    The rendered cell is a reduction of a reduction: registry record → stored
    conditions text → tumour list. This re-walks it from the raw record, so a source
    string that *names* a record the artefact does not contain reddens.
    """
    artifact = _artifact()
    studies = artifact["studies"]
    for row in load_pipeline()["pipeline"]:
        for field in ("cancer_type", "conditions_verbatim", "description"):
            for nct in _ncts(row[field]["source"]):
                assert nct in studies, (row["name"]["value"], field, nct)


def test_official_conditions_text_is_exactly_what_the_registry_returned():
    """The reduction is auditable only if the anchor was not edited on the way in."""
    studies = _artifact()["studies"]
    for row in load_pipeline()["pipeline"]:
        field = row["conditions_verbatim"]
        if field["confidence"] != "official":
            continue
        ncts = _ncts(field["source"])
        assert ncts, row["name"]["value"]
        expected = "; ".join(c for n in ncts for c in studies[n]["conditions"])
        assert field["value"] == expected, row["name"]["value"]


def test_each_matched_record_names_this_rows_own_drug():
    """⚠ The query that could disqualify the fill, kept live.

    Two rows' trials were found by ACRONYM rather than by an id already on disk
    (``IDeate-Lung01``, ``INTELLANCE-1``). Nothing about an acronym search guarantees
    the record is this drug's — and if it were not, the conditions would be another
    programme's and the cell would still look perfectly plausible. So every matched
    record's own interventions must name the row's agent.
    """
    studies = _artifact()["studies"]
    checked = 0
    for row in load_pipeline()["pipeline"]:
        stem = re.split(r"[ (-]", row["name"]["value"])[0].lower()
        for nct in _ncts(row["conditions_verbatim"]["source"]):
            blob = " ".join(studies[nct]["interventions"]).lower()
            assert stem in blob, (row["name"]["value"], nct, blob)
            checked += 1
    assert checked == 5


def test_the_acronym_that_resolved_to_nothing_is_recorded_as_a_negative():
    """⚠ The lookup that FAILED is on disk too, and it changed the data.

    ``IDeate-PanTumor01`` is named in ifinatamab deruxtecan's citation and matched no
    registry acronym on the retrieval date. The script takes **exact** acronym equality
    with no title fallback, precisely so it cannot choose which study a citation meant;
    the consequence is that this row's cancer type comes from IDeate-Lung01 alone, and
    the row's own source string says so.
    """
    artifact = _artifact()
    lookups = {(x["row_id"], x["query"]): x for x in artifact["lookups"]}
    assert lookups[("ifinatamab-deruxtecan", "IDeate-PanTumor01")]["matched"] == []
    assert lookups[("ifinatamab-deruxtecan", "IDeate-Lung01")]["matched"] == ["NCT05280470"]
    row = {r["id"]["value"]: r for r in load_pipeline()["pipeline"]}["ifinatamab-deruxtecan"]
    assert "IDeate-PanTumor01" in row["conditions_verbatim"]["source"]
    assert "NCT05280470" in row["conditions_verbatim"]["source"]


def test_every_named_absence_was_actually_searched():
    """An absence that was never looked for is a gap; this one is a finding.

    All six rows with no maker were queried by intervention name and the registry
    returned nothing. The negative is recorded in the artefact, and each row's source
    quotes the query that produced it.
    """
    artifact = _artifact()
    searched = {x["row_id"]: x for x in artifact["lookups"] if x["kind"] == "searched"}
    assert len(searched) == 6
    for row_id, lookup in searched.items():
        assert lookup["matched"] == [], row_id
    for row in load_pipeline()["pipeline"]:
        if row["description"]["value"] is not None:
            continue
        lookup = searched[row["id"]["value"]]
        assert lookup["query"] in row["description"]["source"], row["id"]["value"]


def test_the_artefact_is_a_committed_file_and_no_test_reaches_the_network():
    """D-029 — the gate never calls ClinicalTrials.gov."""
    artifact_path = ROOT / load_pipeline()["registry_artifact"]["value"]
    assert artifact_path.is_file()
    assert artifact_path.name.endswith("2026-09-08.json")
    fetcher = (ROOT / "scripts" / "fetch_pipeline_ctgov.py").read_text(encoding="utf-8")
    assert "urllib.request" in fetcher
    for path in sorted((ROOT / "tests").glob("*.py")) + [ROOT / "core" / "adc_catalog.py"]:
        body = path.read_text(encoding="utf-8")
        assert "fetch_pipeline_ctgov" not in body or path.name == "test_d140_pipeline_programme.py"


# ------------------------------------------------------- the guards, going red


def test_a_tumour_type_absent_from_the_stored_text_is_refused(tmp_path):
    """⚠⚠ THE INVENTED-STRING TEST. A tumour typed from memory fails the gate."""
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Urothelial cancer"], source=FIXTURE_CONDITIONS_SOURCE
    )
    with pytest.raises(CatalogError, match="not in this row"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_plausible_tumour_from_another_programme_is_refused(tmp_path):
    """The realistic version: right field, wrong row.

    ``Glioblastoma`` is a true tumour on this very shelf — depatuxizumab mafodotin's.
    On a row whose stored text is a fixture citation it is a fabrication, and the
    loader cannot be talked out of that by the string being real one row over.
    """
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma", "Glioblastoma"], source=FIXTURE_CONDITIONS_SOURCE
    )
    with pytest.raises(CatalogError, match="Glioblastoma"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_an_hpa_staining_source_is_refused(tmp_path):
    """⚠⚠ THE D-093 JOIN TEST. Staining may not fill a clinical column here either."""
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"],
        source=(
            "HPA v22 pathology.tsv IHC High/Medium share for this antigen, read "
            "2026-09-08 from https://v22.proteinatlas.org/about/download"
        ),
    )
    with pytest.raises(CatalogError, match="D-093"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


@pytest.mark.parametrize(
    "source",
    [
        "derived from GET /api/associations for this antigen, 2026-09-08",
        "the census quasi-H score for the best single cancer, 2026-09-08",
        "strongest staining cancer in the supplier survey, 2026-09-08",
    ],
)
def test_every_staining_flavoured_source_is_refused(tmp_path, source):
    """Not just HPA by name: the derived association map and the census too.

    Each is a real table in this repo, each would render a plausible cancer name,
    and none of them is a trial a sponsor is running.
    """
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(value=["Fixture carcinoma"], source=source)
    with pytest.raises(CatalogError, match="D-093"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


@pytest.mark.parametrize(
    "source",
    [
        'openFDA SPL GET https://api.fda.gov/drug/label.json?search=x retrieved 2026-09-08',
        "Drugs@FDA label for this agent, retrieved 2026-09-08",
        "SPL section 1 INDICATIONS AND USAGE text, retrieved 2026-09-08",
    ],
)
def test_an_fda_indication_authority_is_refused_on_a_pipeline_row(tmp_path, source):
    """⚠⚠ D-140's OWN refusal, and the one D-136 could not have written.

    On the Approved shelf an FDA label is *the* authority. Here it is disqualifying:
    none of these agents is approved, so a row that cites a drug label has either
    found somebody else's approval or invented its own. Promotion is out of scope,
    and a source string is not a back door into it.
    """
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(value=["Fixture carcinoma"], source=source)
    with pytest.raises(CatalogError, match="FDA label authority"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_an_uncited_cancer_type_is_refused(tmp_path):
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"], source="everyone knows this one is for that"
    )
    with pytest.raises(CatalogError, match="no D-140 authority"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_an_undated_source_is_refused(tmp_path):
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"],
        source="ClinicalTrials.gov, at some point",
    )
    with pytest.raises(CatalogError, match="no ISO retrieval"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_bare_string_cancer_type_is_refused(tmp_path):
    """A bare string is not data (D-119 decision 2) — at either level."""
    row = _minimal_pipeline_row()
    row["cancer_type"] = "Fixture carcinoma"
    with pytest.raises(CatalogError, match="not a"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))

    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value="Fixture carcinoma", source=FIXTURE_CONDITIONS_SOURCE
    )
    with pytest.raises(CatalogError, match="non-empty list"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


@pytest.mark.parametrize("confidence", ["official", "derived"])
def test_only_reviewed_confidence_is_allowed_for_a_pipeline_cancer_type(tmp_path, confidence):
    """⚠ Stricter than D-136 on purpose, and this is the reason.

    An approved row may carry an `official` cancer type because FDA published the
    words. Nobody official has published a tumour type for an investigational agent
    — the registry publishes what a sponsor is *enrolling* — so `official` is refused
    here as well as `derived`.
    """
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma"],
        source=FIXTURE_CONDITIONS_SOURCE,
        confidence=confidence,
    )
    with pytest.raises(CatalogError, match="is not in"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_cancer_type_with_no_stored_text_to_audit_against_is_refused(tmp_path):
    """D-140 decision 4's corollary — the hole the strict rule closes.

    Null the anchor, keep a plausible dated source, and the category would be
    unfalsifiable. Refused, not downgraded.

    ⚠ **Fixture only.** All 10 committed rows carry stored text, so this branch has
    no live subject — the inverse of the cancer-type absence branch, which has five.
    """
    row = _minimal_pipeline_row()
    row["conditions_verbatim"] = _envelope(value=None, source=FIXTURE_CONDITIONS_SOURCE)
    with pytest.raises(CatalogError, match="no stored text to audit"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_reviewed_verbatim_that_is_not_a_quote_of_the_citation_is_refused(tmp_path):
    """⚠⚠ The audit's own audit.

    Rule 4 checks the tumour against the anchor. That is worth nothing if the anchor
    can be typed, so a `reviewed` anchor must be a literal quote of the citation
    already on disk — otherwise a row could invent the evidence and then pass the
    substring test against it.
    """
    row = _minimal_pipeline_row()
    row["conditions_verbatim"] = _envelope(
        value="Fixture carcinoma and also urothelial cancer",
        source=FIXTURE_CONDITIONS_SOURCE,
    )
    with pytest.raises(CatalogError, match="not a literal quote"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_an_official_verbatim_with_no_record_named_is_refused(tmp_path):
    """`official` means a registry record returned it. Say which one."""
    row = _minimal_pipeline_row()
    row["conditions_verbatim"] = _envelope(
        value="Fixture carcinoma",
        source="ClinicalTrials.gov, retrieved 2026-09-08",
        confidence="official",
    )
    with pytest.raises(CatalogError, match="names no NCT record"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_blank_cancer_type_with_no_stated_reason_is_refused(tmp_path):
    """Missing stays a NAMED absence, never a blank that looks like data."""
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(value=None, source="")
    with pytest.raises(CatalogError, match="missing source"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))

    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(value=None, source="none found")
    with pytest.raises(CatalogError, match="no D-140 authority"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_named_absence_loads():
    """⚠ Unlike D-136's, this branch has FIVE live subjects, so it is not fixture-only.

    D-136 had to say its absence path was exercised by fixture alone because all 15
    approved rows resolved. Here half the shelf is preclinical or patent-stage, so the
    honest outcome for those rows *is* the absence — and each one states which lookup
    came back empty rather than rendering a blank.
    """
    absent = [r for r in load_pipeline()["pipeline"] if r["cancer_type"]["value"] is None]
    assert len(absent) == 5
    for row in absent:
        source = row["cancer_type"]["source"]
        assert source.strip()
        assert re.search(r"\d{4}-\d{2}-\d{2}", source), row["id"]["value"]
        assert "returned 0 studies" in source or "Neither names a tumour" in source


def test_a_repeated_tumour_type_is_refused(tmp_path):
    row = _minimal_pipeline_row()
    row["cancer_type"] = _envelope(
        value=["Fixture carcinoma", "fixture carcinoma"], source=FIXTURE_CONDITIONS_SOURCE
    )
    with pytest.raises(CatalogError, match="repeats"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


# ------------------------------------------------------------- the description


def test_a_sponsor_that_appears_in_no_source_is_refused(tmp_path):
    """⚠⚠ THE INVENTED-MAKER TEST. 'Who is making it' is audited, not trusted.

    The same discipline as the tumour list, applied to the other half of the ask: the
    maker has to appear in the field's own source, which is where the registry's
    `leadSponsor` or the citation's own wording is quoted.
    """
    row = _minimal_pipeline_row()
    row["description"] = _envelope(
        value="Pfizer — a fixture-directed ADC.",
        source=(
            "this row's source_citation in data/adc_reference_mapping.csv "
            "(CURATED 2026-07-27) names Fixture Bio as the sponsor"
        ),
    )
    with pytest.raises(CatalogError, match="does not appear in this field's own source"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_description_with_no_maker_half_is_refused(tmp_path):
    """A programme blurb with nobody behind it is not what this column is for."""
    row = _minimal_pipeline_row()
    row["description"] = _envelope(
        value="A fixture-directed ADC in early development.",
        source=(
            "this row's source_citation in data/adc_reference_mapping.csv "
            "(CURATED 2026-07-27) names Fixture Bio as the sponsor"
        ),
    )
    with pytest.raises(CatalogError, match="maker"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_blank_description_that_looks_like_data_is_refused(tmp_path):
    row = _minimal_pipeline_row()
    row["description"] = _envelope(value="   ", source=FIXTURE_CONDITIONS_SOURCE)
    with pytest.raises(CatalogError, match="blank that looks like data"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_a_description_longer_than_a_one_liner_is_refused(tmp_path):
    row = _minimal_pipeline_row()
    row["description"] = _envelope(
        value="Fixture Bio" + PIPELINE_DESCRIPTION_SEPARATOR + "x" * PIPELINE_DESCRIPTION_MAX_CHARS,
        source=(
            "this row's source_citation in data/adc_reference_mapping.csv "
            "(CURATED 2026-07-27) names Fixture Bio as the sponsor"
        ),
    )
    with pytest.raises(CatalogError, match="capped at"):
        load_pipeline(_write(tmp_path / "p.json", _minimal_pipeline([row])))


def test_committed_descriptions_are_short_and_name_a_maker_first():
    for row in load_pipeline()["pipeline"]:
        value = row["description"]["value"]
        if value is None:
            continue
        assert len(value) <= PIPELINE_DESCRIPTION_MAX_CHARS, row["id"]["value"]
        maker = value.split(PIPELINE_DESCRIPTION_SEPARATOR)[0]
        assert _normalise(maker) in _normalise(row["description"]["source"])


def test_committed_makers_match_the_registry_lead_sponsor():
    """⚠ The disqualifying check for the maker half, run against the raw record.

    A sponsor quoted into a source string is only as good as the record it was
    quoted from. This reads the artefact back: every maker must appear in the lead
    sponsor of a study that row's own source names.
    """
    studies = _artifact()["studies"]
    checked = 0
    for row in load_pipeline()["pipeline"]:
        value = row["description"]["value"]
        if value is None:
            continue
        ncts = _ncts(row["description"]["source"])
        assert ncts, row["id"]["value"]
        sponsors = _normalise(" ".join(studies[n]["lead_sponsor"] for n in ncts))
        maker = _normalise(value.split(PIPELINE_DESCRIPTION_SEPARATOR)[0])
        # ⚠ ifinatamab's maker is the citation's `Daiichi Sankyo/Merck`, which the
        # registry does not carry whole — the lead sponsor is the first half. The
        # assertion is that the registry sponsor is IN the maker or the maker is in
        # the registry sponsor, never that a name appears from nowhere.
        assert any(part and part in sponsors for part in maker.split(" ")[:2]), (
            row["id"]["value"], maker, sponsors
        )
        checked += 1
    assert checked == 4


# --------------------------------------------------------- the shelf boundary


def test_the_approved_shelf_is_untouched_by_this_change():
    """⚠ D-136 filled Approved from the FDA label; D-140 must not have moved a byte.

    Read as a property of the committed file rather than trusted to the diff: every
    approved row still carries the label pair, and no pipeline field leaked in.
    """
    from core.adc_catalog import load_catalog

    rows = load_catalog()["adcs"]
    assert len(rows) == 15
    for row in rows:
        assert row["cancer_type"]["value"], row["id"]["value"]
        assert row["label_indications_verbatim"]["confidence"] == "official"
        assert "conditions_verbatim" not in row
        assert "description" not in row


def test_pipeline_fields_are_exactly_the_ten_the_schema_names():
    assert PIPELINE_FIELDS == (
        "id",
        "name",
        "antigen",
        "uniprot_accession",
        "development_stage",
        "phase",
        "source_citation",
        "cancer_type",
        "conditions_verbatim",
        "description",
    )
    for row in load_pipeline()["pipeline"]:
        assert set(row) == set(PIPELINE_FIELDS)


def test_no_pipeline_row_was_promoted_to_approved(tmp_path):
    """Out of scope, and mechanically so: filling a cancer type is not an approval."""
    data = load_pipeline()
    assert data["scope"]["value"] == "pipeline_investigational"
    for row in data["pipeline"]:
        assert row["development_stage"]["value"] in ("clinical", "preclinical")
    raw = json.loads(PIPELINE_V1.read_text(encoding="utf-8"))
    raw["pipeline"][0]["development_stage"] = _envelope(value="approved")
    with pytest.raises(CatalogError, match="development_stage"):
        load_pipeline(_write(tmp_path / "p.json", raw))


# ------------------------------------------------------------- the log leads it


def test_d140_entry_exists_in_the_living_log():
    """The check is the HEADING, not a citation of it (D-062 / method-note item 7).

    PR #90 named D-062 in its title and shipped no `### D-062`; thirteen later
    citations then pointed at nothing. So this asserts the entry itself, anchored to
    a line start so a quotation of the heading inside another entry cannot satisfy it
    (D-136 amendment 1).
    """
    log = DOCS_README.read_text(encoding="utf-8")
    assert re.search(r"^### D-140 — The ADC Pipeline shelf gets a cancer type", log, re.M)
    assert len(re.findall(r"^### D-140 —", log, re.M)) == 1
    # ⚠ Exactly one. This entry shipped as `### D-139` and collided with the
    # served-path flip, which merged first; the renumber has to leave no twin behind.
    assert len(re.findall(r"^### D-139 —", log, re.M)) == 1
    assert re.search(r"^### D-139 — The served PDB stops being a constant", log, re.M)
    # ⚠ Widened at D-141 by ADDING, never by a `>=`. This entry barred `### D-141`
    # while it was the newest; the confidence-Kabsch lander then claimed 141 (it read
    # the open-PR list *after* #263 was published, so it saw 140 held and skipped it —
    # the clean version of the duplicate this entry records). #263 merging reddened
    # the bar exactly as intended, so 141 is named here and `### D-144` takes the bar.
    # ⚠ Widened again at D-143 by ADDING: the Track B structural-only copy entry claimed 142
    # off `30f402f` after `grep` (highest written = 141) and `gh pr list --state open`
    # (#222 / #200 / #197, none spending a `D-1NN`), and was then renumbered to 143 by owner
    # ruling (2026-09-09) with 142 left HELD and barred below. It touches no pipeline field.
    assert re.search(r"^### D-141 — The gate had nothing to answer with", log, re.M), (
        "D-141 must be the confidence-Kabsch lander entry, not some other entry "
        "that took the number"
    )
    assert re.search(r"^### D-143 — Track B stops claiming a composite", log, re.M), (
        "D-143 must be the Track B structural-only copy entry, not some other entry "
        "that took the number"
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
    assert "\n### D-145" not in log, (
        "D-145 is the next free integer and must stay unspent until an entry claims it "
        "by name here — never admitted by a `>=`"
    )


def test_the_log_entry_records_the_counts_it_reports():
    """⚠ Bounded by the NEXT heading, whatever it is — never by a named neighbour.

    D-135's and D-136's suites both shipped a slice bounded by the entry that
    happened to be below at branch time, and both silently widened when something
    merged between them. That defect is not re-imported here.
    """
    log = DOCS_README.read_text(encoding="utf-8")
    rest = log.split("\n### D-140 —", 1)[1]
    next_heading = re.search(r"\n### D-\d", rest)
    entry = rest[: next_heading.start()] if next_heading else rest
    assert "5 of 10" in entry
    assert "4 of 10" in entry
    assert "D-093" in entry
    assert "D-136 decision 8" in entry
    # The slice really is only D-140's own entry.
    assert "contents rail" not in entry


def test_the_log_records_that_d136_decision_8_was_amended_not_ignored():
    """⚠⚠ A reversal has to be written down where the reversed rule lives.

    D-136 decision 8 says the pipeline schema admits no indication field, and a test
    in its suite enforced that. D-140 changes it. The failure mode being guarded is
    the silent one: change the code, redden the old test, edit the old test, and leave
    the log claiming the opposite of what ships.
    """
    log = DOCS_README.read_text(encoding="utf-8")
    d136 = re.search(r"^### D-136 —", log, re.M)
    d135 = re.search(r"^### D-135 —", log, re.M)
    assert d136 and d135
    entry = log[d136.start(): d135.start()]
    assert "D-140" in entry, "D-136's own entry must record that D-140 amended it"
