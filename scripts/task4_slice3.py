#!/usr/bin/env python3
"""Task 4 — bounded slice 3: band **31–100**, n = **1,101**. Unsupervised, like slices 1 and 2.

    python scripts/task4_slice3.py --enumerate                    # reports, writes NOTHING
    python scripts/task4_slice3.py --enqueue --i-am-the-owner     # writes the Run 2 rows
    python scripts/task4_slice3.py --fold --i-am-the-owner        # folds them, unattended
    python scripts/task4_slice3.py --report                       # the harvest, no tunnel needed

⚠⚠ **SLICE 3 ONLY. SLICE 4 REQUIRES A FRESH OWNER RULING — do not chain slices.**

⚠ **The machinery is imported from slice 1**, not copied — `SliceRun` and the stranger guard both.
A second copy is how two campaigns diverge under one name (`F-046`).

**⚠⚠ THIS SLICE'S TRANSPORT TERM IS UNMEASURED, AND THAT IS DECLARED RATHER THAN ESTIMATED.**

`D-157 amendment 4` retracted the "per-fold constant" framing: transport measured **4.7 s/fold**
in band 251–384 and **0.7 s/fold** in band 1–30 — a factor of **6.7**. Band 31–100 sits between
them, ⚠⚠ **and two points do not licence an interpolation** — that is amendment 4's whole subject,
and carrying either value here would repeat the mistake the amendment exists to retract.

> **So the projection below is FOLD-TIME ONLY, stated as a floor**, and this campaign is what
> measures the missing term: `(elapsed − fold_time) / n_folds`, reported per band on completion.

⚠ **Inherited without re-learning** (slices 1 and 2 paid for each of these): the surface probe
deferred by one fold · `GET` never `HEAD` (405) · the body measured, not `Content-Length` · an
unreachable surface as a named category, never a fold failure · every stop condition reachable ·
ASCII-only printed strings · the stranger guard called before the first claim.

⚠ **The fold needs NO TUNNEL.** `DATABASE_URL` is for `--enqueue` only; `--report` needs neither.
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
from scripts.task4_slice1 import (   # noqa: E402 — the debugged machinery, shared not copied
    PROGRESS_COLUMNS,
    SliceRun,
    refuse_on_strangers,
)

#: ⚠⚠ THE HARD BOUND, IN THE TOOL RATHER THAN IN THE INVOCATION.
BAND = (31, 100)
EXPECTED_N = 1101
#: Fold time only, from slice 1's own 31–100 sample. ⚠ The flat-through-~44 aa observation makes
#: this a reasonable floor for the band's lower half and a weaker one above it.
FOLD_S = 16.5
#: ⚠⚠ DELIBERATELY ABSENT. Slice 1 measured 4.7 s/fold at 251–384; slice 2 measured 0.7 at 1–30.
#: `D-157 amendment 4` retracts the constant framing, so there is no value to carry here and none
#: is invented. This campaign MEASURES it.
TRANSPORT_S = None

assert BAND[1] <= CAP_AA, "the band's ceiling is above the measured-safe envelope"

OUT_DIR = REPO / "data" / "control" / "task4_slice3"
ENUMERATION_JSON = OUT_DIR / "enumeration.json"
ENQUEUED_JSON = OUT_DIR / "enqueued.json"
PROGRESS_CSV = OUT_DIR / "progress.csv"


# ── the population ──────────────────────────────────────────────────────────────────────────

def the_band() -> list[dict[str, Any]]:
    """The 1,101, enumerated from the manifest. ⚠ Refuses on any count but `EXPECTED_N`."""
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


def projection(n: int = EXPECTED_N) -> dict[str, Any]:
    """Fold-time-only, stated as a FLOOR with the missing term named.

    ⚠⚠ Returns no single figure for elapsed. `D-157 amendment 4`: the transport term is per-band
    and this band's is unmeasured, so an elapsed number here would be an estimate wearing a
    measurement's clothes.
    """
    return {
        "n": n,
        "fold_s": FOLD_S,
        "fold_only_h": FOLD_S * n / 3600,
        "transport_s": TRANSPORT_S,
        "transport_status": "UNMEASURED for band 31-100; NOT carried from 251-384 (4.7 s) or "
                            "1-30 (0.7 s) - D-157 amendment 4",
        "elapsed_h": None,
    }


def enumerate_slice() -> int:
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

    p = projection()
    print(f"\nprojection: FOLD TIME ONLY, {p['fold_s']} s x {p['n']} = "
          f"{p['fold_only_h']:.2f} h  -- A FLOOR, NOT AN ESTIMATE OF ELAPSED")
    print(f"  transport: {p['transport_status']}")
    print("  !! Two measured points do not licence an interpolation. This campaign measures the")
    print("     missing term as (elapsed - fold_time) / n_folds and reports it per band.")
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
        # ⚠ The band overlaps Task 3's twenty; what is ENQUEUED is the complement. The BAND stays
        # 1,101 and the arithmetic is printed rather than assumed.
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

    # ⚠⚠ The stranger guard, before the first claim. `run_worker` claims the next job of its TIER,
    # not "one of mine".
    if refuse_on_strangers(enqueued, worker_tier()):
        return 1

    base = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev")
    run = SliceRun(enqueued, base, progress_csv=PROGRESS_CSV)
    print(f"slice 3: band {BAND[0]}-{BAND[1]}, {len(enqueued)} rows, surface {base}")
    if run.done:
        print(f"! RESUMING: {run.done} fold(s) already in {_rel(PROGRESS_CSV)}.")
    print("stop conditions: all folded | 3 consecutive unlanded artifacts | 20 min idle | "
          "10 h wall")
    p = projection(len(enqueued))
    print(f"projection: {p['fold_only_h']:.2f} h of FOLD TIME - a floor. Transport for this band "
          f"is unmeasured and this run is what measures it.")

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

    b = [int(r["served_structure_bytes"]) for r in rows if r["served_structure_bytes"]]
    if b:
        print(f"\n3 - SERVED ARTIFACTS: {min(b):,} - {max(b):,} bytes")

    walls = [float(r["wall_seconds"]) for r in rows if r["wall_seconds"]]
    if walls:
        import datetime
        ts = [datetime.datetime.fromisoformat(r["at"]) for r in rows if r["at"]]
        fold_only = sum(walls)
        print(f"\n4 - WALL TIME, fold and elapsed reported SEPARATELY so the transport term")
        print(f"    for this band can be derived rather than assumed:")
        print(f"    fold time mean {fold_only/len(walls):>5.1f}s  total {fold_only/3600:.2f} h")
        if len(ts) > 1:
            elapsed = (ts[-1] - ts[0]).total_seconds()
            per_fold = (elapsed - fold_only) / max(1, len(ts) - 1)
            print(f"    elapsed        {elapsed/3600:>5.2f} h  ({ts[0].strftime('%H:%M')} -> "
                  f"{ts[-1].strftime('%H:%M')})")
            print(f"    !! TRANSPORT for band {BAND[0]}-{BAND[1]}: "
                  f"(elapsed - fold_time) / n = {per_fold:.1f} s/fold")
            print(f"    compare: 4.7 s/fold at 251-384, 0.7 s/fold at 1-30. This is a THIRD")
            print(f"    measured point, not a confirmation of either.")
    print("\n! SLICE 4 IS NOT AUTHORISED. Report the harvest; the owner rules.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/task4_slice3.py")
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
