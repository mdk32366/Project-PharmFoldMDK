# D-080 — Claim discipline in educational surfaces: a briefing breaches D-028 by **supplying a premise**, not only by making a claim — plus the glossary as singular data, reading level as a ruled constraint, and the `external_value` category Constraint A never had

> **STAGED ENTRY — merge into `docs/README.md` before the briefing surface ships.**
>
> **⚠ Confirm the number against the live log before merging.** Snapshot state read this session:
> highest `### D-` is **D-075**; **D-076** claimed by a staged file with no log entry; **D-077**
> staged; **D-078 reserved by name** in D-077 decision 7 for the F-008 precision A/B; **D-079**
> staged this session (clinical association layer). **D-080 is next free *if* all of those land as
> written.** Check the thing, not the reference to it.

- **Date:** 2026-08-17
- **Status:** Proposed → Accepted on merge.
- **Type:** A **decision**. It rules how a class of surface may speak. It produces no measurement.
- **Relates:** **D-015 §1a**; **D-016**; **D-024** (the honest reading travels with the result);
  **D-028** (**the entry this extends** — the UI detects and classifies, never explains);
  **D-050 / Constraint A** (derive, don't hardcode — **§5 fills a hole in it**); **D-069** (every
  surface self-sufficient); **D-074** (a finding stays open until the instrument carries the
  statement of what it gets wrong); **A-017** (the fixture must discriminate); **UI_Plan_v2 §5**
  (the one-sentence-wide gap) and **§7** (the briefing, metaphor kept, outcome claims bounded);
  **F-005**; **F-012**; **D-079** (whose clinical terms enter the same glossary).
- **Provenance (D-016):** Planner raised, owner ruled, 2026-08-17 — *"Entering a D-entry doesn't
  hurt, for the good and proper reasons you bring up."* The reasons: §6 and §7 of the briefing copy
  contain rulings, and **a ruling that lives only in a content file is a ruling nobody will find in
  the log.** Artifacts governed: `BRIEFING-copy-about-adcs.md`, `glossary.json`.

---

## Context — why D-028 does not already cover this

D-028 was written about **attribution**. Its worked example is a string on the Scorer surface:

> ✅ *"Feature 6 accounts for most of this target's structural rank."* — about the model, true.
> ❌ *"This target ranks higher because its epitope is more accessible."* — about biology, and the
> system has no standing to say it.

That rule is well-formed and the Scorer surface obeys it. **It does not reach the briefing, because
the briefing does not attribute anything.** It teaches.

**And a teaching surface can breach D-028 without containing a single forbidden sentence.** The
mechanism:

1. The briefing says, truthfully, *antibodies bind accessible surface patches.*
2. The Scorer says, compliantly, *feature 6 accounts for most of this target's structural rank.*
3. The reader — correctly, using only what the product gave them — concludes *this target ranks
   higher because its epitope is more accessible.*

**Nobody wrote the forbidden sentence. The product supplied both halves and the reader assembled
it.** The claim is then attributed to us, and we cannot point to where we made it.

**This is the finding this entry exists for, and it generalises:** D-028 governs what a surface
*asserts*; it has nothing to say about what a surface *supplies as a premise*. The briefing is the
highest-leverage premise-supplying surface in the product, because it is where the reader's mental
model is built before they see a single number.

---

## Decision (1) — ⚠ **A surface is accountable for the premises it supplies, not only for the claims it makes.** The load-bearing ruling.

**Ruled:** any surface that teaches mechanism must be reviewed against the claims *other* surfaces
make, and the test is not *"is each sentence true?"* but:

> **Can a reader assemble a D-028-forbidden sentence from this surface plus any other surface in the
> product, using no outside knowledge?**

If yes, one of the two must change, and **the teaching surface changes** — because the Scorer's
attribution string is load-bearing on the result and the briefing's phrasing is not.

**The concrete application, already made in the copy:** the briefing may state that antibodies bind
conformational surface patches. It **may not** state or imply that feature 6, feature 7, SASA, or
any highlighted region *measures*, *finds*, *predicts*, or *approximates* that. The copy discharges
this by naming the gap outright — *whether the measurement relates to where antibodies bind is the
open question this project is testing, not an assumption the tool is built on.*

**Why this framing rather than silence:** the alternative was to omit the mechanism entirely, which
would make the tool incomprehensible and would not remove the inference — a reader who knows any
immunology supplies the premise themselves. **Naming the gap explicitly is the only version that
both teaches and holds.** It is also, as a matter of positioning, the stronger claim: a project that
states its central question as open is doing science, and one that quietly assumes the answer is not.

---

## Decision (2) — The banned-phrase list is a **gate**, not a style guide

D-028's copywriting requirement has, until now, been enforced by care. Care does not survive a
Builder session at 1 a.m.

**Ruled — the following constructions are barred from every rendered UI string**, checked
mechanically across all surfaces including the briefing, the glossary, tooltips, and the
Limitations page:

| Barred | Because |
|---|---|
| "binding site", "possible binding site", "candidate binding site" | asserts biology the system cannot assess |
| "epitope" used to label a **computed region** | conflates the biological object with a geometric one |
| "antibody-accessible", "reachable by an antibody", "druggable surface" | asserts reachability from an unglycosylated single-chain prediction |
| "likely", "probable", "predicted" applied to **binding** (as opposed to structure) | a confidence claim on a quantity never estimated |
| "this target is a good / promising / strong ADC candidate" | the outcome claim UI_Plan_v2 §7.2 bounds |

- The term **epitope** remains permitted as a **glossary and teaching term** — it must be, or the
  mechanism cannot be explained. It is barred only as a **label on a computed object**. The gate
  distinguishes the two by context, and where it cannot, the copy is rewritten rather than the gate
  loosened.
- **The list is extensible and additions are appended here, dated.** A phrase removed from the list
  requires an entry saying why.
- **Proven by revert** (A-017): insert a barred phrase into a fixture surface, watch the gate redden.

---

## Decision (3) — One glossary, as **data**, singular by construction

**Owner ruling, 2026-08-17: one merged glossary, hyperlinked, with tooltips, dual-audience.**

**Ruled:**

1. **`glossary.json` is the single source.** Every term, from every surface — ADC briefing, Scorer,
   coverage, clinical layer, and the **16 rejected topological-domain terms** — lives in this one
   file. **No second glossary file may exist.**
2. **It is data, not prose.** Tooltips cannot be driven from markdown, and a prose glossary
   alongside a data one is two paths to one definition — the project's most-repeated defect class,
   in its least-guarded form.
3. **⚠ The `source` field is provenance only and MUST NOT be used to re-split the file.** It records
   which surface introduced a term. A UI that filters the glossary by `source` has recreated the two
   glossaries this ruling exists to prevent, and the filtering is barred rather than discouraged.
4. **Dual-audience is structural, not aspirational:** every entry carries `plain` (the tooltip,
   written for a non-scientist) and `technical` (the expanded entry). Neither may be empty. An entry
   whose `plain` field merely restates the term fails review.
5. **No term is defined twice**, and every bolded or linked term in any surface resolves to exactly
   one entry. Both directions are asserted: unresolved links fail, and orphan entries are reported.
6. **The 16 rejected topology terms are a recorded gap**, not an omission — they are named in
   `_open_items` and the standing ruling that each carries its reason, dual-audience, is unchanged.

---

## Decision (4) — Reading level is a **ruled constraint**, not a preference

**Owner ruling, 2026-08-17: 8th-grade reading level for the briefing.**

**Recorded as a decision rather than a style note, because it is load-bearing on D-024 and D-069.**
Those entries require that the honest reading — the coverage line, the caveats, the limitations —
**travels with the result**. A caveat written so that only a specialist can parse it has not
travelled anywhere. **The reader who most needs the limitation is the least equipped to decode it**,
so prose difficulty is a mechanism by which a disclosure obligation is technically met and
substantively defeated.

**Ruled:**

- The briefing and every `plain` glossary field are written at approximately 8th-grade level.
- **Domain terms are not avoided — they are defined on first use and glossed.** Vocabulary
  avoidance would make the surface useless to the scientist audience and is not what this rules.
- **Limitations are held to the same standard as the explanations.** A briefing written plainly with
  caveats written densely is the precise failure this decision prevents, and §7 of the copy is where
  it would happen.

---

## Decision (5) — The `external_value` category: **the hole in Constraint A**

**Constraint A (D-050) rules that every number on a surface derives from the payload, never typed.**
It has no provision for a number that is **not a project measurement at all** — a literature value
like *~90% of epitopes are conformational* or *15–25 contact residues*. Under Constraint A as
written such a number is a violation, which is wrong; the honest handling is not to derive it but to
**label it**.

**Ruled — every number rendered in the UI is exactly one of three kinds, and the kind is explicit:**

| Kind | Rule |
|---|---|
| **Derived** | Computed from the live payload. Never typed. Constraint A, unchanged. |
| **External** | A literature value. Carries `external_value` in the glossary, is **cited**, and is **marked in the copy as external**. |
| **Configured** | A fixed parameter of our own method (the 0.25 threshold, the 1.4 Å probe). Derived from the named constant, never a literal. |

- **⚠ A derived number and an external number may not render adjacent without visible distinction.**
  Side by side and unmarked, the external one borrows the derived one's provenance — which is
  D-016's failure mode exactly: a claim whose *how it is known* has been silently upgraded.
- **Every `external_value` requires a verifiable citation before publication.** The two currently in
  the copy (~90% conformational; 15–25 residues) are **flagged and unverified** — Planner
  recollection, citations not checkable from the drafting session. They ship in the UI marked as
  external; they do not enter the paper until sourced.

---

## Decision (6) — Disclosure is a **mount precondition**, not a caption

**D-074's available exit for F-005 and F-012 is that the instrument carries the statement of what it
gets wrong.** A caption satisfies that in letter only, because a caption can be removed in a layout
change by someone who never read the finding.

**Ruled:**

- **Structure-region rendering on the 3Dmol viewer cannot mount without the F-012 single-chain
  disclosure component present.** Not styled beside it — a hard dependency. **Proven by revert:**
  remove the component, the region-rendering test reddens.
- The same applies to any surface reporting feature 6 or feature 7: the disclosure is a dependency
  of the number, not a neighbour of it (D-069).
- **The general principle, which is the reusable part:** *where a finding against the instrument is
  open, the disclosure is a structural dependency of the thing it qualifies.* This is how D-074's
  second exit is discharged in a UI, and it applies to every future open finding without needing to
  be re-ruled.

---

## Decision (7) — What this entry does **NOT** do

- **It does not amend D-028** — it extends its reach to premise-supplying surfaces and gives it a
  gate. The existing attribution rule is untouched.
- **It does not amend Constraint A** — it adds the category Constraint A lacked. Derived numbers are
  governed exactly as before.
- **It does not touch the six features, the scorer, F-004, or any result.**
- **It does not close F-005 or F-012.** Both remain open; this rules how they are disclosed.
- **It does not supply the 16 topology glossary entries.** Recorded gap.
- **It does not verify the two external values.** Flagged, unverified, gated for the paper.

---

## Deep-learning justification

**The briefing is where the reader's model of the model is built, and every result is interpreted
through it.** A correct result read through a wrong mental model produces a wrong conclusion, and
the product — not the reader — is responsible for that.

The specific DL content the briefing carries is the distinction that F-012 §8 identified as the
project's recurring lesson: **the gap between what a network optimised and what we read off its
output.** ESMFold optimised single-chain structure from sequence. It did not optimise quaternary
assembly, glycosylation, or binding. Every limitation in §7 of the copy is an instance of that one
gap, and teaching it plainly is the most transferable thing this project has to say to a reader.

Decision 1 is the DL-adjacent ruling proper: **a system's honesty is a property of what a user can
conclude from it, not of what it asserts.** For a product built on a model whose outputs are
routinely over-read, that distinction is the difference between a defensible tool and a persuasive
one.

---

## Consequences / test surface — written before the components

- Banned-phrase gate runs over **all** rendered strings; proven by revert (decision 2).
- Every linked term resolves to exactly one `glossary.json` entry; unresolved links fail; orphan
  entries are reported (decision 3.5).
- `plain` and `technical` are both non-empty for every entry (decision 3.4).
- No second glossary file exists; a `source`-filtered glossary view fails (decision 3.3).
- Every UI number carries its kind; a derived and an external number rendering adjacent without
  distinction fails (decision 5).
- Structure-region rendering cannot mount without the F-012 disclosure; proven by revert
  (decision 6).
- Each of the four limitations in copy §7 links to its owning Limitations entry; broken or missing
  links fail.
- **Adversarial review, recorded as a required step rather than a habit:** before the briefing
  ships, one pass whose only question is decision 1's test — *what forbidden sentence can a reader
  assemble from this surface plus any other?* Findings from that pass are logged, not silently
  edited.

---

## Open items

| Item | Gates | Owner |
|---|---|---|
| 16 rejected topology terms merged into `glossary.json` | glossary completeness | Matt / Planner |
| Citations for the two `external_value` numbers | **the paper**, not the UI | Matt |
| Adversarial premise-assembly review pass | briefing ship | Matt / Planner |
| Banned-phrase list implemented as a gate | briefing ship | Builder |
