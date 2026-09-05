"""D-119 — ADC-A: the FDA-approved catalog is a dated JSON contract.

Pure and fixture-testable (no network, no DB, no GPU). The live openFDA query
dated ``data/adcs/adcs.v1.json``; it does not run here. Weekly Drugs@FDA watch
is Emma's ops lane (``data/adcs/README.md``) — never this module and never the
gate (D-029: a live FDA call must not redden CI).

This is **not** ``core.adc_reference``. That file is the scorer's Group B/C
instrument. This catalog is the approved-drug roster ADC-B will consume.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parent.parent
CATALOG_V1 = _ROOT / "data" / "adcs" / "adcs.v1.json"

FIELD_KEYS = ("value", "source", "as_of", "confidence")
CONFIDENCES = ("official", "reviewed", "derived")
# Identity + approval + reviewed target. No DAR / efficacy / chemistry (D-119 dec 8).
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
)
HEADER_FIELDS = (
    "catalog_id",
    "schema_version",
    "scope",
    "completeness",
    "approvals_reconciled_as_of",
    "antigen_mapping_reviewed_as_of",
    "emma_watch",
    "named_exclusions",
)
INVENTED_SCIENCE_KEYS = ("dar", "ic50", "orr", "pfs", "os", "payload", "linker")
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
            _check_field(f"adcs[{i}].{name}", row[name])
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
