# REPORT — Code → Planner — 2026-09-15 · Amendment 9 actioned: branch re-scan, the E.2 walk named from source, and what the census page actually counts

**Governs:** `ORDERS-Code-2026-09-16-reattach-and-collapse (9).md`, Amendment 9.

**Where this file lives:** `C:\Users\mdk32\Downloads\`, for the owner to forward. A4.8 asks for it on the
branch too. That commit waits on the owner: its pre-commit scan will match the words `password` and `token`
in this report's own prose.

**Session:** 2026-09-15, America/Los_Angeles (PDT).

**Production access:** no database and no tunnel. The reads are:
- git blobs;
- source files;
- anonymous GETs on the public read API (`https://pharmfoldmdk.fly.dev/api/...`).

---

## 1. A9.5 — owed items, closed

| item | state | how known |
|---|---|---|
| tunnel closed; `url`, `PYTHONUTF8` removed | **done** | owner: *"Window B: Removed. Window A: Tunnel Closed."* Code at 2026-09-15T22:15:33Z: 0 listeners on 16300–16499; pid 22464 gone; only the Fly agent |
| `e5-tunnel-closed.txt` | **written, committed** in `a57ea4d` | branch `d167-phase-e-evidence` |
| credential re-scan over **everything on the branch** vs `main` (`d892c96`) | **done**, §2 | committed blobs via `git show HEAD:<path>` |
| was `a57ea4d` committed before its scan? | **No.** Its 5 files were scanned **before** commit with the full pattern set and the literal password: 0 hits. The first attempt, which bundled the report, **stopped** on the report's prose hit, and nothing was committed until it was split. | console of the commit step |
| the Phase E read report | **committed by the owner's ruling** (§2 note) | **`62e9899`** on `d167-phase-e-evidence` (pushed); literal password re-checked absent, 0 credentialed URLs |

---

## 2. Branch re-scan (A9.5)

- **Scope:** the 7 files changed on `d167-phase-e-evidence` vs `main` @ `d892c96`, read from the **committed**
  blobs, plus the then-untracked report.
- **Patterns:** `password`, `passwd`, `postgres(ql)://`, `user:pass@`, `FlyV1`, `secret`, `token`, **and
  the literal password.** The password was read in-process from `.env` and never printed; its length is
  32, so the literal probe could hit.

| file | result |
|---|---|
| `data/control/d167/phase_d/01a-witness-attempt1-placeholder-url.txt` | `password` ×2: the psycopg line with placeholder user `<user>` (owner-ruled A8.4) |
| `data/control/d167/phase_d/README.md` | `password` ×3: **prose**, the A8.4 line describing the hit and the scan |
| `data/control/d167/phase_e/e2-tunnel-open.txt` | clean |
| `data/control/d167/phase_e/e3-read-console.txt` | clean |
| `data/control/d167/phase_e/e4-identity-gap-analysis.txt` | clean |
| `data/control/d167/phase_e/e5-tunnel-closed.txt` | clean |
| `data/control/d167/phase_e_read.json` | clean |
| `docs/REPORT-Code-2026-09-15-phase-E-read.md` | `password` ×3, `token` ×1: prose (the scans; `WORKER_AUTH_TOKEN` named as a rotation owed) |

**Literal password: 0 hits in every file. Credentialed URLs: 0.**

**The report's hits** were shown to the owner line by line (lines 25, 26, 136, 140). The owner ruled
**commit**; the commit message records the ruling.

**⚠ Deviation, recorded (Code):**
- `2085cad` added the A8.4 README line **without scanning the README first**. Only `01a` was scanned before
  that commit.
- The line holds the word `password` ×3 as prose, and today's re-scan confirms no literal password on the
  branch.
- Rule taken: every file in a commit is scanned before that commit, including a file Code wrote in the
  same step.

---

## 3. A9.4 — what the census page counts, named from the route's source

**A9.4 says:** "E.2's census walk item reads '3,648 rows' if the live census page shows a row count at all.
If it shows distinct proteins or identities, it states that key."

**Measured from source: the census page counts census PROTEINS, one per accession, not run-1 rows.**

- **`app/reads.py::list_census`** (the list behind the table and the summary):
  - **population:** `ProteinAnalysis.cohort_tranche > COHORT_TRANCHE`, so the cohort's tranche-0 rows are
    excluded;
  - **representatives:** grouped by accession, one representative per accession via
    `choose_census_representative`;
  - **never-folded proteins:** appended from the manifest.
- **`choose_census_representative`** (`app/reads.py:947`):
  - never a tile as the protein; the spare tiles **3693/3695/3696 are named as never winning**;
  - prefers an assembled parent, then a tiles-only parent;
  - otherwise the **lowest id** among non-tile folded rows (`min(..., key=lambda r: r.id)`).
- **`census_summary`** (`app/reads.py:1548`):
  - `manifest_rows` is keyed *"every census protein row after D-118 identity (one per accession), folded or
    not"*;
  - `folded` is keyed *"census proteins with a parent or single-pass structure and a mean pLDDT (tile
    windows are not proteins)"*.
- **Surfaces:**

  | component | shows | key |
  |---|---|---|
  | `CensusTable.jsx:379–380, 458–460` | *"N folded, plus M listed but never folded"* | `folded !== false` over the list rows |
  | `CensusPopulationStrip.jsx:49–54` (on `/coverage`) | `manifest_rows` *"proteins in the census, folded or not"* and `folded` | `/api/census/summary` |

  The collapsed "What was measured" block in `CensusView.jsx` is **static**, counted off
  `census_manifest.v7.csv` (`censusSummary.js`).

⇒ **The 3,648 row-keyed reading is not on the census page.** The page's keys are accession-level, and they
are **not moved by Phase D**:
- the collapse removed spare tile rows, which never represent a protein;
- the re-attached rows lose the lowest-id choice to each accession's existing Run-1 row.

### 3.1 Live measurement (anonymous public API, after Phase D and Phase E)

| request | result |
|---|---|
| `GET /api/census/summary` | `manifest_rows` **3,467**, `folded` **3,463**; kinds assembled 45 · single-pass 3,418 · mucin 3 · none 1 |
| `GET /api/census` | **3,467** rows; the `CensusTable` rule gives **3,463 folded, 4 never folded** |
| list representatives among re-attached analyses 4870–4906 | **none** |
| list representatives among dropped 3693/3695/3696 | **none** |
| `Q2T9K0` / `Q9UBD6` / `Q96CP7` / `Q15391` list representative | **336 / 973 / 597 / 522**, all Run-1 rows |

**The before-value, same day and pre-sitting:** `core/db_identity.py` (`D-159`) records *"the census stood at
3,467 manifest rows / 3,463 folded"*. **Unchanged.**

### 3.2 How a census card resolves (the walk's URLs depend on it)

- **UI:** `ui/src/App.jsx:20–22` `/census/:id` → `CensusProteinView` → `getCensusDetail(id)` →
  `GET /api/census/{id}` (`CensusProteinView.jsx:89`).
- **API** (`app/read_routes.py:396–455`):
  - a **numeric** id resolves through `canonical_census_analysis_id`, and a tile id is 404 *"a tile window,
    not a census protein"*;
  - an **accession** resolves to the representative row.

| request | served id | fold | `mean_plddt` |
|---|---|---|---|
| `/api/census/4870` | 4870 | **Run 2, re-attached** (`folded_at 2026-09-13T15:24:37Z`) | 56.72 |
| `/api/census/Q2T9K0` | **336** | **Run 1** (`folded_at 2026-08-16T14:20:50Z`) | 56.72 |
| `/api/census/4906` | 4906 | Run 2 | 56.28 |
| `/api/census/Q9UBD6` | 973 | Run 1 | 56.28 |
| `/api/census/4875` | 4875 | Run 2 | 75.05 |
| `/api/census/Q96CP7` | 597 | Run 1 | 75.05 |
| `/api/census/4869` | 4869 | control job 4868, Run 2 | 58.37 |

⚠ **Observation, not a claim:** for these three accessions the Run-1 and Run-2 folds give **identical
`mean_plddt` to two decimals**. That is consistent with the fold path's determinism (`F-077`'s three
byte-identical tile pairs), but n = 3, and neither bytes nor per-residue arrays were compared. Not claimed.

---

## 4. The E.2 walk, as named for the owner

**Order and pass criteria**, from the orders' E.2 with A9.4's key correction:

1. **Control first:** `https://pharmfoldmdk.fly.dev/census/4869` (job 4868, `Q15391`).
   - Structure renders; pLDDT **58.37**; provenance panel populated.
   - ⚠ If the control fails to render, stop: that is the pre-existing 3Dmol defect, and the walk cannot
     speak for the 37.
2. **Three of the 37.** Each renders like the control, and the provenance panel shows a **full** record
   (model, revision, dtype, chunk, ECD bounds, fold time), not five fields:
   - `https://pharmfoldmdk.fly.dev/census/4870`: job 4869, the first, `Q2T9K0`, pLDDT **56.72**
   - `https://pharmfoldmdk.fly.dev/census/4906`: job 4905, the last, `Q9UBD6`, pLDDT **56.28**
   - `https://pharmfoldmdk.fly.dev/census/4875`: job 4874, the highest pLDDT **75.05**, `Q96CP7`
3. **Census page:** `https://pharmfoldmdk.fly.dev/census`.
   - The table line reads **"3,463 folded, plus 4 listed but never folded"**.
   - Key: census proteins, one per accession. **Not** "3,648 rows" (§3).
4. **The owner states pass/fail per item.** A fail is recorded, not re-walked until it passes.

**Confirmed for the list:**
- **Highest pLDDT**, from the committed capture blob: job **4874**, 75.05. Mean 55.21, min 46.86 (A8.3/E.2).
- **By-accession caution** given to the owner: `/census/Q2T9K0` shows the **Run-1** fold (id 336), not the
  re-attached row. That is correct behaviour; the walk uses analysis ids.

---

## 5. For the close-out

1. **A shared defect class** (A9.3): a truncated read presented as a count.
   - Planner errors 6 and 7.
   - Code's `LIMIT 50` diagnostic, printed as *"…: 50"*.
   - Named once, as a class.
2. **Code deviation:** the README line in `2085cad` was committed without a pre-commit scan of that file (§2).
3. **Census-page keys** (§3): accession-level and stable across Phase D. Any future "census count" in the
   log states its key — row-keyed run-1 (3,648), identity-keyed (3,576), or census proteins (3,467 /
   3,463 folded).
4. **Run 1 / Run 2 `mean_plddt` equality** on three rows (§3.2): an observation, eligible for a determinism
   check, not asserted.

---

## 6. Next

- **Owner:** the E.2 walk (§4).
- **Code, after the walk (E.3, the debt-paying commit):**
  - delete `tests/test_f078_owed_restore.py`;
  - `OWED_RESTORE` becomes PAID in `task4_slice3.py` / `task4_slice4.py`, keeping **DO NOT RE-FOLD** and the
    `--restore` prohibition; the operator copy is for owner approval;
  - `F-078` amendment 3 (census 3,651 → 3,648 row-keyed by the collapse, nothing scientific lost);
  - `F-077` collapse note; `D-166` note that `0014` is applied;
  - `.gitattributes` `data/control/d167/** -text` with its `git check-attr` test (A8.5).
- **Code, then:** `CLOSEOUT-2026-09-16.md`, carrying A9.2's R1–R4 pre-registration **verbatim** as the next
  session's first item, above slice 4.
- **Unchanged, owner's timing:** rotate `fly-user` and `WORKER_AUTH_TOKEN`, then drop `DATABASE_URL` from
  `.env` (A8.6).
