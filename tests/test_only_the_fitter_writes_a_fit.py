"""`D-079` decision 1's last clause, closed: **only the fitter may write a fit.**

⚠⚠ WHY THIS EXISTS. `D-079 amendment 5` audited *"no refit — `ranking_run` id=2 is read from its
row"* and found it TRUE but **contained rather than asserted**: `scripts/fit_scorer.py` is absent
from the deployed image, so no refit can happen there — but nothing checked that some *other*
module could not write one. *The clause was true because nobody had refitted.*

⚠ That is exactly what the sibling clause rested on before `D-079 amendment 4` found it was
fiction: the census→scorer import bar was asserted **by name** in the decision text and did not
exist. **Having been wrong once in this decision, "nobody does it" is not left as the guard twice.**

WHAT IS PINNED, and it is a property rather than a state: a unit test cannot see production, so it
does not try. It asserts that **no code path outside `scripts/fit_scorer.py` constructs a
`TargetScore` or a `RankingResult`** — the two rows that make a run a *fit*. A refit that cannot be
written by anything else is contained by the code, not by the packaging.
"""

from __future__ import annotations

import ast
import pathlib

from _tracked_sources import tracked_files

REPO = pathlib.Path(__file__).resolve().parent.parent
SEARCH_DIRS = ("app", "core", "db", "scripts", "worker")

#: The rows that make a ranking run a FIT. Only the fitter may construct them.
FIT_ROWS = ("TargetScore", "RankingResult")

#: `db/models.py` DEFINES them; `scripts/fit_scorer.py` is the fitter and is the point of the rule.
FIT_WRITERS = {"scripts/fit_scorer.py"}
EXEMPT = {"db/models.py"}

#: ⚠ `RankingRun` is a different object: `core/enqueue.py` creates one to group a fold batch, with
#: an EMPTY `scorer_version` and no scores. That is not a fit. Allowed, and named so the allowance
#: is deliberate rather than an oversight.
RUN_CONSTRUCTORS = {"scripts/fit_scorer.py", "core/enqueue.py"}


# ⚠⚠ TRACKED FILES ONLY. This walked the filesystem until 2026-09-04, when another
# bot team's untracked, BOM-prefixed script made five tests red locally while CI stayed green.
# An untracked file is another team's working state, not this repository's code under test.
# ⚠ The refusal to SKIP an unparseable tracked file is unchanged — see Unparseable below.
def _python_files() -> list[pathlib.Path]:
    return tracked_files(REPO, SEARCH_DIRS)


class Unparseable(AssertionError):
    """⚠⚠ A file in the tree that this interpreter cannot parse. NOT skipped, and not swallowed.

    Found on the first run of this test: `scripts/kc1_engulfing_range.py` used a nested same-quote
    f-string — PEP 701, Python 3.12+ — while the venv and CI both run 3.11. It had been committed
    days earlier because it was authored and executed under a 3.14 interpreter by mistake, and no
    test had ever parsed `scripts/`. ⚠ A guard that skipped it would have hidden a file that cannot
    run at all, which is worse than the rule this test exists to enforce.
    """


def _constructions(rel: str, names: tuple[str, ...]) -> list[str]:
    """Every `Name(...)` call constructing one of `names`, as 'file:line'."""
    src = (REPO / rel).read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:  # noqa: PERF203
        raise Unparseable(
            f"{rel}:{e.lineno} does not parse under this interpreter — {e.msg}. "
            f"A file the project's own Python cannot read is a defect, not a reason to skip."
        ) from e
    return [f"{rel}:{n.lineno}" for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in names]


def _scan(names: tuple[str, ...]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for p in _python_files():
        rel = p.relative_to(REPO).as_posix()
        if rel in EXEMPT:
            continue
        hits = _constructions(rel, names)
        if hits:
            found[rel] = hits
    return found


def test_only_the_fitter_constructs_a_fit():
    """⚠⚠ THE CLAUSE, AS A PROPERTY. A `TargetScore` or `RankingResult` built anywhere else is a
    second path to a fit, and `D-079` dec 1 permits exactly none."""
    found = _scan(FIT_ROWS)
    rogue = {k: v for k, v in found.items() if k not in FIT_WRITERS}
    assert not rogue, (
        "these construct a fit outside scripts/fit_scorer.py — D-079 dec 1 bars a refit:\n  "
        + "\n  ".join(f"{k}: {', '.join(v)}" for k, v in sorted(rogue.items())))


def test_the_detector_actually_finds_the_fitters_own_writes():
    """⚠ `F-045`: a proof that cannot fail is not a proof. If the scan finds nothing anywhere, the
    test above passes vacuously — and it would keep passing after someone narrowed `SEARCH_DIRS`
    or renamed the models. Pin that it reaches the one file that legitimately writes a fit."""
    found = _scan(FIT_ROWS)
    assert "scripts/fit_scorer.py" in found, (
        "the detector no longer sees the fitter's own TargetScore/RankingResult construction — "
        "the scan was narrowed and the rule above silently stopped being checked")
    assert len(found["scripts/fit_scorer.py"]) >= 2, found["scripts/fit_scorer.py"]


def test_ranking_run_creation_is_confined_and_the_allowance_is_deliberate():
    """⚠ A `RankingRun` is not a fit. `core/enqueue.py` creates one to group a fold batch, with an
    empty `scorer_version` and no scores — measured in production as 0 rows, because it reuses an
    existing run first. The allowance is pinned so a THIRD creator cannot appear unnoticed."""
    found = _scan(("RankingRun",))
    rogue = {k: v for k, v in found.items() if k not in RUN_CONSTRUCTORS}
    assert not rogue, (
        "a new RankingRun constructor appeared:\n  "
        + "\n  ".join(f"{k}: {', '.join(v)}" for k, v in sorted(rogue.items())))


def test_the_enqueue_path_never_writes_a_fit_beside_its_run():
    """⚠⚠ The allowance above is only safe while `enqueue` writes a run and NOTHING ELSE. A
    `TargetScore` appearing in that module would turn a permitted grouping into a fit."""
    assert not _constructions("core/enqueue.py", FIT_ROWS), (
        "core/enqueue.py constructs a fit row — its RankingRun allowance assumes it does not")


def test_the_serving_tier_cannot_write_a_fit_at_all():
    """The tier that is actually deployed, checked separately from the repo-wide rule — `app/` and
    `core/` ship; `scripts/` (bar one ingest) and `worker/` do not."""
    for d in ("app", "core"):
        hits = {k: v for k, v in _scan(FIT_ROWS).items() if k.startswith(f"{d}/")}
        assert not hits, f"the deployed tier can construct a fit: {hits}"
