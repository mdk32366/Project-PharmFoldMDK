"""D-150 — three orthogonal status axes on the census surface. These must go red.

One badge was answering three unrelated questions, and a reader had no way to tell
which one it had answered:

    A  is a structure served, and what KIND of thing is it
    B  was this protein scored and ranked
    C  if it was assembled from tiles, is its seam solved

**The witness is FAT2.** ``GET https://pharmfoldmdk.fly.dev/api/census/Q9NYQ8``, read
live on 2026-09-09, answers ``folded: true`` · ``structure_kind: "assembled"`` ·
``structure_kind_label: "assembled (provisional)"`` · ``hold48_kind:
"parent_stitched"`` · ``scored: false`` · ``assembler_note: "assembled by pLDDT
overlap, not superimposed; seam not solved"`` · ``assembly_review.served_path.solved:
false`` with ``not_flipped_reason: "not_in_pass_subset"``. **Four statuses, and the
card's Status block led with one expression for all of them:**
``structure_kind_label ?? (folded === false ? 'NOT FOLDED' : 'Folded')``.

⚠ **Why nothing ever caught it.** ``Folded`` is *true* of a single-pass fold, of a
provisional assembly whose seam is not solved, and of a parent the D-139 gate refused
to flip. The word cannot be wrong — which is exactly why it told a reader nothing, and
why no assertion about its correctness would ever have failed.

⚠ **What these assertions pin, and why each can go red on its own:**

1. **One module owns all three rules.** A surface that re-derives an axis is a second
   definition waiting to disagree with the first (D-133 am. 1's ``topologyBadgeKey``
   lesson, applied where the list and the card carry *different payloads*).
2. **The bare-``Folded`` fallback is gone from the card**, and the card's Status block
   no longer prints IGF2R's ``≈ 88.76 Å`` inline — that is a measurement on a
   *different protein*, and a true number in the wrong place is a false implication.
3. **``bandFor(null)`` no longer says "not folded".** It is the 3Dmol colour function
   for every residue of a structure that is *on disk and rendering*; a missing NUMBER
   was being reported as a missing STRUCTURE.
4. **The status column is a real ``COLUMNS`` entry**, so D-087's "sorts on every
   column" stays true — the exact defect D-133 had to repair for Structure.
5. **``tiles_only`` can never wear the fold verdict.** Those rows are served
   ``folded: false`` while their tiles sit on disk.
6. **The entry exists.** Method-note item 7 / the D-062 defect: a commit message
   naming a decision is not the decision being logged. The check is the ``### D-150``
   entry, never a reference to it.

⚠ **Nothing here is a seam claim.** ``assembled`` stays **provisional**, the served
path stays the **assembler**, the **10.0 Å** gate does not move, and no parent is
flipped. ⚠ **Nothing here scores or ranks** — D-079 dec 1 and D-109 ruling 7 are
untouched, and axis B exists precisely to keep saying so.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")

UI = ROOT / "ui" / "src"
STATUS = (UI / "structureStatus.js").read_text(encoding="utf-8")
PLDDT = (UI / "plddt.js").read_text(encoding="utf-8")
CENSUS_TABLE = (UI / "components" / "CensusTable.jsx").read_text(encoding="utf-8")
CENSUS_DETAIL = (UI / "components" / "CensusDetail.jsx").read_text(encoding="utf-8")
CENSUS_PAGE = (UI / "components" / "CensusProteinView.jsx").read_text(encoding="utf-8")
CONFIDENCE = (UI / "components" / "Confidence.jsx").read_text(encoding="utf-8")
VIEWER = (UI / "components" / "StructureViewer.jsx").read_text(encoding="utf-8")
UI_TEST = UI / "components" / "CensusStatus.d150.test.jsx"


def _plain(text: str) -> str:
    """⚠ Markdown emphasis stripped as well as whitespace: the log writes ``**never** a bare
    ``Folded```, and a substring check would miss it and read as an absent claim."""
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


def _entry() -> str:
    """The D-150 entry only — the log is 27k lines and a substring match anywhere in it
    proves nothing about the entry that is supposed to carry the claim."""
    start = LOG.index("### D-150")
    return LOG[start: LOG.index("\n### D-149", start)]


def _strip_js_comments(src: str) -> str:
    """⚠⚠ COMMENTS FIRST, ALWAYS. Every file in this change explains the defect it repairs, in
    prose that necessarily quotes the forbidden strings — ``'Folded'``, ``not folded``,
    ``88.76``. A raw grep would find the guard's own warning about itself and report the defect
    as still present. This project has recorded that shape (`F-024`) more times than any other,
    including inside tests written to catch it."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"^\s*//.*$", " ", src, flags=re.M)


# ------------------------------------------------------- one module, three rules


def test_one_module_owns_all_three_axes():
    """⚠ Each axis is a named export, so a surface asks the rule rather than re-deriving it."""
    for name in ("structureServed", "structureServedLabel", "scoreState", "seamState"):
        assert f"export function {name}" in STATUS, f"{name} is not exported from structureStatus.js"


def test_axis_a_declares_exactly_the_four_categories():
    """⚠ Four and only four. A fifth invented here would be a category no payload can produce."""
    code = _strip_js_comments(STATUS)
    values = set(re.findall(r"export const STRUCTURE_(?:NONE|TILES_ONLY|ONESHOT|ASSEMBLED_SERVED) = '([^']+)'", code))
    assert values == {"none", "tiles_only", "oneshot", "assembled_served"}, values


def test_axis_c_declares_exactly_the_four_seam_states():
    """⚠ The KEYS, not the copy — `SEAM_*_COPY` is prose and is allowed to be edited; the state set
    is a contract and is not."""
    code = _strip_js_comments(STATUS)
    values = set(re.findall(r"export const SEAM_(?!\w*COPY\b)[A-Z_]+ = '([^']+)'", code))
    assert values == {"n/a", "provisional_assembler", "pass_path_served", "artifacts_absent"}, values


def test_the_tiles_branch_runs_before_the_folded_denial():
    """⚠⚠ THE NAMED FORBIDDEN CASE, ASSERTED ON THE ORDER RATHER THAN ON AN OUTPUT. A
    ``tiles_only`` row is served ``folded: false`` because no PARENT was assembled — its tiles are
    on disk. Reading the denial first printed **NOT FOLDED** over a payload saying the opposite.
    Branch order IS the rule, so the rule is what is pinned; the rendered outcome is pinned
    separately in the vitest file."""
    body = _strip_js_comments(STATUS)
    body = body[body.index("export function structureServed"):]
    body = body[: body.index("\n}")]
    tiles = body.index("tiles_only")
    denial = body.index("folded === false")
    assert tiles < denial, (
        "the folded denial is read before the tiles branch, so a tiles_only row can still be "
        "labelled NOT FOLDED — the exact claim D-150 exists to stop")


def test_an_absent_folded_field_is_never_read_as_a_denial():
    """⚠ ``=== false``, never ``!r.folded``. Legacy rows predate the field, and the census table's
    folded count has read ``!== false`` since it arrived. A missing field is not a recorded
    ``false``, and treating it as one would print NOT FOLDED over every legacy row."""
    body = _strip_js_comments(STATUS)
    assert "folded === false" in body
    assert not re.search(r"!\s*r\.folded\b", body), (
        "structureServed reads a falsy folded rather than a recorded false")


# ------------------------------------------------------- what the UI must not say


def test_the_card_no_longer_falls_back_to_a_bare_folded():
    """⚠⚠ THE DEFECT, DELETED RATHER THAN COMMENTED AROUND. The Status block led with
    ``structure_kind_label ?? (folded === false ? 'NOT FOLDED' : 'Folded')``."""
    code = _strip_js_comments(CENSUS_DETAIL)
    assert "'Folded'" not in code, "the bare Folded fallback is still reachable on the census card"
    assert "structureServedLabel" in code, "the card does not ask axis A for its structure word"


def test_no_surface_prints_a_bare_folded_as_a_status_word():
    """⚠ Across all four surfaces, comments stripped first. ``NOT FOLDED`` is allowed and required
    where it is true; a standalone ``Folded`` as the whole status is what is barred."""
    for name, src in (
        ("CensusDetail", CENSUS_DETAIL), ("CensusTable", CENSUS_TABLE),
        ("CensusProteinView", CENSUS_PAGE), ("structureStatus", STATUS),
    ):
        code = _strip_js_comments(src)
        assert not re.search(r"['\"]Folded['\"]", code), f"{name} still carries a bare Folded literal"


def test_the_card_does_not_paste_igf2rs_angstroms_onto_every_assembly():
    """⚠⚠ A TRUE NUMBER IN THE WRONG PLACE. The Status block read *"Seam not solved (IGF2R ≈ 88.76 Å
    is a measured caveat, not a solved structure)"* on **every** assembled parent — so a reader of
    FAT2 was handed a measurement taken on IGF2R as part of FAT2's own status. The per-parent
    sentence is ``assembler_note``, which the payload already carries.

    ⚠ The figure is NOT banned from the project: ``MethodNote``, ``PlddtExplainer`` and the viewer
    banner each name IGF2R alongside it, which is a cohort-level disclosure and stays."""
    code = _strip_js_comments(CENSUS_DETAIL)
    assert "88.76" not in code, "the census card still hard-codes IGF2R's seam figure"
    assert "seamState" in code, "the card does not read the per-parent seam rule"


def test_the_seam_rule_reads_assembler_note_and_never_seam_note():
    """⚠⚠ STRONGER THAN A PREFERENCE ORDER, AND THAT IS THE FINDING. This assertion was drafted as
    *assembler_note is read before seam_note* and went red on a ``ValueError`` instead: the rule
    does not reference ``seam_note`` **at all**. It should not. ``seam_note`` opens with *"IGF2R ≈
    88.76 Å is a measured caveat"* — a measurement on a different protein — so a rule that reached
    for it as a fallback would put those angstroms back on every card the moment a parent's own
    ``assembler_note`` was missing. The absence is the guarantee, so the absence is what is pinned."""
    body = _strip_js_comments(STATUS)
    body = body[body.index("export function seamState"):]
    body = body[: body.index("\n}")]
    assert "assembler_note" in body, "seamState does not read this parent's own note"
    assert "seam_note" not in body, (
        "seamState reads seam_note, which quotes IGF2R's ≈ 88.76 Å — another protein's measurement "
        "would ride onto this parent's status line")


def test_an_absent_review_is_named_and_never_falls_to_not_applicable():
    """⚠⚠ AN ABSENT MEASUREMENT IS NOT A SOLVED SEAM. ``assembly_review`` rides on
    ``/api/census/{id}`` and NOT on ``/api/census`` — measured 2026-09-09, the list row carries 34
    keys and that is not one of them. So the list says *artefacts absent* rather than ``n/a``,
    which would read as *this assembly has no seam question*."""
    body = _strip_js_comments(STATUS)
    body = body[body.index("export function seamState"): ]
    body = body[: body.index("\n}")]
    assert "SEAM_ARTIFACTS_ABSENT" in body
    # `n/a` is returned only on the not-an-assembly guard, which is the first branch
    na = body.index("SEAM_NOT_APPLICABLE")
    absent = body.index("SEAM_ARTIFACTS_ABSENT")
    assert na < absent, "the not-applicable answer is reachable after the absence branch"


# ------------------------------------------------------- the pLDDT band


def test_the_absent_plddt_band_says_nothing_about_folding():
    """⚠⚠ THE SHARPEST OF THE THREE. ``bandFor`` is asked by the confidence headline, the
    per-residue plot **and** the 3Dmol colour function — the last of which runs once per residue of
    a structure that is on disk and being drawn. Returning ``not folded`` there stated that the
    fold did not happen, inside the rendering of the fold. None of the three callers is in a
    position to know whether a fold exists, and two only run when one does."""
    code = _strip_js_comments(PLDDT)
    label = re.search(r"export const NO_PLDDT_LABEL = '([^']+)'", code)
    assert label, "plddt.js has no named sentinel label for an absent value"
    assert not re.search(r"fold", label.group(1), re.I), label.group(1)
    assert label.group(1) in ("no pLDDT", "pLDDT unavailable"), (
        f"the pinned wording moved to {label.group(1)!r} without moving this guard")
    assert not re.search(r"'not folded'", code), "the not-folded sentinel is still in plddt.js"


def test_the_band_boundaries_did_not_move_with_the_wording():
    """⚠ D-039's scheme is untouched: this entry renames an ABSENCE, it does not re-cut the bands.
    A copy edit that also moved a boundary would be two decisions in one diff."""
    code = _strip_js_comments(PLDDT)
    assert re.findall(r"min: (\d+),", code) == ["70", "60", "50", "0"]
    assert "COHORT_MAX_PLDDT = 84.23" in code


# ------------------------------------------------------- the census list


def test_the_status_column_is_a_real_columns_entry():
    """⚠ THE TRIPWIRE. Out of ``COLUMNS`` the header button and the sort both vanish, and a
    rendered-text assertion would pass on a hand-drawn ``<th>`` that sorts nothing."""
    cols = re.search(r"export const COLUMNS = \[(.*?)\n\]", CENSUS_TABLE, re.S)
    assert cols, "COLUMNS must stay exported so a test can pin the key"
    entry = re.search(
        r"\{ key: 'status_structure', label: '([^']+)'.*?order: STRUCTURE_SERVED_ORDER",
        cols.group(1), re.S)
    assert entry, "COLUMNS must hold a status column declaring its order"
    label = entry.group(1)
    for word in ("structure", "score", "seam"):
        assert word in label.lower(), f"the status header does not name the {word} axis: {label!r}"


def test_the_status_column_sorts_on_a_category_and_not_on_a_score():
    """⚠⚠ D-079 dec 1: nothing here ranks a census row. The column groups four categories, and
    ``numeric: true`` would compute ``av - bv`` over strings — no order at all, while claiming a
    magnitude. ⚠ And axis B is deliberately NOT a sort key: it is ``false`` on all 3,467 rows, so
    a sort on it would order nothing while implying there was something to order."""
    cols = re.search(r"export const COLUMNS = \[(.*?)\n\]", CENSUS_TABLE, re.S).group(1)
    entry = re.search(r"\{ key: 'status_structure'.*?\},", cols, re.S).group(0)
    assert "numeric: false" in entry
    assert "key: 'scored'" not in cols and "key: 'not_scored" not in cols


def test_the_axis_is_derived_once_onto_the_row():
    """⚠ Derived where the sort can see it, exactly as ``withLens`` does for ``stained_pct``. A
    cell computing its own category while ``compare`` sorted on another would order the table by a
    rule the reader cannot see."""
    assert "export function withStatusAxes" in CENSUS_TABLE
    assert "withStatusAxes(withLens(" in _strip_js_comments(CENSUS_TABLE)


def test_the_topology_column_stops_labelling_a_tiles_row_not_folded():
    """⚠⚠ ``topologyBadgeKey`` read the ``folded === false`` denial first, so a ``tiles_only`` row
    wore **NOT FOLDED** in the column a reader scans. The tiles branch now runs ahead of it."""
    body = _strip_js_comments(CENSUS_TABLE)
    body = body[body.index("export function topologyBadgeKey"):]
    body = body[: body.index("\n}")]
    assert body.index("STRUCTURE_TILES_ONLY") < body.index("folded === false")


def test_the_never_folded_badge_needs_both_the_axis_and_the_recorded_false():
    """⚠⚠ NEITHER CONDITION ALONE IS ENOUGH, and both near-misses are real. The axis alone dresses
    a legacy row that never carried ``folded`` as a denial; ``folded === false`` alone dresses a
    ``tiles_only`` row as one — which is the claim this entry exists to stop. Caught by the vitest
    fixture, not predicted."""
    code = _strip_js_comments(CENSUS_TABLE)
    assert "badge-unfolded" in code, "the never-folded style is no longer applied anywhere"
    # ⚠ Scoped to the status cell. The topology column also carries a `badge-unfolded` span, and it
    # reaches that branch only through `topologyBadgeKey`, whose own tiles guard is pinned above —
    # a file-wide search would find that one and report this rule as satisfied by a different one.
    cell = code[code.index('className="status-cell"'):]
    cell = cell[: cell.index("</td>")]
    guard = re.search(r"([^\n]*badge-unfolded[^\n]*)", cell)
    assert guard, "the status chip no longer carries the never-folded style at all"
    assert "STRUCTURE_NONE" in guard.group(1) and "folded === false" in guard.group(1), guard.group(1)


def test_the_legend_names_the_three_questions_before_the_categories():
    """⚠ The categories without the frame invite the very reading the single badge invited:
    *a structure is served* taken to mean *this protein is done*."""
    assert "STATUS_AXIS_NOTE" in STATUS and "STATUS_AXIS_NOTE" in CENSUS_TABLE
    note = _plain(re.search(r"export const STATUS_AXIS_NOTE =\s*(.*?)\n\n", STATUS, re.S).group(1))
    assert "three separate questions" in note
    for word in ("served", "scored", "seam"):
        assert word in note, f"the axis note does not name the {word} question"


def test_unscored_is_stated_on_every_row_and_never_in_fold_language():
    """⚠⚠ AXIS B IS CONSTANT AND IS PRINTED ANYWAY. ``scored`` is ``false`` for all 3,467 census
    rows (measured 2026-09-09 over ``/api/census?limit=5000``), and a status that only appears
    when something is wrong teaches a reader that silence means fine — after which *no score* has
    to be inferred from *no number*, which reads as a fold that failed."""
    code = _strip_js_comments(STATUS)
    copy = re.search(r"export const NOT_SCORED_COPY = '([^']+)'", code).group(1)
    assert copy == "Not scored, not ranked", copy
    assert not re.search(r"fold|structure", copy, re.I)
    fallback = re.search(r"export const NOT_SCORED_REASON_FALLBACK =\s*'([^']+)'", code)
    assert fallback and "D-079" in fallback.group(1), (
        "a row with not_scored_reason: null renders 'Not scored, not ranked. null' — P55073 is "
        "live in exactly that state")


# ------------------------------------------------------- the protein page


def test_the_never_folded_card_is_gated_on_the_axis_not_on_the_folded_flag():
    """⚠ ``folded === false`` is also true of a ``tiles_only`` parent, so the page shouted NOT
    FOLDED over a payload carrying tile artefacts. ⚠⚠ AND THE CARD IS NOT SOFTENED: an axis-A
    ``none`` row still gets it whole, with all three D-118 reasons."""
    code = _strip_js_comments(CENSUS_PAGE)
    assert "structureA === STRUCTURE_NONE ?" in code, "the card is not gated on axis A"
    assert "<h3>NOT FOLDED</h3>" in code, "the never-folded card lost its heading"


def test_the_viewer_stays_withheld_for_a_tiles_only_parent():
    """⚠ D-118, preserved. A tile window is not the outward-facing region, and drawing one would
    let a 1,656-aa window be read as the ectodomain. The third branch shows neither a dead frame
    nor a misleading structure."""
    code = _strip_js_comments(CENSUS_PAGE)
    assert "structureA === STRUCTURE_TILES_ONLY ?" in code
    branch = code[code.index("structureA === STRUCTURE_TILES_ONLY ?"):]
    branch = branch[: branch.index("<StructureViewer")]
    assert "StructureViewer" not in branch, "the tiles branch draws a viewer"


def test_the_viewer_banner_carries_this_parents_own_seam_note():
    """⚠⚠ THE STANDING ≈ 88.76 Å SENTENCE NAMES IGF2R AND STAYS — it is a cohort-level disclosure.
    What was missing beside it is a line about the protein actually on the page, without which a
    reader of any other assembly is left with one number that was never about their protein."""
    code = _strip_js_comments(VIEWER)
    assert "seamNote" in code, "the viewer takes no per-parent seam note"
    assert "88.76" in code and "IGF2R" in code, "the cohort disclosure was deleted rather than joined"
    assert "provisional" in code, "the assembled banner does not say the artefact is provisional"
    assert "seamNote={seam.note}" in _strip_js_comments(CENSUS_PAGE)


def test_the_confidence_panel_discloses_an_assembled_mean():
    """⚠ The disclosure sits with the NUMBER, not only on the viewer. A reader who scrolls past a
    failed 3Dmol frame meets a confident-looking mean with nothing saying what it is confident
    *of* — for an assembly it is the winner tile's self-report, stitched across an unsolved seam."""
    code = _strip_js_comments(CONFIDENCE)
    assert "assembled-disclosure" in code
    block = code[code.index("assembled-disclosure"):]
    block = block[: block.index("</p>")]
    for phrase in ("not scientifically solved", "provisional"):
        assert phrase in block, f"the assembled disclosure does not say {phrase!r}"


# ------------------------------------------------------- nothing was promoted


def test_no_seam_is_claimed_solved_and_no_parent_is_flipped_here():
    """⚠⚠ THE HARD STOP, ASSERTED. D-139's allowlist is the authority and this entry consults no
    pass count, moves no threshold and flips nothing. ``pass_path_served`` is read off the
    resolver's own ``flipped`` key — and even then the copy refuses the word *solved*."""
    code = _strip_js_comments(STATUS)
    assert "served_path" in code and "flipped === true" in code, (
        "the flip is not read off the D-139 resolver's own answer")
    assert "D126_SERVED_PASS_SUBSET" not in code and "pass_subset_n" not in code, (
        "a pass count is being consulted — D-139: the allowlist is the authority, never a count")
    assert "10.0" not in code, "a gate threshold appears in a display module"
    for const in ("SEAM_PROVISIONAL_COPY", "SEAM_PASS_PATH_COPY"):
        copy = re.search(rf"export const {const} = '([^']+)'", code).group(1)
        assert "not solved" in copy.lower(), f"{const} does not refuse the solved claim: {copy!r}"


def test_the_ui_test_pins_the_fat2_fixture_in_both_directions():
    """⚠⚠ ASSERTING THE NEW WORDING IS THE WEAK HALF. A surface can acquire the honest sentence and
    keep the dishonest one beside it, so the fixture must also prove the OLD reading is
    unavailable."""
    assert UI_TEST.exists(), "the FAT2-shaped vitest fixture is missing"
    text = UI_TEST.read_text(encoding="utf-8")
    assert "Q9NYQ8" in text and "'assembled (provisional)'" in text
    assert "folded: true" in text and "scored: false" in text
    assert "not.toMatch(/NOT FOLDED/)" in text, "nothing pins that the row cannot read as NOT FOLDED"
    assert "not.toMatch(/\\bFolded\\b/)" in text, "nothing pins that the row cannot read as Folded"
    assert "not.toMatch(/88\\.76/)" in text, "nothing pins that IGF2R's figure stays off the card"


# ------------------------------------------------------- the record


def test_the_decision_entry_exists_and_carries_the_witness():
    """⚠⚠ METHOD-NOTE ITEM 7 / THE D-062 DEFECT. A commit message naming a decision is not the
    decision being logged: PR #90 was titled for D-062 and its diff added no ``### D-062``, after
    which thirteen citations treated a missing entry as settled authority. **The check is the
    entry.**"""
    assert re.search(r"^### D-150 — ", LOG, re.M), "there is no ### D-150 entry in the log"
    entry = _plain(_entry())
    assert "q9nyq8" in entry or "fat2" in entry, "the entry does not name its witness"
    for claim in ("assembled (provisional)", "scored: false", "seam not solved"):
        assert claim.lower() in entry, f"the entry does not record {claim!r}"


def test_the_entry_records_the_api_gap_audit():
    """⚠ BUILD step 0. The audit's answer is what licenses axis C being detail-only in v1, so it is
    a finding and belongs in the record — not an assumption the reader has to reconstruct."""
    entry = _plain(_entry())
    assert "assembly_review" in entry
    assert "34" in entry, "the measured list-row key count is not recorded"
    assert "/api/census/" in entry and "/api/census?" in entry, (
        "the entry does not name both payloads it compared")


def test_the_entry_states_what_the_ui_must_not_say():
    """⚠ The forbidden copy is the durable half of this decision. A future surface will be written
    by someone who never met FAT2, and the entry is what tells them."""
    entry = _plain(_entry())
    for phrase in ("never a bare", "not folded"):
        assert phrase in entry, f"the entry does not bar {phrase!r}"


def test_the_architecture_doc_carries_the_new_module():
    """⚠ CLAUDE.md rule 2 — ``ARCHITECTURE.md`` is brought current in the same PR, before it is
    filed."""
    flat = _plain(ARCH)
    assert "d-150" in flat
    assert "structurestatus.js" in flat
    assert "status (structure · score · seam)" in flat


def test_the_next_free_integer_is_named_and_barred_and_148_is_still_a_held_hole():
    """⚠⚠ THE THIRTEENTH PASS THROUGH THIS RESOLUTION. **Bar OR name, never neither.** ``### D-150``
    is claimed by name here; ``### D-148`` is a ``RESERVED.md`` HOLD for the trafficking Spec and
    stays BARRED; ``### D-151`` takes the next-free bar. ⚠ Nothing relaxed to a ``>=``: a ``>=``
    here would pass on a log with no entries at all.

    ⚠ The bars are matched WITH their newline, because this file holds such patterns as *data* in
    order to check the others; a newline-less match would find a "bar" in the file whose job is to
    look for one. That is D-145's recorded mistake, not rediscovered here."""
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 150 in ids, "this entry did not claim its own integer"
    # ⚠⚠ THE 151 BAR BECAME A NAME AT `D-151`, AND THE BAR IS NEITHER DELETED NOR RELAXED. The
    # owner UI-polish ship (Initial Targets label, Kathad DOI anchor, census layout) claimed the
    # integer this entry had barred, so the assertion becomes the stronger statement that 151 is
    # SPENT and named, and the bar moves one integer along to 152. **148 stays barred**: the
    # trafficking hold is unchanged.
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
    assert 154 in ids, "D-154 spent 154 in the live-surface review ship"
    assert 155 in ids, "D-155 spent 155 in the surface-merge ship"
    assert 148 not in ids and 156 not in ids
    assert "\n### D-148" not in LOG, (
        "D-148 is a RESERVED HOLD for the trafficking Spec and must stay unspent until that Spec "
        "claims it by name — never admitted by a `>=`")
    # ⚠⚠ D-154 SPENT the integer this guard barred (the live-surface review ship), so
    # it is NAMED here rather than barred and `### D-156` takes the next-free bar. This is the
    # widening D-145 fixed the shape of: a name is ADDED and nothing becomes a `>=`.
    assert "\n### D-154 — Every UI surface walked on the live site" in LOG, (
        "D-154 was spent by the live-surface review ship, so it must be NAMED here rather "
        "than barred")
    # ⚠⚠ D-155 SPENT the integer this guard barred (the surface-merge ship), so it is NAMED
    # here rather than barred and `### D-156` takes the next-free bar. A name is ADDED and
    # nothing becomes a `>=` — the widening D-145 fixed the shape of.
    assert "\n### D-155 — One population had two tables" in LOG, (
        "D-155 was spent by the surface-merge ship, so it must be NAMED here rather than barred")
    assert "\n### D-156" not in LOG, (
        "D-156 is the next free integer and must stay unspent until an entry claims it by name "
        "— never admitted by a `>=`")


def test_the_reserved_map_bars_151_and_the_pointer_moves_in_this_commit():
    """⚠⚠ MARKER-SAFE, and the reason is mechanical rather than stylistic: this suite locates a row
    with ``re.search(r"^\\| \\*\\*D-1NN\\*\\*", …)``, so striking a marker to ``~~**D-1NN**~~``
    breaks the guard instead of satisfying it. The D-142 / D-145 / D-146 / D-147 rows each record
    the same trap of themselves."""
    assert re.search(r"^\| \*\*D-151\*\*", RESERVED, re.M), (
        "D-151 is cited here, so it must remain a RESERVED row — its row was RETIRED IN PLACE when "
        "the UI-polish ship spent the integer, and deleting or striking it would open a citation "
        "hole indistinguishable from D-062's")
    assert re.search(r"^\| \*\*D-152\*\*", RESERVED, re.M), (
        "D-152 is cited here, so it must remain a RESERVED row — its row was RETIRED IN PLACE when "
        "the surface-navigation ship spent the integer D-153 had held for it, and deleting or "
        "striking it would open a citation hole indistinguishable from D-062's")
    assert re.search(r"^\| \*\*D-148\*\*", RESERVED, re.M), "the trafficking hold lost its row"
    assert not re.search(r"^\| ~~\*\*D-15[012]\*\*~~", RESERVED, re.M), (
        "a marker is struck through; that breaks this suite's lookup instead of satisfying it")
    # ⚠⚠ FLIPPED IN PLACE AT `D-151`, NEVER DELETED. The RULE this encodes is *the pointer moves in
    # the SAME commit that spends the integer*, and the rule is what is kept; only the value moves,
    # and it still skips 148 because a reserved integer is not a free one.
    # ⚠⚠ FLIPPED IN PLACE AGAIN AT `D-153`, AND IT NOW SKIPS **TWO** HOLDS. `D-153` spent 153 (the
    # D-149 burden loader baked into the serving image) and deliberately did NOT take 152: 152 became
    # a HOLD for the concurrent sitewide-layout lane, 148 remains the trafficking hold, so
    # *"next free"* means the lowest AVAILABLE integer, 154.
    assert "Next free `D-` integer: **`D-156`**" in RESERVED, (
        "the next-free pointer moves in the SAME commit that spends the integer")
    assert "Next free `D-` integer: **`D-153`**" not in RESERVED
    assert "Next free `D-` integer: **`D-154`**" not in RESERVED
    assert "Next free `D-` integer: **`D-155`**" not in RESERVED
    assert "Next free `D-` integer: **`D-152`**" not in RESERVED
    assert "Next free `D-` integer: **`D-151`**" not in RESERVED
    assert "Next free `D-` integer: **`D-150`**" not in RESERVED
    assert "Next free `D-` integer: **`D-148`**" not in RESERVED


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ ``RESERVED.md``'s own command, run rather than quoted. **Read the output, not an exit
    code**: the only passing result is that nothing NEW is unresolved. ``D-131`` (the suffix half
    of ``### D-130-B / D-131``) and ``F-067`` (open in #222) are pre-existing and untouched."""
    defined = set(re.findall(r"^### ([DFS]-\d+|DEP-\d+|A-\d+)", LOG, re.M))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    assert sorted(cited - defined - reserved) == ["D-131", "F-067"], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}")
