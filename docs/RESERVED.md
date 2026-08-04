# RESERVED — announced-but-unwritten entry numbers

> **What this file is for.** The citation invariant is: *every cited `D-NNN` / `F-NNN` / `S-NNN` /
> `DEP-NNN` in `docs/README.md` and `ARCHITECTURE.md` resolves to a real `### ` entry.* It was
> **RESTORED on 2026-08-03**, not inherited — D-062 had accumulated **thirteen** citations with no
> entry, and F-009 was cited by shipped UI and by `ARCHITECTURE.md` while existing only as a staged
> document. See `docs/README.md` method-note item 7.
>
> **The problem this file solves.** Some references point *forward*, at entries deliberately not
> written yet. A forward reference that announces its own absence is **not** the D-062 defect —
> D-062's harm was that citations treated a missing entry as **settled authority**, with nothing in
> the text suggesting it was missing. **But it is indistinguishable from the defect to a checker.**
>
> So the distinction cannot live as prose scattered through a method note: that works only while the
> set is small enough to remember. **This file is the whitelist. The checker whitelists this file
> and nothing else.**
>
> ## ⚠ THE RULE
>
> **An unresolved reference that is not listed below is a finding, immediately.** Not a cleanup item,
> not a note for later — the same class as D-062, found early.
>
> Reserving a number is **not** authorisation to do the work behind it. It reserves the integer and
> records what would unblock it. A reservation that is never written is retired here, in the open,
> with a reason.

---

## How to run the check

Named, not built — deliberately, per **D-074 decision 3** (*do not answer a finding with a framework
that becomes a second thing to drift*). It is one command, and it found two holes the first time it
was run:

```bash
python - <<'PY'
import re, pathlib
log  = pathlib.Path('docs/README.md').read_text(encoding='utf-8')
arch = pathlib.Path('ARCHITECTURE.md').read_text(encoding='utf-8')
res  = pathlib.Path('docs/RESERVED.md').read_text(encoding='utf-8')

defined  = set(re.findall(r'^### ([DFS]-\d+|DEP-\d+|A-\d+)', log, re.M))
reserved = set(re.findall(r'^\| \*\*([DFA]-\d+)\*\*', res, re.M))
cited    = set(re.findall(r'\b(?:D|F|S|DEP|A)-\d{3}\b', log + arch))

missing = sorted(cited - defined - reserved)
print('UNRESOLVED AND UNRESERVED:', missing or 'none — invariant holds')
PY
```

**Read the output, not the exit code.** An empty list is the only passing result.

---

## Reserved numbers

| Number | What it will be | Reserved by / when | What unblocks it |
|---|---|---|---|
| **D-010** | *Nothing.* A historical skip — the sequence runs D-001…D-009 then D-011. | Pre-2026-07-19 | **Never.** Not renumbered because commit `c07b95b` already names D-011. Permanent, documented in `docs/README.md`. |
| **D-078** | The F-008 precision A/B pre-registration — the controlled re-fold at the opposite precision | D-077 dec 7, 2026-08-04 | A **raised local ceiling**. If D-077's bisection lifts the ceiling above 440, rental/fp16 targets become locally foldable at int8, creating the first overlap in a partition F-008 recorded as having none. ⚠ **Its outcome can move F-004**, so it is written before any such fold runs. |
| **D-080** | *A revert proof operates on committed state or on a copy — never on a working tree holding uncommitted work.* | Amendment §3, 2026-08-04 | Nothing — writable now. Prompted by assumption-register item 15, which is at **n=2** (D-075's process note is the first occurrence). |
| **F-011** | The surfaceome negative class | Planner, 2026-08-04 | Nothing — the staged finding is complete and mergeable. ⚠ **Staged file not yet received by Code** (see status note below). |
| **F-012** | Task 1 — the chunk-invariance verdict | D-077 dec 2 / amendment §1 | **The GPU run.** Three Trop-2 folds at int8, chunk 64/32/16, read against decision 2's frozen two-row table. The comparator is built and green; no fold has run. |
| **F-013** | Task 3 Arm A — the measured local ceiling | D-077 dec 3-4 / amendment §1 | **The GPU run.** Bisection in (440, 630) at int8/chunk 64, k=4, step 8. May legitimately return `unstable` at every length. |
| **F-014** | *Documenting a duplication is not managing it* — the tenth instance of the two-paths-to-one-quantity class, and the first where the drift was **written down and the writing-down substituted for the fix** | Amendment §7, 2026-08-04 | Nothing — writable now, but **held until `d077-local-fold-envelope` merges**, because it describes code that branch changes. |
| **A-014** | An assumption-register entry cited by F-011's closing line | Planner, 2026-08-04 | **KEEL-4 landing.** `A-` numbers live in the assumption register, not in `docs/README.md`. ⚠ **KEEL-4 not yet received by Code.** |

---

## ⚠ Status note, recorded rather than assumed (D-016)

**As of 2026-08-04, four documents this register depends on have NOT been received in the working
clone**, and their content is known to Code only through `AMENDMENT-2026-08-04-code-feedback.md`,
which describes them:

- `KEEL-4-The-Assumption-Register-v1.md` — defines `A-` numbering and holds items 15/16/17
- `F-011-surfaceome-negative-class.md` — the staged finding claiming F-011
- `PAPERS.md` — where P-001's open item lands
- `ORDERS-Code-2026-08-04-surfaceome-spans.md` — the base order the amendment patches

**The rows above for F-011 and A-014 are therefore sourced from a description of a document, not from
the document.** That is precisely the pointer-not-proof shape (method-note item 7), and it is
recorded here rather than smoothed over: **these two rows must be re-verified against the staged
files when they arrive**, and corrected here if they disagree.

The amendment's own §1 warns that neither claimant on F-011 is merged, so nothing is broken yet.
This register is what keeps that true.

---

## Retired reservations

*(none yet — when a reserved number is abandoned rather than written, it moves here with the reason,
so a future reader can tell "abandoned" from "forgotten".)*
