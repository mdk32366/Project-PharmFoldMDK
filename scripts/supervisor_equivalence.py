#!/usr/bin/env python3
"""D-084 gate: does folding through the D-082 layer-3 supervisor change the STRUCTURE?

    python scripts/supervisor_equivalence.py --arm inprocess  --accession Q8WXD0 --tier local
    python scripts/supervisor_equivalence.py --arm supervised --accession Q8WXD0 --tier local
    python scripts/supervisor_equivalence.py --compare

⚠⚠ **ONE ARM PER INVOCATION, AND THAT IS A SAFETY PROPERTY, NOT A STYLE CHOICE.** The supervised
arm **spawns a child that loads the weights**. If the in-process arm had already cached them in
this process, **two model copies would be resident on one card at the same time** — which is the
configuration that took the host down on 2026-08-12 (a probe running beside a worker). Each arm
therefore runs in **its own process**, writes an artifact, and exits. The comparison reads files.

⚠ **It refuses to run while a job is `claimed`.** A live worker is already holding the weights, and
this script would be the *second* holder. The refusal is a **measurement**, not an assumption — it
reads the queue. `--i-have-stopped-the-worker` overrides it, and is named so that overriding it is
a sentence someone has to mean.

## What it proves, stated narrowly

**That the fold is byte-identical through the supervisor.** ⚠ A layer added to make failures
legible that quietly changed the structures would be **a worse defect than the one it prevents** —
every tranche-4 artifact would be plausible and different, with nothing red.

## What it does NOT prove

⚠ **It is not a determinism control.** `scripts/determinism_control.py` establishes that the recipe
returns the same answer twice **at all**; without that, `inprocess != supervised` and *"folding is
nondeterministic"* are the same observation. ⚠ **Run that first, on the same accession and tier**,
or this comparison cannot be attributed.

⚠ **It does not prove layer 3 catches anything.** Equivalence is the *precondition* for switching
it on, not evidence that it works. The death path is covered by `tests/test_fold_supervisor.py`.

⚠ **It adds no judgement of its own.** `worker.runner.fold` produces the structure and
`worker.fold_compare.compare_folds` compares it — **exactly, with no tolerance** (D-041 dec 4:
*"nearly identical" is the DIFFER branch*). There is no coordinate arithmetic in this file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT_DIR = REPO / "data" / "census"


def _refuse_if_worker_busy(overridden: bool) -> None:
    """⚠ Read the queue. A `claimed` job means the weights are already resident somewhere."""
    if overridden:
        print("⚠ worker-busy check OVERRIDDEN by --i-have-stopped-the-worker")
        return
    import sqlalchemy as sa
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from db.models import JobRecord

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("⚠ no DATABASE_URL — cannot check whether a worker is folding. "
                         "REFUSING: an unchecked card is how two model copies meet.")
    engine = sa.create_engine(url, connect_args={"connect_timeout": 10})
    with Session(engine) as s:
        claimed = s.scalar(select(func.count()).select_from(JobRecord)
                           .where(JobRecord.status == "claimed"))
    if claimed:
        raise SystemExit(
            f"⚠⚠ REFUSING: {claimed} job(s) are `claimed` — a worker is folding right now and "
            f"already holds the weights. Running this would put a SECOND model copy on the card, "
            f"which is the configuration that bugchecked the host on 2026-08-12. Stop the worker, "
            f"then re-run with --i-have-stopped-the-worker.")
    print(f"✅ no claimed jobs — the card is believed free (claimed={claimed})")


def _sequence_and_recipe(accession: str, tier: str) -> tuple[str, dict]:
    """⚠ The recipe is resolved from `TIER_RECIPE` at use time (D-047), never from a stored copy."""
    from core.contracts import TIER_RECIPE

    # ⚠ Reuses the ingest's own cache reader rather than a second one written here. A duplicate
    # loader is a second source for one quantity with nothing comparing them — and it is
    # cache-only, so this measurement performs NO network fetch.
    from scripts.census_ingest import sequence_from_cache

    recipe = TIER_RECIPE[tier]
    seq = sequence_from_cache(accession)
    if not seq:
        raise SystemExit(f"⚠ empty sequence for {accession} — refusing to fold nothing")
    return seq, recipe


def _artifact(arm: str, accession: str, tier: str, pdb: str, plddt: list[float]) -> dict:
    return {
        "arm": arm,
        "accession": accession,
        "tier": tier,
        # ⚠ The hash is over the PDB text, so "same structure" is a byte claim and not a summary.
        "pdb_sha256": hashlib.sha256(pdb.encode()).hexdigest(),
        "pdb_len": len(pdb),
        "n_plddt": len(plddt),
        "mean_plddt": sum(plddt) / len(plddt) if plddt else None,
    }


def run_arm(arm: str, accession: str, tier: str, overridden: bool) -> int:
    _refuse_if_worker_busy(overridden)
    seq, recipe = _sequence_and_recipe(accession, tier)
    print(f"arm={arm} | {accession} | {len(seq)} aa | dtype={recipe['dtype']} "
          f"chunk={recipe['chunk_size']}")

    if arm == "inprocess":
        from worker.runner import fold
        r = fold(seq, dtype=recipe["dtype"], chunk_size=recipe["chunk_size"], source="whole")
        pdb, plddt = r.pdb, list(r.plddt)
    else:
        from worker.fold_supervisor import FoldSupervisor
        sup = FoldSupervisor()
        try:
            payload = sup.fold(seq, dtype=recipe["dtype"], chunk_size=recipe["chunk_size"],
                               source="whole")
        finally:
            # ⚠ Always reaped. A leaked child keeps 8.4 GB on the card until the shell exits.
            sup.stop()
        pdb, plddt = payload["pdb"], list(payload["plddt"])

    art = _artifact(arm, accession, tier, pdb, plddt)
    # ⚠ The PDB itself is kept, not only its hash: a hash mismatch with no artifacts leaves nobody
    # able to say WHAT differed.
    (OUT_DIR / f"supervisor_equivalence.{arm}.pdb").write_text(pdb, encoding="utf-8")
    (OUT_DIR / f"supervisor_equivalence.{arm}.json").write_text(
        json.dumps(art, indent=2), encoding="utf-8")
    print(json.dumps(art, indent=2))
    return 0


def compare() -> int:
    a_p = OUT_DIR / "supervisor_equivalence.inprocess.json"
    b_p = OUT_DIR / "supervisor_equivalence.supervised.json"
    for p in (a_p, b_p):
        if not p.is_file():
            # ⚠ A category. "Not run" must never look like "compared and agreed."
            raise SystemExit(f"⚠ ARM_NOT_RUN — {p.name} absent. Nothing was compared.")
    a, b = json.loads(a_p.read_text()), json.loads(b_p.read_text())

    if (a["accession"], a["tier"]) != (b["accession"], b["tier"]):
        raise SystemExit(f"⚠⚠ THE ARMS ARE NOT THE SAME MEASUREMENT — "
                         f"{a['accession']}/{a['tier']} vs {b['accession']}/{b['tier']}. "
                         f"Comparing them would be meaningless. STOP.")

    from worker.fold_compare import compare_folds
    verdict = compare_folds(
        (OUT_DIR / "supervisor_equivalence.inprocess.pdb").read_text(),
        (OUT_DIR / "supervisor_equivalence.supervised.pdb").read_text(),
    )
    same_hash = a["pdb_sha256"] == b["pdb_sha256"]
    print(f"accession   | {a['accession']} tier={a['tier']}")
    print(f"in-process  | sha256={a['pdb_sha256'][:16]}… mean_plddt={a['mean_plddt']}")
    print(f"supervised  | sha256={b['pdb_sha256'][:16]}… mean_plddt={b['mean_plddt']}")
    print(f"⚠ byte-identical PDB | {same_hash}")
    print(f"⚠ compare_folds      | {verdict}")
    if not same_hash:
        print("\n⚠⚠ THE SUPERVISOR CHANGED THE STRUCTURE. DO NOT ENABLE WORKER_FOLD_IN_CHILD. "
              "⚠ And do NOT attribute this to the supervisor until determinism_control has been "
              "run on this accession and tier — a nondeterministic recipe produces this result "
              "with no supervisor involved.")
        return 1
    print("\n✅ byte-identical. This is the PRECONDITION for enabling layer 3 — not evidence that "
          "layer 3 catches anything.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("inprocess", "supervised"))
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--accession")
    ap.add_argument("--tier", choices=("local", "rental"), default="local")
    ap.add_argument("--i-have-stopped-the-worker", action="store_true",
                    help="⚠ bypass the claimed-job refusal. Named so that using it is a sentence.")
    args = ap.parse_args()

    if args.compare:
        return compare()
    if not args.arm or not args.accession:
        ap.error("--arm and --accession are required unless --compare")
    return run_arm(args.arm, args.accession, args.tier, args.i_have_stopped_the_worker)


if __name__ == "__main__":
    raise SystemExit(main())
