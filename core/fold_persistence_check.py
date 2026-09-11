"""Amended Task 3.3 — the COLUMN is non-NULL **AND** the file resolves. Both. Per fold.

The original order said *"confirm PAE lands"*, and that ambiguity would have hidden the defect
Task 2 repaired: Gate A writes a FILE, Gate B writes the COLUMN, and fixing only the first leaves
``pae_json_path`` NULL while a file sits on disk. **Either half alone passes the wrong fold.**

⚠⚠ AND THE SECOND HALF IS THE ONE THIS PROJECT KEEPS RE-LEARNING: **a path is not a file.**
``F-042``'s open decision 3 — whether the 79 recorded ``pae_json_path`` files actually resolve —
went unanswered for weeks because a non-NULL count was read as a resolution answer. A recorded
path with nothing behind it is the same absence wearing a value.

⚠ Pure and injectable: ``exists`` is a parameter, so the campaign can pass a local ``os.path``
check and a remote run can pass one that asks the serving surface. **The predicate does not care
which, and that is why it can be the same check in both places.**
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Optional

#: The four outcomes, named rather than boolean. A bare False cannot distinguish "the fold emitted
#: no PAE" from "the column was never written" from "the path resolves to nothing" — and those
#: need different responses (accept / stop the campaign / stop the campaign).
OK = "ok"
NO_PAE_EMITTED = "no_pae_emitted"
COLUMN_NULL = "column_null"
FILE_MISSING = "file_missing"

#: The two that must stop a campaign. `NO_PAE_EMITTED` is a legitimate outcome for a fold whose
#: model produced none; the other two mean the persistence path is broken and every subsequent
#: fold will be broken the same way.
FATAL = frozenset({COLUMN_NULL, FILE_MISSING})


@dataclass(frozen=True)
class PersistenceVerdict:
    """One fold's persistence outcome, with the key it was judged on."""

    job_id: int
    outcome: str
    pae_json_path: Optional[str]
    emitted_pae: bool

    @property
    def is_fatal(self) -> bool:
        return self.outcome in FATAL

    def __str__(self) -> str:      # pragma: no cover - a report line, not a contract
        return (f"job {self.job_id}: {self.outcome} "
                f"(emitted_pae={self.emitted_pae}, path={self.pae_json_path!r})")


def check_fold_persistence(
    job_id: int,
    *,
    emitted_pae: bool,
    pae_json_path: Optional[str],
    exists: Callable[[str], bool] = os.path.isfile,
) -> PersistenceVerdict:
    """Amended 3.3, for one fold. **Both halves, and they are not interchangeable.**

    ``emitted_pae`` is whether the fold produced a PAE at all — supplied by the caller because
    only the fold knows. A fold that emitted none cannot have persisted one, and calling that a
    failure would make the check fire on a legitimate outcome (``F-033``'s class: an absence
    reported as the wrong kind of error).
    """
    if not emitted_pae:
        return PersistenceVerdict(job_id, NO_PAE_EMITTED, pae_json_path, emitted_pae)
    if not pae_json_path:
        # ⚠ Gate B never ran. This is precisely the silent half-fix: a file may well be on disk.
        return PersistenceVerdict(job_id, COLUMN_NULL, pae_json_path, emitted_pae)
    if not exists(pae_json_path):
        # ⚠⚠ A PATH IS NOT A FILE. The column is populated and resolves to nothing.
        return PersistenceVerdict(job_id, FILE_MISSING, pae_json_path, emitted_pae)
    return PersistenceVerdict(job_id, OK, pae_json_path, emitted_pae)


def summarise(verdicts: list[PersistenceVerdict]) -> dict[str, object]:
    """Counts per outcome, and whether the campaign may continue.

    ⚠ Reports the BREAKDOWN, never a pass-rate. *"19 of 20 OK"* hides which one failed and how,
    and the two fatal outcomes need different investigations.
    """
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v.outcome] = counts.get(v.outcome, 0) + 1
    fatal = [v for v in verdicts if v.is_fatal]
    return {
        "n": len(verdicts),
        "counts": counts,
        "fatal": fatal,
        "may_continue": not fatal,
    }
