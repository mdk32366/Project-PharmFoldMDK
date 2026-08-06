# SPEC — 2026-08-06 — The landing-header matcher, stated literally

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

> ⚠ **This is a file because the chat channel ate this content three times.** It is the literal
> matcher `tests/test_docs_landing_headers.py` applies. **The test is authoritative; this describes
> it.** If they ever differ, the test governs and this file is wrong.

---

## §1 — The marker, post-normalisation

```
LANDING_MARKER = "THE LOG GOVERNS"
```

⚠ **Matched only AFTER normalisation, never against raw text.** A fixed-string grep for this phrase
once returned **11 where 12 was correct**, because `D-079-census-ingest-tranches-and-recipe-v2.md`
wraps it as `THE LOG\n> GOVERNS`. **It under-reported in the direction that looks safe.**

## §2 — Normalisation. The order of the two steps is the whole thing.

```python
def normalise(text: str) -> str:
    unquoted = [re.sub(r"^\s*>\s?", "", line) for line in text.splitlines()]
    return re.sub(r"\s+", " ", " ".join(unquoted)).strip()
```

⚠ **Strip the leading `> ` PER LINE first, then collapse whitespace.** Reversing the two yields
`THE LOG > GOVERNS` — which still does not match, while looking normalised.

## §3 — Which files are checked

```python
ARTEFACT_PREFIX = re.compile(
    r"^(RULING|RULINGS|ORDERS|CORRECTION|AMENDMENT|SPEC|AUTHORISATION|META-ORDER)")
DATE_IN_NAME        = re.compile(r"2026-(\d{2})-(\d{2})")
CONVENTION_FLOOR    = "2026-08-05"
HEADER_WINDOW_LINES = 12
```

A `docs/*.md` file is **in the set** iff its name matches `ARTEFACT_PREFIX`, contains `2026-NN-NN`,
and that date is `>= CONVENTION_FLOOR`. It **passes** iff `LANDING_MARKER` appears in
`normalise(first 12 lines)`.

**The floor is not arbitrary** — the convention was created by
`RULING-2026-08-05-D-079-denominators-in-the-log.md` §3 and was never retroactive. Without it the
check matches 44 files back to 2026-07-26 and fails on 23.

## §4 — Deliberately outside the set

- **`CLOSEOUT-*` and `PREWORK-*`** — absent from the prefix list **by ruling**: they carry a
  session-record header, not a landing header. **Do not widen the pattern to catch them.**
- **`D-079-census-ingest-tranches-and-recipe-v2.md`** — matches neither the prefix nor the
  date-in-filename requirement, yet is compliant. ⚠ **An asserted known gap**, pinned by three
  assertions in the test so a rename into coverage, a date-convention change, or a lost header each
  reds.
- **`RESULT-*`** — also outside the prefix list. A second uncovered file; reported, not silently
  widened, because widening the convention is a ruling.

## §5 — The header text in use

```
> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.
```

Placed immediately after the `# ` title, separated by one blank line — well inside the 12-line
window. ⚠ **Only `THE LOG GOVERNS` is load-bearing**; the rest is prose the matcher does not read.
