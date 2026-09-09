"""D-142 — the `/targets` Cancer association + Description columns. Every one of these can go red.

⚠⚠ **THE FIELD THAT LOOKED LIKE THE DESCRIPTION IS THE GENE SYMBOL, AND THIS FILE PROVES IT
RATHER THAN ASSERTING IT.** The GO named ``label`` as the likely Description and asked for it to be
verified. It is not: ``data/cohort_82_ecd.csv`` carries ``label`` and ``protein_name`` as separate
columns and ``label == gene`` on all 82 rows. Shipping ``label`` under a *Description* header would
have rendered ``ADAM17`` in a cell whose header promised a description, 82 times.

⚠⚠ **AND THE TRAP IS BUILT INTO THE PROJECT.** On the CENSUS — the other population, the other
supplier — ``label`` really *is* the protein name (``data/census/census_labels.csv``), and
``CensusTable.jsx`` renders it under the header ``Protein``. One key, two populations, two
meanings: ``F-049``'s family. So this suite pins **both** readings, because a test that only
checked the cohort would leave the next reader free to make the same inference from the census.

⚠ **The second finding is a licence one and it is older than this PR.** ``/api/associations`` served
no attribution of any kind, while ``CancerAssociations.jsx`` read ``data.attribution`` — so the
D-053 card has rendered HPA-derived ``qh_score`` values with **no citation** since D-053, and
``HpaAttribution.test.jsx``'s PC3 guard could not see it because the file *imports* the attribution
and the **prop** was ``undefined``. The route now serves one block per covered symbol.

⚠ **Nothing here is a fold claim, a seam claim, a ranking change or a new cancer datum.** No
threshold moves, no scorer runs, the pre-registered pLDDT floor of 50 is untouched, and the D-053
grid is consumed exactly as it is served.
"""
from __future__ import annotations

import csv
import gzip
import inspect
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import reads
from app.main import create_app
from app.read_routes import _association_attributions
from core.cancer_associations import load_associations
from core.manifest import build_manifest
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
ECD_CSV = ROOT / "data" / "cohort_82_ecd.csv"
CENSUS_LABELS = ROOT / "data" / "census" / "census_labels.csv"
TARGET_LIST = (ROOT / "ui" / "src" / "components" / "TargetList.jsx").read_text(encoding="utf-8")
CENSUS_TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
ASSOC_CARD = (
    ROOT / "ui" / "src" / "components" / "CancerAssociations.jsx"
).read_text(encoding="utf-8")
SEARCH_ROWS = (ROOT / "ui" / "src" / "searchRows.js").read_text(encoding="utf-8")
SUMMARY_MODULE = ROOT / "ui" / "src" / "associationSummary.js"
UI_TEST = ROOT / "ui" / "src" / "components" / "TargetList.columns.test.jsx"
SUMMARY_TEST = ROOT / "ui" / "src" / "associationSummary.test.js"
TOKEN = "test-secret-token"


def _flat(text: str) -> str:
    """⚠ Markdown emphasis and newlines flattened: the log writes ``**not** a description``, and a
    substring check for ``not a description`` would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", ""))


def _rows() -> list[dict[str, str]]:
    with ECD_CSV.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ─────────────────────── the disqualifying fact: `label` is the gene ───────────────────────


def test_the_committed_manifest_keeps_label_and_protein_name_as_separate_columns():
    rows = _rows()
    assert rows, "the cohort CSV is empty"
    assert set(rows[0]) >= {"label", "gene", "protein_name"}


def test_label_equals_gene_on_every_cohort_row_so_it_is_not_a_description():
    """⚠⚠ The measurement the GO asked for, run rather than assumed."""
    rows = _rows()
    assert len(rows) == 82, f"the cohort is 82 rows; found {len(rows)}"
    disagreeing = [r["accession"] for r in rows if r["label"] != r["gene"]]
    assert disagreeing == [], (
        "`label` is expected to be the gene symbol on this population; these rows disagree "
        f"and the finding needs re-measuring: {disagreeing}"
    )


def test_every_cohort_row_has_a_protein_name_and_it_differs_from_the_gene():
    """The description exists for all 82, and it is a NAME rather than a repeat of the symbol."""
    rows = _rows()
    blank = [r["accession"] for r in rows if not (r["protein_name"] or "").strip()]
    assert blank == [], f"no protein name for {blank}"
    same = [r["accession"] for r in rows if r["protein_name"].strip() == r["gene"].strip()]
    assert same == [], f"protein_name is just the gene symbol for {same}"


def test_the_manifest_row_carries_the_protein_name_and_never_derives_it():
    manifest = {r.accession: r for r in build_manifest()}
    assert len(manifest) == 82
    by_acc = {r["accession"]: r for r in _rows()}
    for acc, row in manifest.items():
        assert row.protein_name == by_acc[acc]["protein_name"].strip()
        # ⚠ and `label` travels unchanged too: this PR renames nothing
        assert row.label == by_acc[acc]["label"]


def test_a_blank_protein_name_stays_an_absence_and_never_becomes_an_empty_string(tmp_path):
    """⚠ `None`, never `""`. An empty string is a VALUE — to `sortRows.isAbsent` on the surface,
    and to any consumer here — and would file an un-named row as though it had a name."""
    src = _rows()[0]
    csv_path = tmp_path / "one.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(src))
        w.writeheader()
        w.writerow({**src, "protein_name": "   "})
    (row,) = build_manifest(csv_path)
    assert row.protein_name is None


def test_the_census_uses_the_same_key_for_the_other_meaning_and_that_is_the_trap():
    """⚠⚠ `F-049`'s family. On the census `label` IS the protein name, rendered as `Protein`.

    Pinned so a future reader cannot infer the cohort's meaning from the census's, which is
    exactly the inference the GO's hypothesis made.
    """
    with CENSUS_LABELS.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows, "the census labels file is empty"
    # on the census the two really do differ — it is a name, not a symbol
    differing = [r for r in rows if (r.get("label") or "").strip()
                 and r["label"].strip() != (r.get("gene") or "").strip()]
    assert len(differing) > 100, (
        "expected the census `label` to be a protein NAME distinct from the gene on most rows; "
        f"only {len(differing)} differ"
    )
    assert re.search(r"key:\s*'label',\s*label:\s*'Protein'", CENSUS_TABLE), (
        "CensusTable is expected to render `label` under the header `Protein` — if that moved, "
        "the two-meanings finding this suite records needs re-checking"
    )


# ─────────────────────────── the supplier that carries the description ───────────────────────────


@pytest.fixture()
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


class _DummyQueue:
    """Reads never touch the queue; `create_app` still wants one. This asserts that by exploding
    if a read path ever reaches it (the `tests/test_read_routes.py` stub)."""

    def claim(self, worker_id, tier="local"):  # pragma: no cover - must never be reached
        raise AssertionError("a read route touched the queue")


def _client(engine, tmp_path):
    app = create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN,
                     queue=_DummyQueue())
    return TestClient(app)


def test_coverage_serves_a_protein_name_for_every_one_of_the_82(engine, tmp_path):
    body = _client(engine, tmp_path).get("/api/coverage").json()
    rows = body["rows"]
    assert len(rows) == 82
    missing = [r["accession"] for r in rows if not r.get("protein_name")]
    assert missing == [], f"no description would render for {missing}"


def test_the_two_rows_with_no_analysis_still_get_a_description(engine, tmp_path):
    """⚠⚠ WHY IT IS THIS SUPPLIER AND NOT THE DB. `FAT2` and `MUC16` have no `protein_analyses`
    row at all — they fold on no single card — so a description read from the database would have
    been blank for exactly the two rows a reader is most likely to be puzzled by."""
    rows = _client(engine, tmp_path).get("/api/coverage").json()["rows"]
    by_gene = {r["gene"]: r for r in rows}
    for gene in ("FAT2", "MUC16"):
        assert by_gene[gene]["fold_status"] == "not_folded"
        assert by_gene[gene]["protein_name"], f"{gene} has no description to render"


def test_the_light_lists_exact_field_set_is_untouched(engine, tmp_path):
    """⚠⚠ D-034 dec 1: the `/api/analyses` field set is EXACT — it is what stops `sequence`
    returning by accident (`tests/test_read_routes.py::LIST_FIELDS`). The description deliberately
    did NOT go here, and this asserts the restraint rather than trusting it."""
    with Session(engine) as s:
        s.add(ProteinAnalysis(input_type="uniprot", input_value="Q92729", cohort_tranche=0,
                              mean_plddt=77.26,
                              meta={"gene": "NECTIN4", "label": "NECTIN4", "tier": "local"}))
        s.commit()
    (row,) = _client(engine, tmp_path).get("/api/analyses").json()
    assert "protein_name" not in row
    assert "description" not in row
    assert "sequence" not in row and "fold_provenance" not in row
    # ⚠ and the field that LOOKS like a description is still served, unchanged, still the gene
    assert row["label"] == "NECTIN4" == row["gene"]


def test_the_projection_reads_the_manifest_and_computes_no_name():
    """⚠ Read, never derived. A projection that built a name would be a new supplier."""
    keys = next(c for c in reads._coverage_row.__code__.co_consts
                if isinstance(c, tuple) and "accession" in c)
    assert "protein_name" in keys, f"_coverage_row must project `protein_name`: {keys}"
    # ⚠ and it is projected from the manifest row, not computed from anything
    assert "row.protein_name" in inspect.getsource(reads._coverage_row)


# ───────────────────────────── the association supplier and its licence ──────────────────────────


def test_the_association_map_still_covers_the_cohort_unchanged():
    """⚠ The D-053 supplier is CONSUMED. Its counts are its own and this PR moves none of them."""
    payload = load_associations()
    assert payload["pair_count"] == 337
    assert payload["targets_covered"] == 82
    assert payload["cohort_size"] == 82
    assert payload["cutoff"] == 150
    assert payload["unmatched_symbols"] == []


def test_every_target_pairs_are_sorted_descending_in_the_data_contract():
    """⚠ The cell reads the LEADING RUN off the order as given, so the order is the contract.
    If this ever reddened, the surface would report `ordered: false` rather than mis-caption."""
    for symbol, rows in load_associations()["associations"].items():
        scores = [r["qh_score"] for r in rows]
        assert scores == sorted(scores, reverse=True), symbol


def test_the_ties_the_cell_renders_in_full_are_real_and_bounded():
    """⚠⚠ Three targets tie at their leading score, so "the top one" is not well defined for
    them and picking the first row would be an arbitrary choice presented as a measurement."""
    assoc = load_associations()["associations"]
    tied = {sym: [r["cancer"] for r in rows if r["qh_score"] == rows[0]["qh_score"]]
            for sym, rows in assoc.items()}
    multi = {sym: names for sym, names in tied.items() if len(names) > 1}
    assert set(multi) == {"JAG1", "CD53", "INSR"}, (
        f"the tie set moved; the entry records JAG1/CD53/INSR: {sorted(multi)}"
    )
    assert max(len(v) for v in multi.values()) == 3


def test_the_route_serves_one_attribution_block_per_covered_symbol():
    payload = load_associations()
    blocks = _association_attributions(payload["associations"])
    assert set(blocks) == set(payload["associations"])
    assert len(blocks) == 82


def test_every_block_carries_all_four_elements_and_a_real_atlas_link():
    """⚠ 82 of 82 cohort symbols resolve an ENSG, so no cohort row falls back to a stated absence.
    ⚠⚠ And all four elements travel together — three of them would let a surface render three and
    look attributed, which is the failure this whole section is reporting."""
    blocks = _association_attributions(load_associations()["associations"])
    for symbol, block in blocks.items():
        assert set(block) >= {"primary_publication", "website", "data_credit",
                              "deep_link", "deep_link_absent_reason"}, symbol
        assert block["data_credit"] == "Human Protein Atlas", symbol
        # ⚠ the IHC paper, NOT the 2017 transcriptome atlas — a filename is not a modality
        assert block["primary_publication"]["doi"] == "10.1126/science.1260419", symbol
        assert block["deep_link"], f"{symbol} would render no per-datum link"
        assert block["deep_link"].startswith("https://v22.proteinatlas.org/"), symbol
        assert block["deep_link"].endswith(f"-{symbol}/pathology"), symbol


def test_the_live_route_carries_the_attributions(engine, tmp_path):
    body = _client(engine, tmp_path).get("/api/associations").json()
    assert "attributions" in body, "the citation must travel with the map"
    assert body["attributions"]["NECTIN4"]["deep_link"].endswith("-NECTIN4/pathology")
    # ⚠ additive: nothing D-053 served has been renamed or dropped
    for key in ("source", "method", "cutoff", "pair_count", "targets_covered", "cohort_size",
                "unmatched_symbols", "associations"):
        assert key in body, key


def test_the_added_payload_is_measured_rather_than_waved_through():
    """⚠ D-137's discipline: state the cost. The raw growth is 82 copies of three constants,
    which is why gzip absorbs almost all of it — and the numbers are in the log entry."""
    payload = load_associations()
    before = json.dumps(payload).encode()
    payload["attributions"] = _association_attributions(payload["associations"])
    after = json.dumps(payload).encode()
    assert len(after) - len(before) < 60_000, "raw growth larger than the entry records"
    gz_before, gz_after = len(gzip.compress(before, 9)), len(gzip.compress(after, 9))
    assert gz_after - gz_before < 4_000, "gzipped growth larger than the entry records"
    entry = _flat(_d142_entry())
    assert "17,952" in entry and "56,498" in entry, "the raw measurement must be in the log"
    assert "2,148" in entry and "4,039" in entry, "the gzipped measurement must be in the log"


def test_a_supplier_failure_degrades_to_no_blocks_so_the_consumer_fails_closed():
    """⚠ A precondition leaves one direction available: withhold the value, never the citation."""
    assert _association_attributions(None) == {}
    assert _association_attributions({}) == {}


def test_the_detail_card_now_reads_the_per_symbol_block_and_not_the_key_that_never_existed():
    """⚠⚠ The live gap, closed. `data.attribution` was `undefined` on every render, and
    `HpaDeepLink` returns null for a falsy attribution — so the card cited nothing."""
    assert "data.attributions?.[symbol]" in ASSOC_CARD
    assert "attribution={data.attribution}" not in ASSOC_CARD


# ─────────────────────────────── the surface, read as source ────────────────────────────────────


def test_the_description_column_is_a_real_columns_entry_and_not_a_hand_drawn_header():
    """⚠ A column that is not in `COLUMNS` takes its sort with it and the table still renders."""
    assert re.search(r"\{\s*key:\s*'description',\s*label:\s*'Description'", TARGET_LIST)


def test_the_description_column_does_not_read_the_payloads_label():
    """⚠⚠ The whole finding, as a property of the component. `label` is the gene symbol here."""
    assert re.search(r"description:\s*descriptions\[r\.accession\]", TARGET_LIST)
    assert "row.label" not in TARGET_LIST and "r.label" not in TARGET_LIST.replace(
        "label: c.label ?? null", "")


def test_the_association_column_has_no_sort_key_and_the_reason_is_rendered():
    """⚠⚠ Not sortable, and the refusal is printed where the control would be, not in a comment.

    Ordering the cohort by the leading quasi H-score — or by how many types clear the cutoff —
    would make an expression statistic the cell never shows into the order of the list: the de
    facto ranking this surface was ruled against on 2026-08-21 for mean pLDDT, by a quantity with
    even less claim to be the order.
    """
    assert re.search(r"\{\s*key:\s*null,\s*label:\s*'Cancer association'", TARGET_LIST)
    assert "no sort control" in TARGET_LIST


def test_the_claim_boundary_is_rendered_on_the_list_in_d053s_own_vocabulary():
    for phrase in ("expression", "causation", "drives the disease", "clinical indication"):
        assert phrase in TARGET_LIST, phrase


def test_the_cutoff_is_interpolated_and_never_typed_on_this_surface():
    """⚠ D-053 dec 5: our statistics DERIVE. The paper's 290/16 are the only literals and they
    live on the detail card, not here."""
    assert "assoc?.cutoff" in TARGET_LIST or "assoc.cutoff" in TARGET_LIST
    assert not re.search(r"above\s+150", TARGET_LIST)


def test_the_surface_consumes_the_association_supplier_and_re_derives_nothing():
    """⚠ No cutoff arithmetic, no qh_score comparison, no re-sort in the component."""
    assert "getAssociations" in TARGET_LIST
    assert "qh_score" not in TARGET_LIST, (
        "the component must not touch the score itself — the reduction lives in "
        "ui/src/associationSummary.js, tested away from the DOM"
    )
    # ⚠ Scoped to the cell, not to the file: the tier <select> legitimately sorts its own options,
    # and a file-wide ban would fail on that and teach nothing. What may not happen is the CELL
    # re-ordering the pairs — `core/cancer_associations.py` sorts in the data contract (D-053),
    # deliberately not in JSX, and a second ordering here could disagree with the detail card.
    cell = TARGET_LIST.split("function AssociationCell(")[1].split("\nfunction ")[0]
    assert ".sort(" not in cell, (
        "nothing in the association cell may re-order the pairs; the supplier sorts (D-053)"
    )
    assert "summariseAssociations(" in cell


def test_the_reduction_lives_in_its_own_tested_module():
    """⚠ The `sortRows.js` / `searchRows.js` precedent — ordering and matching logic extracted and
    tested in isolation, so the surfaces import a proven mechanism instead of a retrofit."""
    assert SUMMARY_MODULE.is_file()
    assert SUMMARY_TEST.is_file()
    src = SUMMARY_MODULE.read_text(encoding="utf-8")
    assert "ordered" in src, "the contracted order must be checked, not assumed"


def test_the_hpa_citation_is_imported_and_suppressed_when_nothing_rendered():
    assert "HpaCredit" in TARGET_LIST
    assert "assocCredit &&" in TARGET_LIST, (
        "the credit must be conditional — a licence-required citation attached to nothing "
        "is not compliance"
    )


def test_the_new_surface_is_in_the_pc3_covered_set():
    """⚠⚠ `F-052`'s shape is a convention obeyed by every caller except the newest one, and PC3
    exists to catch exactly that. A new HPA-rendering component must be enrolled, not exempt."""
    pc3 = (ROOT / "ui" / "src" / "components" / "HpaAttribution.test.jsx").read_text(
        encoding="utf-8")
    covered = pc3.split("const COVERED = new Set([")[1].split("])")[0]
    assert "'TargetList.jsx'" in covered, (
        "TargetList.jsx renders HPA-derived tumour types and must be in PC3's covered set"
    )


def test_the_row_markup_is_written_once_for_both_bodies():
    """⚠ Two copies of eight cells is a divergence waiting to happen: the next column added to one
    and forgotten in the other renders a table whose partition shows different facts."""
    assert TARGET_LIST.count("function RowCells(") == 1
    assert TARGET_LIST.count("<RowCells") == 2


def test_the_shared_matcher_can_find_a_description():
    """⚠ `F-052` again, in the PR that creates the values: a column of 82 protein names that the
    surface's own search box cannot match. The census has searched protein names all along."""
    assert "r.description" in SEARCH_ROWS


def test_the_bounds_are_declarations_and_the_cause_is_not_clipped():
    """⚠⚠ Parsed, not grepped. D-141 lost a guard to a whole-file check satisfied by a COMMENT
    holding the string it wanted (`F-044`), and the prose above `.rank-cause` in this stylesheet
    contains the literal `max-width`. So comments are stripped before anything is matched."""
    css = (ROOT / "ui" / "src" / "styles.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for selector in (r"\.target-list \.col-rank", r"\.rank-cause",
                     r"\.target-list \.col-description", r"\.target-list \.col-assoc"):
        blocks = re.findall(selector + r"\s*\{([^}]*)\}", css)
        assert blocks, f"no rule for {selector}"
        assert any("max-width" in b for b in blocks), f"{selector} carries no bound"
    # ⚠⚠ WIDENED IN PLACE AT D-152, AND THE CLAIM IS UNCHANGED AND STRICTLY STRONGER. This read
    # `(cause,) = re.findall(...)` — an unpack that asserted there is EXACTLY ONE rule for
    # `.rank-cause`, which was true when the bound had one form and is not a property this test is
    # about. D-152 raises the D-142 bounds at ≥1100px in a media query, so a second block targets
    # the same class, and the unpack raised `ValueError` while the thing it stands for stayed true.
    # ⚠ The no-clipping rule now runs over EVERY block that targets the class, so a later edit that
    # adds an ellipsis to the wide-measure form reddens here where the old unpack would have passed
    # after somebody "fixed" it by taking the first match. **A bound is not a truncation** at every
    # measure, not only at the narrow one.
    causes = re.findall(r"\.rank-cause\s*\{([^}]*)\}", css)
    assert causes, "no rule for .rank-cause"
    cause = "\n".join(causes)
    for banned in ("text-overflow", "max-height", "line-clamp", "overflow: hidden",
                   "white-space: nowrap"):
        assert banned not in cause, f".rank-cause clips its content: {banned}"
    # ⚠⚠ FOUND BY OPENING THE PAGE, NOT BY A TEST. `overflow-wrap: anywhere` shrinks an element's
    # MIN-content size to one character, so the auto table algorithm squeezed the bounded column to
    # ~45px and broke the cause mid-word — "no / ranking / run is / currentl / y served". jsdom has
    # no layout and could not see it. `break-word` leaves the intrinsic minimum alone, and the
    # `min-width` floor is what stops seven competing columns taking the space anyway.
    assert "anywhere" not in cause, ".rank-cause must not use overflow-wrap: anywhere"
    assert "break-all" not in cause, ".rank-cause must not break words mid-word"
    assert "min-width" in cause, ".rank-cause needs a floor as well as a ceiling"


def test_the_component_test_ships_with_the_columns():
    assert UI_TEST.is_file()
    src = UI_TEST.read_text(encoding="utf-8")
    assert "withheld" in src, "the fail-closed HPA case must be asserted"
    assert "no sort control" in src, "the refused sort must be asserted"


# ─────────────────────────────── what must NOT have changed ─────────────────────────────────────


def test_no_new_route_reaches_the_app(engine, tmp_path):
    """⚠ D-051 fires on route SETS. Two payloads gained a field; `system-model.json` is unchanged,
    and `tests/test_architecture_contract.py` is the standing set-equality check."""
    model = json.loads(
        (ROOT / "ui" / "src" / "system-model.json").read_text(encoding="utf-8"))
    paths = {r["path"] for group in model["routes"].values() for r in group}
    assert "/api/associations" in paths and "/api/coverage" in paths
    assert not any("description" in p or "protein_name" in p for p in paths)
    # ⚠ the live route table is what `tests/test_architecture_contract.py` pins against the model;
    # this only has to say that THIS change added nothing to it.
    app = create_app(engine=create_engine("sqlite://"), artifact_root=str(tmp_path),
                     auth_token=TOKEN, queue=_DummyQueue())
    live = {r.path for r in app.routes if getattr(r, "path", "").startswith("/api")}
    assert live <= paths, f"a route reached the app that the picture does not declare: {live - paths}"


def test_the_coverage_partition_and_its_invariant_are_untouched(engine, tmp_path):
    body = _client(engine, tmp_path).get("/api/coverage").json()
    cov = body["coverage"]
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == cov["denominator"] == 82


def test_no_scorer_ranking_or_floor_moved():
    """⚠ The pre-registered floor is 50 and this PR is a list-surface change."""
    plddt = (ROOT / "ui" / "src" / "components" / "TargetList.jsx").read_text(encoding="utf-8")
    assert "export const PLDDT_FLOOR = 50" in plddt
    assert "DEFAULT_SORT = { key: 'rank', dir: 'asc' }" in plddt


def test_no_rank_cause_string_was_reworded_or_dropped():
    """⚠⚠ Demotion is not deletion. The bound is CSS; the seven causes are byte-identical."""
    for cause in (
        "no ranking run is currently served",
        "held out; fold subsequently attempted and failed (CUDA OOM). A later census tiling of "
        "this accession is a different span definition — see Census",
        "'held out'",
        "not folded — never attempted",
        "fold attempted and failed",
        "excluded by the pre-registered mean pLDDT floor of ${PLDDT_FLOOR}",
        "unranked — no cause recorded",
    ):
        assert cause in TARGET_LIST, cause


def test_this_pr_ships_no_ops_no_fold_and_no_new_cancer_datum():
    """⚠ The association CSV is the D-053 artefact, unedited: its row count is its own."""
    with (ROOT / "data" / "cancer_associations.csv").open(encoding="utf-8") as fh:
        data_rows = [ln for ln in fh if not ln.lstrip().startswith("#") and ln.strip()]
    assert len(data_rows) == 338, "337 pairs plus the header — no association was added or removed"


# ────────────────────────────────── the log leads the code ──────────────────────────────────────


def _d142_entry() -> str:
    """The D-142 entry only. ⚠ Bounded by the next `### ` heading whatever it is, so a neighbour's
    text can never be swallowed into these checks (the D-141 helper's reasoning)."""
    start = LOG.index("\n### D-142 —") + 1
    nxt = re.search(r"^### (?!D-142\b)", LOG[start + 1:], re.M)
    return LOG[start:start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_d142_entry_exists_and_leads_the_log():
    """⚠⚠ THE CHECK IS THE HEADING, NEVER A CITATION OF IT (D-062 / method-note item 7).

    PR #90 named D-062 in its title and shipped no `### D-062`; thirteen later citations then
    pointed at nothing. So this asserts the entry itself, anchored to a line start.
    """
    assert re.search(r"^### D-142 — `/targets` gains a Cancer association", LOG, re.M)
    assert len(re.findall(r"^### D-142", LOG, re.M)) == 1, "exactly one D-142 entry"
    assert LOG.index("### D-142 —") < LOG.index("### D-141 —"), "newest first"


def test_the_entry_records_the_label_finding_as_a_measurement():
    entry = _flat(_d142_entry())
    assert "label" in entry and "gene symbol" in entry
    assert "cohort_82_ecd.csv" in entry
    assert "all 82 rows" in entry, "the measurement's denominator must be stated"
    assert "protein_name" in entry
    assert "census_labels.csv" in entry, "the other meaning of the same key must be named"
    assert "F-049" in entry


def test_the_entry_records_the_uncited_card_rather_than_quietly_fixing_it():
    entry = _flat(_d142_entry())
    assert "data.attribution" in entry
    assert "PC3" in entry
    assert "precondition" in entry.lower()
    assert "D-100" in entry


def test_the_entry_measures_column_one_before_it_changed_it():
    entry = _flat(_d142_entry())
    assert "144" in entry, "the longest cause must be measured, not described"
    assert "no rule for" in entry.lower() or "no rule" in entry.lower()
    assert "table-layout: auto" in entry


def test_the_entry_states_the_refused_sort_and_its_reason():
    entry = _flat(_d142_entry())
    assert "not sortable" in entry.lower()
    assert "2026-08-21" in entry, "the ruling the refusal rests on must be named"
    assert "32.2%" in entry


def test_the_entry_names_what_is_not_shipped():
    entry = _flat(_d142_entry()).lower()
    for claim in ("not a new route", "not new cancer data", "not a ranking change"):
        assert claim in entry, claim


def test_the_entry_carries_a_deep_learning_justification():
    entry = _flat(_d142_entry())
    assert "Deep-learning justification" in entry
    assert "membrane_proximal_plddt" in entry


def test_the_entry_records_the_reverts_including_the_one_that_bit_unprompted():
    entry = _flat(_d142_entry()).lower()
    assert "revert" in entry
    assert "recommended" in entry, "the denylist bite must be recorded"
    assert "f-044" in entry, "the comment-satisfied-guard lesson must be carried forward"


def test_the_numbering_provenance_is_recorded_not_assumed():
    entry = _flat(_d142_entry())
    assert "30f402f" in entry, "the tip the id was checked against must be named"
    assert "gh pr list --state open" in entry
    assert "D-142" in entry, "the next-free integer must be barred by name"
    assert "never a >=" in entry.lower()


def test_the_architecture_doc_records_the_shipped_shape():
    """⚠ `ARCHITECTURE.md` is the single source of truth for system shape and must be current
    BEFORE the PR is filed (CLAUDE.md living-documentation rule 2)."""
    flat = _flat(ARCH)
    assert "D-142" in flat
    assert "protein_name" in flat, "the coverage field must be in the Read API description"
    assert "attributions" in flat, "the associations field must be in the Read API description"
