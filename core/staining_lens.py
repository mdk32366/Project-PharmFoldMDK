"""Ways of LOOKING at IHC staining — `D-102`. A lens, never a score.

⚠⚠ THE OWNER'S RULING IS THE WHOLE DESIGN. *"As long as you state what it is, it is neither
judgement nor measurement. It's just a way of looking at the proteins the way they empirically occur
in nature."* `D-079` decision 1 bars the system ASSERTING merit; it does not bar a reader CHOOSING a
view. So this module re-presents observed patient counts and adds no claim of its own.

⚠⚠ AND THE CONDITION — *state what it is* — IS LOAD-BEARING, NOT CEREMONIAL. Measured over the
1,727 folded census genes HPA scored, at n >= 10:

    "stains in 100% of patients"  =  728 genes (42.2%)  under BEST_PANEL
                                  =   16 genes ( 0.9%)  under POOLED

**A factor of forty-five, from the same numbers.** BEST_PANEL is a MAXIMUM over ~20 panels of median
11 patients, so 100% is substantially a selection effect rather than a property of the protein
(`F-043`). Neither lens is wrong; they answer different questions. ⚠ **An unlabelled figure is not a
weaker version of a labelled one — it is a DIFFERENT NUMBER wearing the same words**, which is
`F-049`'s family shape. Every value this module returns therefore travels with its lens and its n,
and `StainingView` has no field that can be read without them.

⚠ NOTHING HERE DIVIDES THE TWO EDGES. `D-093` ruling 4 stands: the tumour side has patient counts,
the normal side has an ordinal level over THREE individuals (amendment 5). The critical-tissue check
is an INDEPENDENT criterion evaluated on its own edge — never a subtraction, never a ratio.
"""
from __future__ import annotations

from typing import Iterable, NamedTuple, Optional

#: The two lenses, named because naming them is the ruling's condition.
BEST_PANEL = "best_panel"
POOLED = "pooled"
LENSES = (BEST_PANEL, POOLED)

LENS_MEANING = {
    BEST_PANEL: "the single cancer type where this protein stained in the largest share of patients",
    POOLED: "every cancer panel added together, one fraction over all patients examined",
}

#: ⚠⚠ THE DEFAULT FLOOR, AND IT IS NOT ZERO. `F-043`: tumour panels are median 11, max 12, and 246
#: of 1,640 sit at n <= 4. Without a floor, a 4-of-4 outranks an 11-of-12 in any ordering — the
#: small panel wins precisely because it is small. The floor is a DECLARED lens parameter, not a
#: hidden constant: the reader sets it and sees it.
DEFAULT_MIN_PATIENTS = 10

#: ⚠⚠ A STATED LIST, NOT A JUDGEMENT — the owner's ruling, and the reason it must be VISIBLE on the
#: surface. A reader who cannot see this list cannot disagree with it, and a list nobody can
#: disagree with is doing the work of a verdict while wearing the clothes of a filter.
#: ⚠ These are HPA's own tissue strings; a name that does not match one is silently no-op, which is
#: why `unknown_critical_tissues()` exists and is asserted in the tests.
CRITICAL_TISSUES = (
    "heart muscle",
    "liver",
    "kidney",
    "lung",
    "cerebral cortex",
    "bone marrow",
)

#: ⚠ Only `High` counts as a critical-tissue hit. `Medium` and `Low` are NOT folded in: that would
#: be a threshold nobody ruled, and the ordinal scale has no distance defined on it.
CRITICAL_LEVEL = "High"


class Panel(NamedTuple):
    """One (gene x cancer) IHC panel, exactly as the supplier serves it."""
    cancer: str
    high: int
    medium: int
    low: int
    not_detected: int

    @property
    def tested(self) -> int:
        return self.high + self.medium + self.low + self.not_detected

    @property
    def positive(self) -> int:
        return self.high + self.medium + self.low


class StainingView(NamedTuple):
    """What one protein looks like THROUGH A NAMED LENS.

    ⚠⚠ There is no bare `fraction` field. `lens`, `patients_positive` and `patients_tested` are
    siblings of the value, so a consumer cannot render the number without having been handed the
    two things that make it mean something.
    """
    lens: str
    patients_positive: Optional[int]
    patients_tested: Optional[int]
    cancer: Optional[str]              # ⚠ populated for BEST_PANEL only — POOLED has no one cancer
    panels_considered: int
    panels_excluded_small: int         # ⚠ how many the floor removed, never silently dropped
    category: str                      # `measured` | `no_panel_meets_floor` | `never_scored`

    @property
    def fraction(self) -> Optional[float]:
        if self.patients_tested:
            return self.patients_positive / self.patients_tested
        return None


def view(panels: Iterable[Panel], lens: str = BEST_PANEL,
         min_patients: int = DEFAULT_MIN_PATIENTS) -> StainingView:
    """One protein through one lens, with everything the figure depends on carried alongside.

    ⚠⚠ AN ABSENCE IS A CATEGORY WITH A CAUSE, and there are two distinct ones here:
    `never_scored` (HPA has no panel for this protein — **nobody looked**) and
    `no_panel_meets_floor` (panels exist, none reaches the floor the reader set). Collapsing them
    into one empty value would report a choice the READER made as a fact about the PROTEIN.
    """
    if lens not in LENSES:
        raise ValueError("unknown lens %r — the lens must be named, never defaulted silently" % lens)

    panels = [p for p in panels if p.tested > 0]
    if not panels:
        return StainingView(lens, None, None, None, 0, 0, "never_scored")

    kept = [p for p in panels if p.tested >= min_patients]
    excluded = len(panels) - len(kept)
    if not kept:
        return StainingView(lens, None, None, None, len(panels), excluded, "no_panel_meets_floor")

    if lens == BEST_PANEL:
        # ⚠ ties broken by the LARGER panel, then by name — never arbitrarily. Two panels at 100%
        # are not equally informative and the bigger one is the one a reader should be shown.
        best = max(kept, key=lambda p: (p.positive / p.tested, p.tested, p.cancer))
        return StainingView(lens, best.positive, best.tested, best.cancer,
                            len(kept), excluded, "measured")

    pos = sum(p.positive for p in kept)
    tot = sum(p.tested for p in kept)
    return StainingView(lens, pos, tot, None, len(kept), excluded, "measured")


def critical_hits(normal_rows: Iterable[tuple[str, str]],
                  tissues: Iterable[str] = CRITICAL_TISSUES) -> tuple[str, ...]:
    """Which of the DECLARED tissues this protein stains `High` in.

    ⚠ `normal_rows` is (tissue, level). Independent of the tumour edge — evaluated on its own data,
    in its own units, and never placed either side of an operator with a tumour count (ruling 4).
    ⚠⚠ And read amendment 5 before trusting a hit or a miss: the normal side is THREE INDIVIDUALS
    per tissue. This is a flag, not a measurement of safety.
    """
    want = {t.lower() for t in tissues}
    return tuple(sorted({t for t, lvl in normal_rows
                         if lvl == CRITICAL_LEVEL and (t or "").lower() in want}))


def unknown_critical_tissues(known_tissues: Iterable[str],
                             tissues: Iterable[str] = CRITICAL_TISSUES) -> tuple[str, ...]:
    """Declared tissue names that match NOTHING in the supplier's vocabulary.

    ⚠⚠ A filter naming a tissue the data has never heard of removes nothing and reports nothing —
    it silently passes every protein and looks like it worked. That is the `Cancer prognostics`
    defect exactly (`D-093 amendment 2` §3): a guard matching a string that never occurs passes
    forever while the thing it means to exclude flows through under its real name.
    """
    known = {(t or "").lower() for t in known_tissues}
    return tuple(sorted(t for t in tissues if t.lower() not in known))
