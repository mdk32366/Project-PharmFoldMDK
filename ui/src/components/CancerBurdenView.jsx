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

// ⚠⚠ D-152 — THE SEARCH MATCHES THE LABEL THIS PAGE ACTUALLY PRINTS, AND NOT THE SHARED PROTEIN
// MATCHER. `../searchRows.js` looks at `accession`, `gene`, `label`, `description` and `aliases`;
// a burden row has none of those, and this route carries no accession, no gene, no score and no
// rank BY DESIGN (D-149's wall). Importing the protein matcher here would have been the one line
// that put a protein vocabulary on the surface that is defined by not having one — so the filter
// is three lines against `display_label`, which is the string the reader can see.
function matchesSite(row, query) {
  const q = query.trim().toLowerCase()
  if (!q) return true
  return String(row.display_label ?? '').toLowerCase().includes(q)
}

export default function CancerBurdenView() {
  const [statistic, setStatistic] = useState('mortality')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')

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
  // ⚠⚠ THE BAR SCALE IS THE FULL POPULATION'S MAXIMUM AND **NEVER** THE FILTERED ONE (D-152).
  // This is the one place a search box could tell a lie on this surface: re-normalising the bars to
  // whatever is on screen would draw a rare cancer at full width the moment a reader typed its
  // name, and a bar chart's whole claim is that length is comparable. So `max` is computed from
  // `ranked` before any filtering, the search HIDES bars and never rescales them, and a filtered
  // view of the bars is a subset of the same chart rather than a new one.
  const max = ranked.length ? Math.max(...ranked.map(barValue)) : 0
  const substituted = rows.filter((r) => r.sex_substituted)
  const shownRanked = ranked.filter((r) => matchesSite(r, query))
  const narrowed = shownRanked.length !== ranked.length

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

      {/* ⚠⚠ THE ERROR IS A STATEMENT AND THE PAGE AROUND IT STAYS UP (D-152). `/api/cancer-burden`
          is returning HTTP 500 on the deployed app as this ships — a load/ops matter held elsewhere
          and deliberately NOT fixed here. What this ship owes it is that the failure renders as a
          failure: the heading, the US-only bar and the statistic toggle are above this line and
          survive it, so the surface says *the request failed* rather than going blank, which reads
          as *there is no cancer burden data*. "Nothing matched", "not loaded" and "the request
          failed" are three different facts and this page keeps them three. */}
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

          {/* ⚠⚠ D-152 — THE SEARCH SITS ABOVE THE BARS AND THE TABLE AND NARROWS BOTH. Owner,
              2026-09-09: *"Apply what was done for Census to the rest of the surfaces."* A reader
              looking for pancreas had to scan a fifteen-bar chart and then a twenty-odd-row table;
              the box answers *is it here, and where* in one keystroke.
              ⚠ It filters BY THE PRINTED LABEL, so what the reader types is what they can see. */}
          <div className="list-controls">
            <label htmlFor="burden-search">Search</label>
            <input
              id="burden-search"
              type="search"
              className="row-search"
              value={query}
              placeholder="cancer site, e.g. pancreas, lung, melanoma"
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          {narrowed && (
            <p className="note filter-count" data-testid="burden-filter-count">
              Showing {shownRanked.length} of {ranked.length} ranked SEER sites matching{' '}
              &ldquo;{query.trim()}&rdquo;.{' '}
              {/* ⚠⚠ THE TWO THINGS A FILTER MUST NOT BE ALLOWED TO IMPLY, SAID OUT LOUD. The bars
                  are still drawn against the full population's maximum, so a short bar is still
                  short; and the rank numbers are the rank WITHIN the statistic, not a position in
                  this filtered view — row #7 is the seventh deadliest site, not the seventh row on
                  screen. */}
              <strong>The bars keep the full ranking&rsquo;s scale and the numbers keep their
              rank</strong> — this hides rows, it does not re-rank or re-scale them.
              {shownRanked.length === 0 && <> Nothing here matches. SEER&rsquo;s site vocabulary is
                the one on screen — <em>Corpus and Uterus, NOS</em> rather than &ldquo;womb&rdquo;,
                and melanoma rather than &ldquo;skin cancer&rdquo; — so a miss may be a naming
                difference rather than an absent disease.</>}
            </p>
          )}

          {/* ── the bars ─────────────────────────────────────────────────────────── */}
          <ol className="burden-bars" aria-label={`${active.label} by cancer site`}>
            {shownRanked.slice(0, 15).map((r) => (
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
          {/* ⚠⚠ D-152 — THE BOUNDED PORT. Seven columns, three of which hold long strings (the
              SEER site name with the melanoma warning attached to one of them, the rate
              denominator, and the counted-in population), so the widest row was setting the width
              of the DOCUMENT and sliding the US-only bar sideways with it.
              ⚠ NO COLUMN IS DROPPED, and on this surface that is a rule rather than a preference:
              "Rate is over" and "Counted in" exist because the denominators differ per row, and a
              layout that dropped either would put two incomparable numbers side by side with
              nothing saying so — the exact defect D-149 built them to prevent. */}
          <div className="table-scroll">
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
                <th>Rate is over</th>
                <th>{active.key === 'mortality' ? 'Deaths' : 'New cases'}</th>
                <th>Counted in</th>
                <th>Period</th>
              </tr>
            </thead>
            <tbody>
              {shownRanked.map((r) => (
                <tr key={`${r.seer_site_id}-${r.sex}`}>
                  {/* ⚠ THE RANK IS THE RANK WITHIN THE STATISTIC, NOT THE ROW'S POSITION HERE. It
                      is served, never derived from the index — so a filtered table shows #1, #7,
                      #13 with gaps, which is the honest rendering: renumbering the visible rows
                      1,2,3 would invent a ranking of the reader's search string. */}
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
                  {/* ⚠⚠ WHAT THE "PER 100,000" IS OVER. A sex-specific rate is per 100,000 of THAT
                      SEX: Breast (female) at 132.53 is per 100,000 women while Lung at 47.17 is per
                      100,000 people. Both are published that way and ranking them together is the
                      standard convention — but the denominators differ, and it shows in this data:
                      by rate, female-only Corpus and Uterus outranks Melanoma of the Skin; by count
                      they reverse. Naming it per row makes the comparison a reader's choice. */}
                  <td className="col-secondary">{r.rate_denominator_label}</td>
                  <td className="mono">{formatCount(r.observed_count)}</td>
                  {/* ⚠ PER ROW, never a column header: the two statistics have different
                      denominators and a header would let one row's population be read onto another. */}
                  <td>{POPULATION_LABEL[r.count_population] ?? r.count_population}</td>
                  <td className="mono">{r.period}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>

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
              <li data-testid="burden-rate-denominator">
                <strong>&ldquo;Per 100,000&rdquo; is not one quantity.</strong>{' '}
                {meta.population_key?.rate_denominator?.text}
              </li>
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

            {/* ⚠⚠ THE NAMED FAILURES, BECAUSE THE PROTEIN CARD POINTS HERE FOR THEM. The
                ClinicalEdges burden slot says *"that page names which and why"* — so this list has
                to exist, or the card's pointer resolves to nothing. That is D-062's defect shape
                (a citation treated as settled while the thing cited was never written), one layer
                down: a UI pointer is a citation too. */}
            {meta.unmappable_hpa_sites && (
              <div className="burden-unmappable" data-testid="burden-unmappable">
                <h4>Tumour names in the protein atlas that do not map to a SEER site</h4>
                <dl>
                  {Object.entries(meta.unmappable_hpa_sites).map(([name, why]) => (
                    <div key={name} className="burden-unmappable-row">
                      <dt>{name}</dt>
                      <dd>{why}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
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
