"""D-119 / D-124 / D-136 — ADC catalogs are dated JSON contracts.

Pure and fixture-testable (no network, no DB, no GPU). The live openFDA queries
dated ``data/adcs/adcs.v1.json``; they do not run here. Weekly Drugs@FDA watch
is Emma's ops lane (``data/adcs/README.md``) — never this module and never the
gate (D-029: a live FDA call must not redden CI).

**D-136** fills the ``cancer_type`` column D-122 shipped as a named absence. Two
openFDA endpoints now back this file and they answer different questions:
``/drug/drugsfda.json`` is approval identity (D-119), ``/drug/label.json`` is the
SPL §1 INDICATIONS AND USAGE text. Each row carries the reviewed tumour-type list
**and** the official text it was reduced from, and
:func:`_check_cancer_type_field` refuses any category that is not a literal
substring of that row's own stored text. ⚠ HPA / census staining may never reach
this column (D-093: staining is not an FDA indication).

This is **not** ``core.adc_reference``. That file is the scorer's Group B/C
instrument. ``adcs.v1.json`` is the approved-drug roster ADC-B (D-122) consumes.
``adcs.pipeline.v1.json`` and ``access.v1.json`` are the D-124 / ADC-C-A
siblings — investigational rows and trials/RTT framing — and are never merged
into v1.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parent.parent
CATALOG_V1 = _ROOT / "data" / "adcs" / "adcs.v1.json"
PIPELINE_V1 = _ROOT / "data" / "adcs" / "adcs.pipeline.v1.json"
ACCESS_V1 = _ROOT / "data" / "adcs" / "access.v1.json"

FIELD_KEYS = ("value", "source", "as_of", "confidence")
CONFIDENCES = ("official", "reviewed", "derived")
# Identity + approval + reviewed target, plus the D-136 indication pair. Still no
# DAR / efficacy / chemistry (D-119 dec 8).
ADC_FIELDS = (
    "id",
    "inn",
    "active_ingredient",
    "brand_name",
    "application_number",
    "current_application_approval_date",
    "marketing_status",
    "sponsor",
    "antigen",
    "uniprot_accession",
    "cancer_type",
    "label_indications_verbatim",
)
HEADER_FIELDS = (
    "catalog_id",
    "schema_version",
    "scope",
    "completeness",
    "approvals_reconciled_as_of",
    "antigen_mapping_reviewed_as_of",
    "indications_reviewed_as_of",
    "emma_watch",
    "named_exclusions",
)
CANCER_TYPE_FIELD = "cancer_type"
VERBATIM_FIELD = "label_indications_verbatim"
# D-136 decision 5 — a cancer type is FDA's indication text or nothing. `derived` is
# refused: unlike an id slug or an INN stem, a tumour type cannot be computed.
CANCER_TYPE_CONFIDENCES = ("official", "reviewed")
INDICATION_AUTHORITIES = (
    "api.fda.gov/drug/label.json",
    "accessdata.fda.gov",
    "drugs@fda",
    "drugsfda",
)
# D-093: HPA IHC is STAINING over a survey population. It is not an FDA indication, and
# the two must never meet in this column. Also refuses the project's own derived
# association map (D-053) as a stand-in for a label.
STAINING_SOURCE_TOKENS = (
    "proteinatlas",
    "protein atlas",
    "pathology.tsv",
    "normal_tissue.tsv",
    "staining",
    "stained",
    "quasi-h",
    "quasi_h",
    "h-score",
    "api/associations",
    "cancer_associations",
    "census",
)
# D-124 pipeline rows: identity + reviewed target + closed stage/phase. No invent.
PIPELINE_FIELDS = (
    "id",
    "name",
    "antigen",
    "uniprot_accession",
    "development_stage",
    "phase",
    "source_citation",
)
PIPELINE_HEADER_FIELDS = (
    "catalog_id",
    "schema_version",
    "scope",
    "completeness",
    "mapping_sourced_as_of",
    "catalog_assembled_as_of",
)
# Architect D-124 phase pin — reject all others.
PHASE_VOCAB = (
    "Phase 1",
    "Phase 1/2",
    "Phase 2",
    "Phase 3",
    "BLA/NDA submitted",
    "Other",
)
DEVELOPMENT_STAGES = ("clinical", "preclinical")
ACCESS_FIELDS = (
    "catalog_id",
    "schema_version",
    "scope",
    "completeness",
    "as_of",
    "disclaimer",
    "clinical_trials_registry",
    "expanded_access_fda",
    "right_to_try_statute",
    "right_to_try_public_law",
    "right_to_try_fda",
    "named_nct_ids_from_pipeline",
)
INVENTED_SCIENCE_KEYS = (
    "dar",
    "ic50",
    "orr",
    "pfs",
    "os",
    "payload",
    "linker",
    "indication",
    "efficacy",
    "response_rate",
)
# v1 is FDA-approved / currently marketed only. These tokens must never appear as a row id.
OUT_OF_SCOPE_IDS = (
    "lumoxiti",
    "moxetumomab-pasudotox",
    "ifinatamab-deruxtecan",
    "right-to-try",
    "pipeline",
)


class CatalogError(Exception):
    """A structural fault in the ADC catalog: missing envelope, bad confidence, or out-of-scope row."""


def _is_field(obj: Any) -> bool:
    return isinstance(obj, dict) and set(obj.keys()) == set(FIELD_KEYS)


def _check_field(label: str, obj: Any) -> None:
    if not _is_field(obj):
        raise CatalogError(f"{label} is not a {{value, source, as_of, confidence}} field")
    if obj["confidence"] not in CONFIDENCES:
        raise CatalogError(f"{label} confidence {obj['confidence']!r} is not in {CONFIDENCES}")
    if obj["value"] is None or obj["value"] == "":
        raise CatalogError(f"{label} value is empty")
    if not obj["source"] or not obj["as_of"]:
        raise CatalogError(f"{label} is missing source or as_of")


def _normalise_indication_text(text: str) -> str:
    """Lowercase, punctuation → single spaces. Both sides of the D-136 substring audit.

    Folds the differences that are not the reader's point — case, hyphens, the ``(NSCLC)``
    parenthetical, the non-breaking hyphen FDA's own SPL text uses — while leaving word
    order and wording intact. ``Non-small cell lung cancer`` matches the label's
    ``non-small cell lung cancer (NSCLC)``; ``Urothelial cancer`` does not match a label
    that never says it.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _check_indication_source(label: str, source: str) -> None:
    """A cancer type is FDA indication text or nothing (D-136 decision 5)."""
    lowered = source.lower()
    for token in STAINING_SOURCE_TOKENS:
        if token in lowered:
            raise CatalogError(
                f"{label} source names {token!r}: HPA / staining is not an FDA indication "
                "(D-093). A cancer type may not be joined from IHC, the derived association "
                "map, or the census."
            )
    if any(auth in lowered for auth in INDICATION_AUTHORITIES):
        return
    if re.search(r"\d{4}-\d{2}-\d{2}", source):
        return
    raise CatalogError(
        f"{label} source names no FDA indication authority {INDICATION_AUTHORITIES} and "
        "no dated secondary citation (D-136 decision 5)"
    )


def _check_verbatim_field(label: str, obj: Any) -> None:
    """``label_indications_verbatim``: FDA's own section 1 text, or a named absence."""
    if not _is_field(obj):
        raise CatalogError(f"{label} is not a {{value, source, as_of, confidence}} field")
    if obj["confidence"] not in CONFIDENCES:
        raise CatalogError(f"{label} confidence {obj['confidence']!r} is not in {CONFIDENCES}")
    if not obj["source"] or not obj["as_of"]:
        raise CatalogError(f"{label} is missing source or as_of")
    value = obj["value"]
    if value is None:
        _check_indication_source(label, obj["source"])
        return
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{label} value must be the label text as returned, or null")
    if obj["confidence"] != "official":
        raise CatalogError(
            f"{label} confidence {obj['confidence']!r} must be 'official': this field is "
            "FDA's own section 1 text as the endpoint returned it (D-136 decision 1)"
        )
    _check_indication_source(label, obj["source"])


def _check_cancer_type_field(label: str, obj: Any, verbatim: Any) -> None:
    """``cancer_type``: a reviewed tumour-type list audited against its own row's label.

    ⚠⚠ THE LOAD-BEARING CHECK (D-136 decision 2). Every token must be a literal
    substring of the official text stored on the same row. A tumour type typed from
    memory does not fail review — it fails here, because a word FDA's text does not
    contain cannot pass a substring test.
    """
    if not _is_field(obj):
        raise CatalogError(f"{label} is not a {{value, source, as_of, confidence}} field")
    if obj["confidence"] not in CANCER_TYPE_CONFIDENCES:
        raise CatalogError(
            f"{label} confidence {obj['confidence']!r} is not in {CANCER_TYPE_CONFIDENCES}: "
            "a cancer type cannot be derived the way an id slug or an INN stem can "
            "(D-136 decision 5)"
        )
    if not obj["source"] or not obj["as_of"]:
        raise CatalogError(f"{label} is missing source or as_of")
    _check_indication_source(label, obj["source"])

    value = obj["value"]
    if value is None:
        # A named absence, never a blank that looks like data (D-136 decision 6). The
        # source above already had to name the query that came back without text.
        return
    if not isinstance(value, list) or not value:
        raise CatalogError(
            f"{label} value must be a non-empty list of tumour types, or null for a "
            "named absence — a bare string is not data (D-119 decision 2)"
        )
    if any(not isinstance(t, str) or not t.strip() for t in value):
        raise CatalogError(f"{label} value has an empty or non-string tumour type")
    if len({t.strip().lower() for t in value}) != len(value):
        raise CatalogError(f"{label} value repeats a tumour type")

    verbatim_value = verbatim.get("value") if isinstance(verbatim, dict) else None
    if not verbatim_value:
        raise CatalogError(
            f"{label} carries tumour types but {VERBATIM_FIELD} on the same row has no "
            "official text to audit them against (D-136 decision 2): a category with "
            "nothing to check it is exactly the invented string this field refuses"
        )
    haystack = _normalise_indication_text(verbatim_value)
    for token in value:
        if _normalise_indication_text(token) not in haystack:
            raise CatalogError(
                f"{label} tumour type {token!r} is not in this row's {VERBATIM_FIELD} "
                "text: an FDA indication this label does not state (D-136 decision 2)"
            )


def _walk_forbidden_keys(obj: Any, trail: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            here = f"{trail}.{k}" if trail else k
            if k.lower() in INVENTED_SCIENCE_KEYS:
                raise CatalogError(
                    f"{here} is an invented-science key refused by D-119 decision 8"
                )
            _walk_forbidden_keys(v, here)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_forbidden_keys(v, f"{trail}[{i}]")


def load_catalog(path: Any = CATALOG_V1) -> dict[str, Any]:
    """Load and validate ``adcs.v1.json``. Raises ``CatalogError`` on a structural fault."""
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise CatalogError("catalog root must be an object")
    if "adcs" not in data:
        raise CatalogError("catalog is missing adcs")
    _walk_forbidden_keys({k: v for k, v in data.items() if k != "adcs"})
    for name in HEADER_FIELDS:
        if name not in data:
            raise CatalogError(f"catalog is missing header field {name}")
        _check_field(name, data[name])
    if data["scope"]["value"] != "fda_approved_only":
        raise CatalogError("v1 scope must be fda_approved_only")
    rows = data["adcs"]
    if not isinstance(rows, list) or not rows:
        raise CatalogError("adcs must be a non-empty list")
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise CatalogError(f"adcs[{i}] is not an object")
        _walk_forbidden_keys(row, f"adcs[{i}]")
        for name in ADC_FIELDS:
            if name not in row:
                raise CatalogError(f"adcs[{i}] is missing {name}")
            if name in (CANCER_TYPE_FIELD, VERBATIM_FIELD):
                continue
            _check_field(f"adcs[{i}].{name}", row[name])
        _check_verbatim_field(f"adcs[{i}].{VERBATIM_FIELD}", row[VERBATIM_FIELD])
        _check_cancer_type_field(
            f"adcs[{i}].{CANCER_TYPE_FIELD}", row[CANCER_TYPE_FIELD], row[VERBATIM_FIELD]
        )
        extra = set(row) - set(ADC_FIELDS)
        if extra:
            raise CatalogError(f"adcs[{i}] has extra keys {sorted(extra)}")
        adc_id = row["id"]["value"]
        if adc_id in seen:
            raise CatalogError(f"duplicate catalog id {adc_id!r}")
        if adc_id in OUT_OF_SCOPE_IDS:
            raise CatalogError(f"{adc_id} is ADC-C / excluded, not a v1 row")
        if row["marketing_status"]["value"] != "Prescription":
            raise CatalogError(
                f"adcs[{i}] marketing_status {row['marketing_status']['value']!r} "
                "is not Prescription (v1 is currently marketed FDA-approved only)"
            )
        seen.add(adc_id)
    return data


def list_adcs(path: Any = CATALOG_V1) -> dict[str, Any]:
    """The catalog object ``GET /api/adcs`` serves."""
    return load_catalog(path)


def get_adc(adc_id: str, path: Any = CATALOG_V1) -> Optional[dict[str, Any]]:
    """One row by derived id, or ``None`` (the route 404s)."""
    wanted = (adc_id or "").strip()
    for row in load_catalog(path)["adcs"]:
        if row["id"]["value"] == wanted:
            return row
    return None


def load_pipeline(path: Any = PIPELINE_V1, approved_path: Any = CATALOG_V1) -> dict[str, Any]:
    """Load and validate ``adcs.pipeline.v1.json``. Raises ``CatalogError`` on a structural fault."""
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise CatalogError("pipeline root must be an object")
    if "pipeline" not in data:
        raise CatalogError("pipeline catalog is missing pipeline")
    _walk_forbidden_keys({k: v for k, v in data.items() if k != "pipeline"})
    for name in PIPELINE_HEADER_FIELDS:
        if name not in data:
            raise CatalogError(f"pipeline catalog is missing header field {name}")
        _check_field(name, data[name])
    if data["scope"]["value"] != "pipeline_investigational":
        raise CatalogError("pipeline scope must be pipeline_investigational")
    if data["completeness"]["value"] != "floor_not_census":
        raise CatalogError("pipeline completeness must be floor_not_census")
    extra_header = set(data) - set(PIPELINE_HEADER_FIELDS) - {"pipeline"}
    if extra_header:
        raise CatalogError(f"pipeline catalog has extra keys {sorted(extra_header)}")
    rows = data["pipeline"]
    if not isinstance(rows, list) or not rows:
        raise CatalogError("pipeline must be a non-empty list")
    approved_ids = {row["id"]["value"] for row in load_catalog(approved_path)["adcs"]}
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise CatalogError(f"pipeline[{i}] is not an object")
        _walk_forbidden_keys(row, f"pipeline[{i}]")
        for name in PIPELINE_FIELDS:
            if name not in row:
                raise CatalogError(f"pipeline[{i}] is missing {name}")
            _check_field(f"pipeline[{i}].{name}", row[name])
        extra = set(row) - set(PIPELINE_FIELDS)
        if extra:
            raise CatalogError(f"pipeline[{i}] has extra keys {sorted(extra)}")
        stage = row["development_stage"]["value"]
        if stage not in DEVELOPMENT_STAGES:
            raise CatalogError(
                f"pipeline[{i}] development_stage {stage!r} is not in {DEVELOPMENT_STAGES}"
            )
        phase = row["phase"]["value"]
        if phase not in PHASE_VOCAB:
            raise CatalogError(
                f"pipeline[{i}] phase {phase!r} is not in the D-124 closed vocab"
            )
        adc_id = row["id"]["value"]
        if adc_id in seen:
            raise CatalogError(f"duplicate pipeline id {adc_id!r}")
        if adc_id in approved_ids:
            raise CatalogError(
                f"{adc_id} is an approved v1 row; pipeline must not merge approved"
            )
        seen.add(adc_id)
    return data


def list_pipeline(path: Any = PIPELINE_V1) -> dict[str, Any]:
    """The catalog object ``GET /api/adcs/pipeline`` serves."""
    return load_pipeline(path)


def get_pipeline_adc(adc_id: str, path: Any = PIPELINE_V1) -> Optional[dict[str, Any]]:
    """One pipeline row by derived id, or ``None`` (the route 404s)."""
    wanted = (adc_id or "").strip()
    for row in load_pipeline(path)["pipeline"]:
        if row["id"]["value"] == wanted:
            return row
    return None


def load_access(path: Any = ACCESS_V1) -> dict[str, Any]:
    """Load and validate ``access.v1.json``. Raises ``CatalogError`` on a structural fault."""
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise CatalogError("access root must be an object")
    _walk_forbidden_keys(data)
    extra = set(data) - set(ACCESS_FIELDS)
    if extra:
        raise CatalogError(f"access payload has extra keys {sorted(extra)}")
    for name in ACCESS_FIELDS:
        if name not in data:
            raise CatalogError(f"access payload is missing {name}")
        _check_field(name, data[name])
    if data["scope"]["value"] != "trials_and_right_to_try_informational":
        raise CatalogError("access scope must be trials_and_right_to_try_informational")
    if data["completeness"]["value"] != "floor_not_census":
        raise CatalogError("access completeness must be floor_not_census")
    disclaimer = data["disclaimer"]["value"]
    if not isinstance(disclaimer, str):
        raise CatalogError("access disclaimer value must be a string")
    lowered = disclaimer.lower()
    for token in ("not medical advice", "not legal advice", "not a treatment recommendation"):
        if token not in lowered:
            raise CatalogError(f"access disclaimer is missing {token!r}")
    return data


def get_access(path: Any = ACCESS_V1) -> dict[str, Any]:
    """The object ``GET /api/adcs/access`` serves."""
    return load_access(path)
