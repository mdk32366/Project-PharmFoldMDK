"""Every numbering namespace that carries written entries is registered and invariant-shaped.

⚠ Companion to `tests/test_f062_ceiling_climb.py`, which guards `F-` alone. This one DISCOVERS the
namespaces, so a namespace added tomorrow is covered without anyone remembering to add it.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from namespace_invariant import HEADING, check, discover  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"

#: ⚠ Three registers, three files. A check reading only `README.md` is blind to `A-` and `P-` —
#: which is exactly the blind spot that hid four unregistered namespaces until 2026-09-04.
REGISTERS = {
    "log": DOCS / "README.md",
    "test_plan": DOCS / "Test_Plan.md",
    "papers": DOCS / "PAPERS-v2.md",
}

#: ⚠⚠ NARROW, STATED, JUSTIFIED — `Test_Plan.md`'s own rule for exemptions.
EXEMPT = {
    "A": (
        "A- is NOT a spend-once identifier. docs/RESERVED.md records that the "
        "`A-0NN (descriptive name)` convention was invented for numbers that MOVE, so "
        "'the pointer exceeds every spent integer' is the wrong rule for it. Guarding it "
        "would assert a property A- does not have. ⚠ Revisit if A- ever gains an entry register."
    ),
}


def _text() -> dict[str, str]:
    return {k: p.read_text(encoding="utf-8") for k, p in REGISTERS.items()}


# ── fixtures over strings: each state stated exactly, each failure shown to bite ──

GOOD_LOG = "### S-001 a\n### S-002 b\n"
GOOD_RES = "Next free `S-` integer: `S-003`"


def test_a_namespace_with_entries_and_no_pointer_is_rejected():
    """⚠ CLAUSE 1. The quiet failure: nothing measures it, so it cannot be shown wrong."""
    with pytest.raises(AssertionError) as exc:
        check({"r": GOOD_LOG}, "Next free `F-` integer: `F-067`")
    assert "NO next-free pointer" in str(exc.value)
    assert "cannot be shown to be wrong" in str(exc.value)


def test_a_pointer_naming_a_spent_heading_is_rejected():
    """⚠ CLAUSE 2a."""
    with pytest.raises(AssertionError) as exc:
        check({"r": GOOD_LOG}, "Next free `S-` integer: `S-002`")
    assert "already a written entry" in str(exc.value)


def test_a_pointer_below_the_highest_spent_is_rejected():
    """⚠ CLAUSE 2b. ⚠ The pointer here is UNSPENT — a spent one would trip clause 2a instead and
    prove only one of the two. That distinction cost a fixture rewrite under F-062 amendment 1."""
    with pytest.raises(AssertionError) as exc:
        check({"r": "### S-001 a\n### S-003 c\n"}, "Next free `S-` integer: `S-002`")
    assert "at or below the highest spent" in str(exc.value)
    assert "already a written entry" not in str(exc.value)


def test_a_correct_register_passes():
    assert check({"r": GOOD_LOG}, GOOD_RES) == {"S": 3}


def test_an_exemption_without_a_stated_reason_is_refused():
    """⚠ An exemption list is a hard-coded list wearing a different hat unless it carries reasons."""
    with pytest.raises(AssertionError) as exc:
        check({"r": GOOD_LOG}, "", exempt={"S": "   "})
    assert "no stated reason" in str(exc.value)


def test_a_decorated_heading_is_still_discovered():
    """⚠⚠ REGRESSION GUARD, and it is here because the first draft of this module failed it.

    `docs/PAPERS-v2.md` writes `## ⟡ P-003 — …`. A pattern anchoring the identifier immediately
    after the hashes silently under-reports and the guard still PASSES — it reported P-003 and
    P-004 as gaps that do not exist. ⚠ A discovery bug does not announce itself.
    """
    found = discover({"r": "## ⟡ P-003 — decorated\n## P-005 — plain\n"})
    assert found == {"P": {3, 5}}
    assert HEADING.search("## ⟡ P-003 — decorated") is not None


# ── the tree itself, through the same functions the fixtures proved ──

@pytest.mark.xfail(
    strict=True,
    reason=(
        "⚠⚠ EXPECTED RED, and it is the point. Measured 2026-09-04 on main: the D- pointer "
        "names D-110 while ### D-110 is written, and DEP-, P- and S- carry entries with no "
        "next-free pointer at all. Creating a register is a DECISION and is the owner's; "
        "Code will not invent one. ⚠ strict=True means this test FAILS the moment the "
        "registers are corrected — the xfail cannot outlive its reason, which is how the "
        "F- guard's narrow scope survived past the blocker that justified it."
    ),
)
def test_every_namespace_in_this_repository_is_registered_and_invariant_shaped():
    checked = check(_text(), (DOCS / "RESERVED.md").read_text(encoding="utf-8"), exempt=EXEMPT)
    assert checked, "no namespace was checked — discovery found nothing, which is itself a defect"
