# RULINGS — 2026-08-07 — The span definition: vocabulary, GPI, coordinates, and the glossary surface

> **OWNER RULINGS, made 2026-08-07 and binding.** They constrain future extraction; they change
> nothing already measured. Where this file and the log differ, **THE LOG GOVERNS.** ⚠ This file is
> provenance for decisions that live in the log; **it is not itself authority.** Cited by the log,
> not restated in it.
>
> ⚠ **Ruled BEFORE any count of what each rule yields.** Task 0's term table and Task 3's GPI
> measurement had not reached the Planner when these were made. **A term list chosen after seeing
> which terms produce the most candidates is a dial, not a rule.** The counts become verification;
> a surprise is a finding, not a temptation.

> **Planner provenance (D-016).** The compartment reasoning in R1 is Planner-supplied from general
> knowledge and is **not sourced at first hand**; it is ruled on that basis and the glossary must
> say so. The GPI trafficking literature in R2 was retrieved by web search 2026-08-07 and is cited.
> Every count is **Code's reading**.

---

## R1 — The vocabulary. Per-term, biological, not lexical.

**The test is one question: *can this face ever reach the outside of the cell?*** ⚠ Not *"is it
usually there"* and not *"how many proteins does it add."* **Acceptance places a protein in the
foldable population, not on a shortlist** — the ranking still happens downstream.

### ACCEPTED — secretory pathway, reaches the plasma membrane

| Term | Why |
|---|---|
| `Extracellular` | Unchanged. The original definition |
| `Lumenal` | ER / Golgi / endosome / lysosome. **The core case.** Vesicle fusion puts this face outside |
| `Lumenal, vesicle` | Secretory-vesicle lumen. **Fuses with the plasma membrane by definition** |
| `Vesicular` | Same, generic |
| `Intragranular` | Secretory-granule lumen. **Exocytosis exposes it** |
| `Exoplasmic loop` | ⚠ *Exoplasmic* **means** the non-cytoplasmic face. A third word for the same thing |
| `Perinuclear space` | ⚠ The space between the inner and outer nuclear membranes is **continuous with the ER lumen.** Same compartment, different name |

### ⚠ HELD PENDING A CHECK — ruled after the check, not before

| Term | Domains | Why held |
|---|---|---|
| `Lumenal, melanosome` | 3, surface class | Melanosomes are **lysosome-related organelles** and their membrane proteins do reach the surface (TYRP1, PMEL). ⚠ **A specialised lineage, and the Planner is reasoning from general knowledge** |
| `Vacuolar` | 2, surface class | Usually lysosome-like or autophagic in human annotation, ⚠ **and lysosomal exocytosis is real** — but weaker than `Lumenal` |

**The check, and it is orthogonal to what is being ruled:** ⚠ **do the proteins carrying these terms
appear in an experimental cell-surface dataset?** Topology vocabulary is a curator's word choice;
surface proteomics is a measurement. **Supporting but weaker evidence: both terms occur on proteins
already in SURFY's positive class** — ⚠ **weak because A-014 holds that a model's positive class is
a prediction, not a fact.**

### REJECTED — cannot reach the plasma membrane on any mechanism

`Mitochondrial intermembrane` · `Mitochondrial matrix` · `Nuclear` · `Peroxisomal matrix` ·
`Peroxisomal` · `Cytoplasmic`

**Mitochondria, peroxisomes and nuclei do not fuse with the plasma membrane.** ⚠ **These are roughly
418 annex domains that a careless widening to *"anything not cytoplasmic"* would have recruited —
proteins that cannot be ADC targets on any mechanism, in the direction that makes the atlas look
bigger.** That is the failure mode this ruling exists to prevent.

### ⚠ RUN TO GROUND, THEN RULED — not dropped silently

`Mother cell cytoplasmic`, **n=1**. **Yeast sporulation vocabulary in a human dataset.** Candidates:
an upstream annotation error · an ortholog-transfer artifact · a legitimate term the Planner does
not recognise. **Report the accession, gene, full feature block and entry review status.** *(It
changes no count either way — `Cytoplasmic` is rejected regardless. This is a data-quality
question.)*

---

## R2 — GPI-anchored proteins: a different extraction rule, and NOT a scoring feature

### R2.1 — The extraction rule: **A, with B as fallback**

| | Rule | Span |
|---|---|---|
| **A** | primary | `Chain` start → (`Lipidation` position − 1) |
| **B** | fallback, when `Lipidation` is absent | `Chain` start → `Chain` end |

**Where all features are present the two differ by about one residue**, which is immaterial in a
several-hundred-residue ectodomain. ⚠ **The ruling is therefore not about the span — it is about
what happens when an annotation is missing.** A is explicit about both boundaries rather than
trusting `Chain` to have been drawn correctly; B recovers proteins A would otherwise drop.

⚠ **Binding, and it matters more than the letter: a protein missing its required feature is
`absent_with_reason`, named — never silently dropped from a denominator.** An absent value is a
**CATEGORY**.

⚠ **And the measurement is a check on the rule, not an input to it:** if A and B diverge by much
more than a residue anywhere, **that is a `Chain` annotation that does not mean what was assumed**,
and it is a finding.

### ⚠ R2.2 — GPI is a DISCLOSED ATTRIBUTE and a STATED LIMITATION. Never a score component.

**The owner's initial reading was that GPI status is a weighty predictor of ADC efficacy. The
Planner checked it. *Weighty* holds; the direction does not.** The literature treats GPI-anchoring
as a **delivery liability**:

- **A GPI-anchored protein lacks a cytosolic tail and therefore encodes no canonical internalisation
  motif; uptake is slow and highly context-dependent.** *(Zeng et al., CEACAM6 ADC study, 2026 — the
  paper calls this class **turnover-limited targets** and builds a delivery-aware framework
  specifically for it.)*
- **GPI-anchored proteins often recycle back to the plasma membrane after endocytosis, with only a
  minor fraction reaching lysosomal degradation.** *(de Goeij et al., Mol Cancer Ther 2016.)*
- ⚠ **The lysosome is where the payload comes off.**

**Not disqualifying — folate receptor alpha is GPI-anchored and mirvetuximab soravtansine is
approved.** ⚠ **But the field engineers around this class** — bispecific ADCs co-targeting CD63,
biparatopic constructs, receptor-ubiquitination strategies. **That machinery exists because the
class is hard.**

**⚠ THREE REASONS GPI DOES NOT ENTER SCORING, and the third is decisive:**

1. **n=12.** Feature 7 required a full pre-registered ablation — D-075, six frozen Decision-4 rows,
   Run A. ⚠ **Adding feature 8 by ruling is the fishing that apparatus exists to prevent.**
2. **The six features measure ECD geometry. None measures internalisation.** GPI status is not a
   geometric property.
3. ⚠⚠ **CIRCULARITY, AND IT IS FATAL. There is no GPI-anchored protein in the ranking set to learn
   from — the extractor excluded all of them.** A coefficient cannot be fitted on an excluded class.
   **Any apparent association would be an artifact of the exclusion.**

**The limitation, to be carried in the UI, the deck and the paper:**

> ⚠ **This method ranks on extracellular geometry and is blind to internalisation. GPI-anchored
> targets recycle rather than trafficking to the lysosome, so a high score on this axis does not
> predict payload delivery — and GPI status is not among the features.**

⚠ **That sentence discloses a real limit, explains why recovered GPI proteins are candidates rather
than answers, and pre-empts the first question a reviewer or a partner will ask.** *"Your model does
not know about internalisation"* is far weaker coming from them than from the paper.

---

## R3 — The coordinate case: its own category

`Q7Z5N4` SDK1. UniProt annotated a 2,009 aa domain as `Extracellular`; the filter matched;
`parse()` returned `None` on `{"start": {"value": null, "modifier": "UNKNOWN"}}` and the row reported
`no_topology`. ⚠ **The artifact reads `None-2009(None)` — a null stringified into something that
still looks like a span.**

**RULED: a new category, `span_boundary_unknown`.** ⚠ **It is neither *no topology* nor a usable
span.** It stays out of the bands, is **named**, and **records the coordinate it does have.**
⚠ **No coordinate is invented** — not 1, not `Signal`+1. **An absent value is a category, never a
low number and never a bare null.** n=1 census-wide, so exactness is free.

---

## R4 — The glossary surface. Every piece states why it fits where it fits.

⚠ **This is D-016 applied to the UI**, and it converts sixteen invisible string comparisons into
**sixteen stated, defensible, auditable decisions.**

**Binding requirements:**

1. **Every term appears — accepted, held, and rejected alike.** ⚠ **A term simply absent reads as
   *"nobody thought of it."* A term listed as rejected with a reason reads as *"considered, and here
   is why not."*** Same distinction as an empty band key versus an omitted one.
2. **Each carries: the compartment · the ruling · the reason · and its provenance** — ⚠ **including
   that the compartment reasoning is Planner-supplied general knowledge, not sourced at first hand.**
3. ⚠ **Plain language beside the technical, per owner instruction.** *"The inside of a lysosome is,
   topologically, the outside of the cell"* does work that *"lumenal domains are topologically
   equivalent to extracellular domains"* does not. **Both appear.**
4. **Tooltips wherever a band, a category or a count is displayed** — `no_extracellular_span`,
   `span_boundary_unknown`, `absent_with_reason`, `fetch_ineligible:<reason>`, and the GPI badge.
5. ⚠ **The GPI badge shows the attribute AND the limitation together.** **It must never read as a
   score, a rank, or a positive signal.**
6. **`no_topology` is renamed to what it measures.** ⚠ It reported five different things, none of
   them *"this protein has no reachable domain."*

---

## R5 — Standing, from earlier today and unchanged

- **`F-025` ratified.** ⚠ A Planner **chat message cannot ratify what a committed document
  reserved** — the owner's ruling is what makes `ba1e687` correct.
- **The 82 are frozen** under the original span definition, permanently. `### F-004` and
  `### F-017` are correct as measured and **are never re-run under a later definition.**
  ⚠ **Every artifact naming a span states which definition produced it. Two definitions, both named,
  never compared without naming which.**
