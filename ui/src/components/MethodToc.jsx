import { useEffect, useState } from 'react'

// D-138: the contents rail for `/method`. ⚠ The entries are READ OFF THE RENDERED HEADINGS, not
// listed here. A hand-kept contents list is a second place the section names live, and this page
// has grown a section per stitch path since D-121 — a list typed here would eventually name a
// section the page does not have, which is the ghost-entry failure the GO forbids. Deriving means
// the rail can be wrong in only one direction (a heading without an `id` goes missing), and the
// test file asserts that direction closed by requiring an `id` on every h2/h3 in the body.
export default function MethodToc({ bodyRef }) {
  const [entries, setEntries] = useState([])
  const [active, setActive] = useState(null)

  useEffect(() => {
    const body = bodyRef.current
    if (!body) return
    setEntries(
      Array.from(body.querySelectorAll('h2[id], h3[id]')).map((h) => ({
        id: h.id,
        level: Number(h.tagName.slice(1)),
        label: h.textContent.trim(),
      })),
    )
  }, [bodyRef])

  // A `/method#<section>` link arrives before the prose is mounted, so the browser's own attempt at
  // the hash has already failed by the time the heading exists.
  useEffect(() => {
    const body = bodyRef.current
    if (!body || entries.length === 0) return
    const id = body.ownerDocument.defaultView?.location?.hash?.slice(1)
    if (!id) return
    const target = body.ownerDocument.getElementById(id)
    if (target && typeof target.scrollIntoView === 'function') target.scrollIntoView()
  }, [bodyRef, entries])

  // Nice-to-have, and cheap: highlight the section being read. Guarded, because a browser without
  // IntersectionObserver (and jsdom) must still get a working set of links rather than a crash.
  useEffect(() => {
    const body = bodyRef.current
    if (!body || entries.length === 0) return
    const view = body.ownerDocument.defaultView
    if (!view || typeof view.IntersectionObserver !== 'function') return
    const onScreen = new Set()
    const observer = new view.IntersectionObserver(
      (records) => {
        for (const record of records) {
          if (record.isIntersecting) onScreen.add(record.target.id)
          else onScreen.delete(record.target.id)
        }
        const first = entries.find((e) => onScreen.has(e.id))
        if (first) setActive(first.id)
      },
      // Only the top slice of the viewport counts, so the active entry is the section you are
      // reading rather than whichever one happens to be last on a tall screen.
      { rootMargin: '0px 0px -70% 0px' },
    )
    for (const entry of entries) {
      const heading = body.ownerDocument.getElementById(entry.id)
      if (heading) observer.observe(heading)
    }
    return () => observer.disconnect()
  }, [bodyRef, entries])

  if (entries.length === 0) return null

  const jump = (event, id) => {
    const body = bodyRef.current
    const target = body?.ownerDocument.getElementById(id)
    // No scrollIntoView (jsdom, very old browsers) → fall through to the href, which is a real
    // fragment link and jumps on its own.
    if (!target || typeof target.scrollIntoView !== 'function') return
    event.preventDefault()
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setActive(id)
    const view = body.ownerDocument.defaultView
    if (view?.history?.replaceState) view.history.replaceState(null, '', `#${id}`)
  }

  return (
    <nav className="method-toc" aria-label="Method contents" data-testid="method-toc">
      <details open>
        <summary>Contents</summary>
        <ol>
          {entries.map((entry) => (
            <li key={entry.id} className={`toc-h${entry.level}`}>
              <a
                href={`#${entry.id}`}
                className={entry.id === active ? 'toc-active' : undefined}
                aria-current={entry.id === active ? 'true' : undefined}
                onClick={(event) => jump(event, entry.id)}
              >
                {entry.label}
              </a>
            </li>
          ))}
        </ol>
      </details>
    </nav>
  )
}
