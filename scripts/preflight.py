#!/usr/bin/env python3
"""Session preflight: the facts a session must not get wrong, measured in seconds.

    python scripts/preflight.py            # human
    python scripts/preflight.py --json     # machine

⚠⚠ WHY THIS EXISTS. On 2026-09-03 three session documents were simultaneously wrong about the same
landed commit, a deleted file, and a PR title — all checkable in under a minute. A closeout said
"nothing shipped" ninety minutes before two PRs landed. On 2026-09-04 a pointer that had been
corrected hours earlier was stale again, and nothing noticed.

⚠ **This prints facts, not opinions. It rules nothing and authorises nothing.**

⚠ **It is for EVERY team working in this repository, not one.** You can audit what another team
committed; you cannot audit their context. A shared prompt cannot be verified — this can, because
it reads the tree and says which ref it read.

⚠ **Exit code is 0 when the tree is measurable, 1 when a stated invariant is broken.** ⚠ A
non-zero exit is not permission to stop; it is a fact to carry into the session.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HEADING = re.compile(r"^#{2,4}[^A-Za-z0-9\n]*([A-Z]{1,4})-(\d+)\b", re.M)
REGISTERS = ("docs/README.md", "docs/Test_Plan.md", "docs/PAPERS-v2.md")
RESERVED = "docs/RESERVED.md"

#: ⚠ Namespaces that are NOT spend-once identifiers. Narrow, stated, justified.
EXEMPT = {"A": "a convention for numbers that MOVE (docs/RESERVED.md), not spend-once identifiers"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def read(rel: str) -> str:
    p = REPO / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def facts() -> dict:
    subprocess.run(["git", "fetch", "origin", "--quiet"], cwd=REPO, capture_output=True)
    head, main = git("rev-parse", "HEAD"), git("rev-parse", "origin/main")
    tracked = [l for l in git("status", "--porcelain", "--untracked-files=no").splitlines() if l]
    untracked = [l[3:] for l in git("status", "--porcelain").splitlines() if l.startswith("??")]

    # ⚠ Untracked .py under scanned source dirs: the 2026-09-04 cross-team hazard.
    src = tuple(f"{d}/" for d in ("app", "core", "db", "worker", "scripts", "tests"))
    untracked_src = [u for u in untracked if u.endswith(".py") and u.startswith(src)]

    spent: dict[str, set[int]] = {}
    for rel in REGISTERS:
        for ns, n in HEADING.findall(read(rel)):
            spent.setdefault(ns, set()).add(int(n))
    reserved = read(RESERVED)

    ns_rows, broken = [], []
    for ns, ints in sorted(spent.items()):
        hi = max(ints)
        m = re.search(rf"Next free `{ns}-` integer: `{ns}-(\d+)`", reserved)
        if ns in EXEMPT:
            ns_rows.append({"ns": ns, "highest": hi, "pointer": None, "state": "exempt"})
            continue
        if not m:
            ns_rows.append({"ns": ns, "highest": hi, "pointer": None, "state": "UNREGISTERED"})
            broken.append(f"{ns}-: {len(ints)} entries, no next-free pointer")
            continue
        ptr = int(m.group(1))
        if ptr in ints:
            state = "VIOLATED (names a spent entry)"
            broken.append(f"{ns}-: pointer {ns}-{ptr:03d} is already written")
        elif ptr <= hi:
            state = "VIOLATED (at or below highest spent)"
            broken.append(f"{ns}-: pointer {ns}-{ptr:03d} <= highest {ns}-{hi:03d}")
        else:
            state = "ok"
        ns_rows.append({"ns": ns, "highest": hi, "pointer": ptr, "state": state})

    return {
        "ref": {"head": head, "origin_main": main, "in_sync": head == main,
                "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "behind": git("rev-list", "--count", "HEAD..origin/main") or "0"},
        "tree": {"tracked_modifications": len(tracked),
                 "untracked": len(untracked),
                 "untracked_sources": untracked_src},
        "namespaces": ns_rows,
        "broken": broken,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    f = facts()
    if ap.parse_args().json:
        print(json.dumps(f, indent=2))
        return 1 if f["broken"] else 0

    r, t = f["ref"], f["tree"]
    print("PREFLIGHT — every figure below is measured from this tree, now")
    print(f"\n  branch          {r['branch']}")
    print(f"  HEAD            {r['head'][:7]}")
    print(f"  origin/main     {r['origin_main'][:7]}"
          + ("  (in sync)" if r["in_sync"] else f"  ⚠ HEAD is {r['behind']} behind"))
    print(f"\n  tracked mods    {t['tracked_modifications']}")
    print(f"  untracked       {t['untracked']}")
    if t["untracked_sources"]:
        print(f"  ⚠ untracked .py under scanned source dirs: {len(t['untracked_sources'])}")
        for u in t["untracked_sources"][:6]:
            print(f"      {u}")
        print("    ⚠ Another team's working state. Guards read `git ls-files`, so these are not"
              "\n      scanned — but they ARE collected by pytest and change local counts.")

    print("\n  NUMBERING")
    for n in f["namespaces"]:
        p = f"{n['ns']}-{n['pointer']:03d}" if n["pointer"] else "—"
        mark = "  " if n["state"] in ("ok", "exempt") else "⚠ "
        print(f"    {mark}{n['ns']:<4} highest {n['ns']}-{n['highest']:03d}   next free {p:<8} {n['state']}")

    if f["broken"]:
        print(f"\n  ⚠⚠ {len(f['broken'])} INVARIANT BREACH(ES):")
        for b in f["broken"]:
            print(f"      - {b}")
        print("\n  ⚠ Carry these into the session. Do not fix a register without an order.")
        return 1
    print("\n  ✅ every registered namespace is invariant-shaped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
