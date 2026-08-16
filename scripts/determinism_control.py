#!/usr/bin/env python3
"""Task 4a — the determinism control. ⚠ MANDATORY, FIRST, BOTH ARMS, BEFORE ANY COMPARISON.

    python scripts/determinism_control.py --accession Q8WXD0 --tier local --repeat 2

⚠⚠ **WITHOUT THIS, "int8 DIFFERS FROM fp16" AND "FOLDING IS NONDETERMINISTIC" ARE THE SAME
OBSERVATION.** Two folds at ONE recipe, per arm, before any cross-recipe number is computed.

## Why this exists rather than `ceiling_probe --repeat 2`

⚠ **`ceiling_probe --repeat k` measures STABILITY, not DETERMINISM.** Its `_attempt` returns
`{"length", "outcome", "mean_plddt"}` — it folds k times and asks whether each **succeeded**. Two
`OK` outcomes prove the recipe does not OOM twice; they say nothing about whether the model returned
the same answer twice. `mean_plddt` equality is a **scalar** signal, and two structurally different
folds can share a mean to the recorded precision.

**This module composes two existing, tested components and adds no judgement of its own:**
`worker.runner.fold` produces the structure; `worker.fold_compare.compare_folds` compares it —
⚠ **exactly, with no tolerance, by design** (D-041 dec 4: *"nearly identical" is the DIFFER
branch*). **It chooses no residues.** The sequence is handed in whole and folded whole; there is no
coordinate arithmetic in this file, which is why it is safe to write immediately before a
measurement.

## What it does NOT do

⚠ **It does not read any cross-recipe comparison. `### D-078` is unwritten.** The arms are folded
and recorded; interpreting int8 against fp16 is a separate, owner-reserved act.

⚠ **It covers the FOLD KERNEL, not the enqueue path** (R12). Nobody may cite it as end-to-end
determinism. The three-number check (`core/fold_reconcile.py`) guards slicing and begins at ingest —
a different failure mode, a different guard, and both are required.

⚠ **Any ceiling it touches is SINGLE-PROCESS headroom.** `runner._MODEL_CACHE` is module-level and
therefore per-process: a probe and a worker folding concurrently hold two copies of the weights on
one card.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.contracts import TIER_RECIPE  # noqa: E402
from core.vram_guard import (  # noqa: E402
    apply_allocator_cap, cuda_memory, peak_vram, reset_peak, sysmem_fallback_state,
)
from worker.fold_compare import compare_folds, fold_from_pdb  # noqa: E402

CENSUS = REPO / "data" / "census"
CACHE = CENSUS / "spancache"
MANIFEST = CENSUS / "census_manifest.v6.csv"


def span_from_manifest(accession: str) -> dict[str, Any]:
    """⚠ The span is READ FROM THE MANIFEST, never recomputed here. The manifest is the
    pre-registration of what folds and how; recomputing would create a second source with nothing
    comparing them."""
    import csv
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["census_accession"] == accession:
                return r
    raise SystemExit(f"⚠ {accession} is not in {MANIFEST.name} — refusing to fold a row the "
                     f"manifest does not pre-register")


def sequence_from_cache(accession: str) -> str:
    """⚠ FROM THE CACHE, NOT THE NETWORK. `ceiling_probe --accession` issues a live UniProt
    request; the cached entry is the one the manifest was built from."""
    p = CACHE / f"{accession}.json"
    if not p.exists():
        raise SystemExit(f"⚠ no cache entry for {accession} — NOT fetched; report and stop")
    return (json.loads(p.read_text(encoding="utf-8")).get("sequence") or {}).get("value", "")


def _digest(cmp_input: dict) -> str:
    """sha256 over the comparator input. ⚠ Exact — coordinates and pLDDT, no rounding.

    Rounding here would be a tolerance, and D-041 dec 4 rules that no tolerance may be invented:
    *"nearly identical" is the DIFFER branch*.
    """
    import hashlib
    payload = json.dumps({"coords": cmp_input["coords"], "plddt": cmp_input["plddt"]},
                         sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def gpu_memory_mib() -> Optional[dict[str, Any]]:
    """Peak/used VRAM, read from `nvidia-smi`. ⚠ Absent is a CATEGORY, never a zero."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=30, check=True).stdout.strip().splitlines()[0]
        used, total = (int(x.strip()) for x in out.split(","))
        return {"used_mib": used, "total_mib": total}
    except Exception as e:                                        # noqa: BLE001
        return {"unavailable": f"{type(e).__name__}: {e}"}


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/determinism_control.py", description=__doc__)
    ap.add_argument("--accession", required=True)
    ap.add_argument("--tier", required=True, choices=("local", "rental"),
                    help="⚠ the recipe is RESOLVED from TIER_RECIPE, never hand-passed (D-047)")
    ap.add_argument("--repeat", type=int, default=2,
                    help="folds at the one recipe. ⚠ 2 is the control; more is more evidence")
    ap.add_argument("--out", default=str(CENSUS / "determinism_control.json"))
    #: ⚠ DEFAULT None = NO CAP, and that is deliberate rather than lax. The pre-registration says
    #: the allocated-vs-reserved gap "decides the cap" — so capping this run would be circular:
    #: the measurement that sets the cap cannot be bounded by the cap it sets. Layer 1 (sysmem
    #: fallback off) is what makes an uncapped run safe, and it is owner-attested below.
    ap.add_argument("--memory-fraction", type=float, default=None,
                    help="⚠ allocator cap. OMIT for the run that MEASURES demand — see D-082")
    ap.add_argument("--layer1-attested", action="store_true",
                    help="⚠ the owner states the sysmem fallback policy is set. It CANNOT be "
                         "verified from code; this records an attestation, never a measurement")
    args = ap.parse_args(argv)

    row = span_from_manifest(args.accession)
    span_aa = int(row["span_aa"])
    start, end = int(row["span_start"]), int(row["span_end"])
    full = sequence_from_cache(args.accession)
    fold_seq = full[start - 1: end]

    # ⚠ THE THREE NUMBERS, CHECKED BEFORE THE FIRST FOLD. A slice that disagrees with its recorded
    # length is a construction defect, and folding it would produce a plausible wrong artifact.
    if len(fold_seq) != span_aa:
        raise SystemExit(f"⚠ STOP: sliced {len(fold_seq)} residues, manifest span_aa is {span_aa}")

    # ⚠ Recipe resolved at fold time from the tier table (D-047 / D-077 dec 3). Not hand-passed,
    # not read from any stored inference_settings.
    recipe = TIER_RECIPE[args.tier]
    dtype, chunk_size = recipe["dtype"], recipe["chunk_size"]

    header = {
        "accession": args.accession, "gene_hint": row.get("census_class", ""),
        "tier": args.tier, "dtype": dtype, "chunk_size": chunk_size, "repeat": args.repeat,
        "manifest": MANIFEST.name, "manifest_span_aa": span_aa,
        "span_start": start, "span_end": end, "sliced_length": len(fold_seq),
        "span_definition": row.get("span_definition", ""),
        "span_starts_at_residue_1": start == 1,
        "gpu_before": gpu_memory_mib(),
        # ⚠ D-082 layer state, recorded on the artifact so a later reader knows what protected
        # this run — or did not.
        "layers": {
            "layer1_sysmem_fallback": {
                **sysmem_fallback_state(),
                # ⚠ ATTESTED, NOT MEASURED. There is no query API; this records who said so.
                "owner_attested_set": bool(args.layer1_attested),
                "attestation_note": ("the owner states the policy is set for BOTH the venv stub "
                                     "and the base interpreter. ⚠ This is testimony, not a "
                                     "measurement, and it is labelled as such."),
            },
            "layer2_allocator_cap": (apply_allocator_cap(args.memory_fraction)
                                     if args.memory_fraction else
                                     {"applied": False,
                                      "why": ("deliberately uncapped: this run MEASURES the demand "
                                              "that decides the cap, so capping it would be "
                                              "circular (D-082 pre-registration §3)")}),
            "layer3_child_process": {"applied": False,
                                     "why": "not wired into the fold path yet — stated, not implied"},
        },
        "cuda_mem_get_info_before": (lambda m: {"free_mib": m[0], "total_mib": m[1]} if m else None)(
            cuda_memory()),
        # ⚠ Stated BEFORE the first fold, so the line that opens the run names what it measured.
        "limitations": [
            "Covers the FOLD KERNEL only, not the enqueue path. Not end-to-end determinism (R12).",
            "Determinism verified on a span BEGINNING AT RESIDUE 1. Only 410 of 3,467 manifest "
            "rows (11.8%) begin there; for proteins whose census span starts at a non-1 residue "
            "the probe was not directly exercised, though the kernel property is expected to "
            "generalise. Stated, not softened.",
            "Any ceiling touched here is SINGLE-PROCESS headroom: runner._MODEL_CACHE is "
            "module-level and per-process, so a probe and a worker folding concurrently hold two "
            "copies of the weights on one card.",
            "NO CROSS-RECIPE COMPARISON IS READ. D-078 is unwritten.",
        ],
    }
    print(json.dumps(header, indent=2))
    print(f"\n⚠ folding {args.accession} {start}-{end} = {span_aa} aa, "
          f"{args.repeat}x at dtype={dtype} chunk_size={chunk_size}\n", file=sys.stderr)

    from worker import runner

    folds, records = [], []
    for i in range(args.repeat):
        # ⚠ BEFORE the fold, or the peak describes the wrong window.
        reset_peak()
        t0 = time.time()
        result = runner.fold(fold_seq, dtype=dtype, chunk_size=chunk_size, source=runner.WHOLE)
        wall = time.time() - t0
        peak = peak_vram()
        cmp_input = fold_from_pdb(result.pdb, result.plddt)
        folds.append(cmp_input)
        # ⚠⚠ PERSISTED, because otherwise the cross-driver question CANNOT BE ANSWERED LATER.
        # The first version of this artifact stored mean_plddt, ca_residues and plddt_len — no
        # coordinates — so "identical across drivers" would have rested on 74.81 == 74.81, a
        # scalar to two decimals. That is exactly the weak signal `ceiling_probe --repeat 2` was
        # rejected for, rebuilt inside the instrument meant to replace it.
        cmp_digest = _digest(cmp_input)
        rec = {
            "attempt": i + 1,
            "wall_clock_s": round(wall, 2),
            "ca_residues_in_pdb": len(cmp_input["coords"]),
            "plddt_len": len(result.plddt),
            "mean_plddt": (result.provenance.mean_plddt if result.provenance else None),
            "gpu_after": gpu_memory_mib(),
            # ⚠⚠ THREE NUMBERS, NONE STANDING FOR THE OTHER. `nvidia-smi used` is RESERVED,
            # inflated by the caching allocator's retained pool — it is what we mistook for demand
            # on 596.72 when we recorded 7,658 MiB. max_allocated is the actual demand.
            "peak_vram": peak,
            "cuda_mem_get_info_after": (lambda m: {"free_mib": m[0], "total_mib": m[1]} if m else None)(
                cuda_memory()),
            "nvidia_driver_version": getattr(result.provenance, "nvidia_driver_version", None),
            # ⚠ A cheap exact identity for the STRUCTURE. Two folds on different drivers with the
            # same digest are identical without needing the sidecar; different digests say only
            # that they differ, and `compare_folds` on the sidecars says WHERE.
            "comparator_digest": cmp_digest,
            # ⚠ The recipe AS RECORDED BY THE FOLD, not as passed in. A fold completing without a
            # recorded recipe is a stop condition.
            "recipe_recorded": {
                "dtype": getattr(result.provenance, "dtype", None),
                "chunk_size": getattr(result.provenance, "chunk_size", None),
            } if result.provenance else None,
        }
        if rec["recipe_recorded"] is None:
            raise SystemExit(f"⚠ STOP: attempt {i+1} completed with NO recorded recipe")
        # ⚠ The third number, read out of the structure the fold actually produced.
        if rec["ca_residues_in_pdb"] != span_aa:
            print(f"⚠ attempt {i+1}: structure holds {rec['ca_residues_in_pdb']} CA residues, "
                  f"manifest span_aa is {span_aa}", file=sys.stderr)
        records.append(rec)
        print(f"  attempt {i+1}/{args.repeat} | {wall:.1f}s | {rec['ca_residues_in_pdb']} CA | "
              f"mean_plddt {rec['mean_plddt']} | peak_alloc "
              f"{peak.get('max_allocated_mib')} MiB | peak_reserved "
              f"{peak.get('max_reserved_mib')} MiB | driver {rec['nvidia_driver_version']}",
              file=sys.stderr)

    # ⚠ EXACT comparison, no tolerance. Every pair, not just the first against the last.
    comparisons = []
    for a in range(len(folds)):
        for b in range(a + 1, len(folds)):
            res = compare_folds(folds[a], folds[b])
            comparisons.append({"pair": [a + 1, b + 1], "identical": res.identical,
                                "divergence": res.describe()})
            print(f"  compare {a+1} vs {b+1} | {res.describe()}", file=sys.stderr)

    deterministic = all(c["identical"] for c in comparisons)
    out = {**header, "attempts": records, "comparisons": comparisons,
           "comparator_sidecar": None,   # filled below once written
           "deterministic": deterministic,
           "verdict": ("IDENTICAL across all pairs — the kernel is deterministic at this recipe"
                       if deterministic else
                       "⚠ NOT IDENTICAL — the kernel is nondeterministic at this recipe, and no "
                       "cross-recipe difference can be attributed until this is resolved")}
    # ⚠ The comparator inputs go to a SIDECAR so the main artifact stays readable, and the main
    # artifact carries each fold's digest so the sidecar is not needed for a yes/no answer.
    import os
    side = Path(args.out).with_suffix(".folds.json")
    with open(side, "w", encoding="utf-8") as fh:
        json.dump({"accession": args.accession, "dtype": dtype, "chunk_size": chunk_size,
                   "nvidia_driver_version": records[0].get("nvidia_driver_version"),
                   "note": ("comparator inputs, persisted so a CROSS-DRIVER comparison is "
                            "answerable later. ⚠ Without these, identity across drivers rests on "
                            "a scalar mean, which is the weak signal this instrument exists to "
                            "replace."),
                   "folds": folds}, fh)
        fh.flush()
        os.fsync(fh.fileno())
    out_extra_sidecar = str(side)

    # ⚠ fsync. The last probe's append-only file came back as 55 bytes of NUL after a hard reset:
    # a write that reaches the page cache and not the disk is not a record.
    out["comparator_sidecar"] = out_extra_sidecar
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    print(f"\n{out['verdict']}")
    print(f"wrote {args.out}")
    return 0 if deterministic else 1


if __name__ == "__main__":
    raise SystemExit(run())
