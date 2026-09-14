"""D-165 — tile geometry is deterministic from a fresh clone.

⚠⚠ **`F-076` is the defect this closes.** `plan_tiles` derived tile edges from
`data/census/spancache`, which is **gitignored** — so a machine that had fetched UniProt spans
snapped the edges and a fresh clone did not. **The same parent planned two different tilings
depending on who ran it**, and five tests asserted a geometry that held only where the cache was
absent.

⚠ The cache is **243 MB across 4,990 raw UniProt entries** and is not committable. The **derived**
ends are 24 KB, and those are what planning needs — so the pin, not the cache, travels with the
repository.

⚠⚠ This is `D-162` rule 8: *anything outside version control that determines a landed artifact is
a defect on the same footing as a single-copy enumeration.* The spancache determined the geometry
of every landed hold-48 tile. It was the third face of that rule when `F-076` found it and the pin
is the fix.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from core.hold48 import (
    PINNED_DOMAIN_ENDS,
    UNIPROT_CACHE,
    domain_ends_span_relative,
    hold48_rows,
    plan_tiles,
    tileable_rows,
)

REPO = Path(__file__).resolve().parent.parent


def test_the_pin_is_committed_and_covers_every_hold48_accession():
    """⚠ A partial pin is worse than none: it would make planning deterministic for some parents
    and not others, which is harder to notice than a uniform failure."""
    assert PINNED_DOMAIN_ENDS.is_file(), (
        "the D-165 pin is absent; tile geometry reverts to depending on a gitignored cache")
    entries = json.loads(PINNED_DOMAIN_ENDS.read_text(encoding="utf-8"))["entries"]
    rows = hold48_rows()
    assert rows, "no hold-48 rows — this guard would pass vacuously"
    missing = [r.accession for r in rows if r.accession not in entries]
    assert not missing, f"the pin does not cover {missing}"


def test_the_pin_is_keyed_by_span_so_a_span_repair_cannot_reuse_stale_ends():
    """⚠⚠ The key is (accession, span_start, span_end). `F-069`/`F-071` span repairs are live, and
    a pin keyed on accession alone would silently carry old ends across a span change — the exact
    wrong-but-plausible shape this project keeps finding."""
    entries = json.loads(PINNED_DOMAIN_ENDS.read_text(encoding="utf-8"))["entries"]
    row = tileable_rows()[0]
    rec = entries[row.accession]
    assert rec["span_start"] == row.span_start and rec["span_end"] == row.span_end

    # a span that does not match the pin must fall THROUGH, not return the pinned ends
    from core.hold48 import _pinned_domain_ends
    assert _pinned_domain_ends(row.accession, row.span_start, row.span_end + 1) is None
    assert _pinned_domain_ends(row.accession, row.span_start, row.span_end) is not None


def test_a_fresh_clone_plans_the_SAME_geometry_as_a_warm_machine():
    """⚠⚠ **THE PROPERTY, and the one that would have prevented `F-076`.**

    An empty cache directory stands in for a fresh clone. Before `D-165` this returned the
    *unsnapped* geometry while a warm machine returned the snapped one.
    """
    empty = Path(tempfile.mkdtemp())
    for row in tileable_rows():
        cold = [(t.start, t.end) for t in plan_tiles(row, cache_dir=empty)]
        warm = [(t.start, t.end) for t in plan_tiles(row)]
        assert cold == warm, (
            f"{row.accession} plans differently with and without the local spancache: "
            f"fresh clone {cold} vs warm {warm}. The pin is not being consulted.")


def test_an_explicit_domain_ends_still_overrides_the_pin():
    """⚠ The pin must not become unbypassable. `tests/test_hold48_tiles.py` asserts the unsnapped
    window arithmetic by passing `domain_ends=[]`, and that has to keep working — otherwise the pin
    would silently redefine what those tests measure."""
    row = next(r for r in tileable_rows() if r.span_aa > 1656)
    pinned = [(t.start, t.end) for t in plan_tiles(row)]
    forced = [(t.start, t.end) for t in plan_tiles(row, domain_ends=[])]
    assert forced != pinned, "an explicit domain_ends no longer overrides the pin"
    assert forced[0][1] == 1656, "the forced geometry is not the unsnapped window"


@pytest.mark.skipif(not UNIPROT_CACHE.is_dir(),
                    reason="no local spancache — the drift check needs the source it pins")
def test_the_pin_AGREES_with_the_cache_it_was_derived_from():
    """⚠ The drift detector. If the cache is re-fetched and UniProt has changed a domain boundary,
    the pin and the source disagree and **that is a finding**, not something to silently re-pin.
    ⚠ Skipped where the cache is absent, which is CI — a machine that cannot see the source cannot
    testify about it."""
    entries = json.loads(PINNED_DOMAIN_ENDS.read_text(encoding="utf-8"))["entries"]
    drift = []
    for row in hold48_rows():
        if not (UNIPROT_CACHE / f"{row.accession}.json").is_file():
            continue
        live = list(domain_ends_span_relative(
            accession=row.accession, span_start=row.span_start,
            span_end=row.span_end, cache_dir=UNIPROT_CACHE))
        if live != entries[row.accession]["domain_ends"]:
            drift.append(row.accession)
    assert not drift, (
        f"the pin disagrees with the local spancache for {drift}. Do NOT re-pin without asking "
        f"why: a changed UniProt domain boundary would move the geometry of landed tiles.")
