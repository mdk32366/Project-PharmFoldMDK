// PR A is the plumbing only (orders §1): one hardcoded line that proves the bundle builds,
// ships in the two-stage image (DEP-006), and serves at pharmfoldmdk.fly.dev with /api and
// /jobs intact (route ordering). The API client + target view (structure viewer coloured by
// pLDDT, provenance panel) are PR B; the coverage view is PR C. No data is fetched here yet —
// deliberately, so PR A stays tiny and the deploy path is what's under test.
export default function App() {
  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', maxWidth: '42rem', margin: '4rem auto', padding: '0 1rem' }}>
      <h1>PharmFoldMDK</h1>
      <p>ADC target exploration — serving tier live. UI arc: PR A (shell).</p>
    </main>
  )
}
