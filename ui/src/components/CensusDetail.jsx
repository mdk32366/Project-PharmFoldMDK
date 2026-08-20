import { bandFor } from '../plddt.js'
import StructuralProfile from './StructuralProfile.jsx'
import ClinicalEdges from './ClinicalEdges.jsx'
import SurfaceCheck from './SurfaceCheck.jsx'
import { HpaDeepLink } from './HpaAttribution.jsx'

// One census protein. Four questions, in the order a reader asks them: what is it, what did we
// fold, how confident is the model, and what is it associated with.
//
// ⚠⚠ EVERY ABSENCE HERE IS A CATEGORY WITH A CAUSE. "No cancer associations" is never printed,
// because it is not what the data says — the association source covers the 82 cohort targets only,
// so for a census protein the honest statement is "outside the source", which is a different fact
// with a different remedy.

function Segments({ detail }) {
  const { topology, segment_count: n, extracellular_total_aa: total,
          discarded_aa: discarded, span_aa: span, segments } = detail

  if (topology === 'no_accepted_segment') {
    return (
      <div className="segments">
        <h4>Extracellular topology</h4>
        <p>
          <strong>No annotated extracellular segment.</strong> This protein is GPI-anchored — it has
          no topological domains <em>by design</em>, and its span comes from the anchor rule rather
          than from a topology annotation.
        </p>
        <p className="caveat">
          ⚠ This is a different molecular architecture, <strong>not</strong> missing data and{' '}
          <strong>not</strong> an intermittent surface.
        </p>
      </div>
    )
  }

  if (topology === 'derivation_stale' || topology === 'derivation_absent'
      || topology === 'derivation_unstamped') {
    return (
      <div className="segments">
        <h4>Extracellular topology</h4>
        {/* ⚠⚠ NOT "unknown", and never the old value. A stale derivation described a manifest that
            is no longer on disk; showing its numbers would be confidently wrong. */}
        <p className="caveat">
          ⚠⚠ <strong>Not shown — the segment derivation is out of date.</strong> It was computed
          from a different revision of the census manifest, so its numbers would describe data that
          is no longer there. <strong>This is withheld deliberately, not missing.</strong>
        </p>
        {detail.derivation_note && <p className="note">{detail.derivation_note}</p>}
      </div>
    )
  }

  if (topology === 'unknown') {
    return (
      <div className="segments">
        <h4>Extracellular topology</h4>
        {/* ⚠ "not derived" is not "contiguous". A surface that defaulted to the benign case would
            state a topology nobody measured. */}
        <p className="caveat">⚠ Segment structure has not been derived for this protein — unknown, not absent.</p>
      </div>
    )
  }

  const contiguous = topology === 'contiguous'
  return (
    <div className="segments">
      <h4>Extracellular topology</h4>
      {contiguous ? (
        <p>
          <strong>Contiguous.</strong> One extracellular region of {total} aa (amino acids), and it is what was
          folded. The structure models the whole extracellular portion.
        </p>
      ) : (
        <>
          <p className="caveat">
            ⚠⚠ <strong>Intermittent — {n} separate extracellular segments.</strong> This protein
            crosses the membrane more than once, so its extracellular portion is several stretches
            rather than one.
          </p>
          <p>
            Extracellular in total: <strong>{total} aa (amino acids)</strong>. Folded here:{' '}
            <strong>{span} aa</strong> — the <em>largest single segment</em>.{' '}
            <strong>
              {discarded} aa across the remaining {n - 1}{' '}
              {n - 1 === 1 ? 'segment was' : 'segments were'} not folded.
            </strong>
          </p>
          <p className="caveat">
            ⚠ An antibody can bind an epitope formed by several loops together. A structure of one
            loop in isolation is <strong>not</strong> a model of that site — read this structure as
            one segment, not as the ectodomain.
          </p>
        </>
      )}
      {segments && <p className="segment-list">Segments (residue ranges): {segments.split(';').join(', ')}</p>}
    </div>
  )
}

function Associations({ assoc }) {
  if (!assoc) return null
  if (assoc.status !== 'covered') {
    return (
      <div className="associations">
        <h4>Cancer associations</h4>
        {/* ⚠⚠ NOT "no associations found". We did not look at this protein. */}
        <p className="caveat">
          ⚠ <strong>Not covered by the association source</strong> — so this is{' '}
          <strong>unknown</strong>, not <em>none</em>. {assoc.coverage_note}.
        </p>
        {/* ⚠⚠ THE SENTENCE THAT WAS MISSING, AND ITS ABSENCE READ AS A CLAIM ABOUT THE PROTEIN.
            The owner read this card as saying LAMP1 has no cancer associations. Measured on the
            SAME card at the time: LAMP1 stains in breast 11/11, carcinoid 4/4, cervical 12/12,
            colorectal 12/12, endometrial 11/11 and glioma 11/11 patients — HPA v22 pathology.tsv,
            which covers 15,313 genes. This block's source covers 113 accessions, all of them in or
            beside the 82.
            ⚠ So two sections about cancer sat on one card: this one saying "unknown", and a fuller
            one below carrying six tumour panels. Saying "unknown" without naming the panel that is
            NOT unknown leaves a reader to conclude the card looked and found nothing. */}
        <p className="caveat">
          ⚠⚠ <strong>This is not the only tumour evidence on this card.</strong> The tumour and
          normal-tissue panels below come from a different and much wider source, and they may well
          carry data for this protein. This section is silent about the source named beneath it —
          nothing more.
        </p>
        <p className="source">Source: {assoc.source}</p>
        {/* ⚠⚠ NO ATTRIBUTION HERE, AND THAT IS THE FIX. This branch renders NO HPA VALUE — it is the
            statement that the source does not cover this protein. Citing HPA beside it attached a
            licence-required credit to nothing, and it did so on 78 of 79 sampled census cards.
            ⚠ The precondition is "never display our content without citation", not "cite us
            wherever the word tumour appears". A citation with no datum is not compliance. */}
      </div>
    )
  }
  if (assoc.hits.length === 0) {
    return (
      <div className="associations">
        <h4>Cancer associations</h4>
        <p>
          <strong>Covered by the source, and no cancer met the threshold.</strong> This one <em>is</em>{' '}
          a measured absence.
        </p>
        <p className="source">Source: {assoc.source}</p>
      </div>
    )
  }
  return (
    <div className="associations">
      <h4>Cancer associations</h4>
      <ul>
        {assoc.hits.map((h) => (
          <li key={h.cancer}>
            {h.cancer} <span className="num">({h.qh_score})</span>
          </li>
        ))}
      </ul>
      <p className="source">Source: {assoc.source}</p>
      {/* ⚠⚠ THE CITATION WAS ON THE WRONG BRANCH, AND THIS IS THE ONE THAT NEEDED IT.
          Before this change `HpaAttribution` appeared ONLY in the `status !== 'covered'` branch —
          which renders no HPA value at all — and was ABSENT here, where `qh_score` renders.
          `qh` is pathology.tsv through our formula (`D-100`: S3 is a verbatim extract, 1,640/1,640),
          so this is HPA content, and HPA words citation as a precondition of display.
          ⚠ The precondition was satisfied only where there was nothing to satisfy it about.
          ⚠⚠ The PC3 guard could not see this: it asserts the FILE imports the attribution, and the
          file did. **A file-level guard cannot see which branch renders the value.** */}
      <HpaDeepLink attribution={assoc.attribution} view="pathology" />
    </div>
  )
}

export default function CensusDetail({ detail, onClose, embedded = false }) {
  if (!detail) return null
  const band = bandFor(detail.mean_plddt)
  return (
    <section className="census-detail panel">
      {/* ⚠ Only when there is somewhere to close TO. On the protein page the panel IS the page,
          and a Close button there would suggest an overlay that does not exist. */}
      {onClose && <button type="button" className="close" onClick={onClose}>Close</button>}
      {/* ⚠ Suppressed when embedded in the protein page, which already carries the identity in
          its own header. Printing gene + accession + name twice on one page reads as a rendering
          fault, and a reader who spots it trusts the numbers underneath less. */}
      {!embedded && (
        <>
          <h3>
            {detail.gene ?? detail.accession}{' '}
            <span className="accession">{detail.accession}</span>
          </h3>
          <p className="protein-name">
            {detail.label ?? <span className="unknown">name unknown</span>}
          </p>
          {/* ⚠⚠ THE NAME ON THE DRUG LABEL IS OFTEN NOT THE NAME ON THIS PAGE. This protein is
              `TNFRSF8` here and `CD30` everywhere a clinician reads about it. Showing the other
              names is what lets a reader confirm they are looking at the protein they meant — the
              owner searched CD30 and concluded it was absent.
              ⚠ SECONDARY, never a rename: the gene symbol above stays the row's identity. */}
          {detail.aliases?.length > 0 && (
            <p className="protein-aliases">
              <span className="aka-label">Also known as</span>{' '}
              {detail.aliases.slice(0, 6).join(' · ')}
            </p>
          )}
        </>
      )}

      <h4>Status</h4>
      <ul className="status-list">
        <li>Folded — tranche {detail.tranche}</li>
        <li>
          Span {detail.span_aa} aa (amino acids; residues {detail.span_start}–{detail.span_end} of{' '}
          {detail.full_length})
        </li>
        <li>Span definition: <code>{detail.span_definition}</code></li>
        <li>
          Confidence:{' '}
          <strong style={{ color: band.color }}>
            {detail.mean_plddt != null ? detail.mean_plddt.toFixed(2) : 'not measured'}
          </strong>{' '}
          — {band.label}
        </li>
        {/* ⚠ Stated on the row, not left to the absence of a score field to imply. */}
        <li className="caveat">
          ⚠ <strong>Not scored and not ranked.</strong> {detail.not_scored_reason}
        </li>
      </ul>

      <Segments detail={detail} />
      {/* ⚠⚠ The structural profile sits BELOW the "not scored and not ranked" line, never above
          it, and never in the slot TargetScorerPanel occupies on a target page. D-089: a census
          page carries no scorer panel, and D-079 amendment 1 warns the profile block must not
          become one by another name. The order of the page is part of that: the reader is told
          this protein is unscored BEFORE being shown a structure-derived number. */}
      <StructuralProfile block={detail.structural_profile_block} />
      {/* ⚠ D-093 edges 1+2 — the human-legible half, BELOW the structural
          profile: the reader meets what the protein IS before what a model
          says about it. */}
      {/* ⚠ Placed BEFORE the clinical edges and after the span it comments on: it is a check on
          the census's own claim, not a fact about the disease. Ordering says what a thing is. */}
      <SurfaceCheck check={detail.surface_check} />

      <ClinicalEdges block={detail.clinical_block} />
      <Associations assoc={detail.cancer_associations} />
    </section>
  )
}
