import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getRanking, getCoverage } from '../api.js'
import { filterRows } from '../searchRows.js'
import CoverageLine from './CoverageLine.jsx'
import Term from './Term.jsx'
import PlddtAmbiguityNote from './PlddtAmbiguityNote.jsx'

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
  // ⚠⚠ D-152 — AN UNRECOGNISED STATUS IS A STATED CATEGORY, NOT A CRASH. `FullResult` reads
  // `ranking.result.distribution` on its first line, so any payload that reached here without a
  // `result` threw and took the whole route to a blank page — no heading, no nav, nothing saying
  // what happened. That is the shape this ship is fixing on `/cancer-burden`, one surface along:
  // **"nothing matched", "not loaded" and "the request failed" must not look the same, and none of
  // them may look like an empty page.**
  // ⚠ It states what it DOES NOT KNOW rather than guessing. `not_run` would be a claim (no result
  // has been recorded); this branch cannot make that claim, so it reports the status it was handed
  // and says the surface does not recognise it. An absence with no cause must say it has no cause.
  if (!ranking.result) {
    return (
      <div className="scorer">
        <h2>The scorer result</h2>
        <p className="scorer-status not-run" data-testid="scorer-unrecognised">
          The ranking supplier returned no result body{status ? ` with status “${status}”` : ''}.
          Nothing is being estimated in its place, and this is a failure to retrieve a result —{' '}
          <strong>not</strong> a statement that no result exists.
        </p>
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
  // ⚠⚠ DERIVED FROM EVERY ROW OF THE RUN, AND **NEVER** FROM THE FILTERED SET (D-152). The Score
  // header's tooltip reports the span, the median and the count of the scores IN THIS RUN — a
  // statistic about the pre-registered result, not about what is currently on screen. Deriving it
  // from `shown` would let a reader typing in a search box rewrite a published number and watch the
  // median move, which is the F-004 result reported as a function of a text input.
  const scores = ranking.rows.map((row) => row.score)                     // for the Score-column tooltip (derived)
  const rankedFolded = coverage.rows.filter(                              // the D-024 disposition count (67 live)
    (x) => x.disposition === 'ranked' && x.fold_status === 'folded').length

  return (
    <div className="scorer">
      <h2>The scorer result</h2>
      {/* ⚠ D-132 — the count moved from 27 to 45; the RULING did not move. These parents
          are disclosed here and are not in the fit, the persist path, or the table. The
          27 stays named as the 2026-09-05 wave slice inside the 45 so this line cannot be
          read as "Wave1+Wave2 were 45 all along". */}
      <p className="note scorer-assembly-note" data-testid="scorer-assembly-note">
        The 45 unique assembled parents (measured 2026-09-08; of them the 2026-09-05
        Wave1+Wave2 closeout slice is 27 — Wave1 PASS 10 + Wave2 PASS 17) are not in
        this ranking (D-109).
      </p>
      {partial && (
        <p className="scorer-status partial">
          Partial result — some pre-registered statistics are blocked. {r.status_detail}
        </p>
      )}

      {/* two-column: explanation left (A–D), the ranking table right (E). Stacks on narrow.
          ⚠⚠ D-152 REVERSED THE SOURCE ORDER: the ranking table (E) is now the FIRST child and the
          explanation the second. Owner, 2026-09-09: *"Apply what was done for Census to the rest of
          the surfaces."* D-151's first rule is that the thing the reader came for comes first, and
          on a page called *the scorer result* that is the ranked table — which used to be the
          second column in the DOM, so on a stacked (narrow) viewport it came after four sections
          and roughly 4,000 characters of explanation.
          ⚠ SOURCE ORDER, NOT A CSS `order`. A grid `order` would move the box and leave the
          reading order — the one a screen reader follows, and the one a narrow viewport collapses
          to — exactly as it was, which is the version of this change that looks fixed and is not.
          ⚠ NOTHING WAS TRADED FOR IT. Section D still carries the two pre-registered outcomes and
          all three caveats, uncollapsed, and the coverage line still precedes the table it
          qualifies, because both facts are properties of source order and source order is what
          moved. */}
      <div className="scorer-cols">
        {/* ── E — the coverage box and the ranking table (D-066: box + table only) ── */}
        <ScorerRanking ranking={ranking} coverage={coverage} r={r} scores={scores}
                       rankedFolded={rankedFolded} />

        <div className="scorer-explain">
          {/* ⚠⚠ D-152 — A, B AND C COLLAPSE INTO ONE DISCLOSURE; D DOES NOT. The line is drawn by
              what the block IS, not by its length: A (the cascade), B (the labels) and C (the
              pre-registration) are how the result was ARRIVED AT, and D is the result — including
              the first negative outcome FIRING, the second not firing, and the three caveats that
              travel with them. A caveat behind a `<summary>` is a caveat the page has decided the
              reader may skip, which is the one thing this surface may never do.
              ⚠ Collapsed is not cut: every date, every count and every named exclusion is in the
              DOM, findable by the browser's own page search, and read unchanged by every assertion
              in `ScorerView.test.jsx`.
              ⚠ It is not `open` — an `open` default restores the exact scroll it was collapsed to
              end while looking like a fix. */}
          <details className="surface-notes scorer-background">
            <summary>
              How the cohort narrows to the fit set, where the labels come from, and what was fixed
              before the run (A · B · C)
            </summary>

          {/* ── A — the cascade ── */}
          <section className="scorer-cascade">
            <h3>A · From the cohort to the fit set</h3>
            <ol className="cascade">
              {/* F-009 — the cohort line presented Kathad as "the cohort" with no comparator/census
                  distinction. The qualifier LINKS to /about rather than repeating the paragraph, so
                  the framing has one source and cannot drift between two surfaces. */}
              <li>
                <b>{coverage.coverage.denominator}</b> cohort targets (Kathad et al.)
                <span className="removes">
                  {' '}— a comparator cohort, not a census; clinically-validated ADC targets fall
                  outside it (<Link to="/about">see About</Link>)
                </span>
              </li>
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
          </details>

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
              {/* D-069 dec 2: caveat (b)'s core is the shared PlddtAmbiguityNote — one source, also
                  rendered on the target scorer panel, so the claim can't drift. Scorer frames it; it
                  does not restate it. */}
              <div className="caveat-b">
                <p><b>(b) Now tested, not open (F-005).</b> The sensitivity result, stated where the reader forms the impression:</p>
                <PlddtAmbiguityNote />
              </div>
              <p><b>(c)</b> The top of the distribution is the famous targets — consistent with signal and
                equally consistent with (b). Not narrated as validation.</p>
            </div>

            {/* D-066 §2: the deferred-columns note lives under section D now, not in the ranking column */}
            <p className="deferred">
              Deferred columns, named rather than faked: baseline rank, delta, and disagreement class.
              <b> Per-feature attribution now renders on each target's page</b> (D-068) — not yet as a
              column in this table.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

/**
 * ⚠⚠ D-152 — SECTION E, EXTRACTED SO THE SEARCH CAN HOLD ITS OWN STATE, AND MOVED TO THE FRONT.
 *
 * The extraction is mechanical: the coverage box, the reconciliation line and the ranking table are
 * the same markup they were, in the same order, with a search box added above the table. It is a
 * component rather than inline JSX only because `FullResult` had no hooks and adding one there
 * would have put a `useState` above four sections of prose that do not use it.
 *
 * ⚠ THE SEARCH FILTERS THE ROWS AND **NOTHING ELSE**. `scores` (the Score header's distribution
 * tooltip), `n_ranking_set`, `rankedFolded` and the reconciliation line are all properties of the
 * pre-registered RUN, and every one of them is computed from the full payload by the caller. A
 * filter that could move a published median would make the F-004 result a function of a text input.
 */
function ScorerRanking({ ranking, coverage, r, scores, rankedFolded }) {
  const [query, setQuery] = useState('')
  // ⚠ The shared matcher (`../searchRows.js`), which reaches aliases — so `HER2` finds `ERBB2` here
  // exactly as it does on `/targets` and `/census`. A local `includes()` would have been the fourth
  // spelling of one behaviour, which is `F-052`.
  const shown = filterRows(ranking.rows, query)
  const narrowed = shown.length !== ranking.rows.length

  return (
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
            immediately above the table it explains. 67 (ranked & folded) → 56 (above the floor).
            ⚠ D-152: these three numbers describe the RUN and do not move when the search narrows
            the view. The line below states what is on screen; this one states what was ranked. */}
        <p className="ranking-reconciliation">
          <b>{rankedFolded}</b> ranked · <b>{r.n_ranking_set}</b> rankable after the pLDDT-{r.plddt_floor}{' '}
          floor · the table below shows those <b>{r.n_ranking_set}</b>
        </p>
        <div className="list-controls">
          <label htmlFor="scorer-search">Search</label>
          <input
            id="scorer-search"
            type="search"
            className="row-search"
            value={query}
            placeholder="gene, accession, or a name like HER2"
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {/* ⚠⚠ A FILTERED TABLE UNDER AN UNQUALIFIED TOTAL IS THE DEFECT THE LINE ABOVE WOULD
            OTHERWISE BECOME: it says *the table below shows those 56*, which stops being true the
            moment a reader types. So the filtered count states itself, and it states that the
            ranking is unchanged — a row absent from a filtered view has not been excluded from the
            run, and on a surface about pre-registration that distinction is the whole point. */}
        {narrowed && (
          <p className="note filter-count">
            Showing {shown.length} of {ranking.rows.length} ranked rows matching{' '}
            &ldquo;{query.trim()}&rdquo;
            {shown.length === 0 && <> — nothing here matches. A target can be in the cohort and
              absent from this table: {r.n_ranking_set} of the cohort cleared the pLDDT-{r.plddt_floor}{' '}
              floor, and the rest are named in the coverage box above rather than hidden.</>}
            {' '}<strong>The ranking itself is unchanged</strong> — this filters the view, not the run.
          </p>
        )}
        {/* ⚠ D-152: the bounded port, for the same reason as every other list this ship touched —
            the sticky `<thead>` resolves against it, so the rank and the score keep their column
            names as 56 rows scroll past. */}
        <div className="table-scroll">
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
            {shown.map((row) => (
              <tr key={row.accession}>
                <td>{row.rank}</td><td>{row.gene}</td><td>{f3(row.score)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </section>
    </div>
  )
}
