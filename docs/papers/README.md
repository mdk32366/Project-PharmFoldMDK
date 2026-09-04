# `docs/papers/` — the paper phase

> **What this folder is.** The home for the work that turns a frozen result into a submitted paper:
> the systematic literature review, the opened primary sources, and the derived reading surfaces
> written for people who are not going to read the log.
>
> ⚠ **What this folder is NOT.** It is **not** a second claim register. **`docs/PAPERS-v2.md` is the
> claim register** and it did not move — see [D-108](../README.md). A paper enters by getting a
> `## P-NNN` section *inside* that file, with a **stated claim** and a **named gate**. Nothing in
> here creates, promotes, or demotes a paper.
>
> **Governing order, highest first:** `docs/README.md` (the decision log) → `docs/PAPERS-v2.md` (the
> claim register) → anything in this folder. Where a file here and a log entry differ, **the log
> entry governs.**

---

## Where things live

| Folder | What goes in it | The bar for entry |
|---|---|---|
| `surfaces/` | Derived reading surfaces — proposals, summaries, decks, abstracts, anything written for a reader outside the project | ⚠ Each file **names the entries it derives from** in its header, and states that the log governs. Non-authoritative by construction. |
| `litreview/` | The systematic review — protocol, search log, screening decisions, the PRISMA counts | The protocol is written **before** the searching, and the search log records queries and dates, not just results. |
| `sources/` | One file per **opened** primary source, with its provenance | ⚠ *Opened* means read, not cited from an abstract. A source nobody opened does not get a file here. |

## ⚠ What did NOT move, and where to find it

Ten citations across the log and the sealed rulings write these paths explicitly, and
[`../RESERVED.md`](../RESERVED.md) line 82 is **forward-only: existing citations are not rewritten.**
So these stayed put deliberately — this table points, it does not relocate:

| Document | Path | What it is |
|---|---|---|
| The claim register | [`../PAPERS-v2.md`](../PAPERS-v2.md) | **The authority.** P-001, P-002, P-003 and the rules that make several papers safe. |
| Paper-phase orientation | [`../PREWORK-2026-08-paper-phase.md`](../PREWORK-2026-08-paper-phase.md) | What a paper actually is, the novelty search, and §0's *do not touch the build*. |
| P-001 amendment 2 | [`../P-001-amendment-2-underpowered.md`](../P-001-amendment-2-underpowered.md) | ⚠ **Paste-ready, not yet merged** — it belongs *inside* `PAPERS-v2.md` under P-001. |
| P-001 amendment ‹N› | [`../P-001-amendment-N-pooled-comparator.md`](../P-001-amendment-N-pooled-comparator.md) | ⚠ **Paste-ready, not yet merged** — same. |

## The index

### `surfaces/`

- [`PROPOSAL-2026-09-02-scholarly-paper.md`](surfaces/PROPOSAL-2026-09-02-scholarly-paper.md) —
  the non-specialist case for the paper. **Revision 2, 2026-09-02. Draft; the branch is not
  selected.** Derives from **D-015 §1** · **D-100** · **F-043** (⚠ OPEN, withdrawn figures) ·
  **F-004** · **F-005** · **F-017** · **F-009** · **F-051** (⚠ OPEN) · **D-075** ·
  [`../PAPERS-v2.md`](../PAPERS-v2.md) P-001.
  ⚠ Carries a **D-074 obligation**: it cites the expression ranking, so §2.1 must carry the
  statement of what the comparator gets wrong. **Not optional; not cuttable for length.**

### `litreview/` · `sources/`

Empty. The lit review is named as open in P-001 (*"systematic lit review (PRISMA-grade)"*) and has
not started.

---

## ⚠ Open — carried from the proposal's §7, and NOT discharged

The proposal states its own definition of done. It is restated here so it is not lost by living only
inside the document it binds. **Revision 2 discharged two items and added two.**

- [x] **§6.1 revised after Run A** (F-017). ⚠ **Revised again when Run B resolves or is formally
      abandoned** — Run B is *blocked*, not pending.
- [x] **§2.1 carries the F-043 D-074 statement**, with the withdrawn flip-rate figures excluded by
      name.
- [ ] **Cross-check against [`../README.md`](../README.md) and [`../PAPERS-v2.md`](../PAPERS-v2.md).**
      ⚠ **Partially discharged at revision 2 — against a DIRTY snapshot.** Re-check against a
      commit. This is the item that caught revision 1; it stays open.
- [ ] **§2 gains the per-target filter trace**, or keeps its explicit *not established* marker.
- [ ] **The near-cutoff check on the four false negatives** — pre-registered, not yet run.
- [ ] **The §6.2 over-claim guard respected in every derived artefact** (deck, abstract, email).
      *The expression method has documented blind spots* is established, and §2.1 now measures one.
      *This project's scorer fills them* is **not**, and does not become established by being
      restated somewhere new.
- [ ] **Every cited entry resolves.** Re-run at revision 2 (2026-09-02): D-015, D-074, D-075, D-100,
      F-004, F-005, F-009, F-017, F-043, F-044, F-051 all resolve as `###` headings in
      [`../README.md`](../README.md); P-001 as a `##` heading in
      [`../PAPERS-v2.md`](../PAPERS-v2.md). ⚠⚠ **Left open deliberately.** Per **F-044**, the
      citation invariant proves a reference *resolves* — **never that it resolves to the right
      thing.** Checking it is not the same as checking the claim.

---

## ⚠ Why the checklist above stays open

Revision 1 of the proposal asserted that the deciding run was outstanding and held both branches at
equal weight. **F-017 had been in the log since 2026-08-06.** The assertion was made from stale
context and it was wrong; it landed under D-108 carrying the error, and revision 2 records it as a
Planner finding in its §8 rather than absorbing it.

**D-108 left this checklist open rather than marking it discharged, and that is what made the error
visible on the next grounding.** So the rule this folder runs on:

⚠ **Never assert absence from a stale snapshot** (KEEL V9). *Not in the log* is a claim about the
log as it is **now**, and it requires re-grounding — not recall. A checklist marked done is a
snapshot; a checklist left open is an instruction to look again.
