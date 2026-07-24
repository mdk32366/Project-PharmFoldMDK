import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The bundle is served by the same Fly app under `/` (DEP-006), with `/api` and `/jobs`
// matched first (route ordering — the trap orders §2a / DEP-006 name). Default base `/`
// puts hashed assets under `/assets`, which FastAPI mounts.
export default defineConfig({
  plugins: [react()],
  build: { outDir: 'dist' },
  // D-046: the vitest harness. Vite ignores this key; vitest reads it. `plugins` and `build`
  // above are untouched, so `vite build`'s output is byte-identical with or without vitest
  // installed. jsdom + globals + the jest-dom setup are what @testing-library/react needs to
  // assert on rendered output; nothing here is imported by any source module, so none of it
  // enters the bundle.
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test-setup.js',
  },
})
