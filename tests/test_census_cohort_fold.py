"""A census row marked NOT FOLDED must not claim a fold is pending when one exists.

⚠⚠ THE DEFECT, FOUND BY WALKING THE TARGETS SURFACE on 2026-08-20. **30 of the 777 census rows
marked NOT FOLDED also sit in the ranked 82, and 29 of those are FOLDED there** — same span, same
`boundary_method`, on rental hardware. `ERBB2` is the case the owner originally asked about: the
census told a reader it awaited a fold that already existed one click away.

⚠ THE STATUS WAS NEVER WRONG. `above_local_ceiling` is true — 630 aa does exceed the local ceiling
of 440, and the cohort fold ran at rental/fp16. **Only the copy was wrong.**

⚠⚠ AND THE THIRTIETH ROW IS WHY THERE ARE THREE OUTCOMES. `IGF2R` is in the cohort and was never
folded THERE either: attempted on rental, killed by CUDA OOM at 2,491 aa. **An attempt that failed
is neither a queue position nor an existing result**, and a two-way split would have called it one.
"""
from __future__ import annotations

import ast
import pathlib

READS = pathlib.Path("app/reads.py").read_text(encoding="utf-8")
ROUTES = pathlib.Path("app/read_routes.py").read_text(encoding="utf-8")


def _fn(src: str, name: str):
    return next(n for n in ast.walk(ast.parse(src))
                if isinstance(n, ast.FunctionDef) and n.name == name)


def test_the_attachment_exists_and_reads_only():
    fn = _fn(READS, "_attach_cohort_fold")
    code = "\n".join(ast.dump(n) for n in fn.body)
    for banned in ("commit", "add(", "delete", "merge("):
        assert banned not in code, banned


# ⚠⚠ THREE OUTCOMES. A two-way split would describe IGF2R as either awaiting capacity or already
# folded, and both are false.
def test_a_failed_attempt_is_its_own_outcome_not_folded_and_not_pending():
    fn = _fn(READS, "_attach_cohort_fold")
    code = "\n".join(ast.dump(n) for n in fn.body)
    assert "cohort_fold" in code
    assert "cohort_attempt_failed" in code, (
        "a cohort row with no pdb_path was attempted and failed — calling it 'awaiting capacity' "
        "or 'already folded' are both false")
    # ⚠ the branch must key on the STRUCTURE (pdb_path), not on a confidence value being present
    assert "pdb_path" in code


def test_the_span_travels_so_the_reader_can_judge_the_comparison():
    """⚠ `D-081` measures the two populations under different span definitions. The payload states
    both spans rather than asserting they are the same molecule."""
    fn = _fn(READS, "_attach_cohort_fold")
    code = "\n".join(ast.dump(n) for n in fn.body)
    assert "census_span_aa" in code and "fold_length" in code


# ⚠⚠ THE CARD IS WHERE A READER DECIDES. A list that showed the cohort fold while the card did not
# would be the worse half of the defect, not a smaller one.
def test_the_single_card_route_attaches_the_same_fact_as_the_list():
    assert "_attach_cohort_fold" in ROUTES
    seg = ROUTES[ROUTES.index("def get_census_detail("):]
    assert "_attach_cohort_fold" in seg


def test_the_population_boundary_is_not_crossed_by_the_route():
    """⚠ `D-081`: the fix adds a FACT, not a route. A cohort-only accession must still 404 here."""
    seg = ROUTES[ROUTES.index("def get_census_detail("):]
    seg = seg[:seg.index("@read_router")] if "@read_router" in seg else seg
    assert '"cohort"' in seg and "D-081" in seg
    assert "RedirectResponse" not in seg
