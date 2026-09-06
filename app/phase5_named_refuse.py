"""D-129-B — the Phase 5 fate registry: which parents are ``accept-refuse``, and why.

Labelling only. This module holds **no geometry, no threshold, no transform
and no artifact read**. It answers one question — *what do we now honestly
call this parent's stitch outcome?* — from fates locked by the Matt Phase 5
sign (``D-0043``, SIGNED 2026-09-05 ~17:58 PT via Emma; D-129 Spec §2).

⚠ **The label may not travel alone** (D-129 Spec §4, §9). ``accept-refuse``
is *why we stopped*; the D-128 OPS rollup is *what we found*. A block for
one of the eight is therefore **constructed carrying** that rollup — the
**0 of 7** and the named give-back (**5** vs D-125, **6** vs D-126) — so
there is no code path that hands a surface the label without the numbers.
Dropping, softening, or splitting them is named a Spec violation, not a
simplification.

⚠ **Phase 4 is cold.** 3272 / 3394 refused ``rmsd_gt_10`` — a different
class — and stay **Phase 4 must-hunt**. They are in this registry only so
that a surface asking about them gets an **open** fate rather than falling
through to a friendlier default. Neither may be labelled accepted, retired,
or closed without explicit Matt GO language (Spec §6).

⚠ **Nothing here is re-measured.** The rollup is quoted **as recorded by
Kaylee** at tip ``9e65cbf``, out_root ``linker_seam_ops_2026-09-05``. A
second number from a second run would not be this one.

⚠ **No accession field exists on purpose.** Five of the seven have no
accession on record in the living log; a field would be an invitation to
fill it from memory (D-016).
"""
from __future__ import annotations

from typing import Any, Optional

DECISION = "D-129-B"
SPEC = "docs/SPEC-phase5-named-refuse.md"

# The label itself. Both halves of the vocabulary the sign uses, kept in one
# string so a surface cannot ship half of it.
ACCEPT_REFUSE_LABEL = "named refuse / accept-refuse"
ACCEPT_REFUSE_FATE = "accept-refuse"
PHASE_4_LABEL = "Phase 4 must-hunt"
PHASE_4_FATE = "phase-4-must-hunt"

# The D-128 linker seven (D-129 Spec §2, itself the SIGNED pin and Kaylee's
# recorded OPS rollup, which agree parent for parent).
D128_LINKER_SEVEN: tuple[int, ...] = (2938, 2939, 3179, 3190, 3321, 3368, 3566)
# The eighth: already accept-refuse under signed triage, re-affirmed by the
# Phase 5 sign rather than newly ruled, and NOT part of the D-128 run.
ALREADY_ACCEPT_REFUSE_PARENT_ID = 3432
ACCEPT_REFUSE_EIGHT: tuple[int, ...] = D128_LINKER_SEVEN + (
    ALREADY_ACCEPT_REFUSE_PARENT_ID,
)
# The RMSD class. Open work, out of this Spec, moved only by a separate Matt GO.
PHASE_4_MUST_HUNT: tuple[int, ...] = (3272, 3394)

# Recorded refuse reason per parent, and which path recorded it. Copied from
# the recorded inventory (D-129 Spec §2) — not re-derived, not re-measured.
RECORDED_REFUSE: dict[int, tuple[str, str]] = {
    2938: ("seam_jump_gt_10", "D-128"),
    2939: ("rmsd_gt_10", "D-128"),
    3179: ("seam_jump_gt_10", "D-128"),
    3190: ("seam_jump_gt_10", "D-128"),
    3321: ("seam_jump_gt_10", "D-128"),
    3368: ("seam_jump_gt_10", "D-128"),
    3566: ("seam_jump_gt_10", "D-128"),
    3432: ("no_domain_pieces", "D-127"),
    3272: ("rmsd_gt_10", "D-127"),
    3394: ("rmsd_gt_10", "D-127"),
}

# The recorded D-128 OPS rollup of the SEVEN. ⚠ As recorded. Not re-measured,
# and this module must never become a second measurement of it.
D128_OPS_ROLLUP: dict[str, Any] = {
    "population": "the D-128 linker seven",
    "pass": 0,
    "refuse": 7,
    "fail": 0,
    "skip": 0,
    "repaired_of_seven": 0,
    "repaired_zero_was_pre_registered": True,
    "pre_registered_at": "D-128 Spec §1b / §3 / §11 (2004c5a / #246), before the run",
    "refuse_seam_jump_gt_10": (2938, 3179, 3190, 3321, 3368, 3566),
    "refuse_rmsd_gt_10": (2939,),
    "n_d125_pass_d128_refuse": 5,
    "n_d126_pass_d128_refuse": 6,
    "n_d127_pass_d128_refuse": 0,
    "n_d127_refuse_d128_pass": 0,
    "gate_angstrom": 10.0,
    "recorded_by": "Kaylee",
    "recorded_at_tip": "9e65cbf",
    "out_root": "linker_seam_ops_2026-09-05",
    "re_measured_here": False,
    "give_back_note": (
        "D-128 gave back 5 parents D-125 had accepted and 6 D-126 had accepted. "
        "That give-back sits beside the allowed zero, never buried under it: "
        "reporting 0 of 7, which we said was allowed, without the 5 and the 6 "
        "beside it would bury a drop under a pre-registration"
    ),
    "best_experimental_path": (
        "D-126 remains the best experimental path until proven otherwise — "
        "2 of its primary 5 recovered, against D-127's 0 of 3 and D-128's 0 of 7"
    ),
    "seams_solved": False,
}

ACCEPT_REFUSE_MEANING = (
    "accept-refuse is the recorded honest outcome of a refusal: the join is "
    "not held, we say it is not held, and we have stopped hunting it. It is "
    "not a success, not a repair, and not a miss to chase with another stitch "
    "algorithm. Accepting a refusal retires the hunt, not the record"
)
NOT_A_D128_MISS = (
    "not a D-128 miss and not a D-128 failure: 0 of 7 repaired was "
    "pre-registered as an allowed outcome before the run, and the diagnosis "
    "half landed"
)
PHASE_4_MEANING = (
    "Phase 4 must-hunt: this parent refused rmsd_gt_10, the whole-overlap "
    "class, and is open work. It is not accept-refuse, not retired, and not "
    "closed, and it moves only on a separate explicit Matt GO"
)
NO_FATE_NOTE = (
    "No Phase 5 fate is recorded for this parent. That absence is not an "
    "accepted refusal, not a solved seam, and not an open must-hunt"
)


def _rollup() -> dict[str, Any]:
    """A fresh copy per call, so a surface cannot mutate the recorded rollup."""
    return dict(D128_OPS_ROLLUP)


def is_accept_refuse(parent_id: Optional[int]) -> bool:
    return parent_id in ACCEPT_REFUSE_EIGHT


def is_phase_4_must_hunt(parent_id: Optional[int]) -> bool:
    return parent_id in PHASE_4_MUST_HUNT


def phase5_fate(parent_id: Optional[int]) -> dict[str, Any]:
    """The fate block for one parent: label, meaning, and the disclosure it owes.

    ⚠ The ``accept-refuse`` branch is the only place the label is produced,
    and it always attaches ``ops_rollup``. Removing the rollup from the block
    is not a formatting choice; it is what §4 forbids.
    """
    pid: Optional[int]
    try:
        pid = int(parent_id) if parent_id is not None else None
    except (TypeError, ValueError):
        pid = None

    if pid is not None and pid in ACCEPT_REFUSE_EIGHT:
        reason, recorded_by_path = RECORDED_REFUSE[pid]
        already = pid == ALREADY_ACCEPT_REFUSE_PARENT_ID
        in_seven = pid in D128_LINKER_SEVEN
        return {
            "parent_job_id": pid,
            "decision": DECISION,
            "spec": SPEC,
            "fate": ACCEPT_REFUSE_FATE,
            "label": ACCEPT_REFUSE_LABEL,
            "is_accept_refuse": True,
            "hunt_closed": True,
            "meaning": ACCEPT_REFUSE_MEANING,
            "not_a_miss": NOT_A_D128_MISS,
            "recorded_refuse_reason": reason,
            "recorded_by_path": recorded_by_path,
            "counted_in_d128_ops_seven": in_seven,
            "reaffirmed_not_newly_ruled": already,
            "already_accept_refuse_note": (
                "3432 was already accept-refuse under signed triage. The Phase 5 "
                "sign re-affirms it rather than newly ruling it, and it is not "
                "one of the D-128 seven: the rollup below is of the seven"
                if already
                else None
            ),
            # §4: the label does not travel alone.
            "disclosure_required": True,
            "ops_rollup": _rollup(),
            "solved": False,
            "default_served": False,
            "served_path": "assembler",
            "signed_by": "D-0043 Phase 5 named-refuse, SIGNED 2026-09-05 ~17:58 PT",
        }

    if pid is not None and pid in PHASE_4_MUST_HUNT:
        reason, recorded_by_path = RECORDED_REFUSE[pid]
        return {
            "parent_job_id": pid,
            "decision": DECISION,
            "spec": SPEC,
            "fate": PHASE_4_FATE,
            "label": PHASE_4_LABEL,
            "is_accept_refuse": False,
            "hunt_closed": False,
            "meaning": PHASE_4_MEANING,
            "recorded_refuse_reason": reason,
            "recorded_by_path": recorded_by_path,
            "counted_in_d128_ops_seven": False,
            "reaffirmed_not_newly_ruled": False,
            "moves_only_on": "a separate explicit Matt GO naming Phase 4",
            "disclosure_required": False,
            "ops_rollup": None,
            "solved": False,
            "default_served": False,
            "served_path": "assembler",
        }

    return {
        "parent_job_id": pid,
        "decision": DECISION,
        "spec": SPEC,
        "fate": None,
        "label": None,
        "is_accept_refuse": False,
        "hunt_closed": False,
        "meaning": NO_FATE_NOTE,
        "recorded_refuse_reason": None,
        "recorded_by_path": None,
        "counted_in_d128_ops_seven": False,
        "reaffirmed_not_newly_ruled": False,
        "disclosure_required": False,
        "ops_rollup": None,
        "solved": False,
        "default_served": False,
        "served_path": "assembler",
    }


__all__ = (
    "ACCEPT_REFUSE_EIGHT",
    "ACCEPT_REFUSE_FATE",
    "ACCEPT_REFUSE_LABEL",
    "ACCEPT_REFUSE_MEANING",
    "ALREADY_ACCEPT_REFUSE_PARENT_ID",
    "D128_LINKER_SEVEN",
    "D128_OPS_ROLLUP",
    "DECISION",
    "NOT_A_D128_MISS",
    "NO_FATE_NOTE",
    "PHASE_4_FATE",
    "PHASE_4_LABEL",
    "PHASE_4_MEANING",
    "PHASE_4_MUST_HUNT",
    "is_accept_refuse",
    "is_phase_4_must_hunt",
    "phase5_fate",
)
