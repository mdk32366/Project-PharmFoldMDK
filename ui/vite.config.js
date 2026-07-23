import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The bundle is served by the same Fly app under `/` (DEP-006), with `/api` and `/jobs`
// matched first (route ordering — the trap orders §2a / DEP-006 name). Default base `/`
// puts hashed assets under `/assets`, which FastAPI mounts.
export default defineConfig({
  plugins: [react()],
  build: { outDir: 'dist' },
})
