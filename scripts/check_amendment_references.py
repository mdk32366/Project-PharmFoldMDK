"""Resolve AMENDMENT references, which the parent citation invariant cannot see.

⚠⚠ THE DEFECT THIS EXISTS FOR. `D-093 amendment 3` is cited in the present tense and there is no
`#### D-093 amendment 3`. The parent invariant reports CLEAN — because `D-093 amendment 3` contains
`D-093`, which exists. **The checker proves the PARENT exists and has no access to whether the
AMENDMENT does.** That is `F-044`'s shape one level down: *a reference that resolves, to the wrong
thing.*

⚠ MA2 — WHICH FORMS ARE RECOGNISED, AND WHICH ARE DELIBERATELY NOT.

RECOGNISED (each measured in the tree before the pattern was written, never assumed):
  `‹ID› amendment N`          — 160 occurrences, the dominant form
  `‹ID› amendments N and M`   — 1 occurrence (`CLOSEOUT-2026-08-19.md`)
  `‹ID› am. N`                — 4 occurrences (`CATCHUP-Planner-2026-08-20.md`)
  ⚠⚠ Each accepts OPTIONAL BACKTICKS around the id. The log's house style is `` `D-093` amendment 4 ``,
  and a pattern requiring whitespace where a backtick sits MISSES 9 references in `docs/README.md`
  alone. **Code's own first pattern had exactly that bug** — which is why MA1 ordered the
  enumeration before the regex.

DELIBERATELY NOT RECOGNISED — categories with causes, never silent passes:
  `‹ID› amendment ‹N›`  — a TEMPLATE PLACEHOLDER (1 occurrence, in a paste-ready scaffold). It names
                          no amendment, so "resolving" it would be meaningless. Counted and reported
                          under `placeholders`, never under `unresolved`.
  bare `amendment N`    — 208 occurrences with NO id. It refers to whichever entry encloses it, and
                          the enclosing entry is context this checker does not track. ⚠ Guessing the
                          parent from position is exactly the wrong-target defect the check exists to
                          prevent, so it is reported under `unattributed` and excluded from the
                          verdict.

⚠ MB4 — THERE IS NO RESERVE TERM, AND THAT IS STATED RATHER THAN OMITTED. `docs/RESERVED.md` has
never held an amendment-level row: reservations are integers, and an amendment consumes no integer
(the `D-099 amendment 1` precedent). So the check is `cited − defined = 0` with **no reserved term**.
A missing term looks like an oversight to the next reader, so it is named here.
"""
from __future__ import annotations

import pathlib
import re
import sys
from collections import Counter

ID = r"(?:[DFS]-\d+|DEP-\d+|A-\d+)"
BT = r"`?"

#: ⚠ the corpus the PARENT invariant uses, so the two checks share a key
PRIMARY = ("docs/README.md", "ARCHITECTURE.md")

CITE_PATTERNS = (
    ("amendment N", re.compile(BT + "(" + ID + ")" + BT + r"\s+amendment\s+(\d+)")),
    ("amendments N and M",
     re.compile(BT + "(" + ID + ")" + BT + r"\s+amendments\s+(\d+)\s+and\s+(\d+)")),
    ("am. N", re.compile(BT + "(" + ID + ")" + BT + r"\s+am\.\s*(\d+)")),
)
PLACEHOLDER = re.compile(BT + "(" + ID + ")" + BT + r"\s+amendment\s+‹N›")
UNATTRIBUTED = re.compile(r"(?<![-\w`])amendment\s+(\d+)")

#: what DEFINES an amendment
DEFINE = re.compile(r"^#### (" + ID + r") amendment (\d+)\b", re.M)


def defined_amendments(text: str) -> set[tuple[str, int]]:
    return {(m.group(1), int(m.group(2))) for m in DEFINE.finditer(text)}


def cited_amendments(text: str) -> tuple[set[tuple[str, int]], Counter]:
    out: set[tuple[str, int]] = set()
    by_form: Counter = Counter()
    for name, rx in CITE_PATTERNS:
        for m in rx.finditer(text):
            ident = m.group(1)
            for g in m.groups()[1:]:
                if g:
                    out.add((ident, int(g)))
                    by_form[name] += 1
    return out, by_form


def check(paths=PRIMARY) -> dict:
    blob = ""
    read = []
    for p in paths:
        f = pathlib.Path(p)
        if f.exists():
            blob += f.read_text(encoding="utf-8") + "\n"
            read.append(p)

    # ⚠⚠ MB5 — THE STRUCTURAL GUARD. `F-050` was reserved in prose, so the reserved parser matched
    # ZERO rows and returned a confident answer about nothing. Same class as a hash range whose
    # markers appeared twice and hashed zero bytes. **A parser that silently matches nothing must
    # refuse, not pass.** These are floors on a tree known to contain far more.
    defined = defined_amendments(blob)
    cited, by_form = cited_amendments(blob)
    if not read:
        raise SystemExit("REFUSED: none of the corpus files exist: %s" % (paths,))
    if len(defined) < 5:
        raise SystemExit(
            "REFUSED: only %d amendment DEFINITIONS matched across %s. The log is known to carry "
            "many more, so the pattern — not the tree — is what changed. A parser matching nothing "
            "returns a valid answer about nothing." % (len(defined), read))
    if len(cited) < 5:
        raise SystemExit(
            "REFUSED: only %d amendment CITATIONS matched. Same reasoning as above." % len(cited))

    unresolved = sorted(cited - defined)
    return {
        "corpus": read,
        "defined": defined,
        "cited": cited,
        "by_form": by_form,
        "placeholders": len(PLACEHOLDER.findall(blob)),
        "unattributed": len(UNATTRIBUTED.findall(blob)),
        "unresolved": unresolved,
    }


def main() -> int:
    r = check()
    # ⚠ the figure states its key, same discipline as the parent check
    print("corpus            : %s" % " + ".join(r["corpus"]))
    print("amendments cited  : %d   (distinct ‹id, n› pairs)" % len(r["cited"]))
    print("amendments defined: %d   (^#### ‹id› amendment N headers)" % len(r["defined"]))
    print("reserved term     : NONE — RESERVED.md has never held an amendment-level row (MB4)")
    print("by form           : %s" % dict(r["by_form"]))
    print("placeholders      : %d  (‹N› template scaffolds — not citations)" % r["placeholders"])
    print("unattributed      : %d  (bare 'amendment N', no id — enclosing entry not tracked)"
          % r["unattributed"])
    print("cited - defined   : %d" % len(r["unresolved"]))
    for ident, n in r["unresolved"]:
        print("   UNRESOLVED: %s amendment %d" % (ident, n))
    return 1 if r["unresolved"] else 0


if __name__ == "__main__":
    sys.exit(main())
