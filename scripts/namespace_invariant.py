"""Every numbering namespace with written entries is registered, and its pointer is invariant-shaped.

⚠⚠ WHY THIS EXISTS. `tests/test_f062_ceiling_climb.py` guards the SAME rule for `F-` alone. On
2026-09-04 `main`'s `D-` pointer named `D-110` while `### D-110`, `### D-111` and `### D-112` all
existed — both clauses violated — and the `F-` guard was GREEN throughout, because it parses `F-`.
⚠ **A guard green over a broken rule is `F-047`'s shape inside the instrument built to prevent it.**

⚠ **DISCOVERY, NEVER A LIST.** Namespaces are found in the registers. A hard-coded list leaves the
next namespace unguarded exactly as `D-` was — silently, while passing.

⚠ **PURE FUNCTIONS OVER STRINGS.** No paths, no I/O. `F-062 amendment 1`'s lesson: a guard that
reads the repository's own files cannot be made red on demand, which is why that defect survived.

⚠⚠ **THE DECORATOR TRAP, recorded because it bit the first draft of this file.** `docs/PAPERS-v2.md`
writes `## ⟡ P-003 — …`. A regex anchoring the identifier immediately after the hashes reports
P-003 and P-004 as GAPS THAT DO NOT EXIST. ⚠ **A discovery bug does not fail loudly; it under-reports
and the guard still passes.** The pattern below skips leading non-alphanumerics deliberately.
"""

from __future__ import annotations

import re

#: ⚠ `[^A-Za-z0-9]*` is the decorator tolerance. Do not tighten it without a fixture.
HEADING = re.compile(r"^#{2,4}[^A-Za-z0-9\n]*([A-Z]{1,4})-(\d+)\b", re.M)

MESSAGE = "the next-free pointer must move in the SAME commit that spends {ns}-{n:03d}"


def pointer_pattern(ns: str) -> re.Pattern[str]:
    return re.compile(rf"Next free `{ns}-` integer: `{ns}-(\d+)`")


def discover(registers: dict[str, str]) -> dict[str, set[int]]:
    """Every namespace carrying at least one written entry, across every register given."""
    found: dict[str, set[int]] = {}
    for text in registers.values():
        for ns, n in HEADING.findall(text):
            found.setdefault(ns, set()).add(int(n))
    return found


def check(registers: dict[str, str], reserved: str,
          exempt: dict[str, str] | None = None) -> dict[str, int]:
    """Assert every discovered namespace is registered and its pointer is invariant-shaped.

    ``exempt`` maps a namespace to the REASON it is not a spend-once identifier. ⚠ An exemption
    without a stated reason is refused — `Test_Plan.md`: *exemptions must be narrow, stated, and
    justified in the test.*
    """
    exempt = exempt or {}
    for ns, reason in exempt.items():
        assert reason.strip(), f"{ns}- is exempted with no stated reason. State one or guard it."

    violations: list[str] = []
    checked: dict[str, int] = {}
    for ns, spent in sorted(discover(registers).items()):
        if ns in exempt:
            continue
        m = pointer_pattern(ns).search(reserved)
        # CLAUSE 1 — a namespace with entries and no pointer cannot go stale, because nothing
        # measures it. That is quieter than a wrong pointer and is not better.
        if m is None:
            violations.append(
                f"{ns}-: {len(spent)} written entries ({ns}-{min(spent):03d}..{ns}-{max(spent):03d}) "
                f"and NO next-free pointer in the register. An untracked namespace cannot be shown "
                f"to be wrong. [clause 1]"
            )
            continue
        ptr, highest = int(m.group(1)), max(spent)
        # CLAUSE 2 — the rule is about MOVEMENT. Pinning a value re-arms the trap for whoever
        # spends the next integer; that is the defect F-062 amendment 1 records.
        if ptr in spent:
            violations.append(
                MESSAGE.format(ns=ns, n=ptr)
                + f" — it names {ns}-{ptr:03d}, which is already a written entry [clause 2a]"
            )
        elif ptr <= highest:
            violations.append(
                MESSAGE.format(ns=ns, n=highest)
                + f" — it is {ns}-{ptr:03d}, at or below the highest spent {ns}-{highest:03d} "
                f"[clause 2b]"
            )
        else:
            checked[ns] = ptr

    # ⚠ EVERY violation is reported at once. A guard that stops at the first one makes the reader
    # fix, re-run, fix — and an unregistered namespace behind a wrong pointer stays invisible for
    # as many rounds as there are defects ahead of it.
    sep = chr(10) + "  - "
    assert not violations, (
        f"{len(violations)} namespace-register violation(s):" + sep + sep.join(violations)
    )
    return checked
