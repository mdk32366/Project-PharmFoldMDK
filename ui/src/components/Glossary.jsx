import { GLOSSARY } from '../glossary.js'

// D-055: the glossary block, rendered on /method. Every term the interface uses, with what the
// letters stand for and one plain sentence. Sourced from glossary.js (the single definition store),
// so it cannot drift from the inline <Term> usages.
export default function Glossary() {
  const terms = Object.keys(GLOSSARY).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()))
  return (
    <section className="glossary">
      <h3>Glossary — every term on one page</h3>
      <dl>
        {terms.map((name) => (
          <div className="glossary-entry" key={name}>
            <dt>{name} <span className="glossary-expansion">({GLOSSARY[name].expansion})</span></dt>
            <dd>{GLOSSARY[name].plain}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
