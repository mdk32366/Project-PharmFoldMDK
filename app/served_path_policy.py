"""D-139 — which stitch path's bytes we actually hand out, per parent.

Phase 6 of the ``D-0043`` stitch honest-endpoint roadmap. ⚠ **Vault
``D-0043`` is external numbering, not a project decision id.**

Selection only. This module holds **no geometry, no threshold, no
transform and no artifact write**. It answers one question — *which
path's structure is served for this parent?* — and it answers it the
same way for the download route and for the review card, because two
answers to that question would drift.

⚠ **Four independent yeses, or the answer is assembler.**

1. the parent is in :data:`D126_SERVED_PASS_SUBSET` (the recorded 17);
2. a ``confidence_kabsch/{parent}/`` tree is on disk;
3. that tree's ``provenance.json`` says ``accepted: true``;
4. ``stitched.pdb`` is actually in that directory.

Any one missing and the parent keeps the assembler, under a **named**
reason. Artifacts alone can never flip a parent — a tree appearing on
disk, a PR merging, or a pass count improving are none of them
authority. The allowlist is the authority, and it is enumerated.

⚠ **Nothing here re-measures anything.** The 10.0 Å gate and the three
refuse reasons live in ``core/hold48_confidence_kabsch.py`` and are
untouched; this module reads the outcome D-126-A already recorded.

⚠ **A served D-126 structure is a recorded outcome, not a solved join.**
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from app.confidence_kabsch_path_read import (
    confidence_kabsch_persist_stem,
    confidence_kabsch_success_pdb_path,
    read_confidence_kabsch_path,
)
from app.kabsch_path_read import ASSEMBLER_PERSIST_STEM
from app.phase5_named_refuse import ACCEPT_REFUSE_TEN
# ⚠ The 27 is imported from D-126's OWN inventory constant, not from
# ``app.reads`` — ``app.reads`` imports this module, and the two constants are
# already pinned equal to ``WAVE1_WAVE2_STITCHED_PARENT_IDS`` by D-125's suite.
from core.hold48_confidence_kabsch import CONFIDENCE_RESTITCH_PARENT_IDS

DECISION = "D-139"
SPEC = "docs/README.md#d-139"
SIGNED_BY = (
    "Matt BUILD GO 2026-09-08 ~2:57 PM PT via Emma — D-0043 stitch "
    "honest-endpoint, Phase 6"
)

SERVED_ASSEMBLER = "assembler"
SERVED_CONFIDENCE_KABSCH = "confidence_kabsch"

# Named refusals. A bare ``False`` cannot tell "never eligible" from "the run
# refused it", and that distinction is the whole Phase 4 / Phase 5 vocabulary.
NOT_IN_PASS_SUBSET = "not_in_pass_subset"
NO_ARTIFACTS = "no_confidence_kabsch_artifacts"
RUN_REFUSED = "confidence_kabsch_refused"
NO_SUCCESS_PDB = "no_confidence_kabsch_success_pdb"
NOT_FLIPPED_REASONS = frozenset(
    {NOT_IN_PASS_SUBSET, NO_ARTIFACTS, RUN_REFUSED, NO_SUCCESS_PDB}
)

# ⚠ The recorded PASS subset, read off `docs/method-hold48-tiles.md`
# §"Inventory on the 27 (no silent holes)" — 17 PASS against 10 accept-refuse.
# It is written out rather than only computed so a reader can see the ids, and
# computed below anyway so a typed list that agrees with nothing cannot ship.
D126_SERVED_PASS_SUBSET: frozenset[int] = frozenset({
    2817, 2917, 2929, 3027, 3097, 3153, 3188, 3217, 3320,
    3379, 3404, 3454, 3469, 3516, 3541, 3569, 3575,
})

# ⚠⚠ The two on-disk records must agree parent-for-parent, at import time.
# D-062's defect is a written number that resolves to nothing; this is the
# cheapest possible guard against becoming it.
assert D126_SERVED_PASS_SUBSET == (
    frozenset(CONFIDENCE_RESTITCH_PARENT_IDS) - frozenset(ACCEPT_REFUSE_TEN)
), "the served PASS subset must be the 27 minus the accept-refuse ten"
assert len(D126_SERVED_PASS_SUBSET) == 17

# ⚠ D-126's OWN pass count is 24, and it is deliberately NOT the subset that
# flips. Seven of those 24 later drew a named refuse from a different path —
# six on D-128 `seam_jump_gt_10`, and 3394 on Phase 4 `rmsd_gt_10`. Serving a
# D-126 pose for a parent D-128 measured as `seam_jump_gt_10` would hand out
# bytes we hold a recorded measurement against, and `phase5_fate()` already
# answers `served_path: "assembler"` for all ten.
D126_OWN_PASS_N = 24
D126_PASS_WITH_LATER_NAMED_REFUSE: tuple[int, ...] = (
    2938, 3179, 3190, 3321, 3368, 3566, 3394,
)
assert len(D126_PASS_WITH_LATER_NAMED_REFUSE) == 7
assert D126_OWN_PASS_N - len(D126_PASS_WITH_LATER_NAMED_REFUSE) == len(
    D126_SERVED_PASS_SUBSET
)

SUBSET_SOURCE = (
    "docs/method-hold48-tiles.md §'Inventory on the 27 (no silent holes)' — "
    "17 PASS against 10 accept-refuse — reconciled at import against "
    "WAVE1_WAVE2_STITCHED_PARENT_IDS minus ACCEPT_REFUSE_TEN. ⚠ Quoted as "
    "recorded; nothing here re-measured a seam"
)

SERVED_LABELS: dict[str, str] = {
    SERVED_ASSEMBLER: (
        "Assembler — pLDDT winner-tile, not a rigid-body transform. This is "
        "the default served structure and the fallback for every parent the "
        "D-139 gate does not clear"
    ),
    SERVED_CONFIDENCE_KABSCH: (
        "Overlap-confidence Kabsch (D-126) — weighted + trimmed overlap-Cα "
        "rigid transform, then the same winner-tile assembler. Served for "
        "this parent under D-139. A recorded outcome, not a solved seam"
    ),
}

NOT_FLIPPED_NOTES: dict[str, str] = {
    NOT_IN_PASS_SUBSET: (
        "This parent is not in the recorded D-126 PASS subset of 17, so the "
        "served path is the assembler. Artifacts on disk do not change that: "
        "the allowlist is the authority, never a pass count"
    ),
    NO_ARTIFACTS: (
        "This parent is eligible, but no overlap-confidence Kabsch tree is on "
        "disk for it, so there are no D-126 bytes to serve. The assembler is "
        "served. An absent tree is not a refusal and not a solved seam"
    ),
    RUN_REFUSED: (
        "An overlap-confidence Kabsch tree is on disk and the recorded run "
        "REFUSED this parent, so the assembler is served. The refusal stands "
        "as recorded; no threshold was moved to admit it"
    ),
    NO_SUCCESS_PDB: (
        "An overlap-confidence Kabsch tree records an accepted run, but no "
        "stitched.pdb is in it, so there is nothing to serve and the "
        "assembler is served. Fail-closed: a missing file is never a pass"
    ),
}

SERVED_NOTE = (
    "Which structure you are handed is resolved per parent (D-139): the "
    "recorded D-126 PASS 17 are served the overlap-confidence Kabsch "
    "structure when its tree is on disk and accepted; every other parent is "
    "served the assembler. Seams are not scientifically solved"
)


def is_pass_subset(parent_id: Optional[int]) -> bool:
    """Membership in the recorded 17. ⚠ The only thing that may authorise a flip."""
    try:
        return int(parent_id) in D126_SERVED_PASS_SUBSET  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


def _block(
    *,
    parent_id: Optional[int],
    served: str,
    eligible: bool,
    not_flipped_reason: Optional[str],
    served_pdb_path: Optional[str],
    download_stem: str,
) -> dict[str, Any]:
    return {
        "decision": DECISION,
        "parent_job_id": parent_id,
        "served": served,
        "served_label": SERVED_LABELS[served],
        "served_note": SERVED_NOTE,
        "eligible": eligible,
        "flipped": served == SERVED_CONFIDENCE_KABSCH,
        "not_flipped_reason": not_flipped_reason,
        "not_flipped_note": (
            NOT_FLIPPED_NOTES[not_flipped_reason] if not_flipped_reason else None
        ),
        "served_pdb_path": served_pdb_path,
        "download_stem": download_stem,
        "persist_stem": (
            confidence_kabsch_persist_stem(parent_id)
            if served == SERVED_CONFIDENCE_KABSCH and parent_id is not None
            else ASSEMBLER_PERSIST_STEM
        ),
        "pass_subset_n": len(D126_SERVED_PASS_SUBSET),
        "pass_subset_parent_ids": sorted(D126_SERVED_PASS_SUBSET),
        "pass_subset_source": SUBSET_SOURCE,
        "gate_angstrom": 10.0,
        "gate_moved": False,
        "auto_flip": False,
        "solved": False,
        "signed_by": SIGNED_BY,
    }


def resolve_served_path(
    artifact_root: Path | str | None,
    *,
    parent_analysis_id: int,
    parent_job_id: Optional[int] = None,
    assembler_pdb_path: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
    confidence_kabsch: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Resolve the served path for one parent. Fail-closed to the assembler.

    ``confidence_kabsch`` may be passed when the caller already projected the
    D-126 block (the review card has), so the tree is not read twice.
    """
    keyed = parent_job_id if parent_job_id is not None else parent_analysis_id
    assembler = dict(
        parent_id=keyed,
        served=SERVED_ASSEMBLER,
        served_pdb_path=assembler_pdb_path,
        download_stem=ASSEMBLER_PERSIST_STEM,
    )

    # (a) the allowlist, checked against BOTH ids — production numbering does
    # not guarantee job id == analysis id (the same reason assembly_review
    # checks inventory membership both ways).
    eligible = is_pass_subset(parent_job_id) or is_pass_subset(parent_analysis_id)
    if not eligible:
        return _block(**assembler, eligible=False, not_flipped_reason=NOT_IN_PASS_SUBSET)

    block = confidence_kabsch
    if block is None:
        block = read_confidence_kabsch_path(
            artifact_root,
            parent_analysis_id=parent_analysis_id,
            parent_job_id=parent_job_id,
            assembler_pdb_path=assembler_pdb_path,
            meta=meta,
        )

    # (b) a tree on disk.
    if not block.get("present"):
        return _block(**assembler, eligible=True, not_flipped_reason=NO_ARTIFACTS)

    # (c) the recorded run accepted this parent.
    if not block.get("accepted"):
        return _block(**assembler, eligible=True, not_flipped_reason=RUN_REFUSED)

    # (d) the bytes are actually there. ⚠ `success_pdb_on_disk` is already
    # fail-closed in the reader (accepted AND stitched.pdb present); the path
    # lookup below is the second half — we must be able to name the file.
    pdb = confidence_kabsch_success_pdb_path(
        artifact_root,
        parent_analysis_id=parent_analysis_id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=assembler_pdb_path,
        meta=meta,
    )
    if not block.get("success_pdb_on_disk") or pdb is None:
        return _block(**assembler, eligible=True, not_flipped_reason=NO_SUCCESS_PDB)

    return _block(
        parent_id=keyed,
        served=SERVED_CONFIDENCE_KABSCH,
        eligible=True,
        not_flipped_reason=None,
        served_pdb_path=str(pdb),
        # ⚠ Never `stitched`. Two files with one name and different coordinates
        # is a bug that outlives the browser tab it started in.
        download_stem="stitched_confidence_kabsch",
    )


__all__ = (
    "D126_OWN_PASS_N",
    "D126_PASS_WITH_LATER_NAMED_REFUSE",
    "D126_SERVED_PASS_SUBSET",
    "DECISION",
    "NOT_FLIPPED_NOTES",
    "NOT_FLIPPED_REASONS",
    "NOT_IN_PASS_SUBSET",
    "NO_ARTIFACTS",
    "NO_SUCCESS_PDB",
    "RUN_REFUSED",
    "SERVED_ASSEMBLER",
    "SERVED_CONFIDENCE_KABSCH",
    "SERVED_LABELS",
    "SERVED_NOTE",
    "SIGNED_BY",
    "SUBSET_SOURCE",
    "is_pass_subset",
    "resolve_served_path",
)
