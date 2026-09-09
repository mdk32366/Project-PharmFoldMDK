"""D-151 — the owner's three UI complaints, guarded at the level a Python suite can reach.

⚠⚠ **READ THE LIMIT BEFORE THE ASSERTIONS.** Nothing in this file, and nothing in
``ui/``'s 792 vitest cases, can see the defect the owner reported. **jsdom computes no
layout**; no element has a width, a scroll offset or a viewport, so an assertion that
claimed to measure a gutter or an overflow would be comparing zero with zero and
passing. The before/after figures in ``### D-151`` come from a headless-Chrome run in
    10|that build and are **not** re-run by any gate. That residual is accepted in the open
rather than answered with a screenshot-diff framework (``D-074`` dec 3), and this
docstring is where it is stated so a later reader does not mistake a green suite for a
measured page.

⚠ **What these assertions CAN do** is redden when the structure the layout depends on is
removed, which is the failure a later edit will actually have — the scroll port deleted,
a disclosure defaulted to ``open``, the retired ``width: 100%`` hack restored, the label
reverted, or the citation constant drifting from the committed source.

    20|What is pinned, and why each can go red on its own:

1. **The label moved and the ROUTE did not.** ``/targets`` is in the Story CTA, in the
   census card's dead-end note and in every shared address; a rename that broke those
   would be a worse defect than the one it fixed. Both halves are asserted together,
   because a test that checked only the words would pass on a broken link.
2. **One DOI, pinned to ``data/cohort_82.txt``.** A constant that drifts from the
   repository's own record renders as a confident link to a paper nobody checked.
3. **The retired hack stays retired**, and the rules that replace it are present — a
   pure absence assertion would pass on a deleted stylesheet.
    30|4. **Neither disclosure is ``open``.** An ``open`` default restores the exact scroll the
   owner objected to while looking like a fix.
5. **The three blocks the rulings keep visible are outside every ``<details>``** — the
   unscored claim (D-079 dec 1), the lens control (D-102) and the HPA credit
   (D-094 / D-100, where the licence makes citation a precondition of *display*).
6. **The entry exists.** Method-note item 7 / the D-062 defect: a commit message naming a
   decision does not log it. The check is the ``### D-151`` entry, never a reference to
   it.

⚠ **Nothing here scores, ranks, folds, deploys or moves a route.** ``D-079`` dec 1 is
    40|untouched and no census row becomes scored.
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
APP_TEST = (UI / "App.test.jsx").read_text(encoding="utf-8")
PAPER = (UI / "cohortPaper.js").read_text(encoding="utf-8")
CSS = (UI / "styles.css").read_text(encoding="utf-8")
CENSUS_VIEW = (UI / "components" / "CensusView.jsx").read_text(encoding="utf-8")
CENSUS_TABLE = (UI / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CENSUS_PAGE = (UI / "components" / "CensusProteinView.jsx").read_text(encoding="utf-8")
TARGET_LIST = (UI / "components" / "TargetList.jsx").read_text(encoding="utf-8")
ADC_CONTEXT = (UI / "components" / "AdcContext.jsx").read_text(encoding="utf-8")
COHORT_SOURCE = (ROOT / "data" / "cohort_82.txt").read_text(encoding="utf-8")

DOI = "10.1371/journal.pone.0308604"


def _plain(text: str) -> str:
    """⚠ Markdown emphasis stripped as well as whitespace: the log writes **Initial
    Targets** and a raw substring check would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


def _entry() -> str:
    """The D-151 entry only. The log is tens of thousands of lines and a substring found
    anywhere in it proves nothing about the entry that is meant to carry the claim."""
    start = LOG.index("### D-151")
    return LOG[start: LOG.index("\n### D-150", start)]


def _strip_jsx_comments(src: str) -> str:
    """⚠ Comments are where this tree explains itself, so they are FULL of the words the
    assertions below look for. A guard that reads them cannot tell a rendered label from
    a paragraph about one — ``F-024``'s family: match the thing you mean."""
    src = re.sub(r"\{/\*.*?\*/\}", "", src, flags=re.S)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"^\s*//.*$", "", src, flags=re.M)


# ── 1 · The menu label, and the route it must not have moved ────────────────────────────
def test_the_nav_label_is_initial_targets_and_the_route_is_unchanged():
    """⚠ BOTH HALVES, TOGETHER. The owner asked for a label; the cost of getting it wrong
    is every existing ``/targets`` link. Asserting the words alone would go green on a
    rename that broke the Story CTA and the census card."""
    app = _strip_jsx_comments(APP)
    assert '<NavLink to="/targets">Initial Targets</NavLink>' in app, (
        "the site nav does not carry the Initial Targets label on the /targets route")
    # ⚠ the ROUTE is still declared, so the deep link resolves
    assert '<Route path="/targets" element={<TargetList />} />' in app
    # ⚠ REDDENS ON REGRESSION: the bare label must not come back on that NavLink
    assert '<NavLink to="/targets">Targets</NavLink>' not in app


def test_the_owner_named_typo_is_barred_rather_than_avoided_by_care():
    """⚠ ``Inital`` is the misspelling the owner called out by name. A rule that lives
    only in somebody's attention is not a rule."""
    for name, src in (("App.jsx", APP), ("CensusProteinView.jsx", CENSUS_PAGE)):
        assert "Inital" not in src, f"{name} misspells Initial"


def test_the_menu_equivalent_link_on_the_census_card_carries_the_same_label():
    """⚠ It reads AS THE MENU NAME — it tells a reader which nav entry holds the row they
    wanted — so it moves with the menu. Scientific copy using the word *targets* does
    not, and this asserts only the link."""
    page = _strip_jsx_comments(CENSUS_PAGE)
    assert '<Link to="/targets">Initial Targets</Link>' in page
    assert '<Link to="/targets">Targets</Link>' not in page


def test_no_route_path_moved_anywhere_in_the_shell():
    """⚠⚠ THE COST OF THE RENAME, ASSERTED AS A NEGATIVE. Every route the shell declared
    before this ship still exists; a label change that quietly relocated one would be the
    defect this entry set out not to commit."""
    app = _strip_jsx_comments(APP)
    for path in ("/", "/targets", "/target/:id", "/coverage", "/census", "/census/:id",
                 "/scorer", "/cancer-burden", "/method", "/adcs", "/adcs/pipeline/:id",
                 "/adcs/:id", "/about"):
        assert f'path="{path}"' in app, f"the route {path} left the shell"


def test_the_wide_measure_is_granted_by_route_and_only_to_the_census_list():
    """⚠ A component reaching up to restyle its own container is a decision about the
    shell made in the wrong file. It is one class here, which is also what makes it
    assertable — jsdom cannot measure a width, and it can read a class."""
    app = _strip_jsx_comments(APP)
    assert "WIDE_ROUTES" in app and "'/census'" in app
    assert "className={wide ? 'wide' : undefined}" in app
    # ⚠ EXACTLY `/census`. A `startsWith` would widen `/census/:id`, which is a card.
    assert "startsWith('/census')" not in app
    assert re.search(r"main\.wide\s*\{[^}]*max-width", CSS), (
        "the wide class has no rule, so the class is decoration")


# ── 2 · The citation ────────────────────────────────────────────────────────────────────
def test_the_cohort_doi_is_one_constant_pinned_to_the_committed_source():
    """⚠⚠ THE ARTEFACT IS NAMED (D-016). A DOI typed at each call site is three strings
    free to disagree, and a citation that disagrees with itself cannot be told from a link
    to a different paper."""
    assert f"'{DOI}'" in PAPER, "cohortPaper.js does not hold the DOI"
    # ⚠ the file the constant is pinned against, read rather than described
    assert DOI in COHORT_SOURCE, "data/cohort_82.txt does not name this DOI"
    assert "Kathad et al. 2024" in COHORT_SOURCE
    assert "82 prioritised ADC targets" in COHORT_SOURCE


def test_the_paper_is_an_anchor_on_targets_and_on_about_from_that_one_constant():
    """⚠ The consumers IMPORT the constant. A second literal on a surface would be the
    drift the module exists to prevent, so its absence is asserted beside the import."""
    for name, src in (("TargetList.jsx", TARGET_LIST), ("AdcContext.jsx", ADC_CONTEXT)):
        body = _strip_jsx_comments(src)
        assert "cohortPaper.js" in src, f"{name} does not import the citation module"
        assert "COHORT_PAPER_URL" in body, f"{name} does not render the paper URL"
        assert 'target="_blank"' in body and "noopener noreferrer" in body, (
            f"{name}'s citation opens a tab without severing the opener")
        assert DOI not in body.replace("COHORT_PAPER_DOI", ""), (
            f"{name} types the DOI itself instead of reading the pinned constant")


def test_the_paper_citation_does_not_absorb_the_hpa_obligation():
    """⚠⚠ TWO SOURCES, TWO OBLIGATIONS, TWO MODULES. D-100 records that Kathad's S3 is a
    verbatim extract of HPA's ``pathology.tsv``, so citing the paper is expressly NOT
    citing HPA. This reddens if the atlas publication is ever routed through the cohort
    module to save a file."""
    assert "10.1126/science.1260419" not in PAPER
    assert "proteinatlas" not in PAPER.lower()
    # ⚠ and the HPA precondition itself is untouched: the list still emits the credit
    assert "HpaCredit" in TARGET_LIST
    assert "HpaAttribution" in CENSUS_TABLE


# ── 3 · The census layout ───────────────────────────────────────────────────────────────
def test_the_retired_width_hack_is_gone_and_its_replacements_are_present():
    """⚠⚠ ASSERTED IN BOTH DIRECTIONS. A bare absence check would pass on a deleted
    stylesheet, which is why the positives ride with the negative — ``A-016``'s rule that
    a red must fire at the claim, applied to a green."""
    assert len(CSS) > 1000, "the stylesheet read reached no bytes"
    assert not re.search(r"\.census-table\s+td:nth-child\(3\)\s*\{[^}]*width:\s*100%", CSS), (
        "the retired width:100% hack is back — it is what made the table overflow right")
    assert re.search(r"\.census-table-scroll\s*\{[^}]*overflow:\s*auto", CSS), (
        "the scroll port has no overflow rule, so the table can widen the document again")
    assert re.search(r"\.census-table-scroll\s*\{[^}]*max-height", CSS), (
        "the port has no height bound — a port that never scrolls vertically leaves the "
        "sticky thead stuck to a scrollport that cannot move")
    assert re.search(r"\.census-table\s+\.protein-name\s*\{[^}]*max-width", CSS), (
        "the protein name has no bound on a block child (D-142's rule)")


def test_the_protein_name_is_bounded_and_never_truncated():
    """⚠ **A bound is not a truncation.** No ellipsis, no clipping, no ``max-height`` on
    the cell: the longest census names run past 70 characters and every one of them stays
    on screen, which is the standing rule ``.col-rank`` and ``.description-text`` follow."""
    block = re.search(r"\.census-table\s+\.protein-name\s*\{([^}]*)\}", CSS).group(1)
    assert "text-overflow" not in block
    assert "ellipsis" not in block
    assert "max-height" not in block
    assert "overflow-wrap" in block, "a bounded name with no wrap rule can only overflow"


def test_the_table_lives_inside_the_scroll_port_with_its_sticky_header():
    """⚠ ``position: sticky`` resolves against the nearest scrollport ancestor, so the
    ``<thead>`` and the wrapper are one fact, not two."""
    table = _strip_jsx_comments(CENSUS_TABLE)
    assert '<div className="census-table-scroll">' in table
    port = table.index('<div className="census-table-scroll">')
    assert table.index("<table>", port) > port, "the table is not inside the port"
    assert re.search(r"\.census-table\s+thead\s+th\s*\{[^}]*position:\s*sticky", CSS)


def test_neither_disclosure_defaults_to_open():
    """⚠⚠ AN ``open`` DEFAULT WOULD RESTORE THE EXACT SCROLL THE OWNER OBJECTED TO WHILE
    LOOKING LIKE A FIX. Matched on the opening tag, because these files discuss ``open``
    in prose immediately above it."""
    assert '<details className="census-background">' in CENSUS_VIEW
    assert '<details className="census-notes">' in CENSUS_TABLE
    assert 'className="census-background" open' not in CENSUS_VIEW
    assert 'className="census-notes" open' not in CENSUS_TABLE


def test_the_long_sections_moved_and_none_of_them_was_deleted():
    """⚠ **Collapsed is not cut.** Every block that used to stand between the reader and
    the list is still rendered — inside the disclosure, in full."""
    for cls in ("census-counts", "census-absences", "census-tranches", "lede"):
        assert f'className="{cls}"' in CENSUS_VIEW, f"{cls} left the page instead of moving"
    # ⚠ and the sections that always sat BELOW the table still do
    for cls in ("census-found", "census-howread", "census-limits"):
        assert f'className="{cls}"' in CENSUS_VIEW


def test_the_three_blocks_the_rulings_keep_visible_are_outside_every_disclosure():
    """⚠⚠ WHAT MAY NOT COLLAPSE IS RULED, NOT CHOSEN, and each has a different authority:
    the unscored claim (D-079 dec 1) because a reader who stops at the first row must have
    met it; the lens control (D-102) because the applied lens is part of what the
    Stained % column MEANS; the HPA credit (D-094 / D-100) because the licence words
    citation as a precondition of *display*.

    ⚠ Positional, not semantic: each must appear BEFORE the disclosure that follows it in
    source order, which is the property that would break if someone moved it inside."""
    view = _strip_jsx_comments(CENSUS_VIEW)
    assert view.index('className="census-bar"') < view.index('<details className="census-background"')

    table = _strip_jsx_comments(CENSUS_TABLE)
    notes = table.index('<details className="census-notes">')
    for marker in ('className="census-scope"', '<div className="lens-control">',
                   "<HpaAttribution attribution="):
        assert marker in table, f"{marker} left the census table"
        assert table.index(marker) < notes, (
            f"{marker} was moved inside or below the disclosure — that block's position "
            f"is fixed by a ruling, not by the layout")


def test_the_ui_guards_exist_and_say_what_they_cannot_see():
    """⚠ The vitest suites are the other half of this change, and the honest limit is
    written into them rather than left for a reader to discover."""
    for name in ("cohortPaper.test.js",):
        assert (UI / name).exists(), f"{name} is missing"
    for name in ("TargetList.citation.d151.test.jsx", "CensusLayout.d151.test.jsx"):
        assert (UI / "components" / name).exists(), f"{name} is missing"
    layout = (UI / "components" / "CensusLayout.d151.test.jsx").read_text(encoding="utf-8")
    assert "jsdom computes no layout" in layout, (
        "the layout suite does not state that it cannot see a layout")
    assert "Initial Targets" in APP_TEST, "the shell suite does not pin the new nav label"


# ── 4 · The log, the architecture doc, and the integer ──────────────────────────────────
def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠⚠ METHOD-NOTE ITEM 7 / THE D-062 DEFECT. A commit message naming a decision does
    not discharge the living-documentation rule. **The check is the entry.**"""
    assert LOG.count("\n### D-151 —") == 1
    assert LOG.index("\n### D-151") < LOG.index("\n### D-150")
    # ⚠ NAMES NO LEADER BY NUMBER. D-147 recorded this trap of itself twice: an assertion
    # that pins *which* entry is newest expires the moment anything newer lands, for
    # reasons that have nothing to do with this entry.
    assert re.search(r"^## Log \(newest first\)\s*\n\s*### D-\d{3} — ", LOG, re.M), (
        "the log does not open with a decision heading")
    between = LOG[LOG.index("\n### D-151"): LOG.index("\n### D-150")]
    assert not re.search(r"^### D-1[0-4]\d\b", between, re.M), (
        "an older entry was inserted above D-150 — the log is ordered newest first")


def test_the_entry_leads_with_the_disqualifying_fact_about_the_citation_asymmetry():
    """⚠⚠ THE FACT THAT POINTS AT THIS PROJECT'S OWN DISCIPLINE RATHER THAN AT A LAYOUT.
    A compliance rule was built for the source whose licence demanded one, and the paper
    the entire cohort comes from fell through the gap. An entry that led with the census
    scroll instead would be reporting the easy half."""
    entry = _plain(_entry())
    head = entry[:2600]
    assert "disqualifying fact" in head
    assert "precondition" in head
    assert "0308604" in head, "the entry does not name the DOI that was absent"
    assert "0 hits" in head or "returns 0" in head, (
        "the entry asserts an absence without the measurement behind it")


def test_the_entry_names_its_instrument_and_its_before_and_after_figures():
    """⚠ Provenance (D-016): a number with no artefact is a belief. The layout figures did
    not come from the test suite and the entry has to say what they did come from."""
    entry = _plain(_entry())
    assert "headless chrome" in entry
    assert "1440" in entry and "900" in entry
    assert "bdc8ddc" in entry, "the entry does not name the commit it measured before"
    for figure in ("914", "3,303", "809", "29,772"):
        assert figure in _entry(), f"the entry does not carry the measured {figure}"


def test_the_entry_states_what_it_cannot_establish():
    """⚠⚠ THE RESIDUAL IS THE PART A GATE CANNOT CHECK, SO IT IS WRITTEN DOWN. jsdom has
    no layout, the measurements ran against a fixture, and nothing was deployed."""
    entry = _plain(_entry())
    assert "what this entry cannot establish" in entry
    assert "jsdom" in entry
    assert "fixture" in entry
    assert "nothing was deployed" in entry


def test_the_entry_refuses_to_call_a_bound_a_truncation():
    """⚠ The standing rule on these surfaces: **demotion is not deletion, and a bound is
    not a truncation.** The entry has to say so, because the next person to meet a wide
    column will reach for an ellipsis."""
    entry = _plain(_entry())
    assert "never truncated" in entry
    assert "no column dropped" in entry


def test_the_architecture_doc_is_current_in_this_same_pr():
    """⚠ CLAUDE.md rule 2 — ``ARCHITECTURE.md`` is brought current in the same PR, before
    it is filed. A stale architecture doc means the PR is incomplete."""
    flat = _plain(ARCH)
    assert "d-151" in flat
    assert "cohortpaper.js" in flat
    assert "census-table-scroll" in flat
    assert "initial targets" in flat
    # ⚠ the row that owns the census surface names this decision, not a paragraph elsewhere
    row = next(l for l in ARCH.splitlines() if l.startswith("| **Census surface**"))
    assert "**D-151**" in row


def test_the_next_free_integer_is_named_and_barred_and_148_is_still_a_held_hole():
    """⚠⚠ **Bar OR name, never neither.** ``### D-151`` is claimed by name here;
    ``### D-148`` is a ``RESERVED.md`` HOLD for the trafficking Spec and stays BARRED;
    ``### D-152`` takes the next-free bar. ⚠ Nothing is relaxed to a ``>=``: a ``>=`` here
    would pass on a log with no entries at all.

    ⚠ The bars are matched WITH their newline, because this file holds such patterns as
    *data* in order to check the others; a newline-less match would find a "bar" in the
    file whose job is to look for one. That is D-145's recorded mistake, not rediscovered
    here."""
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 151 in ids, "this entry did not claim its own integer"
    assert 148 not in ids and 152 not in ids
    assert "\n### D-148" not in LOG, (
        "D-148 is a RESERVED HOLD for the trafficking Spec and must stay unspent until "
        "that Spec claims it by name — never admitted by a `>=`")
    assert "\n### D-152" not in LOG, (
        "D-152 is the next free integer and must stay unspent until an entry claims it by "
        "name — never admitted by a `>=`")


def test_the_reserved_map_retires_151_marker_safe_and_the_pointer_moves_here():
    """⚠⚠ MARKER-SAFE, and the reason is mechanical rather than stylistic: two other
    suites locate the 151 row with ``re.search(r"^\\| \\*\\*D-151\\*\\*", …)``, so striking
    it to ``~~**D-151**~~`` would break those guards instead of satisfying them. The
    D-142 / D-145 / D-146 / D-147 / D-150 rows each record the same trap of themselves."""
    assert re.search(r"^\| \*\*D-151\*\*", RESERVED, re.M), (
        "D-151 lost its row; the citation invariant then has a hole indistinguishable "
        "from D-062's")
    row151 = next(l for l in RESERVED.splitlines() if l.startswith("| **D-151**"))
    assert "WRITTEN" in row151, "the 151 row does not record that the integer was spent"
    assert "Original reservation text" in row151, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)")
    assert re.search(r"^\| \*\*D-152\*\*", RESERVED, re.M), (
        "the bar moved to 152, so 152 must be a RESERVED row")
    assert re.search(r"^\| \*\*D-148\*\*", RESERVED, re.M), "the trafficking hold lost its row"
    assert not re.search(r"^\| ~~\*\*D-15[12]\*\*~~", RESERVED, re.M), (
        "a marker is struck through; that breaks this suite's lookup instead of "
        "satisfying it")
    # ⚠⚠ THE POINTER MOVES IN THE SAME COMMIT THAT SPENDS THE INTEGER, AND IT SKIPS THE
    # HOLD. A reserved integer is not a free one — that is this file's whole purpose.
    assert "Next free `D-` integer: **`D-152`**" in RESERVED
    for spent in ("D-147", "D-148", "D-149", "D-150", "D-151"):
        assert f"Next free `D-` integer: **`{spent}`**" not in RESERVED, (
            f"the pointer still names {spent}, which would hand a spent or held integer "
            f"to the next writer")


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ ``RESERVED.md``'s own command, run rather than quoted. **Read the output, not an
    exit code**: the only passing result is that nothing NEW is unresolved. ``D-131`` (the
    suffix half of ``### D-130-B / D-131``) and ``F-067`` (open in #222) are pre-existing
    and untouched by this ship."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}")
