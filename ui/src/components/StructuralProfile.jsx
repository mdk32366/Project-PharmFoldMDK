// The census structural profile — D-079 amendment 1, ruled by amendment 2 (2026-08-20).
//
// ⚠⚠ D-089 AND AMENDMENT 1 BOTH NAME THIS COMPONENT AS THE RISK: *"a census page still carries no
// scorer panel — a profile block must not become that page by another name."* A number in 0–1 on a
// protein page, rendered like a verdict, IS a scorer panel whatever the heading says. Four things
// keep it from being one, and all four are asserted in StructuralProfile.test.jsx:
//
//   1. THE WORD. It is a "structural profile", never a score, rank or suitability (ruling 1). The
//      component imports nothing from the target-side scorer panel and shares no class prefix.
//   2. THE BAND IS ALWAYS DRAWN. The value is never shown as a bare figure — it is placed against
//      the cohort's own 0.116–0.285, so a reader sees a narrow band, not a verdict. `F-006`.
//   3. THE REFUSAL IS THE SAME SIZE AS THE VALUE. A refused protein gets a stated category and
//      cause in the same slot, not a dash or an empty panel (ruling 3). *A blank is filled in by
//      the reader with an assumption.*
//   4. THE PRECONDITIONS ARE RENDERED, NOT LINKED. Ruling 4 puts them in the same frame; a
//      "read more" would put them in a different one.
//
// ⚠ It deliberately does NOT import plddt.js's band palette: a different quantity from a different
// source must not read as model confidence — the same reasoning CancerAssociations records.

export default function StructuralProfile({ block }) {
  if (!block) return null

  const refused = block.status === 'refused'
  const { cohort_fitted_min: lo, cohort_fitted_max: hi } = block.band_context
  // Position within the cohort's own fitted span, clamped for LAYOUT only — the value itself is
  // never clamped (ruling 3 forbids that), and a value outside the band is refused before it
  // reaches here, so this only guards against a rounding edge.
  const pct = refused ? null
    : Math.max(0, Math.min(100, ((block.structural_profile - lo) / (hi - lo)) * 100))

  return (
    <section className="sprofile">
      <h3>Structural profile</h3>

      <p className="sprofile-what">
        A structure-derived value, <strong>not a score and not a rank</strong>. It is the
        pre-registered model applied to this protein&rsquo;s six measured features. It says nothing
        about whether this protein is a good ADC target.
      </p>

      {refused ? (
        <div className="sprofile-refused">
          <p className="sprofile-refusal-cat">
            <strong>Refused — {block.refusal.category.replace(/_/g, ' ')}</strong>
          </p>
          <p className="sprofile-refusal-why">{block.refusal.detail}</p>
          {block.out_of_range_features.length > 0 && (
            <p className="sprofile-oor">
              Outside the range the model was fitted on:{' '}
              <strong>{block.out_of_range_features.join(', ')}</strong>.
            </p>
          )}
          <p className="sprofile-refusal-note">
            No value is shown because none was computed. A number produced by extrapolating past
            the fitted range would look like the others and mean something different.
          </p>
        </div>
      ) : (
        <div className="sprofile-value">
          <p className="sprofile-figure">{block.structural_profile.toFixed(4)}</p>
          <div className="sprofile-band" aria-hidden="true">
            <div className="sprofile-band-fill" style={{ left: `${pct}%` }} />
          </div>
          <p className="sprofile-band-label">
            against the cohort&rsquo;s own fitted values, which span{' '}
            <strong>{lo}</strong>&nbsp;&ndash;&nbsp;<strong>{hi}</strong>
          </p>
          <p className="sprofile-band-note">{block.band_context.note}</p>
        </div>
      )}

      <details className="sprofile-bar">
        <summary>How the range test works</summary>
        <p>{block.bar}</p>
        <p className="sprofile-prov">{block.provenance}</p>
      </details>

      <div className="sprofile-mount">
        <h4>What this value does not tell you</h4>
        <ul>
          {block.mount_preconditions.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      </div>
    </section>
  )
}
