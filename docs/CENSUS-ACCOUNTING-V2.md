# The whole census, accounted for — every row, under V2, with its reason

> **All 5,016 census rows land in exactly one bucket.** ⚠ Derived from `spans_surface.v2.csv` and
> `spans_annex.v2.csv` — **both V2** (`v2-ruled-vocabulary-2026-08-07`). No V1 artifact is used, and
> no number here is carried over from one.
>
> ⚠ **Correction to an earlier statement.** I previously said the surface set was V1-only and that
> the 1,549 could not be broken down without a re-derivation. **`spans_surface.v2.csv` existed the
> whole time — I opened `spans_surface.csv` and did not check for the V2 file.** The 230-row
> "disagreement" I flagged was V1-vs-V2 by construction (D-081: two definitions, both named,
> neither overwritten), not a defect. **Nothing needed re-running.**

---

## §1 — The top-level partition

| | rows | |
|---|---|---|
| **census** | **5,016** | `surface` 2,807 + `non_surface` 2,209 |
| ├─ **carry a foldable span** | **3,467** | ⚠ **exactly the manifest** — 0 in one and not the other, both directions |
| └─ **carry no span** | **1,549** | broken out in §2 |

⚠ **The manifest reconciles exactly.** `span but not in manifest = 0`, `manifest but no span = 0`.
Stated in both directions because a one-directional check passes while missing half the failures.

---

## §2 — The 1,549 without a span, every reason stated

| rows | class | `span_category` | reason |
|---|---|---|---|
| **1,304** | non_surface | `no_extracellular_span` | no topological domain with an accepted description, and no GPI anchor |
| **215** | surface | `no_extracellular_span` | same |
| **19** | non_surface | ⚠ *(empty)* | `not fetched: uniprot_inactive` |
| **7** | surface | ⚠ *(empty)* | `not fetched: uniprot_inactive` |
| **2** | surface | `absent_with_reason` | `gpi_chain_unannotated` |
| **1** | surface | `absent_with_reason` | `span_contains_transmembrane` |
| **1** | surface | `span_boundary_unknown` | an accepted topological domain matched and the coordinate is `UNKNOWN` |
| **1,549** | | | |

### What the big number actually means

⚠ **1,519 of 1,549 (98%) are `no_extracellular_span` — and that is a RESULT, not a gap.** The V2
vocabulary asks one biological question: *can this face ever reach the outside of the cell?* For
1,519 proteins the answer is no, on any mechanism. **A protein with no extracellular face has
nothing an antibody could bind and nothing to fold** — it is correctly out of scope for an ADC
platform, and it is out by biology rather than by failure.

⚠ **Four times more rows fall out for having no extracellular face than for being too long.**
Length is the constraint that gets discussed; it is not the one that decides the census.

### The 30 that are not that

- **26 `uniprot_inactive`** — ⚠ **never fetched.** These are *not* "no span"; they are **unknown**.
  Absence of evidence, not evidence of absence. See **`F-036`** below.
- **3 `absent_with_reason`** — a GPI anchor with an unannotated chain (2), and a span that would
  have contained a transmembrane segment (1). ⚠ **Named refusals, not silent drops.**
- **1 `span_boundary_unknown`** — ⚠ **the term matched and the coordinate is `UNKNOWN`.** This is
  the fifth thing the old `no_topology` band conflated, and the single row that made `F-025`
  detectable at all.

---

## §3 — The 3,467 that do fold, by what limits them

| span | rows | | limit | verdict |
|---|---|---|---|---|
| 1–440 | **2,691** | 77.6% | none | done or in flight on the local card |
| 441–850 | **566** | 16.3% | local VRAM | rentable 48 GB, single pass |
| 851–1,026 | **69** | 2.0% | VRAM | rentable 80 GB |
| 1,027–2,000 | 102 | 2.9% | ⚠ **trained context** | producible, unvalidated |
| 2,001–4,000 | 26 | 0.7% | context + VRAM | domain assembly |
| 4,001–14,451 | 13 | 0.4% | context + VRAM | domain assembly (10) / disordered (3) |

⚠⚠ **3,326 of 3,467 — 95.9% — sit inside the model's 1,026-residue trained context** and are
foldable as single sequences with defensible results. **141 (4.1%) do not, and that is not a
hardware problem**: `position_embedding_type = rotary` extrapolates, so a longer card buys a
structure, not an answer.

**Plus one row that is neither:** `P55073` carries `U` (selenocysteine), absent from the ESM
vocabulary — foldable only by folding a **different sequence**, with the substitution recorded
(F-033, D-085).

---

## §4 — So: is anything impossible?

**No.**

| | |
|---|---|
| 1,519 | nothing to fold — **no extracellular face**. Correct exclusion, by biology. |
| 26 | **unknown** — never fetched. Resolvable by fetching. |
| 4 | named parse refusals (`absent_with_reason`, `span_boundary_unknown`). Resolvable. |
| 3,326 | **fold today**, or on a rented card, with defensible results. |
| 138 | need **domain assembly** — a method, not a barrier. |
| **3** | ⚠ **mucins** (MUC16, MUC12, MUC17) — a structure is **producible and uninformative**. |

⚠ **The mucins are the only place in the entire census where "we cannot get a useful answer" is
true**, and even there the limit is that **the question is malformed**, not that the computation
cannot run. Tandem-repeat, heavily glycosylated, largely disordered: *"predict its ECD structure"*
is partly the wrong question (D-076, the finding embedded in it).

**3 rows of 5,016.**
