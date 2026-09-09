#!/usr/bin/env python3
"""D-149 — fetch the SEER official aggregate burden artefact from SEER*Explorer.

⚠⚠ THIS SCRIPT TOUCHES THE NETWORK AND THE LOADER DOES NOT. That split is deliberate and it is
the whole reason there are two files: `scripts/seer_cancer_burden.py` reads the **committed**
artefact and can never reach seer.cancer.gov, so a serving host cannot silently re-derive a
different number than the one this repository was reviewed with. Re-running this script is a
**new ingest of a different release**, not a refresh — it rewrites the sha256 and the loader will
say so.

WHAT IT FETCHES. SEER*Explorer's own JSON backend
(`/statistics-network/explorer/source/content_writers/render_region_5.php`) at
`graph_type=10` ("Recent Rates") — the **official** April release, all eligible registries.

⚠ NOT the Preliminary Incidence Estimates (`data_type=3`). `D-093 amendment 6` disqualified that
product by its own documentation — *"selected registries meeting predefined completeness
criteria"*, *"Subject to revision: Yes"*, and a registry selection **re-derived each year**, which
is one name over N populations. `PRELIMINARY_DATA_TYPE` below exists only to be excluded by name.

⚠ NOT SEER Research Data / Research Plus. No case-level record is fetched, and no DUA is involved.

⚠⚠ THE TRAP THIS SCRIPT EXISTS TO REFUSE, AND IT IS NOT HYPOTHETICAL — measured 2026-09-09.
`render_region_5.php` **silently substitutes a different `sex` than the one requested** for
sex-specific sites, and it announces the substitution ONLY in the response key. For **Breast**,
`sex=1` ("Both Sexes") returns **`sex=2` (MALE)**:

    site=55 data_type=2 sex=1  ->  key "2_1_1_55"  rate  0.261793   count   2,457
    site=55 data_type=2 sex=3  ->  key "3_1_1_55"  rate 18.928734   count 212,409

**A loader that trusted its own request parameter would rank breast cancer near the BOTTOM of US
cancer deaths on a rate 72x too small**, and the number would carry six decimal places and a
confidence interval while doing it. That is `F-047`'s class exactly — a confident, plausible,
wrong answer with no error to notice. **So the requested sex is never trusted: the sex written to
the artefact is parsed out of the RESPONSE KEY, every time, and a mismatch is RECORDED rather than
smoothed.**

Usage:
    python scripts/fetch_seer_burden.py --out data/burden          # fetch + write artefact
    python scripts/fetch_seer_burden.py --dry-run --site 47        # one site, print, write nothing
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]

EXPLORER_BASE = "https://seer.cancer.gov/statistics-network/explorer"
REGION_5 = f"{EXPLORER_BASE}/source/content_writers/render_region_5.php"
VAR_FORMATS = f"{EXPLORER_BASE}/source/content_writers/get_var_formats.php"

# graph_type=10 is "Recent Rates" — the 5-year age-adjusted rate block of the official release.
GRAPH_TYPE_RECENT_RATES = 10

# data_type: 1 = SEER Incidence, 2 = U.S. Mortality, 3 = Preliminary Incidence Rates.
DATA_TYPE_INCIDENCE = 1
DATA_TYPE_MORTALITY = 2
PRELIMINARY_DATA_TYPE = 3  # ⚠ named in order to be excluded — see the module docstring.

STAGE_ALL = 101  # "All Stages". Incidence responses are stage-split; anything else is a subset.

SEX_CODES = {1: "both", 2: "male", 3: "female"}

# ⚠ The two statistics have DIFFERENT populations and DIFFERENT periods. They are carried per-row
# rather than as a single header, because a header would let one row's period be read onto another.
POPULATIONS = {
    "mortality": "us_total_nchs",
    "incidence": "seer_registries",
}

# ⚠⚠ THE TOP-LEVEL SEER SITE-RECODE SET, AND WHAT IS DELIBERATELY NOT IN IT.
# Verified 2026-09-09 against SEER*Explorer's own cancer-site definitions page, which states:
# "The cancer sites available in SEER*Explorer are primarily defined using the SEER Site Recode
# ICD-O-3/WHO 2008 variable." Each entry is (explorer_site_id, label, recode_group).
# `recode_group` is the top-level group the site sits under in that recode.
TOP_LEVEL_SITES: tuple[tuple[int, str, str], ...] = (
    (3, "Oral Cavity and Pharynx", "Oral Cavity and Pharynx"),
    (17, "Esophagus", "Digestive System"),
    (18, "Stomach", "Digestive System"),
    (19, "Small Intestine", "Digestive System"),
    (20, "Colon and Rectum (including Appendix)", "Digestive System"),
    (34, "Anus, Anal Canal & Anorectum", "Digestive System"),
    (35, "Liver and Intrahepatic Bile Duct", "Digestive System"),
    (38, "Gallbladder", "Digestive System"),
    (40, "Pancreas", "Digestive System"),
    (46, "Larynx", "Respiratory System"),
    (47, "Lung and Bronchus", "Respiratory System"),
    (50, "Bones and Joints", "Bones and Joints"),
    (51, "Soft Tissue including Heart", "Soft Tissue including Heart"),
    (53, "Melanoma of the Skin", "Skin excluding Basal and Squamous"),
    (55, "Breast", "Breast"),
    (57, "Cervix Uteri", "Female Genital System"),
    (58, "Corpus and Uterus, NOS", "Female Genital System"),
    (61, "Ovary", "Female Genital System"),
    (62, "Vagina", "Female Genital System"),
    (63, "Vulva", "Female Genital System"),
    (66, "Prostate", "Male Genital System"),
    (67, "Testis", "Male Genital System"),
    (71, "Urinary Bladder (Invasive & In Situ)", "Urinary System"),
    (72, "Kidney and Renal Pelvis", "Urinary System"),
    (75, "Eye and Orbit", "Eye and Orbit"),
    (76, "Brain and Other Nervous System", "Brain and Other Nervous System"),
    (80, "Thyroid", "Endocrine System"),
    (83, "Hodgkin Lymphoma", "Lymphoma"),
    (86, "Non-Hodgkin Lymphoma", "Lymphoma"),
    (89, "Myeloma", "Myeloma"),
    (90, "Leukemia", "Leukemia"),
    (110, "Kaposi Sarcoma", "Kaposi Sarcoma"),
    (111, "Mesothelioma", "Mesothelioma"),
)

# ⚠ A CONTEXT ROW, AND IT IS NEVER RANKED AGAINST THE SITES IT CONTAINS. It is carried because a
# reader asking "which cancers kill the most" is owed the denominator — 3.0 million US cancer
# deaths over the pinned period is what makes 662,721 lung deaths legible. Ranking it beside its
# own components would be the two-populations-in-one-table defect (`F-031`), so the loader flags it
# and the surface separates it.
SITE_ALL_COMBINED: tuple[int, str, str] = (
    1, "All Cancer Sites Combined", "All Cancer Sites Combined")

# ⚠⚠ EVERY SITE SEER*EXPLORER OFFERS AND THIS ARTEFACT DOES NOT CARRY, WITH THE REASON.
# `D-093 amendment 6` was written because a licence was RECALLED rather than READ; the same
# discipline applies to an omission. An unstated exclusion reads as an oversight, and an oversight
# gets "fixed" by someone who does not know why it is there.
EXCLUDED_SITES: dict[int, str] = {
    5: "sub_site_of_oral_cavity_and_pharynx",
    6: "sub_site_of_oral_cavity_and_pharynx",
    7: "sub_site_of_oral_cavity_and_pharynx",
    8: "sub_site_of_oral_cavity_and_pharynx",
    9: "sub_site_of_oral_cavity_and_pharynx",
    12: "sub_site_of_oral_cavity_and_pharynx",
    21: "sub_site_of_colon_and_rectum",
    31: "sub_site_of_colon_and_rectum",
    670: "alternate_partition_of_colon_and_rectum_excluding_appendix",
    630: "sub_site_of_kidney_and_renal_pelvis",
    640: "sub_site_of_kidney_and_renal_pelvis",
    600: "histology_subtype_of_esophagus",
    601: "histology_subtype_of_esophagus",
    610: "histology_subtype_of_lung_and_bronchus",
    611: "histology_subtype_of_lung_and_bronchus",
    612: "histology_subtype_of_lung_and_bronchus",
    613: "histology_subtype_of_lung_and_bronchus",
    620: "receptor_subtype_of_breast",
    621: "receptor_subtype_of_breast",
    622: "receptor_subtype_of_breast",
    623: "receptor_subtype_of_breast",
    650: "histology_subtype_of_thyroid",
    651: "histology_subtype_of_thyroid",
    660: "brain_cns_recode_subtype",
    661: "brain_cns_recode_subtype",
    662: "brain_cns_recode_subtype",
    663: "brain_cns_recode_subtype",
    664: "brain_cns_recode_subtype",
    92: "leukemia_subtype",
    93: "leukemia_subtype",
    96: "leukemia_subtype",
    97: "leukemia_subtype",
    100: "leukemia_subtype",
    402: "special_histology_definition_not_in_site_recode",
    409: "special_histology_definition_not_in_site_recode",
    418: "special_histology_definition_not_in_site_recode",
    500: "non_malignant_behaviour_not_a_cancer_site",
    501: "non_malignant_behaviour_not_a_cancer_site",
    502: "non_malignant_behaviour_not_a_cancer_site",
}


class FetchRefused(RuntimeError):
    """⚠ Raised when the fetch may not write. An exception rather than a returned sentinel because
    *a failing check nobody is forced to obey is decoration* (`core/source_pin.py`'s reasoning,
    applied one layer up)."""


def _get(url: str, params: dict[str, object]) -> object:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{url}?{query}",
        headers={"User-Agent": "PharmFoldMDK/D-149 (coursework; contact via repository)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 — fixed https host
        body = resp.read().decode("utf-8")
    payload = json.loads(body)
    # render_region_5.php double-encodes: the body is a JSON *string* holding JSON.
    if isinstance(payload, str):
        payload = json.loads(payload)
    return payload


def fetch_release_pin() -> dict[str, object]:
    """The release identity, read from the live vocabulary rather than typed in.

    ⚠ `stat_type` carries the year ranges of the current release in its own labels — e.g.
    *"Dying from Cancer (2022-2024)"* — and `year_range` maps the numeric codes the data rows
    return. **The pinned years are therefore MEASURED from the response, never asserted.**
    """
    vf = _get(VAR_FORMATS, {})["VariableFormats"]
    return {
        "year_range_codes": vf["year_range"],
        "stat_type_labels": vf["stat_type"],
        "rate_type_labels": vf["rate_type"],
        "site_labels": vf["site"],
        "stage_labels": vf["stage"],
    }


def _parse_rows(payload: dict, *, statistic: str, site_id: int) -> list[dict[str, object]]:
    """Project one `render_region_5.php` response into artefact rows.

    ⚠⚠ THE SEX IS TAKEN FROM THE RESPONSE KEY, NOT FROM THE REQUEST. See the module docstring:
    the request parameter is a wish and the key is the fact, and for Breast they differ by 72x in
    the rate. `key-order` is read from the response too rather than assumed, because the incidence
    and mortality responses carry DIFFERENT key orders (incidence interposes `stage` and
    `subtype`), and hard-coding one order would silently read the stage code as a sex.
    """
    info = payload["info"]
    key_order: list[str] = info["key-order"]
    fields: list[str] = info["data-fields"]
    out: list[dict[str, object]] = []
    for key, block in payload["data"].items():
        parts = key.split("_")
        if len(parts) != len(key_order):
            raise FetchRefused(
                f"{statistic} site={site_id}: response key {key!r} has {len(parts)} parts but "
                f"key-order declares {len(key_order)} ({key_order}). Refusing rather than "
                f"guessing which component is the sex.")
        keyed = dict(zip(key_order, parts))
        if "stage" in keyed and int(keyed["stage"]) != STAGE_ALL:
            continue  # a stage stratum, not the site total
        series = block["data_series"]
        if len(series) != 1:
            raise FetchRefused(
                f"{statistic} site={site_id}: expected one data series for a single-point rate "
                f"block, got {len(series)}")
        values = dict(zip(fields, series[0]))
        sex_code = int(keyed["sex"])
        if sex_code not in SEX_CODES:
            raise FetchRefused(
                f"{statistic} site={site_id}: response key declares sex={sex_code}, which is not "
                f"in the fetched sex vocabulary {sorted(SEX_CODES)}")
        out.append({
            "statistic": statistic,
            "seer_site_id": site_id,
            "sex": SEX_CODES[sex_code],
            "sex_code_returned": sex_code,
            "rate_per_100k": values["rate"],
            "rate_se": values["rate_se"],
            "rate_lower_ci": values["rate_lower_ci"],
            "rate_upper_ci": values["rate_upper_ci"],
            "observed_count": values["count"],
            "year_range_code": block["year_range"],
        })
    return out


def fetch_site(site_id: int, *, statistic: str, sleep: float = 0.3) -> list[dict[str, object]]:
    """Fetch every published sex stratum for one (site, statistic).

    ⚠ All three sex codes are requested and the results deduped ON THE RETURNED KEY. That is not
    redundancy: it is how a site whose "Both Sexes" request is answered with a MALE figure ends up
    carrying its female figure too, instead of carrying the substituted one alone.
    """
    data_type = DATA_TYPE_MORTALITY if statistic == "mortality" else DATA_TYPE_INCIDENCE
    seen: dict[int, dict[str, object]] = {}
    substitutions: list[dict[str, object]] = []
    for requested_sex in (1, 2, 3):
        params = {
            "site": site_id,
            "data_type": data_type,
            "graph_type": GRAPH_TYPE_RECENT_RATES,
            "sex": requested_sex,
            "race": 1,
            "age_range": 1,
        }
        if data_type == DATA_TYPE_INCIDENCE:
            params["stage"] = STAGE_ALL
        payload = _get(REGION_5, params)
        for row in _parse_rows(payload, statistic=statistic, site_id=site_id):
            returned = int(row["sex_code_returned"])
            if returned != requested_sex:
                substitutions.append({
                    "statistic": statistic,
                    "seer_site_id": site_id,
                    "requested_sex": SEX_CODES[requested_sex],
                    "returned_sex": SEX_CODES[returned],
                })
            seen.setdefault(returned, row)
        time.sleep(sleep)
    rows = list(seen.values())
    for row in rows:
        row["sex_substitutions_observed"] = json.dumps(
            [s for s in substitutions if s["returned_sex"] == row["sex"]], sort_keys=True)
    return rows


FIELDNAMES = (
    "statistic",
    "seer_site_id",
    "site_label",
    "recode_group",
    "sex",
    "rate_per_100k",
    "rate_se",
    "rate_lower_ci",
    "rate_upper_ci",
    "observed_count",
    "count_population",
    "period",
    "rate_basis",
    "requested_sex_was_substituted",
)


def build_rows(*, sites, pin: dict[str, object], sleep: float = 0.3) -> list[dict[str, object]]:
    year_ranges = pin["year_range_codes"]
    rows: list[dict[str, object]] = []
    for site_id, label, group in sites:
        for statistic in ("mortality", "incidence"):
            fetched = fetch_site(site_id, statistic=statistic, sleep=sleep)
            if not fetched:
                raise FetchRefused(
                    f"{statistic} site={site_id} ({label}) returned no rate block at all. An "
                    f"absent figure is a category, never a silently dropped row — investigate "
                    f"before re-running.")
            for row in fetched:
                code = str(row.pop("year_range_code"))
                if code not in year_ranges:
                    raise FetchRefused(
                        f"{statistic} site={site_id}: year_range code {code} is absent from the "
                        f"fetched year_range vocabulary. The period cannot be named, so the row "
                        f"is refused rather than written with an unknown period.")
                substituted = json.loads(row.pop("sex_substitutions_observed"))
                rows.append({
                    "statistic": row["statistic"],
                    "seer_site_id": row["seer_site_id"],
                    "site_label": label,
                    "recode_group": group,
                    "sex": row["sex"],
                    "rate_per_100k": row["rate_per_100k"],
                    "rate_se": row["rate_se"],
                    "rate_lower_ci": row["rate_lower_ci"],
                    "rate_upper_ci": row["rate_upper_ci"],
                    "observed_count": row["observed_count"],
                    "count_population": POPULATIONS[row["statistic"]],
                    "period": year_ranges[code],
                    "rate_basis": ("us_mortality_age_adjusted_per_100k"
                                   if row["statistic"] == "mortality"
                                   else "observed_seer_incidence_age_adjusted_per_100k"),
                    "requested_sex_was_substituted": json.dumps(substituted, sort_keys=True),
                })
            print(f"  {statistic:9s} site={site_id:<4d} {label[:44]:<44s} "
                  f"{len(fetched)} sex stratum(s)", file=sys.stderr)
    rows.sort(key=lambda r: (r["statistic"], r["seer_site_id"], r["sex"]))
    return rows


def write_artefact(rows, *, pin, out_dir: pathlib.Path, sites) -> tuple[pathlib.Path, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "seer_us_cancer_burden.v1.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    periods = sorted({(r["statistic"], r["period"], r["count_population"]) for r in rows})
    substituted = [
        {"statistic": r["statistic"], "seer_site_id": r["seer_site_id"], "sex": r["sex"],
         "detail": json.loads(r["requested_sex_was_substituted"])}
        for r in rows if json.loads(r["requested_sex_was_substituted"])
    ]
    provenance = {
        "artefact": csv_path.name,
        "artefact_sha256": digest,
        "artefact_rows": len(rows),
        "fetched_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
        "supplier": "NCI / SEER",
        "product": "SEER*Explorer",
        "product_url": f"{EXPLORER_BASE}/",
        "tier": "official aggregate statistics (SEER*Explorer)",
        "tier_note": (
            "Aggregate statistics only. NOT SEER Research Data / Research Plus: no case-level "
            "record was fetched and no data-use agreement is involved."),
        "release": "SEER November 2025 Submission",
        "release_application_updated": "2026-04-22",
        "graph_type": "Recent Rates (graph_type=10)",
        "excluded_product": (
            "Preliminary Incidence Estimates (data_type=3) — disqualified by D-093 amendment 6: "
            "selected registries, subject to revision, registry selection re-derived each year."),
        "geography": "United States only",
        "us_only_disclaimer": (
            "United States only. These figures describe the US population and say nothing about "
            "cancer burden anywhere else."),
        "attribution": (
            "Data source: SEER*Explorer, Surveillance Research Program, National Cancer "
            "Institute. Credit the National Cancer Institute as the source."),
        "attribution_basis": (
            "NCI reuse policy as read in D-093 amendment 6; the data-vs-text gap was closed by "
            "the owner on 2026-09-09 (docs/OWNER-2026-09-09-D-093-amd6-seer-aggregates-"
            "cleared.md) and the credit requirement SURVIVES that closure."),
        "site_vocabulary": "SEER Site Recode ICD-O-3/WHO 2008",
        "site_vocabulary_url": "https://seer.cancer.gov/siterecode/icdo3_dwhoheme/index.html",
        "site_vocabulary_basis": (
            "SEER*Explorer cancer-site definitions page, read 2026-09-09: 'The cancer sites "
            "available in SEER*Explorer are primarily defined using the SEER Site Recode "
            "ICD-O-3/WHO 2008 variable.'"),
        "periods": [
            {"statistic": s, "period": p, "count_population": pop} for s, p, pop in periods
        ],
        "count_population_key": {
            "us_total_nchs": (
                "Deaths for the TOTAL United States, from the NCHS public use file. A national "
                "count."),
            "seer_registries": (
                "New cases within the SEER registry catchment areas only — NOT the whole United "
                "States. ⚠ A SEER incidence COUNT and a US mortality COUNT have different "
                "denominators and MUST NOT be compared to each other. The age-adjusted RATES "
                "are the comparable quantities."),
        },
        "top_level_sites": [
            {"seer_site_id": sid, "site_label": lab, "recode_group": grp}
            for sid, lab, grp in sites if sid != SITE_ALL_COMBINED[0]
        ],
        "context_row": {
            "seer_site_id": SITE_ALL_COMBINED[0],
            "site_label": SITE_ALL_COMBINED[1],
            "note": ("All Cancer Sites Combined is a DENOMINATOR, not a ranked site. It contains "
                     "the sites above and must never be ordered beside them."),
        },
        "excluded_sites": [
            {"seer_site_id": sid, "reason": why} for sid, why in sorted(EXCLUDED_SITES.items())
        ],
        "sex_substitutions_observed": substituted,
        "sex_substitution_note": (
            "render_region_5.php silently answers some sex-specific site requests with a "
            "different sex than the one requested, announcing it only in the response key. The "
            "sex on every row is parsed from the RESPONSE KEY, never from the request."),
        "globocan": (
            "ABSENT BY RULING. No GLOBOCAN/IARC figure is ingested or rendered — IARC reserves "
            "all rights (D-093 amendment 6)."),
    }
    prov_path = out_dir / "seer_us_cancer_burden.provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    return csv_path, digest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="data/burden", help="directory the artefact is written to")
    ap.add_argument("--site", type=int, action="append", default=None,
                    help="restrict to one or more SEER*Explorer site ids (debugging)")
    ap.add_argument("--dry-run", action="store_true", help="print rows; write nothing")
    ap.add_argument("--sleep", type=float, default=0.3, help="delay between requests, seconds")
    args = ap.parse_args(argv)

    sites = (SITE_ALL_COMBINED,) + TOP_LEVEL_SITES
    if args.site:
        wanted = set(args.site)
        sites = tuple(s for s in sites if s[0] in wanted)
        if not sites:
            raise FetchRefused(f"no site matches {sorted(wanted)}")

    print("reading the release pin from the live vocabulary…", file=sys.stderr)
    pin = fetch_release_pin()
    print(f"  stat_type labels: {pin['stat_type_labels']}", file=sys.stderr)

    rows = build_rows(sites=sites, pin=pin, sleep=args.sleep)
    print(f"{len(rows)} rows over {len(sites)} sites", file=sys.stderr)

    if args.dry_run:
        json.dump(rows, sys.stdout, indent=2)
        print()
        return 0

    csv_path, digest = write_artefact(rows, pin=pin, out_dir=ROOT / args.out, sites=sites)
    print(f"wrote {csv_path} sha256={digest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
