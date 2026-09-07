"""D-129-B / D-130-B / D-131 — Phase 5 + Phase 4 named-refuse fate registry.

Labelling only. This module holds **no geometry, no threshold, no transform
and no artifact read**. It answers one question — *what do we now honestly
call this parent's stitch outcome?* — from fates locked by:

* Matt Phase 5 named-refuse sign (``D-0043``, SIGNED 2026-09-05 ~17:58 PT
  via Emma; D-129 Spec §2) for the eight linker / seam parents.
* Matt Phase 4 named-refuse sign (SIGNED 2026-09-05 ~22:32 PT via Emma;
  D-130-B / D-131) for parents **3272** and **3394** after residual-RMSD
  OPS at tip ``932292d``.

⚠ **The label may not travel alone** (D-129 Spec §4, §9; D-130-B).
``accept-refuse`` is *why we stopped*; the matching OPS rollup is *what we
found*. A block for one of the ten is therefore **constructed carrying**
that rollup — Phase 5 eight carry the D-128 **0 of 7**; Phase 4 two carry
the residual-RMSD **0 of 2** — so there is no code path that hands a
surface the label without the numbers.

⚠ **Phase 4 hunt is closed.** 3272 / 3394 are **named refuse /
accept-refuse**. They are **no longer** Phase 4 must-hunt / open work.
``PHASE_4_MUST_HUNT`` is empty by design; ``is_phase_4_must_hunt`` returns
False for every parent.

⚠ **Nothing here is re-measured.** Phase 5 rollup is quoted as recorded
by Kaylee at tip ``9e65cbf``, out_root ``linker_seam_ops_2026-09-05``.
Phase 4 rollup is quoted as recorded at tip ``932292d``, out_root
``residual_rmsd_ops_2026-09-05``. A second number from a second run
would not be this one.

⚠ **No accession field exists on purpose.** Five of the seven have no
accession on record in the living log; a field would be an invitation to
fill it from memory (D-016).
"""
from __future__ import annotations

from typing import Any, Optional

DECISION = "D-129-B"
DECISION_PHASE4 = "D-130-B / D-131"
SPEC = "docs/SPEC-phase5-named-refuse.md"

# The label itself. Both halves of the vocabulary the sign uses, kept in one
# string so a surface cannot ship half of it.
ACCEPT_REFUSE_LABEL = "named refuse / accept-refuse"
ACCEPT_REFUSE_FATE = "accept-refuse"
PHASE_4_LABEL = "Phase 4 must-hunt"  # retired vocabulary; kept for tests of absence
PHASE_4_FATE = "phase-4-must-hunt"  # retired vocabulary; kept for tests of absence

# The D-128 linker seven (D-129 Spec §2, itself the SIGNED pin and Kaylee's
# recorded OPS rollup, which agree parent for parent).
D128_LINKER_SEVEN: tuple[int, ...] = (2938, 2939, 3179, 3190, 3321, 3368, 3566)
# The eighth: already accept-refuse under signed triage, re-affirmed by the
# Phase 5 sign rather than newly ruled, and NOT part of the D-128 run.
ALREADY_ACCEPT_REFUSE_PARENT_ID = 3432
ACCEPT_REFUSE_EIGHT: tuple[int, ...] = D128_LINKER_SEVEN + (
    ALREADY_ACCEPT_REFUSE_PARENT_ID,
)
# Phase 4 residual-RMSD pair — named refuse after Matt SIGNED Phase 4
# named-refuse 2026-09-05 ~22:32 PT (D-130-B / D-131).
PHASE_4_ACCEPT_REFUSE: tuple[int, ...] = (3272, 3394)
# Ten accept-refuse parents on the 27 (17 PASS + 10 accept-refuse).
ACCEPT_REFUSE_TEN: tuple[int, ...] = ACCEPT_REFUSE_EIGHT + PHASE_4_ACCEPT_REFUSE
# Hunt closed: empty by design after D-131.
PHASE_4_MUST_HUNT: tuple[int, ...] = ()

# Recorded refuse reason per parent, and which path recorded it.
# Phase 5 eight: from D-129 Spec §2. Phase 4 two: from residual-RMSD OPS
# as recorded at tip 932292d (D-130-A / D-130-B) — not re-derived.
RECORDED_REFUSE: dict[int, tuple[str, str]] = {
    2938: ("seam_jump_gt_10", "D-128"),
    2939: ("rmsd_gt_10", "D-128"),
    3179: ("seam_jump_gt_10", "D-128"),
    3190: ("seam_jump_gt_10", "D-128"),
    3321: ("seam_jump_gt_10", "D-128"),
    3368: ("seam_jump_gt_10", "D-128"),
    3566: ("seam_jump_gt_10", "D-128"),
    3432: ("no_domain_pieces", "D-127"),
    3272: ("rmsd_irreducible", "D-130-A"),
    3394: ("rmsd_gt_10", "D-130-A"),
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

# Phase 4 residual-RMSD OPS rollup of the TWO. ⚠ As recorded. Not re-measured.
PHASE4_OPS_ROLLUP: dict[str, Any] = {
    "population": "the Phase 4 residual-RMSD pair (3272, 3394)",
    "pass": 0,
    "refuse": 2,
    "fail": 0,
    "skip": 0,
    "recovered_of_two": 0,
    "recovered_zero_was_allowed": True,
    "pre_registered_at": "D-130 Spec / D-130-A (932292d / #253), before / with the run",
    "refuse_rmsd_irreducible": (3272,),
    "refuse_rmsd_gt_10": (3394,),
    "notes": {
        3272: "rmsd_irreducible; floor ≈ 12.63 Å (above the 10.0 Å gate)",
        3394: "rmsd_gt_10; floor ≈ 4.77 Å; achieved RMSD ≈ 13.77 Å; correspondence offset = 0",
    },
    "gate_angstrom": 10.0,
    "recorded_by": "recorded OPS",
    "recorded_at_tip": "932292d",
    "out_root": "residual_rmsd_ops_2026-09-05",
    "re_measured_here": False,
    "best_experimental_path": (
        "D-126 remains the best experimental path until proven otherwise; "
        "Phase 4 residual-RMSD recovered 0 of 2 at tip 932292d"
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
NOT_A_PHASE4_MISS = (
    "not a Phase 4 miss and not an RMSD-v2 miss: recovered_of_two = 0 was an "
    "allowed outcome written before the run, and both refuse classes landed "
    "beside the label"
)
PHASE_4_MEANING = (
    "named refuse / accept-refuse after Phase 4 residual-RMSD OPS: this parent "
    "refused on the whole-overlap class, the hunt is stopped, and the 0 of 2 "
    "plus refuse class stay beside the label. It is not open must-hunt, not "
    "solved, and not an RMSD-v2 miss"
)
NO_FATE_NOTE = (
    "No Phase 5 fate is recorded for this parent. That absence is not an "
    "accepted refusal, not a solved seam, and not an open must-hunt"
)


def _rollup() -> dict[str, Any]:
    """A fresh copy per call, so a surface cannot mutate the recorded rollup."""
    return dict(D128_OPS_ROLLUP)


def _phase4_rollup() -> dict[str, Any]:
    """Fresh copy of the Phase 4 residual-RMSD OPS rollup."""
    out = dict(PHASE4_OPS_ROLLUP)
    out["notes"] = dict(PHASE4_OPS_ROLLUP["notes"])
    return out


def is_accept_refuse(parent_id: Optional[int]) -> bool:
    return parent_id in ACCEPT_REFUSE_TEN


def is_phase_4_must_hunt(parent_id: Optional[int]) -> bool:
    """Always False after D-131 — Phase 4 hunt is closed."""
    return parent_id in PHASE_4_MUST_HUNT


def is_phase_4_accept_refuse(parent_id: Optional[int]) -> bool:
    return parent_id in PHASE_4_ACCEPT_REFUSE


def phase5_fate(parent_id: Optional[int]) -> dict[str, Any]:
    """The fate block for one parent: label, meaning, and the disclosure it owes.

    ⚠ The ``accept-refuse`` branch is the only place the label is produced,
    and it always attaches ``ops_rollup``. Phase 5 eight get the D-128 seven
    rollup; Phase 4 two get the residual-RMSD 0/2 rollup. Removing the
    rollup from the block is not a formatting choice; it is what §4 forbids.
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
            "phase": "phase5",
            # §4: the label does not travel alone.
            "disclosure_required": True,
            "ops_rollup": _rollup(),
            "solved": False,
            "default_served": False,
            "served_path": "assembler",
            "signed_by": "D-0043 Phase 5 named-refuse, SIGNED 2026-09-05 ~17:58 PT",
        }

    if pid is not None and pid in PHASE_4_ACCEPT_REFUSE:
        reason, recorded_by_path = RECORDED_REFUSE[pid]
        return {
            "parent_job_id": pid,
            "decision": DECISION_PHASE4,
            "spec": SPEC,
            "fate": ACCEPT_REFUSE_FATE,
            "label": ACCEPT_REFUSE_LABEL,
            "is_accept_refuse": True,
            "hunt_closed": True,
            "meaning": PHASE_4_MEANING,
            "not_a_miss": NOT_A_PHASE4_MISS,
            "recorded_refuse_reason": reason,
            "recorded_by_path": recorded_by_path,
            "counted_in_d128_ops_seven": False,
            "reaffirmed_not_newly_ruled": False,
            "already_accept_refuse_note": None,
            "phase": "phase4",
            "moves_only_on": None,
            "disclosure_required": True,
            "ops_rollup": _phase4_rollup(),
            "solved": False,
            "default_served": False,
            "served_path": "assembler",
            "signed_by": (
                "Matt SIGNED Phase 4 named-refuse, 2026-09-05 ~22:32 PT via Emma "
                "(D-130-B / D-131); OPS tip 932292d / residual_rmsd_ops_2026-09-05"
            ),
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
    "ACCEPT_REFUSE_TEN",
    "ALREADY_ACCEPT_REFUSE_PARENT_ID",
    "D128_LINKER_SEVEN",
    "D128_OPS_ROLLUP",
    "DECISION",
    "DECISION_PHASE4",
    "NOT_A_D128_MISS",
    "NOT_A_PHASE4_MISS",
    "NO_FATE_NOTE",
    "PHASE4_OPS_ROLLUP",
    "PHASE_4_ACCEPT_REFUSE",
    "PHASE_4_FATE",
    "PHASE_4_LABEL",
    "PHASE_4_MEANING",
    "PHASE_4_MUST_HUNT",
    "is_accept_refuse",
    "is_phase_4_accept_refuse",
    "is_phase_4_must_hunt",
    "phase5_fate",
)
