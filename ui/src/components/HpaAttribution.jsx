import { createContext, useContext, useEffect, useId, useMemo, useState } from 'react'

// HPA attribution — the four elements, on every surface that renders an HPA-derived value.
//
// ⚠⚠ THE LICENCE WORDS THIS AS A PRECONDITION, NOT A FOOTNOTE: "be sure that our content is never
// displayed in the absence of such citation." That is D-094's shape, written by HPA. So this is a
// MOUNT PRECONDITION — if an HPA value renders and this does not, the surface is out of compliance,
// and a test reds.
//
// ⚠⚠ AND "HPA-DERIVED" IS ABOUT THE SOURCE, NOT THE ROUTE. CancerAssociations reads Kathad's S3,
// and D-100 established S3 is a VERBATIM EXTRACT of pathology.tsv — 1,640/1,640 rows. Citing the
// paper is not citing HPA.
//
// ⚠ The primary publication is the IHC paper. NOT the 2017 transcriptome paper, despite its title
// matching our filename. A filename is not a modality.
//
// ── ⚠⚠ SPLIT BY CASE (owner ruling, 2026-08-21), because ONE BLOCK RENDERED FOUR TIMES ───────────
// Measured on 100 census cards: **79 of 100 rendered FOUR attribution blocks**, 21 rendered none.
// There is no middle case — LAMP1 was not special, it was the 79% case. All four read identically.
//
// ⚠ But they were NOT identical underneath: the four payloads differ in exactly one field,
// `deep_link`, and **75 of the 79 carry THREE DISTINCT deep links**. So "keep the first and drop the
// rest" would silently discard two working per-datum links — and element 4 is the one the licence
// describes per-datum. The split is therefore by CASE, not by de-duplication:
//
//   • elements 1+2+3 (publication · website · image/data credit) are properties of THE SOURCE.
//     They render ONCE per page, from `HpaCreditProvider`.
//   • element 4 (the deep link) is a property of THE DATUM. It renders WITH the value it cites.
//
// ⚠⚠ AND THE PRECONDITION IS PRESERVED BY CONSTRUCTION: the credit renders if and only if at least
// one datum registered. A page cannot show an HPA value without the citation, and cannot show the
// citation attached to nothing.

const HpaCreditContext = createContext(null)

// ⚠ Page-level: the three elements that describe the SOURCE rather than any one datum.
export function HpaCredit({ attribution }) {
  if (!attribution) return null
  const { primary_publication: pub, website, data_credit } = attribution
  return (
    <div className="hpa-attrib hpa-attrib-page" data-hpa-attribution="source">
      <p className="hpa-attrib-cite">
        {/* ⚠ ELEMENT 1 — primary publication */}
        <span className="hpa-attrib-pub">
          {pub.citation}. DOI{' '}
          <a href={pub.url} rel="noopener noreferrer" target="_blank">{pub.doi}</a>
        </span>
        {' · '}
        {/* ⚠ ELEMENT 2 — website reference */}
        <span className="hpa-attrib-site">
          <a href={website.url} rel="noopener noreferrer" target="_blank">{website.name}</a>
        </span>
      </p>

      {/* ⚠⚠ ELEMENT 3 — THE IMAGE/DATA CREDIT, AS ITS OWN ELEMENT. It is deliberately NOT element 2
          doing double duty: the licence asks for a credit, and a hyperlink to a site is not one. */}
      <p className="hpa-attrib-credit">
        <span className="hpa-attrib-credit-label">Image/data credit:</span> {data_credit}
      </p>
    </div>
  )
}

// ⚠⚠ Wrap a PAGE. Blocks that render an HPA value register through `HpaDeepLink`; the source-level
// credit is emitted once, at the foot, and only if something registered.
export function HpaCreditProvider({ children }) {
  const [sources, setSources] = useState({})
  const api = useMemo(() => ({
    register(key, attribution) {
      setSources((s) => (s[key] ? s : { ...s, [key]: attribution }))
    },
    unregister(key) {
      setSources((s) => {
        if (!(key in s)) return s
        const next = { ...s }
        delete next[key]
        return next
      })
    },
  }), [])
  const registered = Object.values(sources)
  return (
    <HpaCreditContext.Provider value={api}>
      {children}
      {/* ⚠ IF AND ONLY IF. No registrations → no credit floating free of any datum. */}
      {registered.length > 0 && <HpaCredit attribution={registered[0]} />}
    </HpaCreditContext.Provider>
  )
}

// ⚠⚠ Element 4, rendered BESIDE THE DATUM IT CITES. Mount this only from a block that is actually
// rendering an HPA value — that is the suppression half of the ruling, and it is the caller's
// decision because only the caller knows whether it drew anything.
export function HpaDeepLink({ attribution, view }) {
  const ctx = useContext(HpaCreditContext)
  const key = useId()
  const registering = Boolean(attribution) && Boolean(ctx)

  useEffect(() => {
    if (!registering) return undefined
    ctx.register(key, attribution)
    return () => ctx.unregister(key)
  }, [registering, ctx, key, attribution])

  if (!attribution) return null

  const link = (
    <div className="hpa-attrib hpa-attrib-datum" data-hpa-attribution={view ?? 'protein'}>
      {/* ⚠ Its ABSENCE renders with a cause: 89 of 2,688 census rows resolve no Ensembl id, and a
          link built without one would 404 or, worse, resolve to a DIFFERENT protein. */}
      {attribution.deep_link ? (
        <a className="hpa-attrib-link" href={attribution.deep_link}
           rel="noopener noreferrer" target="_blank">
          View this protein on the Human Protein Atlas (v22)
        </a>
      ) : (
        <span className="hpa-attrib-nolink">
          No direct atlas link — {attribution.deep_link_absent_reason}
        </span>
      )}
    </div>
  )

  // ⚠⚠ NO PROVIDER, NO LOSS. Rendered outside a page (a component test, a future surface that
  // forgets to wrap), this falls back to the FULL block rather than emitting a bare link with no
  // citation. **The failure mode of forgetting the provider is redundancy, never non-compliance.**
  if (!ctx) {
    return (
      <>
        {link}
        <HpaCredit attribution={attribution} />
      </>
    )
  }
  return link
}

// ⚠ The whole block in one element. Retained for surfaces that are not inside a provider and want
// the complete citation in one place — `CensusTable`'s staining column is the standing case.
export default function HpaAttribution({ attribution, view }) {
  if (!attribution) return null
  return (
    <>
      <HpaDeepLink attribution={attribution} view={view} />
      <HpaCredit attribution={attribution} />
    </>
  )
}
