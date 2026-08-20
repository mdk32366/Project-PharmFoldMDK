// The second instrument — D-103. On the protein card, beneath the span it comments on.
//
// ⚠⚠ WHAT THIS IS FOR, IN ONE SENTENCE: every census row says "this protein has an extracellular
// span", and until now every one of those claims came from ONE source. This is a different
// instrument reading the same claim, so a reader can see whether anything agrees.
//
// ⚠⚠ AND THE TRAP THIS COMPONENT EXISTS TO AVOID: a Golgi or vesicle call is NOT a contradiction.
// The secretory route is ER → Golgi → vesicle → plasma membrane, so a genuine surface protein can
// sit mostly in that pipeline. Rendering "not plasma membrane" as a failure would be a confident
// wrong answer about real biology — so the route has its own wording and reads as SUPPORT.
//
// ⚠ Nothing here is a score, a confidence or a grade. There is no ordering over these categories.

import { HpaDeepLink } from './HpaAttribution.jsx'

const COPY = {
  corroborated_membrane: {
    head: 'Confirmed at the cell surface',
    body: 'A second, independent method — antibody imaging — also places this protein at the ' +
          'plasma membrane. Two different kinds of evidence agree.',
    tone: 'agree',
  },
  corroborated_route: {
    head: 'Confirmed on the route to the surface',
    body: 'Antibody imaging places this protein in the secretory pathway — the ER, Golgi or ' +
          'transport vesicles that carry proteins to the cell surface. That supports the surface ' +
          'assignment rather than contradicting it: this is where such a protein is made and ' +
          'moved, and it is often where most of it sits at any moment.',
    tone: 'agree',
  },
  mixed: {
    head: 'Mixed signal',
    body: 'Antibody imaging places this protein in more than one kind of compartment, or in one ' +
          'that neither supports nor contradicts a surface location. Read the locations below ' +
          'rather than treating this as a verdict.',
    tone: 'mixed',
  },
  unreconciled: {
    head: 'The two methods do not line up',
    body: 'The census places this protein at the cell surface. Antibody imaging places it ' +
          'somewhere a surface protein would not usually sit.',
    tone: 'unreconciled',
  },
  if_not_attempted: {
    head: 'No second opinion available',
    body: 'The atlas holds this protein but never imaged its location, so there is nothing to ' +
          'compare against. That means nobody looked — not that the surface assignment failed a ' +
          'check. This is the most common case.',
    tone: 'absent',
  },
  gene_absent_from_supplier: {
    head: 'No second opinion available',
    body: 'This protein is not in the imaging atlas at all, so no independent reading exists.',
    tone: 'absent',
  },
  no_gene_symbol: {
    head: 'No second opinion available',
    body: 'This record carries no gene symbol, so it cannot be looked up in the imaging atlas.',
    tone: 'absent',
  },
}

export default function SurfaceCheck({ check }) {
  if (!check) return null
  const copy = COPY[check.category]
  if (!copy) return null

  return (
    <section className={`surfchk surfchk-${copy.tone}`}>
      <h3>Is it really on the surface?</h3>

      {/* ⚠⚠ THE TWO INSTRUMENTS ARE NAMED. "Two sources agree" means nothing if the reader cannot
          see that they are different KINDS of evidence — two readings of the same sequence would
          be no corroboration at all. This is the sentence that makes the section worth having. */}
      <p className="surfchk-instruments">
        <strong>Two different kinds of evidence.</strong> The census assignment comes from{' '}
        <em>{check.instruments?.census}</em>. The check comes from{' '}
        <em>{check.instruments?.hpa_if}</em>. They can be wrong in different ways, which is what
        makes the comparison worth making.
      </p>

      <p className="surfchk-verdict">
        <strong>{copy.head}.</strong> {copy.body}
      </p>

      {check.main_locations?.length > 0 && (
        <p className="surfchk-locations">
          <span className="surfchk-label">Imaged in</span>{' '}
          {check.main_locations.join(' · ')}
          {check.if_reliability && (
            // ⚠ HPA's OWN confidence in its imaging call, labelled as theirs. Not our judgement.
            <span className="surfchk-rel">
              {' '}— the atlas rates its own call <strong>{check.if_reliability}</strong>
            </span>
          )}
        </p>
      )}

      {/* ⚠⚠ A DISAGREEMENT IS NOT A VERDICT ON THE PROTEIN. Three causes are possible and we
          cannot tell them apart from here, so all three are printed. Showing the category without
          them would let a reader conclude the protein is not a surface protein, which is a claim
          this comparison cannot support. */}
      {/* ⚠⚠ THIS SURFACE RENDERS HPA VALUES — subcellular locations and HPA's own Reliability (IF)
          from proteinatlas.tsv — and it shipped on 2026-08-20 WITHOUT attribution, after the audit
          that found the gap. F-052: a convention obeyed by every caller except the newest one. */}
      {/* ⚠ SUPPRESSED WHEN NO HPA VALUE RENDERS. The HPA content here is the subcellular
          locations and HPA's own IF reliability; when the category is `if_not_attempted` there
          are neither, and a licence-required citation then cites nothing. Measured: 51 of 79
          sampled census cards were in exactly that state. */}
      {(check.main_locations?.length > 0 || check.if_reliability) && (
        <HpaDeepLink attribution={check.attribution} view="protein" />
      )}

      {check.unreconciled_causes?.length > 0 && (
        <div className="surfchk-causes">
          <p><strong>Any of three things could explain that, and this cannot tell which:</strong></p>
          <ul>
            {check.unreconciled_causes.map((c) => <li key={c}>{c}</li>)}
          </ul>
        </div>
      )}
    </section>
  )
}
