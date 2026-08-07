# ORDERS — Code — 2026-08-06 — The span-extraction audit: what `no_topology` actually excludes

> **Governed by `### D-079`, `### F-011` and `### D-077`. Restates none of them.** Where this file
> and the log differ, **THE LOG GOVERNS.** ⚠ This file is an order, not authority.
>
> ⚠ **NO FILTER IS CHANGED BY THIS ORDER.** It measures what the current filter excludes. Widening
> the vocabulary is a separate ruling that follows this measurement and is owner-reserved.

## FOUR TASKS: 0, 1, 2, 3. Sequential. Hard stop between each.
**If this document does not end with `— END OF SPAN AUDIT (4 of 4) —`, it truncated. Report and request re-delivery.**

> **Planner provenance (D-016):** §1's twelve accessions were measured by the Planner off
> `data/cohort_82_ecd.csv` in the `4b7547c` snapshot, 2026-08-06. The evidence scores and the MSLN
> carve-out are quoted from `data/evidence_scores.csv` and `data/adc_reference_mapping.csv`.
> ⚠ **The GPI-anchor identifications in Task 1 are Planner general knowledge and are NOT verified
> from any data. They are a hypothesis for you to test, not a finding.** No connector, no `.git`,
> no database.

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** read-only inspection of the UniProt JSON cache and the committed CSVs, plus one
follow-up commit correcting an overclaim in an already-pushed commit message.

**Does NOT authorise:**
- ⚠ **Changing the span filter, the term list, or any extraction rule.** Not one line.
- ⚠ **Re-extracting features, re-fitting, re-scoring, or re-folding anything** — the 82 or the census.
- ⚠ **Task 4 (the manifest).** It stays gated: the manifest freezes the foldable population, and
  that population is currently defined by a filter narrower than its name.
- any census row · any fold · Run B · the wiring PR · the freeze · any write to `ranking_runs`,
  `ranking_results`, `target_scores`, `protein_features`, or `ranking_run` ids 2–5

## STOP AND REPORT

- Task 1 shows **any** of the 82 would gain, lose, or change a span under any widened vocabulary
- the cache does not hold an entry for one of the twelve (say which; **do not re-fetch without a word**)
- a permission denial — ⚠ **stop-and-report with the command, the point, and the artifact's state.
  Never a retry, never a workaround**

---

# TASK 0 — Correct the pushed overclaim. Do it first; it is one commit.

`e19b0bf`'s message states, in substance, *SURFY scored 1,858 proteins that have no UniProt membrane
topology today.*

⚠ **That is not established and the code says why.** `scripts/ecd_lengths.py:193-196`:

```python
if feat.get("type") != "Topological domain":
    continue
description = feat.get("description", "") or ""
if "extracellular" not in description.lower():
    continue
```

**What is measured is *no `Topological domain` whose description contains the substring
"extracellular"*.** Your own audit shows **752 of the 1,858 annex rows and 121 of the 448 surface
rows carry topological domains** — under other vocabulary.

**Write a follow-up commit on the same branch.** ⚠ **Do not amend or rewrite pushed history** —
`e41ce85`/`eab1d63` precedent: the mistake and its correction both land, in order.

**It must carry:** the narrowed claim · the file and line numbers above · the three-way split
(**873** recoverable by vocabulary · **931** TM-with-no-topological-domain · **502** neither) ·
and the note that **both foldable counts, 2,352 surface and 332 annex, are floors rather than
populations.**

⚠ **Do not rename the band in this commit.** Renaming is a code change and belongs to the ruling
that follows Task 3.

---

# TASK 1 — ⚠ THE GATE. Does the vocabulary gap touch the 82?

**Twelve of the 82 have `n_extracellular_spans == 0` and bucket `unknown`.** Measured off
`data/cohort_82_ecd.csv`; no error rows; the extractor ran cleanly and returned nothing:

```
P51801 CLCNKB · Q9UJA9 ENPP5 · Q6ZNA5 FRRS1 · P35052 GPC1
P11717 IGF2R  · Q13421 MSLN  · Q8N4M1 SLC44A3 · O15455 TLR3
Q6UXF1 TMEM108 · Q9NV96 TMEM30A · O14798 TNFRSF10C · Q16880 UGT8
```

⚠ **Why this gates everything.** Every feature in `### F-004` and `### F-017` — including feature 1,
ECD length — was computed on spans this filter produced. **If the definition changes and any of the
82 moves, the committed result and any future result are no longer comparable.**

**And two of the twelve are not incidental:**

- **`MSLN` and `GPC1` both carry Kathad evidence score 4** (`data/evidence_scores.csv`).
- ⚠ **`adc_reference_mapping.csv`'s own carve-out names MSLN:** *"CXCR5, MSLN and MUC16 were routed
  probable-positive by the registry pass and have NOT yet been verified; they are absent because
  **unverified, NOT because negative**."*

⚠⚠ **So a probable positive is excluded from the ranking set by an extraction failure rather than by
a labelling decision. `n=12` — the binding constraint on every claim this project makes — may be
partly an artifact of this filter.** That sentence is the reason Task 1 outranks the census work.

## For each of the twelve, from the cache — read-only

Report **one line per accession**, `accession | gene | field | value`:

1. does it carry **any** `Topological domain` feature — and if so, **every distinct `description`
   value with its span**
2. does it carry a **`Transmembrane`** feature
3. ⚠ **does it carry a GPI-anchor annotation** — UniProt records this as a **lipid-moiety-binding
   site**, *not* as topology. **Report the feature type and description verbatim; do not normalise**
4. `signalPeptide` / `Signal` feature, if present, with its span
5. sequence length

⚠ **PLANNER HYPOTHESIS, UNVERIFIED — test it, do not assume it.** MSLN, GPC1 and TNFRSF10C are, to
the Planner's general knowledge, **GPI-anchored**: attached by a lipid anchor, never crossing the
membrane, therefore **no `Transmembrane` and no `Topological domain` at all**, while the entire
mature chain is extracellular. **If that holds, widening the term list recovers nothing for them —
they need a different extraction rule.** ⚠ **If it does not hold, say so plainly; a refutation here
is as useful as a confirmation and this Planner has been wrong twice today.**

## Then the ruling input

**State, for each of the twelve, which bucket it falls in:**

| | Mechanism | Fix |
|---|---|---|
| **1** | Lumenal-family vocabulary | Widen the term list |
| **2** | TM present, faces unlabelled | ⚠ Nothing — a genuine annotation gap |
| **3** | ⚠ **GPI-anchored — entirely extracellular, no topology by design** | **A different extraction rule** |
| **4** | Genuinely not a membrane protein | Correctly excluded |

**Then stop and report before Task 2.**

---

# TASK 2 — The same question over the census `no_topology` populations

**Cache only. No network. Every JSON is already on disk.**

**2a — The 502 with neither TM nor topological domain** (372 annex + 130 surface). ⚠ **How many
carry a GPI-anchor annotation?** **If a meaningful fraction do, that bucket is not "not membrane
proteins" — it is a targetable class the pipeline is structurally blind to**, and it contains the
same category as CEACAM5, one of F-009's four clinically-validated missing targets.

**2b — The 931 with TM and no topological domain** (734 annex + 197 surface). Report the distinct
feature types present, so the gap is characterised rather than named.

**2c — The 873 recoverable by vocabulary.** ⚠ **Report per-term protein counts, not domain counts.**
The earlier tabulation gave domains (843 Lumenal in the annex, 265 Lumenal-family in the surface);
**one protein can carry several, and the ruling needs proteins.**

⚠ **Report each term separately and do not group them into "non-cytoplasmic."** The distinction is
biological, not lexical, and Task 3 depends on the terms staying apart.

**Then stop and report before Task 3.**

---

# TASK 3 — Assemble the ruling input. Do not make the ruling.

**Produce one table the owner can rule from, and nothing else:**

| Term | Proteins, annex | Proteins, surface | Compartment |
|---|---|---|---|

**Terms observed so far** — ⚠ **re-derive from the cache; do not trust this list:**

`Lumenal` · `Lumenal, vesicle` · `Lumenal, melanosome` · `Vesicular` · `Vacuolar` ·
`Perinuclear space` · `Intragranular` · `Exoplasmic loop` · `Mitochondrial intermembrane` ·
`Mitochondrial matrix` · `Nuclear` · `Peroxisomal matrix` · `Peroxisomal` ·
`Mother cell cytoplasmic` · `Cytoplasmic`

⚠ **The ruling is per-term and it is biological, not lexical. Do not widen to "anything not
cytoplasmic."** Secretory-pathway faces — ER, Golgi, endosome, lysosome, secretory vesicle — reach
the plasma membrane. **Mitochondrial, peroxisomal and nuclear faces do not, on any mechanism.** A
careless widening would recruit roughly **418 annex domains that cannot be ADC targets**, and it
would do so in the direction that makes the atlas look bigger. ⚠ **That is the failure mode to
design against here.**

**Report the table. Do not propose a term list, do not change the filter, do not rename the band.**

---

## REPORT BACK

Plain lines, `label | value`. **No box-drawing tables** — eleven consecutive reports have lost their
middle columns.

**Task 0:** the follow-up commit hash · gate count
**Task 1:** twelve accessions, one line each, all five fields · the GPI hypothesis confirmed or
refuted · the four-way bucket assignment · ⚠ **whether any of the 82 would move under any widening**
**Task 2:** 2a GPI count · 2b feature types · 2c **per-protein** term counts
**Task 3:** the term table

⚠ **Then stop.** Task 4's manifest stays gated until the vocabulary ruling lands. **Close the window.**

---

## STILL OPEN, AND NONE OF IT BLOCKS THIS

- ⚠ **`F-025`** — the Planner's recommendation is that this finding takes it: *`no_topology` reports
  an absence that is a vocabulary mismatch and a topology-model mismatch; the foldable denominators
  are floors; the surface class leaks too.* **Owner rules; no number taken here.**
- **Task 3's PR is not open.** ⚠ **Open it after Task 0's follow-up commit**, so it opens complete.
- **The unclassified diagnostic** — ⚠ **never delivered, never run, and its hypothesis is dead.**
  It will be reissued only if this audit leaves a question worth asking.
- **The scoring gate's reading** · **KEEL v6 into the repository** · **the A- reconciliation**.

— END OF SPAN AUDIT (4 of 4) —
