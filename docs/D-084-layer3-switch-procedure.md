# D-084 — Enabling layer 3, step by step

> **Type:** A procedure. ⚠ **Written down rather than recalled**, because it spans a session
> boundary and half the steps are the owner's hands on a terminal I cannot see.
>
> **Owner's standing instruction (2026-08-16):** *"No change on that decision on Layer 3 switch.
> Execute when appropriate."* — so the timing is Code's call; **steps 1 and 3 below are the
> owner's.**

---

## When — and why this exact boundary

⚠ **Tranche 4 is 301–439 aa: the first band that runs up against `known_good = 440`.** That is what
makes *"layer 3 before tranche 4"* a boundary and not a preference.

| tranche | rows | span | vs the 440 ceiling |
|---|---|---|---|
| 1 ✅ | 1,307 | 1–50 aa | far under |
| 2 | 535 | 51–149 aa | far under |
| 3 | 517 | 152–300 aa | under |
| **4** | **332** | **301–439 aa** | ⚠ **runs up against it** |
| 5 | 776 | 441–14,451 aa | over — rental tier |

**The window is created deliberately by NOT ingesting tranche 4.** When tranche 3 drains, the
worker has nothing queued and goes idle. ⚠ **That idle worker IS the window** — it is not a
coincidence to be waited for, it is a state that was arranged.

**Tranches 0–3 fold in-process; tranche 4 starts the new topology.** ⚠ No tranche is split across
two process topologies, so the population folded under each is knowable rather than mixed.

**Precondition, verified by Code, not assumed:**

```
python scripts/crank_status.py
```
⚠ **`pending = 0` AND `claimed = 0` for tranches 1, 2 and 3.** A `claimed` job means the weights
are still resident somewhere.

---

## Step 1 — OWNER: stop the worker

**In the worker's own PowerShell window** — the one that printed
`worker starting - polls silently; watch: fly logs -a pharmfoldmdk`:

```
Ctrl+C
```

⚠⚠ **DO NOT CLOSE THE WINDOW.** Its environment holds `WORKER_AUTH_TOKEN` and `TRANSPORT_URL`,
loaded by `dev-up.ps1` and **inherited, never re-typed**. Closing it means re-running `dev-up.ps1`
to get them back — and ⚠ **`dev-up.ps1` opens a SECOND proxy on the fixed port 16380**, which is a
standing prohibition.

**Confirm:** the PowerShell prompt returns in that window.

---

## Step 2 — CODE: the equivalence gate

```
python scripts/supervisor_equivalence.py --arm inprocess  --accession <acc> --tier local --i-have-stopped-the-worker
python scripts/supervisor_equivalence.py --arm supervised --accession <acc> --tier local --i-have-stopped-the-worker
python scripts/supervisor_equivalence.py --compare
```

⚠ **One arm per invocation, and that is a safety property.** The supervised arm spawns a child that
loads the weights; had the in-process arm cached them in the same process, **two model copies would
be resident on one card — the configuration that bugchecked the host on 2026-08-12.**

⚠ The script **refuses to run while any job is `claimed`**, by *reading the queue*. The override is
spelled `--i-have-stopped-the-worker` so that using it is a sentence someone has to mean.

**Required verdict:** `⚠ byte-identical PDB | True`.

⚠⚠ **If it is not byte-identical: STOP. Do not enable.** And ⚠ **do not attribute the difference to
the supervisor** until `scripts/determinism_control.py` has run on the same accession and tier —
without it, *"the supervisor differs"* and *"the recipe is nondeterministic"* are **the same
observation**.

⚠ What this proves is narrow: **the fold is unchanged.** It is the *precondition* for switching on,
**not evidence that layer 3 catches anything** — the death path is covered by
`tests/test_fold_supervisor.py`, not by this.

---

## Step 3 — OWNER: restart with the flag

**In that same window**, which still has the environment:

```powershell
$env:WORKER_FOLD_IN_CHILD = '1'
& '.venv\Scripts\python.exe' -m worker.main
```

⚠ **CONFIRM THE FIRST LINE READS EXACTLY:**

```
[worker] D-082 layer 3 ENABLED - folding in a child process
```

⚠⚠ **If it says `layer 3 off (set WORKER_FOLD_IN_CHILD=1 to enable)`, the variable did not take —
STOP and report.** Do not proceed on the assumption it worked; that banner is the **only**
confirmation the switch landed, which is why it prints on **every** start, both ways.

> ⚠ The banner is **ASCII only, deliberately.** It first contained an em dash, which raises
> `UnicodeEncodeError` on **cp437** and would have **killed the worker at startup** — a startup
> message that destroys the process it announces. Guarded by
> `test_the_startup_banner_survives_every_windows_console_codepage`, asserted over the source.

---

## Step 4 — CODE: ingest tranche 4

```
python scripts/census_ingest.py --tranche 4 --dry-run   # ⚠ always first
python scripts/census_ingest.py --tranche 4
```

Then watch the first few complete under the new topology before walking away.

---

## Rollback — one step, and it costs nothing

`Ctrl+C` in the worker window, then:

```powershell
Remove-Item Env:\WORKER_FOLD_IN_CHILD
& '.venv\Scripts\python.exe' -m worker.main
```

**Confirm it now prints `layer 3 off`.** ⚠ Any jobs left `claimed` by the stop are **evidence, not
damage** — D-082's `infer_host_down()` reads exactly that signal, and a `claimed` row after a clean
manual stop is expected rather than alarming.

---

## ⚠ What this procedure does NOT do

**It does not make the fold path bugcheck-proof.** ⚠⚠ **Nothing does.** Layer 3 converts every
failure *short of a host death* — segfault, driver reset, allocator abort — into a **named job
outcome with the crank alive**. The 2026-08-12 bugcheck would still have taken the machine down;
**layers 1 and 2 are what address that**, and they are already on.
