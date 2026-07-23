"""DEP-001 — what the Fly image contains, asserted against the Dockerfile.

The image-bloat failure is invisible (a CUDA-laden image still works), so a reviewer's
eye is the wrong instrument — this is the assertion that makes DEP-001 stick. It reads the
Dockerfile and `.dockerignore` as text and checks the ruled contents: the runtime lock only,
`app/` + `core/` + `db/` copied, **no `worker/`, no torch/transformers/streamlit**.

This is the test that makes the FoldSpec relocation (DEP-001 Builder note) permanent: if a
future edit reaches back into `worker/` from the serving tier and the Dockerfile grows a
`COPY worker` or a torch install to satisfy it, this reddens.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "Dockerfile"
DOCKERIGNORE = ROOT / ".dockerignore"


@pytest.fixture
def dockerfile() -> str:
    """The Dockerfile's INSTRUCTIONS, comment lines stripped. DEP-001 is about what the image
    actually installs/copies, not what the comments say — a comment reading "no torch here" is
    correct and must not trip a torch check. A Dockerfile comment is a line whose first
    non-whitespace character is `#` (inline `#` is not a comment in Dockerfile syntax)."""
    assert DOCKERFILE.exists(), "DEP-001: the Fly image needs a Dockerfile at repo root"
    raw = DOCKERFILE.read_text(encoding="utf-8")
    return "\n".join(ln for ln in raw.splitlines() if not ln.lstrip().startswith("#"))


# ── the GPU world must never enter the serving image (DEP-001, D-004, D-018) ──

@pytest.mark.parametrize("forbidden", ["torch", "transformers", "bitsandbytes", "streamlit"])
def test_no_gpu_or_ui_stack_in_image(dockerfile, forbidden):
    assert forbidden not in dockerfile.lower(), \
        f"DEP-001: the serving image must not contain {forbidden!r}"


def test_does_not_copy_worker(dockerfile):
    # The single most important line: worker/ (the CUDA tier, D-004) is never copied in.
    lowered = dockerfile.lower()
    assert "copy worker" not in lowered and "add worker" not in lowered, \
        "DEP-001: worker/ must not be copied into the serving image"


def test_does_not_install_worker_or_dev_requirements(dockerfile):
    assert "worker/requirements.txt" not in dockerfile, \
        "DEP-001: the image installs the runtime lock, not worker/requirements.txt"
    assert "requirements-dev" not in dockerfile, \
        "DEP-001: the image installs requirements.lock, not the dev lock"


# ── the image installs exactly the hash-locked runtime tier (DEP-001, D-013) ──

def test_installs_hash_locked_runtime(dockerfile):
    assert "requirements.lock" in dockerfile, "DEP-001: install the runtime lock"
    assert "--require-hashes" in dockerfile, \
        "D-013: the image installs with --require-hashes, like the gate"


@pytest.mark.parametrize("pkg_dir", ["app", "core", "db"])
def test_copies_the_serving_packages(dockerfile, pkg_dir):
    # app/ (transport) + core/ (queue + the relocated FoldSpec contract) + db/ (ORM models).
    assert f"copy {pkg_dir}" in dockerfile.lower(), \
        f"DEP-001: the serving image must copy {pkg_dir}/"


def test_copies_data_for_the_manifest(dockerfile):
    # D-038: GET /api/coverage computes core/manifest.py from data/cohort_82_ecd.csv at request
    # time. Without data/ in the image the route passes locally and 500s in prod — so the copy is
    # pinned here rather than left to a reviewer's eye. (data/ is CSVs, not the GPU world.)
    assert "copy data" in dockerfile.lower(), \
        "D-038: the serving image must copy data/ so core/manifest.py can compute coverage"


# ── the two-stage build: Node builds the bundle, never enters the runtime (DEP-006) ──

def _runtime_stage(dockerfile: str) -> str:
    """Non-comment lines from the LAST ``FROM`` onward — the runtime stage. Stage 1 is the Node
    builder; everything DEP-001 rules about the image is about what runs, i.e. this stage."""
    lines = dockerfile.splitlines()
    last_from = max(i for i, ln in enumerate(lines) if ln.lstrip().lower().startswith("from "))
    return "\n".join(lines[last_from:]).lower()


def test_two_stage_build_has_a_node_builder(dockerfile):
    # DEP-006: stage 1 builds the React bundle on a Node image.
    assert "node:" in dockerfile.lower(), "DEP-006: a Node build stage builds the bundle"


def test_node_and_npm_never_enter_the_runtime_stage(dockerfile):
    # DEP-006: the built assets arrive via `COPY --from` as static files; the runtime tier stays
    # Python + the hash-locked lock, with NO npm/node instruction after the runtime FROM. A serving
    # image that acquired a JS runtime it never executes is the same invisible bloat as one with CUDA.
    runtime = _runtime_stage(dockerfile)
    assert "npm" not in runtime, "DEP-006: no npm instruction in the runtime stage"
    assert "node:" not in runtime and " node " not in runtime, \
        "DEP-006: no node instruction in the runtime stage"


def test_build_uses_npm_ci_not_install(dockerfile):
    # D-037: `npm ci` installs EXACTLY the committed lockfile and FAILS on drift; `npm install`
    # silently resolves and rewrites it. That difference is the whole (weaker-than-D-013) guarantee.
    low = dockerfile.lower()
    assert "npm ci" in low, "D-037: the build installs with npm ci"
    assert "npm install" not in low, "D-037: never npm install (it rewrites the lock)"


# ── .dockerignore excludes the worker tier at the context level too ───────────

def test_dockerignore_excludes_worker_and_cruft():
    assert DOCKERIGNORE.exists(), "a .dockerignore keeps worker/ and cruft out of the build context"
    ignore = DOCKERIGNORE.read_text(encoding="utf-8")
    assert "worker/" in ignore, ".dockerignore must exclude worker/ from the build context"
