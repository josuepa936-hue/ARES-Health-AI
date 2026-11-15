import { defineConfig } from '@playwright/test';
import { existsSync } from 'node:fs';
export default defineConfig({
  testDir: './public-e2e',
  workers: 1,
  timeout: 30000,
  use: {
    baseURL: process.env.ARES_PUBLIC_TEST_URL || 'http://127.0.0.1:18000',
    headless: true,
    launchOptions: {
      executablePath:
        process.env.ARES_CHROMIUM ||
        (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined),
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    },
    trace: 'retain-on-failure',
  },
  outputDir: 'test-results/public',
});
