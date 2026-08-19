"""Every engine built from `DATABASE_URL` routes through `normalize_db_url`.

⚠⚠ WHY, AND IT IS THE THIRD TIME THIS SHAPE HAS BITTEN IN ONE SESSION. `db/dburl.py`'s own
docstring says *"This one helper is applied by BOTH the serving tier and the migration
environment, so a future re-attach ... cannot silently break either path again."* Five callers
observed it. The census ingest was the sixth engine-builder and the only one that did not — it
called `create_engine(url)` on the raw environment value, and on the production host that
resolved to psycopg2, which `D-012` deliberately does not install:

    ModuleNotFoundError: No module named 'psycopg2'

⚠ It failed AFTER passing every other guard — artifact hash verified, 2,690 rows loaded, outcome
vocabulary checked — because the connection is the last thing that happens. A guard that fires
late is still a guard, but the ones that would have caught it earlier are the ones that generalise.

⚠⚠ The convention existed, was documented, and was followed five times out of six. **A rule kept
by observation rather than by a check is a rule until someone new writes the sixth caller.**
That is the whole reason this file exists rather than a comment reminding people.
"""

from __future__ import annotations

import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
SEARCH_DIRS = ("app", "core", "db", "scripts", "worker")

# `db/dburl.py` defines the helper; `tests/` builds throwaway SQLite engines on purpose.
EXEMPT = {"db/dburl.py"}


def _python_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for d in SEARCH_DIRS:
        root = REPO / d
        if root.is_dir():
            out.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return out


def _calls_normalizer(tree: ast.AST) -> bool:
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "normalize_db_url" for n in ast.walk(tree))


def _violations() -> list[str]:
    """Files that build an engine from `DATABASE_URL` and never call the normalizer at all.

    ⚠⚠ THE FIRST VERSION OF THIS WAS STRICTER AND WRONG. It required the normalizer to wrap the
    first argument of `create_engine` — a coding SHAPE — and reddened on
    `scripts/taskb_pae_inventory.py`, which is correct: it normalizes inside `proxy_url()` and
    passes the result down. *A test that reddens on correct code is worse than no test*, and I
    had already said so about a prose-scanning guard earlier the same day.

    ⚠ What this checks now is the PROPERTY: the module routes its URL through the one helper
    somewhere. Honest about the residue — a file that normalizes on one path and not another
    passes this. Pinning the call site would catch that and re-break `taskb`; the narrower rule
    is the one that catches the mistake actually made (the ingest never mentioned the helper).
    """
    bad: list[str] = []
    for path in _python_files():
        rel = path.relative_to(REPO).as_posix()
        if rel in EXEMPT:
            continue
        src = path.read_text(encoding="utf-8")
        if "create_engine(" not in src or "DATABASE_URL" not in src:
            continue
        tree = ast.parse(src)
        if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id == "create_engine" for n in ast.walk(tree)):
            continue
        if not _calls_normalizer(tree):
            bad.append(rel)
    return bad


def test_no_engine_is_built_from_a_raw_database_url():
    bad = _violations()
    assert not bad, (
        "these build a SQLAlchemy engine from DATABASE_URL without normalize_db_url — on Fly's "
        "bare `postgresql://` they resolve to psycopg2, which D-012 does not install:\n  "
        + "\n  ".join(bad))


def test_the_detector_sees_the_callers_that_already_comply():
    """⚠ A detector that finds nothing proves nothing. `F-045`: a proof that cannot fail is not a
    proof. This pins that the scan actually reaches the files it claims to police, so a future
    edit that quietly narrows `SEARCH_DIRS` cannot turn the test above into a no-op."""
    seen = set()
    for path in _python_files():
        src = path.read_text(encoding="utf-8")
        if "create_engine(" in src and "normalize_db_url" in src:
            seen.add(path.relative_to(REPO).as_posix())
    for expected in ("core/enqueue.py", "scripts/fit_scorer.py",
                     "scripts/census_ingest_features.py"):
        assert expected in seen, (
            f"the detector no longer reaches {expected} — the scan was narrowed and the rule "
            f"above silently stopped being checked")


def test_normalize_db_url_is_idempotent_and_passes_sqlite_through():
    """The two properties every caller relies on, asserted here rather than assumed from the
    docstring — the ingest passes a SQLite DSN in tests and a bare Postgres URL in production."""
    from db.dburl import normalize_db_url

    bare = "postgresql://u:p@host:5432/db"
    once = normalize_db_url(bare)
    assert once.startswith("postgresql+psycopg://")
    assert normalize_db_url(once) == once, "not idempotent — a second call doubled the driver"
    assert normalize_db_url("sqlite:///x.db") == "sqlite:///x.db"
