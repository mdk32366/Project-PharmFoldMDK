#!/usr/bin/env python3
"""D-128-A — linker / seam honesty CLI limited to the Spec's 27 parent ids.

    python -m scripts.linker_seam_restitch --manifest tiles.json --out-root /ops \\
        [--assembler-dir /ops/2817] [--d125-dir /ops/kabsch/2817] \\
        [--d126-dir /ops/confidence_kabsch/2817] \\
        [--d127-dir /ops/piecewise_kabsch/2817]

    python -m scripts.linker_seam_restitch --honesty-report \\
        --out-root /ops --parent-id 2939

    python -m scripts.linker_seam_restitch --confusion-report \\
        --d125-outcomes d125.json --d126-outcomes d126.json \\
        --d127-outcomes d127.json --d128-outcomes d128.json

Not a live Fly re-query. Not a fold. Not F-004 ingest. Not D-128-B UI or
Method. Not a restitch run of the 27. A parent id outside the 27 is
refused. Artifacts land under ``<out-root>/linker_seam/<parent_job_id>/``
and never overwrite assembler ``stitched.pdb``, D-125 ``kabsch/``, D-126
``confidence_kabsch/``, or D-127 ``piecewise_kabsch/`` — those trees are
**read** for the §1a honesty rows.

Primary evaluation is the **seven** signed must-hunt linker parents
(2938, 2939, 3179, 3190, 3321, 3368, 3566). They are the inventory, not
a named-exclusion. **3272 / 3394 / 3432 may be run and recorded but are
not success targets**, and **3432 stays accept-refuse** (signed triage):
it is never counted as a D-128 miss. **0-of-7 repaired is an allowed
outcome** — the honesty rows are the deliverable. The 10.0 Å gate stays.
Seams are recorded, not solved.

Manifest shape matches ``scripts/kabsch_restitch.py`` (D-125-A)::

    {
      "parent_job_id": 2817,
      "length": 20,
      "tile_job_ids": [3673, 3630],
      "tiles": [
        {"pdb": "tile1.pdb", "plddt": "tile1_plddt.json", "pae": "tile1_pae.json",
         "start": 1, "end": 12}
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.hold48_linker_seam import (  # noqa: E402
    ALGORITHM,
    DECISION,
    HONESTY_PATHS,
    LINKER_SEAM_RESTITCH_PARENT_IDS,
    NOT_SUCCESS_TARGET_PARENT_IDS,
    SEAM_HONESTY_GATE_ANGSTROM,
    SEVEN_LINKER_PARENT_IDS,
    WEIGHT_EPSILON,
    WINDOW_HALF_WIDTH_AA,
    InventoryRefused,
    SiblingOverwriteRefused,
    build_ops_success_report,
    read_path_seam_honesty,
    write_linker_seam_restitch,
)
from scripts.kabsch_restitch import load_manifest  # noqa: E402


def _load_outcome_map(path: Path) -> dict[int, bool]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "outcomes" in raw:
        raw = raw["outcomes"]
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be an object of parent_id → accepted")
    out: dict[int, bool] = {}
    for key, val in raw.items():
        out[int(key)] = bool(val.get("accepted")) if isinstance(val, dict) else bool(val)
    return out


def _load_repair_map(path: Path) -> dict[int, bool] | None:
    """``repaired`` is only claimed where a record says a window actually moved."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "outcomes" in raw:
        raw = raw["outcomes"]
    if not isinstance(raw, dict):
        return None
    out: dict[int, bool] = {}
    seen = False
    for key, val in raw.items():
        if isinstance(val, dict) and "repaired" in val:
            seen = True
            out[int(key)] = bool(val["repaired"])
    return out if seen else None


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m scripts.linker_seam_restitch",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--manifest", type=Path, default=None,
                    help="Local tile inventory JSON (not a Fly query)")
    ap.add_argument("--out-root", type=Path, default=None,
                    help="Ops root; writes linker_seam/<parent_job_id>/ under this path")
    ap.add_argument("--assembler-dir", type=Path, default=None,
                    help="Existing assembler artifact dir — refused as a write target")
    ap.add_argument("--d125-dir", type=Path, default=None,
                    help="Existing D-125 kabsch/ dir — refused as a write target")
    ap.add_argument("--d126-dir", type=Path, default=None,
                    help="Existing D-126 confidence_kabsch/ dir — refused as a write target")
    ap.add_argument("--d127-dir", type=Path, default=None,
                    help="Existing D-127 piecewise_kabsch/ dir — refused as a write target")
    ap.add_argument("--parent-id", type=int, default=None,
                    help="Must match the manifest and the 27-id inventory")
    ap.add_argument("--honesty-report", action="store_true",
                    help="Print §1a per-path / per-seam honesty rows read from disk (no fit, no write)")
    ap.add_argument("--confusion-report", action="store_true",
                    help="Emit ops confusion vs D-125 / D-126 / D-127 from outcome JSON (not a live restitch)")
    ap.add_argument("--d125-outcomes", type=Path, default=None,
                    help="JSON map of parent_id → accepted (D-125)")
    ap.add_argument("--d126-outcomes", type=Path, default=None,
                    help="JSON map of parent_id → accepted (D-126)")
    ap.add_argument("--d127-outcomes", type=Path, default=None,
                    help="JSON map of parent_id → accepted (D-127)")
    ap.add_argument("--d128-outcomes", type=Path, default=None,
                    help="JSON map of parent_id → accepted (and optionally repaired) (D-128)")
    ap.add_argument("--honesty-rows", type=Path, default=None,
                    help="Optional seam_honesty.jsonl to count dishonest / unknown seams from")
    return ap


def _banner(parent_job_id: int | None) -> None:
    print(
        f"{DECISION} {ALGORITHM} inventory_n={len(LINKER_SEAM_RESTITCH_PARENT_IDS)} "
        f"seven={sorted(SEVEN_LINKER_PARENT_IDS)} "
        f"not_success_targets={sorted(NOT_SUCCESS_TARGET_PARENT_IDS)} "
        f"W={WINDOW_HALF_WIDTH_AA} epsilon={WEIGHT_EPSILON} "
        f"gate={SEAM_HONESTY_GATE_ANGSTROM} no_trim_loop=True "
        f"parent={parent_job_id}  "
        f"# not a Fly re-query; not a named-exclusion; seams recorded, not solved",
        file=sys.stderr,
    )


def _honesty_report(out_root: Path, parent_job_id: int) -> int:
    rows = []
    for path_name in HONESTY_PATHS:
        rows.extend(
            row.to_json_row() for row in read_path_seam_honesty(out_root, parent_job_id, path_name)
        )
    print(json.dumps({"parent_job_id": parent_job_id, "seam_honesty": rows}, indent=2))
    dishonest = [r for r in rows if r["honest"] is False]
    unknown = [r for r in rows if r["honest"] is None]
    for row in dishonest:
        print(
            f"dishonest seam: path={row['path']} tile{row['moving_tile_index']} "
            f"max_ca_jump={row['max_ca_jump_angstrom']} Å "
            f"(> {SEAM_HONESTY_GATE_ANGSTROM} Å — no success PDB is honest for this seam)",
            file=sys.stderr,
        )
    for row in unknown:
        print(
            f"unknown seam: path={row['path']} tile{row['moving_tile_index']} "
            f"reason={row['absence_reason']} (unknown is not honest; null is not 0.0)",
            file=sys.stderr,
        )
    return 0


def _confusion_report(args: argparse.Namespace) -> int:
    missing = [
        name
        for name, val in (
            ("--d125-outcomes", args.d125_outcomes),
            ("--d126-outcomes", args.d126_outcomes),
            ("--d127-outcomes", args.d127_outcomes),
            ("--d128-outcomes", args.d128_outcomes),
        )
        if val is None
    ]
    if missing:
        print(
            "refuse: --confusion-report needs --d125-outcomes, --d126-outcomes, "
            "--d127-outcomes, and --d128-outcomes",
            file=sys.stderr,
        )
        return 2
    try:
        d125 = _load_outcome_map(args.d125_outcomes)
        d126 = _load_outcome_map(args.d126_outcomes)
        d127 = _load_outcome_map(args.d127_outcomes)
        d128 = _load_outcome_map(args.d128_outcomes)
        repaired = _load_repair_map(args.d128_outcomes)
        rows = []
        if args.honesty_rows is not None:
            rows = [
                json.loads(line)
                for line in args.honesty_rows.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"refuse: cannot read outcomes: {exc}", file=sys.stderr)
        return 2
    report = build_ops_success_report(
        d125, d126, d127, d128, d128_repaired=repaired, honesty_rows=rows
    )
    print(json.dumps(report.to_json(), indent=2))
    for label, value in (
        ("n_d125_pass_d128_refuse", report.n_d125_pass_d128_refuse),
        ("n_d126_pass_d128_refuse", report.n_d126_pass_d128_refuse),
        ("n_d127_pass_d128_refuse", report.n_d127_pass_d128_refuse),
    ):
        if value:
            print(
                f"named finding: {label}={value} "
                f"(a drop on a prior path's PASS set is not silent success)",
                file=sys.stderr,
            )
    print(
        f"repaired_of_seven={report.repaired_of_seven} "
        f"(source={report.repaired_of_seven_source}; 0-of-7 is an allowed outcome; "
        f"gate stays {SEAM_HONESTY_GATE_ANGSTROM} Å; seams recorded, not solved)",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.confusion_report:
        return _confusion_report(args)

    if args.honesty_report:
        if args.out_root is None or args.parent_id is None:
            print("refuse: --honesty-report needs --out-root and --parent-id", file=sys.stderr)
            return 2
        if args.parent_id not in LINKER_SEAM_RESTITCH_PARENT_IDS:
            print(
                f"refuse: parent_job_id {args.parent_id} is not in the 27-id inventory",
                file=sys.stderr,
            )
            return 2
        _banner(args.parent_id)
        return _honesty_report(args.out_root, args.parent_id)

    if args.manifest is None or args.out_root is None:
        print(
            "refuse: --manifest and --out-root are required "
            "(or --honesty-report / --confusion-report)",
            file=sys.stderr,
        )
        return 2
    try:
        parent_job_id, length, tile_job_ids, tiles = load_manifest(args.manifest)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"refuse: cannot read manifest: {exc}", file=sys.stderr)
        return 2
    if args.parent_id is not None and args.parent_id != parent_job_id:
        print(
            f"refuse: --parent-id {args.parent_id} != manifest parent_job_id {parent_job_id}",
            file=sys.stderr,
        )
        return 2
    _banner(parent_job_id)
    if parent_job_id in NOT_SUCCESS_TARGET_PARENT_IDS:
        print(
            f"note: parent {parent_job_id} is recorded, not a success target of this Spec "
            f"(3272 / 3394 are the rmsd_gt_10 class; 3432 stays accept-refuse and is not a "
            f"D-128 miss)",
            file=sys.stderr,
        )
    try:
        result = write_linker_seam_restitch(
            tiles,
            length,
            args.out_root,
            parent_job_id=parent_job_id,
            tile_job_ids=tile_job_ids,
            assembler_dir=args.assembler_dir,
            d125_dir=args.d125_dir,
            d126_dir=args.d126_dir,
            d127_dir=args.d127_dir,
        )
    except InventoryRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    except SiblingOverwriteRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2

    print(
        f"accepted={result.accepted} repaired={result.repaired} out={result.out_dir} "
        f"seams={len(result.seams)} honesty_rows={len(result.honesty)}",
        file=sys.stderr,
    )
    for seam in result.seams:
        print(
            f"  seam tile{seam.moving_tile_index}: source={seam.offending_seam_source} "
            f"window=[{seam.window_start},{seam.window_end}] W={WINDOW_HALF_WIDTH_AA} "
            f"n_ca={seam.n_ca} rmsd={seam.rmsd_angstrom} "
            f"max_ca_jump={seam.max_ca_jump_angstrom} refuse={seam.refuse_reason}",
            file=sys.stderr,
        )
    for row in result.honesty:
        state = "honest" if row.honest else ("dishonest" if row.honest is False else "unknown")
        print(
            f"  honesty {row.path} tile{row.moving_tile_index}: "
            f"max_ca_jump={row.max_ca_jump_angstrom} {state} "
            f"source={row.source} absence={row.absence_reason}",
            file=sys.stderr,
        )
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
