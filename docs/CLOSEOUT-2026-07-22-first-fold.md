# Session Close-Out — 2026-07-22 → -23 (First Fold Through Production)

**Opened with:** `docs/PREWORK-first-fold.md`
**The milestone:** the entire pipeline ran end to end in production for the first time. Real
ESMFold inference, through the deployed transport, persisted durably. The neural network did
load-bearing work through the production path.

---

## 1. What shipped, and what ran

**Merged this session:** `worker/main.py` (#49, the worker entry point), the deployment arc
(#48, Dockerfile + fly.toml + deploy job), `core/enqueue` CLI (#50, the prod invocation entry
point), and D-032 (Postgres promoted to a required check, #46).

**Provisioned and proven on Fly:**
- `pharmfoldmdk` app deployed to `sjc`, transport API live and answering (404 JSON on `/`,
  401 on an unauthenticated `/jobs/claim` — auth working).
- MPG cluster `sentinel-holy-rain-4562` attached; schema migrated to head **supervised**
  (DEP-005 phase 1), `analysis_embeddings (embedding vector(384))` with a functional HNSW index.
- Secrets (`DATABASE_URL`, `WORKER_AUTH_TOKEN`) and the `artifacts` volume in place.

**The first fold — NECTIN4 (`Q96NY8`), the target of a marketed ADC (enfortumab vedotin):**
- Claimed over HTTP at `00:02:54`, completed at `00:03:44` — **50 s wall-clock** (weights
  pre-loaded), local tier, int8 (S-003 recipe, confirmed by the bitsandbytes 8-bit path
  engaging).
- **mean pLDDT 77.26** — a confident, real structure, not garbage.
- Artifacts durable on the Volume: `structure.pdb` (194 KB), `plddt.json`, `pae.json.gz`
  (805 KB), `provenance.json`. Job `complete`, analysis row's post-fold columns populated
  (`pdb_path`, `mean_plddt`, `pae_json_path`) — the D-031 write-semantics working on prod.

The full sequence, from the Fly logs: `claim → 200` · `artifacts → 204` · `complete → 204`,
in that order — D-031 §3's done-ordering (complete only after artifacts persist) holding in
production.

---

## 2. Two provisional numbers, now measured

Both were labelled provisional pending this fold. Both are now grounded — and one is worse
than estimated, which matters.

| Number | Was | Measured | Consequence |
|---|---|---|---|
| Small-fold wall-clock | — | **50 s** (318 aa, local, weights warm) | The small end of D-030's lease; comfortable |
| PAE gzip ratio | est. **5–10×** (D-031) | **~2.2×** (805 KB gz vs ~1.8 MB raw) | **Below estimate — the large-rental PAE upload is a *bigger* lease concern, not smaller** |

**The honest reading, for the D-030/D-031 amendment:** this fold retires the *small local*
end. It makes the *large rental* end look **harder**. At 2.2× compression, a 1600-residue
rental target's PAE is ~45+ MB compressed over a residential uplink — squarely the lease-budget
risk D-030 flagged, now with a real ratio behind it. **The heartbeat D-030 named as the
structural fix looks more necessary, not less.** The large-rental fold (still an owner action)
is where the lease actually gets tested.

---

## 3. The pattern, held to the very end

The day's recurring finding — *a claim read as fact until the artifact corrects it* — did not
stop at the pipeline. Tonight's instances:

- **First-fold target went through two wrong candidates.** Trop-2 (the Planner's suggestion —
  turned out to be the S-003 spike target and a Group C probe, **not** in the 82) and `P16109`
  (an unverified accession the Planner typed as an example). The CSV settled it: NECTIN4.
- **The `postgres`-uses-stock-`postgres:16` claim** carried in the hazard doc and D-032 was
  wrong — D-019 switched it to a pgvector image. Surfaced writing DEP-005.
- **The `CREATE EXTENSION` "blocker" was database-scoped** — refused on `fly-db`, unnecessary
  on `pharmfoldmdk` where pgvector was pre-installed. Checking the wrong database produced a
  false blocker.
- **The `DATABASE_URL` driver scheme** — `fly mpg attach` writes bare `postgresql://`, which
  resolves to the uninstalled psycopg2. Caught supervised during the migration, fixed in
  `app/config.py` (#48).
- **The first enqueue silently wrote nothing** — the tunnel had dropped and `DATABASE_URL`
  was empty; the enqueue failed without landing a row, which the `204`-only worker logs made
  visible. Re-run with a verified connection: `created=1`.

Several of these were the Planner's own claims corrected by the tree or the live system. That
is the discipline working, not failing — and it is worth carrying into the UI arc, where the
temptation to build against an imagined data shape is strongest.

---

## 4. Carried hazards — status

- **`worker/requirements.txt` is incomplete** (D-018's accepted cost, landed). The GPU install
  was discovered piecemeal tonight — numpy and transformers were both missing and installed by
  hand. A `worker/requirements-frozen.txt` was captured from the working install
  (`accelerate==1.14.0` et al.) but is **untracked and needs re-saving as UTF-8**; it is its
  own small D-018 amendment PR, not folded into anything yet.
- **The tunnel drops silently**, and a dropped tunnel makes a prod write fail without an
  obvious error (§3). For batch work tonight, verify the connection before and after.
- **pgvector seam 2** is better covered than the docs said (pgvector CI image, D-019); its
  remaining prod exposure was **retired** by DEP-005 phase 1 — the vector column, extension,
  and HNSW index all built on the real cluster. `docs/HAZARD-search-path-seams.md` and D-032
  need the stock-image correction.
- **D-030 lease / heartbeat** — §2. The provisional 3600 s is safe for small folds; the
  heartbeat is the real fix and is now better motivated by the measured PAE ratio.

---

## 5. Owner actions, parked

- **The frozen worker requirements** — re-save UTF-8, make it a D-018 amendment PR so
  `worker/requirements.txt` finally pins the full stack.
- **The large-rental first fold** — the measurement that actually tests D-030's lease. Needs
  the A6000.
- **`docs/HAZARD-search-path-seams.md` + D-032** — correct the stock-image claim (§4).

---

## 6. Start-here tomorrow

See `docs/PREWORK-ui-arc.md`. In short: **step 2 — the React UI (D-033)**, now that a real
`protein_analyses` row exists to build against. The structure viewer, provenance panel, and
coverage-line component are all buildable against tonight's folds. The ranking-with-disagreements
view (the demo's centrepiece) still waits for the scorer, which waits for the full cohort's
features — step 3.

**Tonight, before sleep (optional, in progress):** fold the 40 local-tier targets locally —
free, own hardware, no rental. That gives the UI arc 40 real structures to render instead of
one. See the run guide.

---

## 7. Definition of done — met

- First fold through the production path: **done and verified** (job complete, mean pLDDT 77.26,
  artifacts durable).
- Two provisional numbers measured (§2); amendment to D-030/D-031 named for Code.
- Deployment fully live; DEP-005 phase 1 complete.
- Close-out written after the milestone, not before.
