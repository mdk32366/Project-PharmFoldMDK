# ORDERS — Code — the backup as three facts, the read-only role, phase 1's status, and `F-049`

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, no newline
normalisation) = `283689e1008f7e1bfac1928d93cbd99297c757d027e60db947937c037c92e86e`
**bytes** = `7670`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header** — provenance goes in
> `SPEC-2026-08-19-landed-artifact-provenance.md`.
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold. Tranche 5 HELD** (`D-091` r2).

---

## §0 — Owner rulings carried in (2026-08-19)

**R1 — ⚠ The 2026-08-17 credential is NOT rotated. Owner's decision, made knowingly, recorded.**
⚠⚠ **The exposure is unchanged by anything below: the credential exists outside systems the owner
controls, and only rotation ends it.** **The read-only role protects us from our own `pytest`. It
does nothing about a credential someone else already holds.** **Stated once, recorded, not raised
again.**

**R2 — Code verifies the backup.** §1. ⚠ **This is the standing precondition on every tunnel.**

**R3 — Code may execute the read-only grant.** §2. ⚠⚠ **The GRANT is Code's; the CREDENTIAL is the
owner's** — **a production credential that the owner never sees is worse than the one we are not
rotating.**

**R4 — `F-049` is written for the `scorer_version` finding.** §4.

---

## §1 — ⚠⚠ Task HA — the backup, as THREE facts. A single yes is not an answer

**KEEL-1 V9 Principle 1, second clause, and it is not one question:**
**a COMPLETED backup exists · its AGE, stated as exposure · WHAT IT DOES NOT COVER.**

⚠ **Principle 1's blood line is ours:** *2,771 rows to 1 — and we recovered it from a backup nobody
had ever verified existed. It worked. That is luck standing in for process.*

**HA1 — ⚠ FIRST, and it may change everything below: is a RESTORE even possible on this plan?**
**Can a Fly managed Postgres backup be restored into a scratch target?** ⚠⚠ **If it cannot, then
*"a backup exists and has never been restored"* is the honest finding and it is a DIFFERENT RISK
POSTURE from an unverified one.** **Report that before attempting anything.**

**HA2 — Does `zp2wjrej9lwodn4q` have a COMPLETED backup?** ⚠ **Report the status field verbatim, the
timestamp, and the size.** **A backup listed as *in progress*, *pending* or *failed* is not a backup,
and *scheduled* is a plan.**

**HA3 — ⚠ AGE, stated as EXPOSURE, not as a date.** *"Most recent completed backup is N hours old,
therefore up to N hours of writes are unrecoverable"* — **the sentence a person can act on.**

**HA4 — ⚠⚠ WHAT IT DOES NOT COVER.** **The `/data/artifacts` mount is NOT in Postgres.** ⚠ **Are the
folded structures on that volume backed up at all, by anything?** **2,690 folds represent real GPU
spend and a database backup does not touch them.** **Report the volume's backup state separately and
name it as a distinct exposure.**

**HA5 — ⚠ Accept by REPRODUCTION, not by label, to whatever depth `HA1` permits.** **If a restore
into a scratch target is possible, do it and report a ROW COUNT from the restored copy.** **If it is
not, say so plainly — *unverifiable on this plan* is a category with a cause, and it is a finding.**

**HA6 — ⚠⚠ The old cluster `gjpkdonnmkeoyln4` was ORDERED DESTROYED and never verified.** **Report
whether it still exists.** **The 2026-08-17 recovery came from a backup on it.** ⚠ **If it is gone
and the new cluster's backup is unverified, the recovery path we actually used no longer exists.**

## §2 — Task HB — the read-only role, and the credential boundary

**HB1 — Write the `CREATE ROLE` / `GRANT`**: `SELECT` on the tables and nothing else — **no
`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, no DDL**, and ⚠ **no ownership of any table**, since an
owner can truncate regardless of grants. **Also `REVOKE` anything inherited from `PUBLIC`.**

**HB2 — ⚠⚠ THE PASSWORD DOES NOT ORIGINATE IN YOUR TERMINAL.** **It comes from the owner or from
Fly's secret store.** ⚠ **It is never printed, never echoed, never in a transcript** — *the standing
item at the top of this order exists because a credential was printed in one.*

**HB3 — ⚠ The grant is itself a PRODUCTION WRITE.** **It goes through whatever path the existing
ruling permits.** **Report what you intend to run BEFORE running it**, and ⚠ **the Planner will not
infer the syntax.**

**HB4 — ⚠⚠ `GD2`: prove the refusal AT THE DATABASE.** **Connect as that role, attempt a `TRUNCATE`,
and report the permission error text.** **That is the difference between *we checked* and *it cannot
happen*** — and the guard we have today does not fire through a tunnel, because `D-092` refuses by
hostname and a tunnel's hostname is `localhost`.

**HB5 — ⚠ HB1–HB4 do not proceed until `HA` reports.** **R2 is a precondition, not a parallel task.**

## §3 — Task HC — phase 1, and whether its completion was ever recorded

**The log rules:** *Phase 1 — the initial migration is run BY HAND, supervised, BEFORE the first
deploy … the owner runs `alembic upgrade head` … and confirms the schema exists.* **Phase 2 is the
release command, *ruled but wired AFTER phase 1 succeeds*.**

**HC1 — Find and cite the entry that rules this** — number **and** name. ⚠ *A quotation without an
entry number is a quotation from nowhere.*

**HC2 — ⚠⚠ Does ANY entry record phase 1 as DONE?** **Not *the app works* — a recorded outcome.**
⚠ **The app serves 2,690 census rows, so a schema exists; that is circumstantial and it is not the
same claim as *the ruled procedure was followed and confirmed*.** **If completion was never written,
phase 2's precondition CANNOT BE CHECKED, and that is the finding.**

**HC3 — Once `HB` lands, report production's current `alembic_version`** and whether it matches
`head` in the tree. ⚠ **Read-only.**

## §4 — Task HD — `F-049`, and it is Code's to write

⚠⚠ **`scorer_version` establishes the same CODE and never the same PARAMETERS.**

**The evidence is already in the log and is not an argument:** ***`F-005` records runs 3 and 4 sharing
`scorer_version=a927dc4532b7` while having different feature sets and therefore different parameter
counts — 5 and 3.*** **Same string, different parameters, already shipped.**

**The entry carries:**
- ⚠ **The consequence: any comparison between two runs resting on a matching version string is
  unfounded.** **`/api/ranking` filters on `valid ∧ run_kind='preregistered'` and the version travels
  with the rows** — **so the surface can present two runs as comparable when they are not.**
- ⚠⚠ **`ranking_runs` stores no coefficients, no standardizer mean or sd, no λ.** **So `D-041` claims
  the fit is reproducible and NOTHING STORED MAKES THAT CHECKABLE** — `F-045`'s shape: *the record
  says what was done and not enough to redo it.*
- **What would have to be persisted for `FB3` to be answerable without fitting**: the seven
  parameters, the standardizer's mean and sd, and the selected λ. ⚠ **Name it; do not build it** —
  `D-074` decision 3.
- **Status: OPEN.** ⚠ `D-074`: a finding against an instrument stays open until the instrument no
  longer exhibits it **or carries in itself the statement of what it gets wrong.**

⚠ **`F-049` was previously earmarked for the guard-direction sweep. This is the cleaner instance and
it takes the number; the sweep takes the next free one.** **Report both numbers when they land.**

## §5 — ⚠ What is NOT ordered

**No tunnel until `HA` reports.** **No ingest.** **No migration.** **No fit, no refit, no new ranking
run.** **No credential rotation** — R1, owner's decision.
⚠⚠ **If `HA1` says a restore is impossible on this plan, STOP AND REPORT before `HB`.** **That answer
changes the owner's risk posture and the decision returns to him.**

## §6 — Report

⚠ **`HA` first and separately** — it gates everything else in this order.
Then branch and tip · **number and title of every entry landed, in the message that lands it** · the
invariant with its keys, tested before any merge · the gate without `.env` sourced.
