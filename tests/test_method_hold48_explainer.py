"""D-121 — Method hold-48 8th-grade explainer. These must be able to go red.

The owner-facing write-up and the /method addendum must name assembler-not-Kabsch,
disclose the IGF2R seam as not solved, say the rental is CLOSED, and carry a
real ``### D-121`` living-log heading. This PR must not ADD ``/adcs``
(D-122 already shipped them on main at ``86f8a10``).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = (ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8")
NOTE = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(
    encoding="utf-8"
)
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
APP = (ROOT / "ui" / "src" / "App.jsx").read_text(encoding="utf-8")

# D-122 merge on main. Diff/pin: this PR rebases onto it and must not ADD /adcs.
D122_MAIN = "86f8a10"


def _flat(text: str) -> str:
    """Line-wrap is not the claim. Collapse whitespace so a wrap cannot hide it."""
    return re.sub(r"\s+", " ", text)


def test_assembler_not_kabsch():
    """Assemble is a pLDDT winner-tile assembler, not Kabsch."""
    for text, label in ((DOC, "method-hold48-tiles.md"), (NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        assert "winner-tile assembler" in flat, label
        assert "not Kabsch" in flat, label
        lowered = flat.lower()
        assert "seams solved" not in lowered, label
        assert "kabsch aligned" not in lowered, label
        assert "we ran kabsch" not in lowered, label
        # Must refuse the holoprotein premise, not merely omit the words.
        assert "not a superimposed holoprotein" in lowered or "not kabsch" in lowered, label


def test_seam_not_solved():
    """IGF2R ~88.76 Å is a disclosure, not a solved structure."""
    for text, label in ((DOC, "method-hold48-tiles.md"), (NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        assert "88.76" in flat, label
        assert "not scientifically solved" in flat, label
        assert "fix the seam" not in flat.lower(), label


def test_rental_closed():
    """Hold-48 rental is CLOSED. The explainer must not invite a new rent."""
    for text, label in ((DOC, "method-hold48-tiles.md"), (NOTE, "MethodNote.jsx")):
        assert "CLOSED" in text, label
        assert "Terminated" in text, label
        assert "waiting on rented capacity" not in text, label


def test_d121_living_log_present():
    """Living-doc rule: the heading exists. A citation is not the entry."""
    assert re.search(r"^### D-121 — Method hold-48 8th-grade explainer", LOG, re.M)
    assert "### D-118 — Phase 1 P0 honesty" in LOG
    assert "### D-120 — Phase 2 review UI" in LOG
    assert "### D-122 — ADC-B:" in LOG
    assert "### D-123 —" in LOG
    assert "#229 stays merged" in LOG
    assert "Do not reopen" in LOG or "do not reopen" in LOG.lower()


def test_this_pr_must_not_add_adcs():
    """THIS PR does not ADD /adcs. D-122 already shipped them on main.

    Do not assert that main lacks /adcs. Do not regress D-122 routes.
    The check is a diff/pin against ``86f8a10``.
    """
    # D-122 routes must still exist (regression if this PR deletes them).
    assert 'path="/adcs"' in APP
    assert 'path="/adcs/:id"' in APP
    assert "AdcsView" in APP
    assert "AdcCard" in APP

    # This PR's Method surfaces do not introduce an /adcs route.
    assert "AdcsView" not in NOTE
    assert 'to="/adcs"' not in NOTE
    assert 'path="/adcs"' not in NOTE

    # Diff/pin vs D-122 main: no added App.jsx /adcs lines; no new ADC-B files.
    app_diff = subprocess.check_output(
        ["git", "diff", D122_MAIN, "--", "ui/src/App.jsx"],
        cwd=ROOT,
        text=True,
    )
    added = [
        ln for ln in app_diff.splitlines()
        if ln.startswith("+") and not ln.startswith("+++")
    ]
    assert not any('path="/adcs"' in ln or "AdcsView" in ln or "AdcCard" in ln for ln in added), (
        "this PR must not ADD /adcs on top of D-122"
    )

    new_files = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=A", D122_MAIN],
        cwd=ROOT,
        text=True,
    )
    assert "AdcsView" not in new_files
    assert "AdcCard" not in new_files
    assert "adcCatalog" not in new_files
