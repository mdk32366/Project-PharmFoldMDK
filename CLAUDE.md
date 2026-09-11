# CLAUDE.md — Project rules for PharmFoldMDK

These rules are binding for every working session on this repo. Follow them exactly.

## Context

PharmFoldMDK is an **Antibody-Drug Conjugate (ADC) target exploration platform** built as
graded coursework for a **Deep Learning** class in an ML Master's program.

## The Prime Directive — deep learning must do load-bearing work

This is a deep learning course project. A neural network must be responsible for a primary
output; do not ship a deliverable that is only a wrapper around an external service.
Evaluate every decision against: **"Where is the deep learning, and does our system run or
use it in a defensible way?"** See `ARCHITECTURE.md` §1.

## Living-documentation rules (mandatory)

1. **Design-decision log leads the code.** *Every design decision gets written into
   `docs/decisions.md` **before** the work it describes is finished.* If the reasoning isn't
   logged yet, log it first (append-at-top `D-NNN` entry with a deep-learning
   justification), then build.

   ⚠ **The entries moved on 2026-09-11 (`D-156`).** The five KEEL documents are five files, and
   `docs/README.md` is **no longer the log** — it holds the rules, the method notes, the entry
   template and the open questions. Write entries here:

   | document | holds | the question it answers |
   |---|---|---|
   | `docs/decisions.md` | `### D-NNN` | *Why is it like this?* |
   | `docs/findings.md` | `### F-NNN` | *How do we know?* |
   | `docs/assumptions.md` | `### A-NNN` | *What are we taking for granted?* |
   | `ARCHITECTURE.md` | current-state shape | *What am I looking at?* |
   | `docs/Test_Plan.md` | the guards | *What would catch it if it broke?* |

   **The allocator is `docs/RESERVED.md`.** It holds the **next free `D-`, `F-` and `A-` integer**,
   and ⚠⚠ **the pointer moves in the SAME commit that spends one.** Never take a number without
   reading it; the pointer once drifted by thirty-six integers because nothing asserted it.
   ⚠ `docs/SHIP-INDEX.md` (formerly `docs/decisions.md`) is the ship index — *which id ships what* —
   and is **not** the log.

   **⚠ A commit message naming a decision does NOT discharge this rule** (added 2026-08-03 after
   **D-062**). PR #90 was titled *"F-004 + D-062: the pre-registered result, and the scorer surface
   that renders it"* and its diff added `### F-004` and **no `### D-062`**. The surface shipped, and
   **thirteen** later citations treated D-062 as settled authority — pointing at an entry that was
   never written. **The check is the entry, not the reference to it:** before claiming a decision is
   logged, confirm a matching `### D-NNN` exists in `docs/decisions.md`. See method-note item 7.
   ⚠⚠ **And the same defect ran for 38 days in the `A-` namespace at 71× the scale** — `A-014`,
   `A-016` and `A-017` were cited **71 times in shipped Python** with no entry anywhere, because the
   citation invariant read only `docs/README.md` + `ARCHITECTURE.md` and **never read the code**.
   `D-156` widened it; run the check in `docs/RESERVED.md` before claiming the invariant holds.

2. **Architecture doc stays true.** `ARCHITECTURE.md` (repo root) is the single source of
   truth for system shape. Any PR that changes structure, data flow, dependencies, or
   deployment MUST update `ARCHITECTURE.md` in the same PR. **Bring `ARCHITECTURE.md`
   current before filing any PR** — a stale architecture doc means the PR is incomplete.

3. **This log wins over the original planning docs.** The TDD/UI/DB/test plans in `docs/`
   are original intent; where a `docs/decisions.md` decision diverges, the log is authoritative.

4. **Every claim names how it is known (provenance, D-016).** A written record does not make a
   claim true. Before a number or a status enters any of the five documents, or a PR, name the
   artefact behind it — the raw log line, the query output, the run URL. If you cannot name it,
   you are recording a belief, not a finding. A summary is not knowing: prefer the breakdown to
   the total, and prefer the query whose answer could disqualify you. Four claims were reversed
   across 2026-07-19/21, each true as stated and wrong in what it implied, each caught only by
   returning to the raw artefact.

## Working clone

Do all commits/PRs in `C:\Projects\Project-PharmFoldMDK` (remote:
https://github.com/mdk32366/Project-PharmFoldMDK). The near-identically-named
`C:\Projects\Project PharmFoldMDK` (space, not dash) is a stale non-git folder — do not use it.
