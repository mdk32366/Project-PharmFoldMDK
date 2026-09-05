"""D-121 — Method hold-48 8th-grade explainer. These must be able to go red.

The owner-facing write-up and the /method addendum must name assembler-not-Kabsch,
disclose the IGF2R seam as not solved, say the rental is CLOSED, and carry a
real ``### D-121`` living-log heading. This PR must not ADD ``/adcs``
(D-122 already shipped them on main at ``86f8a10``).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = (ROOT / "docs" / "method-hold48-tiles.md").read_text(encoding="utf-8")
NOTE = (ROOT / "ui" / "src" / "components" / "MethodNote.jsx").read_text(
    encoding="utf-8"
)
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
APP = (ROOT / "ui" / "src" / "App.jsx").read_text(encoding="utf-8")

# D-122 / #232 shipped /adcs + /adcs/:id on main (86f8a10). D-124 / ADC-C-B
# adds /adcs/pipeline/:id before :id. MethodNote still must not grow a route.
# Pin is the path list, not `git diff 86f8a10` — shallow CI has no that SHA.
D122_ADCS_PATHS = ["/adcs", "/adcs/:id"]
D124_ADCS_PATHS = ["/adcs", "/adcs/pipeline/:id", "/adcs/:id"]


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


def test_d125_b_method_addendum_names_does_and_does_not():
    """D-125-B addendum: what Kabsch does / does not; never seams solved."""
    for text, label in ((DOC, "method-hold48-tiles.md"), (NOTE, "MethodNote.jsx")):
        flat = _flat(text)
        lowered = flat.lower()
        assert "What Kabsch does" in flat, label
        assert "What Kabsch does not do" in flat, label
        assert "default served" in lowered, label
        assert "not scientifically solved" in lowered, label
        assert "not medical advice" in lowered, label
        assert "seams solved" not in lowered, label
        assert "kabsch aligned" not in lowered, label
        assert "we ran kabsch" not in lowered, label
        assert "full-length af-quality" not in lowered, label


def test_d125_b_living_log_present():
    """Living-doc rule: the B heading exists. A citation is not the entry."""
    assert re.search(
        r"^### D-125-B — UI dual-path honesty",
        LOG,
        re.M,
    ), "D-125-B must be a real ### entry, not a citation of one"
    assert re.search(r"^### D-125 — Kabsch restitch Spec", LOG, re.M)


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
    """D-121 Method surfaces do not ADD /adcs. D-122 routes stay.

    D-124 / ADC-C-B is the authorized third path (pipeline card).
    Deleting either shipped D-122 path still goes red. Shallow CI
    cannot ``git diff 86f8a10``.
    """
    paths = re.findall(r'path="(/adcs[^"]*)"', APP)
    assert paths == D124_ADCS_PATHS, paths
    for required in D122_ADCS_PATHS:
        assert required in paths
    assert '<NavLink to="/adcs">ADCs</NavLink>' in APP
    assert 'path="/adcs" element={<AdcsView />}' in APP
    assert 'path="/adcs/:id" element={<AdcCardRoute />}' in APP
    assert "AdcsView" in APP
    assert "AdcCard" in APP

    # D-121 Method surfaces do not introduce a route.
    assert "AdcsView" not in NOTE
    assert 'to="/adcs"' not in NOTE
    assert 'path="/adcs"' not in NOTE
