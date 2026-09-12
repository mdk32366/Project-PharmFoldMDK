#!/usr/bin/env python3
"""Task 3 — the 20 Run 2 folds: enqueue them, fold them under the gate, record what the run is FOR.

    python scripts/task3_run2_folds.py --enqueue                  # reports, writes NOTHING
    python scripts/task3_run2_folds.py --enqueue --i-am-the-owner # writes the 20 Run 2 rows
    python scripts/task3_run2_folds.py --fold --i-am-the-owner    # folds them, records per fold
    python scripts/task3_run2_folds.py --report                   # the three answers

⚠⚠ THIS IS `AMENDMENT 5` §4.2's EXPRESS EXCEPTION, AND IT IS TWENTY ROWS. Task 4's 2,691 still
requires (iii); **this must not be cited as precedent for the campaign.** The exception is
contained in this one file so a later reader can bound it by reading one thing.

⚠ **Owner at the keyboard**, as with `scripts/backfill_run_label.py`. Every mode reports by
default and writes only under `--i-am-the-owner`.

**THE THREE THINGS THE RUN EXISTS TO ANSWER**, and each is answered by the instrument that can
actually see it rather than by the most convenient one:

1. **Does free VRAM recover across folds under `D-105`'s topology?** ⚠⚠ Read from the GATE's own
   `Preflight.free_mib` — the number the gate already takes immediately before each fold — and
   **never re-read afterwards in the parent.** A second reading at a different instant is a
   different measurement (`F-061`'s shape), and the whole question is *what the next preflight
   sees*. `F-064` measured 7,043 → 1,649 MiB with a persistent child; if the series does not
   climb back, the topology did not deliver the property it was landed for.
2. **The band-weighted projection, with the naive figure beside it.** This script writes the CSV
   and `scripts/task3_timing_sample.py --project` computes it. ⚠ **One projector, not two.**
3. **`Q8WXF7`'s outcome at L = 1.** Answered by `core.fold_persistence_check`'s four named
   outcomes against the DB **after** the fold, because the question is whether PAE *landed*, not
   whether it was produced — `column_null` and `file_missing` are different answers from
   `no_pae_emitted` and only one of the three is the owner's pre-registered `leave it`.

⚠⚠ **THE MEMBERSHIP GUARD IS NOT CEREMONY.** `run_worker` claims the next job **of its tier**,
not "one of mine". If any pending local job is outside the 20, this refuses to start rather than
folding a stranger into a 20-row exception.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
import time
from typing import Any, NamedTuple, Optional

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

#: `AMENDMENT 5` §4.2 — twenty rows, no others. A different number here is a different ruling.
SAMPLE_N = 20
#: ⚠ `F-063` reached `highest_ok = 384` and the host BUGCHECKED before 392 was written. `F-064`
#: is the post-fold headroom collapse. Both OPEN. This is a hard stop, not a preference.
CAP_AA = 384
#: The generation this campaign writes. `run: 1` is every existing census row (3,656 of 3,656).
RUN_LABEL = 2

def _rel(path: pathlib.Path) -> str:
    """Repo-relative when it can be, absolute otherwise.

    ⚠⚠ `Path.relative_to` RAISES on a path outside the repo, and every call here is inside a
    message - two of them inside REFUSALS. A refusal that raises while explaining itself reports
    nothing at all, which is worse than the condition it was refusing.
    """
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


OUT_DIR = REPO / "data" / "control" / "task3_run2"
FOLDS_CSV = OUT_DIR / "folds.csv"
ENQUEUED_JSON = OUT_DIR / "enqueued.json"

#: ⚠ The projector reads `span_aa` and `wall_seconds` by NAME. They are first here so a reader
#: can see that this file feeds that one, and `test_the_csv_this_writes_is_what_the_projector_reads`
#: pins it behaviourally rather than by comment.
FOLD_COLUMNS = [
    "fold_index", "accession", "job_id", "span_aa", "wall_seconds",
    "free_mib_before", "requirement_mib", "peak_vram_mib",
    "child_wall_s", "parent_wall_s", "emitted_pae",
]


# ── the population ──────────────────────────────────────────────────────────────────────────

def the_twenty() -> list[dict[str, Any]]:
    """The 20, from the ONE selector, never re-derived here.

    ⚠ `scripts/task3_timing_sample.select()` is seed-pinned (20260911), so the population is
    **enumerable and reproducible** rather than described — which is what §4.2 asks for when it
    says a later reader must be able to find exactly these rows.
    """
    from scripts.task3_timing_sample import select      # noqa: PLC0415 — reuse, do not re-derive

    rows = select()
    if len(rows) != SAMPLE_N:
        raise SystemExit(f"refusing: the selector returned {len(rows)} rows, not {SAMPLE_N}. "
                         f"§4.2's exception is {SAMPLE_N} rows and this is a different population.")
    over = [r for r in rows if r["span"] > CAP_AA]
    if over:
        raise SystemExit(
            "refusing: %d of the selection exceed the %d aa cap (%s). F-063 bugchecked this host "
            "before 392 and F-064 is open; no fold above the cap runs on this card."
            % (len(over), CAP_AA, ", ".join("%s(%daa)" % (r["accession"], r["span"]) for r in over)))
    return rows


def _manifest_rows_for(accessions: set[str]) -> dict[str, dict[str, str]]:
    """The manifest rows behind the 20, keyed by accession, across tranches 1-4."""
    from scripts.census_ingest import MANIFEST          # noqa: PLC0415

    found: dict[str, dict[str, str]] = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("census_accession") in accessions:
                found[r["census_accession"]] = r
    missing = accessions - set(found)
    if missing:
        raise SystemExit(f"refusing: {len(missing)} of the selection are not in the manifest: "
                         f"{sorted(missing)}")
    return found


def run2_payloads() -> list[dict[str, Any]]:
    """Build the 20 payloads and **validate each against the consumer before any write.**

    ⚠⚠ `assert_claimable` is reused rather than re-derived. The first tranche-1 ingest wrote ten
    rows whose `inference_settings` lacked `model_revision`; the dry run passed because it never
    called the contract it was writing for, and `/claim` then stranded all ten with `attempts=0`.
    **A dry run that does not exercise the consumer is not a dry run.**
    """
    from scripts.census_ingest import assert_claimable, build_row   # noqa: PLC0415

    sample = {r["accession"]: r for r in the_twenty()}
    rows = _manifest_rows_for(set(sample))
    payloads = []
    for acc, sel in sorted(sample.items(), key=lambda kv: kv[1]["span"]):
        p = build_row(rows[acc])
        assert_claimable(p)                     # ⚠ raises HERE, before any row is written
        fold_len = p["meta"]["fold_length"]
        if fold_len != sel["span"]:
            raise SystemExit(
                f"refusing: {acc} folds {fold_len} aa but the selector banded it at {sel['span']}. "
                f"The projection's band weights would be computed on a length nothing folded.")
        payloads.append(p)
    return payloads


# ── enqueue ─────────────────────────────────────────────────────────────────────────────────

def _engine():
    from sqlalchemy import create_engine                 # noqa: PLC0415
    from db.dburl import normalize_db_url                # noqa: PLC0415

    # ⚠⚠ `normalize_db_url` is NOT optional. A hand-rolled replace here resolved to psycopg2 —
    # which D-012 does not install — and worked locally while failing on Fly.
    return create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)


def _existing_run2(session, accessions: list[str]) -> dict[str, int]:
    """Accessions that already carry a Run 2 job, so a second pass writes nothing twice.

    ⚠ Filtered in PYTHON, not SQL. `inference_settings` is JSON on SQLite and JSONB on Postgres,
    and a JSON-path predicate is not the same predicate on both engines (`F-056`).
    """
    from sqlalchemy import select                        # noqa: PLC0415
    from db.models import JobRecord, ProteinAnalysis     # noqa: PLC0415

    hits: dict[str, int] = {}
    rows = session.execute(
        select(ProteinAnalysis.id, ProteinAnalysis.input_value, JobRecord.inference_settings)
        .join(JobRecord, JobRecord.analysis_id == ProteinAnalysis.id)
        .where(ProteinAnalysis.input_value.in_(accessions))).all()
    for analysis_id, acc, settings in rows:
        if isinstance(settings, dict) and settings.get("run") == RUN_LABEL:
            hits[acc] = analysis_id
    return hits


def enqueue(owner: bool) -> int:
    payloads = run2_payloads()
    accs = [p["accession"] for p in payloads]

    print(f"the {len(payloads)} Run {RUN_LABEL} rows this would write "
          f"(cap {CAP_AA} aa, selector seed-pinned):")
    print(f"{'accession':<12}{'span':>6}{'tranche':>9}{'tier':>8}")
    for p in payloads:
        print(f"{p['accession']:<12}{p['meta']['fold_length']:>6}"
              f"{p['meta']['cohort_tranche']:>9}{p['meta']['tier']:>8}")

    if not owner:
        print("\nDRY RUN - nothing was written. Re-run with --i-am-the-owner to write.")
        return 0

    from sqlalchemy.orm import Session                   # noqa: PLC0415
    from db.models import JobRecord, ProteinAnalysis     # noqa: PLC0415

    written = []
    with Session(_engine()) as s:
        already = _existing_run2(s, accs)
        if already:
            print(f"\nREFUSING: {len(already)} of the {SAMPLE_N} already carry a Run {RUN_LABEL} "
                  f"job: {sorted(already)}", file=sys.stderr)
            print("A second write would make the campaign's own population ambiguous.",
                  file=sys.stderr)
            return 1
        for p in payloads:
            analysis = ProteinAnalysis(
                input_type="uniprot",
                input_value=p["accession"],
                structure_source="esmfold_local",
                # ⚠⚠ NULL, and it is the structural bar on scoring: fit_scorer selects BY run id.
                ranking_run_id=None,
                cohort_tranche=p["meta"]["cohort_tranche"],
                meta=p["meta"],
            )
            s.add(analysis)
            s.flush()
            # ⚠⚠ `run: 2` IS THE WHOLE POINT AND OMITTING IT IS WORSE THAN NOT WRITING THE ROW.
            # A row with no label is NOT Run 1 and is NOT Run 2 — it is invisible to
            # `app.reads.keep_run_1` and indistinguishable from the generation it exists to be
            # compared against. `F-018`: the label is POSITIVELY DECLARED, never inferred.
            job = JobRecord(analysis_id=analysis.id, status="pending", tier=p["meta"]["tier"],
                            inference_settings={**p["inference_settings"],
                                                "model_id": "facebook/esmfold_v1",
                                                "run": RUN_LABEL})
            s.add(job)
            s.flush()
            written.append({"accession": p["accession"], "analysis_id": analysis.id,
                            "job_id": job.id, "span_aa": p["meta"]["fold_length"]})
        s.commit()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ENQUEUED_JSON.write_text(json.dumps(written, indent=2), encoding="utf-8")
    print(f"\nWROTE {len(written)} Run {RUN_LABEL} rows. ! The ids, so the population is "
          f"ENUMERABLE rather than described:")
    for w in written:
        print(f"  {w['accession']:<12} analysis_id={w['analysis_id']:<8} job_id={w['job_id']:<8} "
              f"span={w['span_aa']}")
    print(f"\nalso written to {_rel(ENQUEUED_JSON)}")
    return 0


# ── fold ────────────────────────────────────────────────────────────────────────────────────

class FoldRecorder:
    """Records what the run is for, paired to the job rather than inferred from it.

    ⚠ The gate's `Preflight` is captured through the `preflight_fn` seam so `free_mib` is the
    number **the gate itself took**, at the gate's instant. Pairing is by call order, checked
    against the length — a mismatch raises rather than recording a plausible wrong number
    (`F-024`: a non-unique match taking the wrong occurrence).
    """

    def __init__(self, allowed: dict[int, str]) -> None:
        self.allowed = allowed                  # job_id -> accession, the 20 and no others
        self.rows: list[dict[str, Any]] = []
        #: ⚠ Every job this run TOOK, whether it folded, refused or failed. The stop condition
        #: counts this and never `len(self.rows)` — see the note at `should_stop`.
        self.attempts = 0
        self._last_pf: Any = None

    def attempted(self, job_id: int) -> None:
        """Called for every claimed job, BEFORE the outcome is known."""
        self.attempts += 1

    def preflight(self, real):
        def _pf(length, dtype, chunk_size, **kw):
            pf = real(length, dtype, chunk_size, **kw)
            self._last_pf = pf
            return pf
        return _pf

    def record(self, spec, result, wall_s: float) -> None:
        if spec.job_id not in self.allowed:
            raise SystemExit(
                f"refusing: job {spec.job_id} is not one of the {SAMPLE_N}. §4.2's exception is "
                f"twenty rows and this run just claimed a stranger.")
        pf = self._last_pf
        if pf is not None and pf.length != len(spec.sequence):
            raise SystemExit(
                f"refusing: the gate's preflight was taken at length {pf.length} and this fold is "
                f"{len(spec.sequence)}. The pairing assumption is broken and every free_mib "
                f"recorded after this point would be attached to the wrong fold.")
        rec = getattr(result, "fold_record", None) or {}
        self.rows.append({
            "fold_index": len(self.rows) + 1,
            "accession": self.allowed[spec.job_id],
            "job_id": spec.job_id,
            "span_aa": len(spec.sequence),
            "wall_seconds": round(wall_s, 2),
            "free_mib_before": getattr(pf, "free_mib", None),
            "requirement_mib": getattr(pf, "required_mib", None),
            "peak_vram_mib": rec.get("peak_vram"),
            "child_wall_s": rec.get("child_wall_s") or rec.get("wall_s"),
            "parent_wall_s": rec.get("parent_wall_s"),
            # ⚠ What the FOLD produced. Whether it LANDED is a different question and is asked of
            # the database in --report, because a produced-but-unpersisted PAE is exactly the
            # two-gate defect Task 2 repaired.
            "emitted_pae": getattr(result, "pae", None) is not None,
        })

    def write(self) -> pathlib.Path:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(FOLDS_CSV, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FOLD_COLUMNS)
            w.writeheader()
            w.writerows(self.rows)
        return FOLDS_CSV


def make_fold_callable(rec: "FoldRecorder", pae_post_fn, fold_fn, preflight_fn):
    """The fold callable `run_worker` drives — ⚠ ASSEMBLED FROM `worker.main`'s PARTS, NOT REBUILT.

    ⚠⚠ THIS IS THE ONE PLACE THIS SCRIPT COULD DIVERGE FROM PRODUCTION, so it is extracted and
    pinned. `worker.main.run()` builds the same call and cannot be used directly here because the
    recorder needs the SPEC — `run()`'s lambda closes over it and never hands it out, and pairing
    a fold to a job by length would be `F-024` (two of the twenty are both 38 aa).

    ⚠ `F-046` — divergent parameters under one name — is the risk, and
    `test_this_script_gates_exactly_as_the_production_worker_does` is the assertion, driven
    behaviourally against both rather than by comparing source text.
    """
    def _fold_one(spec):
        rec.attempted(spec.job_id)
        t0 = time.time()
        result = fold_from_spec_ref()(spec, fold_fn,
                                      pae_post_fn=pae_post_fn,
                                      preflight_fn=rec.preflight(preflight_fn))
        rec.record(spec, result, time.time() - t0)
        r = rec.rows[-1]
        print(f"[{r['fold_index']:>2}/{SAMPLE_N}] {r['accession']:<12} {r['span_aa']:>4} aa  "
              f"wall={r['wall_seconds']:>7.2f}s  free_before={r['free_mib_before']} MiB  "
              f"peak={r['peak_vram_mib']} MiB  pae={'yes' if r['emitted_pae'] else 'NO'}",
              flush=True)
        return result
    return _fold_one


def fold_from_spec_ref():
    """Indirection so the seam is importable without pulling `worker.main` at module import."""
    from worker.main import fold_from_spec                # noqa: PLC0415
    return fold_from_spec


def cuda_ready() -> tuple[bool, str]:
    """Can THIS interpreter fold? ⚠⚠ CHECKED BEFORE THE FIRST CLAIM, NOT DISCOVERED ON IT.

    ⚠ Learned by spending twenty of them. The run was started under the interpreter on `PATH`,
    which carries **`torch 2.13.0+cpu`**: `torch.cuda.is_available()` is False, so `preflight`
    could not read free VRAM, every fold was correctly REFUSED as `refused_no_measurement` — and
    `run_worker` reported each refusal as a deterministic failure, marking all twenty `failed`
    without a single fold being attempted. The GPU was idle at 7,899 MiB free throughout.

    ⚠⚠ **The gate behaved exactly as designed; the campaign was started in a process that could
    never satisfy it.** This is the precondition that was checkable before anything was spent and
    was not checked — the class this repository keeps recording, one layer out from the fold.
    """
    try:
        import torch                                    # noqa: PLC0415
    except Exception as exc:                            # pragma: no cover - environment
        return False, f"torch does not import here ({exc})"
    if not torch.cuda.is_available():
        return False, (f"torch {torch.__version__} in {sys.executable} reports "
                       f"cuda.is_available() = False. A CPU build cannot fold and cannot read "
                       f"free VRAM, so every preflight would refuse with refused_no_measurement "
                       f"and every job would be marked failed without a fold being attempted.")
    return True, f"torch {torch.__version__}, cuda available"


def worker_tier() -> str:
    """The ONE source for the tier, read once and used by both the guard and the run.

    ⚠ `F-046` — divergent parameters under one name. A guard that checks `local` while the run
    claims `rental` is protecting a queue that will not be drained.
    """
    return os.environ.get("WORKER_TIER", "local")


def _claimable_pending(session, tier: str) -> dict[int, str]:
    """The jobs this run could actually claim — ⚠⚠ THE SAME PREDICATE THE CLAIM USES, NOT A
    WIDER ONE.

    `core/queue.py`'s claim filters `status = 'pending' AND tier = :tier` in the SQL, and says in
    its own comment why the tier match is strict: *"A NULL-tier job is claimed by NOBODY,
    deliberately: three-valued logic makes `NULL = 'local'` unknown, hence false. `OR tier IS
    NULL` would have been the friendly-looking version and would have restored the exact hole."*

    ⚠⚠ **So a NULL-tier pending job is not a stranger — it is unclaimable, and refusing to start
    because one exists refuses on a job that could never have been folded.** The same reasoning
    covers any other tier: a pending `rental` job is exactly as unreachable from a local worker.
    ⚠ **This filters on the tier rather than only on NULL for that reason** — excluding NULL
    alone would fix the symptom and leave the class one step along.

    ⚠ The guard must ask the question the CLAIM asks, or it is guarding a different queue than
    the one that will be drained. It is deliberately no wider: anything this run CAN claim is
    still checked, which is the whole protection.
    """
    from sqlalchemy import select                        # noqa: PLC0415
    from db.models import JobRecord, ProteinAnalysis     # noqa: PLC0415

    rows = session.execute(
        select(JobRecord.id, ProteinAnalysis.input_value)
        .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
        .where(JobRecord.status == "pending")
        .where(JobRecord.tier == tier)).all()      # ⚠ strict, like the claim. Never `OR IS NULL`.
    return {jid: acc for jid, acc in rows}


def fold(owner: bool) -> int:
    if not ENQUEUED_JSON.is_file():
        print(f"refusing: {_rel(ENQUEUED_JSON)} does not exist. Run --enqueue first; "
              f"the job ids it records are what bounds this run to twenty.", file=sys.stderr)
        return 1
    enqueued = json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))
    allowed = {int(e["job_id"]): e["accession"] for e in enqueued}
    if len(allowed) != SAMPLE_N:
        print(f"refusing: {len(allowed)} enqueued ids, not {SAMPLE_N}.", file=sys.stderr)
        return 1

    from sqlalchemy.orm import Session                   # noqa: PLC0415

    tier = worker_tier()
    with Session(_engine()) as s:
        pending = _claimable_pending(s, tier)
    strangers = {jid: acc for jid, acc in pending.items() if jid not in allowed}
    if strangers:
        print(f"REFUSING: {len(strangers)} CLAIMABLE pending job(s) are outside the twenty "
              f"({sorted(strangers.items())[:5]}). `run_worker` claims the next job of its TIER, "
              f"not 'one of mine' - starting now could fold a stranger into a 20-row exception.",
              file=sys.stderr)
        return 1
    print(f"queue check: {len(pending)} claimable pending job(s) at tier={tier!r}, "
          f"all inside the twenty.")
    print("  (a NULL-tier or other-tier pending job is NOT counted here - the claim's own "
          "predicate is strict, so nothing else is reachable from this run.)")

    ok, why = cuda_ready()
    print(f"interpreter check: {why}")
    if not ok:
        print(f"REFUSING: {why}", file=sys.stderr)
        print("Run this under the CUDA interpreter (.venv/Scripts/python.exe on this host).",
              file=sys.stderr)
        return 1

    if not owner:
        print("\nDRY RUN - no fold ran. Re-run with --i-am-the-owner to fold.")
        return 0

    from core.vram_guard import preflight as real_preflight     # noqa: PLC0415
    from worker.main import (build_client, config_from_env,     # noqa: PLC0415
                             process_per_fold_fn)
    from worker.orchestrator import run_worker                  # noqa: PLC0415

    rec = FoldRecorder(allowed)
    config = config_from_env()
    client = build_client(config)
    _fold_one = make_fold_callable(rec, client.persist_pae, process_per_fold_fn(), real_preflight)

    try:
        run_worker(client, _fold_one, config.worker_id,
                   poll_interval=config.poll_interval,
                   tier=tier,
                   # ⚠⚠ ATTEMPTS, NOT RECORDINGS. `rec.rows` only grows on a fold that
                   # RETURNED; a refused fold records nothing, so counting rows meant a run in
                   # which everything refused could never reach its own stop condition. It
                   # didn't: twenty refusals left the loop polling an empty queue until it was
                   # killed by hand. A stop condition unreachable in the failure case is not a
                   # stop condition.
                   should_stop=lambda: rec.attempts >= SAMPLE_N)
    finally:
        # ⚠ Written even on a mid-run stop. A campaign that dies at fold 11 and records nothing
        # has cost eleven folds and bought nothing.
        path = rec.write()
        print(f"\nrecorded {len(rec.rows)} fold(s) to {_rel(path)}")
    return 0


class QueueRow(NamedTuple):
    """One job joined to its analysis. ⚠ `pdb_path` is on `protein_analyses`, not on `jobs`."""

    id: int
    status: str
    analysis_id: int
    pdb_path: Optional[str]


#: The statuses a requeue has always reset. ⚠ `complete` is deliberately absent: requeue must
#: never destroy a good fold.
REQUEUABLE_STATUSES = ("failed", "claimed", "pending")


def requeue_candidates(jobs, *, artifact_is_empty):
    """Which of these jobs should go back to `pending`.

    ``jobs`` are `QueueRow`s — ⚠⚠ **a JOIN, because `pdb_path` is on `protein_analyses` and
    `jobs` does not have the column at all.** Passing `JobRecord`s here made
    `getattr(j, "pdb_path", None)` `None` on every row, so nothing was probed and nothing was
    selected; `§3.2`'s report-before-write is what caught it, expecting eleven and printing zero.
    ⚠ And the test fixture had *invented* the attribute — **the fixture-replacing-its-subject
    pattern from this morning's method note, committed hours after writing it.**
    ``artifact_is_empty`` is a predicate on the analysis id, **injected so the caller decides
    where emptiness is established** — the same shape `check_fold_persistence` uses for `exists`,
    and for the same reason: the artifact lives on the Fly volume, so a local `os.path` check
    would misreport every row.

    **Two populations, and the second is why this function exists.**

    1. Anything **not** `complete` — `failed`, `claimed`, `pending`. ⚠ Unchanged behaviour: this
       EXTENDS the predicate, it does not replace it.
    2. ⚠⚠ **`complete` WITH a `pdb_path` WHOSE SERVED ARTIFACT IS EMPTY.** Eleven rows reached
       that state when the child returned no fold: `run_worker` uploaded
       `FoldResult(pdb="", …)`, marked the job complete, and the serving surface now answers
       `200` with **zero bytes**. **Finished work that finished nothing.**

    ⚠ **Skipping `complete` is right in general and wrong here**, which is why the emptiness is
    established rather than assumed: a `complete` row with real bytes is a good fold and requeuing
    it would destroy one.

    ⚠ **Not by id range and not by `run == 2`.** A hardcoded `3698..3708` is a one-off that is
    wrong the next time, and `run == 2` will match rows that folded correctly as soon as any do.
    ⚠ **A `complete` row with NO `pdb_path` is a different condition** — it is neither selected
    nor probed here, because a probe for an artifact that was never claimed asks the surface a
    question about nothing.
    """
    out = []
    for j in jobs:
        if j.status != "complete":
            out.append(j)
        elif getattr(j, "pdb_path", None) and artifact_is_empty(j.analysis_id):
            out.append(j)
    return out


def requeue(owner: bool) -> int:
    """Put the twenty back to `pending` after a run that failed them without folding.

    ⚠⚠ BY JOB ID, NEVER BY ACCESSION. `core.enqueue.requeue_jobs` keys on the accession, and
    every one of these twenty has TWO jobs — the Run 1 original and this campaign's Run 2 row.
    Requeuing by accession would reach a Run 1 job as well if it were ever non-complete, which is
    `F-024` exactly: a non-unique match taking a row nobody asked for. These ids are held in
    `enqueued.json` and nothing else is touched.
    """
    if not ENQUEUED_JSON.is_file():
        print(f"refusing: {_rel(ENQUEUED_JSON)} does not exist.", file=sys.stderr)
        return 1
    enqueued = {int(e["job_id"]): e for e in json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))}

    from sqlalchemy import select                        # noqa: PLC0415
    from sqlalchemy.orm import Session                   # noqa: PLC0415

    from db.models import JobRecord                      # noqa: PLC0415

    from db.models import ProteinAnalysis                # noqa: PLC0415

    with Session(_engine()) as s:
        # ⚠ JOINED: `pdb_path` lives on `protein_analyses`. `jobs` has no such column, so a
        # job-only query cannot answer the question this predicate asks.
        joined = s.execute(
            select(JobRecord, ProteinAnalysis.pdb_path)
            .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
            .where(JobRecord.id.in_(list(enqueued)))).all()
        if len(joined) != len(enqueued):
            print(f"refusing: found {len(joined)} of {len(enqueued)} job rows.", file=sys.stderr)
            return 1
        jobs = [j for j, _p in joined]
        rows = [QueueRow(id=j.id, status=j.status, analysis_id=j.analysis_id, pdb_path=p)
                for j, p in joined]
        by_id = {j.id: j for j in jobs}
        base = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev")
        is_empty = _served_structure_is_empty(base)
        print(f"establishing artifact emptiness against the SERVING SURFACE at {base} "
              f"(never this filesystem)")
        todo = requeue_candidates(rows, artifact_is_empty=is_empty)
        todo_ids = {r.id for r in todo}
        left = [r for r in rows if r.id not in todo_ids]
        print(f"\n{len(todo)} job(s) to requeue; {len(left)} left alone.")
        for j in sorted(todo, key=lambda j: j.id):
            why = ("complete, served artifact is ZERO BYTES" if j.status == "complete"
                   else j.status)
            print(f"  job {j.id} ({enqueued[j.id]['accession']}): {why} -> pending")
        for j in sorted(left, key=lambda j: j.id):
            print(f"  job {j.id} ({enqueued[j.id]['accession']}): {j.status}, left alone")
        if not owner:
            print("\nDRY RUN - nothing was written. Re-run with --i-am-the-owner.")
            return 0
        for r in todo:
            j = by_id[r.id]
            j.status = "pending"
            j.error = None
            j.worker_id = None
            j.claimed_at = None
            j.attempts = 0          # a deliberate operator retry gets a full budget (D-044)
        s.commit()
    print(f"\nrequeued {len(todo)} job(s).")
    return 0


# ── report ──────────────────────────────────────────────────────────────────────────────────

def vram_recovery(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Does free VRAM come back between folds? ⚠ Reported as a SERIES, never as a single verdict.

    `F-064` measured 7,043 → 1,649 MiB with a persistent child — a collapse that recovered only
    on process exit. If `D-105`'s topology delivers, every fold's gate should see roughly the
    first fold's free. **A falling series means the topology did not deliver the property it was
    landed for, and the gate will start refusing mid-campaign.**
    """
    seen = [r for r in rows if r.get("free_mib_before") not in (None, "")]
    if not seen:
        return {"verdict": "unmeasured", "detail": "no gate reading was recorded"}
    vals = [int(r["free_mib_before"]) for r in seen]
    first, lowest = vals[0], min(vals)
    return {
        "verdict": "recovers" if lowest >= first * 0.9 else "DOES NOT RECOVER",
        "first": first, "lowest": lowest, "last": vals[-1], "n": len(vals),
        "series": vals,
        "detail": ("every gate saw at least 90% of the first fold's free VRAM"
                   if lowest >= first * 0.9 else
                   f"free fell to {lowest} MiB against {first} at the first gate - F-064's shape, "
                   f"and the gate will refuse before the campaign ends"),
    }


def report() -> int:
    if not FOLDS_CSV.is_file():
        print(f"refusing: {_rel(FOLDS_CSV)} does not exist. Nothing has been folded.",
              file=sys.stderr)
        return 1
    rows = list(csv.DictReader(open(FOLDS_CSV, encoding="utf-8")))
    print(f"{len(rows)} fold(s) recorded of {SAMPLE_N}\n")

    print("1 - FREE VRAM ACROSS FOLDS (read from the gate, never re-read after)")
    v = vram_recovery(rows)
    print(f"    verdict: {v['verdict']} - {v['detail']}")
    if "series" in v:
        print(f"    series (MiB, in fold order): {v['series']}")
    print()

    print("2 - BAND-WEIGHTED PROJECTION")
    print(f"    python scripts/task3_timing_sample.py --project "
          f"{_rel(FOLDS_CSV)}")
    print("    ! ONE projector. This script does not compute a second one.\n")

    print("3 - PAE AT L = 1, AND THE PRE-REGISTERED RULE")
    tiny = [r for r in rows if int(r["span_aa"]) == 1]
    if not tiny:
        print("    no 1-residue fold is recorded yet.")
    for r in tiny:
        emitted = str(r["emitted_pae"]).lower() == "true"
        print(f"    {r['accession']}: the fold {'EMITTED' if emitted else 'emitted NO'} PAE.")
        print("    ! That is what the fold produced. Whether it LANDED is the four-outcome check")
        print("      below, against the database - a produced-but-unpersisted PAE is the two-gate")
        print("      defect Task 2 repaired, and it reads as success from here.")
    print()
    print("    the four named outcomes need the DB and the owner's proxy:")
    print("      python scripts/task3_run2_folds.py --persistence --i-am-the-owner")
    return 0


def _head_served(base_url: str, artifact: str, analysis_id: int):
    """Fetch one served artifact and measure it. Returns ``(found, n_bytes)``.
    ⚠ ONE probe, two questions.

    ⚠⚠ **GET, NOT HEAD, AND THAT IS MEASURED RATHER THAN ASSUMED.** `HEAD
    /api/analyses/{id}/structure` answers **`405 Method Not Allowed`, `allow: GET`** — the route
    is declared `@read_router.get`. A HEAD-based probe therefore learns nothing about any row,
    and the first version of this refused all twenty on the 405.

    ⚠⚠ IT MUST ASK THE SERVING SURFACE, NOT THIS LAPTOP. The artifacts live on the Fly volume, so
    an `os.path` check here would misreport every row — `check_fold_persistence`'s default of
    `os.path.isfile` is right for a local campaign and catastrophically wrong for this one.
    ⚠ Asking the surface is also the stronger question: a file the volume holds but the surface
    will not serve is not persisted in any sense a reader can use.

    ⚠ **A 5xx or an unreachable host RAISES.** Returning "missing" or "empty" for an outage would
    turn a bad minute into a fabricated verdict on twenty rows.
    """
    import urllib.error          # noqa: PLC0415
    import urllib.request        # noqa: PLC0415

    url = f"{base_url.rstrip('/')}/api/analyses/{analysis_id}/{artifact}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            if not 200 <= r.status < 300:
                return False, 0
            # ⚠ The BODY is read and measured rather than trusting `Content-Length`. The bytes
            # that reach a reader are the thing in question, and a header is a claim about them.
            return True, len(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, 0
        raise SystemExit(f"refusing: {url} returned {e.code}; that is not an answer about the "
                         f"artifact.")
    except urllib.error.URLError as e:
        raise SystemExit(f"refusing: cannot reach {url} ({e.reason}). An unreachable surface is "
                         f"an absent measurement, not a missing file.")


def _served_pae_exists(base_url: str):
    """Does the PAE resolve on the serving surface? (`check_fold_persistence`'s `exists`.)"""
    def _exists(analysis_id: int) -> bool:
        found, _n = _head_served(base_url, "pae", analysis_id)
        return found
    return _exists


def _served_structure_is_empty(base_url: str):
    """⚠⚠ Is the served STRUCTURE zero bytes? The eleven answer `200` with nothing behind it.

    ⚠ `200` + zero bytes is the worst shape an absence can take — it reads as success at every
    layer above it, which is exactly how eleven rows came to look like finished work.
    ⚠ A **404** is NOT empty-in-this-sense: no artifact was served at all, which is a different
    condition and is not what this predicate selects on.
    """
    def _is_empty(analysis_id: int) -> bool:
        found, n = _head_served(base_url, "structure", analysis_id)
        return bool(found) and n == 0
    return _is_empty


def persistence(owner: bool) -> int:
    """The four named outcomes per fold, asked of the database rather than of the fold."""
    if not (ENQUEUED_JSON.is_file() and FOLDS_CSV.is_file()):
        print("refusing: --enqueue and --fold must both have run.", file=sys.stderr)
        return 1
    if not owner:
        print("DRY RUN - this reads production. Re-run with --i-am-the-owner.")
        return 0

    from sqlalchemy import select                                    # noqa: PLC0415
    from sqlalchemy.orm import Session                               # noqa: PLC0415

    from core.fold_persistence_check import check_fold_persistence, summarise  # noqa: PLC0415
    from db.models import ProteinAnalysis                            # noqa: PLC0415

    emitted = {int(r["job_id"]): str(r["emitted_pae"]).lower() == "true"
               for r in csv.DictReader(open(FOLDS_CSV, encoding="utf-8"))}
    enqueued = {int(e["job_id"]): e for e in json.loads(ENQUEUED_JSON.read_text(encoding="utf-8"))}

    base = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev")
    served = _served_pae_exists(base)
    print(f"resolving PAE against the SERVING SURFACE at {base} (not this filesystem)\n")

    verdicts = []
    with Session(_engine()) as s:
        for job_id, e in sorted(enqueued.items()):
            path = s.scalar(select(ProteinAnalysis.pae_json_path)
                            .where(ProteinAnalysis.id == e["analysis_id"]))
            v = check_fold_persistence(
                job_id,
                emitted_pae=emitted.get(job_id, False),
                pae_json_path=path,
                exists=lambda _p, _id=e["analysis_id"]: served(_id))
            verdicts.append(v)
            print(f"  {e['accession']:<12} span={e['span_aa']:<4} {v.outcome}"
                  + ("  FATAL - stop the campaign" if v.is_fatal else ""))

    summary = summarise(verdicts)
    # ⚠ `fatal` holds verdict OBJECTS; rendering them as text here rather than letting json.dumps
    # raise, because a report that crashes after twenty folds has cost the folds and bought
    # nothing.
    summary["fatal"] = [str(v) for v in summary["fatal"]]
    print()
    print(json.dumps(summary, indent=2))
    return 0 if summary["may_continue"] else 1


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/task3_run2_folds.py")
    ap.add_argument("--enqueue", action="store_true", help="write the 20 Run 2 rows")
    ap.add_argument("--fold", action="store_true", help="fold them under the gate, recording")
    ap.add_argument("--requeue", action="store_true",
                    help="put the twenty back to pending after a run that failed them")
    ap.add_argument("--report", action="store_true", help="the three answers")
    ap.add_argument("--persistence", action="store_true", help="the four outcomes, from the DB")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true",
                    help="⚠ perform it. Without this every mode reports and writes nothing.")
    args = ap.parse_args(argv)
    if args.enqueue:
        return enqueue(args.owner)
    if args.fold:
        return fold(args.owner)
    if args.requeue:
        return requeue(args.owner)
    if args.persistence:
        return persistence(args.owner)
    if args.report:
        return report()
    ap.print_help()
    return 2


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
