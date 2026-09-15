#!/usr/bin/env python3
"""D-167 — RE-ATTACH slice 2's 37 rows to the ESMFold folds already on the volume. OWNER-GATED.

    python scripts/d167_reattach.py --print-capture-command          # the owner pastes the printed line
    flyctl ssh sftp get /tmp/d167_capture.json data/control/d167/capture.json
    python scripts/d167_reattach.py --url <tunnel> --capture data/control/d167/capture.json --capture-sha <pasted>
    python scripts/d167_reattach.py --url <tunnel> --capture ... --capture-sha ... --i-am-the-owner
    python scripts/d167_reattach.py --url <tunnel> --witness            # 480 before, 517 after
    python scripts/d167_reattach.py --url <tunnel> --revert [--i-am-the-owner]

⚠⚠ **THE DESIGN IS `D-167` AND ITS AMENDMENT 1**, transcribed, not adapted. Every value the write sets
is copied from a measured control (jobs 4866-4868 in `data/control/d167/state_before.json`) or from
the in-sitting volume capture — never from what a completed row is remembered to look like.

⚠⚠ **THE DIRECTORY IS THE JOB ID, NOT THE ANALYSIS ID** (`D-167` §2). Job 4869's analysis is 4870
and its structure is `/data/artifacts/4869/structure.pdb`. A write keyed by `analysis_id` would point
every row at its neighbour and pass every check except identity.

Order, each a refusal that writes nothing:

1. `verify()` — PURE, before any connection opens: capture sha256 == the pasted value; `captured_at`
   within 60 min; every directory present with the controls' file set; the controls' paths equal their
   stored paths in `_write_files`' format, and their provenance equals the stored `fold_provenance`;
   structure bytes == `progress.csv` served bytes (only once the controls show that equality);
   `f078_identity_check.check()` 37/37; no drift from the committed volume dump; the pLDDT summary;
   and `round(mean(plddt.json), 2)` == provenance `mean_plddt` for all 40 (A3.4).
2. the served-surface probe, calibrated: controls 200 with sha == capture, the 37 404.
3. in ONE transaction (read-only for the dry run, by the database): role preamble (A3.2/A4.2) →
   `assert_campaign_target` → no `claimed` job → slice 2's complete siblings grouped by
   `structure_source` equal the before-state (A3.1) → every one of the 40 rows equals
   `state_before.json` column for column → 37 + 37 updates, each rowcount 1.
4. after commit: the 37 serve 200 with sha == capture and `fold_provenance` == captured. A mismatch
   exits 3 and writes nothing more; `--revert --i-am-the-owner` restores `state_before.json` exactly.

⚠ `completed_at` is RECONSTRUCTED — `fold_provenance.folded_at` (the worker's clock) + `wall_seconds`
— and said so in `metadata.reattach`. The control residual against the server's clock is ±0.08 s.
`progress.csv`'s local `at` is never read. `worker_id` and `claimed_at` stay NULL: the claim record
was lost at the `F-078` boundary and no artifact holds it (A3.5).

⚠ Code never passes `--i-am-the-owner` (`F-075`). Tunnel: bound by name, Direct IP vs
`fly mpg status` pasted before the first command and the closure after (A4.3), `127.0.0.1` in the URL.

⚠ PowerShell: the printed capture command carries `\\"` escapes. Run it from Git Bash, or put `--%`
after `flyctl` so PowerShell passes the rest verbatim.
"""

from __future__ import annotations

import argparse
import base64
import collections
import copy
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from typing import Any, Callable, NamedTuple, Optional

from sqlalchemy import create_engine, text

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import scripts.f078_identity_check as ic                                   # noqa: E402
from core.db_identity import WrongDatabase, assert_campaign_target         # noqa: E402
from core.db_role import format_preamble, index_build_refusal, role_preamble  # noqa: E402
from db.dburl import normalize_db_url                                      # noqa: E402
from scripts.d166_collapse_duplicate_tiles import CLAIMED_SQL              # noqa: E402
from scripts.d167_read_state import read_only_transaction                  # noqa: E402

BASE = "https://pharmfoldmdk.fly.dev"
STATE_BEFORE = REPO / "data" / "control" / "d167" / "state_before.json"
CAPTURE_PATH = REPO / "data" / "control" / "d167" / "capture.json"
CAPTURE_MODULE = REPO / "scripts" / "d167_volume_capture.py"
PROGRESS = ic.PROGRESS

ROOT = "/data/artifacts"
FIRST, LAST = 4869, 4905
OWED = tuple(range(FIRST, LAST + 1))
CONTROLS = (4866, 4867, 4868)
SLICE2_IDS = (4389, 4905)
SLICE2_KEY = "id range 4389-4905"
MAX_CAPTURE_AGE_S = 3600
#: ⚠ A cross-check computed from the provenance, not assumed (`PREWORK-2026-09-16` §1).
PLDDT_SUMMARY = (55.21, 46.86, 75.05)
DRIFT_FIELDS = ("input_length", "ecd_start", "ecd_end", "mean_plddt", "folded_at")
REQUIRED_FILES = {"structure.pdb", "plddt.json", "provenance.json"}


class Failure(NamedTuple):
    clause: str
    job: Optional[int]
    message: str


class Refusal(Exception):
    """Raised inside a transaction so the transaction rolls back having written nothing."""


def load_progress() -> dict[int, dict]:
    with open(PROGRESS, newline="", encoding="utf-8") as fh:
        return {int(r["job_id"]): r for r in csv.DictReader(fh)}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


# ── 1. verify: pure, before any connection opens ────────────────────────────────────────────────

def verify(raw: bytes, pasted_sha: str, *, now: dt.datetime, state_before: dict) -> list[Failure]:
    """Every precondition of `D-167` §4, returning ALL failures so each lands on its own row."""
    fails: list[Failure] = []

    def fail(clause: str, job: Optional[int], message: str) -> None:
        fails.append(Failure(clause, job, message))

    got = sha256(raw)
    if got != (pasted_sha or "").strip().lower():
        fail("1 capture sha256", None, f"file sha256 {got} != pasted {pasted_sha!r}")
    cap = json.loads(raw.decode("utf-8"))
    captured = dt.datetime.fromisoformat(cap["captured_at"])
    if captured.utcoffset() != dt.timedelta(0):
        fail("2 captured_at age", None, f"captured_at {cap['captured_at']} is not UTC")
    elif abs((now - captured).total_seconds()) > MAX_CAPTURE_AGE_S:
        fail("2 captured_at age", None, f"captured_at {cap['captured_at']} is more than "
             f"{MAX_CAPTURE_AGE_S // 60} min from now ({now.isoformat()})")

    controls = {c["job"]["id"]: c for c in state_before["control"]}
    owed = {r["job"]["id"]: r for r in state_before["owed_37"]}
    if tuple(sorted(controls)) != CONTROLS or tuple(sorted(owed)) != OWED:
        fail("0 state_before", None, f"controls {sorted(controls)} / owed {len(owed)} rows")
        return fails
    progress = load_progress()
    dirs = cap.get("dirs", {})
    bad: set[int] = set()

    # 3 — presence and the controls' file set
    sets: dict[int, frozenset] = {}
    for j in CONTROLS + OWED:
        d = dirs.get(str(j))
        if not d or not d.get("present"):
            fail("3 file set", j, "directory absent from the capture")
            bad.add(j)
        else:
            sets[j] = frozenset(d.get("files", {}))
    control_sets = [sets[j] for j in CONTROLS if j in sets]
    if not control_sets:
        fail("3 file set", None, "no control directory was captured; nothing to calibrate against")
        return fails
    reference = collections.Counter(control_sets).most_common(1)[0][0]
    if not REQUIRED_FILES <= reference:
        fail("3 file set", None, f"the controls' file set {sorted(reference)} lacks {sorted(REQUIRED_FILES)}")
        return fails
    for j, s in sets.items():
        if s != reference:
            fail("3 file set", j, f"files {sorted(s)} != the controls' {sorted(reference)}")
            bad.add(j)

    # 4 — the path frame, calibrated on the controls first; control provenance == stored
    for j in CONTROLS:
        if j in bad:
            continue
        a, files = controls[j]["analysis"], dirs[str(j)]["files"]
        if not (files["structure.pdb"]["path"] == a["pdb_path"] == f"{ROOT}/{j}/structure.pdb"):
            fail("4 path frame", j, f"captured {files['structure.pdb']['path']!r}, stored "
                 f"{a['pdb_path']!r}, _write_files format {ROOT}/{j}/structure.pdb")
            bad.add(j)
            continue
        if "pae.json.gz" in files and not (
                files["pae.json.gz"]["path"] == a["pae_json_path"] == f"{ROOT}/{j}/pae.json.gz"):
            fail("4 path frame", j, f"pae captured {files['pae.json.gz']['path']!r} stored "
                 f"{a['pae_json_path']!r}")
            bad.add(j)
            continue
        if dirs[str(j)].get("provenance") != a["metadata"].get("fold_provenance"):
            fail("4 control provenance", j, "captured provenance.json != the stored fold_provenance")
            bad.add(j)
    for j in OWED:
        if j in bad:
            continue
        files = dirs[str(j)]["files"]
        for name in ("structure.pdb", "pae.json.gz"):
            if name in files and files[name]["path"] != f"{ROOT}/{j}/{name}":
                fail("4 path frame", j, f"{name} at {files[name]['path']!r}, not {ROOT}/{j}/{name}")
                bad.add(j)

    # 5 — disk bytes vs served bytes: only once the controls show the two frames agree
    control_mismatch = [j for j in CONTROLS if j not in bad and dirs[str(j)]["files"]["structure.pdb"]["size"]
                        != int(progress[j]["served_structure_bytes"])]
    if control_mismatch:
        for j in control_mismatch:
            fail("5 size frame (controls)", j, "disk size != progress.csv served bytes on a CONTROL: "
                 "the two frames differ, so the 37 are not compared")
    else:
        for j in OWED:
            if j in bad:
                continue
            disk = dirs[str(j)]["files"]["structure.pdb"]["size"]
            served = int(progress[j]["served_structure_bytes"])
            if disk != served:
                fail("5 size", j, f"structure.pdb {disk} bytes != progress.csv {served}")

    # 6 — identity, by the one checker (f078_identity_check)
    ok = [j for j in OWED if j not in bad]
    prov = {j: dirs[str(j)]["provenance"] for j in ok
            if isinstance(dirs[str(j)].get("provenance"), dict) and "folded_at" in dirs[str(j)]["provenance"]}
    seqs = {j: "".join(ic.THREE.get(r, "X") for r in dirs[str(j)].get("ca_residues") or []) for j in ok}
    for j, acc, reasons in ic.check(prov, seqs, ic.load_expected(), ic.load_progress_at()):
        if j not in bad and reasons:
            fail("6 identity", j, f"{acc}: {'; '.join(reasons)}")

    # 7 — drift from the committed volume dump
    dump_prov, _ = ic.parse_dump(ic.decode(ic.DUMP.read_bytes()))
    for j in ok:
        p = prov.get(j, {})
        for field in DRIFT_FIELDS:
            if p.get(field) != dump_prov.get(j, {}).get(field):
                fail("7 drift vs volume dump", j,
                     f"{field}: capture {p.get(field)!r} != dump {dump_prov.get(j, {}).get(field)!r}")

    # 8 — the pLDDT summary, computed
    means = [prov[j]["mean_plddt"] for j in OWED if j in prov
             and isinstance(prov[j].get("mean_plddt"), (int, float))]
    if len(means) == len(OWED):
        summary = (round(sum(means) / len(means), 2), min(means), max(means))
        if summary != PLDDT_SUMMARY:
            fail("8 pLDDT summary", None, f"mean/min/max {summary} != pre-work {PLDDT_SUMMARY}")

    # 9 — A3.4: the per-residue array agrees with the provenance, on all 40
    for j in CONTROLS + OWED:
        if j in bad:
            continue
        d = dirs[str(j)]
        arr, p = d.get("plddt"), d.get("provenance") or {}
        if not isinstance(arr, list) or not arr:
            fail("9 plddt.json mean", j, "no per-residue pLDDT array")
            continue
        mean = round(sum(arr) / len(arr), 2)
        if mean != p.get("mean_plddt"):
            fail("9 plddt.json mean", j, f"round(mean(plddt.json), 2) {mean} != provenance {p.get('mean_plddt')}")
        elif j in controls and mean != controls[j]["analysis"]["mean_plddt"]:
            fail("9 plddt.json mean", j, f"control mean {mean} != stored column {controls[j]['analysis']['mean_plddt']}")
    return fails


# ── 2. the plan: pure ───────────────────────────────────────────────────────────────────────────

def reconstruct_completed_at(folded_at: str, wall_seconds: Any) -> dt.datetime:
    """`folded_at` (UTC, the worker's clock) + `wall_seconds`. ⚠ Reconstructed, and said so."""
    t = dt.datetime.fromisoformat(folded_at)
    if t.utcoffset() != dt.timedelta(0):
        raise Refusal(f"folded_at {folded_at} is not UTC")
    return (t + dt.timedelta(seconds=float(wall_seconds))).astimezone(dt.timezone.utc)


def build_plan(capture: dict, state_before: dict, progress: dict[int, dict], *,
               now: dt.datetime, capture_sha: str) -> list[dict]:
    """The 37 row writes, keyed by JOB id, copying the controls' `structure_source` and `tier`."""
    sources = {c["analysis"]["structure_source"] for c in state_before["control"]}
    tiers = {c["job"]["tier"] for c in state_before["control"]}
    if len(sources) != 1 or len(tiers) != 1:
        raise Refusal(f"the controls disagree: structure_source {sources}, tier {tiers}")
    source, tier = next(iter(sources)), next(iter(tiers))
    written_at = now.astimezone(dt.timezone.utc).isoformat()
    plan = []
    for row in sorted(state_before["owed_37"], key=lambda r: r["job"]["id"]):
        job, analysis = row["job"], row["analysis"]
        j = job["id"]
        d = capture["dirs"][str(j)]
        files, prov = d["files"], d["provenance"]
        pdb_path = f"{ROOT}/{j}/structure.pdb"
        if files["structure.pdb"]["path"] != pdb_path:
            raise Refusal(f"job {j}: captured structure at {files['structure.pdb']['path']!r}, not {pdb_path}")
        meta = copy.deepcopy(analysis["metadata"] or {})
        meta["fold_provenance"] = copy.deepcopy(prov)
        meta["reattach"] = {"decision": "D-167", "written_at": written_at, "capture_sha256": capture_sha,
                            "completed_at_reconstructed": True,
                            "claim_record": "lost at the F-078 boundary"}
        plan.append({
            "job_id": j,
            "analysis_id": job["analysis_id"],
            "status_before": job["status"],
            "pdb_path": pdb_path,
            "pae_json_path": f"{ROOT}/{j}/pae.json.gz" if "pae.json.gz" in files else None,
            "mean_plddt": prov["mean_plddt"],
            "structure_source": source,
            "tier": tier,
            "completed_at": reconstruct_completed_at(prov["folded_at"], progress[j]["wall_seconds"]),
            "metadata": meta,
        })
    return plan


def capture_command() -> str:
    payload = base64.b64encode(CAPTURE_MODULE.read_bytes()).decode("ascii")
    return f'flyctl ssh console -C "python -c \\"import base64;exec(base64.b64decode(\'{payload}\'))\\""'


# ── 3. the served surface ───────────────────────────────────────────────────────────────────────

Fetch = Callable[[str], "tuple[int, bytes]"]


def http_fetch(url: str) -> tuple[int, bytes]:
    """⚠ A 404 is an answer; any other error RAISES — an outage is never reported as 'absent'."""
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 404, b""
        raise


def probe_before(fetch: Fetch, plan: list[dict], capture: dict, state_before: dict, base: str) -> list[str]:
    bad = []
    for c in state_before["control"]:
        j, aid = c["job"]["id"], c["job"]["analysis_id"]
        status, body = fetch(f"{base}/api/analyses/{aid}/structure")
        want = capture["dirs"][str(j)]["files"]["structure.pdb"]["sha256"]
        if status != 200 or sha256(body) != want:
            bad.append(f"control job {j}: served {status} sha {sha256(body)[:16]} != disk {want[:16]} - "
                       f"the probe cannot separate the two states, so it proves nothing")
    for p in plan:
        status, _ = fetch(f"{base}/api/analyses/{p['analysis_id']}/structure")
        if status != 404:
            bad.append(f"job {p['job_id']}: served {status} before the write, expected 404")
    return bad


def probe_after(fetch: Fetch, plan: list[dict], capture: dict, base: str) -> list[str]:
    bad = []
    for p in plan:
        d = capture["dirs"][str(p["job_id"])]
        status, body = fetch(f"{base}/api/analyses/{p['analysis_id']}/structure")
        if status != 200 or sha256(body) != d["files"]["structure.pdb"]["sha256"]:
            bad.append(f"job {p['job_id']}: structure served {status}, sha {sha256(body)[:16]} != capture")
        status, body = fetch(f"{base}/api/analyses/{p['analysis_id']}")
        served = json.loads(body).get("fold_provenance") if status == 200 else None
        if served != d["provenance"]:
            bad.append(f"job {p['job_id']}: served fold_provenance != captured provenance.json")
    return bad


# ── 4. the database ─────────────────────────────────────────────────────────────────────────────

def reread(conn) -> list[dict]:
    jobs = [r[0] for r in conn.execute(text(
        "SELECT to_jsonb(j) FROM jobs j WHERE j.id BETWEEN :a AND :b ORDER BY j.id"),
        {"a": CONTROLS[0], "b": LAST})]
    analyses = {r[0]["id"]: r[0] for r in conn.execute(text(
        "SELECT to_jsonb(a) FROM protein_analyses a "
        "WHERE a.id IN (SELECT analysis_id FROM jobs WHERE id BETWEEN :a AND :b)"),
        {"a": CONTROLS[0], "b": LAST})}
    return [{"job": j, "analysis": analyses.get(j["analysis_id"])} for j in jobs]


def differences(rows: list[dict], state_before: dict) -> list[str]:
    want = {r["job"]["id"]: r for r in state_before["control"] + state_before["owed_37"]}
    got = {r["job"]["id"]: r for r in rows}
    out = []
    for j in sorted(set(want) | set(got)):
        if j not in want or j not in got:
            out.append(f"job {j}: in {'the database' if j in got else 'state_before'} only")
            continue
        for part in ("job", "analysis"):
            w, g = want[j][part] or {}, got[j][part] or {}
            for col in sorted(set(w) | set(g)):
                if w.get(col) != g.get(col):
                    out.append(f"job {j} {part}.{col}: before {w.get(col)!r}, now {g.get(col)!r}")
    return out


def sibling_sources(conn) -> dict[str, int]:
    return {r[0]: r[1] for r in conn.execute(text(
        "SELECT a.structure_source, count(*) FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
        "WHERE j.id BETWEEN :lo AND :hi AND j.status = 'complete' AND a.pdb_path IS NOT NULL "
        "GROUP BY 1 ORDER BY 1"), {"lo": SLICE2_IDS[0], "hi": SLICE2_IDS[1]})}


def witness(conn) -> int:
    """`F-080`: slice 2's rows complete with a structure, keyed by id range. Read-only."""
    for line in format_preamble(role_preamble(conn)):
        print(line)
    assert_campaign_target(conn)
    return conn.execute(text(
        "SELECT count(*) FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
        "WHERE j.id BETWEEN :lo AND :hi AND j.status = 'complete' AND a.pdb_path IS NOT NULL"),
        {"lo": SLICE2_IDS[0], "hi": SLICE2_IDS[1]}).scalar()


def apply(conn, plan: list[dict], state_before: dict, *, write: bool,
          say: Callable[[str], None] = print) -> None:
    """`D-167` §4 steps 1-8 in one transaction. Raises `Refusal`/`WrongDatabase` having written nothing."""
    pre = role_preamble(conn)
    for line in format_preamble(pre):
        say(line)
    refusal = index_build_refusal(pre)
    if refusal:
        say(f"  ⚠ {refusal}\n  ⚠ The re-attach depends on neither the collapse nor 0014: it PROCEEDS (A4.2).")
    assert_campaign_target(conn)
    say("D-159: ACCEPTED (cluster identity, floor, anchor)")

    claimed = [r[0] for r in conn.execute(CLAIMED_SQL)]
    if claimed:
        raise Refusal(f"{len(claimed)} job(s) are claimed - a fold is live: {claimed}")

    source = plan[0]["structure_source"]
    want = {source: state_before["slice2"][SLICE2_KEY]["complete_and_pdb_path"]}
    got = sibling_sources(conn)
    if got != want:
        raise Refusal(f"slice 2's complete siblings by structure_source are {got}, expected {want} (A3.1)")
    say(f"siblings by structure_source: {got}")

    diffs = differences(reread(conn), state_before)
    if diffs:
        raise Refusal("rows changed since the Phase B read:\n  " + "\n  ".join(diffs[:40]))
    say("the 40 rows equal state_before.json column for column")

    if not write:
        return
    written_a = written_j = 0
    for p in plan:
        sets = "pdb_path = :pdb, mean_plddt = :m, structure_source = :s, metadata = CAST(:md AS jsonb)"
        params = {"pdb": p["pdb_path"], "m": p["mean_plddt"], "s": p["structure_source"],
                  "md": json.dumps(p["metadata"]), "aid": p["analysis_id"]}
        if p["pae_json_path"] is not None:              # D-106: omit the SET when absent
            sets += ", pae_json_path = :pae"
            params["pae"] = p["pae_json_path"]
        n = conn.execute(text(f"UPDATE protein_analyses SET {sets} WHERE id = :aid AND pdb_path IS NULL"),
                         params).rowcount
        if n != 1:
            raise Refusal(f"analysis {p['analysis_id']}: rowcount {n}, expected 1")
        written_a += 1
        n = conn.execute(text(
            "UPDATE jobs SET status = 'complete', completed_at = :c, tier = :t "
            "WHERE id = :j AND status = :s0 AND tier IS NULL"),
            {"c": p["completed_at"], "t": p["tier"], "j": p["job_id"], "s0": p["status_before"]}).rowcount
        if n != 1:
            raise Refusal(f"job {p['job_id']}: rowcount {n}, expected 1")
        written_j += 1
    if (written_a, written_j) != (len(OWED), len(OWED)):
        raise Refusal(f"wrote {written_a} analyses and {written_j} jobs, expected {len(OWED)} and {len(OWED)}")


def revert(conn, state_before: dict, *, write: bool, say: Callable[[str], None] = print) -> None:
    """Restore the 37 rows to `state_before.json` exactly, under the same guards."""
    for line in format_preamble(role_preamble(conn)):
        say(line)
    assert_campaign_target(conn)
    claimed = [r[0] for r in conn.execute(CLAIMED_SQL)]
    if claimed:
        raise Refusal(f"{len(claimed)} job(s) are claimed - a fold is live: {claimed}")
    aids = [r["analysis"]["id"] for r in state_before["owed_37"]]
    carrying = conn.execute(text(
        "SELECT count(*) FROM protein_analyses WHERE id = ANY(:a) AND metadata ? 'reattach'"),
        {"a": aids}).scalar()
    say(f"rows carrying metadata.reattach: {carrying} of {len(aids)}")
    if not write:
        return
    for row in state_before["owed_37"]:
        a, j = row["analysis"], row["job"]
        n = conn.execute(text(
            "UPDATE protein_analyses SET pdb_path = :p, pae_json_path = :pae, mean_plddt = :m, "
            "structure_source = :s, metadata = CAST(:md AS jsonb) "
            "WHERE id = :aid AND metadata ? 'reattach'"),
            {"p": a["pdb_path"], "pae": a["pae_json_path"], "m": a["mean_plddt"],
             "s": a["structure_source"], "md": json.dumps(a["metadata"]), "aid": a["id"]}).rowcount
        if n != 1:
            raise Refusal(f"revert analysis {a['id']}: rowcount {n}, expected 1")
        n = conn.execute(text(
            "UPDATE jobs SET status = :st, tier = :t, completed_at = CAST(:c AS timestamptz), "
            "attempts = :n, worker_id = :w, claimed_at = CAST(:ca AS timestamptz), error = :e "
            "WHERE id = :j AND status = 'complete'"),
            {"st": j["status"], "t": j["tier"], "c": j["completed_at"], "n": j["attempts"],
             "w": j["worker_id"], "ca": j["claimed_at"], "e": j["error"], "j": j["id"]}).rowcount
        if n != 1:
            raise Refusal(f"revert job {j['id']}: rowcount {n}, expected 1")
    diffs = differences(reread(conn), state_before)
    if diffs:
        raise Refusal("the revert does not reproduce state_before.json:\n  " + "\n  ".join(diffs[:40]))


# ── 5. main ─────────────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None, fetch: Optional[Fetch] = None) -> int:
    ap = argparse.ArgumentParser(description="D-167 re-attach of slice 2's 37 (owner-gated)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--capture", default=str(CAPTURE_PATH))
    ap.add_argument("--capture-sha", default="")
    ap.add_argument("--state-before", default=str(STATE_BEFORE))
    ap.add_argument("--base-url", default=BASE)
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--witness", action="store_true")
    ap.add_argument("--print-capture-command", action="store_true")
    args = ap.parse_args(argv)
    fetch = fetch or http_fetch

    if args.print_capture_command:
        print(capture_command())
        print("flyctl ssh sftp get /tmp/d167_capture.json data/control/d167/capture.json")
        print("# PowerShell: insert --% after flyctl in the first line, or run it from Git Bash.")
        return 0
    if not args.url:
        print("REFUSING: no --url and no DATABASE_URL. The operator names the target.")
        return 1
    state = json.loads(pathlib.Path(args.state_before).read_text(encoding="utf-8"))

    def engine():
        return create_engine(normalize_db_url(args.url), future=True, connect_args={"connect_timeout": 15})

    try:
        if args.witness:
            eng = engine()
            try:
                with read_only_transaction(eng) as conn:
                    n = witness(conn)
            finally:
                eng.dispose()
            print(f"witness: {n}")
            print(f"  key: jobs {SLICE2_IDS[0]}-{SLICE2_IDS[1]}, complete AND pdb_path IS NOT NULL. "
                  f"Phase B read {state['slice2'][SLICE2_KEY]['complete_and_pdb_path']} on this key.")
            return 0

        if args.revert:
            eng = engine()
            try:
                if args.owner:
                    with eng.begin() as conn:
                        revert(conn, state, write=True)
                    print("\n✓ REVERTED: the 37 rows equal state_before.json.")
                else:
                    with read_only_transaction(eng) as conn:
                        revert(conn, state, write=False)
                    print("\nDRY RUN - nothing was written. Re-run with --i-am-the-owner to revert.")
            finally:
                eng.dispose()
            return 0

        if not args.capture_sha:
            print("REFUSING: no --capture-sha. The owner pastes the sha256 the machine printed.")
            return 1
        raw = pathlib.Path(args.capture).read_bytes()
        now = dt.datetime.now(dt.timezone.utc)
        failures = verify(raw, args.capture_sha, now=now, state_before=state)
        if failures:
            print(f"REFUSING: {len(failures)} precondition failure(s), nothing was connected to:")
            for f in failures:
                print(f"  [{f.clause}] job {f.job if f.job is not None else '-'}: {f.message}")
            return 1
        print("1. verify: every precondition met (40 directories, identity 37/37, pLDDT 40/40)")
        capture = json.loads(raw.decode("utf-8"))
        plan = build_plan(capture, state, load_progress(), now=now, capture_sha=sha256(raw))

        bad = probe_before(fetch, plan, capture, state, args.base_url)
        if bad:
            print("REFUSING: the served-surface probe is not calibrated:")
            for b in bad:
                print(f"  {b}")
            return 1
        print("2. probe calibrated: controls 200 with sha == capture, the 37 404")

        eng = engine()
        try:
            if not args.owner:
                with read_only_transaction(eng) as conn:
                    apply(conn, plan, state, write=False)
                print("\n3. WHAT THE WRITE WOULD DO: 37 protein_analyses + 37 jobs rows")
                for p in plan[:3] + [{"job_id": "..."}] + plan[-1:]:
                    print(f"   {p}" if p["job_id"] == "..." else
                          f"   job {p['job_id']} -> analysis {p['analysis_id']}  {p['pdb_path']}  "
                          f"plddt {p['mean_plddt']}  completed_at {p['completed_at'].isoformat()}")
                print("\nDRY RUN - nothing was written. Re-run with --i-am-the-owner. OWNER AT THE KEYBOARD (F-075).")
                return 0
            with eng.begin() as conn:
                apply(conn, plan, state, write=True)
        finally:
            eng.dispose()

        bad = probe_after(fetch, plan, capture, args.base_url)
        if bad:
            print("\nPOST-WRITE PROBE MISMATCH - nothing more is written automatically:")
            for b in bad:
                print(f"  {b}")
            print("  Report it. `--revert --i-am-the-owner` restores state_before.json.")
            return 3
        print(f"\n✓ RE-ATTACHED {len(plan)} rows; every structure serves the captured bytes and provenance.")
        print("NEXT: python scripts/d167_reattach.py --url <tunnel> --witness   # expect 517")
        return 0
    except (Refusal, WrongDatabase) as e:
        print(f"\nREFUSING: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
