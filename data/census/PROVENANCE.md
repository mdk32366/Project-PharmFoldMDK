# Census data provenance

> Task A of `docs/ORDERS-Code-2026-08-04-b-scale-readiness.md`. **Every count that reaches a surface,
> a deck, or the paper is read off a file named here, on a date named here.**

---

## ⚠ `table_S3_surfaceome.xlsx` — NOT OBTAINED. The authoritative source serves a pointer, not the table.

**Status: BLOCKED. Task A is not complete and no count has been read off the membraneome table.**

### What was attempted, in order (2026-08-04)

| # | Action | Result |
|---|---|---|
| 1 | `GET https://wlab.ethz.ch/surfaceome/table_S3_surfaceome.xlsx` (the URL the order names) | **HTTP 301** → `https://wollscheidlab.org/SURFY`. The lab has moved domains; the order's URL is stale. Following it with `-L` yielded **74,159 bytes of HTML** (the SURFY landing page), sha256 `eea3cd8a…`. |
| 2 | Resolved the download link from that page | Relative href `table_S3_surfaceome.xlsx`, i.e. `https://wollscheidlab.org/SURFY/table_S3_surfaceome.xlsx` |
| 3 | `GET https://wollscheidlab.org/SURFY/table_S3_surfaceome.xlsx` | **HTTP 200, 132 bytes**, sha256 `f3df0fa89f4a6b16b7fb6afa95732e0b7a3391579c1864c2d180f02a13aafc80` — a **Git LFS pointer stub**, not a spreadsheet (magic bytes `vers`, not `PK`). |

### ⚠ The finding: this was never a broken download

The 132 bytes served by the lab's own site are **byte-identical** to the copy in the owner's
`Downloads` folder. Confirmed by hash, both `f3df0fa8…`.

```
version https://git-lfs.github.com/spec/v1
oid sha256:2f1b8262463ce1c59a1f945d22f0e9638cb3bfbf5aabe197f43b562a62fb055a
size 6864772
```

**So the order's premise is wrong in a way worth recording.** It says *"the pointer came from a
mirror"* and instructs a re-fetch from *"the direct source."* **The direct source is the pointer.**
The site appears to have been deployed from a git repository without resolving its LFS objects, so
the 6,864,772-byte spreadsheet is **not retrievable from the documented source at all** — not by
re-downloading, not by a different client, not by trying harder.

**And a second-order point about the expected hash.** `2f1b8262…` — the value Task A instructs us to
verify against — **is itself read out of this pointer.** It is a trustworthy statement of what the
content hash *should* be (that is what an LFS oid is), but it is not independent confirmation that
anyone has ever held the real file. **Nobody in this project has verified the actual bytes, because
nobody in this project has had the actual bytes.**

### What this blocks, and what it does not

- ❌ **Blocked:** Task A §1.4 — "read every count off the file." Row count, per-cutoff counts, and the
  positive/negative split **cannot be read**, and none is recorded here.
- ❌ **Blocked:** F-011's magnitudes. **2,216** (negative class) and **~5,102** (total scored) remain
  *unverified* and *Planner arithmetic from a figure legend* respectively, exactly as F-011 v2 labels
  them. The negative class — the subject of that finding — **has still never been counted.**
- ✅ **Not blocked:** Task B. Its input is `surfaceome_ids.txt`, which is present and verified below.
  The mapping does not depend on the spreadsheet.

### Routes not taken, named so the next attempt does not repeat them

Per the order (*"a mismatch is stop-and-report, not a retry"*) the following were **not** attempted
and are the live options for whoever unblocks this:

1. **LFS batch API** — requires the origin repository URL, which the pointer does not carry.
2. **PNAS supplementary material** — Bausch-Fluck et al. 2018 published Table S3 with the paper; the
   journal's copy is a different artifact and **would need its own hash recorded**, since it may not
   match `2f1b8262…`. If it differs, that is a fact to record, not a failure to reconcile away.
3. **Contact the lab.** The deployment defect is theirs and is presumably unintentional.

**⚠ If a copy is obtained from anywhere other than the declared oid, it is a DIFFERENT artifact until
proven otherwise.** Record its hash, its source, and whether it matches `2f1b8262…`. Do not assume a
file with the right filename is the right file — a filename is not an identity.

### Retained evidence

`table_S3_surfaceome.xlsx.LFS-POINTER-NOT-THE-TABLE` — the 132-byte stub, kept under a name that
states what it is. **Deliberately not named `.xlsx`**: a file named for data it does not contain is
the trap this whole entry is about.

---

## ✅ `surfaceome_ids.txt` — present, counted, not inherited

- **Source:** supplied by the owner, 2026-08-04, in `Downloads`. Upstream origin not independently
  established.
- **sha256:** `8a7b7e68fc893163f100cdd761f3bef3d2cb8ece752f79cef3cbacd166062954` (33,783 bytes), recorded 2026-08-04. A copy is staged at `data/census/surfaceome_ids.txt`.
- **Counted, not cited (D-016):** **2,886 non-empty lines, 2,886 unique.** This confirms F-011 v2's
  single verified figure by re-counting rather than accepting it.
- **Identifier form — the mismatch is TOTAL, not partial:** **0 of 2,886 are accession-shaped**;
  **2,886 of 2,886** end `_HUMAN`. First three `1A01_HUMAN`, `1A02_HUMAN`, `1A03_HUMAN`.
- **Consequence:** every join in this project is keyed by accession, so the mapping step (Task B) is a
  **hard prerequisite, not a fallback or a cleanup pass.** Until it runs the census has 2,886
  identifiers and **0 joinable rows.** A "try accession, else map" code path would succeed on
  nothing — which is why `scripts/census_spans.py` refuses on missing input rather than improvising.

---

## ⟡ `membraneome-reconstructed-2026-08-04` — the table, reconstructed because the source is still unobtainable

**Status: RECONSTRUCTION. Not the upstream artifact, and named so it cannot be mistaken for it.**
See `### F-016` in `docs/README.md`.

- **Origin:** a scrape of the table published at `wollscheidlab.org/SURFY`, supplied by the owner in
  `Downloads` 2026-08-04, then rebuilt and UniProt-annotated.
- **⚠ The stub above was re-verified the same day.** Both copies in `Downloads` hash to
  `f3df0fa8…` with magic bytes `vers`, not `PK`. **The upstream table is still not obtained**, so
  this reconstruction is a substitute for it and is never a substitute for its identity.

| File | Role | sha256 |
|---|---|---|
| `membraneome-reconstructed-2026-08-04.csv` | ✅ **source of record** — 7,903 rows, diffable, greppable. **Tests read this.** | `5a705cc9165eb863f51116c31f2a5f56080bf8941bf994a612f9d85fc6944d37` |
| `membraneome-reconstructed-2026-08-04.xlsx` | **derived** from the CSV by `scripts/build_membraneome_xlsx.py`; human-readable, carries a `PROVENANCE` sheet | `28bf04132f626154a451d46127c1b1f00bbe39a02c45c77015f264f5033c14a2` |

⚠ **Parent and child, not siblings.** The two files first existed side by side, built independently
from the same scrape — **two paths to one quantity, with nothing comparing them**, which is this
project's signature defect class and would have drifted the first time either was regenerated. The
workbook is now *derived*, there is exactly one derivation, and
`tests/test_membraneome_artifacts.py` reddens on row-count, header, or derived-column disagreement.
**Do not hand-edit the workbook: edit the CSV and rebuild.**

⟡ **Provenance is bound, not adjacent.** The workbook records the sha256 of the CSV it was actually
built from, and `scripts/census_spans.py` records the sha256 of whatever it actually read. A
filename is not an identity — the same principle as the retained stub above.

- **Counted, not cited:** 7,903 rows — `surface` 2,886 · `non_surface` 2,216 · `unclassified` 2,801.
- **⚠ The denominator is 2,807, not 2,886.** Keyed by accession, 79 surface identifiers collapse
  into four HLA loci UniProt has merged. Identifiers are not proteins.
- **Corroborated:** 2,886 and 2,216 match the figures published on the SURFY site exactly, and the
  2,886 surface entry names are set-identical to `surfaceome_ids.txt` above.
- **⚠ Not corroborated:** 7,903 and the 2,801 unclassified rows. The site publishes no total, and
  the per-cell values of the non-surface rows cannot be checked against a source never served.
- **If the upstream `.xlsx` is ever obtained, it supersedes this without argument.**
