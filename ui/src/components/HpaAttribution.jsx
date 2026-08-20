// HPA attribution — the four elements, on every surface that renders an HPA-derived value.
//
// ⚠⚠ THE LICENCE WORDS THIS AS A PRECONDITION, NOT A FOOTNOTE: "be sure that our content is never
// displayed in the absence of such citation." That is D-094's shape, written by HPA. So this
// component is a MOUNT PRECONDITION — if an HPA value renders and this does not, the surface is out
// of compliance, and a test reds.
//
// ⚠⚠ AND "HPA-DERIVED" IS ABOUT THE SOURCE, NOT THE ROUTE. CancerAssociations reads Kathad's S3,
// and D-100 established S3 is a VERBATIM EXTRACT of pathology.tsv — 1,640/1,640 rows. Citing the
// paper is not citing HPA. D-053 predates the clinical layer, so that surface has rendered HPA data
// unattributed for far longer than the entry that found the gap.
//
// ⚠ The primary publication is the IHC paper. NOT the 2017 transcriptome paper, despite its title
// matching our filename. A filename is not a modality.

export default function HpaAttribution({ attribution, view }) {
  if (!attribution) return null
  const { primary_publication: pub, website, data_credit, deep_link, deep_link_absent_reason } =
    attribution

  return (
    <div className="hpa-attrib" data-hpa-attribution={view ?? 'protein'}>
      {/* ⚠⚠ ELEMENT 4 — THE PER-DATUM LINK, and a single block per page does not discharge it.
          ⚠ Its ABSENCE renders with a cause: 89 of 2,688 census rows resolve no Ensembl id, and a
          link built without one would 404 or, worse, resolve to a different protein. */}
      {deep_link ? (
        <a className="hpa-attrib-link" href={deep_link} rel="noopener noreferrer" target="_blank">
          View this protein on the Human Protein Atlas (v22)
        </a>
      ) : (
        <span className="hpa-attrib-nolink">
          No direct atlas link — {deep_link_absent_reason}
        </span>
      )}

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

      {/* ⚠⚠ ELEMENT 3 — THE IMAGE/DATA CREDIT, AS ITS OWN ELEMENT. Amendment 1 clause 3 dropped it
          and NC confirmed it was never built. It is deliberately NOT element 2 doing double duty:
          the licence asks for a credit, and a hyperlink to a site is not a credit. */}
      <p className="hpa-attrib-credit">
        <span className="hpa-attrib-credit-label">Image/data credit:</span> {data_credit}
      </p>
    </div>
  )
}
