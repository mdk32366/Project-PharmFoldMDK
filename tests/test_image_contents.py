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


# ── .dockerignore excludes the worker tier at the context level too ───────────

def test_dockerignore_excludes_worker_and_cruft():
    assert DOCKERIGNORE.exists(), "a .dockerignore keeps worker/ and cruft out of the build context"
    ignore = DOCKERIGNORE.read_text(encoding="utf-8")
    assert "worker/" in ignore, ".dockerignore must exclude worker/ from the build context"
