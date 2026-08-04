#!/usr/bin/env python3
"""D-077 Task 1c — fold one fixed sequence at three chunk sizes and compare exactly.

    python scripts/chunk_invariance_run.py

THE QUESTION (D-077 decision 2). `ARCHITECTURE.md:616-618` records, as INFERENCE
NOT MEASUREMENT, that HER2 at 630 aa might fold at chunk 16/32 — untested. If so,
the local envelope is not a single length but a length-per-chunk_size curve, and
the free envelope is much larger than 440. But a fold produced at a different
`chunk_size` is only usable if chunk_size does not change the output. Chunking
tiles the trunk's triangular attention; it SHOULD be output-invariant. Should is
not measured.

THE READING IS ALREADY FIXED — two rows, frozen before this ever ran:

  byte-identical across all three  -> chunk_size is a MEMORY/TIME KNOB ONLY. The
      ceiling is a curve, folds across chunk sizes are commensurable, and probing
      at chunk 16/32 (Task 3 Arm B) is legitimate.

  different at all, by any margin  -> chunk_size is a RECIPE DIMENSION. The
      ceiling is defined ONLY at chunk 64, folds across chunk sizes are NOT
      commensurable, Arm B is ABANDONED (not deferred), and the divergence is a
      reportable finding in its own right — ESMFold's chunked trunk is not
      output-invariant is a methods note nobody publishes.

There is no third reading and no tolerance may be invented after seeing a diff
(D-041 dec 4). "Nearly identical" is the DIFFER branch.

WHAT IS FOLDED, and why not Trop-2. Decision 2 permits "the existing test
fixture's source, or Trop-2 at ~248 aa". Trop-2 (TACSTD2, P09758) is NOT in the
cohort — F-009 records it as one of four clinically-validated ADC targets Kathad's
filters excluded — so it has no row in `protein_analyses` and no sequence anywhere
in the repo (`data/heldout_positives.csv` carries its accession and trial data
only). The ~93 Trop-2 folds in `ARCHITECTURE.md:598-599` were dev-era. So this
uses the FIRST option decision 2 names: the source already folded by
`tests/test_runner.py::test_fold_produces_structure_and_provenance`, in-repo, no
network, no slicing judgement.

SAFETY. Writes only to `data/derived/`. Holds no database session; probe/diagnostic
folds must never reach `protein_analyses`, because `/api/coverage`'s folded count
would move and F-004's denominator 56 would move with it (D-077 dec 5).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.contracts import TIER_RECIPE  # noqa: E402
from worker.fold_compare import compare_folds, fold_from_pdb  # noqa: E402

# The existing GPU-test fixture source (tests/test_runner.py:209), verbatim.
FIXTURE_SOURCE = "MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVP" * 2

CHUNK_SIZES = (64, 32, 16)
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "derived" / "chunk_invariance"


def main() -> int:
    from worker import runner

    dtype = TIER_RECIPE["local"]["dtype"]          # resolved, not hand-passed (D-047/D-077 dec 3)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"D-077 Task 1c — chunk invariance")
    print(f"  sequence : test-fixture source, {len(FIXTURE_SOURCE)} aa")
    print(f"  dtype    : {dtype} (resolved from TIER_RECIPE['local'])")
    print(f"  chunks   : {', '.join(map(str, CHUNK_SIZES))}")
    print(f"  out      : {OUT_DIR}\n")

    folds: dict[int, dict] = {}
    for cs in CHUNK_SIZES:
        t0 = time.time()
        print(f"  folding at chunk_size={cs} ...", flush=True)
        result = runner.fold(FIXTURE_SOURCE, dtype=dtype, chunk_size=cs, source=runner.WHOLE)
        elapsed = time.time() - t0

        (OUT_DIR / f"chunk_{cs}.pdb").write_text(result.pdb, encoding="utf-8")
        (OUT_DIR / f"chunk_{cs}.plddt.json").write_text(json.dumps(result.plddt), encoding="utf-8")

        folds[cs] = fold_from_pdb(result.pdb, result.plddt)
        print(f"    -> {elapsed:.1f}s, {len(folds[cs]['coords'])} CA atoms, "
              f"mean pLDDT {(result.provenance.mean_plddt if result.provenance else None)}")

    print("\n  exact comparisons (no tolerance, first divergence reported):")
    verdicts = {}
    for a, b in ((64, 32), (64, 16), (32, 16)):
        res = compare_folds(folds[a], folds[b])
        verdicts[(a, b)] = res
        print(f"    chunk {a} vs {b}: {res.describe()}")

    all_identical = all(v.identical for v in verdicts.values())

    print("\n" + "=" * 72)
    if all_identical:
        print("  VERDICT: byte-identical across all three chunk sizes.")
        print("  READING (D-077 dec 2, row 1, frozen before this run):")
        print("    chunk_size is a MEMORY/TIME KNOB ONLY. The ceiling is a curve,")
        print("    folds across chunk sizes are commensurable, and Task 3 Arm B")
        print("    (probing at chunk 16/32) is UNLOCKED.")
    else:
        first = next(v for v in verdicts.values() if not v.identical)
        print("  VERDICT: outputs DIFFER.")
        print("  READING (D-077 dec 2, row 2, frozen before this run):")
        print("    chunk_size is a RECIPE DIMENSION. The ceiling is defined ONLY at")
        print("    chunk 64, folds across chunk sizes are NOT commensurable, and")
        print("    Task 3 Arm B is ABANDONED, NOT DEFERRED.")
        print(f"    First divergence (the evidence for the F-entry): {first.divergence.describe()}")
    print("=" * 72)
    print("  Land this as F-012 citing D-077. Do not invent a third reading.")

    summary = {
        "task": "D-077 Task 1c chunk invariance",
        "sequence": "tests/test_runner.py fixture source",
        "sequence_length": len(FIXTURE_SOURCE),
        "dtype": dtype,
        "chunk_sizes": list(CHUNK_SIZES),
        "all_identical": all_identical,
        "comparisons": {f"{a}v{b}": (v.identical if v.identical else v.divergence.describe())
                        for (a, b), v in verdicts.items()},
    }
    (OUT_DIR / "verdict.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
