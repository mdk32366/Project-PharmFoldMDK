"""ESMFold fold-runner — sequence in, structure + provenance out (D-018).

The **pure** fold-runner: it folds one sequence with given parameters and records
exactly what it did. It does NOT select the cohort, query UniProt, choose ECD
boundaries, or route to a compute tier — that is the orchestrator, a later step
(D-018). It writes artifacts to files and touches no database.

HOST-AGNOSTIC by construction: `dtype` and `chunk_size` are parameters, defaulting
to the S-003-measured local recipe (int8 trunk / chunk 64) that fits the 8 GB GPU;
the rented tier (D-011) passes `dtype="fp16"`, and `chunk_size=64` — the trunk's
triangular attention is O(L³), so even a 95 GiB card OOMs on large L unchunked, and
chunking is mandatory, not optional (D-042, correcting D-011). Nothing here assumes
which host it runs on. A CUDA OOM is raised as `FoldError` (D-030 §4) so the loop
reports it and continues rather than crashing (closeout §3a).

torch/transformers are imported **lazily inside `fold`**, so this module imports on
a machine with no CUDA stack (the CI gate has none — D-013 §4/D-018): every function
below except `fold` is pure and unit-tested there. `fold` itself is GPU-bound and is
validated on a GPU host by the owner (the int8 recipe is already measured — S-003/S-005).

PROVENANCE is not optional (D-016, D-015 §1a): each fold records its dtype, chunk_size,
model revision, whether the input was a sliced ECD or a whole sequence (the GPI-anchored
fallback, D-009 §2), the ECD bounds when sliced, and whether a length cap truncated the
input. A truncated fold is a different molecule and must be excludable from ranking
claims later — which is impossible unless the flag is captured *at fold time*.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from worker.orchestrator import FoldError   # the shared fold-failure contract (D-030 §4); a plain
# Exception, torch-free — safe to import on the CI gate, which has no CUDA (D-018). orchestrator
# imports only core.contracts + stdlib, so there is no import cycle with runner.

# The only released ESMFold checkpoint (S-001), pinned by revision for reproducibility
# (ARCHITECTURE §7). The worker manifest pins the libraries; this pins the weights.
MODEL_ID = "facebook/esmfold_v1"
MODEL_REVISION = "75a3841ee059df2bf4d56688166c8fb459ddd97a"

# S-003-measured local recipe that fits 8 GB (int8 ESM-2 trunk, folding head full precision,
# axial chunk 64). Overridden per host — the A6000 uses fp16 / no chunk (D-011).
DEFAULT_DTYPE = "int8"
DEFAULT_CHUNK_SIZE = 64

# The ESM-2 submodules to leave OUT of int8 quantization (S-003 recipe): quantize the
# language-model trunk only, keep the folding head and heads in full precision.
INT8_SKIP_MODULES = [
    "trunk", "distogram_head", "ptm_head", "lm_head", "lddt_head",
    "esm_s_mlp", "esm_s_combine", "af2_to_esm",
]

# Input provenance: was the runner handed a domain slice or the whole chain?
SLICED_ECD = "sliced_ecd"   # an extracellular-domain slice (D-009 §2, the normal path)
WHOLE = "whole"             # no topological annotation to slice on — GPI-anchored / FOLR1 fallback


@dataclass
class FoldProvenance:
    """The reproducibility + diagnostic record written beside every fold. This is the
    `inference_settings` of D-004 plus the D-015 §1a slice/truncation flags."""

    model_id: str
    model_revision: str
    dtype: str
    chunk_size: Optional[int]
    input_length: int              # residues actually folded (post-cap)
    source: str                    # SLICED_ECD | WHOLE
    ecd_start: Optional[int] = None
    ecd_end: Optional[int] = None
    truncated: bool = False        # did a length cap cut the input? (a different molecule — §1a)
    length_cap: Optional[int] = None
    original_length: Optional[int] = None   # residues before any cap
    mean_plddt: Optional[float] = None       # on the 0–100 scale (rescaled — see rescale_plddt)
    ca_atom_count: Optional[int] = None      # for the §1a fold-sanity diagnostic
    folded_at: Optional[str] = None          # ISO-8601 UTC


@dataclass
class FoldResult:
    """What `fold` returns and `write_artifacts` persists."""

    pdb: str
    plddt: list[float]             # per-residue, 0–100
    pae: Optional[list] = None     # predicted aligned error matrix, if the model emits one
    provenance: Optional[FoldProvenance] = None


# ── pure helpers (unit-tested on the CI gate, no GPU) ─────────────────────────

def rescale_plddt(values: list[float]) -> list[float]:
    """ESMFold hands pLDDT back in the B-factor column on the **0–1 scale**; everything
    downstream expects 0–100 (S-001 gotcha, cost real confusion). Rescale explicitly.

    Idempotent by inspection: if the values already exceed 1.0 they are assumed to be
    on the 0–100 scale and returned unchanged, so a double-call cannot inflate them.
    """
    if not values:
        return []
    if max(values) <= 1.0:
        return [v * 100.0 for v in values]
    return list(values)


def apply_length_cap(sequence: str, length_cap: Optional[int]) -> tuple[str, bool]:
    """Enforce a length cap, reporting whether it truncated. Returns (sequence, truncated).

    A truncated sequence is a **different molecule** (D-015 §1a) — the caller records the
    flag so the fold can be excluded from ranking claims later. No cap (None) never truncates.
    """
    if length_cap is None or len(sequence) <= length_cap:
        return sequence, False
    return sequence[:length_cap], True


def build_provenance(sequence: str, *, dtype: str, chunk_size: Optional[int], source: str,
                     ecd_start: Optional[int], ecd_end: Optional[int],
                     length_cap: Optional[int], now: Optional[datetime] = None) -> FoldProvenance:
    """Construct the provenance record from the fold's inputs (pure; pLDDT/CA filled in
    after the fold). Records the truncation decision via `apply_length_cap`."""
    if source not in (SLICED_ECD, WHOLE):
        raise ValueError(f"source must be {SLICED_ECD!r} or {WHOLE!r}, got {source!r}")
    original_length = len(sequence)
    folded_seq, truncated = apply_length_cap(sequence, length_cap)
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    return FoldProvenance(
        model_id=MODEL_ID, model_revision=MODEL_REVISION,
        dtype=dtype, chunk_size=chunk_size,
        input_length=len(folded_seq), source=source,
        ecd_start=ecd_start, ecd_end=ecd_end,
        truncated=truncated, length_cap=length_cap,
        original_length=original_length, folded_at=stamp,
    )


def write_artifacts(result: FoldResult, out_dir: str | Path) -> dict[str, str]:
    """Persist a fold: `structure.pdb`, `plddt.json`, `pae.json` (if present), and
    `provenance.json`. Returns the paths written. The DB records these paths later — the
    runner deliberately knows nothing about the database (D-018)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    (out / "structure.pdb").write_text(result.pdb, encoding="utf-8")
    written["pdb"] = str(out / "structure.pdb")
    (out / "plddt.json").write_text(json.dumps(result.plddt), encoding="utf-8")
    written["plddt"] = str(out / "plddt.json")
    if result.pae is not None:
        (out / "pae.json").write_text(json.dumps(result.pae), encoding="utf-8")
        written["pae"] = str(out / "pae.json")
    if result.provenance is not None:
        (out / "provenance.json").write_text(
            json.dumps(asdict(result.provenance), indent=2), encoding="utf-8")
        written["provenance"] = str(out / "provenance.json")
    return written


def write_pae(result: FoldResult, out_dir: str | Path) -> Optional[str]:
    """Persist **only** ``pae.json`` — the rental tier's local PAE persist (D-035 part 2 / D-036).

    ``structure.pdb`` / ``plddt.json`` / ``provenance.json`` already persist server-side via the
    upload route, so the pod keeps just PAE — which the upload no longer carries (D-035 part 2) —
    for out-of-band retrieval before termination. Returns the path, or ``None`` when the fold
    emitted no PAE. Deliberately not the four-file ``write_artifacts``: duplicating the other
    three on the pod buys nothing."""
    if result.pae is None:
        return None
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "pae.json"
    path.write_text(json.dumps(result.pae), encoding="utf-8")
    return str(path)


# ── the GPU-bound fold (import-guarded; validated on a GPU host, not in CI) ────

# Loaded models, keyed by (dtype, revision) and reused across folds (closeout §3c: the weights
# were reloading once PER TARGET on the first rental run — `Loading weights: 4498` per fold — a
# direct, measurable cost on rented silicon). A single-recipe batch now loads the weights ONCE.
_MODEL_CACHE: dict = {}


def _load_model(dtype: str):
    """Load the ESMFold tokenizer+model for ``dtype``, CACHED across folds. GPU-bound; validated
    on the owner's GPU host, not CI (no CUDA, D-018). ``chunk_size`` is NOT part of the key — it
    is a runtime trunk setting, not a weight, so it is set per fold on the reused model."""
    import torch  # noqa: PLC0415 — lazy on purpose (see module docstring)
    from transformers import AutoTokenizer, EsmForProteinFolding

    key = (dtype, MODEL_REVISION)
    cached = _MODEL_CACHE.get(key)
    if cached is not None:
        return cached

    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    if dtype == "int8":
        from transformers import BitsAndBytesConfig
        # S-003: int8-quantize the ESM-2 trunk ONLY; folding head stays full precision.
        quant = BitsAndBytesConfig(load_in_8bit=True, llm_int8_skip_modules=INT8_SKIP_MODULES)
        model = EsmForProteinFolding.from_pretrained(
            MODEL_ID, revision=MODEL_REVISION, quantization_config=quant, device_map={"": 0})
    else:
        model = EsmForProteinFolding.from_pretrained(MODEL_ID, revision=MODEL_REVISION).to("cuda")
        if dtype == "fp16":
            model.esm = model.esm.half()
        elif dtype == "bf16":
            model.esm = model.esm.to(torch.bfloat16)
    model.eval()
    _MODEL_CACHE[key] = (tok, model)
    return tok, model


def fold(sequence: str, *, dtype: str = DEFAULT_DTYPE, chunk_size: Optional[int] = DEFAULT_CHUNK_SIZE,
         source: str = SLICED_ECD, ecd_start: Optional[int] = None, ecd_end: Optional[int] = None,
         length_cap: Optional[int] = None) -> FoldResult:
    """Fold one sequence and return structure + provenance. GPU-bound.

    torch/transformers are imported lazily (module docstring). The model is loaded once per
    recipe and reused (`_load_model`, §3c); a CUDA OOM is raised as `FoldError` so the loop
    reports `fail()` and continues instead of the process crashing (closeout §3a).
    """
    import torch  # noqa: PLC0415 — lazy on purpose (see module docstring)

    prov = build_provenance(sequence, dtype=dtype, chunk_size=chunk_size, source=source,
                            ecd_start=ecd_start, ecd_end=ecd_end, length_cap=length_cap)
    folded_seq, _ = apply_length_cap(sequence, length_cap)

    tok, model = _load_model(dtype)                 # cached across folds (§3c)
    if chunk_size is not None:
        model.trunk.set_chunk_size(chunk_size)      # runtime trunk setting, not a weight — per fold

    try:
        inputs = tok([folded_seq], return_tensors="pt", add_special_tokens=False)["input_ids"].to("cuda")
        with torch.no_grad():
            out = model.infer_pdb(folded_seq) if hasattr(model, "infer_pdb") else None
            outputs = model(inputs)
    except torch.OutOfMemoryError as e:
        # D-030 §4 named CUDA OOM a deterministic FoldError; classify it HERE (near torch) so the
        # loop calls fail() and continues instead of the process crashing (closeout §3a). OOM on a
        # fixed (sequence, recipe) is deterministic — a retry would OOM again on a PAID card — so it
        # is terminal, not retried. The batch resilience catch in run_worker is the backstop for any
        # OOM this misses on a torch build without OutOfMemoryError.
        raise FoldError(
            f"CUDA OOM folding {len(folded_seq)} aa at chunk_size={chunk_size} — the trunk's "
            f"triangular attention is O(L^3); chunking is the mitigation (D-042): {e}") from e

    pdb = out if isinstance(out, str) else model.output_to_pdb(outputs)[0]
    # pLDDT lives in the B-factor column on the 0–1 scale — rescale (S-001).
    plddt_raw = outputs["plddt"].mean(dim=-1).squeeze().tolist()
    plddt = rescale_plddt(plddt_raw if isinstance(plddt_raw, list) else [plddt_raw])
    pae = outputs["predicted_aligned_error"].squeeze().tolist() if "predicted_aligned_error" in outputs else None

    prov.mean_plddt = round(sum(plddt) / len(plddt), 2) if plddt else None
    prov.ca_atom_count = pdb.count(" CA ")   # cheap CA count for the §1a fold-sanity diagnostic
    return FoldResult(pdb=pdb, plddt=plddt, pae=pae, provenance=prov)
