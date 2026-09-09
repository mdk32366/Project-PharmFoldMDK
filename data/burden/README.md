# `data/burden/` — the SEER official-aggregate cancer burden artefact (D-149)

| File | What it is |
|---|---|
| `seer_us_cancer_burden.v1.csv` | 174 rows. One row per **(statistic, SEER\*Explorer site, sex)**. |
| `seer_us_cancer_burden.provenance.json` | sha256 pin, release pin, attribution, the excluded product and the excluded sites, with reasons. |

**Regenerate with** `python scripts/fetch_seer_burden.py --out data/burden` (network).
**Load with** `python scripts/seer_cancer_burden.py --load` (no network, ever).

---

## What is pinned

- **Release:** SEER **November 2025 Submission**; SEER\*Explorer application updated **2026-04-22**.
- **Mortality:** U.S. deaths, **NCHS public use file**, **total United States**, age-adjusted per
  100,000. Period **2020-2024** for 32 of 34 sites — see the two exceptions below.
- **Incidence:** **observed SEER incidence**, age-adjusted per 100,000, period **2019-2023**.
- **Geography: United States only.** Nothing here describes burden anywhere else.
- **Attribution:** *Data source: SEER\*Explorer, Surveillance Research Program, National Cancer
  Institute.* Credit the National Cancer Institute as the source.

## ⚠⚠ Three things a reader of this table will get wrong unless they are told

### 1. The two counts have different denominators, and the mortality count is the LARGER one

| Lung and Bronchus | value | population |
|---|---|---|
| deaths, 2020-2024 | **662,721** | the **whole United States** (NCHS) |
| new cases, 2019-2023 | **434,448** | the **SEER registry catchment areas only** |

**More deaths than cases is arithmetically impossible in one population, and these are two
populations.** SEER incidence is registry-based and covers a fraction of the US; US mortality is
national. **The comparable quantities are the age-adjusted RATES**, which is why the rate — not the
count — is what the surface ranks incidence on. Every row carries its own `count_population`, and
`GET /api/cancer-burden` refuses to serve a row whose population is unnamed.

### 2. `Melanoma of the Skin` is not "skin cancer"

The SEER Site Recode ICD-O-3/WHO 2008 group is literally named **"Skin excluding Basal and
Squamous"**, and its members are *Melanoma of the Skin* and *Other Non-Epithelial Skin*.
**Basal-cell and squamous-cell carcinoma — the overwhelming majority of skin cancers — are not in
SEER at all**, and SEER\*Explorer offers no site for them. A surface that labelled row `53` "skin
cancer" would return a confident, plausible figure about a different disease population
(`F-047`'s class; `D-093 amendment 6` is where this trap was first named). **The row keeps SEER's
own name and the exclusion is stated on the surface, not only here.**

### 3. Breast is published per-sex, and asking for "Both Sexes" returns MALE

Measured 2026-09-09 against `render_region_5.php`:

    site=55 data_type=2 sex=1 ("Both Sexes")  ->  response key "2_1_1_55"  rate  0.261793,   2,457 deaths
    site=55 data_type=2 sex=3 ("Female")      ->  response key "3_1_1_55"  rate 18.928734, 212,409 deaths

The API **silently substitutes** the sex and announces it only in the response key. A fetcher that
trusted its own request parameter would have ranked breast cancer near the bottom of US cancer
deaths on a rate **72× too small**. `scripts/fetch_seer_burden.py` therefore parses the sex out of
the **response key**, never the request, and records every substitution it saw in
`requested_sex_was_substituted`. **16 of 174 rows carry a recorded substitution.**

⚠ SEER\*Explorer publishes **no both-sexes figure for breast**, and an age-adjusted rate cannot be
summed across sexes. So no both-sexes breast rate is synthesised: the rows are `Breast (female)`
and `Breast (male)`, each labelled.

## ⚠ Two sites carry a DIFFERENT mortality period, and it is real

`Kaposi Sarcoma` (110) and `Mesothelioma` (111) return mortality for **2019-2023**, not 2020-2024 —
6 of 87 mortality rows. That is what the source's own `year_range` code says for those sites.
**The period is a per-ROW field precisely because of this.** A single header period would have
relabelled six rows with a period they do not have, and nothing would have reddened.

## What is NOT here, and why

| Absent | Reason |
|---|---|
| **Preliminary Incidence Estimates** | Disqualified by `D-093 amendment 6`: selected registries, *"Subject to revision: Yes"*, and a registry selection **re-derived each year** — one name over N populations. |
| **SEER Research Data / Research Plus** | Case-level, controlled, data-use agreement. **No microdata is fetched and none is here.** |
| **GLOBOCAN / IARC** | ⚠ **All rights reserved** (`D-093 amendment 6`). No GLOBOCAN figure is ingested and none is rendered. |
| **Any protein, accession, score or rank** | Burden is a property of a **disease** (`D-093` decision 1). This artefact contains no protein identifier and joins to no ranking. |
| **Basal-cell / squamous-cell skin carcinoma** | Not reportable to SEER; no site exists. |
| Sub-sites, histology subtypes, non-malignant behaviours, and three special histology definitions | Enumerated with a reason each in `provenance.json` → `excluded_sites`. |
