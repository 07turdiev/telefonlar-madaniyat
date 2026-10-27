import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  build: { sourcemap: false },
  server: {
    // Backend (uvicorn) porti. Prod'da /api'ni nginx backendga uzatadi.
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
