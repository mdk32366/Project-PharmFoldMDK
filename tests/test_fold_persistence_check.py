"""Amended Task 3.3's guard — both halves, and neither alone.

⚠⚠ The defect this exists for: the original *"confirm PAE lands"* is satisfied by a file on disk
with a NULL column, and by a populated column pointing at nothing. **Each half passes a fold the
other would fail**, which is why the check is two clauses and the outcomes are named rather than
boolean.
"""
from __future__ import annotations

from core.fold_persistence_check import (
    COLUMN_NULL,
    FILE_MISSING,
    NO_PAE_EMITTED,
    OK,
    check_fold_persistence,
    summarise,
)


def _never(_p: str) -> bool:
    return False


def _always(_p: str) -> bool:
    return True


def test_the_happy_path_needs_both_halves_true():
    v = check_fold_persistence(1, emitted_pae=True,
                               pae_json_path="/data/artifacts/1/pae.json.gz", exists=_always)
    assert v.outcome == OK and not v.is_fatal


def test_a_file_on_disk_with_a_null_column_is_the_SILENT_HALF_FIX_and_is_fatal():
    """⚠⚠ Gate A wrote the file; Gate B never ran. The original wording would have passed this."""
    v = check_fold_persistence(2, emitted_pae=True, pae_json_path=None, exists=_always)
    assert v.outcome == COLUMN_NULL
    assert v.is_fatal, "a NULL column must stop the campaign — every later fold breaks the same way"


def test_a_populated_column_pointing_at_nothing_is_fatal_and_is_a_DIFFERENT_failure():
    """⚠⚠ A PATH IS NOT A FILE — F-042's open decision 3, which a non-NULL count cannot answer."""
    v = check_fold_persistence(3, emitted_pae=True,
                               pae_json_path="/data/artifacts/3/pae.json.gz", exists=_never)
    assert v.outcome == FILE_MISSING
    assert v.is_fatal
    assert v.outcome != COLUMN_NULL, (
        "the two fatal outcomes must stay distinguishable — they need different investigations")


def test_a_fold_that_emitted_no_pae_is_a_NAMED_outcome_and_not_a_failure():
    """⚠ F-033's class: an absence reported as the wrong kind of error. A fold with no PAE cannot
    have persisted one, and failing it would fire the guard on a legitimate result."""
    v = check_fold_persistence(4, emitted_pae=False, pae_json_path=None, exists=_never)
    assert v.outcome == NO_PAE_EMITTED and not v.is_fatal


def test_neither_half_alone_would_discriminate():
    """⚠⚠ THE POINT OF THE AMENDMENT, ASSERTED. A column-only check passes the missing file; a
    file-only check passes the NULL column. Only both together reject both."""
    column_only = check_fold_persistence(5, emitted_pae=True, pae_json_path="/p", exists=_never)
    file_only = check_fold_persistence(6, emitted_pae=True, pae_json_path=None, exists=_always)
    assert column_only.is_fatal, "a column-only check would have passed this fold"
    assert file_only.is_fatal, "a file-only check would have passed this fold"


def test_the_summary_reports_the_breakdown_and_never_a_pass_rate():
    """⚠ '19 of 20 OK' hides which one failed and how. The breakdown is the deliverable."""
    verdicts = [
        check_fold_persistence(1, emitted_pae=True, pae_json_path="/a", exists=_always),
        check_fold_persistence(2, emitted_pae=True, pae_json_path=None, exists=_always),
        check_fold_persistence(3, emitted_pae=True, pae_json_path="/c", exists=_never),
        check_fold_persistence(4, emitted_pae=False, pae_json_path=None, exists=_never),
    ]
    s = summarise(verdicts)
    assert s["n"] == 4
    assert s["counts"] == {OK: 1, COLUMN_NULL: 1, FILE_MISSING: 1, NO_PAE_EMITTED: 1}
    assert s["may_continue"] is False
    assert len(s["fatal"]) == 2, "both fatal kinds must survive into the report separately"


def test_a_clean_run_may_continue():
    verdicts = [check_fold_persistence(i, emitted_pae=True, pae_json_path=f"/{i}", exists=_always)
                for i in range(3)]
    s = summarise(verdicts)
    assert s["may_continue"] is True and s["counts"] == {OK: 3}
