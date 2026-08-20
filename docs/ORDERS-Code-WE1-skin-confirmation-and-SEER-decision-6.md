# ORDERS — Code — the protein count, the HPA skin/melanoma read, and SEER through decision 6

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `5c62568636b94a5ce12729ca2fd5cc68c7c15683deb2304fef0504a719f9191f`
**bytes** = `5996`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **STILL NO INGEST.** §3 ANSWERS decision 6's five questions for SEER; it does not fetch, ingest
> or schema anything. **`D-093` is void if code precedes it.**
> ⚠ Grounding: your report at `feat/tumour-crosswalk-and-burden-copy @ 3811df5`. **No GPU, no rental,
> no fold, no fit.**

---

## §0 — Accepted, and the crosswalk changed the picture

**Seventeen of twenty join in some form** — **10 `mapped` · 3 `mapped_with_aggregation` · 4
`mapped_at_stated_granularity` · 2 `refused` · 1 `uncertain`.** ⚠⚠ **The live copy had been telling
readers the vocabulary could not be joined while 85% of it could.**

⚠ **`uncertain` on urothelial was the right call** — *renal pelvis sits inside two candidate
categories, so summing both double-counts it: a grouping decision, not a lookup.* **Rounding it to
`mapped` would have produced a number inflated by an unknown amount, silently.**

**`WD` is read, quoted and dated.** ⚠⚠ **And the epithelial argument is the part that makes it a
finding rather than a naming complaint: the recode splits into Melanoma and Other Non-Epithelial
Skin, BCC and SCC are epithelial, so THERE IS NO SEER CATEGORY THAT COULD HOLD THEM.** **Documented
and deliberate, not a SEER defect.**

---

## §1 — Task XA — `WE1`, the protein count. One `SELECT`, no new source

⚠ **Stopped correctly under §7 — *that's data, not documentation*.** **Ordered now.**

**XA1 — For the tumour types with NO burden counterpart** (`refused` **carcinoid, skin cancer**, plus
⚠ `uncertain` **urothelial reported SEPARATELY, never pooled with the refusals**): **how many cohort
proteins and how many census proteins carry IHC data in those types?**
⚠ **Both populations, keys stated, NOT pooled** — *`F-011` and `F-016` were different mechanisms and
were never pooled.*

**XA2 — ⚠ Report the rows, not only the counts, for the cohort side.** **82 is small enough to
enumerate and *a count of n is not n rows*.**

**XA3 — ⚠⚠ And the discriminating cut: how many of those proteins carry `High` staining in a tumour
type with no burden counterpart?** **A protein staining `High` in an uncounted indication is the case
that makes the point** — ⚠ **we would hold tumour staining for a population whose size and mortality
nobody knows, and an ADC therapeutic case cannot be made without a denominator.**
**Measure it. The Planner frames it.**

## §2 — ⚠⚠ Task XB — the HPA skin/melanoma read, which the crosswalk turns on

**Your inference: HPA's methods page lists *Skin cancer* and *Melanoma* separately, so *skin cancer*
is likely the non-melanoma population SEER will not count.** ⚠ **Labelled an inference, not
documentation — correctly, and that restraint is why it is worth pursuing.**

**XB1 — Read HPA's own pages for a statement of what its *Skin cancer* samples ARE.** ⚠ **Quote it
with URL and date read.** ⚠⚠ **If HPA does not say, the answer is `hpa_composition_undocumented` and
the inference stays an inference** — **do not upgrade it by argument.**

**XB2 — ⚠ The two HPA pages disagree: 17 forms on the pathology overview, 20 on the methods page, and
the three omitted are carcinoid, lymphoma and skin cancer.** ⚠⚠ **Two of the three are the rows this
order turns on.** **Report the discrepancy as a property of the supplier, with both URLs and both
dates** — *a supplier's own documentation disagreeing with itself, on precisely the rows under
examination, is a fact about the supplier and belongs in decision 6's question (1).*

**XB3 — ⚠ If `Skin cancer` IS documented as non-melanoma, say what that does to the verdict.**
**It may move `refused` → `mapped_at_stated_granularity` on the melanoma side while the BCC/SCC
population stays a COLLECTION hole.** ⚠⚠ **Two facts, not one, and the entry must not let the second
disappear behind the first.**

## §3 — Task XC — SEER through `D-093` decision 6. ANSWER the five, do not fetch

⚠⚠ **Thirteen rows are blocked by nothing but a fetch** — **SEER is US Government, public domain,
credit established by `D-093` amendment 6.** ⚠ **But SEER has never been through decision 6, and *a
supplier that cannot answer (3) with a pinned mapping does not enter the schema*.**

**Answer all FIVE, in decision 6's own format.** ⚠⚠ **It is FIVE questions across FIVE suppliers and
the Planner miscited it as three, twice, in shipped documents.** **HPA is answered on four of five;
item 5 — *the verbatim required attribution string* — remains open for HPA and must be answered for
SEER.**

⚠ **Question (3) is the one that decides entry: does SEER's identifier space join to our tumour
vocabulary WITHOUT a lossy intermediate?** **The crosswalk IS that mapping step — so it is *its own
recorded step with its own failure category, never a silent left-join*, which is decision 6's own
wording.** ⚠⚠ **Report which of the thirteen would survive that clause and which would not.**

**XC1 — ⚠ Question (4), stability: is there a VERSIONED SEER release a value can be pinned to?**
**HPA gave us `v22` in the host name and that pin turned out to carry the LICENCE too.** **Report
SEER's equivalent, or state that it has none** — *a supplier with no version pin is a different risk
class and must be recorded as one.*

**XC2 — ⚠ Do NOT characterise IARC or GLOBOCAN.** **`WF3` asked only whether a second registry is
worth approaching, and characterising its terms is the mistake this project has now recorded twice.**

## §4 — ⚠ Not ordered

**No fetch, no ingest, no table, no schema, no page.** **No hand-mapping to ICD-O** — ⚠ that is a
controlled-vocabulary decision and wants its own entry. **No supplier confirmation for anyone but
SEER, and even that is ANSWERS, not confirmation** — ⚠⚠ **the Planner rules on whether SEER enters
the schema, not this order.**
⚠ **If any question needs data rather than documentation, beyond `XA`'s single `SELECT`, STOP AND
REPORT.**

## §5 — Report

⚠ **`XA3` first — it is the one that reaches the research question.** Then `XA1`/`XA2` with keys ·
`XB1` quoted with URL and date · `XB2`'s discrepancy · `XC`'s five answers with (3) and (4) called out
· branch and tip · both invariants with their keys · the gate without `.env`.
