// D-046: vitest setup. Registers @testing-library/jest-dom's matchers (toBeInTheDocument,
// toHaveTextContent, …) on the global `expect` so component tests can assert on rendered output
// the way a reader encounters it. Loaded only via vite.config.js's `test.setupFiles`; it is not
// imported by any source module and never enters the build.
import '@testing-library/jest-dom'
