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
   `docs/README.md` **before** the work it describes is finished.* If the reasoning isn't
   logged yet, log it first (append-at-top `D-NNN` entry with a deep-learning
   justification), then build.

2. **Architecture doc stays true.** `ARCHITECTURE.md` (repo root) is the single source of
   truth for system shape. Any PR that changes structure, data flow, dependencies, or
   deployment MUST update `ARCHITECTURE.md` in the same PR. **Bring `ARCHITECTURE.md`
   current before filing any PR** — a stale architecture doc means the PR is incomplete.

3. **This log wins over the original planning docs.** The TDD/UI/DB/test plans in `docs/`
   are original intent; where a `docs/README.md` decision diverges, the log is authoritative.

## Working clone

Do all commits/PRs in `C:\Projects\Project-PharmFoldMDK` (remote:
https://github.com/mdk32366/Project-PharmFoldMDK). The near-identically-named
`C:\Projects\Project PharmFoldMDK` (space, not dash) is a stale non-git folder — do not use it.
