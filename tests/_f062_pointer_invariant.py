"""The next-free-pointer invariant, as a PURE FUNCTION over two strings.

⚠⚠ WHY THIS MODULE EXISTS. `tests/test_f062_ceiling_climb.py` read `docs/README.md` and
`docs/RESERVED.md` off disk, so the guard could not be made red without editing the repository.
**A guard that cannot be shown to fail has not been shown to bite** — and this one did not: it
pinned the pointer's VALUE (`F-065`) instead of the RULE, so it passed only while nothing happened
and went red the moment `314df71` spent `F-065`/`F-066` and moved the pointer in the same commit,
which is the discipline its own failure message demands.

⚠ This function touches no file and reads no path. Both inputs are strings, so a fixture can state
any pointer/heading combination and the check can be proven to fail on the bad ones.

⚠ `F-` ONLY. The `D-` namespace is deliberately NOT checked: `main`'s `D-` pointer names `D-106`,
which exists on `main`, so extending this would turn `main` red. That pointer's remedy is sequenced
separately and is not this entry's.
"""

from __future__ import annotations

import re

#: ⚠ The message is UNCHANGED from the assertion this replaces. It was always right — it named
#: MOVEMENT, which is the rule. Only the check was wrong, which pinned a value.
MESSAGE = "the next-free pointer must move in the SAME commit that spends F-{spent}"

_SPENT = re.compile(r"^### F-(\d+) ", re.M)
_POINTER = re.compile(r"Next free `F-` integer: `F-(\d+)`")


def spent_headings(log_text: str) -> set[int]:
    """Every `F-` integer that has a written entry."""
    return {int(n) for n in _SPENT.findall(log_text)}


def next_free_pointer(reserved_text: str) -> int:
    """The integer the reservation file advertises as unspent."""
    m = _POINTER.search(reserved_text)
    assert m is not None, "docs/RESERVED.md states no `Next free `F-` integer` pointer at all"
    return int(m.group(1))


def check_next_free_pointer(log_text: str, reserved_text: str) -> int:
    """Assert the pointer names no spent heading and exceeds every one. Returns the pointer.

    ⚠ Raises ``AssertionError`` — the two clauses are asserted separately so a failure names which
    one broke, not merely that something did.
    """
    spent = spent_headings(log_text)
    pointer = next_free_pointer(reserved_text)

    assert pointer not in spent, MESSAGE.format(spent=f"{pointer:03d}") + (
        f" — the pointer names F-{pointer:03d}, which is already a written entry"
    )
    highest = max(spent, default=-1)
    assert pointer > highest, MESSAGE.format(spent=f"{highest:03d}") + (
        f" — the pointer is F-{pointer:03d}, at or below the highest spent F-{highest:03d}"
    )
    return pointer
