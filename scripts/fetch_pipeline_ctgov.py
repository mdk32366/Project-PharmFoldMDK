"""D-139 — fetch the ClinicalTrials.gov material behind the pipeline catalog, ONCE.

⚠ **Ops lane, never the gate.** This is the only thing in the repo that talks to
ClinicalTrials.gov. It writes a dated artefact
(``data/adcs/artifacts/ctgov.pipeline.<date>.json``) and then every reader — the
catalog file, ``core/adc_catalog.py``, the tests — works from that artefact and
from ``data/adcs/adcs.pipeline.v1.json``. D-029: a live registry call must not
redden CI, so nothing under ``tests/`` imports this module.

Two kinds of lookup, and the difference is recorded per row rather than smoothed:

* ``nct`` — the row's own ``source_citation`` already names an ``NCT________``
  id. Nothing is discovered; the id is read off disk and fetched.
* ``acronym`` — the citation names the trial by ACRONYM (``IDeate-Lung01``,
  ``INTELLANCE-1``) and the registry resolves that acronym to an id. ⚠ This is
  the step that could invent a trial, so the artefact stores the returned
  ``acronym`` and ``interventions`` and :mod:`tests.test_d139_pipeline_cancer_type`
  refuses a match whose interventions do not name the row's own drug.

A row with neither is queried by intervention name anyway (``searched`` kind), so
that its emptiness is a **searched** absence rather than an unexamined one.

Usage (ops, from the repo root)::

    python scripts/fetch_pipeline_ctgov.py --as-of 2026-09-08
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_V1 = ROOT / "data" / "adcs" / "adcs.pipeline.v1.json"
ARTIFACT_DIR = ROOT / "data" / "adcs" / "artifacts"
API = "https://clinicaltrials.gov/api/v2/studies"
NCT_RE = re.compile(r"NCT\d{8}")

# The acronyms a citation names without an id. ⚠ Keys are read back out of the
# citation text before use, so an acronym nobody cited cannot be smuggled in.
ACRONYMS: dict[str, tuple[str, ...]] = {
    "ifinatamab-deruxtecan": ("IDeate-Lung01", "IDeate-PanTumor01"),
    "depatuxizumab-mafodotin": ("INTELLANCE-1",),
}

FIELDS = ",".join(
    (
        "protocolSection.identificationModule",
        "protocolSection.statusModule.overallStatus",
        "protocolSection.conditionsModule",
        "protocolSection.designModule.phases",
        "protocolSection.armsInterventionsModule.interventions",
        "protocolSection.sponsorCollaboratorsModule.leadSponsor",
    )
)


def _get(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 - ops lane, fixed host
        return json.loads(resp.read().decode("utf-8"))


def _summarise(protocol: dict[str, Any]) -> dict[str, Any]:
    ident = protocol.get("identificationModule", {})
    return {
        "nct_id": ident.get("nctId"),
        "acronym": ident.get("acronym"),
        "brief_title": ident.get("briefTitle"),
        "organization": ident.get("organization", {}).get("fullName"),
        "lead_sponsor": protocol.get("sponsorCollaboratorsModule", {})
        .get("leadSponsor", {})
        .get("name"),
        "overall_status": protocol.get("statusModule", {}).get("overallStatus"),
        "phases": protocol.get("designModule", {}).get("phases", []),
        "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
        "interventions": [
            i.get("name")
            for i in protocol.get("armsInterventionsModule", {}).get("interventions", [])
        ],
    }


def fetch_by_id(nct_id: str) -> dict[str, Any]:
    return _summarise(_get(f"{API}/{nct_id}?fields={FIELDS}")["protocolSection"])


def search(param: str, term: str, page_size: int = 10) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({param: term, "pageSize": page_size, "fields": FIELDS})
    payload = _get(f"{API}?{query}")
    return [_summarise(s["protocolSection"]) for s in payload.get("studies", [])]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", required=True, help="retrieval date, ISO (YYYY-MM-DD)")
    args = parser.parse_args()

    pipeline = json.loads(PIPELINE_V1.read_text(encoding="utf-8"))
    lookups: list[dict[str, Any]] = []
    studies: dict[str, dict[str, Any]] = {}

    for row in pipeline["pipeline"]:
        row_id = row["id"]["value"]
        name = row["name"]["value"]
        citation = row["source_citation"]["value"]
        cited_ncts = NCT_RE.findall(citation)
        cited_acronyms = [a for a in ACRONYMS.get(row_id, ()) if a.lower() in citation.lower()]

        for nct_id in cited_ncts:
            studies[nct_id] = fetch_by_id(nct_id)
            lookups.append(
                {
                    "row_id": row_id,
                    "kind": "nct",
                    "query": nct_id,
                    "why": "id read off this row's own source_citation",
                    "matched": [nct_id],
                }
            )
            time.sleep(0.2)

        for acronym in cited_acronyms:
            hits = search("query.term", acronym)
            # ⚠ EXACT acronym equality, and no fallback. A near-miss on a title would
            # let this script CHOOSE which study the citation meant, which is the one
            # judgement it must not make silently. An acronym that resolves to nothing
            # is written out as an empty match and stays a named absence downstream.
            keep = [
                h
                for h in hits
                if (h["acronym"] or "").lower().replace("-", "")
                == acronym.lower().replace("-", "")
            ][:1]
            for hit in keep:
                studies[hit["nct_id"]] = hit
            lookups.append(
                {
                    "row_id": row_id,
                    "kind": "acronym",
                    "query": acronym,
                    "why": "acronym named in this row's source_citation; registry resolved it",
                    "matched": [h["nct_id"] for h in keep],
                }
            )
            time.sleep(0.2)

        if not cited_ncts and not cited_acronyms:
            hits = search("query.intr", name.split("(")[0].strip())
            for hit in hits:
                studies[hit["nct_id"]] = hit
            lookups.append(
                {
                    "row_id": row_id,
                    "kind": "searched",
                    "query": name.split("(")[0].strip(),
                    "why": "no trial named on disk; queried so the absence is a SEARCHED one",
                    "matched": [h["nct_id"] for h in hits],
                }
            )
            time.sleep(0.2)

    artifact = {
        "artifact_id": "ctgov.pipeline",
        "retrieved_as_of": args.as_of,
        "endpoint": API,
        "api": "ClinicalTrials.gov REST API v2",
        "note": (
            "D-139 — raw registry material behind data/adcs/adcs.pipeline.v1.json, "
            "fetched once on the retrieval date by scripts/fetch_pipeline_ctgov.py. "
            "Nothing in tests/ or core/ makes a network call; they read this file. "
            "A lookup of kind 'searched' that matched nothing is a recorded negative "
            "result, not a gap."
        ),
        "lookups": lookups,
        "studies": dict(sorted(studies.items())),
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    out = ARTIFACT_DIR / f"ctgov.pipeline.{args.as_of}.json"
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out} — {len(studies)} studies, {len(lookups)} lookups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
