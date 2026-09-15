#!/usr/bin/env python3
"""Task 4 — bounded slice 4: band **101–250**, n = **600**. Unsupervised, like slices 1–3.

    python scripts/task4_slice4.py --enumerate                    # reports, writes NOTHING
    python scripts/task4_slice4.py --enqueue --i-am-the-owner     # writes the Run 2 rows
    python scripts/task4_slice4.py --preflight --i-am-the-owner   # tunnel-armed, seconds
    python scripts/task4_slice4.py --fold --i-am-the-owner        # folds them, unattended
    python scripts/task4_slice4.py --report                       # the harvest, no tunnel needed

⚠⚠ **SLICE 4 ONLY. SLICE 5 REQUIRES A FRESH OWNER RULING — do not chain slices.**

⚠ **Authorised by the owner, 2026-09-15.** Scope per `D-161`: band 101–250, tranches 1–4, local
tier, Run 2, **600 rows**. ⚠ **Instrument measurement only** — it does not grow the paper
population, does not enter `F-004`, and does not bear on `F-072`.

⚠⚠ **TWO PRECONDITIONS, AND NEITHER IS THIS SCRIPT TO WAIVE.**

1. **`F-078` 37 rows must be settled before this slice folds.** They are slice 2 rows, band 29–30,
   held at `tier = NULL`. If they are restored to `local` while these 600 sit pending, **both
   populations are claimable at once and the per-band transport term is contaminated** — which is
   this campaign entire purpose. Fold them as their own bounded population first, or leave them
   NULL until this slice finishes. ⚠ Either is fine. Doing neither is not.
2. **`D-166` Run-2 identity design.** The enqueue below is a check-then-write standing behind a
   **process-level advisory lock**, inherited from `scripts.task3_run2_folds._existing_run2`.
   ⚠ **A lock is not a constraint** — no UNIQUE index covers the Run-2 identity, because it spans
   `protein_analyses.input_value` and `jobs.inference_settings->>run`. Do not run two enqueues at
   once, and do not read the lock as making that safe.

⚠ **The machinery is imported from slice 1**, not copied — `SliceRun` and the stranger guard both.
A second copy is how two campaigns diverge under one name (`F-046`).

**⚠⚠ THIS SLICE'S TRANSPORT TERM IS UNMEASURED, AND THAT IS DECLARED RATHER THAN ESTIMATED.**

`D-157 amendment 4` retracted the "per-fold constant" framing. **Three bands are now measured:**
**0.7 s/fold** at 1–30, **0.90 s/fold** at 31–100 (slice 3, 1,097 folds, 2026-09-15), and
**4.7 s/fold** at 251–384. ⚠⚠ **Three points licence an interpolation no more than two did** —
and this band sits in the single gap where the measured values jump by a factor of five. Carrying
any of them here would repeat exactly the mistake amendment 4 exists to retract.

> **So the projection below is FOLD-TIME ONLY, stated as a floor**, and this campaign is what
> measures the missing term: `(elapsed − fold_time) / n_folds`, reported per band on completion.

⚠ **Inherited without re-learning** (slices 1 and 2 paid for each of these): the surface probe
deferred by one fold · `GET` never `HEAD` (405) · the body measured, not `Content-Length` · an
unreachable surface as a named category, never a fold failure · every stop condition reachable ·
ASCII-only printed strings · the stranger guard called before the first claim.

⚠⚠ **THE FOLD IS SPLIT INTO TWO SHELLS (`D-160`), AND THE HEADER THAT USED TO SIT HERE WAS FALSE.**
It read *"the fold needs NO TUNNEL; `DATABASE_URL` is for `--enqueue` only"*. That was true when it
was written and stopped being true on 2026-09-13, when **PR #306 added the stranger guard to the
fold path** — `refuse_on_strangers` → `_engine()` → `os.environ["DATABASE_URL"]`, a subscript, so
the fold raised `KeyError` without a tunnel. ⚠ An operator following the old header hit that error
and the nearest fix to hand was `source .env`, **re-arming the shell for ten unattended hours** —
the condition both truncation incidents required. A stale header in a safety-relevant file is worse
than no header.

    --preflight   TUNNEL-ARMED. Seconds. CUDA check, stranger check, writes the clearance.
    --fold        CLEAN SHELL. Hours. Refuses if DATABASE_URL is set, or the clearance is
                  missing, stale (> 1 h), taken at another tier, or covers another population.

⚠ **The fold LOOP genuinely needs no tunnel** — `base = TRANSPORT_URL or https://pharmfoldmdk.fly.dev`,
`config_from_env()` resolves `transport_url` + `auth_token` only, and `run_worker` claims, uploads
and completes over HTTPS. `--report` reads `progress.csv` and touches nothing. ⚠ The fold shell
needs `WORKER_AUTH_TOKEN` exported — **never `source .env`**, which also carries `DATABASE_URL`.
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
    clearance_refusal,
    fold_shell_refusal,
    refuse_on_strangers,
    write_clearance,
)

#: ⚠⚠ THE HARD BOUND, IN THE TOOL RATHER THAN IN THE INVOCATION.
BAND = (101, 250)
EXPECTED_N = 600
#: ⚠⚠ DELIBERATELY ABSENT, unlike slices 1–3, and the absence is the honest answer.
#: Slice 3 measured fold time **20.3 s** over a band whose MEAN SPAN was 47.3 aa. This band mean
#: span is **174.6** — 3.7x longer — and `F-059` records the fold incremental VRAM as O(L²), so
#: fold time does not scale linearly outside the range it was measured in. There is no sample of
#: THIS band to floor against, so no floor is stated.
FOLD_S = None
#: ⚠⚠ DELIBERATELY ABSENT. Three bands measured (0.7 / 0.90 / 4.7 s per fold); this band sits in
#: the gap where they jump by a factor of five. `D-157 amendment 4`. This campaign MEASURES it.
TRANSPORT_S = None

assert BAND[1] <= CAP_AA, "the band's ceiling is above the measured-safe envelope"

OUT_DIR = REPO / "data" / "control" / "task4_slice4"
ENUMERATION_JSON = OUT_DIR / "enumeration.json"
ENQUEUED_JSON = OUT_DIR / "enqueued.json"
PROGRESS_CSV = OUT_DIR / "progress.csv"


# ── the population ──────────────────────────────────────────────────────────────────────────

def the_band() -> list[dict[str, Any]]:
    """The 600, enumerated from the manifest. ⚠ Refuses on any count but `EXPECTED_N`.

    ⚠ `D-161` §3: by tranche this band is **t2 = 216, t3 = 384**, and **no tranche 1 or
    tranche 4 row falls in it** — so a filter that silently dropped one would still
    reconcile to 600 only by luck. The count is asserted, never trusted.
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


def projection(n: int = EXPECTED_N) -> dict[str, Any]:
    """⚠⚠ Returns NO projection for this band, and the refusal is the measurement.

    Slices 1–3 could state a fold-time floor because each had a sample of its own band to floor
    against. **This one does not.** Slice 3 measured 20.3 s at mean span 47.3 aa; this band
    averages 174.6, and `F-059` makes the relationship non-linear. Both terms are unmeasured here,
    so any elapsed number would be an estimate wearing the clothes of a measurement — which is
    `D-157 amendment 4` subject exactly.
    """
    return {
        "n": n,
        "fold_s": FOLD_S,
        "fold_only_h": None if FOLD_S is None else FOLD_S * n / 3600,
        "fold_status": "UNMEASURED for band 101-250. Slice 3 measured 20.3 s at MEAN SPAN 47.3 "
                       "aa; this band mean span is 174.6, and F-059 records incremental VRAM as "
                       "O(L^2), so fold time is not linear outside the measured range.",
        "transport_s": TRANSPORT_S,
        "transport_status": "UNMEASURED for band 101-250; NOT carried from 1-30 (0.7 s), "
                            "31-100 (0.90 s) or 251-384 (4.7 s) - D-157 amendment 4",
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
    print("\nprojection: NONE IS OFFERED FOR THIS BAND, and that is the measurement.")
    print(f"  fold time: {p['fold_status']}")
    print(f"  transport: {p['transport_status']}")
    print("  !! Slices 1-3 each had a sample of their OWN band to floor against. This one does")
    print("     not, so no floor is stated rather than one being borrowed from a shorter band.")
    print("     This campaign measures both terms and reports them per band on completion.")
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
    from core.db_identity import assert_campaign_target   # noqa: PLC0415 - D-159

    written = []
    with Session(_engine()) as s:
        # ⚠⚠ D-159: ASK THE DATABASE WHICH DATABASE IT IS, BEFORE WRITING A SINGLE ROW.
        # The engine came from DATABASE_URL and a tunnel does not say which cluster it reaches.
        # ⚠ A population floor alone cannot do this: the forensic cluster zp2wjrej9lwodn4q holds
        # the same census (the live one was restored from its backup) and would pass every count.
        # Raises WrongDatabase before the first INSERT; one home, every caller (F-046).
        assert_campaign_target(s.connection())
        # ⚠ The band overlaps Task 3's twenty; what is ENQUEUED is the complement. The BAND stays
        # 600 and the arithmetic is printed rather than assumed.
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
    # ⚠⚠ D-160: THIS SHELL MUST NOT BE ARMED, AND THAT IS THE VERY FIRST THING CHECKED. An armed
    # shell is the defect itself, so the operator learns it in the first second rather than after
    # three other refusals have sent them looking somewhere else.
    shell = fold_shell_refusal(os.environ)
    if shell:
        print(shell, file=sys.stderr)
        return 1

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

    # ⚠⚠ The stranger guard's VERDICT, carried from `--preflight`'s armed shell. The check itself
    # needs a database; this run must not have one. `run_worker` claims the next job of its TIER,
    # not "one of mine", so the clearance is bound to the tier AND the exact population AND is
    # refused once stale - a stale clear is not a clear.
    stale = clearance_refusal(OUT_DIR, enqueued, worker_tier())
    if stale:
        print(f"REFUSING: {stale}", file=sys.stderr)
        return 1
    print(f"stranger clearance: fresh, tier={worker_tier()!r}, {len(enqueued)} ids")

    base = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev")
    run = SliceRun(enqueued, base, progress_csv=PROGRESS_CSV)
    print(f"slice 4: band {BAND[0]}-{BAND[1]}, {len(enqueued)} rows, surface {base}")
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


def preflight() -> int:
    """⚠ D-160 step one: the TUNNEL-ARMED half, and it runs in seconds rather than hours.

    Confirms the interpreter, runs the stranger check against the database, and writes the
    clearance the clean-shell `--fold` will demand. ⚠ Close this shell afterwards.
    """
    if not ENQUEUED_JSON.is_file():
        print(f"refusing: {_rel(ENQUEUED_JSON)} does not exist. Run --enqueue first.",
              file=sys.stderr)
        return 1
    enqueued = {int(e["job_id"]): e for e in json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))}

    ok, why = cuda_ready()
    print(f"interpreter check: {why}")
    if not ok:
        print(f"REFUSING: {why}", file=sys.stderr)
        return 1

    tier = worker_tier()
    if refuse_on_strangers(enqueued, tier):
        return 1

    path = write_clearance(OUT_DIR, tier, enqueued)
    print(f"\nclearance written: {_rel(path)}  (valid 1 hour, tier={tier!r}, "
          f"{len(enqueued)} ids)")
    # ! ASCII-only in printed strings, inherited from slices 1 and 2 and asserted by
    # tests/test_task4_slice4.py::test_printed_strings_stay_ascii. The console this runs on is not
    # UTF-8, and a warning that raises UnicodeEncodeError is a warning nobody reads.
    print("\n!! CLOSE THIS SHELL. Fold in a clean one:")
    print("    export WORKER_AUTH_TOKEN=...      # and TRANSPORT_URL if not the default")
    print("    python scripts/task4_slice4.py --fold --i-am-the-owner")
    print("!! Do NOT `source .env` there - it carries DATABASE_URL, and this fold runs for hours.")
    return 0


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
            print(f"    compare: 0.7 at 1-30, 0.90 at 31-100, 4.7 at 251-384 s/fold.")
            print(f"    This is a FOURTH measured point and it lands in the gap where the")
            print(f"    three jump by a factor of five. It confirms none of them.")
    print("\n! SLICE 5 IS NOT AUTHORISED. Report the harvest; the owner rules.")
    owed_restore_notice()
    return 0


#: !! THE OWED RESTORE, PRINTED WHERE THE OPERATOR WILL ACTUALLY BE (F-078 amendment 1).
#: Order B set slice 2 37 lost rows to tier NULL so slice 3 1,097 could be the only claimable
#: population. Slice 3 folded 1097/1097 on 2026-09-15 and THE DEBT IS STILL OPEN.
#: A NULL-tier job is claimable by NOBODY and `refuse_on_strangers` deliberately does not
#: count one - so if the restore is forgotten it is forgotten SILENTLY, and slice 2 stays
#: 480/517 for ever. That is the same shape as everything F-078 records: a loss no check
#: watches. ! So the reminder lives in `--report`, the command run at the moment the fold
#: ends, rather than in a document someone has to remember to open.
#: !! AND IT NOW CARRIES A SECOND WARNING THAT IS SPECIFIC TO THIS SLICE: restoring the 37
#: to tier `local` while these 600 are pending makes BOTH populations claimable at once,
#: which contaminates the per-band transport term this campaign exists to measure. Fold the
#: 37 as their own bounded population first, or leave them NULL until this slice finishes.
#: !! F-078 amendment 2 (2026-09-15): the 37 FOLDS were never lost - only their database rows. The
#: artifacts are on the volume, identity 37/37. A re-fold would overwrite them, so the notice no
#: longer prints restore-and-re-fold steps. The ordering warning survives for the re-fold branch.
OWED_RESTORE = [
    "",
    "=" * 78,
    "!! OWED, AND NOT YET DONE: SLICE 2's 37 (F-078 amendments 1 and 2)",
    "=" * 78,
    "  Jobs 4869-4905 were set tier NULL on 2026-09-15 so slice 3 could be the only claimable",
    "  population. Slice 3 folded 1097/1097 the same day. THE DEBT IS STILL OPEN.",
    "",
    "  The cut, stated from the database because that is the leg that stays verifiable",
    "  (F-078 amendment 1): job 4868 completed 15:24:36.578Z and SURVIVED; job 4869 was",
    "  claimed 64 ms later and its DATABASE ROW did not.",
    "",
    "  !! THEIR FOLDS WERE NOT LOST (F-078 amendment 2). All 37 artifacts are on the volume;",
    "  sizes match progress.csv 37/37 and identity is 37/37 (scripts/f078_identity_check.py).",
    "",
    "  !! DO NOT RE-FOLD THEM, AND DO NOT RUN f078_null_tier_the_37.py --restore.",
    "  A re-fold uploads into the same /data/artifacts/{job_id}/ directories and overwrites",
    "  the verified bytes. The script refuses --restore for exactly that reason.",
    "",
    "  Owed instead: the OWNER rules re-attach (link the existing artifacts to the 37 rows)",
    "  or re-fold. The rows stay tier NULL until that ruling is written.",
    "",
    "  ! A NULL-tier job is claimed by nobody and the stranger guard does not count it, so",
    "  nothing else in this system will ever raise its hand about these rows. This notice IS",
    "  the guard. Do not delete it until slice 2 reads 517/517.",
    "",
    "  !! ORDERING, IF THE RULING IS RE-FOLD: making the 37 claimable while slice 4's 600 are",
    "  pending puts BOTH populations in one claimable pool, which contaminates the per-band",
    "  transport term this campaign exists to measure. Re-attach makes nothing claimable.",
    "=" * 78,
]


def owed_restore_notice() -> None:
    for line in OWED_RESTORE:
        print(line)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/task4_slice4.py")
    ap.add_argument("--enumerate", dest="enumerate_", action="store_true",
                    help="count the band, project it, write it to disk. No DB write.")
    ap.add_argument("--enqueue", action="store_true", help="write the Run 2 rows")
    ap.add_argument("--preflight", action="store_true",
                    help="D-160: tunnel-armed stranger check; writes the clearance. Seconds.")
    ap.add_argument("--fold", action="store_true", help="fold them, unattended. CLEAN shell.")
    ap.add_argument("--report", action="store_true", help="the harvest, no tunnel needed")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true")
    args = ap.parse_args(argv)
    if args.enumerate_:
        return enumerate_slice()
    if args.enqueue:
        return enqueue(args.owner)
    if args.preflight:
        return preflight()
    if args.fold:
        return fold(args.owner)
    if args.report:
        return report()
    ap.print_help()
    return 2


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
