"""Every hash-pinned artifact in the tree is protected from git's own checkout filter.

⚠⚠ WHY THIS TEST EXISTS. `F-047` member 15 recorded that `core.autocrlf=true` would rewrite
LF -> CRLF on checkout and break every authored `sha256` on a fresh clone — *a guard
manufacturing its own failure signal, indistinguishable from the channel corruption it was built
to detect.* A `.gitattributes` was added and the class was considered handled.

⚠ IT RECURRED ON 2026-08-20, because the rule was scoped to the `docs/` files that existed when
it was written and nobody widened it when `data/census/census_features.v1.jsonl` landed. The blob
was committed intact; the WORKING COPY came back CRLF and hashed to `0a17cab2…` against a pinned
`c08f9f1d…`. It was caught only because the ingest verifies its source before writing.

⚠⚠ *A rule applied to one directory and not another is not a rule.* This test is the difference
between having fixed an instance and having closed the class: it DERIVES the set of hash-pinned
artifacts from the tree and fails if any of them is unprotected — so the next one to land is
covered without anyone remembering to widen anything.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
GITATTRS = REPO / ".gitattributes"

# A file is HASH-PINNED if it DECLARES an `AUTHORED-SHA256` over itself — the marker followed by
# `= <64 hex>` — or if it is named as the `output` of a manifest that pins a sha256 for it.
#
# ⚠⚠ THE DECLARATION FORM IS REQUIRED, AND THE REASON IS THIS TEST'S OWN HISTORY. It first matched
# a bare `AUTHORED-SHA256` anywhere in the file, and went red on `docs/README.md` the moment an
# entry was written that DESCRIBES the rule — *"docs carrying `AUTHORED-SHA256`"*. The log is not a
# pinned artifact; it declares no hash over itself. ⚠ A detector that cannot tell a MENTION from a
# DECLARATION reddens on correct files, and a test that reddens on correct code is worse than none.
# ⚠ `re.S` because real declarations wrap the range across a newline before the `=`.
#
# ⚠⚠ AND THE STRICTER FORM IMMEDIATELY EXPOSED TWO ERRORS IN THE OTHER DIRECTION, BOTH MINE:
#   - `AMENDMENT-2026-08-19-planner-log-entries.md` declares with a COLON (`AUTHORED-SHA256: <hash>`),
#     not `= `<hash>``. A real declaration the first stricter regex MISSED — the narrow-detector
#     failure, arriving one edit after the broad-detector failure. Both forms are accepted now.
#   - `ORDERS-Code-2026-08-19-clinical-edges-1-and-2.md` and
#     `SPEC-2026-08-19-supplier-survey-clinical-edges.md` say, in their own text, *"no
#     `AUTHORED-SHA256` IS DECLARED, AND THAT IS DELIBERATE."* They were never pinned. I added them
#     to `.gitattributes` on 2026-08-20 believing otherwise; the entries are harmless and stay, and
#     the mistaken reading is recorded there rather than quietly removed.
AUTHORED = re.compile(rb"AUTHORED-SHA256.{0,200}?[=:]\s*`?[0-9a-f]{64}`?", re.S)


def _protected() -> set[str]:
    out: set[str] = set()
    if not GITATTRS.exists():
        return out
    for line in GITATTRS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and "-text" in parts[1:]:
            out.add(parts[0])
    return out


def _hash_pinned() -> set[str]:
    found: set[str] = set()
    for p in (REPO / "docs").glob("*.md"):
        if AUTHORED.search(p.read_bytes()):
            found.add(p.relative_to(REPO).as_posix())
    # artifacts pinned by a sibling manifest (the ingest pattern)
    for man in (REPO / "data").rglob("*.manifest.json"):
        import json
        try:
            m = json.loads(man.read_text(encoding="utf-8"))
        except Exception:                                        # noqa: BLE001
            continue
        if "sha256" in m and "output" in m:
            target = man.parent / m["output"]
            if target.exists():
                found.add(target.relative_to(REPO).as_posix())
                found.add(man.relative_to(REPO).as_posix())
    return found


def test_every_hash_pinned_artifact_is_marked_minus_text():
    pinned = _hash_pinned()
    assert pinned, "found no hash-pinned artifacts — the detector is broken, not the tree"
    unprotected = sorted(pinned - _protected())
    assert not unprotected, (
        "these carry a pinned sha256 but nothing stops git rewriting their line endings on "
        "checkout — F-047 member 15, recurring:\n  " + "\n  ".join(unprotected))


def test_no_hash_pinned_artifact_is_crlf_in_the_working_tree():
    """⚠ The rule above is a declaration; this is the measurement. A `.gitattributes` entry added
    without re-checking-out the file leaves the corrupted copy in place, and the declaration would
    read as a fix while the bytes stayed wrong."""
    bad = []
    for rel in sorted(_hash_pinned()):
        raw = (REPO / rel).read_bytes()
        if b"\r\n" in raw:
            bad.append(f"{rel} ({raw.count(chr(13).encode() + chr(10).encode())} CRLF)")
    assert not bad, "hash-pinned artifacts are CRLF in the working tree:\n  " + "\n  ".join(bad)


def test_the_census_artifact_still_hashes_to_its_manifest():
    """The end-to-end claim, not a proxy for it: the file on disk hashes to the pin its own
    manifest declares. This is the assertion the ingest makes before it writes anything."""
    import hashlib
    import json
    man_path = REPO / "data" / "census" / "census_features.v1.manifest.json"
    if not man_path.exists():                     # the artifact is optional in a fresh tree
        return
    man = json.loads(man_path.read_text(encoding="utf-8"))
    art = man_path.parent / man["output"]
    got = hashlib.sha256(art.read_bytes()).hexdigest()
    assert got == man["sha256"], (
        f"{art.name} does not hash to its manifest.\n  pinned {man['sha256']}\n  actual {got}\n"
        f"⚠ If nothing edited it, this is the checkout filter, not tampering.")
