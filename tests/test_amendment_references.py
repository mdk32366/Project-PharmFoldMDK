"""The amendment-reference check — the parent invariant cannot see one level down.

⚠⚠ `D-093 amendment 3` is cited in the present tense and does not exist, and the parent citation
invariant reports CLEAN — because `D-093 amendment 3` contains `D-093`, which does exist. **The
checker proves the PARENT and has no access to the AMENDMENT.** `F-044`'s shape, one level down.
"""
from __future__ import annotations

import pathlib

import pytest

from scripts.check_amendment_references import (
    CITE_PATTERNS,
    check,
    cited_amendments,
    defined_amendments,
)


def test_the_house_style_backtick_form_is_matched():
    """⚠⚠ Code's own first pattern missed this and MA1 exists because of it.

    The log writes `` `D-093` amendment 4 `` — backtick between the id and the word. A pattern
    requiring whitespace there misses 9 references in `docs/README.md` alone.
    """
    plain, _ = cited_amendments("D-093 amendment 4 is fine")
    ticked, _ = cited_amendments("`D-093` amendment 4 is fine")
    whole, _ = cited_amendments("`D-093 amendment 4` is fine")
    assert ("D-093", 4) in plain
    assert ("D-093", 4) in ticked, "the backticked form is the DOMINANT form and must match"
    assert ("D-093", 4) in whole


def test_the_and_form_is_matched_because_a_grep_cannot_see_it():
    """⚠ `amendments 2 and 3` cites TWO amendments and contains neither literal string."""
    got, _ = cited_amendments("`D-093` amendments 2 and 3 shipped")
    assert ("D-093", 2) in got and ("D-093", 3) in got


def test_the_abbreviated_form_is_matched():
    got, _ = cited_amendments("`D-093` am. 4 covers it")
    assert ("D-093", 4) in got


def test_a_definition_requires_a_fourth_level_header():
    assert defined_amendments("#### D-093 amendment 4 — title") == {("D-093", 4)}
    # ⚠ a mention in prose is a CITATION, never a definition
    assert defined_amendments("see `D-093` amendment 4") == set()
    # ⚠ and a third-level header is the PARENT entry, not an amendment
    assert defined_amendments("### D-093 — the layer") == set()


# ⚠⚠ MB5 — THE STRUCTURAL GUARD. `F-050` was reserved in prose, the parser matched zero rows, and
# the invariant returned a confident answer about nothing. A parser matching nothing must REFUSE.
def test_the_checker_refuses_rather_than_passing_when_it_parses_nothing(tmp_path):
    empty = tmp_path / "empty.md"
    empty.write_text("nothing here at all\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        check([str(empty)])
    assert "REFUSED" in str(e.value)
    assert "about nothing" in str(e.value)


def test_the_checker_refuses_when_no_corpus_file_exists():
    with pytest.raises(SystemExit) as e:
        check(["does/not/exist.md"])
    assert "REFUSED" in str(e.value)


# ⚠ MA2 — the two forms deliberately NOT resolved, each a category with a cause.
def test_a_template_placeholder_is_not_counted_as_a_citation():
    got, _ = cited_amendments("`D-079` amendment ‹N› — scaffold")
    assert got == set(), "‹N› names no amendment; resolving it would be meaningless"


def test_a_bare_amendment_number_with_no_id_is_not_attributed():
    got, _ = cited_amendments("as amendment 2 records")
    assert got == set(), "guessing the parent from position is the wrong-target defect itself"


def test_every_declared_form_actually_matches_something_it_claims_to():
    """⚠ A pattern that matches nothing is decoration. Each is exercised on its own example."""
    samples = {
        "amendment N": "`D-001` amendment 1",
        "amendments N and M": "`D-001` amendments 1 and 2",
        "am. N": "`D-001` am. 1",
    }
    for name, rx in CITE_PATTERNS:
        assert rx.search(samples[name]), name


#: ⚠⚠ STRICT XFAIL, AND IT IS A SELF-REMOVING MARKER — NOT A SUPPRESSION.
#: The orders were: run red, land `D-093 amendment 3`, run green. **Amendment 3 could not be
#: landed** — the file the orders' sha256 identifies contains `#### D-093 amendment 2`, which is
#: already in the log (9,327 vs 9,328 chars, identical title). The hash MATCHED, so transmission was
#: faithful; the wrong file was attached. Reported, not worked around.
#: ⚠ `strict=True` means that the moment amendment 3 lands, this test XPASSes — and a strict xfail
#: that passes FAILS THE SUITE. The declaration cannot be forgotten or silently outlive the defect;
#: whoever lands amendment 3 is forced to delete this marker.
#: ⚠⚠ The citation is NOT removed to make this green. §5: a citation removed is a finding erased.
@pytest.mark.xfail(
    strict=True,
    reason="D-093 amendment 3 is cited and unwritten. The Planner holds it; the file transmitted "
           "with its hash contained amendment 2 instead. Landing amendment 3 turns this XPASS, "
           "which fails the suite until this marker is removed.")
@pytest.mark.skipif(not pathlib.Path("docs/README.md").exists(), reason="log absent")
def test_the_live_log_resolves_every_amendment_it_cites():
    """⚠⚠ THIS TEST IS THE POINT. It was RED on `D-093 amendment 3` when written, against the real
    tree — no synthetic fixture. It goes green only when the amendment lands."""
    r = check()
    assert r["unresolved"] == [], (
        "amendment references that resolve to nothing: %s. ⚠ Per the orders, a dangling reference "
        "is REPORTED and the Planner writes the entry — it is NEVER fixed by deleting the "
        "citation, because a citation removed is a finding erased." % (r["unresolved"],))
