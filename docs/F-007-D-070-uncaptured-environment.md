# F-007 + D-070 + orders — the uncaptured environment, said from what is recorded

> **Sequence: the precedence realignment and its re-walk come FIRST.** The freeze holds on that.
> This rides after it, same day.
> **Scope:** `ui/src/components/Provenance.jsx` (+ tests), `docs/`. **UI-only.**
> **NOT in this PR:** `app/`, routes, `worker/`, migrations, any data mutation, any re-fold.

---

## PART 1 — the entries

### F-007 — The pinned worker environment and the measured one disagree on torch

- **Date:** 2026-07-29
- **Type:** A finding. Nothing ruled.
- **How known (D-016):** `worker/requirements.txt` pins **`torch==2.11.0+cu128`**, described in its
  own header as *"the versions MEASURED in the S-003 spike, on the RTX PRO 2000 (Blackwell
  sm_120)."* The captured environment on `protein_analyses` id=75 (folded 2026-07-25, rental tier)
  records **`torch_version: 2.8.0+cu128`**. `transformers` agrees at **5.14.1**; **torch does not.**

**The rental pod ran a different torch build than the pinned worker manifest.** Not necessarily a
defect — D-018 accepted this exact exposure in writing: *"these dependencies are NOT covered by the
root lock-file guarantee… a breaking release here reddens no gate and is discovered at fold time,
on a GPU host — that is the accepted cost of keeping CUDA out of CI."* **This is that accepted cost,
observed rather than anticipated.**

#### Finding — the manifest is not a reliable proxy for what ran

**On the single fold where both a manifest and a measurement exist, they disagree.** Any method that
reconstructs a fold's environment from the pinned manifest therefore has a **demonstrated failure
rate of one for one on the only case that can test it.**

**This is D-045 paying for itself.** The entry was written on the reasoning that *"same weights,
different kernels"* is a real source of variation. **It was, and nothing else would have found it.**

**⚠ The bound, stated:** the pin was measured on the **local** box; the disagreement is on the
**rental** tier. **No local fold post-dates D-045**, so the local path has no measurement and this
finding says nothing about it either way. **Unknown, not fine.**

---

### D-070 — An uncaptured environment is explained from what IS recorded, and never populated from inference

- **Date:** 2026-07-29
- **Status:** Proposed → Accepted on merge.
- **Relates:** D-045 (the capture), D-048 (the two-population panel), D-016 (name how it is known),
  D-050 (derived, never duplicated), DEP-001 (`worker/` is not in the serving image), F-007.

**Context.** 76 of 80 folds predate D-045 and show four fields as *not captured*. The owner knows
which machine ran them. **The system records `tier` and `folded_at` and does not record the
environment.** Those are different states of knowledge and the panel currently renders only the
second.

#### Decision (1) — render what IS recorded, in a visually distinct block

For a fold with no captured environment, the panel additionally renders, **derived**:

- **`tier`** — which machine class ran it (local GPU box / rented A6000).
- **`folded_at`** — already rendered.
- A pointer to the pinned worker manifest **by name**, as the place the intended environment is
  recorded.

**This is strictly more informative than "not captured" and asserts nothing that was not measured.**

#### Decision (2) — ⚠ inferred values NEVER enter the captured fields

`torch_version`, `transformers_version`, `device_name` and `cuda_version` render **only** from the
captured record. **An inferred value in a captured field is indistinguishable from a measured one**,
and **F-007 proves such an inference would have been wrong at least once.**

**The block is visually and textually separate**, and says what it is: *what we can say from the
record*, not *what ran*.

#### Decision (3) — ⚠ the manifest's CONTENTS are not duplicated into the serving tier

The obvious next step — show the pinned torch version — requires the manifest in the serving image.
**`worker/` is excluded by DEP-001**, so the only routes are a constant typed into the UI or a copy
of the file into `data/`. **Both create a second source of truth for a value that already has one**,
and it would drift silently the moment the pin changes.

**Ruled: name the manifest, never render its contents.** A reader who wants the version reads the
repo, where it is authoritative.

#### Decision (4) — no backfill, no re-fold

**No inferred value is written to any record.** The block is computed at render time from data
already served, so **there is nothing stored to become stale or to be mistaken for measurement.**

**⚠ Re-folding to populate the fields is refused, and not on cost grounds:** the six features,
F-004's fit, F-005's ablations and F-006's distribution were all computed from **these** folds. New
folds would produce new structures and new features, and **the reported result would no longer
correspond to the data behind it.**

- **Deep-learning justification.** Provenance is the whole basis of the claim that *"we ran this
  ourselves"* is checkable rather than asserted (D-051, MethodNote). **A panel that mixes measured
  and inferred values destroys exactly the property it exists to provide** — and F-007 shows the
  inference would have been wrong on the one occasion it could be checked.

- **Consequences / test surface:**
  - The block renders **only** when the captured environment is absent — asserted both ways.
  - **The four captured fields still render `not captured`** when uncaptured. **They are never
    populated by the new block** — asserted.
  - `tier` is **derived** from the payload; **no manifest content, no version string, no device
    model appears in any component** — Constraint-A extended.
  - A captured fold renders **no** inference block.
  - Readability delta reported.

---

## PART 2 — orders

**Order of work:** land F-007, then D-070 · tests red first (both branches: captured and uncaptured)
· `Provenance.jsx` · gate · owner merge.

**⚠ Four things that will bite:**

1. **Do not populate the four fields.** Decision 2 is the entry's whole point.
2. **Do not import, copy or type the manifest's contents.** Decision 3.
3. **Do not write anything to the database.** Render-time only.
4. **Do not re-fold anything.** Decision 4.

**Owner copy call — one, draft and flag:** the wording of the inference block. It must make the
distinction legible to a non-expert without sounding defensive. Proposed:

> **What we can say:** this fold ran on the **{tier}** tier on **{folded_at}**. The software
> environment for that tier is pinned in the repository's worker manifest, but it was **not recorded
> per-fold** — capture began later (D-045). **This is what the record holds, not a reconstruction.**
