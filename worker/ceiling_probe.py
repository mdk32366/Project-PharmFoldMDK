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

# ── D-077 decision 4: the repeat rule ────────────────────────────────────────
#
# ⚠ WHY THIS LAYER EXISTS. Everything below the repeat layer assumes a SHARP,
# MONOTONE boundary and cannot report that it isn't one: `bounds_from_history`
# raises the floor on ANY SINGLE `ok` and lowers the ceiling on ANY SINGLE
# failure, and `next_probe_length` then raises `ValueError` when `bad <= good`.
# So a history like `ok@560, oom@500` — entirely plausible 378 MiB from the wall
# on the local card — makes the probe CRASH rather than report the flakiness. The
# instrument had no vocabulary for "the boundary is a band."
#
# That is NOT logged as a defect. It was correct for the A6000, which sits far
# from its wall (D-022). It is a design assumption that is not obviously correct
# for a card with 378 MiB of headroom, so D-077 dec 4 recorded — before any probe
# ran — that a `ValueError` during the run is to be read as A RESULT, not a bug,
# and added this layer so the result is REPORTABLE instead of fatal.
#
# k = 4 is INHERITED, not tuned: 630 aa was ruled fatal on 4-for-4
# (ARCHITECTURE.md:598-599). A future session that changes k is amending a frozen
# pre-registration and needs a new dated entry.
K_REPEAT = 4
REPEAT_STEP = 8            # D-077 dec 4 stopping rule: stop when bad - good <= 8

OK = "ok"
OOM = "oom"
ERROR = "error"

# D-077 dec 4 verdicts. `UNSTABLE` is a PRE-REGISTERED, LEGITIMATE, REPORTABLE
# outcome — not an error state. Arm A may return it at every probed length and
# that is a measurement, not a broken run.
GOOD = "good"
BAD = "bad"
UNSTABLE = "unstable"
INSUFFICIENT = "insufficient"


# ── recipe resolution (D-077 decision 3) ─────────────────────────────────────

def recipe_for_tier(tier: str, dtype: Optional[str] = None,
                    chunk_size: Optional[int] = None) -> dict:
    """Resolve the fold recipe for `tier` from `TIER_RECIPE`, refusing contradictions.

    D-077 dec 3, applied from D-047's principle: the recipe is RESOLVED, never
    passed by hand. This module's `--dtype` historically defaulted to fp16 because
    it was written for the A6000 (D-022), and a local run that forgot
    `--dtype int8` would measure a ceiling for a recipe the local tier does not
    use — which would then be written into the constant routing int8 production
    folds. Two paths to one quantity, free to drift.

    A caller may RESTATE the tier's own values (harmless, and useful in a logged
    command line). Anything else raises: the probe would otherwise silently
    measure something the routing constant must not be updated from.
    """
    from core.contracts import TIER_RECIPE  # noqa: PLC0415 — stdlib-only serving leaf

    if tier not in TIER_RECIPE:
        raise ValueError(f"unknown tier {tier!r}; known tiers are {sorted(TIER_RECIPE)}")

    recipe = dict(TIER_RECIPE[tier])
    if dtype is not None and dtype != recipe["dtype"]:
        raise ValueError(
            f"--dtype {dtype!r} contradicts tier {tier!r}, which folds at "
            f"{recipe['dtype']!r}. A ceiling measured under any other recipe may not "
            f"update the routing constant (D-077 dec 3)."
        )
    if chunk_size is not None and chunk_size != recipe["chunk_size"]:
        raise ValueError(
            f"--chunk-size {chunk_size!r} contradicts tier {tier!r}, which folds at "
            f"chunk {recipe['chunk_size']!r} (D-077 dec 3)."
        )
    return recipe


# ── the repeat layer (D-077 decision 4) ──────────────────────────────────────

def _outcomes_at(history: list[dict], length: int) -> list[str]:
    """Outcomes recorded at one length, in order. Malformed rows ignored — the log
    is append-only and a torn final line from a crash must not manufacture or
    destroy a verdict."""
    return [
        row["outcome"] for row in history
        if isinstance(row.get("length"), int)
        and row["length"] == length
        and row.get("outcome") in (OK, OOM, ERROR)
    ]


def _has_run_of(outcomes: list[str], predicate, k: int) -> bool:
    run = 0
    for o in outcomes:
        run = run + 1 if predicate(o) else 0
        if run >= k:
            return True
    return False


def verdict_at_length(history: list[dict], length: int, k: int = K_REPEAT) -> str:
    """The D-077 dec 4 verdict at one length: good / bad / unstable / insufficient.

    - `good`   — k consecutive clean folds AND nothing has ever failed here.
    - `bad`    — k consecutive failures AND nothing has ever folded here.
    - `unstable` — both kinds seen. The boundary is a BAND at this length.
    - `insufficient` — not enough evidence yet either way.

    ⚠ The "and nothing has ever" halves are load-bearing. `ok, ok, ok, ok, oom` is
    a real run of four followed by a real failure; treating it as `good` would let
    a single lucky streak raise the routing constant on a card that then crashes a
    host. The conservative reading wins, which is the entire purpose of k.
    """
    outcomes = _outcomes_at(history, length)
    if not outcomes:
        return INSUFFICIENT

    any_ok = any(o == OK for o in outcomes)
    any_fail = any(o != OK for o in outcomes)

    if any_ok and any_fail:
        return UNSTABLE
    if any_ok and _has_run_of(outcomes, lambda o: o == OK, k):
        return GOOD
    if any_fail and _has_run_of(outcomes, lambda o: o != OK, k):
        return BAD
    return INSUFFICIENT


def unstable_lengths(history: list[dict], k: int = K_REPEAT) -> list[int]:
    """Every length whose verdict is `unstable`, ascending. Reported, not hidden."""
    lengths = {row["length"] for row in history if isinstance(row.get("length"), int)}
    return sorted(L for L in lengths if verdict_at_length(history, L, k) == UNSTABLE)


def repeat_bounds_from_history(history: list[dict], init_good: int, init_bad: int,
                               k: int = K_REPEAT) -> tuple[int, int]:
    """Bounds under the repeat rule — the function the probe loop actually uses.

    Only a `good` verdict raises the floor; only a `bad` verdict lowers the
    ceiling. An `unstable` or `insufficient` length moves NEITHER, which is what
    keeps a non-monotone history from ever reaching `next_probe_length` with
    inverted bounds.

    `bounds_from_history` is deliberately left alone as the raw k=1 reconstruction
    (D-077 dec 4 does not log its behaviour as a defect); this is a layer ABOVE
    it, not a replacement. Deterministic on a fixed history, as dec 4 requires.
    """
    good, bad = init_good, init_bad
    lengths = sorted({row["length"] for row in history if isinstance(row.get("length"), int)})
    for length in lengths:
        verdict = verdict_at_length(history, length, k)
        if verdict == GOOD:
            good = max(good, length)
        elif verdict == BAD:
            bad = min(bad, length)
    return good, bad


def ceiling_band(history: list[dict], init_good: int, init_bad: int,
                 k: int = K_REPEAT) -> tuple[int, int]:
    """The measured ceiling as `(highest 4-for-4 good, lowest 4-for-4 bad)`.

    When the two ends meet the boundary was sharp and the band is degenerate; when
    they do not, the ceiling IS a band and **routing uses the conservative (low)
    end** — `core.manifest.FoldCeiling.unstable_band` carries it, and
    `tier_for_span` reads the low end.
    """
    return repeat_bounds_from_history(history, init_good, init_bad, k)


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
    ap.add_argument("--dtype", default=None,
                    help="fold precision; OMIT with --tier so the recipe is resolved, "
                         "not hand-passed (D-077 dec 3). Passing one that contradicts "
                         "the tier is refused. Defaults to fp16 for untiered A6000 runs.")
    ap.add_argument("--chunk-size", type=int, default=None)
    ap.add_argument("--tier", default=None, choices=("local", "rental"),
                    help="resolve dtype/chunk_size from TIER_RECIPE for this tier. "
                         "REQUIRED for any run whose number may update a routing constant.")
    ap.add_argument("--repeat", type=int, default=None,
                    help=f"k consecutive folds required for a verdict (D-077 dec 4 freezes "
                         f"k={K_REPEAT} for tiered runs; changing it needs a new entry)")
    ap.add_argument("--out", default="a6000_ceiling.jsonl", help="append-only results log (also the resume file)")
    args = ap.parse_args(argv)

    # ── D-077 dec 3: the recipe is resolved from the tier table, never hand-passed.
    # Without --tier this stays the D-022 A6000 probe with its fp16 default, so no
    # existing invocation changes; WITH --tier the recipe is authoritative and a
    # contradicting flag raises rather than silently measuring the wrong thing.
    if args.tier:
        recipe = recipe_for_tier(args.tier, dtype=args.dtype, chunk_size=args.chunk_size)
        dtype, chunk_size = recipe["dtype"], recipe["chunk_size"]
        k = args.repeat if args.repeat is not None else K_REPEAT
        step = args.step if args.step != DEFAULT_STEP else REPEAT_STEP
    else:
        dtype = args.dtype if args.dtype is not None else "fp16"
        chunk_size = args.chunk_size
        k = args.repeat if args.repeat is not None else 1
        step = args.step

    source = _read_source(args)
    init_good = args.good
    init_bad = args.bad if args.bad is not None else len(source)
    out = Path(args.out)

    # ⚠ Bounds and recipe are stated BEFORE the first fold (order §3), so the line
    # that opens a run names what it measured — a ceiling whose recipe is unknown
    # after the fact may not update anything.
    print(f"probe: tier={args.tier or 'untiered (D-022 A6000 default)'} "
          f"dtype={dtype} chunk_size={chunk_size} k={k} step={step} "
          f"bounds=({init_good}, {init_bad})", file=sys.stderr)

    history = _read_history(out)
    if history:
        print(f"resuming from {len(history)} prior attempt(s) in {out}", file=sys.stderr)
    good, bad = repeat_bounds_from_history(history, init_good, init_bad, k)

    while True:
        length = next_probe_length(good, bad, step)
        if length is None:
            break
        # k attempts at this length before the bounds move at all. With k=1 this is
        # the original single-shot behaviour, so untiered runs are unchanged.
        for attempt in range(k):
            print(f"  probing length {length} ({attempt + 1}/{k}) (good={good}, bad={bad})...",
                  file=sys.stderr)
            rec = _attempt(source, length, dtype, chunk_size)
            with out.open("a", encoding="utf-8") as fh:  # persist BEFORE the next fold
                fh.write(json.dumps(rec) + "\n")
            history.append(rec)
            print(f"    -> {rec['outcome']}", file=sys.stderr)
            # An unstable length is already decided; stop burning folds on it.
            if verdict_at_length(history, length, k) == UNSTABLE:
                print(f"    -> UNSTABLE at {length} (D-077 dec 4: a result, not a bug)",
                      file=sys.stderr)
                break

        moved_good, moved_bad = repeat_bounds_from_history(history, init_good, init_bad, k)
        if (moved_good, moved_bad) == (good, bad):
            # Neither bound moved — the length was unstable or inconclusive, and
            # bisecting again would re-probe it forever. Stop and report the band.
            print(f"  bounds did not move at {length}; stopping (the band is the result)",
                  file=sys.stderr)
            break
        good, bad = moved_good, moved_bad

    history = _read_history(out)
    band_low, band_high = ceiling_band(history, init_good, init_bad, k)
    unstable = unstable_lengths(history, k)

    label = args.tier or "A6000"
    if unstable or band_low != ceiling_from_history(history, init_good):
        print(f"\n{label} single-fold ceiling is a BAND: ({band_low}, {band_high}) aa "
              f"at dtype={dtype}, chunk_size={chunk_size}, k={k}. "
              f"Routing uses the low end. Unstable lengths: {unstable or 'none'}. Log: {out}")
    else:
        print(f"\n{label} single-fold ceiling: {band_low} aa "
              f"at dtype={dtype}, chunk_size={chunk_size}, k={k} "
              f"(next failing length ~{band_high}). Log: {out}")
    print("⚠ This number does NOT update core.manifest.LOCAL_CEILING. The constant "
          "moves in the same PR as the F-entry that measured it, or not at all (D-077).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
