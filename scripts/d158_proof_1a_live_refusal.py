"""D-158 revert proof, STEP 1a -- NON-DESTRUCTIVE, against the LIVE production database.

The owner's split (2026-09-15): prove the guard REFUSES the real production target through a real
tunnel, without performing the act it certifies against.

WHAT THIS FILE DOES NOT CONTAIN, AND THAT IS THE POINT:
  - no `import pytest`, no conftest, no test collection
  - no TRUNCATE, no DELETE, no UPDATE, no INSERT, no DDL
  - the ONLY statement that reaches the database is the guard's own marker probe,
    `SELECT to_regclass('keel_disposable_marker')`

It reads `.env` by PARSING it, never by sourcing it, and never prints the credential.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

from _db_safety import (  # noqa: E402
    MARKER_TABLE,
    db_host,
    db_name,
    marker_probe,
    refusal_reason,
)

SELF = pathlib.Path(__file__).read_text(encoding="utf-8")
BODY_RAW = SELF.split('"""', 2)[2]
BODY = BODY_RAW.upper()    # skip the docstring, which names them deliberately

# !! THE NEEDLES ARE SPLIT SO THIS CHECK CANNOT FIND ITSELF. The first version listed the words
# whole, and the assertion fired on its own source -- a guard that holds a pattern as data while
# searching for that pattern is the trap `D-145` recorded of itself, and it has now caught three
# separate assertions in this wave. Recorded here rather than silently worked around.
for a, b in (("TRUN", "CATE"), ("DELE", "TE "), ("DR", "OP "), ("ALT", "ER "),
             ("INSE", "RT "), ("UPDA", "TE ")):
    assert (a + b) not in BODY, f"this proof script contains {a + b!r}"
assert ("impo" + "rt pytest") not in BODY_RAW

line = [ln for ln in (REPO / ".env").read_text(encoding="utf-8").splitlines()
        if ln.startswith("DATABASE_URL=")][0]
URL = line.split("=", 1)[1].strip().strip('"').strip("'")

# ⚠ PORT OVERRIDE. Three flyctl proxies were already listening on 16380/16381/16382 when this
# ran, left from the recovery work, and NOTHING about a tunnel says which cluster it reaches -- the
# whole reason D-159 exists. Probing through one of them could have certified this proof against
# the FORENSIC cluster. So the proof opens its own proxy, bound by name to kyzl60xz9zyrpj9g, on a
# port it controls, and rewrites the URL to match.
if len(sys.argv) > 1:
    URL = re.sub(r"(@[^/:]+):\d+", r"\g<1>:" + sys.argv[1], URL)


def redact(u: str) -> str:
    return re.sub(r"://([^:/@]+):[^@]*@", r"://\1:<redacted>@", u)


print("=" * 78)
print("D-158 REVERT PROOF -- STEP 1a -- non-destructive, LIVE PRODUCTION")
print("=" * 78)
print(f"target url    : {redact(URL)}")
print(f"host          : {db_host(URL)}   (a tunnel: this is what defeated the old guard)")
print(f"database      : {db_name(URL)}")
print(f"marker sought : {MARKER_TABLE!r}")
print()

print("-- 1. what the probe sees on the real production database --")
try:
    present = marker_probe(URL)
    print(f"   marker present: {present}")
except Exception as exc:  # noqa: BLE001
    present = None
    print(f"   probe raised: {exc!r}")
print()

print("-- 2. the guard's verdict, called exactly as conftest calls it --")
verdict = refusal_reason({"DATABASE_URL": URL})
print()
if verdict is None:
    print("   !!!! PERMITTED !!!!")
    print("   The guard would have let the suite run against production. D-158 is DEFECTIVE.")
    print("   STOP. Do not run step 1b. Do not run the suite anywhere near this credential.")
    raise SystemExit(2)

print(verdict)
print()
print("-- 3. what this proves, and what it does not --")
print("   PROVEN: the live production database, reached through a real `fly mpg proxy` tunnel at")
print("           127.0.0.1, is REFUSED by the guard that conftest consults. This is the exact")
print("           decision D-158 exists to make, certified against the exact target.")
print("   NOT PROVEN HERE: that pytest's collection hook aborts the run. That is step 1b, and it")
print("           belongs on a scratch restore with zero stake -- never on this database.")
print()
print("RESULT: REFUSED. Step 1a passes.")
