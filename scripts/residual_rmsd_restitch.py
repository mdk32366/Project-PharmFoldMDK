#!/usr/bin/env python3
"""D-130-A — residual-RMSD hunt CLI limited to the Spec's 27 parent ids.

    python -m scripts.residual_rmsd_restitch --manifest tiles.json --out-root /ops \\
        [--assembler-dir /ops/2817] [--d125-dir /ops/kabsch/2817] \\
        [--d126-dir /ops/confidence_kabsch/2817] \\
        [--d127-dir /ops/piecewise_kabsch/2817] \\
        [--d128-dir /ops/linker_seam/2817]

    python -m scripts.residual_rmsd_restitch --decomposition-report \\
        --out-root /ops --parent-id 3272 --manifest tiles.json

    python -m scripts.residual_rmsd_restitch --confusion-report \\
        --d125-outcomes d125.json --d126-outcomes d126.json \\
        --d127-outcomes d127.json --d128-outcomes d128.json \\
        --d130-outcomes d130.json

Not a live Fly re-query. Not a fold. Not F-004 ingest. Not D-130-B UI or
Method. Not an ops restitch run of the 27. A parent id outside the 27 is
refused. Artifacts land under ``<out-root>/residual_rmsd/<parent_job_id>/``
and never overwrite the assembler ``stitched.pdb``, D-125 ``kabsch/``, D-126
``confidence_kabsch/``, D-127 ``piecewise_kabsch/`` or D-128 ``linker_seam/``
— those trees are **read** for the §1a decomposition rows.

Primary evaluation is the **two** Phase 4 must-hunt parents **3272** and
**3394**. They are the inventory, not a named-exclusion: the CLI still runs
the 27, and the eight `accept-refuse` parents (2938, 2939, 3179, 3190, 3321,
3368, 3566 + 3432) may be **recorded** but are **never success targets** and
never a D-130 miss — Phase 5 is not reopened here. **Recovering 0 of 2 is a
pre-registered allowed outcome**; the decomposition rows are the deliverable.
The 10.0 Å gate stays. The floor is one-directional: over the gate it
certifies a refusal, under it it proves nothing. Seams are measured, not
solved.

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

from core.hold48_residual_rmsd import (  # noqa: E402
    ACCEPT_REFUSE_PARENT_IDS,
    ALGORITHM,
    DECISION,
    NOT_SUCCESS_TARGET_PARENT_IDS,
    PHASE_4_PAIR_PARENT_IDS,
    RESIDUAL_FLOOR_GATE_ANGSTROM,
    RESIDUAL_RMSD_RESTITCH_PARENT_IDS,
    InventoryRefused,
    SiblingOverwriteRefused,
    build_ops_success_report,
    collect_decomposition,
    write_residual_rmsd_restitch,
)
from scripts.kabsch_restitch import load_manifest  # noqa: E402


def _load_outcome_map(path: Path) -> dict[int, bool]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "outcomes" in raw:
        raw = raw["outcomes"]
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be an object of parent_id -> accepted")
    out: dict[int, bool] = {}
    for key, val in raw.items():
        out[int(key)] = bool(val.get("accepted")) if isinstance(val, dict) else bool(val)
    return out


def _load_recovery_map(path: Path) -> dict[int, bool] | None:
    """``recovered`` is only claimed where a record says identity moved a register."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "outcomes" in raw:
        raw = raw["outcomes"]
    if not isinstance(raw, dict):
        return None
    out: dict[int, bool] = {}
    seen = False
    for key, val in raw.items():
        if isinstance(val, dict) and "recovered" in val:
            seen = True
            out[int(key)] = bool(val["recovered"])
    return out if seen else None


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m scripts.residual_rmsd_restitch",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--manifest", type=Path, default=None,
                    help="Local tile inventory JSON (not a Fly query)")
    ap.add_argument("--out-root", type=Path, default=None,
                    help="Ops root; writes residual_rmsd/<parent_job_id>/ under this path")
    ap.add_argument("--assembler-dir", type=Path, default=None,
                    help="Existing assembler artifact dir — refused as a write target")
    ap.add_argument("--d125-dir", type=Path, default=None,
                    help="Existing D-125 kabsch/ dir — refused as a write target")
    ap.add_argument("--d126-dir", type=Path, default=None,
                    help="Existing D-126 confidence_kabsch/ dir — refused as a write target")
    ap.add_argument("--d127-dir", type=Path, default=None,
                    help="Existing D-127 piecewise_kabsch/ dir — refused as a write target")
    ap.add_argument("--d128-dir", type=Path, default=None,
                    help="Existing D-128 linker_seam/ dir — refused as a write target")
    ap.add_argument("--parent-id", type=int, default=None,
                    help="Must match the manifest and the 27-id inventory")
    ap.add_argument("--decomposition-report", action="store_true",
                    help="Print §1a per-path / per-seam rows read from disk (no fit, no write)")
    ap.add_argument("--confusion-report", action="store_true",
                    help="Emit ops confusion vs D-125 / D-126 / D-127 / D-128 from outcome JSON")
    ap.add_argument("--d125-outcomes", type=Path, default=None,
                    help="JSON map of parent_id -> accepted (D-125)")
    ap.add_argument("--d126-outcomes", type=Path, default=None,
                    help="JSON map of parent_id -> accepted (D-126)")
    ap.add_argument("--d127-outcomes", type=Path, default=None,
                    help="JSON map of parent_id -> accepted (D-127)")
    ap.add_argument("--d128-outcomes", type=Path, default=None,
                    help="JSON map of parent_id -> accepted (D-128)")
    ap.add_argument("--d130-outcomes", type=Path, default=None,
                    help="JSON map of parent_id -> accepted (and optionally recovered) (D-130)")
    ap.add_argument("--decomposition-rows", type=Path, default=None,
                    help="Optional residual_decomposition.jsonl to count classes from")
    ap.add_argument("--seam-rows", type=Path, default=None,
                    help="Optional seams.jsonl to count audits / corrections / refusals from")
    return ap


def _banner(parent_job_id: int | None) -> None:
    print(
        f"{DECISION} {ALGORITHM} inventory_n={len(RESIDUAL_RMSD_RESTITCH_PARENT_IDS)} "
        f"phase_4_pair={sorted(PHASE_4_PAIR_PARENT_IDS)} "
        f"not_success_targets={sorted(NOT_SUCCESS_TARGET_PARENT_IDS)} "
        f"floor_gate={RESIDUAL_FLOOR_GATE_ANGSTROM} no_trim=True no_weights=True "
        f"no_window=True no_pieces=True parent={parent_job_id}  "
        f"# not a Fly re-query; not a named-exclusion; the floor is "
        f"one-directional; seams measured, not solved",
        file=sys.stderr,
    )


def _decomposition_report(out_root: Path, parent_job_id: int, manifest: Path | None) -> int:
    """Read-only §1a rows. Needs the manifest for the pre-transform geometry.

    ⚠ The floor is measured from the **input** tiles, before any transform —
    that is what makes it a property of the two tiles rather than of a path
    (Spec §1a). Without a manifest there are no input tiles, so the report
    says so instead of printing a floor it could not have measured.
    """
    if manifest is None:
        print(
            "refuse: --decomposition-report needs --manifest — the floor is measured "
            "from the pre-transform input tiles and is not guessed from a tree",
            file=sys.stderr,
        )
        return 2
    _parent, _length, _ids, tiles = load_manifest(manifest)
    rows = [row.to_json_row() for row in collect_decomposition(out_root, parent_job_id, tiles, ())]
    print(json.dumps({"parent_job_id": parent_job_id, "residual_decomposition": rows}, indent=2))
    for row in rows:
        if row["residual_class"] == "irreducible":
            print(
                f"certified refuse: path={row['path']} tile{row['moving_tile_index']} "
                f"floor={row['rmsd_floor_angstrom']} Å > {RESIDUAL_FLOOR_GATE_ANGSTROM} Å "
                f"(no rigid transform can pass this correspondence — a certificate, not a fix)",
                file=sys.stderr,
            )
        elif row["residual_class"] == "unknown":
            print(
                f"unknown row: path={row['path']} tile{row['moving_tile_index']} "
                f"reason={row['absence_reason']} "
                f"(unknown is neither irreducible nor placement; null is not 0.0)",
                file=sys.stderr,
            )
    print(
        f"note: a floor at or below {RESIDUAL_FLOOR_GATE_ANGSTROM} Å proves NOTHING — "
        f"it is not a recovery forecast and never an argument to loosen the gate",
        file=sys.stderr,
    )
    return 0


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _confusion_report(args: argparse.Namespace) -> int:
    missing = [
        name
        for name, val in (
            ("--d125-outcomes", args.d125_outcomes),
            ("--d126-outcomes", args.d126_outcomes),
            ("--d127-outcomes", args.d127_outcomes),
            ("--d128-outcomes", args.d128_outcomes),
            ("--d130-outcomes", args.d130_outcomes),
        )
        if val is None
    ]
    if missing:
        print(
            "refuse: --confusion-report needs --d125-outcomes, --d126-outcomes, "
            "--d127-outcomes, --d128-outcomes, and --d130-outcomes",
            file=sys.stderr,
        )
        return 2
    try:
        d125 = _load_outcome_map(args.d125_outcomes)
        d126 = _load_outcome_map(args.d126_outcomes)
        d127 = _load_outcome_map(args.d127_outcomes)
        d128 = _load_outcome_map(args.d128_outcomes)
        d130 = _load_outcome_map(args.d130_outcomes)
        recovered = _load_recovery_map(args.d130_outcomes)
        rows = _read_jsonl(args.decomposition_rows) if args.decomposition_rows else []
        seams = _read_jsonl(args.seam_rows) if args.seam_rows else []
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"refuse: cannot read outcomes: {exc}", file=sys.stderr)
        return 2
    report = build_ops_success_report(
        d125,
        d126,
        d127,
        d128,
        d130,
        d130_recovered=recovered,
        decomposition_rows=rows,
        seam_rows=seams,
    )
    print(json.dumps(report.to_json(), indent=2))
    for label, value in (
        ("n_d125_pass_d130_refuse", report.n_d125_pass_d130_refuse),
        ("n_d126_pass_d130_refuse", report.n_d126_pass_d130_refuse),
        ("n_d127_pass_d130_refuse", report.n_d127_pass_d130_refuse),
        ("n_d128_pass_d130_refuse", report.n_d128_pass_d130_refuse),
        ("n_d126_recovered_d130_refuse", report.n_d126_recovered_d130_refuse),
    ):
        if value:
            print(
                f"named finding: {label}={value} "
                f"(a drop on a prior path's PASS set is not silent success)",
                file=sys.stderr,
            )
    print(
        f"recovered_of_two={report.recovered_of_two} "
        f"(source={report.recovered_of_two_source}; 0-of-2 is a pre-registered allowed "
        f"outcome and a named refuse after a failed hunt is complete; gate stays "
        f"{RESIDUAL_FLOOR_GATE_ANGSTROM} Å; n_placement is not a recovery forecast)",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.confusion_report:
        return _confusion_report(args)

    if args.decomposition_report:
        if args.out_root is None or args.parent_id is None:
            print(
                "refuse: --decomposition-report needs --out-root and --parent-id",
                file=sys.stderr,
            )
            return 2
        if args.parent_id not in RESIDUAL_RMSD_RESTITCH_PARENT_IDS:
            print(
                f"refuse: parent_job_id {args.parent_id} is not in the 27-id inventory",
                file=sys.stderr,
            )
            return 2
        _banner(args.parent_id)
        try:
            return _decomposition_report(args.out_root, args.parent_id, args.manifest)
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"refuse: cannot read manifest: {exc}", file=sys.stderr)
            return 2

    if args.manifest is None or args.out_root is None:
        print(
            "refuse: --manifest and --out-root are required "
            "(or --decomposition-report / --confusion-report)",
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
    if parent_job_id in ACCEPT_REFUSE_PARENT_IDS:
        print(
            f"note: parent {parent_job_id} is accept-refuse (D-129 Phase 5) — recorded here, "
            f"never a success target of this Spec and never a D-130 miss; Phase 5 is not "
            f"reopened",
            file=sys.stderr,
        )
    elif parent_job_id not in PHASE_4_PAIR_PARENT_IDS:
        print(
            f"note: parent {parent_job_id} is recorded for confusion against the prior paths; "
            f"the Phase 4 must-hunt pair is {sorted(PHASE_4_PAIR_PARENT_IDS)} and a pass here "
            f"is not a Phase 4 recovery",
            file=sys.stderr,
        )
    try:
        result = write_residual_rmsd_restitch(
            tiles,
            length,
            args.out_root,
            parent_job_id=parent_job_id,
            tile_job_ids=tile_job_ids,
            assembler_dir=args.assembler_dir,
            d125_dir=args.d125_dir,
            d126_dir=args.d126_dir,
            d127_dir=args.d127_dir,
            d128_dir=args.d128_dir,
        )
    except InventoryRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    except SiblingOverwriteRefused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2

    print(
        f"accepted={result.accepted} recovered={result.recovered} out={result.out_dir} "
        f"seams={len(result.seams)} decomposition_rows={len(result.decomposition)}",
        file=sys.stderr,
    )
    for seam in result.seams:
        print(
            f"  seam tile{seam.moving_tile_index}: n_overlap_ca={seam.n_overlap_ca} "
            f"dRMSD={seam.internal_drmsd_angstrom} floor={seam.rmsd_floor_angstrom} "
            f"class={seam.residual_class} verified={seam.correspondence_verified} "
            f"offset={seam.register_offset_aa} evidence={seam.identity_evidence} "
            f"rmsd={seam.rmsd_angstrom} max_ca_jump={seam.max_ca_jump_angstrom} "
            f"refuse={seam.refuse_reason}",
            file=sys.stderr,
        )
    for row in result.decomposition:
        print(
            f"  decomposition {row.path} tile{row.moving_tile_index}: "
            f"n_overlap_ca={row.n_overlap_ca} rigid_rmsd={row.rigid_rmsd_angstrom} "
            f"dRMSD={row.internal_drmsd_angstrom} floor={row.rmsd_floor_angstrom} "
            f"class={row.residual_class} floor_exceeds_gate={row.floor_exceeds_gate} "
            f"rmsd_src={row.rigid_rmsd_source} drmsd_src={row.internal_drmsd_source} "
            f"absence={row.absence_reason}",
            file=sys.stderr,
        )
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
