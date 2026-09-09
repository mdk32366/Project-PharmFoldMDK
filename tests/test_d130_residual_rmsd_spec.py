"""D-130 — Phase 4 residual-RMSD hunt Spec. These must be able to go red.

Spec GO: the living-log heading exists, the Spec file exists, the Phase 4 pin
is quoted verbatim, the primary inventory is **exactly** {3272, 3394}, the
**eight** ``accept-refuse`` parents stay out of it (Phase 5 is not reopened),
the single failure mode is **residual RMSD** and nothing else, the **10.0 Å**
gate stays with every loosening route fenced, the **floor** is written as
**one-directional**, §1b's only permitted refit is **D-125's unchanged** on a
correspondence corrected by **residue identity**, ``recovered_of_two`` = 0 is
**pre-registered**, the sixth tree name collides with none of the five, and
this PR edits no ``hold48_*.py``, no Method file and no UI file.

⚠ **Three failures these pin red.** **Inventory bleed** (T-1193): the hunt
quietly grows a linker half, a domain half, or a third parent — the pin says
*"residual RMSD only — never dual with linker/domain-partition"*, and a
Spec that hunts everything has pre-registered nothing. **Gate erosion**
(T-1194): a `0 of 2` read as a reason the threshold is too strict, which is
the exact move four Specs in a row have forbidden. **The floor read
backwards** (T-1195): treating ``floor ≤ 10.0 Å`` as a promise that a parent
is recoverable, or as evidence the gate is wrong. The bound runs one way,
its constant is not tight, and the arithmetic here proves both rather than
asserting them.
"""
from __future__ import annotations

import hashlib
import itertools
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
SPEC_PATH = ROOT / "docs" / "SPEC-residual-rmsd-hunt.md"
SPEC = SPEC_PATH.read_text(encoding="utf-8")
D129_SPEC_PATH = ROOT / "docs" / "SPEC-phase5-named-refuse.md"
D129_SPEC = D129_SPEC_PATH.read_text(encoding="utf-8")
D128_SPEC = (ROOT / "docs" / "SPEC-linker-seam-honesty.md").read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
TEST_PLAN = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
METHOD_PATH = ROOT / "docs" / "method-hold48-tiles.md"

# The Phase 4 pair the GO named, with the ONLY accessions this log carries
# for them. A sixth id here would be an invention (D-016).
PHASE_4_PAIR = {3272: "Q6V0I7", 3394: "Q8TDW7"}

# Phase 5's fates, listed so a leak into this Spec's inventory is a failure
# rather than a judgement call. Not this Spec's work.
ACCEPT_REFUSE_EIGHT = (2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432)

GATE_ANGSTROM = "10.0"

# The five sibling trees / modules already on disk. A sixth may not reuse a
# name, and this Spec may not edit a module.
PRIOR_TREES = ("kabsch/", "confidence_kabsch/", "piecewise_kabsch/", "linker_seam/")
SIXTH_TREE = "residual_rmsd/"
SIXTH_MODULE = "core/hold48_residual_rmsd.py"

MODULE_PINS = {
    "core/hold48_kabsch.py": "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e",
    "core/hold48_confidence_kabsch.py": "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18",
    "core/hold48_piecewise_kabsch.py": "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04",
    "core/hold48_linker_seam.py": "c270f8711040471a9080a23ab4c1e167a0cc2eedf546c3481cd9ed4f4eb19843",
    "core/hold48_stitch.py": "6e2fcb643e4f5549297182e42def2a54fbb48d2e33659798d7314d56486ef629",
}

# ⚠ A hash alone would let a later PR buy this green by reverting the file.
# Content survival is checked separately (T-1198) — the hash says "unedited
# in THIS PR", the content says "the disclosure is still there".
#
# ⚠ Re-pinned at **D-132** (`4c250063…` → below), the inventory amend, which is
# the decision entry behind the edit. It appends one scope paragraph: the Phase 4
# figures above were measured on the **27**-parent Wave1+Wave2 slice and describe
# only it, while the volume measured **45** assembled parents on 2026-09-08. No
# OPS number is restated, re-scoped, or softened, and the content guards below
# are untouched — the digest moved, the disclosure did not.
# ⚠ Re-pinned at **D-139** (`219409f6…` → below), the served-path flip, which is
# the decision entry behind this edit — exactly what the pin demands. The Method
# file gains an **Addendum D-139** and, on each earlier "served is still the
# assembler" sentence, an in-place scope marker naming D-139 (D-129-C's rule: a
# claim a later decision narrowed never stands alone). ⚠ **Additive and in the
# safe direction:** no OPS figure is restated, re-scoped or softened, no refuse
# class is dropped, and every parent this file's earlier sections are about is
# named as EXCLUDED from the flip. The by-content guards below are untouched —
# the digest moved, the disclosure did not.
METHOD_SHA256 = "e40035aeacdcd68814a9d891a9b50ac6028c39b42190b04e600614a6030cb7a9"


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _plain(text: str) -> str:
    """Flat, lowercased, markdown decoration stripped.

    Phrase checks read the *claim*, not its formatting — otherwise moving a
    ``**`` or wrapping a line inside a ``>`` block silently disarms a pin.
    """
    stripped = re.sub(r"[*`>\"\u201c\u201d]", "", _flat(text))
    return re.sub(r"\s+", " ", stripped).lower()


def _section(number: str, following: str | None) -> str:
    """One numbered section of the D-130 Spec. ``following=None`` = to the end."""
    body = SPEC.split(f"## {number}")[1]
    return body if following is None else body.split(f"## {following}")[0]


def _d130_entry() -> str:
    """Just the D-130 living-log entry.

    Negative checks must be scoped to this entry: the full log is 20k lines
    of history that legitimately quotes phrases this entry forbids, so a
    repo-wide ban would either fail on old prose or be watered down until it
    catches nothing.
    """
    after = LOG.split("### D-130 —", 1)
    assert len(after) == 2, "no ### D-130 entry to scope against"
    return after[1].split("\n### ", 1)[0]


def _absent(banned: tuple[str, ...], text: str, label: str) -> None:
    """Assert none of ``banned`` appears, without a pathological pytest diff."""
    plain = _plain(text)
    present = [phrase for phrase in banned if phrase in plain]
    assert present == [], f"{label} makes a forbidden claim: {present}"


def _sha256(path: Path) -> str:
    # Normalize CRLF->LF so Windows checkouts match the LF pins from Linux CI.
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


BANNED_SOLVED_CLAIMS = (
    "the seams are solved",
    "seams are now solved",
    "we solved the seam",
    "the seam is repaired",
    "the seams are fixed",
    "full-length af-quality structure",
    "the residual is solved",
    "the rmsd class is solved",
)


# ---------------------------------------------------------------- T-1191


def test_d130_heading_exists_in_the_living_log():
    """The check is the entry, not a citation of one (D-062 / method-note 7)."""
    assert re.search(r"^### D-130 — Phase 4 residual-RMSD hunt", LOG, re.M), (
        "D-130 must be a real ### entry, not a citation of one"
    )
    # Every entry this one cites as authority must itself be a real heading.
    for cited in (
        r"^### D-129 — Phase 5 named-refuse",
        r"^### D-129-B —",
        r"^### D-129-C —",
        r"^### D-128 — Linker / seam honesty Spec",
        r"^### D-128-A —",
        r"^### D-127 — Piecewise / domain-aware Kabsch Spec",
        r"^### D-126 — Overlap-confidence Kabsch Spec",
        r"^### D-125 — Kabsch restitch Spec",
    ):
        assert re.search(cited, LOG, re.M), f"cited entry missing: {cited}"
    entry = _plain(_d130_entry())
    assert "docs spec only" in entry
    assert "algorithm authority" in entry
    assert "residual rmsd" in entry


def test_spec_file_exists_and_names_its_authority():
    assert SPEC_PATH.is_file()
    flat = _plain(SPEC)
    assert "phase 4 residual-rmsd hunt" in flat
    assert "algorithm authority" in flat
    assert "go phase 4" in flat
    assert "2026-09-05 ~20:39 pt" in flat
    # It points back at the log, which governs.
    assert "the log governs" in flat
    assert "### D-130" in SPEC, "the Spec must tell a reader to confirm the heading"
    assert "SPEC-residual-rmsd-hunt.md" in INDEX


def test_the_phase_4_go_is_bound_with_provenance():
    """The GO, its route, its date, and the vault id it rules under."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _plain(text)
        assert "emma/matt go phase 4 rmsd" in flat, name
        assert "go phase 4" in flat, name
        assert "d-0043" in flat, name
        # Vault numbering is not repo numbering — the D-114 / D-129 trap.
        assert "external numbering" in flat, name
        assert "d-043" in flat, name
    # D-129 §6 required exactly this, and the Spec says the requirement is met.
    spec_flat = _plain(SPEC)
    assert "explicit matt go" in spec_flat
    assert "d-129 §6" in spec_flat


def test_the_pin_is_quoted_verbatim_and_every_clause_is_placed():
    """§12 carries the source, so clauses can be checked against the artefact."""
    sec = _section("12.", None)
    for clause in (
        "Parents: 3272, 3394",
        "Mode: residual RMSD only — never dual with linker/domain-partition",
        "3272: hard mismatch; not in D-128 OPS seven",
        "3394: D-126 recover gave-back; not hunted in D-128",
        "recover with honesty OR named refuse after failed hunt",
        "served=assembler",
        "no linker-v2",
        "no F-004 / no auto-flip",
        "no kitchen-sink Spec",
        "never solved without measurement",
        "not another RMSD-v2 without new Matt GO",
    ):
        assert clause in sec, f"pin clause missing from the verbatim block: {clause}"
    # And each clause is mapped to the section that binds it.
    assert "Where the pin lands in this Spec" in sec
    assert "```text" in sec, "the source must be a verbatim block, not a paraphrase"


def test_no_vault_prose_is_invented():
    """The vault is not on disk here; say so rather than implying a file."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _plain(text)
        assert "obsidian" in flat, name
        assert "no vault file is on disk" in flat, name
    assert "the log governs" in _plain(LOG)


def test_d130_is_the_next_free_decision_id():
    """D-130 must not collide, and must be the newest id in the log.

    ⚠ Exact, not ``>=``: a stray ``### D-131`` reddens here, and a second
    ``### D-130 —`` entry reddens too.

    ⚠ **Widened at D-130-A — from an empty suffix set to exactly ``{-A}`` —
    rather than loosened.** The Spec PR asserted no ``D-130-*`` entry existed
    because neither A nor B was authorised; the Emma BUILD GO of 2026-09-06
    authorised **A**. **Widened again at D-130-B** — the Matt SIGNED Phase 4
    named-refuse GO (2026-09-05 ~22:32 PT via Emma) authorised **B**, so
    ``### D-130-B`` is *required* and enumerated with ``{-A, -B}``. A second
    ``### D-130-A`` or ``### D-130-B`` fails on the count.

    ⚠ **Widened at D-132 — from "130 is the newest id" to "132 is the only id
    above it" — rather than loosened.** Spending D-132 reddened the ``max``
    form BY DESIGN: the guard did its job. The successor is enumerated, so a
    stray ``### D-131`` still reddens, and D-132 must be the
    inventory-amend entry rather than any entry that took the number.

    ⚠ **Widened again at D-133 — from ``[132]`` to ``[132, 133]`` — and again
    by enumeration, not by a ``>=``.** Spending D-133 reddened the previous
    form BY DESIGN, which is the guard working rather than a false alarm.
    D-133 is the census sortable-Structure-column entry, named here so an
    entry that merely *takes* the number still fails, and a stray
    ``### D-134`` fails too.

    ⚠ **Widened again at D-134 — to ``[132, 133, 134]`` — the same way.** D-134
    is the stitched-parent census-identity fix; it is named below.

    ⚠ **Widened again at D-135 — to ``[132, 133, 134, 135]`` — and again by
    enumeration rather than by a ``>=``.** Spending D-135 reddened the previous
    form BY DESIGN: that is the collision guard working, not a false alarm.
    D-135 is the Coverage dual-population / Story-consumability entry, named
    below so an entry that merely *takes* the number still fails, and a stray
    ``### D-136`` fails too.

    ⚠ **Widened again at D-136 — to ``[132, 133, 134, 135, 136]`` — the same
    way.** D-136 fills the ADC Approved Cancer type column from the FDA label;
    it is named below. ⚠ **This is the two-branch collision the guard exists
    for, and it resolved by ADDING rather than loosening:** D-135 and D-136 were
    in flight together, each widened this list to exclude the other, and the
    merge carries **both** ids and **both** named-entry assertions instead of
    relaxing either to a ``>=``.

    ⚠ **Widened again at D-137 — to ``[132, 133, 134, 135, 136, 137]``** — the
    third live two-branch collision in a row. D-137 (the census sortable
    **Cost** column) was written while #260 (D-136) was still open, so it landed
    as ``[…, 135, 137]`` with 136 named as the in-flight id it was deliberately
    not taking (F-065's class, avoided by reading the open-PR list rather than
    assuming). #260 then merged, this assertion reddened **exactly as its own
    comment predicted**, and the rebase inserted 136 beside 137. **The redness
    was the guard working**; both ids are carried, neither claim is weakened, and
    a stray ``### D-138`` still fails rather than slipping under a ``>=``.

    ⚠ **Widened again at D-138 — to ``[132, 133, 134, 135, 136, 137, 138]``** —
    the FOURTH live collision in a row, same resolution. D-138 (the ``/method``
    contents rail, #262) was opened at tip ``1b0251b`` while #261 (D-137) was
    still open, so it landed as ``[…, 136, 138]`` with **137 named as the
    in-flight id it was deliberately not taking**, read off ``gh pr list
    --state open`` rather than assumed. #261 then squash-merged at ``68fe0228``,
    this assertion reddened **exactly as both branches' comments predicted**, and
    the merge inserted 137 beside 138.     ⚠ **Four collisions, four resolutions by
    ADDING.** A ``>=`` would make each of them go away and would also end the
    guard's ability to tell a spent id from a free one, which is the only thing
    it does. A stray ``### D-139`` still fails.

    ⚠ **Widened again at D-139 — to ``[132, …, 138, 139]``** — the fifth pass,
    same resolution. D-139 flips the served PDB to D-126 for the recorded PASS
    seventeen. ⚠ It read ``gh pr list --state open`` at tip ``dd06e9c``, got #222,
    #200 and #197, none of which spends a ``D-1NN`` id, and concluded 139 was free.

    ⚠⚠ **Widened again at D-140 — to ``[132, …, 139, 140]`` — and the conclusion
    above turned out to be wrong, which is the finding.** The ADC Pipeline
    programme-fields branch (#263) was cut from the same ``dd06e9c``, ran the same
    open-PR check, reached the same answer, and took the same 139: **two entries
    titled ``### D-139``**, invisible to each other because #263 was not yet an
    open PR when the other branch looked. The served-path work merged first
    (``1e9777c``) and named the resolution in its own commit message — *"Pipeline
    #263 takes D-140."* — so 139 stays with the entry that merged holding it and
    #263 renumbered. ⚠ **An open-PR check proves no PUBLISHED branch spent the id;
    it cannot prove no unpublished one did.** This enumeration is what caught it.
    Both ids are named below and ``### D-141`` is barred by name.

    ⚠ **Widened again at D-141 — to ``[132, …, 139, 140, 141]``** — the sixth
    pass, and the collision above resolving cleanly one branch later. D-141 lands
    the D-126 OPS trees on the serving volume so D-139's gate has bytes to answer
    with. It was cut from ``1e9777c``, ran the open-PR check **after** #263 was
    published, saw 140 held, and took 141 — the D-138 precedent, applied with the
    benefit of exactly the lesson the paragraph above records. #263 then merged at
    ``578f5ac``, this assertion reddened **as that branch's own comment predicted**,
    and the rebase inserted 140 beside 141. **All three ids are named below** and
    ``### D-144`` is barred. ⚠ Six widenings, six resolutions by ADDING; a ``>=``
    would have concealed every collision above instead of catching it.

    ⚠ **Widened again at D-143 — to ``[132, …, 140, 141, 143]``, with 142 deliberately
    ABSENT** — the seventh pass. The Track B copy branch was cut from ``30f402f``,
    ``grep``ed the log for the highest written entry (141), read
    ``gh pr list --state open`` (#222 / #200 / #197, none spending a ``D-1NN``) and took
    **142**; the owner then ruled the id to **143** (2026-09-09) and the PR was
    renumbered, with nothing visible in the tree spending 142. ⚠ The open-PR weakness
    above still stands and gains a second face: it cannot see an unpublished branch, and
    it cannot see an authority holding an integer either. 142 is registered in
    ``docs/RESERVED.md`` and stays BARRED below; ``### D-144`` takes the next-free bar.
    """
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 130 in ids
    #
    # ⚠ Widened again at **D-147** — to `[…, 145, 146, 147]` — by enumeration, for the EIGHTH
    # time, and by ADDING as every pass before it. ⚠⚠ **The FOURTH reserved integer to be SPENT
    # rather than skipped** (142, 145 and 146 were the first three, all 2026-09-09): 147 sat in
    # `docs/RESERVED.md` as the next free `D-`, `D-146` cited it in order to bar it, and this
    # enumeration reddened **by design** the moment an entry claimed it. D-147 adds the
    # `ecd_intermittent` disclosure to the census structural ranking rows and touches nothing this
    # suite measures. A bare `### D-148` still reddens.
    # ⚠⚠ Widened again at **D-151** — to `[…, 149, 150, 151]` — by enumeration, for the
    # ELEVENTH time, and never by a `>=`. Spending 151 reddened the previous form BY DESIGN; that
    # is the collision guard working, and it is the only reason this file had to be opened by an
    # entry about a menu label, a DOI anchor and a census layout. ⚠⚠ **The FIFTH reserved integer
    # to be SPENT rather than skipped** (142, 145, 146 and 147 were the first four): 151 sat in
    # `docs/RESERVED.md` as the next free `D-`, `D-150` cited it in order to bar it, and this
    # enumeration went red the moment an entry claimed it. **148 stays absent** — the trafficking
    # hold is unchanged, so a bare `### D-148` is still a real collision and still reddens here.
    # ⚠⚠ Widened again at **D-150** — to `[…, 147, 149, 150]` — by enumeration, for the
    # TENTH time, and never by a `>=`. Spending 150 reddened the previous form BY DESIGN; that is
    # the collision guard working, and it is the only reason this file had to be opened by an
    # entry about census status chips. **148 stays absent** — the trafficking hold is unchanged,
    # so a bare `### D-148` is still a real collision and still reddens here.
    # ⚠⚠ Widened again at **D-149** — to `[…, 146, 147, 149]` — by enumeration, for the NINTH
    # time, and never by a `>=`. Spending 149 reddened the previous form BY DESIGN; that is the
    # collision guard working.
    # ⚠⚠ **148 IS DELIBERATELY ABSENT FROM THIS LIST AND MUST STAY ABSENT — and it is the FIRST
    # hole here that is a DECISION rather than a suffix or a collision.** `docs/RESERVED.md` holds
    # 148 for the trafficking Spec (owner instruction, 2026-09-09), so `D-149` skipped it. A bare
    # `### D-148` is therefore still a real collision and still reddens here, exactly as a bare
    # `### D-131` does for the other kind of hole. **The two holes have different causes and the
    # list distinguishes them in prose, because an unexplained gap in an enumerated set reads as an
    # oversight to the next reader.**
    assert [i for i in ids if i > 130] == [
        132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 149,
        150, 151
    ], (
        f"D-130's successors must be exactly D-132, D-133, D-134, D-135, D-136, "
        f"D-137, D-138, D-139, D-140, D-141, D-142, D-143, D-144, D-145, D-146 and D-147 — "
        f"⚠ 142 is no longer absent: docs/RESERVED.md reserved it and the /targets columns "
        f"entry is the holder that wrote it, so it is ADDED here beside 143; ⚠ 145 was "
        f"reserved the same way and is ADDED beside 144 by the image-permanence entry; "
        f"⚠ 146 the same way again, ADDED by the Track B live-route copy entry; ⚠ 147 the "
        f"same way once more, ADDED by the census `ecd_intermittent` entry; ⚠ 150 by the "
        f"census structure-status honesty entry; ⚠ 151 by the owner UI-polish entry "
        f"(Initial Targets label, Kathad DOI anchor, census layout); "
        f"found {ids[-15:]}"
    )
    assert re.search(r"^### D-139 — The served PDB stops being a constant", LOG, re.M), (
        "D-139 must be the served-path flip entry, not some other entry that "
        "took the number"
    )
    assert re.search(r"^### D-140 — The ADC Pipeline shelf gets a cancer type", LOG, re.M), (
        "D-140 must be the ADC pipeline programme-fields entry, not some other entry "
        "that took the number"
    )
    assert re.search(r"^### D-141 — The gate had nothing to answer with", LOG, re.M), (
        "D-141 must be the confidence-Kabsch lander entry, not some other entry "
        "that took the number"
    )
    assert re.search(r"^### D-143 — Track B stops claiming a composite", LOG, re.M), (
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
    assert re.search(r"^### D-142 — `/targets` gains a Cancer association", LOG, re.M), (
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
                     LOG, re.M), (
        "D-144 must be the census structural-rank entry, not some other entry that took "
        "the number"
    )
    # ⚠ Widened again at **D-145** — to `[…, 142, 143, 144, 145]` — for the TENTH time, and by
    # ADDING as every pass before it. ⚠⚠ **The SECOND reserved integer to be SPENT rather than
    # skipped** (142 was the first, the same day): 145 sat in `docs/RESERVED.md` as the next free
    # `D-`, `D-144` cited it in order to bar it, and this bar reddened **by design** when an entry
    # claimed it. D-145 bakes the D-144 structural-rank loader into the Fly serving image as one
    # explicit `COPY` — image permanence, no formula, no route, no schema, no threshold — so it
    # touches nothing this suite measures and is named only because this is an enumerated id
    # check. `### D-146` now takes the next-free bar; no bar was deleted, each became a name.
    assert re.search(r"^### D-145 — The D-144 loader stops living on the production host",
                     LOG, re.M), (
        "D-145 must be the image-permanence entry that bakes the structural-rank loader in, "
        "not some other entry that took the number"
    )
    # ⚠ Widened again at **D-146** — to `[…, 143, 144, 145, 146]` — for the ELEVENTH time, and by
    # ADDING as every pass before it. ⚠⚠ **The THIRD reserved integer to be SPENT rather than
    # skipped** (142 and 145 were the first two, both the same day): 146 sat in
    # `docs/RESERVED.md` as the next free `D-`, `D-145` cited it in order to bar it, and this bar
    # reddened **by design** when an entry claimed it. D-146 retires Track B's offline clause —
    # the copy denied being a ranked surface in this application while
    # `GET /api/census-structural-ranking` answers `valid` — so it is copy only, with no route,
    # no formula, no schema and no threshold, and is named only because this is an enumerated id
    # check. `### D-147` now takes the next-free bar; no bar was deleted, each became a name.
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     LOG, re.M), (
        "D-146 must be the Track B live-route copy entry, not some other entry that took "
        "the number"
    )
    # ⚠ Widened again at **D-147** by ADDING, never by a `>=` — the TWELFTH pass. ⚠⚠ **The FOURTH
    # reserved integer to be SPENT rather than skipped** (142, 145 and 146 were the first three,
    # all the same day): 147 sat in `docs/RESERVED.md` as the next free `D-`, `D-146` cited it in
    # order to bar it, and this bar reddened **by design** the moment an entry claimed it.
    # D-147 adds the `ecd_intermittent` disclosure to the census structural ranking rows —
    # a served category, no score and no formula — and is named only because this is an
    # enumerated id check. **No RMSD, no gate and no residual moves.**
    # `### D-148` now takes the next-free bar; nothing was relaxed to a `>=` and no bar was
    # deleted, only replaced by a name.
    assert re.search(r"^### D-147 — The census rank stops presenting a loop as an ectodomain",
                     LOG, re.M), (
        "D-147 must be the census `ecd_intermittent` entry, not some other entry that took "
        "the number"
    )
    assert "\n### D-148" not in LOG, (
        "D-148 is the next free integer and must stay unspent until an entry claims it "
        "by name here — never admitted by a `>=`"
    )
    assert re.search(r"^### D-138 — `/method` gets a contents rail", LOG, re.M), (
        "D-138 must be the /method contents-rail entry, not some other entry that "
        "took the number"
    )
    assert re.search(r"^### D-136 — The ADC Approved Cancer type column", LOG, re.M), (
        "D-136 must be the ADC cancer-type entry, not some other entry that "
        "took the number"
    )
    assert re.search(r"^### D-137 — The census gains a sortable Cost column", LOG, re.M), (
        "D-137 must be the census sortable-Cost-column entry, not some other entry "
        "that took the number"
    )
    assert re.search(r"^### D-134 — Stitched parents were invisible", LOG, re.M), (
        "D-134 must be the stitched-parent census-identity entry, not some "
        "other entry that took the number"
    )
    assert re.search(r"^### D-135 — Coverage gains a SECOND population", LOG, re.M), (
        "D-135 must be the Coverage dual-population / Story entry, not some "
        "other entry that took the number"
    )
    assert re.search(r"^### D-132 — Assemble-inventory amend", LOG, re.M), (
        "D-132 must be the inventory-amend entry, not some other entry that "
        "took the number"
    )
    assert re.search(r"^### D-133 — Census gains a sortable Structure column", LOG, re.M), (
        "D-133 must be the census sortable-Structure-column entry, not some "
        "other entry that took the number"
    )
    assert len(re.findall(r"^### D-130 —", LOG, re.M)) == 1, "exactly one D-130 entry"
    assert len(re.findall(r"^### D-130-A —", LOG, re.M)) == 1, "exactly one D-130-A entry"
    assert len(re.findall(r"^### D-130-B", LOG, re.M)) == 1, "exactly one D-130-B entry"
    suffixes = sorted(set(re.findall(r"^### D-130(-[A-Z])? ", LOG, re.M)))
    assert suffixes == ["", "-A", "-B"], f"unexpected D-130 suffix entries: {suffixes}"
    assert len(re.findall(r"^### D-130", LOG, re.M)) == 3, "Spec + A + B"
    # The pointer is the owner's; this entry spends an id, it does not repair one.
    assert "next-free pointer" in _plain(_d130_entry())


# ---------------------------------------------------------------- T-1192


def test_the_primary_inventory_is_exactly_the_phase_4_pair():
    """Two parents. A third id in the §3 inventory table is a failure."""
    sec = _section("3.", "4.")
    rows = re.findall(r"^\|\s*\*\*(\d{4})\*\*\s*\|", sec, re.M)
    assert sorted(int(r) for r in rows) == sorted(PHASE_4_PAIR), (
        f"§3's inventory table must hold exactly 3272 and 3394; found {rows}"
    )
    for pid, acc in PHASE_4_PAIR.items():
        row = re.search(rf"^\|\s*\*\*{pid}\*\*\s*\|.*$", sec, re.M)
        assert row, f"{pid} has no §3 inventory row"
        assert acc in row.group(0), f"{pid}'s row does not carry {acc}"
        assert "rmsd_gt_10" in row.group(0), f"{pid}'s row does not name its refuse"
        assert str(pid) in LOG, pid
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "3272" in flat and "3394" in flat, name
        assert "phase 4 must-hunt" in flat, name


def test_the_accept_refuse_eight_are_out_and_phase_5_is_not_reopened():
    """Phase 5's fates are not this Spec's inventory, and are not re-hunted."""
    sec = _section("3.", "4.")
    inventory_rows = re.findall(r"^\|\s*\*\*(\d{4})\*\*\s*\|", sec, re.M)
    for pid in ACCEPT_REFUSE_EIGHT:
        assert str(pid) not in inventory_rows, f"{pid} leaked into the §3 inventory"
    assert not set(PHASE_4_PAIR) & set(ACCEPT_REFUSE_EIGHT), "the fate sets are disjoint"
    # Named as OUT, with their fate, in the out-of-inventory table.
    out_block = sec.split("Explicitly out of the primary inventory")[1]
    for pid in ACCEPT_REFUSE_EIGHT:
        assert str(pid) in out_block, f"{pid} is not named as out of this Spec"
    assert "accept-refuse" in _plain(out_block)
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "phase 5 is not reopened" in flat, name
        assert "accept-refuse" in flat, name
    spec_flat = _plain(SPEC)
    assert "3432 stays accept-refuse" in spec_flat or "3432 stays" in spec_flat
    assert "not re-hunted" in spec_flat
    assert "not a d-130 miss" in spec_flat


def test_no_invented_accessions():
    """Only the two on record are named, and no third is written from memory."""
    sec = _section("3.", "4.")
    # Every UniProt-shaped token in §3 must be one the log already carries.
    known = set(PHASE_4_PAIR.values()) | {"Q7Z408", "Q5SZK8", "Q8IZF6"}
    found = set(re.findall(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b", sec))
    assert found <= known, f"§3 names an accession this log does not carry: {found - known}"
    for acc in PHASE_4_PAIR.values():
        assert acc in LOG, acc
    assert "nobody writes an accession from memory" in _plain(SPEC)


def test_recorded_history_is_marked_as_read_not_re_measured():
    """D-016: the §3 histories are reads of the record, not fresh findings."""
    sec_flat = _plain(_section("3.", "4."))
    assert "not re-measured" in sec_flat
    assert "checking that two records agree is not a measurement" in sec_flat
    # The two histories the GO named, each attributable.
    assert "hard mismatch" in sec_flat
    assert "not in the d-128 ops seven" in sec_flat
    assert "give-back" in sec_flat
    assert "2 of 5" in sec_flat or "2 of the 5" in sec_flat
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        assert "as recorded" in _plain(text), name


# ---------------------------------------------------------------- T-1193


def test_the_failure_mode_is_singular_and_named():
    """One class: residual RMSD. The pin's own words, bound."""
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "single failure mode" in flat or "one failure mode" in flat, name
        assert "residual rmsd" in flat, name
        assert "whole-overlap" in flat or "whole overlap" in flat, name
    spec_flat = _plain(SPEC)
    assert "rmsd_gt_10" in SPEC
    assert "never dual with linker/domain-partition" in spec_flat


def test_inventory_and_mode_bleed_are_written_as_forbidden():
    """⚠ The failure this file exists to redden: the hunt grows a second half.

    A Spec that hunts the linker class *and* the domain class *and* the
    residual class has pre-registered nothing — whichever half passes gets
    reported. The pin forbids it by name, so the fence is checked by name.
    """
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _plain(text)
        assert "not a linker" in flat, name
        assert "not a domain-partition spec" in flat, name
        assert "not both" in flat, name
        assert "kitchen sink" in flat or "kitchen-sink" in flat, name
    spec_flat = _plain(SPEC)
    assert "no dual-mode spec" in spec_flat
    # The frozen families, refused by their own names.
    for banned in ("linker-v2", "piecewise-v2", "rmsd-v2"):
        assert f"no {banned}" in spec_flat, banned
    # And the fit units that belong to the earlier Specs.
    hard = _plain(_section("9.", "10."))
    for unit in (
        "no pieces",
        "no window",
        "no linker-inherit",
        "domain intervals as the fit unit",
    ):
        assert unit in hard, unit


def test_a_third_parent_cannot_be_added_by_the_cli_run():
    """Running the 27 for confusion is allowed; treating them as targets is not."""
    sec_flat = _plain(_section("3.", "4."))
    assert "cli may also re-run all 27" in sec_flat
    assert "not success targets" in sec_flat
    assert "not a phase 4 recovery" in sec_flat


def test_spec_never_says_solved():
    _absent(BANNED_SOLVED_CLAIMS, SPEC, "the D-130 Spec")
    _absent(BANNED_SOLVED_CLAIMS, _d130_entry(), "the D-130 log entry")
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "never solved without measurement" in flat, name
    assert "this spec never says solved" in _plain(SPEC)


# ---------------------------------------------------------------- T-1194


def test_the_gate_stays_at_ten_and_every_loosening_route_is_fenced():
    """10.0 A stays. A `0 of 2` licenses none of it."""
    assert GATE_ANGSTROM in SPEC
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "10.0 å stays" in flat, name
    spec_flat = _plain(SPEC)
    for fence in (
        "no gate loosen",
        "no per-parent exception",
        "named-exclusion",
        "no threshold spec-as-fix",
        "not a threshold change",
    ):
        assert fence in spec_flat, fence
    assert "0 of 2 does not license one" in spec_flat
    # The gate is D-128's, unchanged — this Spec introduces no second number.
    assert "10.0 å" in _plain(_section("2.", "3."))


def test_trim_is_forbidden_and_the_d126_lie_surface_is_named():
    """⚠ Trim-as-fix is only refusable if the risk is named — so it is named.

    D-126's trimmed / weighted score ran small while the full overlap ran
    28-68 A, and 3272 — one of this Spec's two parents — is on that list.
    A Spec that forbade trim without saying why would be a preference; this
    one cites the artefact.
    """
    hard = _plain(_section("9.", "10."))
    assert "no trim" in hard
    assert "trim-as-fix" in hard
    assert "d-126 lie surface" in hard
    assert "28–68 å" in hard or "28-68 å" in hard
    assert "3272" in hard, "the lie surface must be named on a parent of THIS Spec"
    # Subset selection is trim under any other name.
    assert "any subset selection that improves a number is trim" in hard
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        assert "no trim" in _plain(text), name


def test_the_only_permitted_fit_is_d125s_unchanged():
    """No new geometry: unweighted, untrimmed, full overlap, whole tile."""
    sec = _plain(_section("1b.", "2."))
    assert "exactly d-125's fit, unchanged" in sec
    assert "unweighted" in sec
    assert "untrimmed" in sec
    assert "full corrected overlap" in sec
    assert "no weights" in sec
    assert "no trim loop" in sec
    assert "no pieces" in sec
    assert "no window" in sec
    assert "no linker-inherit" in sec
    # And it feeds the EXISTING assembler, replacing nothing.
    assert "winning_tile" in _section("1b.", "2.")
    assert "no new geometry" in _plain(SPEC)


# ---------------------------------------------------------------- T-1195


def test_the_floor_is_written_as_one_directional():
    """⚠ The failure: `floor <= 10 A` read as a promise, or as gate criticism."""
    sec = _plain(_section("1a.", "1b."))
    assert "one-directional" in sec
    assert "proves nothing" in sec
    assert "sufficient and never necessary" in sec
    # The four backwards readings, each named as forbidden.
    for wrong in (
        "means this parent can be fixed",
        "the 10.0 å gate is too strict here",
        "recovery forecast",
    ):
        assert wrong in sec, wrong
    assert "spec violation" in sec
    hard = _plain(_section("9.", "10."))
    assert "reading it backwards is a spec violation" in hard
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (ARCH, "arch"), (INDEX, "index")):
        assert "one-directional" in _plain(text), name


def test_the_floor_is_labelled_mathematics_and_not_a_measurement():
    """D-016: an inequality is proved; no parent's floor is computed here."""
    sec = _plain(_section("1a.", "1b."))
    assert "proof" in sec
    assert "mathematics, not a measurement" in sec
    assert "no parent's floor is computed, asserted, or estimated" in sec
    assert "not a measurement" in _plain(_section("10.", "11."))
    assert "proved mathematics" in _plain(SPEC)
    # The three-valued class, with unknown belonging to neither bucket.
    for value in ("irreducible", "placement", "unknown"):
        assert value in sec, value
    assert "unknown is not irreducible" in sec or "unknown is neither" in sec


def test_the_claimed_inequality_actually_holds_and_is_not_tight():
    """The Spec's load-bearing claim, checked as arithmetic rather than prose.

    ⚠ A Spec that asserts a bound the code cannot reproduce is exactly the
    pointer-is-not-proof failure this project keeps re-learning. So the
    inequality ``RMSD(R, t) >= dRMSD / 2`` is exercised here on constructed
    point sets under real rigid transforms — including transforms far from
    optimal, since the claim is about *every* rigid motion, not the best one.

    The second half matters just as much: the bound is **not tight**, which
    is precisely why ``irreducible`` is *sufficient and never necessary*.
    A future edit that promoted the floor to "the answer" would have to get
    past this.
    """

    # ⚠ The divisor exercised below is the one the Spec states. Without this,
    # a Spec that quietly changed the constant would be asserting a bound
    # nothing checks — the pointer-is-not-proof shape again.
    assert "internal_drmsd_angstrom / 2" in SPEC
    assert r"\mathrm{dRMSD}/2" in SPEC

    def drmsd(p, q):
        pairs = list(itertools.combinations(range(len(p)), 2))
        total = sum(
            (_dist(p[i], p[j]) - _dist(q[i], q[j])) ** 2 for i, j in pairs
        )
        return math.sqrt(total / len(pairs))

    def rmsd(p, q):
        return math.sqrt(sum(_dist(a, b) ** 2 for a, b in zip(p, q)) / len(p))

    def rotate_z(points, radians):
        c, s = math.cos(radians), math.sin(radians)
        return [(c * x - s * y, s * x + c * y, z) for x, y, z in points]

    def translate(points, shift):
        return [(x + shift[0], y + shift[1], z + shift[2]) for x, y, z in points]

    # A deterministic, non-degenerate reference set and a genuinely
    # differently-shaped partner (not a rigid image of it).
    reference = [
        (0.0, 0.0, 0.0),
        (3.8, 0.0, 0.0),
        (7.1, 1.9, 0.0),
        (9.6, 4.8, 1.2),
        (10.4, 8.6, 3.1),
        (8.2, 11.9, 2.4),
    ]
    deformed = [
        (0.0, 0.0, 0.0),
        (3.8, 0.0, 0.0),
        (6.9, 2.2, 0.4),
        (7.4, 6.0, 2.9),
        (4.8, 9.1, 4.6),
        (0.9, 9.9, 3.3),
    ]

    floor = drmsd(reference, deformed) / 2.0
    assert floor > 0, "the fixture must actually disagree about internal shape"

    for radians in (0.0, 0.4, 1.1, 2.7, 5.9):
        for shift in ((0.0, 0.0, 0.0), (2.5, -1.0, 0.7), (-40.0, 12.0, 3.0)):
            moved = translate(rotate_z(reference, radians), shift)
            assert rmsd(moved, deformed) >= floor - 1e-9, (
                "RMSD >= dRMSD / 2 must hold for EVERY rigid transform; it "
                f"failed at radians={radians}, shift={shift}"
            )

    # dRMSD is rigid-invariant: moving one copy must not move the floor.
    spun = translate(rotate_z(reference, 1.9), (11.0, -4.0, 2.0))
    assert abs(drmsd(spun, deformed) / 2.0 - floor) < 1e-9, (
        "the floor must be invariant under rigid motion of either copy"
    )

    # Identical shapes have a zero floor and can be fitted perfectly — so a
    # small floor really does say nothing about the achieved RMSD.
    far = translate(rotate_z(reference, 2.2), (95.0, -60.0, 40.0))
    assert drmsd(far, reference) / 2.0 < 1e-9
    assert rmsd(far, reference) > 50.0, (
        "a zero floor coexists with an enormous achieved RMSD — the bound is "
        "not tight, which is why `irreducible` is sufficient and never necessary"
    )


# ---------------------------------------------------------------- T-1196


def test_the_correspondence_audit_is_decided_by_identity_never_by_score():
    """The one recovery route, and the search it is not."""
    sec = _plain(_section("1b.", "2."))
    assert "residue identity" in sec
    assert "never by rmsd" in sec or "never chosen by score" in sec
    assert "unique and identity-determined" in sec or "must be unique" in sec
    # Ambiguity refuses instead of picking a winner.
    assert "ambiguous" in sec
    assert "do not choose among candidate offsets by rmsd" in sec
    assert "do not scan a window of offsets and keep the best" in sec
    # Re-pairing is not subset selection.
    assert "it is not a subset chosen for fit quality" in sec
    assert "correspondence_unverifiable" in _section("1b.", "2.")


def test_the_audit_is_gated_on_the_required_half():
    """§1b runs only where §1a said `placement`; auditing anyway is a search."""
    sec = _plain(_section("1b.", "2."))
    assert "runs only where" in sec
    assert "placement" in sec
    assert "rmsd_irreducible" in sec
    assert "running the audit anyway to see what happens is a search" in sec


def test_required_half_records_every_path_and_names_how_it_is_known():
    """§1a is per (path, seam), across all five trees, with sources."""
    sec = _section("1a.", "1b.")
    for path in ("kabsch", "confidence_kabsch", "piecewise_kabsch", "linker_seam", "residual_rmsd"):
        assert path in sec, path
    for field in (
        "n_overlap_ca",
        "rigid_rmsd_angstrom",
        "internal_drmsd_angstrom",
        "rmsd_floor_angstrom",
        "residual_class",
        "floor_exceeds_gate",
    ):
        assert field in sec, field
    flat = _plain(sec)
    assert "no trim, no subset, no window" in flat
    assert "null is not 0.0" in flat
    assert "honest absence with a stated reason" in flat
    assert "must not rewrite, append to, or overwrite" in flat
    assert "how it is known" in flat
    # The deliverable is the measurement, not a pass count.
    assert "recovers zero parents has run this spec" in flat


# ---------------------------------------------------------------- T-1197


def test_the_new_refuse_names_are_new_and_are_not_conflated():
    """A reason name from another algorithm is a different measurement."""
    sec = _section("2.", "3.")
    for reason in (
        "overlap_ca_lt_3",
        "rmsd_irreducible",
        "correspondence_unverifiable",
        "rmsd_gt_10",
        "singular_covariance",
    ):
        assert reason in sec, reason
    flat = _plain(sec)
    assert "new reason names, not renames" in flat
    assert "linker_jump_gt_10" in sec, "D-127's name must be named as NOT this one"
    assert "seam_jump_gt_10" in sec, "D-128's name must be named as NOT this one"
    assert "must never be conflated" in flat
    assert "carried unchanged" in flat
    # Fail-closed, all-or-nothing, rows still written.
    assert "fail closed" in flat
    assert "all-or-nothing parent" in flat
    assert "a refuse is a recorded outcome" in flat


def test_zero_of_two_is_pre_registered_and_a_named_refuse_completes_the_spec():
    """Both allowed outcomes, written before any run — not discovered after."""
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "recovered_of_two" in flat, name
        assert "pre-registered" in flat, name
        assert "allowed outcome" in flat, name
    spec_flat = _plain(SPEC)
    assert "named refuse after a failed hunt" in spec_flat
    assert "complete outcome" in spec_flat or "complete completion" in spec_flat
    assert "before any run" in spec_flat
    # The escalation route the pin closes.
    assert "accept-refuse or a dual-path disclose" in spec_flat
    assert "not another rmsd-v2 without a new matt go" in spec_flat


def test_the_ops_report_fields_are_required_and_name_the_embarrassing_one():
    """§11 is a required report field set, not a CI assert."""
    sec = _section("11.", "12.")
    for field in (
        "n_overlap_pairs_measured",
        "n_irreducible",
        "n_placement",
        "n_residual_unknown",
        "n_correspondence_audited",
        "n_correspondence_corrected",
        "n_correspondence_unverifiable",
        "recovered_of_two",
        "n_d125_pass_d130_refuse",
        "n_d126_pass_d130_refuse",
        "n_d127_pass_d130_refuse",
        "n_d128_pass_d130_refuse",
        "n_d126_recovered_d130_refuse",
    ):
        assert field in sec, field
    flat = _plain(sec)
    assert "not a ci assert" in flat
    assert "do not bury a drop inside an overall accept count" in flat
    # The count most likely to embarrass the run is named as such (D-016:
    # prefer the query whose answer could disqualify you).
    assert "most likely to embarrass the run" in flat
    assert "n_placement" in sec and "not a recovery forecast" in flat
    assert "which figures were measured by that run" in flat


# ---------------------------------------------------------------- T-1198


def test_the_sixth_tree_and_module_names_collide_with_nothing():
    """A sixth path may not overwrite a fifth."""
    sec = _section("5.", "6.")
    assert SIXTH_TREE in sec
    assert SIXTH_MODULE in sec
    for tree in PRIOR_TREES:
        assert tree in sec, f"{tree} must be named as NOT overwritten"
    assert SIXTH_TREE.rstrip("/") not in {t.rstrip("/") for t in PRIOR_TREES}
    flat = _plain(sec)
    assert "sixth sibling tree" in flat
    assert "do not overwrite" in flat
    assert "collide with none" in flat
    assert "may not reuse an earlier name" in flat
    assert "residual_rmsd_decomposition_then_winning_tile" in sec
    assert "decision" in flat and "d-130" in flat


def test_this_spec_pr_edits_no_module_no_method_and_no_ui():
    """Docs only. Five modules pinned; the Method file pinned; no ui/ path.

    ⚠ Strengthened at D-130-A rather than relaxed: the sixth module now has to
    **exist**, carry this Spec's algorithm string, and contain none of the
    frozen family's knobs — so "A shipped" cannot be claimed by a file that
    quietly re-imports a window, a weight, or a trim loop. The five digests
    below are untouched.
    """
    sixth = ROOT / SIXTH_MODULE
    assert sixth.is_file(), "D-130-A's sixth sibling module must be on disk"
    sib = sixth.read_text(encoding="utf-8")
    assert "residual_rmsd_decomposition_then_winning_tile" in sib
    assert "def write_residual_rmsd_restitch" in sib
    assert "rmsd_irreducible" in sib and "correspondence_unverifiable" in sib
    assert "import numpy" not in sib and "from numpy" not in sib
    assert "trim_highest_residual" not in sib  # not D-126
    assert "DomainInterval" not in sib  # not D-127
    assert "WINDOW_HALF_WIDTH_AA =" not in sib  # not D-128
    assert "def winning_tile" not in sib, "the assembler is imported, not re-implemented"

    for name, expected in MODULE_PINS.items():
        path = ROOT / name
        assert path.is_file(), name
        assert _sha256(path) == expected, (
            f"{name} was edited — D-130 is a docs Spec PR and may not touch "
            "geometry, a threshold, or a served byte"
        )
        assert "D-130" not in path.read_text(encoding="utf-8"), (
            f"{name} names D-130 — the Spec must not have become a code change"
        )
    assert _sha256(METHOD_PATH) == METHOD_SHA256, (
        "method-hold48-tiles.md digest must match the D-130-B / D-131 tip "
        "(Method edit is B's; further drift reddens)"
    )
    assert not re.search(r"\bui/src/", SPEC), "no UI file belongs in this Spec PR"
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _plain(text)
        assert "no method file edit" in flat, name
        # ⚠ On the raw flattened text, not `_plain`: `_plain` strips ``*`` for
        # emphasis, which would silently eat the glob in ``hold48_*.py`` and
        # leave this pin matching a string nobody wrote.
        assert re.search(r"[Nn]o\s+(>\s+)?`hold48_\*\.py`\s+edit", _flat(text)), name
        assert "methodnote.jsx" in flat, name


def test_the_method_excerpt_is_authority_and_is_eighth_grade():
    """§7 carries the copy a later B must ship, in plain language."""
    sec = _section("7.", "8.")
    flat = _plain(sec)
    assert "8th-grade" in flat
    assert "required method copy" in flat
    assert "this spec pr ships no method edit" in flat
    # The precedent it follows, named rather than assumed.
    for pr in ("#243", "#246", "#249"):
        assert pr in sec, pr
    # The train, as recorded, including the two failures and the best path.
    for path in ("d-125", "d-126", "d-127", "d-128"):
        assert path in flat, path
    assert "0 of 7" in flat
    assert "0 of 3" in flat
    assert "2 of\nits 5".replace("\n", " ") in flat or "2 of its 5" in flat
    assert "d-126 is still the best of them" in flat
    # Phase 5's label survives on the owner surface, with its numbers.
    assert "accept-refuse" in flat
    assert "we have stopped trying to fix them" in flat
    assert "gave back" in flat
    # Phase 4, in plain words, including the floor and its one direction.
    assert "3272" in sec and "3394" in sec
    assert "residual rmsd" in flat
    assert "floor" in flat
    assert "proves nothing at all" in flat
    assert "never a reason to move the 10.0 å limit" in flat
    assert "we are not adding a fifth way of moving tiles" in flat
    assert "fixing zero of the two is an allowed outcome" in flat
    assert "served" in flat and "assembler" in flat
    assert "not medical advice" in flat
    assert "f-004" in flat


def test_out_of_scope_fences_are_written():
    sec = _plain(_section("8.", "9."))
    for fence in (
        "linker spec",
        "domain-partition spec",
        "dual-mode spec",
        "linker-v2 / piecewise-v2 / rmsd-v2",
        "threshold change",
        "served-path swap",
        "rent / gpu / runpod / fly post",
        "claiming seams solved",
        "self-merging",
        "inventing an accession",
    ):
        assert fence in sec, fence
    assert "**Yes — this PR.**" in _section("8.", "9.")
    assert "later emma / matt go" in sec
    assert "trinity merges" in _plain(SPEC)
    # A and B are not pre-authorised by the Spec that specs them.
    log_flat = _plain(_d130_entry())
    assert "does not invent d-130-a or d-130-b" in log_flat
    assert "no self-merge" in log_flat


# ---------------------------------------------------------------- T-1199


def test_the_d129_crosslink_moves_the_hunt_without_moving_the_fate():
    """§6 records that the GO arrived — and that nothing else changed."""
    flat = _flat(D129_SPEC)
    assert "Phase 4 amendment (D-130)" in flat
    assert "SPEC-residual-rmsd-hunt.md" in D129_SPEC
    assert "### D-130" in D129_SPEC
    section_6 = D129_SPEC.split("## 6.")[1].split("## 7.")[0]
    low = _plain(section_6)
    assert "go phase 4" in low
    assert "spec-governed" in low
    # ⚠ The whole point: governed is not accepted.
    assert "still not accept-refuse" in low
    assert "a governed hunt is an open fate" in low
    assert "phase 5 is not reopened" in low
    assert "freeze is not repealed" in low
    assert "the log governs" in low
    # And D-129's own clauses are untouched by the cross-link.
    assert "3432 stays accept-refuse" in low
    assert "may not be softened, dropped, split apart" in low
    _absent(BANNED_SOLVED_CLAIMS, D129_SPEC, "the D-129 Spec after the cross-link")


def test_the_standing_disclosure_and_the_freeze_survive():
    """D-129 §4 and §7 are inherited, not spent."""
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _plain(text)
        assert "0 of 7" in flat, name
        assert "standing" in flat, name
        assert "served" in flat and "assembler" in flat, name
        assert "no auto-flip" in flat, name
        assert "no f-004" in flat, name
        assert "best experimental" in flat, name
    spec_flat = _plain(SPEC)
    assert "ungutted" in spec_flat or "may not be softened" in spec_flat
    assert "both failed rescues" in spec_flat or "both the d-127 and d-128 failed rescues" in spec_flat
    assert "callable" in spec_flat
    # Only ONE freeze clause is satisfied, and it is named.
    assert "phase 4 rmsd only on explicit matt go" in spec_flat
    assert "is not repealed" in spec_flat or "not a repeal" in spec_flat
    # D-128's Spec keeps its own Phase 5 amendment — nothing here undoes it.
    assert "Phase 5 amendment (D-129)" in _flat(D128_SPEC)


def test_ship_index_plan_architecture_and_test_plan_carry_d130():
    """⚠ Widened at D-130-A — the ship rows move with the ship, exactly.

    The Spec PR pinned *"D-130 Spec … Yes — this PR"* and *"D-130-A … Later
    Emma / Matt GO"*. A's GO arrived, so the Spec row must now read
    **already shipped** and **A** must be this PR — and B must **still** be
    unauthorised, which is the clause a tidy-up would quietly drop.
    """
    index_flat = _flat(INDEX)
    assert "Active ship — D-130" in index_flat
    assert re.search(r"\*\*D-130 Spec\*\*.*Already shipped on `main` \(#252", index_flat)
    assert re.search(r"\*\*D-130-A\*\*.*\*\*Yes — this PR\.\*\*", index_flat)
    assert re.search(r"\*\*D-130-B\*\*.*Later Emma / Matt GO", index_flat)
    # A ships code; it does not discharge the mandatory Method obligation.
    assert "does **not** discharge" in INDEX or "does not discharge" in INDEX.lower()
    assert re.search(r"\*\*D-129 Spec\*\*.*Already shipped on `main` \(#249", index_flat)
    assert "SPEC-residual-rmsd-hunt.md" in INDEX
    # PLAN + ARCHITECTURE point at D-130 and its Spec file.
    assert "**D-130**" in PLAN
    assert "SPEC-residual-rmsd-hunt.md" in PLAN
    assert "confirm `### D-130` exists" in PLAN
    assert "D-130" in ARCH
    assert "SPEC-residual-rmsd-hunt.md" in ARCH
    arch_flat = _plain(ARCH)
    assert "residual_rmsd/" in ARCH
    assert "one-directional" in arch_flat
    assert "phase 4 must-hunt" in arch_flat
    # Test plan carries the D-130 T-ids and this file.
    for tid in ("T-1191", "T-1194", "T-1195", "T-1199"):
        assert tid in TEST_PLAN, tid
    assert "test_d130_residual_rmsd_spec.py" in TEST_PLAN


def test_this_pr_runs_no_ops_and_re_measures_nothing():
    """Every prior figure is quoted; none is re-derived (D-016)."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _plain(text)
        assert "not an ops run" in flat, name
        assert "nothing is re-measured here" in flat or "nothing re-measured here" in flat, name
        assert "no re-measure" in flat or "not re-measured" in flat, name
    entry = _plain(_d130_entry())
    # The tip was confirmed against the remote rather than taken from the brief.
    assert "544e821" in entry
    assert "confirmed against the remote before citing" in entry
    # And the provenance names the disagreement it found while confirming.
    assert "cbcb47d" in entry


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
