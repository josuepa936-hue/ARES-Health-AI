import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './offline-e2e',
  workers: 1,
  timeout: 30000,
  expect: { timeout: 10000 },
  use: {
    baseURL: 'http://127.0.0.1:8000',
    headless: true,
    launchOptions: {
      executablePath: process.env.ARES_CHROMIUM || '/usr/bin/chromium',
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    },
    trace: 'retain-on-failure',
  },
  reporter: [['list'], ['json', { outputFile: '/results/browser-results.json' }]],
  outputDir: '/results/browser',
});
