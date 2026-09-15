# D-167 Phase D — the sitting's console logs (`ORDERS` A4.8, A5 stop rules)

Each step's FULL console output, pasted by the owner into its own file, committed on this branch.
Not chat, not upload: the Planner fetches the same bytes (KEEL Principles 8-9).

| file | step (Amendment 5 runbook) | expectation |
|---|---|---|
| `00-tunnel-open.txt` | tunnel bound by name; `fly mpg status` | Direct IP matches; URL uses `127.0.0.1` |
| `01-witness-before.txt` | `d167_reattach.py --witness` | `witness: 480` (A5.2) |
| `02-capture.txt` | printed capture line (with `--%`), `sftp get` | last line a sha256; `capture.json` transferred |
| `03-reattach-dry.txt` | re-attach dry run | exit 0, `DRY RUN - nothing was written` |
| `04-reattach-owner.txt` | re-attach `--i-am-the-owner` | exit 0; exit 3 = REPORT before any revert (A5.5) |
| `05-witness-after.txt` | `--witness` | `witness: 517` |
| `06-collapse-dry.txt` | collapse dry run | exit 0; WAITS if the role cannot build `0014` (A4.2) |
| `07-collapse-owner.txt` | collapse `--i-am-the-owner` | `COLLAPSED 3` |
| `08-alembic.txt` | `$env:DATABASE_URL` set → upgrade → current → `Remove-Item` | `0014_enqueue_identity_unique` |
| `09-tunnel-closed.txt` | tunnel closed | stated |

`data/control/d167/capture.json` is committed beside this directory (Phase E.3).

⚠ Stop rules: any `REFUSING`, any exit ≠ 0, or any expectation not met stops the sitting at that line.
Steps 3 and 4 are independent; a stop in 4 does not undo 3. Python: `.\.venv\Scripts\python.exe`.
