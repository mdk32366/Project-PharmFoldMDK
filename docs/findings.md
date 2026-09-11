# PharmFoldMDK — Findings (`findings.md`)

> **The question this document answers (KEEL-4 §2): "How do we know?"**
>
> **This file is the authoritative home of the `F-NNN` entries** — moved out of
> [`README.md`](README.md) by **`D-156`** on 2026-09-11. ⚠ **No entry was edited,
> renumbered, or reworded by the move; it was byte-preserving and asserted as such.**
>
> - **The rules that govern writing here** live in [`README.md`](README.md) — the log
>   leads the code, every claim names how it is known (`D-016`), and the entry template.
> - **The next free `F-` integer** lives in [`RESERVED.md`](RESERVED.md), which is
>   the sole allocator. ⚠ **The pointer moves in the SAME commit that spends the integer.**
> - **Newest first.** Add a new entry at the **top**.

---

## Log (newest first)

### F-070 — ⚠⚠ The census structure panel is EMPTY, SILENTLY, for very short spans — the endpoint serves a valid PDB in every case, so the shipped description of this defect (*"3Dmol dynamic import failing on census pages"*) names a cause that is not happening, and the disjunction ordered to diagnose it had **two branches and both are false**

- **Date:** 2026-09-11 · **Status:** ⚠ **OPEN, and ⚠⚠ WRITTEN-NOT-REPAIRED by standing
  instruction — the TEXT lands here; the cartoon gap does not.** No viewer code moves under this
  entry.
- **How known (`D-016`):** walked live on `pharmfoldmdk.fly.dev` 2026-09-11 — **four accessions**,
  spans **1** (`Q9H902`), **3** (`Q8N8F6`), **8** (`O60725`), **24** (`Q96LB2`) — and the structure
  endpoint read directly for each. ⚠ **No fix, no deploy and no re-fold was involved in knowing
  this.**

**⚠ THE REPLACEMENT TEXT, LANDED AS WRITTEN. This paragraph is the open item; the old one-liner is
withdrawn.**

> Census structure panels render empty for very short spans. Walked 2026-09-11 on the live site:
> spans 1 and 3 empty, spans 8 and 24 render. **The endpoint serves a valid PDB in every case
> (1-residue = 200, 690 bytes, one CA atom)**, so this is a **representation gap in the cartoon
> style, not a load failure** — 3Dmol cannot spline a backbone from one CA — **and the panel
> gives no named reason.** 37 rows certainly affected (spans 1–3), up to 99 if 4–7 also fail.
> Boundary between 4 and 8 unmeasured. Four accessions walked; this does not establish that all
> census pages render.

---

**⚠⚠ WHY THE OLD DESCRIPTION IS NOT MERELY IMPRECISE — IT IS REFUTED BY THE SAME PAGE LOAD.**

A failed dynamic import is **page-wide**: the module either resolves for the bundle or it does not.
**Spans 8 and 24 render their cartoons on the same build, from the same chunk, on the same day.**
⚠ **Row-dependent behaviour cannot be caused by a module that failed to load**, so the walk that
found the empty panels simultaneously disproved the stated cause. The description survived because
nobody had to reconcile the two halves: the failing rows were the only ones ever opened.

**⚠ THE DEFECT PROPER IS THE SILENCE, NOT THE SPLINE.** 3Dmol declining to draw a backbone through
one α-carbon is correct behaviour. What is wrong is that the panel is **empty with no error, no
placeholder and no named reason, while the confidence bar renders directly below it** — so the page
shows a working measurement beside a blank frame and asserts nothing about the blank.

> ⚠⚠ **This is `F-018`'s shape at the pixel layer — an absent value read as an affirmative one.**
> An empty frame under a heading that says a structure is served reads as *this protein has no
> structure*, and the row it appears on is one where a structure **is** on disk and **is** being
> served. **`D-150` already ruled on this class in copy** — *a status that appears only when
> something is wrong teaches a reader that silence means fine* — and the viewer is the one surface
> the ruling did not reach.

---

**⚠⚠ THE ORDERED DIAGNOSTIC WAS A DISJUNCTION, AND NEITHER BRANCH IS TRUE.**

`ORDERS-Code-2026-09-11-Run-2-census-refold.md` §4.7, verbatim:

> *"if pages work with Run 2 files present, it was a missing asset; if they still fail, it is
> isolated to the front end and the SPA catch-all."*

| branch | what it would mean | measured |
|---|---|---|
| *missing asset* | the PDB is absent or unreachable | ❌ **200, 690 bytes, one CA atom** — served |
| *front end / SPA catch-all* | the chunk or route never resolves | ❌ **spans 8 and 24 render on the same build** |

⚠ **A third cause — the one that is happening — was outside the disjunction**: the payload is
valid, the module loads, and the **renderer cannot represent this particular molecule.**
⚠⚠ **And the disjunction was gated behind Run 2**, so a question a browser answered in minutes was
scheduled behind a fold campaign that has not run. **`AMENDMENT 1` §4.7 is RETIRED as unsound.**

**⚠ Recorded as a Planner error, and it is NOT added to the day's tally of seven.** The seven are
instances of *reasoning about this repository instead of reading it* (`F-068`). This is a different
shape — **a two-branch disjunction presented as exhaustive over causes that neither branch had
measured, with the measurement deferred to an event that had not happened.** ⚠ **Merging the two
classes into one count would blur exactly the denominator `D-016` exists to protect**, so it is
recorded here by name and left out of that number.

---

**WHAT THIS ENTRY DOES NOT CLAIM.**
- ⚠ **Not that 3Dmol is at fault.** It is the instrument; declining to spline one atom is right.
  ⚠ **Not that the fix is a cartoon** — what a one-residue panel should show is a design question
  and is not answered here.
- ⚠⚠ **Not that the boundary is known.** Spans **4–7 are UNMEASURED**; 37 is certain and 99 is a
  ceiling, and quoting 99 as the count would be `F-047`'s wrong-but-plausible.
- ⚠ **Not that the rest of the census renders.** **Four** accessions were walked. That is a
  positive control for the working case, not a survey.
- ⚠ **Not a repair, and not an authorisation for one.** The standing instruction is explicit: the
  text lands, the cartoon gap does not.

**Relied on by:** `F-069`, which holds this as **instrument 3** of four over the short-span
population — ⚠ **and says so precisely because the viewer's own defect is separate and narrower
than the population's.**

---

### F-069 — ⚠⚠ Four instruments have tripped over one population and each recorded it separately: a 1-residue "extracellular span" is not a foldable protein, and the span pipeline treats it as one

- **Date:** 2026-09-11 · **Status:** ⚠ **OPEN, and ⚠⚠ WRITTEN-NOT-REPAIRED.** It must not be
  repaired before Run B freezes — the spans are inputs to the folded set `D-075`'s anchor rests on,
  and changing them moves the anchor. **Alongside category E, for the same reason.**
- **How known (`D-016`):** four independent measurements, listed below with their own keys. ⚠ **No
  new fetch and no new fold was run for this entry** — it joins observations that already existed.

**⚠⚠ THE ENTRY IS ABOUT THE SPAN PIPELINE. Folding, the viewer and PAE are the instruments that
tripped over it, not the subject.** Each was recorded where it was found, and the population
underneath them was never named.

**1 — `F-048` (2026-08-19).** For **58** census proteins the V2 span is a short extracellular loop
**inside** a larger transmembrane domain — the annotation and the span describe different objects.
⚠ **All 58 are folded and live on the browsable census surface, the shortest a FIVE-residue span**,
and `D-094`'s mount preconditions have never been checked against that case.

**2 — the manifest itself.** Key: `data/census/census_manifest.v7.csv`, tranches 1–4, n = 2,691.

| span | rows | share |
|---|---|---|
| ≤ 30 aa | **525** | 19.5% |
| ≤ 20 aa | 293 | 10.9% |
| ≤ 5 aa | 73 | 2.7% |
| **== 1 aa** | **10** | 0.4% |

**3 — the viewer (walked live, 2026-09-11).** Key: four accessions on `pharmfoldmdk.fly.dev`.
Spans **1** (`Q9H902`) and **3** (`Q8N8F6`) render an **EMPTY panel**; spans **8** (`O60725`) and
**24** (`Q96LB2`) render. ⚠ **The endpoint serves a valid PDB in every case** — the 1-residue
payload is `200`, 690 bytes, **one CA atom** — so this is a representation gap, not a load failure:
3Dmol cannot spline a backbone from one atom. **37 rows certainly affected (spans 1–3), up to 99 if
4–7 also fail; the boundary between 4 and 8 is UNMEASURED.**

**4 — PAE at L = 1.** ⚠ **PENDING, and pre-registered rather than guessed.** PAE is a *pairwise*
matrix; at L = 1 there is no pair. **Pre-registered by the owner before the measurement:** if the
re-fold of `Q8WXF7` (1 aa) emits **no PAE**, the 1-residue rows cannot serve the campaign's stated
purpose — determinism **and** PAE — and leave it; if PAE is emitted as a degenerate **1×1** matrix,
they stay and the comparison has substrate. **The n = 20 timing sample answers it.**

---

**⚠⚠ WHAT JOINS THEM.** A fold ran, a structure was served, a profile was computed and a viewer was
mounted **for objects that are one to three amino acids long**. Each instrument behaved correctly
in isolation and none asked whether the input was a protein. **The pipeline has no notion of a span
too short to be a molecule**, so every stage downstream inherits one.

⚠ **The cost is not the ten rows.** It is that **525 rows — 19.5% of the census — sit in a band
where "folded" has been treated as meaning the same thing it means at 400 aa**, and the census
surface says `Structure served` for all of them.

**⚠ WHAT THIS ENTRY DOES NOT CLAIM.**
- ⚠⚠ **Not that a threshold is known.** Where a span stops being a molecule is **not measured
  here**, and picking one now — after seeing which rows fall outside it — is what pre-registration
  exists to prevent (`F-055`'s shape).
- ⚠ **Not that the 525 are wrong.** A 24-residue span folds and renders; the finding is that
  nothing distinguishes it from a 1-residue one.
- ⚠ **Not that the viewer is the defect** — it is instrument 3. ⚠ And its own defect is separate
  and narrower: the panel is **silently** empty, with no named reason, while the confidence bar
  renders directly below it.
- ⚠ **Not that any of these rows should be removed from the census.** That is a scope ruling and it
  is the owner's.
- ⚠ **Not a repair, and not an authorisation for one.**

**Relied on by:** ⚠ the Task 3 sample, which deliberately retains `Q8WXF7` (1 aa) and `Q9Y3E0`
(2 aa) so instrument 4 reports at n = 20 rather than at n = 2,572.

---

### F-068 — ⚠⚠ The production-writing fold path had neither safety property the measurement path has — and the disqualifying fact is that **both omissions were already written down in `ARCHITECTURE.md`, on `main`, and read as design notes rather than gaps**

- **Date:** 2026-09-11 · **Status:** ⚠ **OPEN.** It closes when the writing path no longer exhibits
  the asymmetry — `D-074`: a finding against an instrument stays open until the instrument no
  longer exhibits the problem. ⚠ **A fix exists on a branch; a branch is not a closure.**
- **How known (`D-016`):** `grep -rn "preflight\|vram_guard" worker/main.py worker/orchestrator.py
  worker/runner.py` at `main` `5085ba6` returns **nothing**; `scripts/rb_local_tile_folds.py`'s
  module docstring states its own DB refusal; `ARCHITECTURE.md:835` read in full.

**THE ASYMMETRY, IN ONE SENTENCE.** **The only fold path that can write rows has no envelope gate
and no per-fold process topology; the only path that has both cannot write.**

| | writes the DB | envelope gate | process-per-fold |
|---|---|---|---|
| `scripts/rb_local_tile_folds.py` | ❌ **refuses by start-up assert** — imports nothing from `db/` | ✅ `preflight(requirement_mib=6357)` | ✅ `D-105`, child exits per tile |
| `worker/main.py` → `fold_from_spec` | ✅ claim → upload → complete | ❌ **none** | ❌ one persistent child |

⚠ **`F-042`'s shape one layer down.** That finding named *a guard placed where the money is, not
where the data is*. This is **a guard placed where the MEASUREMENT is, not where the WRITES are.**

⚠⚠ **EVERY WORKER-PATH FOLD ON THIS HOST HAS RUN UNGATED.** Stated plainly and not softened: the
census was folded through the path with no preflight, on the card `F-063` records bugchecking its
host.

---

**⚠⚠ THE DISQUALIFYING FACT, AND IT IS NOT THAT NOBODY NOTICED.**

`ARCHITECTURE.md:835` — on `main`, in the **VRAM guard** row, today and for weeks — contains both
halves:

> *"⚠ The fold loop still does not consult the guard (`F-049`; RB, not RA)."*

> *"The child is **persistent, one per worker** — `_MODEL_CACHE` is per-process, so a child per
> fold would reload 8.4 GB every time."*

**They were visible. They were written down, in the architecture document, in the row that exists
to describe this very subsystem. Nobody read them as gaps.**

⚠ **This refutes the framing the finding was first given** — that the omissions *"were not visible
until something tried to use the writing path at scale."* They were visible to anyone who opened
the file. **What was missing was not the information; it was the reading.**

**⚠⚠ AND THE SECOND CLAUSE IS THE WORSE HALF.** It states the *reason* for the topology — weight
reload cost — and **does not connect it to `F-064`, which was OPEN at the time and says the exact
opposite**: in-process release does **not** restore free for the next preflight (7,043 → 1,649 MiB
after a successful fold, recovering only on process exit).

> **So the document holds the design rationale and the open finding that contradicts it, in the
> same file, unjoined.** That is not an undocumented gap. **It is a documented one wearing a
> parenthetical.**

---

**⚠ WHAT THIS DOES TO `F-050`, AND IT STRENGTHENS RATHER THAN WEAKENS THE CASE.**

A guard-direction sweep hunts for guards that cannot fail in the direction they claim to protect.
⚠⚠ **Here the stated limitation of a documented capability WAS the defect — so a sweep looking for
a missing guard would have walked past a sentence that names the missing guard.** `F-050` stays
RESERVED and unwritten; this is evidence for it and a warning about its method.

**⚠ Recorded as a Planner error, because the original text asserted invisibility and the evidence
was in a file the Planner held and had not read.** `AMENDMENT 6` §3.1's *"neither omission was
visible"* is **withdrawn on evidence**. ⚠ **Seventh instance today of reasoning about this
repository instead of reading it** — and the standing refusal on `[L]`-and-unpromoted
justifications exists for exactly this.

---

**WHAT THIS ENTRY DOES NOT CLAIM.**
- ⚠ **Not that the folds already run are wrong.** Ungated is not the same as incorrect; the census
  folded. What is unmeasured is how close any of them came.
- ⚠ **Not that the persistent child was a mistake when it was made.** Weight-reload cost is real
  and the rationale is sound in isolation. **The defect is that it was never rejoined to `F-064`.**
- ⚠ **Not closed by the branch that repairs it.** `D-074` — the instrument must stop exhibiting it,
  and that is measured after the fix lands, not asserted by it.
- ⚠ **Not a claim about the rental tier.** This is the local worker path on this host.

**Relied on by:** `D-157`'s residual on campaign cost · the Task 3 timing sample, whose per-fold
weight reload is a direct consequence of repairing the second half.

---

### F-066 — The IGF2R failure recorded as a card ceiling was a fold of the full chain, 227 residues longer than the ECD span the pipeline slices; and the attempt counter recorded zero attempts

- **Date:** 2026-09-02 · **Status:** ⚠ **OPEN.** It closes when the record states what job 57 actually attempted, **or** when the attribution is corrected wherever it is carried.
- **How known (`D-016`):** read-only SQL against production as `pharmfold-readonly`, 2026-09-02, under `ORDERS-Code-2026-09-02-fold-state-measurement.md` PART 3 §6.

**THE MEASUREMENT.** `jobs`/`protein_analyses` **57**: `accession = P11717`, `cohort_tranche = 0`, `status = 'failed'`, `tier = 'rental'`, `structure_source = ''` (**empty string, not NULL**), `span_aa` **absent**, `pdb_path` / `pae_json_path` / `mean_plddt` all NULL, `claimed_at` set 2026-07-25, `completed_at` NULL, **`attempts = 0`**.

`jobs.error`, in part: *"CUDA OOM folding **2491 aa** at chunk_size=32 … Tried to allocate 11.84 GiB."*

**THREE THINGS, SEPARABLE.**

1. ⚠⚠ **The object folded was 2,491 aa — the full chain.** The pending row 3356 carries **2,264**, the sliced ECD span, verified against its own stored sequence. **The failed attempt was 227 residues longer than the object the pipeline slices.** ⚠ **What is NOT claimed:** that this was a defect at the time. The ECD-slicing discipline may have landed after 2026-07-23, in which case 2,491 was correct then and the record simply does not say so. **Determining which requires the boundary-method history and has not been done.**
2. ⚠ **The project record carries this as *"IGF2R, A6000 ceiling."*** That reads as a card limit. The error is an OOM **on an object 227 residues longer than the one now scheduled.** ⚠ Whether the ECD span would also have OOM'd on that card is **unmeasured and is not asserted either way.** **The attribution may be right for the wrong reason, which is not the same as being right.**
3. ⚠ **`attempts = 0` on a row that was claimed and failed.** The counter did not record the attempt it failed on. ⚠ This is a **third** instance beside the two stale `claimed_open` failures already measured, and it is **not established** whether the counter is wrong or is incremented on a path this failure did not take.

**WHY IT MATTERS.** ⚠ **P11717 is the ruled pilot** (`D-109` ruling 6). The pilot's success criteria must not be read against a historical failure of a **different object**. ⚠ And `structure_source = ''` is an **empty string standing where a named category belongs** — the class this project closes repeatedly: absent values are named categories with causes, never silent blanks.

**NOT CLAIMED.** That job 57 should be deleted (`D-109` ruling 6 forbids it) · that the ceiling attribution is wrong (it is **unverified**, which is different) · that the counter is defective · that any other `structure_source` row is affected — **it is one row of 3,547.**

- **Amended by:** `F-066 amendment 1` (2026-09-11) — a fourth `attempts = 0` instance on a
  disjoint failure path, and the 2,691 / 2,690 mechanism correction.

#### F-066 amendment 1 — ⚠⚠ A FOURTH `attempts = 0` instance, on a different accession, a different tranche and a different failure mode; and the 2,691 / 2,690 seam is a MECHANISM correction, not a missing row

- **Date:** 2026-09-11 · **Status:** ⚠ **OPEN.** The parent stays open; this narrows clause 3 and closes nothing.
- ⚠ **Sub-entry beneath its parent, consuming NO integer** — the `D-099 amendment 1` precedent.
- **How known (`D-016`):** read-only SQL against production 2026-09-11 through the owner-held
  `flyctl mpg proxy`, role **`schema_admin`**, PostgreSQL **16.14 Percona**, repo `main` at
  **`ffea42e`**. ⚠ The tunnel was write-capable for its lifetime and **nothing was written** —
  recorded because a read whose role could have written is a different object from one that could not.

**1 — THE FOURTH INSTANCE, AND IT IS NOT THE SAME SHAPE AS THE OTHER THREE.**

Clause 3 of the parent records `attempts = 0` as a **third** instance, beside two stale
`claimed_open` failures, and states it is **not established** whether the counter is wrong or is
incremented on a path those failures did not take. **A fourth is now measured, and it discriminates
between those two explanations better than the first three could:**

| | parent's instance | this amendment's |
|---|---|---|
| id / accession | **57** / `P11717` (IGF2R) | **2015** / `P55073` (DIO3) |
| `cohort_tranche` | 0 — cohort-82 | **3 — census** |
| `structure_source` | `''` (empty string) | **`esmfold_local`** |
| failure | `CUDA OOM folding 2491 aa at chunk_size=32` | `unexpected fold failure: Unable to create tensor…` |
| class | a memory ceiling | ⚠ **`F-033`'s class** — an untokenisable residue surfacing as a tensor-shape complaint |
| `attempts` | **0** | **0** |

⚠⚠ **The two failures share NO path except the counter.** One is an allocator OOM on a rental-tier
cohort row; the other is a tokeniser rejection on a local-tier census row with a populated
`structure_source`. **They fail in different code, on different tiers, in different populations —
and both record zero attempts.** ⚠ That is evidence **against** *"the counter is incremented on a
path this failure did not take"* and **for** *"the counter does not record the attempt"*, because
two disjoint paths would both have to miss the same increment.

⚠ **Stated as evidence, not as a ruling.** `n = 2` of the four are now characterised well enough to
compare; the other two (`claimed_open`) are **not re-measured here** and the parent's *"not
established"* stands until they are. **What changes is that the question is now answerable** —
the parent could not distinguish the explanations and this pair begins to.

**2 — ⚠⚠ THE 2,691 / 2,690 SEAM: THE ACCESSION WAS RIGHT, THE MECHANISM WAS NOT.**

A derivation circulated as *"2,691 planned − 1 never folded = 2,690 **recorded**"*, naming `P55073`.
**The accession is correct. The mechanism is not, and the difference is the whole point of the
partition discipline `F-042` exists for:**

> ⚠⚠ **2,691 rows ARE recorded.** `P55073` has a `protein_analyses` row. What it lacks is a
> **`pdb_path`**, because the fold **failed**. Nothing is missing from the table.

**Measured, by tranche, key = `protein_analyses` rows:**

| cohort_tranche | rows | `pdb_path` non-NULL | `pae_json_path` non-NULL |
|---|---|---|---|
| 1 | 1,307 | 1,307 | **0** |
| 2 | 535 | 535 | **0** |
| 3 | 517 | **516** | **0** |
| 4 | 332 | 332 | **0** |
| **census 1–4** | **2,691** | **2,690** | **0** |

**So both figures are right and they count different things:**

> **2,691 = RECORDED rows. 2,690 = FOLDED rows.** `F-042`'s 2,690 denominator is **folded**, never
> **planned**, and the one-row gap now has a **named cause** rather than a plausible story.

⚠ **Why this matters beyond bookkeeping.** *"One row never folded"* and *"one row folded and lost
its artifact"* imply different repairs, and a re-fold campaign sized on the wrong one would look
correct and be off by a row in the direction nobody checks. **A denominator gap with no named cause
is exactly what `F-042`'s partition discipline exists to prevent.**

⚠ **Independent support, and it is not a second measurement.** `scripts/census_ingest.py` already
excludes untokenisable residues as a **named category before any write** under `D-085` — `P55073`'s
exact failure mode, pre-guarded. **That is corroboration from the code, not confirmation from the
data**, and it does not promote the derivation to a measurement; the SQL above does that.

**3 — WHAT THIS AMENDMENT DOES NOT CLAIM.**

- ⚠ **Not that the counter is defective.** Two disjoint paths recording zero is evidence; the
  increment site has **not** been read, and the two `claimed_open` instances have **not** been
  re-measured.
- ⚠ **Not that `P55073` should be re-folded, repaired, or deleted.** It is a measurement.
- ⚠ **Not that any recorded `pdb_path` resolves.** ⚠⚠ **A path is not a file.** The counts above are
  **recorded**, never **resolved**, and conflating the two is the trap in its original form.
- ⚠ **Not that the parent's clause 1 or 2 is affected.** The full-chain attribution and the
  *"2,491 vs 2,264"* finding are untouched by this.

---

### F-065 — A second decision namespace ran alongside the log for one work session, and three of its integers collide with live entries

- **Date:** 2026-09-02 · **Status:** ✅ **CLOSED on ruling** — `D-109` ruling 1 states that the repository namespace governs, and no repository artifact cites a `D-00NN` integer.
- **How known (`D-016`):** issue **#210** cites `D-0027, amends D-0026; D-0024 no-climb remains`, with canon at an Obsidian path outside the repository. Collisions checked by `grep -n "^### D-02[467]" docs/README.md`.

**The collision.** All three integers exist in `docs/README.md` with unrelated subjects:

| external | repository entry at the colliding number |
|---|---|
| `D-0024` | **D-024** — coverage and limitations are a first-class UI surface |
| `D-0026` | **D-026** — enqueue: the manifest becomes `protein_analyses` + `jobs` |
| `D-0027` | **D-027** — the scorer's feature set, fixed before fitting |

⚠ **This is `F-044`'s family and the worst version of it.** `F-044` records that the citation invariant proves a reference *resolves*, never that it resolves to the *right thing*. Here a reader resolving `D-0027` against the log lands on the scorer's feature set — a **live, load-bearing entry in a different subject area** — and nothing anywhere would object. ⚠ The invariant cannot catch this class at all, because both namespaces produce well-formed, resolvable references.

⚠ **It also runs against `D-108`, ruled the same day:** *a second home for claims is exactly how `D-062` happened.* `D-108` gave derived reading surfaces a folder **specifically so they could not become a second authority**. This was a second authority holding a decision the log did not have.

**What is NOT claimed.** ⚠ **No claim that the external work is wrong.** The rented-fold session produced the 728 folds and the hold-48 split, and `D-109` adopts most of its substance. ⚠ **No claim that the collision caused a defect** — no repository artifact cites a `D-00NN` integer, which is why this closes on ruling rather than on repair.

**Why it closes rather than staying open.** `D-074` holds a finding against an instrument open until the instrument no longer exhibits the problem **or** states what it gets wrong. Ruling 1 removes the second namespace's standing entirely, so the instrument no longer exists to exhibit it.

⚠ **The residual, named:** the Obsidian canon still holds content not in the repository. `D-109` carries the hold-48 substance forward; **anything else from that session that has not been carried forward is not in the project.** Continuity lives in the repository (KEEL Principle 8).

- **Amended by:** —

---

### F-064 — ⚠⚠ After a successful Blackwell RB fold, in-process release does not restore free for the next preflight: free collapsed 7043→1649 MiB while reserved stayed ~6900; after process exit the GPU was free again

- **Date:** 2026-08-31 · **Status:** ⚠ **OPEN.** It closes when successive local tiles on this card either (a) each start from a cold process (or equivalent teardown that restores free before the next preflight), or (b) the residual is named and accepted. ⚠ Process-per-tile is the prescribed next gate; do not lower operational max below 380 on this evidence alone.
- ⚠ **Do not take `F-050`.** The guard-direction sweep stays RESERVED and unwritten.
- **How known (`D-016`):** RB re-gate after Matt host clear (F-063). Card: NVIDIA RTX PRO 2000 Blackwell, ~8151 MiB, driver 610.88, WDDM. Harness on main via PR #199 (`fb3826cb`): `route=local` AND `length≤384`, `MEASURED_SUCCESS_PEAK_MIB=6357`, climb exact-L preferred else hard envelope, `WORKER_FOLD_IN_CHILD=1`, `--limit 10`, no `--continue-after-rb4`. Artifact: `data/control/rb_local/rb_local_summary.regate384.csv` (PR #201).

**THE NUMBERS.**

| fact | value |
|---|---|
| tile 1 | O75445 USH2A t17 **L=380** |
| tile 1 requirement | 6357 / `hard_envelope_6357` |
| tile 1 preflight | FIT (`free_before=7043`) |
| tile 1 peak_alloc / reserved | **6336** / **6900** |
| tile 1 pct_depart_f059 | 0.000926 |
| tile 1 folded | yes |
| tile 2 | O75445 USH2A t18 **L=374** |
| tile 2 preflight | **refused_insufficient_headroom** (`free=1649`, need 6357) |
| folded | **1/10**; tiles 3–10 not attempted |
| after process exit | nvidia-smi ~0 used / ~7899 free |

**THE SUBSTANCE.**

1. ⚠⚠ **The F-063 envelope licensed the first fold.** L=380 succeeded under 6357 with peak_alloc 6336. This is not a too-long-tile finding and does not authorize dropping operational max below 380.
2. ⚠ **In-process release did not restore free.** After tile 1, reserved stayed ~6900 and free fell to 1649 — same collapse shape as F-063’s climb `free_before`. `release_resident_model` / empty-cache inside one long-lived process is insufficient on this WDDM card.
3. ⚠ **Exit restores the device.** After the batch process ended, the GPU reported free again. The failure is residency across tiles in one process, not a stuck driver after exit. Process-per-tile (fresh OS process that exits before the next preflight) is the prescribed next gate.

**WHAT IT DOES NOT ESTABLISH.**

- Not a refutation of F-059 (tile 1 departure was tiny).
- Not a rewrite of D-104 / `route_at`.
- Not permission to `--continue-after-rb4`, climb, or rent.
- Not that Layer-1 / fold-in-child were unset for the successful tile.

- **Relied on by:** **D-105** (RB re-gate process-per-tile); process-per-tile RB re-run; any claim that empty_cache alone serializes folds on this card.
- **Assumptions refused:** that clearing the model cache in-process restores cold-start free between successive RB tiles on this Blackwell laptop.
- **Amended by:** —

---

### F-063 — ⚠⚠ Allocator-cap + child + Layer-1 attestation did not prevent a host bugcheck: climb reached highest_ok=384 with free_before collapsed to 1513 MiB, then the host died before 392 was written

- **Date:** 2026-08-31 · **Status:** ⚠ **OPEN.** It closes when folds on this host are either (a) proven safe under a gate that refuses before free/reserved collapse of this shape, or (b) ruled off this host with the residual named and accepted. ⚠ **No further folds on this host by any recipe until Matt clears it** (D-082 / climb docstring).
- ⚠ **Do not take `F-050`.** The guard-direction sweep stays RESERVED and unwritten.
- **How known (`D-016`):** Blackwell ceiling climb on MDKDevLaptop after Matt Layer-1 attestation. Card: NVIDIA RTX PRO 2000 Blackwell, ~8151 MiB, driver 610.88, WDDM. Command class: `ceiling_climb` / Q8WXD0 / tier local / int8 / chunk 64 / `--start 248 --stop 456 --step 8` / `--memory-fraction 0.85` / `--empty-cache` / `--fold-in-child` / `--layer1-attested`. Artifact: `data/census/ceiling_climb.blackwell.int8.20260831.jsonl` (8889 bytes, **0 NUL bytes** — fsync held). Companion: `data/census/ceiling_climb.blackwell.int8.20260831.runlog.err.txt` (and empty `.runlog.txt`). Control copies: `data/control/blackwell-climb-20260831/`. Matt reported OOM + **system crash**. Climb processes killed after. No `oom_caught` / stop / summary line in the jsonl. Note: `LastBootUpTime` still showed 2026-08-27 after the event — may have been a GPU/driver hard fault without a full OS reboot; either way the host was not safe to continue.

**THE NUMBERS.**

| fact | value |
|---|---|
| OK ladder | 248,256,…,384 — **18** ok steps |
| highest_ok | **384 aa** |
| last OK peak_alloc | **6357 MiB** |
| last OK peak_reserved | **6902 MiB** |
| last OK free_before | **1513 MiB** |
| last OK f059_peak_mib | 6350.37 |
| last OK pct_depart_f059 | 0.001044 |
| last OK wall | 54.16 s |
| next planned | 392…456 — **not recorded** |

F-059 agreement on every OK step was tight (pct_depart ≤ ~0.0014). The law tracked demand. The host still died.

**THE SUBSTANCE.**

1. ⚠⚠ **D-082’s three layers did not keep the host alive on this climb.** Allocator cap (0.85), persistent child (`fold-in-child`), and owner-attested Prefer No Sysmem Fallback were all in force. The failure was a **host crash / hard fault**, not a catchable `oom_caught` in the jsonl.
2. ⚠ **Headroom had already collapsed while steps were still `ok`.** At L=384, `free_before_mib=1513` with reserved 6902 near the cap. Empty-cache did not restore free. The climb continued. The next step was never fsynced.
3. ⚠ **`highest_ok=384` / peak_alloc 6357 is a recorded last OK, not a license.** It is a **candidate** `MEASURED_SUCCESS_PEAK_MIB` for a future RB re-gate on this card only after Matt clears the host. ⚠ **Do not run `--continue-after-rb4` or any local tile fold from it tonight.**

**WHAT IT DOES NOT ESTABLISH.**

- Not that Layer-1 was unset (Matt attested; flag was passed).
- Not a refutation of F-059 (departures were small on OK steps).
- Not a rewrite of D-104 / `route_at`.
- Not permission to rent, resume climb, or fold on this host tonight.

- **Relied on by:** host clear; Blackwell RB re-gate (`scripts/rb_local_tile_folds.py`: L≤384 filter on the D-104 local population, `MEASURED_SUCCESS_PEAK_MIB=6357`, per-tile climb-exact peak else hard envelope, **D-105 process-per-tile**, artifact `data/control/rb_local/rb_local_summary.regate384.procpertile.csv`; `rb_local_summary.regate384.csv` is the PR #201 early-stop evidence and is not overwritten by that path); F-062 (card-bound envelopes).
- **Assumptions refused:** that cap + child + Layer-1 attestation is sufficient to make over-allocation fail as a job rather than as a bugcheck / hard fault on this WDDM laptop.
- **Amended by:** —

---

### F-062 — ⚠⚠ Measured-success envelopes are card-bound: S-005’s 6665 MiB does not license a Blackwell FIT, and F-059 within 10% does not certify headroom

- **Date:** 2026-08-31 · **Status:** ⚠ **OPEN.** It closes when local RB gates on a measured success recorded on the **same card / recipe / allocator fraction** that will fold — or when the residual is named and accepted.
- ⚠ **Do not take `F-050`.** The guard-direction sweep stays RESERVED and unwritten.
- **How known (`D-016`):** RB4 stop on the laptop GPU. Card: NVIDIA RTX PRO 2000 Blackwell, 8151 MiB total, driver 610.88, WDDM. First tile under longest-first order: **Q96QU1 PCDH15** `tile_index=1`, span 278–717, **L=440**. `preflight` **FIT** under `requirement_mib=6665` / `margin_mib=0` (the S-005 measured-success envelope from Trinity’s RB spec) with `free_before=7043` MiB. Fold raised **CUDA OOM** at ~12.9 s; `peak_allocated_mib=6559`, `peak_reserved_mib=6774`. `f059_peak_gib=6.499514`; `pct_depart_f059=0.0145` (1.45%). Batch **stopped** (non-zero); did not skip to the next tile. Artifact: `data/control/rb_local/rb_local_summary.csv` on main via PR #195 (`88d59bb6`).

**THE SUBSTANCE.**

1. ⚠⚠ **S-005’s 6665 MiB is not a measurement of this card.** S-005 (2026-07-19) recorded 440 aa clean at int8/chunk 64 with peak 6665 MiB on an earlier stack/day. Using that number as `requirement_mib` on Blackwell produced **FIT then OOM** — the failure mode the guard exists to prevent, transferred across hardware.
2. ⚠ **F-059 within 10% does not certify headroom.** Departure was 1.45%, under RB4’s law-check stop. The fold still OOMed. The law predicts demand; it does not certify free headroom after the caching allocator’s reserved pool, a 0.85 cap, or a different GPU.
3. ⚠ **D-104 `route_at=440` vs F-059’s local ceiling ~431–432 is live, not paper.** Local route includes L=440; F-059’s fitted local ceiling is ~431–432 aa. The first tile in longest-first local order is exactly that collision.

**WHAT IT DOES NOT ESTABLISH.**

- Not a refutation of F-059’s coefficients (one OOM, different card).
- Not permission to pass `f059_peak_gib` as `requirement_mib` (F-061 stands).
- Not an open of rental / RC / RD.
- Not a rewrite of the D-104 table — a `route_at` amendment is a **separate owner ruling**.

- **Relied on by:** Blackwell `ceiling_climb` (Matt ruled C then A); RB re-gate after climb (L≤ `highest_ok_length`, new `MEASURED_SUCCESS_PEAK_MIB` on this card).
- **Assumptions relied on:** none new. ⚠ **One refused:** that a measured peak on one card licenses `preflight` FIT on another.
- **Amended by:** —

#### F-062 amendment 1 — the guard pinned the pointer's VALUE, so it goes red on the discipline it was written to enforce; and a second pin of the same value is guarded by nothing

- **Date:** 2026-09-03
- **Status:** ⚠ **OPEN** until both pins are invariant-shaped or removed, and the assertion has been shown to bite.
- **Found by:** Planner, diagnosing a red `test` check that blocked PR #209. ⚠ **Code was forbidden by order from rerunning, fixing, or diagnosing it, and did not.** ⚠ **The second pin was found by Code**, reading the file under an order whose scope was the assertion alone; **it reported the pin and did not touch it, because extending scope would have been Code deciding scope.**
- **Context — two pins of the same literal, in one file:** `tests/test_f062_ceiling_climb.py` line 8, the module docstring, reads *"RESERVED next-free is F-065; F-050 stays reserved"*; line 69 asserts `"Next free \`F-\` integer: \`F-065\`" in reserved`, with the message *"the next-free pointer must move in the SAME commit that spends F-064"*. ⚠ **`docs/RESERVED.md` on `docs/paper-phase-structure` reads `Next free \`F-\` integer: \`F-067\``**, because `314df71` spent `F-065` and `F-066` and **moved the pointer in the same commit** — ⚠ **exactly the discipline the assertion's own failure message demands.**
- **The defect:** ⚠⚠ **The guard fires on the correct behaviour it was written to enforce.** It encoded a rule about **movement** as a literal **value**, so it passes only while nothing happens and goes red every time an `F-` integer is legitimately spent. ⚠ **Not a false alarm about a real problem; a true alarm pointed backwards.**
- ⚠⚠ **The second pin is the more dangerous one.** The assertion at line 69 is a literal **guarded by a test that goes red.** The docstring at line 8 is a literal **guarded by nothing.** ⚠ **It goes stale silently — no diff, no failing test to mark the moment** — the defect `ui/src/censusSummary.js` records of itself at line 12 as *"a sentence that keeps its wording while the world moves under it, with no diff and no failing test to mark the moment (`F-049` amendment 2, instance 4)."* ⚠ **And had the assertion alone been fixed, the file's stated contract summary would assert `F-065` while its assertion checked an invariant and the pointer read `F-067`: the file contradicting itself, which is worse than the state before the fix.**
- **Why the defect survived:** ⚠ **the test reads the repository's own files** — `LOG = REPO / "docs" / "README.md"` and `RESERVED = REPO / "docs" / "RESERVED.md"` at lines 21–23 — **so it could never be shown to fail without editing them.** A guard that cannot be made red on demand has not been shown to bite. **The remedy therefore extracts a pure function over two strings before it changes the assertion**, so the failing cases are demonstrated against fixtures rather than against the tree. ⚠ **The docstring is not under test and no fixture can prove it** — it is reviewed, not verified, and the record says which of the two pins was proven.
- **Attribution, stated precisely:** ⚠ **On `origin/main` this test PASSES** — that pointer still reads `F-065`. **The branch turned it red.** `D-013` holds: the red is attributable to a commit in this repository, and it is `314df71`. ⚠ **What is NOT true is that `314df71` did anything wrong.** **A red gate attributable to a commit is not the same as a defective commit.**
- **What is NOT claimed:** ⚠ Not that the other assertions in this file are defective — `test_f050_was_not_taken()` (`def` at line 58) carries an invariant-shaped check at line 61, `assert re.search(r"^### F-050 ", log, re.M) is None`, which survives every land. ⚠ **The correct pattern was already in the file, in the immediately preceding test, eight lines above the broken assertion.** ⚠ Not that `F-062`'s finding is wrong. ⚠ Not that the ceiling-climb pins are wrong. ⚠ **Not that this is the `F-050` sweep** — that is reserved and the owner's.
- **The remedy, and the refused one:** ✅ **The assertion checks the invariant:** the pointer's integer is **not** a spent `### F-NNN` heading, **and** is greater than every spent heading. ⚠ **The failure message stays exactly as written**, generalising only the named integer. ✅ **The docstring states the RULE, not a value** — that the next-free pointer must exceed every spent heading and must not name a spent one — **or it drops the clause entirely.** ⚠ **A summary line restating a value the file already checks is a second copy that can drift**, and this is what drifting looks like. ❌ ⚠ **REFUSED: bumping either literal `F-065` → `F-067`.** It re-arms the identical trap for whoever spends `F-067` next and converts a guard into a maintenance obligation nobody will remember. ⚠ **Refused on purpose and recorded as refused**, because it is the fastest thing to do and that is precisely why it needed a ruling.
- ⚠ **Scope of the remedy:** the assertion parses the **`F-` namespace only.** ⚠ **`main`'s `D-` pointer names `D-106`, and `### D-106` exists on `main`** — both clauses of the same invariant violated, in the `D-` namespace, with **no test guarding it**. ⚠ **Extending the check there is deliberately NOT done here**: it would turn `main` red until the corrected pointer lands, and that correction is in PR #209. **Sequenced after the merge, and named so it is not forgotten.**
- **Deep-learning justification:** Neutral to the DL core — no weights, no inference, no data path, no change to the fold recipe. ⚠ **The relevance is that this guard sits in the file protecting the ceiling-climb contracts**, and `F-062`'s own finding is that *measured-success envelopes are card-bound*. **A guard that goes red for a reason unrelated to what it protects trains a reader to discount it**, and the next red in this file — one that does concern the climb, the card, or the fold — arrives already discounted.
- **Closes when:** both pins are invariant-shaped or removed, **and** the assertion has been shown to fail at the assertion against a fixture where the pointer names a spent integer. ⚠ **A test that has never failed has not been shown to bite**; ⚠ **an error-red is not a failure-red.**
- **Relates:** `F-062` (parent) · `F-049` (a sentence keeping its wording while the world moves under it — ⚠ **the docstring pin's class**) · `F-044` (a reference silently acquiring the wrong target) · `F-039` (a second copy of a record that can drift) · `D-013` (a red gate is attributable to a commit) · ⚠ `F-050` **RESERVED and UNWRITTEN — named as the reservation it is, not as evidence.**
- **Amended by:** —

---

### F-061 — ⚠⚠ Recording `F-059` on the tile is not measuring the case in front of it, and `preflight` still refuses an absent measurement

- **Date:** 2026-09-01 · **Status:** ⚠ **OPEN.** It closes when the fold path constrains on a
  **measured** memory requirement for the case in front of it — or continues to state, in itself,
  that it does not and why. ⚠ `F-050` remains RESERVED for the guard-direction sweep and is not
  this entry.
- **How known (`D-016`):** `F-059` §1 and §5 (the law, and the clause that a law is not a
  measurement of the case); `core/vram_guard.py:preflight` as written (`requirement_mib is None` →
  `refused_no_measurement`); `F-049` / `F-053` §4 (`preflight` is written, tested, and consulted by
  nothing, and it has guarded the length axis); this pass's RA2 artifact, which is cache-only and
  performs no live CUDA read.

**THE DISTINCTION, AND IT IS THE WHOLE FINDING.**

`F-059` fits `peak_GiB = 5.24 + 7.215e-06 · L^1.983`. That is a **law**. RA3 records it on every
tile as `f059_peak_gib`. ⚠⚠ **A law is not a measurement of the case in front of it** — `F-059` §5,
quoted into `docs/ORDERS-Code-2026-08-23-the-rental-run.md` RA3, and not weakened here.

`vram_guard.preflight()` still takes a **measured** `requirement_mib`. `None` is
`refused_no_measurement`. ⚠ **Passing `f059_peak_gib` (converted or not) as `requirement_mib` would
be plugging the law in as the measurement**, and the test that pins this must go red if that
happens. The helper `f059_peak_gib(L)` is therefore a **recorder**, not a second door into
`preflight`. The `preflight` signature is unchanged.

**WHAT THIS PASS DID NOT DO, STATED ON THE ARTIFACT.**

| fact | where it lives |
|---|---|
| the fold loop still does not consult the guard | `preflight_why` on every tile row; RB, not this pass |
| RA2 emitted the CSV with no live CUDA | same field; cache-only |
| `requirement_mib` was `None` | `preflight_outcome = refused_no_measurement` |
| `F-059` was recorded, not consulted | `f059_peak_gib` column, separate from `preflight` |

⚠ **`F-049` established the guard is consulted by nothing.** This pass does not close that. It
names the residual on the tile so a later fold cannot read the recorded law as a preflight that
ran.

**WHAT THIS DOES NOT ESTABLISH.**

- ⚠ **Not that any tile fits the local card.** `F-059` predicts; `ceiling_climb` measured 432 aa on
  one protein, one day, one driver. A different sequence at the same length is not that measurement
  (`vram_guard.DEFAULT_MARGIN_MIB` exists for this reason).
- ⚠ **Not a licence to fold.** RB is a later pass. Abort-before-fold remains unbuilt here.
- ⚠ **Not `F-050`.** The guard-direction sweep stays reserved and unwritten.
- ⚠ **Not a close of `F-053`.** The fold path still does not constrain on the memory axis. This
  entry is the record that we stated we did not, and why.

- **Relied on by:** RA3 · `D-104` · `core/vram_guard.py:f059_peak_gib` · `data/census/tranche6_tiles.csv`
- **Amends nothing.** `F-059` §5 stands. `F-053` stays OPEN.

---

### F-059 — ⚠⚠ The fold's incremental VRAM is O(L²), and the band `D-077` calls UNMEASURED was measurable from ten folds already committed — no new fold was needed, and `F-053`'s release hypothesis does not survive the law

- **Date:** 2026-08-22 · **Status:** ⚠ **OPEN.** It closes when the fold path constrains on the
  measured memory law — or states, in itself, which quantity it constrains on and why not this one.
- **How known (`D-016`):** **re-analysis of measurements already in the tree. No fold was run for
  this entry.** `data/control/sb_timing/timings.json` — ten local int8 chunk-64 folds, 2026-08-20
  02:40–02:43 UTC, driver 610.88, the same run `F-053` reports. Cross-checked against
  `data/census/ceiling_climb.int8{,.release,.uncapped}.jsonl` — 2026-08-16, `Q8WXD0` truncation
  series, **a different protein, a different script, a different day.**

---

**1 — THE LAW.**

Subtracting the resident model at `span_aa = 1` from each peak gives the fold's own cost:

| span | peak GiB | incremental GiB |
|---|---|---|
| 1 | 5.24 | 0.00 — the resident model |
| 134 | 5.36 | 0.12 |
| 218 | 5.55 | 0.31 |
| 315 | 5.89 | 0.65 |
| 439 | 6.50 | 1.26 |

**Consecutive fitted exponents: 1.95 · 2.01 · 1.99.**

> **`incremental_GiB = 7.215e-06 · L^1.983`**, against a **5.24 GiB** resident model and **1.43 GiB**
> of CUDA context / workspace / fragmentation overhead, calibrated from `free_after = 0.03` at 439 aa.

⚠ **The exponent is 2 because the resident tensor is the pair representation.** Chunking at 64 stops
the trunk materialising its O(L³) triangular attention; what stays is O(L²). **The law is
mechanistic, not merely fitted** — which is why it is quoted further out than a bare curve fit earns,
and it is still an extrapolation out there.

**2 — ⚠⚠ IT CROSS-VALIDATES ON AN INDEPENDENT PROTEIN, WHICH IS WHY IT IS AN ENTRY AND NOT A FIT.**

| check | law predicts | independently measured | source |
|---|---|---|---|
| peak at 456 aa | 6.59 GiB | **6.60 GiB** | `ceiling_climb.int8.uncapped.jsonl` |
| max span, local 8 GiB card | 431 aa | **432 aa** | `ceiling_climb.int8.release.jsonl` |

**Two paths to one quantity, compared ON THE NUMBERS: agreement to 0.01 GiB and to one residue.**

**3 — ⚠⚠ `F-053` §5's HYPOTHESIS DOES NOT SURVIVE, AND THE CORRECTION IS RECORDED, NOT PATCHED AWAY.**

`F-053` §5 states, explicitly as a hypothesis and not as a claim: *"some part of the `441–629` band
may be foldable LOCALLY if the model is released and reloaded around large folds,"* on the ground
that releasing frees ~5.24 GiB against a ~1.26 GiB incremental.

⚠⚠ **The arithmetic compares two quantities that are never in memory at different times.** **A fold
requires the weights.** Releasing the model changes what is resident **between** folds, not the peak
**during** one, and the peak is what OOMs. **Peak(L) = 5.24 + incremental(L)** whether or not
anything was released beforehand.

**Applying the law to the band the hypothesis is about:**

| L | predicted peak | against ~6.53 GiB usable |
|---|---|---|
| 456 aa | 6.59 GiB | measured OK **uncapped only**, at `free = 0` |
| 500 aa | 6.86 GiB | **does not fit** |
| 629 aa | 7.80 GiB | **does not fit, by a wide margin** |

**So the `441–629` band is not locally foldable at this recipe, released or not.** ⚠ **`F-053`'s
hypothesis was correctly labelled as one, and it is the reasoning that fails, not the discipline.**

⚠⚠ **AND `F-053 amendment 1` CALLED THIS, FROM DATA THAT ALREADY EXISTED.** Written 2026-08-20, it refused §5 on exactly the right ground — *"the incremental was measured at 439 aa and its scaling is UNMEASURED… trunk attention is at least O(L²); there is no reason to expect 629 aa to cost 1.26 GiB"* — and separated the time law from the memory one. **The fit above is L^1.983.** ⚠ **The prediction was correct and the measurement was already in the tree when it was made.** *What was missing was not a fold; it was the subtraction.*

⚠ **A precision this entry must not blur.** `ceiling_climb.int8.release.jsonl` applies
`torch.cuda.empty_cache()` — **it empties the CACHE; it does not unload the MODEL.** Its
`free_after_release_mib = 1,517` is the proof: **~6.6 GiB stays resident.** So it does **not**
directly test `F-053`'s unload-and-reload proposal, and reading it as though it did would be
`F-047`'s shape exactly. **What it does show is corroborating and pointed:** the released arm
reached `highest_ok = 432` while the **uncapped** arm reached **456**. ⚠⚠ **Releasing did not raise
the ceiling. Lifting the 0.85 allocator cap did.**

**4 — ⚠ WHAT WAS ORDERED THAT DID NOT NEED TO BE RUN.**

`HANDOFF-Code-rental-phase-1-COMPLETE.md` §4 ordered **one fold at ~500 aa** to obtain *"the FIRST
DATUM on the memory-versus-length curve,"* adding *"one point does not make a curve and your report
must say so."* ⚠⚠ **Ten points were already committed, from the run the same document cites twice
for its 5.24 and 1.26 figures.** **The curve existed; only the subtraction was missing.**

⚠⚠ **And the ordered fold is predicted to OOM at 6.86 GiB against ~6.53** — on the owner's laptop,
where `D-082`'s failure mode is a host bugcheck and `preflight` is unwired and guards the length
axis. **A measurement already in hand would have removed the reason to attempt it.**

**5 — ⚠ WHAT THIS DOES NOT ESTABLISH.**

- **Fitted over 134–439 aa; cross-validated at one point, 456 aa.** Every figure beyond that is
  extrapolation. The 48 GiB card's ~2,528 aa is **5.8× past the fitted range** — **planning, never
  permission.** ⚠ **Each card class still needs its own `ceiling_climb` before anything is queued.**
- **int8, `chunk_size = 64`, one card, one driver.** ⚠ **fp16 is unmeasured and roughly doubles the
  resident model**, which moves the intercept, not necessarily the exponent.
- ⚠ **It does not license weakening `preflight()`.** `refused_no_measurement` on an unmeasured length
  remains correct: **a law is not a measurement of the case in front of it.**
- ⚠ **It says nothing about whether any of these targets is worth folding.** Cost and tractability
  only — `census_cost.py`'s standing caveat, `D-077` decision 1.

**⚠ Relied on by:** `docs/PRICING-2026-08-22-all-remaining-tranches.md` §2. **Amends nothing** —
`F-053` §5 is refuted in the open above and left standing where it is written.

---

### F-060 — ⚠⚠ A cost plan split on the constraint that had stopped binding: tranche 5's boundary was never VRAM, and the 141 rows money cannot help are the surface class the platform exists for

- **Date:** 2026-08-22 · **Status:** ⚠ **OPEN.** It closes when the rental plan is split on the
  trained context rather than on card capacity, or when the residual is named and accepted.
- **How known (`D-016`):** `census_manifest.v7.csv` (3,467 rows, tranche 5 = 776, spans re-derived
  here), `facebook/esmfold_v1`'s `max_position_embeddings = 1026`, and
  `PROPOSAL-claim-tier-filter-and-tranche-5-cost.md` §2 and §3 read **as two dated layers of one
  document**, which is the point of the entry.

---

**1 — THE PLAN SPLIT ON MEMORY.**

§2 of the proposal (2026-08-16) bands tranche 5 at **441–850 / 851–2,000 / 2,001–4,000 / 4,001+**,
with verdicts *"plausible on 48 GB," "needs 80 GB class," "beyond single-card estimate."* ⚠ **Every
boundary is a card-capacity boundary**, resting on an explicitly-flagged estimate — *"~850 aa"* for a
48 GB card — which the document itself marks *"extrapolations and the project's own instrument
refuses to make them."*

**2 — THE ESTIMATE WAS 3× PESSIMISTIC, AND THE BOUNDARY MOVED OFF THE TABLE ENTIRELY.**

`F-059`'s measured law puts a 48 GB card at **~2,528 aa**, not ~850. ⚠⚠ **Only 25 of 776 rows exceed
it.** **Memory stops being the binding constraint for 97% of the tranche the moment the law is
fitted** — and it was fittable from data committed on 2026-08-20.

**3 — ⚠⚠ WHAT ACTUALLY BINDS, AND THE DOCUMENT ALREADY KNEW.**

§3 of the same proposal — **added 2026-08-16, the same day, after the owner challenged a word** —
records the real limit: **`max_position_embeddings = 1026`.** Rotary embeddings extrapolate, so
**nothing refuses a long sequence; it returns a structure and there is no evidence it means
anything.** §3 states it plainly: *"This is not a hardware question and renting a bigger card does
not touch it."*

| tranche-5 rows | count |
|---|---|
| ≤ 1,026 aa — inside the trained context | **635** |
| **> 1,026 aa — outside it** | **141** |
| of those 141, `census_class = surface` | ⚠⚠ **136** |

**4 — ⚠⚠ THE FINDING: §3 CORRECTED THE DOCUMENT'S LANGUAGE AND LEFT ITS BUDGET ALONE.**

§3 retracts *"infeasible"* and *"impossible"* — **a real correction, recorded rather than edited
away, and right.** ⚠⚠ **But §2's cost table above it was never re-split.** The document therefore
carries, in one file, **a section that identifies the binding constraint and a section that prices
the work against a different one** — and the priced section reads as current because nothing in it
is *wrong*, only **scoped to a constraint that had been superseded four screens below.**

⚠⚠ **The class: when a constraint is relieved, a plan written against it does not announce that it
has stopped applying.** It keeps returning clean numbers about the wrong axis. **`F-053` named this
for a guard — length versus memory. This is the same defect one level up, in a budget** — and here
the superseding fact was not merely available, it was **in the same document, added the same day.**
⚠ *A correction that fixes the prose and not the arithmetic leaves the arithmetic looking ratified.*

**5 — ⚠ THE CONSEQUENCE, AND IT CUTS BOTH WAYS.**

- **The purchase is smaller and better-defined than the plan implied:** 635 rows, **17–29 GPU-h,
  $9–23** — memory no longer binding, all inside the trained context.
- **The expensive tail should not be bought at all.** The 141 cost ~$65–104 and buy structures with
  **no evidence any of them means anything.** ⚠⚠ **That is an expensive purchase, not a cheap one,
  because the output is unevaluable.**
- ⚠⚠ **And for the ten that matter most the remedy is FREE.** FAT1–4, LRP1 / LRP1B / LRP2, USH2A,
  ADGRV1, PKHD1L1 are stacks of independently-folding domains, **most of them inside 440 aa — inside
  the LOCAL ceiling.** **Domain assembly is not a workaround for these; §3 already argues it is the
  correct model.** ⚠ It changes `boundary_method`, so the artifacts are **not comparable to
  single-pass folds** without saying so (`D-076` Tier 2).
- **The three mucins stay excluded on the biology** — `D-085`, `D-076` Tier 3. ⚠ *Neither compute nor
  assembly helps.*

**6 — ⚠ WHAT THIS DOES NOT ESTABLISH.**

- ⚠⚠ **It does not establish that a fold past 1,026 aa is worthless — only that nothing here makes
  it EVALUABLE.** That is an absence of evidence, named as one, and it is the reason not to spend.
  **`D-085`'s ruling already forbids reading *excluded* as *unfoldable*, and this entry does not.**
- **Row counts are from the manifest, not from a live database read.** ⚠ The proxy on 16380 was
  closed. **Fold state does not enter the split; `tier` and `span_aa` do.**
- ⚠ **It is not a suitability axis.** Nothing here says any of the 635 is a good ADC target.
- ⚠ **`D-089` still holds — no census row is scored** — and nothing above changes that.

**⚠ Relied on by:** `docs/PRICING-2026-08-22-all-remaining-tranches.md` §3 and §5. **Cites `F-059`
for the law and `D-085` / `D-076` for the exclusions; amends neither, and amends no clause of the
proposal, which is left standing in both its layers.**

---

### F-056 — ⚠⚠ The test substrate forgives exactly the mistake production rejects: 2,690 census cards were 500 in production while the suite was green

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN.** It closes when no test's correctness depends on
  SQLite's coercion behaviour, or when each such test states that it does.
- **How known (`D-016`):** measured directly against both engines while diagnosing a live outage.

**⚠⚠ THE OUTAGE.** **Every one of the 2,690 FOLDED census cards returned HTTP 500 in production.**
**Sampled 8/8 folded → 500; 8/8 unfolded → 200.** ⚠ **The unfolded rows return before the offending
call, which is why they worked and why the scope stayed hidden.**

**⚠ THE CAUSE.** Widening `/census/{analysis_id}` to `str` so accessions could be used as keys left
one downstream consumer passing the raw parameter — `census_profile_block(engine, analysis_id)`,
signature `analysis_id: int`.

**⚠⚠ AND THE REASON THE GATE CANNOT SEE THIS CLASS AT ALL:**

```
SQLite:   session.get(ProteinAnalysis, "1970")   -> row found   (string PK silently coerced)
SQLite:   session.get(ProteinAnalysis, "A0AVI2") -> None, no raise
Postgres: rejects both
```

⚠⚠ **This is not a coverage gap. The test substrate has DIFFERENT SEMANTICS from the thing it stands
in for, and no quantity of additional SQLite tests would have caught it.** ⚠ *Distinguishing that
from the day's other two green-tests-broken-production findings is what makes this its own entry.*

**⚠ THE REMEDY, and it has two halves that do different work:**
1. **The guard asserts WHAT IS PASSED — the resolved `int` — which is checkable on ANY engine.**
   ⚠ *The assertion stops depending on the substrate.*
2. ⚠⚠ **A second test RECORDS THE DIVERGENCE AS A FACT, so it reddens if SQLite or SQLAlchemy ever
   tightens.** **A known divergence that silently disappears is a guard whose premise expired without
   notice.** *(Code's second half, and the one the Planner would have omitted.)*

⚠ **What this does NOT claim:** not that SQLite is the wrong substrate · not that every test is
suspect · ⚠⚠ **only that a test's correctness may rest on engine behaviour nobody stated, and that
every test in this project resolving a primary key stands on it.**

---

### F-057 — ⚠⚠ A parameter whose type widens has as many defects as it has consumers, and they do not announce themselves together

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN.**

**Widening `/census/{analysis_id}` produced TWO defects from ONE change:**

| consumer | defect | scope |
|---|---|---|
| `census_profile_block` | **HTTP 500 on Postgres** | **2,690 cards** |
| structure / pLDDT URLs | **HTTP 422** | the viewer |

⚠⚠ **The first was fixed one day before the second was found, by the same person, who did not look
for a second consumer.** *(Code's own framing, adopted verbatim as the entry's thesis.)*

⚠ **`F-052`'s family with a NEW MECHANISM.** **Not *a convention the newest caller missed* — a
SIGNATURE CHANGE whose blast radius nobody enumerated.** ⚠⚠ **And the two defects surfaced days apart
with different status codes on different surfaces, so nothing connected them.**

**⚠ THE REMEDY IS THE `PA` SHAPE: enumerate the consumers, BOTH DIRECTIONS, before fixing the one in
front of you.** *Forward — what does this function call? Reverse — what calls this parameter?*
⚠ **Name the check; do not build a framework** (`D-074` decision 3).

⚠⚠ **And the aggravating fact: `StructureViewer` had NO TEST FILE AT ALL.** **The component that
failed for five days was untested, which is why five days was possible.**

---

### F-058 — ⚠⚠ Three guards, three resolutions, and each fix inherited the previous level's unit

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN**, and ⚠⚠ **this entry is the reason the others recur.**

| # | guard | its unit | what it could not see |
|---|---|---|---|
| 1 | `NC`, the first attribution audit | **one component** | four other components rendering HPA data |
| 2 | `PA` / `PC3`, built to fix that | **the component set** | ⚠ **which BRANCH inside a component renders the value** |
| 3 | the branch fix | **the branch** | ⚠ *unknown — and that is the point* |

**⚠⚠ THE INSTANCE THAT NAMES IT.** In `CensusDetail`, the HPA attribution appeared **only in the
`status !== 'covered'` branch — which renders NO HPA value — and was absent from the branch rendering
`qh_score`, which is HPA content by `D-100`.**

⚠⚠ **So the licence precondition rendered where there was nothing to satisfy it about, and was absent
exactly where it binds.** **The suppression defect and the compliance defect were THE SAME DEFECT seen
from two sides, and only one of them looked like a defect.**

**⚠ `PC3` could not see it: *it asserts the file IMPORTS the attribution, and the file did.*** ⚠⚠ **A
file-level guard cannot see which branch renders the value.** *(Code's diagnosis.)*

**⚠⚠ THE GENERAL FORM, WHICH IS WHY THIS IS A FINDING AND NOT THREE INSTANCES: each remedy adopted
the granularity of the level it was fixing, and the next defect lived one level down.** ⚠ **A guard
inherits its unit from the defect that prompted it, and the defect that prompted it is by
construction the coarsest one anybody had noticed.**

**⚠ Named, not built** (`D-074` dec 3): **when writing a guard, state its UNIT explicitly and name the
next finer unit it cannot see.** ⚠⚠ **`PC3` would have said *"file-level; cannot see branches"*, and
this entry would have been unnecessary.**

---

### F-055 — ⚠⚠ A pre-registered floor excludes a target by 0.54 on a scale this project has never calibrated

- **Date:** 2026-08-21 · **Status:** ⚠ **OPEN**, and ⚠⚠ **NOT a proposal to move the floor.**
- **How known (`D-016`):** the 26 unranked cohort rows, measured at v100 while building
  `D-102 amendment 2`.

**`D-060` pre-registered a pLDDT floor at 50. Eleven cohort rows fall below it, spanning 30.68–49.46.**
⚠⚠ **The highest excluded row is `ATP2B2` at 49.46 — short by 0.54.**

**⚠⚠ THE FLOOR HOLDS AND THIS ENTRY DOES NOT ASK FOR IT TO MOVE.** **`D-060` ruled it before the data
existed, and moving a threshold after seeing which rows fall outside it is precisely what
pre-registration prevents.** ⚠ *Code identified this while building and explicitly declined to
propose a change — that restraint is the reason the observation is usable.*

**⚠ WHAT IT COSTS, WHICH IS THE ENTRY:**
- **A hard cutoff on a continuous scalar excludes a row by 0.54.** ⚠⚠ **`F-043`'s shape, turned on
  our own instrument** — *there we found a cutoff sitting on the modal value of an ~11-patient
  estimator; here we exclude a target by half a point.*
- ⚠⚠ **AND THE SCALE IS UNCALIBRATED FOR THESE TARGETS.** **`D-039` records that pLDDT calibration is
  not established for this cohort and that no code has ever fetched an experimental structure.**
  **So the 0.54 is half a point of a quantity whose relationship to accuracy is, on this population,
  unmeasured.**
- ⚠ **`F-051` sharpens it further:** the score the floor gates entry to **already carries 32.2% of
  its attribution on `membrane_proximal_plddt`** — **so confidence gates admission AND weights the
  result.**

**⚠ WHAT THE SURFACE DOES ABOUT IT, AND IT IS ALL THIS ENTRY LICENSES.** **The unranked group states
the pre-registered floor of 50 and renders `49.46`** — ⚠⚠ **a reader can judge the cutoff without us
moving it.** **`D-102`'s stated lens, applied to a threshold.**

**⚠ What this entry does NOT claim** — not that `ATP2B2` is a good target · not that 50 is the wrong
number · ⚠⚠ **not that any alternative floor was tested, because testing one now would be choosing a
threshold after seeing the data** · and not that the eleven are comparable to one another, since
30.68 and 49.46 are not near neighbours.

**Relied on by:** `D-102 amendment 2` §4.

---

### F-054 — ⚠⚠ 1,012 green tests certified a feature that was ENTIRELY ABSENT from production: every test asserted the SHAPE of the code, none asserted that a row came back, and a broad `except` converted one attribute error into 777 silently missing rows

- **Date:** 2026-08-20 · **Status:** ⚠ **OPEN** · **Author:** Code
- ⚠ The integer was confirmed against the live log before writing, and `docs/RESERVED.md`'s next-free pointer moved in the SAME commit that spent it.
- ⚠⚠ **Self-reported. The author of this entry is the author of the defect, and shipped it to production the same afternoon it fixed the thing it deleted.**

**WHAT HAPPENED.** PR #175/#176 deployed **v98** with the day's headline fix: the **777 never-folded census proteins**, added to the census list so that `HER2`/`ERBB2` — the owner's original question — is findable at all. The gate was green: **1,012 passed, 19 skipped**, plus 333 UI tests. Walking the surface after deploy:

| | |
| --- | --- |
| `/census/P11717` | **HTTP 500** |
| `/api/census` rows, live | **2,690** |
| manifest rows | **3,467** |
| unfolded rows actually served | **0 of 777** |

**⚠ THE FEATURE WAS NOT DEGRADED. IT WAS ABSENT**, and the census had silently returned to exactly its pre-fix state — the state the owner had reported as a defect that morning.

**THE CAUSE, IN ONE ATTRIBUTE.** `_attach_cohort_fold` read `c.error` to render a failed cohort attempt. **`ProteinAnalysis` has no `error` column.** The failure text lives on the JOB — `JobRecord.error` — and the helper that joins it, `_failed_accessions`, was **already in the same file, four hundred lines above the line that invented a second way to get it**. ⚠ That half is ordinary: a wrong attribute, an `AttributeError`, a 500 on the card route. It is loud and it is findable.

**⚠⚠ THE HALF THAT IS THE FINDING.** The `try` did not guard the enrichment. It guarded **both the row construction and the enrichment together**:

```python
try:
    unfolded = [dict(r) for r in unfolded_rows()]   # ← the 777 rows
    _attach_cohort_fold(engine, unfolded)           # ← optional decoration, and it raised
    out.extend(unfolded)                            # ← never reached
except Exception:
    pass                                            # ⚠ "degrades to the folded list alone"
```

The comment stated the intent — *tolerate a missing manifest* — and the code delivered something else entirely: **any fault anywhere in the block deletes 777 rows and returns a well-formed, HTTP 200, shorter list.** A handler written to survive an absent file was the mechanism that made present data absent.

**⚠⚠ WHY 1,012 TESTS SAW NOTHING.** All five tests covering this code parse the module with `ast` and assert on the tree: *does the function mention `cohort_attempt_failed`*, *does it avoid `commit`*, *does `census_span_aa` appear*. Every one passed, and every one would still pass today with the defect restored. **An AST test asks whether code was WRITTEN. It cannot ask whether it RUNS**, and it can never see a column that does not exist, because the column's absence is a fact about the database and the test never reaches one.

⚠ This is not an argument against the structural tests — three of them caught real inversions this week. It is the observation that **the suite had no test of the other kind at all** for this path, so the two questions were never distinguished and the weaker one stood in for both.

**HOW IT WAS FOUND: by walking the surface, after deploy.** Not by the gate, not by the deploy, not by a health check. ⚠ **That is the third defect this week found only by walking** — `F-052`'s exact observation, recurring inside the week `F-052` was written, in code written by the person who wrote `F-052`.

**⚠ WHAT THIS IS NOT.** Not `F-047`: nothing here was wrong-but-plausible, and no number was subtly off. **The answer was missing, and absence rendered as a shorter list** — which is worse than a wrong number, because a wrong number can be checked against something and a row that was never sent cannot.

**THE RESIDUAL, MEASURED.** Across `app/`, `core/` and `worker/` there are **9** `try` blocks with a broad, silent handler. **After this repair, 0 of them guard a statement that adds rows to a caller's list** (measured by AST: an `append`/`extend` inside the guarded body). ⚠ The widest surviving handler is `worker/runner.py:254`, guarding **4** statements, and **it has not been audited** — width is the risk, and 4 statements under one `except Exception` is the same shape at a smaller size.

**WHAT SHIPPED.**
1. The reason is read from `_failed_accessions` — the existing helper, already filtered to `COHORT_TRANCHE`, so it cannot leak a census failure onto a cohort row.
2. ⚠⚠ **The rows are extended into the list BEFORE anything that can raise touches them.** The guard now wraps the enrichment alone. Enrichment is optional; the rows are not.
3. Two tests, **both proved by revert — red at the assertion, not an error**. ⚠ The first version of the ordering test compared string offsets and reddened on correct code, because it matched `_attach_cohort_fold` **in its own explanatory comment** — `F-052`'s shape reproduced inside the test written to catch it, the fourth instance this week. It now walks the tree and asks which statements share a `try`.

**WHY IT STAYS OPEN.** The repair is specific to one route. What is not closed: **nothing in the gate asserts that any surface returns rows.** ⚠ A test that fetches the census list and asserts `>= 3,467` rows — or asserts that `ERBB2` is in it — did not exist before this entry and does not exist now, because it needs a database the gate does not have. **Until an end-to-end assertion exists somewhere, the class is open and the next instance will also ship green.**

---

### F-021 — A loader that inserts where it must update, rewrites inputs it was not asked to touch, and binds to the most recent run by default — three clauses with three different fates, and only one is repaired

- **Date reserved:** 2026-08-05, `RULING-2026-08-05-STOP-feature-7-not-extracted.md` §3.6 ·
  **Written:** 2026-08-19 · **Status:** ⚠ **OPEN.** It closes when
  `scripts/extract_features.py --load` upserts, or when the residual below is named and accepted.
- ⚠ **Written because it was cited before it existed.** `F-052` names `F-021` under *relied on by*,
  and the log pointed at a finding with no entry. **A reserved number that is cited is owed.**

---

**⚠⚠ THE ENTRY'S POINT IS THAT THE THREE CLAUSES DID NOT MOVE TOGETHER.** A class entry that reports
*"fixed"* or *"open"* for a three-part defect loses the only interesting thing about it.

**CLAUSE 1 — inserts where it must update. ⚠ CONTAINED, NOT REPAIRED.**
`scripts/extract_features.py:181` is still `session.add(ProteinFeatures(...))` — a pure insert, no
delete, no upsert. **The code is unchanged.** What changed is underneath it: migration `0010` added
`uq_protein_features_analysis_id`, measured in production. ⚠ So a second `--all --load` no longer
takes 80 rows to 160; **it raises `IntegrityError` and writes nothing.**
⚠⚠ **That is containment, and containment is worth less than it looks.** The loader still expresses
the wrong intent; the database now refuses it. **A caller who reads the code learns the wrong rule
and finds out at the constraint.** Recorded as a residual rather than as a fix.

**CLAUSE 2 — rewrites inputs it was not asked to touch. ✅ CLOSED, and by construction.**
`fill_feature_7` writes `membrane_proximal_sasa` **and nothing else**, in place, keyed by
`analysis_id`: **only where NULL** (an existing value is never overwritten, *including a legitimate
`0.0` — a fully buried window is a measurement, not an absence*), **`ranking_run_id` untouched**,
and **row count before == row count after, asserted inside the transaction.** ⚠ Not "we were
careful": the properties are checked where they could fail.

**CLAUSE 3 — binds to the most recent run by default. ✅ REMOVED at the CLI, ⚠ with dead code left.**
`--load` now errors without `--ranking-run`; the default that resolved to
`order_by(RankingRun.id.desc())` — id=4, `plddt_only`, on a docstring assumption true when one run
existed — was **deleted, not corrected.** ⚠ **The residue: `load_features()` still carries an
`if ranking_run_id is None` branch resolving to the newest run.** Unreachable from the CLI,
reachable by a direct call. **Named here rather than left for someone to find, and it is worse now
than when written: the newest run is id=5, a `sensitivity` run.**

---

**⚠⚠ AND THE THING THAT MAKES THE RESIDUAL LEGIBLE: TWO LOADERS NOW WRITE THE SAME TABLE UNDER
DIFFERENT DISCIPLINES.**

| | `scripts/extract_features.py --load` | `scripts/census_ingest_features.py` |
|---|---|---|
| write | **pure INSERT** | **UPSERT**, by `analysis_id` |
| re-run | raises at the constraint | **no-op**, keyed to the source `sha256` |
| bar | none | acceptance bar **inside** the transaction, rollback proven |
| `ranking_run_id` | **required** by flag | **NULL** — a category: *belongs to no run* |

⚠ **The newer one is what the older one should be.** That is not an argument for deleting the older
one — it fits the cohort, which does belong to a run — **but a reader comparing them learns two
different rules for one table, and only one of them is enforced by anything but a constraint.**

---

**⚠ WHY IT WAS RESERVED FOR TWO WEEKS AND WHAT THAT COST.** Nothing. **The defect never fired**: the
`--load` path was not run again, and the census ingest was written fresh. ⚠⚠ **But the reservation
was doing no work either** — it named a hazard that a later author would not have read, and the
protection that actually arrived was a **unique constraint added for a different reason.**
*A reserved number is a note to a future reader who has no reason to look for it.*

**⚠ What closes this entry:** `--load` upserting, or an accepted statement that the constraint is
the guard and the loader's intent is left wrong on purpose. **Neither has been ruled.**

**Relied on by:** `F-052` · `D-079 amendment 3`.

### F-053 — ⚠⚠ `CEILING_KNOWN_GOOD = 440` is a LENGTH; what actually binds is ~1.26 GiB of headroom against a 5.24 GiB resident model — and the guard, the climb and the preflight all measure the wrong axis

- **Date:** 2026-08-20 · **Status:** ⚠ **OPEN.** It closes when the fold path constrains on the
  quantity that binds, or states in itself which quantity it constrains on.
- **How known (`D-016`):** ten local int8 chunk-64 folds at the census recipe, spans chosen at evenly
  spaced ranks, on the RTX PRO 2000 (8.0 GiB, display holding ~1.1 GiB). **Measured, not modelled.**

---

**1 — THE MEASUREMENT.**

| span | time | peak VRAM | free after |
|---|---|---|---|
| **1 aa** | 13.7 s ⚠ *≈11.7 s of it loading 4,498 tensors* | **5.24 GiB** | 1.48 GiB |
| **439 aa** | 73.1 s | **6.50 GiB** | ⚠⚠ **0.03 GiB** |

⚠ **The Planner ordered ten folds describing this range as *"well inside `CEILING_KNOWN_GOOD = 440`."*
The first fold refuted the premise, and Code stopped rather than act on a belief the data had just
contradicted.** **0.03 GiB free of 8.0 is not *inside* anything.**

**2 — ⚠⚠ THE DECOMPOSITION, AND IT IS THE FINDING.**

**ESMFold stays RESIDENT between folds, by design — ~5.24 GiB.** **So the 6.50 GiB peak is
`resident model + fold`, and the INCREMENTAL cost of the largest census span is only ~1.26 GiB.**

⚠⚠ **`CEILING_KNOWN_GOOD = 440` encodes a LENGTH. The quantity that binds is MEMORY HEADROOM against
a resident model. They are different constraints and the log conflates them** — **one is a property
of the sequence, the other is a property of the card, the model AND a caching policy.**

**3 — ⚠ THE EVIDENCE IS THREE MIS-CALIBRATIONS IN ONE RUN, ALL BY THE SAME MECHANISM.**

**Code's guard was set at 6.9 GiB and blocked everything** — ⚠ **6.88 GiB is essentially the whole
card, and the 6.50 GiB peak had succeeded.** **Then it guarded TOTAL ALLOCATION rather than
HEADROOM.** **Then 1.6 GiB free against a fold that had already completed from 1.48.**

⚠⚠ **Code's own diagnosis, and it is the entry's thesis:** ***"My guard mis-calibrated three times
precisely because I kept reasoning about the length-shaped quantity instead of the memory-shaped
one."*** **The final threshold was grounded in a MEASURED SUCCESS rather than a fourth guess.**

**4 — ⚠⚠ WHAT ELSE MEASURES THE WRONG AXIS, AND THIS IS WHY IT LANDS BEFORE THE CLIMB.**

- **`vram_guard.preflight()` refuses on an unmeasured LENGTH** — ⚠ `refused_no_measurement`.
  **`F-049` established it is written, tested and consulted by nothing.** ⚠⚠ **So the guard nobody
  calls would also have guarded the wrong quantity if anybody had.**
- **`scripts/ceiling_climb.py` climbs the LENGTH axis to bracket `(440, 630)`.** ⚠⚠ **If the binding
  constraint is memory-shaped, the climb measures a proxy — and a proxy whose relationship to the
  real constraint depends on a policy nobody has recorded.**
- ⚠ **`D-082`'s blood line is a host bugcheck from over-allocation.** **A length-shaped guard cannot
  see an over-allocation that arrives by any other route.**

**5 — ⚠⚠ THE CONSEQUENCE FOR RENTAL, STATED AS A HYPOTHESIS AND NOT AS A CLAIM.**

**The model is resident BY POLICY, not by physics.** ⚠⚠ **Releasing it between folds would free
~5.24 GiB — roughly five times the incremental cost of the largest census fold measured.**

**So a named, UNMEASURED hypothesis: some part of the `441–629` band may be foldable LOCALLY if the
model is released and reloaded around large folds.** ⚠ **`FC` placed 3 of 6 recoverable positives in
exactly that band.**

**⚠ The cost side, so this is not read as free:** **reloading costs ≈11.7 s.** **Across 2,690 census
folds that is ~8.7 h of pure loading and is absurd. Across a handful of large folds against 75 s+
each, it is trivial.** ⚠⚠ **The policy is not one decision — it is a per-tier decision that nobody
has recorded as a decision at all.**

**⚠ NOT MEASURED, NOT CLAIMED, AND NOT A REASON TO SPEND OR NOT SPEND.** **It is a question the
rental ruling should be made in front of rather than behind.**

**6 — ⚠ What this entry does NOT claim.**
- **Not that `CEILING_KNOWN_GOOD = 440` is wrong.** ⚠ **It is a correct measurement of a length under
  an unrecorded policy** — *and that is precisely the problem: it is presented as a property of the
  hardware.*
- **Not that the climb is worthless** — ⚠ **only that its result is conditional on a caching policy
  that is not stated beside it.**
- ⚠⚠ **Not that any of the `441–629` band folds locally.** **n = 2 at the extremes and 10 in total is
  not a distribution**, and the incremental figure is one measurement at one span.
- **Not a proposal to change the caching policy.** *`D-074` decision 3: name the check, do not build
  the framework.*

**Relied on by:** ⚠ the rental ruling · `F-049` · and any future citation of `CEILING_KNOWN_GOOD`,
**which should carry *"a length, under a resident-model policy"* wherever it appears.**

#### F-053 amendment 1 — ⚠ §5's hypothesis has a hole: `span^1.26` is a TIME law and says nothing about MEMORY

- **Date:** 2026-08-20 · **Status:** `F-053` stays **OPEN.**

**§5 proposed that releasing the resident model frees ~5.24 GiB against a ~1.26 GiB incremental, so
part of the `441–629` band might fold locally.**

⚠⚠ **THE INCREMENTAL WAS MEASURED AT 439 aa AND ITS SCALING IS UNMEASURED.** **The Planner reasoned
*5.24 freed versus 1.26 incremental, therefore headroom* — and silently assumed the incremental is
roughly flat in span.** ⚠ **Trunk attention is at least O(L²); there is no reason to expect 629 aa to
cost 1.26 GiB, and no measurement either way.** ***`span^1.26` describes TIME. Nothing measured here
describes memory growth.*** *(Code's catch.)*

⚠ **And reload is not free in a second way:** **the 1-aa fold took 13.9 s against 2.0 s for the
21-aa fold, so the ~11.7 s load is PER-INVOCATION, not amortised** — **~13% overhead across a handful
of 75–101 s folds, and the 8.7 h across 2,690.**

**⚠⚠ THE TEST THAT SETTLES IT IS BETTER THAN THE ARGUMENT AND COSTS TWO MINUTES: one fold at ~500 aa
with the model released.** **It answers the question directly and it is the first datum on the
memory-versus-length curve §4 says nobody has.**

⚠ **Until it runs, §5 is a question and must not be cited as a reason to spend or not spend.**

**⚠ A separate correction, same run.** **The `F-042` path (c) projection moved 6.95 h → 7.67 h on the
fixed worker, and that is RUN VARIANCE, NOT THE FIX** — *the squeeze fix changes shape handling for
one protein and fold time for none.* **Eight of ten folds agree within 5%; the entire +10.4% comes
from the two longest, 439 aa going 75.2 s → 101.1 s.** ⚠⚠ **Thermal state and card contention. The
honest figure is ~7–8 h, and if a ruling is sensitive to that spread it needs REPEAT RUNS, not a
better fit.** **A tighter regression on unstable measurements is precision theatre.**

> **⚠ LANDED 2026-08-22** from `docs/F-052-amendment-2-and-F-053-amendment-1.md`, AUTHORED-SHA256 `e3bc5a03…c7320` **verified on landing over the declared 4,122-byte range**; line endings converted LF→CRLF to match this file, and the pinned source left untouched. ⚠⚠ **Its central claim has since been MEASURED, and it was right:** it said the incremental's scaling was unmeasured and *"trunk attention is at least O(L²)"*. **`F-059` fits L^1.983 from ten folds already committed on 2026-08-20** — the exponent Code predicted, from data that existed when this was written. ⚠ **The two-minute test it recommends is therefore NOT owed**: the curve was already in the tree, and `F-059` §3 shows the ~500 aa fold it proposes is predicted to OOM. ⚠ **The other sub-entry in that same file — the `squeeze()` defect beneath `F-052` — is STILL UNLANDED, and is deliberately NOT cited at amendment level here: naming it would be a forward reference to nothing.** ⚠⚠ *This note first did exactly that, and the citation invariant refused it on the first run — recorded, not patched away, because it is `F-044`’s shape inside a note about an unlanded amendment.*

---

### F-052 — A convention that exists, is documented, and is obeyed by every caller except the newest one — and each test written to close it was scoped to its author's own field of view

- **Date:** 2026-08-20 · **Written by:** Code, about Code. **Status:** ⚠ **OPEN.** It closes when a
  convention in this repository is enforced by a derived check rather than by observation, or when
  the residual is named and accepted.
- **How known (`D-016`):** three instances in one session, each found by running the code in an
  environment that was not the author's. **Two failed on the production host after passing every
  local check; one was caught locally by an unrelated precondition.**

⚠ **A correction inside the entry that reports it: I described these to the owner as *"three
failures on the host."* Two were on the host. The `.gitattributes` instance was caught locally, by
the ingest's source check.** *Three of a class, two of them on the host* — recorded rather than
rounded, because the whole subject here is claims that are almost right.

---

**⚠⚠ THE SHAPE, STATED BEFORE THE INSTANCES SO THEY ARE NOT THREE ANECDOTES.**

**A rule exists. It is written down. Every existing caller obeys it. The next caller does not — and
nothing red fires, because the rule was never a check.** ⚠ **In all three the author had read the
rule; in two, the author had *written a test for it* and the test passed on the broken code.**

---

**INSTANCE 1 — `.gitattributes` scoped to a directory.** *(caught locally, by an unrelated guard)*
Full record at **`F-047 amendment 2`, member 22.** The rule protected four `docs/` files; a pinned
artifact landed under `data/`, was checked out CRLF, and stopped matching its manifest.
⚠ Caught because `scripts/census_ingest_features.py` verifies its source **before** writing.

**INSTANCE 2 — a transitive import of a module the image does not ship.** *(production host)*
```
scripts/census_ingest_features.py → core.clinical_ingest → scripts.kathad_reproduction
ModuleNotFoundError: No module named 'scripts.kathad_reproduction'
```
⚠⚠ **A test for exactly this existed and passed.** It regex-scanned the ingest's **own** imports for
`scripts.*` and found none, while its docstring promised the failure it did not check — *"would
build fine and fail at run time, on the production host."* **A one-file scan answers *does this file
import a stranger*; the question is *can it REACH one*. One level of indirection, and one level was
enough.** ⚠ **The cause was accidental coupling, not a missing file:** `core/clinical_ingest.py`
imports the Kathad helpers for the `D-100` grid, which `verify_source` never touches. **Fixed by
moving four provenance helpers into `core/source_pin.py` — stdlib only — not by shipping more.**

**INSTANCE 3 — an engine built from a raw `DATABASE_URL`.** *(production host)*
```
ModuleNotFoundError: No module named 'psycopg2'
```
`db/dburl.py`'s own docstring says *"This one helper is applied by BOTH the serving tier and the
migration environment, so a future re-attach ... cannot silently break either path again."*
⚠⚠ **Five callers obeyed it. The sixth was mine.** ⚠ **It failed AFTER every other guard passed** —
artifact hash verified, 2,690 rows loaded, outcome vocabulary checked — **because the connection is
the last thing that happens.** The guards worked; none was pointed here.

---

**⚠⚠ AND THE SECOND-ORDER FINDING, WHICH IS THE REASON THIS IS AN ENTRY AND NOT THREE FOOTNOTES.**

**Each remedy was, on its first attempt, scoped the same way the defect was.**
- **Instance 1's** first blast-radius scan required the hash on its marker's line and reported **3**
  files; deriving the set from the tree found **6**.
- **Instance 2's** test checked direct imports; the defect was transitive.
- **Instance 3's** test was written, then **reddened on correct code** — it required the normalizer
  to wrap `create_engine`'s first *argument*, a coding SHAPE, and
  `scripts/taskb_pae_inventory.py` legitimately normalises inside a helper and passes the result
  down. ⚠ *A test that reddens on correct code is worse than no test*, and that sentence had been
  written about a different guard **the same day**.

**⚠ THE FIX THAT WORKED, ALL THREE TIMES, WAS TO DERIVE THE SET RATHER THAN ENUMERATE IT** — pinned
artifacts derived from the tree; the import graph walked rather than the file scanned; every module
that builds an engine found rather than the ones remembered. **An enumerated rule protects the
members its author could see.**

**⚠ AND INSTANCE 3'S DERIVED CHECK IMMEDIATELY FOUND A FOURTH INSTANCE NOBODY WAS LOOKING FOR:**
`scripts/taskb_pae_inventory.py` had **hand-reimplemented** the normalisation inline. **It works —
which is the point.** *A second implementation of a documented single-source helper goes stale
silently, the first time the helper learns a new scheme.* ⚠ **It was fixed, not exempted:** an
exemption satisfies a test by editing the test.

---

**⚠⚠ THE CONDITION THAT HID ALL THREE, NAMED.** Every local verification ran with **the whole
repository on the path**, against a database reached the way this laptop reaches it. **The serving
image ships `app/ core/ db/ data/` and one script; production hands over a bare `postgresql://`.**
⚠ **A test environment richer than production is not a test of production**, and *"it passed
locally"* was true and worthless in all three.
**The instrument that would have caught instances 2 and 3 before the first deploy is not exotic: it
is `cp -r` of the shipped subset into a temp directory.** It exists now
(`docs/MEASUREMENT-OUTPUT-…`, the simulated layout) and it reproduced both failures.

**⚠ WHAT THIS ENTRY DOES NOT CLAIM.**
- **Not that the guards failed.** `D-058`'s stdlib pin, the artifact hash, the acceptance bar and
  the pLDDT floor all held. **Three conventions had no check at all** — that is a different fact
  from a check that missed.
- ⚠ **Not a proposal to build a framework.** `D-074` decision 3: *do not answer a finding with a
  framework that becomes a second thing to drift.* Three derived tests, each ten lines of `ast`.
- ⚠ **Not generalisable to a rate.** Three instances, one session, one author, no denominator —
  `F-047`'s survivorship caveat applies unchanged.

---

**⚠⚠ INSTANCE 4, AND IT HAPPENED INSIDE THE COMMIT THAT LANDS THIS ENTRY.**

The regression test written for instance 1 detects a pinned artifact by searching for
`AUTHORED-SHA256`. **Writing the sentence *"docs carrying `AUTHORED-SHA256`"* into this entry made
`docs/README.md` match it** — and the gate went red claiming the LOG was an unprotected pinned
artifact. **The log declares no hash over itself.** ⚠ *A detector that cannot tell a MENTION from a
DECLARATION reddens on correct files*, which is the failure instance 3's first test already made
once, the same day.

⚠ **Tightened to require the declaration form — and the tightening immediately produced the
OPPOSITE error, one edit later.** `AMENDMENT-2026-08-19-planner-log-entries.md` declares with a
**colon** (`AUTHORED-SHA256: <hash>`), which the stricter pattern missed: **a real pin, undetected.**
**Broad detector → false positive; narrow detector → false negative; two edits apart, one afternoon.**

⚠⚠ **And it exposed two files I had protected on a wrong reading.**
`ORDERS-Code-2026-08-19-clinical-edges-1-and-2.md` and
`SPEC-2026-08-19-supplier-survey-clinical-edges.md` state **in their own text** that *"no
`AUTHORED-SHA256` IS DECLARED, AND THAT IS DELIBERATE."* **They were never pinned.** The
`.gitattributes` entries stay — `-text` on an unpinned document costs nothing, and removing them
would erase the evidence — **with the misreading recorded beside them rather than tidied away.**

**⚠ What instance 4 adds: the derived check is not a solution, it is a smaller problem.** Deriving
the set removed the *enumeration* failure and left the *predicate* failure — and the predicate is
now the thing scoped to what its author can see. **This entry does not claim that is solved.**

#### F-052 amendment 1 — ⚠⚠ The strongest instance yet: two of the five uncovered surfaces were built by the author of the convention, hours after documenting it — and the guard found the fifth mid-report

- **Date:** 2026-08-20 · **Status:** `F-052` stays **OPEN.** ⚠ **Deriving the set removed the
  ENUMERATION failure and left the PREDICATE failure; the derived checks in the tree remain PARTIAL.**

---

**1 — THE MEASUREMENT.** `PA` enumerated every surface rendering HPA-derived data, **both directions**
— components back to their source, **and every HPA-sourced field forward to wherever it surfaces.**

| # | component | renders | audited before `PA`? |
|---|---|---|---|
| 1 | `ClinicalEdges` | patient counts, normal levels | ✅ `NC` |
| 2 | `CancerAssociations` | quasi H-score | ❌ named by the Planner |
| 3 | ⚠ `SurfaceCheck` | subcellular, `Reliability` (IF) | ❌ **built this session** |
| 4 | ⚠ `CensusTable` | stained %, n, critical count | ❌ **built this session** |
| 5 | ⚠⚠ `CensusDetail` | `qh_score`, inline | ❌ **found by the `PC3` guard** |

**The Planner said two was *"a floor, not a total."* It was 40% of the answer.**

**2 — ⚠⚠ TWO OF THE FIVE WERE BUILT BY THE AUTHOR OF THE CONVENTION, AFTER THE AUDIT THAT FOUND THE
GAP.** Code's own words: ***"That's `F-052` landing on me directly, not as an abstraction."***

⚠ **`F-052`'s subject is *a convention that exists, is documented, and is obeyed by every caller
except the newest one*.** **Here the newest callers were written by the person who had documented the
convention hours earlier, in the same session, while the remedy for the previous instance was still
in flight.**

⚠⚠ **That is not carelessness and recording it as carelessness would teach nothing. It is the class's
actual mechanism: a convention lives in the author's ATTENTION, not in the code, until something
enforces it — and attention does not survive a context switch, even a short one, even in the person
who wrote it down.**

**3 — ⚠⚠ THE GUARD FIRED BEFORE THE REPORT CLAIMING FOUR WAS FINISHED.**

`PC3` — *a test that fails when a new HPA-rendering surface appears uncovered* — **found
`CensusDetail` on its first run.** It renders `qh_score` **inline, in its own list, separately from
the `CancerAssociations` component it also mounts.**

⚠ ***"`NC` missed it, your count missed it, and my own enumeration stopped at the component boundary,
which is exactly the scoping failure `PC3` exists to catch."***

**This is the amendment's most useful line, and it is the difference between the previous instances
and this one:** ⚠⚠ **every earlier member of this class was caught by a person, later. This one was
caught by a structure, immediately** — **and it caught the enumeration that was being written to
close it.**

**4 — ⚠ What this changes about the remedy, and it is narrow.**

- **The enumeration alone would NOT have found the fifth.** ⚠ **A one-time census of surfaces is a
  snapshot; the defect is that the set GROWS.** **`PC3` is the part that survives the session.**
- ⚠ **The reverse direction is what found 3 and 4** — *every HPA-sourced field forward to wherever it
  surfaces*. **A forward-only enumeration reproduces the author's field of view, which is the defect.**
- ⚠⚠ **`F-052` still does NOT close.** `D-074`: **a finding against an instrument stays open until the
  instrument no longer exhibits it.** **`PC3` covers HPA-rendering surfaces and nothing else** — the
  predicate failure is unrepaired everywhere else, **and this entry is evidence the class recurs
  within hours under ordinary work.**

**5 — ⚠ Two sentences from the run worth preserving, because they stop a re-derivation.**
***"A filename is not a modality"*** — `pathology.tsv` is IHC, and the 2017 *pathology atlas of the
human cancer transcriptome* is the wrong paper despite matching the name.
***"A hyperlink to a site is not a credit"*** — the image/data credit is its own element and its own
obligation.

**6 — ⚠ And one honest test-naming defect, reported rather than tidied.** Removing the `href` reddened
the **`PD`** (`v22`) assertion rather than the link assertion, **because deleting the anchor leaves
the version filter with nothing to check.** ⚠⚠ **A correct red under the wrong name** — the
*error-red versus failure-red* distinction, applied to which test claims the catch. **Recorded as
observed.**

**Relied on by:** `F-047` · `D-093 amendment 9`.

---

**Relied on by:** ⚠ `F-021`, whose first clause is now closed by `uq_protein_features_analysis_id`
while the entry itself remains reserved-unwritten.
**Assumptions relied on:** `A-016` (any red proves the assertion bites) — twice, since two of the
three remedies were themselves proven only by a revert that reddened at the assertion.

### F-051 — ⚠⚠ "The two confidence features" is really one: `membrane_proximal_plddt` carries 32.2% of attribution and `mean_plddt_ecd` 6.4%

- **Date:** 2026-08-19 · **Status:** ⚠ **OPEN.** An observation with a pre-registered fork —
  **not a conclusion and not a reinterpretation of `F-005`.**
- **How known (`D-016`):** read-only SQL as the `pharmfold-readonly` role against `target_scores` and
  `protein_features`, **run 2, 56 targets**. ⚠ **No fit, no refit, no new ranking run.** Instruments
  committed as `scripts/fd1_recover_coefficients.py` and `scripts/fd1_attribution_share.py` — **the
  numbers are re-derivable, not quoted.**

---

**THE MEASUREMENT.** Mean share of total absolute attribution across the 56 scored targets:

| feature | share |
|---|---|
| ⚠⚠ **`membrane_proximal_plddt`** | **32.2%** |
| `largest_patch_fraction` | **24.0%** |
| `radius_of_gyration` | 16.6% |
| `ecd_length` | 12.3% |
| `sasa_normalized` | 8.5% |
| ⚠ **`mean_plddt_ecd`** | **6.4%** |
| **the confidence pair together** | **38.6%** |

**`32.2 / 6.4 = 5.03` — a factor of five between the pair.**
**Per target: median 40.8% · max 72.5% · ⚠ 11 of 56 above 50%.**

**THE RECOVERY THIS RESTS ON IS EXACT, AND IT WAS CHECKED THREE WAYS.**
- **All 56 rows lie on one line per feature — max residual `~1e-16`.** Attributions are precisely
  `coefficient × standardized feature`, as `D-041` decision 1 documents.
- ⚠⚠ **The feature↔attribution PAIRING was tested, not inherited: all 6×6 combinations, diagonal
  `~1e-16`, every off-diagonal `~1e-1`.** **A transposed index would have produced six plausible
  slopes and an entirely wrong attribution story.**
- ⚠ **The fit population is confirmed as these 56**: the `FD1`-implied means agree with means computed
  directly from `protein_features` over the same 56 to **`≤6.9e-09`.**

⚠ **The intercept fell out of the same recovery — `-1.324660466`, implied identically by all 56 rows,
spread `1.11e-15`** — so **seven parameters are known on the raw scale and fully determine the
model's predictions.** ⚠⚠ **But NOT the standardized coefficients: `sd_k` is not persisted, and
computing it over the fit set would be fitting.** See `F-049` amendment 1.

---

**WHAT THIS ADDS TO `F-005`, AND WHAT IT DOES NOT.**
`F-005` measured **`FULL 0.607 / 8-of-12`** against **`no_plddt 0.562 / 6-of-12`** — two of six
features carry the difference. ⚠⚠ **This says the work inside that pair is done almost entirely by
ONE of them, and it is the MEMBRANE-PROXIMAL one.**
⚠ **`F-005`'s result is unchanged. Its READING is what this bears on, and the reading is `P-001`'s to
settle.**

**⚠⚠ THE FORK, PRE-REGISTERED HERE SO IT IS NOT CHOSEN AFTER THE FACT.**

**A — the circularity reading.** A dominant *global* confidence feature would suggest the score partly
tracks **how PDB-like a sequence is**; the PDB is enriched for studied proteins, which is enriched for
existing drug targets. ⚠ **The same circularity that bars GPI status and `therapeutic_precedent`,
through a side door.**

**B — the informative-uncertainty reading.** A dominant *membrane-proximal* confidence feature
suggests **ESMFold is uncertain near the membrane boundary, and that uncertainty is itself
informative about the region an ADC must reach.**

⚠⚠ **THE MEASUREMENT FAVOURS B AND DOES NOT ESTABLISH IT. The dominant feature is REGIONAL, not
global — which is what A would have predicted least.** ⚠ **`D-075`'s `geom_proxy` — `membrane_proximal_sasa`, the confidence-blind measure of the same region — is the instrument that
separates them, and `F-017` records it firing at `0.6607 / 0.6324 / 8-of-12`.** **Whether that
settles the fork is a `P-001` question and is not settled here.**

---

**⚠⚠ WHAT THIS ENTRY DOES NOT CLAIM. THE FIRST IS LOAD-BEARING.**
- ⚠⚠ **ATTRIBUTION SHARE IS NOT VARIANCE EXPLAINED.** The features are correlated — `D-075` records
  feature 7 against pLDDT at **Pearson −0.49, Spearman −0.55** — and the share decomposes **one linear
  predictor**, not causal contribution. **A 32.2% share is not a 32.2% causal role.** *(Code's
  caution, adopted verbatim.)*
- ⚠ **Not that `mean_plddt_ecd` is useless.** A small share in a correlated set is evidence about
  **this decomposition on these 56 targets**, not about no contribution.
- ⚠ **Not a proposal to change `FEATURE_NAMES`.** `D-027`'s six IS the pre-registration, the gate
  asserts `len == 6`, and **a feature dropped because its share looked small is a post-hoc model
  change** — what `D-041`'s pre-registration exists to prevent.
- ⚠ **Not generalisable past the cohort.** 56 targets, 12 labelled positives, an
  **expression-selected** cohort — `A-014` and `F-011` both apply to the label side.
- ⚠⚠ **Not a statement about the census.** No census row is scored (`D-089`), **and no census row
  carries a feature row at all** — 0 of 2,690.

**Assumptions relied on:** `A-014` — the cohort's labels descend from an expression screen.
**Relied on by:** ⚠ `P-001`, which must state the confidence dependence rather than let a reviewer
find it — **and which now has a sharper thing to state than *"two of six features are confidence."***

### F-049 — `scorer_version` establishes that two runs used the same CODE, never that they used the same PARAMETERS — and nothing persisted makes `D-041`'s reproducibility claim checkable

- **Date:** 2026-08-19
- **Status:** ⚠ **OPEN — a finding against an instrument (`D-074`).** It closes when two runs cannot be presented as comparable on the strength of a matching version string, **or** when the residual is named and accepted in the open. ⚠ **Naming what would have to be persisted is not persisting it** — `D-074` decision 3, and this entry deliberately stops at the naming.

- **The finding.** `ranking_runs.scorer_version` is a **code** version. It says the same source produced both runs. ⚠⚠ **It says nothing about the seven numbers the model actually is**, and two runs of identical code on different inputs have different parameters by construction.

- **⚠ The evidence is already in the log and is not an argument.** `F-005` records the two `D-065` ablations:

  | run | id | feature set | parameters | `scorer_version` |
  |---|---|---|---|---|
  | `no_plddt` | 3 | features 1, 2, 5, 6 | **5** | `a927dc4532b7` |
  | `plddt_only` | 4 | features 3, 4 | **3** | `a927dc4532b7` |

  **Same string. Different parameter counts. Already shipped.** ⚠ Not a hypothetical collision — *the version string was already carrying two different models on the day it was introduced.*

- **⚠⚠ The consequence, and it reaches the surface.** `/api/ranking` filters `valid ∧ run_kind='preregistered'` and **the version travels with the rows**. So a reader — or a later query — comparing two runs on a matching `scorer_version` is comparing *nothing that was checked*. **`run_kind` is what actually separates the pre-registered run from the ablations; `scorer_version` looks like it does the same job and does not.** *A field that appears to identify a model and identifies a checkout.*

- **⚠ What `ranking_runs` actually persists**, read from `db/models.py` rather than assumed:

  ```
  id · target_list_version · scorer_version · run_kind · created_at
  ```

  **No coefficients. No standardizer mean or sd. No λ.** Per target, `target_scores` carries `score`, `rank` and the six `β_k·x_k` `attributions`; `ranking_results` carries the LOO distribution.

- **⚠⚠ SO `D-041` CLAIMS THE FIT IS REPRODUCIBLE AND NOTHING STORED MAKES THAT CHECKABLE.** The parameters of a **pre-registered** run cannot be recovered from the record. **This is `F-045`'s shape at the level of a result rather than an instrument:** *the record says what was done and not enough to redo it.* ⚠ The claim may well be true — this is not evidence that it is false — **but it is unfalsifiable from the record, and an unfalsifiable reproducibility claim is a belief with a decision number.**

- **What would have to be persisted for `FB3` to be answerable without fitting.** ⚠ **Named, not built:**
  1. the **seven parameters** — six coefficients on standardized features plus the intercept;
  2. the standardizer's **per-feature mean and sd**, without which a standardized coefficient cannot be reconstructed from anything;
  3. the **selected λ**, since a 13-point grid chosen by inner CV is part of what produced them.

  ⚠ **Item 2 is the one that bites.** The per-feature attributions *are* persisted, so `attribution_k(i) = coef_k · x̂_k(i)` and the **raw-scale** slope `coef_k / sd_k` is recoverable from persisted values. **The standardized coefficient — which `D-041` decision 1 makes the attribution basis — is not**, and recovering `sd_k` by computing it over the fit set would be **reconstructing the standardizer, which is fitting.**

- **⚠ What this does NOT claim.**
  1. **Not that any run is wrong.** `F-004`'s and `F-005`'s reported numbers stand; this is about what can be *rechecked*, not about what was computed.
  2. **Not that `scorer_version` is useless.** It correctly detects that the code changed. ⚠ It is precise about one thing and blind to its neighbour — **`F-044`'s exact shape, in a database column rather than in a citation.**
  3. **No remedy is adopted here.** Persisting parameters is a schema change with its own entry, and `D-074` decision 3 warns against answering a finding with a framework.

- **⚠ How it was found.** Not by review and not by a test. The Planner asked whether `FD1` could be answered from persisted values instead of a refit; checking the model to answer that question surfaced what the model does **not** hold. *The question was about arithmetic and the answer was about the record.*


#### F-049 amendment 1 — ⚠⚠ The entry was too broad. The MODEL is recoverable from persisted values; the STANDARDIZED coefficients are not, and only the second half survives

- **Date:** 2026-08-19 · **Status:** `F-049` stays **OPEN**, on a **narrower** claim. ⚠ **Written the same day as the entry it corrects, because the measurement that refutes half of it was run hours later.**

- **What the entry said.** *"`D-041` claims the fit is reproducible and NOTHING STORED MAKES THAT CHECKABLE … the record says what was done and not enough to redo it."* ⚠⚠ **The second clause is wrong as written, and the measurement is not close.**

- **What was actually recovered**, from persisted values only, by exact linear solve — **a reproduction, not a fit** (`GE4`):

  `attribution_k(i) = coef_k · x̂_k(i) = coef_k · (x_k(i) − mean_k) / sd_k`

  is exactly linear in the raw feature, so across the 56 scored rows at `ranking_run_id = 2`:

  | k | feature | raw-scale coefficient `coef_k / sd_k` | implied `mean_k` |
  |---|---|---|---|
  | 0 | `ecd_length` | **+0.0001536014218** | 413.26786 |
  | 1 | `radius_of_gyration` | **−0.4576446602** | 0.15600094 |
  | 2 | `mean_plddt_ecd` | **+0.003082622556** | 69.002672 |
  | 3 | `membrane_proximal_plddt` | **+0.01459632517** | 66.002025 |
  | 4 | `sasa_normalized` | **−0.001590501602** | 71.020666 |
  | 5 | `largest_patch_fraction` | **−0.3924876377** | 0.73453592 |

  **And the intercept, which `GE` did not anticipate: `−1.324660466`**, implied identically by all 56 rows (spread `1.11e-15`).

  ⚠⚠ **So SEVEN parameters are known on the raw scale, and they fully determine the model's predictions.** *A model whose predictions can be reproduced exactly is reproducible in the sense that matters to a reader checking a result.*

- **⚠ `GE2`'s self-check, which was the point rather than the coefficients.** Max residual per feature: `5.6e-17 · 3.5e-17 · 4.9e-17 · 3.9e-16 · 9.7e-17 · 5.6e-17` — float noise. **Every one of the 56 rows lies on the same line, for all six features.** No drift, no non-determinism, and **`attributions` are exactly what `D-041` decision 1 documents them to be.** ⚠ *The instrument was checked and it passed; the finding is that the entry overstated what the check would show.*

- **⚠ The pairing was TESTED, not assumed.** All 6 × 6 combinations of attribution index against feature column were fitted: the diagonal returns ~`1e-16`, every off-diagonal ~`1e-1`. **The documented ordering is confirmed by measurement rather than inherited from a comment.**

- **What survives, and it is the sharper half.** ⚠⚠ **`sd_k` is not persisted, so `coef_k` and `sd_k` remain entangled — only their ratio is determined.** The **standardized** coefficients, which `D-041` decision 1 makes the **attribution basis for comparing features against each other**, cannot be recovered. Computing `sd` over the fit set would reconstruct the standardizer, which is fitting and is barred.
  - ⚠ **Signs DO survive**, since `sd_k > 0`: `ecd_length` **+** · `radius_of_gyration` **−** · `mean_plddt_ecd` **+** · `membrane_proximal_plddt` **+** · `sasa_normalized` **−** · `largest_patch_fraction` **−**.
  - **So `FB3` — *are run 2's coefficients still reproducible today* — remains unanswerable without fitting**, and that was the entry's real subject.

- **⚠⚠ AND A SEPARATE FINDING THE RECOVERY EXPOSED: "the two pLDDT features" is one feature.** Read straight off the persisted attributions, no coefficients needed:

  | feature | mean \|attribution\| | share |
  |---|---|---|
  | `membrane_proximal_plddt` | 0.101982 | **32.2%** |
  | `largest_patch_fraction` | 0.075954 | 24.0% |
  | `radius_of_gyration` | 0.052473 | 16.6% |
  | `ecd_length` | 0.038851 | 12.3% |
  | `sasa_normalized` | 0.026843 | 8.5% |
  | ⚠ `mean_plddt_ecd` | 0.020237 | **6.4%** |

  **The two confidence features carry 38.6% of total attribution magnitude — but `membrane_proximal_plddt` alone is 32.2% and `mean_plddt_ecd` is 6.4%, a factor of five.** ⚠ `F-005` reports `plddt_only` (both confidence features, three parameters) matching the full model; **this says the work inside that pair is done almost entirely by ONE of them.** Per target: median **40.8%**, max **72.5%**, and **11 of 56 targets have pLDDT carrying over half** their attribution.
  - ⚠ **Stated as an observation, not a conclusion.** Attribution magnitude is not importance, and `D-041` decision 1 makes `β·x` the attribution basis without making it a ranking of features. **Whether this reopens `F-005`'s reading is the Planner's.**

- **Why the entry was too broad.** It was written from `db/models.py` — *what the schema stores* — and concluded about *what can be recovered*. ⚠⚠ **Those are different questions, and the second needs the data, not the schema.** *Reasoning from the shape of the record to the limits of the record, without querying it.*

---

#### F-049 amendment 2 — ⚠⚠ Two more instances, both closed on the surface — and one was a claim that stayed TRUE ONLY BY A NAMING RULE

- **Date:** 2026-08-19 · **Status:** `F-049` stays **OPEN.** ⚠ Its closure condition is about
  `scorer_version` — *two runs cannot be presented as comparable on the strength of a matching
  version string* — and neither instance below touches that. **These are members of the family,
  not the finding.**

---

**INSTANCE 3 — `ranked` meant two populations on two live endpoints. CLOSED IN THE PAYLOAD.**

`/api/coverage` reported `ranked = 67`; `/api/ranking` reported `n_ranking_set = 56`. Both correct,
eleven rows apart, **and neither payload said which population it counted.**

⚠ **A CORRECTION FIRST, BECAUSE I REPORTED THIS WRONG.** I told the owner there was *"no statement
anywhere of which population either describes."* **That is false for the UI**: `D-066` decision 2
already renders *"67 ranked · 56 rankable after the pLDDT-50 floor"* beside the scorer table, and it
was verified live in the deployed bundle. **The defect was the JSON only** — for a consumer that
never renders the page. *I repeated an order's wording without checking the surface.*

**Closed by `population_key` on both routes**: each number names its kind and points **by name and
by route** at the number it is not. Every partition cell is keyed, not only `ranked` — *a rule
applied to one cell and not the others is not a rule.*

⚠⚠ **AND THE GUARD WAS DEFEATED TWICE BY MY OWN REVERT PROOF BEFORE IT HELD.**
- **Attempt 1, a token scan.** Rewriting `n_ranking_set`'s description as a *disposition*
  description while keeping every required token (`plddt`, `floor`, `coverage.ranked`,
  `/api/coverage`) left **all six tests green.** *A token scan pins that words are PRESENT, never
  that the sentence MEANS what it should*, and keyword-stuffing walks straight through it.
- **Attempt 2, a prose ban — which reddened on CORRECT code.** Asserting `"MANIFEST DISPOSITION"`
  absent from `n_ranking_set` matched the legitimate **disclaimer**, *"it is NOT `coverage.ranked`,
  which is the manifest disposition."* ⚠ **Prose cannot distinguish *I am one* from *that other one
  is one*.**
- **What held: the KIND became STRUCTURED DATA.** `kind` is the claim, `text` is for the human.
  ⚠⚠ **When a test must check what a string MEANS, the meaning belongs in a field, not in the
  string.** That generalises past this payload and is the reusable part of this amendment.

---

**INSTANCE 4 — ⚠⚠ A PAGE ASSERTED THE ABSENCE OF A THING THAT WAS ABOUT TO EXIST, AND WOULD HAVE
STAYED "TRUE" BY DEFINITION.**

`/census` said *"None of these proteins has been scored or ranked."* **True when written**: no model
output existed for any census protein. The structural profile (`D-079` amendment 1, ruled by
amendment 2) put the pre-registered model's output one click away, on `/census/:id`.

⚠ **Every literal clause still held** — measured before touching anything: census `target_scores`
**0**, feature rows bound to a ranking run **0**, default order accession, no score column.
⚠⚠ **The sentence would nonetheless have been true only because ruling 1 decided to call the output
something other than a score.** *A claim that survives on what we decided to call something is not
the claim the reader is reading.*

**This is `F-049`'s family INVERTED.** The parent entry is *one word meaning two things*. This is
**one thing carrying two words — and a page asserting the absence of one of them.**

⚠ **The page's own justification had already gone false and nobody re-read it:** `CensusView`'s
header comment read *"there is no score column, **because there is no score**."* There is no score
COLUMN; there **is** a model output. **Corrected in place, the old wording kept visible.**

**Closed by disclosure rather than by deletion**: both true clauses stay, and the sentence now names
the profile, calls it *a measurement, not a verdict*, and states that **no protein is ordered by
it.** Six tests pin the disclosure to the **same sentence** — *a disclosure three sections down is a
different claim from a qualified one* — and one asserts **no `0.xxxx` figure appears in any table
row**, so the disclosure cannot become the feature.

⚠ **It never shipped false.** The branch was unmerged when the owner asked whether the claim was
still true. **The defect was scheduled, not shipped, and it was caught by re-reading a sentence
against a changed world rather than by any test.**

---

**⚠ WHAT THE TWO INSTANCES ADD TO THE FAMILY.**
**Instance 3 is a word that acquired a second meaning. Instance 4 is a claim that kept its meaning
while the world moved under it.** ⚠⚠ **The second is harder, because nothing about the sentence
changes when it goes wrong** — there is no diff, no failing test, and no moment at which anyone
edits the false thing into place. **What caught it was a person re-reading a claim they already
believed.**

**Relied on by:** `D-079 amendment 3` · `F-052`.

---

### F-047 — ⚠ The wrong-but-plausible answer: the defect class where nothing errors, nothing is malformed, and the number is wrong

- **Date:** 2026-08-19 · **Status:** ⚠ **OPEN and STANDING.** It accumulates members; it does not close.

- **The shape.** A query, a guard, a grep or a report returns a **well-formed, correctly-typed, plausibly-sized answer that is wrong** — and **nothing objects.** ⚠ **This is not an error class. Errors announce themselves. This class is defined by its silence**, and it is `F-011`'s *plausibility, not error, is the failure mode at scale* applied to the instruments rather than to the data.

- ⚠ **Already doctrine, and the entry cites rather than re-derives it.** **KEEL-1 V9 Principle 8's fifth clause** names it: *"be most suspicious of the well-formed answer: an empty result from a mismatched key, a zero from a stale connection, a 405 read as a 404. In every one of those the wrong answer arrives correctly formatted, and nothing objects."* ⚠⚠ **Three of that clause's examples are this project's own scars.**

- **The members, and THREE OF SIX ARE PLANNER-MADE. That is the point of the entry.**

  1. ⚠⚠ **The `50` that should have been `58`** *(Planner, 2026-08-19)*. The ruling on the engulfing category **quoted a count measured under the strict-both convention while simultaneously ruling the at-or-before / at-or-after convention.** 4 features sit flush at `s0`, 4 flush at `s1`; **those 8 are exactly what the convention moves.** ⚠ **The hazard fired inside the order that commissioned the check for it** — the same order wrote *"which side it falls on is a choice, not a fact."*
  2. ⚠⚠ **The `## P-004` grep** *(Planner, 2026-08-19)*. Written as a guard against a **false collision** (`P-00[0-9]` returns `DEP-004`/`DEP-005`), it **manufactures a false absence**: P-003 and P-004 carry `⟡`, so their headings are `## ⟡ P-003 —` and `^## P-00` **excludes exactly the two entries the check is about.** The result reads *P-003 is cited with no entry* — clean, confident, false. **Committed in `docs/PREWORK-2026-08-19.md` §2b; corrected by a landing note beside it, the instruction not edited.** ⚠ **Code's own record of the catch: *luck of ordering, not a control.***
  3. ⚠⚠ **`COMMITTED to docs/ as provenance`, false on four documents** *(Planner, 2026-08-19)*. Four `ORDERS-Code-2026-08-19*` files each assert their own provenance in their header and **none was in the repository.** ⚠ **A document asserting its own provenance cannot be falsified from inside itself** — the sharpest member of the pointer-is-not-proof family. **Cause: paste to Code and commit to repo are two acts, and the header claimed the second because the first had happened.** **Remedy, structural rather than documentary:** the author writes **`TO BE COMMITTED`**, and the landing header — received time, `sha256` as received, and the note that only the header differs — **is stamped by whoever lands it**, on the `ORDERS-Code-2026-08-18-tranche-6-premeasurement.md` precedent. **The author no longer makes the claim, so the author cannot make it falsely.**
  4. **The `−18 / +4 / −39 / −2` byte deltas** *(Code, self-caught)*. Four true numbers offered as evidence that the re-verification covered the `.pyc` collision. ⚠ **They describe a different driver, in a different file, at different sizes** — the colliding pair was `a < s0 → a <= s0` and `b < s0 → b <= s0`, both **`+1`**. ⚠⚠ *A clean number meaning something other than it appears to, inside the report of a finding about exactly that.* **See `F-045`.**
  5. **The sum-to-sum partition check** *(Code, self-caught)*. A partition validated by comparing its total to itself — **a tautology that could not fail.** ⚠ **A partition that checks only its total is not checked.** Replaced by a per-cause reconciliation: **2,033 + 215 + 21 + 58 + 0 = 2,327**, and **2,327 + 1,140 = 3,467.**
  6. **The prior catalogue** (`PREWORK-2026-08-19` §3): a **case-mismatched join returning a clean zero three times** · a **`Staged` secret answering `0` rows** where a restart does not apply it · a **`405` read as a `404`** · **five wrong files in one day, every one real, well-formed, correctly-schema'd data from the right organisation.**

- ⚠⚠ **THE DENOMINATOR IS UNKNOWN AND THIS ENTRY MUST NEVER REPORT A RATE.** Every member above was **caught**. An instance that was never caught leaves no trace by construction — that is the definition of the class. **This is survivorship and must be labelled as such wherever it appears**, exactly as `KEEL-4 V9` §6 requires of the assumption score. **What six members do establish, with no denominator: when this project went looking, it found them. Enough to justify the instrument, and not enough to justify a percentage.**

- **What actually catches this class, from the members rather than from theory:**
  - ⚠ **A declared length beat a checksum.** Two passages arrived with corrupted `sha256` values; the **stated byte counts** (149 → 120, 289 → 259) caught the corruption the hashes could not.
  - **Reconcile both directions and per-cause, never total-to-total.**
  - **Reproduce a known-good subset** — `D-100`'s 337/337 and 1,303/1,303, `M4`'s six reported **as accessions rather than as a count.**
  - ⚠ **Make the check able to fail on the corpus it runs against.** `F-046`'s invisible inequality and `F-045`'s self-check that fails when the disagreeing-span count is zero are the same move.

- **Relied on by:** `F-044` · `F-045` · `F-046` · `F-048` · `D-095 amendment 1`.

- ⚠ **LANDED BY CODE, 2026-08-19.** Verbatim from `docs/AMENDMENT-2026-08-19-planner-log-entries.md`, which releases this number from `docs/RESERVED.md`. ⚠⚠ **One member of this entry bit the landing of this entry.** Member 3's remedy — *`sha256` as received, stamped by whoever lands it* — **assumes a file changes hands.** This document arrived as **chat text, not as a file**, so **no received-artefact hash exists to record**, and the hash in the landing header is of **Code's transcription**, which is a strictly weaker claim: it proves what was landed, not that it matches what was sent. **The remedy is sound and its precondition was not met. Recorded rather than papered over.**


#### F-047 amendment 1 — ⚠⚠ Eight more members in one day, ELEVEN of twenty-one now Planner-made — and the catch rate, not the count, is the finding

- **Date:** 2026-08-19 · **Status:** `F-047` stays **OPEN and STANDING.** It accumulates; it does not
  close.

⚠ **Why an amendment rather than a rewrite:** the original entry's six members stand unchanged. **A
class entry that is edited to look tidier loses the thing that makes it evidence — that the members
arrived one at a time, in the course of ordinary work, and that most were caught by someone other
than their author.**

---

**14 — ⚠ The Planner asked a question the log had answered three weeks earlier.** *(Planner)*
It opened a scoring discussion asking whether the fitted scores are calibrated probabilities or an
ordering. **`F-006` (2026-07-29) already ruled: *the fitted scores are compressed toward the base
rate, and are not calibrated probabilities* — min 0.116, median 0.220, max 0.285, n 56.** ⚠ **Not a
wrong answer: a confident question built on `D-041` and `core/features.py` with no search of the
findings.** **Same root as the rest of the class — reasoning from a partial read that produced
something well-formed.**

**15 — ⚠⚠ `core.autocrlf=true` would have broken every authored hash on a fresh clone.** *(Code,
caught BEFORE it fired)*
Git rewrites LF→CRLF on checkout, so a clone's bytes differ from the commit's and **the verification
guard would have reported corruption on files nothing had touched** — ⚠ **a guard manufacturing its
own failure signal, indistinguishable from the channel corruption it was built to detect. We would
have chased the channel.** **No `.gitattributes` existed; one was added, scoped to the four files,
and proven by round-tripping each through git's own checkout filter.**
⚠ **The only member so far caught before producing a wrong answer rather than after.**

**16 — ⚠⚠ An order cited an artifact in the present tense before it existed.** *(Planner)*
`ORDERS-Code-cancer-surface-attribution.md` §0 stated the licence text *"is landing as
`docs/HPA-licence-2026-08-19-as-read.md`."* **It was not in the repository and had never been
created**, so **`D-093` amendment 3's entire licence finding cited an artifact that did not exist.**
⚠ *A commit message naming a decision is not evidence the decision was logged* — **and this is its
sibling: an order naming an artifact is not evidence the artifact was created.** **Closed by landing
the file with its verbatim region hashed.**

**17 — ⚠ The Planner criticised a leak that a decision had already prevented.** *(Planner)*
It argued the scorer is *"fitted on tens of targets and applied to 2,690 census rows."*
⚠⚠ **No census row is scored. All 2,690 carry `scored=False`**, because `D-089` rules *a page per
census protein, deliberately without a scorer panel.* **The premise was false and the snapshot could
have said so.** ⚠ **It points the good way: the risk was foreclosed three weeks earlier by a decision
nobody re-read.**

**18 — ⚠⚠ A hash range whose markers appeared twice hashed ZERO BYTES.** *(Code)*
The header describing the range contained the range markers, so a plain `index()` matched the
header's copy and the region resolved empty. **A valid `sha256` of nothing — and it would have
matched itself forever.** ⚠ **Anchored to line starts.** ⚠⚠ **Second occurrence in one day of a
marker line containing its own marker**, and **the argument for a declared BYTE COUNT beside every
hash: a stated length caught a corruption that two truncated checksums could not.**

**19 — ⚠⚠ A correction that inverted the control it was correcting.** *(Planner)*
Having under-delegated a production write, the Planner *corrected* itself by instructing the owner to
hand-run an Alembic migration — ⚠ **precisely the operation KEEL step 16 exists to stop a human
performing.** *Hand-deploy dies; manual = emergencies only.* **It proposed making the owner the tired
person at the terminal that branch protection was built against.**

**20 — ⚠⚠ And the correction to THAT was also uninformed.** *(Planner)*
The log had already ruled both halves: ***"Phase 1 — the initial migration is run BY HAND,
supervised, BEFORE the first deploy"***, and phase 2, ***"a `release_command` … ruled but wired AFTER
phase 1 succeeds."*** ⚠⚠ **The Planner was right, then wrong, then right again, and had read the entry
at no point.** **Both moves were made from doctrine rather than from the log**, and the second
happened to land where the log already was. ⚠ *Arriving at the correct place by accident is not the
same as knowing it*, and the accident is what this member records.

**21 — ⚠⚠ A privilege sweep proved a role safe against the wrong database.** *(Code)*
`fly mpg connect` with no `--database` lands in `fly-db`, holding Fly's sample tables — `countries`,
`metrics`, `timeseries`, `update_logs`. **The first sweep ran there and returned a clean,
well-formed, entirely correct answer about the wrong object.** ⚠ **Had the `TRUNCATE` proof run
there, it would have "proven" the reader safe against a database that is not ours.**
⚠⚠ **Caught by reading the table names. No check caught it; looking did.**
**Standing rule adopted: `--database` is ALWAYS EXPLICIT, never defaulted** — ⚠ *a dial with a
default that does not announce itself*, the same defect the missing-`straddle` `TypeError` closed.

---

**⚠⚠ THE COUNT IS NOT THE FINDING. THE CATCH RATE IS.**

**Twenty-one members; eleven Planner-made.** ⚠ **An entry in this family listing only the Builder's
instances would be a false reading of the record — and one listing only the Planner's would be a
different false reading.** **Members 15, 18 and 21 are Code's, all three self-caught, and 15 is the
only member in the entry caught before it produced a wrong answer at all.**

⚠⚠ **AND THE DENOMINATOR REMAINS UNKNOWN. THIS ENTRY STILL REPORTS NO RATE.** Every member was
**caught**; an uncaught instance leaves no trace **by construction**, which is the definition of the
class. **Survivorship, labelled as such, exactly as `KEEL-4` V9 §6 requires of the assumption score.**
**What twenty-one members establish, with no denominator: when this project goes looking, it finds
them. Enough to justify the instrument, not enough to justify a percentage.**

**⚠ What the day's members add to *what catches this class*, from the members rather than from
theory:**
- ⚠⚠ **A control case in every proof.** Three write verbs refusing looks identical to a role that
  refuses everything — **two `SELECT`s returning 2,771 is what made the refusal a measurement.**
- ⚠ **Name the target explicitly; never accept a default.** Member 21, and the `straddle` `TypeError`.
- ⚠ **A declared byte count beside every hash.** Members 18 and the truncated checksums.
- ⚠⚠ **Read the log before correcting from doctrine.** Members 14, 17 and 20 — **three in one day,
  all Planner, all preventable by one search.**

**Relied on by:** `F-044` · `F-045` · `F-046` · `F-048` · `F-049` · `D-093 amendment 2` ·
`D-093 amendment 3`.

#### F-047 amendment 2 — ⚠⚠ Member 15 RECURRED, on a data artifact, and was caught by an unrelated ingest's source check rather than by anything watching for it

- **Date:** 2026-08-20 · **Status:** `F-047` stays **OPEN and STANDING.** It accumulates; it does
  not close.

⚠ **One member, landed on its own rather than held for a batch.** `F-047 amendment 1` recorded eight
at once because they arrived in one day. **Holding this one until a second appears would make the
entry a summary of a session rather than a record of an event** — and member 15's whole point was
that it was caught *before* it fired. This one fired.

---

**22 — ⚠⚠ `core.autocrlf` broke a hash-pinned artifact after the guard against it already existed.**
*(Code, caught by an unrelated instrument)*

**Member 15 is the parent and it reads: *"`core.autocrlf=true` would have broken every authored hash
on a fresh clone"* — caught before it fired, closed by adding `.gitattributes`, scoped to the four
`docs/` files that existed that day.** ⚠ **The scoping is the defect.** When
`data/census/census_features.v1.jsonl` landed — committed LF, blob intact, **matching its manifest
inside git** — the checkout filter handed back 2,690 CRLF lines and a `sha256` of `0a17cab2…`
against a pinned `c08f9f1d…`. **Nothing had touched the file.**

⚠ **What caught it was not a guard aimed at this.** `scripts/census_ingest_features.py` verifies its
source before writing, and the *first thing the ingest did was refuse the ingest*. **No test, no
review and no checklist was watching the artifact; an unrelated precondition happened to look.**

⚠⚠ **AND THE FIRST MEASUREMENT OF THE BLAST RADIUS WAS ITSELF TOO NARROW.** A scan requiring the
`sha256` on the same line as its marker reported **3** affected files. The regression test derives
the pinned set from the tree instead — *docs carrying `AUTHORED-SHA256`, plus any artifact named as
a manifest's `output`* — and found **3 more** that wrap the hash across lines. **Ten files, not
four, not three.** ⚠ *The remedy had been scoped to what the detector happened to see, one level up
from the original defect scoping the rule to the directory that happened to exist.*

**Closed as a class, not as an instance:** `tests/test_hash_pinned_artifacts_are_protected.py`
derives the set rather than listing it, so the next pinned artifact is covered without anyone
remembering to widen anything. ⚠ **Three assertions, because the declaration and the bytes are
different claims:** marked `-text`, **not CRLF on disk**, and *the census artifact still hashes to
its own manifest*. **A `.gitattributes` entry added without re-checking-out the file reads as a fix
while the bytes stay wrong.**

⚠ **What this adds to *what catches this class*:** **a rule written against today's members is a
rule against today's members.** Members 15 and 22 are the same defect at two scopes — the second
made possible by the first's remedy being enumerated rather than derived. **`F-052` records this as
one of three instances in a single session and is the entry that generalises it.**

**Relied on by:** `F-052`.

---

#### F-047 amendment 3 — ⚠⚠ A cause INVENTED from an absence, a test whose TITLE argued for the defect, and a Planner debt recorded twice against the wrong party

- **Date:** 2026-08-21 · **Status:** `F-047` stays **OPEN and STANDING.**

**⚠⚠ MEMBER — THE INVENTED CAUSE, AND THE MECHANISM IS NEW TO THIS ENTRY.** *(Code, self-caught.)*
**`rankCause` inferred `below_floor` from the ABSENCE of a rank.** ⚠ **It labelled a fold of
`mean_plddt` 77.26 *"excluded by the pre-registered floor of 50."***

- ⚠⚠ **This is not a missing category. It is an INVENTED one — a false statement about a good fold,
  assembled from correct components.** ***It quoted a real threshold from a real decision, so it
  would survive review by anyone who knew `D-060` existed.***
- ⚠⚠ **And the failure at scale is not the same defect 82 times.** ***It is ONE ABSENT FACT becoming
  82 INDIVIDUAL ACCUSATIONS, each pointing at a different protein.*** **A page that could not reach
  `/api/ranking` would have rendered 82 rows each accusing itself of failing a floor it passed.**
- **Repaired: it tests against the floor, and an unserved ranking is ONE shared cause.**
  ⚠ **The empty-ranking fixture is the guard — the corpus cannot produce an unserved ranking, so only
  a deliberate fixture reaches it** (`F-046`). ⚠⚠ **That fixture existed BY ACCIDENT: the sort suite
  simply had no ranking data. It is deliberate now.**

**⚠⚠ MEMBER — A TEST WHOSE TITLE ARGUED FOR THE DEFECT.** *(Code, self-caught.)*
**`TargetList.sort.test.jsx` was titled *"default order is unchanged (the ceiling-at-a-glance story
depends on it)"* and pinned pLDDT descending.**

- ⚠ **The second test this week found asserting a defect, after `App.test.jsx` pinned
  `/folded targets/i`.** ⚠⚠ **But this one is worse: `App.test.jsx` merely PINNED copy; this title is
  a RATIONALE a reviewer would accept without checking whether the story was still true.**
- ⚠⚠ **And the reader defect beneath it: it read the first `td`, which is now Rank, so every ordering
  assertion had been comparing FOUR IDENTICAL CAUSE STRINGS.** **Passing forever, on constants.**

**⚠⚠ MEMBER — THE PLANNER RECORDED A DEBT TWICE AGAINST THE WRONG PARTY.** *(Planner.)*
**`ORDERS-Code-2026-08-19f-ADDENDUM-viewer-defect.md` was written, hashed, presented — and NEVER
LANDED.** `git log --all --diff-filter=A` returns nothing for that path.

- ⚠⚠ **`BF1`–`BF4` were never in front of Code as text. The task was INVISIBLE, not declined.**
- ⚠ **The Planner recorded it twice as an open item HELD BY CODE** — in `CLOSEOUT-2026-08-19` and in
  `PREWORK-2026-08-20`'s holder table — **and used it as the example justifying that table's
  existence.** ⚠⚠ **The holder column was right; the holder was wrong.**
- **`F-047`'s class exactly: a specific, plausible, checkable attribution that was false**, and
  ⚠ **it survived five days because nobody asked the question the column was built to prompt.**

**⚠ And what `BF1` did establish once asked:** `/assets/3Dmol-MBA9E7yK.js` → **200,
`application/javascript`, 588,119 bytes**; ⚠⚠ **and the CONTROL is what earns it — a genuinely absent
asset returns 404/`application/json`, so there is no SPA fallback under `/assets/` at all**, ruling
out the classic cause by measurement rather than inspection. ⚠ **Whether the fault was ever delivery
remains unknown, because the text describing it no longer exists.**

#### F-047 amendment 4 — ⚠⚠ Three more, and all three are a check that PASSED while being wrong

- **Date:** 2026-08-21 · **Status:** `F-047` stays **OPEN and STANDING.**

**⚠⚠ MEMBER — AN INVISIBLE BYTE INVERTED A GUARD.** *(Code, self-caught.)* **`\b` escapes became
literal BACKSPACE bytes through a Python heredoc** — the regex was `/‹BS›import…/`. **Three of them,
two inside `UB3`.**
⚠⚠ ***`UB3` was green BECAUSE it was broken:*** **a regex containing an unmatchable byte returns `[]`,
and the *"no bad matches"* assertion passed.** ⚠ **Only `cat -A` showed it — the Read tool renders it
as nothing at all.**
⚠⚠ **Sixth string-mangling instance this week and the FIRST where the damage was an absence of a
rendered character rather than a visible corruption.** **Every prior one announced itself as garbage;
this one announced itself as correct.**
**⚠ The durable line: a check whose expected-empty result is ALSO its failure mode cannot distinguish
*nothing wrong* from *nothing looked at*.** **The remedy is a positive control — assert the pattern
matches something it should.**

**⚠⚠ MEMBER — A TEST ASSERTED THE RIGHT STRING AGAINST A PAGE SHOWING SOMETHING ELSE.** *(Code,
self-caught.)* **`text-transform: uppercase` renders `IMAGE/DATA CREDIT:`; `textContent` IGNORES CSS
transforms; so the existing assertion on `/Image\/data credit:/` PASSED against an uppercased page.**
⚠ **Second time this week a test was green about text the reader never saw.** **The new test reads
the stylesheet.** ⚠⚠ ***`textContent` is not what the reader reads.***

**⚠ MEMBER — THE PLANNER FLATTENED A DISTINCTION THE ENTRY ALREADY DREW.** *(Planner.)* **The order
said *"the four elements, PER DATUM."*** ⚠⚠ **`D-093 amendment 3` item 3 does not say that** — the
GENERAL case is two page-level obligations and the SPECIFIC case adds two more, **of which only the
DIRECT URL is per-datum.** **Code built what the order said: four full blocks on 79% of census cards,
zero on the rest, no middle case.**
⚠⚠ **And the de-duplication that looked obvious would have breached the licence: the four blocks
differ in exactly one field, and 75 of 79 cards carry THREE DISTINCT DEEP LINKS.** ***"Keep the first
and drop the rest" would have thrown away two working per-datum links*** — **the one element the
licence describes per-datum.**
⚠ **Suppression was the larger half: ~172 of 316 blocks carried attribution for no rendered value** —
`cancer_assoc` **78 of 79**, `surface_check` 51, `clin_normal` 39, `clin_tumour` 4. ⚠⚠ **More than
half the attribution on the surface was attached to nothing, which is citation inflation: a reader
cannot tell which citations are load-bearing.**

**⚠ AND A METHOD CORRECTION WORTH THE SPACE.** *(Code, self-caught.)* **A first pass at the
empty-block counts GUESSED the payload keys — `rows`/`tumour`/`normal` against the real
`hits`/`tumours`/`normal_tissues` — and returned a suspiciously uniform 79/79 for all three.**
⚠⚠ **A wrong key returning a clean, uniform, plausible answer, caught because the uniformity was too
good rather than by any check.** ***A result that is suspiciously tidy is evidence about the query,
not about the data.***

### F-048 — For 58 census proteins the V2 span is a short extracellular loop INSIDE a larger transmembrane domain, and the annotation and the span are describing different objects

- **Date:** 2026-08-19
- **Status:** ⚠ **OPEN.** It closes when the surface question below is ruled, **or** when the residual is named and accepted. ⚠⚠ **It is NOT a tranche 6 finding** — 0 of the 58 sit in tranche 5, and none is past the trained context. **It is a census finding, and the census is on a live browsable surface.**

- **The finding.** ⚠⚠ **The V2 span is a short extracellular loop inside a larger transmembrane domain. Engulfment is not an annotation artifact; it is what a loop in a multi-pass protein looks like.**

- **How it was found.** Not by looking for it. `clip` was being given a refusal for a case the owner had ruled unruled (`F-046`), and characterising what it would refuse — **58 features, 58 distinct accessions, one each** — turned a data-hygiene category into a statement about molecules. ⚠ *The descriptions were the evidence, not the counts:* **MARVEL · ABC transmembrane type-1/2 · Cytochrome b561 · KASH · HIG1 · UPAR/Ly6**, and the `I` repeats of the plexin/semaphorin-like stack. **Polytopic membrane domains, every one.** 44 `Domain`, 14 `Repeat`.

- **⚠ Why this is a finding and not an observation: it is `F-037`'s shape one layer down.** `F-037` established that **`span_aa` is the largest extracellular segment, not the extracellular content.** For these 58 the largest segment is **a loop**, and the domain annotation describes **the membrane bundle the loop sits inside.** ⚠⚠ **The engulfment is the annotation and the span disagreeing about which object is being described** — one names a multi-pass bundle, the other names a few residues poking out of it.

- **⚠⚠ It vindicates `F-046`'s refusal in one sentence.** Clipping an engulfing feature would have recorded that **a 5-residue loop IS a MARVEL domain** — 100% domain coverage, one domain, exactly span length. **That is not a rounding error in a coverage number. It is a false statement about a molecule, generated silently, on every row it touched.** *Refuse rather than attempt.*

- **⚠⚠ THE SURFACE QUESTION, WHICH IS THE OWNER'S AND IS WHY THIS IS OPEN.** Measured against the live API rather than inferred from the manifest — `GET /api/census`, 2,690 rows, read-only:

  | | |
  |---|---|
  | the 58 | **58** |
  | ⚠⚠ **of those, present on the live browsable surface** | **58 of 58** |
  | in tranche 5 (held, unfolded) | **0** |
  | tranche distribution | **31 in tranche 1, 27 in tranche 2**, 0 in 3/4/5 |
  | `span_aa` min · median · max | **5 · 45 · 145** |
  | rows at `span_aa` ≤ 20 | **12** |
  | rows at `span_aa` ≤ 10 | **2** |

  **The shortest is `Q9ULH0`, analysis id 382: a span of FIVE residues (681-685), served with `mean_plddt` 61.38, inside a `KAP NTPase` domain annotated 440-953.** Next is `Q9NX76` at 7 aa inside a MARVEL domain, and `A8MV81` at 11 aa inside HIG1 1-92.

  ⚠ **`D-094`'s mount preconditions have never been checked against a five-residue span**, and a mean pLDDT over 5 residues is a different object from a mean over 500 wearing the same label. **Stop-and-report, per the order: this is a surface question and no remedy is proposed here.**

- **⚠ Where it does NOT reach, measured so the scope is not overstated.** `clip` — the rule that would make the false statement — **never meets these 58 outside the equivalence proof.** Every `clip` call site runs on the 141 (`task_m4`, `task_o2`, `task_regimes`), the ten (`task_m3`), or two named accessions (`task_n`). The three full-census iterations use `admit_raw` and `drop` only. **So `F-046`'s stop-and-report clause does not fire on that axis; this entry's does, on a different one.**

- **⚠ And `no_domains` gains its fourth cause from this, with the denominator stated.** Of the **3,467** rows in `census_manifest.v7.csv`, **2,327 have no domain intervals under `drop`** and 1,140 have at least one (2,327 + 1,140 = 3,467). The causes, each named, checked against an independently counted total rather than against their own sum:

  | cause | what it means | the 141 | census |
  |---|---|---|---|
  | `no_domainlike_features_in_the_chain` | the UniProt entry carries no `Domain`/`Repeat` anywhere | **10 — all ten** | 2,033 |
  | `features_exist_but_none_overlaps_the_span` | annotated, but every feature lies wholly outside `[s0, s1]` | 0 | 215 |
  | `all_overlapping_features_overhang_a_boundary` | every overlapping feature crosses exactly one edge, so `drop` rejects each | 0 | 21 |
  | ⚠ `all_overlapping_features_ENGULF_the_span` | **this finding** — dropped because they engulf, not because they are absent | **0** | **58** |
  | `dropped_mixed_engulfing_and_overhang` | kept as an unfirable branch with its zero | 0 | **0** |
  | **total** | | **10** | **2,327** |

  **So the 141's ten `no_domains` rows are genuine absences of annotation, not rejections** — the cause each needed, named. ⚠ **And a rejection had been arriving under a label that says absence**, which is the thing `D-085` and the span-category work exist to prevent.

- **⚠ What this does NOT claim.**
  1. **No claim that the spans are wrong.** The V2 rule is the ruled rule and these are what it produces on multi-pass proteins. **The disagreement is between two descriptions, and naming it is not choosing between them.**
  2. **No claim about fold quality.** `mean_plddt` on a 5-residue span is reported here as a *fact about what is served*, not as evidence the structure is bad. ⚠ `D-039` already says pLDDT is self-reported and locally scoped; **a 5-residue mean is simply outside anything the convention was calibrated on** (`F-046`'s population-specificity point, and `A-014`).
  3. **No remedy proposed.** The surface ruling is the owner's, and `D-074` decision 3 warns against answering a finding with a framework.

---

### F-046 — Three straddle predicates lived under one name in two modules, and the rule behind `D-095`'s founding numbers had no name at all

- **Date:** 2026-08-19
- **Status:** ✅ **CLOSED.** **Amended by: `fc8040c`** — one function, `straddle` keyword-only with no default. ⚠ The finding is recorded before the fix in `7591164`, and the two are deliberately separate commits: one commit that both recorded the divergence and deleted it would leave this entry pointing at state no longer reachable.

- **The finding, quoted at `7011e24` so it is checkable after the code is gone.** Two functions, both named `domain_intervals`, both filtering `("Domain", "Repeat")`, differing by one inequality:

  ```python
  # scripts/tranche6_runs.py:64            — "drop"
  if a is None or b is None or a < s0 or b > s1:
      continue
  out.append((int(a), int(b), f.get("description", ""), f.get("type")))

  # scripts/tranche6_domain_survey.py:67   — "admit_raw"
  if a is None or b is None or b < s0 or a > s1:
      continue
  out.append((a, b, f.get("description", ""), f.get("type")))
  ```

  ⚠⚠ **`a < s0 or b > s1` admits only what is wholly inside. `b < s0 or a > s1` admits anything overlapping, at its RAW coordinates.** They agree on every protein whose domains sit clear of the span boundary — which is 139 of the 141 — and disagree silently on the two that do not.

- **⚠⚠ THERE ARE THREE RULES, NOT TWO, AND THE THIRD IS THE ONE THAT PRODUCED `D-095`.** `clip` was ruled (`CLOSEOUT-2026-08-18` §5) and unimplemented. `drop` was Task L's. **`admit_raw` was `scripts/tranche6_domain_survey.py`'s, it is what computed FAT1's 2,289 aa and FAT4's 3,037 aa, and it had never been named anywhere in this project.** ⚠ A two-column comparison had already lost it: *the rule was chosen by which module you imported from, which is a default nobody wrote down.*

- **⚠ What it cost, measured rather than estimated.** Over the 141, `admit_raw` counts **45 residues the span does not contain** (in-run total 180,847 against `clip`'s 180,802). That is the same 275-residue definitional divergence recorded in `CLOSEOUT-2026-08-18` §5, seen from the third side.

- **The equivalence proof (`scripts/tranche6_domain_intervals_equivalence.py`).** It carries **frozen verbatim copies** of all three deleted implementations as oracles, because a proof that imports the thing it is proving against proves nothing once that thing is gone.

  | | |
  |---|---|
  | corpus | **4,990 documents · 4,669 spans · 41,674 intervals** — cache-wide for `admit_raw`, not sampled |
  | compared on | ⚠ **hashes of serialised intervals, never on counts** — two interval lists of equal length can differ in every coordinate |
  | `admit_raw` | `997add511d427cbd48e1` == `997add511d427cbd48e1` |
  | `drop` | `589ea8b36339398f31cd` == `589ea8b36339398f31cd` |
  | `clip` | `919a2d005ccbc96e7edc` == `919a2d005ccbc96e7edc` |

  ⚠⚠ **The proof checks itself, and that self-check is the discriminating fixture.** A corpus in which no domain crosses a span boundary makes all three rules agree, so an equivalence proof over it would pass **while proving nothing**. It therefore counts the spans on which the rules actually disagree — **1,296** — and **fails when that count is zero.**

- **⚠⚠ Member: an inequality the data cannot see.** Flipping `b < s0` to `b <= s0` leaves the cache-wide proof **GREEN**, because **no annotated domain in 4,990 documents ends exactly at a span start.** The fixture suite goes **RED**. Three fixtures now pin those boundaries deliberately.

  | flip | corpus | fixtures |
  |---|---|---|
  | `a < s0` → `a <= s0` | RED | RED |
  | ⚠ **`b < s0` → `b <= s0`** | **GREEN** | **RED** |
  | `a > s1` → `a >= s1` | RED | RED |
  | `clip` truncation off by one | RED | RED |

  **The two gates are not redundant, and nothing said so until the flip was run.** ⚠ *An inequality the data cannot discriminate has to be pinned by a fixture or it is not pinned at all* — and the corpus was 4,990 documents, which is exactly the size at which a corpus starts to feel like proof.

- **⚠ Member: a named limitation, which is an absence with a cause and not an untested path.** `scripts/tranche6_runs.py` **cannot** be stdout-compared pre- and post-reconciliation, because the pre-change file cannot run against the post-change module — **that is the missing-`straddle` `TypeError` working as designed.** For that script the comparison is on its artifact (`data/census/tranche6_runs.csv`, `1f0a5ca84a2934dc…`, byte-identical and git-clean) and on the function (the cache-wide proof above), not on stdout.

- **Nothing downstream moved, checked on artifacts.** `D-095`'s own evidence script, `scripts/tranche6_domain_survey.py`, produces **byte-identical stdout** pre and post: `aad52b28a7eac3f471666eebaf729eb201526da77e714eac368f7aaef2711cd3`. ⚠ So the entry may be re-cited at a revision with that hash rather than re-derived: **the evidence script's output is unchanged, and here is the hash.**

- **⚠ One thing deliberately NOT changed.** The coordinate read stayed `location.start.value` rather than moving to `_coords`, which additionally rejects an `UNKNOWN` modifier. Measured across all 4,990 cached documents and **9,008** `Domain`/`Repeat` features: **zero** carry an `UNKNOWN` modifier and **zero** lack `start`/`end`. The two reads agree on this cache **by data, not by construction**, so switching would be a behavioural change wearing a refactor's clothes. **Named instead of taken.**

- **⚠⚠ THE ENGULFING CASE: CLIP's STATED RATIONALE COVERS EDGES AND NOT ENGULFMENT.** `CLOSEOUT-2026-08-18` §5 argues CLIP as *"a clipped straddler occupies its residues; dropping it manufactures a gap at the span boundary that does not exist in the molecule."* **That is an argument about edges.** A feature beginning at-or-before `s0` and ending at-or-after `s1` has **no edge inside the span at all**, so the argument does not reach it, and the owner ruled the case **explicitly NOT ruled** (2026-08-19).

  What `clip` would otherwise do: **replace the span with itself** — one domain of exactly span length, 100% coverage, a single run equal to the whole span. ⚠ For any row past context that manufactures a `run_interior` cut where the annotation asserted no internal boundary. **So `clip` REFUSES** (`UnruledEngulfingFeature`, naming the accession and the feature); `admit_raw` and `drop` are defined on this case and keep their behaviour. *Refuse rather than attempt — the `preflight()` pattern: a case with no ruling is a stop, not a green light.*

  | population | engulfing features | distinct accessions |
  |---|---|---|
  | the 141 (`D-098`) | ⚠ **0** — reported because an empty category is a measurement | 0 |
  | the ten `D-095` subjects | **0** | 0 |
  | the full census | **58** | **58 — one each, not concentrated** |

  ⚠ **CORRECTION to the figure in the ruling as delivered, which said 50.** 50 is the count under a *strictly*-beyond-both-boundaries test. Under the ruled convention — at-or-before `s0` **and** at-or-after `s1` — it is **58**: 4 features sit flush at `s0` while exceeding `s1`, and 4 sit flush at `s1` while preceding `s0`. **The 8 are exactly what the convention moves, and they are the reason to state it.**

- **⚠⚠ THE BOUNDARY CONVENTION, AND THE FIXTURES THAT ARE THE ONLY THING PINNING IT.** A feature with `a == s0` **and** `b == s1` satisfies *wholly within* and *at-or-before the start and at-or-after the end* at once. **It is classified `engulfing`, and `engulfing` is tested first** — because the hazard is defined by the **clipped result**, not the raw coordinates: `clip` maps every such feature onto exactly `[s0, s1]`, and a domain of exactly span length is the unruled object however far outside it began. ⚠ A convention filing the flush case as `inside` would pass the identical hazard through under a name that says it is safe.

  ⚠⚠ **Measured: that case occurs 0 times in the 141, 0 in the ten, and 0 in the full census.** *The corpus cannot exercise this choice, so only a fixture can pin it* — **the same sentence as the invisible inequality above, applied before the fact rather than after.** Seven deliberate fixtures pin the convention: the flush-both case, the four one-sided boundary cases, and the two one-residue-inside controls.

- **⚠ And `no_domains` gains a cause, which is why the category matters.** A row whose only overlapping features **engulf** the span reports `no_domains` under `drop` **because its features were dropped, not because it carries no annotation** — an absence and a rejection arriving under one label. Causes, summed against an independently counted total:

  | cause | the 141 | full census |
  |---|---|---|
  | `no_domainlike_features_in_the_chain` | **10 — all ten** | 2,033 |
  | `features_exist_but_none_overlaps_the_span` | 0 | 215 |
  | `all_overlapping_features_overhang_a_boundary` | 0 | 21 |
  | ⚠ `all_overlapping_features_ENGULF_the_span` | **0** | **58** |
  | `dropped_mixed_engulfing_and_overhang` | 0 | 0 |
  | **total** | **10** | **2,327** |

  **So the 141's ten `no_domains` rows are all genuine absences of annotation**, not rejections — the cause each one needed, named.

- **⚠ What the 58 actually are, because a rule should be written against the biology.** 44 `Domain`, 14 `Repeat`; span lengths min 5, median 45, max 145; ⚠⚠ **none past the 1,026 aa trained context, so none can enter tranche 6 today.** The descriptions are MARVEL, ABC transmembrane, Cytochrome b561, KASH, HIG1, UPAR/Ly6 — **polytopic membrane domains.** The V2 span is a short extracellular loop *inside* a larger transmembrane domain. **Engulfment is not an annotation artifact; it is what a loop in a multi-pass protein looks like.** That is an argument for a rule; the rule is the owner's.

- **Consequences.** `straddle` is keyword-only with **no default**: omitting it raises `TypeError`, an unrecognised value raises `UnknownStraddleRule`, and a positional argument raises. ⚠ `D-095 amendment 1` records `straddle_handling` on every derived artifact beside `merge_rule` and its gap tolerance; **this entry is what makes that parameter nameable at all.** ⚠ The gap tolerance itself is **zero uncovered residues**, stated as the number rather than as `start <= prev_end + 1` — see `docs/PASSAGES-2026-08-19-gap-tolerance-and-merge-rule.md`, which exists because that sentence was corrupted three times in transit and the repository does not drop bytes.

---

### F-045 — A revert proof certified a flip it never ran: two edits of equal size inside one clock second, and the second executed against the first's bytecode

- **Date:** 2026-08-19
- **Status:** ✅ **CLOSED 2026-08-19, on `D-074`'s SECOND clause and explicitly not its first.** ⚠⚠ **Clause 1 — *the instrument no longer exhibits it* — is NOT met and cannot be.** `PYTHONDONTWRITEBYTECODE=1` prevents recurrence in new drivers and **validates nothing retrospectively**; the **23 of 23** prior revert proofs stay `driver_unknown`, and no fix makes them otherwise, because the driver was never a recorded property to recover. **Clause 2 — *it carries in itself the statement of what it gets wrong* — is met by this entry:** the mechanism, the named colliding pair, the controlled reproduction under both cache settings, and the enumeration with its unknown. ⚠ **Closing on clause 2 means the residual is ACCEPTED IN THE OPEN, not repaired.** Every *proven by revert* older than 2026-08-19 in this log is a claim whose method is unrecorded, and that sentence is the closure.
- **⚠ What this entry is NOT.** It is **not** the wrong-but-plausible-answer family. `PREWORK-2026-08-19.md` §3 named `F-045` for that; **the number moved to `F-047`**, which is reserved and unwritten. A reader arriving here from the prework is in the wrong entry — ⚠⚠ *which is `F-044`'s subject exactly, and the invariant cannot see it.*

- **⚠⚠ THE FINDING, WHICH IS NOT THE `.pyc`.** **The driver is not a recorded property of a revert proof.** This log says *proven by revert* twenty-seven times across twelve entries, and **not one of them records how the break reached the interpreter.** `A-016 (any red proves the assertion bites)` and `A-017 (the fixture must reach the code under test)` are the rules by which this project decides a test is real — so **`A-016` compliance has never been auditable.** The record carries the verdict and discards the method. ⚠ *The `.pyc` collision is how the gap surfaced; the missing field is what it means.*

- **The mechanism, in one line.** CPython validates a cached `.pyc` against the source's `(mtime, size)`, with **mtime truncated to seconds**. A driver applied flip 1, ran the suite, restored, then applied flip 2 — **same file, same resulting size, same clock second** — so the interpreter reused flip 1's bytecode and **flip 2 was never executed.**

- **⚠ THE COLLIDING PAIR, NAMED, AND THE CONTRADICTION IN THE FIRST REPORT OF IT.** Two statements were issued that cannot both bear on the same event, and the second one was irrelevant:

  | | file | delta | fate |
  |---|---|---|---|
  | flip 1 `a < s0` → `a <= s0` | `scripts/tranche6_domain_census.py` | **+1** | ran |
  | ⚠⚠ flip 2 `b < s0` → `b <= s0` | `scripts/tranche6_domain_census.py` | **+1** | **executed flip 1's bytecode** |
  | flip 3 clip truncation | `scripts/tranche6_domain_census.py` | +4 | ran |

  ⚠ **A third flip, `a > s1` → `a >= s1`, also carries `+1`** and shares the same size; it was added to the driver after the fix, so it never collided, but it was equally exposed.

  ⚠⚠ **The `-18 / +4 / -39 / -2` deltas reported alongside this describe a DIFFERENT driver** — the first one, whose four flips landed in `scripts/tranche6_runs_clip_compare.py` and the census module at different sizes. **They are true and they say nothing about the collision.** They were offered as evidence of the defect's scope and they do not reach its subject: *a clean number that means something other than it appears to*, in the report of a finding about clean numbers that mean something else. **Recorded, not quietly dropped.**

- **⚠ Reproduced under control, so the mechanism is measured rather than inferred.** The three-flip sequence was re-run twice against the same file:

  | | flips 1 and 2 present `(mtime_s, size)` | flip 1 vs flip 2 digests | flip 2 verdict |
  |---|---|---|---|
  | bytecode caching **ON** | `(1787066189, 29949)` — **identical** | **identical** | **RED (false)** |
  | bytecode caching **OFF** | `(1787066190, 29949)` | differ | **GREEN (true)** |

  **The false red was flip 1's result, printed under flip 2's label.** ⚠ And the honest answer underneath is that flip 2 is **not caught by the corpus at all** — it is caught only by fixtures written afterwards.

- **⚠⚠ WHAT THE RE-CERTIFICATION DID AND DID NOT COVER, stated because the distinction is the whole of `F-045`'s reach.** The four flips re-run with bytecode writing disabled were the **first driver's**, at deltas `-18 / +4 / -39 / -2` — **all distinct, so a size collision was impossible among them.** ⚠ **They are NOT the colliding pair.** The colliding pair was re-run separately, by the corrected `§9` driver, which is what produced the corpus-GREEN / fixtures-RED table in `F-046`. **So the defect's own subject was re-verified — but not by the run first cited for it, and the re-certification is a real measurement of something adjacent to the defect rather than of the defect.**

- **⚠⚠ The first proof reported that flip as CAUGHT.** It printed a red test, a real assertion, and a plausible digest pair. Re-run with `PYTHONDONTWRITEBYTECODE=1`, the same flip is **not caught by the corpus at all** — it is caught only by fixtures written afterwards. **A green that is green for a reason unrelated to the thing under test, and a red that is red for the previous experiment.**

- **⚠ Why this is worse than an ordinary false positive.** `A-016 (any red proves the assertion bites)` and `A-017 (the fixture must reach the code under test)` make the revert proof **the instrument that certifies the other instruments.** A test is believed here because a revert proof reddened it. **A false green in this instrument is a false green wherever it was used**, and it does not announce itself: the output is indistinguishable from a genuine pass.

- **The forward fix, stated as forward-only.** The drivers now run with `PYTHONDONTWRITEBYTECODE=1`. ⚠⚠ **That validates nothing retrospectively, and treating a forward fix as retroactive coverage is the same error one level up.**

- **⚠ The enumeration (Task T), reported with its key and its `unknown`.** *Which prior revert proofs were produced by a driver applying more than one flip in a single run?*

  | population | key | n |
  |---|---|---|
  | log entries recording a revert proof | one row per `###` entry in `docs/README.md` | **12** (D-097, D-094, D-090, D-086, D-084, F-039, F-038, F-034, F-026, D-079, D-077, D-075 — 27 mentions) |
  | test files documenting one | one row per file under `tests/` matching `revert` | **12** |
  | ⚠ **committed drivers that shell out to `pytest`** | grep over `scripts/ tests/ core/ worker/ app/` | **0** |
  | `driver_known_multi_flip` | driver identifiable | **2**, both 2026-08-19, both this session |
  | ⚠⚠ **`driver_unknown`** | driver not identifiable | **all prior proofs** |

  ⚠⚠ **The finding inside the finding: the driver is not a recorded property of a revert proof.** No driver was ever committed, and the ad-hoc ones do not survive their session. So for every prior proof the answer is not *lost* — **it was never captured.** The enumerable set is the proofs; the unenumerable field is how each was applied. *`unknown` is the honest value and it is the majority value.*

- **The re-certification's own result, which stands on its own terms.** All four of the first driver's flips reproduce with bytecode writing disabled, each red at its named test, zero collection errors, both files restored byte-identical. **The defect fired only where two flips happened to share a resulting size**, and among those four none did.

- **⚠ The enumeration's integers, with the population named and summing.**

  | population (key) | n | `driver_known` | `driver_unknown` |
  |---|---|---|---|
  | log entries recording a revert proof, prior to 2026-08-19 (one `###` entry) | **12** | 0 | **12** |
  | test files documenting one (one file under `tests/`) | **12** | 0 | **12** |
  | ⚠ overlap — a test file named inside such an entry (`test_ceiling_probe.py`) | **1** | — | — |
  | **union: distinct prior revert-proof-bearing artifacts** | **23** | **0** | **23** |
  | driver runs on 2026-08-19 (this session) | **5** | **5** | 0 |

  ⚠ **`driver_unknown` is 23 of 23, not a word**, and it is 23 **because the field was never captured**, not because records were lost. Committed drivers that shell out to `pytest`: **0**.

- **⚠ What would actually close this.** Not a framework — `D-074` decision 3. Candidates, none ruled:
  - **Record the driver beside the proof.** A revert proof states what it broke and what reddened; it does not state how the break reached the interpreter. One line would make Task T answerable next time.
  - **Assert execution, not just outcome.** A break that also changes an observable string proves the new code ran; a red alone does not distinguish *caught* from *stale*.
  - ⚠ **`D-080` is adjacent and still reserved** — *a revert proof operates on committed state or on a copy, never on a working tree holding uncommitted work.* This is the same instrument failing for a neighbouring reason, and the two should probably be ruled together.

- **⚠ How it was found.** Not by the suite and not by review. The driver reported four `[PASS]` rows and **two of them carried byte-identical digest pairs** — the same numbers under two different experiments. *A clean number that means something other than it appears to*, which is this project's most productive shape and the reason `F-047` is worth writing.

---

### F-044 — The citation invariant proves that a reference RESOLVES, never that it resolves to the right thing: it finds holes, not mismatches

- **Date:** 2026-08-17
- **Status:** ⚠ **OPEN — a finding against an instrument (`D-074`).** It closes when a reference to a numbered entry cannot silently acquire the wrong target, **or** when the residual is named and accepted in the open. ⚠ **Adding a second checker is not automatically the remedy** — `D-074` decision 3 warns against answering a finding with a framework that becomes a second thing to drift.

- **The finding.** The check `RESERVED.md` documents is:

  ```
  missing = sorted(cited - defined - reserved)
  ```

  ⚠⚠ **That is a set-membership test on integers.** It proves every cited `D-NNN` / `F-NNN` **exists**. It has no access to what the entry *says*, so it cannot detect a citation that resolves to a **real entry with the wrong content**. **It finds holes. It cannot find mismatches.**

- **⚠ The evidence is a contrast, observed the same day, and the contrast is the finding.**

  | defect | what happened | the invariant |
  |---|---|---|
  | **hole** — the then-next-free `D-` integer, cited before it existed | a sub-entry named it in a *"next free … remains …"* line | ⚠ **caught in one run**, first execution, unambiguous |
  | **mismatch** — `D-095` cited for the wrong thing | `ORDERS-Code-2026-08-18` §3 and `scripts/taskc_multidomain_population.py` both said the PAE comparison *"is a `D-095` decision"* | ⚠⚠ **silent through every run**, in the log and in a committed script |

  When that order was written, `D-095` was the next free integer. It was then taken by **the tranche-6 tiling design document**, which says nothing about a PAE comparison. ⚠ **Both documents were committed, and both passed the invariant, because `D-095` exists.**

- **⚠⚠ Why the mismatch is the worse of the two, which is the whole point.** `D-062`'s recorded harm was *citations treating a missing entry as settled authority, with nothing in the text suggesting it was missing.* **A hole announces itself the moment anyone follows it** — the target is not there. **A mismatch does not.** The reader follows the pointer, finds a real, well-formed, confidently-written entry, and reads it as the authority for a claim it never made. ⚠ **The remedy for `D-062` closed the route that fails loudly and left open the route that fails quietly.**

- **⚠ The same shape is not confined to citations, which is why this is a finding and not a note.** On 2026-08-17, in one HPA download of one version: `proteinatlas.tsv` has `Gene` = **the symbol** (`TSPAN6`); `pathology.tsv` and `normal_tissue.tsv` have `Gene` = **the Ensembl id**, with the symbol in `Gene name`. **A join on `Gene` across them returns a clean, plausible, entirely empty intersection and raises nothing.** `D-100` records the identical trap inside a single file — S3's `Gene` is Ensembl, matching on it gives **0 of 82**. ⚠ *A name that resolves to the wrong object is the general defect; the citation checker is one instance of the blind spot, not the whole of it.*

- **⚠⚠ THE REMEDY ALREADY EXISTS IN THIS REPOSITORY, APPLIED TO ONE NAMESPACE AND NEVER GENERALISED.** `RESERVED.md` rules, for `A-` only:

  > *"every **new** local `A-` reference is written as **`A-0NN (descriptive name)`**, never as a bare number. If a number moves … the citations do not orphan — **the name carries them.**"*

  That was invented because `A-` numbers might **move**. The defect here is a number being **reused** — a different mechanism producing the identical failure, *a citation pointing at the wrong entry*. ⚠ **The mitigation is described as "available now and free" and was scoped to the namespace whose problem prompted it.** This is the project's own recurring sentence: **a rule applied to one shape and not another is not a rule** — the sentence that names the `pytest`/`SELECT` failure of 2026-08-17 and the backtick/encoding failure of the same day.

- **⚠ What this does NOT claim.**
  1. **The invariant is not broken and must not be weakened.** It is *sound* on the failure mode it was built for and caught a live instance the same day, first run. **This is a finding about its scope, not its correctness.**
  2. **No claim that other mismatches exist.** ⚠ **One is confirmed (`D-095`); the rest of the log is UNCHECKED**, because checking it requires reading every citation against its target and no tool here does that. *Unmeasured is not zero.*
  3. **No remedy is adopted here.** Naming the defect is not fixing it, and `D-074` decision 3 is explicit that a framework answering a finding becomes a second thing to drift.

- **Candidate remedies, none ruled, stated so the choice is visible:**
  - **Generalise the `A-` convention:** cite as **`D-NNN (short name)`**, so a reused integer orphans the name instead of silently re-pointing it. ⚠ Costs nothing at write time and is the only candidate already proven in this repo.
  - **Forward references never name a bare integer** — the rule that would have prevented both `D-095` *and* the hole above. `RESERVED.md` is the index; the log points at it.
  - **A content check** — assert each cited entry's title matches the citing context. ⚠ Almost certainly the `D-074` decision-3 trap: it needs maintenance, and a checker nobody trusts is worse than a rule everybody reads.

- ⚠⚠ **This entry tripped its own subject, twice, while being written.** The first draft named the then-next-free integer in the evidence table and again in the remedy list — **and the invariant refused it, immediately, both times.** ⚠ *That is the finding in miniature:* the check is **fast, exact and unarguable** against a hole, including one written by the person documenting holes; and it said nothing at all about `D-095` sitting mismatched in the same file. **The instrument is not unreliable. It is precise about one thing and blind to its neighbour.**

- **⚠ How it was found, because that is evidence about how much else is unchecked.** Not by the invariant, and not by review. **The owner read a sentence in a report and recognised the number had moved under it.** Every automated gate in this repository passed over `D-095` in both the log and a committed script, on every run, for the whole of the day it was wrong.


#### F-044 amendment 1 — ⚠⚠ A Planner instance: the reserved row's CLASS matched, its INSTANCE did not, and the pointer that would have shown it was never followed

- **Date:** 2026-08-19 · **Status:** the finding stays **OPEN** — `D-074`: a finding against an instrument stays open until the instrument no longer exhibits it. **This is the instrument exhibiting it, one day after the entry was written.**

- **What happened.** The Planner directed that the `domain_intervals` divergence be written as **`F-014`**, quoting that reservation's text — *"documenting a duplication is not managing it — the tenth instance of the two-paths-to-one-quantity class, and the first where the drift was written down and the writing-down substituted for the fix."* **The class description matched exactly.**

- ⚠⚠ **`F-014` is reserved for a different instance.** `AMENDMENT-2026-08-04-code-feedback.md` §160–165 reserves it for **`scripts/ecd_lengths.py` carrying a hand-duplicated `CEILING_KNOWN_GOOD`/`CEILING_KNOWN_BAD` while `core/manifest.py`'s comment documented the duplication.** `ARCHITECTURE.md:693–697` records that instance **already fixed and guarded** by `tests/test_manifest.py::test_no_second_copy_of_the_ceiling_survives_in_the_tree`.

- ⚠ **The specific failure, and it is sharper than a misread.** `RESERVED.md`'s row carries **two** columns — the class description **and** a pointer, *"Amendment §7, 2026-08-04"*. **The Planner read the description and never followed the pointer.** It then **ordered Code to check the reservation's RELEASE CONDITION** (*held until `d077-local-fold-envelope` merges*) — ⚠⚠ **so it verified the half that had a check and asserted the half that did not.** *Pointer-is-not-proof, one day after writing the rule against it.*

- **Caught by Code**, who followed the pointer and reported the mismatch rather than writing what was ordered. ⚠ **`F-014` remains RESERVED and untouched;** the divergence took `F-046`.

- ⚠ **What this adds to `F-044`.** The original entry establishes that the citation invariant proves a reference **resolves**, never that it resolves to the **right thing**. **This instance shows the same hole in a `RESERVED.md` row**: the whitelist proves a number is legitimately unwritten and has no access to **what it was reserved for.** **The remedy is the one already ruled — cite by number AND name — extended to reservations: a reservation is cited by number and INSTANCE, never by class.**

- ⚠ **LANDED BY CODE, 2026-08-19.** Verbatim from `docs/AMENDMENT-2026-08-19-planner-log-entries.md`. **The release condition itself was verified and holds:** `d077-local-fold-envelope` merged as PR #122 at `d6622f9`, 2026-08-05, an ancestor of both `main` and `HEAD`, with **0** commits unmerged. **So `F-014` is writable today — for its own subject, which is not this one.**

---

### F-042 — ESMFold emits PAE on every forward pass and the pipeline discards it: 2,690 of 2,690 census folds carry none

- **Date:** 2026-08-17
- **Status:** ⚠ **OPEN.** It closes when the local-tier persistence path is repaired **and** the 2,690 existing rows either carry PAE or carry the statement that they do not and why. ⚠ **Repairing the path forward does not close it** — the recorded census stays PAE-less.

- **The finding.** PAE — `predicted_aligned_error` — is the folding head's learned confidence about the **relative position of two residues**. `protein_analyses.pae_json_path` is **NULL on all 2,690 census folds** and non-NULL on **79 of 80** cohort rows (the exception is IGF2R, which never folded). **The model produces the quantity on every forward pass and the pipeline throws it away.**

- **⚠ Not `pae_never_emitted`, and this was established by observation, not inference.** The control fold (`D-099`, commit `cc2551f`) ran **25 local int8 chunk-64 folds — the exact census recipe — and PAE was emitted on 25 of 25, every matrix dimension matching its span.** ⚠ Before that run the two categories were indistinguishable from the database alone, and the difference matters: one is a model limitation, the other is a pipeline defect. **It is the second.**

- **Evidence — the fold-day partition, which reconciles with no residue:**

  | fold day | rows | PAE NULL | PAE set |
  |---|---|---|---|
  | 2026-07-23 / 24 / 25 | 75 / 2 / 2 | 0 | **79** |
  | **2026-08-16** | **2,690** | **2,690** | **0** |

  75 + 2 + 2 + 2,690 = **2,769 against 2,771 rows**; the two missing are IGF2R and `P55073`, which never folded. ⚠ **A clean partition, not a suggestive one.**

- **The mechanism — two persistence paths, both scoped to the paid tier:**
  1. **The upload stopped carrying PAE** (`D-035` part 2), so `app/artifacts.py:persist` no longer sets the column from the wire.
  2. **The compensating out-of-band route** (`D-036`) writes the column via `_write_pae_file` → `_update_pae_path`, but it is fed by `worker/main.py:_persist_pae_local`, which fires **only `if artifact_dir:`** — documented *"set on the RENTAL box."*

  **The local tier falls through both.** ⚠⚠ **And the backstop was attached to the expensive path, not the important one:** `scripts/retrieve_rental_pae.py` is *"the blocking gate before pod termination"* — so on rental a missing PAE is loud, and **on local there is no pod to terminate and therefore no gate.** *A guard placed where the money is, not where the data is.*

- **⚠ What the mechanism is NOT, recorded because it was claimed and refuted:**
  - **Not the tier tags.** `D-090` measures **2,733 local / 38 rental**; census tranches 1–4 total 2,691, all local, so **only 38 rows in the database are tagged rental against 79 carrying PAE.** At least 41 PAE-bearing rows are tagged local. ⚠ `jobs.tier` was **backfilled 2026-08-17 from a length rule** and does not record where a job ran, so it cannot support a tier explanation in either direction.
  - **The July folds nonetheless ran on rented hardware** — `CLOSEOUT-2026-07-23-full.md`, *"the First Rented Fold."* ⚠ **Tier and date are perfectly confounded in the table**: no local July fold and no rental August fold exist as separate cells, so **the partition that revealed the finding cannot identify its cause.** The code path did that, not the data.
  - ⚠ **A Planner-proposed discriminator was dead on arrival** — listing July `pae.json` files on the local box returns empty under **both** hypotheses. Recorded because a check that cannot separate its hypotheses is not a check (`F-001`'s shape).

- **⚠⚠ What was actually lost, stated precisely.** `pLDDT` is **per-residue and local** — how sure the model is about where one residue sits. **PAE is pairwise and relative** — whether two residues are confidently positioned *with respect to each other*. **They are not substitutes.** So the census can report confidence about every residue's local geometry and **nothing whatsoever about whether two domains are confidently placed relative to one another** — which is exactly the quantity `D-091` ruling 3 requirement 3 asks for, on the population where re-folding is most expensive.

- **⚠ What this does NOT claim.** **No published result is affected.** `F-004`, `F-005`, `D-075` and the Run A ablation use pLDDT and geometry; **none consumes PAE.** Nothing is invalidated and nothing is re-run.

- **⚠ Why it went unnoticed for a month.** **Nothing consumed PAE**, so its absence produced no error, no warning and no visibly wrong number — the artifacts were correct, complete and plausible. **A capability nothing uses degrades silently**, and this was found only because a *different* question needed it. ⚠ **That is the general lesson and it is not specific to PAE:** the pipeline emits other things nobody reads, and their state is equally unknown.

- **Open decisions this creates, named rather than assumed:**
  1. **Repair the local persistence path.** ⚠ **Its own entry**, after this finding — repairing it inside the control fold would have begun backfilling the NULLs the finding is about.
  2. ⚠ **Whether to re-fold the 2,690 to recover PAE is a DECISION, not a remedy.** It is local and costs no money, and `determinism_control.int8.610.88` shows the kernel is deterministic at this recipe, so a re-fold should reproduce. **But it writes 2,690 rows and it is not this entry's to make.**
  3. ⚠ **Whether the 79 `pae_json_path` files RESOLVE is unanswered** — blocked by a permission denial on the volume, and correctly stopped-and-reported rather than worked around. **A path is not a file.**

---

### F-043 — A hard cutoff on a ~11-patient ordinal statistic: a quarter of Kathad's surviving pairs turn on one pathologist call

- **Date:** 2026-08-17 (⚠ authored "2026-08-18"; stamped with the real date)
- **Status:** ⚠ **OPEN — a finding against an instrument (`D-074`).** The Kathad filter is this project's comparator. It stays open until the comparator no longer exhibits this, **or** until every surface citing the expression ranking carries the statement of what it gets wrong.

- **The finding.** The quasi-H-score is a weighted percentage over an HPA panel of **median 11, mean 10.2, maximum 12** patients. **246 of 1,640 rows have n ≤ 4; two have n = 2.** At n = 12 the statistic moves in **8.33-point steps**; at n = 4, 25 points. A hard `≥150` cutoff is applied to an estimator that can take only a few dozen distinct values.

  | perturbation | of the 337 kept | of the 1,303 excluded | grid-wide |
  |---|---|---|---|
  | **one patient, one category** | **83 (24.6%)** | 33 (2.5%) | 116 (7.1%) |
  | two patients | 151 (44.8%) | 85 | 236 (14.4%) |

- ⚠⚠ **52 pairs sit at EXACTLY 150.0** — the cutoff lands on the most populated discrete value the estimator can take. `≥150` gives **337**; `>150` gives **286**. **The inequality sign is worth 51 pairs.**

- ⚠ **The method disagrees with itself across two representations in one file.** Using the paper's own printed `percent_` columns with the paper's own formula yields **329**, not 337 — **eight of the exact-150 pairs fall below on rounding alone.**

- **⚠ What is NOT established, stated before anyone cites this:**
  1. **The 83 is an UPPER BOUND on one-move flips.** It does not yet check that a patient exists in the source category to move — a row with `Low = 0` cannot lose a Low. **The availability constraint must be applied before the number is published.**
  2. ⚠ **No claim that Kathad's arithmetic is wrong. We reproduced every value exactly** (`D-100`). The finding is about the **stability of the filter's output**, not its correctness.
  3. ⚠ **Whether the paper's own limitations section states this is UNCHECKED** — the Planner has no search. *"They did not mention it"* is not a claim this entry makes. It decides whether the framing is *quantifying a stated caveat* or *identifying an unstated one*.
  4. **The antibody choice is a second, independent, unquantified source of movement.** **52.5% of HPA genes carry more than one antibody** (9,140 / 17,407, measured); S3 does not say which was used. **Additive to this finding, not included in it.**

- **Why it matters here.** `F-009` records four clinically-validated ADC targets as false negatives of this filter. ⚠ **Instability at the boundary is a MECHANISM that produces false negatives** — it turns four anecdotes into an expected behaviour. **It does not prove those four arose this way**, and checking whether they sit near the cutoff is a separate, pre-registerable measurement.

#### F-043 amendment 1 — ⚠⚠ THE FLIP RATES ARE WITHDRAWN. The perturbation rule was underspecified in the entry text.

- **Date:** 2026-08-17 · **Status:** ⚠ **The 83 / 33 / 116 and 151 / 85 / 236 figures MUST NOT BE CITED.** Withdrawn same day, before any external use.

- **What happened.** Code could not reproduce **83** under **any of five candidate perturbation rules, including the one the entry appears to describe.** The entry's prose says *"one patient reclassified by one category"*; the arithmetic behind the number was the distance test `|qh − 150| < 100/total`. ⚠ **Those diverge as soon as a single patient can move more than one category** — `Not detected → High` is three steps, not one — and **the entry states neither.**

- ⚠⚠ **This is the same defect the Planner required Code to fix twice on the same day.** A3 was re-run under **three type sets** and reported at **five values of *k*** on the ruling that *a single choice is a dial wearing the costume of a measurement.* **The Planner then published a single flip count under an unstated rule.** Recorded as a **Planner finding**, not absorbed.

- ⚠ **It is also `F-044`'s family, one level down:** a number in the log **whose definition cannot be recovered from the log.** `F-044` is about a citation resolving to the wrong content; this is a measurement resolving to no reconstructable method. **Both fail silently — the entry is well-formed, confident, and unreproducible.**

- **What SURVIVES, unaffected:**
  - ⚠ **52 pairs at exactly 150.0**; `≥150` → **337**, `>150` → **286**. **Depends on no perturbation rule.** This was already ruled the number that leads.
  - Panel sizes: median **11**, mean 10.2, max **12**; **246 of 1,640 rows at n ≤ 4**.
  - The **8 rounding flips** between raw counts and the paper's printed percent columns.
  - `D-100`'s reproduction — **337/337 and 1,303/1,303** — untouched.

- **The re-derivation, pre-registered here:**
  1. **All five candidate rules, reported side by side.** ⚠ **Enumerated in advance; no sixth is added after the results are seen.**
  2. **Availability-constrained and unconstrained for each.** ⚠ **The gap between them is the result**; Code measured **201 → 169** on the 337 under its own rule.
  3. ⚠⚠ **On the FULL v22 IHC grid — 20,082 genes × 20 cancers, 401,640 rows — with the reproducible funnel depths nested inside it** (5,543 membrane · 4,875 protein-level · 82/337). **`1,731` is NOT among them: stage 3 does not reproduce and is disclosed as a named gap, never approximated.**
  4. ⚠ **The 337 are survivorship-conditioned** — 82 genes that cleared four further filters *after* the cutoff fired. **A flip rate measured on them is conditioned on survival**, and the population the cutoff acted on is upstream.
  5. ⚠ **Directional hypothesis, recorded BEFORE measurement and not to be defended if it fails:** stage 6b requires qh > 150 on mRNA as well, which plausibly enriches the 82 for high expressers and pushes near-boundary pairs out — **so 24.6% may UNDERSTATE instability upstream.**

- ⚠ **`F-043`'s status returns to OPEN pending the re-derivation.** Nothing downstream cited the withdrawn figures; **`CLDN18.2` at 133.33, two available moves from 150, is independent of t** ⟵ ⚠ **TRANSMISSION TRUNCATED HERE, TWICE, AT THE IDENTICAL CHARACTER.** The tail was requested and re-sent unchanged. **Merged as received rather than completed by Code** — finishing an owner's sentence is inventing a ruling. **The tail is outstanding.**

##### ⚠ Code's note on merge — one surviving figure is refuted, and it is not corrected in place

- ⚠⚠ **`>150` → 286 is WRONG. The measurement is 285, and the inequality sign is worth 52 pairs, not 51.** All **52** boundary rows are float-**equal** to 150.0 and **none is float-above**, so `337 − 52 = 285` is forced. Re-verified at merge against S3 through `scripts/kathad_reproduction.py`.
- ⚠ **It is left as written in the bullet above and corrected here instead**, because *corrections are recorded, never patched away* — and because a withdrawal notice that silently edits its own surviving figures is the shape it exists to prevent.
- ⚠ **The finding is STRENGTHENED by one pair**, not weakened. The `52 at exactly 150.0` figure — the one ruled to lead — is unaffected and independently confirmed.


---

### F-041 — Two of the three candidate boundary sources cannot supply a boundary, and InterPro cannot supply a count either

- **Date:** 2026-08-17
- **Status:** ⚠ **OPEN** — it is a property of the instrument, and the instrument still exhibits it.
- **Evidence:** `scripts/tranche6_domain_survey.py` part 1; cache-wide verification over all **4,990** `data/census/spancache` entries.

- **Context:** D-091 ruling 3 and `PREWORK-2026-08-18.md` §3 frame tranche 6's first decision as a **choice among three sources** — *UniProt `Domain` vs Pfam vs InterPro* — warning that **they will not agree.** They do not agree. ⚠ **But that is not the finding.**

- ⚠⚠ **The comparison as posed cannot be run, because two of the three do not carry the object being compared.** In the UniProtKB cache: **UniProt `Domain`/`Repeat` features carry `start`/`end`**; **Pfam carries a count (`MatchStatus`) and no position**; **InterPro carries neither** — family membership only.

- **Cache-wide, with denominators:** **0 of 22,176** InterPro xrefs declare an instance count, against **8,251/8,251** for Pfam, **6,059/6,059** PROSITE, **3,200/3,200** SMART, and 100% for CDD, Gene3D, SUPFAM, PANTHER and FunFam. ⚠ **No database carries coordinates at any point in the cache.** All 4,990 files parsed; **zero counterexamples.** The check was written so that **one hit would have disqualified it**.

- ⚠ **This is a category difference, not a disagreement in number** — the **F-038** shape. Comparing FAT1's *"UniProt 39"* against *"InterPro 9"* compares **39 domain instances** against **9 family memberships**: two different objects, and the comparison would have looked entirely meaningful.

- **The absence has a cause, stated (the "every absence is a CATEGORY" rule):** InterPro's UniProtKB cross-reference is **entry-level by construction** — it records which families the protein belongs to, never how many times or where. ⚠ **The counts and coordinates exist upstream**, in the InterPro *matches* API and InterProScan, **a different instrument this project has never fetched.** So *"use InterPro boundaries"* is **not a parameter change but a new instrument**, with its own cache, provenance and freshness obligations (D-088).

- ⚠ **The disagreement does not even point in one direction.** PROSITE finds **63** where UniProt finds 39 (FAT1) and **8** where UniProt finds 42 (ADGRV1). No systematic offset reconciles them; the sources annotate different things.

- **Consequence:** D-095 decision 1 selects UniProt **by availability**, and ⚠ **that must be legible in the artifact** — otherwise a later reader takes `boundary_method` as a considered verdict that UniProt's annotation is *correct*, which it is not and which this evidence cannot support.

---

### F-040 — ESMFold folds MONOMERS, so an obligate oligomer's subunit interface is indistinguishable from an antibody-accessible patch

- **Date:** authored against a pre-D-076 snapshot · **entered this log:** 2026-08-17
- **Status:** ⚠ **OPEN — a finding against the instrument (D-074).** It stays open until ESMFold no longer exhibits it, **or** until every surface reporting features 6 and 7 carries the statement of what they get wrong.
- **Full text:** `docs/F-040-single-chain-oligomer-interface.md`
- ⚠⚠ **RENUMBERED: claimed `F-012`, already spent** by *ESMFold's chunked trunk is not output-invariant*. See `F-039`.

- **The finding:** the model predicts a **single chain**. Where a protein is an obligate oligomer, the surface that would be **buried against its partner** is rendered as exposed — ⚠ **indistinguishable, in the output, from a patch an antibody could reach.** Features 6 and 7 are therefore biased **in a direction**, not merely noisily.
- ⚠ **§2 is the entry:** it separates **what is established** (verifiable from code and the model definition) from **what is reasoned** (everything about magnitude and direction on *this* cohort). **§5 pre-registers the measurement that would settle magnitude, before it runs.**
- ⚠⚠ **§6: oligomeric state MUST NOT become feature 8, and MUST NOT filter anything.** The finding is a caveat on interpretation, **not a new axis** — adding it as a feature would convert a disclosure into a score.

- ⚠ **It is the same shape as `F-037`, one level down.** F-037: `span_aa` is the largest extracellular segment, not the extracellular content. F-040: the structure is a monomer, not the assembly. **Both are cases where the artifact is not the thing the reader assumes it is**, and neither is visible from the artifact alone.

---

### F-039 — Three staged documents arrived claiming numbers already written, and one claimed a filename already in use

- **Date:** 2026-08-17
- **Status:** ⚠ **CLOSED 2026-08-17 — merged as `D-093`, `D-094`, `F-040`.** The renumbering was done with both documents open, and the collision itself is what this entry records.
- **What happened:** five documents were delivered for `docs/`. Three are staged log entries, and **each claims an integer the live log has already spent**:

  | arrived as | claims | ⚠ live state |
  |---|---|---|
  | `D-079-clinical-association-layer.md` | `D-079` | **WRITTEN** — *the census: ingest 2,807 surface proteins…* |
  | `D-080-claim-discipline-educational-surfaces.md` | `D-080` | **RESERVED** — *a revert proof operates on committed state…* |
  | `F-012-single-chain-oligomer-interface.md` | `F-012` | **WRITTEN** — *ESMFold's chunked trunk is not output-invariant…* |

- ⚠ **This is not carelessness, and the documents say so themselves.** Each carries *"⚠ Confirm the number against the live log before merging"* and states the snapshot it was written against: **highest `### D-` is D-075**. The live log is at **D-092**. **They were authored against a tree seventeen decisions old** — the numbering is stale, not wrong, and the instruction to re-check is the thing that worked.

- ⚠⚠ **AND TWO DIFFERENT DOCUMENTS ARRIVED UNDER ONE FILENAME.** `CLOSEOUT-2026-08-17.md` exists twice: mine (state + the database incident, `048f447a…`, 8,959 B) and the Planner's (*"The disclosure arc"*, `4e3903e1…`, 13,632 B). ⚠ **Copying the incoming file in unchanged would have destroyed the other silently** — no error, no diff, one file. *A filename is not an identity* stops being a slogan here.

- **What was done, and what deliberately was not:**
  - All five **placed in `docs/`**, each with its **sha256 recorded above/below**.
  - The three staged entries **renamed to `STAGED-<subject>.md`** — ⚠ **the number is removed from the filename**, because a filename asserting `D-079` is a claim on an integer the file does not hold. The claim now lives only inside the document, where the merge step must resolve it.
  - The Planner's closeout renamed to **`CLOSEOUT-2026-08-17-planner-disclosure-arc.md`**.
  - ⚠ **Merged 2026-08-17 as `D-093` / `D-094` / `F-040`.** ⚠ **The authors’ snapshot notes were left EXACTLY as written** — they are true statements about the tree each author read, and rewriting one would falsify the provenance it exists to record. **The claim is corrected; the observation is not.** Sibling cross-references were renumbered with them **after reading every citation in context** — `F-012 §8` and *“D-079 decision 6’s supplier-before-contract rule”* resolve to the siblings, not to the spent entries, and a blind rename would have rewritten the meaning. ⚠ **NOT originally merged here.** Renumbering is a decision about what the entries *are*, and it belongs to whoever merges them with both documents open. **Next free: `D-093`, `D-094`, `F-039`** (this entry takes `F-039`; the staged findings take what remains).

- ⚠ **The contents are not reviewed here.** They concern a clinical-association layer, claim discipline in educational surfaces, and a single-chain/oligomer-interface finding against the instrument. **None of that has been checked against the current code**, and the census work of the last two days may bear on all three.

---

### F-038 — A census protein page displayed the COHORT's measured ceiling, and six census structures exceed it

- **Date:** 2026-08-16
- **Status:** fixed
- **What happened:** `ui/src/plddt.js` bakes the cohort's measured maximum into the top band's caveat — *"cohort max 84.23 — no target reaches the high-confidence range"* — and `Confidence` renders it wherever it appears. **D-089 put `Confidence` on census protein pages**, so a census structure was shown beside a ceiling belonging to a different population.

- **Measured, after tranche 4 drained:**

  | population | max mean pLDDT | rows > 84.23 | rows ≥ 90 |
  |---|---|---|---|
  | cohort (the 82) | **84.23** | 0 | 0 |
  | ⚠ **census** | **89.25** | **6** | 0 |

  ⚠⚠ **Six census structures already exceed the ceiling the page was quoting at them**, and the highest is 89.25 — within one point of the high-confidence band the caveat says nothing reaches.

- ⚠ **The claim was never false; it was about the wrong population.** *"Cohort max 84.23"* is exactly true of the 82. Shown on a census page it describes a set the protein is not in — the same shape as the tranche-filter leaks (`_folded_accessions`, `_failed_accessions`), one surface silently answering with another population's numbers.

- ⚠ **The count that found it was not looking for it.** The owner asked for a low-pLDDT tally at tranche 4's drain; `max 89.2` in the output is what did not fit. **Same pattern as every serious defect this project has caught — a check that existed to find something else.**

- **Fixed:** `Confidence` takes an optional `caveat`. ⚠ **Passing nothing keeps the cohort behaviour byte-for-byte**, so target pages are untouched. The census page supplies its own, and ⚠ **quotes NO census maximum** — that number moves every time a tranche completes, and one baked in here would go stale in silence, which is the D-088 trap one layer up.

- ⚠ **The test found a SECOND instance the fix had missed.** `PlddtExplainer` also printed `COHORT_MAX_PLDDT`, and it is rendered on the same page — so the first fix closed one leak and left its twin. `showCohortMax` now gates it; the *"why the scores run lower"* explanation is about the **method** and is population-independent, so only the number is conditional.

- **Evidence:** 3 tests on the page + 4 new on `Confidence` (a file that did not exist). ⚠ **`caveat=""` SUPPRESSES the note rather than falling back to the cohort's** — a caller saying *"this population has nothing to add"* must not have the removed claim restated for them. UI **213 passed** across 31 files. Revert proof: removing the override reds 2.

---

### F-037 — `span_aa` is the LARGEST extracellular segment, not the extracellular content, and 47.6% of the census has more than one

- **Date:** 2026-08-16
- **Status:** open — ⚠ **no span, fold or artifact is wrong; what was missing is the CONTEXT beside them.**
- **What is true:** `core/span_extract.extract()` keeps the longest accepted topological domain — `if best is None or n > best` — and **silently discards every other one**. For a single-pass receptor the longest segment *is* the ectodomain and the two are the same thing. ⚠ **For a multi-pass protein it is one loop out of several**, and no artifact said which case a row was.

- **Measured, cache-only, no span altered:**

  | topology | rows | |
  |---|---|---|
  | `contiguous` (1 segment) | 1,693 | 48.8% |
  | ⚠ **`intermittent` (>1 segment)** | **1,649** | **47.6%** |
  | `no_accepted_segment` (GPI — a different architecture, D-081) | 125 | 3.6% |

  ⚠⚠ **92,709 residues of extracellular material are discarded.** Worst: `Q9UHC9` — **7 segments, 830 aa extracellular, 272 folded, 558 discarded.**

- ⚠ **Why it matters here specifically.** A reader seeing `span_aa = 272` reasonably reads *"the extracellular region is 272 aa."* For `Q9UHC9` the extracellular region is **830 aa across 7 segments** and 272 is the biggest one. **An antibody can bind a conformational epitope spanning several loops — a structure of one loop in isolation is not a model of that site.** On an ADC platform that is the difference between a candidate and an artifact.

- **And it is visible in the confidence numbers.** Across **2,510 folded rows** joined to the segment derivation:

  | topology | n | median pLDDT | below 50 |
  |---|---|---|---|
  | contiguous | 879 | **67.9** | 13.1% |
  | ⚠ **intermittent** | 1,556 | **50.9** | **45.4%** |
  | GPI | 75 | 70.5 | 4.0% |

  ⚠⚠ **Intermittent spans are ~3.5× more likely to fold below 50.**

- ⚠ **CAUSATION IS NOT CLAIMED, and the data cannot separate the two explanations:** (a) a fragment folded out of its structural context predicts worse, or (b) the extracellular loops of multi-pass proteins are genuinely short and flexible, so a low score is the correct answer. **Both are plausible, both are informative, and they lead to the same practical conclusion** — an intermittent span's structure is a weaker basis for epitope work — **but they are different claims and only one of them is about our method.** Separating them needs a re-fold of a segment in context, which has not been done.

- **Remedy:** `scripts/span_segments.py` → `data/census/span_segments.csv` — **context only, nothing behind it altered.** ⚠ The topology is a **word** (`contiguous` / `intermittent` / `no_accepted_segment`), never a bare integer: *"1"* and *"7"* mean different things to someone deciding whether a structure models a binding site, and a count invites the reader to do that reasoning unaided.

- ⚠ **`no_accepted_segment` is NOT "intermittent" and NOT a defect.** GPI-anchored proteins have no topological domains **by design** and take their own rule (D-081). Collapsing them into a segment count would report a different molecular architecture as missing data — ⚠ the exact `no_topology` conflation `F-025` was about.

---

### F-036 — A row that was never fetched carries an EMPTY span_category, so "unknown" and "has a span" are the same filter

- **Date:** 2026-08-16
- **Status:** open
- **What happened:** accounting for all 5,016 census rows under V2, every no-span row carries a `span_category` — `no_extracellular_span` (1,519), `absent_with_reason` (3), `span_boundary_unknown` (1). ⚠ **Except 26.** The `uniprot_inactive` rows — never fetched — have **`span_category = ''`**, the same value carried by every row that *does* have a span.

- **Measured:**

  | | rows |
  |---|---|
  | `span_category == ''` | **3,493** |
  | …of which actually carry a span | 3,467 |
  | ⚠ …of which carry **no span, never fetched** | **26** |

  ⚠ **A consumer filtering `span_category == ''` to mean "has a span" silently picks up 26 rows that were never looked at.**

- **Why it matters, and it is the project's own rule:** *an absent value is a CATEGORY, never a low number and never a bare null.* ⚠ **`uniprot_inactive` is not "no extracellular span" — it is "we do not know."** Absence of evidence against evidence of absence, and the two lead to opposite actions: one is a correct permanent exclusion, the other is **resolvable by fetching**. Collapsing them into the same empty string is exactly the `no_topology` defect that `F-025` was about — **one band meaning several things** — reappearing in the field that was supposed to have fixed it.

- ⚠ **The `no_span_reason` column DOES carry it** (`not fetched: uniprot_inactive`), so the information survives. **That is what makes this a defect rather than a data loss** — and also what makes it easy to miss: the row looks complete until you filter on the wrong one of the two columns.

- ⚠ **It has not bitten.** `census_manifest.v7.csv` is built from rows that **have a span**, not from `span_category == ''`, so no unfetched row ever reached a tranche — confirmed both directions: `span but not in manifest = 0`, `manifest but no span = 0`. **The manifest is correct by a different predicate than the one that is wrong**, which is luck, not design.

- **Remedy (not implemented):** give the 26 a category of their own — `absent_not_fetched`, or `identity_inactive`. ⚠ **Do NOT reuse `absent_with_reason`**: that means *"parsed, and refused for a stated reason"*, which is a claim about the entry's content. **These were never parsed at all.**

- ⚠ **A ruling is wanted on the 26 themselves, separately from the column.** They are UniProt-inactive accessions — merged or withdrawn. Whether the census should follow the merge targets, or record them permanently as inactive-at-this-release, is a **scope decision, not a bug fix**, and it interacts with the *"two facts, never one date"* rule: re-fetching 26 rows would put a second fetch date in a file whose whole provenance model forbids that.

- ⚠⚠ **A TEST HELD THE DEFECT IN PLACE, and it is recorded here rather than taking its own integer** (an eighth integer under momentum is the F-025 defect). `test_a_never_fetched_row_takes_no_v2_category_and_keeps_its_reason` **asserted `span_category == ""`** — so the blank was not merely emitted, it was **pinned**, in the test file whose entire subject is not asserting things about data that did not move. ⚠ **A test can hold a defect as firmly as it holds a behaviour**, and a gate that is green because it agrees with the bug is a gate that has stopped being evidence. It now asserts the identity category and **still** asserts the half that was always right: no span invented, no `parsed_under` stamped.

- **Detail:** `docs/CENSUS-ACCOUNTING-V2.md`.

---

### F-035 — The local/rental routing is computed by the manifest and enforced by nobody

- **Date:** 2026-08-16
- **Status:** ⚠ **claim-time filter CLOSED 2026-08-17 (D-090). Remedy item 3 — the independent length guard — REMAINS OPEN**, and the reason is stated below rather than left as an unticked box.
- **What is true:** `core/manifest.py` decides `local` vs `rental` per row, records `tier_reason`, and `TIER_RECIPE` resolves the recipe from it **at claim time** (D-047) — `local → int8`, `rental → fp16`. ⚠ **And `core/queue.py:claim()` selects `WHERE status = 'pending' ORDER BY created_at, id`. No tier. No length.** A worker takes the oldest pending job, whatever it is.

- ⚠⚠ **It has never bitten because no rental row has ever been ingested.** The only thing keeping rental work off the local card is that **none exists yet** — *an operational convention doing a guard's job*, holding exactly until someone runs the obvious next command.

- **What it would cost the moment tranche 5 lands:** 776 rows, all `tier=rental`, 441–14,451 aa, resolving **`fp16`**, against a card measured at **8,150 MiB total** with `known_good = 440` **at int8**. ⚠⚠ **An fp16 probe is what bugchecked this host on 2026-08-12**, and on WDDM the over-allocation is not refused — the driver spills to system memory and faults in kernel mode. ⚠ **D-082 layer 3 does not survive that.** ⚠ **FIFO is a delay, not a safeguard**: those rows would be claimed the instant tranche 4 drained, most likely unattended.

- **Remedy (proposed, NOT implemented — tranche 4 is mid-flight and the claim path is untouched):**
  1. `WORKER_TIER`, **defaulting to `local`** — ⚠ wrongly refusing work costs an idle GPU; wrongly accepting it costs a host.
  2. ⚠ **Filtered IN THE SQL, never checked after the claim.** A post-claim refusal marks the job `claimed` then declines it — the shape that stranded ten jobs: `attempts=0`, no error, nothing retryable.
  3. **An independent length guard at fold time.** ⚠ Tier is a *label*; length is the physical constraint. `vram_guard.preflight()` already returns `REFUSED_NO_MEASUREMENT` and is **simply not wired in**.
  4. **State the composition on refusal** — ⚠ an idle worker and an empty queue must never look identical.

- **CLOSED (D-090):** `jobs.tier` (migration `0009`), filtered **inside the claim SQL** — `AND tier = :tier`, never `OR tier IS NULL`. `WORKER_TIER` defaults to `local`. Production migrated at **0 pending / 0 claimed**, backfilled to **2,733 local + 38 rental, 0 untagged**.

- ⚠ **STILL OPEN — remedy item 3, the length guard.** Tier is a *label*; length is the physical constraint, and a mislabelled row must still be refused. `vram_guard.preflight()` exists and is **not wired in**. ⚠ **It cannot simply be switched on**: it returns `REFUSED_NO_MEASUREMENT` for any unmeasured length, and **no ceiling has been measured for rental hardware** — so wiring it today would refuse every legitimate rental fold. **It needs a `ceiling_climb` on the rented card first**, which is part of the rental arc and has not begun. **Recorded as open rather than ticked off.**

- **Detail:** `docs/PROPOSAL-claim-tier-filter-and-tranche-5-cost.md`, which also carries the tranche-5 cost model and the §3 correction retracting *"impossible"*.

---

### F-034 — The verification harness would have triggered the failure it was built to verify against

- **Date:** 2026-08-16
- **Status:** fixed
- **What happened:** `scripts/supervisor_equivalence.py` — the gate that had to pass before layer 3 could be switched on — folded **`sequence_from_cache(accession)`, the FULL protein**, not the manifest span.

  ⚠⚠ **`Q8N423`'s span is 439 aa. Its full chain is 597 aa — well past the measured 440 ceiling.** Had that accession been chosen, **the tool proving it was safe to enable the VRAM-death guard would itself have folded 597 residues on a card whose ceiling is 440** — risking the exact failure layer 3 exists to catch, **before layer 3 was on**, on a host that bugchecked four days earlier.

- ⚠ **It was caught by checking the input, not by the tool objecting.** Nothing in the harness compared the fold length to the ceiling; the check happened because the accession's length was looked up before folding it. **`Q6ZVN8` was under 440 by luck (426 aa full), so the run would have gone green and taught nothing.**

- **Why the defect existed:** the harness was written to answer *"does the supervisor change the structure?"*, and **any sequence answers that.** ⚠ **So the sequence was chosen for convenience rather than fidelity** — and a verification that does not fold what the worker folds is not measuring the workload it is clearing.

- **Fixed:** it now folds the **manifest span** with `source='sliced_ecd'` and the same coordinates the worker uses; asserts the slice length equals `span_aa` (a disagreement is a construction defect, not a rounding difference); and ⚠ **REFUSES anything past `CEILING_AA = 440`** — *a verification that triggers the failure it is verifying against is worthless.*

- ⚠ **A second defect in the same instrument, recorded here rather than given its own integer** (taking an integer under momentum is the F-025 defect): `compare_folds` takes **mappings with `coords` and `plddt`**, not PDB text. The first call passed strings and died in `fold["coords"]`. ⚠ **It was fixed by reading the contract, NOT by removing the call** — deleting the comparison would have left the sha256 as the only evidence, and a byte hash over a rendered file is a weaker claim than CA coordinates compared with no tolerance. **Both arms were then re-run, so the evidence comes from the code that ships rather than the code that was repaired.**

- **The class:** ⚠ **both defects were in the instrument, and both were invisible until it was run against real data.** Same shape as `ceiling_probe._attempt` (an `except` that never runs because there is no process left) and the revert proof that performed the `setattr` itself. **An instrument is code, and code that has never been exercised against the real case is a hypothesis.**

- **Evidence:** gate 655 passed, 15 skipped, exit code 0. The corrected harness produced `byte-identical PDB | True` and `compare_folds | identical` on `Q6ZVN8` (364 aa span, 36–399 of 426).

---

### F-033 — A residue the tokenizer has no word for fails as a tensor-shape complaint, not as "this protein cannot be folded"

- **Date:** 2026-08-16
- **Status:** open — ⚠ **the row is correctly `failed`; what is open is the VOCABULARY, not the outcome.**
- **What happened:** the first failure in 2,359 census folds. `P55073`, tranche 3, span 68–304:

  ```
  unexpected fold failure: Unable to create tensor, you should probably activate truncation
  and/or padding with 'padding=True' 'truncation=True' to have batched tensors with the same
  length. Perhaps your features (`input_ids`) have excessive nesting …
  ```

  ⚠ **Nothing in that message is true of the actual problem.** It names truncation, padding and batching. The span needs none of them. **The span contains `U` — selenocysteine**, the 21st amino acid, and **`U` is not in the ESM vocabulary.**

- **Measured, not inferred** (the message is so misleading that inference would have been a guess):

  | probe | result |
  |---|---|
  | 20 standard residues | OK, `shape=(1, 10)` |
  | same + `U` | ⚠ **raises `ValueError`, the exact production message** |
  | same + `X` | OK, `shape=(1, 21)` |
  | `"U" in tok.get_vocab()` | **False** |
  | `"X" in tok.get_vocab()` | **True** |

  ⚠ **`X` — "unknown residue" — is IN the vocabulary and folds.** So the model has a word for *"I don't know what this is"* and no word for *"this is selenocysteine."* `tokenize("U")` returns `['U']` and then converts to `None`, and the `None` is what the nesting complaint is actually about — **three layers away from the cause.**

- **Bounded, and the bound was measured across every tranche before any conclusion:** **1 span of 3,467** contains a non-standard residue. It is this one, the residue is `U`, and **tranches 4 and 5 contain none.** ⚠ **This is not a wave; it is a single row**, and that is a measurement rather than a hope.

- **Why it is a finding even though the outcome was correct:** the job **is** `failed`, with the error stored — D-024 held, and the crank did not stop. ⚠ **But the recorded reason is a lie about the cause.** A future reader debugging *"excessive nesting"* would look at batching, padding and the enqueue path — **none of which is involved.** The project's own rule is that an absent value is a **CATEGORY**: *"cannot be folded: contains selenocysteine, absent from the model vocabulary"* is a category; *"Unable to create tensor"* is noise that happens to be red.

- ⚠ **NOT fixed, and deliberately not, mid-crank.** A guard belongs at **ingest**, where `MUC16` and `FAT2` are already named exclusions with stated reasons (D-022) — the precedent exists and this is the same shape. But tranche 3 is **already ingested and folding**, changing the ingest path now would alter nothing for the row that failed, and **the population would then span two versions of the enqueue rule mid-tranche.** ⚠ Same reasoning as D-084. **Owner ruling wanted** on whether `P55073` becomes a third named exclusion or the guard becomes general.

---

### F-032 — A dry run that does not exercise its consumer's contract is not a dry run

- **Date:** 2026-08-16 · **Status:** Accepted. **Closed under D-074** — the instrument no longer
  exhibits it: `scripts/census_ingest.py` builds the consumer's object before any write.
- **⚠ Number verified live.** Highest `### F-` written was F-025; F-026–F-032 appeared nowhere in
  the log, `docs/RESERVED.md` or `ARCHITECTURE.md`.
- **Provenance (D-016):** Code's reading of the production database, 2026-08-16.

**The census ingest's dry run validated slices, spans and every DB invariant — and omitted
`model_revision` from `inference_settings`.** `/claim` subscripts `s["model_revision"]`, raised
`KeyError`, and did so **after** marking each job `claimed`. ⚠ **Ten jobs became permanently stuck:
`attempts=0`, no error recorded, nothing retryable, GPU idle at 0 MiB.**

⚠⚠ **The dry run passed because it never called the consumer it was writing for.** It checked the
producer's internal consistency and stopped there. ⚠ **And the pre-registration named the field
correctly — *"model id/revision"* — while the code implemented half of it**, so the document was
right and the artifact did not match it.

⚠ **At 1,307 rows this would have been 1,307 silently stuck jobs.** A failure that leaves **no trace
in the row** is worse than one that fails loudly: a failed job is visible and retryable; a job
marked `claimed` and abandoned looks like work in progress forever.

**Remedy:** the producer **constructs the consumer's object before any write**, and the test reads
the required keys **out of the consumer's source** — ⚠ **never a hand-kept list, because a
hand-kept list is exactly what drifted.**

---

### F-031 — Two populations in one table, joined on a key that is no longer unique

- **Date:** 2026-08-16 · **Status:** Accepted. **Closed under D-074** — every `select(ProteinAnalysis…)`
  in `app/` is tranche-filtered, enumerated by test.
- **Provenance (D-016):** measured **before** the first census row was written.

**75 of the 82 cohort accessions also appear in the census manifest; all 82 appear in the roster** —
`P04626` HER2, `P00533` EGFR, `Q13421` MSLN, `P11717` IGF2R, `Q8WXI7` MUC16 among them.

`coverage_payload` iterates the 82 and looks each accession up in a dict built from the database.
⚠ **Two of those dict-builders were not tranche-filtered.** The first census fold of `P04626` would
have put a **census** `analysis_id` under HER2's accession, and the cohort's coverage row would then
point at a fold measured under a **different span definition**.

⚠⚠ **It would have overwritten a reported result** — `coverage` is a tranche-zero surface and the
82's fold status feeds `### F-004`'s denominators. **Not appeared beside; overwritten.**

⚠ **And there is no `ORDER BY`**, so with a cohort row and a census row sharing an accession the
surviving entry is **whatever the database returns last — nondeterministic, and silently so.**

⚠ **The general form: adding a second population to a table silently re-types every key that was
unique in the first.** `input_value` did not change; what it *means* did.

---

### F-030 — The unsafe branch was the default, reached by omission

- **Date:** 2026-08-16 · **Status:** Accepted. **Closed under D-074** — an unrecognised
  `boundary_method` now raises; `whole` is an explicit opt-in.

`core/enqueue.py:_fold_input` branched on `boundary_method`, **not on the presence of coordinates**:

```
'sliced_ecd'                    -> AssertionError raised                    ✅
'whole' / '' / None / anything  -> folded 2,000 residues, source='whole'   ⚠ nothing red
```

⚠ **The safe branch required an exact literal. Every other value — including absence — fell through
to folding the whole sequence.** And the census manifest carried **no `boundary_method` column at
all**, so any ingest would have had to supply one.

⚠⚠ **`whole` is a LEGITIMATE recorded outcome** (D-024 routes whole-method targets to it), so
**3,468 census proteins would have folded full-length with every artifact internally consistent** —
fold succeeds, recipe recorded, provenance intact, `source='whole'`. **Nothing red anywhere.**

⚠ **The general form: when a fall-through is a valid outcome rather than an error, omission becomes
indistinguishable from choice.** The remedy is that both branches cost a keystroke.

⚠ **And the coordinate check was an `assert`** — see `### F-029`.

---

### F-029 — `assert` used as a guard vanishes under an optimisation flag

- **Date:** 2026-08-16 · **Status:** Accepted. ⚠ **NOT closed under D-074** — four remain in
  `scripts/`, ruled for conversion. **Latent, not live**: neither script is run by CI or the crank,
  and nothing in the repo passes `-O`.

**`python -O` strips every `assert`.** A check written as one is **a comment that occasionally
runs** — and it is invisible when it stops running.

**Found in the fold path**, where an `assert` stood between a manifest span and a 2,000-residue
fold. **Still present in two scripts**, and ⚠ **the sharpest case is `scripts/intersection_check.py`,
whose own comment reads *"if it stops reconciling, the reports below are unsafe"*: under `-O` that
check evaluates to nothing and the unsafe reports print anyway.** ⚠ **A checker whose checks are
asserts has an entire output that is a claim that verification happened.**

**The rule:** ⚠ **any check whose failure would produce a wrong artifact raises an explicit
exception.** `assert` is for internal invariants whose violation is a crash — never for a guard
standing between a claim and a result.

---

### F-028 — An order that asks for confirmation invites confirmation

- **Date:** 2026-08-06 (reserved) · 2026-08-16 (written) · **Status:** Accepted. **Process finding;
  no instrument to close under D-074.**

**An instruction phrased as *"confirm that X"* asks a different question from *"what is X?"** — and
the first is answered agreeably far more often than the second. Instances this project logged
include a span audit ordered over **twelve** proteins where the data held **thirteen**: the
selection criterion was inherited from the order rather than re-derived, and ⚠ **the criterion chosen
to find the defect was blind to one instance of it.**

⚠ **The remedy is not scepticism, it is RE-DERIVATION**: the receiving party recomputes the
population from the source and reports the count **before** answering the question asked of it. Where
the order's list and the derived list disagree, **the disagreement is the finding.**

---

### F-027 — Derive from source, not from context

- **Date:** 2026-08-06 (reserved) · 2026-08-16 (written) · **Status:** Accepted. **Closed under
  D-074** for the instance that produced it — the relocation was redone from the source document.

**A block relocated within the decision log was reconstructed from conversational context rather
than re-extracted from the source**, and it silently lost a trailing separator: `### D-071` hashed
`371e7127` before and `e4283d60` after.

⚠ **The content looked right.** A reconstruction from memory of a thing one has just read is the
hardest kind of error to see, because the reader supplies from context exactly what the artifact is
missing. **The remedy is mechanical: re-extract from the source file, never retype from the
conversation** — and hash both sides.

---

### F-026 — A verification that shares an implementation with its subject verifies nothing

- **Date:** 2026-08-06 (reserved) · 2026-08-16 (written) · **Status:** Accepted. ⚠ **Recurred on
  2026-08-16 and was caught by a revert**, which is the only reason it is closable.

**A check built on the same code as the thing it checks cannot disagree with it.**

⚠ **The 2026-08-16 recurrence is the cleanest instance this project has:** a test asserting that
`fold()` assigns its environment from a dict **performed the assignment loop inside the test itself**.
It exercised the loop **in the test**, not the one in `fold()` — so reverting `fold()` to the broken
hand-written version left the test **green**. **A-017 clause (a): the fixture never reached the code
under test.**

⚠ **The same shape in data:** a residue count read from a field recorded beside a claim cannot
disagree with the claim; it must be **read out of the artifact** — which is why `reconcile_fold`
parses the PDB rather than trusting `fold_length`.

**Remedy:** the verifier and the subject must not share an implementation — and where they must
(a GPU-only path), ⚠ **assert over the subject's SOURCE**, and **prove by revert**, because a revert
that leaves the suite green is the only way this defect announces itself.

---

### F-025 — `no_topology` reported an absence that was five different things: a band name that made a claim its filter could not support

- **Date:** 2026-08-07
- **Status:** Accepted. ⚠ **NOT closed under D-074** — the instrument still exhibits it at the moment
  this is written, and the rename and the re-extraction land in the same arc but not in this entry.
  It closes when `scripts/ecd_lengths.py` no longer produces a band called `no_topology`, or when the
  band carries a statement of what it gets wrong.
- **Type:** An **instrument finding**. It is about what the extractor measures, not about the biology
  it was pointed at.
- **⚠ Number verified live, not inherited — and the verification found a second thing.** The highest
  `### F-` written was **F-020**; `F-021`–`F-024` are reserved and unwritten; **F-025 is the next free
  integer.** ⚠ **But `F-025` appears nowhere in `docs/RESERVED.md`, `docs/README.md` or
  `ARCHITECTURE.md` — zero occurrences.** It was claimed in commit `ba1e687` and in PR #133 on the
  strength of a chat message, and **there was no reservation row to strike.** The owner's
  `RULINGS-2026-08-07-span-definition.md` R5 ratifies it: *a Planner chat message cannot ratify what a
  committed document reserved.* Recorded because a number taken outside the register and later found
  to be free is right by luck, not by procedure.
- **Provenance (D-016):** every count is Code's reading, off
  `data/census/spancache` (5,009 cached UniProt entry JSONs, **0 fetches**),
  `data/census/spans_annex.csv`, `data/census/spans_surface.csv` and `data/cohort_82_ecd.csv`.
  Instrument: `scripts/span_extraction_audit.py`. Output verbatim:
  `docs/AUDIT-OUTPUT-2026-08-07-span-extraction.txt`. Superseding correction:
  `docs/CORRECTION-2026-08-06-no-topology-is-not-no-topology.md`.

- **Context.** `scripts/ecd_lengths.py:194-196`:

  ```python
  if feat.get("type") != "Topological domain":
      continue
  description = feat.get("description", "") or ""
  if "extracellular" not in description.lower():
      continue
  ```

  ⚠ **What is measured is *no `Topological domain` whose description contains the substring
  "extracellular"*.** The band was called `no_topology`, and that name was used interchangeably with
  *"this protein has no reachable domain"* in the span reports, in two hypotheses built on top, and in
  a commit message that reached `main`.

- **Finding — the band reported FIVE different things, and only one of them is "no topology":**

  | | Mechanism | Annex | Surface | What fixes it |
  |---|---|---|---|---|
  | 1 | A reachable face under other vocabulary (`Lumenal`, `Vesicular`, `Exoplasmic loop`, …) | 553 | 106 | Widen the term list |
  | 2 | `Transmembrane` present, faces never labelled | 734 | 197 | ⚠ **Nothing — a genuine annotation gap** |
  | 3 | GPI-anchored: no topology **by design** | 1 | 125 | A different extraction rule |
  | 4 | Only an unreachable or cytoplasmic face | 199 | 15 | Correctly excluded |
  | 5 | ⚠ Term matched, **coordinate `UNKNOWN`** | 0 | 1 | A coordinate rule |

  Counts are proteins, and the columns sum to the populations they came from: **1,858 annex** and
  **448 surface** (mechanism 3 and 5 are drawn from within mechanism 4's and the neither-bucket's
  rows; the audit output carries the full reconciliation).

- ⚠ **Mechanism 5 is the one nobody was looking for, and it is the F-020 shape.** `Q7Z5N4` SDK1
  carries `Topological domain 'Extracellular'` with
  `{"start": {"value": null, "modifier": "UNKNOWN"}, "end": {"value": 2009, "modifier": "EXACT"}}`.
  **The current filter matches it** — the description does contain *extracellular*. `parse()` admits
  `Span(start=None, end=2009)`, `largest_span` returns `None` because it cannot subtract a null, and
  the row reports `no_topology`. **A 2,009 aa ECD that UniProt did annotate as extracellular, lost to
  a coordinate modifier rather than to a word.** An absent *measurement* reported as absence of the
  *thing*. n=1 census-wide.

- ⚠ **And the selector used to look for the problem masked it.** The audit was ordered over *twelve*
  of the 82 with `n_extracellular_spans == 0`. Re-deriving on the field that actually drives the
  pipeline — a blank `largest_span_aa` — returns **thirteen**. SDK1's `n_extracellular_spans` is
  **1**: it matched, and it still has no span. **The criterion chosen to find the defect was blind to
  one instance of it.**

- **The 82, all thirteen, bucketed:** **1** vocabulary 3 *(IGF2R, TLR3, TMEM30A)* · **2** annotation
  gap 6 *(CLCNKB, ENPP5, FRRS1, SLC44A3, TMEM108, UGT8)* · **3** GPI 3 *(GPC1, MSLN, TNFRSF10C)* ·
  **5** coordinate 1 *(SDK1)* · ⚠ **4 — not a membrane protein: EMPTY.** **Every one of the thirteen
  has membrane evidence. None was correctly excluded.**

- ⚠⚠ **`MSLN` is out of the ranking set by an extraction failure, not by a labelling decision.**
  `Q13421` carries `Lipidation` `'GPI-anchor amidated serine'` at 598, **no** `Transmembrane`, **no**
  `Topological domain`, and a `Signal` peptide — attached by a lipid tail, crossing nothing, mature
  chain entirely extracellular. UniProt records a GPI anchor as a **lipid-moiety-binding site**, which
  is a feature type the extractor's topology model cannot produce. MSLN and `GPC1` both carry Kathad
  evidence score 4, and `data/adc_reference_mapping.csv`'s own carve-out names MSLN as absent because
  **unverified, not negative**. **So `n=12` — the binding constraint on every claim this project
  makes — is partly an artifact of this filter.**

- ⚠ **Both foldable counts are FLOORS, not populations.** `2,352` surface and `332` annex count only
  proteins with an explicitly *extracellular* span. **The surface class leaks too** — 106 surface
  proteins have a reachable face and are counted today as having none.

- ⚠⚠ **AND MECHANISM 5 WAS ALREADY KNOWN — IN A DOCSTRING — FOR THREE WEEKS.** `core/manifest.py`'s
  module docstring, written for **D-024 v** on 2026-07-22, says in as many words:

  > *SDK1 (Q7Z5N4) has n_spans==1 but null bounds (`None-2009(None)`), so it is `whole` — keying off
  > n_spans would slice a None (D-024 v).*

  **The behaviour was correct.** The manifest routed SDK1 to a whole-sequence fold rather than
  slicing a null, and it named the accession, the shape and the hazard. ⚠ **What was wrong was the
  LABEL, and the label is what everyone read.** The band went on calling it `no_topology` — an
  absence of topology — while the code three modules away knew the topology was present and only a
  coordinate was missing. **Mechanism 5 had to be rediscovered from the other end, by an audit that
  found thirteen where the order said twelve.**

  ⚠ **This is KEEL-4's Principle 11 scar verbatim: a hazard written into a code comment and left
  live for weeks, because writing it down felt like handling it.** **Recording a hazard in a
  docstring is not guarding it.** The guard is the category — `span_boundary_unknown` — and it did
  not exist until today. **No number is taken for this; it is a clause of this finding.**

- ⚠⚠ **AND THE SIXTH MECHANISM WAS IN THE FIX, NOT IN THE FILTER — `Q13421` MSLN.** The GPI span
  rule selected the mature chain by `min(Chain start)`, which on mesothelin took **37** and produced
  a **561 aa** span. Mesothelin is made as a precursor: the N-terminal megakaryocyte-potentiating
  factor is cleaved and **secreted**, so ~250 of those residues are never on the cell. ⚠ **On the
  protein this finding is named after, and it would have folded, scored, banded and looked entirely
  normal.** `P51654`'s −195 and MSLN's +250 are the same defect at opposite ends of the molecule —
  rule B was barred for over-reading the C-terminus, and this is its N-terminal twin, **live while
  B never fired.**

  ⚠ **The first correction was also wrong, and it is recorded rather than replaced.** Selecting the
  chain whose **end** coincides with the anchor conflated two jobs — disambiguating among chains,
  and testing whether a chain is valid at all — and it **excluded `P06731` CEACAM5, one of
  `### F-009`'s four clinically-validated missing targets, on a nine-residue end mismatch at a
  boundary rule A never reads.** An exclusion on annotation *form* rather than on biology.
  **The Planner wrote that ruling and corrected it.**

  The rule is now one rule: **the chains that CONTAIN the anchor; among them, the LATEST start.**
  ⚠ Latest start is conservative, not arbitrary: annotating both `Mesothelin` 37-598 and
  `Mesothelin, cleaved form` 296-598 is an assertion that 37-295 *can be removed*. **The rule can
  only under-read, and over-reading is what folds things that are not there.** MSLN lands at
  **302 aa**, the mature form the ADCs bind; CEACAM5 returns at **641 aa**.

- ⚠⚠ **THE LARGEST CLAUSE, AND IT IS NOT ABOUT THE FILTER: THE CENSUS FOLD PATH WOULD HAVE FOLDED
  3,468 FULL-LENGTH SEQUENCES INSTEAD OF EXTRACELLULAR DOMAINS.** `core/enqueue.py:81` branched on
  `boundary_method`, **not on the presence of coordinates**. The safe branch required the exact
  literal `"sliced_ecd"`; **the unsafe branch was the default, reached by omission.** Measured
  2026-08-07 — a census row carrying `span_aa=302` and no coordinates:

  ```
  boundary_method='sliced_ecd'  -> AssertionError raised                    ✅
  boundary_method='whole'       -> folded 2000 residues, source='whole'   ⚠ nothing red
  boundary_method=''            -> folded 2000 residues, source='whole'   ⚠ nothing red
  boundary_method='census_span' -> folded 2000 residues, source='whole'   ⚠ nothing red
  boundary_method=None          -> folded 2000 residues, source='whole'   ⚠ nothing red
  ```

  **And the census manifest carried no `boundary_method` column at all**, so any ingest would have
  had to supply one. ⚠ **`whole` is a legitimate recorded outcome** — D-024 routes whole-method
  targets to it — so every artifact would have been internally consistent: fold succeeds, recipe
  recorded, provenance intact, `source='whole'`. **Describing the wrong molecule, 3,468 times, with
  nothing red anywhere.**

  ⚠ **Found because a specified content-hash tuple named `span_start` and `span_end`, and building
  it found there were none.** A specification acting as an audit. The manifest had only `span_aa` —
  **a length, which cannot slice a sequence.**

- ⚠ **A reporting trap this produced, recorded because it nearly passed.** Manifest revision 1 and
  revision 3 have **identical membership (3,468) and an identical fold order — 3,468 of 3,468 —
  while two spans differ**: `P51654` 529→195 and `Q13421` 561→302. The seeded shuffle keys on the
  accession set, not on span values, so **an unchanged fold order is not evidence of an unchanged
  manifest.** A reader diffing the two by row count, membership or order would have concluded that
  nothing moved, on the revision where the whole point of the day's work moved.

- **Consequences.** The band is renamed to what it measures; the vocabulary, the GPI rule and the
  coordinate category are ruled in `RULINGS-2026-08-07-span-definition.md` and implemented against the
  census only. ⚠ **The 82 are frozen — `### D-081`.** The annex's 84.8% is largely an instrument
  artifact rather than a finding about UniProt's coverage, and **the `### F-016` collision dissolves**:
  the table can be the whole membraneome, these can be properly annotated membrane proteins, and they
  still read `no_topology` under a filter looking for one word.

---

### F-017 — The confidence-blind structural axis recovers what `no_plddt` lost: Decision 4 row 1 fired, and the proxy that never reads confidence is nonetheless correlated with it

> **The fired row, quoted from `docs/README.md` §D-075 Decision (4), before any prose:**
>
> | **All three of `geom_proxy`'s statistics sit toward FULL** (median ≳0.6071, mean ≳0.6176, count 8-of-12) — the proxy recovers what `no_plddt` lost | **Confound weakened.** The signal is geometric accessibility, not confidence. The membrane-proximal information matters; its *pLDDT encoding* was not what carried it. |

**Cites D-075 and F-004. Amends neither.** F-004 stands as the record of the six-feature pre-registered result. D-075's frozen interpretation selected this reading before the number existed.

#### The triple, three-against-three (D-041 dec 4 — never one statistic)

| Run | median | mean | count ≥0.5 |
|---|---|---|---|
| **`geom_proxy` (id=5)** | **0.6607** | **0.6324** | **8-of-12** |
| FULL anchor (id=2) | 0.6071 | 0.6176 | 8-of-12 |
| `no_plddt` baseline (id=3) | 0.5625 | 0.5893 | 6-of-12 |
| *`plddt_only` (id=4) — not an anchor* | *0.6786* | *0.6295* | *9-of-12* |

All three of `geom_proxy`'s statistics clear the row's stated `≳` against FULL. **No threshold was invented; the row's own condition is the test.** This is not the ambiguous row and not the split row.

Twelve LOO percentiles: `0.1339 · 0.4732 · 0.4732 · 0.4732 · 0.6339 · 0.6518 · 0.6696 · 0.6875 · 0.6875 · 0.7946 · 0.9375 · 0.9732`. The triple was **recomputed from these by the Planner, independently of the run**, and reproduces to full float precision. `n_ranking_set` 56 · `n_fit_positives` 12 · `loo_status` complete, twelve folds converged · `scorer_version` `5ccab48772b5` · `geom_proxy` = 6 parameters (5 features + intercept).

Head-to-head over the **8 overlapping** targets — overlap with the two-valued evidence comparator, **not** a convergence count; all twelve folds converged. Spearman **+0.0483**, the same magnitude as FULL's with opposite sign, and **read as evidence of nothing** per Decision 4's dead-discriminator clause, whose quantisation behaviour the log predicted in advance.

#### ⚠ Three things this result does NOT license

1. **`geom_proxy`'s median exceeds FULL's. That is not a finding and is not reported as one.** The gap is **3.00 × (1/56)** — three of the finest increments the ranking set can express — and the median falls between the 6th and 7th sorted values, so one target's rank moves it. Decision 0.1–0.3 named this fragility before the run. **Decision 4 has no row for "better than FULL"; the row says *toward*.** Five features outscoring six at n=12 is within noise.
2. **`plddt_only` (id=4) carries the highest median and count of any run.** It is correctly not an anchor and Decision 4 does not use it. **It is reported here because omitting it would misrepresent the result.** The fired row's reading concerns *this comparison*; it is **not** a finding that confidence carries no signal — id=4 shows plainly that it does. The row's own second sentence is the synthesis: the membrane-proximal information matters, and its *pLDDT encoding* was not what carried it. **Two encodings of one quantity, both of which work.**
3. **F-005 is refined, not reversed, and is not amended.** F-005 remains true as recorded: remove pLDDT and the signal drops (id=3, 0.5625 / 0.5893 / 6-of-12). What is new is that **a single confidence-blind membrane-proximal feature recovers it.**

#### ⚠ The residual confound — measured, and it narrows the claim

Feature 7's confidence-blindness is **architectural**: `Atom` carries no `b_factor`, `parse_pdb` never reads columns 60-66, and the contaminated fixture reds on both arms — differing pLDDT *values* (11.1442 vs 88.1873) and differing pLDDT *array length* (11.1442 vs 12.2295). **The code cannot see confidence. That is proven, not assumed.**

**Blindness at the input is not independence at the statistic.** Feature 7 is computed over coordinates ESMFold itself produced. Measured over the 56 ranking-set rows, no nulls:

| | Pearson | Spearman |
|---|---|---|
| feature 7 vs feature 4 (`membrane_proximal_plddt`) | **−0.4898** | **−0.5490** |
| feature 7 vs feature 3 (`mean_plddt_ecd`) | **−0.6208** | **−0.4694** |
| *control:* feature 4 vs feature 3 | +0.7959 | +0.7695 |

⚠ **The confidence-blind proxy is confidence-correlated** — moderately to strongly, negatively, in the mechanistically expected direction: more exposed membrane-proximal SASA goes with lower pLDDT, because ESMFold is less confident where structure is less packed. It sits well below the two confidence features' correlation with each other, and nowhere near zero.

**This does not change which row fired, and it could not have selected it** — the measurement was specified before it ran and its interpretation was fixed in advance in both branches. **But it binds the claim.** The supportable statement is: **feature 7 recovers the membrane-proximal signal without reading confidence — not free of confidence.** Architecturally blind is proven; statistically independent is **measured false**.

**Instrument note.** These coefficients are a property of **this cohort as folded, at one recipe composition** — not a constant of the features. See D-075 Decision 6. They must not be cited as a general figure.

#### The attention control, and a disclosure that is not softened

Run B is blocked: `scripts/attention_control.py --freeze` is a deliberate stub. PR #109 shipped the assembly seam and not the network fetchers. **The snapshot protocol was pre-registered at `73bca8f`, before this result existed.** Under its §3, **Run A survived — so the proxies will be frozen knowing Run A survived.** That sentence goes on the snapshot's face and stands here. The query template and endpoints were already committed constants; **what is post-result is the data pull, and the rules governing that pull were fixed before the result existed.**

#### How this is known (D-016)

Run executed by Code against live production, 2026-08-06, from `ORDERS-Code-2026-08-05-D-075-run.md`. All governing §0 confirmations passed, including the confidence-blindness fixture's contaminated arm reddening on **both** arms.

**Two cross-version checks cleared beforehand.** `no_plddt` and `preregistered` each reproduced their stored anchors under today's `scorer_version` `5ccab48772b5`, so the boundary between id=2's `91e646e4a289` and the current scorer — opened by D-075 making the projection unconditional — is **closed by measurement rather than documented as closed**. ⚠ The first such check was specified against `no_plddt`, which had always projected and therefore could not have detected the change; the Planner corrected the specification to test `preregistered`, the arm that actually changed.

Post-state matched two independently written pre-registrations term for term: `ranking_runs` (4,4) → (5,5) · `ranking_results` 4 → 5 · `target_scores` 168 → 224 · `protein_features` unwritten, feature-7 non-null 79 → 79 · **id=2, id=3 and id=4 byte-unchanged**. No void condition fired.

**Every production number above is Code's reading. The Planner has no database access and recomputed only the triple from the twelve percentiles.**

Denominators, each stating its key, **never summed**: cohort of record **82** (Kathad-2024-PLOSONE) · rows carrying `protein_features` **80** (two named exclusions never enqueued, D-026) · ranking set **56** · excluded **24 of 80** (`held_out`, `below_floor`, and IGF2R `not_folded`).

> #### ⚠ DISCLOSURE added 2026-08-07 — a statement about the inputs, NOT a correction to the result
>
> **Nothing above is amended.** The triple, the twelve percentiles, the correlations and the quoted
> fired row are **unchanged and are not restated here.** The result stands exactly as measured.
>
> **What is now known, and was not known when this entry was written:** the spans every feature was
> computed on were produced by the span definition described in `### F-025`, and **three of the 82 —
> `IGF2R`, `TLR3`, `TMEM30A` — carry a domain that definition does not admit.** They are `held_out`
> here for a reason that is a property of the filter rather than of the proteins.
>
> ⚠ **This does not move a number in this entry, and no number in this entry may be re-derived to
> find out whether it would.** `### D-081` freezes the cohort permanently, and the reason is in that
> entry: re-measuring the 82 after `### D-075`'s interpretation was sealed would spend the
> pre-registration that makes this result mean anything.
>
> **The operative consequence is comparability, not validity.** `n_ranking_set = 56` and the cohort's
> dispositions are **definition-dependent**, and any census figure computed under the ruled 2026-08-07
> definition is **a different measurement** — comparable only when both definitions are named.
> See `### F-025` and `### D-081`; they are cited, not summarised.

---

### F-020 — An absent measurement coerced to zero and fit as though measured: `--ablate geom_proxy` would have returned D-075 Decision 4's ambiguous row for the wrong reason

- **Date:** 2026-08-06 (the defect was found and the guard shipped 2026-08-05)
- **Status:** **CLOSED under D-074** — the instrument no longer exhibits the defect. See **Closure**
  below for what that rests on and who read it.
- **Type:** A **finding** about the fit path. It cost nothing in the end because it was caught before
  the run it would have corrupted; what it would have cost is the point of the entry.
- **⚠ Number verified, not inherited.** Reserved in `RESERVED.md` on 2026-08-05 **before** the fix, per
  the F-017 precedent (*a number contested mid-task is contested under pressure*). At the time of
  writing the highest `### F-` in this log was **F-016**; F-017, F-018, F-019, F-021, F-022 and F-023
  are reserved and unwritten. Confirmed by reading this file for a `### F-020` header, not for a
  reference to one (method note item 7).
- **Provenance (D-016):** the three code sites are quoted from the tree at
  `PharmFoldMDK-snapshot-2026-08-05-4b7547c`. **The closure evidence is Code's reading of the live
  database on 2026-08-05 and is attributed as such below** — it is **not** Planner-verified, and the
  Planner has no database access.
- **Relates:** **D-075** (the pre-registration this would have spent); **F-004** (the pre-registered
  result, untouched); **F-021** (the loader defect found in the remedy); **F-023** (the residual bare
  null the fill left); **D-074** (a finding is not closed until the instrument stops exhibiting it);
  **D-027** (null-with-a-reason, never an imputed value).

**⚠ This is not F-018, and the two must not be merged.** F-018 is a **vocabulary** defect in the
**identity** path — an absent status recorded as an affirmative one — and it costs a **miscounted
census row**. F-020 is in the **fit** path and it costs a **fabricated result**. They are the same
*shape* at different altitudes, which is exactly why a later reader will be tempted to collapse them.

#### The defect — three links, none of which reddens

Migration `0007` created `protein_features.membrane_proximal_sasa`. **Nothing populated it.** Feature 7
is a named input of the `geom_proxy` ablation (`FEATURE_SETS["geom_proxy"] = (0, 1, 4, 5, 6)`), so a
`--ablate geom_proxy` run would then have done this:

1. **`scripts/fit_scorer.py`** assembled the row as
   `float(rec.membrane_proximal_sasa or 0.0)` — **an absent measurement becomes `0.0`.**
2. **The same file printed a WARNING and proceeded.** Its own text read *"a 0.0 placeholder here
   would be an imputed value (D-027)"* — ⚠ **it named the defect and then committed it.**
3. **`core/scorer.py`'s standardizer** is
   `(features[j] - self.means[j]) / self.stds[j] if self.stds[j] > 0 else 0.0` — a **zero-variance
   column standardises to `0.0` for every row.** No crash, no `NaN`, nothing red.

**So feature 7 would have entered the fit as a constant and contributed exactly nothing.**
`geom_proxy` `(0, 1, 4, 5, 6)` collapses to `no_plddt` `(0, 1, 4, 5)` **plus one inert dimension.**

#### ⚠ Why this was the most expensive available failure

The result would have landed at the `no_plddt` baseline — **D-075 Decision 4's second row**, which
this log names as *"the expected case at n=12"* and reports as **ambiguous**.

**And it would have fired for the wrong reason.** Not *"the SASA proxy did not recover the signal"*
but ***"the proxy was never computed."*** The two are indistinguishable in the output: same
`run_kind='sensitivity'`, a plausible triple, and the WARNING lines scrolled off above it.

⚠ **A pre-registered run producing its most likely outcome, for a reason invisible in its own
artifact, nine days before it is presented.** The pre-registration cannot protect against this,
because the pre-registration is about *what the numbers mean* — not about whether the input existed.

#### The guard

`--ablate geom_proxy` now **raises** rather than warns when any ranking-set row lacks feature 7.

- **Scoped to the named ablation, never to the fit.** The pre-registered six have no feature 7 and
  legitimately never did. ⚠ **A guard that reddened the pre-registered path would make F-004
  unreproducible in order to protect an ablation** — worse than the defect it fixes.
- **Scoped to ranking-set rows.** An excluded row's placeholder is inert by construction.
- **It runs before `create_ranking_run()`**, so a refusal writes no run row.
- **`or 0.0` was removed, not guarded around.** A membrane-proximal SASA of exactly `0.0` is a
  legitimate measurement — a fully buried window — and `or` cannot distinguish it from an absence.

#### Closure — what it rests on, and whose reading it is

**⚠ Read and reported by Code, 2026-08-05, against the live database. Not verified by the Planner,
who has no database access.** Recorded this way because D-016 permits an attributed reading and
forbids an anonymous one.

> **Code's reading, 2026-08-05:** the same guard was demonstrated **refusing** and then, after
> feature 7 was measured, **passing** — same guard, same rows, **with the run table untouched on both
> sides.** The refusal named **56 of 56** ranking-set rows; `ranking_runs` read `(4, 4)` before and
> after each demonstration. The pre-registered six-feature path passed throughout, so **F-004 remains
> reproducible.**

**The D-074 basis, stated explicitly:** *a finding is not closed when the fix is written; it is
closed when the instrument stops exhibiting it.* The before/after pair — refusal, then pass, on the
same instrument against the same population — **is** that evidence. ⚠ **The fix having been merged
would not have been.**

#### What it changed about how this project works

- **A warning that names a defect and proceeds is not a guard.** It transfers the decision to whoever
  is reading stdout, at the moment they are least likely to be reading it.
- **The dangerous failures are the plausible ones.** Nothing here would have crashed. Three separate
  artifacts on 2026-08-05 had this property, and it is why `test_zero_eligible_rows_is_an_ERROR_not_a_result`
  exists: *a census where nothing is fetchable is not a census result; it is a broken pipeline wearing one.*
- **A pre-registration protects the interpretation, not the input.** D-075's §0 had five confirmations
  and none of them asked whether feature 7 had a value.

---

### F-016 — The `Non_Surface` marker in the reconstructed Table S3 is a section heading, not a partition: everything below it is the **whole** membraneome

- **Date:** 2026-08-04. **Entered this log:** 2026-08-04, **in the same commit as F-011**, per
  `RULINGS-2026-08-04-F016` §6.1 — F-016 discharges F-011's flags and may not precede it.
- **Type:** A **finding** about a file this project was about to read positionally, caught before any
  census was built on it. **Nothing is ruled here.** One data artifact written, one script default
  removed.
- **Number:** **F-016**, the next free integer. F-013/F-014/F-015 stay reserved.
- **Relates:** **F-011** (whose magnitudes this discharges and whose `~5,102` it withdraws),
  **D-077 dec 1.3** (present-flagged-excluded-from-nothing, the treatment reused for inactive rows).
- **Full text:** `docs/F-016-non-surface-marker-is-not-a-partition.md`.

**The marker at row 2888 is a section heading, and the section it heads is the entire table.** All
2,886 surface rows appear **again** below it, field-for-field identical. **Splitting on row position
labels the entire positive class SURFY-negative** — the precise inversion `core/census.py` exists to
prevent. Derive class from the `Surfy` column, **never from row number.**

**Two gaps were live in the census before a single row was loaded:**

| | The gap | The cost had it shipped |
|---|---|---|
| 1 | The classes **do not partition** the table — 2,801 rows carry a blank class cell | "Not positive" overstates the negative class by **126%** (5,017 vs 2,216) |
| 2 | The **identifier count is not the protein count** | 2,886 identifiers are **2,807 distinct accessions**; 79 collapse into four HLA loci UniProt has merged |

⚠ **Three classes, always named:** `surface` · `non_surface` · `unclassified`. `unclassified` is
never merged into either and never dropped — and is **not evidence for F-011.**

**UniProt cross-check, 2026-08-04:** 7,746 active · 105 merged · 52 inactive · **0 unaccounted.** No
accession is corrupt; the divergence is eight years of upstream drift, which is itself the evidence
the reconstruction is faithful to a 2018 snapshot. Merged rows keep their pre-merge identifier;
inactive rows are `foldable=no`, retained and flagged, **never dropped.**

⟡ **`class_conflict` — the mechanism, not just the flag.** `Q96PC5` and `P01764` each carry rows in
two classes. **The classifier did not contradict itself:** each pair carries **distinct pre-merge
accessions** (`O15320`/`Q96PC5`, `P01765`/`P01764`) and exactly one row per pair is `merged`. SURFY
classified two separate entries; **UniProt's merge manufactured the contradiction** — the same
mechanism as the HLA collapse, surfacing as a contradiction instead of a count. **Resolved by
neither**, because resolving would assert that a merged entity has one localization, a biological
claim nobody has made. Both conflicts are `non_surface` × `unclassified`, so **the 2,807 surface
denominator is unaffected.**

⚠ **Not named `table_S3_surfaceome.xlsx`.** That name belongs to an artifact nobody has obtained —
the published URL still serves a 132-byte LFS pointer stub. Consequently `census_spans.py --source`
**has no default and is required**, and the script records the source file's sha256 in its output.

---

### F-011 — The surfaceome classifier's negative class is not "cannot be a target": localization is condition-dependent, and the excluded class may be the one with the best therapeutic window

- **Date:** 2026-08-04. **Entered this log:** 2026-08-04, **late** — see the landing note below.
- **Type:** A **finding** about a boundary this project was about to inherit, caught before
  inheriting it. **Nothing is ruled. No code, no route, no result.**
- **Number:** **F-011**, reserved for exactly this in `RESERVED.md`. F-012 is the Task 1c verdict;
  F-013/F-014/F-015 stay reserved.
- **Relates:** **F-009** (the same shape, a filter that removes the interesting cases), **F-016**
  (which read the table this entry could only cite, and supersedes two of its numbers), **A-014**
  (*an upstream model's negative class is a prediction, not a fact* — still blocked on KEEL-4).
- **Full text:** `docs/F-011-surfaceome-negative-class-v2.md`, which stays. Both existing is the
  **D-075 precedent**, not a duplication defect.

#### ⚠ Landing note — this entry is the D-062 defect in the Planner's own output

**F-011 v2 was written, placed in `docs/`, and pushed — and was never in this log.** "In `docs/` and
pushed" felt like landed and was not. That is **precisely D-062**: a citation treated as settled
authority with nothing in the text suggesting the entry was missing — committed one day after the
orders telling Code to **grep for the header, not trust the filename.**

**It surfaced only because F-016 ran that grep before merging on top of it.** F-016 discharges
F-011's flags, and an entry cannot discharge flags in an entry that does not exist. Recorded here
rather than quietly fixed, because the failure is the interesting part: the rule was written, the
rule was correct, and its author did not apply it to their own artifact.

#### ⚠ Supersession — `RULINGS-2026-08-04-F016` §6.4

- **2,216** moves from *unverified* to **counted** — off the file, matching the SURFY site exactly.
- **~5,102** is **WITHDRAWN, not corrected.** Never a row count; no corrected version exists. It
  assumed the classes partition the table. They do not — the table holds **7,903**, of which
  **2,801** carry a blank class cell.
- ⟡ **The argument is unchanged; its scope narrows.** This finding is about how SURFY defines its
  **negative** class. That holds **for the 2,216.** It says nothing about the 2,801 unclassified,
  which are unexamined by a different mechanism. **They must not be recruited into it.**

#### Provenance of every number — each with its key

⚠ A `verified` label answers *"where did this come from?"* and says nothing about *"is this the
quantity we need?"* — **a verified number with no key is incomplete by construction.** That is how
2,886 went wrong below: correct, verified, and not the denominator.

| Number | Key | Status | How known |
|---|---|---|---|
| **2,886** positive class | identifiers (entry names) | ✅ VERIFIED — ⚠ **not the denominator** | `surfaceome_ids.txt`: 2,886 lines, 2,886 unique. Counted, not cited. |
| **2,807** positive class | **distinct accessions** | ✅ **COUNTED — the denominator** | F-016. 79 collapse into four HLA loci UniProt has merged. Every join here is keyed by accession. |
| **2,216** negative class | identifiers | ✅ **COUNTED** *(was: not verified)* | F-016, off the `Surfy` column; matches the SURFY site. |
| **2,801** unclassified | identifiers | ✅ **COUNTED** | F-016. Blank `Surfy` cell. **Not this finding's subject.** |
| ~~**~5,102**~~ | — | ❌ **WITHDRAWN** | Planner arithmetic resting on an unstated partition assumption. |
| **93.5%** accuracy | — (a rate) | ⚠ Cited, not opened at first hand | PNAS abstract. |

#### The finding

The census universe was about to be defined as SURFY's positive class, with the negative class
treated as ineligible. That rests on a proposition nobody had stated: **"a protein SURFY calls
non-surface cannot be an ADC target."** **Mechanistically sound, empirically leaky — and every leak
runs toward the targets ADCs most want.**

**Sound:** an IgG cannot reach an epitope inside the ER lumen. A protein genuinely confined to an
intracellular membrane is unreachable. Not disputed.

- **Leak 1 — classifier error.** Reported accuracy 93.5%. Across a negative class of order two
  thousand, implied misclassifications are in the hundreds.
- **Leak 2 — steady-state localization is not "never at the surface."** The non-surface training set
  spans ER, endosome, Golgi, lysosome, mitochondrion, nucleus, peroxisome, cytosol (PNAS Fig. 1B).
  **Endosomal and lysosomal membrane proteins traverse the plasma membrane as part of their
  transport cycle** — their mechanism, not an exception to it.
- **Leak 3 — the labels encode normal conditions.** Trained on CSPA mass-spectrometry data from
  cultured cells. **A protein reaching the surface only under disease conditions is labelled
  non-surface by construction.**

#### ⚠ Why this is more than a caveat

**Condition-dependent surface trafficking is not a defect in a target — it is the selectivity
property an ADC exists to exploit.** Intracellular in normal tissue, surface-exposed in tumour, is a
*better* window than surface-everywhere. **So the classifier that makes the census tractable may
exclude, by construction, the class with the strongest theoretical window.**

#### The same shape a third time, and that is itself the finding

| Instance | The filter | What it excluded |
|---|---|---|
| **F-009** | Kathad's expression-and-selectivity filter | Trop-2, CD33, CD30, CEACAM5 — clinically validated ADC targets |
| **F-011** | SURFY's localization classifier | Potentially the condition-dependent-trafficking class |
| *(pattern)* | — | **The filter that makes a list tractable removes the interesting cases.** |

F-009's resolution applies unchanged: **name the boundary, do not inherit it silently, do not claim
to fill it.**

#### ⚠ Citation status, recorded not silent

Leaks 1–3 come from the SURFY resource page and the PNAS abstract and figure legends, read
2026-08-04. The examples offered in conversation — **GRP78/HSPA5, calreticulin, nucleolin, LAMP1** —
are **Planner-supplied from general knowledge, NOT opened at first hand.** Leads, not evidence.
**None may reach a surface, a deck, or a paper until its primary source is opened.** The finding
stands without them.

⟡ **The entry names its own weakest point:** it argues that an upstream model's negative class
should not be inherited as fact, while resting its magnitudes on that model's paper rather than its
data. Not fatal, not hidden — **and now discharged by F-016.**

#### What this rules — nothing. What it changes — the ingest.

- ✅ **Ingest the full membraneome table, not the positive subset.** SURFY score and class travel as
  columns. ⟡ **Done — `data/census/membraneome-reconstructed-2026-08-04.csv` (F-016).**
- ✅ **The negative class is a labelled annex** — retained, flagged.
- ❌ **Annex members are NOT census members and are NOT ranked.**
- ❌ **No claim that this project's method recovers them.** F-009's over-claim guard, verbatim.
- **Deep-learning justification.** Every discipline this log applies to ESMFold's pLDDT applies to
  SURFY's score. **An upstream model's negative class is a prediction, not a fact.**

---

### F-012 — ESMFold's chunked trunk is **not** output-invariant: chunk 16 diverges from chunk 64, and the folded cohort spans three different recipes

- **Date of run:** 2026-08-04. **Entered this log:** 2026-08-04, same day, before any use.
- **Type:** A **finding** — the result of D-077 Task 1c. It **cites D-077 and amends nothing.**
- **Number:** **F-012**, reserved for exactly this in `RESERVED.md` (amendment §1). F-011 belongs to
  the surfaceome negative class; F-013 stays reserved for Task 3 Arm A.
- **Relates:** **D-077 decision 2** (the two-row frozen table this reads against), **D-042** (which
  changed rental `chunk_size` `None`→`64` after O(L³) falsified the no-chunk assumption — the source
  of the cohort split below), **F-008** (the two-precision confound this adds a *third* axis to),
  **D-045/D-071** (fold provenance, without which the cohort split would be unknowable), **D-041 dec 4**
  (no threshold invented after the fact), **D-047** (recipe resolved at fold time).

#### The verdict, read against the frozen table and only against it

**⚠ Row 2 fired: the outputs DIFFER.** D-077 decision 2 fixed both readings before this ran, and its
second row says *"outputs differ **at all, by any margin**"* is the differ branch — **"nearly
identical" is the differ branch.** No tolerance was invented after seeing the numbers (D-041 dec 4).

| Comparison | Coordinates | pLDDT |
|---|---|---|
| **chunk 64 vs 32** | **0 / 342 differ** | **0 / 114 differ** |
| **chunk 64 vs 16** | **45 / 342 differ**, max abs delta **1.0e-3 Å** | **111 / 114 differ**, max abs delta **2.08e-3** |
| **chunk 32 vs 16** | 45 / 342 differ, max abs delta 1.0e-3 Å | 111 / 114 differ, max abs delta 2.08e-3 |

**First divergence (the evidence dec 2 calls for):** residue 0, field `plddt`,
`19.8300302028656` vs `19.829827547073364`.

**Therefore, per the pre-registered reading:** `chunk_size` is a **recipe dimension**, not a
memory/time knob. **The local ceiling is defined ONLY at chunk 64.** Folds produced at different
chunk sizes are **not commensurable**. **Task 3 Arm B — the extended envelope at chunk 32/16 — is
ABANDONED, NOT DEFERRED.**

#### How known (D-016), including the control that makes it interpretable

- **Run:** `scripts/chunk_invariance_run.py`, local NVIDIA RTX PRO 2000 Blackwell Laptop GPU (8151 MiB
  total, 7043 MiB free), torch 2.11.0+cu128, `dtype=int8` resolved from `TIER_RECIPE["local"]`.
  Artifacts: `data/derived/chunk_invariance/` (three PDBs, three pLDDT arrays, `verdict.json`).
- **Sequence:** the existing GPU-test fixture source (`tests/test_runner.py:209`), **114 aa**.
  Decision 2 permitted "the existing test fixture's source, **or** Trop-2 at ~248 aa"; the first was
  used because **Trop-2 has no sequence in this repo** — F-009 records TACSTD2/P09758 as one of the
  four clinically-validated ADC targets *excluded* from the 82, so it has no `protein_analyses` row,
  and `data/heldout_positives.csv` carries its accession and trial data only. The ~93 Trop-2 folds in
  `ARCHITECTURE.md:598-599` were dev-era.
- **⚠ THE DETERMINISM CONTROL, run before the verdict was believed.** Two folds at the **same** recipe
  were compared at chunk 64 and again at chunk 16: **byte-identical both times.** Without this, *"chunk
  16 differs"* is indistinguishable from *"folds are nondeterministic"* and the whole comparison is
  uninterpretable. The divergence is a real effect of `chunk_size`.
- **Comparator:** `worker/fold_compare.py`, exact equality, no tolerance, proven to bite against a
  deliberately contaminated rounding implementation before it was trusted.

#### ⚠ The consequence nobody had looked for: the folded cohort is already split across recipes

**How known (D-016):** read-only query over `protein_analyses.metadata->'fold_provenance'`, all 80 rows,
2026-08-04.

| `(dtype, chunk_size)` | Targets |
|---|---|
| `('int8', 64)` | **42** |
| `('fp16', None)` | **34** |
| `('fp16', 64)` | **3** |
| no `fold_provenance` recorded | **1** |

**34 folds ran unchunked.** That is D-042's own history — rental `chunk_size` was `None` until the
first rental run falsified the assumption that more VRAM makes chunking unnecessary — and D-045's
provenance capture is the only reason it is visible at all. **Until today this was harmless, because
chunking was assumed output-invariant. That assumption is what D-077 decision 2 said was never
measured, and it is now measured false for 16-vs-64.**

**⚠ WHAT THIS DOES AND DOES NOT ESTABLISH — the line matters.** This run compared **64 / 32 / 16 at
int8 on one 114-aa sequence**. It did **NOT** measure `None` versus `64`, did not measure at `fp16`,
and did not measure on a cohort-length sequence. So:

- **Established:** `chunk_size` can change ESMFold's output; the cohort contains three recipes.
- **NOT established:** that the 34 unchunked folds differ from the 37 chunked ones, or by how much.
  **`None` vs `64` is unmeasured**, and it is the comparison that would matter.
- **Refused:** any claim that the cohort's features are compromised, and equally any claim that they
  are fine. Both would be beliefs. The measurement that would settle it is **reserved as F-015**.

**This is F-008's shape one axis over.** F-008 recorded precision confounded with length and tier;
this adds `chunk_size`, and unlike F-008's it is confounded with *when the fold ran* rather than with
length. D-075 decision 6 already declined to resolve F-008 and is not weakened by this — but a
survival result there must not be over-read as excluding this either.

#### ⚠ The sub-structure, reported as evidence and explicitly NOT acted on

**chunk 64 and chunk 32 were perfectly identical; only chunk 16 diverged.** That is real information
and belongs in the record. **It is not a licence to probe Arm B at chunk 32.** Decision 2 says the
extended-envelope branch is *abandoned, not deferred*, on the differ branch — and "64 and 32 agreed on
one 114-aa sequence, so 32 is safe" is exactly the post-hoc carve-out the pre-registration exists to
forbid. n=1 sequence, at one length, on one card. **If chunk 32 is ever wanted, it is a new dated
entry with its own measurement, not an exception read out of this one.**

#### Honest limits of this finding

- **n = 1 sequence, 114 aa, one card, one torch build.** Generality is unmeasured.
- **Coordinates were compared through the PDB text format**, which quantises to 3 decimal places — so
  the observed 1.0e-3 Å max delta is *one unit in the last written place*. The true underlying
  difference may be smaller or larger; what is certain is that it is visible at file precision.
- **The magnitude is tiny and the direction of the ruling does not depend on that.** A reader who
  wants to call 2e-3 pLDDT "noise" is asking for a tolerance, and the answer is the one written before
  the numbers existed.

- **Deep-learning justification.** This is a statement about the model's numerics: chunking tiles the
  trunk's triangular attention, and the tiling changes the floating-point reduction order, so the
  network's own output is not invariant to a setting chosen purely for memory. That is load-bearing
  for whether folds produced under different memory budgets may share a ranking at all — the question
  the whole local-envelope idea rested on — and it is answered against the convenient direction.

- **Consequences.**
  - **Task 3 Arm B is abandoned.** Arm A (chunk 64, the production recipe) is unaffected and still
    ungated.
  - `LOCAL_CEILING` is **unchanged at 440** and now provably *recipe-scoped* — D-077 dec 3's binding
    of the constant to `(hardware, dtype, chunk_size)` is vindicated by its own Task 1.
  - **No reported result changes.** F-004, F-005, the LOO distribution and the ranking are untouched;
    nothing here reaches the scorer.
  - **F-015 reserved** for the `None`-vs-`64` measurement at fp16, which is the open question this
    opened and cannot itself answer.

### F-009 — The 82 is Kathad's comparator, not a target census: four clinically-validated ADC targets sit outside it, and that is what motivates the project

- **Date of finding:** 2026-08-01. **Entered this log:** 2026-08-03.
- **Type:** A finding — a property of the cohort plus a checkable list. Nothing is ruled.
- **⚠ Why the entry date lags:** the finding was written as a staged document
  (`docs/F-009-cohort-boundary-false-negatives.md`) and **cited by shipped code before it entered the
  log** — the `/about` and `/scorer` cohort-boundary note (2026-08-03) and `ARCHITECTURE.md` both name
  F-009. That made it the **last open instance of D-062's defect**: a citation pointing at an authority
  the log did not contain. This entry closes it. **Unlike D-062 this is not a reconstruction** — the
  staged document survives with its own reasoning and provenance, so this entry is *sourced*, not
  recovered from effects.
- **Relates:** D-075 (the confound §3's over-claim guard protects), F-004 (the result whose scope this
  bounds), D-029/D-040 (the curated reference the absences were checked against), D-062 (the defect
  class this closes), D-054 (the evidence-baseline deferral).
- **How known (D-016):** cohort membership checked by grep against `data/adc_reference_mapping.csv` and
  `data/cohort_82.txt` — CD30/TNFRSF8, CEACAM5, CD33/SIGLEC3 and TACSTD2 all **absent**. Accessions
  since verified from the **UniProt REST API** (see the closed checklist below).

#### The finding

The research question is *does a structure-derived axis reorder an **expression-based** ranking* — and
the expression-based ranking is **Kathad et al. 2024's**. The 82 is therefore *Kathad's cohort*,
inherited whole so both rankings cover the same targets and the delta means something. Adding a target
outside Kathad's ranking would have nothing to compare against: it would **break** the comparison, not
complete it. So *"why isn't CD30 in the 82"* has a clean answer — **because CD30 is not in Kathad's
cohort.** The boundary is a property of the comparator, not of this project's biology judgement.

**The sharper point, and the actual finding:** four clinically-validated ADC targets were **excluded by
Kathad's expression-and-selectivity filters**.

| Target | Accession | ADC | Furthest status | In the 82? |
|---|---|---|---|---|
| **Trop-2** (TACSTD2) | **P09758** | sacituzumab govitecan · datopotamab deruxtecan | FDA-approved (2 ADCs) | **No** |
| **CD33** (SIGLEC3) | **P20138** | gemtuzumab ozogamicin (Mylotarg) | FDA-approved 2000 | **No** |
| **CD30** (TNFRSF8) | **P28908** | brentuximab vedotin (Adcetris) | FDA-approved 2011 | **No** |
| **CEACAM5** | **P06731** | tusamitamab ravtansine | Phase 3 (CARMEN-LC03, NCT04154956) | **No** |

**Expression-and-selectivity filtering drops clinically-validated targets.** That is a concrete
demonstration that the expression axis is *incomplete*, and therefore that stress-testing it against a
different axis is worth doing at all. **The false negatives motivate the project; they do not undermine
it.**

#### ⚠ The over-claim guard — the load-bearing constraint

**Do NOT claim the structural method "would have caught" these targets.** Three reasons, all recorded
before any such claim could be made: (1) they are **unfolded and unscored** — there is no such result;
(2) CD30's 2011 approval makes it **maximally attention-rich**, so its pLDDT would be inflated for
exactly the reason D-075 interrogates — using it as validation walks into the confound; (3) the
defensible claim indicts the **comparator**, not this project's scorer: *the expression axis has
documented false negatives, therefore expression alone is insufficient, therefore an orthogonal axis is
worth measuring.* **"The comparator has blind spots" stays strictly separate from "our scorer fills
them."** Conflating them hands the critic the next punch. **This is now enforced as a denylist test on
both shipped placements, not as an editorial habit.**

#### An embedded correction (D-016) — the "first ADC" slip

**Adcetris (brentuximab vedotin, 2011) was *Seagen's* first ADC, not the first ADC.** That is
**Mylotarg** (gemtuzumab ozogamicin, CD33, FDA-approved **2000** — eleven years earlier). The two
claims share the word *"first"* and fuse in memory; only *"Seagen's first"* survives the record.
Mylotarg's 2000 approval, **2010 voluntary withdrawal** and 2017 re-approval at lower dose partly
erased it from the popular ADC narrative, which is why *"Adcetris was first"* is a common slip. **No
artifact may call Adcetris the first ADC** — a pharma-literate audience will catch it, and a wrong
historical claim in the setup is disproportionately costly for a project whose credibility rests on
how-known discipline. The staged deck was checked clean; the claim lived only in conversation.

> **⚠ Citation status, recorded not silent.** The sources for the CD33-was-first claim (Nature *Sig
> Transduct Target Ther* 2022; AACR *Clin Cancer Res* 2018; and the CEACAM5 phase-3 set) are
> **Planner-supplied and have not been opened by the builder or owner** — the same convention
> `data/adc_reference_mapping.csv` uses for its unopened citations. The claim is therefore recorded
> **as sourced but unverified-at-first-hand**, and — deliberately — **the shipped UI copy states neither
> the superlative nor the year.** The log carries the claim with its citation status; the user-facing
> surface makes only the part that needed no superlative. If the superlative is ever wanted on a
> surface, open the primary sources first.

#### What has happened since the finding was written (artefact-sourced)

- **§5's open accession checks are CLOSED.** All three were verified against the UniProt REST API on
  2026-08-01: **CD30/TNFRSF8 = P28908 ✓**, **CEACAM5 = P06731 ✓**, **Trop-2/TACSTD2 = P09758 ✓**
  (CD33 = P20138 re-verified). Every guess in the staged doc was correct — and was still checked.
- **§4's future-work item has been BUILT**, as the held-out validation set's Phase A:
  `data/heldout_positives.csv`, **20** clinically-validated ADC targets disjoint from the 82 by
  accession, each with a ClinicalTrials.gov source URL. The four above are members. **Phase B — folding
  and validating them — remains sealed behind D-075 surviving.** §4 said *"explicitly NOT claimed as
  done"*; the curation half now is, the validation half is not.
- **The framing reached the UI**, with the examples derived from that CSV rather than hardcoded and a
  drift test binding the two.

- **Deep-learning justification.** This bounds what the graded result *claims*. The scorer re-orders a
  comparator; without this entry a reader could take the ranking as a statement about the ADC-target
  space, which the data does not support. It also supplies the strongest available motivation for a
  structural axis existing at all — the expression axis demonstrably misses clinically-validated
  targets — while refusing the adjacent, unearned claim that our axis recovers them.

- **Consequences.** F-004/F-005/F-006 unchanged — this bounds scope, not result. The comparator's
  incompleteness is **not** a defect in the cohort choice: inheriting Kathad whole is what makes the
  delta meaningful (D-054's deferral rests on the same logic). ⚠ The 20-row held-out set carries its own
  named limit — **absence from that file is not evidence of absence from the field** — so it must never
  be presented as a complete census either; that would repeat this finding's error one level out.

### F-010 — `/api/coverage`'s `analysis_id` is sourced only from folded rows, so the one target whose record most needs explaining reports `null`

- **Date:** 2026-08-03
- **Type:** A finding against an instrument. **Nothing is ruled and nothing is fixed here** — logged
  deliberately unfixed (owner ruling) so it is not smuggled into an unrelated UI PR. The fix belongs
  to whoever is next in `app/reads.py` with a reason to be there.
- **Relates:** **D-043** (a failed fold is not an unattempted one — the same family: a failure falling
  out of a path that succeeds for every other row); **D-038** (`/api/coverage` as the honest-denominator
  supplier); **D-073/D-074** (the same error class reproduced *inside* the instrument built to measure
  it, and the rule that a finding against an instrument is not closed until the instrument stops
  exhibiting it — see the closing note).
- **Numbering:** `F-009` is reserved for the cohort-boundary finding; merged `ARCHITECTURE.md` already
  cites F-009 with that meaning, so this took the next free integer rather than displacing it.

**How known (D-016):** `GET https://pharmfoldmdk.fly.dev/api/coverage`, 2026-08-03, while diagnosing
IGF2R's null `mean_plddt` for the sortable-list work. IGF2R's coverage row reports
**`analysis_id: null`** — while `/api/analyses` reports **`id: 57`** for the same target and the
database confirms `protein_analyses` id=57 exists. Read against `app/reads.py`
`_folded_accessions` / `_coverage_row`.

**The mechanism, named precisely.** `_folded_accessions()` builds `{accession: analysis_id}` under
`WHERE pdb_path IS NOT NULL`, and `_coverage_row()` then sets `analysis_id = folded.get(row.accession)`.
IGF2R's fold hit a CUDA OOM at 2,491 aa, so its `pdb_path` is null and it is absent from that map.

**So this is not a broken join — it is a NAME that does not mean what it says.** The field is called
`analysis_id`, which reads as *"the id of this target's analysis row"*, but it is populated only when
the fold **succeeded**. IGF2R *has* an analysis row; it has no *structure*. The value silently answers
a different question — `folded_analysis_id` — under a name that promises the general one. Adjacent to
D-074's lesson and distinct from it: D-074 is an instrument drifting from its written record; this is a
field whose **name over-promises relative to its own population rule**, and the record was never
written down at all.

#### ⚠ Why this is cosmetic *today* and stops being cosmetic the moment anything consumes it

**Today:** nothing reads `coverage.rows[].analysis_id`. The UI links to targets from `/api/analyses`
(which carries the real `id`), and the D-075 sortable list joins coverage by **accession**, not by
`analysis_id`. So the null is currently inert.

**The trap for a future consumer, stated explicitly so it is not inherited silently:** the first code
that uses `analysis_id` to link a coverage row to its analysis record will work for **79 of 80 rows**
and return null for the one row a reader is most likely to click — the failure they want explained. A
null that appears only on the exceptional row is the hardest kind to notice in review and the easiest
to mistake for "no record exists" when the record does exist. **Anyone reaching for this field should
either fix the population rule first or join by accession instead.**

**Also recorded:** the failure is *asymmetric by construction*, which is why it survived. Every healthy
row gets a correct `analysis_id`; only the failed fold gets a null. A test over the folded majority
passes. This is the D-043 shape again — the exceptional row being the one the code forgets — and it is
the third time this class has appeared (D-043 in the surface, D-073 inside the instrument, now in the
coverage projection).

- **Deep-learning justification.** Neutral to the model; measurement hygiene on the route that supplies
  the **honest denominator** the graded ranking claim rests on. The counts `/api/coverage` serves are
  correct — `fold_status` and `fail_reason` are right for IGF2R, which is what the denominators use — so
  no reported figure is affected. What is wrong is a per-row identifier nobody has consumed yet.

- **Consequences / what closing this requires (D-074).** Not fixed here. When it is fixed, the honest
  options are: populate `analysis_id` for every target that *has* an analysis row (renaming the folded
  map's role), or **rename the field to `folded_analysis_id`** so the name states its own rule. Either
  discharges the finding; a null left under the general name does not. **Per D-074, this entry alone
  does not close anything** — the instrument still exhibits the finding, so until `app/reads.py` changes
  or carries an in-file statement of this limit, F-010 stays open. **No code, no test, no route change
  in this entry.**

### F-008 — The cohort was folded under two precisions confounded with length; F-005 gains a third candidate explanation the design cannot rule out

- **Date:** 2026-07-29
- **Type:** A finding. Nothing ruled — it **bounds** F-005, it does not replace it.
- **How known (D-016):** read-only SQL over `protein_analyses` (79 folded) grouped by `tier`, plus a
  within-tier pLDDT~length regression. No re-fold, no mutation.

**Measured — the split.**

| tier | precision | n | fold length (aa) | mean pLDDT |
|---|---|---|---|---|
| **local** | int8, chunked | 42 | 13–439 (mean 175) | **61.88** |
| **rental** | fp16 | 37 | 441–2213 (mean 735) | **71.04** |

Tier was assigned by length (≤440 aa local), so **precision is confounded with length by
construction** — no protein folded both ways, no overlap in the length ranges.

#### Finding — a third horn for F-005

F-005 Finding 3 named two live explanations for the pLDDT-carried signal (training-set attention;
genuine order-versus-disorder). There is a third, not previously in the log: **pLDDT is a model
output, not a physical measurement, and int8 trunk quantization changes the numerics relative to
fp16.** Because tier = precision = length, and length is feature 1, **features 3–4 (pLDDT) partly
encode which machine and precision ran the fold, which was decided by size.** The signal F-005
attributes to confidence could in part be an artifact of the compute split.

#### ⚠ The direction complicates the artifact reading — do not call it an int8 penalty

The rental folds are **longer** (735 vs 175 aa) yet score **higher** (71.04 vs 61.88) — the *opposite*
of the usual expectation that longer chains fold with more disorder and lower confidence. So the
between-tier gap is **not straightforwardly an int8 quantization penalty**; something else moves with
it. **This makes the confound harder to characterise, not easier** — which is the honest position and
the stronger one.

#### The within-tier texture — "two curves", not "two populations on one line", but still unresolved

Regressing pLDDT on length **within** each tier, the slopes differ in sign:

| tier | slope (pLDDT per 100 aa) | corr(pLDDT, length) |
|---|---|---|
| local | **+4.09** | +0.43 |
| rental | **−1.45** | −0.53 |

The differing slopes **rule out a single straight-line length relationship** ("two populations on one
line"). But they are consistent **both** with precision changing the length-response **and** with a
single non-linear, humped pLDDT-length curve peaking near the 440-aa tier boundary. Because the length
ranges do not overlap, **the data cannot distinguish these.** It distinguishes *two curves from one
line*; it does not resolve *precision from length*.

#### The label bound — observed-balanced, not confound-free

The 12 labels split **6/6** across tiers (rate 14.3% local vs 16.2% rental). This is **consistent with
no hardware→label path, but does not establish one:** at n=12, a genuine 2:1 tier skew would produce
6/6 often enough that it cannot be ruled out. Balanced is what was observed; "no confound path" is more
than twelve points can carry.

#### Unresolvable by construction — the resolution path

Precision cannot be separated from length in this data (no overlap). The only test of the precision
effect is a **controlled A/B — re-fold a handful of proteins at the opposite precision as a diagnostic
spike, never touching the reported cohort** (D-070 dec 4 refuses re-folding the result's folds). Named
as the only resolution path; not run.

- **Deep-learning justification.** This names a possible measurement artifact in the **load-bearing
  feature** — the one F-005 shows carries the signal — and it is exactly the confound an examiner looks
  for in a cohort folded two ways. Naming it, bounded, is a stronger position than leaving it for a
  reader to notice.

- **Consequences.** F-005's open question gains a third, currently-inseparable candidate; **F-004 /
  F-005 / F-006 stand — this bounds them.** No code, no re-fold, no change to the reported result.
  **⚠ Root cause and the design lesson:** the length-threshold tier rule created this confound. A
  future cohort either folds at a single precision, or **deliberately overlaps the length ranges across
  precisions** so the effects can be separated — a lesson that generalises past this project.

---

### F-007 — The pinned worker environment and the measured one disagree on torch

- **Date:** 2026-07-29
- **Type:** A finding. Nothing ruled.
- **How known (D-016):** `worker/requirements.txt` pins **`torch==2.11.0+cu128`**, described in its own
  header as *"the versions MEASURED in the S-003 spike, on the RTX PRO 2000 (Blackwell sm_120)."* The
  captured environment on `protein_analyses` id=75 (folded 2026-07-25, rental tier) records
  **`torch_version: 2.8.0+cu128`**. `transformers` agrees at **5.14.1**; **torch does not.**

**The rental pod ran a different torch build than the pinned worker manifest.** Not necessarily a
defect — D-018 accepted this exact exposure in writing: *"these dependencies are NOT covered by the root
lock-file guarantee… a breaking release here reddens no gate and is discovered at fold time, on a GPU
host — that is the accepted cost of keeping CUDA out of CI."* **This is that accepted cost, observed
rather than anticipated.**

#### Finding — the manifest is not a reliable proxy for what ran

**On the single fold where both a manifest and a measurement exist, they disagree.** Any method that
reconstructs a fold's environment from the pinned manifest therefore has a **demonstrated failure rate
of one for one on the only case that can test it.** **This is D-045 paying for itself** — the entry was
written on the reasoning that *"same weights, different kernels"* is a real source of variation. It was,
and nothing else would have found it.

**⚠ The bound, stated:** the pin was measured on the **local** box; the disagreement is on the **rental**
tier. **No local fold post-dates D-045**, so the local path has no measurement and this finding says
nothing about it either way. **Unknown, not fine.**

**Amendment (2026-07-29, D-071 §1).** The local path was measured: on the fold host, in the worker
venv, `torch 2.11.0+cu128 · cuda 12.8 · NVIDIA RTX PRO 2000 Blackwell · transformers 5.14.1` — **an
exact match to the pin.** The local box agrees with `worker/requirements.txt`; the *"unknown, not
fine"* bound is closed for the local tier. **The rental disagreement (2.8.0 vs pinned 2.11.0) now
stands alone as the finding** — the pin is right where it was taken, wrong where the ephemeral pod ran
a different build.

---

### F-006 — The fitted scores are compressed toward the base rate, and are not calibrated probabilities

- **Date:** 2026-07-29
- **Type:** A finding. **Nothing is ruled here.**
- **How known (D-016):** read-only SQL against `target_scores` where `ranking_run_id = 2` (the
  pre-registered run), over the live proxy on `localhost:16380` — `MIN`, `PERCENTILE_CONT(0.5)`,
  `MAX`, `COUNT(*)`.

| | |
|---|---|
| min | **0.116** |
| median | **0.220** |
| max | **0.285** |
| count | **56** |
| labelled fraction (12 / 56) | **0.214** |

---

#### Finding (1) — the median sits on the base rate, and nothing reaches 0.3

**Median 0.220 against a labelled fraction of 0.214.** The typical target is lifted almost nothing
off the prior. The whole field spans **0.116–0.285**; rank 1 is the ceiling and sits ~0.065 above
the median.

**⚠ A reader shown "rank 1 = 0.285" with no framing will read it as a middling probability**, when
it is the top of a field that never clears 0.3.

#### Finding (2) — ⚠ this is the expected signature of L2 shrinkage at n=12, not necessarily a weak ordering

**Compression of absolute scores toward the base rate is what an L2-penalized fit on twelve
positives is expected to produce.** D-041 chose L2 precisely to shrink unstable coefficients, and
shrunk coefficients yield outputs pulled toward the prior.

**The absolute spread is therefore weak evidence about the ordering, in either direction.** The
evidence about the ordering is **F-004's leave-one-out percentile distribution** — median 0.607, 8
of 12 above chance — which is computed on **positions, not values**, and is unaffected by
compression.

**Stated plainly: compressed scores do not by themselves make the ranking uninformative, and they
are not evidence that it is informative either.** The two questions are separate and only the second
was pre-registered.

#### Finding (3) — ⚠ the score is NOT a calibrated probability

A logistic model outputs a number in [0,1], **but calibration was never tested** and no calibration
claim was pre-registered. **Nothing on any surface may present 0.285 as "a 28.5% chance"**, and the
`Score` tooltip must say so explicitly.

**Recorded as a Planner correction:** an earlier draft of that tooltip read *"the model's estimated
probability that a target belongs to the labelled set."* **Withdrawn** — it implied calibration that
was never established.

---

#### Consequences

- The `Score` column tooltip carries **the scale, the observed range, the labelled fraction, and the
  non-calibration statement**, all derived from `/api/ranking`, none typed (D-050).
- **`COUNT(*) = 56` is what surfaced D-066** — the cross-check earned its place and is recorded as
  having done so.
- **No re-fit, no re-scaling, no calibration step.** Any of those would be a model change after
  seeing a result. If calibration is ever wanted it is a new entry, dated after this one.

---

### F-005 — The sensitivity analysis: the above-chance signal is carried by ESMFold's confidence, not by the geometry — and the attention explanation is not supported

- **Date:** 2026-07-29
- **Type:** A finding. **Nothing is ruled here.** The reading below follows D-065 decision 3's
  outcome table, which was fixed **before either ablation ran.**
- **⚠ This does NOT replace F-004.** D-058 decision 2 and D-065 decision 4: a sensitivity analysis
  is reported *after* the pre-registered result, presented as sensitivity, and never as the headline.
  **F-004 remains the result. This bounds it.**
- **Cites F-004; does not amend it** (D-065 decision 4).
- **How known (D-016):** two authorised runs of `scripts/fit_scorer.py --run --persist --ablate`,
  one each, after PR #91. Persisted as `ranking_run` **id=3** (`no_plddt`) and **id=4**
  (`plddt_only`), both `run_kind='sensitivity'`, `scorer_version=a927dc4532b7`. **Neither is served
  by `/api/ranking`**, which filters `valid ∧ run_kind='preregistered'` and continues to serve id=2.

---

#### The design held

**Denominators identical across all three runs** (D-065 decision 2): ranking set **56** · positives
**12** · head-to-head **8** · common reference **12**. All three: `loo_status=complete`, **12 of 12
folds converged**, `fulldata_status=converged`. **No raise in either ablation** — expected, since
fewer parameters make convergence more likely, and recorded because D-065 required a raise to be
reported as a finding had one occurred.

| Run | median | mean | ≥0.5 | Spearman | params |
|---|---|---|---|---|---|
| **FULL** (F-004, id=2) | **0.607** | 0.618 | **8/12** | −0.0483 | 7 |
| **`no_plddt`** (id=3) | **0.562** | 0.589 | **6/12** | −0.0483 | 5 |
| **`plddt_only`** (id=4) | **0.679** | 0.629 | **9/12** | **−0.2897** | 3 |

#### Finding (1) — D-065 decision 3, row 2, **first clause fires**

> *"`no_plddt` ≈ chance, `plddt_only` ≈ full-model shift → **the axis is substantially
> pLDDT-driven**."*

**`plddt_only`, on two features and three parameters, matches and slightly exceeds the full model.**
**`no_plddt`, on four features and five parameters, falls to 6 of 12 above chance — exactly even.**
**Two of the six features carry the result. The four geometry features are close to inert.**

This is consistent with predictions D-027 recorded before any data existed: **features 1 and 2 are
collinear by construction** (ECD length and length-normalised radius of gyration), and **feature 6
is the fragile one**. A geometry set that contributes little is the anticipated shape, not a surprise.

#### Finding (2) — ⚠ row 2's **second clause is NOT supported**, and this is the substantive result

D-065 decision 3's row 2 continues: *"the attention pathway is a live explanation."* **The one
measurement bearing on that pathway points the other way.** F-004 caveat (b) named a specific
mechanism: pLDDT partly reflects training-set representation → research attention → having been
attempted as an ADC. **If that were operating, `plddt_only` should align MORE closely with the
evidence score** (the project's available proxy for attention-and-precedent). **It aligns less** —
Spearman **−0.2897** vs **−0.0483** for FULL and `no_plddt`, further from zero and in the negative
direction, the opposite of what the attention mechanism predicts. **The pre-registered reading
half-fires**, and is reported as half-firing rather than forced onto a row.

**⚠ Bound on this inference.** The evidence score is a weak attention proxy — **two values, twelve
targets** (F-004; D-060 decision 8). *"Not supported"* means the one available test points away,
**not** that the pathway is excluded.

#### Finding (3) — what is now open, and it is a better question than the one it replaces

**ESMFold's own confidence about a protein predicts whether people have built an ADC against it
better than the geometry ESMFold predicts.** Two candidate explanations, both live, **neither
distinguishable by this design:** (1) **training-set representation → research attention** — F-004's
original confound, **weakened by Finding (2), not eliminated**; (2) **order versus disorder — a
genuine structural mechanism** — pLDDT tracks predicted order, disordered regions make poor antibody
epitopes, so a well-ordered ECD is a real structural argument for accessibility, and on this reading
**pLDDT is a legitimate feature, not a confound at all** (D-027's *epitope-region pLDDT* justification
borne out). **Distinguishing them requires an instrument this project does not have.** Named as the
open question. Not resolved, and not narrated as if it were.

#### Finding (4) — ⚠ `plddt_only` beating FULL is unremarkable and must not be over-read

**Three parameters against twelve positives generalises better than seven.** At this n that ordering
is expected and is **not evidence that pLDDT is superior** to the full set — only that the geometry
features are not adding enough to pay for their parameters **at this cohort size.**

#### Finding (5) — the three models disagree per target while agreeing on one coarse statistic

FULL and `no_plddt` return **identical Spearman to four decimals (−0.0483)** while producing
substantially different per-target percentiles (NECTIN4 0.848 → 0.634, JAG1 0.580 → 0.830). Against a
two-valued comparator six-and-six among twelve, **Spearman depends only on the rank-sum of the
score-5 group** and is quantised in steps of ~0.024, so two genuinely different models can agree on
that one statistic; `plddt_only`'s −0.2897 confirms it varies by run. **Agreement on a coarse
statistic computed against a degenerate comparator is not agreement between the models.**

---

#### Consequences

- **F-004 caveat (b) is now tested rather than open**, and its status changes rather than its text:
  the **specific** attention mechanism it named is **not supported** by the one available test; a
  **new, better-posed** open question replaces it (Finding 3). **F-004 is not amended** — this entry
  is the update, and the ordering of the two entries is the record.
- **⚠ The ranking rendered by `/api/ranking` is substantially a pLDDT-driven ordering.** Any surface
  describing what the score measures must not imply the geometry features are doing the work. **The
  `structural score` definition (D-055/D-062 tooltips) is read against this finding before it ships.**
- **The pre-registered result stands unchanged.** Six features, seven parameters, the reported
  distribution, both negative-outcome tests. No parameter altered after any result existed, and no
  third ablation run (D-065 decision 1).
- **The strongest available follow-up is now clear**, and it is not more parameters: an independent
  attention proxy, or an independent disorder measure, would separate Finding 3's two explanations.
  **That is a next-session arc with its own entry**, and D-041's line still governs — *the honest
  route is more labelled data, not more parameters.*

---

### F-004 — The pre-registered result: the structural axis is modestly above chance, indistinguishable from the comparator, and not a proxy for it

- **Date:** 2026-07-28
- **Type:** The pre-registered result (D-041). **A finding, not a decision** — nothing is ruled here.
- **How known (D-016):** one authorised run of `scripts/fit_scorer.py --run --persist` against
  `main` after #89 (D-064's label fix). Persisted as **`ranking_run` id=2**,
  `scorer_version=91e646e4a289`, `ranking_results` id=2, 56 `target_scores`.
  **Run exactly once. No re-run, no parameter changed after the result existed.**
- **Provenance chain:** an earlier run under the D-064 defect produced `ranking_results` id=1 with
  a **zero-positive label set**. That row is **retained and marked invalid**, not overwritten
  (D-064 decision 3). `ranking_runs` id=1 is the enqueue's anchor for 80 folds and is untouched.

---

#### The inputs, all fixed before the run

Six features (D-027) · L2 logistic regression, seven parameters (D-041) · 13-point λ grid, 5-fold
stratified inner CV, no RNG (D-060) · pLDDT floor 50 (D-041 §5) · **12 curated label accessions**
(F-003) · ranking set **56** · comparator **12** · head-to-head **8** (F-002, recomputed against the
curated file).

#### Result (1) — the pre-registered object: the leave-one-out percentile distribution

**`loo_status = complete`. 12 of 12 folds converged. No non-convergent targets.**

| Target | Percentile | | Target | Percentile |
|---|---|---|---|---|
| EGFR | 0.955 | | SLC3A2 | 0.634 |
| CDCP1 | 0.902 | | JAG1 | 0.580 |
| ERBB2 | 0.866 | | CD276 | 0.562 |
| NECTIN4 | 0.848 | | CDH11 | 0.384 |
| MERTK | 0.812 | | FGFR3 | 0.384 |
| | | | UPK1B | 0.312 |
| | | | SLC39A6 | 0.170 |

**Median 0.607 · mean 0.617 · 8 of 12 above 0.5**, against a null expectation of 0.5.

**A modest upward shift.** D-041 decision 3 fixed the reported object as *the full distribution with
median and spread* and barred a single summary number as the headline. **No significance test was
pre-registered and none is computed** — at n=12 one would be underpowered, and choosing a test after
seeing the distribution is the degree of freedom pre-registration exists to remove.

#### Result (2) — D-041 decision 3's first negative outcome: **FIRES**

On the 8 held-out positives carrying an evidence score, percentiles computed within the common
reference set of 12 (D-060 decision 8):

| | structural | comparator |
|---|---|---|
| mean | **0.573** | **0.5625** |
| median | **0.625** | **0.750** |

**Not distinguishable — and the direction reverses between mean and median.** That reversal is the
cleanest possible statement of the finding: which axis looks better depends on which summary you
choose, which is what *"not distinguishable"* means at this size. D-041's own words for this case:

> *"the structural axis adds nothing measurable at this cohort size. That is the result."*

**⚠ The comparator's degeneracy was predicted and held.** The evidence percentiles came back as
**exactly two values, 0.75 and 0.25** — because the published evidence score takes only two values
(nine 4s, eight 5s across 17 targets). D-060 decision 8 recorded this **before any number existed**,
and it bounds what this comparison could ever have shown in either direction.

#### Result (3) — D-041 decision 4's second negative outcome: **DOES NOT FIRE**

**Spearman(structural, evidence) = −0.0483 over N=12.**

D-015 §3 pre-registered that a **strong** correlation with the evidence score would *also* be a null
— it would mean the features proxy attention-and-precedent rather than measuring structure.
**Near-zero says they do not.** The structural axis is measuring something largely orthogonal to the
comparator.

#### Result (4) — the two together, which is the finding

> **The structural score ranks attempted-ADC targets modestly above chance, is not distinguishable
> from an expression-and-attention comparator, and is not a proxy for it. At twelve positives, the
> axis measures something different and cannot be shown to add anything.**

That combination is more informative than either null alone: **orthogonal but unproven** is a
different result from *"the features just re-learned the comparator,"* and the second was the more
likely prior.

---

#### ⚠ Three caveats that travel with this result, always

**(a) The design is conservative and biases toward the null.** Each held-out positive is ranked
among a pool that still contains the eleven training positives the model was fit to score highly.
That pushes held-out percentiles **down**. Five targets nonetheless exceeded 0.80, so the training
positives do not uniformly dominate — but **the bias runs toward understating, not overstating.**

**(b) An open confound: pLDDT may carry attention.** Two of the six features are pLDDT-derived, and
**pLDDT is partly a function of how well-represented a protein's family is in ESMFold's training
data — which tracks research attention, which tracks having been attempted as an ADC.** That is a
path by which the score could proxy attention *through the network's own confidence* rather than
through structure. Result (3) argues against it, **but the evidence score is a weak stand-in for
attention** (two values, 17 targets). **Recorded as an open confound, not as resolved.** (Tested by
D-065.)

**(c) The top of the distribution is the famous targets.** EGFR, ERBB2 and NECTIN4 sit in the top
four. **Consistent with signal and equally consistent with (b).** It is not narrated as validation.

#### What this result does NOT claim

- **Not** that the score predicts clinical success. The label is *attempted*, not *viable* (D-041).
- **No per-target biological or clinical claim** (D-028). The delivery-agnostic framing appears once
  in the method note, never on a row.
- **Not** agreement with the paper: 12 derived labels against 22 published, with the gap recorded as
  a finding and its explanations named-but-unresolved (F-003 Finding 1).
- **Not** a significance claim. None was pre-registered; none is made.

#### Consequences

- **`fulldata_status = converged`**, 56 `target_scores` exist. **Both of D-041's negative-outcome
  tests are computable; neither is blocked** (D-064 decision 5's blocked branch does not apply).
- **The ranking table is buildable on real scores** — the first time in the project's history that
  has been true. It is still not mocked and still not required to be complete.
- **The honest route to a stronger result is more labelled data, not more parameters** (D-041).
  The roster's floor of 12 (F-003 Finding 6) is the binding constraint.
- **Deep-learning justification.** This is where the graded deliverable's claim actually resolves:
  ESMFold's structural output, turned into a judgement (D-041 §2), produces a pre-registered result
  that is falsifiable and honestly bounded — a modest, orthogonal, unproven signal, reported as
  such rather than dressed up. The rendering surface (D-062) makes that legible to a grader.

---

### F-003 — The Group B curation pass: 12 labels against 22, and what the instrument got wrong

- **Date:** 2026-07-27
- **Type:** Instrument/method finding (`F-NNN`). **Not a decision** — it records what the curation
  produced and what the tooling got wrong. The classification judgements themselves are the owner's
  (D-040 decision 1).
- **How known (D-016), by tier, because the tiers are not equal evidence:**
  1. **Registry pass** — `scripts/curate_group_b.py` against ClinicalTrials.gov, 2026-07-26, all 82
     symbols under UniProt aliases. Output: `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv`.
  2. **Targeted literature + patent pass** — 2026-07-27, **20 symbols**, one query minimum each,
     sources opened and read.
  3. **Landscape survey** — 2026-07-27, **19 symbols**, checked against ADC clinical-landscape
     reviews enumerating the **>50 antigens** in the **>200-candidate** clinical pipeline.
     **A survey-level negative is weaker evidence than a target-specific one** and is recorded as
     such in the file header.
- **Produces:** `data/adc_reference_mapping.csv` — the labels D-041's fit consumes.

---

#### Finding 1 — 12 label accessions against the paper's 22; the name check passes

Measured by running `core.adc_reference` against the curated file:

```
drug rows loaded ......... 13
group_b drug rows ........ 13
group_b ACCESSIONS ....... 12     <- two ERBB2 drug rows collapse to one label
group_c rows ............. 0      (deferred with reason)
stages: approved 3, clinical 4, preclinical 6
D-040 name check ERBB2/NECTIN4/EGFR present: True
D-040 count check: 12 derived vs 22 published -> -10
```

**⚠ Drugs are not targets.** Two approved ERBB2 ADCs are two rows and **one** label. The fit set
counts accessions, not rows, and an earlier Planner figure of 15 conflated them. Corrected here.

**The −10 gap is a finding, not a discrepancy reconciled away** (D-040 decision 1 pre-registered
exactly this). Candidate explanations, **named and not resolved**:

- **The roster is incomplete by three** — see Finding 6. The count is a floor.
- **The preclinical tail is registry-invisible by construction**, which the 07-26 closeout already
  predicted from PODXL.
- **Our exclusion set may be stricter than theirs.** The paper says 22 targets were "tested as
  ADCs" and does not publish its inclusion rule; this entry's rule excludes radioimmunoconjugates,
  peptide-drug conjugates, naked antibodies and family precedent explicitly.
- **They may hold information not in the public record.**

**No criterion was loosened toward 22.** Doing so would fit the labels to the comparator and
silently pre-decide D-041's result.

#### Finding 2 — the script's `review_as_probable_group_b` routing carried a 27% false-positive rate

**4 of 15 routed positives were wrong**, each falsified by a target-specific search:

| Target | Why it failed | Class |
|---|---|---|
| **SORT1** | TH1902 (sudocetaxel zendusortide) is a **peptide-drug conjugate** | excluded modality |
| **MCOLN1** | zero hits; a lysosomal channel is the wrong compartment for an ADC | no agent |
| **SMO** | small-molecule target; hits were patent boilerplate and a saporin **research reagent** | no agent |
| **FLT1** | icrucumab (IMC-18F1) is a **naked** blocking IgG1 | no payload |

**This is not a defect in the script** — D-057 built it to *gather evidence and refuse to draw the
conclusion*, and it did. **The rate is what "probable" was worth: roughly 4 in 5.** Recorded so the
next runner sizes their review effort against a measured number rather than the word.

**The misses clustered where the biology makes an ADC implausible**, and the owner's domain read
flagged all four before any search ran.

#### Finding 3 — the script's peptide-drug-conjugate exclusion did not fire

SORT1 routed positive because TH1902 is a registry-visible SORT1-targeting conjugate and **the PDC
exclusion never triggered.**

**This is the same defect class as D-057 decision 3** — the `radioimmunoconjugate ⊃ immunoconjugate`
substring bug, which the calibration test caught *before the script ever reached a network*. The
calibration covered the radio case and **not** the peptide case. **A calibration set proves the
cases it contains and nothing else.**

**⚠ Compounding factor, observed in the primary literature:** an OSMR paper describes a **⁶⁷Cu
radioimmunoconjugate** and calls its own construct "the ADC" in the methods. **Exclusion cannot rely
on the source's terminology; the payload must be checked.**

#### Finding 4 — seven contaminant classes, each observed, none hypothetical

1. **Radioimmunoconjugate** — CDCP1's ch10D7-**⁸⁹Zr**; OSMR's ⁶⁷Cu.
2. **Family-member ADC** — NOTCH2←Notch3, EPHA4←EphA2/EphA5, CDH11←P-cadherin, TSPAN15←TSPAN8,
   ITGB5←ITGB6.
3. **Research-reagent conjugate** — FITC/HRP/PE/agarose/saporin catalogue antibodies.
4. **Patent boilerplate** — a generic ADC-embodiment paragraph present in nearly every therapeutic
   antibody patent (LRP6). **The most dangerous, because it reads as a target-specific hit.**
5. **Naked antibody** — PCDH7 (mAb7), ENTPD1 (Phase I blockers), BTN3A3 (ICT01), FLT1 (icrucumab).
6. **Excluded conjugate modality** — SORT1's peptide-drug conjugate.
7. **Lexically similar symbol** — FGFR1 returned on FLT1; SLC34A2 (NaPi2b) returned on SLC3A2.
   **Distinct from (2): not a family member, a look-alike symbol.**

#### Finding 5 — the family-adjacency pattern, and why it makes the silence credible

Four families in the cohort have real ADC programs, **every one against a sibling gene**: EphA2 and
EphA5 but not EphA4; Notch3 but not Notch2; P-cadherin and CDH6 but not CDH11; TSPAN8 but not
TSPAN15; ITGB6 but not ITGB5.

**This is the Kathad cohort's selection method showing through.** Targets were selected on
expression, not ADC precedent — so where a family holds a validated ADC antigen, the cohort often
contains the other member. **It is a structural reason the registry-invisible tail is genuinely
empty rather than merely unsearched**, and it strengthens the negatives rather than weakening them.

#### Finding 6 — ⚠ the roster is incomplete by three, and the file says so

**CXCR5, MSLN and MUC16** were routed probable-positive by the registry pass and were **never
verified** — they fell outside both the 33-row headroom set and the 12-row verification set.

**They are absent from the file because unverified, NOT because negative.** The file's header
carries an explicit carve-out to that effect, because *"absence is a negative"* would otherwise
mislabel three probable positives by omission.

**Consequence: the count of 12 is a floor, not a total.** None of the three is in the ranking set
anyway — CXCR5 is below the pLDDT floor (47.63), MSLN is `held_out`, MUC16 is unfolded — **so the
fit set is unaffected**, but D-040's count check is not final until they are curated.

#### Finding 7 — GRIN1's tooling gap is closed

Its registry pass ran on reduced aliases (a `[NMDA]` bracket-syntax query returning HTTP 400), so
its silence was weaker evidence than its neighbours'. **Closed by a targeted literature pass:** the
GRIN1 literature is entirely neurology — epilepsy variants, stroke neuroprotection, anti-NMDAR
encephalitis autoantibodies. Anti-GluN1 antibodies exist, naked, non-oncology. **No conjugate.**

**A documented tooling defect converted into a documented closed gap**, rather than left as a silent
weakness in one row.

#### Finding 8 — the day's net effect: the fit set did not grow; its composition was corrected

**12 rankable positives before curation, 12 after.** Four removed (SORT1, MCOLN1, SMO, FLT1), four
added (CDCP1, JAG1, UPK1B, CDH11).

**That is the more valuable operation.** Four false positives in a twelve-positive set is **33%
label noise**, and noise in the positive class is precisely what a seven-parameter logistic
regression cannot absorb. **Removing four wrong labels improves the fit more than adding four right
ones would have.**

**⚠ D-041's sizing clause stands and is triggered:** 12 positives against seven parameters is ~1.7
per parameter, versus the ~3 D-041 called *"the upper end of what this labelled set supports."*
**Recorded as a finding, not absorbed.**

---

#### Owner rulings recorded (D-040 decision 1 reserves these; they are transcribed, not made here)

- **A target-specific patent claiming antibodies AND conjugates COUNTS**, even without a named
  clinical agent — applied to **UPK1B** (WO2017112829A1) and **CDH11** (US12522657). **A generic
  ADC-embodiment paragraph inside an antibody patent does NOT** — LRP6.
- **SORT1 is excluded**, resolving the one row where the hand draft and the script disagreed.
  **The hand draft was right.** The disagreement was settled by evidence, not by preference, and
  the instrument defect it exposed is Finding 3.
- **Accepted risk:** citations on **CDCP1** and **JAG1** were opened and verified by the owner;
  the remaining Planner-supplied citations were **not**, and the file header names them. Recorded,
  not silent; amendable.
- **A label cannot be deferred to the reader.** An earlier instruction to "state the disagreement
  and let the user decide" was withdrawn: Group B is the fit's binary target, D-041 pre-registers
  that labels are fixed before fitting, and the loader has no undecided state. **The disagreement is
  recorded here; the label is decided.**

#### Consequences

- **`test_the_committed_scaffold_loads_empty_and_valid` is RED** and must be **rewritten, never
  deleted** — it asserted the scaffold held no roster and fired the moment one landed, which is the
  tripwire working. Replace with a pin on the curated roster: 13 drug rows, 12 label accessions,
  the three named targets present, `group_c() == []`.
- **`application_number` is blank on both ERBB2 rows**, pending openFDA reconciliation (D-029). The
  repo already has that check; run it rather than type the numbers from recall.
- **Group C is absent with reason**, so `group_c()` returns `[]`. D-027's out-of-cohort probe
  (TROP2/HER3/CLDN18.2) additionally requires those targets to be **folded**, and they were never
  enqueued. Deferred with its trigger.
- **`scripts/curate_group_b.py` carries two known gaps** — the PDC exclusion (Finding 3) and the
  bracket-syntax alias failure (Finding 7). Both are cheap fixes and neither is blocking.
- **D-041's intersection requirement is still not discharged.** The labelled ∧ folded ∧ above-floor
  intersection must be **recomputed against this file** before the fit, and that recomputation is
  the recorded one. F-002's provisional figures are superseded by it.

---

### F-002 — Pre-fit cohort measurement: the folded set, the floor cost re-measured, and the four denominators the scorer depends on

- **Date:** 2026-07-27
- **Type:** Instrument/method finding. **Not a decision.**
- **How known (D-016):** `scripts/intersection_check.py` (untracked at time of measurement), run
  2026-07-27 against the live deployment `https://pharmfoldmdk.fly.dev` — `GET /api/analyses` and
  `GET /api/coverage` — joined to `data/derived/adc_reference_mapping_REVIEW-2026-07-26.csv` and
  `data/evidence_scores.csv`. Standard library only, no database credentials.

---

#### Two Planner errors this measurement found, recorded before the numbers because they change how the numbers read

1. **`/api/analyses` is the enqueued set, not the folded set.** `core/enqueue.py` creates a
   `protein_analyses` row at **enqueue** time; the list route returns those rows. A first pass read
   its 80 rows as 80 folds. **The folded count is 79** (`/api/coverage`, the D-038 supplier built to
   be the honest denominator). **80 was never a fold count.**
2. **A failed fold was absorbed into the below-floor bucket.** The script's predicate was
   `plddt is None or plddt < FLOOR`, so IGF2R — `fold_status=failed`, no pLDDT — counted as
   below-floor. **This is the D-043 error class reproduced inside the instrument used to measure
   it:** a failed fold is not an unattempted one, and it is not a low-confidence one either.

**A third, methodological:** the uncorrected pass returned **67**, and D-050 records `CoverageLine`
correctly showing **67 = `ranked ∧ folded`** in the 79-fold era. Two different quantities, identical
value. The collision prompted the check that found a missing `disposition` filter. **A number that
matches one you already trust is the most dangerous kind of wrong.**

#### The partition, which reconciles exactly

```
82  = 67 ranked + 13 held_out + 2 excluded          (/api/coverage)
79 folded     = 67 ranked∧folded + 12 held_out∧folded
 1 failed     = IGF2R  (held_out, rental, whole_sequence_fold)
 2 not_folded = MUC16, FAT2  (excluded, over_local_ceiling)
```

#### Finding 1 — every `ranked` target is folded: 67 of 67

The three gaps sit in `held_out` and `excluded` — partitions that were never entering a ranking.

**⚠ The claim "the fold arc is complete" is NOT supported and was withdrawn before it was spoken.**
The Planner drafted it from `82 − 80 = 2`; the endpoint returned three non-folded targets and the
Builder refused the sentence. **The supported claim is narrower and stronger**, and it is the one
that goes to the demo.

#### Finding 2 — the floor cost, re-measured on the right denominator

D-041 §5 recorded **~24% below pLDDT 50, measured on 42 folds**, never re-measured since.

**IGF2R's `mean_plddt` is null** (measured 2026-07-27), so the failed fold is reported separately
rather than absorbed:

> **12 of 79 = 15.2% below the pLDDT 50 floor, plus 1 failed fold, reported separately.**
> **This supersedes D-041 §5's ~24%.**

**The floor is cheaper than D-041 feared.** Recorded with the same rigour a movement against the
project would get.

#### Finding 3 — the four denominators the scorer depends on

| Quantity | Value | Status |
|---|---|---|
| **Ranking denominator** — folded ∧ `ranked` ∧ pLDDT ≥ 50 | **56** | final |
| **Comparator denominator** (D-059) — evidence score ∧ ranking set | **12** | final |
| Provisional fit set — probable positives ∧ ranking set | 12 | **superseded by F-003** |
| Provisional head-to-head — fit set ∩ comparator | 8 | **superseded by F-003** |

#### Finding 4 — the comparator's covered set is positive-enriched, and this is pre-registered

**8 of 12** scored-and-rankable targets were probable positives (**67%**) against **12 of 56**
across the ranking set (**21%**). Expected — the paper's high-evidence targets are the ones people
built ADCs against — but **every comparator statistic is computed on a small, non-random,
positive-enriched subsample.**

**Recorded before the fit**, so a correlation arriving later reads as anticipated rather than
explained away. D-041 decision 4 already warns that *"a high correlation arrives looking like
validation and is not."*

#### Finding 5 — three positives fall outside the ranking set, for three different reasons

| Target | pLDDT | Mechanism |
|---|---|---|
| **CXCR5** | 47.63 | **below floor** — folded, confidence under 50 |
| **MSLN** | 75.04 | **`held_out`** — whole-method, boundary-method incomparable (D-021 §1a). **A method exclusion, not a quality one.** |
| **MUC16** | — | **not folded** — `over_local_ceiling`, 14,451 aa |

**Three mechanisms, three named targets, none silent.** MSLN is the one worth saying aloud: the
cohort's most-attempted ADC antigen after HER2, folded well, excluded because our boundary method
cannot produce a comparable feature 4 for it.

**⚠ A real question raised and deliberately not resolved:** mesothelin is GPI-anchored, so "whole
sequence" is close to "ECD" and the incomparability argument may not bite for this target.
**Resolving it under deadline, for the one target that would add a valuable positive, would be
fitting the method to the desired outcome.** The principled version — *whole-method targets with no
cytoplasmic domain may be method-comparable* — needs its own entry and its own evidence. **Deferred
with its trigger (D-054 manner), not dismissed.**

#### Consequences

- **Every 42-fold-era statistic is stale**, as is *"79 of 82 with 3 remaining"* and D-041 §5's ~24%.
  Re-derive, never re-hardcode at today's value (D-050).
- **`/api/analyses` must not be used as a fold count anywhere.** `/api/coverage` is the D-038
  supplier for that question.
- **⚠ This measurement does NOT discharge D-041's requirement.** The labelled ∧ folded intersection
  must be **recomputed against `data/adc_reference_mapping.csv`** before the fit. See F-003.

---

### F-001 — INSTRUMENT CORRECTION: WHEA corrected-error rate was **inverted**, not merely invalid
- **Date:** 2026-07-19
- **Status:** Accepted. **This retroactively restates evidence in S-001, S-002 and S-003.**
- **Type:** Finding about the *measuring instrument*, not about the system under test. Logged
  separately because it invalidates reasoning across multiple prior entries.

**The claim:** WHEA **Id 17 (corrected)** errors are **crash debris, not a precursor ramp.** Every
comparison in this investigation that used corrected-error *rate* was measuring the wrong quantity.

**Evidence 1 — corrected errors are logged *with* the fatal, never *before* it.** Per-second
grouping of all WHEA events today:

| Second | Events |
|---|---|
| 16:32:33 | **Id1 ×1** + Id17 ×13 *(same second)* |
| 16:32:34 | Id17 ×18 |
| 16:44:45 | **Id1 ×1** + Id17 ×31 *(same second)* |
| 16:48:16 | **Id1 ×1** + Id17 ×3 *(same second)* |
| 18:04:51 | Id17 ×3 *(no fatal)* |
| 18:06:27 | Id17 ×3 *(no fatal)* |
| 19:02:29 | **Id1 ×1** + Id17 ×3 *(same second)* |

In **all four** crashes the fatal is logged **first or simultaneously** with the corrected errors.
There is no gradual ramp preceding a fatal. The corrected errors are what the machine emits *as it
dies*.

**Evidence 2 — six burst days produced zero fatals.** Corrected-error volume does not predict crashes:

| Date | corrected | fatal |
|---|---|---|
| 2026-05-27 | 3 | **1** ← crash on only 3 corrected |
| 2026-06-09 | **65** | **0** ← 65 corrected, no crash at all |
| 2026-06-13 | 3 | 0 |
| 2026-06-15 | 3 | 0 |
| 2026-07-04 | 3 | 0 |
| 2026-07-10 | 31 | 0 |
| 2026-07-14 | 40 | 0 |
| 2026-07-19 | 74 | **4** |

**65 corrected errors with no crash (06-09), versus a crash on only 3 (05-27).** The instrument is
not just noisy — it is **anti-correlated with the thing we were using it to predict.**

**RESTATEMENTS forced by this finding:**

1. **S-002's rate comparison is void.** *"65 corrected in the crashing window vs 0 in clean runs"*
   was **three crash events versus zero crash events, double-counted** — the corrected errors were
   debris from those same three crashes. **The valid measure was always the fatal count: now 4 vs 0.**
2. **The fp16 control's "zero corrected errors" is weaker than recorded.** It reduces to
   **"no crash"** — which host survival had already established independently. **The refutation of
   the spill mechanism still stands, but it stands on the fatal count, not the corrected count.**
3. **"217 corrected errors since May, pre-existing" was true and largely irrelevant.** It does not
   describe a steadily degrading link. It describes a fault that **fires in bursts and usually
   recovers**. The 18:04/18:06 events previously attributed to the driver install **may equally have
   been a spontaneous burst — that is now unknowable, and is recorded as unknowable.**
4. **What survives with no instrument at all — and it is the strongest evidence in the
   investigation:**
   > **4 crashes in 4 HER2 (630 aa) attempts. 0 crashes in ~93 Trop-2 (248 aa) folds today** —
   > across **both precisions**, **spilling and not**, including 83 consecutive folds under
   > sustained load.

   This correlation depends on no event log, no severity bucketing, and no interpretation of WHEA
   semantics. Everything else in S-002 is weaker than this one line.

- **Deep-learning justification:** neutral (instrumentation), but it protects every downstream
  decision — the local tier's viability was being judged against a metric that was measuring
  crash aftermath.
- **Method note connection:** this is the same failure as `params_all_on_cuda` and the WHEA counts —
  **a true summary that answered a different question than the one asked.** Extend the method note:
  before using a metric as a *leading indicator*, verify its events actually **precede** the thing
  it is meant to predict.

