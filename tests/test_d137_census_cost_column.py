"""D-137 — the census Cost column. Every one of these must be able to go red.

``core/foldability.py`` has held this project's only pre-fold cost instrument since
**D-077 decision 6**, and until this PR **no served surface read it**: ``grep -rn
"foldability"`` over ``app/`` and ``ui/`` returned **0**. A census of 3,467 proteins
printed each protein's span and said nothing about what that span costs — so D-077's
licensed ✅ *Reproducibility* claim (*"M of these folds are reproducible by any reader
with a consumer 8 GB card and no cloud spend"*) was unreadable from the surface holding
the data.

⚠⚠ **THE TESTS THAT MATTER MOST HERE ARE NOT THE ARITHMETIC ONES** — the same warning
``tests/test_foldability.py`` opens with, one level out. D-077 decision 1 pre-registered
three refusals, and a *served* cost axis is the first thing in this project capable of
breaking all three:

1. **It must not become a model feature.** Local-foldability is a monotone step function
   of ECD length, which is **feature 1** of the pre-registered six (D-027) — the F-008
   confound. So ``app/census_cost_read.py`` joins the structural guard that
   ``core/scorer.py`` and ``core/features.py`` cannot reach the cost instrument.
2. **It must not sit beside suitability without its label.** Asserted on the *header*, on
   the served ``cost_axis``, and on the legend that renders it — not on a doc.
3. **⚠ It must not filter the census.** The nearest miss, and the reason half this file
   exists: **D-133 am. 1 shipped fold-type chips**, so a ``local`` / ``rental`` /
   ``over ceiling`` chip set is now the obvious next control. A census that hides the rows
   it cannot afford to fold is a census of *our budget*, biased by span length — i.e. by
   feature 1. These tests fail on a cost chip, a cost checkbox, a cost term inside
   ``filterRows``/``KIND_ORDER``, a predicate parameter on ``apply_cost``, and on a row
   count that shrinks through the live route.

⚠ **Nothing here is a fold claim, a seam claim or a ranking change.** ``assembled`` stays
provisional, the served path stays the assembler, D-109 ruling 7 is untouched, and no
census row acquires a score.
"""
from __future__ import annotations

import ast
import csv
import inspect
import re
from collections import Counter
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import reads
from app.census_cost_read import (
    COST_AXIS,
    COST_LABEL,
    COST_MEANING,
    COST_ORDER,
    COST_VERDICTS,
    SPAN_UNRECORDED,
    apply_cost,
    cost_block,
    cost_for_span,
    cost_recipe,
)
from app.main import create_app
from core.foldability import LOCAL, OVER_CEILING, RENTAL, envelope
from core.manifest import LOCAL_CEILING, tier_for_span
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
CENSUS_TABLE = (ROOT / "ui" / "src" / "components" / "CensusTable.jsx").read_text(
    encoding="utf-8"
)
SUPPLIER = (ROOT / "app" / "census_cost_read.py").read_text(encoding="utf-8")
UI_TEST = ROOT / "ui" / "src" / "components" / "CensusTable.cost.test.jsx"
TOKEN = "test-secret-token"


def _plain(text: str) -> str:
    """⚠ Markdown emphasis stripped as well as whitespace: the log writes ``**not** a filter``,
    and a substring check for ``not a filter`` would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


def _d137_entry() -> str:
    """The D-137 entry only. The log is 24k lines; a substring match anywhere in it proves
    nothing about the entry that is supposed to carry the claim (method-note item 7).

    ⚠⚠ BOUNDED BY THE NEXT HEADING, WHATEVER IT IS — never by a named neighbour. The first
    version sliced to ``### D-135`` because D-135 was the entry below when this was written;
    D-136 then merged **between** them, and the slice silently grew to include a whole
    unrelated entry — so every `in entry` assertion below would have passed on **D-136's**
    prose. D-136's own suite records the identical defect (it had bounded itself by `D-134`).
    A hidden merge-order dependency in a test that exists to check the record is the record
    checking the wrong thing.
    """
    start = LOG.index("### D-137")
    nxt = re.search(r"^### (?!D-137\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def _code_only(source: str) -> str:
    """Source with docstrings and comments removed — so a *discussion* of the ceiling, or of the
    word ``affordable``, is not mistaken for a second copy of the constant or for a filter.

    ⚠ ``/* … */`` is stripped as a BLOCK, not line-by-line. A first version dropped only lines
    *starting* with a comment marker, which leaves every ``{/* … */}`` JSX comment in the body —
    so the filter check below reddened on the cell comment that explains why there is no filter.
    A guard that fires on its own documentation is a guard nobody will keep.
    """
    body = re.sub(r'"""(?:.|\n)*?"""', "", source)          # python docstrings
    body = re.sub(r"/\*(?:.|\n)*?\*/", "", body)            # /* … */, incl. JSX {/* … */}
    return re.sub(r"(?m)^\s*(#|//).*$", "", body)           # line comments


# ─────────────────────────────────────────────── the vocabulary is not a second vocabulary


def test_the_categories_are_foldabilitys_own_words():
    """⚠ D-077's three verdicts, imported and not restated. A fourth *price* would be a second
    cost model; the fourth member here is an **absence** and is checked as one below."""
    assert COST_ORDER == (LOCAL, RENTAL, OVER_CEILING)
    assert COST_VERDICTS == (LOCAL, RENTAL, OVER_CEILING, SPAN_UNRECORDED)
    assert set(COST_LABEL) == set(COST_VERDICTS) == set(COST_MEANING)
    # the served TERM keeps the vocabulary's own word; only the underscore goes, exactly as
    # `tiles_only` renders `tiles only` (D-133)
    assert COST_LABEL[LOCAL] == "local"
    assert COST_LABEL[RENTAL] == "rental"
    assert COST_LABEL[OVER_CEILING].replace(" ", "_") == OVER_CEILING


def test_the_order_is_a_cost_order_and_excludes_the_absence():
    """⚠⚠ `span_unrecorded` has no place in a cost order. At the END of the array it would be
    the DEAREST row on one descending click — an absence rendered as the worst value, which is
    the same defect as bucketing it affordable, wearing the opposite sign."""
    assert SPAN_UNRECORDED not in COST_ORDER
    assert COST_ORDER.index(LOCAL) < COST_ORDER.index(RENTAL) < COST_ORDER.index(OVER_CEILING)


def test_the_verdict_agrees_with_the_envelope_it_wraps():
    """A second implementation of the boundary would drift from the first. This one delegates,
    and the boundary cases prove it rather than the middle of each band."""
    for span in (
        1,
        LOCAL_CEILING.local_bound,
        LOCAL_CEILING.local_bound + 1,
        LOCAL_CEILING.rental_bound - 1,
        LOCAL_CEILING.rental_bound,
        LOCAL_CEILING.rental_bound + 1,
    ):
        assert cost_for_span(span) == envelope(span), span


def test_it_agrees_with_the_manifest_router_on_every_census_span():
    """⚠ The served cost class and the routing the pipeline actually performs must never
    disagree about a protein — a census quoting a price for a routing that does not happen.

    Checked against the real census manifest, not invented spans.
    """
    spans = _manifest_spans()
    assert spans, "no spans read — the fixture is not exercising anything"
    for span in spans:
        tier, _ = tier_for_span(span)
        verdict = cost_for_span(span)
        if tier == "local":
            assert verdict == LOCAL, f"span {span}: manifest local, cost model {verdict}"
        else:
            assert verdict in (RENTAL, OVER_CEILING), f"span {span}: disagreement"


# ─────────────────────────────────────────── the absence is named, and never priced as free


@pytest.mark.parametrize(
    "value",
    [None, 0, -1, "", "   ", "n/a", "630 aa", 630.5, True, False, [], {}, float("nan")],
)
def test_anything_that_is_not_a_span_is_a_named_absence_never_local(value):
    """⚠⚠ THE ONE THAT MATTERS. `envelope()` raises on a missing span *by design* — quietly
    bucketing an unmeasured target as affordable is how a cost estimate becomes a fiction
    (D-024) — and a read route may not raise on thousands of rows. So the absence is NAMED.

    ⚠ `True` is in this list on purpose: `isinstance(True, int)` is `True` in Python, so a
    truthiness flag reaching this field would otherwise be costed as a 1 aa free local fold.
    ⚠ `0` is here too: a zero-length span is not a free fold, it is a measurement that did not
    happen — the reading `core/census.py::categorise` already gives it.
    """
    assert cost_for_span(value) == SPAN_UNRECORDED
    assert cost_for_span(value) != LOCAL


def test_a_span_that_arrives_as_a_json_string_or_float_is_still_a_span():
    """⚠ `meta` is JSON: `630` can arrive as `"630"` or `630.0`, and reporting an absence where
    a measurement exists is the same class of error in the other direction."""
    assert cost_for_span("630") == cost_for_span(630)
    assert cost_for_span(630.0) == cost_for_span(630)
    assert cost_for_span(" 300 ") == cost_for_span(300)


def test_the_underlying_envelope_still_raises_so_batch_callers_keep_the_guard():
    """⚠ The route's need for a non-raising read must not soften the instrument. `envelope`
    keeps refusing to guess for every caller that should still be refused."""
    with pytest.raises((ValueError, TypeError)):
        envelope(None)


# ─────────────────────────────────────────────────────── the block a row carries, and its recipe


def test_every_row_carries_the_axis_statement_and_the_ceiling_recipe():
    """⚠⚠ D-077 dec 1 refusal 2: a surface placing cost beside suitability must say so **in the
    same visual frame**. It rides on the row for the same reason `scored: false` does — so no
    consumer has to remember the bar. ⚠ D-016 / D-077 dec 3: a cost claim without its recipe is
    not checkable, because the same span is affordable at int8 and not at fp16."""
    block = cost_block(300)
    assert set(block) == {"cost", "cost_label", "cost_note", "cost_axis", "cost_recipe"}
    assert block["cost"] == LOCAL
    axis = _plain(block["cost_axis"])
    assert "not suitability" in axis
    assert "filters nothing" in axis or "not a filter" in axis
    assert "score" in axis and "rank" in axis
    recipe = block["cost_recipe"]
    for token in (LOCAL_CEILING.dtype, str(LOCAL_CEILING.chunk_size),
                  str(LOCAL_CEILING.local_bound), str(LOCAL_CEILING.rental_bound)):
        assert token in recipe, token


def test_the_recipe_moves_when_the_measured_ceiling_moves():
    """Proves the recipe is READ rather than coincidentally agreeing with the constant. A module
    that hard-coded today's numbers would pass every assertion above and fail this one."""
    import dataclasses

    raised = dataclasses.replace(LOCAL_CEILING, known_good=600)
    assert str(raised.local_bound) in cost_recipe(raised)
    assert cost_for_span(500) == RENTAL                      # against the real ceiling
    assert cost_for_span(500, ceiling=raised) == LOCAL       # against a raised one


def test_no_ceiling_literal_is_written_in_the_supplier():
    """D-050 / D-077 dec 3: a literal here would be a second copy of the routing constant —
    the exact drift the one-constant rule exists to prevent, re-created by the module built to
    consume it. ⚠ Prose *about* the ceiling is stripped first; a discussion is not a copy."""
    body = _code_only(SUPPLIER)
    for literal in (str(LOCAL_CEILING.known_good), str(LOCAL_CEILING.known_bad)):
        assert literal not in body, f"ceiling literal {literal!r} hardcoded; read LOCAL_CEILING"


def test_the_ceiling_never_reaches_the_component():
    """⚠ Same rule one layer out: the measured numbers arrive on the wire, so a copy edit in
    the UI cannot create a second ceiling."""
    body = _code_only(CENSUS_TABLE)
    for literal in (str(LOCAL_CEILING.known_good), str(LOCAL_CEILING.known_bad)):
        assert literal not in body, f"the UI must not restate the ceiling ({literal})"
    assert "cost_recipe" in CENSUS_TABLE, "the recipe has to come from somewhere"


def test_rental_never_travels_bare_and_carries_its_closure():
    """⚠⚠ Rental for the hold-48 remainder CLOSED 2026-09-05 PT (pod Terminated), and
    `core/census_unfolded.py` already refuses the words *"waiting on rented capacity"* because
    a live-queue claim about a closed rental is false. A bare `rental` badge on 349 rows would
    re-open exactly that claim, one column along."""
    note = COST_MEANING[RENTAL]
    assert "2026-09-05" in note
    assert "closed" in note.lower()
    plain = _plain(note)
    assert "not a queue position" in plain
    for forbidden in ("waiting on rented capacity", "awaiting rental", "in the rental queue"):
        assert forbidden not in _plain(" ".join(COST_MEANING.values())), forbidden


def test_over_ceiling_is_not_collapsed_into_rental_and_not_confused_with_assembly():
    """⚠ "costs money" and "folds on no single card" are different facts, and pooling them lets
    a census quote a price for something that cannot be bought (D-077's own words).
    ⚠ And `over_ceiling` is about SINGLE-PASS fold length, not about how a structure was made —
    a tiled protein is still over the single-pass ceiling, so the two columns can disagree."""
    assert COST_MEANING[OVER_CEILING] != COST_MEANING[RENTAL]
    plain = _plain(COST_MEANING[OVER_CEILING])
    assert "not the same class as rental" in plain
    assert "assembl" in plain or "tiles" in plain


def test_the_absence_is_not_borrowed_from_no_topology():
    """⚠ `core.census.NO_TOPOLOGY` means *fetched successfully, and the protein has no numeric
    ECD span* — and that module states it "REQUIRES A SUCCESSFUL FETCH". The read path cannot
    attest a fetch ever happened, so using that word here would assert a fact we do not have."""
    from core.census import NO_TOPOLOGY

    assert SPAN_UNRECORDED != NO_TOPOLOGY
    assert SPAN_UNRECORDED not in {NO_TOPOLOGY}
    plain = _plain(COST_MEANING[SPAN_UNRECORDED])
    assert "no cost" in plain or "no envelope" in plain
    assert "never counted as affordable" in plain


# ─────────────────────────────────────── refusal 3: it must not filter the census. Structurally.


def test_apply_cost_has_no_predicate_to_filter_with():
    """⚠⚠ THE REFUSAL IS THE SIGNATURE. D-077 dec 1 refusal 3 is enforced by there being
    nothing here to enforce it with — no `only_local`, no `max_cost`, no `include`. A caller who
    wants an affordable-only census has to write the comprehension in the open."""
    params = list(inspect.signature(apply_cost).parameters)
    assert params == ["rows", "ceiling"], f"apply_cost grew a parameter: {params}"
    body = _code_only(SUPPLIER)
    for banned in ("if cost ==", "if verdict ==", ".remove(", "continue"):
        assert banned not in body, f"a branch that can drop a row: {banned!r}"


def test_apply_cost_returns_every_row_in_the_order_it_was_given_them():
    """⚠ Including the row whose span was never measured — the one an affordability filter would
    take first, and the one D-077 says stays in the census flagged and unfolded."""
    rows = [
        {"accession": "Q00001", "span_aa": 300},
        {"accession": "Q00002", "span_aa": 500},
        {"accession": "Q00003", "span_aa": 5000},
        {"accession": "Q00004", "span_aa": None},
        {"accession": "Q00005"},
    ]
    out = apply_cost(rows)
    assert [r["accession"] for r in out] == [f"Q0000{i}" for i in range(1, 6)]
    assert [r["cost"] for r in out] == [
        LOCAL, RENTAL, OVER_CEILING, SPAN_UNRECORDED, SPAN_UNRECORDED,
    ]
    assert all("cost_axis" in r for r in out)


def test_no_cost_split_is_exposed_by_the_supplier():
    """⚠ `core.foldability.split` / `core.census.census_split` stay BATCH tools. A served
    `2,691 / 349 / 427` on the census page is a headline, and a headline about our budget beside
    an unscored census is what refusal 2 is about. The page shows a class per row instead."""
    import app.census_cost_read as mod

    public = [n for n in dir(mod) if not n.startswith("_")]
    offenders = [n for n in public if re.search(r"split|count|total|summar", n, re.I)]
    assert not offenders, f"the cost supplier must not expose a census-wide split: {offenders}"


def test_the_component_has_no_cost_filter_of_any_kind():
    """⚠⚠ THE NEAREST MISS, ASSERTED WHERE IT WOULD BE WRITTEN. D-133 am. 1 shipped fold-type
    chips, so a cost chip set is the obvious next control — and it is the one refusal 3 forbids.

    Prove this bites: add a `costFilter` state and a chip, and this reddens by name.
    """
    body = _code_only(CENSUS_TABLE)
    for banned in (
        "costFilter",
        "setCostFilter",
        "excludeCost",
        "excludeOverCeiling",
        "affordable",
        "COST_ORDER.map",           # a chip row over the cost categories
    ):
        assert banned not in body, f"a cost filter control: {banned!r}"
    # ⚠ and the filter pipeline itself must not learn the word. `base`/`kinded`/`filterRows`
    # are the three narrowing steps; none of them may key off cost.
    pipeline = body[body.index("const shown = useMemo"): body.index("const declared")]
    assert "cost" not in pipeline.lower(), (
        f"the narrowing pipeline mentions cost — it must only SORT by it:\n{pipeline}"
    )
    # ⚠ The chip vocabulary is fold types only. Read from `ui/src/structureKinds.js`, where
    # D-135 moved `KIND_ORDER` so `/coverage`'s second-population strip could share it — a
    # search against the component would now find only the re-export and pass on nothing.
    kinds_src = (ROOT / "ui" / "src" / "structureKinds.js").read_text(encoding="utf-8")
    kinds = re.search(r"KIND_ORDER = \[(.*?)\]", kinds_src, re.S)
    assert kinds, "KIND_ORDER moved again — re-point this check at it rather than deleting it"
    for word in (LOCAL, RENTAL, OVER_CEILING, SPAN_UNRECORDED):
        assert word not in kinds.group(1), f"{word!r} became a fold-type chip"


def test_the_refusal_is_written_where_the_next_control_would_go():
    """⚠ D-074: an instrument that can be misused carries the statement of its own limits, and
    the person who adds the next chip will be reading the chip block — not this file."""
    chips = CENSUS_TABLE[CENSUS_TABLE.index("THE FOLD-TYPE FILTER"):]
    chips = chips[: chips.index("</div>")]
    plain = _plain(chips)
    assert "no cost chip" in plain
    assert "census of" in plain and "budget" in plain
    assert "feature 1" in plain


# ──────────────────────────────── refusal 1: the cost instrument stays out of the scoring path


def test_the_cost_supplier_is_not_reachable_from_the_scorer_or_the_features():
    """⚠⚠ The structural half of refusal 1, extended to the new module.

    Documenting "must not become a model feature" does not prevent it. `tests/test_foldability.py`
    already asserts the scorer cannot reach `core/foldability.py`; a *served* wrapper around it is
    a second door to the same room, so it is closed the same way.

    Proven by revert: add `from app.census_cost_read import cost_for_span` to `core/scorer.py`
    and watch this redden.
    """
    for name in ("core/scorer.py", "core/features.py"):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module]
            for m in mods:
                assert "census_cost_read" not in m and "foldability" not in m, (
                    f"{name} imports {m!r} — a compute budget must not reach the scoring "
                    f"path (D-077 dec 1 refusal 1)"
                )


def test_the_supplier_declares_no_feature_or_score_surface():
    """A defensive check with a specific target: nothing here may look like it belongs in the
    six. A `feature`- or `score`-named public callable is the first step of refusal 1's defect."""
    import app.census_cost_read as mod

    public = [n for n in dir(mod) if not n.startswith("_")]
    offenders = [n for n in public if "feature" in n.lower() or "score" in n.lower()]
    assert not offenders, f"the cost supplier must not expose feature/score surface: {offenders}"


def test_the_census_row_projection_does_not_import_the_cost_supplier():
    """⚠ The same wall `census_profile_read.py` stands behind: the module that projects census
    rows must not be the place a compute budget and a ranking meet. The ROUTE composes them."""
    tree = ast.parse((ROOT / "app" / "reads.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods = [node.module]
        for m in mods:
            assert "census_cost_read" not in m and "foldability" not in m, (
                f"app/reads.py imports {m!r} — compose the cost axis at the route instead"
            )
    assert "from app.census_cost_read import apply_cost" in (
        ROOT / "app" / "read_routes.py"
    ).read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────── the column, in the component


def test_cost_is_a_real_columns_entry_and_not_a_hand_drawn_header():
    """⚠ THE TRIPWIRE. Out of `COLUMNS` the header button and the sort both vanish, and a
    rendered-text assertion would pass on a `<th>` that sorts nothing."""
    cols = re.search(r"export const COLUMNS = \[(.*?)\n\]", CENSUS_TABLE, re.S)
    assert cols, "COLUMNS must stay exported so a test can pin the key"
    entry = re.search(
        r"\{ key: 'cost', label: '([^']+)', numeric: (true|false),\s*\n\s*order: (\w+) \}",
        cols.group(1),
    )
    assert entry, "COLUMNS must hold a cost column declaring its order"
    label, numeric, order = entry.groups()
    # ⚠⚠ THE HEADER ITSELF SAYS WHICH AXIS IT IS. A column called only 'Cost' beside an unscored
    # census invites the reader to read cheap as good, which is refusal 2 exactly.
    assert re.search(r"cost", label, re.I), label
    assert re.search(r"not suitability", label, re.I), (
        f"the header must deny the suitability reading in the header; got {label!r}"
    )
    assert numeric == "false", "there is no magnitude in the cell — the order carries it"
    assert order == "COST_ORDER"


def test_the_column_sorts_on_the_category_never_on_the_label():
    """`cost_label` is prose the server owns. Sorting it would re-order the table on a copy
    edit — D-133's lesson, learnt on `structure_kind_label`."""
    assert "key: 'cost'," in CENSUS_TABLE
    assert "key: 'cost_label'" not in CENSUS_TABLE
    assert "key: 'cost_note'" not in CENSUS_TABLE


def test_the_cost_order_is_declared_above_the_columns_that_read_it():
    """⚠ `COLUMNS` reads `COST_ORDER` at module evaluation. Declared below, it would be in scope
    and uninitialised — a temporal-dead-zone throw at import, not a lint warning."""
    assert CENSUS_TABLE.index("export const COST_ORDER") < CENSUS_TABLE.index(
        "export const COLUMNS"
    )
    ui_order = re.search(r"export const COST_ORDER = \[(.*?)\]", CENSUS_TABLE).group(1)
    assert [w.strip(" '\"") for w in ui_order.split(",")] == list(COST_ORDER), (
        "the UI's cost order must be the API's, in the API's order"
    )


def test_a_value_outside_the_order_sorts_last_in_both_directions():
    """⚠⚠ The null rule, extended. `span_unrecorded` is not in `COST_ORDER`, so it maps to null
    and sorts last both ways. Placed at the END of the order instead it would be the DEAREST row
    on one descending click — an absence rendered as the worst value."""
    assert "function sortValue" in CENSUS_TABLE
    fn = CENSUS_TABLE[CENSUS_TABLE.index("function sortValue"):]
    fn = fn[: fn.index("\n}")]
    assert "indexOf" in fn and "i < 0 ? null : i" in fn
    # and `compare` still applies the null-last rule before the direction flip
    cmp = CENSUS_TABLE[CENSUS_TABLE.index("function compare"):]
    cmp = cmp[: cmp.index("\n}")]
    assert "if (av == null) return 1" in cmp
    assert "if (bv == null) return -1" in cmp


def test_the_default_sort_is_still_accession():
    """D-102 / D-079: a reader-chosen sort is a lens; a page arriving ordered by cost has
    chosen — and ordering an unscored census by our budget is the most misreadable choice
    available."""
    assert "useState({ key: 'accession', dir: 'asc' })" in CENSUS_TABLE
    assert "useState({ key: 'cost'" not in CENSUS_TABLE


def test_one_rule_decides_the_cost_badge_and_the_legend_asks_it():
    """⚠⚠ A nested ternary is not a thing another surface can interrogate — which is why the
    topology column went six entries without a legend until D-133 am. 1 extracted one."""
    assert "export function costBadgeKey" in CENSUS_TABLE
    assert "const costKey = costBadgeKey(r)" in CENSUS_TABLE
    legend = CENSUS_TABLE[CENSUS_TABLE.index("const costLegend = useMemo"):]
    legend = legend[: legend.index("}, [rows])")]
    assert "costBadgeKey(r)" in legend, "the legend must ask the same rule the cell asks"


def test_the_three_absences_stay_three():
    """⚠ `span_unrecorded` (the server looked, there is no span) · `not_served` (the row carries
    no cost FIELD — rendering it as the first would assert something only the server can say) ·
    an unknown verdict (rendered verbatim rather than coerced into a word we understand)."""
    fn = CENSUS_TABLE[CENSUS_TABLE.index("export function costBadgeKey"):]
    fn = fn[: fn.index("\n}")]
    assert "'not_served'" in fn
    assert "'span_unrecorded'" in fn
    assert "'unknown_verdict'" in fn
    assert "never an implied local fold" in CENSUS_TABLE


def test_the_legend_is_read_off_the_rows_and_not_typed_in_the_component():
    """⚠ Strictly stronger than D-133 am. 1, where `STRUCTURE_LEGEND`'s meanings are typed in
    the component and only the term is the API's. Here the supplier owns both, so the page
    cannot come to define `rental` differently from the module that assigns it."""
    assert "COST_LEGEND" not in CENSUS_TABLE, (
        "a typed cost legend is a second definition of the vocabulary"
    )
    for served in ("cost_label", "cost_note", "cost_axis", "cost_recipe"):
        assert served in CENSUS_TABLE, served
    # ⚠ and no fragment of a served meaning is duplicated into the component
    assert "reproducible by any reader" not in CENSUS_TABLE
    assert "pod Terminated" not in _code_only(CENSUS_TABLE)


def test_the_axis_statement_is_rendered_in_the_same_frame_as_the_column():
    """⚠⚠ D-077 dec 1 refusal 2's actual requirement: *in the same visual frame*. Not a
    tooltip, not a glossary page, not a doc — the legend block that sits against the header
    row, and at full size, because a caveat set smaller than its datum is one the page has
    decided the reader may skip."""
    legend = CENSUS_TABLE[CENSUS_TABLE.index('<div className="census-legend">'):]
    legend = legend[: legend.index("<table>")]
    assert "{costAxis}" in legend
    assert "{costRecipe}" in legend
    assert re.search(r"What the Cost column says", legend)
    css = (ROOT / "ui" / "src" / "styles.css").read_text(encoding="utf-8")
    assert ".census-legend .cost-axis" in css


def test_the_badges_are_not_coloured_good_and_bad():
    """⚠⚠ A DECISION, NOT A PALETTE. Green-`local` / red-`over_ceiling` would say *good* and
    *bad* about a protein on a cost axis, in the same frame as a sentence denying it. An
    expensive protein is not a worse target; it is a dearer fold."""
    css = (ROOT / "ui" / "src" / "styles.css").read_text(encoding="utf-8")
    block = css[css.index(".badge-cost {"): css.index(".census-table .cost-cell")]
    # the greens and reds this stylesheet uses for good/bad elsewhere
    for verdict_colour in ("#68d391", "#fc8181", "#f56565", "#e53e3e"):
        assert verdict_colour not in block, (
            f"{verdict_colour} is a good/bad hue; the cost badges differ by class, not by merit"
        )
    for needed in (".badge-cost-local", ".badge-cost-rental", ".badge-cost-over_ceiling"):
        assert needed in block, needed


def test_the_cost_cell_renders_no_figure():
    """⚠ The column reports a CLASS. A number in it — a length, a dollar figure, a rank — is a
    magnitude the reader will compare, and comparing budgets across an unscored census is the
    ranking D-079 bars arriving by a different route."""
    cell = CENSUS_TABLE[CENSUS_TABLE.index('<td className="cost-cell">'):]
    cell = cell[: cell.index("</td>")]
    assert not re.search(r">\s*\d", cell), f"a figure in the cost cell:\n{cell}"
    assert "span_aa" not in cell, "the span is its own column; the cost cell is a class"


# ───────────────────────────────────────────────────── the live route: shape and row count


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(eng)
    return eng


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover
        raise AssertionError("a read route touched the queue")


def _client(engine, tmp_path):
    return TestClient(
        create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN,
                   queue=_DummyQueue()),
        raise_server_exceptions=True,
    )


def _seed(engine) -> None:
    """Four census proteins spanning all four outcomes, including one with NO span in `meta` —
    the row an affordability filter would drop first."""
    rows = [
        ("Q00001", {"span_aa": 300}),
        ("Q00002", {"span_aa": LOCAL_CEILING.local_bound + 1}),
        ("Q00003", {"span_aa": LOCAL_CEILING.rental_bound + 100}),
        ("Q00004", {}),                     # ⚠ no span recorded at all
    ]
    with Session(engine) as s:
        for acc, meta in rows:
            s.add(ProteinAnalysis(
                input_type="uniprot", input_value=acc, cohort_tranche=5,
                structure_source="esmfold", pdb_path="/data/x.pdb", mean_plddt=60.0,
                meta={"gene": acc, **meta},
            ))
        s.commit()


def test_the_route_stamps_a_cost_on_every_row_it_serves(engine, tmp_path):
    served = _client(engine, tmp_path).get("/api/census").json()
    _seed(engine)
    served = _client(engine, tmp_path).get("/api/census").json()
    assert served, "no census rows served — the fixture proves nothing"
    for row in served:
        assert row["cost"] in COST_VERDICTS, row
        assert row["cost_label"] == COST_LABEL[row["cost"]]
        assert row["cost_note"] == COST_MEANING[row["cost"]]
        assert row["cost_axis"] == COST_AXIS
        assert row["cost_recipe"] == cost_recipe()


def test_the_route_serves_exactly_as_many_rows_as_the_reader_built(engine, tmp_path):
    """⚠⚠ REFUSAL 3, COUNTED THROUGH THE LIVE ROUTE. A cost stamp that silently dropped rows
    would look exactly like a shorter census, and no shape assertion above would notice."""
    _seed(engine)
    built = reads.list_census(engine)
    served = _client(engine, tmp_path).get("/api/census").json()
    assert len(served) == len(built)
    assert [r.get("accession") for r in served] == [r.get("accession") for r in built]


def test_the_row_with_no_span_is_served_named_and_not_affordable(engine, tmp_path):
    """⚠ It stays IN the census, flagged — D-077's own remedy: *"Unaffordable targets stay in
    the census, flagged, unfolded."* And it is not `local`."""
    _seed(engine)
    served = _client(engine, tmp_path).get("/api/census").json()
    row = next(r for r in served if r["accession"] == "Q00004")
    assert row["cost"] == SPAN_UNRECORDED
    assert row["cost"] != LOCAL
    assert row["span_aa"] is None
    assert "never counted as affordable" in _plain(row["cost_note"])


def test_all_four_outcomes_are_reachable_through_the_route(engine, tmp_path):
    """A fixture that exercises one branch proves one branch. The boundary spans come from the
    measured ceiling, so the test moves with it rather than pinning a literal."""
    _seed(engine)
    served = _client(engine, tmp_path).get("/api/census").json()
    by_acc = {r["accession"]: r["cost"] for r in served}
    assert by_acc["Q00001"] == LOCAL
    assert by_acc["Q00002"] == RENTAL
    assert by_acc["Q00003"] == OVER_CEILING
    assert by_acc["Q00004"] == SPAN_UNRECORDED


def test_the_story_summary_gains_no_cost_total(engine, tmp_path):
    """⚠ `census_summary` reduces `reads.list_census`, which the ROUTE stamps after calling —
    so the Story's four numbers cannot acquire a cost figure by accident. A served
    `2,691 / 349 / 427` is a headline about our budget beside an unscored census."""
    _seed(engine)
    summary = _client(engine, tmp_path).get("/api/census/summary").json()
    flat = _plain(str(summary))
    for word in ("cost", "local", "rental", "over_ceiling"):
        assert word not in flat, f"the census summary grew a cost claim: {word}"


def test_no_census_row_gained_a_score(engine, tmp_path):
    """⚠ D-079 dec 1 is untouched: a cost class is not a score, and the row still says so."""
    _seed(engine)
    served = _client(engine, tmp_path).get("/api/census").json()
    assert all(r["scored"] is False for r in served if "scored" in r)


# ───────────────────────────────────────────────── the provenance the entry claims, re-measured


def _manifest_spans() -> list[int]:
    with (ROOT / "data" / "census" / "census_manifest.v7.csv").open(
        encoding="utf-8", newline=""
    ) as fh:
        return [int(r["span_aa"]) for r in csv.DictReader(fh) if (r["span_aa"] or "").strip()]


def test_the_measured_split_the_entry_records_is_still_the_measured_split():
    """⚠⚠ D-016: the entry states `local 2,691 / rental 349 / over_ceiling 427` over 3,467
    manifest rows. Re-measured here, so the claim in the log is a **finding** rather than a
    number someone remembers — and so it reddens the day the manifest or the ceiling moves,
    which is the moment the entry needs amending rather than the moment it becomes wrong."""
    spans = _manifest_spans()
    counts = Counter(cost_for_span(s) for s in spans)
    assert (len(spans), counts[LOCAL], counts[RENTAL], counts[OVER_CEILING]) == (
        3467, 2691, 349, 427,
    ), f"the manifest split moved: {len(spans)} rows, {dict(counts)} — amend D-137"
    assert counts[SPAN_UNRECORDED] == 0, "the manifest carries no blank span today"
    entry = _d137_entry()
    for figure in ("2,691", "349", "427", "3,467"):
        assert figure in entry, f"D-137 must state {figure}"


def test_the_split_reconciles_with_the_never_folded_reasons():
    """⚠⚠ THE QUERY WHOSE ANSWER COULD DISQUALIFY THE AXIS, run rather than asserted in prose —
    and it already earned its keep. The first version of D-137 claimed *"349 and 427 reconcile
    exactly"* with `core/census_unfolded.py`'s reasons; this test reddened at `424 == 427` and
    the entry was corrected before the PR was filed.

    ⚠ `rental` IS exact. `over_ceiling` is NOT, and the gap is the **3 mucins**: their recorded
    reason is `mucin_out_of_class` (D-111 — never ESMFold) while their spans are over-ceiling
    anyway. **A row can be refused for a reason that is not its cost**, and the cost column must
    never be read as the reason a protein is missing.
    """
    from core.census_unfolded import unfolded_rows

    rows = unfolded_rows()
    if not rows:
        pytest.skip("census manifest/features artifacts absent — nothing to reconcile")
    reasons = Counter(r.get("not_folded_reason") for r in rows)
    counts = Counter(cost_for_span(s) for s in _manifest_spans())
    assert reasons["ceiling_unmeasured"] == counts[RENTAL] == 349
    assert reasons["above_local_ceiling"] == 424
    assert reasons["mucin_out_of_class"] == 3
    assert reasons["above_local_ceiling"] + reasons["mucin_out_of_class"] == counts[OVER_CEILING]
    # ⚠ and the residue: one row is neither, its cost is `local`, and its cause is a DEFECT
    # rather than a category — 237 aa, should have folded, and nothing records why.
    assert reasons["reason_unrecorded"] == 1
    dio3 = next(r for r in rows if r.get("not_folded_reason") == "reason_unrecorded")
    assert cost_for_span(dio3["span_aa"]) == LOCAL
    entry = _plain(_d137_entry())
    assert "p55073" in entry, "the 777th row's unexplained absence must be named, not rounded"
    assert "424" in entry and "mucin" in entry, (
        "the entry must carry the inexact half of the reconciliation, not only the exact half"
    )


def test_every_folded_census_protein_is_inside_the_local_envelope():
    """⚠⚠ THE CLAIM D-077 LICENSES, MEASURED — and it is stronger than the 2,691 headline.

    ✅ *Reproducibility* reads: *"M of the folds underlying this result are reproducible by any
    reader with a consumer 8 GB GPU and no cloud spend."* Against `census_features.v1.jsonl`,
    **M is all of them**: the census's folds are not *mostly* locally reproducible, they are
    **all** locally reproducible — because the rows that were not affordable were never folded.

    ⚠ That asymmetry is also why the axis must not filter (refusal 3). The 777 absent rows are
    absent BECAUSE of their span; dropping them from the census would delete the evidence of the
    very bias D-077 says a cost-filtered census would introduce.
    """
    features = ROOT / "data" / "census" / "census_features.v1.jsonl"
    if not features.exists():
        pytest.skip("census features artifact absent")
    import json

    folded = {
        json.loads(line)["accession"]
        for line in features.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    assert len(folded) == 2690, f"the folded artifact moved: {len(folded)} — amend D-137"
    with (ROOT / "data" / "census" / "census_manifest.v7.csv").open(
        encoding="utf-8", newline=""
    ) as fh:
        rows = [r for r in csv.DictReader(fh) if r["census_accession"] in folded]
    assert len(rows) == 2690
    costs = Counter(cost_for_span(int(r["span_aa"])) for r in rows)
    assert costs == {LOCAL: 2690}, f"a folded census protein outside the local envelope: {costs}"
    entry = _plain(_d137_entry())
    assert "2,690" in entry and "all 2,690" in entry


# ───────────────────────────────────────────────────────────────────────── the record


def test_the_d137_entry_exists_before_the_code_claims_it():
    """⚠⚠ Method-note item 7 / the D-062 defect: a commit message naming a decision is NOT the
    decision being logged. The check is the `### D-137` entry, never a reference to it."""
    assert re.search(
        r"^### D-137 — The census gains a sortable Cost column", LOG, re.M
    ), "D-137 must be the census sortable-Cost-column entry"
    assert len(re.findall(r"^### D-137", LOG, re.M)) == 1, "exactly one D-137 entry"
    entry = _plain(_d137_entry())
    for cite in ("d-077", "d-024", "d-027", "d-087", "d-102", "d-118", "d-133", "f-008"):
        assert cite in entry, cite
    assert "deep-learning justification" in entry


def test_the_entry_carries_all_three_refusals_rather_than_citing_them():
    """⚠ D-074: an instrument that can be misused states its own limits where they are read.
    D-077's refusals are reproduced in the entry, not pointed at."""
    entry = _plain(_d137_entry())
    assert "not suitability" in entry
    assert "must not filter the census" in entry
    assert "must not become a feature" in entry
    assert "feature 1" in entry


def test_the_entry_states_the_out_list_and_claims_no_ops():
    entry = _plain(_d137_entry())
    for phrase in ("no rent", "no emit", "no fly write", "no migration", "no backfill",
                   "no f-004", "no ranking"):
        assert phrase in entry, phrase
    assert "rental stays closed" in entry


def test_the_entry_measures_the_payload_it_adds_rather_than_asserting_it_is_cheap():
    """⚠ D-016: the caveats ride on every row, and `app/reads.py` records the list at 7.1 MB /
    825 KB gzipped. The cost of repeating them is a number in the entry, with the method."""
    entry = _d137_entry()
    assert "2,732,206" in entry and "18,064" in entry
    assert "gzip" in entry.lower()
    assert "not measured" in _plain(entry), (
        "the client-side parse cost is unmeasured and must be named as such"
    )


def test_the_entry_names_what_is_not_shipped():
    """⚠ An unnamed omission reads as an oversight. D-069 wants every surface self-sufficient;
    the detail card is owed and says so."""
    entry = _plain(_d137_entry())
    assert "detail" in entry and "owed" in entry
    assert "census_summary is untouched" in entry or "census_summary" in entry


def test_the_numbering_provenance_is_recorded_not_assumed():
    """⚠⚠ F-065's class: two decision namespaces collided because a number was assumed free.
    D-137 records which ids were checked, where they were read, and what it would take to
    close the 136 hole — which is held by an in-flight PR, not lost."""
    entry = _plain(_d137_entry())
    assert "d-135" in entry and "d-136" in entry
    assert "#259" in entry and "#260" in entry
    assert "f-065" in entry


def test_the_architecture_doc_records_the_served_shape():
    """Living-doc rule 2: a PR that changes the served payload updates ARCHITECTURE, in the
    same PR and before it is filed."""
    assert "D-137" in ARCH
    plain = _plain(ARCH)
    assert "cost to fold" in plain
    assert "app/census_cost_read.py" in ARCH
    assert "tests/test_d137_census_cost_column.py" in ARCH
    assert "ui/src/components/CensusTable.cost.test.jsx" in ARCH


def test_the_component_test_ships_with_the_column():
    """A column asserted only in Python is a column no render ever exercised — and the
    ordering, the legend and the absence-rendering only exist once React runs."""
    assert UI_TEST.exists(), "the CensusTable cost-column test must ship with it"
    text = UI_TEST.read_text(encoding="utf-8")
    assert "COLUMNS" in text and "costBadgeKey" in text
    assert re.search(r"expect\(accessions\(\)\)\.toEqual\(", text), (
        "the UI test must pin the ORDER, not merely that a header exists"
    )
