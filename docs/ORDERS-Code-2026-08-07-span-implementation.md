# ORDERS — Code — 2026-08-07 (revised) — Implement the span rulings, re-extract, and surface it

> **Governed by `RULINGS-2026-08-07-span-definition.md` (owner, binding), `### D-079`, `### F-025`
> and `### D-081`.** Restates none of them. Where this file and the log differ, **THE LOG GOVERNS.**
> ⚠ This file is an order, not authority.
>
> ⚠ **SUPERSEDES `ORDERS-Code-2026-08-07-f025-and-definition-freeze.md`** for Tasks 1–3 only.
> **Its Task 0 (the term table + the 873 / 659 / 107 reconciliation) still stands and is still
> owed.** Do not execute both.

## SIX TASKS: 0–5. Sequential. Hard stop between each.
**If this document does not end with `— END OF SPAN IMPLEMENTATION (6 of 6) —`, it truncated. Report and request re-delivery.**

> **Planner provenance (D-016):** every count below is **Code's reading**. The Planner independently
> reproduced only the 12-vs-13 selector arithmetic and the 96.2% / 25.1% ratios. The GPI trafficking
> citations were retrieved by web search 2026-08-07. **No connector, no `.git`, no database.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** two log entries and one decision entry · `RESERVED.md` updates · **changes to the
span extraction rules per the rulings** · **re-extraction of census spans only** · UI glossary and
tooltip work · Task 4's manifest **once Tasks 0–3 land**.

**Does NOT authorise:**
- ⚠⚠ **ANY re-extraction, re-fit, re-score, re-rank or re-fold of the 82.** **D-081 forbids it
  absolutely.** `### F-004` and `### F-017` are frozen. **If any change would touch
  `protein_analyses`, `protein_features`, `ranking_runs`, `ranking_results` or `target_scores` for
  the cohort — STOP.**
- ⚠ **GPI status as a feature, a score component, a rank input, or a sort key.** R2.2. **It is a
  disclosed attribute only.**
- ⚠ **Scoring any census row.** D-079 dec 1 stands; the scorer-import refusal enforces it.
- Run B · the wiring PR · the freeze.

## STOP AND REPORT

- any change would alter a cohort artifact — ⚠ **stop before writing, not after**
- the next free `F-` or `D-` integer differs from expected — **confirm live, never assume**
- the checker returns anything but `UNRESOLVED AND UNRESERVED: none — invariant holds`
- a re-extraction changes a **surface** count in a direction the rulings do not explain
- a permission denial — ⚠ **stop-and-report: the command, the point, the artifact's state**

---

# TASK 0 — Still owed. The term table and one reconciliation.

**`span-extraction.txt` has not reached the Planner.** Paste it or give the path on the branch.

⚠ **And state, one line each, what population each of these counts:** **873** (proteins with any
`Topological domain`) · **659** ("vocabulary-recoverable") · **107** (surface reachable, *"not 106 —
the extra is SDK1"*). **873 and 659 differ by 214 and the Planner will not guess why.** ⚠ **A
residual is not a measurement.**

---

# TASK 1 — `### F-025` into the log

**Per the previous order's Task 1, unchanged.** Five mechanisms with counts · the code at
`ecd_lengths.py:194-196` · **13 of 82 in buckets 3 / 6 / 3 / 1 with bucket 4 EMPTY** ·
⚠ **`MSLN` excluded by extraction not labelling, so `n=12` is partly an artifact** · both foldable
counts are floors · **the Planner's selector defect that masked SDK1** · **not closed under D-074.**

Strike `F-025` in `RESERVED.md`, run the checker verbatim, report the literal output and set size.

---

# TASK 2 — `D-081`: the definition freeze

⚠ **Confirm the next free `D-` live.** Expected `D-081` (D-079 highest written; D-078, D-080
reserved-unwritten). **Report the literal value.**

**Content:** the 82 frozen permanently · ⚠ **the trigger as measured — `IGF2R`, `TLR3`, `TMEM30A`
would gain spans** · `n_ranking_set` is **definition-dependent** · every artifact naming a span
states which definition produced it · **options rejected**: re-running the 82 *(destroys D-075's
pre-registration)*, amending F-004 *(D-074 — corrections recorded openly, never patched into a
sealed result)*.

**Then the `### F-017` disclosure**, ⚠ **as a disclosure and NOT a correction — cite F-025, do not
restate it, and do not touch the triple, the percentiles, the correlations or the fired row.**

---

# TASK 3 — Implement the span rulings. Census only.

⚠ **Pre-register your expected post-state before you change a line, as a COMPOSITION never a total** —
rows gaining a span by mechanism, band split before and after, and **which tables stay untouched.**
The Planner's is deliberately absent.

## 3a — Vocabulary

**Accept:** `Extracellular` · `Lumenal` · `Lumenal, vesicle` · `Vesicular` · `Intragranular` ·
`Exoplasmic loop` · `Perinuclear space`
**Reject:** `Mitochondrial intermembrane` · `Mitochondrial matrix` · `Nuclear` ·
`Peroxisomal matrix` · `Peroxisomal` · `Cytoplasmic`
**Held, NOT accepted yet:** `Lumenal, melanosome` · `Vacuolar` — **Task 5**

⚠ **An accepted term list, not a substring match.** ⚠ **Every term the data contains must resolve to
accept / reject / held.** **An unrecognised term is `term_unruled`, named and reported — never
silently dropped and never silently accepted.** *That is the defect this whole arc came from.*

## 3b — GPI: rule A with B fallback

**A:** `Chain` start → (`Lipidation` position − 1). **B, when `Lipidation` is absent:** `Chain`
start → `Chain` end. ⚠ **Record which rule produced every span.**

⚠ **Missing a required feature is `absent_with_reason`, named — never silently dropped from a
denominator.**

⚠ **Report where A and B diverge by more than one residue.** They should differ by ~1; **a larger
divergence is a `Chain` annotation that does not mean what was assumed, and it is a finding.**

## 3c — `span_boundary_unknown`

New category for the SDK1 shape. ⚠ **Out of the bands, named, recording the coordinate it does
have. No coordinate is invented — not 1, not `Signal`+1.**

## 3d — Rename

`no_topology` → **`no_extracellular_span`** or better. ⚠ **It reported five different things.**
**Rename in code, output, and the UI together** — a renamed band and a stale label is two names for
one thing.

## 3e — Tests. A-017, three clauses, each separately.

- ⚠ **(c) — the fixtures that discriminate, and this task is not done without them:** a protein
  whose only face is `Lumenal` *(gains a span; under the old filter, none)* · one whose only face is
  `Mitochondrial matrix` *(gains nothing — **the rejection must bite**)* · **a GPI protein with
  `Lipidation`** *(rule A)* · **a GPI protein without it** *(rule B)* · **an SDK1-shaped null
  coordinate** *(`span_boundary_unknown`, not a span and not `no_extracellular_span`)* ·
  **an unrecognised term** *(`term_unruled`)*.
- **(a)** every fixture reaches the code — assert non-zero rows processed.
- **(b)** one property, one test.
- **Prove by revert; report the file and line each red fires at.** ⚠ **An error-red and a
  failure-red are different objects.**

## 3f — Re-extract census spans, then report

⚠ **Census only. The cohort is frozen.** Surface and annex, from the existing cache, **no network.**

**Report, off the file:** band split before and after, every key including zeros · rows gained
**by mechanism** · the three denominators reconciling · ⚠ **the new foldable counts, stated as
populations under the new definition and never compared to 2,352 / 332 without naming both
definitions.**

---

# TASK 4 — The UI glossary surface

**Per R4. Every term appears — accepted, held, and rejected alike.**

⚠ **A term simply absent reads as *"nobody thought of it."* A term listed as rejected with a reason
reads as *"considered, and here is why not."*** Same distinction as an empty band key versus an
omitted one.

**Each entry carries:** the compartment · the ruling · the reason · ⚠ **and its provenance,
including that the compartment reasoning is Planner-supplied general knowledge and not sourced at
first hand.**

⚠ **Plain language beside the technical, both present.** *"The inside of a lysosome is,
topologically, the outside of the cell"* does work that *"lumenal domains are topologically
equivalent to extracellular domains"* does not.

**Tooltips wherever a band, category or count is displayed:** `no_extracellular_span` ·
`span_boundary_unknown` · `absent_with_reason` · `fetch_ineligible:<reason>` · `term_unruled` · the
GPI badge.

## ⚠ 4a — The GPI badge. Read this twice.

**The badge shows the attribute AND the limitation together, and must never read as a score, a rank,
or a positive signal.**

**Tooltip text, to be adapted but not weakened:**

> **GPI-anchored.** This protein is attached to the outside of the cell by a lipid anchor rather
> than by crossing the membrane, so its whole mature chain is extracellular. ⚠ **It has no
> cytoplasmic tail — which means it lacks the internal signals that normally pull a bound antibody
> into the cell and on to the lysosome, where an ADC's payload is released. GPI-anchored targets
> tend to recycle back to the surface instead.** Approved ADCs against this class exist (folate
> receptor alpha), but the field engineers around the problem. **This ranking measures extracellular
> shape and is blind to internalisation, so a high score here does not predict payload delivery.**

**And a standing limitation line wherever a rank or score is displayed:**

> ⚠ **Ranks on extracellular geometry. Blind to internalisation, expression level, and antigen copy
> number.**

**No deploy to Fly that has not passed the gate.** ⚠ **Walk the deployed surface after the merge** —
systematic surface walks have caught what automated tests missed.

---

# TASK 5 — The two held terms, and one run to ground. Read-only.

**5a — `Lumenal, melanosome` (3 domains) and `Vacuolar` (2), both surface class.** ⚠ **The check is
orthogonal to what is being ruled: do the proteins carrying these terms appear in an experimental
cell-surface dataset?** Topology vocabulary is a curator's word choice; surface proteomics is a
measurement. **Report the accessions, genes, and whether each is experimentally surface-detected.**
⚠ **Report also that they sit in SURFY's positive class — supporting but weaker, since A-014 holds
that a model's positive class is a prediction, not a fact.**

**5b — `Mother cell cytoplasmic`, n=1.** ⚠ **Yeast sporulation vocabulary in a human dataset.**
Report the accession, gene, full feature block, and the entry's review status. **Ruled after, not
dropped silently.** *(Changes no count — `Cytoplasmic` is rejected regardless. A data-quality
question.)*

**Report and stop. The owner rules.**

---

## REPORT BACK

Plain lines, `label | value`. **No box-drawing tables** — eleven consecutive reports have lost their
middle columns.

**T0** term table · the three population definitions · **T1** `F-025` hash, checker output, set size ·
**T2** the `D-` integer confirmed live, both hashes · **T3** your pre-registration first, then the
before/after split, gains by mechanism, A-vs-B divergences, every revert's file and line ·
**T4** the deployed surface walked, not just the tests green · **T5** both checks, no recommendation

---

## THEN — and this is what the day is for

**Once Tasks 0–3 land, Task 4 of the census order is unblocked:** the manifest, ⚠ **seed recorded
before the first shuffle**, carrying the attention-tilt limitation and the new span definition by
name. **Then 4a's determinism control — mandatory, first, both arms — then tranche 1, then the
crank.**

⚠ **Scoring census rows remains barred.** Folding is not scoring, and the gate is on scoring.

## STILL OPEN

⚠ Three findings unnumbered · the vocabulary check (T5) · **KEEL v6 into the repository** and the
A- reconciliation · Task 3's PR · the unclassified diagnostic *(never delivered, hypothesis dead,
not reissued)*.

— END OF SPAN IMPLEMENTATION (6 of 6) —
