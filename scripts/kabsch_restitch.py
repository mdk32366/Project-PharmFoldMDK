#!/usr/bin/env python3
"""D-125-A — restitch CLI limited to the Spec's 27 parent ids.

    python -m scripts.kabsch_restitch --manifest tiles.json --out-root /ops \\
        [--assembler-dir /ops/2817]

Not a live Fly re-query. Not a fold. Not F-004 ingest. Not D-125-B UI.
A parent id outside the 27 is refused. Kabsch artifacts land under
``<out-root>/kabsch/<parent_job_id>/`` and never overwrite an assembler
``stitched.pdb``.

Manifest (paths relative to the manifest file unless absolute)::

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

from core.hold48_kabsch import (  # noqa: E402
    ALGORITHM,
    DECISION,
    KABSCH_RESTITCH_PARENT_IDS,
    AssemblerOverwriteRefused,
    InventoryRefused,
    write_kabsch_restitch,
)
from core.hold48_stitch import TileFold  # noqa: E402


def _resolve(base: Path, p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (base / path)


def load_manifest(path: Path) -> tuple[int, int, list[int], list[TileFold]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    parent_job_id = int(raw["parent_job_id"])
    length = int(raw["length"])
    tile_job_ids = [int(x) for x in raw.get("tile_job_ids", [])]
    tiles: list[TileFold] = []
    base = path.parent
    for row in raw["tiles"]:
        pdb = _resolve(base, row["pdb"]).read_text(encoding="utf-8")
        plddt = json.loads(_resolve(base, row["plddt"]).read_text(encoding="utf-8"))
        pae = json.loads(_resolve(base, row["pae"]).read_text(encoding="utf-8"))
        tiles.append(
            TileFold(
                start=int(row["start"]),
                end=int(row["end"]),
                pdb=pdb,
                plddt=plddt,
                pae=pae,
            )
        )
    return parent_job_id, length, tile_job_ids, tiles


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m scripts.kabsch_restitch",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Local tile inventory JSON (not a Fly query)",
    )
    ap.add_argument(
        "--out-root",
        required=True,
        type=Path,
        help="Ops root; writes kabsch/<parent_job_id>/ under this path",
    )
    ap.add_argument(
        "--assembler-dir",
        type=Path,
        default=None,
        help="Existing assembler artifact dir — refused as a write target",
    )
    ap.add_argument(
        "--parent-id",
        type=int,
        default=None,
        help="Must match the manifest and the 27-id inventory",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
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
    print(
        f"{DECISION} {ALGORITHM} inventory_n={len(KABSCH_RESTITCH_PARENT_IDS)} "
        f"parent={parent_job_id}  # not a Fly re-query",
        file=sys.stderr,
    )
    try:
        result = write_kabsch_restitch(
            tiles,
            length,
            args.out_root,
            parent_job_id=parent_job_id,
            tile_job_ids=tile_job_ids,
            assembler_dir=args.assembler_dir,
        )
    except InventoryRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    except AssemblerOverwriteRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    print(
        f"accepted={result.accepted} out={result.out_dir} seams={len(result.seams)}",
        file=sys.stderr,
    )
    for seam in result.seams:
        print(
            f"  seam tile{seam.moving_tile_index}: n_ca={seam.n_ca} "
            f"rmsd={seam.rmsd_angstrom} refuse={seam.refuse_reason}",
            file=sys.stderr,
        )
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
