#!/usr/bin/env python3
"""F-078 amendment 2 — does each orphaned volume artifact belong to the job whose directory holds it?

    python scripts/f078_identity_check.py            # the committed dump, the committed expectations
    python scripts/f078_identity_check.py <dump>     # another dump of the same shape

DISK ONLY. No tunnel, no database, no network. The dump was taken by the owner on the production
machine (read-only `grep -H` over `provenance.json` and the CA lines of `structure.pdb` for
`/data/artifacts/4869..4905`) and is committed at `data/control/f078/`.

⚠⚠ **WHY THIS EXISTS.** `F-078` recorded the 37 as lost from BOTH stores. Its witness to the volume
was the served surface, and `GET /api/analyses/{id}/structure` resolves through the row's
`pdb_path` — **so it cannot see a file whose row lost its path.** That is exactly the state a
database-only restore leaves behind. Byte counts matching `progress.csv` say the files are the right
size; they do not say they are the right protein. This does.

**Three independent records per job, none of them the volume:**

1. the residues in `structure.pdb`  ==  the accession's UniProt sequence at the provenance's
   `ecd_start..ecd_end`  (`f078_identity_expected.json`, extracted from `data/census/spancache`,
   which is gitignored — `F-076` — so the expectation is committed rather than read off a cache)
2. provenance `input_length` and the PDB residue count  ==  the enqueued `span_aa`
3. provenance `folded_at` (UTC)  within 60 s of `progress.csv`'s `at`, which is LOCAL time,
   **UTC-7, converted explicitly** (`F-078` §3). Measured offset is ~19 s: `folded_at` is the fold's
   START and `at` is its end.

⚠ **Negative control, per row:** the sequence is also tested against a DIFFERENT job's accession and
must not be found there. A check that cannot fail is not a check (`D-162` rule 7); the tests also
mutate the dump and require the failure to land on exactly the mutated row.

⚠ No `assert` in the checking path (`core/fold_reconcile.py`'s rule): it vanishes under `-O`.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
F078 = REPO / "data" / "control" / "f078"
DUMP = F078 / "f078_identity.volume_dump.txt"
EXPECTED = F078 / "f078_identity_expected.json"
PROGRESS = REPO / "data" / "control" / "task4_slice2" / "progress.csv"

FIRST_JOB, LAST_JOB = 4869, 4905
#: progress.csv is written on the fold host's LOCAL clock; 2026-09-13 is PDT.
PROGRESS_UTC_OFFSET = dt.timezone(dt.timedelta(hours=-7))
MAX_CLOCK_GAP_S = 60

THREE = dict(ALA="A", ARG="R", ASN="N", ASP="D", CYS="C", GLN="Q", GLU="E", GLY="G", HIS="H",
             ILE="I", LEU="L", LYS="K", MET="M", PHE="F", PRO="P", SER="S", THR="T", TRP="W",
             TYR="Y", VAL="V")


def decode(raw: bytes) -> str:
    """The owner's capture came through a PowerShell redirect, which wrote UTF-16 with a BOM."""
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig")


def parse_dump(text: str) -> tuple[dict[int, dict], dict[int, str]]:
    prov: dict[int, dict] = {}
    seqs: dict[int, list[str]] = {}
    for line in text.splitlines():
        m = re.match(r"^(\d+)/provenance\.json:\s*\"(\w+)\":\s*(.+?),?\s*$", line)
        if m:
            prov.setdefault(int(m[1]), {})[m[2]] = json.loads(m[3])
            continue
        m = re.match(r"^(\d+)/structure\.pdb:(ATOM.*)$", line)
        if m and m[2][12:16].strip() == "CA":
            seqs.setdefault(int(m[1]), []).append(THREE.get(m[2][17:20], "X"))
    return prov, {j: "".join(s) for j, s in seqs.items()}


def check(prov: dict[int, dict], seqs: dict[int, str], expected: dict[int, dict],
          progress_at: dict[int, str]) -> list[tuple[int, str, list[str]]]:
    jobs = list(range(FIRST_JOB, LAST_JOB + 1))
    out = []
    for i, j in enumerate(jobs):
        e = expected[j]
        acc, span = e["accession"], e["span_aa"]
        p, s = prov.get(j), seqs.get(j, "")
        fails: list[str] = []
        if not p or not s:
            out.append((j, acc, ["missing provenance or CA lines in the dump"]))
            continue
        st, en = p.get("ecd_start"), p.get("ecd_end")
        sl = e["uniprot_sequence"][st - 1:en] if isinstance(st, int) and isinstance(en, int) else None
        if sl != s:
            fails.append(f"sequence != UniProt[{st}..{en}] (pdb {s[:12]}.. uniprot {str(sl)[:12]}..)")
        if p.get("input_length") != span or len(s) != span:
            fails.append(f"length pdb={len(s)} input_length={p.get('input_length')} span={span}")
        folded = dt.datetime.fromisoformat(p["folded_at"]).astimezone(dt.timezone.utc)
        local = dt.datetime.fromisoformat(progress_at[j]).replace(tzinfo=PROGRESS_UTC_OFFSET)
        gap = abs((folded - local.astimezone(dt.timezone.utc)).total_seconds())
        if gap > MAX_CLOCK_GAP_S:
            fails.append(f"folded_at {folded.isoformat()} vs progress {local.isoformat()} gap {gap:.0f}s")
        other = expected[jobs[(i + 1) % len(jobs)]]
        if other["accession"] != acc and s in other["uniprot_sequence"]:
            fails.append(f"NEGATIVE CONTROL FAILED: sequence also found in {other['accession']}")
        out.append((j, acc, fails))
    return out


def load_expected() -> dict[int, dict]:
    return {r["job_id"]: r for r in json.loads(EXPECTED.read_text(encoding="utf-8"))["rows"]}


def load_progress_at() -> dict[int, str]:
    with open(PROGRESS, newline="", encoding="utf-8") as fh:
        return {int(r["job_id"]): r["at"] for r in csv.DictReader(fh)}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    dump = pathlib.Path(argv[0]) if argv else DUMP
    prov, seqs = parse_dump(decode(dump.read_bytes()))
    results = check(prov, seqs, load_expected(), load_progress_at())
    for j, acc, fails in results:
        print(f"{j} {acc:<8} {'OK' if not fails else 'FAIL: ' + '; '.join(fails)}")
    ok = sum(not f for _, _, f in results)
    print(f"\nidentity confirmed: {ok} of {len(results)}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
