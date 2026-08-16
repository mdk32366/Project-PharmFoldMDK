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


#: ⚠ The measured A6000 single-fold ceiling. Folding past it is the failure mode this whole
#: layer exists for, and a VERIFICATION that triggers it would be self-defeating.
CEILING_AA = 440


def _sequence_and_recipe(accession: str, tier: str) -> tuple[str, dict, dict]:
    """The **manifest SPAN**, the recipe, and the coordinates — not the whole protein.

    ⚠⚠ **The first version folded `sequence_from_cache(accession)` — the FULL sequence.** For a
    tranche-4 row that is the wrong molecule *and* a real hazard: `Q8N423`'s span is 439 aa but its
    full chain is **597 aa, well past the 440 ceiling**. A verification harness would have folded
    597 residues and risked **the exact failure layer 3 exists to catch, before layer 3 was on.**

    ⚠ It now folds **what the worker folds** — the slice, with `source='sliced_ecd'` and the same
    coordinates — so equivalence is measured on the real workload rather than a longer one.
    """
    import csv

    from core.contracts import TIER_RECIPE
    # ⚠ The ingest's own cache reader, not a second one. Cache-only: no network fetch.
    from scripts.census_ingest import sequence_from_cache

    manifest = REPO / "data" / "census" / "census_manifest.v7.csv"
    rows = [r for r in csv.DictReader(manifest.open(encoding="utf-8"))
            if r["census_accession"] == accession]
    if not rows:
        raise SystemExit(f"⚠ {accession} is not in the census manifest — refusing to invent a span")
    r = rows[0]

    full = sequence_from_cache(accession)
    start, end = int(r["span_start"]), int(r["span_end"])
    span = full[start - 1: end]
    if not span:
        raise SystemExit(f"⚠ empty span for {accession} — refusing to fold nothing")
    if len(span) != int(r["span_aa"]):
        raise SystemExit(f"⚠⚠ {accession}: slice is {len(span)} aa, manifest says {r['span_aa']} — "
                         f"STOP. A slice disagreeing with its recorded length is a construction "
                         f"defect, not a rounding difference.")
    if len(span) > CEILING_AA:
        # ⚠ REFUSE. A verification that triggers the failure it is verifying against is worthless.
        raise SystemExit(f"⚠⚠ {accession}: span is {len(span)} aa, past the {CEILING_AA} aa "
                         f"ceiling. REFUSING — pick a shorter accession.")
    return span, TIER_RECIPE[tier], {"ecd_start": start, "ecd_end": end,
                                     "span_aa": int(r["span_aa"]), "full_length": len(full)}


def _ca_coords(pdb_path: Path) -> list[tuple[float, float, float]]:
    """CA coordinates in residue order, parsed from the PDB. ⚠ No tolerance, no rounding — the
    strings are converted once and compared as given."""
    out = []
    for line in pdb_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            out.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return out


def _artifact(arm: str, accession: str, tier: str, pdb: str, plddt: list[float]) -> dict:
    return {
        "arm": arm,
        "accession": accession,
        "tier": tier,
        # ⚠ The hash is over the PDB text, so "same structure" is a byte claim and not a summary.
        "pdb_sha256": hashlib.sha256(pdb.encode()).hexdigest(),
        "pdb_len": len(pdb),
        "n_plddt": len(plddt),
        # ⚠ Kept in full, not summarised: `compare_folds` needs the per-residue values, and a mean
        # cannot distinguish two structures that differ.
        "plddt": list(plddt),
        "mean_plddt": sum(plddt) / len(plddt) if plddt else None,
    }


def run_arm(arm: str, accession: str, tier: str, overridden: bool) -> int:
    _refuse_if_worker_busy(overridden)
    seq, recipe, coords = _sequence_and_recipe(accession, tier)
    print(f"arm={arm} | {accession} | span {len(seq)} aa "
          f"({coords['ecd_start']}-{coords['ecd_end']} of {coords['full_length']}) | "
          f"dtype={recipe['dtype']} chunk={recipe['chunk_size']} | ceiling {CEILING_AA}")

    if arm == "inprocess":
        from worker.runner import fold
        r = fold(seq, dtype=recipe["dtype"], chunk_size=recipe["chunk_size"],
                 source="sliced_ecd", ecd_start=coords["ecd_start"], ecd_end=coords["ecd_end"])
        pdb, plddt = r.pdb, list(r.plddt)
    else:
        from worker.fold_supervisor import FoldSupervisor
        sup = FoldSupervisor()
        try:
            payload = sup.fold(seq, dtype=recipe["dtype"], chunk_size=recipe["chunk_size"],
                               source="sliced_ecd", ecd_start=coords["ecd_start"],
                               ecd_end=coords["ecd_end"])
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

    # ⚠ `compare_folds` takes MAPPINGS with "coords" and "plddt" — NOT PDB text. The first
    # version passed strings and died in `fold["coords"]`. Fixed by reading the contract rather
    # than by removing the call: the CA coordinates are the substantive comparison, and the sha256
    # below is only a byte claim over the rendered file.
    from worker.fold_compare import compare_folds
    verdict = compare_folds(
        {"coords": _ca_coords(OUT_DIR / "supervisor_equivalence.inprocess.pdb"),
         "plddt": a["plddt"]},
        {"coords": _ca_coords(OUT_DIR / "supervisor_equivalence.supervised.pdb"),
         "plddt": b["plddt"]},
    ).describe()
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
