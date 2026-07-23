// API client for the read API (D-034 / D-038). Same-origin: the bundle is served by the same
// Fly app under `/` (DEP-006), so relative paths need no base URL and no CORS.

async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(`${path} -> HTTP ${r.status}`)
  return r.json()
}

export const listAnalyses = () => getJSON('/api/analyses')
export const getAnalysis = (id) => getJSON(`/api/analyses/${id}`)
export const getPlddt = (id) => getJSON(`/api/analyses/${id}/plddt`)
export const getCoverage = () => getJSON('/api/coverage')

// 3Dmol.js takes the structure BY URL (D-034 decision 2) so the browser caches it independently
// of the metadata — never inline it in the detail JSON.
export const structureUrl = (id) => `/api/analyses/${id}/structure`
