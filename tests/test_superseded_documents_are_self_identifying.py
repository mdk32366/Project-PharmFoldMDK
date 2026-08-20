"""A preserved supersession chain is only useful if the reader can tell which link they are on.

⚠⚠ THE DEFECT THIS EXISTS FOR, AND IT CAUGHT THE PLANNER. Three versions of one draft were preserved
— `f9da826f` → `02d7856a` → `d1466e00` — each superseded copy correctly suffixed. **The CURRENT one
kept the plain name.** So the stale artifacts announced themselves and the live one did not, and the
Planner read the superseded copy's status line and raised a stale-state alarm from it.

⚠ The reading was the visible failure; **the filenames were the mechanism.** A reader reaching for
*"the draft"* got the right file by alphabetisation, not by design, and had to already know which
hash was current in order to know they were on it.

**The remedy is not "check which link you are on" — that is a discipline that depends on remembering.
It is that the wrong link cannot be reached by a name that does not say what it is.** Every member of
a multi-version family carries its STATE and its OWN hash prefix, so a filename alone answers the
question.
"""
from __future__ import annotations

import hashlib
import pathlib
import re

DOCS = pathlib.Path("docs")

# `‹basename›-STATE-‹hash8›.md`
SUFFIX = re.compile(r"^(?P<family>.+?)-(?P<state>LANDED|SUPERSEDED|WITHDRAWN)-(?P<hash>[0-9a-f]{8})$")

# the range markers a hash-pinned document declares
ANCHORS = (b"\n#### ", b"\n### ", b"\n## \xc2\xa7")


def _families() -> dict[str, list[pathlib.Path]]:
    fams: dict[str, list[pathlib.Path]] = {}
    for p in sorted(DOCS.glob("*.md")):
        m = SUFFIX.match(p.stem)
        family = m.group("family") if m else p.stem
        fams.setdefault(family, []).append(p)
    return fams


def test_every_member_of_a_multi_version_family_names_its_state_and_hash():
    """⚠ The rule, and it binds the CURRENT member hardest — that is the one that was unlabelled."""
    offenders = []
    for family, members in _families().items():
        # a family is multi-version once any member is marked superseded/withdrawn
        marked = [p for p in members if SUFFIX.match(p.stem)]
        if not any(SUFFIX.match(p.stem).group("state") != "LANDED" for p in marked):
            continue
        for p in members:
            if not SUFFIX.match(p.stem):
                offenders.append(
                    f"{p.name} is in a superseded family and carries no STATE-hash suffix — "
                    f"a reader cannot tell which link it is without opening it")
    assert offenders == [], offenders


def test_the_hash_in_the_filename_is_the_hash_of_the_file():
    """⚠⚠ A LABEL THAT CAN LIE IS WORSE THAN NO LABEL. If the suffix says `d1466e00`, the document's
    own AUTHORED-SHA256 range must hash to it — otherwise the naming convention becomes a second
    thing to drift, which is `D-074` decision 3's whole objection."""
    checked = 0
    for p in sorted(DOCS.glob("*.md")):
        m = SUFFIX.match(p.stem)
        if not m:
            continue
        raw = p.read_bytes()
        # ⚠ the declared range differs per document; try each known anchor and accept the one that
        # reproduces the claimed prefix, so this test does not need a per-file table to maintain.
        got = []
        for anchor in ANCHORS:
            i = raw.find(anchor)
            if i == -1:
                continue
            got.append(hashlib.sha256(raw[i + 1:]).hexdigest())
        assert any(h.startswith(m.group("hash")) for h in got), (
            f"{p.name} claims {m.group('hash')} but no declared range reproduces it — "
            f"the filename is asserting something the bytes do not support")
        checked += 1
    assert checked >= 3, f"only {checked} labelled documents checked"


def test_a_family_has_at_most_one_landed_member():
    """⚠ Two LANDED members would mean two live versions of one artifact, which is the state the
    chain exists to make impossible."""
    for family, members in _families().items():
        landed = [p for p in members
                  if (m := SUFFIX.match(p.stem)) and m.group("state") == "LANDED"]
        assert len(landed) <= 1, f"{family} has {len(landed)} LANDED members: {[p.name for p in landed]}"
