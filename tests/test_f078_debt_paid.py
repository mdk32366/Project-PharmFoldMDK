"""F-078 amendment 3 / D-167 — the debt is PAID, and the prohibition outlives the reminder.

⚠⚠ Slice 2 reads 517 on the database witness (480 before, same key, same sitting). The reminder that
existed only because the debt was silent — `tests/test_f078_owed_restore.py` — is deleted, and its
removal is the record that the debt was paid. What must NOT be deleted with it:

- the `--restore` refusal (it lives in `tests/test_f078_restore_refused.py`, moved in Phase C);
- DO NOT RE-FOLD in the operator notice — the verified bytes on the volume are still the measurement;
- byte preservation of the evidence the payment rests on (`ORDERS` A8.5: `data/control/d167/** -text`).

⚠ RED FIRST: every property below is asserted against the tree as it stands before the rewrite, so each
fails at its assertion — the notice is still OWED, the reminder still exists, the evidence is not
EOL-exempt.
"""

from __future__ import annotations

import importlib
import inspect
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SLICES = ("scripts.task4_slice3", "scripts.task4_slice4")


def test_the_owed_restore_reminder_is_deleted_because_the_debt_is_paid():
    assert not (REPO / "tests" / "test_f078_owed_restore.py").exists(), (
        "slice 2 reads 517/517 on the database witness; the reminder is deleted in the commit that pays "
        "the debt (PREWORK-2026-09-16 section 1)")
    assert (REPO / "tests" / "test_f078_restore_refused.py").is_file(), (
        "the --restore refusal must outlive the reminder (ORDERS section 1.3)")


@pytest.mark.parametrize("mod", SLICES)
def test_the_report_prints_the_paid_notice_not_the_owed_one(mod):
    m = importlib.import_module(mod)
    notice = getattr(m, "F078_PAID_NOTICE", None)
    assert notice is not None, f"{mod} has no F078_PAID_NOTICE"
    assert not hasattr(m, "OWED_RESTORE"), f"{mod} still carries the OWED notice"
    src = inspect.getsource(m.report)
    assert "f078_paid_notice()" in src, f"{mod} --report does not print the paid notice"
    assert "owed_restore_notice()" not in src
    text = "\n".join(notice)
    for needle in ("PAID", "D-167", "480", "517", "d167_reattach.py", "--witness", "2026-09-15",
                   "DO NOT RE-FOLD", "--restore", "4869", "4905"):
        assert needle in text, f"{mod}: the paid notice does not say {needle!r}"
    assert "NOT YET DONE" not in text


@pytest.mark.parametrize("mod", SLICES)
def test_the_paid_notice_is_ascii(mod):
    """Printed by --report at the end of a long unattended run; cp1252 must not crash it (A7.4)."""
    m = importlib.import_module(mod)
    bad = [ln for ln in getattr(m, "F078_PAID_NOTICE", []) if any(ord(c) > 127 for c in ln)]
    assert not bad, f"non-ASCII in the paid notice: {bad}"


def test_the_null_tier_script_no_longer_prescribes_paying_the_debt_with_restore():
    src = (REPO / "scripts" / "f078_null_tier_the_37.py").read_text(encoding="utf-8")
    assert "pay it with `--restore" not in src, "the script still tells an operator to pay with --restore"
    assert "delete tests/test_f078_owed_restore.py" not in src
    assert "D-167" in src, "the script does not say how the debt was paid"


@pytest.mark.parametrize("rel", ["data/control/d167/capture.json",
                                 "data/control/d167/state_before.json",
                                 "data/control/d167/phase_e_read.json"])
def test_the_d167_evidence_is_exempt_from_end_of_line_conversion(rel):
    """`ORDERS` A8.5: each is verified by sha256; a Windows checkout under core.autocrlf would silently
    change its bytes. `git check-attr` is asked, not `.gitattributes` grepped."""
    out = subprocess.run(["git", "check-attr", "text", "--", rel], cwd=REPO,
                         capture_output=True, text=True).stdout.strip()
    assert out.endswith(": text: unset"), out
