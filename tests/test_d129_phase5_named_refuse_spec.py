"""D-129 — Phase 5 named-refuse Spec. These must be able to go red.

Spec GO: the living-log heading exists, the Spec file exists, the **eight**
parents (the D-128 linker seven + 3432) are ``accept-refuse``, the forbidden
labels are written as forbidden (open must-hunt / solved / a D-128 miss), the
D-128 OPS **0 of 7** and its named confusion stay a **mandatory** D-128-B
disclosure (accept-refuse is not Method silence), 3272 / 3394 stay **Phase 4
must-hunt** behind explicit Matt GO language, the stitch family **freezes**
(no linker-v2, 10.0 A gate, served = assembler, D-126 best experimental,
both failed rescues disclosed), the D-128 Spec carries the cross-link as a
**label** change only, and this PR edits no Method file, no UI file, and no
``hold48_*.py``.

⚠ Two failures these pin red. **Relabel-and-forget:** mark the eight accepted
and drop the 0-of-7 / the regress, so the surface reads like success — the
disclosure is pinned as a requirement *of the label*. **Relabel-as-defeat:**
read a pre-registered allowed outcome as a *D-128 miss*, which is how a
project argues itself into loosening a gate.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
SPEC_PATH = ROOT / "docs" / "SPEC-phase5-named-refuse.md"
SPEC = SPEC_PATH.read_text(encoding="utf-8")
D128_SPEC_PATH = ROOT / "docs" / "SPEC-linker-seam-honesty.md"
D128_SPEC = D128_SPEC_PATH.read_text(encoding="utf-8")
INDEX = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs" / "PLAN-ui-post-wave2-endstate.md").read_text(encoding="utf-8")
TEST_PLAN = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
STITCH = (ROOT / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
METHOD_PATH = ROOT / "docs" / "method-hold48-tiles.md"

# The D-128 linker seven (D-128 Spec §3 — itself the D-127 OPS
# `linker_jump_gt_10` class, as recorded) plus 3432, which was ALREADY
# accept-refuse under signed triage. Eight fates, locked by the Matt Phase 5
# sign 2026-09-05 ~17:58 PT via Emma. ⚠ Not re-measured.
SEVEN_LINKER_PARENT_IDS = (2938, 2939, 3179, 3190, 3321, 3368, 3566)
ALREADY_ACCEPT_REFUSE_PARENT_ID = 3432
ACCEPT_REFUSE_EIGHT = SEVEN_LINKER_PARENT_IDS + (ALREADY_ACCEPT_REFUSE_PARENT_ID,)

# Phase 4 must-hunt: the `rmsd_gt_10` class. NOT accept-refuse, and moved only
# by a separate Matt GO.
PHASE_4_MUST_HUNT = {3272: "Q6V0I7", 3394: "Q8TDW7"}

# Accessions this log already carries. The other five of the seven are NOT on
# record — the Spec says so instead of inventing one (D-016).
RECORDED_ACCESSIONS = {2939: "Q7Z408", 3368: "Q5SZK8", 3432: "Q8IZF6"}
UNRECORDED_ACCESSION_PARENT_IDS = (2938, 3179, 3190, 3321, 3566)

# The recorded D-128 OPS rollup of the seven, as recorded by Kaylee at tip
# `9e65cbf`, out_root `linker_seam_ops_2026-09-05`. ⚠ NOT re-measured, and this
# suite must not become a second measurement of it.
OPS_PASS, OPS_REFUSE, OPS_FAIL, OPS_SKIP = 0, 7, 0, 0
OPS_REPAIRED_OF_SEVEN = 0
OPS_SEAM_JUMP_REFUSED = (2938, 3179, 3190, 3321, 3368, 3566)
OPS_RMSD_REFUSED = (2939,)
OPS_CONFUSION = {
    "n_d125_pass_d128_refuse": 5,
    "n_d126_pass_d128_refuse": 6,
    "n_d127_pass_d128_refuse": 0,
    "n_d127_refuse_d128_pass": 0,
}
# Recorded as-is and deliberately NOT re-derived here (D-016).
OPS_RECORDED_NOT_REDERIVED = {"n_seams_measured": 35, "n_honesty_unknown": 4}
OPS_DISHONEST_LINKER_SEAM = 6
GATE_ANGSTROM = "10.0"

# D-127's refuse histogram, as recorded: the fates below must exhaust it.
D127_REFUSE_TOTAL = 10

# Modules on `main` at `9e65cbf`. A moved hash means a `hold48_*.py` was
# edited — forbidden in this docs-only Spec PR.
D125_KABSCH_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"
D126_CONF_SHA256 = "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18"
D127_PIECEWISE_SHA256 = "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04"
D128_LINKER_SEAM_SHA256 = "c270f8711040471a9080a23ab4c1e167a0cc2eedf546c3481cd9ed4f4eb19843"
# The Method file. ⚠ RE-PINNED at D-129-B. The Spec PR (`1baf4c0` / #249)
# shipped `885ecda3…` — §5 was authority only, and a docs Spec PR may not
# edit the Method file. A **B** PR is precisely the PR that may, and D-129-B
# is the §3 re-label §8 gated on a later Emma GO. Re-pinning a digest is only
# honest because the by-content guard below
# (`test_the_shipped_method_disclosure_survives_by_content_not_just_by_hash`)
# is left untouched: a softened 0-of-7 still fails with a reason, not a hash.
#
# ⚠ Re-pinned again at **D-129-C** (`4cd8f832…` → below). Its failure message
# asks for a decision entry behind any Method edit outside the labelling
# BUILD, and `### D-129-C` is that entry: the §7 provenance inject gained the
# supersession clause D-129-B put only on the sentence beneath it. **Additive
# only** — the by-content guard below is again left untouched, and
# `tests/test_d129_c_must_hunt_supersession.py` adds a second content guard
# that goes red if the rule is ever satisfied by deleting the sentence.
#
# ⚠ Re-pinned again at **D-132** (`4c250063…` → below). The failure message asks
# for a decision entry behind any Method edit outside the labelling BUILD, and
# `### D-132` is that entry: the inventory amend adds a scope paragraph saying
# "the 27" is the RUN POPULATION, not the volume, because the volume measured
# **45** on 2026-09-08. **Additive, and additive in the safest direction** — it
# adds a limit on what the OPS numbers cover and restates none of them. Every
# by-content guard below is again left untouched, so a softened 0-of-7, a
# deleted refuse class, or a run silently re-scoped onto 45 parents still fails
# with a reason rather than on a digest.
METHOD_SHA256 = "219409f619c9d13e94945cd5dcb641bc41e1c312f38e0be77ea848756b9904dd"

MODULE_PINS = {
    "core/hold48_kabsch.py": D125_KABSCH_SHA256,
    "core/hold48_confidence_kabsch.py": D126_CONF_SHA256,
    "core/hold48_piecewise_kabsch.py": D127_PIECEWISE_SHA256,
    "core/hold48_linker_seam.py": D128_LINKER_SEAM_SHA256,
}


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _plain(text: str) -> str:
    """Flat, lowercased, with markdown decoration stripped.

    Phrase checks read the *claim*, not its formatting — otherwise moving a
    ``**``, or a line wrapping inside a ``>`` blockquote, silently disarms a
    pin. Emphasis, backticks, quotes and blockquote markers all go.
    """
    stripped = re.sub(r"[*`>\"\u201c\u201d]", "", _flat(text))
    return re.sub(r"\s+", " ", stripped).lower()


def _section(number: str, following: str | None) -> str:
    """One numbered section of the D-129 Spec. ``following=None`` = to the end."""
    body = SPEC.split(f"## {number}")[1]
    return body if following is None else body.split(f"## {following}")[0]


def _d129_entry() -> str:
    """Just the D-129 living-log entry.

    Negative checks must be scoped to this entry: the full log is 20k lines of
    history that legitimately quotes phrases like "not that the seams are
    solved", and a repo-wide ban would either fail on old prose or be watered
    down until it catches nothing.
    """
    after = LOG.split("### D-129 —", 1)
    assert len(after) == 2, "no ### D-129 entry to scope against"
    return after[1].split("\n### ", 1)[0]


def _absent(banned: tuple[str, ...], text: str, label: str) -> None:
    """Assert none of ``banned`` appears, without a pathological pytest diff.

    Comparing two short lists keeps the failure message readable; asserting
    ``x not in huge_single_line_string`` makes pytest character-diff ~40 KB.
    """
    plain = _plain(text)
    present = [phrase for phrase in banned if phrase in plain]
    assert present == [], f"{label} makes a forbidden claim: {present}"


def _sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


# Claims that may never appear: a fix nobody measured.
BANNED_SOLVED_CLAIMS = (
    "the seams are solved",
    "seams are now solved",
    "we solved the seam",
    "the seam is repaired",
    "the seams are fixed",
    "full-length af-quality structure",
    "seams are now honest",
    "accept-refuse means solved",
)


# ---------------------------------------------------------------- T-1172


def test_d129_heading_exists_in_the_living_log():
    """The check is the entry, not a citation of one (D-062 / method-note 7)."""
    assert re.search(
        r"^### D-129 — Phase 5 named-refuse",
        LOG,
        re.M,
    ), "D-129 must be a real ### entry, not a citation of one"
    # The entries it cites as parents must still be real headings too.
    assert re.search(r"^### D-128 — Linker / seam honesty Spec", LOG, re.M), (
        "D-129 cites D-128 as authority; that heading must exist (D-062)"
    )
    assert re.search(r"^### D-128-A — Linker / seam honesty core", LOG, re.M), (
        "D-129 cites the D-128-A core entry; that heading must exist"
    )
    assert re.search(r"^### D-127-B — UI four-path honesty", LOG, re.M)
    assert re.search(r"^### D-127 — Piecewise / domain-aware Kabsch Spec", LOG, re.M)
    log_flat = _flat(LOG).lower()
    assert "docs spec only" in log_flat or "docs only" in log_flat
    assert "not d-128-b" in log_flat
    assert "phase 5 named-refuse" in log_flat


def test_spec_file_exists_and_names_its_authority():
    assert SPEC_PATH.is_file()
    flat = _flat(SPEC).lower()
    # Labels, not algorithms — the whole scope of this Spec.
    assert "authority is over labels, not over algorithms" in flat
    assert "accept-refuse" in flat
    assert "named refuse" in flat
    assert "phase 5 named-refuse" in flat
    # It points back at the log, which governs.
    assert "the log governs" in flat
    assert "### D-129" in SPEC, "the Spec must tell a reader to confirm the heading"
    assert "SPEC-phase5-named-refuse.md" in INDEX


def test_matt_signed_phase_5_is_bound_with_provenance():
    """The sign is the authority; it is named, dated, and routed."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        plain = _plain(text)
        assert (
            "d-0043 phase 5 named-refuse, signed 2026-09-05 ~17:58 pt" in plain
            or "matt signed phase 5 named-refuse" in plain
        ), name
        assert "2026-09-05" in plain, name
        assert "17:58 pt" in plain, name
        assert "emma" in plain, name
        assert "sign phase 5 as drafted" in plain, name
    # The D-0043 roadmap phase this sign belongs to.
    assert "D-0043" in LOG
    assert "D-0043" in SPEC
    assert "Phase 5" in LOG
    # Model pin is unchanged, not re-decided.
    assert "D-0037" in LOG


def test_no_vault_prose_is_invented():
    """Vault prose enters only as the verbatim SIGNED source Emma supplied."""
    entry = _plain(_d129_entry())
    assert "no vault file is on disk" in entry
    assert "obsidian" in entry, "the log must say where the vault actually lives"
    assert "emma confirmed the vault pin matches" in entry
    # The source is quoted, not paraphrased: a fenced verbatim block exists.
    assert "## 11. The SIGNED source, verbatim" in SPEC
    assert "# Phase 5 named-refuse — SIGNED (D-0043)" in SPEC
    # Invention stays forbidden even though quoting is now possible.
    assert "invented" in entry
    assert "paraphrased as if quoted" in entry or "reconstructed" in entry
    # No vault file has appeared in this repo (scoped: docs/ and repo root).
    strays = [
        q
        for q in list((ROOT / "docs").glob("*vault*")) + list(ROOT.glob("*vault*"))
    ]
    assert strays == [], f"a vault file appeared on disk: {strays}"


def test_signed_source_is_quoted_verbatim_and_every_clause_is_bound():
    """§11 reproduces the pin, and each clause is mapped to a section."""
    sec = _section("11.", None)
    # The pin's own lines, verbatim — not reworded.
    for line in (
        "Status: SIGNED 2026-09-05 ~17:58 PT — Matt: Sign Phase 5 as drafted.",
        "Forced by: D-128 OPS tip 9e65cbf — PASS 0 / REFUSE 7 / recovered 0",
        "Architect: diagnosis yes, repair no.",
        "Freeze unchanged: served=assembler; D-126 best experimental; "
        "no threshold loosen; no F-004; no auto-flip.",
        "Linker class → accept-refuse (failed hunt): 2938 seam_jump_gt_10; "
        "2939 rmsd_gt_10; 3179/3190/3321/3368/3566 seam_jump_gt_10.",
        "Already accept-refuse: 3432 (no_domain_pieces) unchanged.",
        "Still must-hunt Phase 4 later: 3272, 3394 (RMSD).",
        "label linker seven + 3432 as named refuse",
        "D-126 remains best experimental callable.",
        "Stop: no linker-v2 without new Matt GO; no gate loosen; "
        "Phase 4 RMSD only on explicit Matt GO.",
        "Scar candidate S-20260905: linker/seam honesty diagnosed; "
        "did not repair; seven → named refuse.",
    ):
        assert line in sec, f"pin line not quoted verbatim: {line[:60]}"
    # Exact citation form, and the external-numbering trap.
    assert "D-0043 Phase 5 named-refuse, SIGNED 2026-09-05 ~17:58 PT" in SPEC
    plain = _plain(SPEC)
    assert "external numbering" in plain
    assert "not repo ### d-043" in plain or "not** repo **### d-043" in _flat(SPEC).lower()
    assert "### d-043" in plain, "the colliding repo id must be named to be avoided"
    # And each clause is mapped to a section, so "bound exactly" is checkable.
    assert "Where the pin lands in this Spec" in SPEC
    entry = _plain(_d129_entry())
    assert "d-0043" in entry
    assert "### d-043" in entry


def test_the_five_item_freeze_is_bound_item_for_item():
    """The pin's freeze clause has five items, including no F-004 / no auto-flip."""
    sec = _plain(_section("7.", "8."))
    assert "freeze unchanged" in sec
    for clause in (
        "served=assembler",
        "d-126 best experimental",
        "no threshold loosen",
        "no f-004",
        "no auto-flip",
    ):
        assert clause in sec, clause
    # "unchanged" is the operative word: these are carried, not re-decided.
    assert "unchanged is the operative word" in sec
    assert "callable" in sec, "the pin says D-126 stays callable, not merely named"
    # The Stop clause, with its qualifier intact.
    assert "not without a new matt go" in sec
    assert "no linker-v2 without new matt go" in sec, "the pin's Stop line, quoted"
    assert "forbidden by default" in sec
    assert "no linker-v2 without a new matt go" in _plain(_section("9.", "10."))
    hard = _plain(_section("9.", "10."))
    assert "no f-004" in hard and "no auto-flip" in hard
    assert "phase 4 rmsd only on explicit matt go" in hard


def test_scar_candidate_stays_a_candidate():
    """No scar registry is created and no repo id is assigned (cf. the D- pointer)."""
    assert "S-20260905" in SPEC
    plain = _plain(SPEC)
    assert "scar candidate" in plain
    assert "no s-nnnnnnnn scar registry" in plain
    assert "naming a candidate is not ruling it" in plain
    entry = _plain(_d129_entry())
    assert "s-20260905" in entry
    assert "naming a candidate is not ruling it" in entry
    # The repo genuinely has no scar registry; this PR must not have added one.
    assert not list((ROOT / "docs").glob("*scar*")), "a scar registry appeared"
    others = [
        f for f in (ROOT / "docs").glob("*.md")
        if f.name != "SPEC-phase5-named-refuse.md"
        and "S-20260905" in f.read_text(encoding="utf-8")
        and f.name != "README.md"
    ]
    assert others == [], f"the scar candidate leaked into {others}"


def test_d129_is_the_next_free_decision_id():
    """D-129 must not collide, and its successor must be exactly D-130.

    ⚠ D-129-B (the labelling BUILD) and D-129-C (the `must-hunt`
    supersession hygiene patch) are **suffixes** of this id, not new
    numbers: neither spends a `D-` id of its own and neither opens a
    pointer. So the Spec entry stays unique as `### D-129 —`, and exactly
    one `### D-129-B` and one `### D-129-C` join it.

    ⚠ Widened at D-129-C — from 2 to 3 — rather than loosened: the count is
    still exact, so a second Spec entry or a **fourth** D-129-* entry
    reddens, and the suffix set is enumerated so a stray `### D-129-D`
    fails by name instead of slipping under a `>=`.
    """
    ids = sorted({int(m) for m in re.findall(r"^### D-(\d{3})\b", LOG, re.M)})
    assert 129 in ids
    # ⚠ Widened at D-130 — from "129 is the highest" to "130 is the only id
    # above it" — rather than loosened. Spending D-130 reddened the old form
    # BY DESIGN: that is the collision guard working, not a false alarm. The
    # successor is enumerated rather than admitted by a `>=`, so a stray
    # `### D-131` still reddens, and D-130 must be THIS Spec's successor
    # heading rather than any entry that happens to take the number.
    #
    # ⚠ Widened again at **D-132** — from `[130]` to `[130, 132]` — and again by
    # enumeration, not by a `>=`. Spending D-132 reddened the previous form BY
    # DESIGN; that is the guard working. ⚠ 131 is deliberately ABSENT from this
    # list and must stay absent: it is spent, but as the suffix half of the
    # `### D-130-B / D-131` heading, so it never appears as its own `### D-1NN`.
    # A bare `### D-131` would be a real collision and still reddens here.
    #
    # ⚠ Widened again at **D-133** — from `[130, 132]` to `[130, 132, 133]` — and
    # again by enumeration. Spending D-133 (the census sortable Structure column)
    # reddened the previous form BY DESIGN; the successor is named below rather
    # than admitted by a `>=`, so a stray `### D-134` still reddens.
    #
    # ⚠ Widened again at **D-134** — to `[130, 132, 133, 134]` — same way. D-134 is
    # the stitched-parent census-identity fix; it is named below.
    #
    # ⚠ Widened again at **D-135** — to `[130, 132, 133, 134, 135]` — and again by
    # enumeration. Spending D-135 (Coverage dual population + Story consumability)
    # reddened the previous form BY DESIGN; the successor is named below, so a stray
    # `### D-136` still reddens instead of being admitted by a `>=`.
    #
    # ⚠ Widened again at **D-136** — to `[130, 132, 133, 134, 135, 136]` — and again
    # by enumeration. D-136 fills the ADC Approved Cancer type column from the FDA
    # label; it is named below. ⚠ **This is the two-branch collision the guard is for,
    # and it resolved by ADDING rather than loosening:** D-135 and D-136 were in flight
    # together, each widened this list to exclude the other, and the merge carries
    # **both** ids and **both** named-entry assertions. Neither was relaxed to a `>=`
    # to make the conflict go away.
    #
    # ⚠ Widened again at **D-137** — to `[130, 132, 133, 134, 135, 136, 137]` — the same
    # way, and for the third time it was a live two-branch collision rather than a
    # sequential one. D-137 is the census sortable **Cost** column. It was written while
    # #260 (D-136) was still open, so it landed here as `[…, 135, 137]` with 136 named as
    # the in-flight id it was deliberately not taking (F-065's class, avoided by reading
    # the open-PR list rather than assuming). #260 then merged, this assertion reddened
    # **exactly as its own comment predicted**, and the rebase inserted 136 beside 137.
    # **The redness was the guard working. Both ids are carried and neither claim is
    # weakened** — a stray `### D-138` still reddens rather than slipping under a `>=`.
    assert [i for i in ids if i > 129] == [130, 132, 133, 134, 135, 136, 137], (
        f"D-129's successors must be exactly D-130, D-132, D-133, D-134, D-135, D-136 "
        f"and D-137; found {ids[-8:]}"
    )
    assert re.search(r"^### D-136 — The ADC Approved Cancer type column", LOG, re.M), (
        "D-136 is the recorded successor id; it must be the ADC cancer-type entry, "
        "not some other entry that took the number"
    )
    assert re.search(r"^### D-137 — The census gains a sortable Cost column", LOG, re.M), (
        "D-137 is the recorded successor id; it must be the census sortable-Cost-column "
        "entry, not some other entry that took it"
    )
    assert re.search(r"^### D-134 — Stitched parents were invisible", LOG, re.M), (
        "D-134 is the recorded successor id; it must be the stitched-parent "
        "census-identity entry, not some other entry that took it"
    )
    assert re.search(r"^### D-135 — Coverage gains a SECOND population", LOG, re.M), (
        "D-135 is the recorded successor id; it must be the Coverage "
        "dual-population / Story entry, not some other entry that took it"
    )
    assert re.search(r"^### D-132 — Assemble-inventory amend", LOG, re.M), (
        "D-132 is the recorded successor id; it must be the inventory-amend "
        "entry, not some other entry that took the number"
    )
    assert re.search(r"^### D-133 — Census gains a sortable Structure column", LOG, re.M), (
        "D-133 is the recorded successor id; it must be the census "
        "sortable-Structure-column entry, not some other entry that took it"
    )
    assert re.search(r"^### D-130 — Phase 4 residual-RMSD hunt", LOG, re.M), (
        "D-130 is the recorded successor id; it must be the residual-RMSD "
        "Spec entry, not some other entry that took the number"
    )
    assert len(re.findall(r"^### D-129 —", LOG, re.M)) == 1, "exactly one D-129 Spec entry"
    assert len(re.findall(r"^### D-129-B —", LOG, re.M)) == 1, "exactly one D-129-B entry"
    assert len(re.findall(r"^### D-129-C —", LOG, re.M)) == 1, "exactly one D-129-C entry"
    suffixes = sorted(set(re.findall(r"^### D-129(-[A-Z])? ", LOG, re.M)))
    assert suffixes == ["", "-B", "-C"], f"unexpected D-129 suffix entries: {suffixes}"
    assert len(re.findall(r"^### D-129", LOG, re.M)) == 3, "the Spec and its two suffixes"


# ---------------------------------------------------------------- T-1173


def test_the_eight_parents_are_accept_refuse():
    """Fates locked: seven + 3432, all accept-refuse, in Spec and log."""
    assert len(ACCEPT_REFUSE_EIGHT) == 8
    assert len(set(ACCEPT_REFUSE_EIGHT)) == 8, "no duplicate parent in the eight"
    sec = _section("2.", "3.")
    for pid in ACCEPT_REFUSE_EIGHT:
        # A named id somewhere in §2 is not enough — five of the eight are also
        # named in §2's "accession not on record" list. Require the parent's own
        # inventory ROW, and require that row to carry the fate.
        row = re.search(rf"^\|\s*\*\*{pid}\*\*\s*\|.*$", sec, re.M)
        assert row, f"{pid} has no §2 inventory row"
        assert "accept-refuse" in row.group(0), (
            f"{pid}'s §2 row does not label it accept-refuse: {row.group(0)}"
        )
        assert str(pid) in SPEC, pid
        assert str(pid) in LOG, pid
    # Exactly eight fate rows — no quiet addition either.
    rows = re.findall(r"^\|\s*\*\*(\d{4})\*\*\s*\|", sec, re.M)
    assert sorted(int(r) for r in rows) == sorted(ACCEPT_REFUSE_EIGHT), rows
    spec_flat = _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "eight" in spec_flat
    assert "eight" in log_flat
    assert "accept-refuse" in _flat(sec).lower()
    assert "accept-refuse" in log_flat
    assert "accept-refuse" in _flat(INDEX).lower()
    # The eight are the seven plus 3432 — stated, not left to arithmetic.
    assert "+ 3432" in SPEC or "+ **3432**" in SPEC
    assert "linker seven" in spec_flat
    assert "linker seven" in log_flat


def test_3432_is_reaffirmed_not_newly_ruled():
    """3432 was already accept-refuse (signed triage). Nothing re-opens it."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "3432" in text, name
        assert "already" in flat, name
        assert "re-affirmed, not newly ruled" in flat, name
        assert "signed triage" in flat, name
    spec_flat = _flat(SPEC).lower()
    assert "not re-open" in spec_flat or "does not re-open" in spec_flat
    # And it is not the Phase 4 class.
    assert "3432 is not phase 4" in spec_flat


def test_accept_refuse_is_defined_as_a_recorded_refusal():
    """The label means an accepted refusal — never a success or a repair."""
    for text, name in ((SPEC, "Spec"), (_d129_entry(), "log")):
        plain = _plain(text)
        assert "recorded honest outcome of a refusal" in plain, name
        assert "not held" in plain, name
        assert "stop hunting" in plain, name
        assert "not a success" in plain, name
        assert "not a repair" in plain, name
        # The hunt closes; the record does not.
        assert "retires the hunt, not the record" in plain, name
    # It is a fate, not a metric: it rewrites no measured row.
    assert "a fate, not a metric" in _plain(SPEC)
    assert "seam_honesty.jsonl" in SPEC


def test_no_invented_accessions_for_unrecorded_parents():
    """D-016: name the artefact or say it is not on record. Never invent one."""
    spec_flat = _flat(SPEC).lower()
    assert "not recorded in this log" in spec_flat
    assert "do not invent" in spec_flat
    assert "from memory" in spec_flat
    assert "not recorded in this log" in _flat(LOG).lower()
    for pid in UNRECORDED_ACCESSION_PARENT_IDS:
        assert str(pid) in SPEC, pid
    # Only accessions this log already carries may appear in either file.
    allowed = set(RECORDED_ACCESSIONS.values()) | set(PHASE_4_MUST_HUNT.values())
    for text, name in ((SPEC, "Spec"),):
        found = set(re.findall(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b", text))
        assert found <= allowed, f"{name} invents accessions: {found - allowed}"
    for pid, acc in RECORDED_ACCESSIONS.items():
        assert acc in SPEC, acc
        assert str(pid) in SPEC, pid


# ---------------------------------------------------------------- T-1174


def test_forbidden_labels_are_named_as_forbidden():
    """The three wrong labels are written down as wrong, in the Spec and log."""
    sec = _section("3.", "4.")
    sec_flat = _flat(sec).lower()
    assert "forbidden labels" in sec_flat
    # (1) never open must-hunt.
    assert "open must-hunt" in sec_flat
    assert "fifth stitch algorithm" in sec_flat or "fifth algorithm" in sec_flat
    # (2) never solved / fixed / repaired — the standing park, carried forward.
    for parked in (
        "solved",
        "fixed",
        "repaired",
        "aligned",
        "superimposed",
        "seams solved",
        "seams fixed",
        "full-length af-quality",
    ):
        assert parked in sec_flat, parked
    # (3) never a D-128 miss.
    assert "a d-128 miss" in sec_flat
    assert "d-128 failure" in sec_flat
    entry = _plain(_d129_entry())
    for required in (
        "never as open must-hunt",
        "never as solved",
        "never as a d-128 miss",
    ):
        assert required in entry, required
    # The label rule is a requirement on B, not a suggestion.
    assert "must" in sec_flat
    assert "never" in sec_flat


def test_zero_of_seven_is_pre_registered_not_a_miss():
    """0-of-7 was allowed BEFORE the run — reading it as failure is the error."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "pre-registered" in flat, name
        assert "allowed outcome" in flat, name
        assert "0-of-7" in text or "0 of 7" in text, name
    spec_flat = _flat(SPEC).lower()
    # Named to the sections that pre-registered it, before the run.
    assert "d-128 §1b / §3 / §11" in spec_flat or "§1b / §3 / §11" in spec_flat
    assert "before the run" in spec_flat or "*before* the run" in _flat(SPEC).lower()
    # The diagnosis half landed; the repair half did not. Both said plainly.
    assert "diagnosis" in spec_flat
    assert "recovered nothing" in spec_flat
    # And it does not license a gate move.
    assert "does not license" in spec_flat or "not license" in spec_flat


def test_spec_never_says_seams_are_solved():
    """This Spec never says solved. Accept-refuse is not a fix."""
    plain = _plain(SPEC)
    assert "never says solved" in plain
    assert "seams are not solved" in plain
    assert "never claim seams solved" in plain
    _absent(BANNED_SOLVED_CLAIMS, SPEC, "the D-129 Spec")
    # Same check on the log entry that governs it, scoped to that entry.
    _absent(BANNED_SOLVED_CLAIMS, _d129_entry(), "the D-129 log entry")
    # And the standing forbidden-language park is carried, not dropped.
    for parked in ("aligned", "superimposed", "seams solved", "seams fixed"):
        assert parked in plain, parked


# ---------------------------------------------------------------- T-1175


def test_b_must_still_disclose_the_d128_ops_rollup():
    """accept-refuse != Method silence. The label and disclosure ship together."""
    sec = _section("4.", "5.")
    sec_flat = _flat(sec).lower()
    assert "must disclose" in sec_flat or "must be disclosed" in sec_flat
    assert "mandatory" in sec_flat
    # The headline outcome of the seven.
    assert "PASS 0 / REFUSE 7 / FAIL 0 / SKIP 0" in _flat(sec)
    assert "repaired_of_seven" in sec
    # Per-parent refuse reasons, both classes.
    assert "seam_jump_gt_10" in sec
    assert "rmsd_gt_10" in sec
    for pid in OPS_SEAM_JUMP_REFUSED:
        assert str(pid) in sec, pid
    for pid in OPS_RMSD_REFUSED:
        assert str(pid) in sec, pid
    # Honesty counts and the gate.
    assert "n_dishonest_linker_seam" in sec
    assert GATE_ANGSTROM in sec
    # The obligation is bound to a named PR, not left ownerless.
    assert "d-128-b" in sec_flat
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _flat(text).lower()
        assert "method silence" in flat, name
        assert "0 of 7" in flat, name


def test_the_shipped_disclosure_is_discharged_and_now_standing():
    """D-128-B already shipped it; this Spec makes it permanent, not re-owed."""
    sec = _plain(_section("4.", "5."))
    assert "already discharged, and now standing" in sec
    assert "cd071d7" in _section("4.", "5.")
    assert "#248" in _section("4.", "5.")
    # The four ways it could be quietly lost are each named.
    for guard in ("do not gut it", "do not split it", "do not let the §3 label replace it"):
        assert guard in sec, guard
    assert "inherits it" in sec
    assert "spec violation" in sec
    # B's own sentence is kept as the standard, so the bar is not re-invented.
    assert "bury a drop under a pre-registration" in sec
    # And the Spec is explicit that it is not restating a new obligation.
    assert "does not restate it as a new obligation" in sec
    for text, name in ((SPEC, "Spec"), (_d129_entry(), "log"), (INDEX, "index")):
        plain = _plain(text)
        assert "cd071d7" in plain, name
        assert "standing" in plain, name


def test_the_owed_relabel_is_named_and_is_discharged_at_d129_b():
    """The Spec named one open item; D-129-B closed it.

    ⚠ Extended at D-129-B. The Spec and the `### D-129` entry are historical
    records and still say the re-label was owed — that stays pinned, because
    a Spec that stopped naming what it deferred would be unreadable. What is
    added is the other half: `ARCHITECTURE.md` must name the id that
    discharged it, so the doc cannot sit claiming an open item that shipped.
    """
    for text, name in ((SPEC, "Spec"), (_d129_entry(), "log"), (ARCH, "arch")):
        plain = _plain(text)
        assert "still call" in plain or "still calls the seven" in plain, name
        assert "must-hunt" in plain, name
    arch_plain = _plain(ARCH)
    assert "d-129-b" in arch_plain, "ARCHITECTURE must name the id that re-labelled"
    assert "was owed" in arch_plain, "the owed item must read as closed, not open"
    log_plain = _plain(LOG)
    assert "### d-129-b" in log_plain, "the BUILD needs its own entry (D-062)"
    plain = _plain(SPEC)
    assert "superseded by this sign" in plain or "superseded by the phase 5 sign" in plain
    assert "later method / ui pr" in plain
    assert "not in this docs spec pr" in plain or "not** in this docs spec pr" in plain
    # It adds a label; it does not remove a number.
    entry = _plain(_d129_entry())
    assert "adds a label; it does not remove a number" in entry
    # §8 carries it as its own row, owned and gated.
    split = _plain(_section("8.", "9."))
    assert "the §3 re-label" in split
    assert "already shipped" in split and "cd071d7" in _section("8.", "9.")


def test_confusion_keys_are_exact_and_valued():
    """The §11 keys appear by name with their recorded values, not as prose."""
    sec = _section("4.", "5.")
    for key, value in OPS_CONFUSION.items():
        assert key in sec, key
        assert key in SPEC, key
        assert key in LOG, key
        row = re.search(rf"{re.escape(key)}.{{0,80}}", _flat(sec))
        assert row and str(value) in row.group(0), f"{key} must show {value}"
    for key, value in OPS_RECORDED_NOT_REDERIVED.items():
        assert key in sec, key
        assert str(value) in sec, f"{key} = {value}"
    assert str(OPS_DISHONEST_LINKER_SEAM) in sec
    # The two headline regress numbers are also legible as plain copy.
    flat = _flat(SPEC).lower()
    assert "5" in SPEC and "6" in SPEC
    assert "vs d-125" in flat
    assert "vs d-126" in flat


def test_burying_the_regress_is_named_a_spec_violation():
    """A drop is a named finding placed BESIDE the accept count, never under it."""
    sec_flat = _flat(_section("4.", "5.")).lower()
    assert "gave back" in sec_flat
    assert "beside" in sec_flat
    assert "never buried" in sec_flat or "never buried under it" in sec_flat
    spec_flat = _flat(SPEC).lower()
    assert "spec violation" in spec_flat
    # §3 without §4 is a violation, not a simplification — said in the hard stops.
    hard = _flat(_section("9.", "10.")).lower()
    assert "never method silence" in hard or "is never method silence" in hard
    assert "spec violation" in hard
    assert "not a simplification" in hard
    log_flat = _flat(LOG).lower()
    assert "not a bury" in log_flat or "not licence to bury" in log_flat


def test_ops_disclosure_names_its_provenance_and_disclaims_measurement():
    """D-016: the rollup names who recorded it, at what tip, and from what run."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text)
        assert "Kaylee" in flat, name
        assert "9e65cbf" in flat, name
        assert "linker_seam_ops_2026-09-05" in flat, name
        lower = flat.lower()
        assert "as recorded" in lower, name
        assert "not re-measured" in lower, name
        assert "do not re-measure" in lower, name
    # This PR ran nothing.
    log_flat = _flat(LOG).lower()
    assert "not an ops run" in log_flat
    assert "no rent" in log_flat or "no rent / gpu" in log_flat


def test_both_failed_rescues_stay_disclosed():
    """D-127 AND D-128. Neither replaces nor softens the other."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "d-127 and d-128 failed rescues stay disclosed" in flat, name
    spec_flat = _flat(SPEC).lower()
    # The standing D-127 figures are still quoted, not dropped.
    assert "pass 17 / refuse 10 / fail 0" in spec_flat
    assert "recovered_of_primary_three" in SPEC
    assert "may not replace one with the other" in spec_flat
    assert "may not soften either" in spec_flat


# ---------------------------------------------------------------- T-1176


def test_phase_4_pair_stays_must_hunt():
    """3272 / 3394 are the RMSD class and remain open work."""
    sec = _section("6.", "7.")
    sec_flat = _flat(sec).lower()
    assert "phase 4 must-hunt" in sec_flat
    for pid, acc in PHASE_4_MUST_HUNT.items():
        assert str(pid) in sec, pid
        assert acc in sec, acc
        assert str(pid) in LOG, pid
    assert "rmsd_gt_10" in sec
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        assert "Phase 4 must-hunt" in _flat(text), name
    assert "phase 4 must-hunt" in _flat(PLAN).lower()


def test_phase_4_pair_is_not_in_the_accept_refuse_eight():
    """The two fate sets are disjoint. No parent is accepted and must-hunt."""
    assert not set(PHASE_4_MUST_HUNT) & set(ACCEPT_REFUSE_EIGHT)
    sec_flat = _plain(_section("6.", "7."))
    assert "they are not accept-refuse" in sec_flat
    assert "not in the §2 eight" in sec_flat
    assert "must not label them accepted" in sec_flat
    inventory = _section("2.", "3.")
    # The §2 inventory table must not list them as a fate.
    for pid in PHASE_4_MUST_HUNT:
        assert not re.search(
            rf"^\|\s*\*\*{pid}\*\*\s*\|", inventory, re.M
        ), f"{pid} must not have an accept-refuse row in the §2 inventory"


def test_reclassifying_phase_4_requires_matt_go_language():
    """Neither parent moves without explicit Matt GO language naming Phase 4."""
    sec_flat = _flat(_section("6.", "7.")).lower()
    assert "separate matt go" in sec_flat
    assert "explicit matt go language" in sec_flat
    # Named routes that may NOT do it on their own.
    for route in ("b pr", "ops run", "ui convenience", "tidy-up"):
        assert route in sec_flat, route
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "separate matt go" in flat, name
        assert "explicit matt go language" in flat, name
    hard = _flat(_section("9.", "10.")).lower()
    assert "without explicit\nmatt go language" in hard or "matt go language" in hard


def test_no_rmsd_spec_bleed():
    """This Spec does not spec, scope, or schedule Phase 4."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "no rmsd spec bleed" in flat, name
    spec_flat = _flat(SPEC).lower()
    assert "does **not** spec, scope, schedule, design, or pre-authorise phase 4" in spec_flat
    assert "is **not** that go" in spec_flat
    assert "not a phase 4 / rmsd spec" in spec_flat


# ---------------------------------------------------------------- T-1177


def test_no_linker_v2_and_the_family_freezes():
    """No fifth stitch algorithm follows from this sign."""
    sec = _section("7.", "8.")
    sec_flat = _flat(sec).lower()
    assert "no linker-v2" in sec_flat
    for banned in (
        "piecewise-v3",
        "new decomposition",
        "second window size",
        "trim loop",
        "soft invent blend",
        "linker-inherit",
        "joint placement",
    ):
        assert banned in sec_flat, banned
    assert "no restitch" in sec_flat
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (INDEX, "index"), (ARCH, "arch")):
        flat = _flat(text).lower()
        assert "no linker-v2" in flat, name
        assert "freeze" in flat, name
    assert "no linker-v2" in _flat(PLAN).lower()
    # A fifth algorithm would need its own GO.
    assert "own matt go" in sec_flat


def test_gate_stays_at_10_and_does_not_loosen():
    """10.0 A stays. W = 32 stays. Epsilon stays. 0-of-7 licenses none of it."""
    assert GATE_ANGSTROM in SPEC
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "10.0 å stays" in flat, name
        assert "does not loosen" in flat or "not loosen" in flat, name
        assert "w = 32" in flat, name
        assert "1e-3" in text, name
        assert "no per-parent exception" in flat, name
        assert "named-exclusion" in flat, name
    spec_flat = _flat(SPEC).lower()
    assert "no threshold spec-as-fix" in spec_flat
    assert "0-of-7 does not license one" in spec_flat
    # This Spec changes no threshold at all.
    assert "not a threshold change" in spec_flat


def test_served_stays_assembler_and_d126_stays_best_experimental():
    for text, name in ((SPEC, "Spec"), (LOG, "log"), (ARCH, "arch")):
        flat = _flat(text).lower()
        assert "served stays assembler" in flat or "served = **assembler**" in flat, name
        assert "best experimental path until proven otherwise" in flat, name
    spec_flat = _flat(SPEC).lower()
    assert "no auto-flip" in spec_flat
    assert "a swap is a **matt go**" in spec_flat or "swap is a matt go" in spec_flat
    assert "default served = assembler" in spec_flat
    # Quantified, not asserted: 2 of 5 vs 0 of 3 vs 0 of 7.
    assert "2 of its primary 5" in SPEC
    assert "0 of 3" in SPEC
    assert "0 of 7" in SPEC
    assert "proven otherwise" in spec_flat
    assert "a measured result, not a newer idea" in spec_flat


# ---------------------------------------------------------------- T-1178


def test_d128_spec_carries_the_phase5_crosslink_in_section_3_and_9():
    """D-128 §3 inventory and §9 hard stops record the new fate and point here."""
    flat = _flat(D128_SPEC)
    lower = flat.lower()
    assert "Phase 5 amendment (D-129)" in flat
    assert "SPEC-phase5-named-refuse.md" in D128_SPEC
    assert "### D-129" in D128_SPEC
    assert "no longer must-hunt" in lower
    assert "accept-refuse" in lower
    assert "Matt SIGNED Phase 5 named-refuse" in flat
    # Placed in §3 (inventory) and §9 (hard stops), not in a footnote.
    section_3 = D128_SPEC.split("## 3.")[1].split("## 4.")[0]
    section_9 = D128_SPEC.split("## 9.")[1].split("## 10.")[0]
    for sec, name in ((section_3, "§3"), (section_9, "§9")):
        sec_lower = _flat(sec).lower()
        assert "d-129" in sec_lower, name
        assert "accept-refuse" in sec_lower, name
        assert "no longer must-hunt" in sec_lower or "not must-hunt" in sec_lower, name
    # The eight, and the boundary, both carried.
    assert "3432" in section_3
    assert "3272 / 3394" in section_9
    assert "phase 4 must-hunt" in _flat(section_9).lower()
    # The disclosure obligation travels with the label.
    assert "method silence" in _flat(section_9).lower()


def test_crosslink_changes_a_label_not_the_algorithm():
    """The amendment is explicit that the shipped algorithm does not move."""
    lower = _flat(D128_SPEC).lower()
    assert "a label, not an algorithm" in lower
    assert "stand exactly as shipped" in lower or "stand as shipped" in lower
    assert "10.0 å" in lower
    assert "w = 32" in lower
    assert "1e-3" in D128_SPEC
    # And the log says the same, so the two cannot drift.
    log_lower = _flat(LOG).lower()
    assert "authority is over labels, not over algorithms" in log_lower
    assert "does not change one line of stitch geometry" in log_lower


def test_d128_spec_still_never_says_solved():
    """The amendment must not smuggle in a fix claim."""
    plain = _plain(D128_SPEC)
    assert "never says solved" in plain
    assert "the seams are not solved" in plain
    assert "the seams are still not solved" in plain
    _absent(BANNED_SOLVED_CLAIMS, D128_SPEC, "the D-128 Spec")
    # The D-128 Spec keeps its own standing language.
    assert "signed triage" in plain
    assert "must-hunt" in plain
    # No accession invented by the amendment.
    found = set(re.findall(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b", D128_SPEC))
    allowed = set(RECORDED_ACCESSIONS.values()) | set(PHASE_4_MUST_HUNT.values()) | {"Q9P273"}
    assert found <= allowed, f"D-128 Spec gained accessions: {found - allowed}"


def test_this_spec_pr_does_not_edit_hold48_modules():
    """Hard stop: this is a labelling Spec. No core module moves a byte."""
    for name, expected in MODULE_PINS.items():
        path = ROOT / name
        assert path.is_file(), name
        assert _sha256(path) == expected, (
            f"{name} was edited — a labelling Spec PR may not touch hold48_*.py"
        )
    assert "def winning_tile" in STITCH
    assert "D-129" not in STITCH
    assert "accept_refuse" not in STITCH
    assert "phase5" not in STITCH.lower()
    for name in MODULE_PINS:
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "D-129" not in text, name


# ---------------------------------------------------------------- T-1179


def test_the_method_edit_landed_at_b_and_not_in_the_spec_pr():
    """§5 is authority. The Method file is edited at B, never in a Spec PR.

    ⚠ Flipped at D-129-B. The Spec PR shipped no Method edit; the §3
    re-label did, under the later Emma GO §8 required. What this now pins
    is that the Method file is at **B's** content and carries the D-129-B
    section — and, still, that the Spec itself claims no Method edit.
    """
    method = METHOD_PATH.read_text(encoding="utf-8")
    assert _sha256(METHOD_PATH) == METHOD_SHA256, (
        "method-hold48-tiles.md moved off the D-129-B pin — a Method edit "
        "outside the labelling BUILD needs its own decision entry"
    )
    assert "## Addendum D-129-B" in method, "the §3 re-label must be on the Method file"
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "no method edit" in flat or "ships no method edit" in flat, name
        assert "method-hold48-tiles.md" in text, name
    assert "authority only" in _flat(SPEC).lower()


def test_the_shipped_method_disclosure_survives_by_content_not_just_by_hash():
    """Do not gut what D-128-B shipped.

    The sha256 pin below already fails on any edit, but a hash mismatch says
    only "changed". This says *what* must still be there, so a future PR that
    softens the OPS disclosure fails with the reason rather than a digest.
    """
    method = METHOD_PATH.read_text(encoding="utf-8")
    plain = _plain(method)
    # The zero, and the give-back that must travel with it.
    assert "pass 0 · refuse 7 · fail 0 · skip 0" in plain or "pass 0" in plain
    assert "repaired_of_seven" in method
    assert "n_d125_pass_d128_refuse" in method
    assert "n_d126_pass_d128_refuse" in method
    assert "5" in method and "6" in method
    # B's own statement of why they are inseparable.
    assert "bury a drop under a pre-registration" in plain
    # The standing facts D-129 also depends on.
    assert "pre-registered as an" in plain
    assert "d-126 remains the best experimental path" in plain
    assert "no linker-v2" in plain
    assert "3432 stays accept-refuse" in plain
    assert "accept-refuse" in plain
    # And it still refuses the fix claim. Checked as the presence of the
    # negation rather than the absence of the words: this file says "never
    # claim the seams are solved", so a substring ban would fire on the very
    # sentence that forbids the claim.
    assert "never claim the seams are solved" in plain
    assert "seams are not scientifically solved" in plain
    assert "not a seam that" in plain or "recorded is not a seam that was solved" in plain


def test_no_ui_file_in_this_spec_pr():
    """No React, no MethodNote.jsx. The labels land at B."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text)
        assert "MethodNote.jsx" in flat, name
        lower = flat.lower()
        assert "no ui" in lower, name
    spec_flat = _flat(SPEC).lower()
    assert "any ui / react file" in spec_flat
    # The UI obligation is named and owned by D-128-B.
    assert "d-128-b" in spec_flat


def test_method_excerpt_is_authority_and_is_eighth_grade():
    """§5 carries the copy a later B must ship, in plain language."""
    sec = _section("5.", "6.")
    sec_flat = _flat(sec).lower()
    assert "8th-grade" in sec_flat
    assert "required method copy" in sec_flat
    assert "this spec pr ships no method edit" in sec_flat
    # Same additive pattern, and the precedent it follows is named.
    assert "#243" in sec
    assert "#246" in sec
    assert "#245" in sec
    for prior in ("d-121", "d-125-b", "d-126-b", "d-127-b"):
        assert prior in sec_flat, prior
    # The excerpt names all four paths and what happened to each.
    for path in ("d-125", "d-126", "d-127", "d-128"):
        assert path in sec_flat, path
    assert "0 of 7" in sec_flat
    assert "2 of its 5" in sec_flat or "2 of 5" in sec_flat
    assert "0 of 3" in sec_flat
    # The plain-language meaning of the label, both halves.
    assert "these joins do not hold" in sec_flat
    assert "stopped trying to fix them" in sec_flat
    assert "does **not** mean the seam is solved" in _flat(sec).lower()
    assert "it does **not** mean we stop reporting the numbers" in _flat(sec).lower()
    assert "gave back" in sec_flat
    # The two still-open parents, and the served path.
    assert "3272" in sec and "3394" in sec
    assert "still being looked at" in sec_flat
    assert "served" in sec_flat and "assembler" in sec_flat
    assert "no fifth stitching" in sec_flat
    assert "never claim seams solved" in sec_flat
    # Method's standing limits stay.
    assert "not medical advice" in sec_flat
    assert "f-004" in sec_flat


def test_out_of_scope_fences_are_written():
    sec = _section("8.", "9.")
    sec_flat = _flat(sec).lower()
    for fence in (
        "linker-v2 spec",
        "phase 4 / rmsd spec",
        "merging\nd-128-b".replace("\n", " "),
        "self-merging",
        "re-opening 3432",
        "reclassifying 3272 / 3394",
        "restitch or ops run",
        "rent / gpu / runpod / fly post",
        "threshold change",
        "served-path swap",
        "claiming seams solved",
    ):
        assert fence in sec_flat, fence
    # PR split names who ships what.
    assert "**Yes — this PR.**" in sec
    assert "d-128-b" in sec_flat
    assert "later emma go" in sec_flat
    assert "trinity merges" in _flat(SPEC).lower()
    log_flat = _flat(LOG).lower()
    assert "does not merge d-128-b" in log_flat
    assert "no self-merge" in log_flat


# ---------------------------------------------------------------- T-1180


def test_ops_figures_are_internally_consistent_before_they_are_quoted():
    """D-016: check the arithmetic of the recorded rollup before repeating it.

    These are identities over the RECORDED numbers, not a re-measurement.
    """
    # The run covered exactly the seven.
    assert OPS_PASS + OPS_REFUSE + OPS_FAIL + OPS_SKIP == len(SEVEN_LINKER_PARENT_IDS)
    # The refuse histogram accounts for every refusal.
    assert len(OPS_SEAM_JUMP_REFUSED) + len(OPS_RMSD_REFUSED) == OPS_REFUSE
    assert set(OPS_SEAM_JUMP_REFUSED) | set(OPS_RMSD_REFUSED) == set(
        SEVEN_LINKER_PARENT_IDS
    )
    assert not set(OPS_SEAM_JUMP_REFUSED) & set(OPS_RMSD_REFUSED)
    # Nothing was repaired because nothing passed.
    assert OPS_REPAIRED_OF_SEVEN == OPS_PASS == 0
    # PASS 0 forces this one: D-128 accepted nobody, so it rescued no D-127 refuse.
    assert OPS_CONFUSION["n_d127_refuse_d128_pass"] == 0
    # The seven ARE D-127's linker_jump_gt_10 refuses, so none was a D-127 PASS.
    assert OPS_CONFUSION["n_d127_pass_d128_refuse"] == 0
    # No confusion count can exceed the run's population.
    for key, value in OPS_CONFUSION.items():
        assert 0 <= value <= len(SEVEN_LINKER_PARENT_IDS), key
    # Dishonest-after-move agrees with the seam_jump refuses; 2939 is unknown,
    # not dishonest, because it refused before any transform (null != 0.0).
    assert OPS_DISHONEST_LINKER_SEAM == len(OPS_SEAM_JUMP_REFUSED)
    assert OPS_DISHONEST_LINKER_SEAM + len(OPS_RMSD_REFUSED) == OPS_REFUSE
    # And the Spec states that reading, rather than leaving it to the reader.
    spec_flat = _flat(SPEC).lower()
    assert "internal consistency" in spec_flat
    assert "forced" in spec_flat
    assert "refused **before any transform**" in _flat(SPEC).lower()
    assert "null is not zero, unknown is not honest" in spec_flat
    assert "internal consistency" in _flat(LOG).lower()


def test_eight_plus_phase4_pair_exhaust_the_d127_refuses():
    """Every D-127 refuse now carries exactly one fate: accepted, or Phase 4."""
    assert len(ACCEPT_REFUSE_EIGHT) + len(PHASE_4_MUST_HUNT) == D127_REFUSE_TOTAL
    assert not set(ACCEPT_REFUSE_EIGHT) & set(PHASE_4_MUST_HUNT)
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text)
        assert "8 + 2 = 10" in flat, name
        lower = flat.lower()
        assert "disjoint" in lower, name
        assert "exactly one fate" in lower, name
    spec_flat = _flat(SPEC).lower()
    assert "nothing is left unlabelled" in spec_flat
    assert "no parent is in both" in spec_flat
    # It is arithmetic on a recorded histogram, and says so.
    assert "not** a re-measurement" in spec_flat or "not a re-measurement" in spec_flat


def test_unreproducible_counts_are_marked_recorded_not_rederived():
    """A summary is not knowing: say what cannot be reconstructed here."""
    for text, name in ((SPEC, "Spec"), (LOG, "log")):
        flat = _flat(text).lower()
        assert "not re-derived" in flat, name
        assert "n_seams_measured" in text, name
        assert "n_honesty_unknown" in text, name
        assert "recording a belief" in flat, name
    for key, value in OPS_RECORDED_NOT_REDERIVED.items():
        assert f"{key}` = **{value}**" in SPEC or f"**{value}**" in SPEC, key


def test_ship_index_plan_architecture_and_test_plan_carry_d129():
    index_flat = _flat(INDEX)
    # ⚠ Re-pointed at D-130, not weakened. These two lines used to read
    # "Active ship — D-129" and "D-129 Spec … **Yes — this PR.**", which
    # were true while D-129 was in flight and are false now that #249, #250
    # and #251 have landed and D-130 is the active ship. Both are replaced
    # by the claim that is *currently* checkable — the index records the
    # D-129 Spec as shipped, with its PR number — so the pin still fails if
    # D-129 is dropped from the index, renumbered, or quietly demoted.
    assert "Active ship — D-130" in index_flat
    assert re.search(r"\*\*D-129 Spec\*\*.*Already shipped on `main` \(#249", index_flat)
    assert re.search(r"\*\*D-130 Spec\*\*.*\*\*Yes — this PR\.\*\*", index_flat)
    assert re.search(r"D-128 Spec.*Already shipped on `main`", index_flat)
    assert re.search(r"D-128-A.*Already shipped on `main`", index_flat)
    assert re.search(r"D-128-B.*Already shipped on `main`", index_flat)
    assert "9e65cbf" in INDEX
    assert "SPEC-phase5-named-refuse.md" in INDEX
    # PLAN + ARCHITECTURE point at D-129 and its Spec file.
    assert "**D-129**" in PLAN
    assert "SPEC-phase5-named-refuse.md" in PLAN
    assert "confirm `### D-129` exists" in PLAN
    assert "D-129" in ARCH
    assert "SPEC-phase5-named-refuse.md" in ARCH
    arch_flat = _flat(ARCH).lower()
    assert "accept-refuse" in arch_flat
    assert "phase 4 must-hunt" in arch_flat
    assert "no linker-v2" in arch_flat
    # ARCHITECTURE is current: D-128-A is no longer described as "this PR".
    assert "D-128-A** is the core BUILD (this PR" not in ARCH
    # Test plan carries the D-129 T-ids and this file.
    for tid in ("T-1172", "T-1175", "T-1176", "T-1180"):
        assert tid in TEST_PLAN, tid
    assert "test_d129_phase5_named_refuse_spec.py" in TEST_PLAN
