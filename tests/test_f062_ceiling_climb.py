"""F-062 + ceiling_climb wiring — pins that can go red if the landing is missing.

⚠ These tests do NOT climb and do NOT fold. CI has no Blackwell GPU; Kaylee runs
the climb on MDKDevLaptop. A test that imported torch.cuda and folded would not
run at all, so the assertions here are the contracts the GPU run depends on:

- F-062 is a real `### ` header (the D-062 defect was a cited number with no entry)
- the RESERVED next-free `F-` pointer names no spent heading and exceeds every one;
  F-050 stays reserved
- ceiling_climb refuses without --layer1-attested, before any climb
- --fold-in-child / WORKER_FOLD_IN_CHILD wiring is present (D-082 layer 3)
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
LOG = REPO / "docs" / "README.md"
RESERVED = REPO / "docs" / "RESERVED.md"
SCRIPT = REPO / "scripts" / "ceiling_climb.py"
CHILD = REPO / "worker" / "ceiling_climb_child.py"


def _load_climb():
    import importlib.util
    name = "ceiling_climb"
    if name in sys.modules:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_f062_is_a_log_header():
    """⚠ The check is the entry, not a reference to one (D-062)."""
    text = LOG.read_text(encoding="utf-8")
    headers = re.findall(r"^### F-062 — .+$", text, re.M)
    assert len(headers) == 1, headers
    assert "card-bound" in headers[0]
    assert "6665" in headers[0]
    # Substance pins — a truncated paste would drop these.
    assert "S-005’s 6665 MiB is not a measurement of this card" in text or \
           "S-005's 6665 MiB is not a measurement of this card" in text
    assert "F-059 within 10% does not certify headroom" in text
    assert "Do not take `F-050`" in text
    assert "88d59bb6" in text
    assert "Q96QU1" in text
    # Not a rewrite of D-104's table
    assert "Not a rewrite of the D-104 table" in text


def test_f050_was_not_taken():
    """The guard-direction sweep stays RESERVED. This PR must not spend F-050."""
    log = LOG.read_text(encoding="utf-8")
    assert re.search(r"^### F-050 ", log, re.M) is None
    reserved = RESERVED.read_text(encoding="utf-8")
    assert "| **F-050** |" in reserved
    assert "guard-direction sweep" in reserved


def test_reserved_next_free_is_f065_and_f050_still_reserved():
    reserved = RESERVED.read_text(encoding="utf-8")
    # ⚠⚠ F-062 amendment 1. This asserted the LITERAL `F-065`, so it passed only while nothing
    # happened and went red the moment 314df71 spent F-065/F-066 and moved the pointer IN THE SAME
    # COMMIT — the discipline the failure message itself demands. It encoded a rule about MOVEMENT
    # as a fixed VALUE. ⚠ The message was always right; only the check was wrong.
    # ⚠ Bumping the literal to F-067 was REFUSED on the record: it re-arms the identical trap for
    # whoever spends F-067 next, and converts a guard into a maintenance obligation.
    check_next_free_pointer(LOG.read_text(encoding="utf-8"), reserved)
    assert "Next free `F-` integer: `F-062`" not in reserved
    assert "| **F-050** |" in reserved
    # F-062 is written, not reserved
    assert re.search(r"^\| \*\*F-062\*\*", reserved, re.M) is None




def test_f064_entry_present_in_findings_log():
    """F-064 spent the integer; header and key measured facts must appear."""
    log = LOG.read_text(encoding="utf-8")
    assert re.search(r"^### F-064 ", log, re.M), "F-064 header missing from docs/README.md"
    m = re.search(r"^### F-064 .*?(?=\n### |\Z)", log, re.M | re.S)
    assert m, "could not isolate F-064 entry"
    entry = m.group(0)
    assert "7043" in entry and "1649" in entry
    assert "380" in entry

def test_f063_entry_present_in_findings_log():
    """F-063 spent the integer; header and key measured facts must appear."""
    log = LOG.read_text(encoding="utf-8")
    assert re.search(r"^### F-063 ", log, re.M), "F-063 header missing from docs/README.md"
    m = re.search(r"^### F-063 .*?(?=\n### |\Z)", log, re.M | re.S)
    assert m, "could not isolate F-063 entry"
    entry = m.group(0)
    assert "**384 aa**" in entry or "highest_ok=384" in entry
    assert "1513" in entry

def test_refuses_to_climb_without_layer1_attested():
    """⚠ REQUIRED. Missing attestation is a non-zero refuse, not a warning and climb."""
    mod = _load_climb()
    with pytest.raises(SystemExit) as ei:
        mod.assert_layer1_attested(False)
    msg = str(ei.value)
    assert ei.value.code != 0
    assert "--layer1-attested" in msg
    assert "REFUSING TO CLIMB" in msg

    # Through run(), and BEFORE cache/CUDA: a fake accession must not be the error.
    with pytest.raises(SystemExit) as ei2:
        mod.run(["--accession", "DOESNOTEXIST"])
    msg2 = str(ei2.value)
    assert "layer1-attested" in msg2
    assert "DOESNOTEXIST" not in msg2
    assert "no cache entry" not in msg2


def test_layer1_attested_is_not_the_default():
    """Attestation is an operator act. Defaulting it on would make the flag theatre."""
    mod = _load_climb()
    ns = mod.build_parser().parse_args(["--accession", "Q8WXD0"])
    assert ns.layer1_attested is False


def test_fold_in_child_honors_flag_and_WORKER_FOLD_IN_CHILD(monkeypatch):
    """D-082 layer 3 / rb_local pattern: CLI flag OR env == '1'."""
    mod = _load_climb()
    monkeypatch.delenv("WORKER_FOLD_IN_CHILD", raising=False)
    assert mod.fold_in_child_enabled(False) is False
    assert mod.fold_in_child_enabled(True) is True
    monkeypatch.setenv("WORKER_FOLD_IN_CHILD", "1")
    assert mod.fold_in_child_enabled(False) is True
    monkeypatch.setenv("WORKER_FOLD_IN_CHILD", "0")
    assert mod.fold_in_child_enabled(False) is False
    assert mod.fold_in_child_enabled(True) is True


def test_fold_in_child_cli_and_env_are_wired_in_source():
    """A helper with no call site is decoration. The climb must consult both."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "--fold-in-child" in src
    assert "WORKER_FOLD_IN_CHILD" in src
    assert "fold_in_child_enabled" in src
    tree = ast.parse(src)
    found_flag = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = getattr(node, "func", None)
        if getattr(func, "attr", None) != "add_argument":
            continue
        args = [a.value for a in node.args if isinstance(a, ast.Constant)]
        if "--fold-in-child" in args:
            found_flag = True
    assert found_flag, "--fold-in-child is not an argparse flag"
    child_src = CHILD.read_text(encoding="utf-8")
    assert "apply_allocator_cap" in child_src
    assert "peak_vram" in child_src
    assert "empty_cache" in child_src


def test_usable_bounds_default_to_the_blackwell_climb():
    """--start 248 --stop 456 --step 8, local, 0.85, empty-cache ON, fresh jsonl."""
    mod = _load_climb()
    ns = mod.build_parser().parse_args(["--accession", "Q8WXD0", "--layer1-attested"])
    assert ns.start == 248
    assert ns.stop == 456
    assert ns.step == 8
    assert ns.memory_fraction == 0.85
    assert ns.tier == "local"
    assert ns.empty_cache is True
    assert ns.fold_in_child is False  # opt-in, like worker.main
    assert Path(ns.out) == mod.DEFAULT_OUT
    assert mod.DEFAULT_OUT.parent == mod.CENSUS
    assert not mod.DEFAULT_OUT.exists(), (
        "the default jsonl must be fresh — a committed file would refuse the climb"
    )


def test_climb_child_parent_does_not_import_torch():
    """Same invariant as fold_supervisor: only the child holds weights."""
    src = CHILD.read_text(encoding="utf-8")
    head = src[: src.index("def _child_main")]
    assert not re.search(r"^\s*(import torch|from torch|from worker\.runner)", head, re.M)


def test_script_imports_no_db_by_ast():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    banned = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            banned += [a.name for a in node.names if a.name.split(".")[0] in {"db", "sqlalchemy"}]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            top = mod.split(".")[0]
            if top in {"db", "sqlalchemy"} or mod == "core.enqueue":
                banned.append(mod)
    assert not banned


# ⚠⚠ F-062 amendment 1 — the pointer invariant, proven against FIXTURES rather than the tree.
#
# The guard below used to read docs/README.md and docs/RESERVED.md off disk and compare the pointer
# to a LITERAL. It could not be made red without editing the repository, and it pinned a value where
# the rule is about movement. These four cases feed the pure helper two strings, so each state can
# be stated exactly and the bad ones can be SHOWN to fail.
#
# ⚠ None of these is a pure absence guard: each asserts the PRESENCE of a specific outcome —
# a raise with a named clause, or a returned pointer value.
from _f062_pointer_invariant import MESSAGE, check_next_free_pointer, spent_headings  # noqa: E402

_LOG_TO_066 = "### F-064 a\n### F-065 b\n### F-066 c\n"


def test_pointer_naming_a_spent_heading_is_rejected():
    """⚠ FIXTURE 1: the pointer names an integer that IS a written entry."""
    with pytest.raises(AssertionError) as exc:
        check_next_free_pointer(_LOG_TO_066, "Next free `F-` integer: `F-066`")
    assert "already a written entry" in str(exc.value)
    assert MESSAGE.split(" — ")[0].format(spent="066") in str(exc.value)


def test_pointer_below_the_highest_spent_heading_is_rejected():
    """⚠ FIXTURE 2: the pointer is UNSPENT but still lower than the highest spent heading.

    ⚠ The gap matters. A first draft used a pointer that was itself spent, which tripped clause one
    and never exercised clause two — the two clauses are separate defects and a fixture that cannot
    tell them apart proves only one. This log deliberately omits F-065 so the pointer is free, and
    the ordering clause is the only thing that can reject it.
    """
    log_with_gap = "### F-064 a" + chr(10) + "### F-066 c" + chr(10)
    with pytest.raises(AssertionError) as exc:
        check_next_free_pointer(log_with_gap, "Next free `F-` integer: `F-065`")
    assert "at or below the highest spent" in str(exc.value)
    assert "already a written entry" not in str(exc.value)


def test_pointer_one_past_the_highest_spent_heading_is_accepted():
    """FIXTURE 3: one past the highest spent — the only correct state."""
    assert check_next_free_pointer(_LOG_TO_066, "Next free `F-` integer: `F-067`") == 67


def test_the_real_repo_files_satisfy_the_invariant_at_this_ref():
    """⚠ FIXTURE 4: the tree itself. Pointer F-067, highest spent F-066.

    ⚠ This is the only case that touches disk, and it does so through the SAME pure function, so
    the tree is checked by the code the fixtures proved rather than by a second implementation.
    """
    pointer = check_next_free_pointer(
        LOG.read_text(encoding="utf-8"), RESERVED.read_text(encoding="utf-8")
    )
    assert pointer == 67
    assert max(spent_headings(LOG.read_text(encoding="utf-8"))) == 66
