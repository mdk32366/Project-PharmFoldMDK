"""D-082 — make an over-VRAM fold fail as a job rather than as a bugcheck.

⚠⚠ **THERE IS NOTHING TO CATCH.** On 2026-08-16 an fp16 fold took the host down: bugcheck
`0x0000001e` (`KMODE_EXCEPTION_NOT_HANDLED`) with `0xC0000005`, Kernel-Power 41, unclean reboot.
Host RAM was not the constraint. **On WDDM an allocation exceeding VRAM is not refused — the driver
spills into shared system memory**, and under pressure that path faulted in kernel mode.

**Every instrument we had assumed the opposite.** `ceiling_probe._attempt` is
`except Exception -> OOM`; the worker loop reports `fail()` and continues. **Neither runs. There is
no process left.** ⚠ **Any design whose safety rests on an `except` is unsound here.**

So this module does not catch. It **prevents**, in three layers, and **the outermost is not ours**:

  1. ⚠⚠ **DRIVER — owner action.** NVIDIA *CUDA → Sysmem Fallback Policy = "Prefer No Sysmem
     Fallback"* for the venv's `python.exe`. With fallback off the driver **returns** `CUDA out of
     memory` instead of spilling. **This is the only layer that addresses the mechanism that killed
     the host.** The other two are defence in depth. ⚠ It cannot be set from code, and it cannot be
     read back reliably either — so `sysmem_fallback_state()` reports *unknown*, never *ok*.
  2. **ALLOCATOR** — `set_per_process_memory_fraction` caps the caching allocator so it raises
     `torch.cuda.OutOfMemoryError` in Python. ⚠ **Not total**: cuBLAS/cuDNN workspaces and the CUDA
     context do not all route through it. A strong guard, not a proof, and it says so.
  3. **PROCESS** — fold in a child, so a hard child death leaves a parent alive to record a named
     outcome. ⚠ **It does not survive a bugcheck. Nothing does.**

⚠ **AND THE CRANK REFUSES RATHER THAN ATTEMPTS.** `preflight` compares free VRAM against a
**measured** requirement. **An absent measurement is a CATEGORY, not a green light** — a length with
no curve is routed out, never tried.

⚠ **`nvidia-smi used` IS NOT THE PEAK.** It reports *reserved*, inflated by the caching allocator's
retained pool. `reset_peak_memory_stats()` / `max_memory_allocated()` is the instrument, and its
result belongs on the fold record beside the recipe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

#: ⚠ Fraction of total VRAM the caching allocator may hand out. Deliberately conservative: the
#: card drives a display, so `mem_get_info` reported only 7,043 MiB free of 8,150 at rest — context
#: and driver reservations take ~1.1 GB before we allocate anything.
DEFAULT_MEMORY_FRACTION = 0.85

#: ⚠ Margin between a measured requirement and free VRAM. It exists because the requirement curve
#: is measured on ONE protein per length and a different sequence at the same length is not
#: guaranteed to demand the same memory.
DEFAULT_MARGIN_MIB = 512

#: The outcome vocabulary. ⚠ `HOST_DOWN` is INFERRED, never observed — see `infer_host_down`.
FIT = "fits"
REFUSED_NO_MEASUREMENT = "refused_no_measurement"
REFUSED_INSUFFICIENT_HEADROOM = "refused_insufficient_headroom"
HOST_DOWN = "host_down"

PREFLIGHT_OUTCOMES: tuple[str, ...] = (FIT, REFUSED_NO_MEASUREMENT, REFUSED_INSUFFICIENT_HEADROOM)

#: F-059 §1 — the fitted incremental law, against a 5.24 GiB resident model.
#: ⚠ A LAW, NOT A MEASUREMENT OF THE CASE IN FRONT OF IT (F-061). Do not pass the
#: return value of `f059_peak_gib` as `preflight(..., requirement_mib=...)`.
F059_RESIDENT_GIB = 5.24
F059_INCREMENTAL_COEFF = 7.215e-06
F059_INCREMENTAL_EXPONENT = 1.983


def f059_peak_gib(length: int) -> float:
    """F-059 peak GiB at length L: `5.24 + 7.215e-06 · L^1.983`.

    ⚠ This records the law. It is not a measured requirement for the fold in
    front of it, and it must not be converted and passed as `requirement_mib`
    (F-061). `preflight` still refuses when `requirement_mib` is None.
    """
    if length < 0:
        raise ValueError(f"length must be >= 0, got {length!r}")
    return F059_RESIDENT_GIB + F059_INCREMENTAL_COEFF * (float(length) ** F059_INCREMENTAL_EXPONENT)


class VramGuardRefused(RuntimeError):
    """⚠ The fold was REFUSED before it was attempted. Raised, never warned.

    A refusal is a routing decision with a reason, not an error to be retried. Retrying it is how a
    guard becomes a suggestion.
    """


@dataclass
class Preflight:
    """What the guard decided, and on what evidence. ⚠ Every field is recorded on the fold row."""
    outcome: str
    length: int
    dtype: str
    chunk_size: Optional[int]
    free_mib: Optional[int] = None
    total_mib: Optional[int] = None
    required_mib: Optional[int] = None
    margin_mib: int = DEFAULT_MARGIN_MIB
    memory_fraction: Optional[float] = None
    detail: str = ""
    layers: dict[str, Any] = field(default_factory=dict)

    @property
    def may_fold(self) -> bool:
        return self.outcome == FIT


def cuda_memory() -> Optional[tuple[int, int]]:
    """`(free_mib, total_mib)` from the driver, or None when there is no CUDA.

    ⚠ This is the number that matters, not the card's label. It reported **7,043 free of 8,150** on
    a display-driving 8 GB card — and int8 at 416 aa peaked at 7,658 by `nvidia-smi`, i.e. *above*
    the budget. **The fold that succeeded may already have been spilling.**
    """
    try:
        import torch  # noqa: PLC0415 — lazy, so this module imports on the CI gate with no CUDA
        if not torch.cuda.is_available():
            return None
        free, total = torch.cuda.mem_get_info()
        return free // 2 ** 20, total // 2 ** 20
    except Exception:                                             # noqa: BLE001
        return None


def sysmem_fallback_state() -> dict[str, str]:
    """⚠ LAYER 1 IS NOT READABLE FROM HERE, AND THIS SAYS SO RATHER THAN GUESSING.

    The NVIDIA *Sysmem Fallback Policy* is a per-application driver setting with no supported
    query API. **Reporting it as `ok` because we could not find a problem would be an absent
    measurement coerced into an affirmative** — the F-018 shape, one layer down.
    """
    return {
        "state": "unknown",
        "why": ("the NVIDIA Sysmem Fallback Policy is a per-application driver setting with no "
                "supported query interface; it is OWNER ACTION and cannot be confirmed from code"),
        "owner_action": ("NVIDIA Control Panel -> Manage 3D Settings -> Program Settings -> "
                         "the venv's python.exe -> CUDA - Sysmem Fallback Policy -> "
                         "'Prefer No Sysmem Fallback'"),
        "why_it_matters": ("without it, exceeding VRAM SPILLS to shared system memory instead of "
                           "raising, and the failure is a host bugcheck rather than an exception"),
    }


def apply_allocator_cap(fraction: float = DEFAULT_MEMORY_FRACTION) -> dict[str, Any]:
    """⚠ LAYER 2. Cap the caching allocator so it raises in Python instead of asking the driver.

    Returns what was applied. ⚠ **A strong guard, not a proof** — cuBLAS/cuDNN workspaces and the
    CUDA context do not all route through the caching allocator, so a capped process can still
    reach the driver by another path. Recorded honestly rather than reported as safety.
    """
    if not 0 < fraction <= 1:
        raise ValueError(f"memory fraction must be in (0, 1]: {fraction!r}")
    try:
        import torch  # noqa: PLC0415
        if not torch.cuda.is_available():
            return {"applied": False, "why": "no CUDA device"}
        torch.cuda.set_per_process_memory_fraction(fraction)
        return {"applied": True, "fraction": fraction,
                "covers": "the PyTorch caching allocator only",
                "does_not_cover": "cuBLAS/cuDNN workspaces, the CUDA context, and any allocation "
                                  "that bypasses the caching allocator"}
    except Exception as e:                                        # noqa: BLE001
        return {"applied": False, "why": f"{type(e).__name__}: {e}"}


def preflight(length: int, dtype: str, chunk_size: Optional[int], *,
              requirement_mib: Optional[int], margin_mib: int = DEFAULT_MARGIN_MIB,
              fraction: float = DEFAULT_MEMORY_FRACTION, apply_cap: bool = True) -> Preflight:
    """⚠ REFUSE RATHER THAN ATTEMPT. Decide BEFORE the allocation, on a measured requirement.

    `requirement_mib` is the **measured** peak for this length and recipe. ⚠ **`None` means no
    measurement exists, and that is a REFUSAL, not a permission** — a length with no curve is
    routed out rather than tried. Guessing it is how a host gets rebooted.
    """
    layers = {"layer1_sysmem_fallback": sysmem_fallback_state()}
    layers["layer2_allocator_cap"] = (apply_allocator_cap(fraction) if apply_cap
                                      else {"applied": False, "why": "not requested"})

    mem = cuda_memory()
    free, total = mem if mem else (None, None)
    base = dict(length=length, dtype=dtype, chunk_size=chunk_size, free_mib=free, total_mib=total,
                required_mib=requirement_mib, margin_mib=margin_mib, memory_fraction=fraction,
                layers=layers)

    if requirement_mib is None:
        return Preflight(outcome=REFUSED_NO_MEASUREMENT, **base,
                         detail=(f"no measured VRAM requirement for {length} aa at dtype={dtype} "
                                 f"chunk_size={chunk_size}. ⚠ An absent measurement is a category, "
                                 f"not a green light — this length is routed out, not attempted."))
    if free is None:
        return Preflight(outcome=REFUSED_NO_MEASUREMENT, **base,
                         detail="free VRAM could not be read; refusing rather than assuming it fits")
    if requirement_mib + margin_mib > free:
        return Preflight(outcome=REFUSED_INSUFFICIENT_HEADROOM, **base,
                         detail=(f"needs {requirement_mib} MiB + {margin_mib} MiB margin = "
                                 f"{requirement_mib + margin_mib} MiB, but only {free} MiB is free"))
    return Preflight(outcome=FIT, **base,
                     detail=f"{requirement_mib} + {margin_mib} margin <= {free} MiB free")


def peak_vram() -> dict[str, Any]:
    """Peak VRAM for the current process. ⚠ `nvidia-smi used` is NOT this.

    `nvidia-smi` reports *reserved* — inflated by the caching allocator's retained pool — which is
    why 7,658 MiB was recorded for a fold whose true demand is unknown. **Both numbers are returned
    and neither stands for the other.**
    """
    try:
        import torch  # noqa: PLC0415
        if not torch.cuda.is_available():
            return {"unavailable": "no CUDA device"}
        return {"max_allocated_mib": torch.cuda.max_memory_allocated() // 2 ** 20,
                "max_reserved_mib": torch.cuda.max_memory_reserved() // 2 ** 20}
    except Exception as e:                                        # noqa: BLE001
        return {"unavailable": f"{type(e).__name__}: {e}"}


def reset_peak() -> None:
    """Zero the peak counters. ⚠ Call BEFORE the fold, or the number describes the wrong window."""
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
    except Exception:                                             # noqa: BLE001
        pass


def infer_host_down(jobs_left_running: int) -> dict[str, Any]:
    """⚠ `HOST_DOWN` IS INFERRED, NEVER OBSERVED — the instrument is not running when it happens.

    A job left `claimed`/`running` across a restart is **evidence of a host death**. ⚠ **Its absence
    is not proof of health**, and this returns that asymmetry rather than a boolean, because a
    boolean would let "no evidence" read as "fine".
    """
    if jobs_left_running > 0:
        return {"verdict": HOST_DOWN, "evidence": f"{jobs_left_running} job(s) left claimed/running "
                                                  f"across a restart",
                "action": "⚠ STOP. Do not continue the crank silently — reconcile first."}
    return {"verdict": "no_evidence_of_host_death",
            "caveat": ("⚠ NOT a clean bill of health. A host that died before claiming anything, "
                       "or after a job was reconciled, leaves no such row.")}
