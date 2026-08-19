# SPEC — 2026-08-19 — the HPA v22 deep-link pattern, DERIVED FROM THE SITE

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority.
>
> ⚠ **`EG1`. Nothing here renders anything** — the surface is blocked on `ED`, which needs a
> production write and the owner at the keyboard.

---

## §1 — ⚠ The pattern was DERIVED, not constructed

`EG1` is explicit that inferring the URL shape from recollection is barred: *"a deep link that 404s
discharges nothing, and one that silently resolves to the CURRENT release while sitting beside v22
data is worse — it looks right and cites a source that is not the source."*

**Method: ask the site.** `https://v22.proteinatlas.org/ENSG00000115850` redirects **once, on the
same host**, to its canonical form, and the page's own `href`s then enumerate every view:

```
canonical   https://v22.proteinatlas.org/<ENSG>-<GENE NAME>
views       /pathology   /tissue   /subcellular   /structure   /brain   /blood+protein
            /cell+line   /immune+cell   /metabolic   /single+cell+type   /tissue+cell+type
            /summary/rna   /summary/sections
```

**EG1d — the two edges take two different tabs, and the base is identical:**

| edge | supplier | deep link |
|---|---|---|
| 1 — protein → tumour | `pathology.tsv` | `https://v22.proteinatlas.org/<ENSG>-<GENE>/pathology` |
| 2 — protein → normal tissue | `normal_tissue.tsv` | `https://v22.proteinatlas.org/<ENSG>-<GENE>/tissue` |

## §2 — ⚠⚠ EG1c: the `v22` host does NOT redirect to the current release

```
https://v22.proteinatlas.org/                   http=200  redirects=0
https://v22.proteinatlas.org/ENSG00000115850    http=200  redirects=1
   -> https://v22.proteinatlas.org/ENSG00000115850-LCT      ⚠ same host, canonicalisation only
```

**So decision 6 question 4's stability answer holds** — *the version is in the host name* — and the
`STOP AND REPORT` branch does not fire. ⚠ **This was checked FIRST**, before any link was verified,
because a redirect to the current release would have refuted the stability answer and made every
verified link meaningless.

## §3 — EG1b: verified on real census genes, and on a negative case

| accession | gene | view | result |
|---|---|---|---|
| `P51677` | CCR3 | `/pathology` | **http 200** |
| `P05362` | ICAM1 | `/tissue` | **http 200** |
| `Q96LB2` | MRGPRX1 | `/pathology` | **http 200** |
| ⚠ negative — a constructed ENSG that does not exist | `ENSG00000000000-NOTAGENE` | `/tissue` | **http 404** |
| ⚠⚠ negative — a real `hpa_absent` census row | `Q8NGY7` / OR10J6P | — | **no ENSG exists, so no link can be constructed at all** |

**A bar with no negative case cannot fail.** Two are recorded, and they fail differently: **a wrong
gene 404s; an unmapped protein has no URL to be wrong.**

⚠ **`Q8NGY7` is `EG4`'s first category made concrete** — no HPA datum renders, so **no citation is
owed and no orphan citation block may be emitted.**

## §4 — ⚠ A measurement artifact, recorded because it looked like a finding and was not

Six deep links returned `http=000` — **no response at all** — when issued in a tight loop, while the
same URLs returned `200` when issued singly moments later. ⚠⚠ **`000` is not `404`.** It is the
absence of an HTTP response, and reading it as *"the link does not resolve"* would have been the
`405`-read-as-`404` shape a third time this week.

**Cause: request rate from this machine, not anything about HPA or the pattern.** Recorded so a
later reader does not re-derive it as a site defect — and **any implementation that verifies links
in bulk must pace itself**, or it will manufacture exactly this false negative at scale.
