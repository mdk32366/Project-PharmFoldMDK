"""D-149 — the SEER official-aggregate US cancer burden surface.

⚠⚠ **EVERY TEST HERE IS RED-CAPABLE AGAINST A SPECIFIC WAY THIS SURFACE COULD LIE**, not against a
generic "does it work". The failure modes it was built to refuse, each with a test:

- a figure served without its **US-only** qualifier (`D-093 amendment 6`'s US-only clause);
- a **SEER incidence count compared against a US mortality count** — Lung carries 662,721 deaths
  against 434,448 cases, impossible in one population and ordinary in two;
- **incidence ranked by count**, which would order a registry-area number as though it were national;
- a **`sex` trusted from the request** rather than read from the source's answer — the 72x breast trap;
- `Melanoma of the Skin` relabelled **"skin cancer"**, which SEER's own category name excludes;
- a **GLOBOCAN** figure appearing at all;
- the **NCI attribution** going missing, including on a fresh database with no run;
- a **protein, accession, gene, score or rank** reaching a disease-level surface, or a **join** to any
  ranking table;
- the **loader reaching the network**, which would make a served figure a function of fetch time.

⚠ The id discipline is at the bottom: `### D-149` is claimed by name, `### D-148` is a `RESERVED.md`
HOLD for the trafficking Spec and stays barred, and `### D-150` takes the next-free bar.
"""

from __future__ import annotations

import ast
import json
import pathlib
import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from core.cancer_burden import (
    ATTRIBUTION,
    STATISTICS,
    US_ONLY_DISCLAIMER,
    US_ONLY_SHORT,
    is_primary_sex_stratum,
)
from db.models import Base

import scripts.seer_cancer_burden as loader

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
TOKEN = "test-token"

ARTEFACT = ROOT / "data" / "burden" / "seer_us_cancer_burden.v1.csv"
PROVENANCE = ROOT / "data" / "burden" / "seer_us_cancer_burden.provenance.json"

#: ⚠ An accession-shaped token. Every join in this project is keyed by accession, so this is the
#: shape that would appear if a protein ever reached this surface.
ACCESSION_RE = re.compile(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b")


class _DummyQueue:
    def claim(self, *a, **k):
        return None


@pytest.fixture(scope="module")
def rows():
    return loader.read_rows()


@pytest.fixture
def engine(rows):
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    loader.persist(eng, rows)
    return eng


@pytest.fixture
def empty_engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _client(engine, tmp_path) -> TestClient:
    app = create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN,
                     queue=_DummyQueue())
    return TestClient(app, raise_server_exceptions=True)


# ─────────────────────────────── the committed artefact and its pin ──────────────────


def test_the_artefact_and_its_provenance_sidecar_both_exist_and_agree():
    """⚠ `A-017` — the fixture must reach the code under test. A row count of zero would make every
    scan below pass for the wrong reason."""
    assert ARTEFACT.is_file() and PROVENANCE.is_file()
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert loader.read_rows.__module__  # the loader is importable at all
    got = loader.read_rows()
    assert len(got) == int(prov["artefact_rows"]) == 174
    assert len({(r["statistic"], r["seer_site_id"], r["sex"]) for r in got}) == len(got), (
        "the artefact grain is (statistic, site, sex); a duplicate means one figure is served twice")


def test_the_release_is_pinned_and_it_is_the_official_product_not_the_preliminary_one():
    """⚠⚠ `D-093 amendment 6` disqualified the Preliminary Incidence Estimates because the registry
    selection is **re-derived each year while the product name never changes** — one name over N
    populations. A pinned release is the only thing that makes that distinction checkable."""
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert prov["release"] == "SEER November 2025 Submission"
    assert prov["release_application_updated"] == "2026-04-22"
    assert "Preliminary" in prov["excluded_product"]
    assert "re-derived each year" in prov["excluded_product"]
    assert "Recent Rates" in prov["graph_type"]
    assert prov["geography"] == "United States only"


def test_the_loader_refuses_a_hash_mismatch_rather_than_loading_whatever_is_on_disk(tmp_path):
    """⚠⚠ `A-016` — any red proves the assertion bites, and this is the assertion that stands
    between the repository and a figure nobody reviewed. A changed artefact is a NEW INGEST of a
    DIFFERENT release, not a re-run of the pinned one."""
    from core.source_pin import IngestRefused
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    tampered = tmp_path / "seer_us_cancer_burden.v1.csv"
    text = ARTEFACT.read_text(encoding="utf-8")
    tampered.write_text(text.replace("662721", "999999"), encoding="utf-8")
    with pytest.raises(IngestRefused, match="does not match its pinned sha256"):
        loader.read_rows(artefact=tampered, provenance=prov)


def test_the_loader_cannot_reach_the_network_at_all():
    """⚠⚠ THE SEPARATION IS THE DECISION, AND IT IS CHECKED AT IMPORT GRANULARITY. If the loader
    could fetch, a serving host could silently re-derive a figure this repository was never reviewed
    with — and the sha256 pin would be pinning nothing, because the fetch would precede it.

    ⚠ The check is on the **parsed imports**, not a substring: a comment naming `urllib` is the
    separation being documented, and matching prose would make the guard fire on its own docstring.
    """
    src = (ROOT / "scripts" / "seer_cancer_burden.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    forbidden = {"urllib", "requests", "httpx", "http", "socket", "aiohttp", "urllib3"}
    assert not (imported & forbidden), (
        f"the LOADER imports a network client {sorted(imported & forbidden)} — it must read the "
        f"committed artefact only; scripts/fetch_seer_burden.py is the network half")
    assert "seer.cancer.gov" not in src, "the loader names a host"
    # ⚠ and the fetcher DOES reach the network — otherwise this test is vacuous, passing because
    # nothing in the tree fetches at all rather than because the halves are separated.
    fetcher = (ROOT / "scripts" / "fetch_seer_burden.py").read_text(encoding="utf-8")
    assert "seer.cancer.gov" in fetcher and "urllib.request" in fetcher


# ─────────────────── ⚠⚠ US-ONLY: the obligation that must not be droppable ───────────


def test_us_only_is_on_the_header_in_meta_and_on_every_single_row(engine, tmp_path):
    """⚠⚠ ON EVERY ROW, DELIBERATELY. *"Lung cancer kills 662,721 people"* is a sentence about the
    United States that reads as a sentence about the world, and a row lifted out of a list into a
    slide, a notebook or a spreadsheet takes only what is on it."""
    body = _client(engine, tmp_path).get("/api/cancer-burden").json()
    assert body["result_status"] == "valid"
    assert body["meta"]["us_only"] == US_ONLY_DISCLAIMER
    assert "United States only" in body["meta"]["us_only"]
    assert body["meta"]["geography"] == "united_states"
    assert body["rows"], "no rows — the row-level assertion below would be vacuous"
    for row in body["rows"]:
        assert row["disclaimer"] == US_ONLY_SHORT, (
            f"row {row['seer_site_id']}/{row['sex']} carries no US-only qualifier")


def test_us_only_and_the_nci_credit_survive_a_database_with_no_run(empty_engine, tmp_path):
    """⚠⚠ THE `not_run` CASE IS WHERE THE OBLIGATION WOULD BE DROPPED, AND IT IS THE CASE THAT
    SHIPS. No `--load` has run against Fly, so production answers `not_run` today. **A licence
    obligation that appears only once data happens to be loaded is one a fresh database silently
    drops** — and a not-run panel is exactly where a reader goes looking for the number elsewhere.
    """
    client = _client(empty_engine, tmp_path)
    for path in ("/api/cancer-burden", "/api/cancer-burden/meta"):
        body = client.get(path).json()
        assert body["result_status"] == "not_run", path
        assert body["meta"]["us_only"] == US_ONLY_DISCLAIMER, path
        assert body["meta"]["attribution"] == ATTRIBUTION, path
        assert "National Cancer Institute" in body["meta"]["attribution"], path
    # ⚠ and never a 404: `not_run` is a 200 with a stated category (the /api/ranking posture, D-062)
    assert client.get("/api/cancer-burden").status_code == 200


def test_the_nci_attribution_is_stored_beside_the_figures_not_only_rendered(engine):
    """⚠ `D-093 amendment 6` obtained NCI's reuse policy verbatim — *"Credit the National Cancer
    Institute as the source"* — and the owner's 2026-09-09 ruling closed that amendment's
    data-vs-text gap **while leaving this obligation standing**. A UI string is one refactor from
    being dropped with nothing red; a column is not."""
    from sqlalchemy.orm import Session

    from db.models import CancerBurdenRun
    with Session(engine) as s:
        run = s.query(CancerBurdenRun).one()
        assert run.attribution == ATTRIBUTION
        assert run.geography_disclaimer == US_ONLY_DISCLAIMER
        assert run.release == "SEER November 2025 Submission"
        assert run.source_sha256 and len(run.source_sha256) == 64


# ───────── ⚠⚠ THE COUNT TRAP: two populations, and the deaths count is the larger ────


def test_the_two_counts_have_different_populations_and_the_payload_says_so_per_row(engine,
                                                                                  tmp_path):
    """⚠⚠ MEASURED ON THE PINNED RELEASE: Lung and Bronchus carries **662,721 deaths** against
    **434,448 new cases**. More deaths than cases is impossible in ONE population and unremarkable
    in TWO — the deaths are national (NCHS) and the cases cover the SEER registry catchment areas
    only. This test pins the arithmetic that makes the trap real, so nobody later "fixes" the
    apparent inconsistency by making the two counts comparable."""
    body = _client(engine, tmp_path).get("/api/cancer-burden").json()
    lung = {r["statistic"]: r for r in body["rows"]
            if r["seer_site_id"] == 47 and r["sex"] == "both"}
    assert lung["mortality"]["observed_count"] == 662721
    assert lung["incidence"]["observed_count"] == 434448
    assert lung["mortality"]["observed_count"] > lung["incidence"]["observed_count"], (
        "the trap this surface exists to disarm has disappeared from the data — re-check the "
        "populations before assuming it was fixed")
    assert lung["mortality"]["count_population"] == "us_total_nchs"
    assert lung["incidence"]["count_population"] == "seer_registries"
    # the two populations are named on the wire, with the numbers quoted inside
    key = body["meta"]["count_population_key"]
    assert "not the whole United States" in key["seer_registries"]["text"]
    assert "662,721" in key["seer_registries"]["text"]
    assert "434,448" in key["seer_registries"]["text"]
    # ⚠ per-ROW, never a run header
    for row in body["rows"]:
        assert row["count_population"] in ("us_total_nchs", "seer_registries")
    assert "count_population" not in (body["run"] or {})


def test_period_is_per_row_because_two_sites_carry_a_different_one(engine, tmp_path):
    """⚠⚠ `Kaposi Sarcoma` and `Mesothelioma` return mortality for **2019-2023** while the other 32
    sites return **2020-2024** — the source's own `year_range` code says so. A single run-level
    period would have relabelled six rows with a period they do not have, and **nothing would have
    reddened**, because a header is consistent with itself."""
    body = _client(engine, tmp_path).get("/api/cancer-burden?statistic=mortality").json()
    by_period: dict[str, set[str]] = {}
    for row in body["rows"]:
        by_period.setdefault(row["period"], set()).add(row["site_label"])
    assert set(by_period) == {"2020-2024", "2019-2023"}, by_period
    assert by_period["2019-2023"] == {"Kaposi Sarcoma", "Mesothelioma"}
    assert "period" not in (body["run"] or {})
    inc = _client(engine, tmp_path).get("/api/cancer-burden?statistic=incidence").json()
    assert {r["period"] for r in inc["rows"]} == {"2019-2023"}


def test_deaths_rank_by_count_and_incidence_by_rate_and_every_row_states_which(engine, tmp_path):
    """⚠⚠ THE ASYMMETRY IS THE HONESTY, NOT AN INCONSISTENCY. A mortality count is national, so
    *"which cancers kill the most people in the US"* has a real national answer. A SEER incidence
    count is not national, so ranking incidence by count would order a partial-US number as though
    it were a whole-US one."""
    client = _client(engine, tmp_path)
    mort = client.get("/api/cancer-burden?statistic=mortality").json()
    ranked = [r for r in mort["rows"] if r["rank_within_statistic"] is not None]
    assert all(r["rank_basis"] == "observed_count" for r in ranked)
    assert ranked[0]["site_label"] == "Lung and Bronchus"
    assert ranked[0]["observed_count"] == 662721
    counts = [r["observed_count"] for r in ranked]
    assert counts == sorted(counts, reverse=True), "deaths are not ordered by count"

    inc = client.get("/api/cancer-burden?statistic=incidence").json()
    iranked = [r for r in inc["rows"] if r["rank_within_statistic"] is not None]
    assert all(r["rank_basis"] == "rate_per_100k" for r in iranked)
    rates = [r["rate_per_100k"] for r in iranked]
    assert rates == sorted(rates, reverse=True), "incidence is not ordered by rate"
    # ⚠⚠ AND THE ORDERS GENUINELY DIFFER, so the choice of basis is not a tautology. Measured on
    # this release they agree for the first four and diverge at **rank 5**: by RATE, female-only
    # `Corpus and Uterus, NOS` (28.66 per 100,000 WOMEN) outranks `Melanoma of the Skin` (22.34 per
    # 100,000 PEOPLE); by COUNT melanoma is larger. ⚠ The first draft of this test compared only the
    # top three, where the two orders happen to agree — it would have passed while establishing
    # nothing, and rewriting it is what surfaced the sex-scoped denominator now on every row.
    by_count = [r["display_label"] for r in sorted(iranked, key=lambda r: -r["observed_count"])]
    by_rate = [r["display_label"] for r in iranked]
    assert by_rate != by_count, (
        "count order and rate order agree over the WHOLE list on this data, so this test cannot "
        "distinguish them — re-derive it before trusting it")
    assert by_rate[4] == "Corpus and Uterus, NOS (female)", by_rate[:6]
    assert by_count[4] == "Melanoma of the Skin", by_count[:6]
    # ⚠ and every row states what its "per 100,000" is over, which is what makes that divergence
    # legible instead of looking like a bug
    for row in iranked:
        assert row["rate_denominator"] in ("per_100k_people", "per_100k_females",
                                           "per_100k_males")
    assert next(r for r in iranked if r["display_label"] == "Breast (female)")[
        "rate_denominator_label"] == "per 100,000 women"


def test_all_cancer_sites_combined_is_served_flagged_and_never_ranked(engine, tmp_path):
    """⚠ `F-031`: two populations in one table. `All Cancer Sites Combined` CONTAINS every other
    site, so ordering it beside them would be a ranking over two populations. It is served — a
    reader owed *"which kills the most"* is owed the denominator — and flagged so nothing ranks it.
    """
    body = _client(engine, tmp_path).get("/api/cancer-burden?statistic=mortality").json()
    ctx = [r for r in body["rows"] if r["is_context_row"]]
    assert ctx, "the denominator row is missing entirely"
    both = next(r for r in ctx if r["sex"] == "both")
    assert both["observed_count"] == 3049139
    for row in ctx:
        assert row["rank_within_statistic"] is None
        # ⚠ an unranked row states WHY rather than carrying a bare null (F-023's defect)
        assert row["not_ranked_because"] == "all_cancer_sites_combined_is_a_denominator"
    ranked = [r for r in body["rows"] if r["rank_within_statistic"] is not None]
    assert all(not r["is_context_row"] for r in ranked)
    # ⚠ and the denominator really is larger than its largest component, or it is not a denominator
    assert both["observed_count"] > max(r["observed_count"] for r in ranked)


# ────────────── ⚠⚠ THE SEX TRAP: 72x, and announced only in a response key ──────────


def test_the_sex_is_the_sources_answer_and_the_substitutions_are_recorded(engine, tmp_path):
    """⚠⚠ THE DISQUALIFYING FACT OF THIS ENTRY. SEER*Explorer answers a Breast *"Both Sexes"*
    request with the **MALE** figure — rate 0.261793 / 2,457 deaths instead of 18.928734 / 212,409 —
    announcing the substitution only in its response key. A pipeline trusting its own request would
    have ranked breast cancer near the BOTTOM of US cancer deaths on a rate **72x too small**, with
    six decimal places and a confidence interval. `F-047`'s class.
    """
    body = _client(engine, tmp_path).get("/api/cancer-burden?statistic=mortality").json()
    breast = {r["sex"]: r for r in body["rows"] if r["seer_site_id"] == 55}
    assert set(breast) == {"female", "male"}, (
        "SEER*Explorer publishes NO both-sexes breast figure; a `both` row here would be invented")
    assert breast["female"]["observed_count"] == 212409
    assert breast["male"]["observed_count"] == 2457
    # the ratio that makes the trap worth a test rather than a comment
    assert breast["female"]["rate_per_100k"] / breast["male"]["rate_per_100k"] > 70
    assert breast["male"]["sex_substituted"] is True, (
        "the male breast row is the one the source substituted for a Both-Sexes request; losing "
        "that flag is losing the only record that the substitution happened")
    # ⚠ the label carries the sex, so a row can never be shown as bare "Breast" while holding the
    # female-only figure
    assert breast["female"]["display_label"] == "Breast (female)"
    assert breast["male"]["display_label"] == "Breast (male)"
    # ⚠ and the primary stratum is BOTH sex rows, not the larger one: picking the larger would drop
    # male breast cancer's 2,457 deaths with nothing saying so (F-018/F-020's family)
    assert breast["female"]["is_primary_sex_stratum"] is True
    assert breast["male"]["is_primary_sex_stratum"] is True


def test_no_both_sexes_rate_is_ever_synthesised(rows):
    """⚠⚠ An age-adjusted rate **cannot be summed across sexes** — the standard populations differ.
    So where the source publishes no `both` row, none is invented: a combined breast rate would be a
    number with no source, which is the thing this project has refused most often."""
    published_both = {(r["statistic"], r["seer_site_id"]) for r in rows if r["sex"] == "both"}
    for statistic in STATISTICS:
        assert (statistic, 55) not in published_both, "a both-sexes breast figure was synthesised"
        assert (statistic, 66) not in published_both, "a both-sexes prostate figure was synthesised"
        assert (statistic, 47) in published_both, (
            "lung publishes a both-sexes figure; its absence would mean the fetch lost a stratum")


def test_the_primary_stratum_rule_is_one_function_shared_with_the_loader():
    """⚠ One rule in one place. A second copy in the loader and a third in the route would be two
    more sources with nothing comparing them."""
    assert is_primary_sex_stratum(sex="both", site_has_both_row=True) is True
    assert is_primary_sex_stratum(sex="female", site_has_both_row=True) is False
    assert is_primary_sex_stratum(sex="female", site_has_both_row=False) is True
    assert is_primary_sex_stratum(sex="male", site_has_both_row=False) is True


def test_every_site_publishes_at_least_one_primary_stratum_per_statistic(rows):
    """⚠⚠ A site that ended up with NO primary row would vanish from the ranked table while its
    figures sat in the database — the absent-value defect, in the direction that is invisible."""
    sites = {r["seer_site_id"] for r in rows}
    for statistic in STATISTICS:
        for site in sites:
            primary = [r for r in rows if r["statistic"] == statistic
                       and r["seer_site_id"] == site and r["is_primary_sex_stratum"]]
            assert primary, f"{statistic} site={site} has no primary sex stratum"


# ─────────────────── ⚠⚠ THE SKIN TRAP, AND THE STATED ABSENCES ──────────────────────


def test_seer_melanoma_is_never_relabelled_skin_cancer(engine, tmp_path):
    """⚠⚠ `D-093 amendment 6` called this the dangerous one, and it was right: the other unmappable
    strings fail LOUDLY where a missing mapping is visible, and this one *"would produce a
    confident, plausible, wrong answer"*. SEER's group is literally named *Skin excluding Basal and
    Squamous*, and BCC/SCC — most skin cancers diagnosed in the US — are not in SEER at all."""
    body = _client(engine, tmp_path).get("/api/cancer-burden").json()
    skin = [r for r in body["rows"] if r["seer_site_id"] == 53]
    assert skin
    for row in skin:
        assert row["site_label"] == "Melanoma of the Skin"
        assert row["recode_group"] == "Skin excluding Basal and Squamous"
        assert "skin cancer" not in row["display_label"].lower()
    # the exclusion is named on the wire, not only in a document
    exclusion = body["meta"]["skin_exclusion"]
    assert "Skin excluding Basal and Squamous" in exclusion
    assert "basal-cell" in exclusion.lower() and "squamous-cell" in exclusion.lower()
    assert "never calls it 'skin cancer'" in exclusion


def test_globocan_appears_only_as_a_stated_refusal_and_never_as_a_figure(engine, tmp_path):
    """⚠⚠ `D-093 amendment 6` read IARC's terms and got the OPPOSITE answer to NCI's — *"IARC
    exercises copyright… All rights are reserved"*, three written-permission triggers, unilaterally
    mutable terms and an indemnification. ⚠ The absence is a stated CATEGORY, never a blank: an
    unexplained absence reads as an oversight, and an oversight gets "fixed" by someone who does not
    know why it is there."""
    body = _client(engine, tmp_path).get("/api/cancer-burden").json()
    assert "ABSENT rather than zero" in body["meta"]["globocan"]
    assert "reserves all rights" in body["meta"]["globocan"]
    # ⚠ and no ROW is a GLOBOCAN figure — the word appears in the refusal and nowhere else
    flat = json.dumps(body["rows"])
    assert "GLOBOCAN" not in flat and "globocan" not in flat.lower()
    assert "IARC" not in flat
    for row in body["rows"]:
        assert row["count_population"] in ("us_total_nchs", "seer_registries"), (
            "a row carries a non-US population — worldwide burden is ABSENT, not ingested")


def test_the_crosswalk_is_refused_and_its_four_failures_are_named(engine, tmp_path):
    """⚠⚠ The protein card's burden slot points HERE for *"which and why"*, so the named list has to
    exist. A pointer to something never written is `D-062`'s defect shape.

    ⚠ And the refusal states the REAL reason, which `D-093 amendment 6` corrected itself to the same
    day it was written: not a missing mapping table, but that HPA's `Cancer` column interleaves
    ICD-O's two independent axes while SEER's own recode mixes them too.
    """
    meta = _client(engine, tmp_path).get("/api/cancer-burden/meta").json()["meta"]
    assert set(meta["unmappable_hpa_sites"]) == {
        "carcinoid", "skin cancer", "head and neck", "urothelial"}
    for name, why in meta["unmappable_hpa_sites"].items():
        assert len(why) > 40, f"{name} is listed with no reason"
    assert "two independent axes" in meta["crosswalk_refused"]
    assert "SIBLINGS" in meta["crosswalk_refused"]


def test_the_excluded_product_and_the_excluded_tier_are_both_stated(engine, tmp_path):
    """⚠ Two refusals that would otherwise be invisible: the wrong SEER product, and the controlled
    tier. `D-093 amendment 6` disqualified the first on its own documentation; the second is the
    DUA microdata this build never touched."""
    meta = _client(engine, tmp_path).get("/api/cancer-burden/meta").json()["meta"]
    assert "Preliminary Incidence Estimates are NOT used" in meta["excluded_product"]
    assert "re-derived each year" in meta["excluded_product"]
    assert "Research Data / Research Plus" in meta["excluded_tier"]
    assert "NOT used and is not present" in meta["excluded_tier"]


# ──── ⚠⚠ NO SCORE JOIN: the hard stop, as a property of the tree and of the payload ──


def test_no_protein_accession_gene_score_or_rank_reaches_the_burden_payload(engine, tmp_path):
    """⚠⚠ `D-093` decision 1: burden is a property of a **DISEASE**. This asserts it of the actual
    bytes on the wire, not of an intention — the payload is flattened to text and searched."""
    client = _client(engine, tmp_path)
    # ⚠⚠ THE SCAN READS `rows` AND `run`, NOT `meta`, AND THE REASON IS THAT `meta` IS WHERE THE
    # REFUSALS LIVE. `meta.separation` says *"no burden figure enters structural_score…"* and
    # `meta.deep_learning_position` names `score_model` — a scan over the whole payload fires on the
    # sentences that state the prohibition, which is *"matching the guard's own documentation"*, the
    # trap `tests/test_clinical_layer_prohibitions.py` names of itself. The first draft did exactly
    # that. What must be clean is the DATA.
    for path in ("/api/cancer-burden", "/api/cancer-burden/meta"):
        body = client.get(path).json()
        flat = json.dumps({k: v for k, v in body.items() if k != "meta"})
        assert not ACCESSION_RE.search(flat), f"{path} carries an accession-shaped token"
        for banned in ("structural_score", "score_membrane", "score_ecd", "score_model",
                       "mean_plddt", "analysis_id", "ranking_run_id"):
            assert banned not in flat, f"{path} carries {banned}"
        # ⚠ and `meta` mentions them ONLY inside a refusal — asserted, not assumed, so a figure
        # smuggled into `meta` would still be caught.
        if body.get("meta"):
            assert not ACCESSION_RE.search(json.dumps(body["meta"])), (
                f"{path} meta carries an accession-shaped token")
            assert "joined to nothing" in body["meta"]["separation"]
            assert "No burden figure enters structural_score" in body["meta"]["separation"], (
                "the separation must name structural_score in order to refuse it")
            assert "does NOT join" in body["meta"]["deep_learning_position"]
        # ⚠ `rank_within_statistic` is an ORDER WITHIN THIS TABLE, never a target rank. The bare
        # key `rank` is what a consumer would join on, and it must not exist.
        for row in body.get("rows", []):
            assert "rank" not in row, "a bare `rank` key invites a join against a target ranking"
            assert "accession" not in row and "gene" not in row


def test_the_burden_tables_have_no_foreign_key_out_of_the_disease_layer():
    """⚠⚠ THE ABSENT JOIN IS THE PRODUCT DECISION, AND A SCHEMA IS WHERE IT IS ENFORCED. A shared
    key would be one `JOIN` away from the `cancer x structure` composite `D-143`, `D-144` and
    `D-146` each refused."""
    from db.models import CancerBurdenRun, CancerBurdenStat
    for model in (CancerBurdenRun, CancerBurdenStat):
        for col in model.__table__.columns:
            for fk in col.foreign_keys:
                target = fk.target_fullname.split(".")[0]
                assert target == "cancer_burden_runs", (
                    f"{model.__tablename__}.{col.name} points at {target} — the burden layer must "
                    f"reference nothing outside itself")
            assert col.name not in ("accession", "gene", "gene_name", "analysis_id",
                                    "structural_score", "rank"), (
                f"{model.__tablename__} carries a protein-path column {col.name}")


def test_the_migration_adds_two_tables_and_alters_nothing():
    """⚠ Additive as a property of the file, not a promise in a commit message."""
    src = (ROOT / "db" / "migrations" / "versions" / "0013_cancer_burden.py").read_text(
        encoding="utf-8")
    assert 'revision: str = "0013_cancer_burden"' in src
    assert 'down_revision: Union[str, None] = "0012_census_structural_rank"' in src
    # ⚠⚠ `upgrade()` ONLY. `downgrade()` MUST call `op.drop_table` — that is what a reversible
    # migration is — so scanning the whole file would have barred the correct implementation. The
    # first draft of this test did exactly that and reddened on `downgrade`: a guard aimed at the
    # wrong half of the file, which is the `F-050` family it is written to avoid.
    tree = ast.parse(src)
    up = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "upgrade")
    calls = [f"{ast.unparse(n.func)}" for n in ast.walk(up) if isinstance(n, ast.Call)]
    assert calls.count("op.create_table") == 2, calls
    for forbidden in ("op.alter_column", "op.drop_column", "op.drop_table", "op.add_column",
                      "op.execute", "op.rename_table"):
        assert forbidden not in calls, (
            f"0013's upgrade() calls {forbidden} — it must be purely additive")
    # ⚠ and `downgrade()` really does reverse it, or the migration is not reversible at all
    down = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "downgrade")
    dcalls = [f"{ast.unparse(n.func)}" for n in ast.walk(down) if isinstance(n, ast.Call)]
    assert dcalls.count("op.drop_table") == 2, dcalls


def test_the_structural_rank_formula_and_its_route_are_untouched_by_this_entry():
    """⚠ `D-149`'s hard stop: no `structural_score` change. Asserted against `D-144`'s own region
    pins rather than restated — one source for the claim, shared with `D-145`'s and `D-146`'s
    guards."""
    from _d144_surface import (
        D144_OWN_FILES,
        D144_SHARED_REGIONS,
        region_digest,
        whole_file_digest,
    )
    for rel, digest in D144_OWN_FILES.items():
        assert whole_file_digest(rel) == digest, f"{rel} moved — D-149 changes no formula"
    for rel, (_s, _t, expected) in D144_SHARED_REGIONS.items():
        assert region_digest(rel) == expected, f"D-144's region of {rel} moved"


def test_the_burden_surface_is_not_reachable_from_the_scoring_modules():
    """⚠ `D-079` amendment 1 ruling 5's wall at file granularity. The reverse direction of
    `tests/test_clinical_layer_prohibitions.py`'s import check: not only must the protein path not
    import the burden surface, the burden surface must not import the scoring path either."""
    for rel in ("core/cancer_burden.py", "app/cancer_burden_read.py",
                "scripts/seer_cancer_burden.py"):
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        for banned in ("core.scorer", "core.features", "core.census_structural",
                       "app.census_structural_read", "app.reads", "app.clinical_read"):
            assert banned not in modules, f"{rel} imports {banned}"


# ─────────────────────────── the dedicated surface, not a buried panel ──────────────


def test_the_ui_route_is_its_own_top_level_landmark_and_not_on_a_scoring_page():
    """⚠⚠ ITS OWN ROUTE IS THE PRODUCT DECISION. A burden figure on Census or Scorer is one glance
    from being read as an input to the score. This asserts the placement rather than trusting it."""
    app_jsx = (ROOT / "ui" / "src" / "App.jsx").read_text(encoding="utf-8")
    assert 'path="/cancer-burden"' in app_jsx
    assert '<NavLink to="/cancer-burden">' in app_jsx
    assert "CancerBurdenView" in app_jsx
    view = ROOT / "ui" / "src" / "components" / "CancerBurdenView.jsx"
    assert view.is_file()
    # ⚠ and the burden component is imported by NOTHING else — not Census, not Scorer, not Method
    for name in ("CensusView.jsx", "CensusTable.jsx", "ScorerView.jsx", "MethodNote.jsx",
                 "Story.jsx", "TargetList.jsx"):
        other = (ROOT / "ui" / "src" / "components" / name)
        if other.is_file():
            assert "CancerBurdenView" not in other.read_text(encoding="utf-8"), (
                f"{name} renders the burden surface — it must be its own page")


def test_the_two_routes_are_declared_in_the_architecture_picture():
    """⚠ `D-051`: a live route the picture does not draw is a picture that is false.
    `tests/test_architecture_contract.py` pins the set both ways; this states that THIS entry's
    routes are in it."""
    model = json.loads((ROOT / "ui" / "src" / "system-model.json").read_text(encoding="utf-8"))
    paths = {r["path"] for group in model["routes"].values() for r in group}
    assert "/api/cancer-burden" in paths
    assert "/api/cancer-burden/meta" in paths


def test_the_protein_card_links_to_the_surface_and_gains_no_figure():
    """⚠⚠ THE FLIP `D-149` MAKES, AND ITS LIMIT. `ClinicalEdges` said *"we do not have that data"*,
    which became FALSE the moment the artefact landed — the figures ARE held. But `D-093` decision 1
    still bars a protein-level burden field, so the card gains a **route** and never a **number**."""
    src = (ROOT / "ui" / "src" / "components" / "ClinicalEdges.jsx").read_text(encoding="utf-8")
    assert '"/cancer-burden"' in src or "'/cancer-burden'" in src
    assert "survival is not held at all" in src.lower(), (
        "/cancer-burden holds no survival statistic, so survival must be refused rather than linked")
    # ⚠⚠ THE RENDERED COPY, NOT THE COMMENTS. The component's comment block QUOTES the false
    # sentence as provenance — recording what was wrong is the record working — so a whole-file
    # substring check fires on the documentation of the fix. The first draft did exactly that. JSX
    # comments here are `{/* … */}` blocks, so they are stripped before the copy is read.
    rendered = re.sub(r"\{/\*.*?\*/\}", "", src, flags=re.S)
    rendered = re.sub(r"^\s*//.*$", "", rendered, flags=re.M)
    assert "we do not have that data" not in rendered, (
        "the false sentence is RENDERED again — US incidence and deaths ARE held and ARE served")
    assert "how many is being measured" not in rendered, (
        "D-093 amendment 6 MEASURED the failures; this renders a measurement as still pending")
    # ⚠ and the provenance really is kept in the comments, or the flip lost its own record (D-129-C)
    assert "we do not have that data" in src, (
        "the superseded sentence must stay quoted in the comment as provenance, not be erased")


def test_the_bare_backspace_regex_defect_is_absent_from_the_tree():
    """⚠⚠ FOUND WHILE FLIPPING THAT COPY, AND KEPT AS A GUARD BECAUSE IT PASSED FOR THE WRONG REASON
    ON EVERY RUN SINCE IT WAS WRITTEN. A `not.toMatch(/<BS>…/)` holding a literal backspace byte
    (0x08) where `\\b` was intended cannot match ordinary text, so the bar was decoration — the
    vacuity `tests/test_clinical_layer_prohibitions.py`'s own docstring names of itself.

    ⚠ Two files carried it and no others; both are repaired. This test is what stops a third.
    """
    offenders = []
    for pattern in ("*.py", "*.js", "*.jsx"):
        for path in ROOT.rglob(pattern):
            rel = str(path.relative_to(ROOT))
            if "node_modules" in rel or rel.startswith(".venv") or rel.startswith(".git"):
                continue
            if b"\x08" in path.read_bytes():
                offenders.append(rel)
    assert not offenders, (
        "a literal backspace byte (0x08) is in a source file — almost certainly a `\\b` regex "
        f"boundary that was eaten by a shell heredoc, making its assertion vacuous: {offenders}")


# ─────────────────────────────── the living log and the id discipline ───────────────


def _d149_entry() -> str:
    """The D-149 entry only, bounded by the next `### ` heading whatever it is — an unmerged
    neighbour may land between this entry and D-147 (the D-141 boundary lesson)."""
    start = LOG.index("\n### D-149 —") + 1
    nxt = re.search(r"^### (?!D-149\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_the_entry_exists_and_leads_with_the_disqualifying_fact():
    entry = _d149_entry()
    assert re.match(r"^### D-149 — The project gets a cancer burden surface of its own", entry)
    lowered = _flat(entry).lower()
    # ⚠ the disqualifying fact is in the TITLE, not buried in the body
    head = _flat(entry.splitlines()[0]).lower()
    assert "male" in head and "72" in head
    for claim in ("2,457", "212,409", "662,721", "434,448", "3,049,139",
                  "seer november 2025 submission", "2026-04-22",
                  "2020-2024", "2019-2023",
                  "skin excluding basal and squamous",
                  "kaposi sarcoma", "mesothelioma"):
        assert claim in lowered, f"the entry does not state {claim!r}"


def test_the_entry_records_the_owner_ruling_and_names_the_artefact_it_is_filed_in():
    """⚠ `D-016`: every claim names how it is known. A ruling recorded only inside the entry it
    authorises is a ruling with no independent existence — the pointer-not-proof shape."""
    entry = _flat(_d149_entry())
    owner_file = ROOT / "docs" / "OWNER-2026-09-09-D-093-amd6-seer-aggregates-cleared.md"
    assert owner_file.is_file(), "the entry names an owner file that does not exist"
    assert "OWNER-2026-09-09-D-093-amd6-seer-aggregates-cleared.md" in entry
    assert "fcfc41c2" in entry, "the NCI email is a scar and is recorded with its id"
    assert "scar" in entry.lower() and "not a gate" in entry.lower()
    text = _flat(owner_file.read_text(encoding="utf-8"))
    assert "US Government, public domain" in text
    assert "still out" in text, "the DUA microdata and GLOBOCAN holds must be restated"
    assert "GLOBOCAN" in text and "Research Data" in text


def test_the_entry_carries_a_deep_learning_justification_and_the_honest_half():
    """CLAUDE.md's prime directive. ⚠⚠ The honest answer here is that there is NO deep learning on
    this surface, and the load-bearing claim is the REFUSAL to join to the one place there is."""
    lowered = _flat(_d149_entry()).replace("**", "").lower()
    assert "deep-learning justification" in lowered
    assert "esmfold" in lowered and "plddt" in lowered and "score_model" in lowered
    assert "runs no model" in lowered, "the entry must state that this surface adds no deep learning"
    assert "refusal" in lowered


def test_the_entry_states_what_it_cannot_establish():
    lowered = _flat(_d149_entry()).lower()
    assert "cannot establish" in lowered
    assert "no test in this repository contacts the deployed application" in lowered
    assert "not_run" in lowered
    # ⚠ the recode_group placements are Code's own and are recorded as unverified, not measured
    assert "unverified rather than presented as measured" in lowered


def test_the_architecture_doc_carries_the_new_surface():
    """⚠ CLAUDE.md rule 2 — `ARCHITECTURE.md` is brought current in the same PR, before it is filed.
    """
    flat = _flat(ARCH)
    assert "D-149" in flat
    assert "/api/cancer-burden" in flat
    assert "cancer_burden_stat" in flat
    assert "0013_cancer_burden" in flat
    assert "662,721" in flat and "434,448" in flat, (
        "the count trap must be in the architecture doc, not only in the log")
    assert "NO ACCESSION, NO GENE, NO SCORE, NO RANK, AND NO FOREIGN KEY OUT" in flat


def test_the_next_free_integer_is_named_and_barred_and_148_is_a_held_hole():
    """⚠⚠ THE TWELFTH PASS THROUGH THIS RESOLUTION, and the first where an integer is SKIPPED BY
    DECISION rather than spent or left free.

    **Bar OR name, never neither.** `### D-149` is claimed by name; `### D-148` is a `RESERVED.md`
    HOLD for the trafficking Spec and stays BARRED; `### D-150` takes the next-free bar. ⚠ Nothing
    relaxed to a `>=`: a `>=` here would pass on a log with no entries at all.

    ⚠ The bars are matched WITH their newline, because this file holds such patterns as *data* in
    order to check the others; a newline-less match would find a "bar" in the file whose job is to
    look for one. That is `D-145`'s recorded mistake, not rediscovered here.
    """
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 149 in ids, "this entry did not claim its own integer"
    assert 148 not in ids
    # ⚠⚠ THE 150 BAR BECAME A NAME AT `D-150`, WHICH IS THE RESOLUTION THIS LOG HAS NOW USED
    # THIRTEEN TIMES. `### D-150` (census structure-status honesty) claimed the integer this entry
    # had barred, so the bar is not deleted and is not relaxed to a `>=` — it becomes the stronger
    # statement that 150 is SPENT and named, and the bar moves one integer along to 151.
    assert 150 in ids, (
        "D-150 was spent by the census structure-status honesty surface; this assertion barred it "
        "and must now NAME it — never delete a bar, and never relax one to a `>=`")
    # ⚠⚠ AND THE 151 BAR BECAME A NAME AT `D-151`, WHICH IS THE FOURTEENTH PASS THROUGH THIS
    # RESOLUTION. `### D-151` (the owner UI-polish ship — the Initial Targets label, the Kathad DOI
    # anchor and the census layout) claimed the integer this entry had barred, so the bar is not
    # deleted and is not relaxed to a `>=` — it becomes the stronger statement that 151 is SPENT
    # and named, and the bar moves one integer along to 152.
    assert 151 in ids, (
        "D-151 was spent by the owner UI-polish ship; this assertion barred it and must now NAME "
        "it — never delete a bar, and never relax one to a `>=`")
    # ⚠⚠ THE 152 BAR BECAME A NAME AT `D-152`, AND THE BAR IS NEITHER DELETED NOR RELAXED. 152 was
    # not merely the next free integer here — `D-153` SKIPPED it and converted it into a HOLD for
    # the concurrent sitewide-layout lane (owner instruction, 2026-09-09). That lane has now claimed
    # it: `### D-152` applies the D-151 census layout pattern to /targets, /coverage, /scorer,
    # /cancer-burden and /adcs. So the bar becomes the stronger statement that 152 is SPENT and
    # named. ⚠ **148 stays barred** — the trafficking hold is unchanged — and **the next-free
    # pointer does NOT move here**, because `D-153` already moved it past 152 to 154.
    assert 152 in ids, (
        "D-152 was spent by the surface-navigation ship, which is the lane D-153 held it for; "
        "this assertion barred it and must now NAME it — never delete a bar, and never relax one "
        "to a `>=`")
    assert 153 in ids, "D-153 spent 153 in the burden-loader bake"
    assert 154 not in ids
    # the two entries this one is built beside, NAMED so a rename cannot pass silently
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on", LOG, re.M)
    assert re.search(r"^### D-147 — The census rank stops presenting a loop as an ectodomain",
                     LOG, re.M)
    assert re.search(r"^### D-150 — The census surface stops answering three questions with one word",
                     LOG, re.M)
    assert re.search(r"^### D-151 — Three owner UI complaints, one ship", LOG, re.M)
    assert "\n### D-148" not in LOG, (
        "D-148 is a RESERVED HOLD for the trafficking Spec and must stay unspent until that Spec "
        "claims it by name — never admitted by a `>=`")
    assert "\n### D-154" not in LOG, (
        "D-154 is the next free integer and must stay unspent until an entry claims it by name "
        "— never admitted by a `>=`")


def test_the_reserved_map_holds_148_bars_150_and_the_pointer_skips_the_hold():
    """⚠⚠ MARKER-SAFE, and the reason is mechanical rather than stylistic: this suite locates the
    D-148 row with `re.search(r"^\\| \\*\\*D-148\\*\\*", …)`, so striking it to `~~**D-148**~~` when
    the trafficking Spec lands would break this guard instead of satisfying it. The `D-142`,
    `D-145` and `D-146` rows each record the same trap of themselves."""
    assert re.search(r"^\| \*\*D-148\*\*", RESERVED, re.M), (
        "D-148 is cited in order to bar it, so it must be a RESERVED row or the citation invariant "
        "has a hole indistinguishable from D-062's")
    row148 = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-148**"))
    assert "trafficking" in row148.lower(), "the 148 hold does not say what it is held FOR"
    assert "Original reservation text" in row148, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)")
    # ⚠ AT LINE START, not anywhere in the file. The 148 cell EXPLAINS that its marker must not be
    # struck, so it necessarily contains the struck form as a quotation — a substring check fires on
    # the row's own warning about itself. `F-024`: match the thing you mean.
    assert not re.search(r"^\| ~~\*\*D-148\*\*~~", RESERVED, re.M), (
        "the D-148 marker is struck through; that breaks this suite's lookup instead of "
        "satisfying it")
    # ⚠⚠ THE 150 ROW SURVIVES ITS OWN SPENDING, AND MARKER-SAFE IS WHY THIS LOOKUP STILL WORKS.
    # `D-150` was written on 2026-09-09 and its row was RETIRED IN PLACE — ✅ WRITTEN recorded
    # inside the cell, the original reservation text kept as provenance (D-129-C), and the literal
    # `| **D-150** |` marker deliberately NOT struck to `~~**D-150**~~`. Striking it would have
    # broken this line rather than satisfied it, which is the trap the D-142 / D-145 / D-146 /
    # D-147 rows each record of themselves, and which the 150 row now records of itself too.
    assert re.search(r"^\| \*\*D-150\*\*", RESERVED, re.M), (
        "D-150 is cited here, so it must remain a RESERVED row — retiring a row by deleting or "
        "striking it opens a citation hole indistinguishable from D-062's")
    row150 = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-150**"))
    assert "WRITTEN" in row150, "the 150 row does not record that the integer was spent"
    assert "Original reservation text" in row150, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)")
    # ⚠⚠ THE 151 ROW SURVIVES ITS OWN SPENDING, AND MARKER-SAFE IS WHY THIS LOOKUP STILL WORKS.
    # `D-151` was written on 2026-09-09 and its row was RETIRED IN PLACE — ✅ WRITTEN recorded
    # inside the cell, the original reservation text kept as provenance (D-129-C), and the literal
    # `| **D-151** |` marker deliberately NOT struck. Striking it would have broken this line
    # rather than satisfied it.
    assert re.search(r"^\| \*\*D-151\*\*", RESERVED, re.M), (
        "D-151 is cited here, so it must remain a RESERVED row — retiring a row by deleting or "
        "striking it opens a citation hole indistinguishable from D-062's")
    row151 = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-151**"))
    assert "WRITTEN" in row151, "the 151 row does not record that the integer was spent"
    assert "Original reservation text" in row151, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)")
    assert re.search(r"^\| \*\*D-152\*\*", RESERVED, re.M), (
        "the bar moved to 152, so 152 must be a RESERVED row")
    # ⚠⚠ THE POINTER MOVES IN THE SAME COMMIT THAT SPENDS THE INTEGER, AND IT SKIPS THE HOLD.
    # A reserved integer is not a free one — that is this file's whole purpose.
    # ⚠⚠ FLIPPED IN PLACE AT `D-153`, NEVER DELETED, AND IT NOW SKIPS **TWO** HOLDS. `D-153` spent
    # 153 (the D-149 burden loader baked into the serving image — this entry's own loader, which
    # `D-149` shipped without) and deliberately did NOT take 152, because 152 became a HOLD for the
    # concurrent sitewide-layout lane while 148 remains the trafficking hold. So *"next free"* means
    # the lowest AVAILABLE integer, 154, and not the lowest unwritten one.
    assert "Next free `D-` integer: **`D-154`**" in RESERVED
    assert "Next free `D-` integer: **`D-153`**" not in RESERVED
    assert "Next free `D-` integer: **`D-152`**" not in RESERVED
    assert "Next free `D-` integer: **`D-151`**" not in RESERVED
    assert "Next free `D-` integer: **`D-150`**" not in RESERVED
    assert "Next free `D-` integer: **`D-148`**" not in RESERVED
    assert "Next free `D-` integer: **`D-147`**" not in RESERVED


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ `RESERVED.md`'s own command, run rather than quoted. **Read the output, not an exit code**:
    the only passing result is that nothing NEW is unresolved. `D-131` (the suffix half of
    `### D-130-B / D-131`) and `F-067` (open in #222) are pre-existing and untouched."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}")
