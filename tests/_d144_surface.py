"""The `D-144` surface pin — ONE implementation, shared by `D-145`'s and `D-146`'s guards.

⚠⚠ **WHY THIS FILE EXISTS, AND IT IS A GUARD-DIRECTION REPAIR RATHER THAN A RELAXATION.**

`D-145` and `D-146` each pinned the **whole file** sha256 of six paths, to assert *"no formula,
schema or route change — D-144 stands"*. Four of those six paths are D-144's own
(`core/census_structural.py`, `app/census_structural_read.py`,
`scripts/census_structural_rank.py`, `db/migrations/versions/0012_census_structural_rank.py`) and a
whole-file pin on them says exactly what it means. ⚠ One of the four was **moved by name at
`D-147`** and the superseded digest is recorded beside it — that is a pin working, not a pin
failing: its own failure message says *"belongs to a different entry with its own ruling"*, and
`### D-147` was that entry.

**Two are SHARED.** `app/read_routes.py` holds every read route in the application and
`db/models.py` holds every table. A whole-file pin on a shared file does not assert *"D-144 did not
move"* — it asserts *"nothing else was ever added"*, which is a different and false property. It
reddens on any later additive entry, and the guards' own failure message licenses exactly that:
*"a formula, schema or route edit belongs to a different entry with its own ruling."* `D-149` is such
an entry, and it added two routes and two tables that touch nothing of D-144's.

⚠⚠ **SO THE FIX IS NARROWER, NOT LOOSER.** For the two shared files the pin becomes a **region**
pin over the D-144-owned block, and **the expected digest is taken from `2170bd8` — the commit where
D-144 merged — not recomputed from the working tree.** A pin recomputed from the thing it pins is
not a pin; it is a mirror. Measured 2026-09-09: both regions are byte-identical between `2170bd8`
and this branch, so the property the guards assert is **preserved in substance and tightened in
scope**. The four whole-file pins are untouched.

⚠ `A-017` (the fixture must reach the code under test): `extract_region` **raises** when its anchor
is absent, and a companion test asserts each region is non-trivially large. A region extractor that
silently returned `""` would hash the empty string identically forever — the vacuity this
repository's own prohibition-scan docstring names of itself.
"""

from __future__ import annotations

import hashlib
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The four paths that are D-144's OWN. ⚠ Whole-file pins, unchanged, digests as they merged.
D144_OWN_FILES = {
    "core/census_structural.py":
        "c859da97f73d9da2628a59dc091f7fbcbd8944d0eebba9096e6b011b62ba12c7",
    # ⚠⚠ MOVED BY `### D-147` (the `ecd_intermittent` serve-time join), and the superseded value is
    # recorded rather than overwritten in silence (D-129-C):
    #     D-144 / D-145 / D-146 : 7f581c690ebc95bceb532f0554e97d7499add4c327fcf15802ec406b69bdef6b
    #     D-147 onward          : 0fff62b0b9471cd4447255275cb13cd4ac07890e8a79aacec2c3d40a5d7142df
    # ⚠ `D-149` does NOT touch this file, so it inherits D-147's value unchanged.
    "app/census_structural_read.py":
        "0fff62b0b9471cd4447255275cb13cd4ac07890e8a79aacec2c3d40a5d7142df",
    "scripts/census_structural_rank.py":
        "ef222d19b2c15777ee65736bdc8f7b57b9ed65be990a1ae71a260dbbc7bbafe0",
    "db/migrations/versions/0012_census_structural_rank.py":
        "8a4a3d49498147ce070798665f53350d335c608b5da41c2d5c6833228a2dfdf0",
}

#: The two SHARED files, pinned over D-144's own region only.
#: ``rel -> (start_prefix, stop_prefixes, sha256_of_that_region_at_2170bd8)``
D144_SHARED_REGIONS = {
    "app/read_routes.py": (
        '@read_router.get("/census-structural-ranking")',
        ("@read_router.get(",),
        "c7f69a501ebabd9d2ef0ab01dba5557e08b73dd910a1ca0d3205bb668b91172f",
    ),
    "db/models.py": (
        "class CensusStructuralRun(Base):",
        ("# NOTE:", "class ClinicalPathology(Base):"),
        "43feb5288cc60274d0e068778352672dd82ada5f16485fdfe1aebb77e9c0cc43",
    ),
}

#: ⚠ The minimum size each region must have, so a mis-anchored extraction that happened to hash to
#: something cannot pass as a region. Measured at `2170bd8`: 29 and 97 lines.
D144_REGION_MIN_LINES = {"app/read_routes.py": 29, "db/models.py": 97}


def normalised(rel: str) -> str:
    """⚠ LF-normalised, per `RESERVED.md`'s hash-discipline ruling: git's `LF→CRLF` conversion on
    checkout means a committed file's delivered bytes differ from its committed ones, and a rule
    that raises a false alarm on every checkout trains its readers to ignore it."""
    return (REPO / rel).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def extract_region(rel: str) -> str:
    """The D-144-owned block of a shared file.

    ⚠⚠ RAISES when the anchor is absent, and that is the point (`A-017`). A deleted
    `@read_router.get("/census-structural-ranking")` is D-144's route being REMOVED — the loudest
    possible version of what this pin exists to catch — so it must not degrade into an extractor
    that returns nothing and hashes stably.
    """
    start, stops, _ = D144_SHARED_REGIONS[rel]
    lines = normalised(rel).split("\n")
    matches = [i for i, ln in enumerate(lines) if ln.startswith(start)]
    if not matches:
        raise AssertionError(
            f"{rel} no longer contains the D-144 anchor {start!r} — D-144's own route or model has "
            f"been renamed or deleted, which is exactly what this pin exists to catch")
    if len(matches) != 1:
        # ⚠ `F-024`: a pattern that occurs more than once, matched without a uniqueness check,
        # takes the wrong occurrence. Five dated instances, two agents, one day.
        raise AssertionError(
            f"{rel} contains {len(matches)} occurrences of the D-144 anchor {start!r}; a region "
            f"pin cannot say which one it means")
    i = matches[0]
    j = len(lines)
    for k in range(i + 1, len(lines)):
        if any(lines[k].startswith(p) for p in stops):
            j = k
            break
    return "\n".join(lines[i:j]).rstrip("\n") + "\n"


def region_digest(rel: str) -> str:
    return hashlib.sha256(extract_region(rel).encode("utf-8")).hexdigest()


def whole_file_digest(rel: str) -> str:
    return hashlib.sha256(normalised(rel).encode("utf-8")).hexdigest()
