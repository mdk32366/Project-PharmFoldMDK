# ORDERS — Code — attribute it: every surface, every datum, and there are more than two

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence** — the header above describes the marker) = `62102e05e3a630c4a5730648dbfd0b9d145446101243a559e8953529b3e7bbac`
**bytes** = `5499`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
> ⚠ Grounding `b06d378`, `git archive`, no manifest, dirty state unknowable.
> **No GPU, no rental, no fold, no fit, no ingest, no migration.**

---

## §0 — Owner ruling, and the thing that changes the scope

**R1 (owner, 2026-08-20): *"So let's attribute it by all means."*** **`D-093` amendment 3 item 3's
four elements ship.**

⚠⚠ **AND THE AUDIT WAS SCOPED TOO NARROWLY. `NC` examined `ClinicalEdges.jsx`. That component's own
header says: *"`CancerAssociations` (D-053) shows the paper's quasi H-score over the 82."*** **So
HPA-derived data renders in AT LEAST TWO components and the audit covered one.**

⚠ **Two consequences:**
- **`qh` RENDERS.** **That answers `D-093` amendment 8 §6's named open item — the one fact that most
  moves the Adaptation reading — and it answers it the LESS convenient way.** **Recorded, not acted
  on; §6 stays parked under amendment 7 trigger 4.**
- ⚠⚠ **`D-053` predates the clinical layer, so HPA data has been on the surface far longer than four
  days, unattributed.** **The gap is older than the entry that found it.**

---

## §1 — ⚠⚠ Task PA — ENUMERATE EVERY SURFACE THAT DISPLAYS HPA-DERIVED DATA. Do not assume two

**PA1 — Both directions** (Part C Step 19):
- **Forward:** every component, route and API payload that renders a value **originating in HPA** —
  `pathology.tsv`, `normal_tissue.tsv`, or **anything computed from them.**
- ⚠ **Reverse:** for every HPA-sourced field in the data model, **where does it surface?**
  **A field that renders nowhere is a category with a cause, not an omission.**

**PA2 — ⚠⚠ `qh` COUNTS AS HPA-DERIVED AND THE ROUTE DOES NOT CHANGE THAT.** `CancerAssociations`
sources from Kathad's S3 — ⚠ **and `D-100` established S3 is a VERBATIM EXTRACT of `pathology.tsv`,
1,640 / 1,640, all four count columns identical.** **CITING THE PAPER IS NOT CITING HPA.** **The
obligation attaches to the underlying source, whichever route the numbers took.**

**PA3 — Report the list with, for each: the component, what it renders, the HPA file behind it, and
whether the row carries a gene identifier a deep link could use.** ⚠ **If any surface renders an
HPA value with NO key back to a gene, say so — that one is a design question, not a rendering one.**

## §2 — Task PB — the four elements, per datum, on every surface `PA` finds

**From `D-093` amendment 3 item 3, and all four are required — the general case AND the specific:**

1. **A Primary publication** — ⚠⚠ **Uhlén M et al., *Tissue-based map of the human proteome*,
   Science (2015), DOI `10.1126/science.1260419`.** **NOT the 2017 *pathology atlas of the human
   cancer TRANSCRIPTOME*, despite matching our filename.** **`pathology.tsv` is IHC.**
2. **The website reference** — *Human Protein Atlas proteinatlas.org*.
3. ⚠ **The image/data credit — *Human Protein Atlas* — AS ITS OWN ELEMENT.** **Amendment 1 clause 3
   dropped it and `NC` confirms it was never built.**
4. ⚠⚠ **THE PER-DATUM DIRECT LINK to `v22.proteinatlas.org`.** **The pattern is already derived and
   verified at `EG1` — reuse it, do not re-derive.** **A single block per page does not discharge
   this.**

## §3 — ⚠⚠ Task PC — the mount precondition, and it covers EVERY surface from `PA`

**The licence words it as a precondition: *"be sure that our content is never displayed in the absence
of such citation."*** ⚠ **`D-094`'s shape, written by HPA.**

**PC1 — A test that reds when an HPA value renders without its citation.** ⚠⚠ **Parameterised over
`PA`'s full list, not written against one component** — **the whole reason this order exists is that
the last audit was scoped to its author's field of view, which is `F-052`'s subject.**

**PC2 — ⚠ Prove it red four ways, each reddening exactly ONE test**, on `NB4`'s pattern: remove the
link · the publication · the website reference · the credit. **Four properties, four proofs.**

**PC3 — ⚠⚠ A test that FAILS WHEN A NEW HPA-RENDERING SURFACE APPEARS UNCOVERED.** **Otherwise the
next component repeats this exactly** — *a convention obeyed by every caller except the newest one*
is `F-052`, and this order is its second instance in three days.

## §4 — Task PD — `v22`, and it is not decoration

⚠⚠ **Every link renders `v22`, matching the pinned ingest.** **`D-093` amendment 8: `v22` states
BY-SA 3.0 and `www` states BY 4.0 — two different licences on two live pages.** ⚠ **A link to the
current release beside v22 data cites a source that is not the source, AND points at different
terms.** **Assert it.**

## §5 — ⚠ Not ordered

**No change to the licence quotation beyond what `NB` shipped** — amendment 3 item 5 stands.
**No decision 7 change. No Adaptation/Collection ruling. No email.**
**No bulk export, no dataset download, no API serving HPA values** — ⚠ **amendment 7 trigger 4, and
it is what keeps amendment 8 §6 parked.**
⚠⚠ **If `PA` finds a surface where attribution cannot be attached without a data-model change, STOP
AND REPORT.** **That is a ruling, not a rendering task.**

## §6 — Report

⚠ **`PA`'s enumeration FIRST** — it sets the scope of everything else and the Planner's count of two
is a floor, not a total.
Then the four elements as **observed renders**, not as code reading · `PC`'s four red proofs ·
⚠ **the live walk once merged**, since `NB5` correctly declined to claim one from a captured DOM ·
branch and tip · **number and title of any entry landed in the message that lands it** · the
invariant with its keys **including the amendment figures** · the gate without `.env`.
