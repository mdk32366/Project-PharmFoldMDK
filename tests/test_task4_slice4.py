"""Task 4, slice 4 — band 101–250, n = 600. Owner-authorised 2026-09-15, scope per `D-161`.

⚠⚠ **This slice is the first that can state NO fold-time floor**, and that is the property most of
these tests defend. Slices 1–3 each had a sample of their own band to floor against. This one does
not: slice 3 measured 20.3 s at **mean span 47.3 aa** and this band averages **174.6**, with
`F-059` recording the fold's incremental VRAM as O(L²) — so the relationship is not linear outside
the range it was measured in. Borrowing slice 3's number would be `D-157 amendment 4`'s exact
subject, one band further along.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SRC = (REPO / "scripts" / "task4_slice4.py").read_text(encoding="utf-8")

slice4 = pytest.importorskip("scripts.task4_slice4")


def test_the_band_and_the_count_are_D161s_ruling():
    """⚠ `D-161` ruled slice 4 IN at 600 rows, band 101–250 — not the 735 the arithmetic
    suggested. The script encodes the ruling, not the arithmetic."""
    assert slice4.BAND == (101, 250)
    assert slice4.EXPECTED_N == 600


def test_the_band_enumerates_to_exactly_600_and_reconciles_by_tranche():
    """⚠⚠ `D-161` §3: t2 = 216, t3 = 384, and NO tranche 1 or tranche 4 row falls in this band.
    A filter that silently dropped one would still total 600 only by luck, so the split is
    asserted as well as the total — `D-162` rule 6's first clause."""
    rows = slice4.the_band()
    assert len(rows) == 600
    by_tranche: dict[int, int] = {}
    for r in rows:
        by_tranche[int(r["tranche"])] = by_tranche.get(int(r["tranche"]), 0) + 1
    assert by_tranche == {2: 216, 3: 384}
    spans = [int(r["span"]) for r in rows]
    assert min(spans) == 101 and max(spans) == 250
    assert round(sum(spans) / len(spans), 1) == 174.6, "D-161 recorded the mean as 174.6"


def test_this_slice_states_NO_fold_time_floor_and_NO_transport_term():
    """⚠⚠ THE PROPERTY. Both terms are unmeasured for this band and both are declared absent."""
    assert slice4.FOLD_S is None, (
        "a fold-time floor was borrowed from a band with a different mean span")
    assert slice4.TRANSPORT_S is None
    p = slice4.projection()
    assert p["fold_only_h"] is None and p["elapsed_h"] is None
    assert "UNMEASURED" in p["fold_status"] and "UNMEASURED" in p["transport_status"]


def test_no_measured_value_from_another_band_is_carried_as_a_CONSTANT():
    """⚠ The three measured transport values may be NAMED as comparators and must never be
    assigned. `D-157 amendment 4` retracted the per-fold-constant framing; this is that retraction
    held in code."""
    tree = ast.parse(SRC)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, float):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                assert node.value.value not in (0.7, 0.9, 0.90, 4.7, 16.5, 20.3), (
                    f"{names} assigns a transport or fold value measured in another band")


def test_the_two_preconditions_are_stated_in_the_file_itself():
    """⚠⚠ Both are orderings that nothing in the code can enforce, so the file has to carry them.

    1. The `F-078` 37 must not be claimable at the same time as these 600, or the per-band
       transport term — the campaign's whole product — is contaminated.
    2. `D-166`'s advisory lock is process-level. No UNIQUE index covers the Run-2 identity.
    """
    assert "F-078" in SRC and "contaminat" in SRC, (
        "the file does not warn that a restored 37 would share the claimable pool")
    assert "D-166" in SRC
    assert "not a constraint" in SRC or "A lock is not a constraint" in SRC, (
        "the file lets the advisory lock read as if it were a constraint")


def test_it_does_not_chain_to_a_further_slice_on_its_own_authority():
    """⚠ Slice 3 said `SLICE 4 REQUIRES A FRESH OWNER RULING`. That sentence has to move forward
    with the campaign or the last slice silently authorises the next one."""
    assert "SLICE 5 REQUIRES A FRESH OWNER RULING" in SRC
    assert "SLICE 5 IS NOT AUTHORISED" in SRC


def test_each_slice_writes_its_own_progress_record():
    """⚠ A shared progress file would let one slice's harvest overwrite another's."""
    from scripts import task4_slice3
    assert slice4.OUT_DIR != task4_slice3.OUT_DIR
    assert slice4.OUT_DIR.name == "task4_slice4"


def test_it_imports_the_machinery_rather_than_redefining_it():
    """⚠ `F-046`: a second copy is how two campaigns diverge under one name."""
    for name in ("SliceRun", "refuse_on_strangers", "write_clearance", "clearance_refusal",
                 "fold_shell_refusal"):
        assert name in SRC, f"{name} is not imported from the shared machinery"
    assert "class SliceRun" not in SRC, "SliceRun was copied rather than imported"


def test_the_stranger_guard_gates_the_claim_and_the_shell_split_holds():
    """⚠⚠ `D-160`: `--preflight` is tunnel-armed and seconds; `--fold` is a clean shell and hours,
    and it REFUSES a set `DATABASE_URL` rather than popping it."""
    assert "refuse_on_strangers" in SRC
    assert "fold_shell_refusal" in SRC
    tree = ast.parse(SRC)
    fold = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "fold")
    first = ast.dump(fold.body[0]) + ast.dump(fold.body[1] if len(fold.body) > 1 else fold.body[0])
    assert "fold_shell_refusal" in first, (
        "the clean-shell check is not the first thing fold() does")


def test_the_owed_restore_notice_survives_into_this_slice():
    """⚠⚠ The 37 are still owed. The notice is the only thing in the system that will ever raise
    its hand about them, because a NULL-tier job is claimable by nobody and the stranger guard
    deliberately does not count one."""
    assert "OWED, AND NOT YET DONE" in SRC
    assert "4869" in SRC and "4905" in SRC
    assert "517/517" in SRC


def test_the_notice_states_the_cut_from_the_DATABASE_not_the_backup_label():
    """⚠ `F-078` amendment 1: `fly mpg backup list` no longer reaches 2026-09-13, so the backup
    label cannot be re-read at source. The database cut can."""
    assert "15:24:36.578Z" in SRC, "the notice cites only the unverifiable leg"
    assert "64 ms" in SRC


def test_printed_strings_stay_ascii():
    """⚠ The console this runs on is not guaranteed UTF-8; a UnicodeEncodeError ten hours in
    would lose the harvest."""
    tree = ast.parse(SRC)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print":
            for arg in ast.walk(node):
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if any(ord(c) > 127 for c in arg.value):
                        bad.append(arg.value[:60])
    assert not bad, f"non-ASCII in printed strings: {bad}"


def test_the_OWED_RESTORE_lines_are_ascii_too():
    """⚠ They are printed by `--report` at the end of a long unattended run, which is the worst
    possible moment for an encoding error."""
    bad = [ln for ln in slice4.OWED_RESTORE if any(ord(c) > 127 for c in ln)]
    assert not bad, f"non-ASCII in the owed-restore notice: {bad}"
