"""Source enumeration for tree-scanning guards: what git TRACKS, never what happens to be on disk.

⚠⚠ WHY THIS EXISTS — measured 2026-09-04. A second bot team working in this repository wrote
``scripts/_emit_igf2r_pilot.py``, untracked and UTF-8-BOM-prefixed. Two AST guards walked the
filesystem, hit it, and died with ``SyntaxError: invalid non-printable character U+FEFF``.
**Five tests red locally. CI green throughout**, because a clean checkout has no untracked files.

⚠ **The guards were not wrong to refuse to skip an unparseable file** — that refusal is deliberate
and is preserved. **They were wrong about whose file it was.** An untracked file is not this
repository's code under test; it is another team's working state, and a guard that fails on it
reports a defect against the wrong team.

⚠ **This is a cross-team boundary, not a style preference.** You can audit what another team
committed. You cannot audit their working tree, and you should not fail on it.

⚠ **NO SILENT FALLBACK.** If git cannot be consulted, this raises. A fallback to ``rglob`` would
restore the exact defect on the exact machines where it is hardest to notice.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path


class GitUnavailable(RuntimeError):
    """⚠ Raised rather than falling back. A guard that quietly changes what it scans is not a guard."""


def tracked_files(repo: Path, dirs: Sequence[str], suffix: str = ".py") -> list[Path]:
    """Every git-tracked file under ``dirs`` ending in ``suffix``, as absolute paths.

    ⚠ Deleted-but-tracked paths are filtered: ``git ls-files`` lists the index, and a file removed
    from the working tree would otherwise be handed to a parser that cannot open it.
    """
    existing = [d for d in dirs if (repo / d).is_dir()]
    if not existing:
        return []
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--", *existing],
            cwd=repo, capture_output=True, check=True, text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover - environment
        raise GitUnavailable(
            f"git ls-files failed in {repo}. This guard scans TRACKED files only and will not "
            f"fall back to walking the filesystem: doing so would scan other teams' untracked "
            f"working state, which is how five tests went red on 2026-09-04."
        ) from exc

    paths = [repo / rel for rel in out.split("\0") if rel.endswith(suffix)]
    return [p for p in paths if p.is_file()]
