"""D-143 — Track B ranks structurally, and says so; the retired composite is gone.

The owner Doc's Track B sentence and its D-123 verbatim extract used to end with an
aspirational product of cancer expression, membrane topology, internalization and
antigen density over normal-tissue risk. There is no HPA/assay data behind four of
those terms; filling them with 0.5 neutrals was rejected by the owner (GO 2026-09-08)
because a placeholder multiplied into a score is indistinguishable, in the number that
comes out, from a measurement. The live sentence now describes what is computed.

⚠ **What these tests are NOT about.** The cohort-82 D-041/D-060 learned scorer — the
LOO logistic over six standardized features, its `Rank` column and MethodNote's prose
about it — is a **different ranking surface over a different population**, and D-143
does not touch it. T-1227 pins that carve-out as a property of the tree, so a future
edit that quietly reaches into the scorer while claiming this entry goes red here.

⚠ Failure-reds against the pre-D-143 tree: T-1225's absence assertions and T-1226's
presence assertions both fail on the retired wording, at the assertion rather than on
an import. T-1228 fails on a missing `### D-143` heading — the check is the entry, not
a citation of it (D-062 / method-note item 7).

⚠⚠ **AMENDED BY D-146 (2026-09-09), in one clause and no more.** T-1226 required the Track B
sentence to say *"it runs offline: it is not a ranked surface in this application"*. `D-144` then
put the structural rank in the database and on `GET /api/census-structural-ranking`, `D-145` baked
its loader into the serving image, and the route answers `result_status: valid` — so this file was
**requiring a lie**, in the most dangerous shape available: green, specific, and defending the
error. That clause now requires the live route and the review-lens status and asserts the denial
**absent**; every other D-143 pin above is unchanged, and the retired wording survives exactly once,
inside the Doc's dated amendment note (D-129-C).

Acceptance tests T-1225–T-1228 (docs/Test_Plan.md addendum 2026-09-08); the flipped clause is
T-1253 (addendum 2026-09-09).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
PAPER_PATH = ROOT / "docs" / "pharmfold-adc-nectin4-paper.md"
PAPER = PAPER_PATH.read_text(encoding="utf-8")
ABOUT_PAPER = (ROOT / "ui" / "src" / "aboutPaper.js").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

#: The retired sentence ending, exactly as it read on `main` at `30f402f`.
RETIRED_COMPOSITE = "rank by (cancer × membrane × internalization × density) / normal risk"

#: What replaced it. One constant, so the two files cannot drift apart from each other
#: by a stray character while both still "look right" to a reader.
STRUCTURAL_CLAUSE = "structure only — membrane × ECD × fold confidence (pLDDT)"

#: ⚠⚠ D-146 — the OTHER retired clause, and this one this file used to REQUIRE. It read true when
#: D-143 shipped and stopped being true when `D-144` put the rank on
#: `GET /api/census-structural-ranking` and `D-145` baked its loader into the serving image. Held
#: as one constant for the same reason as the composite: the presence and absence guards must not
#: drift apart by a stray character.
OFFLINE_DENIAL = "it runs offline: it is not a ranked surface in this application"


def _flat(text: str) -> str:
    """Collapse newlines so a wrapped sentence is searchable as one string.

    ⚠ Load-bearing here, not a convenience: the ONE surviving occurrence of the
    retired composite is line-wrapped inside D-123's own entry, and a check that
    only ever looked at single lines could not see it at all.
    """
    return re.sub(r"\s+", " ", text)


# ─────────────── T-1225 — the retired composite is gone, and the one kept copy is named


def test_the_retired_composite_appears_nowhere_in_docs_or_ui_as_a_live_claim():
    """⚠ Enumerated over every file, never spot-checked on the five we remember.

    Flattened, so a re-wrap of the sentence cannot smuggle it back past a
    line-oriented search.
    """
    carriers = []
    for root in (ROOT / "docs", ROOT / "ui" / "src"):
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "node_modules" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if RETIRED_COMPOSITE in _flat(text):
                carriers.append(str(path.relative_to(ROOT)))
    # ⚠ Three files may still hold the words, and each for a stated reason: the log
    # keeps D-123's historical quotation (checked below), and the two UI test files
    # hold it inside `.not.toContain(...)` — an absence guard has to name the string
    # it forbids. Anything else is the live claim coming back.
    assert carriers == [
        "docs/README.md",
        "ui/src/aboutPaper.test.js",
        "ui/src/components/AdcContext.test.jsx",
    ], (
        "the retired Track B composite must survive ONLY as D-123's record and as the "
        f"forbidden string inside the two negative guards; found it in {carriers}"
    )
    for rel in ("ui/src/aboutPaper.test.js", "ui/src/components/AdcContext.test.jsx"):
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
            if RETIRED_COMPOSITE in line:
                assert ".not.toContain(" in line, (
                    f"{rel} names the retired composite outside a negative assertion: "
                    f"{line.strip()[:120]}"
                )


def test_the_one_surviving_copy_is_d123s_record_and_carries_its_supersession():
    """D-129-C — a superseded claim never stands alone, and is never quietly deleted.

    The quotation stays (rewriting history would make the log look like it was
    always right); what it must not do is stand there reading as current.
    """
    flat = _flat(LOG)
    assert flat.count(RETIRED_COMPOSITE) == 1, (
        "exactly one historical quotation is expected — D-123's deep-learning "
        "justification; a second copy is a live claim wearing a citation's clothes"
    )
    where = flat.index(RETIRED_COMPOSITE)
    window = flat[where: where + 2000]
    assert "AMENDED BY `D-143`" in window, "the quotation must name its supersession"
    assert "RETIRED as a description of what we rank by" in window
    assert STRUCTURAL_CLAUSE in window or "membrane × ECD × fold confidence (pLDDT)" in window
    # ⚠ And the amendment note must not itself re-assert the composite as current.
    assert "0.5 neutrals" in window


def test_no_live_file_names_the_composite_terms_as_what_is_ranked():
    """The absence above is about one sentence; this is about the claim shape.

    A file may still *name* cancer/normal/internalization/density — the new sentence
    does, as exclusions, and so does the "later GO" clause. What may not survive is
    "rank by" or "ranked by" immediately followed by that product.
    """
    for path in (PAPER_PATH, ROOT / "ui" / "src" / "aboutPaper.js"):
        flat = _flat(path.read_text(encoding="utf-8"))
        assert not re.search(r"rank(ed)? by \((cancer|membrane)", flat), path.name
        assert "/ normal risk" not in flat, path.name


# ─────────────── T-1226 — what the sentence says now, in both files, identically


def test_the_paper_and_the_extract_carry_the_same_structural_sentence():
    """D-123 dec 4 — the extract is a character substring of the Doc, not a paraphrase.

    ⚠ Asserted on the Doc as the source: the Doc is edited first and the module
    follows. A module edited alone passes a reader's eye and fails here.
    """
    assert STRUCTURAL_CLAUSE in PAPER
    assert STRUCTURAL_CLAUSE in ABOUT_PAPER
    match = re.search(r"export const TRACK_B =\s*\n\s*'(.+)'\n", ABOUT_PAPER)
    assert match, "TRACK_B must stay a single-quoted one-line literal"
    track_b = match.group(1)
    assert track_b in PAPER, (
        "TRACK_B is not a substring of the owner Doc — the extract has drifted, "
        "which is exactly what D-123's substring discipline exists to catch"
    )


def test_the_sentence_names_its_exclusions_rather_than_defaulting_them():
    """⚠ The point of the entry. Dropping the four terms silently would read honest.

    So the sentence must carry: the exclusion, the refused placeholder, the
    not-readiness, the scope, and the later GO. Each is a separate assertion, so a
    partial rewrite names which clause it dropped.
    """
    match = re.search(r"export const TRACK_B =\s*\n\s*'(.+)'\n", ABOUT_PAPER)
    assert match
    track_b = match.group(1)
    for clause, why in (
        ("Cancer vs normal, internalization and antigen density are **excluded**",
         "the excluded terms must be named, not omitted"),
        ("not filled in as 0.5 neutrals",
         "the refused placeholder must be named — this is the decision, not a detail"),
        ("explicitly **not** ADC readiness",
         "a structural order is not a readiness verdict, and says so itself"),
        ("not a shortlist", "nor a shortlist"),
        ("whole census of outward-facing spans (3,467 rows), not one tranche",
         "the scope must be stated: the full census, not the tranche-5 slice"),
        # ⚠⚠ FLIPPED BY D-146 (owner GO 2026-09-09), and this is the one clause of T-1226 that
        # moved. It required *"it runs offline: it is not a ranked surface in this application"* —
        # a required-string assertion that had become a REQUIRED LIE. `D-144` put the rank in the
        # database and on `GET /api/census-structural-ranking` and `D-145` baked its loader into
        # the serving image; the route answers `result_status: valid` over 3,467 rows. So the
        # clause now requires the live route and the review-lens status, and the denial is
        # asserted ABSENT below. ⚠ **D-079 dec 1 is still not widened by a copy change** — it was
        # narrowed by `D-144` in the log, where a bar belongs, and the copy follows the log.
        ("served live by this application** at /api/census-structural-ranking",
         "the route that serves the order must be named, not denied"),
        ("review lens** — an export for reading, never the source of truth",
         "the spreadsheet's status is D-144's ruling and must travel with the route"),
        ("**Later, on its own GO:**", "the biology composite must stay a later GO"),
        ("real HPA/TCGA expression plus wet assays",
         "what would have to exist before the composite is computed"),
    ):
        assert clause in track_b, why
    # ⚠⚠ D-146 — the absence, asserted BESIDE the presences above rather than in a file of its
    # own. A pure absence guard passes on an empty string; a pure presence guard passes with the
    # denial still sitting one clause away from the route it denies. Both directions or neither.
    assert OFFLINE_DENIAL not in track_b, (
        "the retired offline denial is back in TRACK_B — the rank is served at "
        "/api/census-structural-ranking, so the clause is false (D-146)"
    )
    assert OFFLINE_DENIAL not in _flat(PAPER[PAPER.index("**Track B —"):]).split("*⚠ Amended")[0], (
        "the retired offline denial is back in the Doc's Track B sentence; it may survive ONLY "
        "as the dated quotation inside the amendment note (D-129-C)"
    )
    # Track A is untouched by this entry, and the Doc still holds its red-without-bind.
    assert "Wet binding assays — required" in PAPER and "No bind → stop" in PAPER


def test_the_paper_records_the_amendment_instead_of_silently_swapping_the_line():
    """An owner Doc sentence changed; the Doc says so, dated, with the id."""
    flat = _flat(PAPER)
    assert "Amended 2026-09-08 (owner GO; logged as **D-143**" in flat
    assert "was the **aspiration**, not the computation" in flat
    assert "0.5 neutrals" in flat


# ─────────────── T-1227 — the cohort-82 scorer carve-out, as a property of the tree


def test_the_cohort_82_learned_scorer_is_untouched_by_this_entry():
    """⚠⚠ The hard stop that defines D-143, checked against files rather than intent.

    Two different ranking surfaces exist in this project and D-143 edits copy about
    one of them. So: the scorer's own surfaces must still say what they always said,
    and none of them may pick up this entry's structural sentence.
    """
    scorer = (ROOT / "core" / "scorer.py").read_text(encoding="utf-8")
    assert "logistic" in scorer.lower()
    assert "D-143" not in scorer, "core/scorer.py must not name a copy decision"

    method = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(encoding="utf-8")
    assert "a learned scorer over structure-derived features ranks the cohort" in method, (
        "MethodNote's description of the D-041/D-060 scorer is explicitly out of scope"
    )

    target_list = (ROOT / "ui" / "src" / "components" / "TargetList.jsx").read_text(encoding="utf-8")
    # ⚠ D-155 gave this column a `className` when the merge shrank it to the width of the integer
    # it holds (the cause moved to the Status cell). The claim here is about D-143's scope — the
    # cohort's learned ranking is untouched by a Track B entry — so it asserts the COLUMN, not the
    # object literal that happened to declare it in 2026-09.
    assert "{ key: 'rank', label: 'Rank'" in target_list, "the Rank column stays"

    # ⚠ The structural sentence belongs to ONE surface. If it appears on a scorer
    # surface, the two rankings have been merged in the copy — the exact confusion
    # this entry exists to end.
    for rel in (
        "ui/src/components/MethodNote.jsx",
        "ui/src/components/TargetList.jsx",
        "ui/src/components/ScorerView.jsx",
        "ui/src/components/TargetScorerPanel.jsx",
        "ui/src/targetScore.js",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert STRUCTURAL_CLAUSE not in text, f"{rel} must not carry the Track B sentence"


def test_this_entry_ships_no_code_path_and_no_artefact():
    """Copy only. No score is computed anywhere by this change.

    ⚠ Not a ``git diff`` check (the gate checks out a shallow merge ref, where such a
    check passes by erroring — D-139's note). These are properties of the tree.
    """
    for rel in ("core/scorer.py", "scripts/fit_scorer.py", "app/read_routes.py",
                "core/structural_profile.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "D-143" not in text, f"{rel} names D-143 — this is a copy entry"
    # No structural_score product is implemented in-tree by this entry: the offline
    # order lives outside this repository and the entry says so rather than implying
    # a script exists.
    assert not (ROOT / "scripts" / "rank_census_structural.py").exists()


# ─────────────── T-1228 — the log leads it, and the id guards were widened by adding


def _d143_entry() -> str:
    """The D-143 entry only, bounded by the NEXT `### ` heading whatever it is."""
    start = LOG.index("\n### D-143 —") + 1
    nxt = re.search(r"^### (?!D-143\b)", LOG[start + 1:], re.M)
    return LOG[start: start + 1 + nxt.start()] if nxt else LOG[start:]


def test_the_log_entry_exists_exactly_once_and_leads_the_log():
    """⚠ The check is the `### D-143` HEADING, never a citation of it (D-062 / item 7)."""
    assert re.search(r"^### D-143 — Track B stops claiming a composite", LOG, re.M)
    assert len(re.findall(r"^### D-143 —", LOG, re.M)) == 1, "exactly one D-143 entry"
    assert LOG.index("### D-143 —") < LOG.index("### D-141 —"), "newest first"
    # ⚠⚠ 144 IS NOW WRITTEN, AND THIS BAR REDDENED EXACTLY AS IT SAID IT WOULD. The census
    # STRUCTURAL rank (`D-144`) is the DB/API half of the same structural-only ruling this copy
    # entry describes; its GO assigned it 144 while 142 and 143 were both unwritten. The bar is
    # REPLACED BY A NAME — never deleted — and `### D-145` takes the next-free bar. Never a `>=`.
    assert re.search(r"^### D-144 — The offline census ranking stops being a spreadsheet",
                     LOG, re.M), (
        "D-144 is the recorded successor id; it must be the census structural-rank entry, "
        "not some other entry that took the number"
    )
    # ⚠⚠ 145 IS NOW WRITTEN, AND THIS BAR REDDENED EXACTLY AS ITS PREDECESSOR DID ONE INTEGER
    # AGO. D-145 bakes D-144's structural-rank loader into the Fly serving image as one explicit
    # `COPY` — image permanence for the DB/API half of the same structural-only ruling this copy
    # entry describes, and it changes **no sentence on any surface**. The bar is REPLACED BY A
    # NAME — never deleted — and `### D-146` takes the next-free bar. Never a `>=`.
    assert re.search(r"^### D-145 — The D-144 loader stops living on the production host",
                     LOG, re.M), (
        "D-145 is the recorded successor id; it must be the image-permanence entry, not some "
        "other entry that took the number"
    )
    # ⚠⚠ 146 IS NOW WRITTEN, AND IT IS THIS ENTRY'S OWN SENTENCE THAT MOVED. D-146 retires the
    # Track B clause D-143 shipped — *"it runs offline: it is not a ranked surface in this
    # application"* — because D-144 put the rank on `GET /api/census-structural-ranking` and
    # D-145 baked its loader into the image, so the clause stopped being true. ⚠ **D-143 is NOT
    # amended away by that:** everything else this file pins is unchanged, and the one flipped
    # clause is flipped IN PLACE below (T-1226) rather than deleted. The bar is REPLACED BY A
    # NAME — never deleted — and `### D-147` takes the next-free bar. Never a `>=`.
    assert re.search(r"^### D-146 — Track B stops denying the surface it is served on",
                     LOG, re.M), (
        "D-146 is the recorded successor id; it must be the Track B live-route copy entry, "
        "not some other entry that took the number"
    )
    # ⚠⚠ 147 IS NOW WRITTEN, AND THIS BAR REDDENED EXACTLY AS THE THREE ABOVE IT DID. D-147 adds
    # the `ecd_intermittent` disclosure to the census structural ranking rows — a serve-time join
    # against the committed `span_segments.csv`, changing **no score, no formula, no loader and no
    # sentence this suite pins**, and it takes nothing back from this entry's structural-only
    # framing: the flag is a category on a row, not a fourth factor. The bar is REPLACED BY A
    # NAME — never deleted — and `### D-148` takes the next-free bar. Never a `>=`.
    assert re.search(r"^### D-147 — The census rank stops presenting a loop as an ectodomain",
                     LOG, re.M), (
        "D-147 is the recorded successor id; it must be the census `ecd_intermittent` entry, "
        "not some other entry that took the number"
    )
    assert "\n### D-148" not in LOG, "D-148 is the next free integer"


def test_the_entry_carries_the_cohort_82_hard_stop_and_the_go_that_authorised_it():
    """The carve-out is stated in the entry, not only honoured in the diff."""
    lowered = _flat(_d143_entry()).lower()
    for claim, why in (
        ("d-041", "the learned scorer's own ids must be named as out of scope"),
        ("d-060", "the pre-registered evaluation is out of scope too"),
        ("cohort-82", "the population that is NOT being talked about"),
        ("rank** column", "the /targets Rank column is named as untouched"),
        ("methodnote", "MethodNote's scorer prose is named as untouched"),
        ("owner go **2026-09-08**", "the GO and its date"),
        ("matt", "the GO's owner is named"),
        ("0.5 neutral", "the rejected placeholder is named"),
        ("membrane × ecd × fold confidence (plddt)", "what is ranked instead"),
        ("full census (3467), not t5-only", "the scope the GO fixed"),
    ):
        assert claim in lowered, why


def test_the_entry_carries_a_deep_learning_justification_that_survives_the_cut():
    """CLAUDE.md prime directive — and the honest version of it here.

    Cutting terms out of a product does not remove the network; it leaves the
    ESMFold confidence carrying MORE of the surviving order. The entry has to say
    that, and must not claim the network answered a question about tumour biology.
    """
    lowered = _flat(_d143_entry()).replace("**", "").lower()
    assert "#### deep-learning justification" in lowered
    assert "esmfold" in lowered and "d-003" in lowered
    assert "one of three" in lowered, "the surviving weight of the pLDDT term"
    assert "not satisfied by multiplying guesses" in lowered
    assert "calling it adc readiness would be claiming" in lowered


def test_the_entry_names_the_artefact_behind_every_claim_including_the_missing_one():
    """D-016 — and the disqualifying half is the point.

    The 0.5-neutral history and the offline-rank scope have exactly one artefact:
    the GO. No run log, CSV or notebook for that order is in this repository, and
    the entry must say so rather than let a reader assume a measured provenance.
    """
    entry = _flat(_d143_entry())
    lowered = entry.lower()
    assert "#### provenance (d-016)" in lowered
    assert "no run log, csv or notebook" in lowered, (
        "the absent artefact must be named — an entry that only lists what it has "
        "is the summary-instead-of-records defect this log records twice"
    )
    assert "census_manifest.v6.provenance.json" in entry and '"manifest_rows": 3467' in entry
    assert "censussummary.js" in lowered and "manifestrows: 3467" in lowered
    assert "30f402f" in entry, "the tip the id was claimed against"
    assert "gh pr list --state open" in lowered, "the id was checked, not assumed"
    assert "cannot prove no unpublished one did" in lowered, (
        "the open-PR check's known weakness travels with the claim (D-141's finding)"
    )


def test_d123_points_forward_at_this_entry():
    """A reader who lands on D-123 must be told its Track B line moved."""
    start = LOG.index("### D-123 —")
    entry = _flat(LOG[start: start + 12000])
    assert "**Amended by:**" in entry
    amended_by = entry.split("**Amended by:**", 1)[1][:600]
    assert "D-143" in amended_by, "D-123 must name D-143 as an amender"


def test_d142_is_registered_as_held_rather_than_left_as_an_unresolved_citation():
    """⚠ This entry CITES 142 as skipped, and a citation with no entry is the D-062 defect.

    `docs/RESERVED.md` is the only whitelist the citation check honours, so the skipped
    integer belongs there — with the ruling that caused it and the fact that nothing in
    the tree spends it.
    """
    reserved = (ROOT / "docs" / "RESERVED.md").read_text(encoding="utf-8")
    assert re.search(r"^\| \*\*D-142\*\* \|", reserved, re.M), (
        "D-142 is cited by this entry as held; the citation invariant requires it to be "
        "listed in docs/RESERVED.md, which the checker whitelists and nothing else"
    )
    row = _flat(reserved[reserved.index("| **D-142** |"):][:6000])
    assert "renumbered to `D-143` by owner instruction (2026-09-09)" in row
    assert "nothing visible in the tree spends 142" in row.lower()
    assert "266" in row, "the PR that took the id first is named"
    # ⚠ Amended once the holder was named. Both readings must survive: the named holder
    # AND the fact that the holder's published PR does not actually take 142 (D-129-C —
    # a superseded claim never stands alone; D-016 — prefer the disqualifying query).
    assert "bc-14347bf7" in row, "the holder Trinity named must be recorded"
    assert "not found or not accessible" in row, (
        "the row must say the agent's own record could NOT be read from here — "
        "the pairing is Trinity's word, not a discovery"
    )
    assert "267" in row, "the holder's published PR must be named"
    assert "143 is claimed twice" in row.lower()


def test_the_entry_reports_the_live_143_collision_instead_of_merging_over_it():
    """⚠⚠ Two open PRs write `### D-143`, and an entry that stayed quiet about that would
    be the D-062 shape again: a record that reads settled while the tree is not.

    ⚠ The resolution is NOT taken here. This ship keeps the id Trinity instructed and
    escalates; whichever merges second reddens by design, and the fix is a rebase that
    ADDS the surviving ids.
    """
    entry = _flat(_d143_entry())
    lowered = entry.lower()
    assert "143 is now claimed twice" in lowered
    assert "267" in entry, "the colliding PR must be named by number"
    assert "cursor/d-142-targets-cancer-description-columns-d08d" in entry, (
        "the colliding branch is named — its NAME says 142 while its diff says 143, "
        "which is the whole point"
    )
    assert "gh pr diff 267" in entry, "checked in the diff, not inferred from the title"
    assert "bc-14347bf7" in entry
    assert "not found or not accessible" in lowered, (
        "the unreadable agent record must be disclosed, not smoothed over"
    )
    assert "nothing unilateral" in lowered, "this ship must not resolve it by guessing"
    assert "never a `>=`" in entry or "never a >=" in lowered
    # ⚠ And the resolution is recorded BESIDE the pre-merge reading, not instead of it
    # (D-129-C). #266 merged first, so 143 is spent here and 142 is still free.
    assert "resolved by merge order" in lowered
    assert "f243f93" in entry, "the merge commit that settled the id must be named"
    assert "did not win an argument; it merged first" in lowered, (
        "merge order is not an argument, and the entry must not read as though it were"
    )
    assert "142 is free" in lowered
    # ⚠⚠ WIDENED BY ADDING AT D-142. This asserted that the D-143 entry presents 142 as HELD,
    # "never as a spent authority" — correct while 142 was unspent, and this entry's own text
    # said what would end it: *"142 is free"* for the holder to take. The holder took it, so the
    # requirement is now **held OR spent-by-a-real-heading**: the citation must still resolve, and
    # what it may never be is a spent authority with NO entry — the D-062 defect this file is
    # built around. ⚠ The held phrasing is left in the D-143 entry untouched (D-129-C), so on
    # `main` alone this still matches the first branch.
    entry = _flat(_d143_entry())
    held = "`D-142` is skipped by owner ruling — held, not free" in entry
    spent = bool(re.search(r"^### D-142 — ", LOG, re.M))
    assert held or spent, (
        "the D-143 entry cites 142; that citation must resolve either to a recorded HOLD or to "
        "a real `### D-142` heading — a citation resolving to neither is D-062"
    )
    assert "RESERVED.md" in entry


def test_every_enumerated_id_guard_keeps_the_bar_on_142():
    """⚠ Widened by ADDING. A skipped integer stays BARRED until an entry NAMES it.

    Enumerated over the six guard files rather than spot-checked, so a guard that drops
    the bar while renumbering is caught here instead of by the next collision.

    ⚠⚠ The name is kept for continuity, and it is now half the story: as of `### D-142`
    the requirement is **bar or name**, never neither. Renaming the test would break the
    thread back to the collision it was written for.
    """
    guards = (
        "tests/test_d129_phase5_named_refuse_spec.py",
        "tests/test_d130_residual_rmsd_spec.py",
        "tests/test_d136_cancer_type.py",
        "tests/test_d139_served_path_flip.py",
        "tests/test_d140_pipeline_programme.py",
        "tests/test_d141_land_confidence_kabsch.py",
    )
    for rel in guards:
        text = (ROOT / rel).read_text(encoding="utf-8")
        # ⚠⚠ WIDENED BY ADDING AT D-142 — and the widening is the one THIS TEST'S OWN failure
        # message pre-committed: *"if a holder writes it, this reddens BY DESIGN and 142 is ADDED
        # beside 143 — never relaxed to a `>=`."* The holder wrote it, so the requirement is now
        # **bar OR name**: while 142 is unspent every guard must bar it; once an entry spends it
        # every guard must assert THAT ENTRY by heading. ⚠ The third state stays forbidden — 142
        # neither barred nor named — because an integer that is silently free is how a collision
        # gets in, and that is exactly what happened between #266 and #267.
        barred = '### D-142" not in' in text
        named = "D-142 — `/targets` gains a Cancer association" in text
        assert barred or named, (
            f"{rel} neither bars the held 142 nor names the entry that spends it"
        )
        assert not (barred and named), (
            f"{rel} both bars 142 and names an entry for it; both cannot be true"
        )
        # ⚠⚠ WIDENED THE SAME WAY AT D-144, and by the same rule this test already carries:
        # **bar OR name, never neither.** 144 was the next free integer when this test was
        # written and is now spent by the census structural-rank entry, so a guard must either
        # bar it (while unspent) or name the entry that took it (once spent) — and the next free
        # integer, 145, takes the bar. The third state stays forbidden.
        barred_144 = '### D-144" not in' in text
        named_144 = "D-144 — The offline census ranking stops being a spreadsheet" in text
        assert barred_144 or named_144, (
            f"{rel} neither bars 144 nor names the entry that spends it"
        )
        assert not (barred_144 and named_144), (
            f"{rel} both bars 144 and names an entry for it; both cannot be true"
        )
        # ⚠⚠ WIDENED THE SAME WAY AT D-145, by the same **bar OR name, never neither** rule this
        # test already carries — and this is the second RESERVED integer to be spent rather than
        # skipped, so it exercises exactly the path 142 pre-committed. 145 was the next free
        # integer when D-144 landed and is now spent by the image-permanence entry, so a guard
        # must either bar it (while unspent) or name the entry that took it (once spent). The
        # next free integer, 146, takes the bar. The third state stays forbidden.
        barred_145 = '### D-145" not in' in text
        named_145 = "D-145 — The D-144 loader stops living on the production host" in text
        assert barred_145 or named_145, (
            f"{rel} neither bars 145 nor names the entry that spends it"
        )
        assert not (barred_145 and named_145), (
            f"{rel} both bars 145 and names an entry for it; both cannot be true"
        )
        # ⚠⚠ WIDENED THE SAME WAY AT D-146, by the same **bar OR name, never neither** rule —
        # the THIRD reserved integer spent rather than skipped, and the one that retires this
        # entry's own offline clause. 146 was the next free integer when D-145 landed and is now
        # spent by the Track B live-route copy entry, so a guard must either bar it (while
        # unspent) or name the entry that took it (once spent). The next free integer, 147, takes
        # the bar. The third state stays forbidden.
        barred_146 = '### D-146" not in' in text
        named_146 = "D-146 — Track B stops denying the surface it is served on" in text
        assert barred_146 or named_146, (
            f"{rel} neither bars 146 nor names the entry that spends it"
        )
        assert not (barred_146 and named_146), (
            f"{rel} both bars 146 and names an entry for it; both cannot be true"
        )
        # ⚠⚠ WIDENED THE SAME WAY AT D-147, and this is the pass where the pattern this check
        # holds as *data* had to move with it. 147 was the next free integer while D-146 was the
        # tip; it is now spent by the census `ecd_intermittent` disclosure — a serve-time join on
        # the ranking rows that changes **no score, no formula and no loader** — so demanding that
        # every guard go on barring it would be demanding they defend a written integer. Bar OR
        # name, never neither; the next free integer, 148, takes the bar.
        barred_147 = '### D-147" not in' in text
        named_147 = "D-147 — The census rank stops presenting a loop as an ectodomain" in text
        assert barred_147 or named_147, (
            f"{rel} neither bars 147 nor names the entry that spends it"
        )
        assert not (barred_147 and named_147), (
            f"{rel} both bars 147 and names an entry for it; both cannot be true"
        )
        assert '### D-148" not in' in text, f"{rel} does not bar the next free integer"
        assert "D-143 — Track B stops claiming a composite" in text, (
            f"{rel} must name 143 by its heading, not by a `>=`"
        )
        # ⚠ The bar on 142 must be EXPLAINED where it sits. An unexplained absence
        # assertion is the thing a later session deletes because it looks like a typo.
        # ⚠ A first draft of this check asserted `">=" not in …` nearby, which fired on
        # every guard's own *"never relaxed to a `>=`"* prose — a guard reporting its
        # own good news. Replaced with the claim that actually matters.
        # ⚠ Widened the same way: while barred a guard must say WHY; once spent it must say the
        # reserved integer was spent and by whom. Either way it EXPLAINS itself — an unexplained
        # assertion about an integer is what a later session deletes for looking like a typo.
        assert ("142 is SKIPPED, NOT FREE" in text or "142 is HELD" in text
                or "142 IS NOW WRITTEN" in text), (
            f"{rel} asserts something about 142 without saying why"
        )


# ─────────────── T-1229 — the /method rail suite stops racing the copy it measures


def test_the_method_toc_suite_waits_for_the_async_coverage_beat():
    """⚠⚠ The gate's red on this PR, and it was a RACE rather than a copy change.

    `MethodNote.toc.test.jsx` awaited only `method-toc` — which renders from the static
    headings on the first paint — then asserted synchronously on copy that arrives with
    `getCoverage()`. Two gate runs on byte-identical test and component code disagreed.
    The fix waits for the async beat; it does NOT relax the assertion to the pre-fetch
    fallback, which would pin the page's loading state as its contract.
    """
    toc = (ROOT / "ui" / "src" / "components" / "MethodNote.toc.test.jsx").read_text(encoding="utf-8")
    helper = toc[toc.index("async function renderMethod()"):]
    helper = helper[: helper.index("return view")]
    assert helper.count("await waitFor(") == 2, (
        "the helper must wait for the async coverage beat as well as the rail landmark"
    )
    assert "folds a fixed cohort of 7 candidate" in helper, (
        "the second wait must be on a coverage-DERIVED string, so it settles the same "
        "state the prose assertions read"
    )
    # ⚠ The contract itself is unchanged and still asserted where it always was.
    assert "expect(body).toMatch(/3 ranked-and-folded of 7/)" in toc, (
        "the derived-numbers assertion is the contract (D-050) and must not be weakened "
        "to the pre-fetch fallback copy"
    )
    # ⚠ And the race is now a deterministic test, not a comment: the promise is held open
    # so both states are asserted in order.
    assert "carries the fallback coverage line until getCoverage resolves" in toc
    assert "getCoverage.mockReturnValue(new Promise(" in toc


def test_the_architecture_doc_describes_the_extract_as_structural_only():
    """ARCHITECTURE.md is brought current in the same PR (CLAUDE.md rule 2)."""
    flat = _flat(ARCH)
    assert "aboutPaper.js" in flat
    assert "D-143" in flat
    assert RETIRED_COMPOSITE not in flat
    assert "structural" in flat.lower()
