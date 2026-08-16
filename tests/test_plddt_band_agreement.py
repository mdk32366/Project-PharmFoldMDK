"""The pLDDT band scheme has ONE source, and the analysis script must not fork it.

⚠ `ui/src/plddt.js` declares itself *"the single source of the band scheme"*. When
`scripts/plddt_bands.py` was first written it used the AlphaFold-DB convention (90/70/50) instead
of the project's ruled 70/60/50 — so *"low"* would have meant one thing in the webapp and another
in the analysis. **One word, two meanings.** This pins them together.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.plddt_bands import BANDS  # noqa: E402


def test_the_script_uses_the_bands_the_webapp_declares():
    """⚠ Read out of `ui/src/plddt.js` SOURCE, never a hand-copied list — a hand-copied list is
    exactly what drifts (F-027)."""
    js = (REPO / "ui" / "src" / "plddt.js").read_text(encoding="utf-8")
    ui_mins = sorted(int(m) for m in re.findall(r"min:\s*(\d+)", js))
    py_mins = sorted(lo for lo, _hi, _l, _c in BANDS)
    assert py_mins == ui_mins, (
        f"band edges diverged — script {py_mins} vs ui/src/plddt.js {ui_mins}. "
        f"'low' must not mean two different things.")


def test_there_is_deliberately_no_high_confidence_tier():
    """⚠ Nothing in the cohort reaches 90 (max 84.23). A band nobody occupies invites the reader to
    assume someone might, so the scheme tops out at 'confident backbone' and says so."""
    assert max(lo for lo, _h, _l, _c in BANDS) == 70
    top = [b for b in BANDS if b[0] == 70][0]
    assert "84.23" in top[3], "the cohort-max caveat vanished from the top band"
