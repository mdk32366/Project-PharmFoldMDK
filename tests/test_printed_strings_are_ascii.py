"""Every PRINTED string in an operator script must be ASCII. ⚠ Docstrings and comments need not be.

⚠⚠ WHY THIS EXISTS, AND IT IS THE FOURTH INSTANCE OF ONE LESSON.

`worker/main.py` carries the lesson in a comment: *"an em dash raises UnicodeEncodeError on cp437
and kills the worker at startup. A startup message that can kill the process it announces is worse
than none."* `scripts/backfill_run_label.py` hit it anyway on 2026-09-11 and died before reporting
anything. On 2026-09-12 `scripts/task4_slice1.py` hit it again — **after committing 342 production
rows**: the write succeeded, `enqueued.json` was written, and then

    print(f"⚠ band coverage: ...")

raised `UnicodeEncodeError: 'charmap' codec can't encode character '\\u26a0'` on a console whose
`sys.stdout.encoding` is **cp1252**. The operator saw no confirmation and reported that nothing
had been written. ⚠ **The rows were there. The tool had simply lost the ability to say so.**

> ⚠⚠ **THE LESSON KEEPS RECURRING BECAUSE NOTHING ENFORCED IT.** Three write-ups and a comment did
> not prevent a fourth instance. This is the enforcement, and it is the whole point: a rule that
> lives only in prose is a rule that gets rediscovered.

⚠ **Scoped to the scripts an operator runs at a console**, not to the library code, and **only to
strings that reach `print`** — the reasoning, the docstrings and the comments keep their marks,
because those are read in an editor and never encoded to a terminal.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The scripts a human runs in a console window whose codepage nobody controls.
OPERATOR_SCRIPTS = [
    "scripts/task4_slice1.py",
    "scripts/task3_run2_folds.py",
    "scripts/backfill_run_label.py",
    "scripts/task3_timing_sample.py",
]


def _non_ascii_printed(path: pathlib.Path) -> list[tuple[int, str]]:
    """Every string constant reachable from a `print(...)` call that is not ASCII."""
    out: list[tuple[int, str]] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "print"):
            continue
        for s in ast.walk(node):
            if isinstance(s, ast.Constant) and isinstance(s.value, str) and not s.value.isascii():
                offenders = sorted({c for c in s.value if not c.isascii()})
                out.append((s.lineno, "".join(offenders)))
    return out


@pytest.mark.parametrize("rel", OPERATOR_SCRIPTS)
def test_no_printed_string_can_kill_the_console_it_prints_to(rel):
    path = REPO / rel
    if not path.is_file():
        pytest.skip(f"{rel} is not in this tree")
    bad = _non_ascii_printed(path)
    assert not bad, (
        f"{rel} prints non-ASCII, which raises UnicodeEncodeError on a cp1252/cp437 console and "
        f"kills the process mid-sentence: " + ", ".join(f"line {n} {chars!r}" for n, chars in bad))


@pytest.mark.parametrize("rel", OPERATOR_SCRIPTS)
def test_every_printed_string_survives_the_console_encodings_that_exist_here(rel):
    """⚠ The stronger form, and the one that matches the failure: it is not 'is it ASCII' but
    'can the console encode it'. `cp1252` is what `sys.stdout.encoding` actually reported on the
    machine that lost the confirmation; `cp437` is what `worker/main.py`'s comment names."""
    path = REPO / rel
    if not path.is_file():
        pytest.skip(f"{rel} is not in this tree")
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "print"):
            continue
        for s in ast.walk(node):
            if isinstance(s, ast.Constant) and isinstance(s.value, str):
                for enc in ("cp1252", "cp437"):
                    try:
                        s.value.encode(enc)
                    except UnicodeEncodeError as exc:
                        pytest.fail(f"{rel}:{s.lineno} cannot be printed on a {enc} console "
                                    f"({exc}); the process dies while reporting")


def test_the_guard_itself_can_fail(tmp_path):
    """⚠⚠ A-017 (c). A checker that returns nothing on every input is not a checker. This feeds it
    the EXACT line that killed the enqueue and requires it to be caught."""
    f = tmp_path / "offender.py"
    f.write_text('print(f"⚠ band coverage: {n} new")\n', encoding="utf-8")
    bad = _non_ascii_printed(f)
    assert bad and bad[0][1] == "⚠"

    clean = tmp_path / "clean.py"
    clean.write_text('print(f"! band coverage: {n} new")\n', encoding="utf-8")
    assert _non_ascii_printed(clean) == []


def test_docstrings_and_comments_are_deliberately_NOT_checked(tmp_path):
    """⚠ The rule is about what reaches a terminal. Widening it to every string would strip the
    reasoning out of the files, and the reasoning is read in an editor that has no codepage
    problem — a guard that costs more than the defect is not a good trade."""
    f = tmp_path / "doc.py"
    f.write_text('"""⚠ a docstring with a mark."""\nX = "⚠ not printed"\n', encoding="utf-8")
    assert _non_ascii_printed(f) == []
