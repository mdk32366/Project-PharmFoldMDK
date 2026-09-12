#!/usr/bin/env python3
"""Task 4 — bounded slice 1: band **251–384**, n = **346**. ⚠ The first UNSUPERVISED campaign.

    python scripts/task4_slice1.py --enumerate                    # reports, writes NOTHING
    python scripts/task4_slice1.py --enqueue --i-am-the-owner     # writes the 346 Run 2 rows
    python scripts/task4_slice1.py --fold --i-am-the-owner        # folds them, unattended
    python scripts/task4_slice1.py --report                       # the harvest

⚠⚠ **AMENDMENT 9's THIRD EXPRESS EXCEPTION TO §4.2 IN TWO DAYS, AND FOR THIS SLICE ONLY.** The
owner overrode `(iii)` — fold to staging, production load separate — because no staging target
exists. ⚠ **The remaining ~2,226 rows require a fresh ruling; `(iii)` is not retired, it is
unbuilt and deferred.** Do not chain slices.

⚠ **Why this band and not an easier one.** It is the band where wall time is **NOT** flat —
mean **53.2 s** against ~16.5 s below 44 aa — so it exercises the fold path where the weight
reload does **not** dominate. **It is the part of the campaign least like the twenty already
proven**, which is the point of running it first.

**⚠⚠ WHAT "UNSUPERVISED" CHANGES, AND IT IS THE WHOLE DESIGN OF THIS FILE.** Nobody is watching
after ~13:00. So every failure mode has to be survivable *or* stop cleanly:

- **a crash loses ONE fold, not 346** — `D-105`'s child exits between folds and the queue holds
  the rest `pending`, so a restart resumes where it stopped;
- ⚠ **the run never spins.** Thursday's loop polled an empty queue forever because a refused fold
  recorded nothing. There is an **idle deadline** here: no progress for `IDLE_STOP_S` and it
  stops **cleanly**, writing its record;
- ⚠⚠ **a fold failure is not fatal; a broken PERSISTENCE PATH is.** `FATAL_STREAK` consecutive
  folds whose artifact does not land stops the campaign rather than producing 300 more unusable
  rows. **Thursday's eleven empty rows are why this clause exists.**
- **progress is written as it goes**, never only at the end — a five-hour run that reports on
  completion tells the owner nothing at 13:00 and nothing if it dies at hour four.

⚠ **The fold needs NO TUNNEL.** The worker talks to Fly over HTTPS — claim, upload, complete,
`persist_pae` — and the preflight and the GPU are local. `DATABASE_URL` is needed for
`--enumerate`'s cross-check, `--enqueue` and `--report` only. **A dropped tunnel cannot interrupt
the fold**, which is the single biggest thing that makes this survivable unattended.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
import time
from typing import Any, Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.task3_run2_folds import (          # noqa: E402 — REUSE, do not re-derive
    CAP_AA,
    RUN_LABEL,
    FoldRecorder,
    _engine,
    _existing_run2,
    _head_served,
    _rel,
    _served_structure_is_empty,
    cuda_ready,
    make_fold_callable,
    worker_tier,
)

#: ⚠⚠ THE HARD BOUND, IN THE TOOL RATHER THAN IN THE INVOCATION. A band passed on the command
#: line is a band that can be mistyped at 13:00 by someone who has stopped reading.
BAND = (251, 384)
EXPECTED_N = 346
#: ⚠ `F-063` reached `highest_ok = 384` and the host bugchecked before 392; `F-064` is the
#: post-fold headroom collapse. Both OPEN. `BAND[1]` may never exceed this.
assert BAND[1] <= CAP_AA, "the band's ceiling is above the measured-safe envelope"

OUT_DIR = REPO / "data" / "control" / "task4_slice1"
ENUMERATION_JSON = OUT_DIR / "enumeration.json"
ENQUEUED_JSON = OUT_DIR / "enqueued.json"
PROGRESS_CSV = OUT_DIR / "progress.csv"

#: ⚠⚠ N consecutive folds whose artifact does not land. Not a count of FOLD failures — a fold can
#: fail for its own reasons — but of the PERSISTENCE PATH failing, which is systemic and will not
#: fix itself over the next 300 rows.
FATAL_STREAK = 3
#: ⚠ No progress for this long and the run stops CLEANLY, writing its record. This is the answer
#: to Thursday's forever-poll: the stop condition must be reachable when nothing is being folded.
IDLE_STOP_S = 20 * 60
#: ⚠ A backstop on total wall clock. The twenty projected 5.12 h for this band; this is generous
#: and exists so an unattended run cannot outlive the day.
MAX_WALL_S = 10 * 60 * 60

PROGRESS_COLUMNS = [
    "fold_index", "accession", "job_id", "analysis_id", "span_aa", "wall_seconds",
    "free_mib_before", "requirement_mib", "peak_allocated_mib", "peak_reserved_mib",
    "emitted_pae", "served_structure_bytes", "served_pae", "verdict", "at",
]


# ── the population ──────────────────────────────────────────────────────────────────────────

def the_band() -> list[dict[str, Any]]:
    """The 346, enumerated from the manifest. ⚠ Refuses on any count but `EXPECTED_N`.

    ⚠⚠ If this is not 346 the band definition and `D-157`'s split disagree, and that must be
    RESOLVED rather than overridden — a slice of 344 or 349 is a different population than the one
    the owner ruled on, and the projection it will be compared against was computed over 346.
    """
    lo, hi = BAND
    rows = []
    with open(REPO / "data" / "census" / "census_manifest.v7.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if str(r.get("tranche")) not in {"1", "2", "3", "4"} or not r.get("span_aa"):
                continue
            span = int(float(r["span_aa"]))
            if lo <= span <= hi:
                rows.append({"accession": r["census_accession"], "span": span,
                             "tranche": int(r["tranche"])})
    if len(rows) != EXPECTED_N:
        raise SystemExit(
            f"refusing: the band {lo}-{hi} enumerates {len(rows)} rows, not {EXPECTED_N}. The band "
            f"definition and D-157's split disagree; resolve that rather than folding a different "
            f"population than the one ruled on.")
    over = [r for r in rows if r["span"] > CAP_AA]
    if over:
        raise SystemExit(f"refusing: {len(over)} rows exceed the {CAP_AA} aa envelope.")
    return sorted(rows, key=lambda r: (r["span"], r["accession"]))


def enumerate_slice() -> int:
    """§2.1/§2.2 — count it, cross-check it against `D-157`, and write it to disk. No DB write."""
    rows = the_band()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ENUMERATION_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    from collections import Counter
    spans = [r["span"] for r in rows]
    print(f"band {BAND[0]}-{BAND[1]} inclusive, tranches 1-4: {len(rows)} rows "
          f"(expected {EXPECTED_N})")
    print(f"  by tranche : {dict(Counter(r['tranche'] for r in rows))}")
    print(f"  span range : {min(spans)} - {max(spans)}   mean {sum(spans)/len(spans):.1f}")
    print(f"  written to : {_rel(ENUMERATION_JSON)}")

    # ⚠ The cross-check, because one source agreeing with itself is not agreement.
    from scripts.task3_timing_sample import population
    sel = [r for r in population() if r["band"] == f"{BAND[0]}-{BAND[1]}"]
    print(f"\ncross-check against the projector's own population: {len(sel)} "
          f"({'AGREES' if len(sel) == len(rows) else 'DISAGREES'})")
    print("! The twenty projected 5.12 h for this band at a mean of 53.2 s per fold.")
    print("\nno database was touched. --enqueue writes; the owner is at the keyboard for that.")
    return 0


# ── enqueue ─────────────────────────────────────────────────────────────────────────────────

def enqueue(owner: bool) -> int:
    from scripts.census_ingest import assert_claimable, build_row     # noqa: PLC0415

    rows = the_band()
    by_acc = {r["accession"]: r for r in rows}
    man = {}
    with open(REPO / "data" / "census" / "census_manifest.v7.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["census_accession"] in by_acc:
                man[r["census_accession"]] = r

    payloads = []
    for acc in sorted(by_acc, key=lambda a: by_acc[a]["span"]):
        p = build_row(man[acc])
        assert_claimable(p)          # ⚠ the consumer's object, built BEFORE any row is written
        if p["meta"]["fold_length"] != by_acc[acc]["span"]:
            raise SystemExit(f"refusing: {acc} folds {p['meta']['fold_length']} aa but the band "
                             f"placed it at {by_acc[acc]['span']}.")
        payloads.append(p)
    print(f"{len(payloads)} payloads built and validated against the claim contract.")

    from sqlalchemy.orm import Session                 # noqa: PLC0415
    from db.models import JobRecord, ProteinAnalysis   # noqa: PLC0415

    written = []
    with Session(_engine()) as s:
        # ⚠⚠ THE BAND OVERLAPS TASK 3's TWENTY BY EXACTLY FOUR, AND THAT IS ARITHMETIC,
        # NOT A DEFECT. The stratified sample drew 4 rows from 251-384, and those four were
        # folded as Run 2 on 2026-09-12 with artifacts of 199-246 KB. Re-folding them would give
        # one accession TWO Run 2 rows, breaking the generation partition the campaign rests on
        # - the two-rows-per-accession hazard AMENDMENT 5 section 4.3 names.
        #
        # ⚠ The BAND is still 346 and `the_band()` still enforces that. What is ENQUEUED is
        # the complement, and the arithmetic is printed rather than assumed.
        already = _existing_run2(s, list(by_acc))
        todo = [p for p in payloads if p["accession"] not in already]
        print(f"\nband {BAND[0]}-{BAND[1]}: {len(payloads)} rows")
        print(f"  already carry a Run {RUN_LABEL} row (Task 3 sample): {len(already)} "
              f"-> {sorted(already)}")
        print(f"  to enqueue: {len(todo)}")
        if len(todo) + len(already) != EXPECTED_N:
            print(f"REFUSING: {len(todo)} + {len(already)} != {EXPECTED_N}.", file=sys.stderr)
            return 1
        if not todo:
            print("nothing to enqueue; the band is already covered.")
            return 0
        # ⚠ The owner gate sits AFTER the arithmetic, deliberately. A count you only see once
        # you have committed is a count the dry run did not check - AMENDMENT 8 section 3.2's
        # rule, and the overlap with Task 3 is exactly what a reader needs before authorising.
        if not owner:
            print("\nDRY RUN - nothing was written. Re-run with --i-am-the-owner to write.")
            return 0
        for p in todo:
            a = ProteinAnalysis(input_type="uniprot", input_value=p["accession"],
                                structure_source="esmfold_local", ranking_run_id=None,
                                cohort_tranche=p["meta"]["cohort_tranche"], meta=p["meta"])
            s.add(a)
            s.flush()
            j = JobRecord(analysis_id=a.id, status="pending", tier=p["meta"]["tier"],
                          inference_settings={**p["inference_settings"],
                                              "model_id": "facebook/esmfold_v1",
                                              "run": RUN_LABEL})
            s.add(j)
            s.flush()
            written.append({"accession": p["accession"], "analysis_id": a.id, "job_id": j.id,
                            "span_aa": p["meta"]["fold_length"]})
        s.commit()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ENQUEUED_JSON.write_text(json.dumps(written, indent=2), encoding="utf-8")
    print(f"\nWROTE {len(written)} Run {RUN_LABEL} rows. ids {written[0]['job_id']}"
          f"-{written[-1]['job_id']}, enumerated in {_rel(ENQUEUED_JSON)}")
    print(f"! band coverage: {len(written)} new + {len(already)} already folded = {EXPECTED_N}")
    return 0


# ── the unattended fold ─────────────────────────────────────────────────────────────────────

class SliceRun:
    """The unattended campaign's state: progress on disk, and every stop condition reachable."""

    def __init__(self, allowed: dict[int, dict], base_url: str) -> None:
        self.allowed = allowed
        self.base_url = base_url
        self.rec = FoldRecorder({jid: e["accession"] for jid, e in allowed.items()})
        self.started = time.time()
        self.last_progress = time.time()
        self.fatal_streak = 0
        self.stop_reason: Optional[str] = None
        self.done = 0
        self.verdicts: list[str] = []
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        if not PROGRESS_CSV.is_file():
            with open(PROGRESS_CSV, "w", newline="", encoding="utf-8") as fh:
                csv.DictWriter(fh, fieldnames=PROGRESS_COLUMNS).writeheader()

    # ⚠ Appended per fold, never buffered to the end.
    def _append(self, row: dict[str, Any]) -> None:
        with open(PROGRESS_CSV, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=PROGRESS_COLUMNS).writerow(row)

    def after_fold(self, spec, result) -> None:
        """⚠ The row is ALREADY recorded by `make_fold_callable`; this reads it and adds the
        surface verdict. Recording twice would double-count the fold index and re-run the
        gate-pairing check against a preflight that has moved on."""
        r = self.rec.rows[-1]
        e = self.allowed[spec.job_id]
        peak = (getattr(result, "fold_record", {}) or {}).get("peak_vram") or {}

        # ⚠⚠ THE PERSISTENCE CHECK, FROM THE SERVING SURFACE, PER FOLD. No tunnel needed, which is
        # what lets it run unattended. `column_null` vs `file_missing` needs the DB and is left to
        # --report; what is fatal here is simply that the artifact did not land.
        try:
            _found_s, n_bytes = _head_served(self.base_url, "structure", e["analysis_id"])
            found_p, _n = _head_served(self.base_url, "pae", e["analysis_id"])
            probe_ok = True
        except SystemExit as exc:
            # ⚠ A connection failure is a NAMED CATEGORY, never a fold failure. `refused_no_
            # measurement`'s discipline: routed out is not tried-and-broke.
            n_bytes, found_p, probe_ok = None, None, False
            verdict = f"surface_unreachable ({exc})"[:120]
        if probe_ok:
            if n_bytes == 0:
                verdict = "artifact_empty"
            elif not found_p:
                verdict = "pae_did_not_resolve"
            else:
                verdict = "ok"

        # ⚠ An unreachable surface does NOT advance the fatal streak. The streak exists to detect a
        # broken persistence path, and an outage is not that.
        if verdict == "ok" or not probe_ok:
            self.fatal_streak = 0
        else:
            self.fatal_streak += 1

        self.verdicts.append(verdict)
        self.done += 1
        self.last_progress = time.time()
        self._append({
            "fold_index": self.done, "accession": e["accession"], "job_id": spec.job_id,
            "analysis_id": e["analysis_id"], "span_aa": r["span_aa"],
            "wall_seconds": r["wall_seconds"], "free_mib_before": r["free_mib_before"],
            "requirement_mib": r["requirement_mib"],
            "peak_allocated_mib": peak.get("max_allocated_mib"),
            "peak_reserved_mib": peak.get("max_reserved_mib"),
            "emitted_pae": r["emitted_pae"], "served_structure_bytes": n_bytes,
            "served_pae": found_p, "verdict": verdict,
            "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        print(f"[{self.done:>3}/{len(self.allowed)}] {e['accession']:<9} {r['span_aa']:>4} aa  "
              f"wall={r['wall_seconds']:>7.2f}s  free={r['free_mib_before']} MiB  "
              f"bytes={n_bytes}  {verdict}", flush=True)

        if self.fatal_streak >= FATAL_STREAK:
            self.stop_reason = (f"{self.fatal_streak} consecutive folds whose artifact did not "
                                f"land - the persistence path is broken, not this fold")

    def should_stop(self) -> bool:
        if self.stop_reason:
            return True
        if self.done >= len(self.allowed):
            self.stop_reason = "all rows folded"
            return True
        idle = time.time() - self.last_progress
        if idle > IDLE_STOP_S:
            # ⚠⚠ THE ANSWER TO THURSDAY'S FOREVER-POLL. A stop condition that only counts
            # successes cannot be reached when nothing is succeeding.
            self.stop_reason = (f"no progress for {idle/60:.0f} min - stopping cleanly rather "
                                f"than polling. {self.done} of {len(self.allowed)} folded")
            return True
        if time.time() - self.started > MAX_WALL_S:
            self.stop_reason = f"wall-clock backstop of {MAX_WALL_S/3600:.0f} h reached"
            return True
        return False


def fold(owner: bool) -> int:
    if not ENQUEUED_JSON.is_file():
        print(f"refusing: {_rel(ENQUEUED_JSON)} does not exist. Run --enqueue first.",
              file=sys.stderr)
        return 1
    enqueued = {int(e["job_id"]): e for e in json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))}
    # ⚠ The fold folds what was ENQUEUED. The band bound of 346 lives in `the_band()`; the
    # enqueue writes only the rows that lacked a Run 2 row, so this count is the complement and
    # must not be re-asserted as 346.
    if not enqueued or len(enqueued) > EXPECTED_N:
        print(f"refusing: {len(enqueued)} enqueued ids is not a subset of the band.",
              file=sys.stderr)
        return 1

    ok, why = cuda_ready()
    print(f"interpreter check: {why}")
    if not ok:
        print(f"REFUSING: {why}", file=sys.stderr)
        print("Run under the CUDA interpreter (.venv/Scripts/python.exe).", file=sys.stderr)
        return 1

    base = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev")
    already = sum(1 for _ in csv.DictReader(open(PROGRESS_CSV, encoding="utf-8"))) \
        if PROGRESS_CSV.is_file() else 0
    print(f"slice 1: band {BAND[0]}-{BAND[1]}, {len(enqueued)} rows, surface {base}")
    if already:
        print(f"! RESUMING: {already} fold(s) already in {_rel(PROGRESS_CSV)}. The queue holds "
              f"the rest pending, so a restart costs one fold, not {already}.")
    print(f"stop conditions: all folded | {FATAL_STREAK} consecutive unlanded artifacts | "
          f"{IDLE_STOP_S//60} min idle | {MAX_WALL_S//3600} h wall")

    if not owner:
        print("\nDRY RUN - no fold ran. Re-run with --i-am-the-owner to fold.")
        return 0

    from core.vram_guard import preflight as real_preflight    # noqa: PLC0415
    from worker.main import (build_client, config_from_env,    # noqa: PLC0415
                             process_per_fold_fn)
    from worker.orchestrator import run_worker                 # noqa: PLC0415

    run = SliceRun(enqueued, base)
    config = config_from_env()
    client = build_client(config)
    inner = make_fold_callable(run.rec, client.persist_pae, process_per_fold_fn(), real_preflight)

    def _fold_one(spec):
        # ⚠ ONE assembly, reused. `make_fold_callable` is the seam pinned against `worker.main`'s
        # own gating (F-046); this wrapper only adds the surface check and the progress row, and
        # the recorder is shared so `free_mib_before` stays the GATE's own reading.
        result = inner(spec)
        run.after_fold(spec, result)
        return result

    try:
        run_worker(client, _fold_one, config.worker_id, poll_interval=config.poll_interval,
                   tier=worker_tier(), should_stop=run.should_stop)
    finally:
        print(f"\nSTOPPED: {run.stop_reason or 'the loop returned'}")
        print(f"{run.done} of {len(enqueued)} folded; record in {_rel(PROGRESS_CSV)}")
    return 0 if run.done == len(enqueued) else 1


# ── harvest ─────────────────────────────────────────────────────────────────────────────────

def report() -> int:
    if not PROGRESS_CSV.is_file():
        print(f"refusing: {_rel(PROGRESS_CSV)} does not exist.", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(open(PROGRESS_CSV, encoding="utf-8")))
    from collections import Counter
    print(f"{len(rows)} of {EXPECTED_N} folded\n")
    print("1 - VERDICTS:", dict(Counter(r["verdict"].split(" ")[0] for r in rows)))
    zero = [r["accession"] for r in rows if r["served_structure_bytes"] in ("0", "")]
    print("    zero-byte served structures:", zero or "NONE")

    free = [int(r["free_mib_before"]) for r in rows if r["free_mib_before"]]
    if free:
        print(f"\n2 - FREE VRAM at the gate: first {free[0]}, lowest {min(free)}, last {free[-1]} "
              f"MiB over {len(free)} folds")
        print("    ! a downward drift across 346 folds is a finding F-064 would want")

    walls = [float(r["wall_seconds"]) for r in rows if r["wall_seconds"]]
    if walls:
        mean = sum(walls) / len(walls)
        print(f"\n3 - WALL TIME: mean {mean:.1f}s over {len(walls)} folds "
              f"(min {min(walls):.1f}, max {max(walls):.1f})")
        print(f"    the twenty projected 53.2 s for this band -> {mean/53.2:.2f}x")
        print(f"    band total: {mean*EXPECTED_N/3600:.2f} h against the projected 5.12 h")
        print("    ! a material divergence re-scopes the remaining ~2,226 and is a finding about")
        print("      the projector, which exists because an earlier estimate was out by an order")
        print("      of magnitude.")
    print("\n! SLICE 2 IS NOT AUTHORISED. Report the harvest; the owner rules (AMENDMENT 9 section 4.3).")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/task4_slice1.py")
    ap.add_argument("--enumerate", dest="enumerate_", action="store_true",
                    help="count the band, cross-check it, write it to disk. No DB write.")
    ap.add_argument("--enqueue", action="store_true", help="write the 346 Run 2 rows")
    ap.add_argument("--fold", action="store_true", help="fold them, unattended")
    ap.add_argument("--report", action="store_true", help="the harvest")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true")
    args = ap.parse_args(argv)
    if args.enumerate_:
        return enumerate_slice()
    if args.enqueue:
        return enqueue(args.owner)
    if args.fold:
        return fold(args.owner)
    if args.report:
        return report()
    ap.print_help()
    return 2


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
