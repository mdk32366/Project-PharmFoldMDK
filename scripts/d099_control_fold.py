"""D-099 + amendment 1 — the control fold. LOCAL GPU, NO INGEST.

⚠⚠ THIS SCRIPT CANNOT WRITE THE DATABASE. It imports nothing from `db/` or `core.enqueue`, and a
self-check asserts that at start-up. `D-099` condition 3 is NO INGEST: artifacts land outside
`protein_analyses`, no census row is written, updated or re-pointed, and **the 2,690 keep their
NULL `pae_json_path`** — `F-042` is recorded, not patched away.

⚠ `D-099` condition 2: `boundary_method` stays `sliced_ecd`. Nothing here writes a
`boundary_source` or an assembled method, and `RECOGNISED_BOUNDARY_METHODS` is untouched.

⚠ `D-099` condition 4: local tier only. `dtype`/`chunk_size` come from the manifest row, which
rules `int8`/`64` for all 25 — the recipe these proteins were already folded under.

⚠⚠ F-034's lesson, wired in as a hard stop: **the harness checks its own input.** `fold()` does NOT
slice — `ecd_start`/`ecd_end` are provenance only — so the caller must pass the already-sliced span.
If `len(sliced) != span_aa` the run STOPS. A verification harness that folds the wrong molecule
looks exactly like one that works.

⚠⚠ D-099 amendment 1 §6: the provenance records **whether `artifact_dir` was set, on its face**.
A capture whose survival depends on an unrecorded environment variable is the M3 hazard reproduced
inside its own remedy.

    python scripts/d099_control_fold.py            # all 25
    python scripts/d099_control_fold.py --limit 2  # smoke first
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SAMPLE = REPO / "data" / "census" / "d099_control_sample.csv"
MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
CACHE = REPO / "data" / "census" / "spancache"
#: ⚠ Outside `protein_analyses` by construction — a directory, not a table (D-099 condition 3).
ARTIFACT_DIR = REPO / "data" / "control" / "d099"
SUMMARY = REPO / "data" / "control" / "d099_control_summary.csv"

KNOWN_GOOD_INT8 = 440


def assert_no_db_reachable() -> None:
    """⚠ The guard is structural: these modules are never imported, so this script cannot write a
    row even by mistake. Asserted rather than promised."""
    banned = [m for m in ("db.models", "core.enqueue", "sqlalchemy") if m in sys.modules]
    if banned:
        raise SystemExit(f"⚠ REFUSING TO RUN — database modules already imported: {banned}")


def sliced_sequence(acc: str, span_start: int, span_end: int) -> str:
    doc = json.loads((CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
    seq = doc["sequence"]["value"]
    return seq[span_start - 1:span_end]          # 1-based inclusive -> 0-based slice


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="fold only the first N (smoke test)")
    args = ap.parse_args()

    assert_no_db_reachable()

    with SAMPLE.open(encoding="utf-8") as fh:
        sample = list(csv.DictReader(fh))
    with MANIFEST.open(encoding="utf-8") as fh:
        man = {r["census_accession"]: r for r in csv.DictReader(fh)}
    if args.limit:
        sample = sample[:args.limit]

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_dir_set = True                      # ⚠ recorded on the face of every record

    print(f"subjects        : {len(sample)}")
    print(f"artifact_dir    : {ARTIFACT_DIR}")
    print(f"artifact_dir_set: {artifact_dir_set}   ⚠ recorded in every provenance record")
    print("ingest          : NONE — no database module is imported (D-099 condition 3)\n")

    from worker.runner import fold, write_artifacts   # noqa: PLC0415 — after the DB guard

    rows = []
    for i, s in enumerate(sample, 1):
        acc = s["acc"]
        m = man[acc]
        s0, s1 = int(m["span_start"]), int(m["span_end"])
        span_aa = int(m["span_aa"])
        seq = sliced_sequence(acc, s0, s1)

        # ⚠⚠ F-034: check the input, do not trust the tool to object.
        if len(seq) != span_aa:
            raise SystemExit(
                f"⚠⚠ STOP — {acc}: sliced {len(seq)} residues but the manifest says {span_aa}. "
                "Folding this would fold a different molecule (F-025's shape).")
        if span_aa > KNOWN_GOOD_INT8:
            raise SystemExit(f"⚠ STOP — {acc}: {span_aa} aa exceeds known_good {KNOWN_GOOD_INT8}")

        dtype = m["dtype"]
        chunk = int(m["chunk_size"]) if m["chunk_size"] else None
        print(f"[{i}/{len(sample)}] {acc} arm={s['arm']} n_dom={s['n_dom']} "
              f"span={span_aa} dtype={dtype} chunk={chunk} ...", flush=True)

        t0 = time.time()
        result = fold(seq, dtype=dtype, chunk_size=chunk, source="sliced_ecd",
                      ecd_start=s0, ecd_end=s1)
        dt = time.time() - t0

        out = ARTIFACT_DIR / acc
        written = write_artifacts(result, out)
        pae_present = result.pae is not None
        pae_n = len(result.pae) if pae_present else 0

        # ⚠ The provenance the amendment requires, on its face.
        (out / "d099_provenance.json").write_text(json.dumps({
            "census_accession": acc,
            "arm": s["arm"],
            "n_domains_inside_span": int(s["n_dom"]),
            "span_aa": span_aa, "span_start": s0, "span_end": s1,
            "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
            "dtype": dtype, "chunk_size": chunk,
            "boundary_method": m["boundary_method"],
            "span_definition": m["span_definition"],
            "artifact_dir_set": artifact_dir_set,
            "artifact_dir": str(ARTIFACT_DIR),
            "pae_emitted": pae_present,
            "pae_matrix_n": pae_n,
            "files_written": written,
            "ingested": False,
            "folded_at": datetime.now(timezone.utc).isoformat(),
            "seconds": round(dt, 1),
            "authorised_by": "D-099 + amendment 1",
        }, indent=2), encoding="utf-8")

        mean_plddt = (round(sum(result.plddt) / len(result.plddt), 2)) if result.plddt else None
        print(f"          -> pae_emitted={pae_present} n={pae_n} "
              f"mean_plddt={mean_plddt} {dt:.1f}s", flush=True)

        rows.append({"acc": acc, "arm": s["arm"], "n_dom": s["n_dom"], "span_aa": span_aa,
                     "pae_emitted": pae_present, "pae_matrix_n": pae_n,
                     "mean_plddt": mean_plddt, "artifact_dir_set": artifact_dir_set,
                     "seconds": round(dt, 1)})

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n_pae = sum(1 for r in rows if r["pae_emitted"])
    print(f"\n{'=' * 70}")
    print(f"⚠ PAE EMITTED ON {n_pae}/{len(rows)} LOCAL int8 CHUNKED FOLDS")
    if n_pae == len(rows):
        print("  -> `pae_never_emitted` is EXCLUDED. The census absence is a PIPELINE loss,")
        print("     not a model one: F-042 stands as pae_absent_local_tier.")
    elif n_pae == 0:
        print("  ⚠⚠ NONE. F-042 is a DIFFERENT finding and must be REWRITTEN, not amended")
        print("     (D-099 consequence 1).")
    print(f"summary -> {SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
