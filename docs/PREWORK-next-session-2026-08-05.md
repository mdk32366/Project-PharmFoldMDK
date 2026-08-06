# PRE-WORK — next session (baton from 2026-08-05)

> **Read this, `CLOSEOUT-2026-08-05.md`, and `ARCHITECTURE.md` first.** New chat; upload nothing; let
> the Planner read the connected repository.
>
> ⚠ **Confirm the connector by quotation of a specific named file before trusting anything the
> Planner says about repository state.** Green status is not proof. **On 2026-08-04 and 2026-08-05 the
> Planner had no connector** — a zip and a tree, respectively.

---

## §0 — Confirm before doing anything

1. `git log --oneline -1` on `main`. **Expected `#126` merged.** Report the hash.
2. **The `RESERVED.md` checker — read the output, not the exit code.** Confirm F-017 through F-023
   and A-014/A-016/A-017 all resolve or are reserved.
3. **Migration state, column by column.** `alembic_version` **and** `membrane_proximal_sasa`
   **separately**. ⚠ Expected `0007_membrane_proximal_sasa` / PRESENT. **They must agree.**
4. **Feature 7:** 79 non-null, IGF2R the sole null, ranking-set 56 of 56.
5. **`ranking_runs` (4, 4)**, `ranking_results` 4, `target_scores` 168.

⚠ **Items 3–5 need the tunnel.** `.\scripts\dev-up.ps1 -NoWorker`, then a window with **both** the
venv activated and `.env` loaded — those are separate steps and conflating them cost an hour on
2026-08-05.

---

## §1 — Run A. It is executable for the first time and it is still the spine.

**Deferred five times. The fifth was not a scheduling choice** — the pre-registration's input had
never existed, and no document revealed that.

**Now in place:** feature 7 measured on all 56 ranking-set rows · the guard proven refusing **and**
passing against live production · features 1–6 byte-identical across two passes · id=2 and id=3
untouched · **the frozen interpretation in the log, unread.**

**Governed by `ORDERS-Code-2026-08-05-D-075-run.md`**, whose §4 was **replaced by deletion** — it
reproduces none of Decision 4 and cites `docs/README.md` instead.

⚠ **Three things that will be under pressure with a Pfizer date nine days out:**

1. **Quote the fired row from the log before writing any prose about what it means.**
2. **The log's Decision 4 has SIX rows**, and the third — *the three statistics disagree → reported
   as a split, not resolved to one number* — is **the case the log names as expected at n=12.** A
   Planner-authored table once dropped it.
3. **The `no_plddt` baseline is not chance.** ⚠ And **`plddt_only` (id=4) is not an anchor.** The
   anchors are FULL (id=2) and `no_plddt` (id=3), and nothing else.

**⚠ Enter Run A deliberately, by its own order, in its own window. Never as the next command after
something else** — after the fill, the obvious invocation *is* Run A (close-out error 8).

---

## §2 — The F-017 follow-up commit (small, and it closes two things)

- **F-023's closure** — persist IGF2R's feature-7 `null_reason`. ⚠ **The extractor computes it
  today**; it is persisted, never invented. **D-074: not closed until `protein_features` holds no
  bare null.**
- **Assert the assembler's `WARNING: … re-run scripts/extract_features.py` no longer prints.**
  Unreachable now — ⚠ **assert it, do not reason it.**
- **The three environment findings** and the **`80 written / 79 valued`** imprecision.

---

## §3 — Then the census, which has not started

**`ORDERS-Code-2026-08-05-census-ingest-and-tranches-v2.md`** governs, as amended by six rulings.
⚠ **Nothing in it has run.** Order: Task 1 (0008 + tranche column) → Task 2 → Task 3 → Task 4/4a/4b
→ Task 5.

**Standing constraints, unchanged:**

- **No census row before the tranche column ships.** `protein_analyses` is still the cohort.
- **The census key is `uniprot_current_accession`.** Surface **2,807** · non_surface **2,209** ·
  unclassified **2,793** · class_conflict **2** = 7,811. ⚠ **Four denominators, never summed. Every
  count states its key.**
- **Scoring is inference, never refitting.** ⚠ **No census row is scored before D-075 fires** —
  asserted by an import test, proven by revert.
- **Fold everything reachable; record the recipe on every fold; state the composition beside every
  statistic** (owner ruling). The **precision overlap set** is what makes that recoverable rather
  than merely disclosed — its design lands as **D-078**.
- **Tranche = execution order, never a filter.** Seeded permutation within band; **band-conditional
  statistics reportable, census-wide ones not.**
- **An absent value is a CATEGORY, never a low number, never a bare null.**

---

## §4 — Carried rulings and blockers

| Item | State |
|---|---|
| **KEEL v6 into the repository** | ⚠ **Blocks two things** — the four-document migration *and* the A- reconciliation, which must check **A-014, A-016, A-017**, not only A-017 |
| **The four-document migration** | Owner-ruled: cleanup after feature value. **Today produced ~20 loose files in `docs/`; the case is stronger, the target still unknown.** |
| **D-078** | Trigger amended — *the first census fold at a second precision* |
| **P-002 / PRISMA** | Flow diagram only, never a compliance claim. P-002 remains one good question and four unverified names |

---

## §5 — The two disciplines this session earned, both binding

**`A-017 (the fixture must discriminate)` — a gate requirement, not a lesson.** Any order requiring
proof-by-revert requires the positive control alongside it. **(a)** the fixture reaches the code;
**(b)** each property gets its own test, since a compound test proves only its first failing
assertion; **(c)** the fixture contains a case where correct and incorrect differ. **Five instances,
two agents, one day.**

**`F-022` — independence of source is not independence of inference.** ⚠ Two independent
pre-registrations agreed and were both wrong, because both derived from one artifact. **The
protection was writing the expectation down, not the second reader.** So: **pre-register the expected
post-state before any production write**, in both parties' own words, **before the numbers exist.**

---

## §6 — The through-line, and what it implies for the next order

**Nothing this session crashed.** Every defect would have produced a dated, hashed, provenanced,
plausible artifact — a band split reading `no_topology` for 2,807 proteins, a feature table doubled,
HLA-B weighted 83-fold, a sensitivity run firing the expected row for the wrong reason.

⚠ **The Planner produced eleven defects in one session against a prior rate of about two.** That
tracks the volume of specification written, not the reviewer's diligence. **The implication for the
next order is fewer, smaller orders with their premises checked against the tree before they ship** —
and, where an order specifies both a producer and a consumer, **the contract test between them named
in the same order, or neither specified.**
