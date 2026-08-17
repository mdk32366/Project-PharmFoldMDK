# KEEL V8 — destructive operations: prevention, and recovery

> **Proposed amendment.** ⚠ **V8-a is implemented** (`tests/_db_safety.py`, D-092). **V8-b below is
> proposed and not yet written into any tooling** — it is a rule for a human and an agent to follow,
> and it is deliberately *not* automated, for the reason in §3.
>
> **Occasioned by:** the destruction of the production database on 2026-08-17 and its recovery from
> a backup **nobody had verified existed**.

---

## §1 — The two halves, and why they must not be one amendment

The incident had two independent facts:

1. **A destructive test ran against production.** ⚠ *Prevention.*
2. **Recovery depended on a backup whose existence was discovered after the fact.** ⚠ *Recovery.*

⚠⚠ **Fixing (2) does nothing about (1), and a single "check backups at session start" amendment
would have felt like a remedy while leaving the actual hole open.** They are separate rules with
separate triggers, and collapsing them is the mistake this amendment exists to avoid.

---

## §2 — V8-a — PREVENTION (implemented)

> **The test suite refuses to run against a database whose data is not expendable.**

⚠⚠ **The guard it replaces pointed the wrong way.** `pg_engine` *skips unless* `DATABASE_URL` names
a reachable Postgres — so **supplying production credentials armed the suite.** The safety property
was *"you probably do not have a database"*, which is not a safety property.

- A **hard collection error, never a skip.** ⚠ *A skip is exactly what let a destructive suite look
  harmless.*
- Override is `PHARMFOLD_ALLOW_DESTRUCTIVE_DB=i-know-this-truncates` — ⚠ **not `1`**. A flag someone
  can flick is a flag someone flicks by habit.
- ⚠ **Necessary and not sufficient, and the module says so:** a tunnel to production looks exactly
  like localhost, and `localhost:16380` is one right now.

**Its own tests found two bugs in it, one of which failed OPEN** — `db_host` stopped at the first
`@`, parsing `user:p@ss@prod.example.net` as host `ss`. ⚠ **A guard whose parser can read a
production host as something else is not a guard.**

---

## §3 — V8-b — RECOVERY (proposed)

> **Before any destructive operation, confirm a completed backup exists and state its age.**

**A destructive operation is:** a migration or any DDL · a bulk write, delete or `TRUNCATE` · a
cluster create/destroy/attach/detach · a secret rotation that could orphan access · anything whose
undo is *"restore from backup"*.

**The confirmation is three facts, stated out loud, not looked at:**

1. **A backup exists and its status is `completed`** — ⚠ not `queued`, not `running`. A queued
   backup is not a backup.
2. **Its age.** ⚠ *"There is a backup"* is not the claim that matters; *"the newest completed backup
   is 4 hours old, so up to 4 hours of work is at risk"* is.
3. **What it does not cover.** ⚠ On 2026-08-17 the backups covered the database and **not** the
   fold artifacts — which is why the folds survived a total database loss. **The gap is as much a
   fact as the coverage.**

### ⚠⚠ Why this is NOT a session-start check

**A session-start check runs when nothing is at risk, passes, and trains the reader to skip it.**
That is the same shape as *a guard placed downstream of the filter it guards* — it fires where the
answer cannot change what you do, so it stops being read, and a check nobody reads is a decoration
that costs attention.

⚠ **V8-b is tied to the operation, not the clock.** It runs at the one moment the answer changes the
decision: *if this goes wrong, what is the worst I lose, and can I get it back?*

### ⚠ Why it is not automated

A pre-flight script that queries the backup API and refuses would be easy and would be **the wrong
shape**. The value is not the API call — it is **the operator stating the exposure in their own
words before acting**, because the third fact (*what it does not cover*) is a judgement about the
system, not a field in a response. **Automating it would return `ok` and answer none of it.**

---

## §4 — What this amendment does not claim

⚠ **V8-a would not have prevented every version of the incident.** A proxy to production on
`localhost` passes it. It closes the specific hole (a production hostname in `DATABASE_URL`) and
narrows nothing else.

⚠ **V8-b is a discipline, not a control.** It can be skipped, and it will be skipped under time
pressure — which is exactly when it matters. It is written down so that skipping it is a visible
choice rather than an oversight.

⚠⚠ **And the honest framing of the incident stands: the recovery worked on backups nobody had
verified existed.** That is luck standing in for process. **This amendment converts one of those
into process. It does not make the luck retrospective.**
