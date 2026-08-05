"""F-020 — `--ablate geom_proxy` must REFUSE when a ranking-set row has no feature 7.

⚠ WHY THIS EXISTS, AND WHY A WARNING WAS NOT ENOUGH.  Migration 0007 created
`protein_features.membrane_proximal_sasa`; nothing populated it.  The fit then did three
things in sequence, none of which reddens:

  1. `fit_scorer.py:111`  `float(rec.membrane_proximal_sasa or 0.0)` -- absent becomes 0.0.
  2. `fit_scorer.py:114`  printed a WARNING saying "a 0.0 placeholder here would be an
     imputed value (D-027)" -- and proceeded anyway.
  3. `core/scorer.py:152`  standardizes a zero-variance column to 0.0 for every row.

So feature 7 would enter the fit as a constant, contribute exactly nothing, and
`geom_proxy` (0,1,4,5,6) would collapse to `no_plddt` (0,1,4,5) plus one inert parameter.
**The result would land on the `no_plddt` baseline -- D-075 Decision 4's ambiguous row --
not because the SASA proxy failed to recover the signal, but because it was never computed.**
A confident, dated, persisted `sensitivity` run that is an artifact of an empty column.

⚠ SCOPE, AND IT IS THE POINT.  The refusal belongs to the NAMED ABLATION, not to the fit.
The pre-registered six-feature path legitimately has no feature 7 and must keep running
untouched: a guard that reddens the pre-registered path would make F-004 unreproducible in
order to protect an ablation, which is a worse defect than the one being fixed.

⚠ AND THE REFUSAL MUST PRECEDE `create_ranking_run()`.  This order deliberately runs the
refusal against live production; a guard that raises *after* run creation writes a junk
`ranking_runs` row on every refusal.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fit_scorer as fs  # noqa: E402
from core.scorer import FEATURE_SETS  # noqa: E402

SIX = (1.13, 2.27, 3.41, 4.59, 5.73, 6.87)


def _rec(symbol, *, disp="ranked", plddt=71.5, f7=None, features=None):
    """A FeatureRecord. `f7=None` is the production state this whole file is about."""
    return fs.FeatureRecord(
        symbol=symbol, accession=symbol,
        features=features if features is not None else SIX,
        disposition=disp, mean_plddt=plddt,
        below_plddt_floor=(plddt < 50 if plddt is not None else None),
        membrane_proximal_sasa=f7,
    )


def _rows(records):
    return fs.build_scorer_rows(records, group_b_accessions=set(), evidence_by_symbol={})


# ── the guard itself ─────────────────────────────────────────────────────────
def test_geom_proxy_refuses_when_a_ranking_row_lacks_feature_7():
    """⚠ Prove it bites by restoring the `or 0.0` behaviour (deleting the guard call): the
    fit then proceeds on a constant column and this assertion fails at the `pytest.raises`."""
    records = [_rec("AAA", f7=None), _rec("BBB", f7=12.5), _rec("CCC", f7=None)]
    rows = _rows(records)
    with pytest.raises(fs.Feature7NotExtracted) as exc:
        fs.refuse_if_named_set_needs_feature_7("geom_proxy", records, rows)
    msg = str(exc.value)
    assert "AAA" in msg and "CCC" in msg, f"the refusal must NAME the affected symbols: {msg!r}"
    assert "BBB" not in msg, f"a row that HAS feature 7 must not be named: {msg!r}"


def test_the_preregistered_path_is_unaffected_by_null_feature_7():
    """⚠ The load-bearing scope test. Same fixture, same nulls -- the six-feature path must
    not raise. Prove it bites by scoping the guard to the fit rather than to the named set."""
    records = [_rec("AAA", f7=None), _rec("BBB", f7=None)]
    rows = _rows(records)
    fs.refuse_if_named_set_needs_feature_7("preregistered", records, rows)   # must not raise
    # and the ablations that do not use index 6 are equally unaffected
    for name, idx in FEATURE_SETS.items():
        if 6 not in idx:
            fs.refuse_if_named_set_needs_feature_7(name, records, rows)


def test_excluded_rows_may_still_carry_the_inert_placeholder():
    """A row outside the ranking set is never fit or scored, so its `(0.0,)*7` placeholder is
    inert by construction. Prove it bites by widening the guard to all rows."""
    records = [_rec("KEPT", f7=9.9), _rec("HELDOUT", disp="held_out", f7=None),
               _rec("LOWCONF", plddt=11.0, f7=None)]
    rows = _rows(records)
    assert [r.in_ranking_set for r in rows] == [True, False, False], "fixture precondition"
    fs.refuse_if_named_set_needs_feature_7("geom_proxy", records, rows)      # must not raise


# ── the one that stops a deliberate production refusal from littering the run table ──
def _fittable_records(f7):
    """A cohort the fit can actually complete on: 12 ranking rows, 4 positives, 8 negatives,
    features that vary. ⚠ The variation matters -- a DEGENERATE fixture would raise before
    `create_ranking_run()` for its own reason, and the revert below would then red for that
    reason instead of for the ordering it is meant to prove."""
    return [
        fs.FeatureRecord(symbol=f"G{i:02d}", accession=f"P{i:05d}",
                         features=(100.0 + 7 * i, 12.0 + 0.5 * i, 70.0 + i,
                                   65.0 + 0.7 * i, 0.30 + 0.01 * i, 0.20 + 0.02 * i),
                         disposition="ranked", mean_plddt=70.0 + i, below_plddt_floor=False,
                         membrane_proximal_sasa=f7)
        for i in range(12)
    ]


POSITIVE_ACCESSIONS = {"P00000", "P00003", "P00006", "P00009"}


def test_the_refusal_precedes_create_ranking_run(monkeypatch):
    """⚠ No `ranking_runs` row may be created when the refusal fires.

    Prove it bites by moving the guard after `create_ranking_run()`: the fit then completes,
    the spy records a call, and this fails AT THE ASSERTION below -- not at collection, and
    not because the fixture was degenerate."""
    records = _fittable_records(f7=None)
    calls: list[str] = []

    monkeypatch.setattr(fs, "read_feature_records", lambda engine: records)
    monkeypatch.setattr(fs, "load_labels", lambda path: set(POSITIVE_ACCESSIONS))
    monkeypatch.setattr(fs, "load_evidence", lambda path: {})
    monkeypatch.setattr(fs, "create_ranking_run",
                        lambda *a, **k: calls.append("create_ranking_run") or 999)
    monkeypatch.setattr(fs, "persist_results", lambda *a, **k: (0, 0))

    # ⚠ The CLI formats the refusal and returns 1; the HELPER raises. Asserted at both layers
    # (the helper's raise is pinned by the first test in this file) because a library that
    # raises and a CLI that formats is the layering -- a programmatic caller must not be able
    # to proceed past a printed message.
    assert fs.run(["--run", "--ablate", "geom_proxy", "--persist"],
                  engine_factory=lambda: object()) == 1

    assert calls == [], (
        "the refusal fired AFTER create_ranking_run() -- every deliberate refusal against "
        f"production would write a junk ranking_runs row. calls={calls!r}"
    )


def test_the_fixture_for_the_ordering_test_is_not_degenerate(monkeypatch):
    """⚠ Pins the precondition of the test above. With feature 7 PRESENT the same cohort must fit
    to completion and reach `create_ranking_run()`. Without this, a degenerate fixture would make
    the ordering test pass for the wrong reason and the revert would prove nothing."""
    records = _fittable_records(f7=42.0)
    calls: list[str] = []
    monkeypatch.setattr(fs, "read_feature_records", lambda engine: records)
    monkeypatch.setattr(fs, "load_labels", lambda path: set(POSITIVE_ACCESSIONS))
    monkeypatch.setattr(fs, "load_evidence", lambda path: {})
    monkeypatch.setattr(fs, "create_ranking_run",
                        lambda *a, **k: calls.append("create_ranking_run") or 999)
    monkeypatch.setattr(fs, "persist_results", lambda *a, **k: (0, 0))

    assert fs.run(["--run", "--ablate", "geom_proxy", "--persist"],
                  engine_factory=lambda: object()) == 0
    assert calls == ["create_ranking_run"], (
        "the ordering test's fixture cannot reach create_ranking_run even when feature 7 is "
        f"present, so that test would pass vacuously. calls={calls!r}"
    )


def test_the_named_set_actually_uses_index_six():
    """Pins the premise the guard is scoped on. If `geom_proxy` stopped using index 6 the
    guard would silently never fire, and this file would pass while guarding nothing."""
    assert 6 in FEATURE_SETS["geom_proxy"], FEATURE_SETS["geom_proxy"]
    assert 6 not in FEATURE_SETS["preregistered"], FEATURE_SETS["preregistered"]
