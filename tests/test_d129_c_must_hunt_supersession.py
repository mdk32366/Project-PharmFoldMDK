"""D-129-C — the eight's retired name never stands bare on a LIVE surface.

``### D-129-B`` re-labelled the eight **named refuse / accept-refuse** and
corrected the superseded ``must-hunt`` wording *in place* rather than
deleting it. It corrected one sentence and left the one above it: at
``cbcb47d`` the **MANDATORY §7 provenance inject** on both Method surfaces
still read *"a D-128 OPS restitch of the must-hunt seven at tip 9e65cbf"*,
with the supersession four lines away in the **next paragraph**.

⚠ **The failure this file exists to redden.** A qualifier in the
neighbourhood is not qualification of the claim. The inject is the line a
provenance-minded reader quotes in isolation, so a reader who stops there
carries away a **retired** name with nothing saying it is retired. That is
**D-062's shape one size down** — a pointer near a claim read as proof
about the claim — and the fix is D-062's fix: check the thing, not the
thing near it.

⚠ **The rule is three-valued, not a ban.** ``must-hunt`` stays fully
available in each of the forms that are true:

* **Phase-4-scoped** — ``Phase 4 must-hunt`` / ``phase-4-must-hunt``. This
  names **3272 / 3394**, for whom must-hunt is the **current** status
  (D-129 §6). This PR does not touch them.
* **A negation** — a negation cue governs the occurrence, i.e. the
  sentence *forbids* the badge. Banning the bare words would have fired on
  the very copy that keeps the eight from wearing them: the trap D-128-B
  hit and documented.
* **Supersession-carrying** — the **same sentence** says the name is
  superseded.

Anything else is **bare**, and bare is the defect.

⚠ **Nothing here re-measures, re-labels, or reopens anything.** No fate
moves, no id joins or leaves the eight, no threshold, no geometry, no ops.
Every figure on the touched surfaces is Kaylee's, recorded at tip
``9e65cbf``, out_root ``linker_seam_ops_2026-09-05``.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The LIVE surfaces: prose a reader meets as *current state*, rewritten as
# state changes. Records are deliberately absent and the boundary is argued
# in `### D-129-C` — the dated `### D-NNN` entries of the log recorded what
# was true when they shipped (retro-editing them is the D-016 failure), the
# signed Specs carry in-place amendment blocks instead, `Test_Plan.md` rows
# describe what a test asserts, and the pinned `core/hold48_*.py` name the
# D-128 Spec §3 inventory as a code constant.
#
# ⚠ The list is explicit rather than glob-discovered, so a new document
# cannot opt itself in with a wrong classification. The trade — an eighth
# surface is unchecked until it is added here — is named in the entry.
LIVE_SURFACES = (
    "docs/method-hold48-tiles.md",
    "ui/src/components/MethodNote.jsx",
    "ui/src/components/AssemblyReview.jsx",
    "ARCHITECTURE.md",
    "docs/README.md",
    "docs/decisions.md",
    "docs/PLAN-ui-post-wave2-endstate.md",
)

# `docs/README.md` is append-at-top: only the living header above this
# marker is a surface. Everything below it is the dated record.
LOG_BODY_MARKER = "## Log (newest first)"

# The two the GO named. Kept separate from LIVE_SURFACES so dropping either
# from the enforced set fails loudly instead of silently shrinking the scan.
GO_NAMED_HOLES = (
    "docs/method-hold48-tiles.md",
    "ui/src/components/MethodNote.jsx",
)

TOKEN = "must-hunt"

# Modules this hygiene PR may not touch. Digests as on `main` at `cbcb47d`,
# except phase5_named_refuse.py widened at D-130-B / D-131.
FROZEN = {
    "core/hold48_kabsch.py": "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e",
    "core/hold48_confidence_kabsch.py": "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18",
    "core/hold48_piecewise_kabsch.py": "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04",
    "core/hold48_linker_seam.py": "c270f8711040471a9080a23ab4c1e167a0cc2eedf546c3481cd9ed4f4eb19843",
    "core/hold48_stitch.py": "6e2fcb643e4f5549297182e42def2a54fbb48d2e33659798d7314d56486ef629",
    "app/phase5_named_refuse.py": "d880cd7ac6acdfc89f4037c42bd78d3faf287c26d47d4b3ef07bfce634ccf6fc",
    "app/linker_seam_path_read.py": "5d346eacbcdfdca3370da7c54af16848b5509691da3b4323d40b0f7040c251e8",
}


# --------------------------------------------------------------- the reader
#
# Sentences, not pages. A claim a sentence must make has to be found *in
# that sentence* — the scoping D-127-B documented and D-128-B re-learned by
# mutation, applied here at one level finer.

_ENTITIES = {
    "{' '}": " ",
    "&apos;": "'",
    "&quot;": '"',
    "&nbsp;": " ",
    "&amp;": "&",
    "\u201c": '"',
    "\u201d": '"',
}
# Block-level JSX/HTML elements end a sentence; inline ones (<strong>,
# <code>, <em>) sit *inside* one and must not split it.
_BLOCK_TAG = re.compile(
    r"</?(p|li|ul|ol|h[1-6]|div|section|table|thead|tbody|tr|td|th|blockquote|br)\b[^>]*>",
    re.I,
)
_MD_BLOCK_START = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|\d+\.\s)")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_SEP = "\u241e"

NEGATION_CUES = (
    "not ",
    "never",
    "no longer",
    "none of",
    "forbidden",
    "nor ",
    "neither",
    "may not",
)
# How far back a negation may reach. A cue must govern *this* occurrence,
# not merely share a long sentence with it.
NEGATION_REACH = 80

# ⚠ A file path is not a claim about the eight. `test_d129_c_must_hunt_
# supersession.py` contains both the token and a cue, so a sentence merely
# *naming* this module would score itself green. Paths are removed before
# anything is counted — "a filename is not an identity" (method-note item 7).
_PATH = re.compile(r"[\w./-]*\.(py|jsx|js|md|json|toml|ini|ya?ml|txt|lock)\b")

SUPERSESSION_CUES = (
    "supersession",
    "what they were called",
    "were called",
    "was the name",
    "when this run was chosen",
    "when that run was chosen",
    "since re-labelled",
    "re-labelled",
    "re-label",
    "superseded",
    "supersedes",
    "still called",
    "still calls",
    "still labelled",
    "still describe",
    "no longer",
    "accurate when written",
)


def _normalise(text: str, jsx: bool) -> str:
    for old, new in _ENTITIES.items():
        text = text.replace(old, new)
    if jsx:
        text = _BLOCK_TAG.sub(_SEP, text)
        text = re.sub(r"<[^>]*>", "", text)
    else:
        text = re.sub(r"^\s*>\s?", " ", text, flags=re.M)
    return text.replace("*", "").replace("`", "")


def _blocks(text: str, jsx: bool) -> list[str]:
    text = _normalise(text, jsx)
    if jsx:
        return text.split(_SEP)
    out: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        # A markdown table cell is its own claim; a qualifier in the next
        # column does not reach this one.
        if line.lstrip().startswith("|"):
            if cur:
                out.append(" ".join(cur))
                cur = []
            out.extend(line.split("|"))
            continue
        if not line.strip() or _MD_BLOCK_START.match(line):
            if cur:
                out.append(" ".join(cur))
                cur = []
            if line.strip():
                cur = [line]
        else:
            cur.append(line)
    if cur:
        out.append(" ".join(cur))
    return out


def sentences(text: str, jsx: bool = False):
    for block in _blocks(text, jsx):
        block = re.sub(r"\s+", " ", block).strip()
        for sentence in _SENTENCE_END.split(block):
            if sentence.strip():
                yield sentence.strip()


def classify(sentence: str) -> list[tuple[str, str]]:
    """One verdict per OCCURRENCE, not per sentence.

    A sentence may hold a Phase-4 occurrence and a bare one; grading the
    sentence as a whole would let the true half carry the false half.
    """
    low = _PATH.sub(" ", sentence.lower())
    out: list[tuple[str, str]] = []
    for match in re.finditer(re.escape(TOKEN), low):
        before = low[: match.start()]
        if before.endswith("phase 4 ") or before.endswith("phase-4-"):
            out.append(("phase-4-scoped", sentence))
        elif any(cue in before[-NEGATION_REACH:] for cue in NEGATION_CUES):
            out.append(("negation", sentence))
        elif any(cue in low for cue in SUPERSESSION_CUES):
            out.append(("supersession", sentence))
        else:
            out.append(("BARE", sentence))
    return out


def surface_text(rel: str) -> str:
    text = (ROOT / rel).read_text(encoding="utf-8")
    if rel == "docs/README.md":
        assert LOG_BODY_MARKER in text, (
            f"{LOG_BODY_MARKER!r} is gone from docs/README.md — the slice that "
            "separates the living header from the dated record no longer "
            "holds, so this check would silently scan the wrong thing"
        )
        text = text.split(LOG_BODY_MARKER)[0]
    return text


def occurrences(rel: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for sentence in sentences(surface_text(rel), jsx=rel.endswith(".jsx")):
        if TOKEN in sentence.lower():
            out.extend(classify(sentence))
    return out


def _sha256(path: Path) -> str:
    # Normalize CRLF->LF so Windows checkouts match the LF pins from Linux CI.
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _plain(text: str) -> str:
    stripped = re.sub(r"[*`>\"\u201c\u201d]", "", re.sub(r"\s+", " ", text))
    return re.sub(r"\s+", " ", stripped).lower()


# ---------------------------------------------------------------- T-1187


def test_no_live_surface_carries_a_bare_must_hunt():
    """The check the GO asked for. Reintroduce a bare occurrence, go red."""
    bare: list[str] = []
    for rel in LIVE_SURFACES:
        for verdict, sentence in occurrences(rel):
            if verdict == "BARE":
                bare.append(f"\n  {rel}:\n    {sentence[:400]}")
    assert not bare, (
        "a live surface names the accept-refuse eight `must-hunt` with no "
        "qualifier in that sentence. Make it Phase-4-scoped, a negation, or "
        "supersession-carrying — do NOT delete the sentence (D-129-C):"
        + "".join(bare)
    )


def test_every_go_named_hole_is_actually_in_the_enforced_set():
    """The scan cannot shrink out from under the two surfaces the GO named."""
    for rel in GO_NAMED_HOLES:
        assert rel in LIVE_SURFACES, rel
    for rel in LIVE_SURFACES:
        assert (ROOT / rel).is_file(), f"enforced surface is missing: {rel}"
        assert occurrences(rel) or rel not in GO_NAMED_HOLES, (
            f"{rel} no longer contains the token at all — that is deletion, "
            "not qualification"
        )


def test_the_provenance_inject_carries_the_supersession_itself():
    """The exact hole, pinned by its own sentence on both Method surfaces.

    ⚠ Page-wide is not enough and never was: at ``cbcb47d`` the assertion
    ``"must-hunt is what they were called" in text`` was **green** on a page
    whose inject was bare. This finds the inject's own sentence.
    """
    for rel in GO_NAMED_HOLES:
        injects = [
            (verdict, sentence)
            for verdict, sentence in occurrences(rel)
            if "restitch of the must-hunt" in _plain(sentence)
        ]
        assert injects, f"{rel}: the D-128 OPS provenance inject is gone"
        for verdict, sentence in injects:
            assert verdict == "supersession", (
                f"{rel}: the §7 provenance inject names the retired name "
                f"unqualified ({verdict}): {sentence[:300]}"
            )
            low = sentence.lower()
            assert "9e65cbf" in low, f"{rel}: the inject lost its tip"
            assert "linker_seam_ops_2026-09-05" in low, (
                f"{rel}: the inject lost its out_root"
            )


# ---------------------------------------------------------------- T-1188


def test_the_checker_reddens_on_a_bare_occurrence():
    """Prove the classifier can fail. A green checker that cannot go red
    is the thing this project calls a green check that proves nothing."""
    verdicts = [v for v, _ in classify("a D-128 OPS restitch of the must-hunt seven at tip 9e65cbf.")]
    assert verdicts == ["BARE"]


def test_adjacent_paragraph_supersession_does_not_count():
    """⚠ The permissiveness that IS the hole.

    A checker that let a qualifier reach across a paragraph break would have
    passed ``cbcb47d`` — the supersession really was four lines below the
    bare inject. This fixture is that exact shape, and it must be BARE.
    """
    nearby = (
        "naming a D-128 OPS restitch of the must-hunt seven at tip 9e65cbf.\n"
        "\n"
        'We ran it over the seven signed must-hunt linker parents ("must-hunt"\n'
        "is what they were called when that run was chosen).\n"
    )
    verdicts = [v for v, _ in _all(nearby)]
    assert verdicts[0] == "BARE", "adjacent supersession must not qualify"
    assert verdicts[1:] == ["supersession", "supersession"]

    same_sentence = (
        "naming a D-128 OPS restitch of the must-hunt seven — must-hunt is\n"
        "what they were called when that run was chosen — at tip 9e65cbf.\n"
    )
    assert [v for v, _ in _all(same_sentence)] == ["supersession", "supersession"]


def test_the_jsx_reader_splits_on_block_elements_not_inline_ones():
    """<strong> inside a sentence must not break it; </p> must."""
    inline = (
        "<p>naming a restitch of the must-hunt seven —{' '}"
        "<strong>must-hunt is what they were called</strong> — at tip"
        " <code>9e65cbf</code>.</p>"
    )
    assert [v for v, _ in _all(inline, jsx=True)] == ["supersession", "supersession"]

    across = (
        "<p>naming a restitch of the must-hunt seven at tip 9e65cbf.</p>"
        "<p>must-hunt is what they were called.</p>"
    )
    assert [v for v, _ in _all(across, jsx=True)][0] == "BARE"


def test_a_true_half_sentence_cannot_carry_a_bare_half():
    """Grading per sentence would let the Phase 4 clause launder the eight."""
    mixed = "3272 and 3394 are Phase 4 must-hunt, and the must-hunt seven ran at 9e65cbf."
    assert [v for v, _ in classify(mixed)] == ["phase-4-scoped", "BARE"]


def _all(text: str, jsx: bool = False) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for sentence in sentences(text, jsx=jsx):
        if TOKEN in sentence.lower():
            out.extend(classify(sentence))
    return out


# ---------------------------------------------------------------- T-1189


def test_the_rule_is_three_valued_and_all_three_forms_survive():
    """A ban would have deleted the copy that makes the eight honest."""
    seen = {verdict for rel in LIVE_SURFACES for verdict, _ in occurrences(rel)}
    for form in ("phase-4-scoped", "negation", "supersession"):
        assert form in seen, (
            f"no live surface carries a {form} occurrence any more — the rule "
            "was satisfied by deletion, which is not qualification"
        )


def test_qualifying_is_not_deleting():
    """⚠ The cheapest way to satisfy this file is to delete the sentence.

    So the disclosure D-128-B shipped and the label D-129-B shipped are
    re-pinned here by content. A future edit cannot buy a green hygiene
    check with a number.
    """
    method = _plain((ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8"))
    note = _plain((ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(encoding="utf-8"))
    for text, label in ((method, "method-hold48-tiles.md"), (note, "MethodNote.jsx")):
        # The zero, and the give-back that must travel with it (Spec §4).
        assert "pass 0" in text, label
        assert "refuse 7" in text, label
        assert "repaired_of_seven" in text, label
        assert "n_d125_pass_d128_refuse" in text, label
        assert "n_d126_pass_d128_refuse" in text, label
        assert "bury a drop under a pre-registration" in text, label
        assert "0 of 7" in text, label
        # The standing D-127 figures, beside D-128's.
        assert "0 of 3" in text, label
        assert "d-126 remains the best experimental path" in text, label
        # The label, and the refusals that keep it honest.
        assert "accept-refuse" in text, label
        assert "named refuse" in text, label
        assert "never claim the seams are solved" in text, label
        assert "retires the hunt, not the record" in text, label
        # The D-129-B correction this entry extends, not reverses.
        assert "must-hunt is what they were called" in text, label


def test_the_phase_4_pair_is_left_exactly_where_it_was():
    """⚠ Widened at D-130-B / D-131 — Phase 4 pair is now named refuse.

    D-129-C pinned 3272 / 3394 as still-open must-hunt so a hygiene PR could
    not quietly retire them. The Matt SIGNED Phase 4 named-refuse GO
    (2026-09-05 ~22:32 PT via Emma) authorised that retirement: surfaces must
    now say accept-refuse, and must-hunt-as-current-status is forbidden.
    """
    for rel in ("docs/method-hold48-tiles.md", "ui/src/components/MethodNote.jsx"):
        text = _plain((ROOT / rel).read_text(encoding="utf-8"))
        assert "3272" in text and "3394" in text, rel
        assert "accept-refuse" in text, rel
        assert "named refuse" in text, rel
        assert "still being looked at" not in text, rel
        # Supersession prose may still name "phase 4 must-hunt" while retiring it
        # (D-129-C three-valued rule). Ban only the open-status claims.
        for retired_open in (
            "two joins are still open",
            "they stay phase 4 must-hunt",
        ):
            assert retired_open not in text, f"{rel}: stale open hunt — {retired_open}"


# ---------------------------------------------------------------- T-1190


def test_this_hygiene_pr_edits_no_algorithm_no_registry_and_no_reader():
    """Copy and one test. Nothing that computes anything moves a byte."""
    for name, expected in FROZEN.items():
        path = ROOT / name
        assert path.is_file(), name
        assert _sha256(path) == expected, (
            f"{name} was edited — D-129-C is a copy hygiene patch and may not "
            "touch geometry, the fate registry, or the D-128 reader"
        )


def test_this_pr_runs_no_ops_and_re_measures_nothing():
    """Every figure on the touched surfaces stays Kaylee's, as recorded."""
    for rel in GO_NAMED_HOLES:
        text = _plain((ROOT / rel).read_text(encoding="utf-8"))
        assert "as recorded" in text, rel
        assert "9e65cbf" in text, rel
        assert "linker_seam_ops_2026-09-05" in text, rel
        assert "not run" in text and "re-measured" in text, rel


def test_living_docs_carry_d129_c():
    """The entry exists as a `### ` heading — checked, not cited (D-062)."""
    log = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "### D-129-C" in log, (
        "D-129-C is cited by this suite and by the surfaces it edits; a "
        "citation is not an entry (D-062 / method-note item 7)"
    )
    assert "### D-129-B" in log
    # Slice on the HEADINGS, not on the ids: the entry cites `### D-129-B`
    # in its own prose, and splitting on the bare id would cut it short.
    heads = [m.start() for m in re.finditer(r"^### D-129-[CB] ", log, flags=re.M)]
    assert len(heads) >= 2, "D-129-C must sit at the top of the log, above D-129-B"
    entry = log[heads[0] : heads[1]]
    plain = _plain(entry)
    # The GO, the boundary, and the deep-learning line the template requires.
    assert "hygiene patch only" in plain
    assert "does not reopen phase 5" in plain
    assert "deep-learning justification" in plain
    assert "provenance (d-016)" in plain
    # The count it claims, as a breakdown rather than a total.
    assert "twelve" in plain
    for name in ("decisions.md", "Test_Plan.md", "ARCHITECTURE.md"):
        path = ROOT / name if name == "ARCHITECTURE.md" else ROOT / "docs" / name
        assert "D-129-C" in path.read_text(encoding="utf-8"), name
