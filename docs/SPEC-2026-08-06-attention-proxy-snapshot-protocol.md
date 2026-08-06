# SPEC — 2026-08-06 — The attention-proxy snapshot protocol, pre-registered before Run A

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> **Pre-registered 2026-08-06, BEFORE Run A executed and therefore before any Run A result existed.**
> Ruled by the Planner, 2026-08-06, on Code's report that `scripts/attention_control.py --freeze` is a
> deliberate stub: `build_snapshot()` is fully implemented, its fetchers are injected parameters, and
> **no RCSB/UniProt or PubMed fetcher was ever written.** PR #109 shipped the assembly seam and not
> the network calls.

---

## §1 — What the freeze actually protects, and why a protocol can substitute for data

⚠ **The freeze does not protect the data. It protects against the researcher's degrees of freedom.**
That distinction is the whole ruling: a *rule* can be frozen today, before Run A's result exists,
even though the *snapshot* cannot be taken until the fetchers are wired.

Enumerated, so that nothing is left implicitly open:

| Degree of freedom | State at pre-registration | Closed by |
|---|---|---|
| Which query text | **Closed** | `PUBMED_QUERY_TEMPLATE`, a committed constant predating every result |
| Which endpoints | **Closed** | `PUBMED_ENDPOINT`, `UNIPROT_ENDPOINT`, committed constants |
| Which symbols | **Closed** | the ranking set — not selected, derived |
| **Which pull counts as the snapshot** | ⚠ **OPEN** | §2.1–2.3 below |
| **What happens when a pull partly fails** | ⚠ **OPEN** | §2.2–2.3 below |

**Two open doors, and both are rules rather than data.** Closing them here closes the hole a data
freeze would have closed, at the only moment when doing so is honest.

---

## §2 — The protocol. Binding on the wiring PR and on whoever takes the snapshot.

1. **The as-of date is the date of the first successful pull after the wiring PR merges.**
   ⚠ **Not chosen, and not selected from candidates.** A date that was picked is not an as-of date.

2. **One pull. The first pull IS the snapshot.** If it fails, **the failure is recorded with its
   timestamp on the snapshot itself and the retry is disclosed.** ⚠ **No silent second attempt** — an
   undisclosed retry is a chosen pull wearing the words "first pull".

3. **All-or-nothing over the ranking set.** ⚠ **No symbol is ever re-queried individually.**
   Per-symbol retry is where shopping hides once the query text can no longer move: the query is
   fixed, the endpoints are fixed, and the symbols are fixed — so the last remaining lever is
   *which attempt at which symbol you keep.* This closes it.

4. **The snapshot records, on its face:** the source · the endpoint constant · the committed query
   template · **the resolved query per symbol** · the as-of date · and **Run A's fired Decision-4 row,
   by name.**

5. **Run B is byte-identical reproducible from the snapshot.** `--control` reads the snapshot and
   never queries — the property `load_snapshot()` already enforces by raising rather than falling
   back to a live query.

---

## §3 — ⚠ The disclosure, which is not optional and is not to be glossed

**If Run A survives, the snapshot will be taken knowing that Run A survived.**

That sentence goes **on the snapshot's face** and **into the `### F-017` entry**, in this form:

> *The attention-control proxies were frozen **after** Run A's result was known. **The protocol
> governing the freeze was pre-registered before it** — see
> `SPEC-2026-08-06-attention-proxy-snapshot-protocol.md`, committed 2026-08-06 prior to Run A.*

⚠ **The honest version of that sentence is the one that survives a reviewer. The dishonest version is
not writing it.** The protocol removes the degrees of freedom; it does not remove the ordering, and
the ordering is a fact about how this was done.

**If Run A collapses, Run B is moot** — `ORDERS-Code-2026-08-05-D-075-run.md` §3 makes B conditional
on A surviving, precisely so that a null axis is not followed by a control built to rescue it — and
this entire question dissolves without ever being exercised.

---

## §4 — What was declined, and why it is recorded rather than assumed

**Wiring the fetchers before Run A was declined.** It is a build task inside a run window, and it
would have been the **sixth** deferral of the run this day was sequenced for. ⚠ Recorded as a
decision with a reason, not as an omission — a deferral nobody wrote down is indistinguishable from
an oversight six weeks later, which is the shape `### F-023` exists to record.

**Two cross-version checks ran before Run A and both cleared** (Code, 2026-08-06, no persist, no
write, no row targeted):

| Arm | Recomputed on today's `5ccab48772b5` | Stored | Verdict |
|---|---|---|---|
| `no_plddt` | median 0.5625 / mean 0.5893 / 6-of-12 | id=3 (`a927dc4532b7`) | identical |
| `preregistered` | median 0.6071 / mean 0.6176 / 8-of-12, Spearman −0.04828045495852675 | id=2 (`91e646e4a289`) | **byte-identical** |

⚠ **Three distinct scorer versions are in play** — `91e646e4a289` (id=2), `a927dc4532b7` (id=3/id=4),
`5ccab48772b5` (today). The second check reaches the arm D-075 actually changed: projection became
unconditional, and rows are now **seven** long where id=2 was fitted at **six**. It reproduces
exactly. **Decision 4's FULL anchor is commensurable with the ablation it will be read against.**

⚠ Neither check writes, amends, or targets `ranking_run` id=2. **Creating a second path to a stored
quantity and comparing it in the same breath is the remedy for the two-paths class, not an instance
of it** — the instance is having two paths and never comparing them.
