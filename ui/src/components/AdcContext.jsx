import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses } from '../api.js'

// ADC framing / onboarding (UI Plan v2 §7): keep the metaphor (it is mechanism, not decoration),
// bound the outcome claims, and let the honest limits sharpen the purpose rather than soften it.
// The through-line: conviction about the mechanism, precision about the limits.
export default function AdcContext() {
  // D-050: the cohort statistics below are DERIVED from the live cohort, never hardcoded — a literal
  // count rots silently as the cohort grows (this copy once read "42 … 34.78 to 81.40 … 45%", stale
  // by 42->79). Folded = analyses carrying a numeric mean_plddt; 60 is the D-039 trust divider.
  const [stats, setStats] = useState(null)
  useEffect(() => {
    listAnalyses()
      .then((rows) => {
        const vals = rows
          .map((r) => r.mean_plddt)
          .filter((v) => typeof v === 'number' && !Number.isNaN(v))
        if (!vals.length) return
        const below = vals.filter((v) => v < 60).length
        // D-051 §5: NECTIN4's mean pLDDT was the last hardcoded per-target literal (77.26); derive
        // it from the same fetch. NECTIN4 is id 1 (the prose commits to that); fall back to gene.
        const nectin = rows.find((r) => r.gene === 'NECTIN4' || r.id === 1)
        setStats({
          n: vals.length,
          min: Math.min(...vals),
          max: Math.max(...vals),
          belowPct: Math.round((below / vals.length) * 100),
          nectin4: nectin && typeof nectin.mean_plddt === 'number' ? nectin.mean_plddt : null,
        })
      })
      .catch(() => setStats(null))
  }, [])

  return (
    <div className="prose">
      <h2>What an ADC is, and why target choice is the hard part</h2>

      <p>
        Conventional cytotoxic chemotherapy is an <strong>area weapon</strong>: it acts on rapidly
        dividing cells wherever they are, which is why its toxicity reads as a war of attrition — the
        treatment's reach is not the disease's shape. An <strong>antibody–drug conjugate</strong> is a
        guided munition:
      </p>
      <ul className="adc-parts">
        <li><strong>Antibody</strong> — guidance. It binds a protein the tumour over-expresses.</li>
        <li><strong>Linker</strong> — the fuse. It holds the payload inert in circulation.</li>
        <li><strong>Payload</strong> — the warhead. A cytotoxic released at the target cell.</li>
      </ul>
      <p>That is a genuine change in <em>delivery mechanism</em>, and the metaphor names it accurately.</p>

      <h3>What the mechanism does not license</h3>
      <p>
        The metaphor describes <strong>delivery</strong>, not <strong>outcomes</strong>. ADCs are a
        real and substantial advance — enfortumab vedotin targets <strong>NECTIN4</strong> and changed
        outcomes in urothelial carcinoma — but the payload is still cytotoxic, linkers deconjugate in
        circulation, and the class carries its own dose-limiting toxicities (interstitial lung disease,
        ocular effects, peripheral neuropathy, varying by agent). Resistance develops, notably through
        <strong> antigen downregulation</strong>: an ADC is only as good as its target.
      </p>

      <h3>Why this project exists</h3>
      <p>
        A target must be well-expressed on tumour cells, spare enough on healthy tissue, accessible to
        an antibody, and stable enough not to be simply switched off under pressure.{' '}
        <strong>Choosing well is the unsolved part — which is what this project is about.</strong>
      </p>
      <p>
        <strong>NECTIN4</strong> is the worked example. Enfortumab vedotin was approved for metastatic
        urothelial carcinoma — where patients past platinum chemotherapy and a checkpoint inhibitor had
        little left — and later displaced platinum in the first-line setting with pembrolizumab, the
        rarer achievement of a standard of care changing. It is <code>id 1</code> in this cohort, the
        first target folded through this system's production path{stats?.nectin4 != null && (
          <>, at mean pLDDT <strong>{stats.nectin4.toFixed(2)}</strong></>
        )}. <Link to="/target/1">See its structure →</Link>
      </p>

      <h3>⚠ The success case is a bad prior — and this cohort's own data shows it</h3>
      <p>
        NECTIN4 is well-expressed, accessible, and stable. <strong>Most candidates are not.</strong>{' '}
        {stats ? (
          <>Across the {stats.n} folded targets, mean pLDDT runs from{' '}
          <strong>{stats.min.toFixed(2)} to {stats.max.toFixed(2)}</strong>, and{' '}
          <strong>{stats.belowPct}% fall below 60</strong> — a region where the structure is not
          reliably interpretable.</>
        ) : (
          <>Across the folded targets, mean pLDDT spans a wide range and a substantial fraction fall
          below 60 — a region where the structure is not reliably interpretable.</>
        )}{' '}
        Enfortumab vedotin proves the <em>mechanism</em>; it says nothing about how easy
        the next target is. A tool built in admiration of the one that worked could quietly encode
        "find me more NECTIN4s" — and the{' '}
        <Link to="/coverage">honest coverage line</Link>, the confidence bands, and the
        detection-not-explanation boundary (<Link to="/method">method</Link>) are the discipline that
        prevents exactly that.
      </p>
      <p className="note">
        Conviction about the mechanism, precision about the limits. The mechanism is proven and worth
        being excited about; the target selection is where the difficulty actually lives; and a system
        honest about which is which is the more persuasive artefact, not the more timid one.
      </p>
    </div>
  )
}
