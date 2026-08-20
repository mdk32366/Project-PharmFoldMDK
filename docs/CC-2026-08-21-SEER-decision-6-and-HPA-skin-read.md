# `XB` + `XC` — the HPA skin/melanoma read, and SEER through `D-093` decision 6

> ⚠⚠ **DOCUMENTATION ONLY.** Nothing fetched as data, nothing ingested, no table, no schema, no page,
> no hand-mapping. **These are ANSWERS, not a confirmation** — the Planner rules on whether SEER
> enters the schema (§4 of the order).
> Produced under `ORDERS-Code-WE1-skin-confirmation-and-SEER-decision-6.md` (`5c625686…`, verified).
> **All pages read 2026-08-21.**

---

## §1 — `XB1` — what HPA says its *Skin cancer* samples are

**⚠ HPA DOES NOT STATE THE COMPOSITION OF ITS `Skin cancer` CATEGORY. The verdict stays
`hpa_composition_undocumented`, and the inference stays an inference.**

⚠⚠ **But the evidence moved a long way, and in the predicted direction.** HPA's own dictionary entry
is titled ***"Cancer: Basal cell and squamous cell cancer"*** —
`https://www.proteinatlas.org/learn/dictionary/cancer/basal+cell+and+squamous+cell+cancer`, read
2026-08-21 — and opens:

> *"Skin cancer can be divided into melanoma (see separate text and examples) and **non-melanoma
> skin cancer** (NMSC). The two most frequent subtypes of NMSC are basal cell carcinoma and squamous
> cell carcinoma."*

**And that page's histology examples are labelled, in HPA's own words:**

> *"Skin cancer 1, basal cell carcinoma"* · *"Skin cancer 2, basal cell carcinoma"* ·
> *"Skin cancer 3, squamous cell carcinoma"*

⚠ **Those are HPA's own sample identifiers** — the same `«name» «n»` convention `normal_tissue.tsv`
uses for *"skin 1"* / *"skin 2"* on the LAMP1 card. **So HPA names three of its skin-cancer samples
and every one of them is BCC or SCC**, while treating melanoma as a separate text with separate
examples.

**⚠⚠ THIS IS STILL NOT A COMPOSITION STATEMENT AND IS NOT RECORDED AS ONE.** Three labelled samples
are evidence about three samples. **The order said do not upgrade the inference by argument, and
this is exactly where the argument would be tempting.** *What is missing is a sentence saying what
the category contains — and HPA does not write one for skin.*

### ⚠⚠ `WC` NEEDS A CORRECTION, AND IT IS MINE

The crosswalk said **all twenty** rows carry `hpa_composition_undocumented`. **That is wrong.** HPA
documents composition for **three** of the twenty, on `https://v22.proteinatlas.org/about/assays+annotation`
(read 2026-08-21):

> *"breast cancer includes both ductal and lobular cancer, lung cancer includes both squamous cell
> carcinoma and adenocarcinoma and liver cancer includes both hepatocellular and cholangiocellular
> carcinoma"*

**So: 3 documented, 17 undocumented — not 20.**

⚠ **And row 8 improves because of it.** I marked `liver cancer` `mapped_at_stated_granularity`
because SEER's category is *Liver **and Intrahepatic Bile Duct*** and I took HPA's to be liver only.
**HPA documents its liver category as including cholangiocellular carcinoma — which IS bile duct.**
**The two sides contain the same thing, and the granularity note was mine, not the data's.**

### `XB3` — what the skin read would do to the verdict, if HPA ever states it

⚠⚠ **TWO FACTS, AND THE SECOND MUST NOT DISAPPEAR BEHIND THE FIRST.**
1. If `Skin cancer` is confirmed non-melanoma, the row is **cleanly identified** — we would know
   exactly which population we hold staining for.
2. ⚠ **It stays a `refused` COLLECTION hole regardless.** Knowing the population is BCC/SCC does not
   create a SEER category for it: the recode is *"Skin excluding Basal and Squamous"* and its other
   bucket is *Other **Non-Epithelial** Skin*. **Identification and countability are different
   questions, and only the first would be answered.**

⚠ The melanoma row (11) is unaffected — it already maps cleanly to *Melanoma of the Skin*.

---

## §2 — `XB2` — the supplier's documentation disagrees with itself

| page | states | lists | read |
| --- | --- | --- | --- |
| `v22.proteinatlas.org/humanproteome/pathology` | *"17 different forms of human cancer"* | 17 | 2026-08-21 |
| `v22.proteinatlas.org/humanproteome/pathology/method` | *"20 most common forms of human cancer"* | ⚠ lists **Skin cancer and Melanoma separately** | 2026-08-21 |
| `v22.proteinatlas.org/about/assays+annotation` | *"216 cancer patients corresponding to **20** different types of cancer"* | — | 2026-08-21 |

**Our data carries 20.** ⚠⚠ **Two of the three names the overview omits — `carcinoid` and
`skin cancer` — are the two `refused` rows this order turns on.**

⚠ **One caveat on my own reading, stated rather than hidden:** on the third page I could not verify
that HPA's own enumeration is short, only that the *fetched summary* of it was. **I am reporting the
"17 vs 20" discrepancy from the two pages where the stated NUMBERS differ, which is checkable, and
not from a list length I could not confirm.**

**This belongs in decision 6 question (1) as a property of the supplier:** *a supplier whose own
documentation disagrees about how many categories it has, on precisely the rows under examination.*

---

## §3 — `XC` — SEER against `D-093` decision 6's **five** questions

⚠ Format follows `docs/CC-2026-08-19-decision-6-supplier-answers.md`. ⚠⚠ **FIVE questions. The
Planner miscited it as three, twice, in shipped documents — `F-047` member 10.**

### (1) What it actually serves, at what granularity

**SEER serves cancer INCIDENCE, MORTALITY and SURVIVAL for the United States**, aggregated by its
**Site Recode ICD-O-3/WHO 2008** groupings, by year, and by demographic strata.

⚠ **Granularity is the site recode category — a DISEASE-level statistic.** That is exactly what
`D-093` decision 1 requires: **burden is a property of the disease and attaches by traversal**, never
a protein column. ⚠⚠ **SEER is the right shape for the burden slot in a way HPA never was.**

### (2) Open tier or controlled tier

**Open.** SEER's public incidence statistics are published by the **National Cancer Institute**, a US
Government agency. ⚠ `D-093` amendment 6 already established the credit line — *"credit the National
Cancer Institute"* — and this document does **not** re-characterise those terms.

⚠⚠ **BUT THE POPULATION IS A SCOPE LIMIT, NOT A FOOTNOTE. SEER IS UNITED STATES ONLY.** Every figure
it serves describes a US population. **Our proteins are not US-specific, and a US incidence figure
rendered beside a Swedish antibody panel is two populations on one card.** ⚠ That is a ruling for
the Planner and it is named here because question (2) is where it becomes visible.

### (3) ⚠⚠ Does the identifier space join without a lossy intermediate?

**The identifier is the TUMOUR SITE, and a SEER figure must land on one of HPA's 20 cancer strings.**

⚠⚠ **The crosswalk IS the mapping step — so it must be its own recorded step with its own failure
category, never a silent left-join.** That is decision 6's own wording, and it is satisfied: every
one of the twenty carries a verdict, and the failures are named rather than dropped.

**Which of the thirteen survive this clause:**

| | n | survives (3)? |
| --- | --- | --- |
| `mapped` | **10** | ⚠ **YES** — name to name, no intermediate |
| `mapped_with_aggregation` | **3** | ⚠ **YES, CONDITIONALLY** — the aggregation is a **stated, recorded step**, not a silent one. `colorectal` = 3 categories summed; `head and neck` = 2; `lymphoma` = 4 |
| `mapped_at_stated_granularity` | 4 | ⚠ **NOT YET** — 3 of the 4 rest on my inference about what HPA's category contains; only `liver` is now documented (§1) |
| `refused` / `uncertain` | 3 | **NO**, by construction |

⚠⚠ **So thirteen survive question (3) today, and the three aggregations survive only because the
summation is recorded.** *An aggregation performed silently would be exactly the lossy intermediate
the clause exists to bar.*

### (4) Stability — is there a versioned release a value can be pinned to?

**YES.** `https://seer.cancer.gov/data/data-changes.html`, read 2026-08-21: SEER identifies each
annual release by a **submission date** — *"November 2024 submission"*, *"November 2023 Submission"*
— alongside a publication date, and the citable form combines the submission with the data-year
span, e.g. **"1975-2021 SEER Data, November 2023 Submission"**.

⚠ **The submission date is the stable identifier**, not the publication date: the change history
shows more than one release inside a single calendar year (April and October 2024), so a year alone
does not identify a release.

⚠⚠ **A caution HPA taught us: `v22` was in the HOST NAME, and that pin turned out to carry the
LICENCE too** (`D-093` amendment 8 — v22 is BY-SA 3.0, www is BY 4.0). **SEER's pin is a STRING IN A
CITATION, not a hostname.** Nothing in the URL records which submission a downloaded figure came
from, so **the pin must be captured at fetch time and stored with the value, or it is lost.** That is
a different risk class from HPA's and it is recorded as one.

### (5) The verbatim required attribution string

⚠⚠ **UNANSWERED, AND DELIBERATELY SO.** Answering it means reading SEER's citation/usage page and
recording the required string verbatim with the date read. **That read has not been done**, and
`D-093` amendment 1 exists because a licence was **recalled rather than read** — so a plausible
string reconstructed from `amendment 6`'s summary is precisely the failure to avoid.

⚠ **A supplier confirmed on four of five items is not a supplier confirmed.** ⚠⚠ **HPA is in exactly
the same state** — item (5) open for both its files since 2026-08-19 — **so landing SEER on four of
five would make it the second supplier in the schema with an unanswered attribution string, not the
first.** That is worth the Planner seeing before it rules.

---

## §4 — What this document does NOT do

- ⚠ **No IARC or GLOBOCAN characterisation.** `WF3` asked only whether a second registry is worth
  approaching; the answer stays **yes, worth asking**, and nothing about its terms is asserted.
- **No fetch, no ingest, no table, no schema, no page, no hand-mapping.**
- ⚠⚠ **This is not a confirmation.** Question (5) is unanswered and question (2) surfaces a US-only
  scope limit that is a ruling, not a fact to be absorbed.
- ⚠ **`XA` is not in this document** — it needs the database proxy, and is reported separately.
