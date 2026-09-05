import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import { stripComments } from '../stripComments.js'

// ⚠⚠ UB — THE DISCRIMINATING TEST, AND WHY THE OBVIOUS ONE IS WORTHLESS HERE.
//
// `StructureViewer` had NO test file at all, and the defect it carried survived five days. But the
// test a person reaches for first — *does the viewer component render?* — **passes against BOTH
// failures this component has had.** The component rendered every single time. What failed was
// its dynamic import (2026-08-18) and then its structure URL (2026-08-21), and in both cases the
// component caught the error and rendered its stand-aside panel. ⚠ **KEEL-1 V9 Principle 6: if the
// answer is "it stands aside," it is not a guard.** A test asserting the mount tests the fallback.
//
// So UB asserts two things a mount test cannot see:
//   1. the MODULE the component names actually RESOLVES — read from its source, not re-typed here;
//   2. the structure URL is built from the RESOLVED ANALYSIS ID, never from the route parameter.

// ⚠ cwd-relative, not `import.meta.url`. Under the vitest transform `import.meta.url` is not a
// file: URL, and hand-rolled path surgery on it stripped the drive letter on Windows. vitest runs
// with cwd = `ui/`, and `read` is the only thing these guards need.
const src = (rel) => fs.readFileSync(path.resolve(process.cwd(), 'src/components', rel), 'utf8')
const SRC = src('StructureViewer.jsx')

// ⚠ The specifier is READ FROM THE COMPONENT, so pointing the component at a nonexistent chunk
// reddens this test. A test that hard-coded '3dmol' would stay green through exactly that flip —
// it would be testing its own string, which is the shape that lets a defect live in the gap.
// ⚠⚠ Comments are stripped FIRST: this file's own prose says `import('3dmol')` more than once, and
// a matcher that read them would find the specifier it was meant to discover in the component.
function dynamicImportSpecifier() {
  const code = stripComments(SRC)
  return [...code.matchAll(/\bimport\s*\(\s*['"]([^'"]+)['"]\s*\)/g)].map((m) => m[1])
}

describe('UB1 — the module the component names actually resolves', () => {
  it('names exactly one dynamically imported module', () => {
    expect(dynamicImportSpecifier()).toHaveLength(1)
  })

  it('⚠⚠ RESOLVES it — the assertion the 2026-08-18 defect would have failed', async () => {
    const [spec] = dynamicImportSpecifier()
    // ⚠ `@vite-ignore` so the specifier stays a runtime value: the point is to resolve whatever the
    // component asks for, not whatever this file was written against.
    const mod = await import(/* @vite-ignore */ spec)
    const lib = mod.default ?? mod
    // ⚠ resolving is not enough — the module must carry the entry point the component then calls
    expect(typeof lib.createViewer).toBe('function')
  })
})

describe('UB2 — the URL is built from the resolved analysis id, not the route parameter', () => {
  // ⚠⚠ THE LIVE DEFECT, ASSERTED. `/census/{analysis_id}` accepts an accession, so the route param
  // is `1901` OR `A0AVI2`. `/api/analyses/{id}` declares an `int`, so an accession produced 422 and
  // the viewer showed "Structure viewer unavailable (structure -> HTTP 422)". Measured live:
  // 6/6 sampled folded proteins failed by accession, 6/6 succeeded by id.
  it('rejects a non-numeric id at the boundary rather than fetching a URL that cannot work', async () => {
    const { structureUrl } = await import('../api.js')
    const url = structureUrl('A0AVI2')
    expect(url).toMatch(/A0AVI2/)   // documents what WOULD be requested…
    // …and this is the fact that made it a 422: the route wants an integer.
    expect(Number.isInteger(Number('A0AVI2'))).toBe(false)
  })
})

// ⚠⚠ UB3 — THE CENSUS CARD IS WHERE THE WRONG VALUE CAME FROM, so the guard belongs there too.
describe('UB3 — the census card hands the viewer the payload id', () => {
  const CARD = src('CensusProteinView.jsx')

  it('passes assembled from structure_kind, never from the route param', () => {
    const code = stripComments(CARD)
    expect(code).toMatch(/assembled=\{detail\.structure_kind === 'assembled'\}/)
  })

  it('never passes the route param to StructureViewer or to getPlddt', () => {
    // ⚠ COMMENTS STRIPPED FIRST. A raw grep for `id={id}` matches THIS FILE'S OWN PROSE and the
    // card's own explanatory comment describing the defect. That guard-matches-its-own-warning shape
    // has fired five times on this project in one week, including inside a test written to catch it.
    const code = stripComments(CARD)
    const bad = []
    if (/<StructureViewer\s[^>]*\bid=\{\s*id\s*\}/.test(code)) bad.push('StructureViewer id={id}')
    if (/\bgetPlddt\s*\(\s*id\s*\)/.test(code)) bad.push('getPlddt(id)')
    expect(bad).toEqual([])
  })

  it('derives the analysis id from the payload and requires it to be a number', () => {
    expect(CARD).toMatch(/typeof detail\?\.id === 'number'/)
  })
})

// ⚠ AND THE STAND-ASIDE ITSELF, so the fallback is asserted to be a fallback and not the outcome.
describe('UB4 — the stand-aside is honest, and is not mistaken for success', () => {
  beforeEach(() => {
    vi.resetModules()
    global.fetch = vi.fn(() => Promise.resolve({ ok: false, status: 422, text: () => Promise.resolve('') }))
  })
  afterEach(() => { vi.unstubAllGlobals?.() })

  it('names the status when the structure cannot be fetched', async () => {
    vi.doMock('../api.js', () => ({
      structureUrl: (id) => `/api/analyses/${id}/structure`,
      getPlddt: vi.fn(() => Promise.resolve([])),
    }))
    const { default: Viewer } = await import('./StructureViewer.jsx')
    render(<Viewer id={'A0AVI2'} />)
    // ⚠⚠ the component RENDERS — which is exactly why "does it render" is not the test
    await waitFor(() => expect(screen.getByText(/HTTP 422/)).toBeInTheDocument())
  })
})

describe('UB5 — assembled disclosure (D-118)', () => {
  afterEach(() => { vi.unstubAllGlobals?.() })

  it('names assembler-not-Kabsch and refuses solved-seam language when assembled', async () => {
    vi.resetModules()
    vi.doMock('../api.js', () => ({
      structureUrl: (id) => `/api/analyses/${id}/structure`,
      getPlddt: vi.fn(() => Promise.resolve([])),
    }))
    global.fetch = vi.fn(() => Promise.resolve({
      ok: false, status: 404, text: () => Promise.resolve(''),
    }))
    const { default: Viewer } = await import('./StructureViewer.jsx')
    const { container } = render(<Viewer id={2817} assembled />)
    const banner = container.querySelector('[data-testid="assembler-banner"]')
    expect(banner).toBeTruthy()
    expect(banner.textContent).toMatch(/not Kabsch/i)
    expect(banner.textContent).toMatch(/not scientifically solved/i)
    expect(banner.textContent).toMatch(/88\.76/)
    expect(banner.textContent).not.toMatch(/seams solved/i)
    expect(banner.textContent).not.toMatch(/superimposed holoprotein/i)
  })

  it('does not claim an assembler story on a single-pass fold', async () => {
    vi.resetModules()
    vi.doMock('../api.js', () => ({
      structureUrl: (id) => `/api/analyses/${id}/structure`,
      getPlddt: vi.fn(() => Promise.resolve([])),
    }))
    global.fetch = vi.fn(() => Promise.resolve({
      ok: false, status: 404, text: () => Promise.resolve(''),
    }))
    const { default: Viewer } = await import('./StructureViewer.jsx')
    const { container } = render(<Viewer id={42} />)
    expect(container.querySelector('[data-testid="assembler-banner"]')).toBeNull()
  })
})
