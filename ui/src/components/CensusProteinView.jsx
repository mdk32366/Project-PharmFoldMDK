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
        {/* ⚠ Said at the top, where a reader arriving from a search engine meets it first — not
            buried under the structure they came to look at. */}
        <p className="census-bar">
          <strong>Not scored, not ranked.</strong> This protein was folded to find out whether it
          could be; it has not been assessed as a target, and it is not comparable to the ranked 82.
        </p>
      </header>

      <StructureViewer id={id} />

      <div className="panels">
        <Confidence meanPlddt={detail.mean_plddt} plddt={plddt} />
        <PlddtExplainer />
      </div>

      {/* The measured body — status, extracellular topology (F-037), association coverage.
          ⚠ Reused, not reimplemented: the inline panel and this page must not drift into saying
          different things about the same protein. */}
      <CensusDetail detail={detail} embedded />
    </article>
  )
}
