#!/usr/bin/env python3
"""Task 4 — bounded slice 2: bands **1–30**, n = **525**. Unsupervised, like slice 1.

    python scripts/task4_slice2.py --enumerate                    # reports, writes NOTHING
    python scripts/task4_slice2.py --enqueue --i-am-the-owner     # writes the Run 2 rows
    python scripts/task4_slice2.py --fold --i-am-the-owner        # folds them, unattended
    python scripts/task4_slice2.py --report                       # the harvest, no tunnel needed

⚠⚠ **SLICE 2 ONLY. SLICE 3 REQUIRES A FRESH OWNER RULING — do not chain slices.** Each bounded
slice has been ruled separately (`D-157 amendment 2` records why the pattern matters: three
express exceptions to §4.2 in two days, each defensible, each disclaiming the next).

**⚠ THE MACHINERY IS IMPORTED FROM SLICE 1, NOT COPIED.** `SliceRun` — the stop conditions, the
deferred surface probe, the per-fold progress record — is the part that was debugged in
production across 342 folds, and a second copy is how two campaigns diverge under one name
(`F-046`). This module supplies the band, the projection and the paths; everything else is the
same object.

**⚠⚠ WHAT SLICE 1 LEARNED, AND THIS INHERITS WITHOUT RE-LEARNING IT:**

- **the probe is deferred by one fold** — `run_worker`'s loop is claim → fold → upload → complete,
  so probing inside the fold asks about an artifact that has not been uploaded yet. Slice 1 read
  **0 bytes on three healthy folds** (159–171 KB once they landed) and the fatal streak stopped a
  working campaign;
- ⚠ **`GET`, never `HEAD`** — the route is `@read_router.get` and answers **405** to HEAD;
- ⚠ **the body is measured, not `Content-Length`** — a header is a claim about the bytes;
- ⚠ **an unreachable surface is a named category, never a fold failure**;
- ⚠ **every stop condition is reachable**, including when nothing is succeeding;
- ⚠ **ASCII only in printed strings** — `cp1252` cannot encode `⚠`, and a confirmation line that
  dies takes the report with it while the write has already happened.

⚠ **The fold needs NO TUNNEL.** The worker talks to Fly over HTTPS; `DATABASE_URL` is for
`--enqueue` only. ⚠ **`--report` reads the progress file and needs neither.**
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
from typing import Any, Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.task3_run2_folds import (          # noqa: E402 — REUSE, do not re-derive
    CAP_AA,
    RUN_LABEL,
    _engine,
    _existing_run2,
    _rel,
    cuda_ready,
    make_fold_callable,
    worker_tier,
)
from scripts.task4_slice1 import SliceRun, PROGRESS_COLUMNS   # noqa: E402 — the debugged machinery

#: ⚠⚠ THE HARD BOUND, IN THE TOOL RATHER THAN IN THE INVOCATION.
BAND = (1, 30)
EXPECTED_N = 525
#: The two sub-bands, kept separate because their per-fold costs differ and the projection is
#: reported per band. ⚠ They are NOT separate populations — the slice is one enqueue.
SUB_BANDS = ((1, 10, 130, 16.6), (11, 30, 395, 16.5))
#: ⚠ Measured over slice 1's 342 folds: claim + upload + complete, a PER-FOLD CONSTANT rather
#: than a fraction of fold time (`D-157 amendment 3`). The projector omitted it entirely and was
#: right only by coincidence of two offsetting errors.
TRANSPORT_S = 4.7

assert BAND[1] <= CAP_AA, "the band's ceiling is above the measured-safe envelope"

OUT_DIR = REPO / "data" / "control" / "task4_slice2"
ENUMERATION_JSON = OUT_DIR / "enumeration.json"
ENQUEUED_JSON = OUT_DIR / "enqueued.json"
PROGRESS_CSV = OUT_DIR / "progress.csv"


# ── the population ──────────────────────────────────────────────────────────────────────────

def the_band() -> list[dict[str, Any]]:
    """The 525, enumerated from the manifest. ⚠ Refuses on any count but `EXPECTED_N`.

    ⚠⚠ A slice of 523 is a different population than the one ruled on, and the projection it
    will be compared against was computed over 525. Resolve the disagreement rather than
    override it.
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
            f"refusing: the band {lo}-{hi} enumerates {len(rows)} rows, not {EXPECTED_N}. The "
            f"band definition and D-157's split disagree; resolve that rather than folding a "
            f"different population than the one ruled on.")
    over = [r for r in rows if r["span"] > CAP_AA]
    if over:
        raise SystemExit(f"refusing: {len(over)} rows exceed the {CAP_AA} aa envelope.")
    return sorted(rows, key=lambda r: (r["span"], r["accession"]))


def projection() -> tuple[float, list[str]]:
    """The corrected projection: fold time PLUS the per-fold transport constant, per sub-band."""
    lines, total = [], 0.0
    for lo, hi, n, fold_s in SUB_BANDS:
        secs = (fold_s + TRANSPORT_S) * n
        total += secs
        lines.append(f"  band {lo}-{hi:<3} {n:>4} rows x ({fold_s} + {TRANSPORT_S}) s "
                     f"= {secs/3600:.2f} h")
    return total, lines


def enumerate_slice() -> int:
    """Count it, cross-check it, project it, write it to disk. ⚠ No database, no write to it."""
    rows = the_band()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ENUMERATION_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    from collections import Counter
    spans = [r["span"] for r in rows]
    lo10 = sum(1 for s in spans if s <= 10)
    print(f"band {BAND[0]}-{BAND[1]} inclusive, tranches 1-4: {len(rows)} rows "
          f"(expected {EXPECTED_N})")
    print(f"  sub-bands  : 1-10 {lo10} | 11-30 {len(rows)-lo10}   (expected 130 | 395)")
    print(f"  by tranche : {dict(Counter(r['tranche'] for r in rows))}")
    print(f"  span range : {min(spans)} - {max(spans)}   mean {sum(spans)/len(spans):.1f}")
    print(f"  written to : {_rel(ENUMERATION_JSON)}")

    total, lines = projection()
    print("\ncorrected projection (D-157 amendment 3: transport is a PER-FOLD CONSTANT,")
    print("additive to fold time rather than a fraction of it):")
    for line in lines:
        print(line)
    print(f"  TOTAL {total/3600:.2f} h")
    print("\n! Wall time is flat at ~16.5 s fold-only through ~44 aa - reload dominates, so in")
    print("  this band cost is set by PROCESS COUNT rather than by span length.")
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
        # ⚠⚠ THE BAND OVERLAPS TASK 3's TWENTY, AND THAT IS ARITHMETIC RATHER THAN A DEFECT. The
        # stratified sample drew 4 rows from 1-10 and 4 from 11-30. Re-folding them would give one
        # accession TWO Run 2 rows, breaking the generation partition the campaign rests on.
        # ⚠ The BAND stays 525; what is ENQUEUED is the complement, and the arithmetic is printed.
        already = _existing_run2(s, list(by_acc))
        todo = [p for p in payloads if p["accession"] not in already]
        print(f"\nband {BAND[0]}-{BAND[1]}: {len(payloads)} rows")
        print(f"  already carry a Run {RUN_LABEL} row: {len(already)} -> {sorted(already)}")
        print(f"  to enqueue: {len(todo)}")
        if len(todo) + len(already) != EXPECTED_N:
            print(f"REFUSING: {len(todo)} + {len(already)} != {EXPECTED_N}.", file=sys.stderr)
            return 1
        if not todo:
            print("nothing to enqueue; the band is already covered.")
            return 0
        # ⚠ The owner gate sits AFTER the arithmetic: a count you only see once you have committed
        # is a count the dry run did not check.
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

def fold(owner: bool) -> int:
    if not ENQUEUED_JSON.is_file():
        print(f"refusing: {_rel(ENQUEUED_JSON)} does not exist. Run --enqueue first.",
              file=sys.stderr)
        return 1
    enqueued = {int(e["job_id"]): e for e in json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))}
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
    run = SliceRun(enqueued, base, progress_csv=PROGRESS_CSV)
    print(f"slice 2: band {BAND[0]}-{BAND[1]}, {len(enqueued)} rows, surface {base}")
    if run.done:
        print(f"! RESUMING: {run.done} fold(s) already in {_rel(PROGRESS_CSV)}. The queue holds "
              f"the rest pending, so a restart costs one fold, not {run.done}.")
    print("stop conditions: all folded | 3 consecutive unlanded artifacts | 20 min idle | "
          "10 h wall")

    if not owner:
        print("\nDRY RUN - no fold ran. Re-run with --i-am-the-owner to fold.")
        return 0

    from core.vram_guard import preflight as real_preflight    # noqa: PLC0415
    from worker.main import (build_client, config_from_env,    # noqa: PLC0415
                             process_per_fold_fn)
    from worker.orchestrator import run_worker                 # noqa: PLC0415

    config = config_from_env()
    client = build_client(config)
    inner = make_fold_callable(run.rec, client.persist_pae, process_per_fold_fn(),
                               real_preflight, total=len(enqueued))

    def _fold_one(spec):
        result = inner(spec)
        run.after_fold(spec, result)
        return result

    try:
        run_worker(client, _fold_one, config.worker_id, poll_interval=config.poll_interval,
                   tier=worker_tier(), should_stop=run.should_stop)
    finally:
        # ⚠ The last fold is still held, unprobed. Flush it or the record is short by one.
        if run._held is not None:
            run._probe_and_write(run._held)
            run._held = None
        print(f"\nSTOPPED: {run.stop_reason or 'the loop returned'}")
        print(f"{run.done} of {len(enqueued)} folded; record in {_rel(PROGRESS_CSV)}")
    return 0 if run.done == len(enqueued) else 1


# ── harvest ─────────────────────────────────────────────────────────────────────────────────

def report() -> int:
    """⚠ Reads the progress file only — no tunnel, no database, no network."""
    if not PROGRESS_CSV.is_file():
        print(f"refusing: {_rel(PROGRESS_CSV)} does not exist.", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(open(PROGRESS_CSV, encoding="utf-8")))
    from collections import Counter
    print(f"{len(rows)} folded\n")
    print("1 - VERDICTS:", dict(Counter(r["verdict"].split(" ")[0] for r in rows)))
    zero = [r["accession"] for r in rows if r["served_structure_bytes"] in ("0", "")]
    print("    zero-byte served structures:", zero or "NONE")

    free = [int(r["free_mib_before"]) for r in rows if r["free_mib_before"]]
    if free:
        print(f"\n2 - FREE VRAM at the gate: first {free[0]}, lowest {min(free)}, "
              f"last {free[-1]} MiB over {len(free)} folds "
              f"({'CONSTANT' if len(set(free)) == 1 else 'VARIES'})")

    walls = [float(r["wall_seconds"]) for r in rows if r["wall_seconds"]]
    if walls:
        # ⚠ Per sub-band, because the projection was made per sub-band and a single mean would
        # hide which half it got wrong.
        print(f"\n3 - WALL TIME vs the corrected projection")
        for lo, hi, n, fold_s in SUB_BANDS:
            got = [float(r["wall_seconds"]) for r in rows
                   if r["span_aa"] and lo <= int(r["span_aa"]) <= hi]
            if not got:
                continue
            mean = sum(got) / len(got)
            print(f"    band {lo}-{hi:<3} n={len(got):>4}  fold mean {mean:>5.1f}s "
                  f"(projected {fold_s}s)  -> {mean/fold_s:.2f}x")
        total, _ = projection()
        print(f"    projected total {total/3600:.2f} h over {EXPECTED_N} rows")
        print("    ! elapsed vs projected needs the timestamps; fold time alone omits transport,")
        print("      which is the error D-157 amendment 3 records.")
    print("\n! SLICE 3 IS NOT AUTHORISED. Report the harvest; the owner rules.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/task4_slice2.py")
    ap.add_argument("--enumerate", dest="enumerate_", action="store_true",
                    help="count the band, project it, write it to disk. No DB write.")
    ap.add_argument("--enqueue", action="store_true", help="write the Run 2 rows")
    ap.add_argument("--fold", action="store_true", help="fold them, unattended")
    ap.add_argument("--report", action="store_true", help="the harvest, no tunnel needed")
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
