#!/usr/bin/env python3
"""Find the single-fold sequence-length ceiling on the current GPU (D-022).

D-020 found the rental bucket non-uniform: MUC16/FAT2 are unfoldable as one sequence
on any card, and several targets (NOTCH2 1652, PTPRZ1 1612, LRP6 1351, JAG1 1034) sit
near an unknown limit. D-022 ruled: measure the A6000 single-fold ceiling to route the
borderline. This is that measurement — same shape and method as the local ceiling
(S-004/S-005), a length bisection, but on the rented A6000.

RUN ON THE GPU HOST (RunPod A6000), not in CI — there is no GPU runner. The bisection
LOGIC below is pure and unit-tested on the gate; the fold at each length is GPU-bound
and imported lazily through the runner (D-018).

CRASH-RESILIENT BY DESIGN. S-004 taught that a fold can take the host down (a Windows
bugcheck; on Linux/A6000 the likely failure is a catchable CUDA OOM, but a hang or a
driver fault can still kill the process). So every attempt is appended to a JSONL
results file BEFORE the next one starts, and a re-run REPLAYS that file to resume — a
process death loses at most the in-flight attempt, never the accumulated bounds.

Content note: ESMFold memory scales ~O(length^2) and is dominated by length, not
sequence identity, so a truncation of one long real sequence is a sound probe of the
length ceiling (S-005 used HER2-ECD truncations for exactly this reason).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Anchors from the local-tier work (S-005): 440 aa folded clean, so it is a safe
# known-good lower bound for a bigger card too. The upper bound is the source length
# or a supplied cap. These are DEFAULTS; the A6000 ceiling is what we are measuring.
DEFAULT_GOOD = 440
DEFAULT_STEP = 25          # converge to within one step; finer is more folds = more $

OK = "ok"
OOM = "oom"
ERROR = "error"


# ── pure bisection logic (unit-tested on the CI gate) ─────────────────────────

def next_probe_length(good: int, bad: int, step: int = DEFAULT_STEP) -> Optional[int]:
    """The next length to try, or None when converged.

    `good` = largest length known to fold; `bad` = smallest known to fail; good < bad.
    Converged when the gap is within `step` — the ceiling is then `good` (the largest
    length proven to fold). Returns the midpoint otherwise.
    """
    if bad <= good:
        raise ValueError(f"good ({good}) must be < bad ({bad})")
    if bad - good <= step:
        return None
    return (good + bad) // 2


def bounds_from_history(history: list[dict], init_good: int, init_bad: int) -> tuple[int, int]:
    """Reconstruct (good, bad) from a results log so a crashed probe can resume.

    A length that folded (`ok`) raises the floor; one that failed (`oom`/`error`) lowers
    the ceiling. Out-of-range or malformed rows are ignored — the log is append-only and
    a partial final line from a crash must not corrupt the bounds.
    """
    good, bad = init_good, init_bad
    for row in history:
        length, outcome = row.get("length"), row.get("outcome")
        if not isinstance(length, int) or outcome not in (OK, OOM, ERROR):
            continue
        if outcome == OK:
            good = max(good, length)
        else:
            bad = min(bad, length)
    return good, bad


def ceiling_from_history(history: list[dict], init_good: int) -> int:
    """The largest length proven to fold — the reported ceiling."""
    good = init_good
    for row in history:
        if row.get("outcome") == OK and isinstance(row.get("length"), int):
            good = max(good, row["length"])
    return good


def _read_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            pass                      # a torn final line from a crash — skip, don't die
    return out


# ── the GPU-bound probe loop (owner-run on the A6000) ─────────────────────────

def _attempt(source: str, length: int, dtype: str, chunk_size: Optional[int]) -> dict:
    """Fold source[:length] and classify the outcome. GPU-bound (runner.fold imports
    torch lazily). A CUDA OOM is the expected failure and is caught; anything else is
    recorded as `error` with its message."""
    from worker import runner

    try:
        result = runner.fold(source[:length], dtype=dtype, chunk_size=chunk_size,
                             source=runner.WHOLE)
        return {"length": length, "outcome": OK,
                "mean_plddt": (result.provenance.mean_plddt if result.provenance else None)}
    except Exception as e:  # noqa: BLE001
        msg = f"{type(e).__name__}: {e}"
        outcome = OOM if "out of memory" in str(e).lower() or "CUDA out of memory" in str(e) else ERROR
        return {"length": length, "outcome": outcome, "detail": msg[:300]}


def _read_source(args) -> str:
    if args.fasta:
        text = Path(args.fasta).read_text(encoding="utf-8")
        return "".join(l.strip() for l in text.splitlines() if l and not l.startswith(">"))
    if args.accession:
        from scripts.ecd_lengths import fetch  # reuse the UniProt client
        return (fetch(args.accession).get("sequence") or {}).get("value", "")
    raise SystemExit("provide --fasta or --accession for the probe source sequence")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--fasta", help="path to a (long) source sequence to truncate")
    src.add_argument("--accession", help="UniProt accession to fetch as the source sequence")
    ap.add_argument("--good", type=int, default=DEFAULT_GOOD, help="known-good lower bound")
    ap.add_argument("--bad", type=int, default=None, help="known-bad upper bound (default: source length)")
    ap.add_argument("--step", type=int, default=DEFAULT_STEP)
    ap.add_argument("--dtype", default="fp16", help="A6000 default fp16 (48 GB, no int8 needed)")
    ap.add_argument("--chunk-size", type=int, default=None)
    ap.add_argument("--out", default="a6000_ceiling.jsonl", help="append-only results log (also the resume file)")
    args = ap.parse_args(argv)

    source = _read_source(args)
    init_good = args.good
    init_bad = args.bad if args.bad is not None else len(source)
    out = Path(args.out)

    history = _read_history(out)
    if history:
        print(f"resuming from {len(history)} prior attempt(s) in {out}", file=sys.stderr)
    good, bad = bounds_from_history(history, init_good, init_bad)

    while True:
        length = next_probe_length(good, bad, args.step)
        if length is None:
            break
        print(f"  probing length {length} (good={good}, bad={bad})...", file=sys.stderr)
        rec = _attempt(source, length, args.dtype, args.chunk_size)
        with out.open("a", encoding="utf-8") as fh:      # persist BEFORE the next fold
            fh.write(json.dumps(rec) + "\n")
        if rec["outcome"] == OK:
            good = length
        else:
            bad = length
        print(f"    -> {rec['outcome']}", file=sys.stderr)

    ceiling = ceiling_from_history(_read_history(out), init_good)
    print(f"\nA6000 single-fold ceiling: {ceiling} aa "
          f"(largest proven-foldable; next failing length ~{bad}). Log: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
