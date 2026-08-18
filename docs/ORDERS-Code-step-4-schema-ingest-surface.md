# ORDERS — Code — step 4: attribution, the pre-ingest audit, schema, ingest, surface

> ⚠⚠ **DOWNLOAD AND COMMIT THIS FILE. DO NOT RETYPE IT.** Paste is for reading; the file is the
> record. **AUTHORED-SHA256 range: first `## §` header to EOF. Value in the delivering message.**
>
> ⚠ Planner grounding is `7011e24`. `HEAD` is `b7ecc2a`; the branch is `392ba1d`. Repository
> statements are **as of `7011e24`** and are questions.
>
> **No GPU. No rental. No fold.** **Tranche 5 stays HELD** — `D-091` ruling 2.
> ⚠ **Production writes require the owner at the keyboard. Say what is needed; do not infer flag
> syntax.**

---

## §0 — `D-093 amendment 2` is ENDORSED. Step 4 is open

**Eight rulings and three corrections, cited by number and not restated here.** ⚠ **Read the entry,
not this summary** — *read the body, never the title* is a rule bought on 2026-08-18.

⚠⚠ **One clause the amendment SHOULD have carried and does not. It is the Planner's omission,
recorded same-day, and the prohibition is ordered now rather than after the surface exists** — §6.

---

## §1 — ⚠ The sequence, and only one thing gates the SURFACE

| step | gated on |
|---|---|
| **EA** — the attribution string | nothing. ⚠ **It gates the surface, not the schema** |
| **EB** — the pre-ingest prognostic audit | ⚠⚠ **must complete BEFORE any ingest** |
| **EC** — schema | `EB` |
| **ED** — ingest | `EC` |
| **EE** — surface | `ED` **and `EA`** |

⚠ **Decision 6's bar is question (3), and HPA passes it — so HPA enters the schema now.** **But
amendment 1 clause 3 requires four-part attribution wherever the data renders**, and item 5 is
unanswered. **So schema and ingest proceed; the surface cannot render until `EA` lands.**

## §2 — Task EA — item 5, and it is reading, not research

**Read `https://v22.proteinatlas.org/about/licence`. Record the required attribution string
VERBATIM, with the URL and the date read.**

⚠ **Verbatim** — not a description of the obligation, not a paraphrase, not amendment 1 clause 3
restated. ⚠⚠ ***`D-093` amendment 1 exists because a licence was recalled rather than read.***

**Report it, and report whether it agrees with amendment 1 clause 3's four parts.** ⚠ **If it
disagrees, STOP AND REPORT** — clause 3 would then be a second recollection, and that is a finding.

## §3 — ⚠⚠ Task EB — the pre-ingest prognostic audit. BEFORE any row is written

**Correction 1 corrected the rule. It did not measure the tree.**

**EB1 — Enumerate every cached artifact under `data/` and report whether ANY carries a column
matching `prognos`**, case-insensitive. **Every file, with its path — not a summary verdict.**

**EB2 — ⚠ If the tree is clean, record it as LUCK STANDING IN FOR PROCESS, not as compliance.**
The guard that should have caught it was matching a string that never occurs. **A clean result here
was not produced by the control.**

**EB3 — ⚠⚠ If ANY cached artifact carries one, STOP AND REPORT.** **Ingesting from it is a licence
question, not a code question, and it is the owner's.** **Do not delete, do not filter, do not
proceed.**

**EB4 — The ingest excludes those columns by name AND asserts the exclusion on the written table.**
⚠ **Column-scoped means presence is the violation, not use.**

## §4 — Task EC — schema, tests first

**EC1 — ⚠⚠ The category layering. Ruling 5 gives the PRINCIPLE; produce the complete MAPPING.**
The five measured categories — `ihc_present` · `ihc_gene_absent` · `ihc_panel_empty` · `hpa_absent` ·
`accession_ambiguous` — do not all live on one layer. **`hpa_absent` and `accession_ambiguous` are
outcomes of the MAPPING; `ihc_gene_absent` and `ihc_panel_empty` are the SUPPLIER's encoding.**

⚠ **Produce the layer table yourself and assert it PARTITIONS: every one of the five lands in exactly
one cell, and the cells sum to 3,467 for the manifest and 2,690 for the folded set, separately.**
**Do not pool them.** ⚠ **If three layers are needed rather than two, say so — the Planner ruled a
principle, not a column count.**

**EC2 — `evidence_type` is an ORDINAL enum** (decision 2), and `differential_expression` is its
weakest value. ⚠ **`therapeutic_precedent` is present as a label and is NOT ordered above anything**
— it is not evidence of suitability, it is evidence somebody else tried.

**EC3 — ⚠ A count cannot be stored without its denominator.** Schema-level, not convention-level: **`n`
travels with every number.** Panels are median **11**, max **12**; **246 of 1,640** Kathad rows at
**n ≤ 4**.

**EC4 — ⚠⚠ Assert `Level`'s FULL value set and red on an unhandled value.** All eight, including
`N/A` 1,860 · `Ascending` 172 · `Descending` 73 · `Not representative` 9. **Prove it red by removing
one from the handled set.**

**EC5 — Absent row ≠ `Not detected`.** Ruling 6. **Two columns or two states, never one.**

## §5 — ⚠⚠ Task ED — ingest, and the acceptance bar is already sitting in the tree

**Pre-register the bar in its own commit BEFORE running the ingest**, as `d0fd95e` did for `CA`.

**ED1 — THE BAR: reproduce `D-100` FROM THE INGESTED TABLE, not from the file.** Convention A,
denominator including *Not detected*, must give **337 / 337** kept pairs and exclude **1,303 /
1,303**, with all four count columns identical across **1,640 / 1,640** rows.

⚠⚠ **This is two paths to one quantity — the TSV and the database — compared once, deliberately, on
the numbers.** **If the ingested table reproduces Kathad's grid, the ingest is correct; if it does
not, the ingest is wrong and no row count would have told you.** **The bar costs nothing because
`D-100` already established it.**

**ED2 — Report row counts by supplier with the key**, and ⚠ **both directions**: rows ingested with
no census accession, and census accessions with no ingested row. **A one-directional check cannot see
orphans.**

**ED3 — ⚠ Production write requires the owner at the keyboard.** **State what is needed. Do not infer
the command.**

## §6 — ⚠⚠ Task EE-0 — THE PROHIBITION THE AMENDMENT SHOULD HAVE CARRIED. Write it before the surface

**`P-001` asks whether a STRUCTURE-derived ranking reorders an EXPRESSION-based one.**

⚠⚠ **If ANY clinical-layer field reaches the scorer's feature path, that question becomes
unanswerable — the structural axis would be validated against a ranking that already contains
expression.** **This is worse than the `therapeutic_precedent` circularity, because it would not be
visible in the output.**

**`test_the_scorers_feature_path_is_closed` currently bars `therapeutic_precedent`. ⚠ WIDEN IT TO
EVERY CLINICAL-LAYER FIELD** — expression counts, levels, `qh`, evidence types, reliability, all of
them. **Prove it red by wiring an expression count into the feature vector.**

⚠ **This is a Planner omission from an endorsed amendment, recorded same-day. `F-047` member 11**,
and it wants a line in `D-093` amendment 3 — **the Planner will write it; do not wait for it to
build the test.**

## §7 — Task EE — the surface

**The seven previewed items stand, amended by the rulings:**

1. **Expression renders; burden does not exist.** `burden_supplier_unlicensed` is a **named visible
   category**. ⚠ **`§8.5` is now WRITABLE — the renderer exists** — so: a test that the surface never
   renders a blank there.
2. ⚠ **`differential_expression` is labelled as such, never as *"associated with"*.**
3. **Absence renders as the DERIVED FACT; the record keeps the SUPPLIER ENCODING** (ruling 5).
4. **The n travels with every number.**
5. ⚠⚠ **BOTH EDGES SIDE BY SIDE, EACH IN ITS OWN UNITS, WITH THE INCOMPARABILITY STATED** (ruling 4).
   **No ratio, no difference, no contrast, no index.** **Prove it: a test that reds if tumour and
   normal values are combined into one expression.**
6. ⚠ **Whatever bar the surface uses is NAMED IN FRAME.** *Reaching* has no natural rule — **all-20 is
   785 at any detection, 57 at `qh ≥ 150`, 35 at any `High`.** **A factor of 22 between bars.**
7. ⚠ **Reliability disclosed, no asymmetric filter** (ruling 8). 182,628 `Uncertain` on the normal
   side; **no reliability column at all on the tumour side.**
8. **`therapeutic_precedent` renders with its circularity warning in the same frame** — the GPI-badge
   pattern.
9. ⚠⚠ **`D-094` mount preconditions apply and `F-048` is on these same pages.** **A cancer association
   beside a five-residue span must not become a second place where that span looks authoritative.**
10. **Four-part HPA attribution, all parts together, version-pinned URL.** ⚠ **Blocked on `EA`.**

⚠ **Walk the surface after it lands.** *UI honesty gaps are found by walking, not only by tests* —
and the 3Dmol defect is the standing proof.

## §8 — Report

Branch and tip · ⚠ **number and title of any entry landed, in the message that lands it** · the
invariant with its keys · the gate without `.env` sourced · **and the `D-100` reproduction from the
ingested table, as numbers.**
