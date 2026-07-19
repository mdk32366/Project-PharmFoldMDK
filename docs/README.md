# PharmFoldMDK — Design Decision Log

> **This file is mandatory reading and mandatory writing.**
>
> **THE RULE:** *Every design decision we make gets written in this file **before** the
> work it describes is finished.* The log leads the code. If you are about to build,
> change, or discard something and the reasoning is not yet here, stop and record it
> first. A PR whose work is not reflected in a decision entry is incomplete.
>
> Companion documents:
> - [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — the current-state architecture (must be
>   updated in the same PR as any architectural change, and before any PR is filed).
> - The planning docs in this folder (TDD, DB plan, UI plan, test plan, checklist) — the
>   *original* intent. Where a decision below diverges from them, **this log wins**.

## How to add a decision

Add a new `### D-NNN` entry at the **top** of the log (newest first). Use the template:

```
### D-NNN — <short title>
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by D-XXX | Rejected
- **Context:** why this came up.
- **Decision:** what we are doing.
- **Deep-learning justification:** how this serves (or is neutral to) the DL-core mandate.
- **Consequences:** trade-offs, follow-ups, what it touches.
```

Every substantive decision must state its **deep-learning justification** — this is a
deep learning course project and the neural core is the graded deliverable (see
ARCHITECTURE §1).

---

## Log (newest first)

### D-002 — Governance: living architecture doc + this decision log
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The project must be maintainable and sustainable long-term, and its design
  rationale must be traceable for grading and for future work.
- **Decision:** Maintain `ARCHITECTURE.md` (repo root) as the single source of truth for
  system shape, updated in the same PR as any architectural change and brought current
  before any PR is filed. Maintain this `docs/README.md` as an append-at-top decision log
  where every design decision is written **before** its implementing work is finished.
  Both rules are encoded in `CLAUDE.md` so every working session is bound by them.
- **Deep-learning justification:** Neutral (process). Indirectly protects the DL mandate
  by forcing each decision to state where the deep learning is before code lands.
- **Consequences:** Slight up-front writing overhead per change; in exchange the project
  stays auditable and the DL story stays front-and-center.

### D-001 — Planning docs live in the repo under `docs/`
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Planning docs (TDD v3, DB plan, UI plan, test plan, checklist, proposal)
  were sitting in a non-git sibling folder, unversioned.
- **Decision:** Moved all six into `docs/` with flattened filenames and committed
  (`6ea1e7e`). They are the reference intent; ratified changes are logged here.
- **Deep-learning justification:** Neutral (housekeeping).
- **Consequences:** Single versioned home for project intent; the `.docx` proposal is
  tracked as binary.

---

## Open questions awaiting a decision entry

These are known forks in the road. Each becomes a `D-NNN` entry **before** we act on it.

- **DL core for Iteration 1:** run ESMFold (protein language model) locally for structure
  prediction vs. retrieve from AlphaFold DB with a neural fallback. *This is the pivotal
  decision for the course grade — resolve it first.*
- **Postgres-first vs. SQLite-on-Volume prototype** (Database Plan §5).
- **Where inference runs:** in the FastAPI process vs. a dedicated worker/queue.
- **Embedding model** for semantic search (which encoder, `vector(384)` assumed).
- **Compute for inference on Fly.io:** CPU-only vs. GPU availability, and model size that
  fits (ESMFold memory footprint).
