"""D-133 — the census Structure column. These must go red.

The census table has projected ``structure_kind`` on every row since **D-118** and
rendered ``structure_kind_label`` as a badge in the accession cell — while the
paragraph above the table claimed a sort on **every** column (**D-087**). So the one
identity D-118 exists to serve was the only row property a reader could not group by,
and nothing objected: a badge renders, and a missing ``COLUMNS`` entry is invisible.

⚠ **What these assertions pin, and why each can go red on its own:**

1. **The key is in ``COLUMNS``.** A hand-drawn ``<th>`` would render a header that
   sorts nothing, and a rendered-text assertion would pass on it.
2. **The column is a CATEGORY.** ``numeric: true`` would compute ``av - bv`` over
   strings — ``NaN``, so no order at all — while claiming a magnitude the four kinds
   do not have. Same ruling as the Profile column (D-079 am. 1 ruling 2).
3. **The default sort is still accession.** D-102 licenses a sort the *reader*
   chooses; a page arriving grouped by structure kind is the census choosing.
4. **The kind is drawn once.** The badge MOVED out of the accession cell. Two
   spellings of one fact, only one of them sortable, is worse than the badge alone.
5. **The entry exists.** Method-note item 7 / the D-062 defect: a commit message
   naming a decision is not the decision being logged. The check is the ``### D-133``
   entry, never a reference to it.

⚠ **Nothing here is a seam claim.** ``assembled`` stays **provisional**, the served
path stays the assembler, and this file asserts the caveat travels with the label.
⚠ **Nothing here ranks.** D-109 ruling 7 is untouched; the assembled parents stay out
of F-004.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.reads import STRUCTURE_KIND_LABEL

ROOT = Path(__file__).resolve().parent.parent
LOG = (chr(10) * 2).join((ROOT / "docs" / n).read_text(encoding="utf-8")
                      for n in ("decisions.md", "findings.md", "assumptions.md", "README.md"))
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
CENSUS_TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(
    encoding="utf-8"
)
# ⚠ D-135 moved the kind ORDER and the chip DERIVATION into a shared module, because /coverage's
# second-population strip reads the same vocabulary and a second copy of the order is how two pages
# come to state one population in two orders. The guarantees below are unchanged; they are asserted
# at the file that now holds them, which is the point of reading the source rather than recalling it.
STRUCTURE_KINDS = (ROOT / "ui" / "src" / "structureKinds.js").read_text(encoding="utf-8")
UI_TEST = ROOT / "ui" / "src" / "components" / "CensusTable.structure.test.jsx"


def _plain(text: str) -> str:
    """⚠ Markdown emphasis stripped as well as whitespace: the log writes ``**Not** F-004``,
    and a substring check for ``not f-004`` would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


def _d133_entry() -> str:
    """The D-133 entry only — the log is 24k lines and a substring match anywhere in it
    proves nothing about the entry that is supposed to carry the claim."""
    start = LOG.index("### D-133")
    return LOG[start: LOG.index("### D-132", start)]


# ---------------------------------------------------------------- the column


def test_structure_kind_is_a_real_columns_entry():
    """⚠ THE TRIPWIRE. Out of ``COLUMNS`` the header button and the sort both vanish."""
    cols = re.search(r"export const COLUMNS = \[(.*?)\n\]", CENSUS_TABLE, re.S)
    assert cols, "COLUMNS must be exported so a test can pin the key, not the rendered text"
    entry = re.search(
        r"\{\s*key: 'structure_kind',\s*label: '([^']+)',\s*numeric: (true|false)\s*\}",
        cols.group(1),
    )
    assert entry, "COLUMNS must hold a structure_kind column"
    # ⚠ the substance, not the wording: the header has to name what it groups, or a reader
    # scanning for the seam-spliced proteins cannot find the column that holds them.
    assert re.search(r"assembl", entry.group(1), re.I), (
        f"the Structure header must name assembly; got {entry.group(1)!r}"
    )
    # ⚠⚠ A CATEGORY, NEVER A MAGNITUDE. `numeric: true` orders nothing (NaN over strings)
    # and claims a rank while doing it.
    assert entry.group(2) == "false", "structure kind is a category; it has no magnitude"


def test_the_column_sorts_on_the_category_not_on_the_label():
    """`structure_kind_label` is prose that already changed once ('assembled' →
    'assembled (provisional)'). Sorting it would re-order the table on a copy edit."""
    assert "key: 'structure_kind'," in CENSUS_TABLE
    assert "key: 'structure_kind_label'" not in CENSUS_TABLE


def test_the_default_sort_is_still_accession():
    """D-102 / D-079: a reader-chosen sort is a lens; an arriving order is a choice."""
    assert "useState({ key: 'accession', dir: 'asc' })" in CENSUS_TABLE
    assert "useState({ key: 'structure_kind'" not in CENSUS_TABLE


def test_the_kind_badge_is_drawn_once_and_in_the_new_column():
    """It MOVED; it was not copied. One place to read it, one header to click."""
    assert CENSUS_TABLE.count("badge badge-kind") == 1, "the kind badge is drawn once"
    kind_cell = CENSUS_TABLE[CENSUS_TABLE.index('className="kind-cell"'):]
    kind_cell = kind_cell[: kind_cell.index("</td>")]
    assert "badge-kind" in kind_cell
    assert "structure_kind_label" in kind_cell
    # ⚠ and NOT back in the accession cell, which is where it used to live
    body = CENSUS_TABLE[CENSUS_TABLE.index("{visible.map("):]
    accession_cell = body[: body.index("</td>")]
    assert "/census/" in accession_cell, "sliced the wrong cell"
    assert "structure_kind_label" not in accession_cell


def test_a_row_with_no_kind_states_the_absence():
    """⚠ A blank cell reads as 'single-pass' — a fold that was never performed. The
    never-folded manifest rows carry no kind at all (only the 3 mucins do)."""
    assert "not recorded" in CENSUS_TABLE
    assert "never an implied single-pass fold" in CENSUS_TABLE


def test_the_fold_type_filter_carries_the_assembler_caveat():
    """Narrowing to the seam-spliced proteins must not read as promoting them."""
    plain = _plain(CENSUS_TABLE)
    assert "assembled from tiles" in plain
    assert "not superimposed" in plain
    assert "seam is not solved" in plain


# ------------------------------------------------- D-133 am. 1: legend + chips


def test_one_rule_decides_the_topology_badge():
    """⚠⚠ The legend and the cell must not derive the badge separately. A nested ternary in the
    JSX is not a thing another surface can ask a question of, which is why no legend existed."""
    assert "export function topologyBadgeKey" in CENSUS_TABLE
    # the cell asks it rather than re-testing r.topology itself
    assert "const topo = topologyBadgeKey(r)" in CENSUS_TABLE
    assert "r.topology === 'contiguous' ?" not in CENSUS_TABLE
    # and so does the legend's presence filter
    assert "rows.map(topologyBadgeKey)" in CENSUS_TABLE


def test_the_legend_defines_the_badges_the_column_prints():
    """The column has printed these words since D-087 and defined none of them."""
    plain = _plain(CENSUS_TABLE)
    assert "export const topology_legend".lower() in plain
    for term in ("contiguous", "intermittent (n)", "gpi / no segment", "not derived",
                 "derivation out of date", "not folded / not folded here"):
        assert term in plain, term


def test_the_gpi_acronym_is_spelt_out_once_and_reaches_the_tooltip():
    """⚠⚠ The owner's ruling: four letters must not be explained with the same four letters.
    ⚠ ONE constant — a second copy is how a tooltip and a legend define one word differently."""
    assert CENSUS_TABLE.count("'glycosylphosphatidylinositol'") == 1
    assert "title={GPI_MEANING}" in CENSUS_TABLE
    plain = _plain(CENSUS_TABLE)
    assert "by design" in plain
    assert "not missing data" in plain
    # ⚠ the old tooltip explained GPI with GPI. It must not survive as a TOOLTIP — the comment
    # quoting it is the record of what was replaced, which is the opposite of the defect.
    assert 'title="GPI-anchored: no topological domains by design"' not in CENSUS_TABLE


def test_the_fold_type_chips_default_to_all_and_state_their_own_counts():
    """A page arriving pre-narrowed has chosen for the reader — D-102's bar, one control along.

    ⚠ Re-POINTED at D-135, not relaxed. `KIND_ORDER` and the label derivation moved to
    `ui/src/structureKinds.js` so `/coverage` reads one vocabulary; each assertion below still
    demands the same property, at the file that now owns it. ⚠ And `CensusTable` must still
    RE-EXPORT the order — existing callers and tests import it from there, and a silent relocation
    is how a guard comes to check a file nobody imports.
    """
    assert "useState('all')" in CENSUS_TABLE
    assert "export const KIND_ORDER" in STRUCTURE_KINDS
    assert "export { KIND_ORDER }" in CENSUS_TABLE
    # ⚠ labels read off the rows, never typed beside the filter
    assert "labels.get(k) ?? KIND_NOT_RECORDED_LABEL" in STRUCTURE_KINDS
    assert "KIND_NOT_RECORDED_LABEL = 'not recorded'" in STRUCTURE_KINDS
    # ⚠ a control whose only option is 'all' is not a control
    assert "kinds.length > 1 &&" in CENSUS_TABLE
    assert 'aria-pressed={kindFilter' in CENSUS_TABLE


def test_the_amendment_entry_exists_and_names_the_citation_finding():
    """⚠⚠ The D-081 citation for the GPI by-design claim resolves to an entry that never mentions
    GPI. The amendment must REPORT that rather than propagate it — and must not erase the existing
    citations, because a citation removed is a finding erased."""
    assert re.search(r"^#### D-133 amendment 1 —", LOG, re.M), "the amendment must be defined"
    entry = _plain(_d133_entry())
    assert "f-025" in entry, "the real authority for the by-design category"
    assert "6,836 characters" in entry, "the measurement, not a recollection"
    assert "left in place and named here" in entry
    # and the parent's out-list is not quietly re-opened by the amendment
    for phrase in ("no rent", "no emit", "no fly write"):
        assert phrase in entry, phrase


def test_the_by_design_claim_is_not_attributed_to_d081_on_the_surface():
    """⚠ D-081 is the span-definition freeze: 0 occurrences of 'GPI', 0 of 'anchor'. The legend
    states the claim in plain words with no id attached rather than repeating the mis-citation."""
    i = LOG.index("### D-081 —")
    d081 = LOG[i: LOG.index("\n### ", i + 10)]
    assert "GPI" not in d081 and "anchor" not in d081.lower(), (
        "if D-081 ever gains the GPI rule, amend D-133 am. 1 rather than quietly re-citing it"
    )
    assert "D-081" not in CENSUS_TABLE


def test_the_ui_kinds_are_the_api_kinds():
    """The badge class, the sort and the filter all key off the API's category string.
    A kind renamed on one side and not the other loses a whole group silently."""
    assert set(STRUCTURE_KIND_LABEL) == {
        "single-pass",
        "assembled",
        "tiles_only",
        "mucin",
    }
    # the literal the filter and the tests depend on
    assert "r.structure_kind === 'assembled'" in CENSUS_TABLE
    # ⚠ still provisional on the wire — this PR did not soften the label
    assert STRUCTURE_KIND_LABEL["assembled"] == "assembled (provisional)"


def test_the_component_test_exists_and_pins_the_grouping():
    """A column asserted only in Python is a column no render ever exercised."""
    assert UI_TEST.exists(), "the CensusTable structure-column test must ship with it"
    text = UI_TEST.read_text(encoding="utf-8")
    assert "COLUMNS" in text
    assert "structure_kind" in text
    # the ordering assertion, not merely a 'header exists' one
    assert re.search(r"expect\(accessions\(\)\)\.toEqual\(", text)


# ---------------------------------------------------------------- the record


def test_d133_entry_exists_before_the_code_claims_it():
    """⚠⚠ Method-note item 7: the check is the ENTRY, never a reference to it."""
    assert re.search(
        r"^### D-133 — Census gains a sortable Structure column", LOG, re.M
    ), "D-133 must be the census sortable-Structure-column entry"
    assert len(re.findall(r"^### D-133", LOG, re.M)) == 1, "exactly one D-133 entry"
    entry = _plain(_d133_entry())
    # the rulings it stands on, each named rather than assumed
    for cite in ("d-087", "d-102", "d-118", "d-079", "d-109"):
        assert cite in entry, cite
    # and the four things it must not be read as doing
    assert "not f-004" in entry or "not an api change" in entry
    assert "seam not solved" in entry or "seams are solved" not in entry
    assert "provisional" in entry
    assert "not a rank" in entry or "not a ranking" in entry


def test_the_architecture_doc_records_the_served_shape():
    """Living-doc rule 2: a PR that changes the served UI shape updates ARCHITECTURE."""
    assert "D-133" in ARCH
    plain = _plain(ARCH)
    assert "sortable structure column" in plain or "structure column" in plain
    assert "test_d133_census_structure_column.py" in ARCH


def test_this_pr_claims_no_ops_and_no_ranking_change():
    """The explicitly-out list, asserted where it can go red: the entry says so."""
    entry = _plain(_d133_entry())
    for phrase in ("no rent", "no emit", "no fly write"):
        assert phrase in entry, phrase
    # D-132's inventory is untouched: 45 parents, the 27 as the dated slice inside it
    assert "45" in entry and "27" in entry
