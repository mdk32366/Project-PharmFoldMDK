"""DEP-002 — the deploy job's doc-only guard, tested before it is wired.

The guard lives on the JOB, never the trigger (DEP-002, forced by D-008): `test` and
`postgres` run on every PR/push, and only the *deploy step* is conditional on the change
not being docs-only. The detection — "are all changed paths under `docs/**` or `*.md`?" —
is the unit under test here, extracted into `scripts/deploy_guard.is_docs_only` so both
this test and the CI job call the same code rather than the job re-implementing it in bash.
"""

from __future__ import annotations

import pytest

from scripts.deploy_guard import is_docs_only


@pytest.mark.parametrize("paths", [
    ["docs/README.md"],
    ["docs/README.md", "docs/PREWORK-deployment-arc.md"],
    ["ARCHITECTURE.md", "CLAUDE.md"],          # root *.md are docs (DEP-002: "docs/** and *.md")
    ["docs/sub/nested.txt"],                    # anything under docs/ is a doc
    ["docs/README.md", "", "  "],              # blank lines from `git diff` output are ignored
])
def test_docs_only_changes_skip_deploy(paths):
    assert is_docs_only(paths) is True


@pytest.mark.parametrize("paths", [
    ["app/routes.py"],                          # code only
    ["docs/README.md", "app/main.py"],         # mixed: one code file means NOT docs-only
    ["Dockerfile"],
    ["requirements.lock"],
    [".github/workflows/gate.yml"],
    ["core/contracts.py", "docs/README.md"],
])
def test_code_changes_run_deploy(paths):
    assert is_docs_only(paths) is False


def test_empty_changeset_is_not_docs_only():
    # An empty set is not "docs-only" in any meaningful sense — there are no docs in it.
    # Treating it as not-docs-only means a (rare) empty diff errs toward deploying, which is
    # idempotent, rather than toward silently skipping.
    assert is_docs_only([]) is False
