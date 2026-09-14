"""F-047 amendment 5 — a byte-pinned file must reach the working tree unrewritten, everywhere.

⚠⚠ **THIS DEFECT HAS NOW LANDED THREE TIMES, AND EACH FIX WAS SCOPED TO THE INSTANCE.**

| date | where | what happened |
|---|---|---|
| 2026-08-19 | `docs/` | authored-sha256 artifacts rewritten on checkout; `.gitattributes` created |
| 2026-08-20 | `data/census/census_features.v1.jsonl` | **the same defect**, caught by the ingest's own guard. The fix added **three** files |
| 2026-09-15 | **twelve** data artifacts **and fourteen source modules** | measured here |

⚠ The 2026-08-20 note in `.gitattributes` states the lesson in its own words — *"a rule applied to
one directory and not another is not a rule"* — and then applies the rule to one directory.

⚠⚠ **What made the third instance expensive was not the failure, it was the failure's invisibility.**
The local suite stood at **~34 red on Windows while CI was green**, so the thirty-fifth failure
would have arrived looking exactly like the other thirty-four. *A baseline nobody can tell has
drifted is not a baseline.*

⚠ **And the source half is the wrong-but-plausible class in its purest form.**
`test_d130_residual_rmsd.py` reported *"core/hold48_kabsch.py was edited"* while `git status` said
clean and the index blob hashed to exactly the pinned value. Nothing had edited it. The test was
hashing CRLF bytes against an LF pin — and those pins exist precisely to prove a PR did **not**
touch a sibling module, so a guard that cries *edited* on every clean checkout is one people learn
to ignore.

⚠ The scope is still **not** a blanket `-text` rule. `.gitattributes` declined that for `docs/**` in
2026-08-19 with a stated reason and that reasoning is untouched. What is asserted here is the actual
invariant: **a file whose bytes are pinned must not be rewritten between the index and the disk.**
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ATTRS = (REPO / ".gitattributes").read_text(encoding="utf-8")

#: ⚠ Where a pinned file may live. `docs/` is covered by `.gitattributes` already and its pins are
#: authored provenance rather than test assertions, so the recurrence scan stays off it.
SCANNED = ("data", "core", "app", "scripts", "worker", "db", "ui")

#: ⚠ Bounded so the recurrence guard stays a test and not a batch job.
MAX_SCAN_BYTES = 50 * 1024 * 1024


def _tracked(prefix: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", prefix], cwd=REPO,
                         capture_output=True, text=True).stdout
    return [ln for ln in out.splitlines() if ln.strip()]


def _blob(rel: str) -> bytes | None:
    r = subprocess.run(["git", "cat-file", "-p", f":{rel}"], cwd=REPO, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _untexted() -> set[str]:
    """Every path `.gitattributes` exempts from end-of-line conversion."""
    paths = set()
    for line in ATTRS.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "-text" not in line:
            continue
        paths.add(line.split("-text")[0].strip())
    return paths


EXEMPT = _untexted()
EXEMPT_IN_SCOPE = sorted(p for p in EXEMPT if p.split("/")[0] in SCANNED)


def test_there_are_pinned_files_under_the_rule_at_all():
    """⚠ A guard that iterates an empty list passes forever. Asserted first, by name."""
    assert len(EXEMPT_IN_SCOPE) >= 25, (
        f"only {len(EXEMPT_IN_SCOPE)} pinned files are EOL-exempt; the 2026-09-15 widening added "
        f"twelve data artifacts and fourteen source modules to the three from 2026-08-20, so this "
        f"list should not shrink silently")


@pytest.mark.parametrize("rel", EXEMPT_IN_SCOPE)
def test_an_exempt_file_reaches_the_working_tree_byte_for_byte(rel):
    """⚠⚠ The invariant, stated exactly: **what git stores is what lands on disk.**

    ⚠ Asserted as *index bytes == working bytes*, NOT as "contains no CRLF". Some pinned artifacts
    were authored with CRLF and committed that way deliberately — the contract is byte
    preservation, not a particular line ending, and a guard that demanded LF would be wrong about
    exactly the files the rule exists to protect.
    """
    path = REPO / rel
    if not path.is_file():
        pytest.skip(f"{rel} is listed but not present in this clone")
    blob = _blob(rel)
    if blob is None:
        pytest.skip(f"{rel} is listed but not tracked")
    disk = path.read_bytes()
    assert hashlib.sha256(disk).hexdigest() == hashlib.sha256(blob).hexdigest(), (
        f"{rel} differs between the index and the working tree while being `-text`. Its pinned "
        f"sha256 is wrong on disk right now, and `git status` will call the file clean — which "
        f"reads as tampering rather than as configuration.")


def test_no_UNLISTED_pinned_file_is_being_rewritten():
    """⚠⚠ **THE RECURRENCE GUARD, and the one that would have caught all three instances.**

    Every tracked file in scope whose working bytes differ from its index bytes is hashed both
    ways. If the *index* form matches a sha256 pinned anywhere in the tests or the code, and the
    working form does not, then that file is pinned, drifting, and **not covered by the rule** —
    the state this amendment exists to make impossible to reach quietly.

    ⚠ It enumerates from the tree, not from a list somebody has to remember to update.
    """
    haystack: set[str] = set()
    for prefix in ("tests",) + SCANNED:
        for rel in _tracked(prefix):
            if rel.endswith((".py", ".json")) and ("test" in rel or "manifest" in rel
                                                   or "provenance" in rel or prefix != "data"):
                p = REPO / rel
                if p.is_file() and p.stat().st_size <= MAX_SCAN_BYTES:
                    haystack.update(re.findall(
                        r"[0-9a-f]{64}", p.read_text(encoding="utf-8", errors="replace")))
    assert haystack, "no sha256 pins found at all — this guard would pass vacuously"

    offenders = []
    for prefix in SCANNED:
        for rel in _tracked(prefix):
            if rel in EXEMPT:
                continue
            p = REPO / rel
            if not p.is_file() or p.stat().st_size > MAX_SCAN_BYTES:
                continue
            disk = p.read_bytes()
            if b"\r\n" not in disk:
                continue
            blob = _blob(rel)
            if blob is None or blob == disk:
                continue
            if (hashlib.sha256(blob).hexdigest() in haystack
                    and hashlib.sha256(disk).hexdigest() not in haystack):
                offenders.append(rel)

    assert not offenders, (
        "these files carry a pinned sha256, are rewritten between the index and the working tree, "
        "and are NOT `-text` in .gitattributes, so their pins fail on disk while the blobs are "
        "intact:\n  " + "\n  ".join(offenders)
        + "\n\nAdd them under the F-047 amendment 5 sections of .gitattributes. `a rule applied to "
          "one directory and not another is not a rule` (.gitattributes, 2026-08-20).")
