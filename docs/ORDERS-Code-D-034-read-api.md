# Orders for Code — D-034, the read API

**Session:** 2026-07-23, UI arc step 2. **Planner:** Claude. **Builder:** Code.
**Entry:** `D-034` (accepted, in this PR). **Tree at issue:** `0bc9258`.

Build the read API that D-033's React UI will consume. **Tests first — no code before the
tests exist and fail for the right reason.** Nothing deploys to Fly until the required checks
are green (D-008/D-025).

---

## 0. Land the entry first (CLAUDE.md rule 1)

`docs/README.md` — prepend the `D-034` entry (supplied separately) at the top of the log.
**The log leads the code.** Also in this same PR (rule 2 — a stale architecture doc means the
PR is incomplete):

- **`ARCHITECTURE.md`** — add the read routes to the component table and the serving-tier
  description. The serving tier is no longer "the four worker routes"; it is those plus a
  public read surface.
- **`docs/RUNGUIDE-startup-and-local-batch.md`** — correct **40 → 42**. `--bucket local`
  filters on *tier*; tier is orthogonal to disposition (D-024 iv), so it enqueues 40 `ranked`
  **plus 2 `held_out`** local rows. Verified: `Counter({('ranked','local','sliced_ecd'): 40,
  ('held_out','local','whole'): 2})`.

---

## 1. What to build

Four routes, all `GET`, all under `/api`, all unauthenticated (D-034 decision 4).

| Route | Returns |
|---|---|
| `GET /api/analyses` | light list — one object per row |
| `GET /api/analyses/{id}` | full record incl. `sequence` + `fold_provenance` |
| `GET /api/analyses/{id}/structure` | the PDB file, `text/plain`, streamed |
| `GET /api/analyses/{id}/plddt` | the per-residue pLDDT array |

**Light-list fields, exactly:** `id`, `accession` (from `input_value`), `label`, `gene`,
`mean_plddt`, `disposition`, `held_out`, `tier`, `tier_reason`, `boundary_method`,
`fold_length`, `full_length`.
**Excluded from the list and asserted absent:** `sequence`, `fold_provenance`.

Suggested placement: `app/read_routes.py` + `app/reads.py` (query/projection logic), mirroring
the existing `routes.py` / `artifacts.py` split — handlers stay thin, projection is unit-tested
without HTTP. Register the new router in `create_app`.

### Where the fields live — read this before writing the projection

There is **no `accession`, `gene_symbol`, or `folded_at` column.** The columns are:
`id, user_id, input_type, input_value, structure_source, pdb_path, mean_plddt, pae_json_path,
metadata (attr `meta`), notes, ranking_run_id, created_at`.

- `accession` ← `input_value`
- `gene`, `label`, `tier`, `tier_reason`, `disposition`, `held_out`, `boundary_method`,
  `fold_length`, `full_length`, `sequence`, `fold_provenance` ← all inside `meta`
- `folded_at` exists **only** at `meta.fold_provenance.folded_at`. **Do not sort by
  `created_at`** — 41 of the 42 rows share one batch timestamp, so it does not order the folds.
  Sort the list by `id`.

---

## 2. ⚠ Two things that will bite if missed

**(a) Serve the stored `pdb_path`. Never reconstruct a path.**
Artifacts are written to `{artifact_root}/{job_id}/` (`app/artifacts.py:79`) and `pdb_path` is
stored **absolute** (`/data/artifacts/1/structure.pdb`). In this cohort `job_id ==
analysis_id` **coincidentally**; they are different keys and nothing guarantees it. Look the
row up by integer id, serve `row.pdb_path`. On an unauthenticated endpoint this is also the
path-traversal defence — no client-supplied value ever reaches the filesystem.

**(b) The existing auth test must be REPLACED, not extended.**
`tests/test_transport_routes.py:249` is a hardcoded `parametrize` of four paths. Adding open
`/api` routes will **not** fail it — it will silently stop covering the surface, which is
precisely the "a route added later inherits no check" failure `app/deps.py` exists to prevent.

Replace it with a test that **introspects `app.routes`** and asserts the prefix rule:

> every route under `/jobs` requires the bearer token; every route under `/api` does not;
> **a route matching neither prefix fails the test.**

Iterate the app's actual route table — so a future route in a third namespace breaks the build
rather than slipping through. This is D-034 decision 5 and it is not optional.

---

## 3. Test surface — write these first

Hermetic, following the existing pattern: in-memory SQLite + `create_all` (D-005, **not** the
migration chain) + `TestClient`, per `tests/test_transport_routes.py`'s header. Seed rows whose
`meta` mirrors the real shape — copy it from the production examples in the D-034 entry
(ids 1 and 37), including a `held_out: true` / `boundary_method: "whole"` row, so the tests
exercise both dispositions the cohort actually contains.

1. **List — field set is exact.** Returns all seeded rows; each carries the twelve fields
   above; **`sequence` and `fold_provenance` are absent.** Assert absence explicitly — this is
   the payload-weight ruling and it regresses invisibly.
2. **List — ordering** is by `id`, ascending.
3. **Detail — full record** includes `sequence` and `fold_provenance` with its keys intact
   (`model_id`, `model_revision`, `dtype`, `chunk_size`, `truncated`, `folded_at`,
   `mean_plddt`).
4. **Detail — 404** on an unknown id.
5. **Structure — serves the file at the row's stored `pdb_path`**, content-type `text/plain`,
   body matching what was written. Include a row whose `pdb_path` points somewhere *other* than
   `{root}/{id}/` so a reconstructed path fails the test.
6. **Structure — 404** when the row is unknown, and 404 (not 500) when `pdb_path` is null.
7. **plddt — returns the array**; 404 on unknown id.
8. **Auth property (§2b)** — the introspecting prefix test.
9. **Reads do not mutate.** Row count and one row's fields are unchanged after hitting every
   read route.

**User test (manual, after deploy):** `curl https://pharmfoldmdk.fly.dev/api/analyses` returns
42 rows with no `Authorization` header; `.../api/analyses/1/structure` returns the NECTIN4 PDB
(~194 KB, starts with a PDB record line); `.../api/analyses/999` returns 404;
`curl -X POST .../jobs/claim` still returns 401.

---

## 4. Out of scope — deliberately

- **No PAE route.** 824 KB–1.07 MB per target, ~85% of the 21 MB Volume, and nothing renders
  it this session (D-034 decision 3).
- **No React.** The bundle is the next PR; this one is the supplier.
- **No DEP-001 image change.** No build step or static-serve path yet — that amendment lands
  with the bundle, not here.
- **No pagination.** 42 rows, light payload. If the cohort grows past a few hundred this gets
  revisited; do not pre-build it.
- **No scorer/ranking fields.** They do not exist (D-027 → fit → step 3). Do not stub them.

---

## 5. Definition of done

- `D-034` in `docs/README.md`; `ARCHITECTURE.md` and the run guide corrected **in the same PR**.
- Tests written first, failing for the right reason, then green.
- Both required checks (`test`, `postgres`) green; merged; deployed.
- The four manual curls in §3 verified against `pharmfoldmdk.fly.dev`.
- **Report back:** the actual response size of `GET /api/analyses` for 42 rows. It is the number
  that tells us whether the light/full split was cut in the right place, and it goes in the
  close-out.

---

## 6. If something here is wrong, say so

D-034 was ruled against production queries and `ls -l` on the Volume, but the Planner has not
read every line of `app/`. If the projection cannot be built as specified, or §2a's path
assumption is wrong, or the auth introspection is impossible with FastAPI's route objects —
**surface it rather than working around it.** DEP-005 exists because a Builder refused to guess
past a gap, and that was the right call.
