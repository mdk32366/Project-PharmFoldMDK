"""D-152 — the census navigation pattern on the other five list surfaces, guarded at the level a
Python suite can reach.

⚠⚠ **READ THE LIMIT BEFORE THE ASSERTIONS.** Nothing in this file, and nothing in ``ui/``'s 822
vitest cases, can see what the owner asked for. **jsdom computes no layout** and this file does not
run a browser at all; no element here has a width, a fold or a scroll offset, so an assertion
claiming to measure a gutter would be comparing zero with zero and passing. The before/after figures
in ``### D-152`` come from a headless-Chrome run in that build and are **not** re-run by any gate.
That residual is accepted in the open rather than answered with a screenshot-diff framework
(``D-074`` dec 3), and this docstring is where it is stated so a later reader does not mistake a
green suite for a measured page.

⚠ **What these assertions CAN do** is redden when the structure the layout depends on is removed —
the shared rules deleted, a route dropped out of the wide set, a scroll port unwrapped, a disclosure
defaulted to ``open``, or a block a ruling keeps visible moved inside one.

What is pinned, and why each can go red on its own:

1. **The primitives are shared, not copied.** Five copies of one rule set look identical the day they
   are written and diverge on the first tweak — ``F-052``. The census's own class names ride in the
   same rules, because renaming them would redden the guards ``D-151`` shipped, and rewriting a
   shipped guard to accommodate a refactor is how a guard becomes a decoration.
2. **The wide measure is granted by route, to lists only.** Prose keeps the reading measure; every
   card route stays narrow; membership is a set of literals, never a ``startsWith``.
3. **Every list table is inside a port**, which is also what the sticky ``<thead>`` resolves against.
4. **No disclosure defaults to ``open``** — an ``open`` default restores the scroll it was collapsed
   to end while looking like a fix.
5. **Nothing that makes a claim collapses**, and each exception is named by the ruling that fixes it
   rather than by preference.
6. **The retired defects stay retired**: ``visibility: hidden`` on a laid-out tooltip, and a
   ``.row-search`` class with no rule behind it.
7. **The entry exists.** Method-note item 7 / the D-062 defect: a commit message naming a decision
   does not log it. The check is the ``### D-152`` entry, never a reference to it.

⚠ **Nothing here scores, ranks, folds, deploys or moves a route.** ``D-079`` dec 1 is untouched and
no census row becomes scored.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")

UI = ROOT / "ui" / "src"
APP = (UI / "App.jsx").read_text(encoding="utf-8")
CSS = (UI / "styles.css").read_text(encoding="utf-8")
COMPONENTS = UI / "components"
TARGET_LIST = (COMPONENTS / "TargetList.jsx").read_text(encoding="utf-8")
COVERAGE = (COMPONENTS / "CoverageView.jsx").read_text(encoding="utf-8")
SCORER = (COMPONENTS / "ScorerView.jsx").read_text(encoding="utf-8")
BURDEN = (COMPONENTS / "CancerBurdenView.jsx").read_text(encoding="utf-8")
ADCS = (COMPONENTS / "AdcsView.jsx").read_text(encoding="utf-8")
CENSUS_VIEW = (COMPONENTS / "CensusView.jsx").read_text(encoding="utf-8")
CENSUS_TABLE = (COMPONENTS / "CensusTable.jsx").read_text(encoding="utf-8")

# ⚠ The five surfaces this ship touched, by the file that renders each. `/census` is deliberately
# NOT here — it is the surface the pattern came FROM, and its own guards are `test_d151_ui_polish`.
TOUCHED = {
    "/targets": TARGET_LIST,
    "/coverage": COVERAGE,
    "/scorer": SCORER,
    "/cancer-burden": BURDEN,
    "/adcs": ADCS,
}


def _plain(text: str) -> str:
    """⚠ Markdown emphasis stripped as well as whitespace: the log writes **main.wide** and a raw
    substring check would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


def _entry() -> str:
    """The D-152 entry only. The log is tens of thousands of lines and a substring found anywhere in
    it proves nothing about the entry that is meant to carry the claim."""
    start = LOG.index("\n### D-152 —") + 1
    nxt = re.search(r"^### (?!D-152\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def _strip_jsx_comments(src: str) -> str:
    """⚠ Comments are where this tree explains itself, so they are FULL of the words the assertions
    below look for. A guard that reads them cannot tell a rendered container from a paragraph about
    one — ``F-024``'s family: match the thing you mean."""
    src = re.sub(r"\{/\*.*?\*/\}", "", src, flags=re.S)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"^\s*//.*$", "", src, flags=re.M)


def _css_block(selector_regex: str) -> str:
    """The declarations of the first rule whose selector list matches, with comments removed first.

    ⚠ Comments are stripped BEFORE the search for the same reason as above, and because `D-141` lost
    a guard to exactly this shape: a check satisfied by a comment containing the string it wanted.
    """
    css = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    # ⚠ `re.M`, so a caller can anchor a selector to the START OF A LINE. Without it `^` means start
    # of file and `^\.row-search` silently matches nothing — which this helper then reports as an
    # absent rule, i.e. a guard that fails for the wrong reason. Found by running it.
    m = re.search(selector_regex + r"\s*\{([^}]*)\}", css, re.M)
    assert m, f"no rule matched {selector_regex}"
    return m.group(1)


# ── 1 · The primitives are shared, not copied ───────────────────────────────────────────────────
def test_the_disclosure_and_the_port_are_defined_once_for_every_surface():
    """⚠⚠ THE F-052 SHAPE, PREVENTED RATHER THAN DETECTED. Five copies of these declarations would
    render identically on the day they were written and diverge on the first tweak, and no component
    test could see it because every surface would still look right."""
    assert len(CSS) > 1000, "the stylesheet read reached no bytes"
    assert re.search(r"\.surface-notes,\s*\.census-background,\s*\.census-notes\s*\{", CSS), (
        "the disclosure block is no longer one rule shared with the census")
    assert re.search(r"\.table-scroll,\s*\n\.census-table-scroll\s*\{", CSS), (
        "the scroll port is no longer one rule shared with the census")
    # ⚠ and D-151's own rules are still readable exactly as its guards read them — a refactor that
    # renamed them would have broken three shipped guards instead of satisfying them
    assert re.search(r"\.census-table-scroll\s*\{[^}]*overflow:\s*auto", CSS)
    assert re.search(r"\.census-table-scroll\s*\{[^}]*max-height", CSS)
    assert '<details className="census-background">' in CENSUS_VIEW
    assert '<details className="census-notes">' in CENSUS_TABLE
    assert '<div className="census-table-scroll">' in CENSUS_TABLE


def test_the_sticky_header_is_written_against_the_shared_port():
    """⚠ ``position: sticky`` resolves against the nearest scrollport ancestor and a box with no
    height bound never scrolls, so the port, its ``max-height`` and this rule are ONE mechanism.
    Written against `.table-scroll` rather than per surface, so a sixth list inherits it by being
    wrapped rather than by remembering to."""
    port = _css_block(r"\.table-scroll,\s*\n\.census-table-scroll")
    assert "overflow: auto" in port
    assert "max-height" in port
    head = _css_block(r"\.table-scroll thead th")
    assert "position: sticky" in head
    assert "top: 0" in head


def test_the_shared_search_box_has_a_rule_behind_its_class():
    """⚠⚠ IT DID NOT, AND THAT IS THIS ENTRY'S SECOND FOUND DEFECT. ``TargetList`` rendered
    ``className="row-search"`` while ``rg -n 'row-search' ui/src/styles.css`` returned **0**, so the
    search box the owner asked for by name drew as an unstyled browser default beside a census box
    that was styled. A class with no rule is not a style — it is a hope."""
    block = _css_block(r"^\.row-search")
    for prop in ("background", "border", "padding"):
        assert prop in block, f".row-search has no {prop} rule: {block}"


def test_a_closed_tooltip_is_not_laid_out():
    """⚠⚠ THE FIRST FOUND DEFECT, BARRED BY NAME RATHER THAN REMEMBERED. A ``visibility: hidden``
    box is still LAID OUT, and an absolutely-positioned laid-out box still enlarges the document's
    scrollable overflow. 320px of closed tooltip was doing that on every page; at the old 60rem
    measure it hung into the gutter unnoticed, and a widened ``/scorer`` measured **144 px** of
    standing horizontal overflow. ⚠ The text stays in the DOM — ``aria-describedby`` resolves to a
    ``display: none`` element by specification — so F-006's tooltip requirement is untouched."""
    block = _css_block(r"\.term-def")
    assert "display: none" in block
    assert "visibility: hidden" not in block, (
        "the laid-out-while-hidden tooltip is back; it silently widens every document it is on")
    assert re.search(r"\.term:hover \.term-def[^{]*\{[^}]*display:\s*block", CSS)


# ── 2 · The wide measure, granted by route ──────────────────────────────────────────────────────
def test_the_wide_measure_reaches_every_list_route_and_no_prose_route():
    """⚠ A component reaching up to restyle its own container is a decision about the shell made in
    the wrong file. It is a set of literals here, which is also what makes it assertable — jsdom
    cannot measure a width and it can read a class."""
    app = _strip_jsx_comments(APP)
    assert "WIDE_ROUTES" in app
    for route in ("/targets", "/coverage", "/census", "/scorer", "/cancer-burden", "/adcs"):
        assert f"'{route}'" in app.split("WIDE_ROUTES")[1].split("])")[0], (
            f"{route} is a list route and is not in the wide set")
    # ⚠⚠ THE NEGATIVE HALF IS THE POINT OF THE SET. Widening a paragraph makes it harder to read, so
    # the prose routes are absent BY DECISION and their absence is asserted, not assumed.
    wide_set = app.split("WIDE_ROUTES")[1].split("])")[0]
    for prose in ("'/method'", "'/about'"):
        assert prose not in wide_set, f"{prose} is prose and must keep the reading measure"
    assert "className={wide ? 'wide' : undefined}" in app
    # ⚠ EXACT PATHS. A `startsWith` would widen `/census/:id`, `/target/:id`, `/adcs/:id` and
    # `/adcs/pipeline/:id`, every one of which is a card.
    assert "startsWith(" not in app
    assert re.search(r"main\.wide\s*\{[^}]*max-width", CSS), (
        "the wide class has no rule, so the class is decoration")


def test_no_route_path_moved_anywhere_in_the_shell():
    """⚠⚠ THE COST OF A LAYOUT SHIP, ASSERTED AS A NEGATIVE. Every route the shell declared before
    this ship still exists; a re-layout that quietly relocated one would break every shared address
    to buy nothing, which is the trap D-151 refused when it moved a label and not a path."""
    app = _strip_jsx_comments(APP)
    for path in ("/", "/targets", "/target/:id", "/coverage", "/census", "/census/:id",
                 "/scorer", "/cancer-burden", "/method", "/adcs", "/adcs/pipeline/:id",
                 "/adcs/:id", "/about"):
        assert f'path="{path}"' in app, f"the route {path} left the shell"
    assert '<NavLink to="/targets">Initial Targets</NavLink>' in app, (
        "D-151's nav label was lost by this ship")


# ── 3 · Every touched surface got the pattern ───────────────────────────────────────────────────
def test_every_touched_surface_wraps_its_table_in_the_shared_port():
    for route, src in TOUCHED.items():
        body = _strip_jsx_comments(src)
        assert '<div className="table-scroll">' in body, (
            f"{route} has no scroll port — its table can widen the document again")


def test_every_touched_surface_that_collapsed_prose_used_the_shared_disclosure():
    """⚠ ``/coverage`` and ``/cancer-burden`` are deliberately absent: neither COLLAPSED anything.
    Coverage's long block was moved below the table (D-135 makes it a claim, and moving a block is
    not demoting it — hiding one is), and the burden page's long blocks were already below its
    table, which is where D-151 left the census's. **A surface that needed no disclosure did not get
    one to look consistent.**"""
    for route in ("/targets", "/scorer", "/adcs"):
        body = _strip_jsx_comments(TOUCHED[route])
        assert 'className="surface-notes' in body, f"{route} lost its disclosure"
    for route in ("/coverage", "/cancer-burden"):
        body = _strip_jsx_comments(TOUCHED[route])
        assert "surface-notes" not in body, (
            f"{route} grew a disclosure it was ruled not to need — check the entry before adding "
            f"one, because on this surface the long block is a CLAIM")


def test_no_disclosure_on_any_surface_defaults_to_open():
    """⚠⚠ AN ``open`` DEFAULT RESTORES THE EXACT SCROLL THE COLLAPSE EXISTS TO END, WHILE LOOKING
    LIKE A FIX. Matched on the opening tag, because these files discuss ``open`` in the prose
    immediately above it."""
    for route, src in TOUCHED.items():
        for m in re.finditer(r"<details className=\"surface-notes[^\"]*\"([^>]*)>", src):
            assert "open" not in m.group(1), f"{route} ships an open-by-default disclosure"


def test_every_touched_surface_has_a_search_box():
    """⚠ Four of the five never had one. ``/coverage`` listed the same 82 proteins as ``/targets``
    and offered no way to find one; ``/adcs`` had a sortable table and no way to reach a row."""
    for route, src in TOUCHED.items():
        body = _strip_jsx_comments(src)
        assert 'className="row-search"' in body, f"{route} has no search box"
        assert 'type="search"' in body, f"{route}'s search box is not typed as one"


def test_the_shared_matcher_is_reused_where_the_population_is_proteins():
    """⚠⚠ AND IS DELIBERATELY NOT REUSED WHERE IT IS NOT. ``../searchRows.js`` reads accession,
    gene, label, description and aliases. That is right for the two cohort lists — it is why
    ``CA-125`` reaches ``MUC16`` and ``HER2`` reaches ``ERBB2``. It is wrong for an ADC row, whose
    identity is its drug name and INN, and it is wrong for a burden row, which carries no accession,
    gene, score or rank BY DESIGN (D-149's wall). **A search box that silently cannot find
    ``Enhertu`` is worse than none, because the miss reads as *this drug is not in the catalog*.**"""
    # ⚠ COMMENTS STRIPPED FIRST, and the negative half is exactly why: both files EXPLAIN at length
    # why they do not import the shared matcher, so they necessarily contain its name as prose. A
    # substring check over the raw source fires on the file's own reasoning about itself — `F-024`,
    # match the thing you mean — and it did, on the first run of this test.
    for route in ("/coverage", "/scorer"):
        assert "searchRows.js" in TOUCHED[route], f"{route} does not use the shared matcher"
    for route in ("/cancer-burden", "/adcs"):
        assert "searchRows.js" not in _strip_jsx_comments(TOUCHED[route]), (
            f"{route} was pointed at the protein matcher; its rows have none of those fields")
    assert "function matchesAdc" in ADCS
    assert "function matchesSite" in BURDEN


# ── 4 · What may NOT collapse is decided by the rulings ─────────────────────────────────────────
def test_the_standing_claims_stay_outside_every_disclosure_and_above_it():
    """⚠⚠ WHAT MAY NOT COLLAPSE IS RULED, NOT CHOSEN, and each has a different authority. Positional
    rather than semantic: each must appear BEFORE the disclosure that follows it in source order,
    which is the property that would break if someone moved it inside."""
    # /targets — the fold-confidence claim (a green dot must not read as a verdict on a target) and
    # ⚠⚠ the D-151 paper citation, whose whole finding was that the cohort's primary source could
    # not be reached. Collapsing it would undo that entry one release later.
    tl = _strip_jsx_comments(TARGET_LIST)
    notes = tl.index('<details className="surface-notes')
    for marker in ('className="note confidence-scope-note"', 'className="note cohort-paper-cite"'):
        assert marker in tl, f"{marker} left /targets"
        assert tl.index(marker) < notes, (
            f"{marker} was moved inside or below the disclosure — its position is fixed by a "
            f"ruling, not by the layout")
    # ⚠ the HPA credit is emitted outside every disclosure, as the licence requires (D-094 / D-100)
    assert tl.index("<HpaCredit") > notes and "surface-notes" not in tl[notes:tl.index("<HpaCredit")].split("</details>")[1]

    # /adcs — the floor claim is what stops a reader counting these rows as *the* approved ADCs
    ad = _strip_jsx_comments(ADCS)
    assert ad.index('className="adcs-floor"') < ad.index('<details className="surface-notes')

    # /scorer — section D holds both pre-registered negative outcomes and the three caveats
    sc = _strip_jsx_comments(SCORER)
    d_start = sc.index('className="scorer-result"')
    close = sc.index("</details>")
    assert close < d_start, "section D was pulled inside the A/B/C disclosure"
    assert 'className="caveats"' in sc and sc.index('className="caveats"') > close


def test_coverage_keeps_the_denominator_first_and_moves_the_census_strip_without_hiding_it():
    """⚠⚠ D-135's CLAUSES, EACH STILL TRUE. The strip is below the coverage line, labelled, carries
    no fraction, and is in NO disclosure — what changed is only that the table now comes between
    them. **Moving a block is not demoting it; hiding one is.**"""
    cov = _strip_jsx_comments(COVERAGE)
    assert cov.index("<CoverageLine") < cov.index('<div className="table-scroll">')
    assert cov.index("<CensusPopulationStrip") > cov.index("</table>")
    assert "surface-notes" not in cov, "the census population strip was collapsed rather than moved"


def test_the_burden_surface_keeps_every_block_a_ruling_placed():
    """⚠ D-149 put the US-only bar above the toggle, the limits below the table and the SEER
    attribution at the foot. None of them moved and none of them is inside a control."""
    b = _strip_jsx_comments(BURDEN)
    assert b.index('className="burden-us-only"') < b.index('className="burden-toggle"')
    assert b.index('className="burden-limits"') > b.index("</table>")
    assert b.index('className="burden-attribution"') > b.index('className="burden-limits"')
    assert "surface-notes" not in b


# ── 5 · A filter narrows a view and may never move a number ─────────────────────────────────────
def test_the_burden_bar_scale_is_derived_before_the_filter():
    """⚠⚠ THE ONE PLACE A SEARCH BOX COULD TELL A LIE ON THIS SURFACE. Re-normalising the bars to the
    filtered maximum would draw a rare cancer at full width the moment a reader typed its name, and
    a bar chart's whole claim is that length is comparable. ⚠ Asserted on the SOURCE LINE that
    computes `max`, because the ordering of these two statements is the entire guarantee."""
    b = _strip_jsx_comments(BURDEN)
    line = next(ln for ln in b.splitlines() if ln.strip().startswith("const max ="))
    assert "ranked.map(barValue)" in line, f"the bar scale is not the full population's: {line}"
    assert "shownRanked" not in line and "matchesSite" not in line, (
        "the bar scale was derived from the filtered rows — a filter must not rescale a chart")
    # ⚠ and the rank is the SERVED rank, never the row index: a filtered table shows #3 with gaps
    assert "{r.rank_within_statistic}" in b


def test_the_scorer_score_distribution_is_derived_from_the_run_not_the_view():
    """⚠⚠ `scores` FEEDS THE SCORE HEADER'S TOOLTIP, WHICH REPORTS THE SPAN, THE MEDIAN AND THE
    COUNT OF THE SCORES IN THIS RUN — a property of the pre-registered result (F-004 / D-062). If a
    filter could move it, a published median would become a function of a text input."""
    sc = _strip_jsx_comments(SCORER)
    line = next(ln for ln in sc.splitlines() if ln.strip().startswith("const scores ="))
    assert "ranking.rows.map" in line, line
    assert "shown" not in line, "the score distribution is derived from the filtered rows"
    # ⚠ and the search state lives in the extracted ranking component, so `FullResult`'s derived
    # numbers cannot see it at all — the guarantee is structural, not a habit
    assert "function ScorerRanking(" in SCORER
    assert "const shown = filterRows(ranking.rows, query)" in SCORER


def test_the_ranking_table_leads_in_source_order_and_not_by_a_css_order():
    """⚠⚠ SOURCE ORDER, NOT A CSS ``order``. A grid ``order`` moves the box and leaves the reading
    order — the one a screen reader follows, and the one a narrow viewport collapses to — exactly as
    it was, which is the version of this change that looks fixed and is not."""
    sc = _strip_jsx_comments(SCORER)
    cols = sc.index('<div className="scorer-cols">')
    assert sc.index("<ScorerRanking", cols) < sc.index('<div className="scorer-explain">', cols)
    assert not re.search(r"\.scorer-(ranking|explain)\s*\{[^}]*\border\s*:", CSS), (
        "the columns were reordered in CSS, which leaves the reading order untouched")


def test_an_unrecognised_ranking_status_is_stated_rather_than_thrown():
    """⚠ `/api/cancer-burden` is 500ing on the deployed app as this ships, and fixing that is held
    elsewhere. What this ship owes every surface is that a failure renders AS a failure: "nothing
    matched", "not loaded" and "the request failed" must not look the same, and none of them may
    look like an empty page. `FullResult` read `ranking.result.distribution` on its first line."""
    assert "if (!ranking.result)" in SCORER
    assert "scorer-unrecognised" in SCORER
    # ⚠ it reports the status it was handed rather than falling back to `not_run`, which would be a
    # CLAIM (that no result has been recorded) this branch is not entitled to make
    assert "no result body" in SCORER


# ── 6 · The guards, the log, the architecture doc, and the integer ──────────────────────────────
def test_the_ui_guard_suite_exists_and_says_what_it_cannot_see():
    layout = COMPONENTS / "SurfaceLayout.d152.test.jsx"
    assert layout.exists(), "the D-152 vitest suite is missing"
    text = layout.read_text(encoding="utf-8")
    assert "jsdom computes no layout" in text, (
        "the layout suite does not state that it cannot see a layout")
    # ⚠ the three cases that guard a NUMBER rather than a container are the ones worth naming here,
    # because they are the ones whose absence would ship a lie rather than an ugly page
    assert "cannot rewrite a statistic" in text


def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠⚠ METHOD-NOTE ITEM 7 / THE D-062 DEFECT. A commit message naming a decision does not
    discharge the living-documentation rule. **The check is the entry.**"""
    assert LOG.count("\n### D-152 —") == 1
    # ⚠⚠ NEWEST FIRST IS BY LAND ORDER, NOT BY NUMBER. `### D-153` landed on `main` while this
    # branch was open and sits BELOW this entry, because this entry lands after it. That is the
    # existing convention working; it is the first time the two orderings disagree, and the entry
    # says so.
    assert LOG.index("\n### D-152") < LOG.index("\n### D-153")
    assert LOG.index("\n### D-153") < LOG.index("\n### D-151")
    # ⚠ NAMES NO LEADER BY NUMBER. D-147 recorded this trap of itself twice: an assertion that pins
    # *which* entry is newest expires the moment anything newer lands, for reasons that have nothing
    # to do with this entry.
    assert re.search(r"^## Log \(newest first\)\s*\n\s*### D-\d{3} — ", LOG, re.M), (
        "the log does not open with a decision heading")
    between = LOG[LOG.index("\n### D-152"): LOG.index("\n### D-151")]
    assert not re.search(r"^### D-1[0-4]\d\b", between, re.M), (
        "an older entry was inserted above D-151 — the log is ordered newest first")


def test_the_entry_leads_with_the_fact_that_the_defect_was_not_the_reported_one():
    """⚠⚠ THE FACT THAT POINTS AT THIS SHIP'S OWN FIRST DRAFT RATHER THAN AT A LAYOUT. A pattern is
    a set of remedies, and applying one means measuring each surface to find which of them it needs.
    An entry that led with "five surfaces got the census treatment" would be reporting the easy
    half."""
    entry = _plain(_entry())
    head = entry[:3000]
    assert "disqualifying fact" in head
    assert "175" in head, "the entry does not name the number the draft asserted"
    assert "16,409" in _entry(), "the entry does not carry the measured page height"
    assert "191" in head, "the entry does not carry the measured row height"


def test_the_entry_names_its_instrument_and_its_before_and_after_figures():
    """⚠ Provenance (D-016): a number with no artefact is a belief. The layout figures did not come
    from the test suite, so the entry has to say what they did come from — and it has to say that
    the fixture is a fixture."""
    entry = _plain(_entry())
    assert "headless chrome" in entry
    assert "puppeteer-core" in entry
    assert "1440" in entry and "900" in entry
    assert "41b9b3b" in entry, "the entry does not name the commit it measured before"
    for figure in ("16,409", "1,130", "144", "1,440"):
        assert figure in _entry(), f"the entry does not carry the measured {figure}"
    # ⚠ the regression proof: /census measuring identically is what says the shared primitives were
    # extracted out from under a shipped surface without disturbing it
    assert "regression proof" in entry


def test_the_entry_states_what_it_cannot_establish():
    """⚠⚠ THE RESIDUAL IS THE PART A GATE CANNOT CHECK, SO IT IS WRITTEN DOWN. jsdom has no layout,
    the measurements ran against a fixture, nothing was deployed, and the burden route is still
    500ing in production."""
    entry = _plain(_entry())
    assert "what this entry cannot establish" in entry
    assert "jsdom" in entry
    assert "fixture" in entry
    assert "nothing was deployed" in entry
    assert "http 500" in entry, "the entry does not name the failure it is NOT fixing"


def test_the_entry_refuses_to_call_a_bound_a_truncation_or_to_drop_a_column():
    """⚠ The standing rule on these surfaces, inherited from D-142 and D-151: **demotion is not
    deletion and a bound is not a truncation.** The entry has to say so, because the next person to
    meet a wide table will reach for an ellipsis."""
    entry = _plain(_entry())
    assert "never drops a column" in entry or "no column dropped" in entry or "never truncated" in entry
    assert "truncat" in entry
    assert "moving a block is not demoting it" in entry


def test_the_architecture_doc_is_current_in_this_same_pr():
    """⚠ CLAUDE.md rule 2 — ``ARCHITECTURE.md`` is brought current in the same PR, before it is
    filed. A stale architecture doc means the PR is incomplete."""
    flat = _plain(ARCH)
    assert "d-152" in flat
    assert "surface-notes" in flat
    assert "table-scroll" in flat
    assert "wide_routes" in flat
    # ⚠ the row that owns the shared pattern names this decision, not a paragraph elsewhere
    row = next(ln for ln in ARCH.splitlines() if ln.startswith("| **List-surface navigation**"))
    assert "**D-152**" in row
    assert "D-151" in row, "the row does not say which decision the pattern came from"


def test_the_next_free_integer_is_named_and_barred_and_148_is_still_a_held_hole():
    """⚠⚠ **Bar OR name, never neither.** ``### D-152`` is claimed by name here; ``### D-148`` is a
    ``RESERVED.md`` HOLD for the trafficking Spec and stays BARRED; ``### D-153`` was spent by the
    burden-loader image bake — the lane that HELD 152 for this one — so it is NAMED rather than
    barred, and ``### D-154`` takes the next-free bar. ⚠ Nothing is relaxed to a ``>=``: a ``>=`` here would pass on a log with no entries at all.

    ⚠ The bars are matched WITH their newline, because this file holds such patterns as *data* in
    order to check the others; a newline-less match would find a "bar" in the file whose job is to
    look for one. That is D-145's recorded mistake, not rediscovered here."""
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 152 in ids, "this entry did not claim its own integer"
    assert 151 in ids, "the entry this one builds on must still be named"
    # ⚠⚠ 153 IS NAMED, NOT BARRED, AND BY A LANE THAT IS NOT THIS ONE. `D-153` (the burden-loader
    # image bake) landed on `main` while this branch was open; it SKIPPED 152, held it for this lane
    # by name, and moved the pointer to 154. So the integer this entry spends was reserved FOR it,
    # and the bar it inherited moves to 154 rather than 153.
    assert 153 in ids, (
        "D-153 was spent by the burden-loader image bake, which held 152 for this lane; it must be "
        "NAMED here rather than barred")
    assert 148 not in ids and 154 not in ids
    assert "\n### D-148" not in LOG, (
        "D-148 is a RESERVED HOLD for the trafficking Spec and must stay unspent until that Spec "
        "claims it by name — never admitted by a `>=`")
    assert "\n### D-154" not in LOG, (
        "D-154 is the next free integer and must stay unspent until an entry claims it by name — "
        "never admitted by a `>=`")


def test_the_reserved_map_retires_152_marker_safe_and_the_pointer_moves_here():
    """⚠⚠ MARKER-SAFE, and the reason is mechanical rather than stylistic: three other suites locate
    the 152 row with ``re.search(r"^\\| \\*\\*D-152\\*\\*", …)``, so striking it to ``~~**D-152**~~``
    would break those guards instead of satisfying them. The D-142 / D-145 / D-146 / D-147 / D-150 /
    D-151 rows each record the same trap of themselves."""
    assert re.search(r"^\| \*\*D-152\*\*", RESERVED, re.M), (
        "D-152 lost its row; the citation invariant then has a hole indistinguishable from D-062's")
    row152 = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-152**"))
    assert "WRITTEN" in row152, "the 152 row does not record that the integer was spent"
    assert "Original reservation text" in row152, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)")
    assert re.search(r"^\| \*\*D-153\*\*", RESERVED, re.M), (
        "D-153 is cited here, so it must remain a RESERVED row")
    assert re.search(r"^\| \*\*D-154\*\*", RESERVED, re.M), (
        "the bar moved to 154, so 154 must be a RESERVED row")
    assert re.search(r"^\| \*\*D-148\*\*", RESERVED, re.M), "the trafficking hold lost its row"
    assert not re.search(r"^\| ~~\*\*D-15[234]\*\*~~", RESERVED, re.M), (
        "a marker is struck through; that breaks this suite's lookup instead of satisfying it")
    # ⚠⚠ AND THE ONE PLACE THIS SHIP DOES **NOT** MOVE THE POINTER, WHICH IS THE POINT RATHER THAN
    # AN OMISSION. The standing rule is *the pointer moves in the SAME commit that spends the
    # integer*, and its purpose is that a spent number is never handed to the next writer. `D-153`
    # skipped 152, held it for this lane and moved the pointer to 154 before this branch landed — so
    # there was nothing left to move, and moving it again would have skipped a FREE integer.
    # ⚠ The assertion that matters is unchanged: the pointer must name NO spent or held number.
    assert "Next free `D-` integer: **`D-154`**" in RESERVED
    for spent in ("D-147", "D-148", "D-149", "D-150", "D-151", "D-152", "D-153"):
        assert f"Next free `D-` integer: **`{spent}`**" not in RESERVED, (
            f"the pointer still names {spent}, which would hand a spent or held integer to the "
            f"next writer")


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ ``RESERVED.md``'s own command, run rather than quoted. **Read the output, not an exit
    code**: the only passing result is that nothing NEW is unresolved. ``D-131`` (the suffix half of
    ``### D-130-B / D-131``) and ``F-067`` (open in #222) are pre-existing and untouched here."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}")
