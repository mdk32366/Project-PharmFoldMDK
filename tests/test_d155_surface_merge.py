"""D-155 — one population, one table. All of these must go red if their claim is reverted.

⚠⚠ **THE DEFECT THIS FILE PINS IS A DELETION, WHICH IS THE HARDEST KIND TO GUARD.** `/coverage` is
retired and `CoverageView.jsx` is gone. A route can be deleted in one line, and everything that was
true *because* it existed — the honest denominator on screen, the per-row reason, the census strip,
the four in-app links that pointed at it — fails silently and separately. So the assertions below
are mostly about **what survived the deletion**, not about the deletion itself.

⚠ The clauses of `D-024` am. §3, `D-135`, `D-043` and `D-118` are NOT re-asserted here: they are
asserted by `tests/test_d135_coverage_dual_population.py` and `ui/src/components/
TargetList.dual.test.jsx`, both of which followed their subject onto the merged surface in this same
ship. **A second copy of a guard is how two guards drift** (`F-052`), so this file asserts what is
new and points at those for what merely moved.

⚠ Source-level throughout, plus the shared vitest file for what a reader sees. No network, no Fly,
no ops, no GPU, no database.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
UI = ROOT / "ui" / "src"
APP = (UI / "App.jsx").read_text(encoding="utf-8")
TARGET_LIST = (UI / "components" / "TargetList.jsx").read_text(encoding="utf-8")
COVERAGE_NOTE = (UI / "components" / "coverageNote.jsx").read_text(encoding="utf-8")
CSS = (UI / "styles.css").read_text(encoding="utf-8")
STORY = (UI / "components" / "Story.jsx").read_text(encoding="utf-8")
ADC_CONTEXT = (UI / "components" / "AdcContext.jsx").read_text(encoding="utf-8")
SCORER_PANEL = (UI / "components" / "TargetScorerPanel.jsx").read_text(encoding="utf-8")

#: Every component that can render a link into the app. ⚠ The sweep is over ALL of them rather than
#: over the three the first pass thought of — which is exactly how two links in
#: `TargetScorerPanel.jsx` were nearly left pointing at a route that no longer exists.
COMPONENTS = sorted((UI / "components").glob("*.jsx")) + sorted(UI.glob("*.jsx"))


def _no_comments(src: str) -> str:
    """⚠ `F-024` — match the thing you mean. Every file in this ship EXPLAINS `/coverage` at length,
    so a raw substring check fires on the reasoning about the deletion rather than on a live link."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


# ───────────────────────────── the route is gone, and nothing points at it ─────────────────────


def test_the_coverage_route_and_its_component_are_both_gone():
    """⚠ Both halves. A route removed while the component stays is dead code that the next reader
    re-mounts; a component removed while the route stays is a blank page."""
    app = _no_comments(APP)
    assert 'path="/coverage"' not in app, "the /coverage route is back in the shell"
    assert "CoverageView" not in app, "the shell still imports the deleted view"
    assert not (UI / "components" / "CoverageView.jsx").exists(), (
        "CoverageView.jsx is back — one population with two tables is the defect D-155 closed")


def test_no_component_anywhere_still_links_to_the_retired_route():
    """⚠⚠ THE SILENT HALF OF A DELETION, AND THE ONE THIS SHIP NEARLY SHIPPED. Three links were
    known (`Story.jsx` ×3, `AdcContext.jsx`) and **two more were found in `TargetScorerPanel.jsx`
    only by sweeping every component**. A link to a retired route does not error: it bounces the
    reader to the Story through the catch-all, with nothing saying why.
    ⚠ The sweep is the guard. A list of three files would have passed on the tree that had the
    defect."""
    offenders = []
    for path in COMPONENTS:
        body = _no_comments(path.read_text(encoding="utf-8"))
        if 'to="/coverage"' in body or 'href="/coverage"' in body:
            offenders.append(path.name)
    assert not offenders, f"these components still link to the retired route: {offenders}"


def test_the_links_that_moved_point_at_the_surface_that_holds_the_content_now():
    """⚠ Repointed, never deleted. The Story's three mentions and the ADC-context one are claims
    about where the honest denominator lives, and it lives on `/targets`."""
    assert STORY.count('to="/targets"') >= 3, "the Story lost a link it should have repointed"
    assert 'to="/targets">honest coverage line</Link>' in ADC_CONTEXT
    assert SCORER_PANEL.count('to="/targets"') >= 2, (
        "the scorer panel's two reason links did not follow the merge")


def test_the_api_route_is_untouched_and_the_system_model_did_not_move():
    """⚠⚠ THE UI ROUTE WENT; THE DATA ROUTE DID NOT. `GET /api/coverage` is what the merged surface
    consumes, and `system-model.json` draws API routes — so `D-051` must NOT fire on this ship, and
    a reader of the architecture diagram must not conclude the denominator supplier was retired."""
    model = (UI / "system-model.json").read_text(encoding="utf-8")
    assert "/api/coverage" in model, "the coverage API route left the system model"
    assert "getCoverage" in TARGET_LIST, "the merged surface stopped consuming /api/coverage"


# ───────────────────────────── what the merged surface must still say ──────────────────────────


def test_the_merged_surface_leads_with_the_denominator_and_closes_with_the_second_population():
    """⚠ Order is the claim. The honest denominator (D-024 am. §3) is above the table; the census
    strip (D-135) is below it; neither is inside a disclosure — asserted structurally, because the
    way this goes wrong is a later ship tidying one of them into the `<details>` beside it."""
    body = _no_comments(TARGET_LIST)
    assert body.index("<CoverageLine") < body.index('<div className="table-scroll">')
    assert body.index("<CensusPopulationStrip") > body.index("</table>")
    for block in ("<CoverageLine", "<CensusPopulationStrip"):
        before = body[: body.index(block)]
        assert before.count("<details") == before.count("</details>"), (
            f"{block} is inside an open <details> — a claim behind a disclosure control")


def test_the_filter_caveat_came_with_the_denominator_it_qualifies():
    """⚠⚠ THE SENTENCE MATTERS MORE HERE THAN IT DID ON THE PAGE IT LEFT. A search box now sits
    between a denominator panel and a ranked table, so *"one row of 82"* under *"67 ranked & folded
    of 82"* is the available misread. ⚠ And it must be TRUE: `CoverageLine` takes `all`, never the
    filtered rows."""
    assert "The denominator above is unchanged" in TARGET_LIST
    element = TARGET_LIST[TARGET_LIST.index("<CoverageLine"):]
    element = element[: element.index("/>") + 2]
    assert "rows={all}" in element, "the denominator is computed from the FILTERED rows"
    assert "filtered" not in element


def test_the_status_cell_keeps_three_axes_apart_and_invents_no_fourth_fold_value():
    """⚠⚠ D-150's PATTERN, ON THE COHORT. One word doing three jobs is the defect that entry fixed
    on the census; four facts on two pages was the mirror image here. ⚠ `D-043`'s three fold values
    stand — a census structure of the same accession is a BRIDGE, never a fourth verdict."""
    assert "function StatusCell" in TARGET_LIST
    for axis in ("status-disposition", "status-fold", "status-confidence"):
        assert axis in TARGET_LIST, f"the {axis} axis left the status cell"
    cell = TARGET_LIST[TARGET_LIST.index("function StatusCell"):]
    cell = cell[: cell.index("\n}")]
    for invented in ("folded elsewhere", "folded in census", "partially folded"):
        assert invented not in cell, f"a fourth fold value appeared: {invented}"


def test_the_rank_cell_names_its_absence_and_never_shows_a_bare_dash():
    """⚠⚠ THE GUARD THAT CAUGHT THIS SHIP'S FIRST DRAFT. `TargetList.rank.test.jsx` rejected an em
    dash here by name, and it was right: an unranked row is not a row with a missing number
    (owner ruling TA2). The cell states the category in a word and the cause is one cell right."""
    cell = TARGET_LIST[TARGET_LIST.index('<td className="mono col-rank-num">'):]
    cell = cell[: cell.index("</td>")]
    assert ">unranked<" in cell, "the rank cell stopped naming the category"
    assert "—" not in cell, "the bare dash is back in the rank cell"
    assert "rankCause(row, rankingServed)" in cell, "the cause stopped travelling as the title"


def test_the_long_reasons_are_disclosed_per_row_and_only_where_one_exists():
    """⚠ A `why` control that opens onto nothing promises a reason the record does not hold, so the
    disclosure is conditional. ⚠ And it is never `open`: an open default restores the exact scroll
    the collapse exists to end while looking like a fix (D-152)."""
    assert "hasCoverageNote(row) ? coverageNote(row) : null" in TARGET_LIST
    assert "{note && (" in TARGET_LIST, "the disclosure is rendered unconditionally"
    note_block = TARGET_LIST[TARGET_LIST.index('className="status-note"'):]
    note_block = note_block[: note_block.index("</details>")]
    assert " open" not in note_block, "the per-row disclosure defaults to open"


def test_the_bridge_module_kept_the_rule_that_a_census_id_never_rides_a_cohort_row():
    """⚠⚠ THE NAMED STOP CONDITION, AND THE MERGE MAKES IT MORE LOAD-BEARING RATHER THAN LESS: one
    row now renders BOTH links — the cohort's `/target/:id` and the census's `/census/:accession`.
    ⚠ Comments stripped first (`F-024`): the module explains this rule at length."""
    code = _no_comments(COVERAGE_NOTE)
    assert "to={`/census/${r.accession}`}" in code
    assert "analysis_id" not in code, "the bridge learned about a census analysis id"
    assert "export function coverageNote" in COVERAGE_NOTE
    assert "export function hasCoverageNote" in COVERAGE_NOTE


# ───────────────────────────── the column budget ───────────────────────────────────────────────


def test_the_rank_column_gave_its_width_back_and_the_description_took_it():
    """⚠ A property of the STYLESHEET, and checkable without a browser — which matters, because the
    rendered figures for this ship are owed rather than measured (see the entry). ⚠ Bounds, not
    truncation: `min-width` halves and `overflow-wrap` are untouched and nothing is ellipsised."""
    wide = CSS.split("@media (min-width: 1100px)")[1]
    wide = wide[: wide.index("\n}")]
    assert "max-width: 5rem" in CSS.split(".target-list .col-rank-num")[1][:120], (
        "the rank column is no longer bounded to the width of its integer")
    assert ".target-list .col-description { max-width: 30rem; }" in wide, (
        "the Description column did not take the width the Rank column gave back")
    assert ".target-list .col-status { max-width: 20rem; }" in wide
    assert "text-overflow" not in CSS.split(".target-list .col-status")[1][:200]


def test_no_column_was_dropped_to_make_the_merge_fit():
    """⚠⚠ THE STANDING RULE OF THIS TABLE: a column removed to make a layout work is data withheld
    to flatter it. Eight headers, and the four the merge touched are each still named."""
    cols = TARGET_LIST[TARGET_LIST.index("const COLUMNS = ["):]
    cols = cols[: cols.index("\n]")]
    for label in ("'Rank'", "'Gene'", "'Accession'", "'Description'",
                  "'Cancer association'", "'Tier'", "'mean pLDDT'"):
        assert label in cols, f"the {label} column left the table"
    assert "Status (disposition" in cols, "the merged status column is not declared"
    assert "confidence" in cols, "the status header stopped naming confidence (D-048's demotion)"


# ───────────────────────────── the wide-measure ruling ─────────────────────────────────────────


def test_the_three_prose_routes_joined_the_wide_measure_and_every_card_stayed_narrow():
    """⚠⚠ AN OWNER RULING THAT SUPERSEDES `D-152` DECISION 2 IN PART, and the negative half is what
    keeps the set meaningful: cards stay at the reading measure."""
    app = _no_comments(APP)
    wide = app.split("WIDE_ROUTES")[1].split("])")[0]
    for route in ("'/'", "'/method'", "'/about'", "'/targets'", "'/census'",
                  "'/scorer'", "'/cancer-burden'", "'/adcs'"):
        assert route in wide, f"{route} is in the owner's wide ruling and is not in the set"
    assert "'/coverage'" not in wide, "a retired route is still in the wide set"
    for card in ("'/target/", "'/census/:", "'/adcs/:"):
        assert card not in wide, f"{card} is a card and must keep the reading measure"
    assert "startsWith(" not in app, "an exact-path set became a prefix match"


def test_the_superseded_argument_is_kept_rather_than_edited_away():
    """⚠ `D-129-C`: a decision that loses is recorded as having lost, in the place a reader will be
    when they wonder why the code disagrees with a shipped entry."""
    assert "D-152 DECISION 2 IS SUPERSEDED" in APP.upper()
    assert "harder to read" in APP, (
        "the reasoning D-155 overruled was deleted rather than kept beside its supersession")


# ───────────────────────────── the living-documentation ritual ─────────────────────────────────


def test_the_log_entry_leads_with_the_measurement_that_changed_the_design():
    assert re.search(r"^### D-155 — One population had two tables", LOG, re.M)
    assert len(re.findall(r"^### D-155 —", LOG, re.M)) == 1
    assert LOG.index("### D-155 —") < LOG.index("### D-154 —"), "newest first"
    entry = LOG.split("### D-155 —", 1)[1].split("\n### D-154 —", 1)[0]
    assert "58%" in entry, "the entry does not carry the measurement that cut three columns to one"
    assert "3 of 82" in entry or "3 of its\n82" in entry
    assert "owed" in entry, "the unmeasured after-figures are not declared as owed"
    assert "Deep-learning justification" in entry
    assert "supersede" in entry.lower(), "the entry does not name what it amends"


def test_the_next_free_integer_is_named_and_barred_and_148_is_still_a_held_hole():
    """⚠⚠ **Bar OR name, never neither.** ``### D-155`` is claimed by name here; ``### D-148`` stays
    BARRED as the trafficking hold; ``### D-156`` takes the next-free bar. Nothing is relaxed to a
    ``>=``: a ``>=`` would pass on a log with no entries at all.

    ⚠ The bars are matched WITH their newline — this file holds such patterns as *data* in order to
    check the others, and a newline-less match would find a "bar" in the file whose job is to look
    for one (D-145's recorded mistake)."""
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 155 in ids, "this entry did not claim its own integer"
    assert 154 in ids and 152 in ids, "the entries this one builds on must still be named"
    assert 148 not in ids and 156 not in ids
    assert "\n### D-148" not in LOG
    assert "\n### D-156" not in LOG, (
        "D-156 is the next free integer and must stay unspent until an entry claims it by name — "
        "never admitted by a `>=`")


def test_the_reserved_map_retires_155_marker_safe_and_the_pointer_moves_here():
    assert re.search(r"^\| \*\*D-155\*\*", RESERVED, re.M), "D-155 lost its row"
    row = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-155**"))
    assert "WRITTEN" in row and "Original reservation text" in row
    assert re.search(r"^\| \*\*D-156\*\*", RESERVED, re.M), "the bar moved to 156 with no row"
    assert not re.search(r"^\| ~~\*\*D-15[56]\*\*~~", RESERVED, re.M)
    assert "Next free `D-` integer: **`D-156`**" in RESERVED
    for spent in ("D-152", "D-153", "D-154", "D-155"):
        assert f"Next free `D-` integer: **`{spent}`**" not in RESERVED


def test_architecture_records_the_retirement_rather_than_only_the_log():
    """⚠ CLAUDE.md rule 2: the route table is system shape. A surface that stops existing is exactly
    the kind of change a stale architecture doc hides."""
    assert "D-155" in ARCH
    assert "/coverage" in ARCH, (
        "the architecture doc says nothing about the route that was retired — a reader following it "
        "would look for a page that is gone")


def test_the_component_suite_ships_beside_the_python_one():
    """⚠ Source text is not a render. The 21 D-135 cases and the merged surface's own cases both
    mount the component; this asserts they exist rather than trusting that they do."""
    dual = UI / "components" / "TargetList.dual.test.jsx"
    assert dual.exists(), "the two-population component suite did not follow the merge"
    assert "D-135" in dual.read_text(encoding="utf-8")
    assert not (UI / "components" / "CoverageView.dual.test.jsx").exists(), (
        "the old component suite is still here — two suites over one surface will drift")


# ───────────────────────────── the follow-up ───────────────────────────────────────────────────


def test_each_status_axis_states_only_what_that_axis_knows():
    """⚠⚠ THE DEPLOYED MERGE SAID `not folded` THREE TIMES on `MUC16` and `FAT2`, and it took reading
    the live page to see it — every suite was green while it was on screen. **It is the defect the
    owner reported at the `D-150` follow-up, re-created by the entry that cites `D-150`.**

    ⚠ Two rules, asserted as source properties here and as counted occurrences in
    `TargetList.merge.d155.test.jsx`: the rank cause renders only where the row HAS a fold, and
    `causeOnly` drops a leading verdict from the confidence axis."""
    # ⚠ FOLLOW-UP 2 lengthened this expression (the disposition gate joined the fold gate), so the
    # assertion pins the FOLD half by name rather than the whole line it happened to be on.
    assert "foldState === 'folded' && causeAddsSomething(" in TARGET_LIST, (
        "the rank cause is back on rows whose fold axis already gives the reason")
    assert "export function causeOnly" in TARGET_LIST
    assert "causeOnly(absentLabel(row))" in TARGET_LIST, (
        "the confidence axis repeats the fold verdict again")


def test_the_rank_cause_names_the_question_it_answers():
    """⚠⚠ *"in the ranking set — excluded by the pre-registered mean pLDDT floor of 50"* is one
    sentence saying a row is in a set and out of it. The halves answer different questions:
    `ranked` is `D-024`'s partition, the floor decides the SCORED set at fit time (`D-066`'s 67 vs
    56). The prefix is what keeps them apart, so it is pinned."""
    assert '"status-line status-cause">no rank — {cause}' in TARGET_LIST, (
        "the cause lost the prefix that says which question it answers")
    disposition = TARGET_LIST[TARGET_LIST.index("status-disposition disp-"):]
    disposition = disposition[: disposition.index("</span>")]
    assert "cause" not in disposition, (
        "the cause is joined onto the disposition line again — that reads as a contradiction")


def test_causeonly_strips_a_verdict_and_never_empties_a_cell():
    """⚠ A known PREFIX, never a search, and never an empty result: a blank cell is an unnamed
    absence, which `D-154` spent an entry closing."""
    body = TARGET_LIST[TARGET_LIST.index("export function causeOnly"):]
    body = body[: body.index("\n}")]
    assert "startsWith(verdict)" in body, "the strip became a search and can truncate a new wording"
    assert "return rest || text" in body, "a label that is only a verdict now renders as an empty cell"


def test_the_prose_pages_actually_fill_the_width_they_were_given():
    """⚠⚠ THE OTHER HALF OF DECISION 6, AND THE HALF-DONE STATE LOOKED WORSE THAN EITHER END.
    `main.wide` is 96rem and `.prose` kept a 44rem measure with no auto margins, so Story, Method
    and About ADCs rendered a narrow column pinned to the LEFT with ~52rem of empty gutter. Owner,
    2026-09-10: *"Story, Method, and About ADCs are simply left justified now. They are not using
    the entire width of the surface."*

    ⚠ SCOPED, NOT GLOBAL. `.prose` is also a CARD's body, and cards keep the reading measure by this
    entry's own negative half — so the override hangs off `main.wide` and a bare `max-width: none`
    on `.prose` would redden here."""
    assert re.search(r"^\.prose \{[^}]*max-width:\s*44rem", CSS, re.M), (
        "the reading measure for a card's prose is gone")
    assert re.search(r"^main\.wide \.prose \{[^}]*max-width:\s*none", CSS, re.M), (
        "the wide routes' prose does not fill the measure the owner ruled for")
    scoped = CSS[CSS.index("main.wide .prose"):]
    assert scoped[: scoped.index("}")].count("max-width") == 1


def test_the_cause_gate_is_an_equality_against_a_named_restatement():
    """⚠⚠ FOLLOW-UP 2, AND THE SHAPE OF THE GATE IS THE CLAIM. Follow-up 1 suppressed the cause where
    the FOLD axis carried it; the deployed page then said *"held out of ranking · no rank — held out
    · folded"*. The gate now also asks whether the DISPOSITION carried it.

    ⚠ An EQUALITY against a named restatement, never a `startsWith`: *"excluded by the pre-registered
    mean pLDDT floor of 50"* begins with `excluded` and belongs on a `ranked` row, so a prefix test
    would delete the one cause on this surface that nothing else explains."""
    assert "export function causeAddsSomething" in TARGET_LIST
    body = TARGET_LIST[TARGET_LIST.index("export function causeAddsSomething"):]
    body = body[: body.index("\n}")]
    assert "!==" in body, "the gate stopped comparing for equality"
    assert "startsWith" not in body and "includes" not in body, (
        "the gate became a substring test — it will swallow the below-floor cause")
    assert "causeAddsSomething(rawCause, row.disposition)" in TARGET_LIST


def test_the_reason_for_a_hold_stays_on_the_row_after_the_cause_is_dropped():
    """⚠ Dropping a repetition must not drop a fact. `held out` with no reason invites the reader to
    supply one, and D-021's reason is a property of the PARTITION — so it rides on the axis as its
    title rather than becoming a fourth line."""
    assert "DISPOSITION_WHY" in TARGET_LIST
    assert "boundary method is not comparable (D-021)" in TARGET_LIST
    # ⚠ the sentence is a two-line concatenation in source, so the halves are asserted; the JOINED
    # string is asserted where it actually matters, on the rendered title, in the vitest file.
    assert "judgement about the target" in TARGET_LIST
    assert "title={DISPOSITION_WHY[row.disposition] || undefined}" in TARGET_LIST
