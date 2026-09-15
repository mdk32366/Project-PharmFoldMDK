# REPORT — Code → Planner — 2026-09-15 · Amendment 6 C.0: the encoding blocker is CONFIRMED, and the fix needs both of its lines

- **Governs:** `ORDERS-Code-2026-09-16-reattach-and-collapse (5).md`, Amendment 6.
- **Where this file lives:** `C:\Users\mdk32\Downloads\` at the owner's request, and on branch
  **`d167-phase-d-sitting`** as `docs/REPORT-Code-2026-09-15-A6-C0-calibration.md` (A4.8).
- **Session date:** 2026-09-15, America/Los_Angeles (PDT, UTC−7).
- **Production access:** none. Every run below is local, on the owner's machine.

---

## 1. Verdict

1. **A6.1's mechanism is CONFIRMED by reproduction** in an environment matching the owner's own terminal.
   A piped `print('✓ ok')` from the venv Python dies with `UnicodeEncodeError` and exit 1.
2. **A6.1's fix is CONFIRMED, and both of its lines are needed.**
   - `PYTHONUTF8=1` alone stops the crash but writes **mojibake** into the captured output and the log.
   - Only `PYTHONUTF8=1` plus `[Console]::OutputEncoding = UTF-8` yields the right string and the right
     bytes.
3. **⚠ The first C.0 run did NOT go red, and that result was wrong about the owner's terminal.** Code's
   PowerShell tool host injects `PYTHONIOENCODING=utf-8:surrogateescape`, which hides the defect.
   - Per A6.1's own rule a non-failing RED is reported to the Planner. It is reported here **with its
     cause**, and the environment has since been corrected.
4. **A6.1's list of affected lines is incomplete.** Four more printed lines were found (§4). Two of them
   are on paths A6.1 did not name, one of them after an irreversible delete commits. The fix covers all
   of them.

---

## 2. What happened, in order

### 2.1 Run 1 — blocked by Code's tooling, not executed

The Planner's C.0 block contains `Remove-Item Env:PYTHONUTF8`. Code's PowerShell tool refused the whole
command (*"Remove-Item on system path ''\u2713' is blocked"*), a misparse by the tool's permission
checker. Nothing ran.
- **Workaround:** `$env:PYTHONUTF8 = $null`, which is equivalent for a process-scoped variable.
- **Owner's terminal:** the owner's own PowerShell does not have this checker. `Remove-Item Env:` is
  fine there.

### 2.2 Run 2 — measured nothing

Code passed the Python source as `$code = 'print(chr(0x2713) + " ok")'`. **PowerShell 5.1 does not
escape embedded double quotes when it passes an argument to a native program.** Python received
`print(chr(0x2713) +` and raised `SyntaxError` in both the red and green variants. That tests argument
quoting, not encoding.
- ⚠ **Relevance to the sitting:** no runbook argument contains a `"` except the capture line, and that
  line passes through `--%`, which bypasses this parsing (measured earlier, readiness report §3). `$url`
  must not contain a `"`.

### 2.3 Run 3 — ⚠ RED did not fail

This used the Planner's exact source `print('\u2713 ok')`. With `PYTHONUTF8` unset it printed `✓ ok`
and exited 0.

### 2.4 Why — two hosts on the same machine disagree

Measured with `python -c "import sys, locale; print(sys.stdout.encoding, …)"`, piped, `PYTHONUTF8` unset:

| host | `PYTHON*` in env | piped `sys.stdout.encoding` | `utf8_mode` | `locale.getpreferredencoding` |
|---|---|---|---|---|
| Code's **PowerShell** tool | **`PYTHONIOENCODING=utf-8:surrogateescape`** | **utf-8** | 0 | cp1252 |
| Code's **Bash** tool (Git Bash) | none | **cp1252** | 0 | cp1252 |

**Machine code pages** (`HKLM\…\Nls\CodePage`): `ACP=1252`, `OEMCP=437`.

**Independent corroboration, found by accident:** earlier in this sitting-prep, a Code scan running
under the Bash tool **crashed with `UnicodeEncodeError: 'charmap' codec can't encode character '\u26a0'`**
while printing a source line containing `⚠`. That is A6.1's mechanism, in a second host, before C.0 was
understood.

### 2.5 The owner's persistent environment

Checked at User and Machine level:
- `PYTHONIOENCODING`, `PYTHONUTF8` and `PYTHONLEGACYWINDOWSSTDIO`: **all unset**.
- `HKCU\Console` `CodePage`: **unset**.

⇒ A PowerShell window the owner opens starts **without** the injected variable. It is in the failing
state by default.

### 2.6 Run 4 — C.0 with the owner's terminal emulated

The tool's `PYTHONIOENCODING` was cleared and `[Console]::OutputEncoding` restored to cp437 (OEMCP).
Then three variants, each captured with A6.2's form (`& $py -c $code 2>&1 | ForEach-Object { "$_" }`)
and written with A6.3's form (`[IO.File]::WriteAllLines(…, UTF8Encoding($false))`).

**Evidence is read from the captured string's code points and the log file's bytes, NOT from the screen**
(§2.7):

| variant | exit | captured `$out[0]` code points | holds U+2713 | log file first bytes |
|---|---|---|---|---|
| **RED**: no `PYTHONUTF8`, console 437 | **1** | `Traceback (most recent call last):` | no | `54 72 61 63 65 62 61 63 6B…` (the traceback) |
| **PARTIAL**: `PYTHONUTF8=1`, console 437 | 0 | **U+0393 U+00A3 U+00F4** U+0020 U+006F U+006B = `Γ£ô ok` | **no** | `CE 93 C2 A3 C3 B4 20 6F 6B…` |
| **GREEN**: `PYTHONUTF8=1` + console UTF-8 | 0 | **U+2713** U+0020 U+006F U+006B = `✓ ok` | **yes** | **`E2 9C 93 20 6F 6B 0D 0A…`**, no BOM |

**RED's traceback**, as captured:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 0: character maps to <undefined>
[stdout.encoding=cp1252 utf8_mode=0]
```

**Readings:**
- **RED** — the mechanism holds exactly: piped stdout encodes cp1252, strict on unencodable characters.
- **PARTIAL** — ⚠ **the half-fix fails silently.** Python writes correct UTF-8 bytes, PowerShell decodes
  them as cp437, and the log records `Γ£ô ok`. No exit code, no traceback, wrong evidence.
- **GREEN** — correct in memory and on disk. The A6.3 writer emits no BOM.

### 2.7 ⚠ Instrument note — Code's tool cannot show the owner's console

In the same run, the screen showed PARTIAL as `✓ ok` and GREEN as `� ok`, the **inverse** of the
truth. Code's tool reads PowerShell's own output bytes, so a cp437 decode followed by a cp437 re-encode
round-trips back to a visible `✓`.
- **Rule:** display in Code's tool is not evidence here; code points and file bytes are.
- ⚠ **Unmeasured:** what the owner's real console *displays* under GREEN. It does not affect the logs.

---

## 3. `PYTHONUTF8=1` side effects on the Phase D path: none found

`PYTHONUTF8=1` also changes Python's default text encoding for `open()` and subprocess text mode. Over
`scripts/d167_reattach.py`, `scripts/d166_collapse_duplicate_tiles.py`, `scripts/d167_read_state.py`,
`scripts/f078_identity_check.py`, `core/db_identity.py`, `core/db_role.py`, `db/dburl.py` and
`db/migrations/env.py`:

| check | result |
|---|---|
| `open()` / `read_text()` / `write_text()` in text mode without `encoding=` | **none** (AST scan) |
| subprocess in text mode | one: `d167_read_state.py:111` `git` output, ASCII. Unaffected. |
| `alembic.ini` | 5 non-ASCII bytes, valid UTF-8 |
| `db/migrations/versions/0001…0014` | all valid UTF-8 (6–288 non-ASCII bytes each) |

⇒ Under UTF-8 mode alembic reads its config and migrations in their true encoding. Nothing on the path
decodes differently for the worse.

---

## 4. ⚠ A6.1's table is incomplete — every printed non-cp1252 character on the Phase D path

This was a source scan of **printed** lines (`print(`, `say(`, message strings) for characters cp1252
cannot encode, on `main` @ `ee55298`. Docstrings and comments are excluded; they are never printed.

| file:line | char | text | when it prints | in A6.1? |
|---|---|---|---|---|
| `scripts/d167_reattach.py:406` | ⚠ | `⚠ {refusal}` / re-attach proceeds | inside the transaction, role path | yes |
| `scripts/d167_reattach.py:538` | ✓ | `✓ REVERTED` | after a revert commits | yes |
| `scripts/d167_reattach.py:594` | ✓ | `✓ RE-ATTACHED …` | after commit and post-probe | yes |
| `scripts/d166_collapse_duplicate_tiles.py:244` | ⚠ | a duplicate not in F-077 | refusal path | yes |
| `scripts/d166_collapse_duplicate_tiles.py:246` | ✓ | `✓ exactly the three F-077 named` | **dry run and owner run** | yes |
| `scripts/d166_collapse_duplicate_tiles.py:290` | ⚠ | artifact left in place | dry run and owner run | yes |
| `scripts/d166_collapse_duplicate_tiles.py:298` | ⚠ | no artifact deleted | dry run and owner run | yes |
| **`scripts/d166_collapse_duplicate_tiles.py:303`** | ⚠ | `Re-run with --i-am-the-owner … ⚠ OWNER AT THE KEYBOARD` | **the dry run's LAST line** | **NO** |
| **`scripts/d166_collapse_duplicate_tiles.py:328`** | ✓ | `✓ COLLAPSED {n} duplicate rows` | ⚠⚠ **AFTER the delete commits** | **NO** |
| **`scripts/d166_collapse_duplicate_tiles.py:331`** | ⚠ | `If 0014 still refuses …` | after the delete commits | **NO** |
| **`core/db_identity.py:118`** | ⚠ | the *damaged live cluster* refusal message | when that refusal is printed | **NO** |

**Consequences in the RED state:**
- **`:328`** is the collapse's copy of A6.1's line-594 hazard. **An irreversible delete of three rows
  commits and is then reported as a crash.** Unlike the re-attach, there is no `--revert`.
- **`:303`** means the collapse **dry run** would already crash, at its end, if the fix were omitted.
  A6.1 put the earliest crash at `:246`, which runs before it.
- **`db_identity.py:118`** means a refusal would print as a traceback. It still writes nothing, but the
  evidence is a traceback, not the reason.

**All of these are covered by A6.1's environment fix;** §2.6 GREEN is the calibration. No code change on
the sitting day (A6.1). Making printed output ASCII is a close-out item.

**The witness path (step 1) prints only `§`** (`core/db_role.format_preamble`). That is cp1252-encodable,
so step 1 alone would **not** have crashed in RED. Under PARTIAL it would have been logged as mojibake.

---

## 5. Proposals for the Planner

1. **Add a one-line environment calibration at step 0, in the owner's real terminal, after the two fix
   lines and before the tunnel.** This measures the environment the sitting actually runs in, not
   Code's emulation of it:

   ```powershell
   $env:PYTHONUTF8 = "1"; [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
   $c0 = & $py -c "import sys; print(sys.stdout.encoding, sys.flags.utf8_mode, '\u2713')" 2>&1 | ForEach-Object { "$_" }; "exit: $LASTEXITCODE"
   [int][char]($c0.Trim())[-1]      # expect 10003 (U+2713); anything else stops step 0
   ```

   **Expected:** `exit: 0`, and `utf-8 1 ✓` captured, with the last character's code point `10003`.
   ⚠ It uses no embedded double quotes (§2.2).

   **The probe is itself calibrated** (`D-162` rule 7). Code ran it verbatim in the emulated owner
   terminal (§2.6's environment), in all three states:

   | state | exit | probe reads | verdict |
   |---|---|---|---|
   | no fix (no `PYTHONUTF8`, console 437) | **1** | the expression cannot evaluate (`Cannot convert value "cp1252 0" to type "System.Char"`) | stops: exit ≠ 0 |
   | half fix (`PYTHONUTF8=1` only) | 0 | **`244`** (U+00F4, the mojibake `ô`) | stops: ≠ 10003 |
   | full fix (both lines) | 0 | **`10003`**; captured head `utf-8 1` | proceed |

   ⚠ The half-fix row matters most: exit 0 and no traceback, so only the code-point check catches it.
2. **Accept §4's four additional lines** into the close-out's "make printed output ASCII" item, and name
   `d166_collapse_duplicate_tiles.py:328` as the most severe (after an irreversible commit).
3. **Record the instrument finding:** Code's PowerShell tool injects `PYTHONIOENCODING`, and its screen
   cannot show the owner's console. Any future encoding calibration by Code must clear that variable and
   read code points or bytes.

---

## 6. Error accounting — Code, this step

1. **Run 2 tested quoting instead of encoding.** Code chose a Python string containing `"` without
   checking PS 5.1's native-argument handling. Caught by the `SyntaxError`, and no conclusion was drawn
   from it.
2. **Run 3's "RED passed" was a result about Code's tool, not the owner's terminal.** It came one step
   from being reported as *"the mechanism is wrong"*. What stopped that: it contradicted Code's own
   earlier Bash-host crash, and the difference was measured before anything was concluded.
   - **Lesson:** a calibration is only about the environment it ran in; state that environment.
3. **The first scan crashed on its own output** (§2.4), the same mechanism. Re-run with
   `PYTHONUTF8=1` and `ascii()` output.

**Owner still owes before step 0** (unchanged from A6):
- no enqueue running
- the model was not changed this session
- the tunnel bound by name, with its Direct IP vs `fly mpg status` pasted
