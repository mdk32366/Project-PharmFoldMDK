import { Link } from 'react-router-dom'

// The SECOND population on `/coverage` (D-135).
//
// ⚠⚠ WHAT THIS COMPONENT MUST NOT BE, stated before what it is. It is **not more coverage**. The
// coverage line above it states the D-024 partition over the cohort — `ranked ∧ folded` of the
// manifest's own denominator — and the entire point of D-024 is a denominator that does not grow
// with how much work has happened. A census count placed anywhere near that headline would be the
// most flattering version of exactly the failure D-024 exists to forbid, and it would be worse than
// the original, because the two numbers are measured under DIFFERENT SPAN DEFINITIONS (D-081) and
// so cannot be added even in principle.
//
// ⚠ So this is a POPULATION, not a fraction. There is no denominator here, no percentage, and no
// second coverage figure — the strip says how large the other population is and how its structures
// were produced, and it says whose numbers they are before it prints any of them.
//
// ⚠ Every count is DERIVED from `/api/census/summary` (Constraint A / D-050). Nothing here is typed:
// the kinds, their labels and their counts all arrive in `summary.structure_kinds`, in the payload's
// own order, so a kind the census acquires later appears without a UI change and a kind it does not
// hold is simply absent — never rendered as a zero, which is what the census truthfully showed for
// all 45 assembled parents before D-134 repaired the identity check.
//
// ⚠ Additive. `/coverage`'s job is the honest denominator; a census fetch that fails costs this
// strip and nothing else, so `summary == null` renders nothing at all rather than an empty frame.
export default function CensusPopulationStrip({ summary }) {
  if (!summary) return null
  const kinds = summary.structure_kinds ?? []
  const assembled = kinds.find((k) => k.kind === 'assembled')

  return (
    <section className="census-population panel">
      {/* ⚠⚠ THE LABEL IS THE FIRST THING, AND IT NAMES THE POPULATION. "A different population"
          rather than "more proteins": the reader has just been told the honest denominator is the
          cohort intersection, and the next number they meet is an order of magnitude larger. If
          they have to infer that it belongs to something else, most of them will not. */}
      <h3>A different population — the wider census</h3>
      <p className="census-population-bar">
        <strong>These are not more of the cohort, and they do not extend the denominator above.</strong>{' '}
        The census is a separate measurement of every human surface protein we could define a
        boundary for, cut under a <strong>different span definition</strong> — so a census count and
        a cohort count cannot be added, subtracted or compared. It is{' '}
        <strong>not scored and not ranked</strong>, and nothing here is a candidate list.
      </p>

      {/* ⚠ The two population sizes, each stating its own key — the same discipline the summary
          payload carries. A bare pair of numbers here would invite the reader to divide them. */}
      <dl className="census-population-figures">
        <div>
          <dt>{summary.manifest_rows?.toLocaleString()}</dt>
          <dd>proteins in the census, folded or not</dd>
        </div>
        <div>
          <dt>{summary.folded?.toLocaleString()}</dt>
          <dd>of them have a structure and a measured confidence</dd>
        </div>
      </dl>

      {kinds.length > 0 && (
        <>
          <p className="census-population-kinds-lede">
          {/* ⚠ HOW the structures were produced, which is the half `/coverage` had no way to
              say. A single-pass fold and a seam-assembled one are different products of the same
              network with different failure modes (D-133). */}
            How those structures were produced — open any of these in the census:
          </p>
          <ul className="census-population-kinds">
            {kinds.map((k) => (
              <li key={k.kind}>
                {/* ⚠⚠ THE COUNT OPENS. A figure a reader cannot check is a figure they have to
                    take on trust; `?structure=<kind>` lands on the filtered list with the same
                    count under it (D-135 decision 7). ⚠ The link is not an endorsement and the
                    chip is not a rank (D-079) — it narrows a list and orders nothing. */}
                <Link className="chip" to={`/census?structure=${k.kind}`}>
                  {k.label} {k.n.toLocaleString()}
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}

      {/* ⚠⚠ THE CAVEAT TRAVELS WITH THE LINK, exactly as it does beside the census chips
          themselves (D-133 am. 1: "the caveat arrives with the act"). Pointing a reader at the
          assembled proteins from the honesty page and NOT saying what an assembly is would use this
          page's own credibility to overstate them. ⚠ Count-free on purpose: the number is in the
          chip above, derived; repeating it in prose is a second place for it to go stale. */}
      {assembled && (
        <p className="caveat">
          ⚠ <strong>Assembled is provisional.</strong> The longest spans were folded as overlapping
          tiles and joined where they overlap by per-residue confidence — <strong>not
          superimposed</strong>. The seam is recorded, not solved, so &ldquo;assembled&rdquo; says
          how the structure was made and never how good it is. These proteins are not in the
          ranking.
        </p>
      )}
    </section>
  )
}
