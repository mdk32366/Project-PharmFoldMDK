"""F-078 amendment 2 — the 37 volume artifacts are the right proteins, and the check can say otherwise.

⚠ Disk only: the committed volume dump, the committed UniProt expectations, slice 2's committed
`progress.csv`. Nothing reads `data/census/spancache` (gitignored — `F-076`), so this runs the same
on a fresh clone as on the machine that took the measurement.

⚠⚠ `D-162` rule 7: a verification states what it would return if the thing were absent. Each
mutation below changes ONE fact about ONE job and requires the failure on exactly that row — not
merely "fewer than 37", which a checker failing everything would also satisfy.
"""
from __future__ import annotations

import re

import pytest

import scripts.f078_identity_check as ic


@pytest.fixture(scope="module")
def dump_text() -> str:
    return ic.decode(ic.DUMP.read_bytes())


def _run(text: str):
    prov, seqs = ic.parse_dump(text)
    return ic.check(prov, seqs, ic.load_expected(), ic.load_progress_at())


def _failing(results) -> list[int]:
    return [j for j, _, fails in results if fails]


def test_the_dump_reaches_the_parser(dump_text):
    """A parser that matches nothing makes every later assertion vacuous."""
    prov, seqs = ic.parse_dump(dump_text)
    assert sorted(prov) == list(range(4869, 4906))
    assert sorted(seqs) == list(range(4869, 4906))
    assert {len(s) for s in seqs.values()} == {29, 30}


def test_all_37_are_the_proteins_their_jobs_name(dump_text):
    results = _run(dump_text)
    assert len(results) == 37
    assert _failing(results) == [], [r for r in results if r[2]]


def _mutate_residue(text: str, job: int) -> str:
    lines = text.splitlines()
    pre = f"{job}/structure.pdb:"
    i = next(k for k, ln in enumerate(lines)
             if ln.startswith(pre) and ln[len(pre):][12:16].strip() == "CA")
    body = lines[i][len(pre):]
    new = "TRP" if body[17:20] != "TRP" else "GLY"
    lines[i] = pre + body[:17] + new + body[20:]
    return "\n".join(lines)


def _shift_folded_at(text: str, job: int) -> str:
    return re.sub(rf'({job}/provenance\.json:\s*"folded_at":\s*"2026-09-13T)(\d\d)',
                  lambda m: m[1] + f"{int(m[2]) + 1:02d}", text, count=1)


def _shift_ecd_start(text: str, job: int) -> str:
    return re.sub(rf'({job}/provenance\.json:\s*"ecd_start":\s*)(\d+)',
                  lambda m: m[1] + str(int(m[2]) + 1), text, count=1)


def _drop_last_ca(text: str, job: int) -> str:
    lines = text.splitlines()
    pre = f"{job}/structure.pdb:"
    i = max(k for k, ln in enumerate(lines)
            if ln.startswith(pre) and ln[len(pre):][12:16].strip() == "CA")
    return "\n".join(lines[:i] + lines[i + 1:])


@pytest.mark.parametrize("mutate, job", [
    (_mutate_residue, 4880),
    (_shift_folded_at, 4890),
    (_shift_ecd_start, 4900),
    (_drop_last_ca, 4875),
])
def test_one_wrong_fact_fails_exactly_its_own_row(dump_text, mutate, job):
    mutated = mutate(dump_text, job)
    assert mutated != dump_text, "the mutation did not change the dump; the test proves nothing"
    assert _failing(_run(mutated)) == [job]
