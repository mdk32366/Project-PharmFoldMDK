#!/usr/bin/env python3
"""D-127-A — piecewise / domain-aware Kabsch CLI limited to the Spec's 27 parent ids.

    python -m scripts.piecewise_kabsch_restitch --manifest tiles.json --out-root /ops \\
        [--assembler-dir /ops/2817] [--d125-dir /ops/kabsch/2817] \\
        [--d126-dir /ops/confidence_kabsch/2817]

    python -m scripts.piecewise_kabsch_restitch --confusion-report \\
        --d125-outcomes d125.json --d126-outcomes d126.json --d127-outcomes d127.json

Not a live Fly re-query. Not a fold. Not F-004 ingest. Not D-127-B UI.
Not a restitch run of the 27. A parent id outside the 27 is refused.
Artifacts land under ``<out-root>/piecewise_kabsch/<parent_job_id>/``
and never overwrite assembler ``stitched.pdb``, D-125 ``kabsch/``, or
D-126 ``confidence_kabsch/``.

The primary three (2939 / 3272 / 3432) are **not** skipped — they are
the evaluation inventory, not a named-exclusion. 0-of-3 recovered is
an allowed outcome. Confusion vs D-125 **and** vs D-126 is a required
**report** field, not a CI assert against live ops.

Manifest shape matches ``scripts/kabsch_restitch.py`` (D-125-A) plus
optional domain-snap fields (same emit source; not a second annotation)::

    {
      "parent_job_id": 2817,
      "length": 20,
      "tile_job_ids": [3673, 3630],
      "accession": "Q9P273",
      "span_start": 1,
      "span_end": 20,
      "domain_intervals": [[1, 10], [12, 20]],
      "tiles": [
        {"pdb": "tile1.pdb", "plddt": "tile1_plddt.json", "pae": "tile1_pae.json",
         "start": 1, "end": 12}
      ]
    }

``domain_intervals`` wins when present (hermetic). Else accession +
span read the same UniProt Domain/Repeat cache emit uses. A missing
cache is empty intervals (``no_domain_pieces``), not a fetch.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.hold48 import UNIPROT_CACHE  # noqa: E402
from core.hold48_piecewise_kabsch import (  # noqa: E402
    ALGORITHM,
    DECISION,
    PIECEWISE_RESTITCH_PARENT_IDS,
    PRIMARY_THREE_PARENT_IDS,
    RMSD_REFUSE_ANGSTROM,
    WEIGHT_EPSILON,
    InventoryRefused,
    SiblingOverwriteRefused,
    build_ops_success_report,
    write_piecewise_kabsch_restitch,
)
from scripts.kabsch_restitch import load_manifest  # noqa: E402


def _load_outcome_map(path: Path) -> dict[int, bool]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[int, bool] = {}
    if isinstance(raw, dict) and "outcomes" in raw:
        raw = raw["outcomes"]
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be an object of parent_id → accepted")
    for key, val in raw.items():
        pid = int(key)
        if isinstance(val, dict):
            out[pid] = bool(val.get("accepted"))
        else:
            out[pid] = bool(val)
    return out


def _domain_kwargs(manifest_path: Path) -> dict:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    kwargs: dict = {}
    if raw.get("domain_intervals") is not None:
        kwargs["domain_intervals"] = raw["domain_intervals"]
    if raw.get("accession") is not None:
        kwargs["accession"] = raw["accession"]
    if raw.get("span_start") is not None:
        kwargs["span_start"] = int(raw["span_start"])
    if raw.get("span_end") is not None:
        kwargs["span_end"] = int(raw["span_end"])
    if raw.get("cache_dir") is not None:
        kwargs["cache_dir"] = Path(raw["cache_dir"])
    else:
        kwargs["cache_dir"] = UNIPROT_CACHE
    return kwargs


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m scripts.piecewise_kabsch_restitch",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Local tile inventory JSON (not a Fly query)",
    )
    ap.add_argument(
        "--out-root",
        type=Path,
        default=None,
        help="Ops root; writes piecewise_kabsch/<parent_job_id>/ under this path",
    )
    ap.add_argument(
        "--assembler-dir",
        type=Path,
        default=None,
        help="Existing assembler artifact dir — refused as a write target",
    )
    ap.add_argument(
        "--d125-dir",
        type=Path,
        default=None,
        help="Existing D-125 kabsch/ dir — refused as a write target",
    )
    ap.add_argument(
        "--d126-dir",
        type=Path,
        default=None,
        help="Existing D-126 confidence_kabsch/ dir — refused as a write target",
    )
    ap.add_argument(
        "--parent-id",
        type=int,
        default=None,
        help="Must match the manifest and the 27-id inventory",
    )
    ap.add_argument(
        "--confusion-report",
        action="store_true",
        help="Emit ops confusion vs D-125 and vs D-126 from three outcome JSON files (not a live restitch)",
    )
    ap.add_argument(
        "--d125-outcomes",
        type=Path,
        default=None,
        help="JSON map of parent_id → accepted (D-125)",
    )
    ap.add_argument(
        "--d126-outcomes",
        type=Path,
        default=None,
        help="JSON map of parent_id → accepted (D-126)",
    )
    ap.add_argument(
        "--d127-outcomes",
        type=Path,
        default=None,
        help="JSON map of parent_id → accepted (D-127)",
    )
    return ap


def _print_confusion(
    d125: dict[int, bool],
    d126: dict[int, bool],
    d127: dict[int, bool],
) -> None:
    report = build_ops_success_report(d125, d126, d127)
    payload = report.to_json()
    print(json.dumps(payload, indent=2))
    if report.n_d125_pass_d127_refuse:
        print(
            f"named finding: n_d125_pass_d127_refuse={report.n_d125_pass_d127_refuse} "
            f"(a drop on the D-125 PASS set is not silent success)",
            file=sys.stderr,
        )
    if report.n_d126_pass_d127_refuse:
        print(
            f"named finding: n_d126_pass_d127_refuse={report.n_d126_pass_d127_refuse} "
            f"(a drop on the D-126 PASS set is not silent success)",
            file=sys.stderr,
        )
    print(
        f"recovered_of_primary_three={report.recovered_of_primary_three} "
        f"(0-of-3 is an allowed outcome; gate stays {RMSD_REFUSE_ANGSTROM} Å)",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.confusion_report:
        missing = [
            name
            for name, val in (
                ("--d125-outcomes", args.d125_outcomes),
                ("--d126-outcomes", args.d126_outcomes),
                ("--d127-outcomes", args.d127_outcomes),
            )
            if val is None
        ]
        if missing:
            print(
                "refuse: --confusion-report needs --d125-outcomes, --d126-outcomes, and --d127-outcomes",
                file=sys.stderr,
            )
            return 2
        try:
            d125 = _load_outcome_map(args.d125_outcomes)
            d126 = _load_outcome_map(args.d126_outcomes)
            d127 = _load_outcome_map(args.d127_outcomes)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"refuse: cannot read outcomes: {exc}", file=sys.stderr)
            return 2
        _print_confusion(d125, d126, d127)
        return 0

    if args.manifest is None or args.out_root is None:
        print("refuse: --manifest and --out-root are required (or --confusion-report)", file=sys.stderr)
        return 2
    try:
        parent_job_id, length, tile_job_ids, tiles = load_manifest(args.manifest)
        domain_kwargs = _domain_kwargs(args.manifest)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"refuse: cannot read manifest: {exc}", file=sys.stderr)
        return 2
    if args.parent_id is not None and args.parent_id != parent_job_id:
        print(
            f"refuse: --parent-id {args.parent_id} != manifest parent_job_id {parent_job_id}",
            file=sys.stderr,
        )
        return 2
    print(
        f"{DECISION} {ALGORITHM} inventory_n={len(PIECEWISE_RESTITCH_PARENT_IDS)} "
        f"primary_three={sorted(PRIMARY_THREE_PARENT_IDS)} "
        f"epsilon={WEIGHT_EPSILON} gate={RMSD_REFUSE_ANGSTROM} "
        f"no_trim_loop=True parent={parent_job_id}  "
        f"# not a Fly re-query; not a named-exclusion",
        file=sys.stderr,
    )
    try:
        result = write_piecewise_kabsch_restitch(
            tiles,
            length,
            args.out_root,
            parent_job_id=parent_job_id,
            tile_job_ids=tile_job_ids,
            assembler_dir=args.assembler_dir,
            d125_dir=args.d125_dir,
            d126_dir=args.d126_dir,
            **domain_kwargs,
        )
    except InventoryRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    except SiblingOverwriteRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    print(
        f"accepted={result.accepted} out={result.out_dir} seams={len(result.seams)}",
        file=sys.stderr,
    )
    for seam in result.seams:
        piece_bits = ",".join(
            f"[{p.interval[0]}-{p.interval[1]} n_ca={p.n_ca} rmsd={p.rmsd_angstrom}]"
            for p in seam.pieces
        )
        print(
            f"  seam tile{seam.moving_tile_index}: pieces={piece_bits or 'none'} "
            f"rmsd_full={seam.rmsd_full_overlap_angstrom} "
            f"max_ca_jump={seam.max_ca_jump_angstrom} "
            f"linker_n={seam.linker_n} max_linker_jump={seam.max_linker_ca_jump} "
            f"refuse={seam.refuse_reason}",
            file=sys.stderr,
        )
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
