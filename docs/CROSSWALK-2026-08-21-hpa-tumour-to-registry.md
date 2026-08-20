# CROSSWALK — HPA tumour vocabulary → cancer-registry categories

> ⚠⚠ **DOCUMENTATION AND MEASUREMENT ONLY.** Nothing ingested, no table created, no page built, no
> hand-mapping performed, no licence characterised beyond `D-093` amendment 6.
> Produced under `ORDERS-Code-tumour-crosswalk-REISSUE.md` (`01949c98…`, verified).
> **Read 2026-08-21.**

---

## §1 — The twenty, and where they come from

⚠ The vocabulary was **derived from the live surface**, not from a file: `/api/census/{acc}` →
`clinical_block.tumours[].cancer`, over 60 sampled folded cards. **Twenty distinct values**, and
sampling saturated well before 60.

**⚠⚠ AND HPA'S OWN TWO PAGES DISAGREE ABOUT HOW MANY THERE ARE.**

| HPA page | says | read |
| --- | --- | --- |
| `/humanproteome/pathology` | *"17 different forms of human cancer"*, and lists 17 | 2026-08-21 |
| `/humanproteome/pathology/method` | *"20 most common forms of human cancer"*, listing **Skin cancer and Melanoma separately** | 2026-08-21 |

**Our data carries 20.** The methods page matches; the overview does not. ⚠ The three the overview
omits are exactly **`carcinoid`, `lymphoma`, `skin cancer`** — and one of those three is the row this
whole order turns on.

---

## §2 — `WC` — what HPA documents its samples to CONTAIN

**`WC1` — measured answer: HPA documents the NAMES and it does not document the CONTENTS.**
Neither the pathology overview nor its Methods Summary states what tumour subtypes any named
category contains. The methods page refers the reader to the 2017 publication for detail.

⚠ The only quantitative statement found is about a **different modality**: *"nearly 8000 cancer
patients representing 17 major types of cancer"* — that is the RNA/survival layer. **Our layer is
immunohistochemistry**, and `F-047`'s standing warning applies: *a filename is not a modality*, and
neither is a patient count from the neighbouring analysis.

**`WC2` — therefore all twenty rows carry `hpa_composition_undocumented`**, and every verdict below
that depends on composition is qualified by it. ⚠ **This is a category with a cause, not a gap in
the work.**

---

## §3 — `WB` — the twenty rows

**Registry side read from SEER's Site Recode ICD-O-3/WHO 2008 category list**
(`seer.cancer.gov/siterecode/icdo3_dwhoheme/`, read 2026-08-21).
⚠ Verdicts are against **SEER's site recode**, the categorisation the burden figures are published
under. A different registry may group differently — that is `WF3`.

| # | HPA `Cancer` (verbatim) | candidate SEER category | aggregation | verdict | kind (§5) |
|---|---|---|---|---|---|
| 1 | `breast cancer` | Breast | — | `mapped` | — |
| 2 | `carcinoid` | ⚠⚠ *none — it is a MORPHOLOGY, not a site* | — | **`refused`** | ⚠ **JOIN (axis)** |
| 3 | `cervical cancer` | Cervix Uteri | — | `mapped` | — |
| 4 | `colorectal cancer` | Colon **+** Rectum **+** Rectosigmoid Junction | ⚠ **3 categories summed** | `mapped_with_aggregation` | — |
| 5 | `endometrial cancer` | Corpus Uteri | — | ⚠ `mapped_at_stated_granularity` | — |
| 6 | `glioma` | Brain and Other Nervous System | — | ⚠ `mapped_at_stated_granularity` | — |
| 7 | `head and neck cancer` | Oral Cavity and Pharynx **+** Larynx | ⚠ **2 groups summed** | `mapped_with_aggregation` | — |
| 8 | `liver cancer` | Liver and Intrahepatic Bile Duct | ⚠ includes bile duct | `mapped_at_stated_granularity` | — |
| 9 | `lung cancer` | Lung and Bronchus | — | `mapped` | — |
| 10 | `lymphoma` | Hodgkin **+** Non-Hodgkin (nodal and extranodal) | ⚠ **4 categories summed** | `mapped_with_aggregation` | — |
| 11 | `melanoma` | **Melanoma of the Skin** | — | `mapped` | — |
| 12 | `ovarian cancer` | Ovary | — | `mapped` | — |
| 13 | `pancreatic cancer` | Pancreas | — | `mapped` | — |
| 14 | `prostate cancer` | Prostate | — | `mapped` | — |
| 15 | `renal cancer` | Kidney and Renal Pelvis | ⚠ includes renal pelvis | `mapped_at_stated_granularity` | — |
| 16 | **`skin cancer`** | ⚠⚠ **NONE** | — | **`refused`** | ⚠⚠ **COLLECTION** |
| 17 | `stomach cancer` | Stomach | — | `mapped` | — |
| 18 | `testis cancer` | Testis | — | `mapped` | — |
| 19 | `thyroid cancer` | Thyroid | — | `mapped` | — |
| 20 | `urothelial cancer` | Urinary Bladder **+** Ureter **+** Renal Pelvis | ⚠ **3 categories; renal pelvis is ALSO in row 15** | ⚠ `uncertain` | ⚠ **JOIN** |

### Distribution

| verdict | n | rows |
| --- | --- | --- |
| `mapped` | **10** | 1, 3, 9, 11, 12, 13, 14, 17, 18, 19 |
| `mapped_with_aggregation` | **3** | 4, 7, 10 |
| `mapped_at_stated_granularity` | **4** | 5, 6, 8, 15 |
| **`refused`** | **2** | **2 (carcinoid), 16 (skin cancer)** |
| ⚠ **`uncertain`** | **1** | **20 (urothelial)** |

**⚠⚠ THIRTEEN of twenty join today** (`mapped` + `mapped_with_aggregation`), four more join at a
stated granularity, and **two refuse.** ⚠ **The live copy said the names *"cannot be matched up"* —
that sentence was false about seventeen of twenty rows,** and `WA` has already replaced it.

⚠ **Row 20 is `uncertain` and is NOT rounded toward `mapped`:** urothelial carcinoma occurs in
bladder, ureter and renal pelvis, and **renal pelvis is inside row 15's category too**. Summing
both rows would double-count it. Which grouping is right is a decision, not a lookup.

⚠ **Row 5, 6, 8, 15 are `mapped_at_stated_granularity`, not `mapped`:** SEER's category is *wider*
than HPA's name in each case (corpus uteri ⊃ endometrium; brain ⊃ glioma; liver+bile duct ⊃ liver;
kidney+renal pelvis ⊃ kidney). Both sides must be printed for what they **contain**, never for what
they are called.

---

## §4 — `WD` — the skin question, READ

**`WD1` — quoted from the primary source.**
**SEER Program Coding and Staging Manual 2026**, September 2025, **page 15**, under
***"b. Do not report (Exceptions to reporting requirements)"*** —
`https://seer.cancer.gov/manuals/2026/SPCSM_2026_MainDoc.pdf`, read **2026-08-21**:

> **i. Skin primary (C440-C449) with any of the following histologies**
> Malignant neoplasm (8000-8005)
> Epithelial carcinoma (8010-8046)
> Papillary and squamous cell carcinoma (SCC) (8050-8086)
> Squamous intraepithelial neoplasia III (SIN III) (8077) of skin sites coded to C44_
> Basal cell carcinoma (8090-8110)
>
> **Note 1:** *"If the registry collects basal or squamous cell carcinoma of skin sites (C440-C449),
> sequence them in the 60-87 range and **do not report to SEER**."*
>
> **Note 2:** *"SCC of sites coded to C44 (for example, C442 located in the head or neck) is not
> reportable."*

And from the **site recode category list** (read 2026-08-21), the skin grouping is literally named:

> **"Skin excluding Basal and Squamous"** — subdivided into **"Melanoma of the Skin"** and
> **"Other Non-Epithelial Skin"**.

**⚠⚠ THE EXCLUSION IS REAL, AND IT IS WIDER THAN "the name is odd".** BCC and SCC are *epithelial*,
so SEER's remaining bucket — *Other **Non-Epithelial** Skin* — cannot hold them either. **There is
no SEER category for non-melanoma epithelial skin cancer at all.**

**`WD2` — the finding, stated as the useful kind:**
⚠⚠ **The most common cancers in humans are systematically not counted by the primary US cancer
registry.** That is not a naming quirk and not a join problem — **it is a COLLECTION hole**, and it
is the kind that is a real epidemiological gap rather than a task.

⚠ **And it is not a defect in SEER.** The manual states the rule openly; the site recode category
*says so in its own name*. **The gap is documented, deliberate, and load-bearing for anyone who
tries to size a skin-cancer indication from registry data.**

**`WD3` — corroboration already on our surface:** `LAMP1`'s `normal_tissues` carries **"skin 1"** and
**"skin 2"** as separate `High` entries — HPA's free text splitting one tissue two ways with no code
to reconcile them. ⚠ The tumour side is the harder version of the same absence.

⚠⚠ **AND THE STRONGEST SIGNAL IS IN HPA'S OWN LIST:** the methods page carries **`Skin cancer` and
`Melanoma` as SEPARATE categories.** That separation implies HPA's *"skin cancer"* is *non-melanoma*
skin cancer — i.e. precisely the population SEER does not count. ⚠ **This is an INFERENCE from the
separation, not documentation**, because §2 established HPA documents no category's contents. **It
is the single most valuable thing to confirm**, and confirming it converts row 16 from `refused` to a
clean `mapped_at_stated_granularity` **against a registry that counts that population**.

---

## §5 — `WE` — which kind of hole, per non-`mapped` row

| row | kind | why |
| --- | --- | --- |
| **16 `skin cancer`** | ⚠⚠ **COLLECTION** | SEER does not COUNT this population. A real epidemiological gap |
| **2 `carcinoid`** | ⚠ **JOIN (axis)** | carcinoid is a MORPHOLOGY; the site recode is by SITE. Our data does not say where the carcinoid was, so there is nothing to join *on* — a task, not a finding |
| **20 `urothelial`** | ⚠ **JOIN** | three registry categories, one overlapping row 15. A decision about grouping, not a missing count |
| 5, 6, 8, 15 | ⚠ **UNMEASURED (partial)** | the join works; what is unmeasured is **what HPA's category contains** (§2). Neither a research hole nor a task until `WD`'s inference is confirmed |

⚠⚠ **Only row 16 is a research hole.** Reporting rows 2 or 20 as one would be the over-claim `P-004`
argues against in other people's work — a task dressed as a discovery.

**`WE1` — the count that reaches the research question.**
**Two of twenty** HPA tumour types have no burden counterpart today (`carcinoid`, `skin cancer`).
⚠⚠ **For those two we hold tumour staining over a population whose size and mortality nobody knows**,
and a target can look attractive in an indication with no denominator.

⚠ **How many proteins that touches is NOT reported here, and the reason is §7.** Counting cohort and
census proteins carrying IHC in those two indications means reading `clinical_pathology` across
2,690 cards — **that is DATA, not documentation**, and §7 says stop and report. **The query is one
`SELECT` against a table we already hold, needs no new source, and I will run it the moment it is
ordered.**

---

## §6 — `WF` — the route out of every verdict

**`WF1` — ⚠⚠ THIRTEEN ROWS ARE READY AND BLOCKED ONLY BY A FETCH.**
`mapped` (10) + `mapped_with_aggregation` (3). SEER is **US Government, public domain**, and `D-093`
amendment 6 already established the credit line — *"credit the National Cancer Institute"*.
**Nothing stands between those thirteen rows and an incidence figure except downloading the data.**
⚠ **The live copy implied otherwise and that is why `WA` shipped first.**

⚠ **But no supplier enters the schema without `D-093` decision 6's five questions, and SEER has never
been through them.** What decision 6 would need for SEER — *stated, not answered, because answering
it here is exactly the mistake this order records twice*:
1. what the source **is** and which modality it measures;
2. its **population and denominator** — SEER is **US-only**, which is a scope limit on every figure;
3. its **vintage** and how a version is pinned;
4. its **terms**, read rather than recalled;
5. the **attribution** the terms require at the point of display.

**`WF2` — a JOIN hole is a task, and it is an afternoon.**
Rows **2** and **20** are plugged by a human mapping twenty names onto a controlled vocabulary once.
⚠ Row 2 needs more than a mapping: `carcinoid` carries **no site**, so it needs either a site from
HPA or a decision to report it against an all-sites denominator — **which is a decision, not a
mapping**. ⚠⚠ **Not performed under this order**: it is a ruling about a controlled vocabulary and
wants its own entry.

**`WF3` — a COLLECTION hole is a SEEK.**
⚠ Row **16** is refused **by SEER**, not by every registry. SEER is US-only and counts under US
rules; **a cancer uncounted by one registry may be counted by another**, and IARC's programmes count
different populations under different rules.
⚠⚠ **Worth asking: YES**, and that is the whole of this line. **I have not characterised IARC's
terms, coverage or whether it counts non-melanoma skin cancer** — that is decision 6's question, and
the order records twice what happens when it is answered from memory.

---

## §7 — What this document does NOT do

- **No data was downloaded**, no registry file fetched, no table created, no schema touched, no page
  built, and **no hand-mapping performed**.
- ⚠ **No licence characterised** beyond what `D-093` amendment 6 established for HPA and NCI.
- ⚠⚠ **`WE1`'s protein count is deliberately unreported** — it needs a query, and §7 says stop.
- ⚠ Row 16's central inference — that HPA's *"skin cancer"* is non-melanoma — **is labelled an
  inference and is not counted as documentation** anywhere above.
