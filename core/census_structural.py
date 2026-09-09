"""The census STRUCTURAL rank — `D-144`. Three factors, multiplied, and nothing else.

⚠⚠ **`STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready`.** That sentence is this module's
whole contract and it travels on the run, on the payload and on **every row** rather than
living in a doc a reader has to go and find (the `census_cost_read.py` shape, D-077 dec 1
refusal 2). A number ordering 3,467 human surface proteins, unlabelled, is read as a
shortlist of ADC targets. It is not one.

⚠⚠ **THIS IS NOT THE COHORT-82 SCORER AND MUST NEVER BE CONFUSED WITH IT.** `core/scorer.py`
is the **learned** ridge model of `D-041` / `D-060` — six pre-registered structure-derived
features, fit on Group B labels, served through `/api/ranking` from `ranking_runs` /
`target_scores` / `ranking_results` at `run_kind='preregistered'`. **None of that is touched
here.** This module fits nothing, learns nothing, and consumes no label: it is a **fixed
arithmetic product of three stated quantities**, persisted to its own two tables and served
on its own route. The two surfaces answer different questions over different populations
measured under different span definitions (`D-081`), and the separation is the point.

═══════════════════════════════════════════════════════════════════════════════
THE FORMULA — LOCKED BY THE GO, AND THE EXCLUSIONS ARE PART OF IT
═══════════════════════════════════════════════════════════════════════════════

    structural_score = score_membrane × score_ecd × score_model

    score_membrane  1.0 if `census_class == "surface"`, else 0.2
    score_ecd       min(1.0, span_aa / 200); **0** when `span_aa` is missing or 0
    score_model     mean_plddt / 100  when the analysis carries a PDB **and** a pLDDT
                    0.8               when it carries a PDB and **no** pLDDT
                    0.3               when there is **no fold at all**

⚠⚠ **FOUR FACTORS ARE EXCLUDED AND THEIR ABSENCE IS DELIBERATE:** `cancer`, `normal_risk`,
`internalization`, `density`. The offline draft carried them as **0.5 neutrals** for every
protein the project has no measurement for, which multiplies a made-up number into every
row and then ranks on the product — an imputed value fit as though measured (`F-020`'s
shape). **A factor we cannot measure is left out of the product entirely, not set to a
half.** `EXCLUDED_FACTORS` names them so a future edit that reintroduces one has to delete
a constant that says why it is gone, and `tests/test_d144_census_structural_rank.py` walks
this module's **AST** asserting no numeric constant `0.5` appears in it — a source-text grep
would have been satisfied by this paragraph, which is `F-044`'s shape (*a reference that
resolves, to the wrong thing*).

⚠ **`score_model = 0.3` for a protein with no fold is not a neutral either — it is a
PENALTY, and it is the one component that makes this ranking a statement about ESMFold's
output rather than about UniProt annotation.** A never-folded protein cannot be certified
by the network, so the formula says so, in the score, at a third of the weight a fold with
average confidence would earn.

═══════════════════════════════════════════════════════════════════════════════
THE REFERENCE SINK — A YARDSTICK IS NOT A NEXT TARGET
═══════════════════════════════════════════════════════════════════════════════

An antigen that already has an ADC pointed at it is a **reference point**, not a candidate:
NECTIN4/`Q96NY8` (Padcev, approved) is the canonical case. Those rows keep their computed
score — blanking it would hide the yardstick — carry `is_reference: true`, and **sort to the
end**, after every candidate.

⚠⚠ **THE SET IS DERIVED BY JOIN FROM THE COMMITTED CURATED FILE, NEVER TYPED HERE.**
`core.adc_reference.load_mapping()` over `data/adc_reference_mapping.csv` — the same
per-row-cited file `D-029` / `D-040` already govern. A hand-typed list of accessions inside
this module would be a second copy of a curation free to drift from the one the ADC surfaces
consult, which is the `D-062` shape. Measured 2026-09-09: **12** cited antigen accessions,
**12 of 12** present in `census_manifest.v7.csv`.

⚠ **`is_reference` NEVER ENTERS THE SCORE.** It is an ordering and display fact only, so a
reference row's score stays comparable to the candidates it is a yardstick for. There is no
branch here that multiplies, floors or scales by it, and a test asserts the score of a row
is identical whether or not it is flagged.
"""

from __future__ import annotations

import csv
import functools
import hashlib
import pathlib
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

_ROOT = pathlib.Path(__file__).resolve().parent.parent

#: The committed population. ⚠ The DENOMINATOR IS A FILE, NOT THE DATABASE (`D-024`): reading
#: the population from `protein_analyses` would make it a function of how much folding has
#: happened, so a tranche nobody has folded yet would silently leave the census.
CENSUS_MANIFEST = _ROOT / "data" / "census" / "census_manifest.v7.csv"
CENSUS_LABELS = _ROOT / "data" / "census" / "census_labels.csv"

# ── the banner, and it is not optional furniture ─────────────────────────────

#: ⚠⚠ THE ONE STRING EVERY SURFACE MUST CARRY. Short by design: it rides on 3,467 rows.
STRUCTURAL_ONLY = "STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready"

#: The long form, for a run row and a payload header — never for a per-row field.
DISCLAIMER = (
    "STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready. This rank is the product of three "
    "structural quantities only: whether the protein is annotated cell-surface, how long its "
    "extracellular span is (saturating at 200 aa), and how confident ESMFold was about the "
    "structure we hold for it. It carries NO tumour expression, NO normal-tissue risk, NO "
    "internalisation and NO antigen density, and it is NOT the learned cohort-82 scorer served "
    "at /api/ranking (D-041 / D-060). A high position here means 'structurally tractable and "
    "confidently folded', never 'good ADC target'."
)

#: ⚠⚠ NAMED, NOT SILENTLY OMITTED. The four factors the offline draft carried as 0.5 neutrals.
#: An absent factor is a category; a 0.5 standing in for one is a fabricated measurement.
EXCLUDED_FACTORS: tuple[tuple[str, str], ...] = (
    ("cancer", "no per-protein tumour-expression weight enters this score; the HPA edges exist "
               "(D-093) but composing them into a rank is a separate, later GO"),
    ("normal_risk", "no normal-tissue penalty enters this score; the HPA normal-tissue edge is "
                    "measured (D-093 dec 5) and deliberately not composed here"),
    ("internalization", "never measured by this project for any protein"),
    ("density", "never measured by this project for any protein"),
)

# ── the three components ─────────────────────────────────────────────────────

#: `census_class` value that earns the full membrane factor. Everything else is 0.2 —
#: including `unclassified` and `class_conflict` (`F-019`), which are NOT surface claims.
SURFACE_CLASS = "surface"
MEMBRANE_SURFACE = 1.0
MEMBRANE_OTHER = 0.2

#: The ECD factor saturates here: 200 aa of extracellular span is treated as enough, and more
#: is not better. ⚠ A cap, not a threshold — a 199 aa span scores 0.995, not 0.
ECD_SATURATION_AA = 200

#: `score_model`, the three cases. ⚠ `MODEL_NO_FOLD` is a PENALTY, not a neutral (see the
#: module docstring); `MODEL_FOLD_WITHOUT_PLDDT` is the confidence of a fold we hold but whose
#: per-residue confidence was not persisted — a recorded structure with an unrecorded number.
MODEL_FOLD_WITHOUT_PLDDT = 0.8
MODEL_NO_FOLD = 0.3

#: Row-level flags. ⚠ Every one of them is a CATEGORY on the row, never an absent field a
#: reader has to infer from a value (`D-079` amendment 1 ruling 2's rule, applied to flags).
FLAG_NO_FOLD = "no_fold"
FLAG_FOLD_WITHOUT_PLDDT = "fold_without_plddt"
FLAG_SPAN_UNRECORDED = "span_unrecorded"
FLAG_ECD_SATURATED = "ecd_saturated"
FLAG_NON_SURFACE = "non_surface_class"
FLAG_REFERENCE = "reference_not_a_candidate"

FLAG_MEANING = {
    FLAG_NO_FOLD: ("no structure is held for this protein, so score_model is the 0.3 penalty "
                   "— never a neutral, and never treated as an average fold"),
    FLAG_FOLD_WITHOUT_PLDDT: ("a structure is held but its mean pLDDT was not persisted, so "
                              "score_model is 0.8 — a recorded fold with an unrecorded "
                              "confidence, not a confident fold"),
    FLAG_SPAN_UNRECORDED: ("no extracellular span is recorded, so score_ecd is 0 and the product "
                           "is 0. ⚠ A named absence, never imputed"),
    FLAG_ECD_SATURATED: ("the extracellular span is at or above 200 aa, where score_ecd caps at "
                         "1.0; a longer span earns nothing further"),
    FLAG_NON_SURFACE: ("census_class is not `surface`, so score_membrane is 0.2. ⚠ Includes "
                       "`unclassified` and `class_conflict` (F-019) — neither is a surface claim"),
    FLAG_REFERENCE: ("an ADC is already directed at this antigen (data/adc_reference_mapping.csv, "
                     "D-029 / D-040), so it is a REFERENCE point and sorts after every candidate. "
                     "⚠ Its score is computed and comparable; the flag never enters the score"),
}


class ImplausiblePlddt(ValueError):
    """⚠⚠ Raised rather than clamped. `mean_plddt` is on the **0–100** scale (`db.models`), and
    the failure this guards is a *unit swap*: a 0–1 value would divide to ~0.008 and produce a
    row that ranks last for a fold that is actually excellent — a wrong-but-plausible number
    (`F-047`). Clamping would hide it; a neutral would fabricate it; so the load refuses and
    names the accession."""


def score_membrane(census_class: Any) -> float:
    """1.0 for `surface`, 0.2 for anything else — including an absent class.

    ⚠ An absent `census_class` takes 0.2 and is NOT an error: the roster records
    `unclassified` for 2,793 proteins, and the honest reading of *"we do not have a surface
    claim"* is the low factor, not the full one."""
    return MEMBRANE_SURFACE if _text(census_class) == SURFACE_CLASS else MEMBRANE_OTHER


def score_ecd(span_aa: Any) -> float:
    """`min(1.0, span_aa / 200)`, and **0** for a missing, zero or unusable span.

    ⚠ `bool` is refused explicitly: `isinstance(True, int)` is `True` in Python, so a
    truthiness flag reaching this field would otherwise score as a 1 aa span."""
    span = _whole_residues(span_aa)
    if span is None:
        return 0.0
    return min(1.0, span / ECD_SATURATION_AA)


def score_model(has_pdb: bool, mean_plddt: Any) -> float:
    """The fold factor, in the three cases the GO locks — and they are three, not two.

    ⚠⚠ *No fold* (0.3) and *fold whose confidence was not persisted* (0.8) are **different
    facts** and pooling them would either flatter 777 never-folded proteins or punish a fold we
    actually hold. `F-042` is why the second case exists at all: this pipeline has already
    shipped structures whose sibling numbers were discarded.
    """
    if not has_pdb:
        return MODEL_NO_FOLD
    plddt = _plddt(mean_plddt)
    if plddt is None:
        return MODEL_FOLD_WITHOUT_PLDDT
    return plddt / 100.0


@dataclass(frozen=True)
class StructuralScore:
    """One protein's score and the three factors it is the product of.

    ⚠ The components are carried, never re-derived by a consumer: a surface that recomputed
    `structural_score / score_ecd` to recover a factor would divide by zero on every
    span-unrecorded row, and `D-041`'s attribution discipline (the parts travel with the
    total) applies to an arithmetic product exactly as it does to a fitted one."""

    score_membrane: float
    score_ecd: float
    score_model: float
    structural_score: float
    has_fold: bool
    flags: tuple[str, ...] = field(default_factory=tuple)


def structural_score(
    census_class: Any,
    span_aa: Any,
    *,
    has_pdb: bool,
    mean_plddt: Any = None,
    is_reference: bool = False,
) -> StructuralScore:
    """The locked product, with its components and its flags.

    ⚠ `is_reference` reaches ONLY the flag list. There is no arithmetic path from it to
    `structural_score`, which is what lets a reference row be read as a yardstick against the
    candidates rather than a differently-scored thing."""
    membrane = score_membrane(census_class)
    ecd = score_ecd(span_aa)
    model = score_model(has_pdb, mean_plddt)

    flags: list[str] = []
    if not has_pdb:
        flags.append(FLAG_NO_FOLD)
    elif _plddt(mean_plddt) is None:
        flags.append(FLAG_FOLD_WITHOUT_PLDDT)
    span = _whole_residues(span_aa)
    if span is None:
        flags.append(FLAG_SPAN_UNRECORDED)
    elif span >= ECD_SATURATION_AA:
        flags.append(FLAG_ECD_SATURATED)
    if _text(census_class) != SURFACE_CLASS:
        flags.append(FLAG_NON_SURFACE)
    if is_reference:
        flags.append(FLAG_REFERENCE)

    return StructuralScore(
        score_membrane=membrane,
        score_ecd=ecd,
        score_model=model,
        structural_score=membrane * ecd * model,
        has_fold=bool(has_pdb),
        flags=tuple(flags),
    )


# ── ordering: candidates by score, references after all of them ──────────────


def rank_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Descending `structural_score`, **references sunk to the end**, ties broken by accession.

    ⚠⚠ THE SINK IS THE FIRST SORT KEY, NOT A POST-HOC MOVE. An antigen with an approved ADC
    would otherwise occupy the top of a list captioned *next targets*; sorting it to the end is
    the offline behaviour this lands, and `rank` is assigned **after** the sink so the top
    candidate is rank 1 rather than rank 1-behind-a-reference.

    ⚠ The accession tiebreak is not cosmetic: 1,998 of 3,467 manifest spans are under 200 aa and
    thousands of products collide, so without a total order two runs over identical inputs would
    disagree about rank and the idempotent replace would look like a change.
    """
    ordered = sorted(
        rows,
        key=lambda r: (
            bool(r.get("is_reference")),
            -float(r.get("structural_score") or 0.0),
            str(r.get("accession") or ""),
        ),
    )
    for i, row in enumerate(ordered, start=1):
        row["rank"] = i
    return ordered


# ── the population, and the reference set, both from committed files ─────────


@functools.lru_cache(maxsize=1)
def reference_accessions(path: Any = None) -> frozenset[str]:
    """Accessions with a cited ADC pointed at them — the reference sink, **by join**.

    ⚠ Reads `core.adc_reference.load_mapping()`, which raises `CurationError` on an uncited
    row (`D-029`). A failure to load is NOT swallowed into an empty set here: an empty
    reference set would silently promote NECTIN4 into the candidate list, which is the exact
    outcome the sink exists to prevent."""
    from core.adc_reference import ADC_MAPPING, load_mapping

    rows = load_mapping(path or ADC_MAPPING)
    return frozenset(
        (r.get("uniprot_accession") or "").strip().upper()
        for r in rows
        if (r.get("uniprot_accession") or "").strip()
    )


@functools.lru_cache(maxsize=1)
def census_labels(path: Any = None) -> dict[str, str]:
    """`accession -> gene`, from the committed labels CSV. Absent file ⇒ empty, and a row then
    serves `gene: null` — an unknown name, never a guessed one."""
    p = pathlib.Path(path or CENSUS_LABELS)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8", newline="") as fh:
        return {
            r["census_accession"]: (r.get("gene") or "").strip()
            for r in csv.DictReader(fh)
            if r.get("census_accession")
        }


def census_population(path: Any = None) -> list[dict[str, Any]]:
    """The population this rank is over: every row of `census_manifest.v7.csv`.

    ⚠⚠ **THE MANIFEST, NOT THE FOLDED CENSUS, AND NOT THE ROSTER.** Three candidate
    populations exist and the choice is stated rather than defaulted:
      * the **manifest** (3,467) — every census protein carrying a measured V2 extracellular
        span, i.e. every row for which `score_ecd` is a measurement. **This is the one.**
      * the **folded census** (2,690 in `census_features.v1.jsonl`) — would make the population
        a function of how much GPU time has been spent (`D-024`), and would drop tranche 5.
      * the **roster** (7,811) — 4,344 of those rows carry **no** span under V2, so `score_ecd`
        is 0 for every one of them and the formula cannot order them at all. Including them
        would pad the list with 4,344 zeroes that look like verdicts. They are named as
        out-of-population by `population_key`, not silently dropped.
    """
    p = pathlib.Path(path or CENSUS_MANIFEST)
    if not p.exists():
        return []
    genes = census_labels()
    out: list[dict[str, Any]] = []
    with p.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            acc = (r.get("census_accession") or "").strip().upper()
            if not acc:
                continue
            out.append({
                "accession": acc,
                "gene": genes.get(acc) or None,
                "census_class": (r.get("census_class") or "").strip() or None,
                "span_aa": _whole_residues(r.get("span_aa")),
                "tranche": _whole_residues(r.get("tranche")),
            })
    return out


# ── the version pin ──────────────────────────────────────────────────────────

_FORMULA_VERSION: Optional[str] = None


def formula_version() -> str:
    """A short hash of THIS module's source, the `core.features.feature_version()` pattern
    (`D-027`): a run persisted under a formula that has since changed is then detectable rather
    than silent. Derived, never a hand-typed `"v1"`."""
    global _FORMULA_VERSION
    if _FORMULA_VERSION is None:
        _FORMULA_VERSION = hashlib.sha256(
            pathlib.Path(__file__).read_bytes()
        ).hexdigest()[:12]
    return _FORMULA_VERSION


# ── coercion helpers, both refusing to guess ─────────────────────────────────


def _text(value: Any) -> str:
    return value.strip().lower() if isinstance(value, str) else ""


def _whole_residues(value: Any) -> Optional[int]:
    """A positive whole number, or `None`. The `census_cost_read._whole_residues` rule, applied
    to a span and a tranche: a `bool` is refused, a JSON `"442"` or `442.0` is the measurement,
    and a fraction of a residue is not a span."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, float):
        return int(value) if value > 0 and value.is_integer() else None
    if isinstance(value, str):
        s = value.strip()
        if s.isdigit():
            n = int(s)
            return n if n > 0 else None
    return None


def _plddt(value: Any) -> Optional[float]:
    """`mean_plddt` on the 0–100 scale, or `None` when it was not persisted.

    ⚠⚠ Raises `ImplausiblePlddt` on a value outside 0–100 **and on a value in (0, 1]** — the
    unit-swap case. 1.0 is a legal 0–100 pLDDT in arithmetic and an impossible one in fact
    (`D-039`'s bands put the census floor an order of magnitude above it), so admitting it
    would let a 0–1 fraction through as the finding it is not. **0.0 is admitted** — a
    persisted zero is a measurement this module has no licence to reinterpret."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ImplausiblePlddt(f"mean_plddt is a bool ({value!r}), not a confidence")
    if not isinstance(value, (int, float)):
        raise ImplausiblePlddt(f"mean_plddt {value!r} is not a number")
    plddt = float(value)
    if plddt < 0 or plddt > 100:
        raise ImplausiblePlddt(
            f"mean_plddt {plddt} is outside the 0–100 scale db.models declares")
    if 0 < plddt <= 1:
        raise ImplausiblePlddt(
            f"mean_plddt {plddt} looks like a 0–1 fraction on a 0–100 field. Refusing rather "
            f"than dividing by 100 again: that would rank an excellent fold last (F-047).")
    return plddt
