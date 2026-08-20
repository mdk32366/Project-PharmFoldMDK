import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCensusDetail, getPlddt } from '../api.js'
import StructureViewer from './StructureViewer.jsx'
import Confidence from './Confidence.jsx'
import PlddtExplainer from './PlddtExplainer.jsx'
import CensusDetail from './CensusDetail.jsx'

// A page per census protein, the same shape as the target page: structure coloured by pLDDT,
// confidence with its band, and the measured properties beneath.
//
// ⚠⚠ WHAT THIS PAGE DELIBERATELY DOES NOT HAVE, and the absence is the point: no scorer panel, no
// rank, no suitability verdict. `TargetView` carries `TargetScorerPanel` because the 82 WERE scored;
// D-079 dec 1 bars scoring any census row, so the equivalent panel here would have to invent one.
// ⚠ Giving a census protein a page that LOOKS like a ranked target's page is exactly how a reader
// concludes it is one — so the "not scored" statement is carried in the body, not left to the
// absence of a panel to imply.
//
// ⚠ The structure and pLDDT routes are NOT tranche-filtered (`get_structure_path` reads the stored
// `pdb_path` for any analysis id), so they are reused rather than duplicated. A second pair of
// routes would be a second source for one artifact with nothing comparing them.
// ⚠⚠ THE CARD'S COPY AS A PURE FUNCTION, and the reason is a test that could not be written well
// against the JSX. Scanning source text for "no structure yet" and checking a `cohort_fold` appears
// nearby passed at a wide window (it reached the banner's guard) and failed at a narrow one (the
// banner's own phrase sits further from its guard). A character window is the wrong instrument for
// a branching question. As a function, the rule is just an assertion about return values.
//
// ⚠ THREE STATES: a fold exists in the ranked 82 · it was attempted there and failed · neither.
export function unfoldedCopy(detail) {
  if (detail.folded !== false) return null
  if (detail.cohort_fold) {
    return {
      bar: 'This protein has not been folded in the census. It IS one of the ranked 82 and was '
        + 'folded there — but that is a separate measurement under a different span rule, and '
        + 'nothing on this page is derived from it.',
      body: 'Nothing below is missing because it failed: no census structure exists, so this page '
        + 'carries no confidence score, structural profile or staining panel derived from one. The '
        + 'ranked fold above is a different measurement and is not substituted here.',
    }
  }
  return {
    bar: 'This protein has not been folded, so nothing has been measured from a structure — and it '
      + 'has not been assessed as a target either. It is not comparable to the ranked 82.',
    body: 'Nothing below is missing because it failed: there is no structure yet, so there is no '
      + 'confidence score, no structural profile and no staining panel to show.',
  }
}

export default function CensusProteinView({ id }) {
  const [detail, setDetail] = useState(null)
  const [plddt, setPlddt] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setDetail(null)
    setPlddt(null)
    setError(null)
    // ⚠ Only the detail is page-critical. A fold with no `plddt.json` must still render its
    // identity, its topology and its reasons — the same degradation rule the target page uses.
    getCensusDetail(id)
      .then((d) => { if (!cancelled) setDetail(d) })
      .catch((e) => { if (!cancelled) setError(e.message ?? String(e)) })
    getPlddt(id)
      .then((p) => { if (!cancelled) setPlddt(p) })
      .catch(() => { if (!cancelled) setPlddt(null) })
    return () => { cancelled = true }
  }, [id])

  if (error) {
    return (
      <article className="census-protein">
        <p className="error">Could not load census protein {id}: {error}</p>
        {/* ⚠ A cohort id 404s here by design — the two populations are measured under different
            span definitions (D-081) and must not be reachable through one another's route. */}
        <p className="note">
          If this is one of the 82 ranked targets it will not be here — those live under{' '}
          <Link to="/targets">Targets</Link>.
        </p>
        <p><Link to="/census">← back to the census</Link></p>
      </article>
    )
  }
  if (!detail) return <p className="loading">Loading census protein {id}…</p>

  return (
    <article className="census-protein">
      <p className="breadcrumb"><Link to="/census">← the wider protein census</Link></p>

      <header className="target-header">
        <h2>{detail.gene ?? detail.accession}</h2>
        <p className="subtitle">
          {detail.accession}
          {detail.label ? ` · ${detail.label}` : ''}
        </p>
        {/* ⚠⚠ The other names this protein goes by, on the card itself. `TNFRSF8` is `CD30` to
            everyone who reads about the drug, and a reader who cannot see that connection cannot
            tell they have found the protein they were looking for. Secondary, never a rename. */}
        {detail.aliases?.length > 0 && (
          <p className="protein-aliases">
            <span className="aka-label">Also known as</span>{' '}
            {detail.aliases.slice(0, 6).join(' · ')}
          </p>
        )}
        {/* ⚠ Said at the top, where a reader arriving from a search engine meets it first — not
            buried under the structure they came to look at. */}
        <p className="census-bar">
          {/* ⚠ The bar asserted "this protein WAS FOLDED" on every card, including the ones that
              were never folded — a false claim sitting directly above a NOT FOLDED banner. */}
          <strong>Not scored, not ranked.</strong>{' '}
          {unfoldedCopy(detail)?.bar
            ?? 'This protein was folded to find out whether it could be; it has not been assessed as a target, and it is not comparable to the ranked 82.'}
        </p>
      </header>

      {/* ⚠⚠ NEVER FOLDED — NO STRUCTURE, AND THE PAGE SAYS SO INSTEAD OF DRAWING A DEAD FRAME.
          HER2 reaches this page because it is in the manifest; there is simply no fold to show.
          An empty viewer would read as a broken widget — the same false signal the census list
          gave when it answered "no protein matches that search". */}
      {detail.folded === false ? (
        <section className="unfolded-card">
          <h3>NOT FOLDED</h3>
          {/* ⚠⚠ THREE OUTCOMES, AND THE CARD USED TO STATE ONLY ONE. "Waiting on rented capacity"
              was shown for 29 proteins whose fold ALREADY EXISTS in the ranked 82 — at the same
              span, on rental hardware — and for IGF2R, which was tried on rental and died of CUDA
              OOM. A queue position, an existing result and a failed attempt are three different
              facts and the card said the same thing for all of them. */}
          {detail.cohort_fold ? (
            <p className="unfolded-why">
              <strong>Not folded in the census — but a fold of this protein exists.</strong>{' '}
              It is one of the <strong>82 ranked targets</strong>, and there it was folded on
              rented hardware
              {detail.cohort_fold.mean_plddt != null && (
                <> at a mean confidence of <strong>{detail.cohort_fold.mean_plddt}</strong></>
              )}.{' '}
              {/* ⚠ D-081: the two populations are measured under different span definitions, so
                  the reader is given the spans rather than an assurance they are the same. */}
              <span className="caveat">
                ⚠ The two are measured separately — this census span is{' '}
                <strong>{detail.span_aa} aa</strong>
                {detail.cohort_fold.fold_length
                  ? <> and the ranked fold covered <strong>{detail.cohort_fold.fold_length} aa</strong></>
                  : null}
                , so compare them before treating one as the other.
              </span>
            </p>
          ) : detail.cohort_attempt_failed ? (
            <p className="unfolded-why">
              <strong>Not folded — and it was tried.</strong> This protein is one of the 82 ranked
              targets, and the fold was attempted there on rented hardware and{' '}
              <strong>failed</strong>
              {detail.cohort_attempt_failed.reason && (
                <>: <code>{detail.cohort_attempt_failed.reason.slice(0, 90)}</code></>
              )}.{' '}
              <span className="caveat">
                ⚠ That is not a queue position. Renting more capacity does not obviously fix it.
              </span>
            </p>
          ) : (
            <p className="unfolded-why"><strong>{detail.not_folded_copy}.</strong></p>
          )}
          <p>
            Its extracellular stretch is{' '}
            <strong>{detail.span_aa} aa (amino acids)</strong> — long by the standards of what this
            project could fold locally.{' '}
            {unfoldedCopy(detail)?.body}
          </p>
          <p className="caveat">
            ⚠ <strong>This is not a judgement about the protein.</strong> It is a statement about
            which proteins had a graphics card available, and nothing more.
          </p>
        </section>
      ) : (
        <StructureViewer id={id} />
      )}

      {detail.folded !== false && (
      <div className="panels">
        {/* ⚠ NOT the cohort's ceiling. The default note states "cohort max 84.23", which is a
            fact about the 82 — and six census structures already exceed it. ⚠ No census maximum is
            quoted either: it moves every time a tranche completes, and a number baked in here
            would go stale silently (the D-088 trap). */}
        <Confidence
          meanPlddt={detail.mean_plddt}
          plddt={plddt}
          caveat="the confidence bands are shared with the ranked 82, but this protein is not one of them — the cohort's measured ceiling does not describe the census"
        />
        {/* ⚠ Without the cohort's ceiling — see the Confidence note above. */}
        <PlddtExplainer showCohortMax={false} />
      </div>
      )}

      {/* The measured body — status, extracellular topology (F-037), association coverage.
          ⚠ Reused, not reimplemented: the inline panel and this page must not drift into saying
          different things about the same protein. */}
      <CensusDetail detail={detail} embedded />
    </article>
  )
}
