#!/usr/bin/env python3
"""D-141 — land the EXISTING D-126 OPS ``confidence_kabsch/`` trees onto the serving volume.

    python -m scripts.land_d139_confidence_kabsch \\
        --source-out-root <the D-126-A run's out_root> \\
        --dest-artifact-root /data/artifacts [--dry-run]

⚠ The source ``out_root`` is deliberately a placeholder. This repository does not
record which one the D-126-A run used, and inventing a plausible-looking path
here would be a name a future reader could mistake for a recorded fact. Run
``--dry-run`` first: it prints exactly which parents the root you named carries.

D-139 shipped the served-path gate and, in the same breath, printed the number
that embarrasses it: **eligible 17 / flipped 0**, every one of the seventeen
resolving to the assembler under ``no_confidence_kabsch_artifacts``. The gate is
not broken — condition (b), *a tree on disk*, is simply false on the Fly volume,
because the D-126-A OPS output was written to an ops ``out_root`` and never
travelled. This moves those bytes. It is the only thing it does.

⚠ **This is a COPY, and nothing else.** No Kabsch, no fold, no GPU, no rent, no
emit, no F-004, no migration, no threshold. It computes no geometry and reads no
tile: every seam, every RMSD and every accept/refuse in the landed trees was
decided by the D-126-A run and is carried across byte-for-byte. A parent flips
because a recorded run accepted it, never because this script ran.

⚠ **The allowlist is the authority, and it is imported, not retyped.**
``app.served_path_policy.D126_SERVED_PASS_SUBSET`` — the recorded seventeen — is
the only set of ids this script will write. Anything else is
:class:`LandRefused`, including a perfectly accepted tree sitting in the source
root: D-139's whole point is that artifacts alone never flip a parent, and a
lander that quietly widened the set would be that hard stop defeated by its own
delivery mechanism.

⚠ **Landing is not passing.** A landed tree makes the D-126 pose the *served*
one for a parent that already carried a recorded PASS. It does not solve a seam,
does not move the 10.0 Å refuse gate, and does not turn any of the ten
accept-refuse parents into anything. Seams are not scientifically solved.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from app.kabsch_path_read import default_artifact_root  # noqa: E402
from app.served_path_policy import (  # noqa: E402
    D126_SERVED_PASS_SUBSET,
    NO_ARTIFACTS,
    NO_SUCCESS_PDB,
    RUN_REFUSED,
    resolve_served_path,
)
from core.hold48_confidence_kabsch import (  # noqa: E402
    confidence_kabsch_out_dir,
    kabsch_out_dir,
    refuse_sibling_overwrite,
)

DECISION = "D-141"
SERVES = "D-139"
SIGNED_BY = (
    "Matt BUILD GO 2026-09-08 ~4:04 PM PT via Emma — land the D-126 OPS trees so "
    "D-139's gate has bytes to answer with"
)

#: Without these two the D-139 gate cannot say yes, so a tree lacking either is
#: refused rather than half-landed. ``provenance.json`` carries ``accepted``;
#: ``stitched.pdb`` is the served structure itself.
REQUIRED_FILES: tuple[str, ...] = ("provenance.json", "stitched.pdb")
#: Written by every D-126-A run. Its absence is reported, never fatal — the
#: review card falls back to ``provenance["seams"]``.
EXPECTED_FILES: tuple[str, ...] = ("seams.jsonl",)
#: D-126 runs its own ``winning_tile``, so its confidence arrays can differ from
#: the assembler's. They travel with the PDB or the served page colours D-126
#: coordinates with assembler numbers (D-139 decision 5).
PREFERRED_FILES: tuple[str, ...] = ("stitched_plddt.json", "stitched_pae.json")
LANDED_FILES: tuple[str, ...] = REQUIRED_FILES + EXPECTED_FILES + PREFERRED_FILES
#: ⚠ The SAME set, deliberately in a different order — see :func:`_copy_tree`.
#: ``provenance.json`` is what makes a directory *look landed* to every D-126
#: reader, so it is written last and the equality below is asserted rather than
#: trusted: two lists that drifted apart would reinstate the partial-state hole
#: this ordering exists to close, and would do it silently.
COPY_ORDER: tuple[str, ...] = (
    "stitched.pdb",
    "stitched_plddt.json",
    "stitched_pae.json",
    "seams.jsonl",
    "provenance.json",
)
#: ⚠ Checked with a raise, never an ``assert``: ``assert`` vanishes under ``python -O``,
#: and a guard that can be switched off by an interpreter flag is a comment that
#: usually runs (D-082's rule, applied one file down).
if set(COPY_ORDER) != set(LANDED_FILES):  # pragma: no cover — import-time pin
    raise RuntimeError("COPY_ORDER must reorder LANDED_FILES, not change its membership")
if COPY_ORDER[-1] != "provenance.json":  # pragma: no cover — import-time pin
    raise RuntimeError(
        "provenance.json must land last, or a partial copy reads as landed-wrong"
    )

LANDED = "landed"
#: Skip reasons. ⚠ Three of the five are spelled exactly as D-139's own named
#: refusals, because a parent this script skips and a parent the served-path gate
#: declines must not be described in two vocabularies.
SKIP_NO_SOURCE_TREE = "no_source_tree"
SKIP_UNREADABLE_PROVENANCE = "unreadable_provenance"
SKIP_RUN_REFUSED = RUN_REFUSED
SKIP_NO_SUCCESS_PDB = NO_SUCCESS_PDB
SKIP_DEST_EXISTS = "dest_already_landed"

SKIP_NOTES: dict[str, str] = {
    SKIP_NO_SOURCE_TREE: (
        "no confidence_kabsch/{parent}/ directory under the source out_root. An "
        "absent tree is not a refusal — this parent keeps the assembler under "
        f"{NO_ARTIFACTS!r} until someone points this script at a root that has it"
    ),
    SKIP_UNREADABLE_PROVENANCE: (
        "provenance.json is missing or is not parseable JSON, so the run's "
        "accept/refuse cannot be read. Fail-closed: unknown is never a pass"
    ),
    SKIP_RUN_REFUSED: (
        "the recorded D-126-A run REFUSED this parent (accepted is not true). The "
        "refusal stands as recorded and no threshold was moved to admit it"
    ),
    SKIP_NO_SUCCESS_PDB: (
        "provenance records an accepted run but stitched.pdb is not in the tree, "
        "so there are no bytes to serve. A missing file is never a pass"
    ),
    SKIP_DEST_EXISTS: (
        "a confidence_kabsch tree is already on the destination for this parent. "
        "Re-run with --overwrite to replace it; silently clobbering served bytes "
        "is not a default"
    ),
}


class LandRefused(RuntimeError):
    """A hard stop. ⚠ Aborts the run rather than degrading it to a skip."""


@dataclass
class ParentOutcome:
    parent_id: int
    outcome: str
    reason: Optional[str] = None
    source_dir: Optional[Path] = None
    dest_dir: Optional[Path] = None
    files_landed: tuple[str, ...] = ()
    files_left_behind: tuple[str, ...] = ()
    flipped_after: Optional[bool] = None

    @property
    def landed(self) -> bool:
        return self.outcome == LANDED

    def line(self) -> str:
        """One line per parent, `landed` or `skip`, as the Spec asks."""
        if self.landed:
            extra = (
                f" (+{len(self.files_left_behind)} left behind)"
                if self.files_left_behind
                else ""
            )
            return (
                f"landed  {self.parent_id}  "
                f"files={','.join(self.files_landed)}{extra}  -> {self.dest_dir}"
            )
        return f"skip    {self.parent_id}  {self.reason}"

    def to_json(self) -> dict[str, Any]:
        return {
            "parent_id": self.parent_id,
            "outcome": self.outcome,
            "reason": self.reason,
            "reason_note": SKIP_NOTES.get(self.reason or "", None),
            "source_dir": str(self.source_dir) if self.source_dir else None,
            "dest_dir": str(self.dest_dir) if self.dest_dir else None,
            "files_landed": list(self.files_landed),
            "files_left_behind": list(self.files_left_behind),
            "flipped_after": self.flipped_after,
        }


@dataclass
class LandReport:
    source_out_root: Path
    dest_artifact_root: Path
    dry_run: bool
    outcomes: list[ParentOutcome] = field(default_factory=list)

    @property
    def eligible(self) -> int:
        return len(D126_SERVED_PASS_SUBSET)

    @property
    def n_landed(self) -> int:
        return sum(1 for o in self.outcomes if o.landed)

    @property
    def n_skipped(self) -> int:
        return sum(1 for o in self.outcomes if not o.landed)

    @property
    def flipped_on_dest(self) -> list[int]:
        """⚠ Re-read off the DESTINATION through D-139's own gate, not counted here.

        The number this run may claim is the number the serving code answers
        with, over the whole allowlist — including parents an earlier run
        landed. Counting our own successful copies would report the thing we
        just did rather than the thing that is now true.
        """
        return sorted(
            pid
            for pid in D126_SERVED_PASS_SUBSET
            if gate_flipped(self.dest_artifact_root, pid)
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "decision": DECISION,
            "serves": SERVES,
            "signed_by": SIGNED_BY,
            "source_out_root": str(self.source_out_root),
            "dest_artifact_root": str(self.dest_artifact_root),
            "dry_run": self.dry_run,
            "eligible": self.eligible,
            "landed": self.n_landed,
            "skipped": self.n_skipped,
            "flipped_on_dest": [] if self.dry_run else self.flipped_on_dest,
            "gate_angstrom": 10.0,
            "gate_moved": False,
            "solved": False,
            "outcomes": [o.to_json() for o in self.outcomes],
        }


def gate_flipped(artifact_root: Path | str, parent_id: int) -> bool:
    """Does D-139's resolver serve D-126 for this parent, on this root?

    ⚠ The verification is the *production* selector, imported. A second
    reimplementation of "is it landed?" would be free to disagree with the code
    that actually hands out bytes, and the disagreement would surface as a
    confident green beside a page still saying ``assembler``.
    """
    block = resolve_served_path(
        artifact_root,
        parent_analysis_id=int(parent_id),
        parent_job_id=int(parent_id),
    )
    return bool(block.get("flipped"))


def require_pass_subset(parent_id: int) -> int:
    """⚠ The one hard stop this script exists to keep. Not a warning."""
    try:
        pid = int(parent_id)
    except (TypeError, ValueError) as exc:
        raise LandRefused(f"parent id {parent_id!r} is not an integer") from exc
    if pid not in D126_SERVED_PASS_SUBSET:
        raise LandRefused(
            f"parent {pid} is not in the recorded D-126 PASS subset of "
            f"{len(D126_SERVED_PASS_SUBSET)} (app.served_path_policy."
            "D126_SERVED_PASS_SUBSET) — refusing to land it. Artifacts alone never "
            "flip a parent, and that includes artifacts this script would have put "
            "there"
        )
    return pid


def resolve_dest_dir(dest_artifact_root: Path | str, parent_id: int) -> Path:
    """``{ARTIFACT_ROOT}/confidence_kabsch/{parent}/``, refusing every neighbour.

    ⚠ The path is *computed* by D-126's own ``confidence_kabsch_out_dir`` and then
    handed to D-126's own ``refuse_sibling_overwrite`` against the two directories
    it must never become — the assembler's ``{root}/{parent}/`` and D-125's
    ``{root}/kabsch/{parent}/``. Both are imported rather than re-derived, so a
    layout change cannot leave this script writing to yesterday's path.
    """
    root = Path(dest_artifact_root)
    dest = confidence_kabsch_out_dir(root, parent_id)
    try:
        refuse_sibling_overwrite(
            dest,
            assembler_dir=root / str(int(parent_id)),
            d125_dir=kabsch_out_dir(root, parent_id),
        )
    except Exception as exc:  # SiblingOverwriteRefused, re-raised in our vocabulary
        raise LandRefused(str(exc)) from exc
    return dest


def _read_provenance(source_dir: Path) -> Optional[dict[str, Any]]:
    prov = source_dir / "provenance.json"
    if not prov.is_file():
        return None
    try:
        loaded = json.loads(prov.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def inspect_source(source_out_root: Path | str, parent_id: int) -> tuple[Path, Optional[str]]:
    """The source tree and, if it may not be landed, the named reason why.

    Read-only. ⚠ The three refuse checks are D-139's conditions (c) and (d) run
    a step early, against the source: a tree that could not flip a parent after
    it landed has no business landing.
    """
    source_dir = confidence_kabsch_out_dir(source_out_root, parent_id)
    if not source_dir.is_dir():
        return source_dir, SKIP_NO_SOURCE_TREE
    provenance = _read_provenance(source_dir)
    if provenance is None:
        return source_dir, SKIP_UNREADABLE_PROVENANCE
    recorded = provenance.get("parent_job_id")
    if recorded is not None:
        try:
            recorded_int = int(recorded)
        except (TypeError, ValueError):
            recorded_int = None
        if recorded_int is not None and recorded_int != int(parent_id):
            raise LandRefused(
                f"{source_dir} holds provenance for parent {recorded_int}, not "
                f"{parent_id} — refusing to land a tree into the wrong parent's "
                "directory"
            )
    if not provenance.get("accepted"):
        return source_dir, SKIP_RUN_REFUSED
    if not (source_dir / "stitched.pdb").is_file():
        return source_dir, SKIP_NO_SUCCESS_PDB
    return source_dir, None


def _copy_tree(source_dir: Path, dest_dir: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Copy the named files only, ⚠ ``provenance.json`` LAST.

    The D-126 readers key *presence* on ``provenance.json``/``seams.jsonl`` and
    *success* on ``accepted`` plus ``stitched.pdb``. So an interrupted copy that
    had already written an accepting provenance beside a missing PDB would read
    as ``no_confidence_kabsch_success_pdb`` at best and, on a slow ``stitched.pdb``
    write, as a truncated served structure at worst. Writing the structure and
    its siblings first, then the seams, then the provenance means every partial
    state of this directory reads as *not yet landed* rather than as *landed
    wrong*. Each file lands through a temporary name and one ``os.replace``, so
    no reader sees a half-written file either.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    landed: list[str] = []
    for name in COPY_ORDER:
        src = source_dir / name
        if not src.is_file():
            continue
        tmp = dest_dir / f".{name}.landing"
        shutil.copy2(src, tmp)
        os.replace(tmp, dest_dir / name)
        landed.append(name)
    present = {p.name for p in source_dir.iterdir() if p.is_file()}
    left_behind = tuple(sorted(present - set(LANDED_FILES)))
    return tuple(landed), left_behind


def land_parent(
    source_out_root: Path | str,
    dest_artifact_root: Path | str,
    parent_id: int,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
) -> ParentOutcome:
    """Land one allowlisted parent, or say in one named word why it was not."""
    pid = require_pass_subset(parent_id)
    dest_dir = resolve_dest_dir(dest_artifact_root, pid)
    source_dir, refusal = inspect_source(source_out_root, pid)
    if source_dir.resolve() == dest_dir.resolve():
        raise LandRefused(
            f"source and destination are the same directory ({dest_dir}) — there "
            "is nothing to land and a copy onto itself is not a no-op worth risking"
        )
    if refusal is not None:
        return ParentOutcome(pid, "skip", refusal, source_dir=source_dir, dest_dir=dest_dir)
    if (dest_dir / "provenance.json").is_file() and not overwrite:
        return ParentOutcome(
            pid, "skip", SKIP_DEST_EXISTS, source_dir=source_dir, dest_dir=dest_dir
        )

    if dry_run:
        would = tuple(n for n in COPY_ORDER if (source_dir / n).is_file())
        present = {p.name for p in source_dir.iterdir() if p.is_file()}
        return ParentOutcome(
            pid,
            LANDED,
            reason=None,
            source_dir=source_dir,
            dest_dir=dest_dir,
            files_landed=would,
            files_left_behind=tuple(sorted(present - set(LANDED_FILES))),
            flipped_after=None,
        )

    landed_files, left_behind = _copy_tree(source_dir, dest_dir)
    for name in REQUIRED_FILES:
        if name not in landed_files:  # pragma: no cover — inspect_source precedes this
            raise LandRefused(f"{dest_dir} is missing {name} after the copy")
    # ⚠ The claim is checked, not asserted. "Landed" means D-139's resolver now
    # serves D-126 for this parent off the destination root — if it does not, the
    # copy achieved nothing and saying otherwise would be the D-062 shape.
    if not gate_flipped(dest_artifact_root, pid):
        raise LandRefused(
            f"parent {pid} was copied to {dest_dir} and the D-139 served-path gate "
            "still answers 'assembler' — refusing to report a land that did not flip"
        )
    return ParentOutcome(
        pid,
        LANDED,
        reason=None,
        source_dir=source_dir,
        dest_dir=dest_dir,
        files_landed=landed_files,
        files_left_behind=left_behind,
        flipped_after=True,
    )


def land(
    source_out_root: Path | str,
    dest_artifact_root: Path | str,
    *,
    parent_ids: Optional[Iterable[int]] = None,
    dry_run: bool = False,
    overwrite: bool = False,
) -> LandReport:
    """Land the allowlisted parents. ⚠ An explicitly named parent must land or raise.

    A sweep (``parent_ids=None``) walks the seventeen and skips what the source
    root does not carry — that is the expected shape of a partial OPS root. But a
    parent named on the command line is a claim that it is there, so a skip is a
    hard stop rather than a line of output somebody has to notice.
    """
    requested_explicitly = parent_ids is not None
    ids = sorted(int(p) for p in parent_ids) if requested_explicitly else sorted(
        D126_SERVED_PASS_SUBSET
    )
    for pid in ids:
        require_pass_subset(pid)

    report = LandReport(
        source_out_root=Path(source_out_root),
        dest_artifact_root=Path(dest_artifact_root),
        dry_run=dry_run,
    )
    for pid in ids:
        outcome = land_parent(
            source_out_root,
            dest_artifact_root,
            pid,
            dry_run=dry_run,
            overwrite=overwrite,
        )
        if requested_explicitly and not outcome.landed:
            raise LandRefused(
                f"parent {pid} was named on the command line and did not land: "
                f"{outcome.reason} — {SKIP_NOTES.get(outcome.reason or '', '')}"
            )
        report.outcomes.append(outcome)
    return report


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m scripts.land_d139_confidence_kabsch",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--source-out-root",
        type=Path,
        required=True,
        help="OPS root of the D-126-A run; reads <root>/confidence_kabsch/<parent>/",
    )
    ap.add_argument(
        "--dest-artifact-root",
        type=Path,
        default=None,
        help=(
            "Serving ARTIFACT_ROOT; writes <root>/confidence_kabsch/<parent>/ "
            "(default: $ARTIFACT_ROOT, else /data/artifacts)"
        ),
    )
    ap.add_argument(
        "--parent-id",
        type=int,
        action="append",
        default=None,
        dest="parent_ids",
        help=(
            "Land only this parent (repeatable). Must be in the PASS 17, and must "
            "land — a named parent that cannot be landed fails the run"
        ),
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would land. Writes nothing",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace a confidence_kabsch tree already on the destination",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit the machine-readable report after the per-parent lines",
    )
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    dest = args.dest_artifact_root or default_artifact_root()
    print(f"{DECISION} — landing D-126 OPS confidence_kabsch trees for {SERVES}")
    print(f"  source out_root      {args.source_out_root}")
    print(f"  dest ARTIFACT_ROOT   {dest}")
    print(f"  allowlist            {len(D126_SERVED_PASS_SUBSET)} parents (PASS 17)")
    if args.dry_run:
        print("  ⚠ DRY RUN — nothing is written")
    try:
        report = land(
            args.source_out_root,
            dest,
            parent_ids=args.parent_ids,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
        )
    except LandRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    for outcome in report.outcomes:
        print(outcome.line())
    print(
        f"eligible {report.eligible} / landed {report.n_landed} / "
        f"skipped {report.n_skipped}"
    )
    if not args.dry_run:
        flipped = report.flipped_on_dest
        print(
            f"D-139 gate on {dest}: eligible {report.eligible} / flipped "
            f"{len(flipped)} — {flipped}"
        )
    print(
        "⚠ A served D-126 structure is a recorded outcome, not a solved join. No "
        "threshold moved (10.0 Å); seams are not scientifically solved."
    )
    if args.as_json:
        print(json.dumps(report.to_json(), indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
