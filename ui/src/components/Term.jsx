import { GLOSSARY } from '../glossary.js'

// D-055: an inline glossary term. The definition must be reachable by KEYBOARD FOCUS and by TAP,
// not hover alone (orders §1c — hover doesn't exist on touch and is invisible to a keyboard). So the
// trigger is a real <button> (focusable, tappable) and the definition is a role="tooltip" node linked
// by aria-describedby (available to assistive tech on focus) and shown on :focus-within/:hover in CSS.
// An undefined term renders as plain text — the contract test is what catches that, not this component.
const slug = (name) => `gloss-${name.replace(/[^a-zA-Z0-9]+/g, '-')}`

export default function Term({ name, children }) {
  const entry = GLOSSARY[name]
  const label = children || name
  if (!entry) return <>{label}</>
  const definition = `${entry.expansion} — ${entry.plain}`
  const id = slug(name)
  return (
    <span className="term">
      <button type="button" className="term-trigger" aria-describedby={id}>{label}</button>
      <span role="tooltip" id={id} className="term-def">{definition}</span>
    </span>
  )
}
