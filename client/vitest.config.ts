import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  define: {
    // Override API URL for tests
    'import.meta.env.VITE_API_URL': JSON.stringify('http://localhost:8000'),
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['src/**/*.{test,spec}.{js,ts}', 'tests/**/*.{test,spec}.{js,ts}'],
    dangerouslyIgnoreUnhandledErrors: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'src/**/*.d.ts',
        'src/main.ts',
        'src/assets/**',
        'src/components/HelloWorld.vue',
        'src/components/TheWelcome.vue',
        'src/components/WelcomeItem.vue',
        'src/components/icons/**',
      ],
      thresholds: {
        global: {
          statements: 90,
          branches: 80,
          functions: 48,
          lines: 90,
        },
      },
    },
    setupFiles: ['./tests/setup.ts'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
