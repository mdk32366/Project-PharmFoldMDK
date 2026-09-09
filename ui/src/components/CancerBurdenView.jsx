import { useEffect, useState } from 'react'
import { getCancerBurden } from '../api.js'

// D-149 — the dedicated cancer burden surface: which cancers kill the most people in the United
// States, and how many are diagnosed. SEER official aggregate statistics, served by
// GET /api/cancer-burden.
//
// ⚠⚠ ITS OWN ROUTE, AND THAT IS THE PRODUCT DECISION. It is deliberately NOT a panel on Method,
// not a column on Census, and not a section of Scorer. A burden figure sitting on a scoring surface
// is one glance from being read as an input to the score — and that is precisely the "cancer ×"
// composite this project has refused three times (D-143, D-144, D-146). The separation is
// structural: this page fetches one route, and that route carries no accession, gene, score or rank.
//
// ⚠⚠ US-ONLY RIDES ON THE HEADER, ON THE TABLE CAPTION, ON EVERY BAR AND ON EVERY ROW. Not a
// tooltip and not a footnote: "lung cancer kills 662,721 people" is a sentence about the United
// States that reads as a sentence about the world, and a row lifted into a slide must take the
// qualifier with it.
//
// ⚠⚠ THE TOGGLE SWITCHES THE RANKING BASIS AS WELL AS THE STATISTIC, AND SAYS SO. Deaths are
// ordered by COUNT — a US mortality count is national (NCHS), so "the most deaths" is a real
// national answer. Incidence is ordered by RATE, because a SEER incidence count covers the registry
// catchment areas only. Ordering incidence by count would rank a partial-US number as a national
// one. The server decides the basis and states it in `rank_basis`; this component renders that
// decision rather than making its own.

const STATISTICS = [
  { key: 'mortality', label: 'Deaths', question: 'Which cancers kill the most people in the US?' },
  { key: 'incidence', label: 'New cases', question: 'Which cancers are diagnosed most in the US?' },
]

// ⚠ The value the bars are drawn from is whatever the SERVER ranked on. A component that picked its
// own bar metric could draw bars in one order and number them in another, and nothing would redden.
function barValue(row) {
  return row.rank_basis === 'rate_per_100k' ? row.rate_per_100k : row.observed_count
}

function formatCount(n) {
  return typeof n === 'number' ? n.toLocaleString('en-US') : '—'
}

function formatRate(n) {
  return typeof n === 'number' ? n.toFixed(2) : '—'
}

// ⚠⚠ THE COUNT COLUMN NAMES ITS OWN POPULATION, ON EVERY ROW. On this release Lung and Bronchus
// carries 662,721 deaths and 434,448 new cases — more deaths than cases, which is impossible in one
// population and unremarkable in two. A reader who compares those two numbers has been misled by
// the layout, so the layout refuses to invite it.
const POPULATION_LABEL = {
  us_total_nchs: 'whole US (NCHS)',
  seer_registries: 'SEER registry areas only',
}

export default function CancerBurdenView() {
  const [statistic, setStatistic] = useState('mortality')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let live = true
    setData(null)
    setError(null)
    getCancerBurden(statistic)
      .then((d) => { if (live) setData(d) })
      .catch((e) => { if (live) setError(e.message) })
    return () => { live = false }
  }, [statistic])

  const active = STATISTICS.find((s) => s.key === statistic) ?? STATISTICS[0]

  // ⚠ The meta block is rendered from the payload, never from a constant in this file. A second copy
  // of the disclaimer in the bundle is a second source, and the two would drift.
  const meta = data?.meta ?? null
  const rows = data?.rows ?? []
  const ranked = rows.filter((r) => r.rank_within_statistic != null)
  const contextRow = rows.find((r) => r.is_context_row && r.sex === 'both')
  const max = ranked.length ? Math.max(...ranked.map(barValue)) : 0
  const substituted = rows.filter((r) => r.sex_substituted)

  return (
    <div className="burden">
      <h2>US cancer burden — deaths and new cases</h2>

      {/* ⚠⚠ THE FIRST THING ON THE PAGE, BEFORE ANY FIGURE. Placed above the toggle deliberately:
          a reader who changes the statistic must not scroll past the geography to do it. */}
      <p className="burden-us-only" data-testid="burden-us-only">
        <strong>United States only.</strong>{' '}
        {meta?.us_only ?? 'These are US figures and describe no other country.'}
      </p>

      <div className="burden-toggle" role="group" aria-label="Statistic">
        {STATISTICS.map((s) => (
          <button
            key={s.key}
            type="button"
            className={`burden-toggle-btn${s.key === statistic ? ' is-active' : ''}`}
            aria-pressed={s.key === statistic}
            onClick={() => setStatistic(s.key)}
          >
            {s.label}
          </button>
        ))}
      </div>
      <p className="burden-question">{active.question}</p>

      {error && <p className="error">Could not load cancer burden: {error}</p>}
      {!data && !error && <p className="loading">Loading cancer burden…</p>}

      {/* ⚠ `not_run` is a stated CATEGORY with the disclaimer and the credit still on screen, never
          a blank page — an empty surface reads as "there is no cancer burden data" rather than as
          "this database has not been loaded". */}
      {data?.result_status === 'not_run' && (
        <p className="burden-not-run" data-testid="burden-not-run">
          No burden run is loaded in this database yet. Nothing is being estimated in its place.
        </p>
      )}

      {data?.result_status === 'valid' && (
        <>
          {/* ── the release pin, so the figures have a date and a version ─────────── */}
          <p className="burden-release">
            <strong>{meta.release}</strong> · SEER*Explorer updated {meta.release_updated} ·{' '}
            {meta.site_vocabulary}
          </p>

          {/* ── the bars ─────────────────────────────────────────────────────────── */}
          <ol className="burden-bars" aria-label={`${active.label} by cancer site`}>
            {ranked.slice(0, 15).map((r) => (
              <li key={`${r.seer_site_id}-${r.sex}`} className="burden-bar-row">
                <span className="burden-bar-label">{r.display_label}</span>
                <span className="burden-bar-track">
                  <span
                    className="burden-bar-fill"
                    style={{ width: `${max ? (barValue(r) / max) * 100 : 0}%` }}
                  />
                </span>
                <span className="burden-bar-value">
                  {r.rank_basis === 'rate_per_100k'
                    ? `${formatRate(r.rate_per_100k)}/100k`
                    : formatCount(r.observed_count)}
                  {/* ⚠ ON EVERY BAR. The bar is the part that gets screenshotted. */}
                  <span className="burden-bar-badge">{r.disclaimer}</span>
                </span>
              </li>
            ))}
          </ol>

          {/* ── the table ────────────────────────────────────────────────────────── */}
          <table className="cohort-table burden-table">
            <caption>
              {active.label} by SEER cancer site — <strong>United States only</strong>. Ordered by{' '}
              {ranked[0]?.rank_basis === 'rate_per_100k'
                ? 'age-adjusted rate per 100,000'
                : 'observed deaths'}
              .{' '}
              {ranked[0]?.rank_basis === 'rate_per_100k'
                ? 'Incidence is ordered by RATE, not by count: a SEER incidence count covers the '
                  + 'registry catchment areas only, so ordering by count would rank a partial-US '
                  + 'number as though it were national.'
                : 'Deaths are ordered by COUNT because US mortality is a national count (NCHS).'}
            </caption>
            <thead>
              <tr>
                <th>#</th>
                <th>Cancer site (SEER)</th>
                <th>Rate per 100,000</th>
                <th>{active.key === 'mortality' ? 'Deaths' : 'New cases'}</th>
                <th>Counted in</th>
                <th>Period</th>
              </tr>
            </thead>
            <tbody>
              {ranked.map((r) => (
                <tr key={`${r.seer_site_id}-${r.sex}`}>
                  <td>{r.rank_within_statistic}</td>
                  <td>
                    {r.display_label}
                    {/* ⚠⚠ THE SKIN TRAP, ON THE ROW IT APPLIES TO. `Melanoma of the Skin` is never
                        relabelled "skin cancer": SEER's group is literally *Skin excluding Basal and
                        Squamous*, and BCC/SCC — most skin cancers — are not in SEER at all. A row
                        that said "skin cancer" would return a confident figure about a different
                        disease population (D-093 amd 6; F-047's class). */}
                    {r.seer_site_id === 53 && (
                      <span className="burden-skin-note" data-testid="burden-skin-note">
                        {' '}⚠ melanoma only — SEER excludes basal- and squamous-cell skin
                        carcinoma, which are most skin cancers. Not &ldquo;skin cancer&rdquo;.
                      </span>
                    )}
                  </td>
                  <td className="mono">{formatRate(r.rate_per_100k)}</td>
                  <td className="mono">{formatCount(r.observed_count)}</td>
                  {/* ⚠ PER ROW, never a column header: the two statistics have different
                      denominators and a header would let one row's population be read onto another. */}
                  <td>{POPULATION_LABEL[r.count_population] ?? r.count_population}</td>
                  <td className="mono">{r.period}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* ── the denominator, separated from the sites it contains ─────────────── */}
          {contextRow && (
            <p className="burden-context" data-testid="burden-context">
              <strong>For scale (not ranked above):</strong> {contextRow.display_label} —{' '}
              {formatCount(contextRow.observed_count)}{' '}
              {statistic === 'mortality' ? 'deaths' : 'new cases'} at{' '}
              {formatRate(contextRow.rate_per_100k)} per 100,000, {contextRow.period}. It contains
              every site in the table, so it is shown apart from them rather than ordered beside
              them.
            </p>
          )}

          {/* ── the honesty block ────────────────────────────────────────────────── */}
          <section className="burden-limits">
            <h3>What these numbers are, and what they are not</h3>
            <ul>
              <li><strong>United States only.</strong> {meta.us_only}</li>
              <li>
                <strong>The two counts are not comparable to each other.</strong>{' '}
                {meta.count_population_key?.seer_registries?.text}
              </li>
              <li><strong>Skin.</strong> {meta.skin_exclusion}</li>
              {substituted.length > 0 && (
                <li data-testid="burden-sex-substitution">
                  <strong>Sex is read from the source&rsquo;s answer, not from our question.</strong>{' '}
                  {meta.population_key?.sex?.text} {substituted.length} row(s) on this view carry a
                  recorded substitution.
                </li>
              )}
              {/* ⚠⚠ GLOBOCAN'S ABSENCE IS A STATED CATEGORY WITH A CAUSE, never a blank. An
                  unexplained absence reads as an oversight, and an oversight gets "fixed" by
                  someone who does not know why it is there. */}
              <li data-testid="burden-globocan"><strong>No worldwide figures.</strong> {meta.globocan}</li>
              <li><strong>Not the preliminary product.</strong> {meta.excluded_product}</li>
              <li><strong>No patient-level data.</strong> {meta.excluded_tier}</li>
              <li>
                <strong>Not joined to any score or rank.</strong> {meta.separation}
              </li>
              <li>
                <strong>No deep learning here, and that is deliberate.</strong>{' '}
                {meta.deep_learning_position}
              </li>
              <li><strong>No crosswalk to protein annotations.</strong> {meta.crosswalk_refused}</li>
            </ul>
          </section>

          {/* ── the licence obligation, at the bottom of the page and in the API ──── */}
          <p className="burden-attribution" data-testid="burden-attribution">
            {meta.attribution}{' '}
            <a href={meta.attribution_url} target="_blank" rel="noreferrer noopener">
              SEER*Explorer
            </a>
            {meta.source_sha256 && (
              <>
                {' '}· committed artefact <code className="mono">{meta.source_file}</code>{' '}
                sha256 <code className="mono">{meta.source_sha256.slice(0, 12)}…</code>
              </>
            )}
          </p>
        </>
      )}
    </div>
  )
}
