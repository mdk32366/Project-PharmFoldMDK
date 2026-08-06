"""The surfaceome census split (ORDERS-Code-2026-08-04-surfaceome-spans-v2 §2).

This is `core/foldability.py`'s three-verdict envelope lifted to census scale,
where two new things are true and both are ways to understate the cost:

  1. **Identifiers fail.** At 2,886 entry names some resolve to nothing, some to
     several. An identifier the pipeline could not resolve is not a free target;
     it is an unknown, and it must appear in the output as one.
  2. **Topology is often absent.** ~16% of the *82* had no sliceable ECD span. A
     silent `0` there classifies every unsliceable target as trivially free and
     understates the paid half — the `?? 0` defect `TargetList.jsx` already
     records, in a new place.

⚠ AND THE ONE THAT IS NOT AN OVERSIGHT BUT A TEMPTATION: the 82's 40/13/16/13
split is an **expression-filtered sample**, not a random draw from the surfaceome.
Scaling it up by a ratio would produce a confident number about a population it
was never drawn from. `test_split_is_measured_not_scaled` exists so that path
cannot be added quietly.

Pure. No GPU, no network, no database. Needs none of the census data to run.
"""

from __future__ import annotations

import dataclasses
import inspect
import re
from pathlib import Path

import pytest

from core.census import (
    LOCAL,
    MULTI,
    NO_TOPOLOGY,
    INACTIVE,
    FETCH_FAILED,
    OVER_CEILING,
    RENTAL,
    UNRESOLVED,
    census_split,
)
from core.manifest import LOCAL_CEILING, FoldCeiling


# ⚠ F-018: `resolved` is RETIRED. The live vocabulary is active/merged/inactive/multi/unresolved,
# and `active` is what a fetchable, correctly-identified row now carries. These fixtures moved
# because the constant rejects the old string -- which is the retirement doing its job.
def _row(span=None, status="active", entry="X_HUMAN"):
    return {"entry": entry, "span_aa": span, "id_status": status}


# ── §2.1 — measured, never scaled ────────────────────────────────────────────

def test_split_is_measured_not_scaled():
    """The split takes a SPAN LIST and returns counts. No path takes a ratio and
    a total.

    D-077 dec 6 / v2 §2: the 82's split is an expression-filtered sample and is
    **not evidence about the surfaceome**. Adding `scale_from(ratio, n)` reddens
    this. Asserted structurally rather than by convention, because the
    extrapolation would look like a helpful convenience at the moment someone
    wants a headline number and does not yet have the spans.
    """
    import core.census as mod

    source = inspect.getsource(mod)
    body = re.sub(r'""".*?"""', "", source, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))

    for banned in ("scale_from", "extrapolat", "ratio", "proportion_of", "estimate_from"):
        assert banned not in body, f"extrapolation vocabulary {banned!r} reached the census module"

    # and no public callable accepts a (ratio, total)-shaped signature
    for name in dir(mod):
        if name.startswith("_"):
            continue
        obj = getattr(mod, name)
        if callable(obj) and not isinstance(obj, type):
            try:
                params = set(inspect.signature(obj).parameters)
            except (TypeError, ValueError):
                continue
            assert not ({"ratio", "total"} <= params), f"{name} takes a ratio and a total"


# ── §2.2-2.4 — it is the same envelope, at scale ─────────────────────────────

def test_split_reads_the_ceiling_structure():
    """Verdicts move when `LOCAL_CEILING` moves. Hardcoding 440 reddens this."""
    rows = [_row(500)]
    assert census_split(rows)[RENTAL] == 1

    raised = dataclasses.replace(LOCAL_CEILING, known_good=600)
    assert census_split(rows, ceiling=raised)[LOCAL] == 1


def test_unstable_band_routes_conservatively():
    """An `unstable` band uses the LOW end (D-077 dec 4). High end reddens this."""
    banded = FoldCeiling(hardware="test", dtype="int8", chunk_size=64,
                         known_good=440, known_bad=630, unstable_band=(472, 512))
    counts = census_split([_row(470), _row(500), _row(520)], ceiling=banded)
    assert counts[LOCAL] == 1 and counts[RENTAL] == 1 and counts[OVER_CEILING] == 1


def test_over_ceiling_is_distinct_from_rental():
    """Three cost categories, not two. Collapsing them reddens this: 'costs money'
    and 'folds on no single card' are different facts, and a census that merges
    them quotes a price for something that cannot be bought."""
    counts = census_split([_row(300), _row(500), _row(700)])
    assert counts[LOCAL] == 1 and counts[RENTAL] == 1 and counts[OVER_CEILING] == 1
    assert LOCAL != RENTAL != OVER_CEILING != LOCAL


# ── §2.5 — ⚠ THE LOAD-BEARING TEST ───────────────────────────────────────────

def test_absent_span_is_a_category_not_a_zero():
    """No numeric ECD span -> `no_topology`. NEVER length 0, never `local`.

    Coercing to 0 reddens this. ~16% of the 82 had no sliceable topology; at
    census scale a silent 0 classifies every unsliceable target as trivially free
    and understates the paid half. This is the `?? 0` defect in a new place.
    """
    counts = census_split([_row(None), _row(None), _row(300)])

    assert counts[NO_TOPOLOGY] == 2
    assert counts[LOCAL] == 1, "the one real span must not be joined by the two absent ones"

    # the specific coercion this guards against
    zeroed = census_split([_row(0)])
    assert zeroed[NO_TOPOLOGY] == 1 or zeroed[LOCAL] == 0, \
        "a span of 0 must not be treated as a foldable 0-length target"


def test_absent_span_never_silently_becomes_affordable():
    """The direction of the error matters: an unknown must never land in a
    category that makes the census look cheaper."""
    counts = census_split([_row(None) for _ in range(10)])
    assert counts[LOCAL] == 0 and counts[RENTAL] == 0 and counts[OVER_CEILING] == 0
    assert counts[NO_TOPOLOGY] == 10


# ── §2.6 — identity failures survive to the output ───────────────────────────

def test_unresolved_and_multi_survive_to_the_output():
    """Both appear as their own counts. Filtering either reddens this.

    v2 §1: a census cost model that silently excludes the identifiers it could
    not resolve is understating the census.
    """
    rows = [_row(300, "active"), _row(None, "multi"), _row(None, "unresolved"),
            _row(None, "unresolved")]
    counts = census_split(rows)

    assert counts[MULTI] == 1
    assert counts[UNRESOLVED] == 2
    assert counts[LOCAL] == 1


def test_identity_status_wins_over_a_span():
    """A `multi` row carrying a span is still `multi`. Counting it by span would
    assert an identity Task B explicitly declined to make."""
    counts = census_split([_row(300, "multi")])
    assert counts[MULTI] == 1 and counts[LOCAL] == 0


def test_every_row_lands_somewhere_and_nothing_is_invented():
    """Exhaustive and conservative: counts sum to the input length exactly. A
    census instrument that dropped rows would understate cost; one that
    duplicated them would overstate it."""
    rows = ([_row(200)] * 3 + [_row(500)] * 2 + [_row(900)] +
            [_row(None)] * 4 + [_row(None, "multi")] * 2 +
            [_row(None, "unresolved")] * 5 + [_row(None, "inactive")])
    counts = census_split(rows)
    assert sum(counts.values()) == len(rows) == 18


def test_empty_census_is_zeroes_not_an_error():
    counts = census_split([])
    assert sum(counts.values()) == 0
    for key in (LOCAL, RENTAL, OVER_CEILING, NO_TOPOLOGY, MULTI, UNRESOLVED, INACTIVE, FETCH_FAILED):
        assert counts[key] == 0


# ── §2.7 — no census-size literal ────────────────────────────────────────────

def test_no_census_size_literal_in_the_module():
    """No `2886`, `2216`, `5102`, `2400` anywhere. Adding one reddens this.

    A census size written into the code is a claim about a file the code has not
    read — and the counts must come off the artifact, dated, every time (D-050).
    """
    source = (Path(__file__).resolve().parent.parent / "core" / "census.py").read_text(
        encoding="utf-8"
    )
    for literal in ("2886", "2216", "5102", "2400"):
        assert literal not in source, f"census-size literal {literal!r} hardcoded"


def test_no_ceiling_literal_in_the_module():
    """The same rule the ceiling itself lives under (D-050, D-077 dec 3)."""
    source = (Path(__file__).resolve().parent.parent / "core" / "census.py").read_text(
        encoding="utf-8"
    )
    body = re.sub(r'""".*?"""', "", source, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    for literal in ("440", "630"):
        assert literal not in body, f"ceiling literal {literal!r} hardcoded; read LOCAL_CEILING"


# ── the refusals travel with the instrument (D-074, D-077 dec 1) ─────────────

def test_the_module_carries_the_refusals():
    """This module is the one most likely to be read by someone building a census
    surface, so decision 1's refusals must be where they will meet them."""
    import core.census as mod

    doc = (mod.__doc__ or "").lower()
    assert "filter" in doc and "census" in doc
    assert "suitability" in doc
    assert "sample" in doc or "extrapolat" in doc


def test_census_is_not_reachable_from_the_scorer():
    """Structural half of D-077 dec 1.1 — same guard `core/foldability.py` carries."""
    import ast

    root = Path(__file__).resolve().parent.parent
    for name in ("core/scorer.py", "core/features.py"):
        tree = ast.parse((root / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module]
            for m in mods:
                assert "census" not in m and "foldability" not in m, \
                    f"{name} imports {m!r} — a compute-budget variable must not reach scoring"
