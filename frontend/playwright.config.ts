import { existsSync } from 'node:fs';
import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.ARES_E2E_ORIGIN || 'http://127.0.0.1:8014',
    headless: true,
    launchOptions: {
      executablePath:
        process.env.ARES_CHROMIUM ||
        (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined),
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    },
    trace: 'retain-on-failure',
  },
  reporter: [['list']],
  outputDir: 'test-results',
});
