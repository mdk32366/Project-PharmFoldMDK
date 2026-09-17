# PLANNER RULING — 2026-09-16 · `D-168` reuses the existing category; R1–R4 opens the session

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it, so nothing is pinned
> by these lines.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Grounded on:** `origin/main` @ **`1e67954`** (the #331 merge), read by the Planner through a public clone.
**Answers:** `PREWORK-2026-09-17.md` §3.4 — *"Ask the Planner before writing the entry."*

---

## 0. Grounding — one correction to the prework's own header

`PREWORK-2026-09-17.md` says it is grounded on `main` @ `f7d0a9d`. **`main` has moved since:**

| commit | what |
|---|---|
| `f7d0a9d` | PR #330, the E.3 debt-paying merge (the prework's stated base) |
| `1b69b3d` | `CLOSEOUT-2026-09-16` + `PREWORK-2026-09-17` |
| **`1e67954`** | **PR #331 merge — current `main`** |

Not a defect: the prework was written before its own merge. ⚠ **Code re-states the base commit at the top
of this session's first report**, and confirms `RESERVED.md` still reads `D-168` / `F-081` / `A-032`.

---

## 1. §3.4 — RULED: reuse `refused_assembled_incommensurable`. The orders were wrong.

**Planner error 9.** `ORDERS-Code-2026-09-16-feature-coverage.md` §2.2 proposed a new category,
`refused_assembled_structure`, for a refusal the tree has shipped since `D-120`. The Planner proposed a
second name for one thing — `F-049`'s family — in a document whose §2.4.3 orders that categories never be
folded together. **Code found it by reading source. Credited.**

**The ruling:**
1. **`D-168` creates no new refusal category.** It cites `D-120` / `D-109` ruling 7 and reuses
   `refused_assembled_incommensurable`.
2. **§2.2 of the feature-coverage orders is superseded** on this point. The rest of §2.2 stands.
3. **The `structure_kind` tag in the v2 artifact still stands, and is not a refusal.** It records what the
   extractor measured. The refusal is decided at profile time, from the row, by
   `_incommensurable_assembly`.
4. **Tiles-only parents:** the orders proposed `no_protein_level_structure` as a *profile* category. ⚠
   **Superseded too** — `_incommensurable_assembly` already returns true for a tile row. If a distinction
   is still wanted, it belongs in the **extraction** artifact's outcome vocabulary, never as a second
   profile refusal.

### 1.1 ⚠⚠ What this changes about the coverage numbers — read before C1/C4

`census_profile_statuses` tests `_incommensurable_assembly(analysis)` **first, and `continue`s**. The
feature row is never consulted for those rows.

**Consequence:** an assembled parent or tile window shows `refused_assembled_incommensurable` **whether or
not it has features**. So:
- **Extracting features for assembled parents will not change what any page displays.** It is a
  measurement for the comparison, not a coverage fix. `D-168` must say so plainly, or the work will look
  like it failed.
- **The 777 gap is smaller than it looks as a *display* problem.** ⚠ The Planner's file-based CSV joined
  the manifest to the features artifact and **did not model this short-circuit**. The 141 spans over
  1,026 aa are where the two differ.
- **C1 and C4 must therefore report three numbers, not one:** representatives with no feature row, **of
  which** how many already refuse as assembled, and how many would actually gain a rendered profile.
  ⚠ Only the third is a coverage gap. Code states each key.

### 1.2 What `D-168` is actually for, then

Not a category. It is the **commensurability ruling**: may features measured on an assembled chain be
compared with, pooled with, or fitted alongside features from a single-pass fold? The existing category
answers the *display* question; `D-168` answers the *analysis* question, which the v2 comparison raises for
the first time. **Planner recommendation to the owner: extract and store them, tagged; never pool them
into a fit or a support range with single-pass vectors.**

---

## 2. §3.2, §3.3, §3.5 — accepted as measured

- **The instrument is unchanged:** `feature_version()` reads `e67a8cf30c1c`, and `git log` over
  `core/features.py` since `8db7345` is empty. §2.4.1's stop condition does not fire. **v2 is the same
  instrument**, which is what makes the v1-equality calibration meaningful rather than circular.
- **The profile panel reads the `protein_features` table**, and the v1 manifest records
  `wrote_database_rows: false`. **C5 is therefore the load-bearing reading of Phase 1** — it decides
  whether 2,690 extracted rows ever reached the table. ⚠ Code raises C5's prominence accordingly.
- **Seven documents cite v1 by sha256.** v2 is additive; no sealed analysis is re-pointed without a ruling.

---

## 3. Order of work — the prework's §4 stands, with two amendments

1. **R1–R4 first**, one read-only tunnel. Nothing else touches the database before it.
2. **Phase 1 C1–C5 in the same tunnel**, with **C1/C4 split by §1.1's three keys** and **C5 raised**.
3. `scripts/feature_coverage_report.py`, tests first. ⚠ It must model the `_incommensurable_assembly`
   short-circuit, or it will reproduce the Planner's CSV error. Its output will then **not** equal §3.1's
   table exactly; that difference is the correction, and it is reported, not reconciled.
4. **`D-168`** written per §1.2. Extraction may proceed; ingest may not.
5. Phase 2, then Phase 3.

## 4. Owner decisions still open

| item | recommendation |
|---|---|
| Population (orders §2.1) | P1 in · P2 if C3 shows a gap · P3 as a ≤100 instrument sample · P4 out |
| `D-168` commensurability (§1.2) | store tagged, never pool into a fit |
| Rotate `fly-user` + `WORKER_AUTH_TOKEN`, then clear `.env` | **before the tunnel if possible** — the prework's §5 already tells Code to check `.env` first |
| The paper's §4.3 loss statement (now zero rows) | owner's wording |
| Slice 4 | stays blocked on the Run-2 identity |

**Planner error count, carried: 9.**
