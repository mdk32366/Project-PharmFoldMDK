# Housekeeping record — 2026-08-01 — eight untracked files removed from `docs/`

> **Why this file exists.** The files below were **never tracked by git**, so deleting them left
> **no commit, no diff, and no revert path** in the repository. There is no artifact to review and
> `git log` will never show this happened. The record therefore has to be prose, written down
> deliberately, or the removal is invisible to every future reader. Owner ruling, 2026-08-01:
> *"record the fact in prose since git can't."*

---

## 1. Six documents belonging to a different project (JARVIS)

They arrived in `docs/` by download, not by authorship. Each was confirmed foreign **by reading it**,
not by its filename — the discipline the same session's near-miss (§3) exists to enforce.

| File | Foreign refs | PharmFoldMDK refs |
|---|---|---|
| `BUILD-ORDER-infra-report-legibility.md` | 4 | 1 — *see note* |
| `BUILD-ORDER-location-pull-silence-diagnostic (2).md` | 8 | 0 |
| `BUILD-ORDER-tdd2-steps-1-3-planning-gate.md` | 8 | 0 |
| `COMMIT-INSTRUCTION.md` | 2 | 0 |
| `TDD-location-freshness-alert (1).md` | 15 | 0 |
| `design-note-answering-late (1).md` | 3 | 0 |

Foreign markers counted: `backend/`, `handlers/`, `0026_github_write_log`, `Registry.run_tool`,
`Project-Jarvis`, `planning_session`, `autoremote`, `Tasker` — **none of which exists in this
repository.** `BUILD-ORDER-tdd2-steps-1-3-planning-gate.md` instructs a migration off head
`0026_github_write_log`; this repo's head is `0007_membrane_proximal_sasa`.

**⚠ The one file with a PharmFoldMDK reference, checked rather than assumed.**
`BUILD-ORDER-infra-report-legibility.md` mentions `pharmfoldmdk` nine times — but only as *a Fly app
observed from JARVIS's fleet report* (an app live at `pharmfoldmdk.fly.dev` that JARVIS's
`_fleet_spend` handler failed to enumerate). Its subject is `handlers/infra.py`, a file this repo does
not contain. **Foreign, and deleted** — but it was the one that needed reading rather than counting.

**⚠ `COMMIT-INSTRUCTION.md` was an instruction to commit three of these into `docs/` and push
straight to `main`.** Executed here it would have placed another project's design records in this
repository's history — where, unlike these deletions, they *would* have been permanent. It was not
executed. Its "docs-only commits to `main` are allowed" clause is JARVIS's rule, not this project's:
`main` here is protected with `enforce_admins: true` and takes no direct pushes (D-008).

## 2. One redundant duplicate — collapsed, not deleted

`D-072-last-three-fold-plan (1).md` and `(2).md` were **byte-identical** (`md5 f3f4ccdf`), as are all
four copies still sitting in the owner's Downloads. **Diffed rather than assumed** — the suffix was
not taken as evidence of staleness, precisely because the same session found a `(2)`-suffixed baton
doc that *was* the newer content (PR #110).

This document is **not clutter**: it is a live staged artifact that `MANIFEST-2026-08-01-handoff.md`
references by its unsuffixed name. Deleting both copies would have removed the staged plan from the
repo. One copy was therefore **kept as `D-072-last-three-fold-plan.md`** so the MANIFEST reference
resolves, and the redundant copy deleted.

**⚠ Open TODO carried forward:** this document is **misnumbered**. D-072 is taken by the miniature
demo notebook (`d46aa1a`). It renumbers to **D-076** — live TODO for the next pre-work, not done here.

## 3. The near-miss this record belongs beside

The same sweep's audit flagged **`docs/README.md`** as "differing" from a newer same-basename copy —
**605,752 bytes vs 15,222**. The candidate was an unrelated project's README (*"Entity Unification
Agent"*, dated May 25). `docs/README.md` is this project's **605 KB design decision log**.

A mechanical *place-the-newer-copy* would have destroyed the entire decision history because two
files shared a basename. It was caught by reading the file instead of trusting the match.

> **The rule this proves: a file's name is not its identity. Any operation that acts on name alone —
> move, overwrite, delete, sync — is one collision away from catastrophe.**

This session produced **three** identity-confusion failures of the same family: orders that never
landed because they were sought by name in the wrong place; a set of foreign docs indistinguishable
from local ones by filename; and a README that would have clobbered the log. **Verify identity by
content before any destructive or overwriting operation.** That is the durable lesson, and it is the
reason this deletion is written down rather than merely done.
