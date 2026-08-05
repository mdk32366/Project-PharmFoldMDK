"""D-077 decision 6 — the census cost model, and the refusals it carries.

This is Phase 2's cost instrument: it answers "what does a census of N targets
cost?" before a dollar is spent, from sequence length alone, folding nothing.

⚠ THE TESTS THAT MATTER MOST HERE ARE NOT THE ARITHMETIC ONES. Local-foldability
is a monotone step function of ECD length, and ECD length is feature 1 of the
pre-registered six (D-027). Tier was assigned BY length; precision BY tier. So
length, tier, precision and foldability are four names for one partition with no
overlap — the confound F-008 recorded and D-075 decision 6 declines to resolve.
D-077 decision 1 therefore refuses, in advance, three things, and this module is
one careless import away from being the thing that breaks them.

Pure. No GPU, no network, no database.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import pytest

from core.foldability import LOCAL, OVER_CEILING, RENTAL, envelope, split
from core.manifest import LOCAL_CEILING, FoldCeiling


# ── D-050: the ceiling is READ, never restated ───────────────────────────────

def test_no_ceiling_literal_anywhere_in_the_module():
    """A literal 440 or 630 in this module would be a second copy of the routing
    constant — the exact drift D-077 dec 3 exists to prevent, re-created by the
    instrument built to consume it."""
    source = (Path(__file__).resolve().parent.parent / "core" / "foldability.py").read_text(
        encoding="utf-8"
    )
    body = re.sub(r'""".*?"""', "", source, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))

    for literal in ("440", "630"):
        assert literal not in body, f"ceiling literal {literal!r} hardcoded; read LOCAL_CEILING"


def test_the_verdict_changes_when_the_constant_changes():
    """Proves it actually READS the ceiling rather than coincidentally agreeing
    with it. A module that hardcoded the same numbers would pass every test above
    and fail this one."""
    raised = dataclasses.replace(LOCAL_CEILING, known_good=600)

    assert envelope(500) == RENTAL                      # against the real 440
    assert envelope(500, ceiling=raised) == LOCAL       # against a raised ceiling


# ── the three verdicts ───────────────────────────────────────────────────────

def test_local_rental_and_over_ceiling_are_three_distinct_verdicts():
    """`over_ceiling` is NOT `rental`. Collapsing them would hide that some
    targets fold on no single card at all, which is a different fact about the
    world than "this one costs money"."""
    assert LOCAL != RENTAL != OVER_CEILING
    assert envelope(300) == LOCAL
    assert envelope(500) == RENTAL
    assert envelope(700) == OVER_CEILING


def test_the_boundary_is_where_the_measured_ceiling_says():
    assert envelope(LOCAL_CEILING.local_bound) == LOCAL
    assert envelope(LOCAL_CEILING.local_bound + 1) == RENTAL
    assert envelope(LOCAL_CEILING.rental_bound - 1) == RENTAL
    assert envelope(LOCAL_CEILING.rental_bound) == OVER_CEILING


def test_an_unstable_band_routes_conservatively():
    """D-077 dec 4: routing uses the LOW end of a band. The cost model must agree
    with `tier_for_span` — two instruments disagreeing about what routes where is
    the drift this entry is about."""
    banded = FoldCeiling(hardware="test", dtype="int8", chunk_size=64,
                         known_good=440, known_bad=630, unstable_band=(472, 512))

    assert envelope(470, ceiling=banded) == LOCAL
    assert envelope(500, ceiling=banded) == RENTAL       # inside the band: not local
    assert envelope(520, ceiling=banded) == OVER_CEILING


def test_it_agrees_with_the_manifest_on_every_cohort_span():
    """⚠ The cost model and the manifest must never disagree about a target.

    Checked against the real cohort spans, not invented ones: if these two ever
    diverge, a census would quote a cost for a routing the pipeline does not
    perform.
    """
    import csv

    from core.manifest import tier_for_span

    root = Path(__file__).resolve().parent.parent
    with open(root / "data" / "cohort_82_ecd.csv", encoding="utf-8") as fh:
        spans = [int(r["largest_span_aa"]) for r in csv.DictReader(fh)
                 if (r["largest_span_aa"] or "").strip()]

    assert spans, "no numeric spans read — the fixture is not exercising anything"
    for span in spans:
        tier, _ = tier_for_span(span)
        verdict = envelope(span)
        if tier == "local":
            assert verdict == LOCAL, f"span {span}: manifest says local, cost model says {verdict}"
        else:
            assert verdict in (RENTAL, OVER_CEILING), f"span {span}: disagreement"


def test_unknown_span_is_not_silently_bucketed():
    """A target whose ECD span was never measured (13 of the 82 rows carry an
    empty `largest_span_aa`) must not be quietly counted as affordable. Guessing
    either way is exactly what D-024 refused."""
    with pytest.raises((ValueError, TypeError)):
        envelope(None)


# ── split() and what it may claim ────────────────────────────────────────────

def test_split_counts_the_three_verdicts():
    counts = split([100, 200, 500, 700, 800])
    assert counts == {LOCAL: 2, RENTAL: 1, OVER_CEILING: 2}


def test_split_is_exhaustive_so_no_target_can_vanish():
    """Every input lands in exactly one bucket and the totals reconcile. A census
    instrument that silently dropped rows would understate cost and — worse —
    would be the filtered census decision 1 forbids."""
    spans = [120, 441, 629, 630, 2491]
    counts = split(spans)
    assert sum(counts.values()) == len(spans)


def test_split_on_an_empty_census_is_zeroes_not_an_error():
    assert split([]) == {LOCAL: 0, RENTAL: 0, OVER_CEILING: 0}


# ── D-077 decision 1 — the refusals, enforced not merely documented ──────────

def test_the_module_carries_decision_ones_three_refusals_in_its_docstring():
    """Per D-074, an instrument that can be misused carries the statement of its
    own limits. This one is one careless import away from becoming a seventh
    feature, and the docstring is where a future reader meets it.

    Asserted, not trusted: the refusals must be IN the module, because a reader
    who reaches for `envelope()` from a feature-extraction module will read the
    docstring and nothing else.
    """
    import core.foldability as mod

    doc = (mod.__doc__ or "").lower()
    assert "must not become a model feature" in doc or "not a model feature" in doc
    assert "census" in doc and "filter" in doc
    assert "suitability" in doc
    assert "cost" in doc and "reproducibility" in doc


def test_the_module_declares_no_feature_extraction_surface():
    """A defensive check with a specific target: nothing here may look like it
    belongs in the six. If a future edit adds a `feature`-named public callable to
    this module, that is the first step of the thing decision 1 refuses."""
    import core.foldability as mod

    public = [n for n in dir(mod) if not n.startswith("_")]
    offenders = [n for n in public if "feature" in n.lower() or "score" in n.lower()]
    assert not offenders, f"foldability must not expose feature/score surface: {offenders}"


def test_foldability_is_not_reachable_from_the_scorer():
    """⚠ The structural half of decision 1's first refusal.

    Documenting "must not become a model feature" does not prevent it. This
    asserts the scorer and the feature extractor do not import this module, so the
    refusal is checkable rather than editorial. Proven by revert: add
    `from core.foldability import envelope` to core/scorer.py and watch it redden.
    """
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
                assert "foldability" not in m, (
                    f"{name} imports {m!r} — a compute-budget variable must not reach "
                    f"the scoring path (D-077 dec 1)"
                )
