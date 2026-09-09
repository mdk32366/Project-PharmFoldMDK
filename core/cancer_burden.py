"""The cancer-burden vocabulary and the sentences that must travel with a figure — `D-149`.

⚠⚠ **WHAT THIS SURFACE IS.** It answers *which cancers kill the most people in the United States,
and how many are diagnosed*, from **SEER official aggregate statistics**. It is a **disease-level**
surface. It carries no protein, no accession, no gene, no score and no rank, and it joins to none of
them — `D-093` decision 1 ruled burden a property of a **disease**, attached by traversal, never a
protein-level column.

⚠⚠ **WHAT IT IS NOT, AND THE THREE REFUSALS ARE LOAD-BEARING.**

1. **It is not protein-level burden.** No `burden` column reaches the protein path;
   `tests/test_clinical_layer_prohibitions.py` has forbidden it since `D-093` and this module does
   not soften that.
2. **It is not composed into `structural_score`.** Not as a factor, not as a tie-break, not as a
   sort key. `D-143` / `D-144` / `D-146` refused a `cancer ×` product three times; a burden figure
   is exactly the number that would make it look reasonable.
3. **It is not worldwide.** `US_ONLY_DISCLAIMER` rides on the payload header **and on every row**,
   for the reason `census_structural_read.py` gives about `STRUCTURAL_ONLY`: a row lifted out of a
   list into a slide takes the sentence with it, and a tooltip does not travel.

⚠ **NO GLOBOCAN.** `D-093` amendment 6 read IARC's terms — *"IARC exercises copyright… All rights
are reserved"*, three separate written-permission triggers, unilaterally mutable terms and an
indemnification. No GLOBOCAN figure is ingested and none is rendered. The string `GLOBOCAN` appears
in this repository only in refusals, and a test asserts it never reaches a served payload.
"""

from __future__ import annotations

#: ⚠ The two statistics, and they are NOT two views of one quantity — different sources, different
#: populations, different periods. The vocabulary lives here so the loader, the read route and the
#: tests share one definition rather than three string literals.
STATISTIC_MORTALITY = "mortality"
STATISTIC_INCIDENCE = "incidence"
STATISTICS = (STATISTIC_MORTALITY, STATISTIC_INCIDENCE)

#: `both` | `female` | `male`. ⚠ Always the sex the SOURCE returned, never the sex requested.
SEX_VALUES = ("both", "female", "male")

#: The run status vocabulary, deliberately identical to `census_structural_runs`' — `valid` is
#: served, `superseded` is what a previous valid run becomes, `invalid` is a run the loader refused
#: to certify. One word in one place: the loader writes it and the read predicate reads it.
RUN_VALID = "valid"
RUN_SUPERSEDED = "superseded"
RUN_INVALID = "invalid"

#: ⚠ `not_run` is a 200 with empty rows, never a 404 — the `/api/ranking` posture (`D-062`).
STATUS_NOT_RUN = "not_run"

GEOGRAPHY_US = "united_states"

#: ⚠⚠ THE US-ONLY DISCLAIMER, IN ONE PLACE, REQUIRED ON EVERY FIGURE AND IN THE API `meta`.
#: It is stored as a COLUMN on the run and asserted by test — not a UI string, because a UI string
#: is one refactor from being dropped and nothing would redden.
US_ONLY_DISCLAIMER = (
    "United States only. These are US figures: SEER reports US cancer statistics and nothing "
    "here describes cancer burden in any other country. Do not read a US rate as a world rate."
)

#: The short form, for a row and for a chart caption. ⚠ Short, not softer.
US_ONLY_SHORT = "US only — SEER/NCI"

#: ⚠⚠ NCI ATTRIBUTION. `D-093` amendment 6 obtained NCI's reuse policy verbatim — *"Credit the
#: National Cancer Institute as the source"* — and the owner's 2026-09-09 ruling closed that
#: amendment's data-vs-text gap **while leaving this obligation standing**. So it ships.
ATTRIBUTION = (
    "Data source: SEER*Explorer, Surveillance Research Program, National Cancer Institute. "
    "Credit the National Cancer Institute as the source."
)

ATTRIBUTION_URL = "https://seer.cancer.gov/statistics-network/explorer/"

#: ⚠ What this surface is NOT, named on the wire. `F-049`'s lesson: a payload that says only what
#: its own number IS still lets a reader assume another number means the same thing. Three routes
#: in this application now serve an ordered list of things, and none of the other two is this one.
SEPARATION = (
    "This is a DISEASE-level surface and it is joined to nothing. It is not /api/ranking (the "
    "cohort-82 learned scorer, D-041/D-060), not /api/census-structural-ranking (a fixed "
    "arithmetic product over census proteins, D-144), and it contributes to neither. No burden "
    "figure enters structural_score as a factor, a tie-break or a sort key, and no row here "
    "carries a protein, an accession, a gene or a score. Burden is a property of a DISEASE "
    "(D-093 decision 1); it is not a property of a protein."
)

#: ⚠⚠ THE COUNT TRAP, STATED ON THE WIRE RATHER THAN ONLY IN A README. Measured on the pinned
#: release: Lung and Bronchus carries 662,721 deaths and 434,448 new cases. More deaths than cases
#: is impossible in ONE population and unremarkable in TWO.
COUNT_POPULATION_KEY = {
    "us_total_nchs": {
        "kind": "NATIONAL_COUNT",
        "text": (
            "Deaths for the TOTAL United States, from the NCHS public use file. A national count "
            "covering the whole US population."
        ),
    },
    "seer_registries": {
        "kind": "REGISTRY_CATCHMENT_COUNT",
        "text": (
            "New cases within the SEER registry catchment areas ONLY — not the whole United "
            "States. ⚠⚠ A SEER incidence COUNT and a US mortality COUNT have DIFFERENT "
            "denominators and MUST NOT be compared: on this release Lung and Bronchus carries "
            "662,721 deaths against 434,448 new cases, which is impossible in one population. "
            "The age-adjusted RATES are the comparable quantities, which is why incidence is "
            "ranked on rate and never on count."
        ),
    },
}

#: The per-field key the surface publishes, on the `population_key` pattern of `/api/coverage` and
#: `/api/census-structural-ranking`. ⚠ Every entry names how the number is known (`D-016`).
POPULATION_KEY = {
    "rate_per_100k": {"kind": "AGE_ADJUSTED_RATE", "text": (
        "Age-adjusted rate per 100,000 person-years, 2000 US standard population, as published by "
        "SEER*Explorer. ⚠ This is the COMPARABLE quantity across sites and across the two "
        "statistics. It is read from the source, never recomputed here."
    )},
    "observed_count": {"kind": "OBSERVED_COUNT_OVER_ITS_OWN_PERIOD", "text": (
        "Observed events over this ROW's period, in this ROW's population. ⚠ See "
        "count_population: the mortality count is national and the incidence count is registry-"
        "area only, so the two counts are not comparable to each other."
    )},
    "period": {"kind": "PER_ROW_PERIOD", "text": (
        "The 5-year window this row's figure covers, read from the source's own year_range code. "
        "⚠ PER-ROW, not per-run: US mortality is 2020-2024 for 32 of 34 sites, but Kaposi Sarcoma "
        "and Mesothelioma are 2019-2023, and SEER incidence is 2019-2023. A single header period "
        "would have relabelled six rows with a period they do not have."
    )},
    "rate_denominator": {"kind": "SEX_SCOPED_DENOMINATOR", "text": (
        "⚠⚠ A SEX-SPECIFIC RATE IS PER 100,000 OF THAT SEX, NOT PER 100,000 PEOPLE. SEER computes "
        "an age-adjusted rate over the population at risk, so `Breast (female)` at 132.53 is per "
        "100,000 WOMEN while `Lung and Bronchus` at 47.17 is per 100,000 PEOPLE. Both are "
        "published this way and ranking them together is the standard convention — but the two "
        "denominators are not the same, so a sex-specific rate is not strictly comparable to a "
        "both-sexes rate even though both read 'per 100,000'. ⚠ The effect is visible in this "
        "data: ordering incidence by rate puts `Corpus and Uterus, NOS` (female-only) above "
        "`Melanoma of the Skin`, while ordering by count reverses them. Every row states its "
        "denominator so the comparison is a reader's choice rather than a hidden one."
    )},
    "sex": {"kind": "PARSED_FROM_SOURCE_RESPONSE", "text": (
        "The sex the SOURCE returned, never the sex requested. ⚠⚠ SEER*Explorer answers a Breast "
        "'Both Sexes' request with the MALE figure — rate 0.26 and 2,457 deaths instead of 18.93 "
        "and 212,409 — announcing the substitution only in its response key. sex_substituted "
        "marks every row where the two differed."
    )},
    "site_label": {"kind": "SOURCE_VOCABULARY_VERBATIM", "text": (
        "SEER Site Recode ICD-O-3/WHO 2008, carried verbatim. ⚠ Melanoma of the Skin is NOT "
        "'skin cancer' — see skin_exclusion."
    )},
    "is_context_row": {"kind": "DENOMINATOR_FLAG", "text": (
        "All Cancer Sites Combined is a DENOMINATOR that contains every other site. It is served "
        "so a reader can see the whole, and flagged so no consumer ranks it beside its own "
        "components (F-031: two populations in one table)."
    )},
    "is_primary_sex_stratum": {"kind": "DISPLAY_SELECTION", "text": (
        "True for the row a per-site view should show: the `both` row where SEER publishes one, "
        "and otherwise EVERY sex-specific row, each labelled with its sex. ⚠ No both-sexes rate "
        "is synthesised — age-adjusted rates cannot be summed across sexes, so a combined breast "
        "rate would be a number with no source."
    )},
}

#: ⚠⚠ THE SKIN TRAP, NAMED ON THE SURFACE AND NOT ONLY IN THE LOG. `D-093` amendment 6 found it
#: first and called it the dangerous one, because the other unmappable tumour strings fail LOUDLY
#: while this one *"would produce a confident, plausible, wrong answer"* — `F-047`'s class.
SKIN_EXCLUSION = (
    "SEER's site-recode group is literally named 'Skin excluding Basal and Squamous', and its "
    "members are 'Melanoma of the Skin' and 'Other Non-Epithelial Skin'. Basal-cell and "
    "squamous-cell carcinoma — the overwhelming majority of skin cancers diagnosed in the US — "
    "are NOT reportable to SEER and have no site here at all. ⚠⚠ So the row labelled 'Melanoma "
    "of the Skin' is melanoma, and this surface never calls it 'skin cancer': that relabelling "
    "would return a confident, plausible figure about a different disease population."
)

#: ⚠ The product that was NOT used, named so the choice is checkable. `D-093` amendment 6
#: disqualified it on its own documentation.
EXCLUDED_PRODUCT = (
    "SEER Preliminary Incidence Estimates are NOT used. Their own documentation says 'selected "
    "registries meeting predefined completeness criteria', 'Subject to revision: Yes' and 'Use "
    "with caution', and the registry selection is re-derived each year — one product name over N "
    "populations, invisible because the name never changes (D-093 amendment 6). This surface uses "
    "the OFFICIAL November-submission / April-release statistics only."
)

#: ⚠ The tier that was NOT used. No case-level record is in this repository and no DUA is involved.
EXCLUDED_TIER = (
    "SEER Research Data / Research Plus (case-level microdata) is NOT used and is not present. "
    "That tier is controlled — each person accessing it submits a separate request and "
    "acknowledges the data agreements. This surface uses aggregate statistics only."
)

#: ⚠⚠ GLOBOCAN'S ABSENCE IS A STATED CATEGORY, NEVER A BLANK. An absent figure with no cause reads
#: as an oversight, and an oversight gets "fixed" by someone who does not know why it is there.
GLOBOCAN_ABSENT = (
    "No GLOBOCAN / IARC figure is ingested or rendered, and worldwide burden is therefore ABSENT "
    "rather than zero. IARC exercises copyright over its materials and reserves all rights, with "
    "three separate written-permission triggers, unilaterally mutable terms and an "
    "indemnification clause (D-093 amendment 6). This is a licensing refusal, not a data gap."
)

#: ⚠ The tumour strings HPA carries that this vocabulary cannot receive, with the reason. `D-093`
#: amendment 6's *"4 of 20 do not join"*, deepened the same day to a two-axis finding. Published
#: because a crosswalk offered without its failures is a crosswalk that lies by omission.
UNMAPPABLE_HPA_SITES = {
    "carcinoid": (
        "A HISTOLOGY, not a site — it occurs across GI, lung and pancreas. The SEER site recode "
        "has no such category and mapping it would need a histology recode, a different "
        "vocabulary entirely."
    ),
    "skin cancer": (
        "⚠⚠ THE DANGEROUS ONE. See skin_exclusion: SEER's category excludes basal- and "
        "squamous-cell carcinoma, which are most skin cancers. A string join would SUCCEED and "
        "return a number about a different disease population."
    ),
    "head and neck": (
        "A regional grouping on neither ICD-O axis. It spans SEER's Oral Cavity and Pharynx plus "
        "larynx from Respiratory System."
    ),
    "urothelial": (
        "A morphology spanning bladder, renal pelvis and ureter. SEER reports these separately, "
        "and renal pelvis already sits inside Kidney and Renal Pelvis."
    ),
}

#: ⚠⚠ AND THE DEEPER REASON, WHICH IS NOT A MISSING MAPPING TABLE. `D-093` amendment 6 corrected
#: itself the same day: HPA's `Cancer` column interleaves ICD-O's two INDEPENDENT axes —
#: topography and morphology — and SEER's own recode mixes them too. Two differently-mixed
#: vocabularies cannot be crosswalked, because the two mixtures do not partition the same space.
CROSSWALK_REFUSED = (
    "No crosswalk from this surface to HPA's tumour strings is offered, and the reason is not a "
    "missing mapping table. HPA's Cancer column interleaves ICD-O's two independent axes — "
    "topography (where a tumour is) and morphology (what it is): 'melanoma' and 'skin cancer' "
    "appear as SIBLINGS when one is a subtype located inside the other. SEER's own recode mixes "
    "axes too, carrying Lymphoma, Myeloma, Leukemia, Mesothelioma and Kaposi Sarcoma beside "
    "Breast and Digestive System. Two differently-mixed vocabularies do not partition the same "
    "space, so a crosswalk between them cannot be pinned (D-093 amendment 6)."
)

#: ⚠⚠ THE DEEP-LEARNING POSITION OF THIS SURFACE, STATED RATHER THAN IMPLIED. CLAUDE.md's prime
#: directive asks where the deep learning is. **It is not here**, and saying so is the honest
#: answer: this surface ingests published aggregates and computes nothing. The network's output is
#: consumed on the census and scorer surfaces (`score_model` from ESMFold pLDDT), and this
#: surface's refusal to join to them is what keeps that number free of an arithmetic it did not
#: earn. A burden figure multiplied into a rank would make a learned quantity look validated by an
#: epidemiological one.
DEEP_LEARNING_POSITION = (
    "This surface runs no model and adds no deep learning: it serves published SEER aggregates "
    "unchanged. The deep learning in this project is ESMFold, whose per-residue pLDDT becomes "
    "score_model on /api/census-structural-ranking — and this surface deliberately does NOT join "
    "to it. Multiplying a cancer death rate into a structural score would make a learned "
    "quantity look validated by an epidemiological one that knows nothing about the protein."
)


def is_primary_sex_stratum(*, sex: str, site_has_both_row: bool) -> bool:
    """The display-selection rule, in one function so the loader and the tests share it.

    ⚠ `both` where the source publishes one; otherwise **every** sex-specific row. The
    alternative — pick the larger stratum — would silently drop male breast cancer's 2,457 deaths
    with nothing saying so, and *an absent value recorded as nothing is the absent-value defect*
    (`F-018` / `F-020`'s family).
    """
    if site_has_both_row:
        return sex == "both"
    return sex in ("female", "male")


#: The three rate denominators, keyed by the row's `sex`. ⚠ A DERIVED STATEMENT, not a new fact:
#: `sex` already determines it, and spelling it out on the row is what stops a reader from reading
#: "per 100,000" as one quantity when it is three.
RATE_DENOMINATOR = {
    "both": "per_100k_people",
    "female": "per_100k_females",
    "male": "per_100k_males",
}

RATE_DENOMINATOR_LABEL = {
    "per_100k_people": "per 100,000 people",
    "per_100k_females": "per 100,000 women",
    "per_100k_males": "per 100,000 men",
}


def rate_denominator(sex: str) -> str:
    """⚠⚠ RAISES on an unknown sex rather than defaulting to `per_100k_people`.

    A default here would be the absent-value defect in its most expensive direction: an unrecognised
    sex would silently acquire the WIDEST denominator, which is exactly the direction that makes a
    sex-specific rate look like a whole-population one.
    """
    try:
        return RATE_DENOMINATOR[sex]
    except KeyError:
        raise ValueError(
            f"sex {sex!r} has no stated rate denominator; a default would make a sex-specific rate "
            f"look like a whole-population one") from None
