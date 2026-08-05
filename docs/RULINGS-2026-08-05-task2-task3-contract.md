# RULINGS — 2026-08-05 — The Task 2 → Task 3 contract break, and the reader that improvises

> **COMMITTED 2026-08-05 with `### D-079` (`docs/README.md`). CITED BY the log, not restated in it —
> where this file and the log differ, THE LOG GOVERNS.** ⚠ This file is provenance for a decision that
> lives in the log; it is not itself authority. Check the `### D-079` header, not a reference to it.

> **Ruled by the Planner, 2026-08-05, in response to Code's checkpoint-2 report.**
> **Found by Code**, inspecting committed code while executing an unrelated instruction. Verified by
> the Planner against `scripts/ecd_lengths.py:114-129` and `scripts/census_spans.py:95,111-113` in the
> `feafeff` tree. **Thirteenth instance of the two-paths class; Planner error.**
>
> **Task 2 resumes only after this document lands.** Task 3 does not start until §3's contract test
> is green and has been proven to bite.

---

## §1 — The defect, confirmed, and it is worse than a break

`ORDERS-Code-2026-08-05-…-v2.md` §2 specifies Task 2's output as
`entry_name, source_accession, uniprot_accession, status, bucket, resolved_on`.

`scripts/census_spans.py:111` gates every span fetch on:

```python
if row["id_status"] == "resolved" and row["accession"]:
```

fed by `read_accession_map`, which reads `row.get("accession")` and
`row.get("status") or row.get("id_status") or "resolved"`.

**Against Task 2's schema, both halves of that gate fail:**

1. **There is no `accession` column** — Task 2 emits `source_accession` and `uniprot_accession`. So
   `accession` is `""` on every row.
2. **No bucket is ever the string `resolved`.** `status` under the new schema carries UniProt's
   vocabulary (`active_reviewed` / `merged` / `inactive`), which never equals `resolved`. Even with
   the column renamed, **the gate never fires.**

**⚠ And it fails silently, in the worst available direction.** An empty accession is not an error on
that path — it simply skips the fetch. `span` stays `None` for all 2,807 rows, `census_split`
classifies every one as unmeasured, and **Task 3's deliverable — "report the band split, counted off
the file" — comes back as `no_topology` / `unresolvable` for the entire census.** A confident,
dated, hash-provenanced artifact that is wrong about every row, with nothing red anywhere.

**⚠ Note the direction, because it is a new shape for this project.** The absent-value rule has been
caught before coercing absence to a *low* value (`(b.mean_plddt ?? 0)`, `TargetList.jsx`). Here
absence is not coerced low — **a resolvable target is recorded as having no topology.** The category
is not lost; it is **invented**. That is a fabrication, not a smoothing.

---

## §2 — Ruling on the two options Code raised

Code named two paths and correctly declined to choose. **Option (a) is adopted. Option (b) is
refused, and the refusal is the point.**

**❌ Option (b) — Task 2 emits a separate file and leaves `accession_map.csv` alone: REFUSED.**
That produces **two files describing the identity of the same 2,807 proteins, with nothing comparing
them.** It is the two-paths class, proposed as the fix for an instance of the two-paths class. It
would also be the cheapest option today and the most expensive one in three weeks, which is the
signature of every prior instance.

**✅ Option (a) — one file, and the consumer changes with it: ADOPTED**, with two additions that
Code's framing did not include and that are where the actual protection lives.

---

## §3 — What Task 2 emits, and what the reader does about it

### 3.1 — Eligibility is **decided once, by the producer**, and named

Task 2's output gains two columns:

| Column | Meaning |
|---|---|
| `census_accession` | ⚠ **Defined in `SPEC-2026-08-05-accession-map-schema.md` §3. Not restated here.** |
| `fetch_eligible` | `true` / `false`. Computed by Task 2 from `bucket` **and** `uniprot_status`. |

⚠ **The 52 `inactive` rows are genuinely unfetchable** and must be `fetch_eligible=false` with their
reason retained — they are an absence with a cause, not a failure.

**Task 3's gate becomes `if row["fetch_eligible"]`** — a boolean the producer computed, not a string
comparison against a status vocabulary that lives in a different file and will drift. **One place
decides eligibility; one place reads the decision.**

### 3.2 — ⚠ `read_accession_map` must **refuse**, not default. This is the load-bearing change.

The reader currently improvises: a missing column becomes `""`, and — worse —
**a missing status becomes `"resolved"`.**

**`scripts/census_spans.py`'s own docstring says it "refuses on missing input rather than improvising
a substitute."** It does that at the **file** level and violates it at the **column** level. The
principle was stated, implemented one layer up, and left unimplemented one layer down.

**Ruling:** `read_accession_map` **raises** on a missing required column, and **raises** on an
unrecognised value in `fetch_eligible`. **The `or "resolved"` default is deleted, not corrected** —
an absent status silently becoming an affirmative one is the defect, and a different default is the
same defect with a different value.

**Red-then-green, corrected form (A-016 — a realistic mistake, failing at the assertion):** feed the
current reader Task 2's new schema. Today that produces a clean empty result. After the change it
must **raise, naming the missing column.** ⚠ Confirm the red fires at the assertion, not at import.

### 3.3 — The cross-file contract test, which is the only thing that prevents recurrence

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_span_reader_accepts_the_map_writer_s_header` | The header Task 2 **actually emits** is accepted by `read_accession_map` with every required field populated | Renaming one column in the writer → red |
| `test_a_fetch_eligible_row_actually_fetches` | A row with `fetch_eligible=true` reaches the fetch path; **assert on the call, not on the output** | Reverting the gate → red |
| `test_zero_eligible_rows_is_an_ERROR_not_a_result` | A map where **no** row is fetch-eligible **raises**; it does not emit a histogram | Emitting an all-`no_topology` split → red |

⚠ **The third test is the one that would have caught this.** The first two pin the contract; the
third pins the **outcome** — and this defect's whole danger was that it produced a plausible artifact
rather than an error. **A census where nothing is fetchable is not a census result. It is a broken
pipeline wearing one.**

---

## §4 — Two smaller items, both ruled

1. **`census_spans.py:95` cites a superseded document** in its `_require` error string —
   `ORDERS-Code-2026-08-04-b-scale-readiness §2`, which #3 §2 supersedes. ⚠ **An error message
   exists to tell the next person where the input comes from**; a stale pointer there is worse than
   no pointer. Update to `ORDERS-Code-2026-08-05-…-v2 §2` **and** D-079 dec 5.
2. **The `or "resolved"` default is its own finding, independent of Task 2.** Any CSV lacking a
   status column would have had every row treated as resolved. **Reserve `F-018`**
   (⚠ `F-017` is held for the D-075 result) — *an absent status recorded as an affirmative one; the
   absent-value rule violated in the passing direction.* Write it when the fix lands, not before.

---

## §5 — Planner accountability

**#3 §2 specified a producer schema and #3 §3 specified a consumer, in the same document, and never
compared them.** The order even instructs Task 3 to *"start from Task 2's outputs and not re-derive
them"* — which is correct, and which made the mismatch load-bearing rather than cosmetic.

⚠ **Thirteenth instance of two-paths-to-one-quantity, and the second in as many days inside
Planner-authored orders** (the F-017 double-claim was the twelfth). The pattern in both: **two things
that must agree, written in one sitting, with nothing asserting they agree.** Proximity in a document
is not a comparison.

**Standing consequence:** where an order specifies a producer and a consumer, it **names the contract
test between them in the same order**, or it does not specify both. Recommend this enters the
close-out and is proposed to the assumption register when KEEL-4 lands against v6.

---

## §6 — Sequence, resumed

1. **Merge #122** — owner. Then Code re-runs the confirmation block **against `main`**.
2. **#2, the D-075 run** — unchanged, unaffected by any of this.
3. **#1 merges** (docs-only), plus this ruling and `F-018`'s reservation.
4. **#3 Task 2 resumes** under §3.1's schema.
5. **#3 Task 3 starts only after §3.3's three tests are green and proven to bite** — the third one
   especially. Its red is an all-`no_topology` split, which is exactly what today's code would have
   shipped.
