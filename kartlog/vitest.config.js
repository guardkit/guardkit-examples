import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({
    hot: !process.env.VITEST,
    compilerOptions: {
      hydratable: true,
      dev: true
    }
  })],
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: [],
    browser: {
      enabled: false
    }
  },
  resolve: {
    alias: {
      '$lib': '/src/lib'
    }
  }
});
