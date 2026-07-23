# Orders for Code — D-035, the rental tier

**Session:** 2026-07-23, second half. **Planner:** Claude. **Builder:** Code.
**Entry:** `D-035` (accepted, lands in this PR). **Tree at issue:** `0bc9258`.
**Prerequisite:** D-034 merged and deployed. These are independent changes; do not interleave.

**Nothing here requires the A6000.** All of it lands before any paid time is bought — that is
the point of the sequencing.

---

## 0. Land the entry first (CLAUDE.md rule 1)

`docs/README.md` — prepend `D-035`. Same PR:

- **`ARCHITECTURE.md`** — the rental tier's artifact path is now asymmetric with the local
  tier's *in transport* (PAE out-of-band) while **identical on disk** (both land under the
  analysis's artifact directory, both populate `pae_json_path`). The component table's
  "Rented-GPU batch" row needs this.
- **D-030 and D-031 amendments** — the 5–10× gzip estimate is falsified at **2.2×** (measured,
  `ls -l /data/artifacts/1/`). Amend in place, marking the estimate as superseded rather than
  deleting it; the reversal is itself evidence (method note item 4).

---

## 1. Three code changes, smallest first

### (a) The httpx timeout — independent, lands regardless of everything else

`worker/http_client.py:34` builds `httpx.Client(base_url=base_url)` with **no timeout**. httpx
defaults to 5 s on all four phases. Set explicitly:

```python
httpx.Timeout(connect=10.0, read=300.0, write=300.0, pool=10.0)
```

**Why this is not cosmetic:** `_post` maps `httpx.HTTPError` → `TransportError`, which the loop
treats as **retryable**. A slow upload therefore times out → retries → exhausts
`submit_attempts` → the job reaps → **re-folds on a paid card.** D-030 named this cost
explicitly. Even at option C's ~1 MB uploads, a marginal residential uplink is exactly how an
intermittent paid retry loop starts.

Do not set the timeout only on `upload` — set it on the client, so every call has a chosen
value rather than an inherited default.

### (b) `upload` stops sending PAE

`worker/http_client.py:46-59` currently gzips `artifacts.pae` into the multipart body. Remove
PAE from the upload. The route's `pae` parameter is already `Optional[UploadFile] = File(None)`
(`app/routes.py`), so **no server-side change is needed** — verify that, don't assume it.

**⚠ Do not touch `runner.write_artifacts`.** It writes `pae.json` to local disk
(`worker/runner.py:145`) and must keep doing so — that local file *is* the artifact option C
retrieves. The runner knows nothing about the database or transport (D-018) and that separation
is what makes this change small. **The two must not be coupled:** a test should assert the
runner still writes `pae.json` while the client no longer uploads it.

### (c) The out-of-band retrieval path — committed code, not a shell one-liner

D-009 §3's binding condition: the cache pipeline must be **committed, reproducible code in this
repo**, not a one-off script. So the PAE transfer is a scripted, re-runnable step —
`scripts/` is the right home, alongside `dev_check_db.py` and friends.

It must: walk the rented box's local artifact directories, and land each `pae.json` (gzipped)
into the corresponding analysis's directory on the Fly Volume, populating `pae_json_path` for
the row. Idempotent — a re-run after a partial transfer converges, same discipline as
`persist_fold` (D-031 (a)).

**⚠ The one hazard that loses data.** D-011 rules **no network volumes** — *"download weights,
fold, upload artifacts, terminate."* PAE on container disk is **destroyed on pod termination**.
So retrieval is a **blocking pre-termination step**: the batch is not done when the last fold
completes; it is done when PAE is off the box and verified. Whatever run-guide text you write
must say that in those terms, because the failure is silent and unrecoverable without a paid
re-fold.

**Design question for you, not pre-ruled:** whether the transfer pushes from the pod to the
transport (a new route — needs a decision entry, D-030's *"a fifth route, not by widening an
existing one"* discipline applies) or pulls/pushes by some other path. **Do not add a route
without ruling it.** If the cleanest shape needs one, say so and it gets an entry before code.

---

## 2. Test surface — write these first

1. **The client has an explicit timeout.** Assert the configured `httpx.Timeout` values, not
   that "a timeout exists" — a test that passes against the 5 s default proves nothing.
2. **`upload` omits PAE.** Inspect the multipart body: `pdb`, `plddt`, `provenance` present,
   `pae` absent.
3. **`write_artifacts` still writes `pae.json`.** The decoupling in §1(b), asserted directly.
4. **The loop's existing guarantees are unchanged** — fold called exactly once per claim, upload
   before complete, transport failure retries the report and never the fold. These already have
   tests; confirm they still pass rather than rewriting them.
5. **The retrieval step is idempotent** — a second run over an already-transferred directory is
   a no-op and does not corrupt `pae_json_path`.
6. **The route accepts an upload with no PAE part** — verify against `app/routes.py`'s existing
   `Optional` parameter; if it does not, that is a server change and it needs saying.

---

## 3. Out of scope

- **No lease heartbeat.** D-030's structural fix stays unbuilt; D-035 restates its trigger (an
  observed reap of live work, or PAE returning to the upload path). Do not build it speculatively.
- **No change to `DEFAULT_STALE_SECONDS`.** It stays 3600 and stays PROVISIONAL. D-035 records
  that its justification weakened; option C restores the margin by another route.
- **No PAE read route.** Nothing renders PAE (D-034 decision 3).
- **No rental fold.** The A6000 is owner action and gates nothing here.

---

## 4. Definition of done

- `D-035` landed; `ARCHITECTURE.md` + D-030/D-031 amendments in the same PR.
- Tests first, failing for the right reason, then green; both required checks green; merged.
- **The §3(b) body-limit probe run once** — a synthetic POST to `/jobs/{id}/artifacts` against
  prod, large enough to be informative. Cost zero, and it settles a fact nobody on this project
  has established. **Report the number.**
- Run-guide text for the rental batch, including the blocking pre-termination retrieval step.

---

## 5. If something here is wrong, say so

D-035 was ruled against the tree and production artifacts, but the Planner has not run a rental
fold — nobody has. The §1(c) transfer path is the least-specified part of this and the most
likely to need a shape the Planner did not anticipate. **Surface it rather than working around
it**, and if it needs a route or a decision, that is an entry before code, not a workaround.

---

## Addendum — Planner's session comments (relayed by owner, 2026-07-23)

Recorded here so the full instruction set lives in the repo, not only in chat.

**Sequencing: hold on React; take D-035 next.** Three reasons:

1. **§3(a) is a live cost bug on a paid card.** `httpx.Client()` with no timeout defaults to
   5 s; `_post` maps the resulting error to `TransportError`, which the loop retries — so a slow
   upload times out, exhausts attempts, reaps, and re-folds on an A6000 you're paying for.
   Nothing about React reduces that exposure.
2. **Nothing in D-035 needs the A6000.** All three changes land before any paid time is bought —
   the rented box should meet finished code.
3. **The React shell is larger and less urgent, and now has a firmer spec:** UI Plan v2 supersedes
   the old plan in full, and D-034's field list is measured rather than assumed.

**Two additions to these orders, given what Code reported on the D-034 close-out:**

- **The body-limit probe (§3(b)/§1(b)) is trivially cheap and worth doing anyway.** Under option C
  the rental upload is ~1 MB, so it is no longer a gate before paid time — but D-031 flagged
  upload size limits as its concern and nobody on this project has established the number. One
  synthetic POST settles it permanently.
- **Flag for §1(c):** Code should expect the out-of-band PAE transfer to be the least-specified
  part, and it may need a route. If it does, that is **an entry before code, not a workaround** —
  D-030's discipline is *"a fifth route, not by widening an existing one."*

**UI Plan v2** is attached to the repo (`docs/UI_Plan_v2.md`); it supersedes `docs/UI_Plan.md`
in full, and the React work is built against it rather than the July document.

**The close-out is the Planner's to write at end of day.** When D-035 lands the Planner will
have: the first fold's cohort landed and read, the read API shipped, the gzip estimate falsified
with its consequences ruled, and the UI plan rebuilt on measured data.
