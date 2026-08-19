"""What may enter the serving image, asserted by ABSENCE.

⚠⚠ `D-079` decision 1 bars a refit outright — *"no refit — `ranking_run` id=2 is read from its
row"* — and `scripts/fit_scorer.py` is the fitter. The census feature ingest needs to run
somewhere holding both a `DATABASE_URL` and the artifact, and the machine is the right place: the
credential never leaves it, which is how migration `0010` was applied. But `COPY scripts/` would
have shipped all 60 scripts, SEVEN of which write, and put a **ruled prohibition one `fly ssh`
away behind no guard at all.**

⚠ So exactly one file is copied, and this test is what keeps it exactly one. The convenient
broadening — `COPY scripts/ ./scripts/` — is one keystroke and would look harmless in a diff.

⚠ This asserts the DECLARATION (the Dockerfile), not the built image, and says so rather than
implying more: no docker daemon runs in the gate. The build itself is the other half of the
proof — a `COPY` of a path `.dockerignore` excludes fails the build loudly, so a green deploy
establishes the file really is in the context.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCKERFILE = REPO / "Dockerfile"
DOCKERIGNORE = REPO / ".dockerignore"

# The only script permitted into the serving tier.
ALLOWED_SCRIPTS = {"scripts/census_ingest_features.py"}

# Scripts that WRITE. None of these may enter the image except the allowed ingest.
WRITERS = {
    "scripts/fit_scorer.py",            # creates ranking runs and refits — D-079 dec 1 bars it
    "scripts/extract_features.py",      # inserts protein_features (F-021)
    "scripts/census_ingest.py",
    "scripts/hpa_census_coverage.py",
    "scripts/hpa_v22_verify.py",
    "scripts/tranche6_domain_survey.py",
}


def _copy_sources() -> list[str]:
    """Every source path named by a COPY in the Dockerfile, comments stripped."""
    out: list[str] = []
    for raw in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.upper().startswith("COPY "):
            continue
        parts = line.split()[1:]
        parts = [p for p in parts if not p.startswith("--")]   # drop --from=, --chmod=
        out.extend(parts[:-1])                                  # last token is the destination
    return out


def test_the_dockerfile_copies_no_script_directory():
    """⚠ A directory COPY is the failure mode: it is smaller in the diff than the file list it
    actually ships."""
    bad = [s for s in _copy_sources()
           if s.rstrip("/") == "scripts" or s.startswith("scripts/*")]
    assert not bad, (
        f"the Dockerfile copies a scripts DIRECTORY ({bad}) — that ships the fitter to the "
        f"production host, and D-079 dec 1 bars a refit")


def test_only_the_allowed_script_is_copied():
    copied = {s for s in _copy_sources() if s.startswith("scripts/")}
    assert copied <= ALLOWED_SCRIPTS, (
        f"scripts entering the serving image that are not permitted: "
        f"{sorted(copied - ALLOWED_SCRIPTS)}")


def test_no_writing_script_reaches_the_image():
    """The claim that matters, stated against the writers by name rather than by category."""
    copied = {s for s in _copy_sources() if s.startswith("scripts/")}
    leaked = sorted(copied & WRITERS)
    assert not leaked, f"scripts that WRITE reached the serving image: {leaked}"


def test_the_fitter_is_named_and_absent():
    """⚠ Named explicitly, not left to the set logic above. `fit_scorer.py` is the one whose
    presence would convert a ruled prohibition into an honour system, and a test that only
    checks a set can be satisfied by editing the set."""
    assert "scripts/fit_scorer.py" not in _copy_sources()
    assert "scripts/fit_scorer.py" in WRITERS, (
        "the fitter was removed from WRITERS — that edit defeats the test above rather than "
        "satisfying it")


def test_dockerignore_excludes_scripts_and_re_includes_only_the_ingest():
    text = DOCKERIGNORE.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    assert "scripts/" in lines, "`scripts/` is no longer excluded from the build context"
    negations = {ln[1:] for ln in lines if ln.startswith("!")}
    scripts_negations = {n for n in negations if n.startswith("scripts/")}
    assert scripts_negations == ALLOWED_SCRIPTS, (
        f"the build context re-includes {sorted(scripts_negations)}; only "
        f"{sorted(ALLOWED_SCRIPTS)} is permitted")


def test_the_allowed_script_exists_so_the_copy_cannot_silently_be_a_typo():
    """⚠ A COPY naming a file that does not exist fails the BUILD, not the gate — and that
    failure would arrive during a deploy. Catch it here instead."""
    for rel in sorted(ALLOWED_SCRIPTS):
        assert (REPO / rel).is_file(), f"{rel} is copied into the image but does not exist"


def test_the_ingest_needs_nothing_from_scripts_that_is_not_shipped():
    """⚠ The copied script must not import a sibling that stays out of the image — that would
    build fine and fail at run time, on the production host, which is the worst place to find it."""
    src = (REPO / "scripts" / "census_ingest_features.py").read_text(encoding="utf-8")
    sibling = re.findall(r"^\s*from\s+scripts\.(\w+)|^\s*import\s+scripts\.(\w+)",
                         src, re.M)
    names = {a or b for a, b in sibling}
    allowed = {pathlib.Path(p).stem for p in ALLOWED_SCRIPTS}
    assert names <= allowed, (
        f"the ingest imports scripts that do not ship: {sorted(names - allowed)}")
