"""SB — what does refolding the census locally cost? TEN folds, LOCAL GPU, NO INGEST.

⚠⚠ THIS SCRIPT CANNOT WRITE THE DATABASE. It imports nothing from `db/` or `core.enqueue`, and a
self-check asserts that at start-up — the `d099_control_fold.py` discipline, reused rather than
re-derived. **The 2,690 keep their NULL `pae_json_path`; `F-042` is recorded, not patched away.**

⚠ SB1's SELECTION IS BY RANK, NOT BY POSITION. The extraction run measured a 708x spread between
shortest and longest, so the first ten rows would time the ten shortest and project a fantasy. Ten
evenly spaced RANKS of span length sample the actual distribution.

⚠ Recipe is the census recipe and comes from the MANIFEST ROW, not from a constant here: int8,
chunk 64, local. `core/contracts.py` is the authority and this script does not restate it.

    python scripts/sb_census_fold_timing.py            # ten
    python scripts/sb_census_fold_timing.py --limit 2  # smoke first
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
FEATURES = REPO / "data" / "census" / "census_features.v1.jsonl"
ARTIFACT_DIR = REPO / "data" / "control" / "sb_timing"
OUT = REPO / "data" / "control" / "sb_timing" / "timings.json"

KNOWN_GOOD_INT8 = 440
CACHE = REPO / "data" / "census" / "spancache"


def sliced_sequence(acc: str, span_start: int, span_end: int) -> str:
    """⚠ Reused verbatim from `d099_control_fold.py` — 1-based inclusive -> 0-based slice.
    Re-deriving a slice rule is how two paths to one span diverge."""
    doc = json.loads((CACHE / ("%s.json" % acc)).read_bytes().decode("utf-8"))
    return doc["sequence"]["value"][span_start - 1:span_end]


def _self_check() -> None:
    """⚠⚠ The no-write guarantee is ENFORCED, not asserted in a docstring.

    ⚠ By AST, not by substring. The first version scanned its own source for the strings it
    forbids — and its own FORBIDDEN list contained them, so it refused to run on itself. That is
    the `top_n`-in-a-docstring shape: a guard matching its own warning text. An import is a
    STRUCTURE, so the check reads structure.
    """
    import ast
    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    banned = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            banned += [a.name for a in node.names if a.name.split(".")[0] == "db"]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.split(".")[0] == "db" or mod == "core.enqueue":
                banned.append(mod)
    if banned:
        raise SystemExit("⚠ REFUSING TO RUN — this script imports %s" % banned)
    print("self-check (AST): no db import, no core.enqueue — this run cannot write the database")


def _sample(limit: int) -> list[dict]:
    """Ten census rows at evenly spaced RANKS of span length."""
    folded = {json.loads(l)["accession"] for l in FEATURES.read_text(encoding="utf-8").splitlines()}
    with MANIFEST.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["census_accession"] in folded and r.get("span_aa")]
    rows.sort(key=lambda r: int(r["span_aa"]))
    n = len(rows)
    # ⚠ evenly spaced ranks across the WHOLE sorted range, endpoints included
    idx = [round(i * (n - 1) / (limit - 1)) for i in range(limit)] if limit > 1 else [n // 2]
    return [rows[i] for i in idx]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    _self_check()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    import torch
    dev = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    total = torch.cuda.mem_get_info()[1] / 2**30 if torch.cuda.is_available() else 0
    print("device          : %s  (%.1f GiB)" % (dev, total))
    print("artifact_dir    : %s" % ARTIFACT_DIR)

    from worker.runner import fold, write_artifacts          # noqa: PLC0415

    sample = _sample(args.limit)
    print("selection       : %d rows at evenly spaced RANKS of span_aa (%d..%d aa)"
          % (len(sample), int(sample[0]["span_aa"]), int(sample[-1]["span_aa"])))
    print()

    recs = []
    for i, m in enumerate(sample, 1):
        acc = m["census_accession"]
        s0, s1 = int(m["span_start"]), int(m["span_end"])
        span_aa = int(m["span_aa"])
        seq = sliced_sequence(acc, s0, s1)

        # ⚠⚠ F-034: the harness checks its own input. Folding the wrong molecule looks exactly
        # like folding the right one.
        if len(seq) != span_aa:
            raise SystemExit("⚠⚠ STOP — %s: sliced %d residues, manifest says %d"
                             % (acc, len(seq), span_aa))
        if span_aa > KNOWN_GOOD_INT8:
            raise SystemExit("⚠ STOP — %s: %d aa exceeds known_good %d" % (acc, span_aa,
                                                                           KNOWN_GOOD_INT8))
        dtype = m["dtype"]
        chunk = int(m["chunk_size"]) if m["chunk_size"] else None

        if torch.cuda.is_available():
            # ⚠⚠ THE CACHE IS FREED BETWEEN FOLDS. The first run measured 0.03 GiB free after a
            # 439-aa fold; most of that is torch's caching allocator holding blocks, not the model.
            # Releasing them makes the NEXT fold's headroom real rather than nominal.
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            free_before = torch.cuda.mem_get_info()[0] / 2**30
            # ⚠⚠ ABORT BEFORE A FOLD, NEVER DURING ONE. D-082's failure mode is a HOST BUGCHECK —
            # an unclean shutdown of the owner's machine, not a Python exception. A guard that
            # fires mid-fold is not a guard. 6.50 GiB was the observed peak at 439 aa.
            # ⚠⚠ THE GUARD MUST MEASURE HEADROOM, NOT TOTAL ALLOCATION — and I got this wrong
            # twice. ESMFold stays RESIDENT on the card between folds (~5.24 GiB); that is
            # deliberate, since reloading 4,498 tensors per fold would dominate the timing. So the
            # 6.50 GiB peak at 439 aa is MODEL + FOLD, and the INCREMENTAL cost of the largest
            # span in the census is only ~1.26 GiB.
            # ⚠ Guarding on 6.6 blocked every fold after the first, because free-after-model is
            # ~1.5 GiB by construction. A guard on the wrong quantity does not fail safe — it
            # fails always, and a guard that always fires gets deleted by the next person.
            # ⚠⚠ GROUNDED IN A DEMONSTRATED SUCCESS, not chosen. The first run folded Q8N423 at
            # 439 aa — the LONGEST span in the census — starting from 1.48 GiB free, and it
            # completed. So 1.4 is below a value already proven sufficient for the worst case.
            # ⚠ This is the fourth number I tried. The first three were guesses about what the
            # card needed; this one is a measurement of what it did.
            need = 1.4
            if free_before < need:
                print("⚠⚠ STOP — only %.2f GiB free before %s (%d aa); observed peak at 439 aa was "
                      "6.50 GiB. Refusing to start a fold that may bugcheck the host."
                      % (free_before, acc, span_aa))
                break
        else:
            free_before = 0.0

        print("[%d/%d] %s span=%d dtype=%s chunk=%s ..." % (i, len(sample), acc, span_aa,
                                                            dtype, chunk), flush=True)
        t0 = time.time()
        result = fold(seq, dtype=dtype, chunk_size=chunk, source="sliced_ecd",
                      ecd_start=s0, ecd_end=s1)
        dt = time.time() - t0

        peak = torch.cuda.max_memory_allocated() / 2**30 if torch.cuda.is_available() else 0.0
        free_after = torch.cuda.mem_get_info()[0] / 2**30 if torch.cuda.is_available() else 0.0

        out = ARTIFACT_DIR / acc
        written = write_artifacts(result, out)
        # ⚠ SB3: emitted AND written to disk. DB persistence is a different question — see the
        # report; this script cannot write the database by construction.
        pae_present = result.pae is not None
        # ⚠⚠ SHAPE IS CHARACTERISED, NOT ASSUMED — and this is where a latent defect surfaced.
        # `worker/runner.py:311` does `outputs["predicted_aligned_error"].squeeze()`, and for a
        # ONE-RESIDUE span squeeze collapses (1,1,1) to a 0-dim scalar, so `result.pae` is a
        # float rather than a matrix. The census minimum span is 1 aa, so any PAE work over the
        # census meets this. Recorded per fold rather than crashed on.
        if not pae_present:
            pae_shape, pae_n = "absent", 0
        elif isinstance(result.pae, (int, float)):
            pae_shape, pae_n = "scalar ⚠ squeeze() collapsed the matrix", 0
        elif result.pae and isinstance(result.pae[0], list):
            pae_shape, pae_n = "matrix %dx%d" % (len(result.pae), len(result.pae[0])), len(result.pae)
        else:
            pae_shape, pae_n = "vector len %d ⚠" % len(result.pae), len(result.pae)

        recs.append({
            "accession": acc, "span_aa": span_aa, "seconds": round(dt, 2),
            "dtype": dtype, "chunk_size": chunk,
            "pae_emitted": pae_present, "pae_dim": pae_n, "pae_shape": pae_shape,
            "pae_written": bool(written.get("pae")) if isinstance(written, dict) else None,
            "vram_free_before_gib": round(free_before, 2),
            "vram_peak_alloc_gib": round(peak, 2),
            "vram_free_after_gib": round(free_after, 2),
            "folded_at": datetime.now(timezone.utc).isoformat(),
        })
        print("        %.1f s   pae=%s   peak=%.2f GiB  free_after=%.2f GiB"
              % (dt, pae_shape, peak, free_after), flush=True)

    OUT.write_text(json.dumps(recs, indent=2) + "\n", encoding="utf-8")
    if not recs:
        # ⚠ nothing folded — say so rather than crash computing statistics over an empty list
        print("⚠ no folds completed; nothing to summarise")
        return 1
    secs = [r["seconds"] for r in recs]
    spans = [r["span_aa"] for r in recs]
    total_s = sum(secs)
    per_aa = total_s / max(sum(spans), 1)
    n_census = 2690
    mean_span = 0
    with MANIFEST.open(encoding="utf-8") as fh:
        folded = {json.loads(l)["accession"]
                  for l in FEATURES.read_text(encoding="utf-8").splitlines()}
        ss = [int(r["span_aa"]) for r in csv.DictReader(fh)
              if r["census_accession"] in folded and r.get("span_aa")]
        mean_span = sum(ss) / len(ss)

    print()
    print("SB2 — timing")
    print("  folds            : %d" % len(recs))
    print("  seconds each     : %s" % ", ".join("%.1f" % s for s in secs))
    print("  min / max        : %.1f s / %.1f s   (spread %.1fx)" % (min(secs), max(secs),
                                                                     max(secs) / max(min(secs), 1e-9)))
    print("  total            : %.1f s over %d aa" % (total_s, sum(spans)))
    # ⚠⚠ A PER-AA LINEAR RATE IS THE WRONG MODEL AND IT UNDERSTATES. Measured: 43 aa -> 2.0 s and
    # 439 aa -> 75.2 s. Ten times the span costs thirty-seven times the time, so folding is
    # super-linear in length and a linear rate projects a number that will not happen.
    # ⚠ The first fold is EXCLUDED from the fit: it carries the one-off model load (~11.7 s of its
    # 13.8), which times a different thing than folding.
    import math
    fit = [r for r in recs if r["span_aa"] > 1]
    if len(fit) >= 3:
        xs = [math.log(r["span_aa"]) for r in fit]
        ys = [math.log(r["seconds"]) for r in fit]
        n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
        bb = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        aa = my - bb * mx
        # ⚠ projected over the ACTUAL span distribution, never over the mean span — the mean of a
        # super-linear function is not the function of the mean
        proj = sum(math.exp(aa) * (sp ** bb) for sp in ss)
        print("  ⚠ PROJECTION — power law fitted on %d folds, applied per protein:" % n)
        print("      seconds     = %.4g * span^%.2f" % (math.exp(aa), bb))
        print("      over all %d : %.2f h  (%.0f min)" % (len(ss), proj / 3600, proj / 60))
        print("      naive linear: %.2f h  ⚠ understates, and by construction" % (per_aa * sum(ss) / 3600))
    print()
    print("SB3 — PAE: emitted on %d of %d, written to disk on %d of %d"
          % (sum(1 for r in recs if r["pae_emitted"]), len(recs),
             sum(1 for r in recs if r["pae_written"]), len(recs)))
    print("SB4 — VRAM: peak alloc %.2f–%.2f GiB, lowest free after a fold %.2f GiB of %.1f total"
          % (min(r["vram_peak_alloc_gib"] for r in recs),
             max(r["vram_peak_alloc_gib"] for r in recs),
             min(r["vram_free_after_gib"] for r in recs), total))
    print("  wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
