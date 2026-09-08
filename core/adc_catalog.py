"""D-119 / D-124 / D-136 / D-140 — ADC catalogs are dated JSON contracts.

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

**D-140** gives the pipeline shelf its own ``cancer_type`` and ``description``,
and it does **not** reuse D-136's machinery. An investigational agent has no FDA
indication to name, so the authority is the **trial registry** the row's own
citation already pointed at (ClinicalTrials.gov Conditions and lead sponsor) or
that citation's own body — and :func:`_check_pipeline_condition_source` **refuses
an FDA label authority here**, because borrowing one would promote a pipeline row
to approved through the source string. The substring audit is the same shape as
D-136's: every tumour token must be a literal substring of the
``conditions_verbatim`` text stored on the same row.

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
# D-140 adds the three programme fields — and they are the ONLY three. An
# investigational row still carries no DAR / efficacy / FDA-label field.
PIPELINE_FIELDS = (
    "id",
    "name",
    "antigen",
    "uniprot_accession",
    "development_stage",
    "phase",
    "source_citation",
    "cancer_type",
    "conditions_verbatim",
    "description",
)
PIPELINE_HEADER_FIELDS = (
    "catalog_id",
    "schema_version",
    "scope",
    "completeness",
    "mapping_sourced_as_of",
    "catalog_assembled_as_of",
    "conditions_reviewed_as_of",
    "registry_artifact",
)
PIPELINE_CONDITIONS_FIELD = "conditions_verbatim"
PIPELINE_DESCRIPTION_FIELD = "description"
# D-140 decision 3 — a pipeline tumour type is a human read of registry or citation
# text, every time. `official` is refused (this row has no FDA anything) and so is
# `derived` (a tumour type cannot be computed from a slug, D-136 decision 5).
PIPELINE_CANCER_TYPE_CONFIDENCES = ("reviewed",)
# The verbatim anchor is either the registry's own Conditions as returned
# (`official`) or this row's curated on-disk citation quoted whole (`reviewed`).
PIPELINE_CONDITIONS_CONFIDENCES = ("official", "reviewed")
PIPELINE_DESCRIPTION_CONFIDENCES = ("reviewed",)
# The two authorities D-140 admits, and nothing else.
PIPELINE_CONDITION_AUTHORITIES = (
    "clinicaltrials.gov",
    "data/adc_reference_mapping.csv",
    "source_citation",
)
# ⚠ An FDA indication authority on a PIPELINE row is refused, not accepted as a
# stronger source: these agents are not approved, and a source string is not the
# place to promote one (D-140 decision 6).
FDA_LABEL_AUTHORITY_TOKENS = (
    "api.fda.gov",
    "accessdata.fda.gov",
    "drugs@fda",
    "drugsfda",
    "drug/label.json",
    "indications and usage",
)
NCT_ID_PATTERN = re.compile(r"NCT\d{8}")
# A description is a maker and one line, not a paragraph.
PIPELINE_DESCRIPTION_SEPARATOR = " — "
PIPELINE_DESCRIPTION_MAX_CHARS = 240
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


def _check_pipeline_condition_source(label: str, source: str) -> None:
    """A pipeline programme claim is registry text or citation text — or nothing.

    Two refusals, and they close different holes. The D-093 denylist is the same
    one D-136 uses: staining is not what a trial is enrolling. The FDA-authority
    refusal is D-140's own: an investigational row that cites a drug label has
    either found somebody else's approval or invented one.
    """
    lowered = source.lower()
    for token in STAINING_SOURCE_TOKENS:
        if token in lowered:
            raise CatalogError(
                f"{label} source names {token!r}: HPA / staining is not what a trial "
                "enrols or what a citation states (D-093). A pipeline cancer type may "
                "not be joined from IHC, the derived association map, or the census."
            )
    for token in FDA_LABEL_AUTHORITY_TOKENS:
        if token in lowered:
            raise CatalogError(
                f"{label} source names the FDA label authority {token!r}: this row is "
                "investigational and has no FDA indication (D-140 decision 6). Citing "
                "one here would promote a pipeline row to approved in a source string."
            )
    if not any(auth in lowered for auth in PIPELINE_CONDITION_AUTHORITIES):
        raise CatalogError(
            f"{label} source names no D-140 authority {PIPELINE_CONDITION_AUTHORITIES}"
        )
    if not re.search(r"\d{4}-\d{2}-\d{2}", source):
        raise CatalogError(f"{label} source carries no ISO retrieval / curation date")


def _check_pipeline_conditions_field(label: str, obj: Any, citation: Any) -> None:
    """``conditions_verbatim``: the text a tumour type may be audited against.

    ``official`` means the registry's own Conditions as returned, and the source must
    name the record. ``reviewed`` means this row's curated citation quoted whole — so
    the loader checks it really is a quote, rather than trusting the word.
    """
    if not _is_field(obj):
        raise CatalogError(f"{label} is not a {{value, source, as_of, confidence}} field")
    if obj["confidence"] not in PIPELINE_CONDITIONS_CONFIDENCES:
        raise CatalogError(
            f"{label} confidence {obj['confidence']!r} is not in "
            f"{PIPELINE_CONDITIONS_CONFIDENCES}"
        )
    if not obj["source"] or not obj["as_of"]:
        raise CatalogError(f"{label} is missing source or as_of")
    _check_pipeline_condition_source(label, obj["source"])
    value = obj["value"]
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{label} value must be the stored text, or null")
    if obj["confidence"] == "official":
        if not NCT_ID_PATTERN.search(obj["source"]):
            raise CatalogError(
                f"{label} claims 'official' but its source names no NCT record: only a "
                "registry record returns Conditions text (D-140 decision 2)"
            )
        return
    # `reviewed` — it must actually be a quote of the citation already on this row.
    citation_value = citation.get("value") if isinstance(citation, dict) else None
    if not citation_value or _normalise_indication_text(value) not in _normalise_indication_text(
        str(citation_value)
    ):
        raise CatalogError(
            f"{label} is 'reviewed' but is not a literal quote of this row's own "
            "source_citation: a verbatim anchor nobody can check against something "
            "already on disk is the invented text this field exists to refuse "
            "(D-140 decision 2)"
        )


def _check_pipeline_cancer_type_field(label: str, obj: Any, conditions: Any) -> None:
    """``cancer_type`` on a pipeline row: audited against that row's own stored text.

    ⚠⚠ The load-bearing check, D-136's rule imported wholesale (D-140 decision 4).
    A tumour typed from memory does not fail review — it fails here.
    """
    if not _is_field(obj):
        raise CatalogError(f"{label} is not a {{value, source, as_of, confidence}} field")
    if obj["confidence"] not in PIPELINE_CANCER_TYPE_CONFIDENCES:
        raise CatalogError(
            f"{label} confidence {obj['confidence']!r} is not in "
            f"{PIPELINE_CANCER_TYPE_CONFIDENCES}: reducing registry or citation text to "
            "a tumour type is a human read, and an investigational agent has no "
            "official indication to inherit one from (D-140 decision 3)"
        )
    if not obj["source"] or not obj["as_of"]:
        raise CatalogError(f"{label} is missing source or as_of")
    _check_pipeline_condition_source(label, obj["source"])

    value = obj["value"]
    if value is None:
        # A named absence: the source above already had to say what was read and
        # came back without a tumour type (D-140 decision 5).
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

    conditions_value = conditions.get("value") if isinstance(conditions, dict) else None
    if not conditions_value:
        raise CatalogError(
            f"{label} carries tumour types but {PIPELINE_CONDITIONS_FIELD} on the same "
            "row has no stored text to audit them against (D-140 decision 4)"
        )
    haystack = _normalise_indication_text(str(conditions_value))
    for token in value:
        if _normalise_indication_text(token) not in haystack:
            raise CatalogError(
                f"{label} tumour type {token!r} is not in this row's "
                f"{PIPELINE_CONDITIONS_FIELD} text: a tumour this row's own registry "
                "record and citation do not state (D-140 decision 4)"
            )


def _check_pipeline_description_field(label: str, obj: Any) -> None:
    """``description``: who is making it, then one line — or a named absence.

    The maker is the load-bearing half, so it is audited the only way a file-local
    check can audit it: the text before the em dash must appear in the source string,
    which is where the registry's ``leadSponsor`` / the citation's own wording is
    quoted (D-140 decision 5).
    """
    if not _is_field(obj):
        raise CatalogError(f"{label} is not a {{value, source, as_of, confidence}} field")
    if obj["confidence"] not in PIPELINE_DESCRIPTION_CONFIDENCES:
        raise CatalogError(
            f"{label} confidence {obj['confidence']!r} is not in "
            f"{PIPELINE_DESCRIPTION_CONFIDENCES}: a one-line programme summary is a "
            "human read (D-140 decision 5)"
        )
    if not obj["source"] or not obj["as_of"]:
        raise CatalogError(f"{label} is missing source or as_of")
    _check_pipeline_condition_source(label, obj["source"])

    value = obj["value"]
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(
            f"{label} value must be a maker and one line, or null for a named absence "
            "— a blank that looks like data is refused (D-140 decision 5)"
        )
    if len(value) > PIPELINE_DESCRIPTION_MAX_CHARS:
        raise CatalogError(
            f"{label} value is {len(value)} characters: a programme one-liner is capped "
            f"at {PIPELINE_DESCRIPTION_MAX_CHARS} (D-140 decision 5)"
        )
    if PIPELINE_DESCRIPTION_SEPARATOR not in value:
        raise CatalogError(
            f"{label} value must read 'maker{PIPELINE_DESCRIPTION_SEPARATOR}one line': "
            "the maker is the half this field exists for, and it has to be separable "
            "to be audited (D-140 decision 5)"
        )
    maker, _, line = value.partition(PIPELINE_DESCRIPTION_SEPARATOR)
    if not maker.strip() or not line.strip():
        raise CatalogError(f"{label} value is missing either the maker or the one line")
    if _normalise_indication_text(maker) not in _normalise_indication_text(obj["source"]):
        raise CatalogError(
            f"{label} maker {maker!r} does not appear in this field's own source: a "
            "sponsor named from memory is exactly the guess D-140 decision 5 refuses"
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
            if name in (
                CANCER_TYPE_FIELD,
                PIPELINE_CONDITIONS_FIELD,
                PIPELINE_DESCRIPTION_FIELD,
            ):
                continue
            _check_field(f"pipeline[{i}].{name}", row[name])
        _check_pipeline_conditions_field(
            f"pipeline[{i}].{PIPELINE_CONDITIONS_FIELD}",
            row[PIPELINE_CONDITIONS_FIELD],
            row["source_citation"],
        )
        _check_pipeline_cancer_type_field(
            f"pipeline[{i}].{CANCER_TYPE_FIELD}",
            row[CANCER_TYPE_FIELD],
            row[PIPELINE_CONDITIONS_FIELD],
        )
        _check_pipeline_description_field(
            f"pipeline[{i}].{PIPELINE_DESCRIPTION_FIELD}", row[PIPELINE_DESCRIPTION_FIELD]
        )
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
