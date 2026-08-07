# TASK 5 — 2026-08-07 — The two held terms, and the yeast term run to ground

> **Read-only. Cache and committed CSVs only, 0 fetches, no database, no ruling taken.**
> Governed by `RULINGS-2026-08-07-span-definition.md` R1 and
> `AMENDMENT-Code-2026-08-07-reparse-and-organism-check.md` A2. Where this file and the log differ,
> **THE LOG GOVERNS.** ⚠ This file is a report. **It proposes nothing. The owner rules.**

**Provenance (D-016):** identities and topology from `data/census/spancache`; experimental surface
status from the `CSPA category` column of
`data/census/membraneome-reconstructed-2026-08-04.csv`, sha256
`5a705cc9165eb863f51116c31f2a5f56080bf8941bf994a612f9d85fc6944d37`.
⚠ **The CSPA paper has not been opened at first hand — the column is inherited from the
reconstructed table, not read from the source.**

---

## §1 — ⚠ The orthogonal check exists in the repository, and it is not SURFY

The ruling asks whether the proteins carrying the held terms *"appear in an experimental cell-surface
dataset"*, on the grounds that **topology vocabulary is a curator's word choice and surface
proteomics is a measurement.**

⚠ **The table carries both, in separate columns, and they must not be confused:**

- **`Surfy` / `Surfy Score` / `surfy_class`** — the **prediction**. A machine-learning classifier.
  **A-014: a model's positive class is a prediction, not a fact.**
- **`CSPA category`** — the **Cell Surface Protein Atlas**: mass-spectrometry labelling of intact
  cells. **This is the measurement.** Distribution across the whole 7,903-row table:
  `1` → 954 · `2` → 356 · `NA` → 6,593.

---

## §2 — 5a: the five proteins carrying a held term. All surface class.

```
accession  gene       held term             largest held span   CSPA      Surfy score
P14679     TYR        Lumenal, melanosome     458 aa  (19-476)  ✅ 1      0.8343
P17643     TYRP1      Lumenal, melanosome     453 aa  (25-477)  ✅ 1      0.9022
P40126     DCT        Lumenal, melanosome     449 aa  (24-472)  ✅ 1      0.8703
Q9Y487     ATP6V0A2   Vacuolar                 74 aa (476-549)  ✅ 1      0.5988
Q13488     TCIRG1     Vacuolar                 64 aa (469-532)  ⚠ NA     0.7166
```

All five are `surfy_class = surface` — ⚠ **supporting but weaker, per A-014.** All five currently
read `no_extracellular_span` under V2, because held is not accepted.

### ⚠ The two terms do NOT get the same answer, and that is the finding

**`Lumenal, melanosome` — 3 of 3 experimentally surface-detected, CSPA category 1.** These are
tyrosinase, TYRP1 and DCT: the melanosomal enzyme family. **TYRP1 is one of the two proteins named
in the ruling's own reasoning**, and the measurement agrees with it independently. Their held spans
are **large ectodomains — 449 to 458 aa** — the shape the pipeline is built for.

**`Vacuolar` — 1 of 2**, and ⚠ **a second, separate reason to be cautious that the ruling could not
have known:** both are V-type proton ATPase subunit *a* — multi-pass proteins whose vacuolar faces
are **short loops, not ectodomains**. Their largest held spans are **74 aa and 64 aa**. ⚠ **Even if
`Vacuolar` were accepted, it would not add an ADC-shaped ectodomain; it would add two short loops.**
`TCIRG1` is additionally **not detected by CSPA.**

⚠ **Reported, not ruled.** The size observation is a fact about these two proteins, not an argument
about the term — a term ruled on the size of the spans it happens to yield today is a dial, not a
rule, and the ruling was explicit about that.

---

## §3 — 5b + A2: the yeast term. ⚠ The serious branch is CLOSED.

The amendment's stop condition — *"if the organism is anything other than Homo sapiens, STOP, run a
census-wide organism sweep, do not proceed to the manifest"* — **does not fire.**

```
accession       P0DKB6
gene            MPC1L
protein         Mitochondrial pyruvate carrier 1-like protein
organism        {"scientificName": "Homo sapiens", "commonName": "Human", "taxonId": 9606}
review status   UniProtKB reviewed (Swiss-Prot)
census class    annex

Topological domain  'Mitochondrial matrix'        2-19    ECO:0000305  PubMed 27317664
Topological domain  'Mother cell cytoplasmic'    43-51    ECO:0000305  PubMed 27317664
Topological domain  'Mitochondrial matrix'      75-136    ECO:0000305  PubMed 27317664
```

⚠ **Hypothesis 3 does not hold.** No non-human row is in the census. **"7,811 human proteins" stands
in the deck, the literature review and `P-003`, and no census-wide organism sweep is owed.**

**What remains is hypothesis 1 or 2, and the evidence points at 1 — ortholog annotation transfer.**
All three domains carry **one source and one evidence code** (`PubMed 27317664`, `ECO:0000305` —
inferred by curator, not experimental), and the `Mother cell cytoplasmic` segment sits **between two
`Mitochondrial matrix` domains** in a mitochondrial carrier. Mitochondrial pyruvate carriers are
studied in yeast; a curator transferring a topology model would carry the compartment vocabulary
with it. ⚠ **Planner general knowledge, not sourced at first hand.**

**It changes no count either way** — cytoplasmic and mitochondrial faces are rejected regardless.
Under V2 the row is `term_unruled`: **named, visible in the glossary, and not silently dropped.**
Reserved in `docs/RESERVED.md` **without an integer**, alongside four other queued findings.

---

## §4 — What this report does NOT do

⚠ **No term is accepted, rejected or re-ruled.** ⚠ **No count moves.** ⚠ **No recommendation is
offered on `Lumenal, melanosome` or `Vacuolar`** — the ruling is the owner's, and both terms remain
held and gaining nothing until it lands.
