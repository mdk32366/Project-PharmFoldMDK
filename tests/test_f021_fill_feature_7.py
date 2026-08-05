"""F-021 — `--fill-feature-7` writes one column, in place, and aborts on anything else.

⚠ WHY A NARROW MODE AND NOT THE OBVIOUS COMMAND.  The obvious remedy for a NULL feature 7 was
`extract_features.py --all --load`.  Verified against the tree, that would have done three
things nobody intended:

  1. `extract_features.py:181` is `session.add(ProteinFeatures(...))` -- a PURE INSERT.  No
     delete, no upsert.  `protein_features` holds 80 rows; `--all --load` makes it **160**, in
     two generations, and the fit's assembler would then have to choose between them.
  2. It rewrites features 1-6.  F-004's stored RESULT is safe (id=2 is read from its row), but
     F-004's INPUTS would stop being reproducible from the database.  The result survives; its
     derivation does not.
  3. `ranking_run_id` defaults to `order_by(RankingRun.id.desc()).first()` -- **id=4,
     `plddt_only`** -- on a docstring assumption that was true when one run existed and is
     false now that four do.

⚠ It runs clean, prints a row count, and reddens nothing.  *Fix what is broken and abort on
everything else* is the entire difference between this mode and that command.

⚠ A-017 (the fixture must reach the code under test).  Several fixtures below are paired with a
positive control asserting the path was ENTERED.  A revert can red at exactly the right
assertion and still prove nothing if the code never ran -- which is how a revert proof in Task A
passed while proving nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import extract_features as ef  # noqa: E402
from core.features import FeatureRow  # noqa: E402
from db.models import Base, ProteinAnalysis, ProteinFeatures, RankingRun  # noqa: E402

SIX = dict(ecd_length=311.0, radius_of_gyration=18.25, mean_plddt_ecd=77.5,
           membrane_proximal_plddt=71.0, sasa_normalized=0.4125, largest_patch_fraction=0.2875)


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _seed(eng, n=3, *, f7=None, run_id=None):
    """n analyses, each with ONE protein_features row carrying the six and a NULL feature 7."""
    with Session(eng) as s:
        if run_id is not None:
            s.add(RankingRun(id=run_id, target_list_version="T", scorer_version="v", run_kind="preregistered"))
        for i in range(n):
            # ⚠ `disposition` comes from ProteinAnalysis.meta and `mean_plddt` from the feature
            # row -- both are inputs to `_exclusion_reason`. Omitting them made every row read as
            # `not_folded`, which is how the A-017 control below caught its sibling comparing
            # set() to set() and calling it agreement.
            a = ProteinAnalysis(id=100 + i, input_type="accession", input_value=f"P{i:05d}",
                                meta={"gene": f"G{i}", "disposition": "ranked"})
            s.add(a)
            s.add(ProteinFeatures(analysis_id=100 + i, ranking_run_id=run_id,
                                  membrane_proximal_sasa=f7, feature_version="fv1",
                                  mean_plddt=71.5, below_plddt_floor=False,
                                  **SIX))
        s.commit()
    return eng


def _records(eng, *, f7=9.5, six_override=None):
    """One ExtractedRecord per seeded analysis, recomputing the SAME six unless overridden."""
    with Session(eng) as s:
        ids = [r.analysis_id for r in s.execute(select(ProteinFeatures)).scalars()]
    out = []
    for k, aid in enumerate(sorted(ids)):
        six = dict(SIX)
        if six_override and aid in six_override:
            six.update(six_override[aid])
        out.append(ef.ExtractedRecord(
            accession=f"P{k:05d}", gene=f"G{k}", analysis_id=aid, disposition="ranked",
            tier="local", boundary_method="uniprot",
            row=FeatureRow(membrane_proximal_sasa=f7, feature_version="fv1", **six),
        ))
    return out


def _snapshot(eng):
    """Every column of every row, so 'only feature 7 changed' is checkable rather than asserted."""
    with Session(eng) as s:
        rows = s.execute(select(ProteinFeatures).order_by(ProteinFeatures.analysis_id)).scalars().all()
        return [{c.name: getattr(r, c.name) for c in ProteinFeatures.__table__.columns} for r in rows]


# ── the load-bearing one: abort on drift ─────────────────────────────────────
def test_a_changed_feature_1_to_6_aborts_the_whole_fill():
    """⚠ THE task. Not 'writes the rows that matched and reports the rest' -- that is the
    corrupting command wearing a report. Prove it bites by writing the matching rows anyway:
    row 101's feature 7 becomes non-null and the `nothing written` assertion reds."""
    eng = _seed(_engine(), n=3)
    before = _snapshot(eng)
    recs = _records(eng, six_override={101: {"radius_of_gyration": 18.26}})   # one row drifts

    with pytest.raises(ef.FeatureDrift) as exc:
        ef.fill_feature_7(eng, recs, dry_run=False)

    msg = str(exc.value)
    assert "101" in msg, f"the drifting row must be NAMED: {msg!r}"
    assert "18.25" in msg and "18.26" in msg, f"BOTH values must be printed: {msg!r}"
    assert _snapshot(eng) == before, "a drift aborted the fill but rows were still written"


def test_a_drift_writes_nothing_even_for_the_rows_that_matched():
    """⚠ The 'whole fill' half of the abort, asserted INDEPENDENTLY of the raise.

    `test_a_changed_feature_1_to_6_aborts_the_whole_fill` reds at `DID NOT RAISE` under the
    'write the matching rows anyway' revert -- so its snapshot assertion never executes and the
    partial-write property goes unproven. This test swallows the exception so the snapshot
    comparison is the ONLY assertion, and reds on the two rows that did match."""
    eng = _seed(_engine(), n=3)
    before = _snapshot(eng)
    recs = _records(eng, six_override={101: {"radius_of_gyration": 18.26}})
    try:
        ef.fill_feature_7(eng, recs, dry_run=False)
    except ef.FeatureDrift:
        pass
    after = _snapshot(eng)
    written = [r["analysis_id"] for b, r in zip(before, after)          # noqa: B905
               if b["membrane_proximal_sasa"] != r["membrane_proximal_sasa"]]
    assert written == [], (
        "the fill wrote the rows that matched and aborted on the rest -- that is the corrupting "
        f"command wearing a report. rows written: {written}")


def test_the_drift_fixture_actually_reaches_the_write_path():
    """⚠ A-017 positive control for the test above. With NO drift the same fixture must reach
    the write and change feature 7 -- otherwise the abort test could pass because nothing ever
    ran, and its revert would prove nothing."""
    eng = _seed(_engine(), n=3)
    res = ef.fill_feature_7(eng, _records(eng), dry_run=False)
    assert res["written"] == 3, res
    assert all(r["membrane_proximal_sasa"] == 9.5 for r in _snapshot(eng))


# ── update, never insert ─────────────────────────────────────────────────────
def test_fill_updates_and_never_inserts():
    """Prove it bites by restoring `session.add(...)`: the count goes 3 -> 6 and this reds."""
    eng = _seed(_engine(), n=3)
    assert len(_snapshot(eng)) == 3
    ef.fill_feature_7(eng, _records(eng), dry_run=False)
    assert len(_snapshot(eng)) == 3, "the fill INSERTED; protein_features must not grow"


def test_fill_writes_only_feature_7():
    """Every other column byte-identical, per row. Prove it bites by writing a second column."""
    eng = _seed(_engine(), n=3)
    before = _snapshot(eng)
    ef.fill_feature_7(eng, _records(eng), dry_run=False)
    after = _snapshot(eng)
    for b, a in zip(before, after):                                   # noqa: B905
        changed = {k for k in b if b[k] != a[k]}
        assert changed == {"membrane_proximal_sasa"}, f"columns changed beyond feature 7: {changed}"


def test_fill_does_not_touch_ranking_run_id():
    """⚠ The id=4 (`plddt_only`) hazard. The fill creates no rows, so it needs no run, and it
    must not rebind the ones it updates. Prove it bites by setting ranking_run_id in the update."""
    eng = _seed(_engine(), n=2, run_id=2)
    ef.fill_feature_7(eng, _records(eng), dry_run=False)
    assert {r["ranking_run_id"] for r in _snapshot(eng)} == {2}


# ── the dry run's read-only-ness is a TESTED property, not a flag's promise ──
def test_dry_run_writes_nothing():
    """⚠ The dry run is the only thing between 'features 1-6 drifted' and a production write,
    and the owner executes it, not Code. Its read-only-ness must be tested, not promised.

    Prove it bites by making the dry-run path fall through to the write: feature 7 becomes
    non-null and this reds on the snapshot comparison, having reached the write path."""
    eng = _seed(_engine(), n=3)
    before = _snapshot(eng)
    res = ef.fill_feature_7(eng, _records(eng), dry_run=True)
    assert _snapshot(eng) == before, "the DRY RUN wrote to the database"
    assert res["would_write"] == 3, res


def test_the_dry_run_fixture_actually_reaches_the_write_path():
    """⚠ A-017 positive control for the dry-run test. The identical fixture with dry_run=False
    must write, so `test_dry_run_writes_nothing` cannot pass because there was nothing to do."""
    eng = _seed(_engine(), n=3)
    before = _snapshot(eng)
    ef.fill_feature_7(eng, _records(eng), dry_run=False)
    assert _snapshot(eng) != before, "the fixture writes nothing even when asked to"


def test_dry_run_reports_the_same_comparison_as_the_write():
    """The dry run's 1-6 comparison is the owner's stop condition, so it must be the same
    computation the write performs. Prove it bites by comparing only on the write path."""
    eng = _seed(_engine(), n=3)
    recs = _records(eng, six_override={101: {"ecd_length": 999.0}})
    with pytest.raises(ef.FeatureDrift):
        ef.fill_feature_7(eng, recs, dry_run=True)


# ── idempotence + the deleted default ────────────────────────────────────────
def test_fill_is_idempotent():
    """Second run writes zero rows and says so. Prove it bites by re-writing non-null rows."""
    eng = _seed(_engine(), n=3)
    first = ef.fill_feature_7(eng, _records(eng), dry_run=False)
    second = ef.fill_feature_7(eng, _records(eng), dry_run=False)
    assert first["written"] == 3 and second["written"] == 0, (first, second)
    assert second["already_present"] == 3, second


def test_fill_writes_only_where_feature_7_is_null():
    """An existing measured value is never overwritten -- including a legitimate 0.0."""
    eng = _seed(_engine(), n=2, f7=0.0)
    ef.fill_feature_7(eng, _records(eng, f7=9.5), dry_run=False)
    assert {r["membrane_proximal_sasa"] for r in _snapshot(eng)} == {0.0}, (
        "a measured 0.0 was treated as absent and overwritten")


def test_load_requires_an_explicit_ranking_run():
    """⚠ The latest-run default is DELETED, not corrected -- it silently resolved to id=4
    (`plddt_only`). Prove it bites by restoring the default: `--load` stops refusing."""
    with pytest.raises(SystemExit):        # argparse rejects it before any DB work
        ef.run(["--all", "--load"], client_factory=_exploding_client,
               engine_factory=_exploding_engine)


def test_load_still_works_when_the_ranking_run_is_named():
    """⚠ A-017 positive control for the test above: `--load --ranking-run N` must get PAST
    argument parsing, so the refusal is about the missing flag and not about `--load` itself."""
    with pytest.raises(RuntimeError, match="client"):     # reached the client, i.e. past argparse
        ef.run(["--all", "--load", "--ranking-run", "2"], client_factory=_exploding_client,
               engine_factory=_exploding_engine)


# ── the ranking-set coverage the owner's stop condition needs ────────────────
def test_the_fill_reports_ranking_set_coverage():
    """⚠ Task C stop condition 2 is the OWNER's to evaluate, at the keyboard, before the bytes
    land. A coverage number confirmed by Code afterward is on the wrong side of the write.

    Prove it bites by dropping the coverage keys from the result: the owner's gate has nothing
    to read and this reds."""
    eng = _seed(_engine(), n=3)
    res = ef.fill_feature_7(eng, _records(eng), dry_run=True, ranking_set_ids={100, 101})
    assert res["ranking_set_total"] == 2, res
    assert res["ranking_set_covered"] == 2, res
    assert res["would_write"] == 3, "the fill still covers all 3 rows, not just the ranking set"


def test_a_ranking_set_row_outside_the_fill_is_reported_uncovered():
    """⚠ The halt case, and the reason the two clauses are separate. The fill's population
    (every row with coordinates) and the guard's population (the ranking set) are different sets
    BY DESIGN -- the original condition conflated them and would have halted on the correct
    outcome. Prove it bites by counting coverage over all rows instead of the ranking set."""
    eng = _seed(_engine(), n=3)
    recs = [r for r in _records(eng) if r.analysis_id != 102]      # 102 not in this fill
    res = ef.fill_feature_7(eng, recs, dry_run=True, ranking_set_ids={100, 101, 102})
    assert res["ranking_set_total"] == 3, res
    assert res["ranking_set_covered"] == 2, (
        "a ranking-set row absent from the fill must read as UNCOVERED", res)


def test_an_already_filled_ranking_row_still_counts_as_covered():
    """Coverage asks 'will every ranking-set row have a value after this fill?', not 'will this
    fill write to it'. An already-measured row is covered. Prove it bites by counting only the
    rows this run writes."""
    eng = _seed(_engine(), n=2, f7=7.5)                            # both already measured
    res = ef.fill_feature_7(eng, _records(eng), dry_run=True, ranking_set_ids={100, 101})
    assert res["would_write"] == 0 and res["ranking_set_covered"] == 2, res


def test_coverage_counts_only_ranking_set_rows():
    """⚠ The conflation the amendment corrected: the fill's population (every row with
    coordinates) is NOT the guard's population (the ranking set), and the original stop condition
    treated them as one -- so it would have halted on the correct outcome.

    Prove it bites by dropping the `rs &` intersection: coverage then reports 3 of 2, counting a
    row the guard never asks about."""
    eng = _seed(_engine(), n=3)
    res = ef.fill_feature_7(eng, _records(eng), dry_run=True, ranking_set_ids={100, 101})
    assert res["would_write"] == 3, "the fill must still cover every row, ranking set or not"
    assert res["ranking_set_total"] == 2, res
    assert res["ranking_set_covered"] == 2, res
    assert res["ranking_set_covered"] <= res["ranking_set_total"], (
        "coverage exceeded the ranking set -- rows outside the guard's population were counted", res)


def _seed_mixed(eng):
    """⚠ A cohort that GENUINELY discriminates: one ranked row, and one `held_out` row whose
    pLDDT is comfortably above the floor. A predicate that looks only at pLDDT keeps the held-out
    row; `fit_scorer`'s keeps it out. Without that asymmetry the agreement test below compares
    two functions that both return 'everything' and calls it agreement."""
    with Session(eng) as s:
        for i, disp in enumerate(("ranked", "held_out")):
            s.add(ProteinAnalysis(id=200 + i, input_type="accession", input_value=f"Q{i:05d}",
                                  meta={"gene": f"H{i}", "disposition": disp}))
            s.add(ProteinFeatures(analysis_id=200 + i, membrane_proximal_sasa=None,
                                  feature_version="fv1", mean_plddt=88.0,
                                  below_plddt_floor=False, **SIX))
        s.commit()
    return eng


def test_ranking_set_membership_is_not_re_derived_in_this_script():
    """⚠ THE anti-two-paths test. Membership is `ranked ∧ folded ∧ pLDDT >= 50 ∧ six present`,
    defined once in `fit_scorer`. Re-implementing it here would be a second path to one quantity
    -- the class that produced the F-017 double-claim, the producer/consumer schema mismatch, and
    the census key defined twice, all on 2026-08-05 alone.

    Prove it bites by hand-rolling the predicate here: a pLDDT-only version keeps the held-out
    row and diverges."""
    import fit_scorer as fs
    eng = _seed_mixed(_seed(_engine(), n=1))
    mine = ef.ranking_set_analysis_ids(eng)
    recs = fs.read_feature_records(eng)
    rows = fs.build_scorer_rows(recs, group_b_accessions=set(), evidence_by_symbol={})
    theirs = {rec.analysis_id for rec, row in zip(recs, rows)       # noqa: B905
              if row.in_ranking_set and rec.analysis_id is not None}
    assert mine == theirs, (mine, theirs)


def test_the_membership_fixture_actually_discriminates():
    """⚠ A-017 positive control for the test above, and it has already earned its place twice:
    once when the fixture excluded EVERY row (so agreement was `set() == set()`), and once when
    it excluded NOTHING (so a pLDDT-only hand-roll agreed by accident). Both directions asserted."""
    eng = _seed_mixed(_seed(_engine(), n=1))
    ids = ef.ranking_set_analysis_ids(eng)
    assert 201 not in ids, "the held-out row is in the ranking set -- the fixture excludes nothing"
    assert 200 in ids and 100 in ids, "the fixture excludes everything, so agreement proves nothing"


def _exploding_client():
    raise RuntimeError("client must not be built in these tests")


def _exploding_engine():
    raise RuntimeError("engine must not be built in these tests")
