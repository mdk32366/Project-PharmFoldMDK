"""D-146 — Track B stops denying the surface it is served on.

`D-143` ended Track B's aspirational biology composite and, in the same sentence, wrote that the
structural order *"runs offline: it is not a ranked surface in this application."* That was true
on 2026-09-08. It stopped being true on 2026-09-09, when `D-144` put `structural_score` in the
database and on `GET /api/census-structural-ranking` and `D-145` baked the loader into the serving
image. From then on two shipped surfaces disagreed about the same object: MethodNote said the API
is the source of truth and the spreadsheet a review lens, while the owner Doc and its D-123 extract
said there was no ranked surface at all.

⚠⚠ **What this file is really guarding against is the shape of the defect, not the sentence.** The
false clause was not merely written down — it was **asserted as required** by
`tests/test_d143_track_b_structural_only.py`, so the tree actively defended it. A green, specific,
load-bearing assertion on a claim that has since become false is worse than no assertion: it makes
the correction look like a regression. Every check here is therefore written in **both directions**
— the live-route language must be present AND the denial must be absent — because a pure absence
guard passes on an empty string and a pure presence guard passes with the denial still sitting one
clause away from the route it denies.

⚠ **What this file CANNOT do, stated where a reader will meet it rather than buried in the log.**
Nothing here contacts the deployed application. If Fly began answering `result_status: not_run`
tomorrow, every test below would stay green and the copy would be false again. That is deliberate
— a test that curls production is a monitor, reddens for reasons no commit caused, and trains its
readers to re-run it — and the residual is named in `### D-146` rather than papered over. **These
tests pin an agreement between documents; the live read recorded in the entry is what pinned the
agreement to the world, once, at a stated minute.**

Failure-reds are read at the assertion, never at an import: the offline denial restored to either
file, the live-route clause deleted from either file, a missing `### D-146` heading, a bare
`### D-147`, a missing RESERVED row, or MethodNote losing its source-of-truth paragraph.

Acceptance test T-1253 (docs/Test_Plan.md addendum 2026-09-09).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from _d144_surface import (
    D144_OWN_FILES,
    D144_REGION_MIN_LINES,
    D144_SHARED_REGIONS,
    extract_region,
    region_digest,
    whole_file_digest,
)

ROOT = Path(__file__).resolve().parents[1]
PAPER_PATH = ROOT / "docs" / "pharmfold-adc-nectin4-paper.md"
ABOUT_PAPER_PATH = ROOT / "ui" / "src" / "aboutPaper.js"
PAPER = PAPER_PATH.read_text(encoding="utf-8")
ABOUT_PAPER = ABOUT_PAPER_PATH.read_text(encoding="utf-8")
LOG = (chr(10) * 2).join((ROOT / "docs" / n).read_text(encoding="utf-8")
                      for n in ("decisions.md", "findings.md", "assumptions.md", "README.md"))
RESERVED = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
METHOD_NOTE = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(encoding="utf-8")

#: The retired clause, exactly as it read on `main` at `a0ac6ce`. One constant, so the presence
#: and absence guards cannot drift apart from each other by a stray character.
OFFLINE_DENIAL = "it runs offline: it is not a ranked surface in this application"

#: The route the rank is actually served on (D-144). ⚠ Written WITHOUT backticks in the copy on
#: purpose: `AdcContext.jsx`'s `Verbatim` renders `**bold**` and nothing else, so a backtick would
#: reach the page as a literal character.
ROUTE = "/api/census-structural-ranking"

#: What the clause must now carry. Each is a separate member so a partial rewrite names the half
#: it dropped rather than failing as one opaque comparison.
REQUIRED_CLAUSES = (
    ("served live by this application", "the order is a live surface and must say so"),
    (ROUTE, "the route must be named, so a reader can check the claim"),
    ("the database and that route are the record",
     "D-144's source-of-truth ruling, restated where the contradiction was"),
    ("review lens", "the spreadsheet's status — an export, never the record"),
    ("never the source of truth", "and the half of it that does the work"),
    ("STRUCTURAL_ONLY", "what changed is where the number lives, not what it is"),
    ("not a shortlist", "still not a shortlist"),
    ("cohort-82 learned scorer", "the OTHER ranking surface, named as what this is not"),
)


def _flat(text: str) -> str:
    """Collapse whitespace so a wrapped sentence is searchable as one string.

    ⚠ Load-bearing, not a convenience: the surviving quotation of the retired clause is
    line-wrapped inside the Doc's amendment note, and a line-oriented search cannot see it.
    """
    return re.sub(r"\s+", " ", text)


def _track_b_from_extract() -> str:
    """`TRACK_B`'s string literal, parsed out of the module rather than imported."""
    match = re.search(r"export const TRACK_B =\s*\n\s*'(.+)'\n", ABOUT_PAPER)
    assert match, "TRACK_B must stay a single-quoted one-line literal (D-123)"
    return match.group(1)


def _track_b_from_doc() -> str:
    """The owner Doc's Track B sentence, bounded by the amendment notes that follow it.

    ⚠ Bounded on the notes deliberately: the retired clause is quoted inside one of them, and a
    slice that swallowed the notes would find the quotation and call it copy.
    """
    start = PAPER.index("**Track B — New Ab, new antigen")
    return _flat(PAPER[start:]).split("*⚠ Amended")[0]


def _violations(track_b: str) -> list[str]:
    """Every way a Track B sentence can fail D-146, as data.

    ⚠⚠ **This function exists so the guard can be tested against a counterfeit** (`A-016`: any red
    proves the assertion bites; `A-017`: the path must be entered). A check that is only ever run
    on the passing input proves that the input passes, not that the check would catch anything.
    """
    found = []
    if OFFLINE_DENIAL in track_b:
        found.append("offline denial present")
    found.extend(f"missing: {clause}" for clause, _ in REQUIRED_CLAUSES if clause not in track_b)
    return found


# ─────────────── the copy itself, in both files, in both directions


def test_the_offline_denial_is_gone_from_both_files():
    """⚠ The Doc first and the extract after — D-123 dec 4's direction of travel.

    The Doc may still hold the words **once**, inside its dated amendment note; the Track B
    sentence itself may not, and the extract may not at all.
    """
    assert OFFLINE_DENIAL not in _track_b_from_doc(), (
        "the owner Doc's Track B sentence still denies being a ranked surface, and "
        f"GET {ROUTE} answers `result_status: valid`"
    )
    assert OFFLINE_DENIAL not in _flat(ABOUT_PAPER), (
        "the D-123 extract still carries the denial — including in a comment, where it reads as "
        "copy to anyone skimming the module"
    )


def test_both_files_name_the_live_route_and_the_review_lens():
    """The positives, enumerated, so a partial rewrite names the clause it dropped."""
    doc_sentence, extract = _track_b_from_doc(), _track_b_from_extract()
    for clause, why in REQUIRED_CLAUSES:
        assert clause in doc_sentence, f"owner Doc: {why}"
        assert clause in extract, f"aboutPaper.js: {why}"


def test_the_extract_is_still_a_character_substring_of_the_owner_doc():
    """⚠ D-123 dec 4, re-asserted here rather than assumed from the D-143 suite.

    This entry edits both files, which is exactly when the substring discipline earns its keep:
    an amendment applied to the module alone passes a reader's eye and fails here.
    """
    assert _track_b_from_extract() in PAPER, (
        "TRACK_B is not a substring of the owner Doc — the extract has drifted"
    )


def test_the_guard_catches_a_restored_denial_and_a_deleted_route():
    """⚠⚠ `A-016` / `A-017` as an executable check rather than a paragraph in the log.

    The three reverts this entry claims are run against the SHIPPED sentence, so the counterfeits
    differ from the real thing by exactly the edit under test.
    """
    shipped = _track_b_from_extract()
    assert _violations(shipped) == [], f"the shipped sentence must pass its own check: {shipped}"

    restored = shipped.replace(
        "and that structure-only order is", f"and {OFFLINE_DENIAL}, and that structure-only order is"
    )
    assert restored != shipped, "the counterfeit must differ from the shipped sentence"
    assert "offline denial present" in _violations(restored), (
        "restoring the retired clause must be caught — this is the revert the GO asked for"
    )

    gutted = shipped.replace(ROUTE, "an internal spreadsheet")
    assert any(v.startswith("missing:") for v in _violations(gutted)), (
        "deleting the route must be caught too: a sentence can be 'fixed' by removing the claim "
        "instead of correcting it, and a pure absence guard would call that a pass"
    )


# ─────────────── the two surfaces now agree


def test_method_note_still_carries_the_source_of_truth_paragraph_it_was_right_about():
    """⚠ MethodNote is VERIFIED, not edited. It is the surface that was already correct.

    If this paragraph ever leaves, the contradiction returns from the other direction and this
    entry's premise is gone.
    """
    flat = _flat(METHOD_NOTE)
    assert "The database and the API are the source of" in flat
    assert f"<code>{ROUTE}</code>" in flat
    assert "review lens" in flat and "never the record" in flat
    assert "STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready" in flat
    assert OFFLINE_DENIAL not in flat, "no surface may deny the census rank is served"


def test_track_b_is_not_pasted_into_a_scorer_surface():
    """⚠ D-143's T-1227 carve-out, kept and extended to this entry's new clause.

    Two ranking surfaces exist. This entry makes Track B name a route; it must not make Track B
    appear on the learned scorer's pages, which is the merge both entries exist to prevent.
    """
    for rel in (
        "ui/src/components/MethodNote.jsx",
        "ui/src/components/TargetList.jsx",
        "ui/src/components/ScorerView.jsx",
        "ui/src/components/TargetScorerPanel.jsx",
        "ui/src/targetScore.js",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "served live by this application" not in text, (
            f"{rel} carries the Track B sentence — the two ranking surfaces are being merged "
            f"in the copy"
        )


def test_the_census_table_still_has_no_rank_column():
    """⚠ Hard stop from the GO, and `D-144`'s own *STANDS, UNCHANGED*: the census table is not a
    ranked shortlist. A copy PR that named the route and then added a column would have made the
    sentence true by moving the product instead of the words."""
    for rel in ("ui/src/components/CensusView.jsx", "ui/src/components/CensusTable.jsx"):
        census = (ROOT / rel).read_text(encoding="utf-8")
        assert "structural_score" not in census, f"{rel}: no structural score column on /census"
        assert "'rank'" not in census, f"{rel}: no rank column on /census"


# ─────────────── the hard stops, as properties of the tree


#: sha256 over LF-normalised bytes (RESERVED.md's hash-discipline ruling) of the D-144 / D-145
#: surface as it stood on `main` at `a0ac6ce`. ⚠ A pin, not a hope: this entry is copy, so a byte
#: moving in any of these files means the PR is no longer what its entry says it is.
#:
#: ⚠⚠ **TWO DIGESTS MOVED AT `D-147`, AND THAT IS THE PIN DOING ITS JOB.** Its failure message
#: says a route, loader or image edit *"belongs to a different entry with its own ruling"*, and
#: `### D-147` is that entry — the `ecd_intermittent` serve-time join and its `/method` paragraph.
#: The superseded values are recorded rather than overwritten in silence (D-129-C):
#:     app/census_structural_read.py       D-146: 7f581c690ebc95bc… → D-147: 0fff62b0b947…
#:     ui/src/components/MethodNote.jsx    D-146: 062fd71ff19a4121… → D-147: fc30481d792a…
#: ⚠⚠ **THE OTHER EIGHT ARE UNTOUCHED, WHICH IS THE HALF WORTH READING.** `core/census_structural.py`
#: (so `formula_version()` still returns the live run's `c859da97f73d`),
#: `scripts/census_structural_rank.py`, migration `0012`, `app/read_routes.py`, `db/models.py`,
#: `Dockerfile`, `.dockerignore` and `core/scorer.py` are **byte-identical** through D-147 — so
#: *"no formula, no schema, no migration, no loader, no image, no learned scorer"* is measured, not
#: asserted. **Nothing was relaxed: two digests moved by name, eight were left to prove the rest.**
#: ⚠ `MethodNote.jsx` also keeps every D-146 paragraph — `test_method_note_still_carries_the_
#: source_of_truth_paragraph_it_was_right_about` reads its text and is unchanged, so the moved
#: digest is an ADDITION to that file rather than an edit of what this entry pinned in it.
#:
#: ⚠⚠ **TWO MORE DIGESTS MOVED AT `D-153` — THE IMAGE PAIR, AND THIS IS THE FIRST TIME THE `image`
#: CLAUSE OF THIS GUARD'S OWN NAME HAS FIRED.** The failure message pre-committed the resolution: an
#: image edit *"belongs to a different entry with its own ruling"*, and `### D-153` is that entry —
#: `scripts/seer_cancer_burden.py` baked in as one explicit `COPY` plus its `.dockerignore`
#: negation, because `D-149` shipped the burden artefact and route without the loader and the file
#: had to be SFTP'd onto `/srv/scripts/` for the load to run. The superseded values are recorded
#: rather than overwritten in silence (D-129-C):
#:     Dockerfile      D-146/D-147: c5af8c8500c3eb97… → D-153: 7f424013f841…
#:     .dockerignore   D-146/D-147: fbd8402067ea504c… → D-153: f4e284270c3e…
#: ⚠⚠ **AND WHAT DID NOT MOVE IS AGAIN THE LOAD-BEARING HALF.** `core/census_structural.py`,
#: `scripts/census_structural_rank.py`, migration `0012` and `core/scorer.py` are still
#: byte-identical, so `formula_version()` still returns `c859da97f73d` — the value the live run
#: recorded — and *"no formula, no schema, no migration, no loader, no learned scorer"* stays a
#: measurement. **The pins were not relaxed: two were moved by name and the rest were left to prove
#: the rest.** ⚠ The `image` pins are also the narrower guard now: the additive shape of the change
#: is asserted line-by-line in `tests/test_d153_bake_burden_loader.py`, so this digest says *"the
#: image surface moved exactly once, at an entry that owns it"* rather than standing alone.
UNTOUCHED_SURFACE = {
    **D144_OWN_FILES,
    # ⚠ moved by `### D-153` (was c5af8c8500c3eb97fe95dfe468568f822811217ddee6b8a4c5a6389f0b64cd68)
    "Dockerfile":
        "7f424013f84159e8d4494eebe9726e6a2d4bc150247655ed69f97638c006ee57",
    # ⚠ moved by `### D-153` (was fbd8402067ea504c6b477483f4b111f114576a73fa0de931b6388b9e0912a63f)
    ".dockerignore":
        "f4e284270c3ea9d98ad10a2f134a158fbf63809e84a5b3f3a6bfabb0789a8635",
    # ⚠ moved by `### D-147` (was 062fd71ff19a4121a2924e00979f7bcc58228234368221ffac423f34956c7074)
    "ui/src/components/MethodNote.jsx":
        "fc30481d792a938c3990a68fff4e1f4c06aad2c7b6397307ed51585e1e48da5f",
    "core/scorer.py":
        "886b88ad8e0d25f1af74d65b25b46ab887c264fde654e9cea172d04ef9fb120b",
}

# ⚠⚠ THE TWO SHARED FILES MOVED TO A REGION PIN — D-149, same repair as `D-145`'s guard.
# `app/read_routes.py` holds every read route and `db/models.py` holds every table, so a WHOLE-FILE
# pin on them never asserted "D-144/D-145 did not move": it asserted "nothing else was ever added",
# which is a different and false property. `D-149` added two routes and two tables that touch
# nothing of D-144's, and this guard's own failure message licenses exactly that — "belongs to a
# different entry with its own ruling".
# ⚠ NARROWER, NOT LOOSER: the region digests in `tests/_d144_surface.py` come from `2170bd8`, the
# commit where D-144 MERGED, never recomputed from this tree. Of the EIGHT other whole-file pins
# here, `MethodNote.jsx` moved at D-147 and the image pair (`Dockerfile`, `.dockerignore`) moved at
# D-153; `core/scorer.py` and the D-144-own files are untouched throughout.


@pytest.mark.parametrize("rel,digest", sorted(UNTOUCHED_SURFACE.items()))
def test_no_formula_schema_route_loader_or_image_byte_moved(rel, digest):
    """⚠⚠ *"Copy amend ONLY"*, as a property rather than an intention.

    ⚠ Normalised line endings, per `RESERVED.md`'s hash-discipline ruling: git's `LF→CRLF`
    conversion on checkout means a committed file's delivered bytes differ from its committed
    ones, and a rule that raises a false alarm on every checkout trains its readers to ignore it.

    ⚠ A tree property, never a `git diff` against `origin/main` — the gate checks out a shallow
    merge ref, where a diff-based check passes by erroring (D-139's precedent).
    """
    assert whole_file_digest(rel) == digest, (
        f"{rel} changed — D-146 is a copy amendment; a formula, schema, route, loader or image "
        f"edit belongs to a different entry with its own ruling (as D-147's route edit did, and as "
        f"D-153's image edit did: see the note on UNTOUCHED_SURFACE, where four digests have now "
        f"moved by name and the formula/schema/loader ones have not)"
    )


def test_the_retired_biology_composite_did_not_come_back_with_the_route():
    """⚠ `D-143`'s ruling is not relaxed by this one. No `cancer ×` product, no 0.5 neutrals as a
    current practice, and the exclusions stay named."""
    for text, label in ((_track_b_from_doc(), "owner Doc"), (_track_b_from_extract(), "extract")):
        assert "/ normal risk" not in text, label
        assert not re.search(r"rank(ed)? by \((cancer|membrane)", text), label
        assert "not filled in as 0.5 neutrals" in text, f"{label}: the refusal stays named"
        assert "are **excluded**" in text, f"{label}: the four terms stay named as excluded"
        assert "structure only — membrane × ECD × fold confidence (pLDDT)" in text, label
        assert "(3,467 rows), not one tranche" in text, f"{label}: the census scope stays"
        assert "**Later, on its own GO:**" in text, f"{label}: the biology composite stays later"


# ─────────────── the Doc records the amendment; the D-143 note stands


def test_the_paper_carries_a_dated_amendment_note_for_this_entry():
    """D-129-C — a superseded claim is never quietly deleted, and never stands alone."""
    flat = _flat(PAPER)
    assert "Amended 2026-09-09 (owner GO; logged as **D-146**" in flat, (
        "the Doc must record this amendment with its date and id, not swap the line silently"
    )
    assert "D-144" in flat and "D-145" in flat, (
        "the note must name what made the clause false, not merely that it is false"
    )
    assert "result_status: valid" in flat and "GABBR2" in flat and "0.8443" in flat, (
        "the live read is the provenance for the amendment (D-016) and travels with it"
    )


def test_the_d143_amendment_note_is_left_standing():
    """⚠ Two notes, not one rewritten. The composite retirement and the offline retirement are
    different rulings on different days, and collapsing them would erase which was which."""
    flat = _flat(PAPER)
    assert "Amended 2026-09-08 (owner GO; logged as **D-143**" in flat
    assert "was the **aspiration**, not the computation" in flat
    assert flat.index("logged as **D-143**") < flat.index("logged as **D-146**"), (
        "the notes read oldest-first under the sentence they amend"
    )


def test_the_retired_clause_survives_only_as_the_docs_dated_quotation():
    """⚠ Exactly one copy, and it must sit inside the note that supersedes it.

    A second copy anywhere is the live claim wearing a citation's clothes — the same rule the
    D-143 suite applies to the retired composite.
    """
    flat = _flat(PAPER)
    assert flat.count(OFFLINE_DENIAL) == 1, (
        "the owner Doc must quote the retired clause exactly once, in its amendment note"
    )
    where = flat.index(OFFLINE_DENIAL)
    window = flat[where: where + 1200]
    assert "**false now**" in window, "the quotation must be marked as no longer true"
    assert ROUTE in window, "and must point at what replaced it"
    # ⚠ And the two UI test files that name the clause may only do so inside a negative assertion.
    for rel in ("ui/src/aboutPaper.test.js", "ui/src/components/AdcContext.test.jsx"):
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
            if OFFLINE_DENIAL in line:
                assert ".not.toContain(" in line, (
                    f"{rel} names the retired clause outside a negative assertion: {line.strip()}"
                )


# ─────────────── the log leads it, and the ids


def _d146_entry() -> str:
    """The D-146 entry only, bounded by the NEXT `### ` heading whatever it is.

    ⚠ Never bounded by a named neighbour: two suites here shipped slices bounded by whatever
    entry happened to be below at branch time, and both silently widened (F-024's class).
    """
    start = LOG.index("\n### D-146 —") + 1
    nxt = re.search(r"^### (?!D-146\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠⚠ THE CHECK IS THE `### D-146` HEADING, NEVER A CITATION OF IT (D-062 / method-note item
    7). A commit message naming this decision does not discharge the living-documentation rule —
    that is precisely what PR #90 did, and thirteen later citations pointed at nothing."""
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on", LOG, re.M)
    assert len(re.findall(r"^### D-146\b", LOG, re.M)) == 1, "exactly one D-146 entry"
    assert LOG.index("### D-146 —") < LOG.index("### D-145 —"), "newest first"


def test_the_entry_leads_with_what_the_gate_cannot_check():
    """⚠⚠ D-016, and the disqualifying half is the point: no test here can see the live route, so
    a future `not_run` would leave the copy false and the suite green."""
    lowered = _flat(_d146_entry()).lower()
    assert "disqualifying fact" in lowered
    assert "not_run" in lowered, "the status that would falsify the copy must be named"
    assert "monitor" in lowered, "and the reason the gate is not made into one"


def test_the_entry_records_the_live_read_that_authorises_the_amendment():
    """The claim rests on one measurement; the entry names it, with the field that could have
    disqualified it (D-016: prefer the query whose answer could disqualify you)."""
    entry = _d146_entry()
    lowered = _flat(entry).lower()
    for claim, why in (
        ("result_status", "the field that decides whether the copy is true"),
        ("valid", "what it returned"),
        ("3,467", "the row count the sentence already claimed as its scope"),
        ("gabbr2", "the top row, named rather than summarised"),
        ("0.8443", "and its score"),
        ("o75899", "with the accession, so the row is findable"),
        ("2026-09-09t06:02:08", "when the run was computed"),
        ("one unauthenticated get at one minute", "what the read is NOT"),
    ):
        assert claim in lowered, why
    assert ROUTE in entry, "the route must be named in the entry, not only in the copy"


def test_the_entry_states_the_contradiction_it_repairs_from_both_sides():
    """⚠ Quoted from both surfaces rather than summarised — a summary of a contradiction reads
    like a preference."""
    entry = _d146_entry()
    lowered = _flat(entry).lower()
    assert "methodnote.jsx" in lowered and "source of truth" in lowered
    assert OFFLINE_DENIAL in _flat(entry), "the retired clause must be quoted, not paraphrased"
    assert "pharmfold-adc-nectin4-paper.md" in lowered
    assert "both were true when written" in lowered, (
        "neither surface was wrong when it shipped, and an entry that implied otherwise would "
        "be rewriting the record"
    )


def test_the_entry_keeps_the_hard_stops_from_the_go():
    lowered = _flat(_d146_entry()).lower()
    for claim, why in (
        ("no formula change", "the formula is untouched"),
        ("no schema change", "and the schema"),
        ("no migration", "and the migration chain"),
        ("no route change", "and the route"),
        ("no census ui rank column", "and the census table"),
        ("0.5 neutrals", "the refused placeholder stays refused"),
        ("cohort-82", "the learned scorer stays a different surface"),
        ("d-079", "the bar this copy change does not widen"),
    ):
        assert claim in lowered, why
    assert "widens nothing" in lowered, (
        "the D-079 narrowing was ruled by D-144 in the log; a copy PR does not move a bar"
    )


def test_the_entry_carries_a_deep_learning_justification_that_names_the_served_output():
    """CLAUDE.md prime directive, in the form this entry actually earns: the only quantity in the
    product that varies with what the network predicted is `score_model`, and at rank 1 it IS the
    score. A copy that denies the order is served hides where the network's output is consumed."""
    lowered = _flat(_d146_entry()).replace("**", "").lower()
    assert "deep-learning justification" in lowered
    assert "esmfold" in lowered and "plddt" in lowered
    assert "score_model" in lowered
    assert "adds no deep learning" in lowered, (
        "the honest half: this entry computes nothing and trains nothing"
    )


def test_the_next_free_integer_is_named_and_barred_across_every_guard():
    """⚠⚠ The ELEVENTH pass through this resolution, and the THIRD reserved integer SPENT rather
    than skipped (`D-142` and `D-145` were the first two, both the same day).

    **Bar OR name, never neither.** Every enumerated guard must NAME the entry that spent 146 and
    BAR the bare `### D-147`. The third state — an integer neither barred nor named — is how the
    #266/#267 collision got in.

    ⚠ The bar is matched WITH its newline (`\\n### D-148" not in`), because two of these files
    hold such patterns as *data* in order to check the others; a newline-less match would find a
    "bar" in the file whose job is to look for one. That is `D-145`'s recorded mistake, not
    rediscovered here.

    ⚠⚠ **WIDENED AT `D-147` BY ADDING A NAME, AND THE PATTERN INSIDE THIS CHECK MOVED WITH IT —
    which is the part worth reading.** This test held the string `\\n### D-147" not in` as **data**,
    in order to require it of nine other files. When 147 was spent, that requirement became a
    demand that nine guards go on barring a written integer: **a required-string assertion that had
    become a required lie**, which is exactly the defect `### D-146` was written to repair, one
    level up and inside its own gate. So the requirement is now that each guard **names 146, names
    147, and bars 148** — three assertions where there were two, nothing relaxed to a `>=`, and
    nothing deleted.
    """
    assert "\n### D-148" not in LOG, (
        "D-148 is the next free integer and must stay unspent until an entry claims it by name "
        "— never admitted by a `>=`"
    )
    guards = (
        "tests/test_d129_phase5_named_refuse_spec.py",
        "tests/test_d130_residual_rmsd_spec.py",
        "tests/test_d136_cancer_type.py",
        "tests/test_d139_served_path_flip.py",
        "tests/test_d140_pipeline_programme.py",
        "tests/test_d141_land_confidence_kabsch.py",
        "tests/test_d143_track_b_structural_only.py",
        "tests/test_d144_census_structural_rank.py",
        "tests/test_d145_bake_structural_loader.py",
        # ⚠ ADDED at `D-147`: the suite that spent 147 is itself an enumerated guard now, so the
        # rule it is checked against is the rule it applies to everyone else.
        "tests/test_d147_ecd_intermittent_flag.py",
    )
    for rel in guards:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "D-146 — Track B stops denying the surface it is served on" in text, (
            f"{rel} does not NAME the entry that spent 146"
        )
        assert "D-147 — The census rank stops presenting a loop as an ectodomain" in text, (
            f"{rel} does not NAME the entry that spent 147"
        )
        assert r'\n### D-148" not in' in text, f"{rel} does not bar the next free integer"


def test_the_reserved_row_is_retired_marker_safe_and_147_has_a_row():
    """⚠⚠ MARKER-SAFE, and the reason is two other suites rather than a style preference.

    `tests/test_d144_census_structural_rank.py` and `tests/test_d145_bake_structural_loader.py`
    both locate the D-146 row with `re.search(r"^\\| \\*\\*D-146\\*\\*", …)`, so striking the
    marker to `~~**D-146**~~` — the convention `~~**D-143**~~` uses — would break two guards
    instead of satisfying them. The `D-142` and `D-145` rows record the same trap of themselves.
    """
    assert re.search(r"^\| \*\*D-146\*\*", RESERVED, re.M), (
        "the D-146 row must keep its literal marker; retirement is recorded INSIDE the cell"
    )
    assert "~~**D-146**~~" not in RESERVED, (
        "striking the D-146 marker breaks two other suites' lookups"
    )
    row = next(ln for ln in RESERVED.splitlines() if ln.startswith("| **D-146**"))
    assert "WRITTEN" in row, "the retired row must say it was written"
    assert "Original reservation text" in row, (
        "the original reservation is provenance and is kept, not replaced (D-129-C)"
    )
    assert re.search(r"^\| \*\*D-147\*\*", RESERVED, re.M), (
        "D-147 is cited in order to bar it, so it must be a RESERVED row or the citation "
        "invariant has a hole indistinguishable from D-062's"
    )
    # ⚠⚠ FLIPPED IN PLACE AT `D-147`, NEVER DELETED, AND FOR THE REASON THIS FILE EXISTS TO TEACH.
    # This asserted the pointer read `D-147`, which was true for exactly as long as 147 was
    # unspent. The rule it encodes is *the pointer moves in the SAME commit that spends the
    # integer*, and that rule is what is kept: it now asserts **`D-148`**, and it asserts that 147
    # is no longer the pointer — so a future land that forgets to move it reddens here rather than
    # drifting, which this file has recorded happening three times, once by thirty-six integers.
    # ⚠⚠ FLIPPED IN PLACE AT `D-150`, NEVER DELETED — the fourth time this same assertion has been
    # moved rather than removed, and the RULE it encodes is what is kept: *the pointer moves in the
    # SAME commit that spends the integer*. Only the value moves.
    # ⚠⚠ AND IT MOVES TO **151**, STILL SKIPPING 148. `D-150` spent 150 (the census structure-status
    # honesty surface); 148 is still a HOLD for the trafficking Spec, and a reserved integer is not
    # a free one — that is `RESERVED.md`'s whole purpose. Four assertions where there was one: the
    # pointer names 151, and it names none of 147, 148 or 150, so a future land that forgets to
    # move it reddens here rather than drifting (this file has recorded that drift three times,
    # once by thirty-six integers).
    # ⚠⚠ FLIPPED IN PLACE AT `D-151`, NEVER DELETED — the fifth time this same assertion has
    # been moved rather than removed, and the RULE it encodes is what is kept: *the pointer moves
    # in the SAME commit that spends the integer*. Only the value moves.
    # ⚠⚠ AND IT MOVES TO **152**, STILL SKIPPING 148. `D-151` spent 151 (the owner UI-polish
    # ship: the Initial Targets label, the Kathad DOI anchor and the census layout); 148 is still a
    # HOLD for the trafficking Spec, and a reserved integer is not a free one — that is
    # `RESERVED.md`'s whole purpose. Five assertions where there was one: the pointer names 152,
    # and it names none of 147, 148, 150 or 151, so a future land that forgets to move it reddens
    # here rather than drifting (this file has recorded that drift three times, once by thirty-six
    # integers).
    # ⚠⚠ FLIPPED IN PLACE AT `D-153`, NEVER DELETED — the sixth time this same assertion has been
    # moved rather than removed, and the RULE it encodes is what is kept: *the pointer moves in the
    # SAME commit that spends the integer*. Only the value moves.
    # ⚠⚠ AND IT MOVES TO **154**, SKIPPING **TWO** HOLDS NOW — which is the new part. `D-153` spent
    # 153 (the D-149 burden loader baked into the serving image) and deliberately did NOT take 152:
    # 148 is still a HOLD for the trafficking Spec and 152 became a HOLD for the concurrent
    # sitewide-layout lane. A reserved integer is not a free one — that is `RESERVED.md`'s whole
    # purpose — so *"next free"* means the lowest AVAILABLE integer and not the lowest unwritten
    # one. Six assertions where there was one: the pointer names 154, and it names none of 147,
    # 148, 150, 151, 152 or 153.
    assert "Next free `D-` integer: **`D-158`**" in RESERVED, (
        "the next-free pointer moves in the SAME commit that spends the integer"
    )
    assert "Next free `D-` integer: **`D-153`**" not in RESERVED
    assert "Next free `D-` integer: **`D-154`**" not in RESERVED
    assert "Next free `D-` integer: **`D-155`**" not in RESERVED, (
        "the pointer still names a SPENT integer — D-153 was spent by the burden-loader image "
        "bake, and naming it would hand a used number to the next writer"
    )
    assert "Next free `D-` integer: **`D-152`**" not in RESERVED, (
        "the pointer still names 152, which D-153 converted into a sitewide-layout HOLD — a hold "
        "is not a free integer, and handing it to the next writer is what this file prevents"
    )
    assert "Next free `D-` integer: **`D-151`**" not in RESERVED, (
        "the pointer still names a SPENT integer — D-151 was spent by the owner UI-polish "
        "ship, and naming it would hand a used number to the next writer"
    )
    assert "Next free `D-` integer: **`D-150`**" not in RESERVED, (
        "the pointer still names a SPENT integer — D-150 was spent by the census structure-status "
        "honesty surface, and naming it would hand a used number to the next writer"
    )
    assert "Next free `D-` integer: **`D-148`**" not in RESERVED, (
        "the pointer still names 148, which D-149 converted into a trafficking HOLD — a hold is "
        "not a free integer, and handing it to the next writer is what this file exists to prevent"
    )
    assert "Next free `D-` integer: **`D-147`**" not in RESERVED, (
        "the pointer still names a SPENT integer — it would hand 147 to the next writer"
    )


def test_the_citation_invariant_holds_on_this_branch():
    """⚠ `RESERVED.md`'s own command, run rather than quoted. **Read the output, not an exit
    code**: the only passing result is that nothing new is unresolved. `D-131` (the suffix half of
    `### D-130-B / D-131`) and `F-067` (open in #222) are pre-existing and untouched."""
    # D-156: every id on the heading, so a compound `### D-130-B / D-131` defines BOTH.
    _headings = chr(10).join(l for l in LOG.splitlines() if l.startswith("### "))
    defined = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", _headings))
    reserved = set(re.findall(r"^\| \*\*([DFA]-\d+)\*\*", RESERVED, re.M))
    cited = set(re.findall(r"\b(?:D|F|S|DEP|A)-\d{3}\b", LOG + ARCH))
    # D-156: was ["D-131", "F-067"]. D-131 resolves now the compound heading parses;
    # F-067 is RESERVED rather than dangling. An empty list is the only passing result.
    assert sorted(cited - defined - reserved) == [], (
        f"the citation invariant moved: {sorted(cited - defined - reserved)}"
    )


def test_the_architecture_doc_no_longer_says_the_track_b_order_is_offline():
    """⚠ CLAUDE.md rule 2 — and this file is where the stale reading would have survived, because
    `ARCHITECTURE.md` restates the D-143 sentence in its own words."""
    flat = _flat(ARCH)
    assert "D-146" in flat, "the architecture doc must name the entry that moved the sentence"
    assert ROUTE in flat
    assert "runs **offline**" not in flat, (
        "ARCHITECTURE.md still describes the Track B order as offline"
    )
    assert "review lens" in flat.lower()


def test_the_test_plan_carries_the_d146_addendum_on_an_id_nobody_else_holds():
    """⚠ T-ids have collided four times here. The check is that this addendum's id appears in NO
    other addendum, not merely that a number was chosen."""
    plan = (ROOT / "docs" / "Test_Plan.md").read_text(encoding="utf-8")
    start = plan.index("### D-146 (this PR;")
    nxt = plan.index("## Addendum", start)
    mine, others = plan[start:nxt], plan[:start] + plan[nxt:]
    assert "(this PR; T-1253)" in mine
    assert "| **T-1253** |" in mine, "T-1253 has no row in the D-146 addendum"
    assert "| **T-1253** |" not in others, (
        "T-1253 is claimed by another addendum as well — the collision is not resolved"
    )
    assert "no test here contacts the deployed application" in _flat(mine).lower(), (
        "the addendum must state what these tests cannot establish"
    )


@pytest.mark.parametrize("rel", sorted(D144_SHARED_REGIONS))
def test_d144s_own_region_of_each_shared_file_has_not_moved(rel):
    """⚠⚠ The narrowed half of the whole-file pin above. `app/read_routes.py` and `db/models.py` are
    SHARED files, so what must not move is **D-144's block inside them**, never the whole file.

    ⚠ The expected digest is `2170bd8`'s — D-144's merge commit — so this asserts *"identical to
    what shipped"* rather than *"identical to itself"*. A pin recomputed from the thing it pins is a
    mirror.
    """
    _start, _stops, expected = D144_SHARED_REGIONS[rel]
    assert region_digest(rel) == expected, (
        f"D-144's own region of {rel} changed — D-146 is a copy amendment; an edit inside D-144's "
        f"block belongs to a different entry with its own ruling"
    )


@pytest.mark.parametrize("rel", sorted(D144_SHARED_REGIONS))
def test_the_region_extractor_actually_reaches_a_region(rel):
    """⚠⚠ `A-017` — the fixture must reach the code under test. A region extractor that returned
    `""` would hash the empty string identically forever and this pin would pass on a DELETED
    route, which is the loudest thing it exists to catch."""
    region = extract_region(rel)
    assert region.count("\n") >= D144_REGION_MIN_LINES[rel], (
        f"the extracted D-144 region of {rel} is only {region.count(chr(10))} lines; a pin over a "
        f"near-empty region asserts nothing"
    )
