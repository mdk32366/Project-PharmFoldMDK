# PASTE-READY — TWO sub-entries — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `e3bc5a03e3122efbe17060dd03d122f94d5cfcba80bc1fd1f1f3a9c1ca4c7320`
**bytes** = `4122`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **TWO sub-entries in one file, for TWO different parents. Split them on landing.**
> **Both are `####` — both titles carry "amendment", unlike `F-053`, which the Planner sent at the
> wrong level and Code correctly landed at `###`.**
> ⚠ **Confirm both numbers against the live log. Three greps each.**

---

#### F-052 amendment 2 — ⚠⚠ Someone met this exact bug one line above, fixed the caller in front of them, and left the sibling

- **Date:** 2026-08-20 · **Status:** `F-052` stays **OPEN.**

**`worker/runner.py`: `outputs["predicted_aligned_error"].squeeze()` collapses `(1,1,1)` to a 0-dim
scalar, so `result.pae` is a FLOAT rather than a matrix.** ⚠ **The census minimum span is 1 aa, so any
PAE work over the census meets it.** **The 439-aa fold returned a proper 439×439 — the defect is
specific to degenerate spans and invisible to every test written against a normal protein.**

⚠⚠ **AND THE LINE DIRECTLY ABOVE HAD THE IDENTICAL DEFECT AND WAS ALREADY PATCHED:**
`plddt_raw if isinstance(plddt_raw, list) else [plddt_raw]`. **Someone met this bug, fixed the caller
in front of them, and did not generalise to its sibling ONE LINE BELOW.**

⚠ **That is `F-052` at its smallest possible blast radius — a convention established, obeyed by the
caller its author was looking at, and not by the next one down.** **The field of view was one line.**

**The repair:** `_pae_matrix` **drops batch dims BY INDEX, never by size**, so no shape decision
depends on how large `L` happens to be, **and it restores the matrix if anything upstream already
collapsed it.**

⚠⚠ **AN HONEST LIMIT ON THE PROOF, reported rather than claimed away:** **only the STRUCTURAL test
reddens on revert.** **The behavioural tests still pass with `squeeze()` restored, because the shape
restoration catches the scalar either way.** ⚠ **So the behavioural fix is the restoration; the
index-drop removes the size-dependent decision.** *Stating what the revert supports rather than a
stronger proof.*

⚠ **The fixture is a 1-residue span and the corpus cannot provide one** — every other census span is
**≥21 aa**, nine measured, all returning proper `N×N`. **Only a deliberate fixture reaches it.**
**`F-046`'s lesson applied before the fact.**

⚠⚠ **And behavioural confirmation the revert proof could not give arrived later, against ESMFold
rather than a fixture: a real matrix where a scalar came back before.**

---

#### F-053 amendment 1 — ⚠ §5's hypothesis has a hole: `span^1.26` is a TIME law and says nothing about MEMORY

- **Date:** 2026-08-20 · **Status:** `F-053` stays **OPEN.**

**§5 proposed that releasing the resident model frees ~5.24 GiB against a ~1.26 GiB incremental, so
part of the `441–629` band might fold locally.**

⚠⚠ **THE INCREMENTAL WAS MEASURED AT 439 aa AND ITS SCALING IS UNMEASURED.** **The Planner reasoned
*5.24 freed versus 1.26 incremental, therefore headroom* — and silently assumed the incremental is
roughly flat in span.** ⚠ **Trunk attention is at least O(L²); there is no reason to expect 629 aa to
cost 1.26 GiB, and no measurement either way.** ***`span^1.26` describes TIME. Nothing measured here
describes memory growth.*** *(Code's catch.)*

⚠ **And reload is not free in a second way:** **the 1-aa fold took 13.9 s against 2.0 s for the
21-aa fold, so the ~11.7 s load is PER-INVOCATION, not amortised** — **~13% overhead across a handful
of 75–101 s folds, and the 8.7 h across 2,690.**

**⚠⚠ THE TEST THAT SETTLES IT IS BETTER THAN THE ARGUMENT AND COSTS TWO MINUTES: one fold at ~500 aa
with the model released.** **It answers the question directly and it is the first datum on the
memory-versus-length curve §4 says nobody has.**

⚠ **Until it runs, §5 is a question and must not be cited as a reason to spend or not spend.**

**⚠ A separate correction, same run.** **The `F-042` path (c) projection moved 6.95 h → 7.67 h on the
fixed worker, and that is RUN VARIANCE, NOT THE FIX** — *the squeeze fix changes shape handling for
one protein and fold time for none.* **Eight of ten folds agree within 5%; the entire +10.4% comes
from the two longest, 439 aa going 75.2 s → 101.1 s.** ⚠⚠ **Thermal state and card contention. The
honest figure is ~7–8 h, and if a ruling is sensitive to that spread it needs REPEAT RUNS, not a
better fit.** **A tighter regression on unstable measurements is precision theatre.**
