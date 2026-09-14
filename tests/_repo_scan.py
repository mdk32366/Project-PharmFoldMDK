"""Repo-scanning helpers, built so a detector cannot match its own source or untracked debris.

⚠⚠ **D-145 amendment 1 makes this a CONVENTION rather than a caution.** The trap has now fired
four times in one wave:

1. a conftest check for `pytest_collection_modifyitems` matched the docstring explaining why that
   hook was abandoned;
2. a bootstrap check for `alembic` matched the sentence saying the marker must not arrive by
   migration;
3. a proof script's forbidden-word list matched **itself**, because the list contained the words;
4. the same script's `import pytest` check matched the docstring promising there isn't one.

**Four instances says the pattern is structural, not incidental.** Any detector that scans the
repository will match its own source unless it is built not to — so the exclusion stops being
something each author remembers and becomes something the helper does.

⚠ And the second half, from the owner's 2026-09-15 ruling on the standing local reds: **a detector
scoped to what its author could see is the same defect `.gitattributes` records about itself.**
`ROOT.rglob(...)` walks gitignored trees — on this machine, 27 GB of real fold artifacts and
whatever ops debris was left there — so a guard asserting *"this suite created no such tree"*
reports failure on a directory from a different month. **Scope the walk to tracked files.**
"""

from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def tracked_files() -> list[Path]:
    """Every file git tracks, as absolute paths. ⚠ Untracked and ignored paths are excluded by
    construction — that is the point, not an optimisation."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO,
                         capture_output=True, text=True).stdout
    return [REPO / rel for rel in out.split("\0") if rel]


def tracked_dirs_named(name: str) -> list[Path]:
    """Tracked directories called `name`, derived from tracked FILES.

    ⚠ A directory is "tracked" only in the sense that git tracks something inside it — git has no
    notion of an empty tracked directory, and pretending otherwise is how this check would go
    quietly vacuous.
    """
    hits = {p.parent for p in tracked_files() if p.parent.name == name}
    hits |= {anc for p in tracked_files() for anc in p.parents if anc.name == name}
    return sorted(hits)


def _caller_source() -> Path | None:
    """The file of the first frame outside this module."""
    for frame in inspect.stack()[1:]:
        path = Path(frame.filename).resolve()
        if path != Path(__file__).resolve():
            return path
    return None


def sources_to_scan(*prefixes: str, exclude_self: bool = True) -> list[Path]:
    """Tracked files under `prefixes`, **excluding the caller's own source by construction**.

    ⚠⚠ `exclude_self` defaults to `True` and that default is the convention. A detector that has
    to remember to exclude itself is a detector that will forget — four times in one wave, on this
    project, by two different authors.
    """
    me = _caller_source() if exclude_self else None
    keep = []
    for path in tracked_files():
        rel = path.relative_to(REPO).as_posix()
        if prefixes and not rel.startswith(prefixes):
            continue
        if me is not None and path.resolve() == me:
            continue
        keep.append(path)
    return keep
