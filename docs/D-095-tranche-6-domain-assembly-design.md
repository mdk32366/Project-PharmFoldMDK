# D-095 — Tranche 6: the domain-assembly design document

- **Date:** 2026-08-17
- **Status:** ⚠ **PROPOSED — written, not ruled.** D-091 ruling 3 requires this document to be
  *written and ruled* before anything folds. This is the written half. **No GPU, no rental, no
  ingest has occurred and none may occur on the strength of this file alone.**
- **Authorised by:** D-091 ruling 3 (owner, 2026-08-17)
- **Companion finding:** **F-041** — two of the three candidate boundary sources cannot supply a
  boundary from the instrument this project owns.
- **Evidence:** `scripts/tranche6_domain_survey.py` (read-only, cache-only, exit 0). Every number
  below is reproducible from it. Cache-file sha256s are in its part 6.

> ⚠ **A note on the date.** The prework that commissioned this is `PREWORK-2026-08-18.md`, but the
> wall clock at the time of writing is **2026-08-17 11:22 -0700**, 32 minutes after commit
> `faf9e32`. The filename's date is aspirational; **this entry is stamped with the real one.**

---

## §0 — What the commissioning question assumed, and what is actually true

D-091 ruling 3 and `PREWORK-2026-08-18.md` §3 both frame item 1 as a **choice among three sources**:

> *The domain-boundary source — UniProt `Domain` vs Pfam vs InterPro. ⚠⚠ They will not agree, and
> picking one after seeing results is how a boundary gets chosen for the answer it gives.*

The prework named the cheapest way to test this: *count the domains under each source and check
whether they agree.* That was the right first move, and it returned an answer the framing did not
anticipate.

**They do not agree. But that is not the finding.** The finding is that **the comparison as posed
cannot be run**, because two of the three named sources do not carry the object being compared.

| source | families | instance count | ⚠ **boundaries** |
|---|---|---|---|
| **UniProt `Domain` + `Repeat`** | — | yes, as features | ✅ **yes — `start`/`end`, EXACT** |
| **Pfam** | yes | yes (`MatchStatus`) | ❌ **none** |
| **InterPro** | yes | ❌ **none — 0 of 22,176 xrefs cache-wide** | ❌ **none** |

⚠ **This is a category difference, not a disagreement in number**, and the project has a name for
that mistake: *a claim about the wrong population* (**F-038**). Comparing "UniProt 39" against
"InterPro 9" for FAT1 would have compared **39 domain instances** against **9 family memberships**
— two different objects, and the comparison would have looked meaningful.

**Full statement of the absence, with its cause (the "every absence is a CATEGORY" rule):**

- **InterPro's UniProtKB cross-reference is entry-level by construction.** It records *which
  InterPro families this protein belongs to*, never how many times or where. The count and the
  coordinates exist upstream — in the InterPro **matches** API and in InterProScan output — which
  are **a different instrument this project does not have and has never fetched.**
- **The member databases (Pfam, SMART, PROSITE, CDD, Gene3D, SUPFAM, PANTHER, FunFam) do declare a
  count** — `MatchStatus` — on **every** xref. **None declares a position.**
- ⚠ **No database in the cache carries coordinates at all.** Verified cache-wide across all 4,990
  entries and 22,176 InterPro xrefs, with zero counterexamples. The check was written so that a
  single hit would have disqualified the claim; there were none.

**Consequence for item 1: the choice is made on availability, and must say so.** Naming UniProt
does **not** arbitrate the disagreement — it declines to. That refusal has to be legible in the
artifact, or a later reader will take `boundary_method` as a considered verdict on which annotation
is *correct*, which it is not.

---

## §1 — The counts, and how badly they disagree

Instances per protein, by source (`tranche6_domain_survey.py` part 2):

| gene | UniProt | (Domain | Repeat) | Pfam | SMART | PROSITE | InterPro |
|---|---|---|---|---|---|---|---|
| FAT1 | **39** | 39 | 0 | 32 | 44 | **63** | n/a |
| FAT2 | **35** | 35 | 0 | 32 | 38 | 52 | n/a |
| FAT3 | **38** | 38 | 0 | 29 | 40 | 62 | n/a |
| FAT4 | **42** | 42 | 0 | 40 | 47 | **79** | n/a |
| LRP1 | **87** | 53 | 34 | 50 | 99 | **116** | n/a |
| LRP1B | **88** | 54 | 34 | 51 | 100 | **126** | n/a |
| LRP2 | **77** | 42 | 35 | 55 | 110 | **125** | n/a |
| USH2A | **47** | 47 | 0 | 32 | 47 | 62 | n/a |
| ADGRV1 | **42** | 36 | 6 | 36 | **19** | **8** | n/a |
| PKHD1L1 | **26** | 17 | 9 | 19 | 27 | **3** | n/a |

⚠ **Not one of the ten agrees**, and **the disagreement does not even point the same way.** PROSITE
finds 63 where UniProt finds 39 in FAT1 — and **8 where UniProt finds 42** in ADGRV1. A rule of
thumb like *"PROSITE is more granular"* would be true for seven subjects and backwards for two. It
is not a systematic offset that could be reconciled; **the sources are annotating different things.**

⚠ **`Repeat` is not optional.** UniProt splits a tandem array across two feature types. Counting
only `Domain` would drop **34** LDL-receptor class B repeats from LRP1, **34** from LRP1B, **35**
from LRP2, and **9** from PKHD1L1 — silently, since the surviving count still looks plausible. This
is a **within-source** ambiguity that exists before any cross-source question, and it is settled in
decision 1(b) below.

---

## §2 — ⚠ The result that changes the design: a domain is small, a RUN is not

This is the load-bearing measurement, and it reverses the intuition behind *"fold the domains
separately."*

| gene | span_aa | domains | smallest | median | largest | runs | **largest run** | runs > 1,026 |
|---|---|---|---|---|---|---|---|---|
| FAT1 | 4,160 | 39 | 37 | 105 | 181 | 9 | **2,289** | **1** |
| FAT2 | 4,030 | 35 | 37 | 105 | 172 | 8 | **1,674** | **1** |
| FAT3 | 4,122 | 38 | 37 | 105 | 203 | 9 | **2,291** | **1** |
| FAT4 | 4,466 | 42 | 37 | 104 | 185 | 10 | **3,037** | **1** |
| LRP1 | 4,400 | 87 | 36 | 41 | 51 | 30 | 360 | 0 |
| LRP1B | 4,420 | 88 | 36 | 41 | 58 | 51 | 223 | 0 |
| LRP2 | 4,398 | 77 | 35 | 41 | 50 | 50 | 224 | 0 |
| USH2A | 5,011 | 47 | 48 | 92 | 247 | 21 | 782 | 0 |
| ADGRV1 | 5,879 | 42 | 42 | 101 | 157 | 40 | 157 | 0 |
| PKHD1L1 | 4,190 | 26 | 22 | 82 | 156 | 25 | 223 | 0 |

**Every single domain instance in all ten is inside the trained context** — the largest anywhere is
**247 aa** (USH2A). If domains could be folded one at a time with nothing else to decide, tranche 6
would be trivial.

⚠ **They cannot, because the domains abut.** FAT1's cadherin repeats share boundaries exactly:

```
Domain    35- 149  ( 115 aa)  Cadherin 1
Domain   150- 257  ( 108 aa)  Cadherin 2      <- starts the residue after Cadherin 1 ends
...
Domain   823- 927  ( 105 aa)  Cadherin 7
Domain   928-1034  ( 107 aa)  Cadherin 8      <- and so on, for 20+ repeats
```

So FAT1's 39 domains collapse into **9 contiguous runs**, one of which is **2,289 aa**. FAT4's is
**3,037 aa**. ⚠ **There is no linker inside that run to cut at.** The choice is not *"where are the
natural seams"* — it is **where to sever a continuous domain stack**, which is a different and much
less comfortable decision.

⚠⚠ **And it is not a neutral one for this particular fold.** Cadherin repeats are rigidified by
Ca²⁺ ions bound **at the interface between consecutive repeats**. A cut between repeat *n* and
*n+1* removes exactly the interface that makes the stack rigid. **The tile will fold; the property
that made the arrangement meaningful is what the cut destroys.** This is *predicted*, not
*measured* — labelled as such per the log's method note item 3, and it is the single most important
thing for the owner to rule on.

**The two regimes are genuinely different and one rule cannot cover both:**

- **FAT1–4** — one oversized run each; **cuts must fall inside a domain stack.**
- **LRP1/1B/2, USH2A, ADGRV1, PKHD1L1** — no run exceeds context; **natural seams already exist.**

---

## §3 — ⚠ What is NOT in a domain, and the F-037 trap waiting here

| gene | span_aa | in a domain | **unannotated** | **unannot %** | longest gap | lead | tail |
|---|---|---|---|---|---|---|---|
| FAT1 | 4,160 | 3,826 | 334 | 8.0% | 142 | 13 | 18 |
| FAT2 | 4,030 | 3,605 | 425 | 10.5% | 130 | 15 | 26 |
| FAT3 | 4,122 | 3,896 | 226 | 5.5% | 141 | 11 | 20 |
| FAT4 | 4,466 | 4,184 | 282 | 6.3% | 181 | 4 | 41 |
| LRP1 | 4,400 | 3,626 | 774 | 17.6% | 102 | 5 | 10 |
| LRP1B | 4,420 | 3,619 | 801 | 18.1% | 100 | 6 | 17 |
| LRP2 | 4,398 | 3,158 | 1,240 | 28.2% | 141 | 1 | 12 |
| USH2A | 5,011 | 4,366 | 645 | 12.9% | 193 | **239** | 115 |
| ADGRV1 | 5,879 | 3,934 | 1,945 | **33.1%** | 278 | 0 | 5 |
| PKHD1L1 | 4,190 | 1,871 | **2,319** | **55.3%** | **574** | 10 | **662** |

⚠⚠ **A design that folds "the domains" folds 44.7% of PKHD1L1 and discards the rest without
saying so.** That is **F-037 exactly, one level down**: F-037 was *`span_aa` is the largest
extracellular segment, not the extracellular content*, and 92,709 residues were discarded. Here the
same shape reappears as *the tiles are the annotated domains, not the span*, and **2,319 residues of
one protein** go with it.

⚠ **"Unannotated" is not "disordered" and not "unimportant."** It is *an absence in the annotation*,
whose causes include genuine disorder, genuine linkers, and **simply not having been annotated
yet** — and nothing in the cache distinguishes them. Treating the absence as a licence to drop the
residues would convert a limitation of the annotation into a claim about the protein.

---

## §4 — The six decisions D-091 requires

### Decision 1 — the domain-boundary source

**(a) UniProt `Domain` + `Repeat` features are the boundary source for tranche 6**, fixed **now**,
before any fold, and the reason is recorded here so it cannot be reverse-engineered later: **it is
the only candidate that supplies coordinates from the instrument this project already owns and has
already provenance-tracked.**

⚠ **This is a choice by availability, and the artifact must say that** — not imply a verdict that
UniProt's annotation is the correct one. The counts disagree; this decision does not resolve the
disagreement, it declines to arbitrate it on the evidence available.

**(b) Both feature types count.** `Domain` alone drops 34/34/35/9 repeats from LRP1/LRP1B/LRP2/
PKHD1L1. The union is the unit.

**(c) ⚠⚠ The boundary source is itself a MODEL OUTPUT, and tranche 6 is a pipeline of models.**
Added 2026-08-17 at Planner's P3, which is correct and which the first draft of this document
missed — it named UniProt without saying what UniProt's domain features *are*.

**Of the 521 domain-like features across the ten subjects, not one carries experimental evidence:**

| evidence | features | what it means |
|---|---|---|
| `ECO:0000255` | **416 (79.8%)** | ⚠ **automatic assertion from a SEQUENCE MODEL** — an HMM/profile hit. 395 cite **PROSITE-ProRule**. |
| `ECO:0000305` | 14 | curator inference |
| **`ECO:0000269`** | **0** | ⚠⚠ **experimental — NONE, in any of the ten** |
| *(no evidence entry)* | ≥91 | ⚠ an absence, not a category — the annotation asserts a boundary and cites nothing |

FAT1–4, LRP2 and USH2A are **100% sequence-model** boundaries. PKHD1L1 is the outlier in the other
direction — only 12% carry an automatic code, and most of its 26 features cite nothing at all.

⚠ **So the design is an HMM deciding where a neural network is allowed to cut.** That is a
defensible pipeline, and it is *not* what a reader assumes when a column says `boundary_method`. The
consequences must be stated rather than discovered:

- **A tile boundary is a prediction with an error bar nobody has measured**, not a landmark. The
  cadherin-interface argument in §2 rests on boundaries that are themselves profile hits.
- ⚠ **The disagreement in §1 is therefore a disagreement BETWEEN MODELS** — PROSITE's profiles
  against Pfam's HMMs against UniProt's ProRule — not between an annotation and a ground truth.
  **There is no arbiter available**, which is why decision 1(a) chooses on availability and says so.
- **`boundary_method = domain_tiled_v1` must resolve to this evidence statement**, not merely to
  "UniProt". A reader who cannot tell that the boundaries are predicted will read the tiles as
  anatomy.

**(d) Adopting Pfam or InterPro boundaries later is a NEW instrument, not a parameter change.** It
requires a network fetch that has never been made, its own cache, its own provenance and its own
freshness rule (D-088). ⚠ **It must not be attempted mid-tranche**, because choosing a boundary
source after seeing which one folds better is precisely the failure D-091 ruling 3 named.

### Decision 2 — per-domain span rules and linkers: **the fold unit is a TILE, not a domain**

⚠ **Every residue of the span belongs to exactly one tile.** Nothing is dropped, ever. This is the
census accounting discipline — *5,016 rows, every one in exactly one bucket* — applied one level
down, and it is the direct answer to §3's trap.

Proposed tiling rule, in order:

1. A tile may not exceed a stated residue budget, **`tile_max_aa`, proposed 1,000** — inside the
   1,026 trained context with headroom, and **stated as a parameter so it is falsifiable**, not
   buried in code.
2. **Prefer to cut at the longest available gap** between domain runs within the budget window.
3. **If no gap exists inside the window — the FAT1–4 case — cut at a domain boundary**, never
   mid-domain, choosing the boundary nearest the budget limit.
4. **Linkers and unannotated regions are RETAINED inside whichever tile contains them.** They are
   not folded separately and never omitted.
5. **A leading or trailing unannotated stretch stays in the first/last tile** unless it exceeds the
   budget alone — PKHD1L1's 662 aa tail and USH2A's 239 aa lead are the cases that force this rule
   to be written rather than discovered.
6. Every tile records `tile_index`, `tile_of`, `tile_start`, `tile_end`, and **`tile_cut_kind` ∈
   {`gap`, `domain_boundary`, `span_end`}** — ⚠ so that a tile cut through a cadherin stack is
   **distinguishable from one cut at a natural seam by reading the artifact alone.**

### Decision 3 — an assembled model is **a SET of structures, not a structure**

⚠⚠ **Tranche 6 emits N artifacts per protein and no concatenated PDB.**

The reasoning is the strongest form of the F-037 lesson: **ESMFold predicts no inter-tile geometry.
A single PDB file placing all tiles in one coordinate frame would state relative orientations that
were never predicted** — and it would state them in a format whose entire convention is that
coordinates are meaningful. ⚠ **The file itself would be the false claim**, independently of any
caption, disclosure or column beside it.

A single-file view may exist **only** as a separate, explicitly-labelled derived artifact whose name
carries the word for what it is (a *layout*, not a *structure*), and never as the primary.

### Decision 4 — `boundary_method` says so

The column already exists and is currently **monovalued: `sliced_ecd` on all 3,467 manifest rows.**
⚠ **So this is purely additive, and no existing row is retrofitted** — which matters, because
retrofitting is forbidden (D-091 ruling 1) and would not be needed here anyway: **every existing row
already declares itself.**

- New `boundary_method`: **`domain_tiled_v1`**
- New `span_definition`: its own value, per the D-081/D-091 precedent that **a definition string
  travels with every artifact that cites it** where a boolean flag does not.

⚠ **A tile row and a single-pass row must never be compared without the method in the query.** Per
D-088's *refuse rather than serve* precedent, a surface that would mix them should **refuse**, not
silently average.

### Decision 5 — pLDDT for an assembly: **there is no mean**

⚠ **A mean over concatenated tiles is a mean over an object that was never predicted as one.**

- **Per-tile pLDDT is reported, always.** It is the only figure that corresponds to something the
  model actually produced.
- If a single number is demanded, it is a **named statistic carrying its denominator** —
  `plddt_tilewise_mean`, **never `plddt`.** F-038 is the precedent: a true number about the wrong
  population is still wrong.
- ⚠ **It is not comparable to a single-pass `plddt`, and the bias has a known direction.** Residues
  at a tile edge lose context on one side, so tile-edge pLDDT is depressed relative to the same
  residue folded in a longer pass. **State the bias; do not correct for it** — a correction would be
  a model of the bias, and this project does not have one.

### Decision 6 — interaction with F-040

⚠ **The caveats compound, and several of these subjects carry both.** From the cached `SUBUNIT`
comments:

- **ADGRV1** — *"Forms a heterodimer, consisting of a large extracellular region (alpha subunit)
  non-covalently linked to a seven-transmembrane moiety (beta subunit)"*, and a **component of the
  USH2 complex** with PDZD7, USH2A and WHRN.
- **USH2A** — component of the same USH2 complex; interacts with collagen IV and fibronectin.
- **LRP1** — *"Heterodimer of an 85-kDa membrane-bound carboxyl subunit and a non-covalently
  attached 515-kDa N-terminal subunit."*
- **FAT2** — *"Homodimer."*
- **FAT4, LRP2** — documented complexes. **FAT3, LRP1B, PKHD1L1** — no `SUBUNIT` comment (⚠ an
  absence in the annotation, **not** evidence of monomeric behaviour).

So a tranche-6 artifact for ADGRV1 is **a tile, of a monomer, of a subunit, of a complex** — three
compounding reasons it is not what a reader assumes, none visible from the structure alone.

⚠ **D-094 makes disclosure a mount precondition**, so a tranche-6 structure may not render at all
until **both** the F-040 monomer caveat and the tiling caveat are present. **This is the first
surface that will be built under D-094 rather than retrofitted to it** — every existing census
surface predates it (`PREWORK-2026-08-18.md` §2).

---

## §5 — What this document does NOT settle, and what it hands back

⚠ **Held for the owner. Nothing below is decided here.**

1. ⚠⚠ **The FAT1–4 cut is the real question.** Decision 2 rule 3 says *cut at a domain boundary
   inside the stack*, which severs a Ca²⁺-stabilised interface. **The alternative is to declare
   FAT1–4 out of scope for tranche 6** on the grounds that the assembly is not defensible for a
   continuous cadherin array. That is a scope ruling, not a technical one, and it is the owner's.
2. **`tile_max_aa = 1,000`** is proposed, not measured. ⚠ **No tile has ever been folded**, and this
   project's own history (F-034, the ceiling work) says the number should come from a measurement.
3. **Whether tranche 6's method bears on tranche 5's 141 rows past the trained context.** ⚠ If
   tiling is sound, *"past the trained context"* stops being a hardware statement for some of those
   rows. **This is deliberately not pursued** — D-091 ruling 2 held tranche 5 entirely, and quietly
   widening scope on the strength of a proposal is exactly what that ruling forbids. **Flagged for
   the owner, not acted on.**
4. **Where tiles are stored, and whether `protein_analyses` gains rows or a child table.** A schema
   question; deferred until the ruling, since a rejected design needs no schema.

## §6 — What was done, and what was not

**Done:** the §3 cheap move, cache-only — 10 subjects, 4,990-entry cache-wide verification, exit 0,
reproducible via `scripts/tranche6_domain_survey.py`, sha256 recorded per file.

**⚠ Not done, deliberately:** no GPU, no rental, no ingest, no network fetch, no database write, no
schema change, no `pytest` run. **`fly` was not invoked.** The proxy was not started.

⚠ **One error was made and is recorded rather than patched away.** The first pass of this analysis
merged *contiguous* domain intervals and reported the largest merged **run** under the heading
*largest single domain* — giving FAT4 a "3,037 aa domain" that does not exist. The corrected
figure is **185 aa**. The mistake is preserved in `scripts/tranche6_domain_survey.py`'s `merge()`
docstring, because **the run/domain distinction it obscured is the single most important structural
fact in this document**, and the near-miss is evidence about how easily it hides.
