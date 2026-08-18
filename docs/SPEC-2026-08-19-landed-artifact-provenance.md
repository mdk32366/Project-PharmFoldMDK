# SPEC — 2026-08-19 — provenance index for artifacts landed BYTE-FOR-BYTE

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority.
>
> ⚠⚠ **THIS INDEX EXISTS BECAUSE THE LANDING HEADER AND THE AUTHORED HASH ARE NOW IN CONFLICT.**
> The four artifacts below were delivered **as files** and are committed **unmodified**. **Adding a
> landing header to any of them would change its bytes and break the very hash that makes it
> verifiable.** So the header moved out of the artifact and into this index — the artifact stays
> byte-identical to what the author hashed, and the provenance is recorded beside it rather than
> inside it.
>
> ⚠ **The four are not covered by `tests/test_docs_landing_headers.py`** — none carries a date in its
> filename, so the convention does not reach them. **Stated rather than discovered: they are outside
> that check by construction, and this index is what covers them instead.**

---

## §1 — ⚠⚠ THE FIRST DELIVERY WHERE THE AUTHORED HASH ACTUALLY VERIFIED SOMETHING

`F-047` member 3's remedy — *the author hashes their own bytes* — failed **twice** in a row, both
times because the artifact reached Code as **chat text** and Code could only hash its own retyping.
`ORDERS-Code-clinical-surface-today.md` §8 diagnosed it correctly: **paste and provenance are two
channels**, and collapsing them makes byte-identity unreachable, so the hash can never match.

**2026-08-19, file channel, four artifacts: FOUR OF FOUR MATCH, on both hash and byte count.**

| artifact | declared range | authored `sha256` | bytes | verdict |
|---|---|---|---|---|
| `D-093-amendment-2-paste-ready.md` | first `####` → EOF | `a594115421ee8bb3be704dabd2c4dde5b4d4b66afbc383e79a401d8d55637a71` | 9,527 | ✅ **MATCH** |
| `ORDERS-Code-step-4-schema-ingest-surface.md` | first `## §` → EOF | `528ede3a4f44fb5695b01f78b96c8e66f2a659fd54c031ef3b7cb26206ff994f` | 8,476 | ✅ **MATCH** |
| `ORDERS-Code-clinical-surface-today.md` | first `## §` → EOF | `667f44bdba924768268e92a2e09f5e3c6ad98dfffa29163b16fcc2df8e4d0e43` | 9,678 | ✅ **MATCH** |
| `ORDERS-Code-cancer-surface-attribution.md` | first `## §` → EOF | `3224e774fad6ca3b4d50f22a533697ab728ab8ec090bb2c940e9457d1a722cb7` | 6,228 | ✅ **MATCH** |

⚠ **The fourth carries its hash INSIDE the file**, above a range that excludes the line carrying it —
`F-047` member 12's fix, and it works: **a hash cannot live inside the bytes it covers**, and putting
it above the range is what makes that possible.

⚠⚠ **What this proves and what it does not.** It proves the bytes Code committed are the bytes the
author hashed. **It does not prove the author hashed what they meant to write** — no hash can. *The
channel is now verifiable; the authorship still is not, and that distinction is the whole content of
the remedy.*

## §2 — ⚠ One artifact named in these orders was NOT delivered

`ORDERS-Code-cancer-surface-attribution.md` §0 states that the HPA licence text *"is landing as
`docs/HPA-licence-2026-08-19-as-read.md`"*.

⚠⚠ **That file is not in `Downloads` and is not in the repository.** `EA`'s evidence — *the required
attribution string, read verbatim, with the URL and the date read* — **is therefore asserted by the
order and not present.** **A document that says another document is landing is not that document
landing**, and this is recorded rather than assumed satisfied.

**Consequence, stated plainly:** the licence-identity conflict the order describes — the page reading
*Attribution-ShareAlike 3.0 International* against amendment 1 clause 1's *CC BY 4.0*, with
*"3.0 International"* not being a licence that exists — **cannot be verified from this repository.**
It rests entirely on the order's own account. ⚠ **The owner holds it, and an email to HPA is named as
the resolution instrument.**

## §3 — How to re-verify any row above

```bash
python - <<'PY'
import hashlib, pathlib, re
SPEC = [("docs/D-093-amendment-2-paste-ready.md", r"^####"),
        ("docs/ORDERS-Code-step-4-schema-ingest-surface.md", r"^## §"),
        ("docs/ORDERS-Code-clinical-surface-today.md", r"^## §"),
        ("docs/ORDERS-Code-cancer-surface-attribution.md", r"^## §")]
for name, pat in SPEC:
    t = pathlib.Path(name).read_text(encoding="utf-8")
    m = re.search(pat, t, re.M)
    body = t[m.start():].encode("utf-8")
    print(f"{name}\n  {len(body):,} bytes  {hashlib.sha256(body).hexdigest()}")
PY
```

⚠ **Read the output, not the exit code.**
