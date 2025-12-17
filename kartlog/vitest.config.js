import { defineConfig } from 'vitest/config'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// Svelte 5 requires browser condition to use client-side lifecycle functions
export default defineConfig({
  plugins: [
    svelte({
      compilerOptions: {
        dev: true
      },
      hot: !process.env.VITEST
    })
  ],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: [],
    testTimeout: 20000,
    hookTimeout: 20000,
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache'
    ]
  },
  resolve: {
    conditions: ['browser', 'import', 'module', 'default']
  },
  ssr: {
    noExternal: ['svelte']
  }
})
