import { useEffect, useState } from 'react'
import { getRanking, getCoverage } from '../api.js'
import CoverageLine from './CoverageLine.jsx'
import Term from './Term.jsx'

// D-062 — the scorer surface. Renders the persisted pre-registered result (F-004); it never
// recomputes and never types a live number — every count and statistic is derived from
// /api/ranking (Constraint-A, D-050/D-051). The paper's published count (22) is served as a source
// constant. The three named targets (ERBB2/NECTIN4/EGFR) and the unverified carve-out
// (CXCR5/MSLN/MUC16, F-003 Finding 6) are fixed symbol names, not live-derived numbers.

const PAPER_NAMED = ['ERBB2', 'NECTIN4', 'EGFR']            // the antigens the paper names (F-003)
const UNVERIFIED = ['CXCR5', 'MSLN', 'MUC16']              // routed probable, unverified — NOT negative (F-003 Finding 6)

const mean = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null)
const median = (xs) => {
  if (!xs.length) return null
  const s = [...xs].sort((a, b) => a - b)
  const n = s.length
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2
}
const f3 = (x) => (x == null ? '—' : x.toFixed(3))

// D-062 / F-006 — the Score COLUMN tooltip. Distinct from the `structural score` Term (which defines
// what the score means); this one carries the observed distribution and the non-calibration boundary.
// Every number is derived from the ranking payload (Constraint-A, D-050) — no literal 0.116/0.220/
// 0.285/56 here. The non-calibration sentence is a claim boundary (F-006 Finding 3): it is asserted
// present in the rendered tooltip DOM and is never trimmed for length. The F-005 pLDDT-driven note
// lives here now (D-066 §2), not as a standalone intro paragraph.
function ScoreColumnHeader({ scores, labelledCount, rankingSetCount }) {
  const lo = f3(Math.min(...scores))
  const hi = f3(Math.max(...scores))
  const mid = f3(median(scores))
  const id = 'gloss-score-column'
  return (
    <span className="term">
      <button type="button" className="term-trigger" aria-describedby={id}>Score</button>
      <span role="tooltip" id={id} className="term-def score-def">
        The model's output for each target, between 0 and 1; higher means more like the{' '}
        {labelledCount} targets people have already built ADCs against. <b>It is not a calibrated
        probability</b> — calibration was never tested at this cohort size, so read it as a position
        in the ordering, not a percentage chance. In this run the {scores.length} scores span{' '}
        {lo}–{hi}, median {mid}, against a labelled fraction of {labelledCount}/{rankingSetCount}. The
        ordering is substantially pLDDT-driven (F-005).
      </span>
    </span>
  )
}

export default function ScorerView() {
  const [ranking, setRanking] = useState(null)
  const [coverage, setCoverage] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getRanking(), getCoverage()])
      .then(([r, c]) => { setRanking(r); setCoverage(c) })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="error">Could not load the scorer result: {error}</p>
  if (!ranking) return <p className="loading">Loading the scorer result…</p>

  const status = ranking.result_status
  if (status === 'not_run') {
    return (
      <div className="scorer">
        <h2>The scorer result</h2>
        <p className="scorer-status not-run">No pre-registered result has been recorded yet.</p>
      </div>
    )
  }
  if (status === 'raised') {
    return (
      <div className="scorer">
        <h2>The scorer result</h2>
        <p className="scorer-status raised">
          The leave-one-out produced no distribution — the fit did not converge.
        </p>
        <p className="scorer-detail">{ranking.result?.status_detail}</p>
      </div>
    )
  }
  return <FullResult ranking={ranking} coverage={coverage} partial={status === 'partial'} />
}

function FullResult({ ranking, coverage, partial }) {
  const r = ranking.result
  const dist = r.distribution || []
  const pcts = dist.map((d) => d.percentile)
  const aboveHalf = pcts.filter((p) => p > 0.5).length
  const hs = r.headto_structural || []
  const he = r.headto_evidence || []
  const distSymbols = new Set(dist.map((d) => d.symbol).concat(r.nonconvergent || []))
  const evidenceValues = [...new Set(he)].sort((a, b) => a - b)
  const scores = ranking.rows.map((row) => row.score)                     // for the Score-column tooltip (derived)
  const rankedFolded = coverage.rows.filter(                              // the D-024 disposition count (67 live)
    (x) => x.disposition === 'ranked' && x.fold_status === 'folded').length

  return (
    <div className="scorer">
      <h2>The scorer result</h2>
      {partial && (
        <p className="scorer-status partial">
          Partial result — some pre-registered statistics are blocked. {r.status_detail}
        </p>
      )}

      {/* two-column: explanation left (A–D), the ranking table right (E). Stacks on narrow. */}
      <div className="scorer-cols">
        <div className="scorer-explain">
          {/* ── A — the cascade ── */}
          <section className="scorer-cascade">
            <h3>A · From the cohort to the fit set</h3>
            <ol className="cascade">
              <li><b>{coverage.coverage.denominator}</b> cohort targets (Kathad et al.)</li>
              <li><b>{coverage.rows.filter((x) => x.fold_status === 'folded').length}</b> folded
                <span className="removes"> — removes what could not be folded on available hardware</span></li>
              <li><b>{coverage.coverage.ranked}</b> ranked
                <span className="removes"> — removes held-out (boundary-method incomparable) and excluded</span></li>
              <li><b>{r.n_ranking_set}</b> rankable <span className="removes"> — removes folds below the <Term name="pLDDT">pLDDT</Term> floor of {r.plddt_floor}</span></li>
              <li><b>{r.n_fit_positives}</b> Group B positives in the fit set
                <span className="removes"> — the labelled subset the model is scored against</span></li>
              <li><b>{hs.length}</b> in the head-to-head <span className="removes"> — positives also carrying a published comparator score</span></li>
            </ol>
          </section>

          {/* ── B — the labels ── */}
          <section className="scorer-labels">
            <h3>B · The labels</h3>
            <p>
              <b>{r.n_fit_positives}</b> curated Group B <Term name="accession">accessions</Term>, against
              the paper's <b>{r.paper_published_count}</b> published — the gap is a finding, its
              explanations named and unresolved (F-003).
            </p>
            <p>
              The three antigens the paper names:{' '}
              {PAPER_NAMED.map((g) => (
                <span key={g} className="label-check">
                  {g} {distSymbols.has(g) ? '✓ present' : '— absent'}{' '}
                </span>
              ))}
            </p>
            <p className="unverified">
              Named as <b>unverified, not negative</b> (F-003 Finding 6): {UNVERIFIED.join(', ')} — routed
              probable-positive by the registry pass, never verified, so absent because unverified. None
              is in the fit set anyway.
            </p>
            <p className="exclusion-classes">
              Exclusions applied span radioimmunoconjugates, peptide-drug conjugates, naked antibodies,
              and family-member <Term name="ADC">ADCs</Term> (F-003 Finding 4).
            </p>
          </section>

          {/* ── C — the pre-registration ── */}
          <section className="scorer-prereg">
            <h3>C · Fixed before the run</h3>
            <ul>
              <li><b>D-027</b> (2026-07-22) — the six features and their count.</li>
              <li><b>D-041</b> (2026-07-23) — the model (seven parameters), and both pre-registered negative outcomes.</li>
              <li><b>D-060</b> (2026-07-27) — the 13-point λ grid, 5-fold inner CV, no RNG, the floor.</li>
              <li><b>D-063 / D-064</b> (2026-07-28) — the LOO-independence and label-path corrections.</li>
            </ul>
            <p className="prereg-note">Every parameter above was dated before the result existed.</p>
          </section>

          {/* ── D — the result (caveat b stays with it) ── */}
          <section className="scorer-result">
            <h3>D · The result</h3>
            <p className="result-intro">
              The <Term name="structural score">structural score</Term> ranks the fit set; its
              leave-one-out distribution is the pre-registered object.
            </p>

            <h4>The leave-one-out distribution ({r.loo_status})</h4>
            <table className="dist-table">
              <thead><tr><th>Target</th><th>Percentile</th></tr></thead>
              <tbody>
                {dist.map((d) => (
                  <tr key={d.symbol}><td>{d.symbol}</td><td>{f3(d.percentile)}</td></tr>
                ))}
              </tbody>
            </table>
            <p>
              Median <b>{f3(median(pcts))}</b> · mean <b>{f3(mean(pcts))}</b> · {aboveHalf} of {dist.length}{' '}
              above 0.5, against a null of 0.5. A modest upward shift; no significance test was
              pre-registered and none is reported.
            </p>

            <h4>Head-to-head vs the comparator (N = {hs.length})</h4>
            <table className="h2h-table">
              <thead><tr><th></th><th>structural</th><th>comparator</th></tr></thead>
              <tbody>
                <tr><td>mean</td><td>{f3(mean(hs))}</td><td>{f3(mean(he))}</td></tr>
                <tr><td>median</td><td>{f3(median(hs))}</td><td>{f3(median(he))}</td></tr>
              </tbody>
            </table>
            <p>
              <b>First negative outcome — FIRES:</b> not distinguishable from the comparator, and the
              direction reverses between mean and median. The comparator is two-valued by construction
              ({evidenceValues.map(f3).join(' and ')}), which bounds what this comparison could show.
            </p>

            <h4>Correlation with the comparator (N = {r.spearman_n})</h4>
            <p>
              Spearman <b>{f3(r.spearman)}</b>. <b>Second negative outcome — DOES NOT FIRE:</b> near-zero,
              so the structural axis is not a proxy for expression-and-attention.
            </p>

            <div className="caveats">
              <h4>Three caveats travel with this result</h4>
              <p><b>(a)</b> The design is conservative and biases toward the null — each held-out positive
                is ranked among a pool still containing the training positives.</p>
              <p><b>(b)</b> Now tested, not open (F-005). Two of the six features — the{' '}
                <Term name="pLDDT">pLDDT</Term> features — carry the result; the four geometry features
                add little. F-004's specific worry was that <Term name="pLDDT">pLDDT</Term> proxies
                research attention through <Term name="ESMFold">ESMFold</Term>'s training-set
                representation. <b>That is not supported</b>: the pLDDT-only ablation aligns <i>less</i>{' '}
                with the comparator, not more — the opposite of what the attention mechanism predicts.
                What remains open is whether pLDDT reflects that attention or a genuine
                order-versus-disorder structural signal, which this design cannot separate.</p>
              <p><b>(c)</b> The top of the distribution is the famous targets — consistent with signal and
                equally consistent with (b). Not narrated as validation.</p>
            </div>

            {/* D-066 §2: the deferred-columns note lives under section D now, not in the ranking column */}
            <p className="deferred">
              Deferred columns, named rather than faked: baseline rank, delta, disagreement class, and
              per-feature attribution. The <b>β·x attributions are stored</b> in the result and simply
              not yet rendered — a display gap, not a data gap.
            </p>
          </section>
        </div>

        {/* ── E — the coverage box and the ranking table (D-066: box + table only) ── */}
        <div className="scorer-ranking">
          <section className="scorer-table">
            <h3>E · The ranking table</h3>
            {/* the coverage box: the D-024 partition plus the three named exclusions (D-062 requires
                them reachable) — both are part of the coverage statement, so they travel together */}
            <div className="coverage-box">
              <CoverageLine coverage={coverage.coverage} rows={coverage.rows} />
              <details className="excluded-set">
                <summary>Excluded from ranking ({(r.excluded || []).length}) — three reasons</summary>
                <ul>
                  {(r.excluded || []).map(([sym, reason]) => (
                    <li key={sym}>{sym} — {reason}</li>
                  ))}
                </ul>
              </details>
            </div>
            {/* D-066 dec 2: the reconciliation the box cannot make — all three numbers derived —
                immediately above the table it explains. 67 (ranked & folded) → 56 (above the floor). */}
            <p className="ranking-reconciliation">
              <b>{rankedFolded}</b> ranked · <b>{r.n_ranking_set}</b> above the pLDDT-{r.plddt_floor}{' '}
              floor · these <b>{r.n_ranking_set}</b> are ranked below
            </p>
            <table className="ranking-table">
              <thead>
                <tr>
                  <th>Rank</th><th>Symbol</th>
                  <th>{scores.length
                    ? <ScoreColumnHeader scores={scores} labelledCount={r.n_fit_positives} rankingSetCount={r.n_ranking_set} />
                    : 'Score'}</th>
                </tr>
              </thead>
              <tbody>
                {ranking.rows.map((row) => (
                  <tr key={row.accession}>
                    <td>{row.rank}</td><td>{row.gene}</td><td>{f3(row.score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      </div>
    </div>
  )
}
