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
from typing import Any, Optional

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
    print(f"\nWROTE {len(written)} Run {RUN_LABEL} rows. ⚠ The ids, so the population is "
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
        self._last_pf: Any = None

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


def _pending_local_jobs(session) -> dict[int, str]:
    from sqlalchemy import select                        # noqa: PLC0415
    from db.models import JobRecord, ProteinAnalysis     # noqa: PLC0415

    rows = session.execute(
        select(JobRecord.id, ProteinAnalysis.input_value)
        .join(ProteinAnalysis, ProteinAnalysis.id == JobRecord.analysis_id)
        .where(JobRecord.status == "pending")).all()
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

    with Session(_engine()) as s:
        pending = _pending_local_jobs(s)
    strangers = {jid: acc for jid, acc in pending.items() if jid not in allowed}
    if strangers:
        print(f"REFUSING: {len(strangers)} pending job(s) are outside the twenty "
              f"({sorted(strangers.items())[:5]}). `run_worker` claims the next job of its TIER, "
              f"not 'one of mine' — starting now could fold a stranger into a 20-row exception.",
              file=sys.stderr)
        return 1
    print(f"queue check: {len(pending)} pending job(s), all inside the twenty.")

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
                   tier=os.environ.get("WORKER_TIER", "local"),
                   should_stop=lambda: len(rec.rows) >= SAMPLE_N)
    finally:
        # ⚠ Written even on a mid-run stop. A campaign that dies at fold 11 and records nothing
        # has cost eleven folds and bought nothing.
        path = rec.write()
        print(f"\nrecorded {len(rec.rows)} fold(s) to {_rel(path)}")
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
    print("    ⚠ ONE projector. This script does not compute a second one.\n")

    print("3 - PAE AT L = 1, AND THE PRE-REGISTERED RULE")
    tiny = [r for r in rows if int(r["span_aa"]) == 1]
    if not tiny:
        print("    no 1-residue fold is recorded yet.")
    for r in tiny:
        emitted = str(r["emitted_pae"]).lower() == "true"
        print(f"    {r['accession']}: the fold {'EMITTED' if emitted else 'emitted NO'} PAE.")
        print("    ⚠ That is what the fold produced. Whether it LANDED is the four-outcome check")
        print("      below, against the database - a produced-but-unpersisted PAE is the two-gate")
        print("      defect Task 2 repaired, and it reads as success from here.")
    print()
    print("    the four named outcomes need the DB and the owner's proxy:")
    print("      python scripts/task3_run2_folds.py --persistence --i-am-the-owner")
    return 0


def _served_pae_exists(base_url: str):
    """⚠⚠ `exists` MUST ASK THE SERVING SURFACE, NOT THIS LAPTOP.

    `check_fold_persistence`'s default is `os.path.isfile`, which is right for a local campaign
    and **catastrophically wrong here**: the PAE lives on the Fly volume, so a local check would
    return `file_missing` for all twenty — a fabricated FATAL that stops a healthy campaign.
    ⚠ Asking `GET /api/analyses/{id}/pae` is also the stronger question: a file the volume holds
    but the surface will not serve is not persisted in any sense a reader can use.
    """
    import urllib.error          # noqa: PLC0415
    import urllib.request        # noqa: PLC0415

    def _exists(analysis_id: int) -> bool:
        url = f"{base_url.rstrip('/')}/api/analyses/{analysis_id}/pae"
        req = urllib.request.Request(url, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return 200 <= r.status < 300
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            # ⚠ A 5xx is NOT "the file is missing". Returning False here would turn an outage
            # into `file_missing` on every row and read as a persistence defect.
            raise SystemExit(f"refusing: {url} returned {e.code}; that is not an answer about "
                             f"whether the PAE resolves.")
        except urllib.error.URLError as e:
            raise SystemExit(f"refusing: cannot reach {url} ({e.reason}). An unreachable surface "
                             f"is an absent measurement, not a missing file.")
    return _exists


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
    ap.add_argument("--report", action="store_true", help="the three answers")
    ap.add_argument("--persistence", action="store_true", help="the four outcomes, from the DB")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true",
                    help="⚠ perform it. Without this every mode reports and writes nothing.")
    args = ap.parse_args(argv)
    if args.enqueue:
        return enqueue(args.owner)
    if args.fold:
        return fold(args.owner)
    if args.persistence:
        return persistence(args.owner)
    if args.report:
        return report()
    ap.print_help()
    return 2


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
