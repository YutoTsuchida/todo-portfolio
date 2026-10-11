import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'

export default defineConfig(({ mode, command }) => {
  const env = loadEnv(mode, fileURLToPath(new URL('..', import.meta.url)), '')
  const target = process.env.API_PROXY_TARGET ?? env.API_PROXY_TARGET
  if (command === 'serve' && mode !== 'test' && !target) {
    throw new Error('Set API_PROXY_TARGET in the root .env or environment')
  }
  return {
    plugins: [react()],
    server: {
      port: 5173,
      strictPort: true,
      proxy: target ? { '/api': { target } } : undefined,
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./tests/setup.ts'],
    },
  }
})
