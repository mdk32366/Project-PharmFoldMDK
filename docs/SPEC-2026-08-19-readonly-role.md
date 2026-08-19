# SPEC — 2026-08-19 — the read-only role: the exact statements, written before anything is run

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority.
>
> ⚠⚠ **NOTHING HERE HAS BEEN RUN.** `HB3` requires the statements to be reported **before**
> execution, and this is that report. **The grant is a production write** and goes through whatever
> path the existing ruling permits.

---

## §1 — ⚠ What this role protects against, and what it does not

**It protects us from our own `pytest`.** `D-092` refuses production **by hostname**, and
`AC1` measured the residual: **through a tunnel the hostname is `localhost`, so the guard does not
fire** — while 14 tests `TRUNCATE` on every test that touches `pg_engine`. A role that *cannot*
truncate closes that hole **at the database**, which is the only place it closes.

⚠⚠ **It does nothing about the 2026-08-17 credential.** That credential exists outside systems the
owner controls and **only rotation ends it** — recorded once, per the owner's ruling, and not raised
again.

## §2 — The statements

⚠ **The password does not originate in Code's terminal, is never printed, never echoed, and never
appears in a transcript** (`HB2`). It is supplied by the owner or from Fly's secret store, and the
placeholder below is **not** a value to fill in on a shared screen.

```sql
-- 1. the role. LOGIN, no inheritance of anything it was not granted, no superuser, no createdb,
--    no createrole, and ⚠ NOBYPASSRLS so a future row-level policy cannot be stepped over.
CREATE ROLE pharmfold_readonly
    LOGIN
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS
    PASSWORD :'readonly_password';        -- supplied out of band; never literal in a transcript

-- 2. connect, and read the schema's shape
GRANT CONNECT ON DATABASE <dbname> TO pharmfold_readonly;
GRANT USAGE   ON SCHEMA   public   TO pharmfold_readonly;

-- 3. ⚠ SELECT and nothing else, on what exists today
GRANT SELECT ON ALL TABLES    IN SCHEMA public TO pharmfold_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO pharmfold_readonly;

-- 4. ⚠⚠ and on what is created LATER, or the next migration silently creates a table this role
--    cannot read — an absence that would look like a bug in a query.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO pharmfold_readonly;

-- 5. ⚠ belt and braces: explicitly remove every write verb, in case a default or an inherited
--    grant supplied one. REVOKE of a privilege never held is a no-op, so this is safe to run.
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
    ON ALL TABLES IN SCHEMA public FROM pharmfold_readonly;
REVOKE CREATE ON SCHEMA public FROM pharmfold_readonly;
```

## §3 — ⚠⚠ Three things this SPEC will not paper over

**1 — `PUBLIC` grants are GLOBAL, and `HB1`'s "REVOKE anything inherited from PUBLIC" cannot be done
role-locally.** A privilege held by `PUBLIC` is held by *every* role; revoking it (`REVOKE … FROM
PUBLIC`) changes the database for the application role too. ⚠ **So it is NOT included above.**
On PostgreSQL 15+ `PUBLIC` no longer holds `CREATE` on `public` by default, which is the grant that
would matter — **but that is a claim about the server version and it must be checked, not assumed**
(`SHOW server_version`). **Named rather than silently skipped.**

**2 — ⚠ OWNERSHIP is the hole that grants cannot close.** `HB1` is right that an owner can truncate
regardless of `REVOKE`. `CREATE ROLE` above makes `pharmfold_readonly` own nothing, and it must
**never** be made the owner of a table, nor a member of the owning role. ⚠⚠ **This is not enforceable
by the statements above** — it is a property of what else is run later, so it is stated as a standing
constraint and is a candidate for a check rather than a comment.

**3 — ⚠ Fly MPG may not grant `CREATE ROLE` to the application user.** If the app's role is not a
superuser and lacks `CREATEROLE`, statement 1 fails and the role must be created through
`fly mpg users` or by an admin connection. **That is a fact about the plan, and it is the first thing
statement 1 will tell us.** *Reported as an expected branch, not discovered as a surprise.*

## §4 — `HB4` — the proof, which is the point

⚠⚠ **Granting is not proving.** After the role exists, connect **as that role** and run:

```sql
TRUNCATE TABLE jobs;          -- must fail
INSERT INTO ranking_runs (target_list_version, scorer_version) VALUES ('x','y');   -- must fail
SELECT count(*) FROM protein_analyses;                                             -- must succeed
```

**Report the permission-error text verbatim for each refusal.** ⚠ *That is the difference between
"we checked" and "it cannot happen"* — and a role that refused `SELECT` too would be a broken grant
wearing the same green tick, which is why the third statement is there.

## §5 — Sequence, and what is still blocked

⚠ `HB5`: none of this proceeds until `HA` reports — and `HA` has now reported on five of its six
questions. **`HA5`, the restore-and-count, requires provisioning a separate billed cluster** and is
the owner's spend decision, stated in the reply rather than taken here.

⚠⚠ **The credential is the owner's** (`R3`). A production credential Code holds and the owner never
sees is worse than the one not being rotated — so the grant runs with the owner supplying the
password, and `HB4`'s proof runs immediately afterward, in the same session, against the same role.
