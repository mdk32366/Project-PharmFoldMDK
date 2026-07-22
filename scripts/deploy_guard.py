"""DEP-002 — doc-only detection for the deploy job's guard.

`is_docs_only(paths)` is True iff there is at least one changed path and **every** changed
path is documentation — under `docs/` or ending in `.md`. The deploy job computes the
changed paths (`git diff` against the previous main commit) and skips the Fly deploy step
when this returns True, so a docs-only push runs the required checks (`test`/`postgres`,
D-032) but does not redeploy prod.

The guard lives on the JOB, never the trigger (DEP-002, forced by D-008): a `paths-ignore`
on the workflow would stop the *required* checks reporting on docs PRs and deadlock them.
Extracted here so the job and the test call the same code rather than the job
re-implementing the match in bash.

CLI: reads newline-separated paths on stdin, prints `true`/`false`:
    docs_only="$(git diff --name-only "$before" "$sha" | python scripts/deploy_guard.py)"
"""

from __future__ import annotations

from typing import Iterable


def _is_doc(path: str) -> bool:
    """A path is documentation if it is under `docs/` or ends in `.md` (DEP-002)."""
    return path.startswith("docs/") or path.endswith(".md")


def is_docs_only(paths: Iterable[str]) -> bool:
    """True iff there is at least one changed path and all of them are docs. An empty
    changeset is NOT docs-only — it errs toward deploying (idempotent) over silently
    skipping. Blank lines (from `git diff` output) are ignored."""
    cleaned = [p.strip() for p in paths if p and p.strip()]
    return bool(cleaned) and all(_is_doc(p) for p in cleaned)


if __name__ == "__main__":
    import sys

    print("true" if is_docs_only(sys.stdin.read().splitlines()) else "false")
