# ORDERS — Code — completing the cancer surface: the attribution layer, under `D-093` amendment 3

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, no newline normalisation) = `3224e774fad6ca3b4d50f22a533697ab728ab8ec090bb2c940e9457d1a722cb7`
**bytes** = `6228`

> ⚠⚠ **The hash travels INSIDE the file now**, above a range that excludes the line carrying it —
> `F-047` member 12's fix. **DOWNLOAD AND COMMIT. DO NOT RETYPE.**
>
> ⚠ **SUPPLEMENT to `ORDERS-Code-step-4-schema-ingest-surface.md`, not a replacement.** That order
> stands in full. **This changes `EA` (now answered) and `EE` item 10 (now much larger), and adds
> `EG`.** Everything else there is unchanged.
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold. Tranche 5 HELD** (`D-091` r2).
> **Production writes require the owner at the keyboard.**

---

## §0 — What changed since step 4 was written

**`EA` is ANSWERED.** The licence page was read 2026-08-19 and its text is landing as
`docs/HPA-licence-2026-08-19-as-read.md`. ⚠ **The answer is not what amendment 1 clause 3 recorded.**

**`D-093` amendment 3 rules:**
- ⚠⚠ **The surface PROCEEDS.** The Planner's earlier *"stop the surface"* is **withdrawn** — attribution
  is required identically under both candidate licences, so the unresolved licence identity does not
  gate display.
- ⚠⚠ **But the obligation is PER-DATUM, not per-page**, and it is currently unimplemented. **That is a
  hard precondition, not a hold.**
- **The licence identity is UNRESOLVED and owner-held** — the page reads *Attribution-ShareAlike 3.0
  International*, amendment 1 clause 1 records *CC BY 4.0*, and *"3.0 International"* is not a licence
  that exists. **An email to HPA is the resolution instrument. Do not act on either reading.**

---

## §1 — Task EG1 — ⚠⚠ Derive the deep-link URL pattern from the SITE. Do not construct it

**The obligation:** *"citation to the specific image, gene, or data used and the URL that links
directly to that information in a manner that will allow a third party to navigate to that image or
data on the site"*, at `v##.proteinatlas.org`.

⚠ **Do NOT infer the URL shape from recollection or from pattern-matching other HPA links.** **A deep
link that 404s discharges nothing, and one that silently resolves to the CURRENT release while
sitting beside v22 data is worse — it looks right and cites a source that is not the source.**

**EG1a — Establish the pattern by navigating the site**, and report it with the example you verified.
**EG1b — ⚠ Verify resolution on at least three real census genes AND one negative case** — a gene in
the `hpa_absent` 95. **A check with no negative case cannot fail.**
**EG1c — ⚠⚠ Confirm the `v22` host serves v22 content and does not redirect.** If it redirects to the
current release, **STOP AND REPORT** — that would also refute decision 6 question 4's stability
answer, which rests on *the version is in the host name*.
**EG1d — Report the pattern separately for the pathology view and the normal-tissue view** if they
differ. **Two edges, possibly two URL shapes.**

## §2 — Task EG2 — the attribution renders WITH the datum, and a test proves it

**The licence's own words:** *"be sure that our content is never displayed in the absence of such
citation."* ⚠⚠ **That is a `D-094` mount precondition written by HPA rather than by us.**

**EG2a — Every rendered HPA value carries its own deep link.** ⚠ **A page-level attribution block does
NOT satisfy this** and must not be built as though it does.
**EG2b — ⚠⚠ THE TEST, AND PROVE IT RED: render an HPA value with its link suppressed and watch the
suite fail.** **A precondition never seen to fire is decoration** — Principle 9.
**EG2c — The general obligation renders too**, and it is two things: a **Primary publication** and
**Human Protein Atlas proteinatlas.org**. Plus the image/data credit **Human Protein Atlas**.
**EG2d — ⚠ `v##` renders as `v22`, matching the pinned ingest.** **Assert it. A link to the current
release beside v22 data is a citation to the wrong source.**

## §3 — ⚠ Task EG3 — the primary publication, and the obvious choice is wrong

**Cite Uhlén M et al., *Tissue-based map of the human proteome*, Science (2015), DOI
`10.1126/science.1260419`** — the antibody/IHC paper.

⚠⚠ **NOT Uhlen M et al., *A pathology atlas of the human cancer TRANSCRIPTOME* (2017)**, despite its
title matching our filename. **Our `pathology.tsv` is IHC, not transcriptome.** **Selecting by title
similarity would cite the wrong modality in the citation that discharges the obligation.**

⚠ **Report which publication you rendered and why**, so a reader can check the choice rather than
inherit it.

## §4 — Task EG4 — the two categories the attribution layer must handle

- **`hpa_absent` (95)** — no value renders, so no citation is owed. ⚠ **Assert that: no orphan
  citation block on a protein with no HPA datum.**
- **`accession_ambiguous` (21)** — ⚠⚠ **KIR/HLA/OR loci where the accession maps to more than one
  gene. WHICH gene's URL would the link carry?** **It does not carry one.** **These render as the
  category, with no value and no link** — *reported, never resolved* (P2). **Assert it.**

## §5 — Task EG5 — walk it, then walk it again

⚠ **`UI honesty gaps are found by walking, not only by tests`**, and the 3Dmol defect is the standing
proof — a `200` that means `404`, live for a full session, found by looking.

**After it lands, walk:** a protein with full data · one at `hpa_absent` · one at
`accession_ambiguous` · one with `ihc_panel_empty` · ⚠⚠ **and one of `F-048`'s 58**, because a cancer
association beside a five-residue span must not become a second place where that span looks
authoritative.

⚠ **Report what the pages LOOK like, not that the tests passed.** *A cloned slide inherited its
source's footer — true, well-formed, correctly styled, about the wrong subject. No check caught it;
looking did.*

## §6 — Unchanged from step 4, restated only because they are easy to lose

⚠ **`§6` of that order — widen `test_the_scorers_feature_path_is_closed` to EVERY clinical-layer
field.** **If expression reaches the scorer, `P-001`'s question stops being answerable and nothing in
the output would show it.** ⚠⚠ **This is the single most important item in either order and it is not
about the surface.**

**Also unchanged:** the `D-100` reproduction **from the ingested table** as the ingest acceptance bar ·
both edges side by side with **no ratio, no difference, no index** (ruling 4) · the bar named in frame
(**785 / 57 / 35**) · reliability asymmetry disclosed with **no asymmetric filter** (ruling 8).

## §7 — Report

Branch and tip · ⚠ **number and title of any entry landed, in the message that lands it** · the
invariant **tested before the merge, from the set** · the gate without `.env` · **the `D-100`
reproduction as numbers** · and ⚠ **the verified deep-link pattern with the example you checked.**
