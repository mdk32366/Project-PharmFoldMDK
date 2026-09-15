"""F-078 amendment 2 — `--restore` stays refused, even for the owner, after the debt is paid.

⚠⚠ MOVED HERE from `tests/test_f078_owed_restore.py` (`ORDERS-Code-2026-09-16` §1.3, `D-167` Phase C).
That file is deleted in the commit that pays slice 2's debt, and it held the ONLY test pinning this
refusal. Paying the debt by re-attach does not make a re-fold of the 37 safe: the verified bytes are
still the measurement. So the guard moves before the reminder is deleted, and the deletion removes the
reminder and not the guard.
"""

from __future__ import annotations


def test_restore_refuses_even_for_the_owner():
    """⚠⚠ `F-078` amendment 2 §4. `--restore` leads to a re-fold, and a re-fold overwrites the 37
    artifacts in place. The script refuses BEFORE it builds an engine, so the refusal cannot depend
    on a tunnel being up. ⚠ The URL below points at nothing: if the refusal moved after the connect,
    this would raise instead of returning 1."""
    import scripts.f078_null_tier_the_37 as f

    url = "postgresql://nobody@127.0.0.1:1/nothing"
    assert f.main(["--url", url, "--restore"]) == 1
    assert f.main(["--url", url, "--restore", "--i-am-the-owner"]) == 1
