import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/**',
        'tests/**',
        'vendor/**',
        '**/*.spec.js',
        '**/*.config.js'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80
      }
    },
    include: ['tests/**/*.spec.js'],
    exclude: ['node_modules', 'vendor'],
    testTimeout: 10000,
    hookTimeout: 10000
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './js'),
      '@components': path.resolve(__dirname, './js/components'),
      '@charts': path.resolve(__dirname, './js/charts'),
      '@data': path.resolve(__dirname, './js/data'),
      '@diagrams': path.resolve(__dirname, './js/diagrams')
    }
  }
});
